import json, math, pickle, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import terza as te
from research.programma6 import asticella as ast
M = pickle.load(open("mio_mazzo.pkl", "rb")); serie = M["serie"]
def nw_t(x, L):
    u = x - x.mean(); n = len(u); s = (u @ u) / n
    for k in range(1, L + 1):
        s += 2 * (1 - k / (L + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / math.sqrt(s / n)
g1 = serie["57 G1"].dropna()
fino57 = json.load(open("/home/user/agentic_trading_system/audits/repro/mazzo_2026-11-12_esito_fino57.json"))["scenari"]["prove 1-57 senza la conferma 50"]
v65 = list(np.array([-1.0, 1.0]) * fino57["dev_V"] / math.sqrt(2))
for n in ("168 B", "160 A", "160 B", "161 B"):
    x = serie[n].dropna(); c = x.index.intersection(g1.index)
    k = g1.loc[c].std() / x.loc[c].std()
    d2 = (k * x.loc[c] - g1.loc[c]).to_numpy(float)
    xs = x.loc[c].to_numpy(float)
    sh = xs.mean()/xs.std(ddof=1)*math.sqrt(52)
    from scipy import stats
    p65 = te.sharpe_corretto(sh, len(xs), float(pd.Series(xs).skew()), float(pd.Series(xs).kurt()+3), v65, 52, n_prove=65)
    print(f"{n}: Sharpe {sh:.2f} prob N65 {p65:.3f} | diff a pari vol (x{k:.2f}): annua {d2.mean()*52:+.3f} t {d2.mean()/(d2.std(ddof=1)/math.sqrt(len(d2))):.2f} NW4 {nw_t(d2,4):.2f} NW8 {nw_t(d2,8):.2f} NW13 {nw_t(d2,13):.2f} ac1 diff {pd.Series(d2).autocorr(1):.2f}")
