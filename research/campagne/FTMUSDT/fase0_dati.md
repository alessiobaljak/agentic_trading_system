# FTMUSDT — dati della Fase 0

Scritto da `codice/fase0_analisi.py`. Periodo: dal 2020-09-01 al 2023-12-31 (in-sample). Costruzione dal 2020-09-01 al 2022-12-30 (851 giorni); validazione dal 2022-12-31 al 2023-12-31.

Fonte: data.binance.vision, file mensili (klines, markPriceKlines, fundingRate), scaricati con `dati.scarica_periodo` con il controllo del CHECKSUM remoto. Nessun file oltre il 2023-12.

## Barre per timeframe e barre tolte dall'allineamento last/mark (`carica_serie_allineate`)

| timeframe | barre tenute | tolte dal last (mancano nel mark) | tolte dal mark (mancano nel last) | buchi nella serie tenuta | prima barra | ultima barra |
|---|---|---|---|---|---|---|
| 15m | 113923 | 193 | 562 | 5 | 2020-09-24 07:00 | 2023-12-31 23:45 |
| 30m | 56962 | 96 | 281 | 4 | 2020-09-24 07:00 | 2023-12-31 23:30 |
| 1h | 28481 | 48 | 141 | 4 | 2020-09-24 07:00 | 2023-12-31 23:00 |
| 2h | 14241 | 24 | 70 | 4 | 2020-09-24 06:00 | 2023-12-31 22:00 |
| 4h | 7121 | 12 | 35 | 4 | 2020-09-24 04:00 | 2023-12-31 20:00 |
| 6h | 4747 | 8 | 24 | 4 | 2020-09-24 06:00 | 2023-12-31 18:00 |
| 8h | 3561 | 6 | 17 | 4 | 2020-09-24 00:00 | 2023-12-31 16:00 |
| 12h | 2374 | 4 | 12 | 4 | 2020-09-24 00:00 | 2023-12-31 12:00 |
| 1d | 1187 | 2 | 6 | 4 | 2020-09-24 00:00 | 2023-12-31 00:00 |

Intervalli (date UTC di apertura delle barre):

* 15m, tolte_last: 2022-10-02 00:00 → 2022-10-02 23:45; 2023-02-24 00:00 → 2023-02-24 23:45; 2023-11-10 03:45 → 2023-11-10 03:45
* 15m, tolte_mark: 2020-09-23 10:30 → 2020-09-24 06:45; 2022-02-26 00:00 → 2022-02-28 23:45; 2022-04-01 00:00 → 2022-04-02 23:45
* 15m, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00; 2023-11-10 03:45 → 2023-11-10 04:00
* 30m, tolte_last: 2022-10-02 00:00 → 2022-10-02 23:30; 2023-02-24 00:00 → 2023-02-24 23:30
* 30m, tolte_mark: 2020-09-23 10:30 → 2020-09-24 06:30; 2022-02-26 00:00 → 2022-02-28 23:30; 2022-04-01 00:00 → 2022-04-02 23:30
* 30m, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00
* 1h, tolte_last: 2022-10-02 00:00 → 2022-10-02 23:00; 2023-02-24 00:00 → 2023-02-24 23:00
* 1h, tolte_mark: 2020-09-23 10:00 → 2020-09-24 06:00; 2022-02-26 00:00 → 2022-02-28 23:00; 2022-04-01 00:00 → 2022-04-02 23:00
* 1h, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00
* 2h, tolte_last: 2022-10-02 00:00 → 2022-10-02 22:00; 2023-02-24 00:00 → 2023-02-24 22:00
* 2h, tolte_mark: 2020-09-23 10:00 → 2020-09-24 04:00; 2022-02-26 00:00 → 2022-02-28 22:00; 2022-04-01 00:00 → 2022-04-02 22:00
* 2h, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00
* 4h, tolte_last: 2022-10-02 00:00 → 2022-10-02 20:00; 2023-02-24 00:00 → 2023-02-24 20:00
* 4h, tolte_mark: 2020-09-23 08:00 → 2020-09-24 00:00; 2022-02-26 00:00 → 2022-02-28 20:00; 2022-04-01 00:00 → 2022-04-02 20:00
* 4h, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00
* 6h, tolte_last: 2022-10-02 00:00 → 2022-10-02 18:00; 2023-02-24 00:00 → 2023-02-24 18:00
* 6h, tolte_mark: 2020-09-23 06:00 → 2020-09-24 00:00; 2022-02-26 00:00 → 2022-02-28 18:00; 2022-04-01 00:00 → 2022-04-02 18:00
* 6h, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00
* 8h, tolte_last: 2022-10-02 00:00 → 2022-10-02 16:00; 2023-02-24 00:00 → 2023-02-24 16:00
* 8h, tolte_mark: 2020-09-23 08:00 → 2020-09-23 16:00; 2022-02-26 00:00 → 2022-02-28 16:00; 2022-04-01 00:00 → 2022-04-02 16:00
* 8h, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00
* 12h, tolte_last: 2022-10-02 00:00 → 2022-10-02 12:00; 2023-02-24 00:00 → 2023-02-24 12:00
* 12h, tolte_mark: 2020-09-23 00:00 → 2020-09-23 12:00; 2022-02-26 00:00 → 2022-02-28 12:00; 2022-04-01 00:00 → 2022-04-02 12:00
* 12h, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00
* 1d, tolte_last: 2022-10-02 00:00 → 2022-10-02 00:00; 2023-02-24 00:00 → 2023-02-24 00:00
* 1d, tolte_mark: 2020-09-23 00:00 → 2020-09-23 00:00; 2022-02-26 00:00 → 2022-02-28 00:00; 2022-04-01 00:00 → 2022-04-02 00:00
* 1d, buchi nella serie tenuta: 2022-02-26 00:00 → 2022-03-01 00:00; 2022-04-01 00:00 → 2022-04-03 00:00; 2022-10-02 00:00 → 2022-10-03 00:00; 2023-02-24 00:00 → 2023-02-25 00:00

