"""Cinque operazioni rifatte a mano dagli zip orari grezzi (open/high) e dal funding grezzo di Binance."""
import sys, glob
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from datetime import datetime, timezone
from research.programma6 import quarta as qa, seconda as sc, ventunesima as vu, esecuzione as es
from research.programma5.strumenti import motore5 as m5
from research.src.dati import funding_da_zip
from research.programma6.motore import TAKER
print('TAKER', TAKER, 'costo moneta', vu.COSTO_MONETA, 'costo btc', vu.COSTO_BTC)
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv').set_index('simbolo')
def fund(s):
    righe = []
    for p in sorted((sc.DATI / s / 'funding').glob('*.zip')):
        righe += funding_da_zip(p)
    return pd.DataFrame(righe, columns=['ts', 'ore', 'tasso']).drop_duplicates('ts')
btc = qa.ore('BTCUSDT')
fbtc = fund('BTCUSDT')
for s in ('PUMPUSDT', 'MORPHOUSDT', 'PNUTUSDT', 'AVAXUSDT', 'MONUSDT', 'SENTUSDT'):
    x = ev.loc[s]
    g0 = int(x['L']) + 1; h0 = g0 * 24; h1 = h0 + 168
    c = qa.ore(s)
    p0 = c.loc[h0, 'open']; b0 = btc.loc[h0, 'open']
    tr_ = c.loc[h0:h1 - 1]
    sopra = tr_.index[tr_['high'] >= 1.3 * p0]
    if len(sopra):
        uh = int(sopra[0]); pc = 1.3 * 1.01 * p0; pb = btc.loc[uh, 'close']; fine_ms = (uh + 1) * 3600_000
    else:
        uh = h1; pc = c.loc[h1, 'open']; pb = btc.loc[h1, 'open']; fine_ms = h1 * 3600_000
    f = fund(s)
    ini_ms = h0 * 3600_000
    # funding pagato fra l'entrata (esclusa) e l'uscita (inclusa) — la convenzione «tocca chi tiene il giorno (m-1)//1440»
    fc = f[(f.ts > ini_ms) & (f.ts <= fine_ms)]['tasso'].sum()
    fb = fbtc[(fbtc.ts > ini_ms) & (fbtc.ts <= fine_ms)]['tasso'].sum()
    r = (pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fb
    print(f"{s} entrata {datetime.fromtimestamp(h0*3600, timezone.utc):%Y-%m-%d %H:%M} p0 {p0:.6g} b0 {b0:.6g} uscita {datetime.fromtimestamp(uh*3600, timezone.utc):%Y-%m-%d %H:%M} pc {pc:.6g} pb {pb:.6g}"
          f" moneta {100*(pc/p0-1):+.2f}% btc {100*(pb/b0-1):+.2f}% funding moneta {100*fc:+.3f}% btc {100*fb:+.3f}% -> r {100*r:+.2f}% | codice {100*x['r']:+.2f}%")
