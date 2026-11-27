import sys, math, pickle
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import asticella as a, terza as te
P = '/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/punti_ciechi/'
D = pickle.load(open(P + 'mazzo_mio.pkl', 'rb'))
serie, sr_g, sr_v = D['serie'], D['sr_g'], D['sr_v']
g1 = serie['57 G1']
righe = []
for n, x in serie.items():
    x = x.dropna()
    if len(x) < 26: continue
    i = te.numeri_settimana(x)
    t = i['sharpe'] * math.sqrt(i['settimane'] / 52)
    anni = x.groupby(pd.to_datetime(x.index.to_numpy() * 86400, unit='s').year).mean()
    c = x.index.intersection(g1.index)
    rho = float(np.corrcoef(x.loc[c], g1.loc[c])[0, 1]) if len(c) > 30 and x.loc[c].std() > 0 else float('nan')
    p = te.sharpe_corretto(i['sharpe'], i['settimane'], i['asimmetria'], i['curtosi'], sr_v, 52, n_prove=len(sr_g))
    righe.append((n, round(i['sharpe'], 2), i['settimane'], round(t, 2), int((anni > 0).sum()), len(anni), round(rho, 2), round(p, 3)))
d = pd.DataFrame(righe, columns=['nome', 'sharpe', 'sett', 't', 'anni_pos', 'anni', 'rho_G1', 'prob'])
f = d[(d.t >= 3) & (d.anni_pos == d.anni) & (d.rho_G1.abs() < 0.5)].sort_values('sharpe', ascending=False)
print('serie con t>=3, ogni anno positivo, |rho con G1|<0,5:', len(f))
print(f.to_string(index=False))
d.to_csv(P + 'p1_tutte.csv', index=False)
