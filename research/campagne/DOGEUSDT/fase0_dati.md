# Fase 0 — I dati di DOGEUSDT

Scritto il 9 ottobre 2026 dalla sessione di campagna. Numeri prodotti da `codice/fase0.py`
(copia in `data/insample/DOGEUSDT/fase0_numeri.json`, fuori da git).

## Periodi (scritti nel log prima di caricare i prezzi)

| | |
|---|---|
| Primo mese di dati (scheda) | 2020-07 |
| Inizio | 2020-07-01 (prima barra presente nell'archivio: 2020-07-10 00:00 UTC) |
| Giorni fino al 2023-12-31 | 1.279 |
| Costruzione | 2020-07-01 → 2022-12-12 (895 giorni), `fine_costruzione_ts` = 1670889599999 |
| Validazione | 2022-12-13 → 2023-12-31 |

## File scaricati e impronte

* Fonte: data.binance.vision, file mensili, dal 2020-07 al 2023-12. DOGEUSDT: klines e
  markPriceKlines su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d (42 mesi ciascuno) e fundingRate
  (42 mesi): 798 file. BTCUSDT (solo riferimento di mercato): klines sugli stessi 9 timeframe,
  378 file.
* Il CHECKSUM pubblicato da Binance è stato controllato su ogni file allo scarico: nessun
  CHECKSUM mancante.
* Impronte SHA-256 dei file: `impronte_DOGEUSDT.json` (impronta del file
  `35b3b4232273b807b31d9d02f9d763d3100263bd050e34b6ad115f343a62afb3`) e
  `impronte_BTCUSDT.json` (`99245a4df590eb3f18c1b633530e56503184971d78b9042a0e92122afb2e68a0`).
  A ogni nuova sessione si riscaricano i file e si controllano con `verifica_impronte`.
* Il primo scarico si è interrotto per un errore non letto dopo circa 500 file; il secondo ha
  completato gli altri. I file già scritti erano stati controllati col CHECKSUM.

## Last e mark allineati (`carica_serie_allineate`, file nativi di ogni timeframe)

| Timeframe | Barre tenute | di cui in costruzione | Barre tolte dal last (mark mancante) | Barre tolte dal mark (last mancante) |
|---|---|---|---|---|
| 15m | 121.691 | 84.924 | 193: 2022-10-02 intero, 2023-02-24 intero, 2023-11-10 03:45 | 24: 2020-07-10 03:00-08:45 |
| 30m | 60.846 | 42.462 | 96: 2022-10-02, 2023-02-24 | 12: 2020-07-10 03:00-08:30 |
| 1h | 30.423 | 21.231 | 48: 2022-10-02, 2023-02-24 | 6: 2020-07-10 03:00-08:00 |
| 2h | 15.212 | 10.616 | 24: idem | 3: 2020-07-10 02:00-06:00 |
| 4h | 7.606 | 5.308 | 12: idem | 2: 2020-07-10 00:00-04:00 |
| 6h | 5.071 | 3.539 | 8: idem | 1: 2020-07-10 00:00 |
| 8h | 3.803 | 2.654 | 6: idem | 1: 2020-07-10 00:00 |
| 12h | 2.536 | 1.770 | 4: idem | 0 |
| 1d | 1.268 | 885 | 2: 2022-10-02, 2023-02-24 | 0 |

Dopo l'allineamento restano due buchi (i due giorni senza mark, uno in costruzione e uno in
validazione) e a 15m una barra singola il 2023-11-10. Il motore li conta (`n_buchi_dati`). Le
prime ore del 2020-07-10 hanno il last senza il mark: la serie allineata parte dalla prima barra
con entrambi. Nessun buco nel last stesso, nessun cambio di contratto o ridenominazione visto
nei dati (la serie è continua dal 2020-07-10).

## Funding

3.809 settlement dal 2020-07-10 08:00 al 2023-12-31 16:00, sempre a 8 ore (colonna
dell'intervallo e distanze fra settlement concordano). Tasso medio 0,0148% a settlement; 8,7%
dei settlement ≥ 0,05%, 14,9% negativi (dati di tutto l'in-sample, costruzione e validazione).

## Volume medio giornaliero in USDT (colonna `quote_volume` delle candele 1d del last)

| Anno | Volume medio giornaliero |
|---|---|
| 2020 (da luglio) | 8,1 milioni |
| 2021 | 1.452 milioni |
| 2022 | 669 milioni |
| 2023 | 519 milioni |

## Mesi sotto la liquidità minima (20 milioni di USDT al giorno)

**Tutti i mesi del 2020: da luglio a dicembre** (medie fra 2,9 e 14,0 milioni). Dal gennaio 2021
ogni mese è sopra (minimo 113,6 milioni nel marzo 2021).

Filtro (uguale per `conta_trade`, per il test e per la (a); le stesse barre vanno fra le vietate
della (b)): nessun ingresso su segnali di barre che aprono in un mese escluso. Una posizione già
aperta esce con la sua uscita. Le date di costruzione e validazione non si spostano: la
costruzione utile per gli ingressi va quindi dal 2021-01-01 al 2022-12-12 (711 giorni), e lo
si dichiara. La storia utile (2021-01 → 2023-12, 3 anni) resta sopra `storia_minima_anni` (2):
nessuno STOP.

## Slippage

Fascia della scheda: 0,02% per lato (volume medio 2023). Il volume del 2021 e del 2022 era più
alto di quello del 2023, quindi per gli anni di costruzione utili la fascia è prudente o giusta;
il 2020, sotto la soglia, è escluso dagli ingressi.

## Controllo positivo degli strumenti

Fatto prima della prima variante (nota del log): una strategia a 1 ora che guarda la barra
dopo il segnale batte nettamente la (a) e la (b) (`t` contro la (b) 57,1) e crolla col ritardo di
una barra (`t` 2,7). Gli strumenti vedono un vantaggio vero e lo perdono quando sparisce.
