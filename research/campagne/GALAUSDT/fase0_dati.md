# Fase 0 — I dati di GALAUSDT

Scritto il 2026-10-09 dalla sessione di campagna, con il protocollo 4.5. Codice:
`codice/scarica.py` (scarico), `codice/fase0.py` (controlli). Uscita grezza dei controlli in
`research/data/insample/GALAUSDT/fase0_uscita.json` (fuori da git, si rigenera).

## Periodi (scritti nel log PRIMA di caricare i prezzi, voce GALAUSDT-N001)

| | Valore |
|---|---|
| Primo mese di dati (scheda) | 2021-09-01 |
| Giorni fino al 2023-12-31 | 852 |
| Costruzione | 2021-09-01 → 2023-04-19 (596 giorni; `fine_costruzione_ts` = 1681948799999) |
| Validazione | 2023-04-20 → 2023-12-31 |

La prima barra del last nei file è del **2021-09-18** (15m: 03:30 UTC; 1h: 03:00; 4h, 8h, 1d:
00:00, cioè la prima candela lunga copre anche ore prima del primo scambio dei file brevi). I
giorni dal 2021-09-01 al 2021-09-17 non hanno candele last: la costruzione effettiva è di 579
giorni. Le date non si spostano (Fase 0, punto 1): la differenza si dichiara qui.

## Scarico e impronte

* Fonte: data.binance.vision, file mensili, solo mesi da 2021-09 a 2023-12. Nessun elenco di
  file remoti: URL costruiti mese per mese.
* GALAUSDT: klines e markPriceKlines su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d (28 mesi ciascuno)
  e fundingRate (28 mesi): 532 file. BTCUSDT (riferimento di mercato): klines sugli stessi 9
  timeframe e mesi: 252 file.
* Checksum remoto (file `.CHECKSUM` di Binance) controllato su ogni file: nessuno mancante,
  nessuno diverso.
* Impronte SHA-256 di ogni file: `impronte_GALAUSDT.json` (532 voci, impronta del file
  `37d2538a163b2eefc3f7fd7b6edf34f61b47cc83b6a77f9827b20bbf0732ec0c`) e `impronte_BTCUSDT.json`
  (252 voci, impronta del file `9afced73290ae03a261384177556987b2d7331582d72ae5807deded4b68de6a2`).
  Una sessione successiva riscarica e confronta con `dati.verifica_impronte`: se cambia, STOP.

## Allineamento di last e mark (`carica_serie_allineate`, file nativi di ogni timeframe)

Barre tolte perché presenti in una serie sola:

| Timeframe | Barre tenute (di cui costruzione) | Tolte dal last (mark mancante) | Tolte dal mark (last mancante) |
|---|---|---|---|
| 15m | 79.857 (55.282) | 289: 2022-07-31, 2022-10-02, 2023-02-24 (giorni interi) e 2023-11-10 03:45 | 72: 2021-09-17 09:30 → 2021-09-18 03:15 |
| 30m | 39.929 (27.641) | 144: i tre giorni interi | 36: 2021-09-17 09:30 → 2021-09-18 03:00 |
| 1h | 19.965 (13.821) | 72: i tre giorni interi | 18: 2021-09-17 09:00 → 2021-09-18 02:00 |
| 2h | 9.983 (6.911) | 36: i tre giorni interi | 9: 2021-09-17 08:00 → 2021-09-18 00:00 |
| 4h | 4.992 (3.456) | 18: i tre giorni interi | 4: 2021-09-17 08:00 → 20:00 |
| 6h | 3.328 (2.304) | 12: i tre giorni interi | 3: 2021-09-17 06:00 → 18:00 |
| 8h | 2.496 (1.728) | 9: i tre giorni interi | 2: 2021-09-17 08:00 → 16:00 |
| 12h | 1.666 (1.154) | 4: 2022-10-02 e 2023-02-24 (il 2022-07-31 a 12h ha il mark) | 2: 2021-09-17 |
| 1d | 832 (576) | 3: i tre giorni | 1: 2021-09-17 |

* Il mark price manca per tre giorni interi (2022-07-31, 2022-10-02, 2023-02-24) e per una barra
  da 15 minuti (2023-11-10 03:45, in validazione). Dopo l'intersezione restano quindi tre buchi di
  un giorno, tutti in costruzione (il 2023-02-24 è prima del 2023-04-19), più la barra da 15
  minuti in validazione. Il motore li conta
  (`n_buchi_dati`) e addebita i funding caduti nel buco sull'ultimo mark disponibile.
* Il mark comincia il 2021-09-17, prima del last: quelle barre del mark si tolgono.
* Nessuna barra tenuta senza volume in USDT. BTCUSDT ha una barra per ogni barra tenuta di
  GALAUSDT su tutti i timeframe (nessuna mancante).

## Sospensioni e cambi di contratto

Nessun cambio di simbolo o ridenominazione nel periodo per quanto risulta dai file (stesso
simbolo `GALAUSDT` in tutti i mesi). Nessuna sospensione oltre ai tre giorni senza mark (il last
c'è in quei giorni, quindi non è una sospensione degli scambi ma un buco del file del mark).

## Funding

2.506 regolamenti dal 2021-09-17 16:00 al 2023-12-31 16:00 UTC, intervallo sempre di 8 ore (00,
08, 16 UTC). Tasso medio 0,0067% a regolamento; minimo -0,75%, massimo +0,10%.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere del last, tutti
i giorni):

| Anno | Volume medio giornaliero | Giorni |
|---|---|---|
| 2021 | 828 milioni | 105 |
| 2022 | 343 milioni | 365 |
| 2023 | 198 milioni | 365 |

Il mese più basso è dicembre 2022 (37,5 milioni al giorno), poi settembre 2022 (55,8 milioni).
**Nessun mese è sotto la soglia di 20 milioni**: nessun mese escluso, il filtro dei mesi non
toglie nessuna barra (è comunque nel codice, uguale per conteggio, test, (a) e (b)).

La fascia di slippage della scheda (0,05% per lato) viene dal volume del 2023 (198 milioni, fascia
50-200 milioni). Negli anni prima il volume era più alto (2021: oltre 800 milioni, fascia 0,02%):
qui la fascia del 2023 è prudente, non ottimista. Alcuni mesi della seconda metà del 2022 sono
sotto 200 milioni come il 2023.

## Storia utile

Dal 2021-09-18 al 2023-12-31: 2,3 anni, sopra il minimo di 2 anni (`storia_minima_anni`). La
campagna prosegue.
