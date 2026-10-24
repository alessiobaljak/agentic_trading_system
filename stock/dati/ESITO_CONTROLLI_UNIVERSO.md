# L'esito dei controlli dei prezzi: i 34 titoli dell'universo «di allora»

Scritto da `python -m stock.dati.scarica` il 24 ottobre 2026 in quattro gruppi in parallelo (dopo che una sola esecuzione era troppo lenta), prezzi di Alpaca dal 2016-01-01 al 2024-12-31, azioni societarie con le scissioni. Per 9 titoli lo scarto è quello già misurato con lo stesso metodo in `ESITO_CONTROLLI.md`. Solo conteggi e date: i prezzi restano in locale.

| Titolo | Barre al giorno | Frazionamenti | Dividendi | Problemi | Barre al minuto (dentro / fuori seduta) | Scarto mediano (90° perc.) |
|---|---|---|---|---|---|---|
| AAPL | 2264 | 1 | 36 | 0 | — | 0.81 (1.52) punti base su 532 fotografie (misura di ESITO_CONTROLLI.md) |
| AGN | 1095 | 0 | 14 | 1 | — | 4.35 (9.24) punti base su 265 fotografie |
| AMD | 2264 | 0 | 0 | 0 | — | 2.40 (14.40) punti base su 529 fotografie |
| AMZN | 2264 | 1 | 0 | 0 | — | 3.00 (7.16) punti base su 530 fotografie (misura di ESITO_CONTROLLI.md) |
| AVGO | 2264 | 1 | 36 | 0 | — | 5.75 (12.44) punti base su 531 fotografie (misura di ESITO_CONTROLLI.md) |
| BA | 2264 | 0 | 17 | 0 | — | 2.85 (6.45) punti base su 530 fotografie |
| BAC | 2264 | 0 | 36 | 0 | — | 3.42 (6.12) punti base su 530 fotografie |
| C | 2264 | 0 | 36 | 0 | — | 1.69 (2.47) punti base su 542 fotografie |
| CRM | 2264 | 0 | 3 | 0 | — | 2.83 (6.96) punti base su 530 fotografie |
| DHR | 2264 | 1 | 35 | 1 | — | 3.50 (9.70) punti base su 530 fotografie |
| FB | 1620 | 0 | 0 | 0 | — | 1.34 (2.96) punti base su 390 fotografie |
| GE | 2264 | 1 | 35 | 1 | — | 4.73 (12.51) punti base su 532 fotografie |
| GOOG | 2264 | 1 | 3 | 0 | — | 4.44 (9.69) punti base su 531 fotografie |
| GOOGL | 2264 | 1 | 3 | 0 | — | 4.36 (9.34) punti base su 530 fotografie (misura di ESITO_CONTROLLI.md) |
| INTC | 2264 | 0 | 35 | 0 | — | 2.14 (3.25) punti base su 533 fotografie |
| JNJ | 2264 | 0 | 36 | 0 | — | 1.37 (3.19) punti base su 530 fotografie |
| JPM | 2264 | 0 | 36 | 0 | — | 1.17 (2.29) punti base su 530 fotografie (misura di ESITO_CONTROLLI.md) |
| LLY | 2264 | 0 | 36 | 0 | — | 3.73 (10.16) punti base su 531 fotografie |
| META | 2264 | 0 | 4 | 0 | — | 1.56 (3.58) punti base su 535 fotografie (misura di ESITO_CONTROLLI.md) |
| MRNA | 1526 | 0 | 0 | 1 | — | 9.22 (26.97) punti base su 352 fotografie |
| MSFT | 2264 | 0 | 36 | 0 | — | 1.03 (1.88) punti base su 534 fotografie (misura di ESITO_CONTROLLI.md) |
| MU | 2264 | 0 | 13 | 0 | — | 2.37 (5.66) punti base su 530 fotografie |
| NFLX | 2264 | 0 | 0 | 1 | — | 4.21 (9.26) punti base su 531 fotografie |
| NVDA | 2264 | 2 | 36 | 1 | — | 2.62 (5.27) punti base su 532 fotografie (misura di ESITO_CONTROLLI.md) |
| PFE | 2264 | 0 | 36 | 0 | — | 2.76 (3.39) punti base su 530 fotografie |
| PG | 2264 | 0 | 36 | 0 | — | 1.28 (2.87) punti base su 530 fotografie |
| PLTR | 1070 | 0 | 0 | 0 | — | 6.11 (12.36) punti base su 250 fotografie |
| PYPL | 2264 | 0 | 0 | 0 | — | 2.34 (4.23) punti base su 531 fotografie |
| QCOM | 2264 | 0 | 37 | 0 | — | 1.89 (4.31) punti base su 530 fotografie |
| SMCI | 2264 | 1 | 0 | 3 | — | 20.06 (43.44) punti base su 415 fotografie |
| TSLA | 2264 | 2 | 0 | 0 | — | 3.60 (8.73) punti base su 532 fotografie (misura di ESITO_CONTROLLI.md) |
| V | 2264 | 0 | 36 | 0 | — | 1.38 (4.23) punti base su 541 fotografie |
| WFC | 2264 | 0 | 36 | 0 | — | 2.07 (3.39) punti base su 531 fotografie |
| XOM | 2264 | 0 | 36 | 0 | — | 1.30 (2.43) punti base su 531 fotografie |

## I problemi trovati

**AGN, salti** (1):
* 2019-06-25: salto — apertura/chiusura di ieri = 1.299 senza frazionamento

**DHR, rettifica dividendi** (1):
* 2016-01-04 → 2023-09-29: rettifica — 1949 giorni, differenza massima 0.1288
**GE, rettifica dividendi** (1):
* 2016-01-04 → 2024-04-01: rettifica — 2074 giorni, differenza massima 0.4048

**MRNA, salti** (1):
* 2020-05-18: salto — apertura/chiusura di ieri = 1.292 senza frazionamento

**NFLX, salti** (1):
* 2022-04-20: salto — apertura/chiusura di ieri = 0.704 senza frazionamento
**SMCI, salti** (3):
* 2020-01-14: salto — apertura/chiusura di ieri = 1.885 senza frazionamento
* 2024-10-30: salto — apertura/chiusura di ieri = 0.709 senza frazionamento
* 2024-11-19: salto — apertura/chiusura di ieri = 1.259 senza frazionamento
**NVDA, salti** (1):
* 2023-05-25: salto — apertura/chiusura di ieri = 1.261 senza frazionamento
