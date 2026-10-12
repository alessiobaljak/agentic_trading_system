# DYDXUSDT — Fase 0: i dati

Scritto il 2026-10-09. Numeri da `codice/fase0.py` (riepilogo locale `data/insample/DYDXUSDT/fase0_riepilogo.json`,
fuori da git) e da `codice/scarica.py`.

## Periodi (scritti nel log prima dei prezzi, voce DYDXUSDT-N001)

| | |
|---|---|
| Inizio (primo giorno del primo mese della scheda) | 2021-09-01 |
| Giorni fino al 2023-12-31 | 852 |
| Costruzione | 2021-09-01 → 2023-04-19 (596 giorni; `fine_costruzione_ts` = 1681948799999) |
| Validazione | 2023-04-20 → 2023-12-31 (256 giorni) |

**Dichiarazione.** I dati veri cominciano il **2021-09-09** (mark e funding) e il **2021-09-10** (last, prima
barra 1d alle 00:00, 1h alle 03:00): i primi 8-9 giorni della costruzione non hanno barre. Le date non si
spostano (Fase 0, punto 1): la costruzione utile è di circa 587 giorni. Storia utile al 2023-12-31: circa 2,3
anni, sopra `storia_minima_anni` (2): la campagna si fa.

## Fonte e impronte

* data.binance.vision, file mensili da 2021-09 a 2023-12: `klines` e `markPriceKlines` su 15m, 30m, 1h, 2h, 4h,
  6h, 8h, 12h, 1d; `fundingRate`. BTCUSDT: `klines` sugli stessi timeframe, 2021-09 → 2023-12 (riferimento di
  mercato).
* Impronte SHA-256 di ogni file: `impronte_DYDXUSDT.json` (532 file) e `impronte_BTCUSDT.json` (252 file),
  in questa cartella. Impronte di quei due file: `a131749b245a78f3e4c048aa518d5e774db9deb6c3c4a908da61b586dbe66ce6`
  (DYDXUSDT) e `9afced73290ae03a261384177556987b2d7331582d72ae5807deded4b68de6a2` (BTCUSDT).
* Il controllo del CHECKSUM remoto era acceso (scarico di rete) e nessun file ha dato `IntegritaFallita`
  (lo scarico è finito senza errori). L'elenco dei file accettati senza CHECKSUM remoto non è stato letto:
  l'uscita del comando stava in una cartella che il guardiano non fa leggere. Si dichiara.

## Allineamento last-mark (`carica_serie_allineate`, file nativi di ogni timeframe)

| Timeframe | Barre tenute (fino al 2023-12-31) | Tolte dal last (manca il mark) | Tolte dal mark (manca il last) | Buchi dopo l'allineamento |
|---|---|---|---|---|
| 15m | 80.721 | 193 | 78 | 3 |
| 30m | 40.361 | 96 | 39 | 2 |
| 1h | 20.181 | 48 | 19 | 2 |
| 2h | 10.091 | 24 | 9 | 2 |
| 4h | 5.046 | 12 | 4 | 2 |
| 6h | 3.364 | 8 | 3 | 2 |
| 8h | 2.523 | 6 | 2 | 2 |
| 12h | 1.682 | 4 | 2 | 2 |
| 1d | 841 | 2 | 1 | 2 |

Intervalli (uguali su tutti i timeframe, alla loro risoluzione):

* tolte dal last perché manca il mark: **2022-10-02** (giorno intero) e **2023-02-24** (giorno intero); a 15m
  anche la barra 2023-11-10 03:45 (in validazione);
* tolte dal mark perché manca il last: **2021-09-09 08:00 → 2021-09-10 03:xx** (il mark parte prima del last);
* i due giorni interi diventano buchi della serie, contati dal motore (`n_buchi_dati`). Il secondo
  (2023-02-24) e il primo (2022-10-02) sono in costruzione.

## Sospensioni e cambi di contratto

Nessun cambio di contratto o ridenominazione nella serie fino al 2023-12-31 (simbolo unico `DYDXUSDT`, prezzi
continui). Le due giornate senza mark sono le sole interruzioni viste.

## Funding

* 2.530 settlement dal 2021-09-09 16:00 al 2023-12-31 16:00; intervallo **8 ore per tutto il periodo** (sia
  quello dichiarato dal file sia quello dalle distanze).
* Tasso medio per settlement: 2021 +0,0232%, 2022 −0,0050%, 2023 +0,0098%; positivi il 76% dei settlement.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele 1d del last, tutti i giorni):
2021 (da settembre): 425 milioni; 2022: 158 milioni; 2023: 201 milioni.

| Mese | Milioni USDT/giorno | Mese | Milioni USDT/giorno |
|---|---|---|---|
| 2021-09 | 670 | 2022-11 | 325 |
| 2021-10 | 580 | 2022-12 | 153 |
| 2021-11 | 293 | 2023-01 | 283 |
| 2021-12 | 233 | 2023-02 | 497 |
| 2022-01 | 249 | 2023-03 | 365 |
| 2022-02 | 156 | 2023-04 | 163 |
| 2022-03 | 116 | 2023-05 | 99 |
| 2022-04 | 125 | 2023-06 | 112 |
| 2022-05 | 154 | 2023-07 | 105 |
| 2022-06 | 74 | 2023-08 | 113 |
| 2022-07 | 249 | 2023-09 | 68 |
| 2022-08 | 113 | 2023-10 | 98 |
| 2022-09 | 68 | 2023-11 | 278 |
| 2022-10 | 116 | 2023-12 | 255 |

**Mesi sotto `liquidita_minima_usdt_giorno` (20 milioni): nessuno.** Il filtro di liquidità esiste nel codice
(`comune.py`, `vietata_liquidita`) ma non toglie nessuna barra.

Fascia di slippage della scheda: 0,02% per lato (volume 2023 fra 200 milioni e 1 miliardo). Nel 2022 il volume
medio (158 milioni) cadeva nella fascia 0,05%: per la costruzione la fascia è ottimista (lezioni/metodo.md);
lo copre in parte il test a costi doppi. Si dichiara.

## Scala dei movimenti (per le previsioni al netto dei costi)

ATR(14) di Wilder diviso il close, mediana sulla costruzione, e costo di un giro (0,14%) in R con uno stop a 2 ATR:

| Timeframe | ATR/close mediano | Costo in R con stop 2 ATR |
|---|---|---|
| 15m | 0,99% | 0,071 |
| 30m | 1,43% | 0,049 |
| 1h | 2,06% | 0,034 |
| 2h | 2,98% | 0,023 |
| 4h | 4,39% | 0,016 |
| 6h | 5,48% | 0,013 |
| 8h | 6,45% | 0,011 |
| 12h | 8,08% | 0,009 |
| 1d | 12,11% | 0,006 |

Uno stop a 2 ATR supera il 6% (`stop_massimo_bot`) quasi sempre da 4h in su: le varianti lente non sono
eseguibili dal bot così come sono (da dichiarare in consegna).

## Prezzo

Primo open 1d (2021-09-10): 13,27 USDT; ultimo close (2023-12-31): 2,95 USDT.
