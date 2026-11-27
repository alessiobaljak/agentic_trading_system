import math, pickle, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import asticella as ast
M = pickle.load(open("mio_mazzo.pkl", "rb")); serie = M["serie"]
flip, n_ok = [], 0
for n, s in serie.items():
    s = s.dropna()
    if len(s) < 52 or ast.sharpe(s) * math.sqrt(len(s) / 52) < 3:
        continue
    n_ok += 1
    anno = pd.to_datetime(s.index.to_numpy() * 86400, unit="s").year
    for a in sorted(set(anno)):
        x = s[anno == a].to_numpy(float)
        media52, comp = x.mean() * 52, np.prod(1 + x) - 1
        if (media52 > 0) != (comp > 0):
            flip.append((n, int(a), len(x), round(media52, 4), round(x.sum(), 4), round(comp, 4)))
print("serie con t >= 3:", n_ok, "| anni che cambiano segno fra media x 52 (esame) e composto:", flip)
s = serie["57 G1"].dropna(); anno = pd.to_datetime(s.index.to_numpy() * 86400, unit="s").year
print("G1 (settimane, somma, composto):", [(int(a), int((anno == a).sum()), round(s[anno == a].sum(), 3), round(np.prod(1 + s[anno == a].to_numpy()) - 1, 3)) for a in sorted(set(anno))])
