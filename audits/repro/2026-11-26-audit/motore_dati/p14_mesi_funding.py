import numpy as np, pandas as pd
from pathlib import Path
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]; C, V = pan["close"], pan["quote_volume"]
# monete-mese con candele (volume > 0) e senza file mensile del funding, prima di novembre 2026
mesi = pd.to_datetime((np.arange(T) + t0) * 86400, unit="s").to_period("M").astype(str)
idx = np.arange(sc.giorno(2021, 1, 4) - t0, sc.giorno(2026, 10, 5) - t0)
U = n.universo_giorni(pan, idx)
buchi, nell_universo = [], 0
for j, s in enumerate(pan["simboli"]):
    fm = {p.name[-11:-4] for p in (sc.DATI / s / "funding").glob("*.zip")}
    if not fm: continue
    primo_f = min(fm)
    vivi = np.isfinite(C[:, j]) & (np.nan_to_num(V[:, j]) > 0)
    mm = sorted({mesi[t] for t in np.flatnonzero(vivi) if mesi[t] < "2026-11" and mesi[t] >= primo_f})
    manca = [m for m in mm if m not in fm]
    if manca:
        giorni_u = int(sum(U[k, j] for k in range(len(idx)) if mesi[idx[k]] in manca))
        nell_universo += giorni_u
        buchi.append((s, manca, giorni_u))
print("monete con mesi senza file del funding (fra il primo file e ottobre 2026):", len(buchi), "| giorni-moneta nell'universo di G1 in quei mesi:", nell_universo)
for b in buchi[:20]: print("  ", b)
