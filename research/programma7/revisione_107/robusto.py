import sys; sys.path.insert(0,'/tmp/revisore107'); sys.path.insert(0,'/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import ventunesima as vu
def boot(d, col, gcol, n=10000):
    d = d.copy(); d['annuncio'] = d[gcol]
    return vu.bootstrap_annunci(d, col, n=n)
for nome, path in [('pubblicato', '/home/user/agentic_trading_system/research/programma7/risultati_quarantacinquesima/eventi_G13C.csv'),
                   ('chiusure corrette + OMG', '/tmp/revisore107/eventi_finale.csv')]:
    d = pd.read_csv(path)
    if nome != 'pubblicato':
        d = d[~d.simbolo.isin(['1000BTTCUSDT','YFIIUSDT','AKROUSDT','DODOUSDT','TLMUSDT','ICPUSDT','SCUSDT','BTSUSDT','BLZUSDT','MEMEFIUSDT'])]
    d['mese'] = d['data'].str[:7]
    print('=====', nome, len(d))
    for col in ['r', 'r_senza']:
        bw = boot(d, col, 'annuncio'); bm = boot(d, col, 'mese'); ba = boot(d, col, 'id_annuncio')
        print(f" {col}: media {bw['media']:+.4f} | p settimana {bw['p']:.4f} ({bw['annunci']}) | p mese {bm['p']:.4f} ({bm['annunci']}) | p annuncio {ba['p']:.4f} ({ba['annunci']})")
        g = d.groupby('annuncio')[col].mean()
        t = g.mean() / (g.std(ddof=1) / np.sqrt(len(g)))
        print(f"   media delle settimane {g.mean():+.4f} t {t:.2f} positive {int((g>0).sum())}/{len(g)}; mediana settimane {g.median():+.4f}")
        mm = d.groupby('mese')[col].agg(['mean','count'])
        print('   mesi positivi', int((mm['mean']>0).sum()), 'su', len(mm))
        # leave one week out
        loo = [(w, d[d.annuncio != w][col].mean()) for w in g.index]
        lo = min(loo, key=lambda x: x[1]); hi = max(loo, key=lambda x: x[1])
        print(f"   togliendo una settimana: media fra {lo[1]:+.4f} e {hi[1]:+.4f}")
        top = g.sort_values(ascending=False).index[:3]
        rest = d[~d.annuncio.isin(top)]
        b3 = boot(rest, col, 'annuncio')
        print(f"   senza le 3 settimane migliori ({list(top)}): media {b3['media']:+.4f} p {b3['p']:.4f}")
    print(d.groupby('mese')[['r','r_senza']].agg(['mean','count']).round(3).to_string())
