# BNBUSDT — Fase 0, i dati della moneta

Scritto il 9 ottobre 2026 dalla sessione di campagna (protocollo 4.5). Codice: `codice/periodi.py`,
`codice/scarica.py`, `codice/fase0.py`, `codice/impronte.py`. Numeri presi dall'uscita di
`codice/fase0.py` (copia locale in `data/insample/BNBUSDT/fase0_rapporto.json`, fuori da git).

## Periodi (scritti nel log prima di caricare i prezzi, voce BNBUSDT-N003)

| | Valore |
|---|---|
| Primo mese di dati (scheda) | 2020-02 |
| Giorni dall'inizio al 2023-12-31 | 1430 |
| Costruzione | 2020-02-01 → 2022-10-28 (1001 giorni), `fine_costruzione_ts` = 1667001599999 |
| Validazione | 2022-10-29 → 2023-12-31 |

## Cosa è stato scaricato

Da data.binance.vision, file mensili dal 2020-02 al 2023-12 (47 mesi), ogni file controllato
col CHECKSUM pubblicato da Binance (nessun CHECKSUM mancante):

* BNBUSDT klines (last) e markPriceKlines (mark) su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d;
* BNBUSDT fundingRate;
* BTCUSDT klines (last) sugli stessi nove timeframe, solo come riferimento di mercato.

La serie dello stop è il last (parametri.yaml): non si scarica a parte.

Impronte SHA-256 di tutti i file (893 di BNBUSDT, 423 di BTCUSDT) in `impronte.json`, accanto a
questo file. Impronta di `impronte.json`:
`b4e4731ea4b792e63b5669d316b32e01aaad0b0209c462eac2a719b31f9fc338`. A ogni nuova sessione i
dati si riscaricano e si confrontano con questo file: se un'impronta cambia, STOP.

## Inizio effettivo dei dati

I file di febbraio 2020 contengono il mark dal 2020-02-01 ma il last solo dal **2020-02-10**
(00:00 UTC per le candele giornaliere, 08:00 per quelle infragiornaliere) e il primo funding è il
2020-02-10 alle 08:00. La serie utile parte quindi il 2020-02-10: nove giorni dopo l'inizio
dell'in-sample. Le date di costruzione e validazione non si spostano (regola della Fase 0).

## Buchi e allineamento last/mark (`carica_serie_allineate`)

Il last non ha buchi su nessun timeframe (controllo barra per barra). Barre tolte
dall'intersezione:

| Timeframe | Barre last | Barre tenute | Tolte dal last (manca il mark) | Tolte dal mark (manca il last) |
|---|---|---|---|---|
| 15m | 136.384 | 135.615 | 769 | 896 |
| 30m | 68.192 | 67.808 | 384 | 448 |
| 1h | 34.096 | 33.904 | 192 | 224 |
| 2h | 17.048 | 16.952 | 96 | 112 |
| 4h | 8.524 | 8.476 | 48 | 56 |
| 6h | 5.683 | 5.651 | 32 | 37 |
| 8h | 4.262 | 4.238 | 24 | 28 |
| 12h | 2.842 | 2.826 | 16 | 18 |
| 1d | 1.421 | 1.413 | 8 | 9 |

Intervalli delle barre tolte dal last (stessi giorni su ogni timeframe): 2021-07-01 (giorno
intero), 2021-07-24 → 2021-07-27 (quattro giorni interi), 2022-07-31, 2022-10-02, 2023-02-24
(giorni interi), più una sola barra a 15m il 2023-11-10 alle 03:45. Le barre tolte dal mark
sono tutte all'inizio: 2020-02-01 → 2020-02-10 (prima che esista il last).

Sono 8 giornate senza mark, 7 delle quali in costruzione. Per il motore sono buchi (li conta
in `n_buchi_dati`); un settlement di funding caduto lì con posizione aperta si addebita
sull'ultimo mark disponibile.

## Sospensioni e cambi di contratto

Nessun cambio di simbolo o di contratto nel periodo: un solo contratto, `BNBUSDT`. Nessuna
cucitura.

## Funding

4.262 settlement dal 2020-02-10 08:00 al 2023-12-31 16:00, sempre a **8 ore** (l'intervallo
dichiarato dal file e quello ricavato dalla distanza fra settlement coincidono per tutto il
periodo).

## Volume medio giornaliero in USDT (colonna `quote_volume` delle candele 1d del last)

| Anno | Volume medio al giorno |
|---|---|
| 2020 | 56 milioni |
| 2021 | 1.452 milioni |
| 2022 | 521 milioni |
| 2023 | 401 milioni |

La fascia di slippage della scheda (0,02% per lato) viene dal volume del 2023. Nel 2020 il
volume era quasi dieci volte più basso (56 milioni, cioè la fascia 0,05% da 50 a 200 milioni):
per i trade del 2020 lo slippage del backtest è ottimista. Il test a costi doppi lo copre solo
in parte; si dichiara accanto a ogni risultato che pesa sul 2020.

## Mesi sotto la liquidità minima (20 milioni di USDT al giorno)

| Mese | Volume medio al giorno |
|---|---|
| 2020-05 | 19,4 milioni |
| 2020-06 | 12,3 milioni |

**Filtro, uguale per `conta_trade`, per il test e per la baseline (a):** nessuna posizione si
apre su un segnale di una barra che apre in maggio o giugno 2020 (UTC). Le stesse barre vanno in
`barre_vietate` della baseline (b). Una posizione già aperta esce con la sua uscita.
Implementato in `codice/comune.py` (`MESI_ESCLUSI`, `indici_esclusi_liquidita`).

Le date di costruzione e validazione non si spostano per questi due mesi: la costruzione ha 61
giorni in cui non si entra.

## Storia utile

Dal 2020-02-10 al 2023-12-31: quasi quattro anni, sopra i 2 di `storia_minima_anni`. La campagna
può proseguire.
