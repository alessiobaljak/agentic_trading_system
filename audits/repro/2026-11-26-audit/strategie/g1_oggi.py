import sys, math
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from research.programma6 import asticella as a, terza as te
serie, soli = a.mazzo()
gr = a.gruppi(serie, a.TAGLIO)
sr_g, sr_v = a.per_v(gr, soli, False), a.per_v(gr, soli, True)
for nome in ('57 G1', '24 F5', '28 K2', '113 N3G'):
    s = serie[nome].dropna()
    i = te.numeri_settimana(s)
    p = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v, 52, n_prove=len(sr_g))
    p57 = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v, 52, n_prove=57)
    sr_v2 = [x for x in sr_v if x <= 3.0]
    p2 = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v2, 52, n_prove=len(sr_g))
    print(nome, 'sharpe', round(i['sharpe'],2), 'settimane', i['settimane'], 'asim', round(i['asimmetria'],2), 'curt', round(i['curtosi'],2),
          '| prob oggi', round(p,3), '| senza serie >3', round(p2,3), '| con N=57', round(p57,3))
