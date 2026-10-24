# L'esito dei controlli dei prezzi

Scritto da `python -m stock.dati.scarica` il 2026-10-24 10:01 UTC, prezzi di Alpaca (tutte le borse americane, feed «sip») dal 2016-01-01 al 2024-12-31. Solo conteggi e date: i prezzi restano in locale.

| Titolo | Barre al giorno | Frazionamenti | Dividendi | Problemi | Barre al minuto (dentro / fuori seduta) | Scarto mediano (90° perc.) |
|---|---|---|---|---|---|---|
| SPY | 2264 | 0 | 33 | 3 | 879616 / 894740 | — |
| QQQ | 2264 | 0 | 37 | 1 | 879605 / 805744 | — |

## I problemi trovati

**SPY, rettifica dividendi** (1):
* 2016-01-04 → 2024-12-19: rettifica — 2257 giorni, differenza massima 0.0034

**SPY, cadenza dividendi** (1):
* 2018-03-16 → 2018-09-21: dividendo mancante? — 189 giorni fra due dividendi, di solito 91

**SPY, minuti** (1):
* 2019-08-12: minuti mancanti — 360 minuti su 390 nella seduta

**QQQ, minuti** (1):
* 2016-02-22: minuti mancanti — 340 minuti su 390 nella seduta

