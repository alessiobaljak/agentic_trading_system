# L'esito dei controlli dei prezzi

Scritto da `python -m stock.dati.scarica` il 2026-10-24 09:40 UTC, prezzi di Alpaca (tutte le borse americane, feed «sip») dal 2016-01-01 al 2024-12-31. Solo conteggi e date: i prezzi restano in locale.

| Titolo | Barre al giorno | Frazionamenti | Dividendi | Problemi | Barre al minuto (dentro / fuori seduta) | Scarto mediano (90° perc.) |
|---|---|---|---|---|---|---|
| SPY | 2264 | 0 | 33 | 2 | — | 0.37 (0.53) punti base su 541 fotografie |
| QQQ | 2264 | 0 | 37 | 0 | — | 0.56 (0.92) punti base su 537 fotografie |
| AAPL | 2264 | 1 | 36 | 0 | — | 0.81 (1.52) punti base su 532 fotografie |
| MSFT | 2264 | 0 | 36 | 0 | — | 1.03 (1.88) punti base su 534 fotografie |
| NVDA | 2264 | 2 | 36 | 1 | — | 2.62 (5.27) punti base su 532 fotografie |
| GOOGL | 2264 | 1 | 3 | 0 | — | 4.36 (9.34) punti base su 530 fotografie |
| AMZN | 2264 | 1 | 0 | 0 | — | 3.00 (7.16) punti base su 530 fotografie |
| META | 2264 | 0 | 4 | 0 | — | 1.56 (3.58) punti base su 535 fotografie |
| TSLA | 2264 | 2 | 0 | 0 | — | 3.60 (8.73) punti base su 532 fotografie |
| AVGO | 2264 | 1 | 36 | 0 | — | 5.75 (12.44) punti base su 531 fotografie |
| BRK.B | 2264 | 0 | 0 | 0 | — | 2.47 (5.67) punti base su 530 fotografie |
| JPM | 2264 | 0 | 36 | 0 | — | 1.17 (2.29) punti base su 530 fotografie |

## I problemi trovati

**SPY, rettifica dividendi** (1):
* 2016-01-04 → 2024-12-19: rettifica — 2257 giorni, differenza massima 0.0034

**SPY, cadenza dividendi** (1):
* 2018-03-16 → 2018-09-21: dividendo mancante? — 189 giorni fra due dividendi, di solito 91

**NVDA, salti** (1):
* 2023-05-25: salto — apertura/chiusura di ieri = 1.261 senza frazionamento

