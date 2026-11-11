# Prova 25 — risultati

Calcolato da `python -m stock.prove.p025` il 2026-11-11 13:45 UTC con le regole di `P025_miscela.md` (committate prima). Dal 2016-11-01 al 2024-12-31 (2054 giorni). Nel conto dell'asticella: 50 serie.

| | Miscela | Tenere lo SPY | Metà SPY e metà QQQ |
|---|---|---|---|
| Guadagno totale | +139.4% | +219.0% | +289.6% |
| **1.** Sharpe annuo con i costi | **1.08** | 0.89 | 0.94 |
| Perdita massima dal picco | -14.6% | -33.8% | -30.9% |
| **2.** Sharpe corretto (soglia 0,95) | 0.05 (gruppi 15, t 3.09) | — | — |
| **3.** Sharpe con i costi doppi, stimato (> 0) | 1.04 | — | — |
| **4.** Trimestri in guadagno (60%) | 26 su 32 (81%) | — | — |
| Anno per anno (da leggere) | 2016: +2.5% 2017: +20.0% 2018: +0.8% 2019: +16.4% 2020: +13.7% 2021: +16.4% 2022: -12.4% 2023: +22.2% 2024: +17.1% | — | — |
| **Esito** | **bocciata** | | |

Da leggere, sullo stesso periodo: Sharpe di ciascuna parte P007_SPY 0.84, P007_QQQ 0.98, P015_SPY 0.95, P015_QQQ 1.07, P016_SPY 0.94, P016_QQQ 0.96.

Correlazioni fra le parti:

| | P007_SPY | P007_QQQ | P015_SPY | P015_QQQ | P016_SPY | P016_QQQ |
|---|---|---|---|---|---|---|
| P007_SPY | 1.00 | 0.92 | 0.10 | 0.09 | 0.09 | 0.09 |
| P007_QQQ | 0.92 | 1.00 | 0.10 | 0.11 | 0.09 | 0.12 |
| P015_SPY | 0.10 | 0.10 | 1.00 | 0.91 | 0.96 | 0.88 |
| P015_QQQ | 0.09 | 0.11 | 0.91 | 1.00 | 0.87 | 0.94 |
| P016_SPY | 0.09 | 0.09 | 0.96 | 0.87 | 1.00 | 0.92 |
| P016_QQQ | 0.09 | 0.12 | 0.88 | 0.94 | 0.92 | 1.00 |
