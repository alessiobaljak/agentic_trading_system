"""Fase 3: R medio dei trade per fasce fisse della forza della barra di segnale (solo costruzione, sola lettura).

  python fase3_forza.py <ID>
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402

vid = sys.argv[1]
tf, costr = VARIANTI[vid][0], VARIANTI[vid][1]
s = comune.carica(tf, "costruzione")
ris = comune.motore.esegui(s.last, None, s.mark, s.funding, comune.fabbrica(s, costr)(), comune.PARAMETRI)
indice = {c.ts: k for k, c in enumerate(s.last)}
close = comune.arr(s.last, "close")
forza = np.array([abs(close[indice[t.ts_entrata] - 1] / close[indice[t.ts_entrata] - 2] - 1) for t in ris.trades])
r = np.array([t.r for t in ris.trades])
fasce = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 1.0]
out = {"id": vid, "trade": len(r)}
for a, b in zip(fasce, fasce[1:]):
    m = (forza >= a) & (forza < b)
    out[f"{a:.2f}-{b:.2f}"] = {"trade": int(m.sum()), "r_medio": round(float(r[m].mean()), 4) if m.sum() else None}
print(json.dumps(out))
