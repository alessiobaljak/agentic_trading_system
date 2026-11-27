import sys, pickle
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from research.programma6 import asticella as a
P = '/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/'
D = pickle.load(open(P + 'mazzo_mio.pkl', 'rb'))
serie, soli = D['serie'], D['soli']
for via in (('168', '169'), ('162', '163', '165', '168', '169')):
    s2 = {k: v for k, v in serie.items() if k.split()[0] not in via}
    gr = a.gruppi(s2, a.TAGLIO)
    print('senza', via, 'serie', len(s2), 'N', len(a.per_v(gr, soli, False)), 'dev V', round(float(np.std(a.per_v(gr, soli, True), ddof=1)), 4))
g = [g for g in D['gr'] if '57 G1' in g['membri']][0]
print('famiglia di G1:', len(g['membri']), 'membri; contiene 168/169:', [m for m in g['membri'] if m.split()[0] in ('168', '169')])
