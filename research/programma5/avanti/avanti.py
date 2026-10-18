"""Programma 5: la prova in avanti delle procedure registrate (REGOLE.md, sezione 9).

Per ogni procedura registrata (``idee/M-NNN/avanti.md``): le candidate sul periodo WA (dal giugno 2025 ai dati piu'
nuovi), la scelta di ogni mese da ottobre 2026 con i soli trade gia' chiusi, e i trade **chiusi** in A (ingresso da
ottobre 2026). Scrive ``avanti/A.json`` e ``avanti/A.md`` con i numeri e, quando una procedura ha almeno 400 trade chiusi
(o dal 2027-03-31), l'esito.

Uso: PYTHONPATH=. python3 research/programma5/avanti/avanti.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import meta, meta2
from research.programma5.strumenti.esplora_calendario import celle as celle_calendario
from research.programma5.strumenti.esplora_fase2 import celle_moneta
from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.fase2 import MONETE_F2

QUI = Path(__file__).parent
RADICE = QUI.parents[2]
CENTO = tuple(json.loads((QUI.parent / "universo_top100.json").read_text())["scelte"])
PRIMO_A = 81                       # 2026-10, mesi contati da 2020-01
N_MESI = 12 * 80                   # abbastanza mesi per gli anni a venire
FINE = datetime(2027, 3, 31, tzinfo=timezone.utc)

PROCEDURE = {
    "M-001c": {"idea": "M-001", "monete": MONETE_F2, "tipo": "netto", "L": 12, "K": 10},
    "M-002": {"idea": "M-002", "monete": CENTO, "tipo": "vantaggio", "L": 12, "K": 10},
    "M-003": {"idea": "M-003", "monete": CENTO, "tipo": "netto", "L": 12, "K": 10},
}


def ultimo_mese() -> int:
    ora = datetime.now(timezone.utc)
    return (ora.year - 2020) * 12 + ora.month - 1


def caso(t: pd.DataFrame, A: dict, ore: np.ndarray, info: dict, ripetizioni: int = 20, seme: int = 2026) -> float:
    """Ingressi a caso nello stesso mese, stessa moneta, stessa direzione e durata, stessi costi (G1 escluse)."""
    rng = np.random.default_rng(seme)
    mese_ora = meta.indice_mese(ore * 60)
    medie = []
    for _ in range(ripetizioni):
        v = []
        for s, m, cella, verso, c in zip(t["simbolo"], meta.indice_mese(t["minuto"].to_numpy()), t["cella"],
                                         t["verso"], t["costo"]):
            if cella.startswith("G1") or cella not in info:
                continue
            d, h = info[cella]
            a = A[h].get(s)
            if a is None:
                continue
            pos = np.flatnonzero((mese_ora == m) & np.isfinite(a))
            if len(pos):
                v.append(d * (1 if verso == "segue" else -1) * a[rng.choice(pos)] - c)
        medie.append(np.mean(v) if v else np.nan)
    return float(np.nanmean(medie))


def esame(t: pd.DataFrame, n_procedure: int, finale: bool) -> dict:
    if t.empty:
        return {"trade": 0, "esito": "nessun trade chiuso"}
    m = t["minuto"].to_numpy()
    e = {"trade": int(len(t)), "netto": m5.bootstrap_giorni(t["netto"].to_numpy(), m, 10000),
         "netto_doppio": float(t["netto_doppio"].mean()), "costo": float(t["costo"].mean())}
    giorno = m // 1440
    somme = t.groupby(giorno)["netto"].sum()
    e["senza_migliore"] = float(t["netto"][giorno != somme.idxmax()].mean()) if len(somme) > 1 else float("nan")
    e["per_moneta"] = {s: {"trade": int(len(g)), "netto": float(g["netto"].mean())} for s, g in t.groupby("simbolo")}
    e["per_mese"] = {str(k): {"trade": int(len(g)), "netto": float(g["netto"].mean())}
                     for k, g in t.groupby(meta.indice_mese(m))}
    if not finale:
        e["esito"] = f"in corso ({len(t)} trade chiusi su 400)"
        return e
    soglia = 0.05 / n_procedure
    monete = [x for x in e["per_moneta"].values() if x["trade"] >= 10]
    if not e["netto"]["p"] <= soglia or not e["netto"]["media"] > 0:
        e["esito"] = f"non passa: p {e['netto']['p']:.4f} oltre {soglia:.4f} o netto non positivo"
    elif not e["netto_doppio"] > 0:
        e["esito"] = "non passa: non positivo a costi doppi"
    elif not e["senza_migliore"] > 0:
        e["esito"] = "non passa: non positivo togliendo il giorno migliore"
    elif sum(1 for x in monete if x["netto"] > 0) < 0.6 * len(monete):
        e["esito"] = "non passa: positivo su meno del 60% delle monete"
    else:
        e["esito"] = "PASSA: strategia valida"
    return e


def main() -> int:
    for f in (m5.DATI / "ore").glob("*_WA.pkl"):
        f.unlink()                 # il periodo WA cresce: le barre si rifanno ogni volta
    ultimo = ultimo_mese()
    finale_data = datetime.now(timezone.utc) >= FINE
    risultati = {}
    cache, pannelli = {}, {}
    for nome, p in PROCEDURE.items():
        chiave = (p["monete"], p["tipo"])
        if chiave not in cache:
            if p["tipo"] == "vantaggio":
                cache[chiave] = meta2.con_versi(meta2.trade_candidate_base(p["monete"], "WA", p["idea"],
                                                                           log=lambda x: None))
            else:
                cache[chiave] = meta.con_versi(meta.trade_candidate(p["monete"], "WA", p["idea"], log=lambda x: None))
        cand = cache[chiave]
        if p["tipo"] == "vantaggio":
            t, scelte = meta2.scegli_eccesso(cand, p["L"], p["K"], PRIMO_A, ultimo, N_MESI)
        else:
            t, scelte = meta.scegli_e_tieni(cand, p["L"], p["K"], PRIMO_A, ultimo, N_MESI)
        finale = finale_data or len(t) >= 400
        e = esame(t, len(PROCEDURE), finale)
        if len(t):
            if p["monete"] not in pannelli:
                ore, P, A = meta.pannello(p["monete"], "WA", p["idea"])
                b, btc = P["ETHUSDT"], P["BTCUSDT"]
                info = {n: (int(d[0]), h) for n, f, h, pp, c, d, v in celle_moneta("ETHUSDT", b, btc, A)}
                info.update({n: (int(d[0]), h) for n, f, h, pp, c, d in celle_calendario(b)})
                pannelli[p["monete"]] = (ore, A, info)
            ore, A, info = pannelli[p["monete"]]
            e["caso_netto"] = caso(t, A, ore, info)
        e["scelte"] = {str(k): [f"{c} | {v}" for c, v in s] for k, s in scelte.items()}
        risultati[nome] = e
        if len(t):
            t.to_csv(QUI / f"trade_A_{nome}.csv.gz", index=False)
        print(nome, e.get("trade"), e.get("esito"), flush=True)
    dati_fino = max((x.name for x in (m5.DATI / "BTCUSDT" / "klines").glob("*.zip")), default="?")
    (QUI / "A.json").write_text(json.dumps({"dati_fino_a": dati_fino, "procedure": risultati}, ensure_ascii=False,
                                           indent=1, default=float), encoding="utf-8")
    righe = ["# Prova in avanti delle procedure (periodo A, dal 2026-10-01)", "",
             f"Calcolo di `avanti.py` (REGOLE.md, sezione 9) con i dati fino a `{dati_fino}`. Solo trade chiusi.", "",
             "| Procedura | Trade chiusi | Netto a trade | Intervallo al 95% | p | A costi doppi | Caso | Esito |",
             "|---|---|---|---|---|---|---|---|"]
    for nome, e in risultati.items():
        if not e.get("trade"):
            righe.append(f"| {nome} | 0 | | | | | | {e['esito']} |")
            continue
        nt = e["netto"]
        righe.append(f"| {nome} | {e['trade']} | {100 * nt['media']:+.3f}% | {100 * nt['basso']:+.3f}; "
                     f"{100 * nt['alto']:+.3f} | {nt['p']:.4f} | {100 * e['netto_doppio']:+.3f}% | "
                     f"{100 * e.get('caso_netto', float('nan')):+.3f}% | {e['esito']} |")
    (QUI / "A.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
