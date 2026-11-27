import json, math, pickle, sys
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import terza as te
M = pickle.load(open("mio_mazzo.pkl", "rb")); S = pickle.load(open("scenari.pkl", "rb"))
v, N, cand = S["v_oggi"], S["N"], S["cand"]
nomi = dict(M["nomi_soli"])
print({k: round(nomi[k], 3) for k in ("151 WE", "153 A", "153 B")})
def riga(vv, tag):
    print(f"{tag:28s} V {len(vv)} dev {np.std(vv, ddof=1):.4f} | " + " ".join(f"{c}={te.sharpe_corretto(*cand[c], vv, 52, n_prove=N):.3f}" for c in ("G1 (misura 12 nov)", "168 A", "168 B", "F5+M7+K2")))
riga(v, "oggi")
riga(v + [nomi["153 B"]], "con 153 B in V")
riga(v + [nomi["153 B"], nomi["151 WE"]], "con 153 B e 151 in V")
print("media di V oggi", round(np.mean(v), 3))
