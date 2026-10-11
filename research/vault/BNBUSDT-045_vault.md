# BNBUSDT-045 nel vault (2024-01-01 → 2026-09-30 23:00 UTC)

**Esito: NON PASSA il criterio del vault.** cadute: profit_factor, rendimento_positivo, sopra_il_caso

Tasso del caso: **0,4%** (4 strategie a entrate casuali su 1000 passano lo stesso criterio).

| Condizione | Valore | Soglia | Esito |
|---|---|---|---|
| Profit factor dopo i costi | 0,55 | almeno 1,10 | no |
| Trade | 94 | almeno 30 | sì |
| Rendimento totale | -9,1% | sopra 0 | no |
| R medio dopo i costi | -0,0872 | sopra -0,0279 (90° percentile delle 1000 entrate casuali) | no |

## Metriche sui trade entrati nel periodo

| | Valore |
|---|---|
| Trade | 94 (2024: 33, 2025: 34, 2026: 27) |
| R medio a trade, dopo i costi | -0,087 |
| R mediano | +0,036 |
| R medio per anno (anno d'uscita) | 2024 -0,041; 2025 -0,113; 2026 -0,112 |
| R medio senza i 3 trade migliori | -0,106 |
| Profit factor | 0,55 |
| Quota di trade vincenti | 54% |
| Uscite | 83 segnale, 11 stop |
| Rendimento totale (somma dei pnl su 1000, come in validazione) | -9,1% |
| Drawdown massimo | -10,4% |
| Costi medi in R / funding medio in R | +0,097 / -0,0009 |
| Baseline (a) | media -0,082; t -0,14, soglia 2,09, non netta |
| Baseline (b), 200 simulazioni (semi 0-199) | media -0,077; t -0,25, soglia 2,09, non netta; p-value 0,5973 |
| Percentile fra le 200 simulazioni della (b) (indizio) | 37,5 |
| Percentile fra le 1000 simulazioni del caso (indizio) | 40,0 |
| Buy and hold per anno (contesto) | 2024 +125%; 2025 +23%; 2026 -11% |
| Correlazione fra R dei trade e BTC nella stessa finestra | 0,61 |
| Trade ridotti per il tetto di leva / violazioni del margine | 1 / 0 |
| Buchi nei dati (contati dal motore su tutta la serie) | 6 |

## Le entrate casuali (tasso del caso)

1000 strategie, semi 0-999: stessa moneta, direzione long, 94 ingressi a distanza di almeno 4 barre (durata media dei trade del periodo), stessa uscita, stop e costi del candidato; ingressi vietati prima della prima barra del periodo, dove il segnale non e' valido (16 barre), nei mesi esclusi della Fase 0 e all'ultima barra. Trade per simulazione: media 93,8 (da 91 a 94). R medio delle simulazioni: media -0,0793, 90° percentile -0,0279. Quante delle 1000 passano ogni condizione: profit factor 4, trade 1000, rendimento 17, sopra il percentile 100; tutte insieme 4.

Prova della gemella: sui semi [0, 199] gli R medi sono identici a quelli di `motore.simula_baseline_casuale` (differenza massima 0.0).

Ultimo giorno: 0 trade chiusi a fine dati; ultimo trade uscito 2026-09-20 07:00 UTC (segnale).

## Dati del periodo

Ultima barra della serie allineata: 2026-09-30 23:00 UTC (attesa 2026-09-30 23:00 UTC); barre dell'ultimo giorno 24 su 24; prima barra del periodo 2024-01-01 00:00 UTC. Buchi nel periodo: 1 (24 barre mancanti, il piu' lungo 24). Settlement di funding nel periodo: 3012.

Intervalli di funding dichiarati nei file (da quando, ore): 2024-01-01 00:00 UTC 8 h.

Avvisi dei dati (D3, solo riportati; mesi sotto il 99%: 1):

- AVVISO 2026-06: 696 barre allineate su 720 attese (96,7%), sotto il 99% (tolte 24 per mark mancante, 0 per last mancante)

Parte prima del 2024 della serie lunga: {'barre_tenute': 33904, 'tolte_last': 192, 'tolte_mark': 224} contro la Fase 0 {'barre_tenute': 33904, 'tolte_last': 192, 'tolte_mark': 224} (uguale).

File mensili del vault leggibili: BNBUSDT klines 1h 33/33, BNBUSDT markPriceKlines 1h 33/33, BNBUSDT fundingRate 33/33, BTCUSDT klines 1h 33/33; mancanti: nessuno; illeggibili: nessuno. CHECKSUM non pubblicati: 0.

| Mese | Barre attese | Last | Mark | Allineate | Quota | Tolte: manca il mark | Tolte: manca il last | Settlement di funding | Ore dichiarate | Distanze osservate (ore) | BTC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-01 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2024-02 | 696 | 696 | 696 | 696 | 100,0% | 0 | 0 | 87 | 8: 87 | 8: 87 | 696 |
| 2024-03 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2024-04 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2024-05 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2024-06 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2024-07 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2024-08 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2024-09 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2024-10 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2024-11 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2024-12 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2025-01 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2025-02 | 672 | 672 | 672 | 672 | 100,0% | 0 | 0 | 84 | 8: 84 | 8: 84 | 672 |
| 2025-03 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2025-04 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2025-05 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2025-06 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2025-07 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2025-08 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2025-09 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2025-10 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2025-11 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2025-12 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2026-01 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2026-02 | 672 | 672 | 672 | 672 | 100,0% | 0 | 0 | 84 | 8: 84 | 8: 84 | 672 |
| 2026-03 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2026-04 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2026-05 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2026-06 | 720 | 720 | 696 | 696 | 96,7% AVVISO | 24 | 0 | 90 | 8: 90 | 8: 90 | 720 |
| 2026-07 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2026-08 | 744 | 744 | 744 | 744 | 100,0% | 0 | 0 | 93 | 8: 93 | 8: 93 | 744 |
| 2026-09 | 720 | 720 | 720 | 720 | 100,0% | 0 | 0 | 90 | 8: 90 | 8: 90 | 720 |

## Come e' stato calcolato

Serie BNBUSDT 1h last e mark da `dati.carica_serie_allineate` dal 2020-02-01 all'ultima barra 2026-09-30 23:00 UTC (fine chiesta 2026-09-30; 57976 barre, indicatori caldi), funding dai settlement del file; contano i trade entrati dal 2024-01-01T00:00:00+00:00. Codice del candidato al commit 2e29620a (SHA-256 controllati prima dell'import). Criterio da `/home/user/vault_BNBUSDT/research/config/parametri.yaml`. Il rendimento totale e' la somma dei pnl divisa per 1000, con la dimensione sul capitale cresciuto dall'inizio della serie (come in validazione); nelle entrate casuali il capitale all'inizio del periodo e' 1000.

Lanciatore sha256 3168e3e4ea61fcece0c8ccd9426a7c9071a3d8f068d6d2015ad62a6d68b45383; impronta del giro fa7f319812484a9244e1df810793329af21d77f738ac8a823d1a84e7b2e8b297; semi del caso [0, 999], della (b) [0, 199]; python 3.11.17, numpy 1.26.4, scipy 1.13.0.

