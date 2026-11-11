# Programma 7 — risultati dell'ottantasettesima prova (prova 149: la 1:1:1)

Regole in `OTTANTASETTESIMA.md` (scritte e committate prima del calcolo, commit 07d171e). Codice: `ottantasettesima.py`; dati completi: `risultati_ottantasettesima/risultati.json`; registro delle 60 combinazioni: `research/trials/ottantasettesima.csv`.

## Le 10 monete (scelte con il volume del 2023, scritte prima di calcolare le strategie)

Volume medio giornaliero 2023 in USDT = somma dei volumi del 2023 / 365 (tabella del programma 6, perpetui di Binance). Nessuno stablecoin o contratto non-moneta fra i primi 14.

| # | moneta | volume medio al giorno | giorni con volume nel 2023 |
|---|---|---|---|
| 1 | BTCUSDT | 11,505 milioni | 365 |
| 2 | ETHUSDT | 5,513 milioni | 365 |
| 3 | SOLUSDT | 1,104 milioni | 365 |
| 4 | XRPUSDT | 811 milioni | 365 |
| 5 | DOGEUSDT | 519 milioni | 365 |
| 6 | APTUSDT | 410 milioni | 365 |
| 7 | BNBUSDT | 401 milioni | 365 |
| 8 | LTCUSDT | 382 milioni | 365 |
| 9 | MATICUSDT | 374 milioni | 365 |
| 10 | BCHUSDT | 339 milioni | 365 |
| 11 (fuori) | OPUSDT | 330 milioni | 365 |
| 12 (fuori) | ARBUSDT | 324 milioni | 284 |
| 13 (fuori) | LINKUSDT | 319 milioni | 365 |
| 14 (fuori) | 1000PEPEUSDT | 301 milioni | 241 |

## Letture scelte dove le regole lasciano margine (da confermare)

* massimo e minimo «delle barre» (strategia B) = massimo dell'alto e minimo del basso delle candele; la chiusura si confronta con questi.
* RSI di Wilder a 14 barre (media mobile con alfa 1/14). Nella C, se nella stessa barra il comprato si chiude (RSI sopra 50) e l'RSI è sopra 70, si apre il venduto.
* Nella A, se la chiusura è uguale alla media si tiene la posizione di prima; la posizione comincia dopo 50 chiusure.
* Il volume medio 2023 è la somma/365 (con i giorni con dati, le monete nate nel 2023 con poche settimane di volume salirebbero in cima).
* Operazione = entrata in una posizione (un rovesciamento da comprato a venduto vale 1 operazione e 2 lati di costo).
* Funding: somma giornaliera del pannello del programma 6, divisa in parti uguali fra le barre del giorno, moltiplicata per la posizione.
* Barre a 4 ore dalle candele mensili a 1 ora dell'archivio di Binance (`quarta.ore`, scaricate con `programma6.scarico_ore`); a 1 giorno dal pannello giornaliero. La storia prima del 2021 serve solo per gli indicatori.
* Il rendimento l'anno e lo Sharpe sono sulle somme settimanali (lunedì-domenica) come le altre prove; settimane intere fra il 1° gennaio 2021 e il 31 ottobre 2026, o dalla prima candela. Il 2026 è parziale (10 mesi); l'anno di nascita di una moneta nata dopo il 2021 pure.
* Sharpe corretto (probabilità, `terza.sharpe_corretto`, 52 settimane): N = 306; la varianza fra le prove viene dagli Sharpe dei 69 gruppi del conto (`asticella`) più le 60 combinazioni. Per capire, nel file `risultati.json` c'è anche lo stesso calcolo con i soli gruppi (`sharpe_corretto_solo_gruppi`).

## Le 60 combinazioni

