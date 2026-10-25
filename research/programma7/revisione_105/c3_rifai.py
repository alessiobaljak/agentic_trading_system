"""Rifà il conto della prova 105 con le candele orarie dagli zip scaricati (qa.ore) quando il pickle p6 non copre l'ora d'entrata."""
import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import esecuzione as es, quarta as qa, seconda as sc, trentesima as tr, ventunesima as vu
from research.programma7 import quarantatreesima as q

pan = sc.pannello(); t0 = pan['t0']
giorni = np.arange(pan['close'].shape[0]) + t0
jb = pan['simboli'].index('BTCUSDT')
fb = pd.Series(pan['funding'][:, jb], index=giorni)
V = pan['quote_volume']
primi = json.loads(q.PRIMI.read_text())
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
print('eventi ammessi', len(eventi))
cb = es.ore_di('BTCUSDT')
print('BTC ore_di da', sc.data(cb.index.min() // 24), 'a', sc.data(cb.index.max() // 24))

cache = {}
def candele(s):
    if s not in cache:
        a = es.ore_di(s)
        z = qa.ore(s)
        if len(z):
            z = z.dropna(how='all')
            # unisce: prima il pickle, poi gli zip per le ore che mancano
            a = z if a.empty else pd.concat([a, z[~z.index.isin(a.index)]]).sort_index()
        cache[s] = a
    return cache[s]

righe = []
for s, L in eventi:
    j = pan['simboli'].index(s)
    f = pd.Series(pan['funding'][:, j], index=giorni)
    op = q.operazione(candele(s), cb, f, fb, L + 1)
    if op:
        righe.append({'data': sc.data(L + 1), 'annuncio': int((L + 1 + 3) // 7), 'simbolo': s, 'L': L, **op})
    else:
        print('ancora senza conto', s, sc.data(L))
ev = pd.DataFrame(righe)
ev.to_csv('/tmp/revisore105/eventi_rifatti.csv', index=False)
orig = pd.read_csv(q.RIS / 'eventi_CB.csv')
m = orig.merge(ev, on='simbolo', suffixes=('_o', '_n'))
print('confronto sui 91 originali: max |diff r|', float((m['r_o'] - m['r_n']).abs().max()))
nuovi = ev[~ev['simbolo'].isin(orig['simbolo'])]
print(nuovi[['data', 'simbolo', 'r', 'fermata', 'ore']].to_string())
print('media nuovi', nuovi['r'].mean())
e = tr.esame(ev, 'r')
print('ESAME su', len(ev), 'eventi:', json.dumps({k: e[k] for k in ('boot', 'prima_meta', 'seconda_meta', 'senza_5_migliori', 'vinti', 'mediana', 'esito')}, default=float, indent=0))
print({a: (v['eventi'], round(100 * v['media'], 2)) for a, v in e['per_anno'].items()})
