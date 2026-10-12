# Vault di BTCUSDT-V10 (Passo 5)

Candidato BTCUSDT-V10 (rottura di volatilità dall'apertura del giorno, long, 1h). Periodo dei trade: entrati dal 2024-01-01T00:00:00+00:00 all'ultima barra 2026-09-30T23:00:00+00:00. Scritto il 2026-10-11T19:27:29Z dal lanciatore `research/vault_strumenti/BTCUSDT.py` (SHA-256 e41893c0863570afc66641af4b3958f96ef06ec4c9c235dc9d4795d125d1ff8d), con il codice del candidato (commit 8634b6ac). Versioni: {'python': '3.11.17', 'numpy': '1.26.4', 'scipy': '1.13.0', 'piattaforma': 'Linux-6.18.44-fc-v114-x86_64-with-glibc2.39', 'macchina': 'x86_64'}.

## Esito: **NON PASSA**

| Condizione | Valore | Soglia | Passa |
|---|---|---|---|
| Profit factor dopo i costi | 1.0665 | almeno 1.10 | no |
| Trade | 325 | almeno 30 | sì |
| Rendimento totale composto | +0.0980 | sopra 0 | sì |
| R medio | +0.0306 | sopra il 90° percentile del caso, -0.2741 | sì |

**Tasso del caso: 0.001** (1 strategie a entrate casuali su 1000 passano lo stesso criterio con lo stesso 90° percentile; semi 0..999, 325 ingressi ciascuna a distanza almeno 10 barre, stessa uscita).
Quante fittizie passano ogni condizione: {'profit_factor': 2, 'trade_minimi': 1000, 'rendimento_positivo': 26, 'sopra_il_caso': 100}. Simulazioni vuote: 0. Trade per simulazione: {'media': 312.29, 'min': 301, 'max': 321}.

## Le metriche della consegna, sul periodo

| | |
|---|---|
| Trade | 325 (per anno di uscita: {'2024': 119, '2025': 118, '2026': 88}) |
| R medio a trade | +0.0306 |
| R medio per anno | {'2024': 0.1585, '2025': -0.0413, '2026': -0.046} |
| R medio senza i 3 migliori | -0.0109 |
| Profit factor | 1.0665 |
| Win rate | 0.4277 |
| Drawdown massimo (trade del periodo, dal capitale iniziale) | 0.1821 |
| Rendimento composto | totale +0.0980; per anno {'2024': 0.2001, '2025': -0.0601, '2026': -0.0264} |
| Baseline (a) | -1.18446; t 4.67061, soglia 2.01565, netta True |
| Baseline (b), 200 semi | -0.46927; t 3.0094, soglia 2.01565, netta True, p-value 0.0015196547905786857 |
| Percentile fra le simulazioni della (b) | 99.0 |
| Buy and hold per anno (contesto) | {'2024': {'long': 1.2088, 'short': -1.2129}, '2025': {'long': -0.0647, 'short': 0.0623}, '2026': {'long': -0.0472, 'short': 0.0448}} |
| Trade ridotti per il tetto di leva | 8 |
| Violazioni della liquidazione | 0 |
| Stop oltre il 6% | 2 |
| Durata media | 9.79 ore |
| Esiti | {'stop': 91, 'target': 0, 'segnale': 234, 'liquidazione': 0, 'fine_dati': 0} |

## I dati del periodo, mese per mese (regola dei dati D2-D3, prima del candidato)

Blocchi (D2): nessuno. Ultima barra allineata 2026-09-30T23:00:00+00:00 (attesa 2026-09-30T23:00:00+00:00). Barre tolte dall'allineamento: 24 su 24096 attese.

* AVVISO 2026-06: 696 barre allineate su 720 attese (96.7%, sotto il 99%): last 720, mark 696, 24 barre tolte dall'allineamento

| Mese | Barre attese | Last | Mark | Allineate | Quota | Avviso | Settlement | Intervalli osservati (ore: volte) |
|---|---|---|---|---|---|---|---|---|
| 2024-01 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2024-02 | 696 | 696 | 696 | 696 | 1.0 |  | 87 | {'8': 87} |
| 2024-03 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2024-04 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2024-05 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2024-06 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2024-07 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2024-08 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2024-09 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2024-10 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2024-11 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2024-12 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2025-01 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2025-02 | 672 | 672 | 672 | 672 | 1.0 |  | 84 | {'8': 84} |
| 2025-03 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2025-04 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2025-05 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2025-06 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2025-07 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2025-08 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2025-09 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2025-10 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2025-11 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2025-12 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2026-01 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2026-02 | 672 | 672 | 672 | 672 | 1.0 |  | 84 | {'8': 84} |
| 2026-03 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2026-04 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |
| 2026-05 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2026-06 | 720 | 720 | 696 | 696 | 0.9667 | AVVISO | 90 | {'8': 90} |
| 2026-07 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2026-08 | 744 | 744 | 744 | 744 | 1.0 |  | 93 | {'8': 93} |
| 2026-09 | 720 | 720 | 720 | 720 | 1.0 |  | 90 | {'8': 90} |

## Da dichiarare

* Ultima barra della serie allineata: 2026-09-30T23:00:00+00:00 (attesa 2026-09-30T23:00:00+00:00). Un trade aperto l'ultimo giorno si chiude al close della barra delle 23:00 con esito fine_dati, senza il settlement di funding delle 00:00 del giorno dopo. Trade chiusi cosi': 0; trade entrati l'ultimo giorno: 1.
* Barre tolte dall'allineamento last/mark nel periodo: 24 su 24096 attese; mesi sotto il 99% (AVVISO, regola D3): ['2026-06']. Buchi nella serie allineata del periodo: 1 (24 ore mancanti). Giorni senza 24 barre allineate: 1 (per la regola della campagna tolgono il segnale del giorno dopo, senza errore). Trade tenuti oltre 23 ore (manca la barra delle 23:00): 0. Settlement di funding caduti in un buco con posizione aperta: 0 (contati su tutta la serie dal 2020).
* Settlement di funding nel periodo: 3012; intervalli osservati fra settlement consecutivi (ore: quante volte): {'8': 3012}. Nessun numero atteso: il conto per mese e' nella tabella.
* Barre vietate alle entrate casuali: {'barre_serie': 58944, 'barre_periodo': 24072, 'ammesse_nel_periodo': 12370, 'vietate_nel_periodo': 11702, 'quota_vietata_nel_periodo': 0.4861}.
* La gemella delle entrate casuali ridà la (b) della campagna sui semi [0, 199]: sì.
* Il percentile del candidato fra le 1000 simulazioni del caso: 99.4 (indizio, non prova).
* Semi: {'caso': [0, 999], 'baseline_b': [0, 199], 'bootstrap': 0, 'ricampionamenti_bootstrap': 2000, 'nota': 'i semi del caso e della (b) partono da 0; la (b) sono i primi 200 semi del caso'}.
* Tempi (secondi): {'candidato': 0.26, 'barre_vietate': 0.35, 'baseline_a': 1.35, 'baseline_b': 43.31, 'caso': 214.81, 'totale': 260.2}.
