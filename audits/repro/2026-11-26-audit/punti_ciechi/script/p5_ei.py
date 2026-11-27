import json, sys, collections, datetime as dt
d = sys.argv[1]
ei = json.load(open(d + '/exchangeInfo.json'))
t24 = {x['symbol']: x for x in json.load(open(d + '/t24.json'))}
prem = {x['symbol']: x for x in json.load(open(d + '/prem.json'))}
S = ei['symbols']
print('simboli', len(S))
print('contractType:', collections.Counter(s.get('contractType') for s in S))
print('underlyingType:', collections.Counter(s.get('underlyingType') for s in S))
print('status:', collections.Counter(s.get('status') for s in S))
def mese(s): return dt.datetime.utcfromtimestamp(s['onboardDate'] / 1000).strftime('%Y-%m')
# dal 1 ottobre 2026
dal = dt.datetime(2026, 10, 1).timestamp() * 1000
nuovi = [s for s in S if s['onboardDate'] >= dal]
print('\nnati dal 1 ottobre 2026:', len(nuovi))
for k, v in collections.Counter((s.get('contractType'), s.get('underlyingType'), s.get('quoteAsset')) for s in nuovi).items(): print('  ', k, v)
for s in nuovi:
    if s.get('underlyingType') == 'COIN' or s.get('contractType') not in ('TRADIFI_PERPETUAL',):
        print('    ', s['symbol'], s.get('contractType'), s.get('underlyingType'), s.get('quoteAsset'), s.get('status'), dt.datetime.utcfromtimestamp(s['onboardDate']/1000).date(), s.get('underlyingSubType'))
# per mese: perpetui su monete in USDT (PERPETUAL, COIN, USDT) contro tradfi
per = collections.defaultdict(lambda: collections.Counter())
for s in S:
    m = mese(s)
    if m < '2025-06': continue
    if s.get('contractType') == 'PERPETUAL' and s.get('underlyingType') == 'COIN' and s.get('quoteAsset') == 'USDT': k = 'moneta_USDT'
    elif s.get('contractType') == 'TRADIFI_PERPETUAL': k = 'tradfi'
    elif s.get('contractType') == 'PERPETUAL' and s.get('quoteAsset') == 'USDC': k = 'USDC'
    else: k = f"{s.get('contractType')}/{s.get('underlyingType')}/{s.get('quoteAsset')}"
    per[m][k] += 1
print('\nper mese (da giugno 2025), onboardDate dei simboli ANCORA in exchangeInfo:')
for m in sorted(per): print('  ', m, dict(per[m]))
# volumi 24 ore
tradfi = [s['symbol'] for s in S if s.get('contractType') == 'TRADIFI_PERPETUAL']
usdt_perp = [s['symbol'] for s in S if s.get('quoteAsset') == 'USDT' and s.get('contractType') in ('PERPETUAL', 'TRADIFI_PERPETUAL')]
vol = lambda xs: sum(float(t24[x]['quoteVolume']) for x in xs if x in t24)
print('\ntradfi', len(tradfi), 'in TRADING', sum(1 for s in S if s.get('contractType') == 'TRADIFI_PERPETUAL' and s['status'] == 'TRADING'))
print('volume 24h tradfi (mld)', round(vol(tradfi) / 1e9, 2), 'perpetui USDT totali (mld)', round(vol(usdt_perp) / 1e9, 2), 'quota', round(vol(tradfi) / vol(usdt_perp), 3))
print('tradfi sopra 50 milioni:', sum(1 for x in tradfi if x in t24 and float(t24[x]['quoteVolume']) > 5e7))
print('tradfi underlyingType:', collections.Counter(s.get('underlyingType') for s in S if s.get('contractType') == 'TRADIFI_PERPETUAL'))
print('tradfi underlyingSubType:', collections.Counter(tuple(s.get('underlyingSubType') or []) for s in S if s.get('contractType') == 'TRADIFI_PERPETUAL').most_common(8))
import statistics
fr = [float(prem[x]['lastFundingRate']) for x in tradfi if x in prem]
print('funding tradfi: n', len(fr), 'mediana', statistics.median(fr), 'quota > 0,01%', round(sum(1 for f in fr if f > 0.0001) / len(fr), 3))
print('primo tradfi:', min(dt.datetime.utcfromtimestamp(s['onboardDate']/1000).date() for s in S if s.get('contractType') == 'TRADIFI_PERPETUAL'))
