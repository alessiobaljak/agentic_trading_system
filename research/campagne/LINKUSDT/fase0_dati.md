# LINKUSDT — Fase 0: i dati

Scritto il 9 ottobre 2026 dalla sessione di campagna (protocollo 4.5). Numeri da
`codice/fase0.py` (rapporto completo in `data/insample/LINKUSDT/fase0_rapporto.json`, fuori da git).

## Periodi (Fase 0 punto 1, scritti nel log prima di caricare i prezzi: voce LINKUSDT-N003)

| | Valore |
|---|---|
| Primo mese di dati (scheda) | 2020-01 |
| Inizio in-sample | 2020-01-01 (prima barra presente nei file: 2020-01-17 08:00 UTC) |
| Costruzione | 2020-01-01 → 2022-10-18 (1022 giorni; `fine_costruzione_ts` 1666137599999) |
| Validazione | 2022-10-19 → 2023-12-31 |

L'archivio parte dal 2020-01-17 08:00 UTC (i file di gennaio 2020 cominciano lì): i primi 16 giorni
del periodo non hanno dati. Le date di costruzione e validazione restano quelle calcolate dal primo
mese (regola della Fase 0); la differenza si dichiara qui.

## Fonte e file

* data.binance.vision, file mensili da 2020-01 a 2023-12: klines (last) e markPriceKlines sui nove
  timeframe ammessi (15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d), fundingRate. 912 file, tutti con il
  CHECKSUM remoto verificato dal caricatore (nessun CHECKSUM mancante segnalato per LINKUSDT).
* Riferimento di mercato: klines last di BTCUSDT sugli stessi nove timeframe, 2020-01 → 2023-12.
* Impronte SHA-256 di ogni file: `impronte.json` in questa cartella (912 file LINKUSDT).
  Impronta di `impronte.json`: `407cef8003f4cae8f69120b094aacd36e4a1bb164d9ca82819e36366257760b9`.
  Le impronte dei file di BTCUSDT sono in `impronte_btcusdt.json` (aggiunte a scarico finito).
* Serie dello stop: last (parametri.yaml); il motore riceve `candele_stop=None`.

## Allineamento last e mark (`carica_serie_allineate`, file nativi di ogni timeframe)

Le barre tolte sono le stesse giornate su tutti i timeframe: il mark price manca per giorni interi.

| Timeframe | Barre tenute | Tolte dal last (mark assente) | Tolte dal mark (last assente) |
|---|---|---|---|
| 15m | 137.918 | 770 | 1 (2020-01-17 07:45) |
| 30m | 68.960 | 384 | 1 (2020-01-17 07:30) |
| 1h | 34.480 | 192 | 1 (2020-01-17 07:00) |
| 2h | 17.240 | 96 | 1 (2020-01-17 06:00) |
| 4h | 8.620 | 48 | 1 (2020-01-17 04:00) |
| 6h | 5.747 | 32 | 0 |
| 8h | 4.310 | 24 | 1 (2020-01-17 00:00) |
| 12h | 2.874 | 16 | 0 |
| 1d | 1.437 | 8 | 0 |

Intervalli tolti dal last (uguali per tutti i timeframe, giorni UTC interi): 2021-07-01; dal
2021-07-24 al 2021-07-27; 2022-07-31; 2022-10-02; 2023-02-24. Solo a 15m anche due barre singole:
2020-01-19 13:15 e 2023-11-10 03:45. Dopo l'allineamento questi intervalli sono buchi della serie,
che il motore conta (`n_buchi_dati`); nessun altro buco. Nessuna barra tenuta senza volume in USDT.
Due di questi intervalli cadono in validazione (2023-02-24 e, a 15m, 2023-11-10 03:45); quello del
2022-10-02 è in costruzione.

## Sospensioni e cambi di contratto

Nessun cambio di simbolo o di contratto nel periodo (un solo simbolo, LINKUSDT, dal primo all'ultimo
file). Le giornate senza mark price sono le sole interruzioni viste.

## Funding

4.334 settlement dal 2020-01-17 08:00 al 2023-12-31 16:00 UTC, intervallo sempre 8 ore (dichiarato
dai file e confermato dalle distanze). Tasso medio per settlement: 2020 0,0105%; 2021 0,0393%;
2022 0,0054%; 2023 0,0093%.

## Volume e liquidità (candele giornaliere del last, colonna quote_volume, 1.445 giorni)

| Anno | Volume medio giornaliero (USDT) |
|---|---|
| 2020 | 220 milioni |
| 2021 | 540 milioni |
| 2022 | 309 milioni |
| 2023 | 319 milioni |

Fascia di slippage della scheda (volume 2023): 0,02% per lato. Il 2020 è nella stessa fascia (sopra
200 milioni), quindi la fascia del 2023 non è ottimista per gli anni prima, salvo i singoli mesi
iniziali del 2020.

**Mesi sotto la liquidità minima (20 milioni di USDT al giorno): solo 2020-01** (13,9 milioni di media
sui giorni con dati). Filtro, uguale per `conta_trade`, per il test, per la baseline (a) e per la (b):
una barra di segnale che apre in un mese sotto la soglia non apre posizioni (`comune.liquida`), e le
stesse barre vanno fra le `barre_vietate` della (b). Una posizione già aperta esce con la sua uscita.
Il mese escluso non sposta le date di costruzione e validazione.

## Storia utile

Dal 2020-01-17 al 2023-12-31: quasi 4 anni, sopra `storia_minima_anni` (2). La campagna prosegue.