| moneta | int. | str. | rend. l'anno | Sharpe | anni positivi | t | Sharpe corretto | operazioni | discesa | esito del filtro |
|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | 4h | A | -11.6% | -0.20 | 2/6 | -0.49 | 0.00 | 883 | -84.9% | non passa: netto non positivo; anni positivi 2/6; t -0.49 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BTCUSDT | 4h | B | +6.5% | 0.13 | 3/6 | 0.31 | 0.00 | 339 | -70.1% | non passa: anni positivi 3/6; t 0.31 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BTCUSDT | 4h | C | -22.9% | -0.59 | 1/6 | -1.43 | 0.00 | 189 | -87.8% | non passa: netto non positivo; anni positivi 1/6; t -1.43 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BTCUSDT | 1d | A | +34.4% | 0.65 | 5/6 | 1.56 | 0.01 | 121 | -59.1% | non passa: anni positivi 5/6; t 1.56 sotto 3; Sharpe corretto 0.01 sotto 0,80 |
| BTCUSDT | 1d | B | +1.8% | 0.04 | 4/6 | 0.08 | 0.00 | 60 | -73.6% | non passa: anni positivi 4/6; t 0.08 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BTCUSDT | 1d | C | -7.7% | -0.23 | 2/6 | -0.55 | 0.00 | 31 | -67.5% | non passa: netto non positivo; anni positivi 2/6; t -0.55 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| ETHUSDT | 4h | A | +10.1% | 0.14 | 4/6 | 0.33 | 0.00 | 905 | -72.1% | non passa: anni positivi 4/6; t 0.33 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| ETHUSDT | 4h | B | -7.6% | -0.12 | 3/6 | -0.28 | 0.00 | 343 | -88.7% | non passa: netto non positivo; anni positivi 3/6; t -0.28 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| ETHUSDT | 4h | C | -40.7% | -0.90 | 0/6 | -2.18 | 0.00 | 186 | -95.6% | non passa: netto non positivo; anni positivi 0/6; t -2.18 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| ETHUSDT | 1d | A | +46.2% | 0.67 | 5/6 | 1.63 | 0.01 | 107 | -64.1% | non passa: anni positivi 5/6; t 1.63 sotto 3; Sharpe corretto 0.01 sotto 0,80 |
| ETHUSDT | 1d | B | +8.7% | 0.14 | 4/6 | 0.33 | 0.00 | 60 | -86.6% | non passa: anni positivi 4/6; t 0.33 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| ETHUSDT | 1d | C | -29.7% | -0.60 | 2/6 | -1.45 | 0.00 | 26 | -89.9% | non passa: netto non positivo; anni positivi 2/6; t -1.45 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| SOLUSDT | 4h | A | +62.5% | 0.60 | 4/6 | 1.44 | 0.00 | 867 | -77.2% | non passa: anni positivi 4/6; t 1.44 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| SOLUSDT | 4h | B | +7.3% | 0.07 | 3/6 | 0.18 | 0.00 | 352 | -91.2% | non passa: anni positivi 3/6; t 0.18 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| SOLUSDT | 4h | C | -34.1% | -0.50 | 1/6 | -1.21 | 0.00 | 190 | -97.4% | non passa: netto non positivo; anni positivi 1/6; t -1.21 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| SOLUSDT | 1d | A | +106.2% | 1.00 | 4/6 | 2.42 | 0.06 | 116 | -88.5% | non passa: anni positivi 4/6; t 2.42 sotto 3; Sharpe corretto 0.06 sotto 0,80 |
| SOLUSDT | 1d | B | +65.1% | 0.69 | 3/6 | 1.66 | 0.01 | 61 | -89.6% | non passa: anni positivi 3/6; t 1.66 sotto 3; Sharpe corretto 0.01 sotto 0,80 |
| SOLUSDT | 1d | C | -74.3% | -0.94 | 3/6 | -2.28 | 0.00 | 30 | -99.8% | non passa: netto non positivo; anni positivi 3/6; t -2.28 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| XRPUSDT | 4h | A | +26.0% | 0.27 | 5/6 | 0.66 | 0.00 | 924 | -95.9% | non passa: anni positivi 5/6; t 0.66 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| XRPUSDT | 4h | B | +10.6% | 0.12 | 4/6 | 0.28 | 0.00 | 325 | -91.6% | non passa: anni positivi 4/6; t 0.28 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| XRPUSDT | 4h | C | -19.1% | -0.27 | 4/6 | -0.66 | 0.00 | 193 | -97.5% | non passa: netto non positivo; anni positivi 4/6; t -0.66 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| XRPUSDT | 1d | A | -11.2% | -0.11 | 3/6 | -0.27 | 0.00 | 144 | -99.0% | non passa: netto non positivo; anni positivi 3/6; t -0.27 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| XRPUSDT | 1d | B | +13.6% | 0.16 | 3/6 | 0.38 | 0.00 | 55 | -86.9% | non passa: anni positivi 3/6; t 0.38 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| XRPUSDT | 1d | C | -6.4% | -0.10 | 5/6 | -0.24 | 0.00 | 27 | -94.2% | non passa: netto non positivo; anni positivi 5/6; t -0.24 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| DOGEUSDT | 4h | A | +73.4% | 0.49 | 4/6 | 1.17 | 0.00 | 945 | -96.2% | non passa: anni positivi 4/6; t 1.17 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| DOGEUSDT | 4h | B | +50.8% | 0.39 | 3/6 | 0.94 | 0.00 | 319 | -92.5% | non passa: anni positivi 3/6; t 0.94 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| DOGEUSDT | 4h | C | -65.9% | -0.57 | 3/6 | -1.38 | 0.00 | 182 | -132.1% | non passa: netto non positivo; anni positivi 3/6; t -1.38 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| DOGEUSDT | 1d | A | +126.6% | 0.59 | 4/6 | 1.43 | 0.00 | 121 | -96.4% | non passa: anni positivi 4/6; t 1.43 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| DOGEUSDT | 1d | B | +44.8% | 0.36 | 3/6 | 0.86 | 0.00 | 51 | -95.6% | non passa: anni positivi 3/6; t 0.86 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| DOGEUSDT | 1d | C | -42.6% | -0.39 | 2/6 | -0.94 | 0.00 | 33 | -112.0% | non passa: netto non positivo; anni positivi 2/6; t -0.94 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| APTUSDT | 4h | A | +24.9% | 0.25 | 2/5 | 0.50 | 0.00 | 568 | -91.0% | non passa: anni positivi 2/5; t 0.50 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| APTUSDT | 4h | B | -2.7% | -0.03 | 3/5 | -0.06 | 0.00 | 251 | -94.9% | non passa: netto non positivo; anni positivi 3/5; t -0.06 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| APTUSDT | 4h | C | -25.2% | -0.38 | 1/5 | -0.77 | 0.00 | 131 | -91.8% | non passa: netto non positivo; anni positivi 1/5; t -0.77 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| APTUSDT | 1d | A | +28.0% | 0.31 | 3/5 | 0.63 | 0.00 | 105 | -85.3% | non passa: anni positivi 3/5; t 0.63 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| APTUSDT | 1d | B | -23.8% | -0.29 | 1/5 | -0.58 | 0.00 | 46 | -94.7% | non passa: netto non positivo; anni positivi 1/5; t -0.58 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| APTUSDT | 1d | C | -11.1% | -0.17 | 3/5 | -0.34 | 0.00 | 22 | -87.1% | non passa: netto non positivo; anni positivi 3/5; t -0.34 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BNBUSDT | 4h | A | +26.3% | 0.29 | 4/6 | 0.70 | 0.00 | 811 | -90.6% | non passa: anni positivi 4/6; t 0.70 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BNBUSDT | 4h | B | +17.3% | 0.22 | 3/6 | 0.53 | 0.00 | 336 | -88.7% | non passa: anni positivi 3/6; t 0.53 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BNBUSDT | 4h | C | -35.1% | -0.52 | 1/6 | -1.25 | 0.00 | 182 | -99.3% | non passa: netto non positivo; anni positivi 1/6; t -1.25 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BNBUSDT | 1d | A | +78.2% | 0.91 | 5/6 | 2.20 | 0.02 | 143 | -59.4% | non passa: anni positivi 5/6; t 2.20 sotto 3; Sharpe corretto 0.02 sotto 0,80 |
| BNBUSDT | 1d | B | +45.0% | 0.54 | 4/6 | 1.30 | 0.00 | 53 | -81.3% | non passa: anni positivi 4/6; t 1.30 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BNBUSDT | 1d | C | -33.4% | -0.46 | 3/6 | -1.10 | 0.00 | 32 | -100.3% | non passa: netto non positivo; anni positivi 3/6; t -1.10 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| LTCUSDT | 4h | A | -60.3% | -0.67 | 1/6 | -1.62 | 0.00 | 1025 | -99.9% | non passa: netto non positivo; anni positivi 1/6; t -1.62 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| LTCUSDT | 4h | B | -49.6% | -0.69 | 0/6 | -1.68 | 0.00 | 366 | -99.0% | non passa: netto non positivo; anni positivi 0/6; t -1.68 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| LTCUSDT | 4h | C | +16.4% | 0.32 | 3/6 | 0.78 | 0.00 | 182 | -68.0% | non passa: anni positivi 3/6; t 0.78 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| LTCUSDT | 1d | A | -55.8% | -0.69 | 1/6 | -1.67 | 0.00 | 183 | -99.6% | non passa: netto non positivo; anni positivi 1/6; t -1.67 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| LTCUSDT | 1d | B | -33.8% | -0.49 | 1/6 | -1.17 | 0.00 | 59 | -98.3% | non passa: netto non positivo; anni positivi 1/6; t -1.17 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| LTCUSDT | 1d | C | +29.9% | 0.68 | 4/6 | 1.65 | 0.01 | 31 | -39.2% | non passa: anni positivi 4/6; t 1.65 sotto 3; Sharpe corretto 0.01 sotto 0,80 |
| MATICUSDT | 4h | A | +56.3% | 0.41 | 4/4 | 0.79 | 0.01 | 558 | -140.9% | non passa: t 0.79 sotto 3; Sharpe corretto 0.01 sotto 0,80 |
| MATICUSDT | 4h | B | +48.6% | 0.42 | 4/4 | 0.81 | 0.01 | 213 | -93.8% | non passa: t 0.81 sotto 3; Sharpe corretto 0.01 sotto 0,80 |
| MATICUSDT | 4h | C | -48.9% | -0.63 | 1/4 | -1.21 | 0.00 | 122 | -94.0% | non passa: netto non positivo; anni positivi 1/4; t -1.21 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| MATICUSDT | 1d | A | +96.0% | 0.66 | 2/4 | 1.28 | 0.03 | 100 | -99.0% | non passa: anni positivi 2/4; t 1.28 sotto 3; Sharpe corretto 0.03 sotto 0,80 |
| MATICUSDT | 1d | B | +122.5% | 1.04 | 3/4 | 2.00 | 0.10 | 35 | -73.1% | non passa: anni positivi 3/4; t 2.00 sotto 3; Sharpe corretto 0.10 sotto 0,80 |
| MATICUSDT | 1d | C | -54.9% | -0.60 | 2/4 | -1.15 | 0.00 | 22 | -99.4% | non passa: netto non positivo; anni positivi 2/4; t -1.15 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BCHUSDT | 4h | A | -1.6% | -0.02 | 4/6 | -0.04 | 0.00 | 974 | -99.4% | non passa: netto non positivo; anni positivi 4/6; t -0.04 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BCHUSDT | 4h | B | +14.2% | 0.16 | 4/6 | 0.38 | 0.00 | 345 | -93.5% | non passa: anni positivi 4/6; t 0.38 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BCHUSDT | 4h | C | -33.4% | -0.50 | 1/6 | -1.20 | 0.00 | 184 | -98.4% | non passa: netto non positivo; anni positivi 1/6; t -1.20 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BCHUSDT | 1d | A | -19.0% | -0.20 | 2/6 | -0.49 | 0.00 | 192 | -98.2% | non passa: netto non positivo; anni positivi 2/6; t -0.49 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BCHUSDT | 1d | B | -6.7% | -0.08 | 2/6 | -0.20 | 0.00 | 60 | -92.8% | non passa: netto non positivo; anni positivi 2/6; t -0.20 sotto 3; Sharpe corretto 0.00 sotto 0,80 |
| BCHUSDT | 1d | C | +2.0% | 0.03 | 2/6 | 0.08 | 0.00 | 28 | -94.5% | non passa: anni positivi 2/6; t 0.08 sotto 3; Sharpe corretto 0.00 sotto 0,80 |

## Esito: passano il filtro 0 combinazioni su 60.


Non è un giudizio di credibilità: chi passa va a backtest-auditor.

## Note sul calcolo

* Il registro `research/trials/ottantasettesima.csv` ha 24 righe di «errore» (le prime 24 combinazioni a 4 ore, scritte alle 12:45) e poi le 60 righe
  del calcolo valido: il primo tentativo è fallito perché le candele a 1 ora del 2021-2025 non erano nella cartella `p6h` (c'erano solo 8 giorni). I
  dati sono stati scaricati con `python3 -m research.programma6.scarico_ore` (archivio pubblico di Binance, con verifica), poi il calcolo è stato rifatto
  per intero con le stesse regole. Le righe di errore non si cancellano; le 60 valide sono le ultime per ogni identificativo.
* Buchi nelle candele a 1 ora: SOL, XRP e LTC mancano di 120 ore in totale (5 giorni nel 2022); le barre a 4 ore incomplete sono scartate.
* MATIC: il perpetuo ha dati fino a settembre 2024 (4 anni, 2021-2024); APT nasce a ottobre 2022 (anni 2022-2026).
* Con la varianza dei soli gruppi del conto (senza le 60 combinazioni) l'esito del filtro non cambia (nessuna passa).
