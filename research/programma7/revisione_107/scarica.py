import sys, os, urllib.request, pandas as pd
from concurrent.futures import ThreadPoolExecutor
ev = pd.read_csv('/tmp/revisore107/eventi_originali.csv')
lav = []
for _, r in ev.iterrows():
    mesi = sorted({pd.Timestamp(h*3600, unit='s').strftime('%Y-%m') for h in range(int(r.h_e)-48, int(r.h_u)+48, 6)})
    for m in mesi:
        s = r.simbolo
        lav.append((f"https://data.binance.vision/data/futures/um/monthly/indexPriceKlines/{s}/1h/{s}-1h-{m}.zip", f"/tmp/revisore107/idx/{s}-{m}.zip"))
        lav.append((f"https://data.binance.vision/data/futures/um/monthly/markPriceKlines/{s}/1h/{s}-1h-{m}.zip", f"/tmp/revisore107/mark/{s}-{m}.zip"))
        lav.append((f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip", f"/tmp/revisore107/fr/{s}-{m}.zip"))
def get(x):
    u, p = x
    if os.path.exists(p): return 'ok'
    try:
        with urllib.request.urlopen(u, timeout=60) as r: b = r.read()
        open(p, 'wb').write(b); return 'ok'
    except Exception as e:
        return f'ERR {u} {e}'
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, lav))
print(len(lav), sum(1 for r in res if r == 'ok'))
for r in res:
    if r != 'ok': print(r)
