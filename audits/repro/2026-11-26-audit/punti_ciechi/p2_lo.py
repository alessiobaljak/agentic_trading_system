import sys, math, pickle
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import asticella as a, terza as te
P = '/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/'
D = pickle.load(open(P + 'mazzo_mio.pkl', 'rb'))
serie, soli, gr, sr_g, sr_v = D['serie'], D['soli'], D['gr'], D['sr_g'], D['sr_v']
# Sharpe e autocorrelazione delle serie a incasso fisso
for n in ('97 CC', '157 A', '157 B', '159 A', '159 B', '161 A', '161 B'):
    x = serie[n].dropna()
    rho = x.autocorr(1)
    sh = a.sharpe(x)
    # correzione di Lo (2002) per autocorrelazione di ordine 1 a scala annua q=52: eta = sqrt(q / (q + 2*sum_{k=1}^{q-1}(q-k) rho^k))
    q = 52
    eta = math.sqrt(q / (q + 2 * sum((q - k) * rho ** k for k in range(1, q))))
    print(n, 'sett', len(x), 'Sharpe', round(sh, 2), 'rho1', round(rho, 2), 'Sharpe Lo (AR1)', round(sh * eta, 2))
g = [g for g in gr if '157 A' in g['membri']][0]
print('famiglia', g['membri'], round(g['sharpe'], 2))
v3 = [1.0 if x > 3 else x for x in sr_v]
for n in ('57 G1', '168 A', '168 B', '169 A', '169 B'):
    x = serie[n].dropna(); i = te.numeri_settimana(x)
    print(n, 'con famiglia a 1,0:', round(te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], v3, 52, n_prove=len(sr_g)), 3))
