# LTCUSDT — Fase 0: i dati

Scritto il 2026-10-09 dalla sessione di campagna (protocollo 4.5). Fonte di ogni numero:
`data/insample/LTCUSDT/fase0_riepilogo.json`, prodotto da `codice/fase0.py` (fuori da git, si
rigenera); le impronte sono in `impronte_LTCUSDT.json` e `impronte_BTCUSDT.json` in questa cartella.

## Periodi (scritti nel log prima di caricare i prezzi, voce LTCUSDT-N001)

| | |
|---|---|
| Inizio (primo mese di dati della scheda) | 2020-01-01 |
| Giorni fino al 2023-12-31 compreso | 1461 |
| Costruzione | 2020-01-01 → 2022-10-18 (1022 giorni; `fine_costruzione_ts` 1666137599999) |
| Validazione | 2022-10-19 → 2023-12-31 |

**La prima barra vera è del 2020-01-09** (last e mark; il primo settlement di funding è il
2020-01-09 08:00 UTC): i primi 8 giorni della costruzione non hanno dati. Le date restano quelle
calcolate da `periodi_campagna` (la regola le fissa dal primo mese della scheda); la costruzione
utile è quindi di 1014 giorni.

## File scaricati

* LTCUSDT: candele last (klines) e mark (markPriceKlines) su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d,
  e funding: 48 mesi ciascuno (2020-01 → 2023-12), nessun mese assente. 912 file.
* BTCUSDT (solo riferimento di mercato): candele last sugli stessi 9 timeframe, 48 mesi ciascuno, 432 file.
* Integrità: per tutti i 1344 file lo SHA-256 combacia col CHECKSUM pubblicato da Binance accanto
  allo zip (1344 su 1344; nessun CHECKSUM mancante, nessuno diverso).
* Impronte: `impronte_LTCUSDT.json` (SHA-256 del file:
  `8e3fca595044e3dedd42f64fda6ae12c3177895bbcf3fafb91b79a45bacb9961`) e `impronte_BTCUSDT.json`
  (`7dbb21b9675aba9cabc252c2b0e556840420c482ff907f453e301d3011840049`). Una sessione successiva
  riscarica e confronta con questi file: se un'impronta cambia, STOP.
* Nessun file successivo al 2023-12 è stato chiesto o elencato.

## Last e mark allineati (`carica_serie_allineate`)

Barre tolte dall'intersezione, uguali in tutti i timeframe salvo il numero di barre:

| Dove | Cosa manca | Barre tolte a 1h | a 15m | a 4h | a 1d |
|---|---|---|---|---|---|
| 2020-01-09 dalle 04:00 alle 07:59 | il last (c'è solo il mark: prime ore del contratto) | 4 tolte dal mark | 15 | 1 | 0 |
| 2020-01-19 13:15 | una barra di last a 15m | — | 1 | — | — |
| 2022-02-26 → 2022-02-28 | il mark (tre giorni interi) | 72 tolte dal last | 288 | 18 | 3 |
| 2022-04-01 → 2022-04-02 | il mark (due giorni interi) | 48 | 192 | 12 | 2 |
| 2022-10-02 | il last (un giorno intero) | 24 tolte dal mark | 96 | 6 | 1 |
| 2023-02-24 | il last (un giorno intero) | 24 | 96 | 6 | 1 |
| 2023-11-10 03:45 | una barra di last a 15m | — | 1 | — | — |

Totali per timeframe (barre tolte dal last / dal mark; barre tenute 2020-01-09 → 2023-12-31):
15m 194 / 495 (138.782 tenute); 30m 96 / 248 (69.392); 1h 48 / 124 (34.696); 2h 24 / 62 (17.348);
4h 12 / 31 (8.674); 6h 8 / 21 (5.783); 8h 6 / 16 (4.337); 12h 4 / 10 (2.892); 1d 2 / 5 (1.446).

Dopo l'intersezione restano 4 buchi in ogni timeframe (2022-02-26→28, 2022-04-01→02, 2022-10-02,
2023-02-24) più, a 15m, due buchi di una barra. Il motore li conta (`n_buchi_dati`) e addebita il
funding caduto in un buco sull'ultimo mark disponibile (`n_funding_in_buco`): si riportano nei
risultati. Il buco del 2022-10-02 è in costruzione; quello del 2023-02-24 è in validazione.

Le candele last di BTCUSDT non hanno buchi su nessun timeframe (2020-01-01 → 2023-12-31).

## Sospensioni e cambi di contratto

Nessun cambio di contratto né ridenominazione nella serie (simbolo unico `LTCUSDT` dalla scheda).
Le giornate senza last del 2022-10-02 e del 2023-02-24 sono mancanze dell'archivio: da qui non si sa
se sono sospensioni della negoziazione; si trattano come buchi.

## Funding

4.358 settlement dal 2020-01-09 08:00 al 2023-12-31 16:00 UTC; intervallo di 8 ore per tutto il
periodo (dichiarato nei file e confermato dalle distanze fra settlement). Tasso medio per settlement:
2020 0,0233%; 2021 0,0366%; 2022 0,0026%; 2023 0,0085%.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele 1d del last, tutti i giorni):

| Anno | Volume medio giornaliero |
|---|---|
| 2020 | 112 milioni |
| 2021 | 670 milioni |
| 2022 | 243 milioni |
| 2023 | 382 milioni |

Mese più basso: 2020-06 con 22,9 milioni al giorno. **Nessun mese sotto la soglia di 20 milioni**:
il filtro dei mesi illiquidi (regola uguale per `conta_trade`, test, baseline (a) e barre vietate
della (b), in `codice/quadro.py`, `mesi_illiquidi` e `vietate_liquidita`) è scritto ma non toglie
nessuna barra.

**Slippage del 2020 probabilmente ottimista** (lezione di metodo): la fascia della scheda (0,02% per
lato) viene dal volume del 2023 (382 milioni, fascia 200 milioni - 1 miliardo); nel 2020 il volume
medio era 112 milioni, che per la regola delle fasce starebbe in quella da 0,05%, e fino a ottobre
2020 sotto i 120 milioni in tutti i mesi. Il test a costi doppi lo copre solo in parte: i risultati
del 2020 vanno letti con questa riserva.

## Storia utile

Dal 2020-01-09 al 2023-12-31: quasi 4 anni, sopra `storia_minima_anni` (2). La campagna procede.
