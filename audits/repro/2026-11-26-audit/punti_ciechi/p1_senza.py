import sys, math, pickle
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from research.programma6 import asticella as a, terza as te
P = '/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/'
D = pickle.load(open(P + 'mazzo_mio.pkl', 'rb'))
s2 = {k: v for k, v in D['serie'].items() if k.split()[0] not in ('157', '159', '161')}
gr = a.gruppi(s2, a.TAGLIO); g, v = a.per_v(gr, D['soli'], False), a.per_v(gr, D['soli'], True)
def soglia(n, srv, N):
    lo, hi = 0.0, 15.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if te.sharpe_corretto(mid, n, 0.0, 3.0, srv, 52, n_prove=N) < 0.80: lo = mid
        else: hi = mid
    return hi
print('senza 157/159/161: N', len(g), 'dev', round(float(np.std(v, ddof=1)), 4), {n: round(soglia(n, v, len(g)), 2) for n in (300, 150, 100, 52, 22)})
# e se N fosse contato dentro la famiglia (es. N = 10) o con N di G1 (57)
print('mazzo com e, N=57:', {n: round(soglia(n, D['sr_v'], 57), 2) for n in (300, 150, 100, 52, 22)})
print('mazzo com e, N=10:', {n: round(soglia(n, D['sr_v'], 10), 2) for n in (300, 150, 100, 52, 22)})
