# Prova 24 — risultati

Calcolato da `python -m stock.prove.p024` il 2026-11-11 13:55 UTC con le regole di `P024_vendite_allo_scoperto.md` (committate prima). Nel conto dell'asticella: 52 serie. Titoli senza prezzi: 2. Date di FINRA: 168 (dal 2018-01-12 al 2024-12-31).

| | A: lungo e corto | B: SPY meno gli affollati |
|---|---|---|
| Periodo | 2018-02-01 → 2024-12-31 (1740 giorni, 83 decisioni) | 2018-02-01 → 2024-12-31 (1740 giorni, 83 decisioni) |
| Titoli per lato | 134 corti, 146 lunghi in media | 134 corti, 0 lunghi in media |
| Ordini eseguiti | 13912 | 5863 |
| Guadagno senza costi / con i costi / costi doppi | +3.8% / -11.9% / -25.4% (SPY +133.0%) | +104.3% / +94.1% / +84.1% (SPY +133.0%) |
| Costi pagati (commissioni + scarto e slittamento, dollari) | 11,452 + 1,670 | 4,632 + 739 |
| Sharpe annuo senza costi | 0.19 | 0.76 |
| **1.** Sharpe annuo con i costi | **-0.56** (SPY 0.73) | **0.71** (SPY 0.73) |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 16, t -1.48) | 0.01 (gruppi 16, t 1.87) |
| **3.** Sharpe con i costi doppi (> 0) | -1.26 | 0.66 |
| **4.** Trimestri in guadagno (60%) | 8 su 27 (30%) | 21 su 27 (78%) |
| Perdita massima dal picco (da leggere) | -14.6% | -25.6% |
| Anno per anno (da leggere) | 2018: -4.2% 2019: -1.3% 2020: -3.6% 2021: -1.7% 2022: +0.0% 2023: +2.4% 2024: -4.0% | 2018: -8.2% 2019: +22.8% 2020: +15.2% 2021: +21.0% 2022: -15.7% 2023: +24.6% 2024: +17.9% |
| **Esito** | **bocciata** | **bocciata** |

Da leggere: B meno SPY, giorno per giorno, media annua -3.35% (t -1.83): è il guadagno (o la perdita) del lato venduto allo scoperto.
