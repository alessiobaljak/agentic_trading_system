# Fase 0 — i dati del paniere

Scritto da `codice/fase0_scrivi_md.py` con i numeri di `codice/fase0_dati.py` (`lavoro/fase0_dati.json`), `codice/scarico.py` (`lavoro/scarico_esito.json`) e `codice/fase0_periodi.py` (`lavoro/fase0_periodi.json`). Solo funzioni di `research/src/dati.py`; solo candele giornaliere di last e mark e funding, dal primo mese della scheda al 2023-12-31 (BTCUSDT dal 2020-01).

## Scarico e impronte

* File scaricati e presenti: 9310 su 9327 mesi chiesti; mesi assenti alla fonte (404): 17; errori dopo 3 tentativi: 0; file accettati senza CHECKSUM remoto: 0.
* Confronto con `impronte_1d.json` (`dati.verifica_impronte`), sulle serie 1d e funding: simboli con differenze o file mancanti: nessuno; file su disco non registrati: nessuno. Le impronte valgono quelle di `impronte_1d.json` (regole.md, sezione 2): non si riscrivono.
* Registrati in `impronte_1d.json` e NON scaricati: BTCUSDT, 96 file a 8 ore (da `klines/8h/BTCUSDT-8h-2020-01.zip` a `markPriceKlines/8h/BTCUSDT-8h-2023-12.zip`): le regole del paniere (sezione 2) vietano ogni timeframe diverso da 1d. Domanda all'utente nel log (PANIERE-006).
* Mesi assenti alla fonte: ICPUSDT fundingRate  2021-05, ICPUSDT fundingRate  2021-06, ICPUSDT fundingRate  2021-07, ICPUSDT fundingRate  2021-08, ICPUSDT fundingRate  2021-09, ICPUSDT fundingRate  2021-10, ICPUSDT fundingRate  2021-11, ICPUSDT fundingRate  2021-12, ICPUSDT fundingRate  2022-01, ICPUSDT fundingRate  2022-02, ICPUSDT fundingRate  2022-03, ICPUSDT fundingRate  2022-04, ICPUSDT fundingRate  2022-05, ICPUSDT fundingRate  2022-06, ICPUSDT fundingRate  2022-07, ICPUSDT fundingRate  2022-08, QTUMUSDT fundingRate  2020-02. Sono tutti mesi di funding: il motore non addebita funding in quei mesi (regole del gruppo, sezione 2, punto 9).

## Periodi (lavoro/fase0_periodi.json, voce PANIERE-005 del log)

Costruzione fino al 2023-01-16 compreso, validazione dal 2023-01-17 al 2023-12-31 (349 giorni). Giorni-moneta 93167, obiettivo 65216, di costruzione 65247.

## Storia, buchi, allineamento

