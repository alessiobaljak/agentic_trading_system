import math, pickle, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import terza as te
from research.programma6 import asticella as ast
M = pickle.load(open("mio_mazzo.pkl", "rb")); S = pickle.load(open("scenari.pkl", "rb"))
serie, soli, gr, cand, N = M["serie"], M["soli"], M["gr"], S["cand"], S["N"]
tv = lambda s, w: s * math.sqrt(w / 52)
def lo(x, L=8):
    x = pd.Series(x).dropna().to_numpy(float); u = x - x.mean(); n = len(u); s = (u @ u) / n
    for k in range(1, L + 1): s += 2 * (1 - k / (L + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / math.sqrt(s) * math.sqrt(52)
fcc = next(g for g in gr if "157 A" in g["membri"])
m = pd.concat([serie[x] for x in fcc["membri"]], axis=1).mean(axis=1)
print("famiglia 97/157/161: Sharpe semplice", round(ast.sharpe(m), 2), "di Lo (8 ritardi)", round(lo(m, 8), 2), "(13)", round(lo(m, 13), 2), "(26)", round(lo(m, 26), 2))
def p(v, tag):
    print(f"{tag:62s} V {len(v)} dev {np.std(v, ddof=1):.3f} | " + " ".join(f"{c}={te.sharpe_corretto(*cand[c], v, 52, n_prove=N):.3f}" for c in ("G1 (misura 12 nov)", "168 A", "168 B", "F5+M7+K2")))
fam = [(g["sharpe"], g["settimane"], g["membri"]) for g in gr]
base = [s for s, w, mm in fam if tv(s, w) >= -3] + [s for s in soli if tv(s, 300) >= -3]
p(base, "oggi")
# simmetrico ma la famiglia di G1 (della candidata) resta in V
v_sym_g1 = [s for s, w, mm in fam if -3 <= tv(s, w) <= 3 or "57 G1" in mm] + [s for s in soli if -3 <= tv(s, 300) <= 3]
p(v_sym_g1, "simmetrico, ma la famiglia di G1 (delle candidate) resta in V")
v_sym = [s for s, w, mm in fam if -3 <= tv(s, w) <= 3] + [s for s in soli if -3 <= tv(s, 300) <= 3]
p(v_sym, "simmetrico (anche la famiglia di G1 fuori)")
# CC con lo Sharpe di Lo al posto di quello semplice (proposta P34)
v_lo = [ (lo(m, 8) if mm == fcc["membri"] else s) for s, w, mm in fam if tv(s, w) >= -3] + [s for s in soli if tv(s, 300) >= -3]
p(v_lo, "proposta P34: famiglia a incasso fisso con lo Sharpe di Lo (8)")
