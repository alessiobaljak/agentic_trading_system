import json, sys
from collections import Counter
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
info = {x["symbol"]: x for x in json.load(open("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore/verifica/api/exchangeInfo.json"))["symbols"]}
pan = sc.pannello(); t0 = pan["t0"]; S = pan["simboli"]; C = pan["close"]; T = C.shape[0]
ok = np.isfinite(C)
buchi = Counter(); chi = {}
for j, s in enumerate(S):
    idx = np.flatnonzero(ok[:, j])
    if len(idx) < 2: continue
    dentro = np.arange(idx[0], idx[-1] + 1)
    for i in dentro[~ok[dentro, j]]:
        d = sc.data(int(i) + t0); buchi[d] += 1; chi.setdefault(d, []).append(s)
print("giorni con candele mancanti dentro la vita delle monete (giorno: monete), i primi 12 per numero:")
for d, n in buchi.most_common(12): print("  ", d, n)
for d in ("2022-02-26", "2022-04-01"):
    l = chi.get(d, [])
    st = Counter(info[s]["status"] if s in info else "assente" for s in l)
    print(d, "monete", len(l), "stato oggi in exchangeInfo:", dict(st), "| non piu' quotate:", [s for s in l if s not in info or info[s]["status"] != "TRADING"][:15])
