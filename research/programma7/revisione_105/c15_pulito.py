import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import trentesima as tr, ventunesima as vu
NON_QUOTAZIONE = ['BATUSDT', 'MANAUSDT', 'CVCUSDT', 'NOMUSDT']
TGE = ['PUMPUSDT', 'MONUSDT', 'MEGAUSDT', 'SENTUSDT']
DATA_DUBBIA = ['SOLUSDT']
for nome, f in (('originale 91', '/home/user/agentic_trading_system/research/programma7/risultati_quarantatreesima/eventi_CB.csv'), ('completo 105', '/tmp/revisore105/eventi_rifatti.csv')):
    d = pd.read_csv(f)
    print('=====', nome)
    for tit, togli in (('nulla', []), ('senza i 4 non-quotazioni', NON_QUOTAZIONE), ('senza le 4 TGE', TGE), ('senza PUMP', ['PUMPUSDT']),
                       ('senza i 9 dubbi', NON_QUOTAZIONE + TGE + DATA_DUBBIA)):
        z = d[~d['simbolo'].isin(togli)]
        e = tr.esame(z, 'r'); b = e['boot']
        print(f"  {tit:28s} n {b['eventi']:3d} media {100*b['media']:+.2f}% IC {100*b['basso']:+.2f};{100*b['alto']:+.2f} p {b['p']:.4f} metà {100*e['prima_meta']:+.2f}/{100*e['seconda_meta']:+.2f} senza5 {100*e['senza_5_migliori']:+.2f} -> {e['esito']}")
    print('  r degli eventi dubbi:', d[d['simbolo'].isin(NON_QUOTAZIONE + TGE + DATA_DUBBIA)][['simbolo', 'data', 'r']].round(3).to_dict('records'))
