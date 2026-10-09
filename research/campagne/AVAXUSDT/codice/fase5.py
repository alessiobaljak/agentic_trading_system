"""Fase 5, test dello scettico su V-14 (solo costruzione): e' solo il mercato?

Divide i trade di V-14 secondo lo z della stessa barra di 4 ore di BTCUSDT (stessa regola: rendimento
della barra / devstd dei 180 rendimenti precedenti). Se l'effetto viene da BTC, i trade con BTC calmo
(z di BTC sotto 1) dovrebbero rendere come il caso.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402

var = VARIANTI["V-14"]
ctx = comune.contesto("4h", "costruzione")
b = comune.btc_close(ctx)
rb = np.r_[np.nan, b[1:] / b[:-1] - 1]
zb = np.full(ctx.n, np.nan)
for i in range(181, ctx.n):
    zb[i] = rb[i] / np.nanstd(rb[i - 180:i])
ris = comune.esegui(var, ctx)
gruppi = {"BTC z < 1 (BTC calmo)": [], "BTC z fra 1 e 2": [], "BTC z >= 2 (anche BTC anomalo)": []}
for t in ris.trades:
    s = ctx.indice_ts[t.ts_entrata] - 1
    z = zb[s]
    k = "BTC z < 1 (BTC calmo)" if z < 1 else ("BTC z fra 1 e 2" if z < 2 else "BTC z >= 2 (anche BTC anomalo)")
    gruppi[k].append(t.r)
for k, v in gruppi.items():
    if v:
        print(f"{k:34s} n {len(v):4d}  R medio {np.mean(v):+.4f}  mediana {np.median(v):+.4f}")
