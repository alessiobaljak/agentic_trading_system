# XRPUSDT — Fase 0: i dati

Scritto il 2026-10-09 dalla sessione di campagna. Fonte: data.binance.vision, file mensili
USDS-M (klines, markPriceKlines, fundingRate), dal 2020-01 al 2023-12, scaricati con
`research/src/dati.py` (`scarica_mese`), codice in `codice/scarica.py` e `codice/fase0.py`.
Numeri grezzi in `data/insample/XRPUSDT/fase0.json` (fuori da git, si rigenera con `codice/fase0.py`).

## Periodi (scritti nel log prima di caricare i prezzi, voce XRPUSDT-N003)

| | dal | al |
|---|---|---|
| In-sample (scheda) | 2020-01-01 | 2023-12-31 (1461 giorni) |
| Costruzione | 2020-01-01 | 2022-10-18 (1022 giorni; `fine_costruzione_ts` 1666137599999) |
| Validazione | 2022-10-19 | 2023-12-31 |

## Scarico e impronte

* 912 file di XRPUSDT (last e mark su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d; funding), 432 file
  di BTCUSDT (solo last, stessi timeframe, solo come riferimento di mercato). Nessun mese
  mancante fra 2020-01 e 2023-12 per nessun tipo. Tutti i file hanno il CHECKSUM remoto
  pubblicato da Binance e combaciano (lista dei CHECKSUM mancanti vuota).
* Impronte SHA-256 di ogni file in `impronte.json` (XRPUSDT) e `impronte_btcusdt.json`
  (BTCUSDT), accanto a questo file. Impronta dei due elenchi:
  * `impronte.json`: `4cec42220949f0a351d327f288518ee329628bb15e54598fcd9f259436013306`
  * `impronte_btcusdt.json`: `7dbb21b9675aba9cabc252c2b0e556840420c482ff907f453e301d3011840049`
  A ogni nuova sessione si riscarica e si confronta con `dati.verifica_impronte`: se cambia, STOP.

## Inizio vero della serie

I file di gennaio 2020 cominciano il **2020-01-06**: last dalle 08:00 UTC (15m: 08:15),
mark dalle 03:00 UTC, funding dal primo settlement delle 08:00 UTC. Fra il 2020-01-01 e il
2020-01-06 non ci sono prezzi (la serie BTCUSDT invece parte il 2020-01-01). Le date di
costruzione e validazione restano quelle scritte prima dei prezzi (dal 2020-01-01): i primi
5 giorni sono semplicemente vuoti. La prima candela giornaliera (2020-01-06) copre solo le
ore dalle 08:00.

## Allineamento last e mark (`carica_serie_allineate`, intersezione)

Barre tenute sull'intero in-sample (2020-01-01 → 2023-12-31) e barre tolte. «Tolte last» =
presenti nel last e non nel mark; «tolte mark» = presenti nel mark e non nel last. Gli
intervalli sono uguali su tutti i timeframe (cambia solo il numero di barre):

| Timeframe | Barre tenute | Tolte last | Tolte mark | Volume USDT mancante |
|---|---|---|---|---|
| 15m | 138.589 | 674 | 500 | 0 |
| 30m | 69.296 | 336 | 250 | 0 |
| 1h | 34.648 | 168 | 125 | 0 |
| 2h | 17.324 | 84 | 63 | 0 |
| 4h | 8.662 | 42 | 32 | 0 |
| 6h | 5.775 | 28 | 21 | 0 |
| 8h | 4.331 | 21 | 16 | 0 |
| 12h | 2.888 | 14 | 10 | 0 |
| 1d | 1.444 | 7 | 5 | 0 |

Intervalli delle barre tolte (UTC):

* presenti nel last, mancano nel mark (giorni interi): 2021-07-01; 2021-07-24 → 2021-07-27;
  2022-10-02 (validazione); 2023-02-24 (validazione); in più, solo a 15m, due barre singole:
  2020-01-19 13:15 e 2023-11-10 03:45;
* presenti nel mark, mancano nel last: 2020-01-06 dalle 03:00 alle 07:59 (prima dell'inizio del
  last); 2022-02-26 → 2022-02-28; 2022-04-01 → 2022-04-02 (giorni interi).

Dopo l'intersezione la serie ha questi **buchi** (il motore li conta in `n_buchi_dati`):
2021-07-01; 2021-07-24 → 07-27; 2022-02-26 → 02-28; 2022-04-01 → 04-02 (costruzione);
2022-10-02; 2023-02-24 (validazione); a 15m anche le due barre singole sopra. In totale
circa 12 giorni su 1461. Un'ipotesi che dipende da quei giorni non c'è; un indicatore che
attraversa un buco lo attraversa come se le barre fossero contigue (scelta comune a candidato,
(a) e (b)).

## Funding

* 4.367 settlement dal 2020-01-06 08:00 al 2023-12-31 16:00, intervallo **sempre 8 ore** (sia
  dichiarato dal file sia dalla distanza fra settlement): nessun passaggio a 4 h o 1 h nell'in-sample.
* Tasso medio per settlement: 2020 0,0225%; 2021 0,0440%; 2022 0,00001%; 2023 0,0075%.
  Minimo −0,5025%, massimo +0,4879%.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` dei file `1d` del last, tutti i 1.451 giorni):

| Anno | Volume medio giornaliero |
|---|---|
| 2020 | 233 milioni |
| 2021 | 1.719 milioni |
| 2022 | 633 milioni |
| 2023 | 811 milioni |

* **Mesi sotto la liquidità minima (20 milioni al giorno): nessuno.** Il filtro dei mesi
  illiquidi esiste nel codice (`quadro.MESI_ILLIQUIDI`, vuoto) ed è uguale per `conta_trade`,
  test, (a) e (b), ma non toglie nessuna barra.
* Mesi fra 20 e 50 milioni (vicini alla soglia): 2020-01 (22 milioni, solo dal 6 gennaio),
  2020-03, 2020-04, 2020-05, 2020-06.
* **Slippage della scheda (0,02% per lato, fascia 200 milioni – 1 miliardo, sul 2023)
  probabilmente ottimista per il 2020**: da gennaio a ottobre 2020 il volume mensile era fra
  22 e 162 milioni al giorno, cioè nelle fasce del protocollo da 0,05% e 0,10% per lato. Lo si
  dichiara (lezione di metodo della prova): i trade del 2020 hanno costi veri probabilmente più
  alti di quelli simulati; il test a costi doppi lo copre solo in parte. Nel 2021 il volume è
  oltre il miliardo (fascia 0,01%): lì lo slippage simulato è prudente.

## Sospensioni e cambi di contratto

Nessun cambio di simbolo o ridenominazione nell'in-sample: un solo simbolo, `XRPUSDT`, dal
primo all'ultimo file. Le sospensioni visibili sono i giorni mancanti elencati sopra.

## Storia utile

Dal 2020-01-06 al 2023-12-31: circa 3,99 anni, sopra `storia_minima_anni` (2). La campagna va avanti.

## Riferimento di mercato

BTCUSDT last su tutti i timeframe ammessi, dal 2020-01-01 al 2023-12-31, completo (nessuna barra
mancante: 35.064 barre a 1h). Si usa per il controllo «è solo il mercato» e per le idee che lo
nominano, allineato ai `ts` di XRPUSDT.
