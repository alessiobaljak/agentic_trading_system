# Fase 0 — I dati di TRBUSDT

Scritto il 2026-10-09 prima di qualunque variante. Numeri da `fase0_numeri.json` e
`fase0_anomalie.json` (prodotti da `codice/fase0.py` e `codice/anomalie.py`), impronte in
`impronte.json`.

## Periodi (Fase 0, punto 1)

Da `scheda_moneta.md`: primo mese di dati 2020-09. Con `periodi_campagna(2020-09-01)`, scritti
nel log prima di caricare i prezzi:

| | |
|---|---|
| inizio | 2020-09-01 (1.217 giorni fino al 2023-12-31) |
| costruzione | 2020-09-01 → 2022-12-30 (851 giorni), fine `1672444799999` ms |
| validazione | 2022-12-31 → 2023-12-31 |

La prima barra nei file è del **2020-09-03** (le 07:00 UTC a 1h; il funding dalle 08:00 del 3
settembre): i primi due giorni del periodo non hanno dati. Le date non si spostano (si dichiara).

## File scaricati e impronte

* Fonte: data.binance.vision, file mensili da 2020-09 a 2023-12. TRBUSDT: candele last
  (`klines`) e mark (`markPriceKlines`) su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, e funding: 760
  file. BTCUSDT: candele last sugli stessi 9 timeframe, solo come riferimento di mercato: 360 file.
* Tutti i 1.120 file sono stati ricontrollati contro il CHECKSUM pubblicato accanto a ogni zip:
  **1.120 uguali, 0 diversi, 0 senza CHECKSUM**.
* Impronte SHA-256 di ogni file in `impronte.json`; l'impronta di quel file è
  `cfbd216a5a8a9a63417bac1236d4c508e6fdbc39bc209861468906d1b2018111`. A ogni nuova sessione i
  dati si riscaricano e si confrontano con queste impronte (sezione 5): se cambiano, STOP.
* Nessun file oltre il 2023-12 è stato chiesto né elencato.

## Cambi di contratto e sospensioni

Nessun cambio di contratto nell'in-sample: una sola serie `TRBUSDT`, nessuna cucitura.
Giorni interi senza candele nel **last** (i file del mark li hanno): 2022-02-26 → 2022-02-28 e
2022-04-01 → 2022-04-02. Giorni interi senza candele nel **mark** (il last li ha): 2021-07-01,
2021-07-24 → 2021-07-27, 2022-10-02, 2023-02-24, più le prime ore del 2020-09-03 e una barra
a 15m del 2023-11-10 03:45. Non si sa se siano sospensioni della moneta o buchi dell'archivio:
non si cerca altro (regola 1).

## Last e mark allineati (`carica_serie_allineate`, intersezione)

| timeframe | barre last | barre mark | tenute | tolte dal last (mark mancante) | tolte dal mark (last mancante) | buchi nella serie tenuta |
|---|---|---|---|---|---|---|
| 15m | 116.132 | 115.956 | 115.459 | 673 | 497 | 7 |
| 30m | 58.066 | 57.979 | 57.730 | 336 | 249 | 6 |
| 1h | 29.033 | 28.990 | 28.865 | 168 | 125 | 6 |
| 2h | 14.517 | 14.495 | 14.433 | 84 | 62 | 6 |
| 4h | 7.259 | 7.248 | 7.217 | 42 | 31 | 6 |
| 6h | 4.839 | 4.832 | 4.811 | 28 | 21 | 6 |
| 8h | 3.630 | 3.624 | 3.609 | 21 | 15 | 6 |
| 12h | — | — | — | (vedi `fase0_numeri.json`) | | 6 |
| 1d | 1.210 | 1.208 | 1.203 | 7 | 5 | 6 |

Gli intervalli di date delle barre tolte sono quelli della sezione precedente (dettaglio per
timeframe in `fase0_numeri.json`). BTCUSDT non ha buchi su nessun timeframe.

## Funding

3.886 settlement dal 2020-09-03 08:00 al 2023-12-31 20:00. Intervallo **8 ore** fino al
2023-10-12; **4 ore** dal 2023-10-12 12:00 (nel periodo di validazione), sia dalla colonna del
file sia dalla distanza fra i settlement. Il motore applica a ogni settlement il tasso vero.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` dei file 1d del last, tutti i giorni):

| anno | volume medio al giorno |
|---|---|
| 2020 (da settembre) | 17,7 milioni |
| 2021 | 46,1 milioni |
| 2022 | 72,5 milioni |
| 2023 | 257,6 milioni |

**Mesi sotto i 20 milioni al giorno** (`liquidita_minima_usdt_giorno`): 2020-09, 2020-10,
2020-12, 2022-01, 2022-02, 2022-03, 2022-04 (in costruzione: 7 mesi su 28) e 2023-03, 2023-04,
2023-05, 2023-06, 2023-07 (in validazione: 5 mesi su 12).

**Filtro, uguale per `conta_trade`, per il test e per la (a)** (`codice/banco.py`,
`_fabbrica`): nessuna posizione si apre su un segnale di una barra che cade in uno di questi
mesi (mese UTC dell'apertura della barra). Le stesse barre vanno nelle barre vietate della (b).
Una posizione già aperta esce con la sua uscita. I mesi non si tolgono dalla serie e le date dei
periodi non si spostano.

**Slippage ottimista per gli anni prima del 2023.** La fascia della scheda (0,02% per lato) viene
dal volume del 2023 (257,6 milioni: fascia da 200 milioni a 1 miliardo). Con il volume di quegli
anni la fascia sarebbe stata 0,10% (2020, 2021: 20-50 milioni) e 0,05% (2022: 50-200 milioni).
Il costo di un giro modellato è 0,14% del nozionale; con la fascia dell'anno sarebbe stato 0,30%
(2020-2021) e 0,20% (2022). Il parametro è congelato e non si cambia; il test a costi doppi
(0,28% a giro) copre il 2022, non del tutto il 2020-2021. Si dichiara in ogni risultato vicino
ai costi.

## Barre anomale (tutto l'in-sample, serie tenute)

* 15m: 6 barre con volume zero e massimo uguale al minimo; 12 barre con un'ombra oltre il 25%
  dalla chiusura precedente (fino al 78% e all'83%, per esempio 2022-06-07 e 2022-11-29).
* 1h: 21 barre con ombre oltre il 25%; 4h: 26; 1d: 63.
Sono stampe vere dell'archivio, non corrette: uno stop sul last le prende. Si tengono e si
dichiarano; le varianti a stop vicini su timeframe corti ne risentono di più.

## Volatilità tipica (per i costi in R)

ATR(14) mediano in percentuale del prezzo, costruzione (`costi_in_r.json`): 15m 1,10%; 30m
1,60%; 1h 2,32%; 4h 4,94%; 8h 7,35%; 1d 13,4%. Costo di un giro (0,14%) in R con stop a 1 ATR:
0,13 (15m), 0,09 (30m), 0,06 (1h), 0,03 (4h), 0,02 (8h), 0,01 (1d). Conseguenza per il bot: uno
stop a 2 ATR supera il 6% del bot già a 4h (circa 10%).

## Storia utile

Dal 2020-09-03 al 2023-12-31: oltre 3 anni, sopra `storia_minima_anni` (2). La campagna prosegue.
