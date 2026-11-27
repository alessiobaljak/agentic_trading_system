import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from research.programma6 import asticella as a, terza as te
serie, soli = a.mazzo()
via = [n for n in serie if n.split()[0] in ('157', '159', '161')]
print('tolte (come in P34: senza 157, 159 e 161):', via)
s2 = {k: v for k, v in serie.items() if k not in via}
gr = a.gruppi(s2, a.TAGLIO)
sr_g, sr_v = a.per_v(gr, soli, False), a.per_v(gr, soli, True)
print('famiglie', len(sr_g), 'in V', len(sr_v), 'dev V', round(float(np.std(sr_v, ddof=1)), 3))
for nome in ['57 G1', '24 F5', '168 A', '168 B', '169 A', '169 B', '156 B', '158 B']:
    s = serie[nome].dropna(); i = te.numeri_settimana(s)
    p = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v, 52, n_prove=len(sr_g))
    print(f"{nome}: Sharpe {i['sharpe']:.2f} -> probabilità senza 157/159/161 = {p:.3f}")
