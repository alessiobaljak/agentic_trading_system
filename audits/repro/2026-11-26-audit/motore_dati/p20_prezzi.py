import numpy as np
from research.programma6 import seconda as sc
pan = sc.pannello(); t0 = pan["t0"]; O, H, L, C, V = (pan[k] for k in ("open", "high", "low", "close", "quote_volume"))
ok = np.isfinite(C)
with np.errstate(invalid="ignore"):
    incoerenti = ok & ((H < np.maximum(O, C) * (1 - 1e-9)) | (L > np.minimum(O, C) * (1 + 1e-9)) | (L <= 0))
print("candele incoerenti (massimo sotto apertura/chiusura, minimo sopra, prezzo <= 0):", int(incoerenti.sum()))
for t, j in np.argwhere(incoerenti)[:8]:
    print("  ", pan["simboli"][j], sc.data(t + t0), O[t, j], H[t, j], L[t, j], C[t, j])
# apertura del giorno lontana dalla chiusura del giorno prima (salto fra candele consecutive)
with np.errstate(all="ignore"):
    salto = O[1:] / C[:-1]
grandi = np.argwhere(ok[1:] & ok[:-1] & ((salto > 1.2) | (salto < 0.8)))
print("aperture lontane piu' del 20% dalla chiusura del giorno prima:", len(grandi))
for t, j in grandi[:12]:
    print("  ", pan["simboli"][j], sc.data(t + 1 + t0), "chiusura prima", C[t, j], "apertura", O[t + 1, j], "volume", round(V[t + 1, j] / 1e6, 1), "M")
