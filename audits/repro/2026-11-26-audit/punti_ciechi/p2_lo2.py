import sys, math, pickle
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from research.programma6 import terza as te
P = '/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/'
D = pickle.load(open(P + 'mazzo_mio.pkl', 'rb'))
serie, sr_g, sr_v = D['serie'], D['sr_g'], D['sr_v']
fam = [g for g in D['gr'] if '157 A' in g['membri']][0]
# lo Sharpe della famiglia (serie media) corretto con Lo AR(1)
import pandas as pd
m = pd.concat([serie[k] for k in fam['membri']], axis=1).mean(axis=1).dropna()
rho = m.autocorr(1); q = 52
eta = math.sqrt(q / (q + 2 * sum((q - k) * rho ** k for k in range(1, q))))
print('famiglia media: rho1', round(rho, 2), 'Sharpe', round(fam['sharpe'], 2), '-> Lo', round(fam['sharpe'] * eta, 2))
for val in (1.0, round(fam['sharpe'] * eta, 2), 1.5, 2.0):
    v3 = [val if x > 3 else x for x in sr_v]
    r = {n: round(te.sharpe_corretto(*[te.numeri_settimana(serie[n].dropna())[k] for k in ('sharpe', 'settimane', 'asimmetria', 'curtosi')], v3, 52, n_prove=len(sr_g)), 3) for n in ('57 G1', '168 A', '168 B', '169 A', '169 B')}
    print('famiglia a', val, 'dev', round(float(np.std(v3, ddof=1)), 3), r)
