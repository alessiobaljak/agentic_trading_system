import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import ventunesima as vu, trentesima as tr

def boot(d, col='r', chiave='annuncio'):
    x = d.copy(); x['annuncio'] = x[chiave]
    return vu.bootstrap_annunci(x, col)

for nome, f in (('originale (91)', '/home/user/agentic_trading_system/research/programma7/risultati_quarantatreesima/eventi_CB.csv'),
                ('completo (105)', '/tmp/revisore105/eventi_rifatti.csv')):
    d = pd.read_csv(f)
    d['mese'] = d['data'].str[:7]
    d['trimestre'] = d['data'].str[:4] + 'Q' + ((d['data'].str[5:7].astype(int) - 1) // 3 + 1).astype(str)
    d['anno'] = d['data'].str[:4]
    print('=====', nome)
    for k in ('annuncio', 'mese', 'trimestre'):
        b = boot(d, chiave=k)
        print(f'  bootstrap per {k}: media {100*b["media"]:+.2f}% IC {100*b["basso"]:+.2f};{100*b["alto"]:+.2f} p {b["p"]:.4f} gruppi {b["annunci"]}')
    # t semplice e t per settimana
    w = d.groupby('annuncio')['r'].mean()
    print(f'  t per evento {d.r.mean()/d.r.std()*np.sqrt(len(d)):.2f}; t sulle medie per settimana {w.mean()/w.std()*np.sqrt(len(w)):.2f} ({len(w)} settimane)')
    for a in sorted(d['anno'].unique()):
        z = d[d['anno'] != a]; b = boot(z)
        print(f'  senza {a}: n {len(z)} media {100*z.r.mean():+.2f}% p {b["p"]:.4f}')
    z = d[~d['anno'].isin(['2024', '2025'])]; b = boot(z)
    print(f'  senza 2024 e 2025: n {len(z)} media {100*z.r.mean():+.2f}% p {b["p"]:.4f}')
    n_w = d.groupby('annuncio')['r'].transform('size')
    n_g = d.groupby('data')['r'].transform('size')
    print('  settimane con >=3 eventi:', (d.groupby('annuncio').size() >= 3).sum(), 'eventi in esse', int((n_w >= 3).sum()))
    z = d[n_w < 3]; b = boot(z)
    print(f'  senza le settimane con 3+ eventi: n {len(z)} media {100*z.r.mean():+.2f}% p {b["p"]:.4f}')
    z = d[n_g == 1]; b = boot(z)
    print(f'  solo i giorni con un evento: n {len(z)} media {100*z.r.mean():+.2f}% p {b["p"]:.4f}')
    # un evento per settimana: la media della settimana
    print(f'  media delle medie settimanali {100*w.mean():+.2f}%')
    s = d.sort_values('r', ascending=False)
    for k in (3, 5, 10):
        print(f'  senza i {k} migliori {100*s.r.iloc[k:].mean():+.2f}%  (p {boot(s.iloc[k:])["p"]:.4f})')
    # metà per data
    dd = d.sort_values('data'); m = len(dd) // 2
    print(f'  metà: {100*dd.r.iloc[:m].mean():+.2f}% , {100*dd.r.iloc[m:].mean():+.2f}%')
    # dal 2026-01-01 in poi
    z = d[d['data'] >= '2025-10-01']
    print(f'  ultimi 12 mesi (da 2025-10): n {len(z)} media {100*z.r.mean():+.2f}%')
    # quanto pesa il lato bitcoin: rendimento senza stop
