import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
from research.programma7 import quarantatreesima as q
pan = sc.pannello(); t0 = pan['t0']
V = pan['quote_volume']
primi = json.loads(q.PRIMI.read_text())
tipi = {}
for b, v in primi.items():
    L = v['primo_giorno_coinbase']
    tipi.setdefault(type(L).__name__ + (':<=0' if isinstance(L, int) and L <= 0 else ''), 0)
    tipi[type(L).__name__ + (':<=0' if isinstance(L, int) and L <= 0 else '')] += 1
print('tipi primo_giorno_coinbase', tipi)
ev = pd.read_csv(q.RIS / 'eventi_CB.csv')
fatti = set(ev['simbolo'])
tutti = []
for b, v in sorted(primi.items()):
    L, s = v['primo_giorno_coinbase'], v['perpetuo']
    if not isinstance(L, int) or L <= 0 or not (q.DA <= L <= q.A) or s == 'BTCUSDT':
        continue
    eta = L - v['primo_giorno_perpetuo']
    j = pan['simboli'].index(s); k = L - t0
    vol = np.nan_to_num(V[k, j]) if 0 <= k < V.shape[0] else None
    tutti.append((b, s, sc.data(L), eta, vol, s in fatti))
df = pd.DataFrame(tutti, columns=['base','perp','L','eta_perp','vol_L','nel_conto'])
print('monete con L nel periodo', len(df))
print('con eta>=30', (df.eta_perp >= 30).sum())
print(df[(df.eta_perp >= 30) & ~df.nel_conto].to_string())
print()
print('L con eta <30 (esclusi):', (df.eta_perp<30).sum())
print(df[(df.eta_perp>=30)&(df.eta_perp<120)].to_string())
