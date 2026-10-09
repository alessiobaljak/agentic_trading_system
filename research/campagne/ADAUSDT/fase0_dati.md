# ADAUSDT — Fase 0: i dati

Scritto il 2026-10-09 dalla sessione di campagna (protocollo 4.5). Codice: `codice/periodi.py`,
`codice/scarica.py`, `codice/fase0.py`, `codice/impronte.py`. Numeri ricavati da quei programmi
sui file scaricati; nessun dato oltre il 2023-12-31.

## Periodi (scritti nel log prima di caricare i prezzi, voce ADAUSDT-N004)

`periodi_campagna(2020-01-01)` (primo mese di dati della scheda: 2020-01):

| | |
|---|---|
| inizio | 2020-01-01 (1.461 giorni fino al 2023-12-31) |
| costruzione | 2020-01-01 → 2022-10-18 (1.022 giorni), `fine_costruzione_ts` = 1666137599999 |
| validazione | 2022-10-19 → 2023-12-31 |

I dati veri cominciano dopo l'inizio dichiarato (sotto): le date non si spostano, la differenza si
dichiara (lezione di metodo).

## Fonte, file e impronte

data.binance.vision, file mensili da 2020-01 a 2023-12: klines e markPriceKlines di ADAUSDT su
15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d; fundingRate di ADAUSDT; klines di BTCUSDT sugli stessi nove
timeframe (solo riferimento di mercato). 1.344 file richiesti, 1.344 presenti, nessun mese assente,
nessun errore, nessun CHECKSUM remoto mancante (ogni zip controllato contro il suo `.CHECKSUM`).

Impronte SHA-256 dei 912 file di ADAUSDT e dei 432 di BTCUSDT in `impronte.json` (accanto a
questo file). Impronta di `impronte.json`:
`7d3b9d8915a35db71127933fca3c38d8edf121402772d360ee795f3523ef2911`.
A ogni nuova sessione: `python research/campagne/ADAUSDT/codice/scarica.py` e poi
`python research/campagne/ADAUSDT/codice/impronte.py verifica` (deve dire 0 differenze; altrimenti STOP).

## Inizio reale dei dati

* Last price (klines): prima barra 2020-01-31 00:00 UTC (1d) / 08:00 UTC (timeframe infragiornalieri
  dopo l'allineamento). Il file di gennaio 2020 contiene solo il 31 gennaio.
* Mark price: dal 2020-01-19. Le barre di mark dal 2020-01-19 al 2020-01-31 non hanno il last e sono
  tolte dall'allineamento (sotto).
* Funding: primo settlement 2020-01-19 16:00 UTC.

Quindi la costruzione utile va dal 2020-01-31 al 2022-10-18 (circa 2,7 anni), di cui marzo e aprile
2020 esclusi per liquidità (sotto).

## Allineamento last/mark (`carica_serie_allineate`, file nativi di ogni timeframe)

| timeframe | barre tenute | barre di calendario 2020-2023 | tolte dal last (mark assente) | tolte dal mark (last assente) |
|---|---|---|---|---|
| 15m | 137.151 | 140.256 | 193 | 1.147 |
| 30m | 68.576 | 70.128 | 96 | 574 |
| 1h | 34.288 | 35.064 | 48 | 287 |
| 2h | 17.144 | 17.532 | 24 | 144 |
| 4h | 8.572 | 8.766 | 12 | 72 |
| 6h | 5.715 | 5.844 | 8 | 48 |
| 8h | 4.286 | 4.383 | 6 | 36 |
| 12h | 2.858 | 2.922 | 4 | 24 |
| 1d | 1.429 | 1.461 | 2 | 12 |

Intervalli delle barre tolte:

* dal last, perché manca il mark: tutto il 2022-10-02 e tutto il 2023-02-24 (su ogni timeframe);
  a 15m anche la barra del 2023-11-10 03:45.
* dal mark, perché manca il last: dal 2020-01-19 al 2020-01-31 (prima che esista il last).

Dopo l'allineamento restano questi buchi nella serie (il motore li conta): 2022-10-02 (dentro la
costruzione), 2023-02-24 (validazione) e, a 15m, 2023-11-10 03:45 (validazione). Nessun volume
mancante sulle barre tenute. Nessun cambio di contratto né sospensione oltre a questi due giorni
senza mark price.

BTCUSDT (riferimento): serie completa su ogni timeframe (140.256 barre a 15m ... 1.461 a 1d).

## Funding

4.327 settlement dal 2020-01-19 16:00 al 2023-12-31 16:00, intervallo di 8 ore per tutto il periodo
(dichiarato dal file e uguale alla distanza fra settlement). Tasso medio per settlement: 2020
+0,0240%, 2021 +0,0365%, 2022 −0,0009%, 2023 +0,0066%.

## Volume e liquidità (`volume_usdt_da_zip` sui file 1d del last, tutti i giorni)

Volume medio giornaliero in USDT per anno: 2020 60,1 milioni; 2021 1.111 milioni; 2022 501 milioni;
2023 272 milioni.

Mesi sotto `liquidita_minima_usdt_giorno` (20 milioni): **2020-01** (13,1 milioni, un solo giorno di
dati), **2020-03** (10,5 milioni), **2020-04** (10,3 milioni). 2020-02 è a 22,4 milioni, 2020-05 a 33,1.

**Filtro scritto qui, uguale per `conta_trade`, per il test e per la baseline (a):** una variante non
apre posizioni su segnali di barre che APRONO in gennaio, marzo o aprile 2020 (UTC). Le stesse barre
vanno in `barre_vietate` della baseline (b). Una posizione già aperta esce con la sua uscita. I mesi
non si tolgono dalla serie (gli indicatori li vedono).

**Fascia di slippage:** 0,02% per lato (scheda, volume del 2023). Nel 2020 il volume medio (60
milioni) era nella fascia 0,05%: per i trade del 2020 i costi del backtest sono ottimisti; il test a
costi doppi copre solo in parte. Nel 2021 (oltre 1 miliardo) la fascia sarebbe stata 0,01%.

## Storia utile

Circa 3,9 anni di dati prima del 2024 (dal 2020-01-31): sopra `storia_minima_anni` (2). La campagna
prosegue.
