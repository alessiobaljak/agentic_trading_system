"""Per ogni evento: un altro libro Coinbase della stessa moneta (USDC, BTC, EUR, ...) aveva candele prima di L?"""
import json, time, urllib.request, datetime as dt
import pandas as pd
p = json.load(open('/tmp/revisore105/scaricati/prodotti.json'))
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv')
prim = json.load(open('/home/user/agentic_trading_system/research/data/coinbase/primi_giorni.json'))
per = {v['perpetuo']: b for b, v in prim.items()}
def candele(prod, a, b):
    url = f"https://api.exchange.coinbase.com/products/{prod}/candles?granularity=86400&start={a:%Y-%m-%dT00:00:00Z}&end={b:%Y-%m-%dT00:00:00Z}"
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as r:
                time.sleep(0.25)
                return json.loads(r.read())
        except Exception as e:
            time.sleep(2 + 2 * k)
    return None
out = []
for _, x in ev.iterrows():
    b = per[x['simbolo']]; L = dt.date(1970, 1, 1) + dt.timedelta(days=int(x['L']))
    for q in p:
        if q['base_currency'] != b or q['quote_currency'] == 'USD':
            continue
        prima = None
        fine = L
        for _ in range(3):           # fino a ~900 giorni prima, finestre di 299
            ini = fine - dt.timedelta(days=299)
            c = candele(q['id'], ini, fine - dt.timedelta(days=1))
            if c:
                prima = dt.date.fromtimestamp(min(r[0] for r in c))
                fine = prima
            else:
                break
        if prima:
            out.append((x['simbolo'], str(L), q['id'], str(prima), (L - prima).days))
for r in out:
    print(r)
print('fatto', len(out))
