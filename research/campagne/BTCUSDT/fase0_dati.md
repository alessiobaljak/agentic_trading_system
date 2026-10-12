# Fase 0 — I dati di BTCUSDT

Scritto l'8 ottobre 2026 dalla sessione di campagna. Numeri da `codice/fase0_analisi.py` e
`codice/fase0_verifica.py` (uscite in `data/insample/BTCUSDT/`, fuori da git).

## Periodi (scritti nel log prima dei prezzi, voce BTCUSDT-N002)

| | |
|---|---|
| Inizio dell'in-sample (scheda) | 2020-01-01 |
| Giorni fino al 2023-12-31 | 1.461 |
| Costruzione | 2020-01-01 → 2022-10-18 (1.022 giorni), `fine_costruzione_ts` = 1666137599999 |
| Validazione | 2022-10-19 → 2023-12-31 |

Nessun mese escluso per liquidita': le date non si spostano.

## File scaricati e impronte

* Fonte: data.binance.vision, file mensili da 2020-01 a 2023-12, solo fino al 2023-12-31.
  Candele last (`klines`) e mark (`markPriceKlines`) su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h,
  1d, e `fundingRate`: 912 file, nessun mese mancante.
* Integrita': tutti i 912 file confrontati con il CHECKSUM SHA-256 pubblicato da Binance
  accanto a ciascuno: 912 uguali, 0 diversi, 0 senza CHECKSUM.
* Impronte dei file: `impronte.json` in questa cartella (912 voci). SHA-256 di
  `impronte.json`: `3632020f86ec6e5c22489de4c5fee9cb85686a65bd80be1d7ebc72f81b6fd7ac`.
  A ogni nuova sessione si riscarica e si confronta con `dati.verifica_impronte`: se cambia
  qualcosa, STOP.

## Buchi

* **Last price:** nessun buco su nessun timeframe (per esempio 35.064 barre orarie su
  35.064 attese).
* **Mark price:** mancano giorni interi (a 1h): 2021-07-01 (24 barre), dal 2021-07-24 al
  2021-07-27 (96 barre), 2022-07-31 (24), 2022-10-02 (24), 2023-02-24 (24); a 15m manca
  anche la barra del 2020-01-19 13:15. In costruzione cadono i primi sette giorni; il
  2023-02-24 cade in validazione.
* **Scelta (scritta prima di ogni test, come chiede `lezioni/metodo.md`):** le serie si
  usano sull'intersezione delle barre last e mark; le barre senza mark si tolgono anche dal
  last. Barre tolte: 192 a 1h (0,55%), 770 a 15m, 384 a 30m, 96 a 2h, 48 a 4h, 32 a 6h, 24 a
  8h, 16 a 12h, 8 a 1d. Il motore conta i buchi che restano (`n_buchi_dati`) e addebita il
  funding caduto in un buco sull'ultimo mark disponibile.
* Nessuna candela anomala (high sotto low o prezzi non positivi).
* Sospensioni e cambi di contratto: nessuno visibile nei dati (serie last continua, nessun
  cambio di simbolo). Nessun punto di cucitura.

## Funding

* 4.383 settlement dal 2020-01-01 00:00 al 2023-12-31 16:00, intervallo sempre di 8 ore (le
  ore dichiarate dal file sono 8 in tutto il periodo).
* **Trappola dei dati:** in 2.233 settlement su 4.383 l'istante nel file e' qualche
  millisecondo dopo l'ora piena (al massimo 47 ms). Il motore considera ambiguo un
  settlement che cade ESATTAMENTE all'apertura di una barra (ingresso o uscita per
  «chiudi»): con il ritardo, il funding all'ingresso si contava anche se era un incasso, e
  quello all'uscita per «chiudi» si perdeva anche se era un costo. Correzione nei dati
  della campagna (`codice/quadro.py`, `carica`): l'istante di ogni settlement si riporta al
  minuto. Scritta prima di ogni test. Proposta per le lezioni di metodo.
* Tasso medio per settlement: 2020 0,0157%; 2021 0,0280%; 2022 0,0038%; 2023 0,0072%.

## Volume e slippage

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere):

| Anno | Volume medio al giorno |
|---|---|
| 2020 | 3,11 miliardi |
| 2021 | 17,5 miliardi |
| 2022 | 12,8 miliardi |
| 2023 | 11,5 miliardi |

Mese piu' basso: gennaio 2020, 1,40 miliardi al giorno. La fascia di slippage della scheda
(0,01% per lato, oltre 1 miliardo al giorno) vale in tutti gli anni, anche nel 2020, quando
il volume era un quarto di quello del 2023: e' ottimista soprattutto per il 2020, e il test
a costi doppi copre questo rischio solo in parte. Mesi sotto i 20 milioni al giorno: nessuno.

## Storia

Quattro anni di in-sample (sopra i 2 di `storia_minima_anni`): la campagna si fa.

## Dati usati come riferimento di mercato

La moneta della campagna e' BTCUSDT stessa: il controllo «e' solo il mercato» si legge
dal buy and hold di BTCUSDT per anno (baseline (c)) e dalla baseline (b).
