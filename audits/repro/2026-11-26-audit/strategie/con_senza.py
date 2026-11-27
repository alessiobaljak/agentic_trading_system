import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from research.programma6 import asticella as a, terza as te
serie, soli = a.mazzo()
gr = a.gruppi(serie, a.TAGLIO)
sr_g, sr_v = a.per_v(gr, soli, False), a.per_v(gr, soli, True)
# senza la famiglia delle serie a incasso quasi fisso (97 CC, 157, 161): tolta da V, N invariato
fam_fisso = [g for g in gr if any(m.startswith(('157', '161')) for m in g['membri'])]
print('famiglia a incasso quasi fisso:', [(round(g['sharpe'],2), g['membri']) for g in fam_fisso])
sr_v2 = [x for x in sr_v if x <= 3.0]
print('N', len(sr_g), 'V', len(sr_v), 'V senza', len(sr_v2))
for nome in ['57 G1', '156 A', '156 B', '158 A', '158 B', '160 A', '160 B', '168 A', '168 B', '169 A', '169 B']:
    if nome not in serie: print(nome, 'non nel mazzo'); continue
    s = serie[nome].dropna(); i = te.numeri_settimana(s)
    p = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v, 52, n_prove=len(sr_g))
    p2 = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v2, 52, n_prove=len(sr_g))
    anni = s.groupby(np.asarray(__import__('pandas').to_datetime(s.index.to_numpy()*86400, unit='s').year)).mean()
    print(f"{nome}: Sharpe {i['sharpe']:.2f}, sett {i['settimane']}, t {i['sharpe']*np.sqrt(i['settimane']/52):.2f}, anni positivi {(anni>0).sum()}/{len(anni)} | prob con {p:.3f} | senza {p2:.3f}")
print('--- con la famiglia a incasso quasi fisso portata a Sharpe 1,0 (correzione di Lo, stima della revisione della 161)')
sr_v3 = [1.0 if x > 3.0 else x for x in sr_v]
print('dev V', round(float(np.std(sr_v, ddof=1)),3), '->', round(float(np.std(sr_v3, ddof=1)),3))
for nome in ['57 G1', '24 F5', '168 A', '168 B', '169 B', '156 B']:
    s = serie[nome].dropna(); i = te.numeri_settimana(s)
    p3 = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v3, 52, n_prove=len(sr_g))
    print(f"{nome}: prob con Lo {p3:.3f}")
