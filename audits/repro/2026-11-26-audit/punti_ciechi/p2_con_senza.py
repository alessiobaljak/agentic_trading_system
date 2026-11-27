import sys, math, pickle, json
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import asticella as a, terza as te
P = '/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/'
D = pickle.load(open(P + 'mazzo_mio.pkl', 'rb'))
serie, soli, gr, sr_g, sr_v = D['serie'], D['soli'], D['gr'], D['sr_g'], D['sr_v']
nomi = ['57 G1', '24 F5', '69 G11', '88 G1N', '168 A', '168 B', '169 A', '169 B']
# numeri pubblicati in esame.json
p7 = '/home/user/agentic_trading_system/research/programma7/'
for c in ('risultati_centosesta', 'risultati_centosettima_bis'):
    e = json.load(open(p7 + c + '/esame.json'))
    for v in ('A', 'B'):
        x = e.get(v) or e.get('varianti', {}).get(v)
        if x is None:
            print(c, 'chiavi', list(e)[:10]); break
        i = x.get('intero', x)
        print(c, v, {k: i.get(k) for k in ('sharpe', 'settimane', 'asimmetria', 'curtosi')}, 'corretto pubblicato:', x.get('corretto', x.get('sharpe_corretto', x.get('esame', {}))) if not isinstance(x.get('corretto'), dict) else x['corretto'])
def prob(nome, srv, N, s=serie):
    x = s[nome].dropna(); i = te.numeri_settimana(x)
    return te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], srv, 52, n_prove=N), i
print('\nMAZZO COM\'E\': N', len(sr_g), 'V', len(sr_v), 'dev', round(float(np.std(sr_v, ddof=1)), 4))
for n in nomi:
    p, i = prob(n, sr_v, len(sr_g))
    x = serie[n].dropna(); anni = x.groupby(pd.to_datetime(x.index.to_numpy() * 86400, unit='s').year).mean()
    print(f"  {n}: Sh {i['sharpe']:.3f} sett {i['settimane']} t {i['sharpe']*math.sqrt(i['settimane']/52):.2f} anni>0 {(anni>0).sum()}/{len(anni)} prob {p:.3f}")
via = [n for n in serie if n.split()[0] in ('157', '159', '161')]
print('\nSENZA', via)
s2 = {k: v for k, v in serie.items() if k not in via}
gr2 = a.gruppi(s2, a.TAGLIO)
g2, v2 = a.per_v(gr2, soli, False), a.per_v(gr2, soli, True)
print('  N', len(g2), 'V', len(v2), 'dev', round(float(np.std(v2, ddof=1)), 4))
for n in nomi:
    p, i = prob(n, v2, len(g2))
    print(f"  {n}: prob senza {p:.3f}")
# famiglie con Sharpe alto nel mazzo com'e'
print('\nfamiglie con Sharpe > 2.5:', [(round(g['sharpe'], 2), g['membri'], g['settimane']) for g in gr if g['sharpe'] > 2.5])
print('V valori > 2.5:', sorted([round(x, 2) for x in sr_v if x > 2.5]))
