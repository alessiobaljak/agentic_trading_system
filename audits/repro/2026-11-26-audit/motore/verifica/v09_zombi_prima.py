import sys
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
pan = sc.pannello(); t0 = pan["t0"]; S = pan["simboli"]; V = pan["quote_volume"]; C = pan["close"]
for s, d in (("LITUSDT", (2025, 12, 23)), ("PUMPUSDT", (2025, 7, 10)), ("CTKUSDT", (2025, 4, 30)), ("SLPUSDT", (2025, 7, 23)),
             ("CVXUSDT", (2025, 7, 23)), ("CVCUSDT", (2025, 5, 16)), ("MAVIAUSDT", (2025, 3, 26)), ("AERGOUSDT", (2025, 4, 16))):
    j = S.index(s); i = sc.giorno(*d) - t0
    k = i - 1; n = 0
    while k >= 0 and np.isfinite(C[k, j]) and np.nan_to_num(V[k, j]) == 0:
        n += 1; k -= 1
    print(f"{s:10s} rilancio {sc.data(i + t0)}: giorni a volume zero subito prima {n} (ultimo scambio {sc.data(k + t0)})")
