# ETCUSDT — Fase 0, i dati della moneta

Scritto il 9 ottobre 2026 dalla sessione di campagna, prima di qualunque ipotesi testata. Numeri da
`codice/fase0_analisi.py` (uscita completa in `data/insample/ETCUSDT/uscite/fase0.json`, fuori da git).

## Periodi (Fase 0, punto 1; nel log alla voce ETCUSDT-N003, prima di caricare i prezzi)

| | |
|---|---|
| Primo mese di dati (scheda) | 2020-01 → inizio 2020-01-01 |
| Giorni fino al 2023-12-31 | 1.461 |
| Costruzione | 2020-01-01 → 2022-10-18 (1.022 giorni; `fine_costruzione_ts` = 1666137599999) |
| Validazione | 2022-10-19 → 2023-12-31 |

Le prime candele del last e del mark sono del **2020-01-16** (08:00 UTC per i timeframe fino a 8h): i
primi 15 giorni del periodo non hanno dati. Le date restano quelle calcolate dal primo mese, come vuole il
protocollo; la differenza si dichiara qui.

## Scarico e impronte

* Fonte: data.binance.vision, file mensili 2020-01 → 2023-12 (48 per serie). ETCUSDT: candele last
  (`klines`) e mark (`markPriceKlines`) su tutti i 9 timeframe ammessi, funding (`fundingRate`).
  BTCUSDT (riferimento di mercato): candele last sui 9 timeframe. Nessun file oltre il 2023-12 è stato
  chiesto né elencato.
* Il primo scarico si è interrotto con un errore che la sessione non ha potuto leggere (l'uscita era
  in una cartella fuori dai percorsi ammessi); il secondo ha trovato tutti i file presenti e ha
  scaricato i mancanti. Ogni file scaricato dalla rete passa il confronto col CHECKSUM pubblicato da
  Binance prima di essere scritto (un file con impronta diversa non si scrive). Nel secondo giro nessun
  CHECKSUM mancante; quelli eventualmente mancanti del primo giro non si conoscono più.
* Impronte SHA-256 di tutti i file (912 di ETCUSDT, 432 di BTCUSDT) in `impronte.json`, accanto a questo
  file. Impronta di `impronte.json`:
  `abd94aee5effba5b05f4e54b26822b79fe9a8b6f60eae972c6b8eb37607d62bd`.
  A ogni nuova sessione si riscaricano i dati e si confrontano le impronte: se cambiano, STOP.

## Last e mark allineati (`carica_serie_allineate`, timeframe nativi)

| Timeframe | Barre tenute | Tolte dal last (manca il mark) | Tolte dal mark (manca il last) | Buchi dopo l'allineamento |
|---|---|---|---|---|
| 15m | 138.590 | 194 | 6 | 4 |
| 30m | 69.296 | 96 | 3 | 2 |
| 1h | 34.648 | 48 | 2 | 2 |
| 2h | 17.324 | 24 | 1 | 2 |
| 4h | 8.662 | 12 | 1 | 2 |
| 6h | 5.775 | 8 | 0 | 2 |
| 8h | 4.331 | 6 | 1 | 2 |
| 12h | 2.888 | 4 | 0 | 2 |
| 1d | 1.444 | 2 | 0 | 2 |

Intervalli delle barre tolte:
* dal last (il mark manca): **tutto il 2022-10-02** e **tutto il 2023-02-24** (UTC), su ogni timeframe;
  in più sul 15m una barra del 2020-01-19 13:15.
* dal mark (il last manca): le ore del 2020-01-16 prima delle 08:00 (il mark parte prima del last).

Il 2022-10-02 cade nella costruzione, il 2023-02-24 nella validazione. Il motore li vede come buchi e
li conta; un funding caduto nel buco con posizione aperta si addebita sull'ultimo mark disponibile.

## Sospensioni e cambi di contratto

Nessun cambio di simbolo né cucitura: la serie è un solo contratto `ETCUSDT` dal 2020-01-16. Oltre ai due
giorni senza mark (sopra) non ci sono buchi nelle candele last.

## Funding

* 4.337 settlement dal 2020-01-16 08:00 al 2023-12-31 16:00 UTC.
* Intervallo: **8 ore per tutto il periodo** (dalle ore dichiarate nei file e dalla distanza fra
  settlement).
* Tasso medio per settlement: 2020 0,0235%; 2021 0,0233%; 2022 −0,0075%; 2023 0,0093%.

## Volume medio giornaliero in USDT (file 1d del last, colonna quote_volume, tutti i giorni)

| Anno | Volume medio giornaliero | Giorni |
|---|---|---|
| 2020 | 39,9 milioni | 351 |
| 2021 | 573,1 milioni | 365 |
| 2022 | 544,2 milioni | 365 |
| 2023 | 197,5 milioni | 365 |

La fascia di slippage della scheda (0,05% per lato, volume 2023 fra 50 e 200 milioni) è **ottimista per
il 2020**, quando il volume medio era sotto i 50 milioni (la fascia sarebbe stata 0,10%), e prudente per
il 2021-2022. Si dichiara; la prova a costi doppi copre in parte il 2020.

## Mesi sotto la liquidità minima (20 milioni di USDT al giorno)

**2020-06** (14,5 milioni), **2020-09** (19,4 milioni), **2020-10** (13,4 milioni). Tutti nella
costruzione. Altri mesi vicini alla soglia: 2020-04 (22,2) e 2020-07 (24,0).

**Filtro (uguale per `conta_trade`, per il test e per la baseline (a)):** nessuna posizione si apre su un
segnale di una barra che apre in uno di quei mesi (UTC). Una posizione già aperta esce con la sua
uscita. Le stesse barre sono vietate agli ingressi casuali della baseline (b). Elenco in
`codice/mesi_esclusi.json`; codice in `codice/comune.py` (`carica`, `Serie.vietate_liquidita`). Le
date di costruzione e validazione non si spostano.

## Storia utile

Dal 2020-01-16 al 2023-12-31, meno 3 mesi sotto la soglia: circa 3,7 anni, sopra i 2 di
`storia_minima_anni`. La campagna prosegue.
