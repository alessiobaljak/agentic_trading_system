# Fase 0 — I dati di AVAXUSDT

Scritto il 9 ottobre 2026 dalla sessione di campagna, prima di qualunque variante. Numeri da
`codice/fase0.py` (file locale `data/insample/AVAXUSDT/fase0_controlli.json`, non in git).

## Date (Fase 0 punto 1, nel log alla voce N003, prima di caricare i prezzi)

| | Dal | Al |
|---|---|---|
| In-sample (scheda: primo mese 2020-09) | 2020-09-01 | 2023-12-31 (1217 giorni) |
| Costruzione (851 giorni) | 2020-09-01 | 2022-12-30 23:59:59.999 UTC (`fine_costruzione_ts` 1672444799999) |
| Validazione | 2022-12-31 | 2023-12-31 |

I dati veri cominciano il 2020-09-22 (mark e funding) e il 2020-09-23 (last): le prime tre
settimane di settembre 2020 della scheda non hanno barre. Le date non si spostano (regola della
Fase 0); la storia utile resta oltre 3 anni, sopra `storia_minima_anni` (2).

## Scarico e integrità

* Fonte: data.binance.vision, file mensili, da 2020-09 a 2023-12, nessun file successivo
  chiesto né elencato. AVAXUSDT: klines e markPriceKlines su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h,
  1d, più fundingRate (760 file). BTCUSDT: klines sugli stessi 9 timeframe (360 file).
* Checksum: per tutti i 1.120 file lo sha256 coincide con il `.CHECKSUM` pubblicato da Binance
  (riletto apposta da `fase0.py`); nessun file senza checksum.
* Impronte: `impronte_AVAXUSDT.json` (sha256 del file
  `e566b39ee7c29191936fd759c2d75f1ff90a23f661c3a3b8fe6fe1eb8166eda3`) e `impronte_BTCUSDT.json`
  (`ea07a6beee094c748a0f254a22d2e3b21067418088b6af48e1ba204fb56f9d90`), in questa cartella.
  A ogni nuova sessione si riscarica e si confronta con `verifica_impronte`.

## Buchi, barre tolte e cambi di contratto

* Il last non ha buchi su nessun timeframe dal 2020-09-23 al 2023-12-31.
* Il mark manca per giorni interi: 2021-07-01, dal 2021-07-24 al 2021-07-27, 2022-07-31,
  2022-10-02, 2023-02-24 (e una barra di 15 minuti il 2023-11-10 03:45). Con
  `carica_serie_allineate` quelle barre del last si tolgono (intersezione) e diventano buchi
  della serie allineata (il motore li conta). Il mark ha in più le barre dal 2020-09-22 al
  2020-09-23 mattina, prima del primo last: tolte.

| Timeframe | Barre last | Barre mark | Allineate | Tolte dal last | Tolte dal mark | Buchi |
|---|---|---|---|---|---|---|
| 15m | 114.692 | 114.009 | 113.923 | 769 | 86 | 6 |
| 30m | 57.346 | 57.005 | 56.962 | 384 | 43 | 5 |
| 1h | 28.673 | 28.503 | 28.481 | 192 | 22 | 5 |
| 2h | 14.337 | 14.252 | 14.241 | 96 | 11 | 5 |
| 4h | 7.169 | 7.126 | 7.121 | 48 | 5 | 5 |
| 6h | 4.779 | 4.751 | 4.747 | 32 | 4 | 5 |
| 8h | 3.585 | 3.563 | 3.561 | 24 | 2 | 5 |
| 12h | 2.390 | 2.376 | 2.374 | 16 | 2 | 5 |
| 1d | 1.195 | 1.188 | 1.187 | 8 | 1 | 5 |

Di questi buchi, in costruzione cadono i giorni del 2021 e del 2022 (luglio 2021, 31 luglio
2022, 2 ottobre 2022); quello del 2023-02-24 è in validazione.

* Cambi di contratto e sospensioni: nessuno visibile nei dati (simbolo unico AVAXUSDT, prezzi
  continui, nessuna serie da ricucire).
* BTCUSDT: nessuna barra di AVAXUSDT senza la barra di BTCUSDT con lo stesso ts, su nessun
  timeframe.

## Funding

3.586 settlement dal 2020-09-22 16:00 al 2023-12-31 16:00, sempre ogni 8 ore (00, 08, 16 UTC):
intervallo dichiarato 8 ore per tutto il periodo e nessuna distanza diversa fra settlement
consecutivi. Tasso minimo −0,75%, massimo 0,518% per 8 ore; 363 settlement sopra 0,03% e 922
negativi (conteggi sui dati, non risultati di strategie: servono a sapere se l'idea I-04 ha
eventi).

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere del last, su
tutti i giorni):

| Anno | Volume medio giornaliero |
|---|---|
| 2020 (da settembre) | 20,9 milioni |
| 2021 | 457 milioni |
| 2022 | 462 milioni |
| 2023 | 289 milioni |

**Mesi sotto la liquidità minima (20 milioni al giorno): 2020-10 (19,7) e 2020-12 (18,0).**
Filtro (in `codice/comune.py`, uguale per `conta_trade`, test e baseline (a)): la variante non
apre posizioni su segnali di barre di quei mesi; una posizione già aperta esce con la sua
uscita; le stesse barre vanno in `barre_vietate` della (b). Settembre 2020 (36,5 milioni su 8
giorni) e novembre 2020 (21,1) restano sopra, di poco.

**Slippage.** La fascia della scheda (0,02% per lato, volume 2023 fra 200 milioni e 1 miliardo)
è ottimista per l'autunno 2020, quando il volume era 18-37 milioni (fascia 0,10%), e per
alcuni mesi del 2021 (giugno-luglio 2021: 73 e 44 milioni, fascia 0,05%). Lo dichiaro come
rischio noto (lezione di metodo): copre in parte il test a costi doppi; un candidato con molti
trade nel 2020 va guardato con questa riserva.

## Storia minima

Storia utile dal 2020-09-23 al 2023-12-31: oltre 3 anni, sopra i 2 richiesti. La campagna va
avanti.
