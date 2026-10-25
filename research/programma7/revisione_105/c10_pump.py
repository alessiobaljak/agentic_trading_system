import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
pan = sc.pannello(); t0 = pan['t0']; sim = pan['simboli']
for s, da, a in (('PUMPUSDT', '2025-04-08', '2025-07-25'), ('MONUSDT', '2025-10-08', '2025-11-28'), ('MEGAUSDT', '2026-01-28', '2026-05-03'), ('SENTUSDT','2025-11-12','2026-01-25'), ('NOMUSDT','2025-09-29','2025-11-15'), ('LINEAUSDT','2025-08-30','2025-10-11'), ('RAVEUSDT','2025-12-12','2026-02-13'), ('XPLUSDT','2025-08-20','2025-12-04')):
    j = sim.index(s)
    g0 = int(pd.Timestamp(da).timestamp() // 86400) - t0; g1 = int(pd.Timestamp(a).timestamp() // 86400) - t0
    d = pd.DataFrame({'data': [sc.data(t0 + g) for g in range(g0, g1)], 'close': pan['close'][g0:g1, j], 'vol_M': pan['quote_volume'][g0:g1, j] / 1e6, 'funding': pan['funding'][g0:g1, j]})
    print('=====', s)
    print(d.iloc[list(range(0, min(8, len(d)))) + list(range(max(8, len(d) - 8), len(d)))].to_string(index=False))
