import sys, os, urllib.request; sys.path.insert(0,'/tmp/revisore107')
from candele import *
from pathlib import Path
ev = pd.read_csv('/tmp/revisore107/eventi_corretti.csv')
st = ev[ev.fermata]
def scarica(s, giorno):
    p = f'/tmp/revisore107/min/{s}-{giorno}.zip'
    if not os.path.exists(p):
        u = f'https://data.binance.vision/data/futures/um/daily/klines/{s}/1m/{s}-1m-{giorno}.zip'
        try:
            with urllib.request.urlopen(u, timeout=60) as r: open(p, 'wb').write(r.read())
        except Exception as e:
            return None
    return p
for _, r in st.iterrows():
    s = r.simbolo; he = int(r.h_e); hs = he + int(r.ore)
    c = es.ore_di(s); p0 = c.loc[he, 'open']; liv = p0 * 1.30
    g = pd.Timestamp(hs*3600, unit='s').strftime('%Y-%m-%d')
    p = scarica(s, g)
    if p is None: print(s, 'niente minuti', g); continue
    m = m5._csv_da_zip(Path(p), m5.KLINE); m['t'] = m5._ms(m['open_time'])//60000
    m = m[['t','open','high','low','close','quote_volume']].astype(float)
    m = m[(m.t >= hs*60) & (m.t < hs*60+60)]
    x = m[m.high >= liv]
    if x.empty: print(s, 'nessun minuto sopra il livello'); continue
    k = x.iloc[0]
    # realistic stop fill: if the minute opens above the level, fill at open (gap); otherwise at the level; then compare with the rule's p0*1.3*1.01
    fill = max(k.open, liv)
    nxt = m[m.t > k.t].head(1)
    print(f"{s:14s} stop {pd.Timestamp(k.t*60, unit='s')} livello {liv:.6g} minuto open {k.open:.6g} high {k.high:.6g} close {k.close:.6g} qv {k.quote_volume:,.0f} | stima riempimento {fill/p0-1:+.3f} (regola +0.313) | ora high {c.loc[hs,'high']/p0-1:+.3f}")
