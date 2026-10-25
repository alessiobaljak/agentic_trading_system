"""Le uscite a +30%: l'ora che fa scattare l'uscita apre già sopra la soglia? (riempimento ottimista); e scomposizione dei lati."""
import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import esecuzione as es, quarta as qa, seconda as sc, ventunesima as vu
pan = sc.pannello(); t0 = pan['t0']
giorni = np.arange(pan['close'].shape[0]) + t0
jb = pan['simboli'].index('BTCUSDT')
cb = es.ore_di('BTCUSDT')
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv')
def candele(s):
    a = es.ore_di(s); z = qa.ore(s)
    if len(z):
        z = z.dropna(how='all'); a = z if a.empty else pd.concat([a, z[~z.index.isin(a.index)]]).sort_index()
    return a
righe = []
for _, x in ev.iterrows():
    s = x['simbolo']; g0 = int(x['L']) + 1; h0 = g0 * 24
    c = candele(s); p0 = c.loc[h0, 'open']; b0 = cb.loc[h0, 'open']
    j = pan['simboli'].index(s)
    f = pd.Series(pan['funding'][:, j], index=giorni); fb = pd.Series(pan['funding'][:, jb], index=giorni)
    uh = h0 + int(x['ore'])
    gu = (uh - 1) // 24
    fc = f[(f.index >= g0) & (f.index <= gu)].sum(); fbb = fb[(fb.index >= g0) & (fb.index <= gu)].sum()
    if x['fermata']:
        o = c.loc[uh, 'open']; hi = c.loc[uh, 'high']
        pc = p0 * 1.3 * 1.01
        pb = cb[cb.index <= uh]['close'].iloc[-1]
        righe.append({'simbolo': s, 'data': x['data'], 'ora': int(x['ore']), 'apertura_ora_su_p0': o / p0 - 1, 'massimo_ora_su_p0': hi / p0 - 1,
                      'r': x['r'], 'r_se_riempito_a_apertura': (pb / b0 - 1) - (max(o, pc) / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb})
    lato_b = (cb.loc[uh, 'open'] if (not x['fermata'] and uh in cb.index) else cb[cb.index <= uh]['close'].iloc[-1]) / b0 - 1
    ev.loc[_, 'lato_btc'] = lato_b; ev.loc[_, 'funding_netto'] = fc - fbb
d = pd.DataFrame(righe)
print(d.to_string())
print('costi fissi a operazione', vu.COSTO_MONETA + vu.COSTO_BTC)
print('lato bitcoin medio', round(100 * ev['lato_btc'].mean(), 2), '% ; funding netto medio', round(100 * ev['funding_netto'].mean(), 3), '%')
print('funding netto: min, max', ev['funding_netto'].min(), ev['funding_netto'].max())
print(ev.sort_values('funding_netto').head(5)[['simbolo','data','funding_netto','r']])
