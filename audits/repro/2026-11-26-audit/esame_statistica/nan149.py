"""Le serie della 149 con settimane vuote (NaN) prima della quotazione: correlazione 0 con le serie piene? Sola lettura."""
import json, math, pickle, sys
from pathlib import Path
import numpy as np
import pandas as pd
REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
from research.programma6 import asticella as ast
from research.programma6 import terza as te
serie, soli = pickle.load(open("mazzo.pkl", "rb"))
gr = pickle.load(open("gruppi.pkl", "rb"))
con_nan = [n for n, s in serie.items() if s.isna().any()]
print("serie con NaN:", con_nan)
# correlazione di una di loro con le serie della 149 della stessa variante su altre monete, con e senza NaN
a = serie["149 APTUSDT_1d_A"]
for b in ("149 SOLUSDT_1d_A", "149 BTCUSDT_1d_A", "149 ETHUSDT_1d_A"):
    if b in serie:
        bb = serie[b]
        c = a.index.intersection(bb.index)
        x, y = a.loc[c], bb.loc[c]
        ok = (x.abs() > 0) | (y.abs() > 0)
        r_code = np.corrcoef(x[ok], y[ok])[0, 1]
        okn = ok & x.notna() & y.notna()
        print(f"  APT_1d_A con {b}: come nel codice {r_code}, togliendo i NaN {np.corrcoef(x[okn], y[okn])[0, 1]:.3f} ({okn.sum()} settimane)")
pulite = {n: (s.dropna() if n in con_nan else s) for n, s in serie.items()}
gr2 = ast.gruppi(pulite, ast.TAGLIO)
mis = json.loads((REPO / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
G1 = (mis["sharpe"], mis["settimane"], mis["asimmetria"], mis["curtosi"])
for nome, g in (("oggi", gr), ("senza NaN", gr2)):
    sr_g, sr_v = ast.per_v(g, soli, False), ast.per_v(g, soli, True)
    fam_nan = [x["membri"] for x in g if any(m in con_nan for m in x["membri"])]
    print(f"{nome}: famiglie {len(sr_g)}, in V {len(sr_v)}, dev {np.std(sr_v, ddof=1):.4f}, G1 {te.sharpe_corretto(*G1, sr_v, 52, n_prove=len(sr_g)):.4f}; famiglie con APT/MATIC {fam_nan}")
