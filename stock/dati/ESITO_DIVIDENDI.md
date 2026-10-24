# Dividendi e frazionamenti: Alpaca contro Yahoo

Scritto da `python -m stock.dati.yahoo` il 2026-10-24 11:24 UTC, dal 2016-01-01 al 2024-12-31. Gli importi di Yahoo sono riportati a quelli di allora (moltiplicati per i frazionamenti successivi); tolleranza 1%.

| Titolo | Dividendi Alpaca | Dividendi Yahoo | Frazionamenti uguali | Differenze |
|---|---|---|---|---|
| SPY | 33 | 36 | sì | 3 |
| QQQ | 37 | 36 | sì | 1 |
| AAPL | 36 | 36 | sì | 0 |
| MSFT | 36 | 36 | sì | 0 |
| NVDA | 36 | 36 | sì | 0 |
| GOOGL | 3 | 3 | sì | 0 |
| AMZN | 0 | 0 | sì | 0 |
| META | 4 | 4 | sì | 0 |
| TSLA | 0 | 0 | sì | 0 |
| AVGO | 36 | 36 | sì | 2 |
| BRK.B | 0 | 0 | sì | 0 |
| JPM | 36 | 36 | sì | 0 |

## Le differenze

* SPY, 2016-03-18: manca a noi (Alpaca —, Yahoo 1.0500) → aggiunto a mano (`integrazioni.py`)
* SPY, 2018-06-15: manca a noi (Alpaca —, Yahoo 1.2460) → aggiunto a mano (`integrazioni.py`)
* SPY, 2024-12-20: manca a noi (Alpaca —, Yahoo 1.9660) → aggiunto a mano (`integrazioni.py`)
* QQQ, 2020-09-21: manca a loro (Alpaca 0.3882, Yahoo —)
* AVGO, 2018-03-21: importo diverso (Alpaca 1.7500, Yahoo 3.5000)
* AVGO, 2018-06-19: importo diverso (Alpaca 1.7500, Yahoo 3.5000)