* Controllo della storia (regole del gruppo, sezione 2, punto 9: prima barra in entrambe le serie prima del 2022-01-01): 80 su 80 superano.
* Monete con la prima barra vera dopo il primo giorno della scheda: 78 su 80 (la prima candela giornaliera può essere parziale, `lezioni/metodo.md`):
  * 1000XECUSDT: scheda 2021-09-01, prima barra allineata 2021-09-17
  * 1INCHUSDT: scheda 2020-12-01, prima barra allineata 2020-12-25
  * AAVEUSDT: scheda 2020-10-01, prima barra allineata 2020-10-16
  * ALGOUSDT: scheda 2020-06-01, prima barra allineata 2020-06-16
  * ALPHAUSDT: scheda 2020-11-01, prima barra allineata 2020-11-23
  * ANKRUSDT: scheda 2021-01-01, prima barra allineata 2021-01-26
  * ARPAUSDT: scheda 2021-10-01, prima barra allineata 2021-10-19
  * ARUSDT: scheda 2021-09-01, prima barra allineata 2021-09-28
  * ATOMUSDT: scheda 2020-02-01, prima barra allineata 2020-02-07
  * AUDIOUSDT: scheda 2021-08-01, prima barra allineata 2021-08-19
  * AXSUSDT: scheda 2020-11-01, prima barra allineata 2020-11-20
  * BAKEUSDT: scheda 2021-05-01, prima barra allineata 2021-05-19
  * BANDUSDT: scheda 2020-07-01, prima barra allineata 2020-07-29
  * BELUSDT: scheda 2020-11-01, prima barra allineata 2020-11-18
  * BLZUSDT: scheda 2020-09-01, prima barra allineata 2020-09-17
  * C98USDT: scheda 2021-08-01, prima barra allineata 2021-08-24
  * CELOUSDT: scheda 2021-09-01, prima barra allineata 2021-09-27
  * CELRUSDT: scheda 2021-03-01, prima barra allineata 2021-03-29
  * CHZUSDT: scheda 2021-01-01, prima barra allineata 2021-01-21
  * COMPUSDT: scheda 2020-06-01, prima barra allineata 2020-06-30
  * CTSIUSDT: scheda 2021-10-01, prima barra allineata 2021-10-26
  * DASHUSDT: scheda 2020-02-01, prima barra allineata 2020-02-04
  * DOTUSDT: scheda 2020-08-01, prima barra allineata 2020-08-22
  * EGLDUSDT: scheda 2020-09-01, prima barra allineata 2020-09-14
  * ENJUSDT: scheda 2020-09-01, prima barra allineata 2020-09-29
  * EOSUSDT: scheda 2020-01-01, prima barra allineata 2020-01-08
  * FLMUSDT: scheda 2020-09-01, prima barra allineata 2020-09-29
  * GRTUSDT: scheda 2020-12-01, prima barra allineata 2020-12-19
  * GTCUSDT: scheda 2021-06-01, prima barra allineata 2021-06-11
  * HBARUSDT: scheda 2021-03-01, prima barra allineata 2021-03-17
  * ICPUSDT: scheda 2021-05-01, prima barra allineata 2021-05-11
  * ICXUSDT: scheda 2020-09-01, prima barra allineata 2020-09-15
  * IOTAUSDT: scheda 2020-02-01, prima barra allineata 2020-02-12
  * KAVAUSDT: scheda 2020-07-01, prima barra allineata 2020-07-28
  * KLAYUSDT: scheda 2021-10-01, prima barra allineata 2021-10-12
  * KNCUSDT: scheda 2020-06-01, prima barra allineata 2020-06-22
  * KSMUSDT: scheda 2020-10-01, prima barra allineata 2020-10-14
  * LINAUSDT: scheda 2021-03-01, prima barra allineata 2021-03-19
  * LPTUSDT: scheda 2021-11-01, prima barra allineata 2021-11-11
  * LRCUSDT: scheda 2020-10-01, prima barra allineata 2020-10-19
  * MANAUSDT: scheda 2021-03-01, prima barra allineata 2021-03-15
  * MKRUSDT: scheda 2020-08-01, prima barra allineata 2020-08-13
  * MTLUSDT: scheda 2021-03-01, prima barra allineata 2021-03-31
  * NEARUSDT: scheda 2020-10-01, prima barra allineata 2020-10-15
  * NEOUSDT: scheda 2020-02-01, prima barra allineata 2020-02-17
  * NKNUSDT: scheda 2021-04-01, prima barra allineata 2021-04-09
  * OCEANUSDT: scheda 2020-11-01, prima barra allineata 2020-11-03
  * OMGUSDT: scheda 2020-07-01, prima barra allineata 2020-07-02
  * ONTUSDT: scheda 2020-02-01, prima barra allineata 2020-02-11
  * PEOPLEUSDT: scheda 2021-12-01, prima barra allineata 2021-12-24
  * QTUMUSDT: scheda 2020-02-01, prima barra allineata 2020-02-20
  * RENUSDT: scheda 2020-10-01, prima barra allineata 2020-10-13
  * RLCUSDT: scheda 2020-07-01, prima barra allineata 2020-07-31
  * ROSEUSDT: scheda 2021-12-01, prima barra allineata 2021-12-31
  * RUNEUSDT: scheda 2020-09-01, prima barra allineata 2020-09-04
  * SANDUSDT: scheda 2021-01-01, prima barra allineata 2021-01-25
  * SFPUSDT: scheda 2021-02-01, prima barra allineata 2021-02-24
  * SKLUSDT: scheda 2020-12-01, prima barra allineata 2020-12-08
  * SNXUSDT: scheda 2020-08-01, prima barra allineata 2020-08-14
  * STMXUSDT: scheda 2021-03-01, prima barra allineata 2021-03-22
  * STORJUSDT: scheda 2020-09-01, prima barra allineata 2020-09-16
  * SUSHIUSDT: scheda 2020-09-01, prima barra allineata 2020-09-04
  * SXPUSDT: scheda 2020-07-01, prima barra allineata 2020-07-21
  * THETAUSDT: scheda 2020-05-01, prima barra allineata 2020-05-27
  * TOMOUSDT: scheda 2020-10-01, prima barra allineata 2020-10-12
  * TRXUSDT: scheda 2020-01-01, prima barra allineata 2020-01-15
  * UNFIUSDT: scheda 2021-02-01, prima barra allineata 2021-02-19
  * UNIUSDT: scheda 2020-09-01, prima barra allineata 2020-09-18
  * VETUSDT: scheda 2020-02-01, prima barra allineata 2020-02-14
  * WAVESUSDT: scheda 2020-08-01, prima barra allineata 2020-08-12
  * XEMUSDT: scheda 2021-03-01, prima barra allineata 2021-03-03
  * XLMUSDT: scheda 2020-01-01, prima barra allineata 2020-01-20
  * XMRUSDT: scheda 2020-02-01, prima barra allineata 2020-02-03
  * XTZUSDT: scheda 2020-02-01, prima barra allineata 2020-02-06
  * YFIUSDT: scheda 2020-08-01, prima barra allineata 2020-08-31
  * ZECUSDT: scheda 2020-02-01, prima barra allineata 2020-02-05
  * ZILUSDT: scheda 2020-06-01, prima barra allineata 2020-06-18
  * ZRXUSDT: scheda 2020-06-01, prima barra allineata 2020-06-24
