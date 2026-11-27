import numpy as np, pandas as pd, collections
from research.programma6 import seconda as sc
pan = sc.pannello()
C = pan["close"]; V = pan["quote_volume"]
T, S = C.shape
cont = collections.Counter(); per = collections.defaultdict(list)
for j in range(S):
    ok = np.flatnonzero(np.isfinite(C[:, j]))
    if len(ok) < 2: continue
    a, z = ok[0], ok[-1]
    for t in range(a, z + 1):
        if not np.isfinite(C[t, j]):
            d = sc.data(pan["t0"] + t); cont[d] += 1; per[pan["simboli"][j]].append(d)
print("giorni mancanti (dentro la vita) per data, i piu' frequenti:")
for d, k in sorted(cont.items(), key=lambda x: -x[1])[:25]: print(" ", d, k)
print("TLM", per["TLMUSDT"][:30]); print("BNX", per["BNXUSDT"][:30]); print("ICP", per["ICPUSDT"][:30]); print("MDT", per["MDTUSDT"])
