import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
pan = sc.pannello(); t0 = pan['t0']; sim = pan['simboli']
C = pan['close']; V = pan['quote_volume']
j = sim.index('PUMPUSDT')
g0 = int(pd.Timestamp('2025-04-10').timestamp() // 86400) - t0; g1 = int(pd.Timestamp('2025-07-20').timestamp() // 86400) - t0
ok = np.isfinite(C[g0:g1, j])
print('PUMPUSDT giorni con prezzo fra 2025-04-10 e 2025-07-20:', ok.sum(), 'di', g1 - g0)
idx = np.flatnonzero(ok)
salti = np.flatnonzero(np.diff(idx) > 1)
for k in salti:
    print('  buco da', sc.data(t0 + g0 + idx[k]), 'a', sc.data(t0 + g0 + idx[k + 1]))
print('  ultimi prezzi prima del buco:', [(sc.data(t0+g0+i), C[g0+i, j], round(np.nan_to_num(V[g0+i, j])/1e6,2)) for i in idx[max(0, salti[0]-2):salti[0]+3]] if len(salti) else '')
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv')
r = []
for _, x in ev.iterrows():
    j = sim.index(x['simbolo']); k = int(x['L']) - t0
    med = np.nanmedian(V[k - 30:k, j]); r.append({'simbolo': x['simbolo'], 'data': x['data'], 'vol_L_su_mediana30': V[k, j] / med if med > 0 else np.inf, 'r': x['r']})
d = pd.DataFrame(r).sort_values('vol_L_su_mediana30', ascending=False)
print(d.head(15).to_string(index=False))
print('mediana del rapporto', d['vol_L_su_mediana30'].median())
