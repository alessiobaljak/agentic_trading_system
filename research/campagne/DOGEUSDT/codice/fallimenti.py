"""Fase 3: studio dei trade in costruzione di una variante gia' testata (dove fallisce, con numeri).

Uso: python fallimenti.py ID. Scrive in data/insample/DOGEUSDT/uscite/fallimenti_<ID>.txt.
Solo dati di costruzione; nessuna nuova regola si testa qui.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro as q  # noqa: E402
from varianti import VARIANTI  # noqa: E402

id_ = sys.argv[1]
v = VARIANTI[id_]()
d = q.serie(v.tf)
v.prepara(d)
cand, mark, fund = q._tagli(d, "costruzione")
ris = q.motore.esegui(cand, None, mark, fund, q.crea_variante(v)(), q.PARAMETRI)
tr = ris.trades
idx = {int(t): k for k, t in enumerate(d["ts"])}
s200 = q.sma(d["close"], 200)
atr_pct = v.a / d["close"]
righe = []


def gruppo(nome, chiave):
    g = {}
    for t in tr:
        g.setdefault(chiave(t), []).append(t.r)
    righe.append(f"\n{nome}:")
    for k in sorted(g, key=str):
        x = g[k]
        righe.append(f"  {k}: n={len(x)} R medio={np.mean(x):.3f} win={np.mean([r > 0 for r in x]):.2f}")


def segnale(t):
    return idx[t.ts_entrata] - 1


gruppo("esito", lambda t: t.esito)
gruppo("anno-trimestre", lambda t: f"{datetime.fromtimestamp(t.ts_entrata/1000, tz=timezone.utc).year}-T{(datetime.fromtimestamp(t.ts_entrata/1000, tz=timezone.utc).month-1)//3+1}")
gruppo("ora UTC dell'ingresso (gruppi di 6)", lambda t: datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).hour // 6)
gruppo("sopra la SMA200 alla barra del segnale", lambda t: bool(d["close"][segnale(t)] > s200[segnale(t)]) if np.isfinite(s200[segnale(t)]) else None)
q_atr = np.nanpercentile([atr_pct[segnale(t)] for t in tr], [33, 67])
gruppo("ATR in % (terzili)", lambda t: int(np.searchsorted(q_atr, atr_pct[segnale(t)])))
vol = d["vol_usdt"]
vm = q.sma(np.nan_to_num(vol), 24 * 7 if v.tf == "1h" else 30)
q_v = np.nanpercentile([vol[segnale(t)] / vm[segnale(t)] for t in tr], [33, 67])
gruppo("volume della barra del segnale / media (terzili)", lambda t: int(np.searchsorted(q_v, vol[segnale(t)] / vm[segnale(t)])))
r = np.array(sorted([t.r for t in tr]))
righe.append(f"\nR ordinati: 5 peggiori {np.round(r[:5], 2).tolist()}, 5 migliori {np.round(r[-5:], 2).tolist()}")
righe.append(f"trade {len(tr)}, R medio {r.mean():.3f}, mediano {np.median(r):.3f}")
uscita = q.RADICE_REPO / "research" / "data" / "insample" / "DOGEUSDT" / "uscite" / f"fallimenti_{id_}.txt"
uscita.write_text("\n".join(righe))
print("\n".join(righe))
