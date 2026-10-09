"""Fase 3: studio dei fallimenti di una variante testata, SOLO sui dati di costruzione.

Uso: python fallimenti.py ETICHETTA. Raggruppa i trade per caratteristiche note all'ingresso e per
esito, e stampa R medio e numero per gruppo. Scrive anche in data/insample/BNBUSDT/fallimenti_<ETICHETTA>.txt.
"""
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import lancia  # noqa: E402

etichetta = sys.argv[1]
v = lancia.SPEC[etichetta][1]("analisi")
d = C.carica(v.tf, "costruzione")
cand = d["candele"]
ris = C.motore.esegui(cand, None, d["mark"], d["funding"], C.fabbrica(v, cand)(), C.parametri())
ctx = C.contesto(v, cand)
ind = ctx.ind
righe = []
for t in ris.trades:
    k = ctx.indice_ts[t.ts_entrata]  # barra d'ingresso; il segnale e' a k-1
    s = k - 1
    dt = datetime.fromtimestamp(cand[s].ts / 1000, tz=timezone.utc)
    atr_rel = ind["atr"][s] / ind["close"][s]
    righe.append({"r": t.r, "esito": t.esito, "barre": (t.ts_uscita - t.ts_entrata) // d["ms_barra"] + 1,
                  "ora": dt.hour, "giorno": dt.weekday(), "anno": dt.year, "atr_rel": atr_rel,
                  "ind": {kk: float(np.asarray(vv, dtype=float)[s]) for kk, vv in ind.items()
                          if kk not in ("ts", "open", "high", "low", "volume")}})
out = []


def gruppo(nome, chiave):
    g = defaultdict(list)
    for r in righe:
        g[chiave(r)].append(r["r"])
    out.append(f"-- per {nome}")
    for kk in sorted(g, key=str):
        out.append(f"   {kk}: n={len(g[kk])} R medio={np.mean(g[kk]):+.3f} quota vincenti={np.mean(np.array(g[kk]) > 0):.2f}")


rr = np.array([r["r"] for r in righe])
out.append(f"{etichetta}: {len(righe)} trade, R medio {rr.mean():+.3f}, mediano {np.median(rr):+.3f}")
gruppo("esito", lambda r: r["esito"])
durate = np.array([r["barre"] for r in righe])
out.append(f"-- durate in barre: quantili 10/33/50/67/90 = {np.quantile(durate, [0.1, 1/3, 0.5, 2/3, 0.9]).round(1).tolist()}, massimo {durate.max()}")
for e in sorted(set(r["esito"] for r in righe)):
    de = np.array([r["barre"] for r in righe if r["esito"] == e])
    out.append(f"   {e}: durata mediana {np.median(de):.1f}, quantili 10/90 = {np.quantile(de, [0.1, 0.9]).round(1).tolist()}")
gruppo("durata in barre (esatta, fino a 8)", lambda r: min(r["barre"], 8))
gruppo("durata in barre (terzili)", lambda r: int(np.searchsorted(np.quantile([x["barre"] for x in righe], [1/3, 2/3]), r["barre"])))
gruppo("anno", lambda r: r["anno"])
gruppo("ora UTC (blocchi di 6)", lambda r: r["ora"] // 6)
gruppo("giorno della settimana", lambda r: r["giorno"])
q = np.quantile([r["atr_rel"] for r in righe], [1/3, 2/3])
out.append(f"-- ATR relativo al prezzo: confini dei terzili {q.round(5).tolist()}, quantili 10/50/90 "
           f"{np.quantile([r['atr_rel'] for r in righe], [0.1, 0.5, 0.9]).round(5).tolist()}")
for soglia in (0.004, 0.005, 0.006, 0.007, 0.008):
    sel = [r["r"] for r in righe if r["atr_rel"] >= soglia]
    out.append(f"   ATR relativo >= {soglia}: n={len(sel)} R medio={np.mean(sel) if sel else float('nan'):+.3f}")
gruppo("ATR relativo al prezzo (terzili, 0=basso)", lambda r: int(np.searchsorted(q, r["atr_rel"])))
for chiave in sorted(righe[0]["ind"]):
    vals = [r["ind"][chiave] for r in righe]
    if np.all(np.isfinite(vals)) and len(set(vals)) > 3:
        qq = np.quantile(vals, [1/3, 2/3])
        gruppo(f"{chiave} al segnale (terzili)", lambda r, c=chiave, qq=qq: int(np.searchsorted(qq, r["ind"][c])))
testo = "\n".join(out)
print(testo)
(C.dati.RADICE_DEFAULT / "data" / "insample" / "BNBUSDT" / f"fallimenti_{etichetta}.txt").write_text(testo, encoding="utf-8")
