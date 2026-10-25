import sys, os, urllib.request; sys.path.insert(0,'/tmp/revisore107')
from candele import *
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ev = pd.read_csv('/tmp/revisore107/eventi_finale.csv'); ev = ev[ev.data >= '2024-01-01']
def scarica(s, giorno):
    p = f'/tmp/revisore107/min/{s}-{giorno}.zip'
    if not os.path.exists(p):
        u = f'https://data.binance.vision/data/futures/um/daily/klines/{s}/1m/{s}-1m-{giorno}.zip'
        try:
            with urllib.request.urlopen(u, timeout=60) as r: open(p, 'wb').write(r.read())
        except Exception: return None
    return p
lav = [(r.simbolo, pd.Timestamp(int(r.h_e)*3600, unit='s').strftime('%Y-%m-%d')) for _, r in ev.iterrows()]
with ThreadPoolExecutor(8) as ex: ps = list(ex.map(lambda x: scarica(*x), lav))
out = []
for (_, r), p in zip(ev.iterrows(), ps):
    if p is None: continue
    m = m5._csv_da_zip(Path(p), m5.KLINE); m['t'] = m5._ms(m['open_time'])//60000
    m = m.set_index('t')[['open','high','low','close','quote_volume','volume']].astype(float)
    t = int(r.h_e)*60
    if t not in m.index: continue
    vw5 = m.loc[t:t+4,'quote_volume'].sum()/m.loc[t:t+4,'volume'].sum()
    out.append(dict(simbolo=r.simbolo, open=m.loc[t,'open'], scarto_vwap5=vw5/m.loc[t,'open']-1, qv5=m.loc[t:t+4,'quote_volume'].sum(), range1=m.loc[t,'high']/m.loc[t,'low']-1))
d = pd.DataFrame(out)
print(len(d)); print(d[['scarto_vwap5','qv5','range1']].describe(percentiles=[.1,.5,.9]).round(4))
