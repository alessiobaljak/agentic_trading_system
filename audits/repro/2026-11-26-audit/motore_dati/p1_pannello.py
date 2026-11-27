import numpy as np, pandas as pd
from research.programma6 import seconda as sc
pan = sc.pannello()
C = pan["close"]; O = pan["open"]; V = pan["quote_volume"]; F = pan["funding"]
T, S = C.shape
print("t0", sc.data(pan["t0"]), "ultimo", sc.data(pan["t0"] + T - 1), "giorni", T, "simboli", S)
n = np.isfinite(C).sum(axis=1)
for k in range(1, 8):
    print("giorno", sc.data(pan["t0"] + T - k), "monete con prezzo", n[T - k])
# buchi interni: giorni NaN fra il primo e l'ultimo prezzo di una moneta
buchi = []
for j in range(S):
    ok = np.flatnonzero(np.isfinite(C[:, j]))
    if len(ok) < 2: continue
    a, z = ok[0], ok[-1]
    nb = int((~np.isfinite(C[a:z+1, j])).sum())
    if nb: buchi.append((pan["simboli"][j], nb, sc.data(pan["t0"]+a), sc.data(pan["t0"]+z)))
print("monete con buchi interni", len(buchi))
for b in sorted(buchi, key=lambda x: -x[1])[:15]: print(" ", b)
# giorni con chiusura uguale a quella del giorno prima e volume > 0 (prezzo fermo con scambi)
