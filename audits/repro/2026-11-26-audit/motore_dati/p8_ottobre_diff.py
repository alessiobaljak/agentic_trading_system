import pandas as pd, numpy as np
from research.programma6 import seconda as sc
x = pd.read_csv("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati/confronto_funding.csv.gz")
o = x[x.g < sc.giorno(2026, 11, 1)].copy(); o["d"] = (o.pannello - o.vero).abs()
print((o.d > 1e-6).sum(), "righe di ottobre diverse su", len(o))
print(o.sort_values("d", ascending=False).head(8).assign(data=lambda z: z.g.map(lambda g: sc.data(int(g))))[["s", "data", "vero", "pannello", "int"]].to_string())
print(o[o.d > 1e-6].g.map(lambda g: sc.data(int(g))).value_counts().to_dict())
