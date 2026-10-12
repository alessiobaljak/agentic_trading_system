# Fase 0 — I dati di 1000SHIBUSDT

Scritto il 9 ottobre 2026 dalla sessione di campagna. Fonte: file mensili di
data.binance.vision (futures USDS-M), scaricati con `src/dati.py` (CHECKSUM di Binance
controllato prima di scrivere: nessun CHECKSUM mancante). Solo mesi fino al 2023-12.
Codice: `codice/scarica.py`, `codice/fase0.py`, `codice/impronte.py`.

## Periodi (calcolati prima di caricare i prezzi, log N003)

| | |
|---|---|
| Inizio (scheda: primo mese di dati) | 2021-05-01 |
| Giorni fino al 2023-12-31 | 975 |
| Costruzione | 2021-05-01 → 2023-03-13 (682 giorni), `fine_costruzione_ts` = 1678751999999 |
| Validazione | 2023-03-14 → 2023-12-31 |

**Primo dato reale:** la prima candela del last è del 2021-05-10 (17:00 UTC a 1 ora, 17:30
a 15 e 30 minuti, 16:00 a 2-8 ore, 00:00 a 1 giorno); il primo funding è del 2021-05-10
16:00. I nove giorni dal 1° al 9 maggio non hanno dati: le date di costruzione e
validazione restano quelle calcolate dal primo mese (regola della Fase 0), e la
costruzione vera è quindi di 673 giorni di dati. Storia utile fino al 2023-12-31: circa
2,64 anni, sopra i 2 di `storia_minima_anni`: la campagna si fa.

## Impronte

`impronte.json` (in questa cartella) contiene lo SHA-256 dei 608 file di 1000SHIBUSDT (9
timeframe × last e mark × 32 mesi, più 32 mesi di funding) e dei 288 di BTCUSDT (9
timeframe × 32 mesi, solo last, solo riferimento di mercato). Impronta del file
`impronte.json`: `71d4cf465c00e73ef6582e4f18491d76840521505bb6c050ae2a7b7b300059e2`.
Le sessioni successive riscaricano i file e li confrontano con `codice/impronte.py verifica`.

## Last e mark allineati (`carica_serie_allineate`, barre tolte)

| Timeframe | Barre tenute | Tolte dal last (mark assente) | Tolte dal mark (last assente) | Buchi nella serie tenuta |
|---|---|---|---|---|
| 15m | 92.473 | 193: 2022-10-02 (96), 2023-02-24 (96), 2023-11-10 03:45 (1) | 34: 2021-05-10 09:00-17:15 | 3 |
| 30m | 46.237 | 96: 2022-10-02 (48), 2023-02-24 (48) | 17: 2021-05-10 | 2 |
| 1h | 23.119 | 48: 2022-10-02 (24), 2023-02-24 (24) | 8: 2021-05-10 09:00-16:00 | 2 |
| 2h | 11.560 | 24 (stessi due giorni) | 4 | 2 |
| 4h | 5.780 | 12 (stessi due giorni) | 2 | 2 |
| 6h | 3.854 | 8 | 1 | 2 |
| 8h | 2.890 | 6 | 1 | 2 |
| 12h | 1.927 | 4 | 1 | 2 |
| 1d | 964 | 2 (2022-10-02, 2023-02-24) | 0 | 2 |

Il mark price manca per due giorni interi, il 2022-10-02 e il 2023-02-24 (entrambi in
costruzione), e per una barra da 15 minuti il 2023-11-10 (validazione). Quei giorni sono
buchi per il motore (contati in `n_buchi_dati`; i funding caduti dentro con posizione
aperta si addebitano sull'ultimo mark e si contano in `n_funding_in_buco`). Le barre del
mark prima dell'inizio del last (2021-05-10 mattina) si tolgono.

## Sospensioni e cambi di contratto

Nessun cambio di contratto nell'in-sample: il simbolo è `1000SHIBUSDT` dalla prima
candela (prezzi e quantità sono per 1000 SHIB); nessuna cucitura. Nessuna sospensione
oltre ai buchi del mark elencati sopra (il last non ha buchi).

## Funding

2.896 settlement dal 2021-05-10 16:00 al 2023-12-31 16:00, intervallo sempre di 8 ore
(dichiarato nei file e confermato dalle distanze). Tasso mediano 0,0100%; negativo nel
23,9% dei settlement; almeno 0,03% nell'8,4%.

## Volume e liquidità

Volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere del
last, tutti i 966 giorni presenti):

| Anno | Volume medio giornaliero |
|---|---|
| 2021 (dal 10 maggio) | 1.286 milioni |
| 2022 | 422 milioni |
| 2023 | 212 milioni |

**Mesi sotto 20 milioni di USDT al giorno: nessuno** (il più basso è 2023-09 con 88
milioni). Il filtro di liquidità della Fase 0 è scritto nel codice (`quadro.mesi_illiquidi`,
nessun ingresso su segnali di barre di un mese sotto la soglia) e uguale per conteggio,
test, (a) e (b), ma con questi dati non esclude nessuna barra.

**Slippage.** La fascia della scheda (0,02% per lato) viene dal volume medio del 2023 (212
milioni, fascia da 200 milioni a 1 miliardo). Nel 2021 e nel 2022 il volume era più alto
(fascia uguale o migliore), ma alcuni mesi stanno sotto i 200 milioni (2021-07, 2022-12,
2023-04/05/06/07/09/10/11), dove la fascia sarebbe 0,05%: lo slippage della scheda è
ottimista per quei mesi. Il test a costi doppi ne copre una parte (lezioni/metodo.md).

## Ampiezza tipica delle barre (per stimare i costi in R)

ATR a 14 barre mediano, in rapporto al prezzo, su tutto l'in-sample: 15m 0,66%; 30m
0,95%; 1h 1,39%; 2h 2,04%; 4h 3,01%; 6h 3,75%; 8h 4,42%; 12h 5,57%; 1d 8,00%. Il costo di
un giro (0,14% del nozionale) vale quindi circa 0,05 R con uno stop a 2 ATR su 1 ora,
0,02 R con uno stop al 6% e 0,11 R con uno stop a 2 ATR su 30 minuti.

## Riferimento di mercato

Candele last di BTCUSDT su tutti i nove timeframe, dal 2021-05 al 2023-12, in
`data/insample/BTCUSDT/` (solo per il controllo «è solo il mercato» e per l'idea I-09).
