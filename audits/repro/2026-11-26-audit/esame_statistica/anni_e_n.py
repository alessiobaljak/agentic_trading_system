"""Anni positivi con la somma contro il conto composto; N con 108 e 111 come 2 famiglie. Sola lettura."""
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
flip = []
for n, s in serie.items():
    s = s.dropna()
    if len(s) < 104:
        continue
    t = ast.sharpe(s) * math.sqrt(len(s) / 52)
    if t < 3:
        continue
    anno = pd.to_datetime(s.index.to_numpy() * 86400, unit="s").year
    for a in sorted(set(anno)):
        x = s[anno == a]
        som, comp = x.sum(), np.prod(1 + x.to_numpy()) - 1
        if (som > 0) != (comp > 0):
            flip.append((n, a, len(x), round(som, 4), round(comp, 4)))
print("serie con t >= 3 e un anno che cambia segno fra somma e conto composto:", flip if flip else "nessuna")
# G1 per anno: somma e composto
s = serie["57 G1"].dropna(); anno = pd.to_datetime(s.index.to_numpy() * 86400, unit="s").year
print("G1 per anno (settimane, somma, composto):", [(a, int((anno == a).sum()), round(s[anno == a].sum(), 3), round(np.prod(1 + s[anno == a].to_numpy()) - 1, 3)) for a in sorted(set(anno))])
mis = json.loads((REPO / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
G1 = (mis["sharpe"], mis["settimane"], mis["asimmetria"], mis["curtosi"])
e168 = json.loads((REPO / "research/programma7/risultati_centosesta/esame.json").read_text())["esame"]["B"]["intero"]
B = tuple(e168[k] for k in ("sharpe", "settimane", "asimmetria", "curtosi"))
sr_g, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
for NN, et in ((len(sr_g), "oggi"), (len(sr_g) - 24, "108 e 111 come 2 famiglie invece di 26"), (len(sr_g) - 26, "108 e 111 fuori da N")):
    print(f"N {NN} ({et}): G1 {te.sharpe_corretto(*G1, sr_v, 52, n_prove=NN):.4f}, 168 B {te.sharpe_corretto(*B, sr_v, 52, n_prove=NN):.4f}")
