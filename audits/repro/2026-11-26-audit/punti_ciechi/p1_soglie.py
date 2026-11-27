import sys, math, pickle
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from scipy import stats
from research.programma6 import terza as te
D = pickle.load(open('/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/mazzo_mio.pkl', 'rb'))
serie, sr_g, sr_v = D['serie'], D['sr_g'], D['sr_v']
N = len(sr_g)
def sr0_annuo(srv, N):
    var = float(np.var([x / math.sqrt(52) for x in srv], ddof=1)); g = 0.5772156649
    return math.sqrt(var) * ((1 - g) * stats.norm.ppf(1 - 1 / N) + g * stats.norm.ppf(1 - 1 / (N * math.e))) * math.sqrt(52)
def soglia(n, srv, N, p=0.80, asim=0.0, curt=3.0):
    lo, hi = 0.0, 15.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if te.sharpe_corretto(mid, n, asim, curt, srv, 52, n_prove=N) < p: lo = mid
        else: hi = mid
    return hi
print('N', N, 'V', len(sr_v), 'dev', round(float(np.std(sr_v, ddof=1)), 4), 'sr0 annuo', round(sr0_annuo(sr_v, N), 3))
print('N=57 sr0', round(sr0_annuo(sr_v, 57), 3))
print('soglie (normale):', {n: round(soglia(n, sr_v, N), 2) for n in (300, 150, 100, 52, 22)})
# senza le serie >3 (la sola correzione 'leggera' dell'analisi del 23 nov)
srv2 = [x for x in sr_v if x <= 3.0]
print('V senza >3:', len(srv2), 'dev', round(float(np.std(srv2, ddof=1)), 4), {n: round(soglia(n, srv2, N), 2) for n in (300, 150, 100, 52, 22)})
# G1 e F5 con le loro asimmetria e curtosi
for nome in ('57 G1', '24 F5', '69 G11', '88 G1N'):
    s = serie[nome].dropna(); i = te.numeri_settimana(s)
    p = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v, 52, n_prove=N)
    print(nome, 'Sh', round(i['sharpe'], 3), 'sett', i['settimane'], 'asim', round(i['asimmetria'], 2), 'curt', round(i['curtosi'], 2), 'prob', round(p, 3),
          '| soglia con la sua forma, stesse settimane:', round(soglia(i['settimane'], sr_v, N, asim=i['asimmetria'], curt=i['curtosi']), 2))
