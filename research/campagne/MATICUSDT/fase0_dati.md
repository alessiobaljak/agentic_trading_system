# MATICUSDT — Fase 0, i dati della moneta

Scritto il 2026-10-09 dalla sessione di campagna (protocollo 4.5). Numeri da
`codice/fase0.py`, salvati in `fase0_misure.json`; impronte in `impronte.json`.

## Periodi (Fase 0 punto 1, scritti nel log prima di caricare i prezzi: voce `MATICUSDT-N002`)

| | |
|---|---|
| Primo mese di dati (scheda) | 2020-10 |
| Inizio (primo giorno del primo mese) | 2020-10-01 |
| Giorni dall'inizio al 2023-12-31 | 1187 |
| Costruzione | 830 giorni, dal 2020-10-01 al 2023-01-08 (`fine_costruzione_ts` = 1673222399999) |
| Validazione | dal 2023-01-09 al 2023-12-31 |

Il primo dato vero è del 2020-10-22 (07:00 UTC sul last a 15m, 00:00 sul giornaliero): i
primi 21 giorni del periodo non hanno candele. Le date sopra restano quelle della regola.

## File scaricati e impronte (Fase 0 punto 2)

* Fonte: data.binance.vision, file mensili da 2020-10 a 2023-12, solo fino al 2023-12-31.
* MATICUSDT: `klines` (last) e `markPriceKlines` (mark) su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h,
  1d; `fundingRate`. 741 file.
* BTCUSDT (solo riferimento di mercato): `klines` sugli stessi timeframe e mesi. 351 file.
* Tutti i 1092 file hanno il CHECKSUM remoto e l'impronta SHA-256 combacia (`codice/scarica.py`,
  rapporto: «esiti {'ok': 1092}»). Nessun mese assente.
* Le impronte di tutti i file sono in `impronte.json`; impronta di quel file:
  `c8b6a726b62460991da9b4f9d93f8eed6484fe589c69f89dbbd327e90f90a3d7`.
  A ogni nuova sessione i dati si riscaricano e si confrontano con queste impronte: se una
  cambia, STOP.

## Last e mark allineati (`carica_serie_allineate`)

Il last price non ha buchi dal primo dato al 2023-12-31 su nessun timeframe. Il mark price
manca in sei giornate intere, uguali su tutti i timeframe; più una barra isolata a 15m.
Queste barre del last si tolgono (intersezione) e diventano buchi per il motore:

| Timeframe | Barre last | Barre mark | Barre tenute | Barre last tolte | Barre mark tolte | Buchi nella serie tenuta |
|---|---|---|---|---|---|---|
| 15m | 111908 | 111141 | 111139 | 769 | 2 | 6 |
| 30m | 55954 | 55571 | 55570 | 384 | 1 | 5 |
| 1h | 27977 | 27786 | 27785 | 192 | 1 | 5 |
| 2h | 13989 | 13893 | 13893 | 96 | 0 | 5 |
| 4h | 6995 | 6947 | 6947 | 48 | 0 | 5 |
| 6h | 4663 | 4631 | 4631 | 32 | 0 | 5 |
| 8h | 3498 | 3474 | 3474 | 24 | 0 | 5 |
| 12h | 2332 | 2316 | 2316 | 16 | 0 | 5 |
| 1d | 1166 | 1158 | 1158 | 8 | 0 | 5 |

Barre del last tolte (mark assente), intervalli di date UTC:

* 2021-07-01 (giornata intera);
* dal 2021-07-24 al 2021-07-27 (quattro giornate intere);
* 2022-07-31 (giornata intera);
* 2022-10-02 (giornata intera);
* 2023-02-24 (giornata intera, periodo di validazione);
* solo a 15m: la barra 2023-11-10 03:45 (validazione).

Barre del mark tolte (last assente): la prima ora del 2020-10-22 (06:30 e 06:45 a 15m; 06:30 a
30m; 06:00 a 1h), prima del primo last.

BTCUSDT: nessun buco su nessun timeframe nel periodo (2020-10-01 → 2023-12-31).

## Sospensioni e cambi di contratto

Nessun cambio di contratto nel periodo in-sample: nessuna apertura oraria che si discosti
più del 20% dalla chiusura precedente (`salti_apertura_oltre_20pct_1h` vuoto), e il simbolo è
lo stesso per tutto il periodo. Nessuna sospensione nel last. Nessuna cucitura.

## Funding

3497 settlement dal 2020-10-22 08:00 al 2023-12-31 16:00 UTC, intervallo di 8 ore per tutto il
periodo (dichiarato nel file e confermato dalla distanza fra i settlement).

## Volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere del last)

| Anno | Volume medio giornaliero |
|---|---|
| 2020 (dal 22 ottobre) | 3,6 milioni |
| 2021 | 636 milioni |
| 2022 | 444 milioni |
| 2023 | 374 milioni |

La fascia di slippage della scheda (0,02% per lato) viene dal volume del 2023 (fra 200 milioni e
1 miliardo). Nel periodo di costruzione alcuni mesi stanno sotto i 200 milioni (2021-02: 94
milioni; 2021-03: 144 milioni; 2022-04: 189 milioni): lì la fascia vera sarebbe 0,05%, quindi
i costi del backtest sono ottimisti in quei mesi. Si dichiara; il test a costi doppi copre solo
in parte.

## Mesi sotto la liquidità minima (20 milioni di USDT al giorno)

2020-10 (1,6 milioni), 2020-11 (4,2), 2020-12 (3,7), 2021-01 (19,3).

**Filtro (uguale per `conta_trade`, per il test, per la baseline (a) e per la (b)):** nessuna
posizione si apre su un segnale di una barra il cui istante di apertura cade in uno di questi
quattro mesi (UTC). Le stesse barre sono vietate agli ingressi casuali della (b). Una posizione
già aperta esce con la sua uscita. In pratica le prime entrate possibili sono sui segnali dal
2021-02-01: il periodo di costruzione utile per gli ingressi va dal 2021-02-01 al 2023-01-08
(707 giorni). Le date di costruzione e validazione non si spostano.

## Storia utile

Dal 2021-02-01 (primo mese liquido) al 2023-12-31: circa 2 anni e 11 mesi, sopra
`storia_minima_anni` (2). La campagna prosegue.
