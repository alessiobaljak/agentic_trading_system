"""È solo il ritorno indietro di chi è salito? Controllo nello stesso giorno con monete di salita simile (giorno L e 14 giorni prima)."""
import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc, ventunesima as vu
from research.programma6.esclusi import ESCLUSI
from research.programma7 import quarantatreesima as q
exec(open('/tmp/revisore105/c12_stessa_settimana_stop.py').read().split("ev = pd.read_csv")[0])
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv')
primi = json.loads(q.PRIMI.read_text())
cbday = {v['perpetuo']: v['primo_giorno_coinbase'] for v in primi.values()}
def rel(k, a, b):
    """rendimento della moneta contro il Bitcoin dalla chiusura di a alla chiusura di b."""
    return (C[b, k] / C[a, k]) / (C[b, jb] / C[a, jb]) - 1
out = []
for _, x in ev.iterrows():
    j = sim.index(x['simbolo']); L = int(x['L']) - t0; e = L + 1
    s1 = (C[L, j] / O[L, j]) / (C[L, jb] / O[L, jb]) - 1
    s14 = rel(j, L - 14, L)
    cand = []
    for k in range(S):
        if k in (j, jb) or sim[k] in ESCLUSI or not (primo[k] <= L - 30 and V[L, k] > 0):
            continue
        cl = cbday.get(sim[k])
        if cl is not None and abs(cl - (L + t0)) <= 45:
            continue
        a1 = (C[L, k] / O[L, k]) / (C[L, jb] / O[L, jb]) - 1
        a14 = rel(k, L - 14, L)
        rk = r_stop(k, e)
        if np.isfinite(rk) and np.isfinite(a1) and np.isfinite(a14):
            cand.append((a1, a14, rk))
    c = np.array(cand)
    # i 10 più vicini per salita (giorno L e 14 giorni), in ranghi
    def rango(v, col):
        return (c[:, col] < v).mean()
    p1, p14 = rango(s1, 0), rango(s14, 1)
    r1 = np.argsort(c[:, 0]).argsort() / len(c); r14 = np.argsort(c[:, 1]).argsort() / len(c)
    dist = np.abs(r1 - p1) + np.abs(r14 - p14)
    vicini = c[np.argsort(dist)[:10], 2]
    out.append({'data': x['data'], 'annuncio': x['annuncio'], 'simbolo': x['simbolo'], 'r': x['r'], 'salita_L': s1, 'salita_14': s14,
                'rango_L': p1, 'rango_14': p14, 'simili_salita': vicini.mean()})
d = pd.DataFrame(out)
print('salita del giorno L contro BTC: mediana', round(100 * d.salita_L.median(), 2), '% ; rango mediano fra le monete dello stesso giorno', round(d.rango_L.median(), 2))
print('salita 14 giorni: mediana', round(100 * d.salita_14.median(), 2), '% ; rango mediano', round(d.rango_14.median(), 2))
print('controllo con salita simile (10 monete per evento):', round(100 * d.simili_salita.mean(), 2), '%')
d['x'] = d['r'] - d['simili_salita']
b = vu.bootstrap_annunci(d, 'x')
print(f'evento - salita simile: {100*b["media"]:+.2f}% IC {100*b["basso"]:+.2f};{100*b["alto"]:+.2f} p {b["p"]:.4f}')
print('correlazione r con salita_L', round(d[['r', 'salita_L']].corr().iloc[0, 1], 3), 'con salita_14', round(d[['r', 'salita_14']].corr().iloc[0, 1], 3))
d['q'] = pd.qcut(d['salita_L'], 3, labels=['bassa', 'media', 'alta'])
print(d.groupby('q')[['r', 'simili_salita', 'salita_L']].mean().mul(100).round(2))
d.to_csv('/tmp/revisore105/salita.csv', index=False)
