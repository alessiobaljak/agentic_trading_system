"""Controllo nella stessa settimana: le altre monete (stessa età, stesso giorno d'entrata), short contro il Bitcoin 7 giorni,
dal pannello giornaliero (apertura→apertura, senza l'uscita a +30%), confrontate con l'evento misurato allo stesso modo."""
import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc, ventunesima as vu
from research.programma6.esclusi import ESCLUSI
from research.programma7 import quarantatreesima as q

pan = sc.pannello(); t0 = pan['t0']; sim = pan['simboli']
O, C, F, V = pan['open'], pan['close'], pan['funding'], np.nan_to_num(pan['quote_volume'])
T, S = C.shape
ok = np.isfinite(C); primo = ok.argmax(axis=0)
jb = sim.index('BTCUSDT')
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti_ctrl.csv')
primi = json.loads(q.PRIMI.read_text())
cbday = {v['perpetuo']: v['primo_giorno_coinbase'] for v in primi.values()}
# monete in comune con Coinbase quotate su Coinbase nei ±45 giorni: fuori dal controllo
def r7(j, e):
    if e + 7 >= T or not (np.isfinite(O[e, j]) and np.isfinite(O[e + 7, j])):
        return np.nan
    return vu.rendimento(pan, j, jb, e, 7)
esclusi = set(ESCLUSI) if not isinstance(ESCLUSI, dict) else set(ESCLUSI)
out = []
for _, x in ev.iterrows():
    j = sim.index(x['simbolo']); L = int(x['L']); e = L + 1 - t0
    eta = L - t0 - primo[j]
    re = r7(j, e)
    tutti, eta_sim = [], []
    for k in range(S):
        if k in (j, jb) or sim[k] in esclusi or not sim[k].endswith('USDT'):
            continue
        if not (primo[k] <= L - t0 - 30 and V[L - t0, k] > 0):
            continue
        cl = cbday.get(sim[k])
        if cl is not None and abs(cl - L) <= 45:
            continue
        rk = r7(k, e)
        if not np.isfinite(rk):
            continue
        tutti.append(rk)
        ek = L - t0 - primo[k]
        if eta / 2 <= ek <= eta * 2:
            eta_sim.append(rk)
    out.append({'data': x['data'], 'annuncio': x['annuncio'], 'simbolo': x['simbolo'], 'r_ore': x['r'], 'r7_giorni': re,
                'mercato': np.mean(tutti), 'n_mercato': len(tutti), 'stessa_eta': np.mean(eta_sim) if eta_sim else np.nan,
                'n_eta': len(eta_sim), 'eta': eta})
d = pd.DataFrame(out)
d.to_csv('/tmp/revisore105/stessa_settimana.csv', index=False)
print('eventi', len(d))
print('evento 7 giorni senza uscita (pannello)', round(100 * d['r7_giorni'].mean(), 2), '| con uscita, ore', round(100 * d['r_ore'].mean(), 2))
print('tutte le altre monete stesso giorno', round(100 * d['mercato'].mean(), 2), '| stessa età', round(100 * d['stessa_eta'].mean(), 2))
for col in ('mercato', 'stessa_eta'):
    d['x_' + col] = d['r7_giorni'] - d[col]
    z = d[np.isfinite(d['x_' + col])]
    b = vu.bootstrap_annunci(z, 'x_' + col)
    print('eccesso evento -', col, round(100 * b['media'], 2), 'IC', round(100 * b['basso'], 2), round(100 * b['alto'], 2), 'p', round(b['p'], 4), 'n', b['eventi'])
d['anno'] = d['data'].str[:4]
print(d.groupby('anno')[['r7_giorni', 'mercato', 'stessa_eta', 'x_mercato', 'x_stessa_eta']].mean().mul(100).round(2))
print('età mediana del perpetuo agli eventi (giorni)', d['eta'].median())
