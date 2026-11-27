import math, pickle, sys
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import terza as te
M = pickle.load(open("mio_mazzo.pkl", "rb")); S = pickle.load(open("scenari.pkl", "rb"))
v, N, cand = S["v_oggi"], S["N"], S["cand"]
n108 = [n for n, s in M["nomi_soli"] if n.startswith(("108 ", "111 "))]
print("varianti 108+111 senza serie:", len(n108), "(108:", sum(n.startswith("108 ") for n in n108), "111:", sum(n.startswith("111 ") for n in n108), ")",
      "Sharpe", sorted(set(s for n, s in M["nomi_soli"] if n.startswith(("108 ", "111 ")))))
for n, tag in ((N, "oggi"), (N - len(n108) + 2, "108 e 111 come 2 famiglie"), (N - len(n108) + 13, "13 famiglie"), (N - len(n108), "tolte")):
    print(f"{tag:28s} N {n} | " + " ".join(f"{c}={te.sharpe_corretto(*cand[c], v, 52, n_prove=n):.3f}" for c in ("G1 (misura 12 nov)", "168 A", "168 B", "F5+M7+K2")))
