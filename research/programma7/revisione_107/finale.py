import sys; sys.path.insert(0,'/tmp/revisore107'); sys.path.insert(0,'/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import ventunesima as vu
pub = pd.read_csv('/home/user/agentic_trading_system/research/programma7/risultati_quarantacinquesima/eventi_G13C.csv')
co = pd.read_csv('/home/user/agentic_trading_system/research/programma7/risultati_quarantacinquesima/controllo_G13C.csv')
s = pub['r'].sort_values(ascending=False)
for k in (1, 3, 5, 10):
    print(f'senza i {k} migliori: {s.iloc[k:].mean():+.4f}')
print('contributo dei 5 migliori:', s.iloc[:5].sum() / len(s))
# differenza dal controllo con bootstrap per settimana
pm = co.groupby('simbolo')['r'].mean()
pub['diff'] = pub['r'] - pub['simbolo'].map(pm)
d = pub.dropna(subset=['diff'])
print('eventi con controllo', len(d), 'differenza', d['diff'].mean())
print('p differenza, bootstrap per evento come nel codice ~0.013; per settimana:', vu.bootstrap_annunci(d, 'diff'))
# fermate
print('fermate', pub.fermata.sum(), 'media r fermate', pub[pub.fermata].r.mean(), 'media r_senza degli stessi', pub[pub.fermata].r_senza.mean())
# funding esatto sul set corretto
fc = pd.read_csv('/tmp/revisore107/funding_confronto.csv')
ev = pd.read_csv('/tmp/revisore107/eventi_corretti.csv')
m = ev.merge(fc[['simbolo','diff_%']], on='simbolo')
m['r_fx'] = m['r'] + m['diff_%'] / 100
print('set corretto (76): r', m.r.mean(), 'con funding esatto', m.r_fx.mean(), vu.bootstrap_annunci(m, 'r_fx'))