## Funding

Settlement: 3583, dal 2020-09-23 16:00 al 2023-12-31 16:00. Intervalli dichiarati dal file nel tempo: dal 2020-09-23 16:00: 8.0 ore.
Distanza fra settlement consecutivi (ore): [8.0].
Tasso: media 0.000188, mediana 0.000100, minimo -0.007500, massimo 0.006934.

## Volume (quote_volume dei file 1d del last, `volume_usdt_da_zip`)

| anno | giorni | volume medio giornaliero (milioni di USDT) |
|---|---|---|
| 2020 | 99 | 4.7 |
| 2021 | 365 | 396.7 |
| 2022 | 360 | 460.2 |
| 2023 | 365 | 199.2 |

Mesi sotto la liquidità minima (media giornaliera < 20 milioni di USDT): 2020-09 (5.6 M), 2020-10 (4.1 M), 2020-11 (5.5 M), 2020-12 (4.3 M).

Filtro (uguale per conta_trade, test e baseline (a); stesse barre vietate alla (b)): nessuna posizione si apre su un segnale di una barra che apre in uno di quei mesi; una posizione già aperta esce con la sua uscita (`quadro.Serie.illiquida`). I mesi non si tolgono dalla serie e non spostano le date di costruzione e validazione.

## Impronte

760 file zip in `data/insample/FTMUSDT/`; le impronte SHA-256 sono in `impronte.json` (questa cartella). Impronta di `impronte.json`: 47cfe2330e465a1898211d804906207cd3ad866127e2adb178fa624f9c0c2d6d.

Riferimento di mercato BTCUSDT (solo last, dal 2020-01): 432 file; impronta dell'elenco ordinato delle impronte: c8fa844caca1685d7cf2edd1b03bf5ca2011deb1a2ae1a96056711b1d2ea49d0.

## Cambi di contratto e sospensioni

La scheda dà un solo simbolo (FTMUSDT) per tutto l'in-sample: nessuna cucitura. Le sospensioni si vedono come buchi nelle tabelle sopra.

## Storia utile

Dal 2020-09-01 al 2023-12-31: 1217 giorni (3,3 anni), sopra i 2 anni di `storia_minima_anni`.

## Note scritte a mano dopo la tabella (osservato)

* **Il primo dato è del 2020-09-24**, non del 2020-09-01: le date di costruzione e
  validazione restano quelle scritte nel log prima dei prezzi (calcolate dal primo mese
  della scheda), come chiede il protocollo.
* **I quattro mesi del 2020 sono sotto la liquidità minima**: in costruzione si apre
  solo su segnali dal 2021-01-01 al 2022-12-30, cioè circa 729 giorni utili su 851 (gli
  indicatori invece si scaldano già sul 2020). Storia utile liquida dal 2021-01 al
  2023-12: 3 anni, sopra i 2 anni minimi. In costruzione gli anni con trade saranno solo
  due (2021 e 2022): la verifica di stabilità temporale della Fase 4 conterà su due anni.
* **Slippage**: la fascia della scheda (0,05% per lato) viene dal volume del 2023 (199 M
  al giorno); nel 2021 e 2022 il volume medio era doppio (397 M e 460 M), quindi in
  costruzione la fascia è prudente, non ottimista.
* **Buchi del mark**: tre periodi (2020-09-23/24, 2022-02-26 → 28, 2022-04-01 → 02) tolti
  dal last; due giorni senza last (2022-10-02, 2023-02-24, quest'ultimo in validazione)
  tolti dal mark. Restano 4 buchi di uno-tre giorni in ogni timeframe (5 a 15 minuti).
* **Funding**: sempre a 8 ore nell'in-sample; tassi fino a ±0,75% per settlement, molto
  oltre il tasso di base 0,01%.