* Barre tolte dall'allineamento (presenti nel last e non nel mark): 418 in tutto; presenti nel mark e non nel last: 260. Dettaglio per moneta nella tabella e, con le date, in `lavoro/fase0_dati.json`.
* Giorni tolti su 5 monete o più (lo stesso giorno senza mark su molte monete): 2021-07-01 (46), 2021-07-24..2021-07-27 (46), 2022-07-31 (24), 2022-10-02 (81), 2023-02-24 (81).

## Tabella per moneta

Colonne: mesi attesi; mesi mancanti di last, mark e funding; barre allineate; barre tolte (solo last / solo mark; fra parentesi quelle in validazione); giorni mancanti nel last fra la prima e l'ultima barra; intervalli del funding (ore, da quando); volume medio giornaliero in milioni di USDT per anno; mesi sotto i 20 milioni (costruzione / validazione); slippage per lato della scheda.

| Moneta | Mesi | Manc. last/mark/funding | Barre | Tolte last/mark (val.) | Giorni manc. last | Funding | Volume per anno (M USDT) | Mesi sotto soglia c/v | Slippage |
|---|---|---|---|---|---|---|---|---|---|
| 1000XECUSDT | 28 | 0/0/0 | 833 | 3/0 (1) | 0 | 8h dal 2021-09-17 | 2021: 41, 2022: 22, 2023: 27 | 8/9 | 0.10% |
| 1INCHUSDT | 37 | 0/0/0 | 1100 | 2/0 (1) | 0 | 8h dal 2020-12-25 | 2020: 116, 2021: 129, 2022: 46, 2023: 39 | 0/3 | 0.10% |
| AAVEUSDT | 39 | 0/0/0 | 1170 | 2/0 (1) | 0 | 8h dal 2020-10-16 | 2020: 56, 2021: 225, 2022: 128, 2023: 69 | 0/0 | 0.05% |
| ALGOUSDT | 43 | 0/0/0 | 1292 | 2/15 (1) | 0 | 8h dal 2020-06-01 | 2020: 23, 2021: 155, 2022: 100, 2023: 44 | 4/0 | 0.10% |
| ALPHAUSDT | 38 | 0/0/0 | 1132 | 2/0 (1) | 0 | 8h dal 2020-11-23 | 2020: 9, 2021: 77, 2022: 32, 2023: 49 | 8/4 | 0.10% |
| ANKRUSDT | 36 | 0/0/0 | 1062 | 8/1 (1) | 0 | 8h dal 2021-01-25 | 2021: 72, 2022: 37, 2023: 43 | 4/4 | 0.10% |
| ARPAUSDT | 27 | 0/0/0 | 802 | 2/0 (1) | 0 | 8h dal 2021-10-19 | 2021: 85, 2022: 25, 2023: 71 | 6/5 | 0.05% |
| ARUSDT | 28 | 0/0/0 | 822 | 3/1 (1) | 0 | 8h dal 2021-09-27 | 2021: 79, 2022: 45, 2023: 21 | 2/7 | 0.10% |
| ATOMUSDT | 47 | 0/0/0 | 1421 | 3/1 (1) | 0 | 8h dal 2020-02-06 | 2020: 18, 2021: 228, 2022: 332, 2023: 120 | 6/0 | 0.05% |
| AUDIOUSDT | 29 | 0/0/0 | 862 | 3/0 (1) | 0 | 8h dal 2021-08-19 | 2021: 74, 2022: 41, 2023: 34 | 3/7 | 0.10% |
| AXSUSDT | 38 | 0/0/0 | 1129 | 8/0 (1) | 0 | 8h dal 2020-11-20 | 2020: 13, 2021: 584, 2022: 239, 2023: 105 | 3/0 | 0.05% |
| BAKEUSDT | 32 | 0/0/0 | 955 | 2/0 (1) | 0 | 8h dal 2021-05-19 | 2021: 82, 2022: 36, 2023: 69 | 5/6 | 0.05% |
| BANDUSDT | 42 | 0/0/0 | 1243 | 8/0 (1) | 0 | 8h dal 2020-07-29 | 2020: 54, 2021: 52, 2022: 68, 2023: 29 | 3/3 | 0.10% |
| BELUSDT | 38 | 0/0/0 | 1137 | 2/0 (1) | 0 | 8h dal 2020-11-18 | 2020: 10, 2021: 48, 2022: 69, 2023: 38 | 8/6 | 0.10% |
| BLZUSDT | 40 | 0/0/0 | 1193 | 8/1 (1) | 0 | 8h dal 2020-09-16; 4h dal 2023-08-14; 8h dal 2023-08-31; 4h dal 2023-09-05; 8h dal 2023-09-13; 4h dal 2023-10-12 | 2020: 4, 2021: 48, 2022: 43, 2023: 95 | 11/6 | 0.05% |
| C98USDT | 29 | 0/0/0 | 858 | 2/0 (1) | 0 | 8h dal 2021-08-24 | 2021: 192, 2022: 40, 2023: 37 | 1/4 | 0.10% |
| CELOUSDT | 28 | 0/0/0 | 824 | 2/0 (1) | 0 | 8h dal 2021-09-27 | 2021: 34, 2022: 43, 2023: 46 | 5/0 | 0.10% |
| CELRUSDT | 34 | 0/0/0 | 1006 | 2/0 (1) | 0 | 8h dal 2021-03-29 | 2021: 112, 2022: 45, 2023: 25 | 7/8 | 0.10% |
| CHZUSDT | 36 | 0/0/0 | 1073 | 2/20 (1) | 0 | 8h dal 2021-01-01 | 2021: 252, 2022: 226, 2023: 55 | 1/2 | 0.05% |
| COMPUSDT | 43 | 0/0/0 | 1272 | 8/0 (1) | 0 | 8h dal 2020-06-30 | 2020: 29, 2021: 74, 2022: 42, 2023: 95 | 4/2 | 0.05% |
| CRVUSDT | 40 | 0/0/0 | 1209 | 8/0 (1) | 0 | 8h dal 2020-09-01 | 2020: 44, 2021: 157, 2022: 167, 2023: 131 | 0/0 | 0.05% |
| CTSIUSDT | 27 | 0/0/0 | 794 | 3/0 (1) | 0 | 8h dal 2021-10-26 | 2021: 77, 2022: 18, 2023: 47 | 10/8 | 0.10% |
| DASHUSDT | 47 | 0/0/0 | 1425 | 2/0 (1) | 0 | 8h dal 2020-02-04 | 2020: 11, 2021: 73, 2022: 35, 2023: 24 | 12/7 | 0.10% |
| DOTUSDT | 41 | 0/0/0 | 1219 | 8/2 (1) | 0 | 8h dal 2020-08-20 | 2020: 86, 2021: 750, 2022: 303, 2023: 158 | 0/0 | 0.05% |
| EGLDUSDT | 40 | 0/0/0 | 1202 | 2/1 (1) | 0 | 8h dal 2020-09-13 | 2020: 18, 2021: 111, 2022: 68, 2023: 40 | 3/3 | 0.10% |
| ENJUSDT | 40 | 0/0/0 | 1181 | 8/0 (1) | 0 | 8h dal 2020-09-29 | 2020: 2, 2021: 144, 2022: 53, 2023: 35 | 5/4 | 0.10% |
| EOSUSDT | 48 | 0/0/0 | 1452 | 2/0 (1) | 0 | 8h dal 2020-01-08 | 2020: 60, 2021: 557, 2022: 205, 2023: 138 | 0/0 | 0.05% |
| FLMUSDT | 40 | 0/0/0 | 1182 | 2/5 (1) | 2 | 8h dal 2020-09-29; 2h dal 2023-09-05; 8h dal 2023-09-09; 4h dal 2023-10-12 | 2020: 12, 2021: 36, 2022: 54, 2023: 37 | 11/5 | 0.10% |
| GRTUSDT | 37 | 0/0/0 | 1101 | 2/5 (1) | 2 | 8h dal 2020-12-19 | 2020: 254, 2021: 111, 2022: 54, 2023: 75 | 0/1 | 0.05% |
| GTCUSDT | 31 | 0/0/0 | 927 | 2/5 (1) | 2 | 8h dal 2021-06-11 | 2021: 84, 2022: 35, 2023: 27 | 4/8 | 0.10% |
| HBARUSDT | 34 | 0/0/0 | 1013 | 2/5 (1) | 2 | 8h dal 2021-03-17 | 2021: 64, 2022: 27, 2023: 46 | 4/1 | 0.10% |
| ICPUSDT | 32 | 0/0/16 | 936 | 3/26 (1) | 1 | 8h dal 2022-09-01 | 2021: 285, 2022: 83, 2023: 53 | 4/2 | 0.05% |
| ICXUSDT | 40 | 0/0/0 | 1195 | 8/1 (1) | 0 | 8h dal 2020-09-14 | 2020: 4, 2021: 51, 2022: 25, 2023: 30 | 12/7 | 0.10% |
| IOTAUSDT | 47 | 0/0/0 | 1412 | 2/5 (1) | 2 | 8h dal 2020-02-12 | 2020: 5, 2021: 78, 2022: 23, 2023: 29 | 18/10 | 0.10% |
| KAVAUSDT | 42 | 0/0/0 | 1244 | 8/0 (1) | 0 | 8h dal 2020-07-28 | 2020: 25, 2021: 68, 2022: 57, 2023: 57 | 3/2 | 0.05% |
| KLAYUSDT | 27 | 0/0/0 | 808 | 3/1 (1) | 0 | 8h dal 2021-10-11 | 2021: 20, 2022: 35, 2023: 26 | 10/7 | 0.10% |
| KNCUSDT | 43 | 0/0/0 | 1281 | 2/5 (1) | 2 | 8h dal 2020-06-22 | 2020: 11, 2021: 36, 2022: 137, 2023: 44 | 6/3 | 0.10% |
| KSMUSDT | 39 | 0/0/0 | 1167 | 2/5 (1) | 2 | 8h dal 2020-10-14 | 2020: 13, 2021: 104, 2022: 32, 2023: 20 | 4/9 | 0.10% |
| LINAUSDT | 34 | 0/0/0 | 1011 | 2/5 (1) | 2 | 8h dal 2021-03-19 | 2021: 73, 2022: 42, 2023: 163 | 3/0 | 0.05% |
| LPTUSDT | 26 | 0/0/0 | 778 | 3/0 (1) | 0 | 8h dal 2021-11-11; 4h dal 2023-08-13; 8h dal 2023-08-21; 4h dal 2023-10-12 | 2021: 47, 2022: 17, 2023: 58 | 10/6 | 0.05% |
| LRCUSDT | 39 | 0/0/0 | 1162 | 2/5 (1) | 2 | 8h dal 2020-10-19 | 2020: 5, 2021: 191, 2022: 105, 2023: 25 | 7/7 | 0.10% |
| MANAUSDT | 34 | 0/0/0 | 1015 | 2/5 (1) | 2 | 8h dal 2021-03-15 | 2021: 425, 2022: 201, 2023: 96 | 1/0 | 0.05% |
| MKRUSDT | 41 | 0/0/0 | 1229 | 2/5 (1) | 2 | 8h dal 2020-08-13 | 2020: 18, 2021: 98, 2022: 35, 2023: 96 | 5/0 | 0.05% |
| MTLUSDT | 34 | 0/0/0 | 998 | 8/1 (1) | 0 | 8h dal 2021-03-30; 4h dal 2023-06-07; 8h dal 2023-06-09 | 2021: 50, 2022: 72, 2023: 78 | 3/1 | 0.05% |
| NEARUSDT | 39 | 0/0/0 | 1161 | 7/6 (1) | 2 | 8h dal 2020-10-14 | 2020: 13, 2021: 158, 2022: 465, 2023: 140 | 4/0 | 0.05% |
| NEOUSDT | 47 | 0/0/0 | 1406 | 8/0 (1) | 0 | 8h dal 2020-02-17 | 2020: 16, 2021: 102, 2022: 35, 2023: 56 | 11/2 | 0.05% |
| NKNUSDT | 33 | 0/0/0 | 989 | 8/0 (1) | 0 | 8h dal 2021-04-09 | 2021: 59, 2022: 26, 2023: 21 | 7/8 | 0.10% |
| OCEANUSDT | 38 | 0/0/0 | 1142 | 7/6 (1) | 2 | 8h dal 2020-11-02 | 2020: 7, 2021: 45, 2022: 44, 2023: 65 | 4/1 | 0.05% |
| OGNUSDT | 33 | 0/0/0 | 993 | 7/5 (1) | 2 | 8h dal 2021-04-01 | 2021: 53, 2022: 81, 2023: 50 | 6/5 | 0.05% |
| OMGUSDT | 42 | 0/0/0 | 1266 | 7/6 (1) | 2 | 8h dal 2020-07-01; 2h dal 2021-11-11; 8h dal 2021-11-12 | 2020: 35, 2021: 139, 2022: 30, 2023: 35 | 8/6 | 0.10% |
| ONTUSDT | 47 | 0/0/0 | 1412 | 8/0 (1) | 0 | 8h dal 2020-02-11 | 2020: 11, 2021: 70, 2022: 21, 2023: 30 | 15/5 | 0.10% |
| PEOPLEUSDT | 25 | 0/0/0 | 731 | 2/6 (1) | 2 | 8h dal 2021-12-23 | 2021: 101, 2022: 179, 2023: 28 | 0/2 | 0.10% |
| QTUMUSDT | 47 | 0/0/1 | 1403 | 8/1 (1) | 0 | 8h dal 2020-03-01 | 2020: 8, 2021: 103, 2022: 30, 2023: 23 | 16/5 | 0.10% |
| RENUSDT | 39 | 0/0/0 | 1167 | 8/0 (1) | 0 | 8h dal 2020-10-13 | 2020: 9, 2021: 56, 2022: 44, 2023: 36 | 5/4 | 0.10% |
| RLCUSDT | 42 | 0/0/0 | 1237 | 7/5 (1) | 2 | 8h dal 2020-07-31 | 2020: 17, 2021: 76, 2022: 55, 2023: 38 | 8/6 | 0.10% |
| ROSEUSDT | 25 | 0/0/0 | 724 | 2/6 (1) | 2 | 8h dal 2021-12-30 | 2021: 55, 2022: 69, 2023: 30 | 2/4 | 0.10% |
| RUNEUSDT | 40 | 0/0/0 | 1206 | 8/0 (1) | 0 | 8h dal 2020-09-04 | 2020: 10, 2021: 127, 2022: 123, 2023: 92 | 4/2 | 0.05% |
| SANDUSDT | 36 | 0/0/0 | 1059 | 7/5 (1) | 2 | 8h dal 2021-01-25 | 2021: 532, 2022: 314, 2023: 125 | 1/0 | 0.05% |
| SFPUSDT | 35 | 0/0/0 | 1034 | 7/0 (1) | 0 | 8h dal 2021-02-24 | 2021: 84, 2022: 37, 2023: 32 | 5/7 | 0.10% |
| SKLUSDT | 37 | 0/0/0 | 1107 | 7/5 (1) | 2 | 8h dal 2020-12-08 | 2020: 11, 2021: 54, 2022: 31, 2023: 28 | 7/9 | 0.10% |
| SNXUSDT | 41 | 0/0/0 | 1228 | 7/0 (1) | 0 | 8h dal 2020-08-14 | 2020: 19, 2021: 63, 2022: 70, 2023: 70 | 2/0 | 0.05% |
| STMXUSDT | 34 | 0/0/0 | 1008 | 7/0 (1) | 0 | 8h dal 2021-03-22; 2h dal 2023-07-23; 8h dal 2023-07-25; 4h dal 2023-10-12 | 2021: 40, 2022: 19, 2023: 68 | 9/3 | 0.05% |
| STORJUSDT | 40 | 0/0/0 | 1190 | 7/6 (1) | 2 | 8h dal 2020-09-15 | 2020: 6, 2021: 89, 2022: 47, 2023: 97 | 7/3 | 0.05% |
| SUSHIUSDT | 40 | 0/0/0 | 1202 | 7/5 (1) | 2 | 8h dal 2020-09-04 | 2020: 105, 2021: 229, 2022: 120, 2023: 62 | 0/1 | 0.05% |
| SXPUSDT | 42 | 0/0/0 | 1252 | 7/0 (1) | 0 | 8h dal 2020-07-21 | 2020: 60, 2021: 167, 2022: 38, 2023: 89 | 5/3 | 0.05% |
| THETAUSDT | 44 | 0/0/0 | 1307 | 7/1 (1) | 0 | 8h dal 2020-05-26 | 2020: 23, 2021: 198, 2022: 97, 2023: 33 | 3/2 | 0.10% |
| TOMOUSDT | 39 | 0/0/0 | 1169 | 7/0 (1) | 0 | 8h dal 2020-10-12 | 2020: 5, 2021: 39, 2022: 20, 2023: 117 | 12/3 | 0.05% |
| TRXUSDT | 48 | 0/0/0 | 1435 | 7/5 (1) | 2 | 8h dal 2020-01-15 | 2020: 39, 2021: 283, 2022: 171, 2023: 72 | 5/0 | 0.05% |
| UNFIUSDT | 35 | 0/0/0 | 1034 | 7/23 (1) | 2 | 8h dal 2021-02-01; 4h dal 2023-10-12 | 2021: 39, 2022: 127, 2023: 71 | 2/2 | 0.05% |
| UNIUSDT | 40 | 0/0/0 | 1193 | 7/1 (1) | 0 | 8h dal 2020-09-17 | 2020: 133, 2021: 249, 2022: 85, 2023: 69 | 0/0 | 0.05% |
| VETUSDT | 47 | 0/0/0 | 1405 | 7/5 (1) | 2 | 8h dal 2020-02-14 | 2020: 26, 2021: 208, 2022: 67, 2023: 29 | 6/2 | 0.10% |
| WAVESUSDT | 41 | 0/0/0 | 1225 | 7/5 (1) | 2 | 8h dal 2020-08-12 | 2020: 39, 2021: 76, 2022: 298, 2023: 91 | 0/0 | 0.05% |
| XEMUSDT | 34 | 0/0/0 | 1022 | 7/5 (1) | 2 | 8h dal 2021-03-03 | 2021: 46, 2022: 22, 2023: 29 | 8/3 | 0.10% |
| XLMUSDT | 48 | 0/0/0 | 1430 | 7/6 (1) | 2 | 8h dal 2020-01-19 | 2020: 39, 2021: 239, 2022: 54, 2023: 78 | 9/0 | 0.05% |
| XMRUSDT | 47 | 0/0/0 | 1421 | 7/2 (1) | 0 | 8h dal 2020-02-01 | 2020: 15, 2021: 69, 2022: 67, 2023: 31 | 8/1 | 0.10% |
| XTZUSDT | 47 | 0/0/0 | 1418 | 7/2 (1) | 0 | 8h dal 2020-02-04 | 2020: 48, 2021: 187, 2022: 69, 2023: 26 | 2/3 | 0.10% |
| YFIUSDT | 41 | 0/0/0 | 1206 | 7/5 (1) | 2 | 8h dal 2020-08-31 | 2020: 191, 2021: 113, 2022: 57, 2023: 46 | 0/3 | 0.10% |
| ZECUSDT | 47 | 0/0/0 | 1414 | 7/6 (1) | 2 | 8h dal 2020-02-04 | 2020: 18, 2021: 95, 2022: 74, 2023: 26 | 7/4 | 0.10% |
| ZILUSDT | 43 | 0/0/0 | 1280 | 7/6 (1) | 2 | 8h dal 2020-06-17 | 2020: 20, 2021: 55, 2022: 195, 2023: 37 | 7/3 | 0.10% |
| ZRXUSDT | 43 | 0/0/0 | 1279 | 7/0 (1) | 0 | 8h dal 2020-06-24 | 2020: 11, 2021: 41, 2022: 39, 2023: 45 | 13/5 | 0.10% |
| BTCUSDT | 48 | 0/0/0 | 1453 | 8/0 (1) | 0 | 8h dal 2020-01-01 | 2020: 3.114, 2021: 17.545, 2022: 12.826, 2023: 11.505 | 0/0 | — |

