# BCHUSDT — Fase 0: i dati della moneta

Scritto il 2026-10-09 dalla sessione di campagna (protocollo 4.5). Fonte: file mensili di
data.binance.vision, scaricati con `scarica_periodo` di `src/dati.py` (codice:
`codice/scarica.py`), resoconto calcolato da `codice/fase0.py`. Tutti i numeri qui
sotto sono osservati sui file, salvo dove è scritto «inferito».

## Date della campagna (scritte nel log prima di caricare i prezzi, voce BCHUSDT-N002)

| | Valore |
|---|---|
| Primo mese di dati (scheda) | 2020-01 |
| Inizio | 2020-01-01 |
| Giorni in-sample | 1.461 |
| Costruzione | 2020-01-01 → 2022-10-18 (1.022 giorni), `fine_costruzione_ts` = 1666137599999 |
| Validazione | 2022-10-19 → 2023-12-31 |

## File scaricati e impronte

* BCHUSDT: candele last (`klines`) e mark (`markPriceKlines`) su 15m, 30m, 1h, 2h, 4h, 6h,
  8h, 12h, 1d, e il funding, da 2020-01 a 2023-12: 912 file. Nessun file oltre il 2023-12.
* BTCUSDT (solo riferimento di mercato): candele last sugli stessi 9 timeframe, 2020-01 →
  2023-12: 432 file.
* CHECKSUM remoto: 912 su 912 (BCHUSDT) e 432 su 432 (BTCUSDT) combaciano con lo SHA-256
  del file su disco; nessun CHECKSUM mancante.
* Le impronte SHA-256 di tutti i 1.344 file sono in `impronte.json`, la cui impronta è
  **0af70c710a79f625508b98f7b4a290c0c93c4c2a8dc0bc597957f212994f5a07**. A ogni nuova
  sessione si riscarica e si verifica con `verifica_impronte`: se cambia, STOP.

## Allineamento last e mark (`carica_serie_allineate`, file nativi di ogni timeframe)

Il mark price manca per due giornate intere; il last non ha buchi propri salvo due barre a
15m. Nessuna barra del mark manca nel last (`tolte_mark` = 0 su tutti i timeframe).

| Timeframe | Barre last | Barre tenute | Tolte (presenti solo nel last) | Intervalli tolti |
|---|---|---|---|---|
| 15m | 140.256 | 140.062 | 194 | 2020-01-19 13:15 (1 barra); 2022-10-02 intero (96); 2023-02-24 intero (96); 2023-11-10 03:45 (1) |
| 30m | 70.128 | 70.032 | 96 | 2022-10-02 intero (48); 2023-02-24 intero (48) |
| 1h | 35.064 | 35.016 | 48 | 2022-10-02 (24); 2023-02-24 (24) |
| 2h | 17.532 | 17.508 | 24 | 2022-10-02 (12); 2023-02-24 (12) |
| 4h | 8.766 | 8.754 | 12 | 2022-10-02 (6); 2023-02-24 (6) |
| 6h | 5.844 | 5.836 | 8 | 2022-10-02 (4); 2023-02-24 (4) |
| 8h | 4.383 | 4.377 | 6 | 2022-10-02 (3); 2023-02-24 (3) |
| 12h | 2.922 | 2.918 | 4 | 2022-10-02 (2); 2023-02-24 (2) |
| 1d | 1.461 | 1.459 | 2 | 2022-10-02; 2023-02-24 |

Le barre tolte diventano buchi che il motore conta (`n_buchi_dati`): 2 buchi su ogni
timeframe (4 a 15m). Il 2022-10-02 cade in costruzione, il 2023-02-24 in validazione.
Nessuna barra tenuta senza volume in USDT. Nessuna sospensione di negoziazione visibile
nel last oltre a queste; nessun cambio di contratto o ridenominazione (serie unica
`BCHUSDT`, nessun punto di cucitura).

## Funding

4.383 settlement dal 2020-01-01 00:00 al 2023-12-31 16:00, intervallo dichiarato 8 ore
per tutto il periodo, 4.382 distanze consecutive tutte di 8 ore (nessun buco). Tasso medio
per settlement: 2020 +0,0205%, 2021 +0,0308%, 2022 −0,0055%, 2023 −0,0082%.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele 1d del last, tutti i
1.461 giorni): 2020 117 milioni, 2021 398 milioni, 2022 114 milioni, 2023 339 milioni.
Minimo mensile: 2020-06 con 55 milioni. **Nessun mese sotto la soglia di 20 milioni**: il
filtro di liquidità non esclude nulla (la maschera dei mesi esclusi è vuota, ma il codice
la applica comunque a `conta_trade`, test, baseline (a) e (b)).

**Slippage ottimista in due anni su quattro.** La fascia della scheda (0,02% per lato) viene
dal volume medio del 2023 (fra 200 milioni e 1 miliardo). Nel 2020 e nel 2022 il volume
medio era fra 50 e 200 milioni, la fascia che il protocollo assegna a 0,05% per lato. La
costruzione (2020-01 → 2022-10) ha circa due terzi dei giorni in quella fascia: i costi
del backtest in costruzione sono probabilmente sottostimati di circa 0,06% per giro in
quegli anni (inferito dalle fasce, non misurato). Il test a costi doppi lo copre in parte:
raddoppia 0,02% in 0,04%, ancora sotto 0,05%. Lo terrò presente nelle previsioni e nella
lettura dei candidati; i parametri restano quelli congelati.

## Storia utile

Quattro anni (2020-01 → 2023-12), sopra il minimo di 2 anni: la campagna prosegue.
