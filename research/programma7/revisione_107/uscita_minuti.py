import sys, os, urllib.request; sys.path.insert(0,'/tmp/revisore107')
from candele import *
from pathlib import Path
ev = pd.read_csv('/tmp/revisore107/eventi_finale.csv')
ev = ev[~ev.fermata & (ev.data >= '2024-01-01')].sort_values('r', ascending=False)
def scarica(s, giorno):
    p = f'/tmp/revisore107/min/{s}-{giorno}.zip'
    if not os.path.exists(p):
        u = f'https://data.binance.vision/data/futures/um/daily/klines/{s}/1m/{s}-1m-{giorno}.zip'
        try:
            with urllib.request.urlopen(u, timeout=60) as r: open(p, 'wb').write(r.read())
        except Exception: return None
    return p
out = []
for _, r in ev.head(15).iterrows():
    s = r.simbolo; hu = int(r.h_u); he = int(r.h_e)
    g = pd.Timestamp(hu*3600, unit='s').strftime('%Y-%m-%d')
    p = scarica(s, g)
    if p is None: print(s, 'no minuti'); continue
    m = m5._csv_da_zip(Path(p), m5.KLINE); m['t'] = m5._ms(m['open_time'])//60000
    m = m.set_index('t')[['open','high','low','close','quote_volume','volume']].astype(float)
    t = hu*60
    p0 = es.ore_di(s).loc[he,'open']
    vw = lambda a, b: (m.loc[a:b,'quote_volume'].sum() / m.loc[a:b,'volume'].sum())
    out.append(dict(simbolo=s, r=r.r, regola=m.loc[t,'open']/p0-1, vwap_5min_dopo=vw(t, t+4)/p0-1, vwap_60min_prima=vw(t-60, t-1)/p0-1, vwap_ultimi_30_prima_reduce=vw(t, t+29)/p0-1,
                    qv_primi5=m.loc[t:t+4,'quote_volume'].sum(), max_5min=m.loc[t:t+4,'high'].max()/p0-1, min_5min=m.loc[t:t+4,'low'].min()/p0-1))
d = pd.DataFrame(out); pd.set_option('display.width', 250)
print(d.round(3).to_string())
print(d.drop(columns='simbolo').mean().round(4))
