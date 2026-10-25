"""Controllo nella stessa settimana con la stessa uscita a +30% (approssimata sui massimi giornalieri), per evento e per le altre monete."""
import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc, ventunesima as vu
from research.programma6.esclusi import ESCLUSI
from research.programma7 import quarantatreesima as q
pan = sc.pannello(); t0 = pan['t0']; sim = pan['simboli']
O, H, C, F, V = pan['open'], pan['high'], pan['close'], pan['funding'], np.nan_to_num(pan['quote_volume'])
T, S = C.shape
ok = np.isfinite(C); primo = ok.argmax(axis=0)
jb = sim.index('BTCUSDT')
COSTI = vu.COSTO_MONETA + vu.COSTO_BTC
def r_stop(j, e, giorni=7):
    """short j long BTC da apertura e; uscita se il massimo del giorno supera +30% (al prezzo soglia +1%, BTC alla chiusura del giorno)."""
    if e + giorni >= T or not np.isfinite(O[e, j]):
        return np.nan
    p0, b0 = O[e, j], O[e, jb]
    for d in range(e, e + giorni):
        if not np.isfinite(H[d, j]):
            return np.nan
        if H[d, j] >= 1.3 * p0:
            return (C[d, jb] / b0 - 1) - (0.313) - COSTI + F[e:d + 1, j].sum() - F[e:d + 1, jb].sum()
    if not np.isfinite(O[e + giorni, j]):
        return np.nan
    return (O[e + giorni, jb] / b0 - 1) - (O[e + giorni, j] / p0 - 1) - COSTI + F[e:e + giorni, j].sum() - F[e:e + giorni, jb].sum()
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv')
primi = json.loads(q.PRIMI.read_text())
cbday = {v['perpetuo']: v['primo_giorno_coinbase'] for v in primi.values()}
esclusi = set(ESCLUSI)
out = []
for _, x in ev.iterrows():
    j = sim.index(x['simbolo']); L = int(x['L']); e = L + 1 - t0; eta = L - t0 - primo[j]
    re = r_stop(j, e)
    tutti, simili = [], []
    for k in range(S):
        if k in (j, jb) or sim[k] in esclusi:
            continue
        if not (primo[k] <= L - t0 - 30 and V[L - t0, k] > 0):
            continue
        cl = cbday.get(sim[k])
        if cl is not None and abs(cl - L) <= 45:
            continue
        rk = r_stop(k, e)
        if not np.isfinite(rk):
            continue
        tutti.append(rk)
        if eta / 2 <= L - t0 - primo[k] <= eta * 2:
            simili.append(rk)
    out.append({'data': x['data'], 'annuncio': x['annuncio'], 'simbolo': x['simbolo'], 'r_ore': x['r'], 'r_giorni_stop': re,
                'mercato': np.mean(tutti), 'stessa_eta': np.mean(simili) if simili else np.nan})
d = pd.DataFrame(out)
print('evento: ore', round(100 * d.r_ore.mean(), 2), '| giorni con stop', round(100 * d.r_giorni_stop.mean(), 2))
print('correlazione ore/giorni', round(d[['r_ore', 'r_giorni_stop']].corr().iloc[0, 1], 3))
print('altre monete stesso giorno', round(100 * d.mercato.mean(), 2), '| stessa età', round(100 * d.stessa_eta.mean(), 2))
for col in ('mercato', 'stessa_eta'):
    d['x'] = d['r_ore'] - d[col]
    z = d[np.isfinite(d['x'])]
    b = vu.bootstrap_annunci(z, 'x')
    print(f'evento (ore) - {col}: {100*b["media"]:+.2f}% IC {100*b["basso"]:+.2f};{100*b["alto"]:+.2f} p {b["p"]:.4f}')
    d['x2'] = d['r_giorni_stop'] - d[col]
    b = vu.bootstrap_annunci(d[np.isfinite(d['x2'])], 'x2')
    print(f'evento (giorni, stessa misura) - {col}: {100*b["media"]:+.2f}% IC {100*b["basso"]:+.2f};{100*b["alto"]:+.2f} p {b["p"]:.4f}')
d['anno'] = d['data'].str[:4]
print(d.groupby('anno')[['r_ore', 'r_giorni_stop', 'mercato', 'stessa_eta']].mean().mul(100).round(2))
d.to_csv('/tmp/revisore105/stessa_settimana_stop.csv', index=False)
