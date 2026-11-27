"""Controprova del problema 7: le 4 serie di prima delle parita' (F5, K2, F5+M7+K2, F9) sostituite con quelle corrette."""
import math
import re
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

M = pickle.load(open(OUT / "mio_mazzo.pkl", "rb"))
S = pickle.load(open(OUT / "scenari.pkl", "rb"))
serie, soli, cand = M["serie"], M["soli"], S["cand"]
CP = REPO / "research/programma6/risultati_controllo_parita"
nuove = {"24 F5": "settimane_F5", "28 K2": "settimane_K2", "28 F5+M7+K2": "settimane_F5_M7_K2", "56 F9": "settimane_F9"}
giuste = {n: ast.periodo(pd.read_csv(CP / f"{f}.csv.gz", index_col=0)["netto"]) for n, f in nuove.items()}
for n, s in giuste.items():
    a, b = serie[n], s
    c = a.index.intersection(b.index)
    print(f"{n}: Sharpe mazzo {ast.sharpe(a):.3f} dopo le parita' {ast.sharpe(b):.3f} settimane diverse {(np.abs(a.loc[c]-b.loc[c])>1e-12).sum()} su {len(c)}")
n_soli_prove = len(soli) - len(M["nomi_soli"])
print("prove senza serie del programma 6:", n_soli_prove)


def calcola(sr, sl, tag):
    gr = ast.gruppi(sr, ast.TAGLIO)
    g, v = ast.per_v(gr, sl, False), ast.per_v(gr, sl, True)
    print(f"{tag:40s} serie {len(sr)} famiglie {len(g)} in V {len(v)} dev {np.std(v, ddof=1):.4f} | G1 "
          f"{te.sharpe_corretto(*cand['G1 (misura 12 nov)'], v, 52, n_prove=len(g)):.4f}")


num = lambda n: int(re.match(r"\d+", n).group())
f57 = {n: s for n, s in serie.items() if num(n) <= 57 and not n.startswith("50 ")}
calcola(f57, soli[:n_soli_prove], "fino alla 57 (mazzo)")
calcola({**f57, **giuste}, soli[:n_soli_prove], "fino alla 57, 4 serie dopo le parita'")
calcola(serie, soli, "oggi (mazzo)")
calcola({**serie, **giuste}, soli, "oggi, 4 serie dopo le parita'")
