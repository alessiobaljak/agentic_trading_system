"""Il controllo della prova 105 rifatto con le stesse candele complete; differenza evento-controllo con bootstrap per settimana."""
import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
sys.path.insert(0, '/tmp/revisore105')
import numpy as np, pandas as pd
from research.programma6 import esecuzione as es, quarta as qa, seconda as sc, trentesima as tr, ventunesima as vu
from research.programma7 import quarantatreesima as q

pan = sc.pannello(); t0 = pan['t0']
giorni = np.arange(pan['close'].shape[0]) + t0
jb = pan['simboli'].index('BTCUSDT')
fb = pd.Series(pan['funding'][:, jb], index=giorni)
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv')
# stessi controlli del codice (stesso seme, stesso ordine degli eventi = 105 ammessi)
primi = json.loads(q.PRIMI.read_text())
V = pan['quote_volume']
eventi = []
for b, v in sorted(primi.items()):
    L, s = v['primo_giorno_coinbase'], v['perpetuo']
    if not isinstance(L, int) or L <= 0 or not (q.DA <= L <= q.A) or s == 'BTCUSDT':
        continue
    if v['primo_giorno_perpetuo'] > L - q.STORIA_MIN:
        continue
    j = pan['simboli'].index(s); k = L - t0
    if not (0 <= k < V.shape[0]) or not np.nan_to_num(V[k, j]) > 0:
        continue
    eventi.append((s, L))
rng = np.random.default_rng(q.SEME)
controlli = []
ultimo = int(giorni[-1]) - q.GIORNI - 1
for s, L in eventi:
    cand = np.arange(L + 60, min(L + 366, ultimo))
    if len(cand):
        for g in rng.choice(cand, size=min(q.CONTROLLI, len(cand)), replace=False):
            controlli.append((s, int(g)))
cb = es.ore_di('BTCUSDT')
cache = {}
def candele(s, completo):
    k = (s, completo)
    if k not in cache:
        a = es.ore_di(s)
        if completo:
            z = qa.ore(s)
            if len(z):
                z = z.dropna(how='all')
                a = z if a.empty else pd.concat([a, z[~z.index.isin(a.index)]]).sort_index()
        cache[k] = a
    return cache[k]
for completo in (False, True):
    cr = []
    for s, g in controlli:
        j = pan['simboli'].index(s)
        op = q.operazione(candele(s, completo), cb, pd.Series(pan['funding'][:, j], index=giorni), fb, g)
        if op:
            cr.append({'data': sc.data(g), 'annuncio': int((g + 3) // 7), 'simbolo': s, 'g': g, 'r': op['r']})
    co = pd.DataFrame(cr)
    print('completo' if completo else 'come il codice', 'controlli', len(co), 'media', round(100 * co['r'].mean(), 3), '%')
    if completo:
        co.to_csv('/tmp/revisore105/controllo_rifatto.csv', index=False)
orig = pd.read_csv(q.RIS / 'controllo_CB.csv')
print('controllo originale', len(orig), round(100 * orig['r'].mean(), 3))
co = pd.read_csv('/tmp/revisore105/controllo_rifatto.csv')
pm = co.groupby('simbolo')['r'].mean()
ev['ctrl'] = pm.reindex(ev['simbolo']).to_numpy()
ev['diff'] = ev['r'] - ev['ctrl']
d = ev[np.isfinite(ev['diff'])]
print('eventi con controllo', len(d), 'diff media', round(100 * d['diff'].mean(), 2))
# bootstrap per evento (come il codice) e per settimana
b = np.random.default_rng(2026).choice(d['diff'].to_numpy(), size=(10000, len(d)), replace=True).mean(axis=1)
print('p per evento', (b <= 0).mean())
bw = vu.bootstrap_annunci(d, 'diff')
print('per settimana', bw)
# sui 91 originali
o = pd.read_csv(q.RIS / 'eventi_CB.csv')
pmo = orig.groupby('simbolo')['r'].mean()
o['diff'] = o['r'] - pmo.reindex(o['simbolo']).to_numpy()
print('91 originali: p diff per settimana', vu.bootstrap_annunci(o[np.isfinite(o['diff'])], 'diff'))
ev.to_csv('/tmp/revisore105/eventi_rifatti_ctrl.csv', index=False)