## Mesi sotto la liquidità minima (20 milioni di USDT al giorno, `dati.mesi_sotto_liquidita`)

Su questi mesi le varianti non aprono posizioni (il filtro lo applica `gruppo.py`); le stesse barre sono vietate alla (b) e alle sfasate.

Sulle 80 monete: 432 mesi-moneta sotto soglia fino a gennaio 2023 e 274 nel 2023, su 3061 mesi-moneta.

* 1000XECUSDT: 2022-01, 2022-02, 2022-06, 2022-07, 2022-10, 2022-11, 2022-12, 2023-01, 2023-02, 2023-03, 2023-04, 2023-05, 2023-08, 2023-09, 2023-10, 2023-11
* 1INCHUSDT: 2023-05, 2023-09, 2023-10
* ALGOUSDT: 2020-06, 2020-09, 2020-10, 2020-12
* ALPHAUSDT: 2020-11, 2020-12, 2022-07, 2022-08, 2022-09, 2022-10, 2022-11, 2022-12, 2023-08, 2023-09, 2023-10, 2023-11
* ANKRUSDT: 2021-01, 2022-06, 2022-07, 2022-12, 2023-05, 2023-08, 2023-09, 2023-10
* ARPAUSDT: 2022-07, 2022-08, 2022-09, 2022-11, 2022-12, 2023-01, 2023-04, 2023-10, 2023-11, 2023-12
* ARUSDT: 2021-09, 2022-12, 2023-04, 2023-05, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10
* ATOMUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-12
* AUDIOUSDT: 2022-09, 2022-10, 2022-12, 2023-05, 2023-06, 2023-07, 2023-09, 2023-10, 2023-11, 2023-12
* AXSUSDT: 2020-11, 2020-12, 2021-01
* BAKEUSDT: 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-03, 2023-04, 2023-05, 2023-06, 2023-07
* BANDUSDT: 2020-10, 2022-09, 2022-10, 2023-05, 2023-08, 2023-09
* BELUSDT: 2020-11, 2020-12, 2021-01, 2022-01, 2022-03, 2022-04, 2022-12, 2023-01, 2023-03, 2023-08, 2023-10, 2023-11, 2023-12
* BLZUSDT: 2020-09, 2020-10, 2020-11, 2020-12, 2021-01, 2022-04, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-03, 2023-04, 2023-05, 2023-06, 2023-07
* C98USDT: 2022-12, 2023-05, 2023-06, 2023-07, 2023-10
* CELOUSDT: 2021-09, 2022-07, 2022-08, 2022-09, 2022-10
* CELRUSDT: 2021-06, 2021-07, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11, 2023-12
* CHZUSDT: 2021-01, 2023-08, 2023-09
* COMPUSDT: 2020-06, 2020-07, 2020-10, 2022-12, 2023-04, 2023-05
* CTSIUSDT: 2021-10, 2022-02, 2022-04, 2022-05, 2022-07, 2022-08, 2022-09, 2022-10, 2022-11, 2023-01, 2023-02, 2023-03, 2023-08, 2023-09, 2023-10, 2023-11, 2023-12
* DASHUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-07, 2020-08, 2020-09, 2020-10, 2020-12, 2022-09, 2022-10, 2023-05, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11, 2023-12
* EGLDUSDT: 2020-09, 2020-10, 2020-11, 2023-07, 2023-08, 2023-09
* ENJUSDT: 2020-09, 2020-10, 2020-11, 2020-12, 2022-12, 2023-05, 2023-06, 2023-07, 2023-08
* FLMUSDT: 2020-10, 2020-11, 2020-12, 2021-01, 2022-01, 2022-03, 2022-04, 2022-05, 2022-11, 2022-12, 2023-01, 2023-03, 2023-04, 2023-05, 2023-08
* GRTUSDT: 2023-09
* GTCUSDT: 2022-09, 2022-10, 2022-12, 2023-01, 2023-04, 2023-05, 2023-06, 2023-07, 2023-10, 2023-11, 2023-12
* HBARUSDT: 2022-06, 2022-07, 2022-08, 2022-12, 2023-05
* ICPUSDT: 2022-07, 2022-08, 2022-09, 2022-10, 2023-08, 2023-09
* ICXUSDT: 2020-09, 2020-10, 2020-11, 2020-12, 2021-01, 2022-06, 2022-07, 2022-08, 2022-09, 2022-10, 2022-11, 2022-12, 2023-03, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10, 2023-12
* IOTAUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-07, 2020-08, 2020-09, 2020-10, 2020-11, 2020-12, 2022-06, 2022-07, 2022-08, 2022-10, 2022-11, 2022-12, 2023-01, 2023-02, 2023-03, 2023-04, 2023-05, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10
* KAVAUSDT: 2020-09, 2020-10, 2020-12, 2023-09, 2023-10
* KLAYUSDT: 2021-10, 2021-12, 2022-03, 2022-04, 2022-06, 2022-07, 2022-08, 2022-09, 2022-12, 2023-01, 2023-05, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10
* KNCUSDT: 2020-06, 2020-09, 2020-10, 2020-11, 2020-12, 2021-07, 2023-04, 2023-05, 2023-12
* KSMUSDT: 2020-10, 2020-11, 2020-12, 2022-12, 2023-03, 2023-04, 2023-05, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11
* LINAUSDT: 2022-07, 2022-09, 2022-12
* LPTUSDT: 2022-03, 2022-04, 2022-05, 2022-06, 2022-08, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-03, 2023-04, 2023-05, 2023-06, 2023-07
* LRCUSDT: 2020-10, 2020-11, 2020-12, 2021-07, 2022-09, 2022-10, 2022-12, 2023-05, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11
* MANAUSDT: 2021-06
* MKRUSDT: 2020-09, 2020-10, 2020-11, 2022-07, 2022-12
* MTLUSDT: 2022-09, 2022-10, 2022-11, 2023-12
* NEARUSDT: 2020-10, 2020-11, 2020-12, 2021-01
* NEOUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-07, 2020-10, 2020-12, 2022-10, 2022-11, 2022-12, 2023-08, 2023-09
* NKNUSDT: 2021-06, 2022-03, 2022-05, 2022-09, 2022-10, 2022-12, 2023-01, 2023-03, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11, 2023-12
* OCEANUSDT: 2020-11, 2020-12, 2021-01, 2021-07, 2023-09
* OGNUSDT: 2022-01, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-03, 2023-04, 2023-05, 2023-06
* OMGUSDT: 2020-07, 2020-12, 2022-08, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11
* ONTUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-07, 2020-10, 2020-11, 2020-12, 2022-07, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-08, 2023-09, 2023-10, 2023-11
* PEOPLEUSDT: 2023-07, 2023-08
* QTUMUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-07, 2020-09, 2020-10, 2020-11, 2020-12, 2022-06, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-04, 2023-05, 2023-06, 2023-09
* RENUSDT: 2020-10, 2020-11, 2020-12, 2021-07, 2022-09, 2023-05, 2023-08, 2023-09, 2023-10
* RLCUSDT: 2020-07, 2020-09, 2020-10, 2020-11, 2020-12, 2021-01, 2022-03, 2022-10, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11, 2023-12
* ROSEUSDT: 2022-10, 2022-12, 2023-07, 2023-08, 2023-09, 2023-10
* RUNEUSDT: 2020-09, 2020-10, 2020-11, 2020-12, 2023-05, 2023-07
* SANDUSDT: 2021-01
* SFPUSDT: 2021-02, 2022-06, 2022-07, 2022-09, 2022-10, 2023-03, 2023-04, 2023-05, 2023-07, 2023-10, 2023-11, 2023-12
* SKLUSDT: 2020-12, 2021-01, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-03, 2023-04, 2023-05, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10
* SNXUSDT: 2020-09, 2020-10
* STMXUSDT: 2022-01, 2022-02, 2022-05, 2022-07, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-03, 2023-06
* STORJUSDT: 2020-09, 2020-10, 2020-11, 2020-12, 2021-01, 2022-09, 2022-12, 2023-03, 2023-05, 2023-08
* SUSHIUSDT: 2023-09
* SXPUSDT: 2022-07, 2022-09, 2022-10, 2022-12, 2023-01, 2023-08, 2023-10
* THETAUSDT: 2020-06, 2020-07, 2020-11, 2023-09, 2023-10
* TOMOUSDT: 2020-10, 2020-11, 2020-12, 2021-01, 2022-01, 2022-02, 2022-07, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-02, 2023-12
* TRXUSDT: 2020-01, 2020-03, 2020-04, 2020-05, 2020-06
* UNFIUSDT: 2021-03, 2022-04, 2023-05, 2023-06
* VETUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-10, 2022-12, 2023-08, 2023-10
* XEMUSDT: 2021-06, 2022-03, 2022-04, 2022-06, 2022-10, 2022-11, 2022-12, 2023-01, 2023-09, 2023-12
* XLMUSDT: 2020-01, 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-09, 2020-10, 2022-12
* XMRUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-07, 2020-08, 2020-09, 2023-09
* XTZUSDT: 2020-10, 2022-12, 2023-05, 2023-08, 2023-09
* YFIUSDT: 2023-08, 2023-09, 2023-10
* ZECUSDT: 2020-02, 2020-03, 2020-04, 2020-05, 2020-06, 2020-07, 2020-09, 2023-08, 2023-09, 2023-10, 2023-11
* ZILUSDT: 2020-06, 2020-07, 2020-08, 2020-09, 2020-10, 2020-11, 2022-12, 2023-08, 2023-09, 2023-10
* ZRXUSDT: 2020-06, 2020-07, 2020-09, 2020-10, 2020-11, 2020-12, 2021-01, 2022-08, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-05, 2023-06, 2023-08, 2023-09
