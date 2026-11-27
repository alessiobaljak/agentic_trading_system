import math, pickle, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import terza as te
M = pickle.load(open("mio_mazzo.pkl", "rb")); S = pickle.load(open("scenari.pkl", "rb"))
serie, cand, N, v_oggi, v_sym = M["serie"], S["cand"], S["N"], S["v_oggi"], S["v_sym"]
def nw_var(x, L):
    u = x - x.mean(); n = len(u); s = (u @ u) / n
    for k in range(1, L + 1): s += 2 * (1 - k / (L + 1)) * (u[k:] @ u[:-k]) / n
    return s
src = {"G1 (misura 12 nov)": "57 G1", "168 B": "168 B", "F5+M7+K2": "28 F5+M7+K2"}
for L in (4, 5):
    out = []
    for c, n in src.items():
        x = serie[n].dropna().to_numpy(float)
        x = x[np.flatnonzero(x != 0)[0]:]
        r = x.var(ddof=0) / nw_var(x, L)
        sh, w, a, k = cand[c]
        neff = max(3, int(round(w * r)))
        out.append(f"{c}: rapporto {r:.2f} sett eff {neff} oggi {te.sharpe_corretto(sh, neff, a, k, v_oggi, 52, n_prove=N):.3f} simm {te.sharpe_corretto(sh, neff, a, k, v_sym, 52, n_prove=N):.3f}")
    print(f"ritardi {L}: " + " | ".join(out))
