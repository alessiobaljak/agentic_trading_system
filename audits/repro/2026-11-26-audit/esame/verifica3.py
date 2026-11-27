"""Controprova del problema 3: varianti di G1 con N = 65 e confronto con G1 sulle stesse settimane."""
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import terza as te  # noqa: E402

M = pickle.load(open(OUT / "mio_mazzo.pkl", "rb"))
serie = M["serie"]
S = pickle.load(open(OUT / "scenari.pkl", "rb"))
cand = S["cand"]
fino57 = json.loads((REPO / "audits/repro/mazzo_2026-11-12_esito_fino57.json").read_text())["scenari"]["prove 1-57 senza la conferma 50"]
dev, N65 = fino57["dev_V"], fino57["famiglie"]
v65 = list(np.array([-1.0, 1.0]) * dev / math.sqrt(2))
for c in ("G1 (misura 12 nov)", "168 A", "168 B", "F5+M7+K2"):
    print(f"{c}: N {N65} dev {dev}: {te.sharpe_corretto(*cand[c], v65, 52, n_prove=N65):.3f}")
s65 = optimize.brentq(lambda s: te.sharpe_corretto(s, 300, 0.56, 4.09, v65, 52, n_prove=N65) - 0.80, 0.3, 6)
print(f"Sharpe che serve per 0,80 con N 65 e dev {dev}: {s65:.3f}")


def nw_t(x, L):
    u = x - x.mean()
    n = len(u)
    s = (u @ u) / n
    for k in range(1, L + 1):
        s += 2 * (1 - k / (L + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / math.sqrt(s / n)


g1 = serie["57 G1"].dropna()
print("G1 ac1 (per la differenza)", round(g1.autocorr(1), 2))
for n in ("168 A", "168 B", "169 A", "169 B", "156 A", "156 B", "158 A", "158 B", "160 A", "160 B"):
    if n not in serie:
        print(n, "non nel mazzo")
        continue
    x = serie[n].dropna()
    c = x.index.intersection(g1.index)
    d = (x.loc[c] - g1.loc[c]).to_numpy(float)
    t0 = d.mean() / (d.std(ddof=1) / math.sqrt(len(d)))
    # alla stessa volatilita' di G1
    k = g1.loc[c].std() / x.loc[c].std()
    d2 = (k * x.loc[c] - g1.loc[c]).to_numpy(float)
    t2 = d2.mean() / (d2.std(ddof=1) / math.sqrt(len(d2)))
    print(f"{n}: settimane {len(d)} diff annua {d.mean()*52:+.4f} t {t0:.2f} NW4 {nw_t(d, 4):.2f} | a pari volatilita' (x{k:.2f}) t {t2:.2f} "
          f"| corr {np.corrcoef(x.loc[c], g1.loc[c])[0,1]:.3f}")
