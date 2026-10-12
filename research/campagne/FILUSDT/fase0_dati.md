# Fase 0 — I dati di FILUSDT

Scritto il 2026-10-09 dalla sessione di campagna, dai calcoli di `codice/fase0.py`
(risultati completi in `fase0_calcoli.json`) e dallo scarico di `codice/scarica.py`.

## Periodi (scritti nel log prima di caricare i prezzi, voce FILUSDT-N004)

| | Valore |
|---|---|
| Inizio dell'in-sample (primo mese della scheda) | 2020-10-01 |
| Giorni fino al 2023-12-31 | 1.187 |
| Costruzione | 2020-10-01 → 2023-01-08 (830 giorni; `fine_costruzione_ts` = 1673222399999) |
| Validazione | 2023-01-09 → 2023-12-31 |

La prima barra disponibile è del **2020-10-16** (00:00 UTC per 4h, 8h, 12h e 1d; 06:00 UTC per
15m, 30m, 1h, 2h e 6h dopo l'allineamento col mark): i primi 15 giorni del periodo non hanno
dati. Le date dei periodi non si spostano (Fase 0, punto 1): la costruzione ha quindi circa 815
giorni di dati veri, non 830.

## Fonte e impronte

* Fonte: data.binance.vision, file mensili USDS-M dal 2020-10 al 2023-12 (39 mesi): candele
  `klines` (last) e `markPriceKlines` (mark) su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, e
  `fundingRate`. Per il riferimento di mercato, le candele `klines` di BTCUSDT sugli stessi 9
  timeframe e mesi. In tutto 1.092 file (FILUSDT 741, BTCUSDT 351); nessun mese mancante.
* Il CHECKSUM pubblicato da Binance accanto a ogni zip è stato confrontato con il file scaricato:
  combacia per tutti; nessun CHECKSUM mancante.
* Le impronte SHA-256 dei 1.092 file sono in `impronte.json` (cartella della campagna).
  **Impronta di `impronte.json`: `f6afc58012b218c8b9fcfe86a8596a910ce232506dd17e37518071e1152931aa`.**
  A ogni nuova sessione, dopo il riscaricamento: `python codice/impronte.py verifica` deve dare
  una lista vuota; altrimenti STOP.
* Nessun file successivo al 2023-12 è stato richiesto o elencato.

## Buchi nei dati

Nessun buco nelle candele di BTCUSDT. Per FILUSDT i buchi sono giorni interi, gli stessi su
tutti i timeframe:

| Serie | Giorni mancanti |
|---|---|
| last (`klines`) | 2022-02-26 → 2022-02-28 (3 giorni); 2022-04-01 → 2022-04-02 (2 giorni) |
| mark (`markPriceKlines`) | 2022-10-02 (1 giorno); 2023-02-24 (1 giorno); a 15m anche la barra del 2023-11-10 03:45 |

Non ci sono cambi di contratto né ricuciture: il simbolo è lo stesso per tutto il periodo. I
buchi del last non sono distinguibili, dai soli file, da una sospensione delle negoziazioni: si
trattano come buchi (il motore li conta; i settlement di funding caduti in un buco con posizione
aperta si addebitano sull'ultimo mark e si contano).

## Allineamento last-mark (`carica_serie_allineate`, intersezione delle barre)

Barre tolte su tutto l'in-sample (2020-10-01 → 2023-12-31). «Tolte dal last» = barre del last
senza mark; «tolte dal mark» = barre del mark senza last.

| Timeframe | Barre tenute | Tolte dal last | Intervalli tolti dal last | Tolte dal mark | Intervalli tolti dal mark |
|---|---|---|---|---|---|
| 15m | 111.815 | 193 | 2022-10-02 (96), 2023-02-24 (96), 2023-11-10 03:45 (1) | 493 | 2020-10-16 02:45-05:45 (13), 2022-02-26→28 (288), 2022-04-01→02 (192) |
| 30m | 55.908 | 96 | 2022-10-02, 2023-02-24 | 247 | 2020-10-16 02:30-05:30 (7), 2022-02-26→28, 2022-04-01→02 |
| 1h | 27.954 | 48 | 2022-10-02, 2023-02-24 | 124 | 2020-10-16 02:00-05:00 (4), 2022-02-26→28, 2022-04-01→02 |
| 2h | 13.977 | 24 | 2022-10-02, 2023-02-24 | 62 | 2020-10-16 02:00-04:00 (2), 2022-02-26→28, 2022-04-01→02 |
| 4h | 6.989 | 12 | 2022-10-02, 2023-02-24 | 31 | 2020-10-16 00:00 (1), 2022-02-26→28, 2022-04-01→02 |
| 6h | 4.659 | 8 | 2022-10-02, 2023-02-24 | 21 | 2020-10-16 00:00 (1), 2022-02-26→28, 2022-04-01→02 |
| 8h | 3.495 | 6 | 2022-10-02, 2023-02-24 | 15 | 2022-02-26→28, 2022-04-01→02 |
| 12h | 2.330 | 4 | 2022-10-02, 2023-02-24 | 10 | 2022-02-26→28, 2022-04-01→02 |
| 1d | 1.165 | 2 | 2022-10-02, 2023-02-24 | 5 | 2022-02-26→28, 2022-04-01→02 |

Il volume in USDT (`quote_volume`) è presente per tutte le barre tenute (0 mancanti). Il giorno
2023-02-24 cade nel periodo di validazione; gli altri buchi nel periodo di costruzione.

## Funding

* 3.515 settlement dal 2020-10-16 08:00 al 2023-12-31 16:00 UTC.
* Intervallo: **8 ore per tutto il periodo** (dichiarato nei file e confermato dalla distanza fra
  settlement).
* Tasso medio 0,0054% per settlement, mediano 0,0100%; positivo nell'84% dei settlement.
* Media per anno: 2020 **−0,148%** (molto negativa: nei primi due mesi e mezzo di vita del
  contratto i long incassavano molto), 2021 +0,036%, 2022 +0,002%, 2023 +0,011%.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere del last, tutti
i giorni, `volume_usdt_da_zip`):

| Anno | Volume medio giornaliero |
|---|---|
| 2020 (dal 16 ottobre) | 82 milioni |
| 2021 | 390 milioni |
| 2022 | 190 milioni |
| 2023 | 221 milioni |

Mese più basso: 2020-12 con 36,9 milioni; poi 2021-01 (47,9 milioni) e 2020-11 (56,2 milioni).
**Nessun mese è sotto la soglia di 20 milioni di USDT al giorno**: il filtro di liquidità non
esclude nessuna barra (`mesi_esclusi.json` è vuoto).

La fascia di slippage della scheda (0,02% per lato) vale per volumi da 200 milioni a 1 miliardo;
nel 2020 e nei mesi 2020-11 → 2021-01 il volume era nella fascia 20-50 o 50-200 milioni, dove lo
slippage del protocollo sarebbe 0,10% o 0,05%: lo slippage di quei mesi è probabilmente
sottostimato (lezioni di metodo: la fascia del 2023 può essere ottimista per gli anni prima).
La prova a costi doppi lo copre solo in parte; per ogni candidato si dichiara la quota di trade
in quei mesi.

## Storia utile

Dal 2020-10-16 al 2023-12-31: 3 anni e 2 mesi e mezzo, sopra i 2 anni di `storia_minima_anni`.
La campagna prosegue.
