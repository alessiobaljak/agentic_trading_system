import json, numpy as np
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
pan = sc.pannello(); t0 = pan["t0"]
out = {}
for (a, m, g) in [(2026, 10, 26), (2026, 11, 2), (2026, 11, 9), (2026, 11, 16), (2026, 11, 23)]:
    i = sc.giorno(a, m, g) - t0
    u = n.universo_lunedi(pan, i)
    out[sc.data(i + t0)] = [pan["simboli"][j] for j in np.flatnonzero(u)]
    print(sc.data(i + t0), int(u.sum()))
tutti = sorted(set(x for v in out.values() for x in v))
print("unione", len(tutti))
json.dump({"universi": out, "unione": tutti}, open("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati/universi_nov.json", "w"))
