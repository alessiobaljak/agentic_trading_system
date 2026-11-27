import math, pickle, sys
import numpy as np, pandas as pd
from scipy import stats
def nw_var(x, L):
    u = x - x.mean(); n = len(u); s = (u @ u) / n
    for k in range(1, L + 1):
        s += 2 * (1 - k / (L + 1)) * (u[k:] @ u[:-k]) / n
    return s
def t_nw(x, L):
    return x.mean() / math.sqrt(nw_var(x, L) / len(x))
M = pickle.load(open("mio_mazzo.pkl", "rb")); serie = M["serie"]
for nome in ("57 G1", "88 G1N", "69 G11", "24 F5"):
    s = serie[nome].dropna()
    d = pd.to_datetime(s.index.to_numpy() * 86400, unit="s")
    for tag, y in (("tutto", s.to_numpy(float)), ("dal 2022", s[d.year >= 2022].to_numpy(float))):
        n = len(y); t0 = y.mean() / (y.std(ddof=1) / math.sqrt(n))
        sp = [stats.spearmanr(y[k:], y[:-k])[0] for k in (1, 2, 3)]
        print(f"{nome:7s} {tag:8s} n {n} t {t0:.2f} NW4 {t_nw(y,4):.2f} NW8 {t_nw(y,8):.2f} NW13 {t_nw(y,13):.2f} rapporto NW8/t {t_nw(y,8)/t0:.2f} | Spearman ac1-3 " + " ".join(f"{v:.2f}" for v in sp))
