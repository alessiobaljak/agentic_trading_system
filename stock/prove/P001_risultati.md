# Prova 1 — risultati

Calcolato da `python -m stock.prove.p001` il 2026-10-24 12:09 UTC con le regole di `P001_ultima_mezzora.md` (committate prima). Periodo dal 2016-01-04 al 2024-12-31.

**L'asticella:** comprare e tenere lo SPY (con i dividendi), Sharpe annuo **0.87** sugli stessi giorni.

| | SPY | QQQ |
|---|---|---|
| Operazioni (giorni con ingresso) | 2259 | 2259 |
| Ordini rifiutati | 0 | 0 |
| Segnali a zero (niente operazione) | 3 | 3 |
| Giorni esclusi | 2019-08-12 | 2016-02-22 |
| Guadagno totale, senza costi | +12.4% | +34.8% |
| Guadagno totale, con i costi | -22.7% | -14.0% |
| Guadagno totale, costi doppi | -47.5% | -45.6% |
| Costi pagati (commissioni + scarto) | 6,435 + 27,175 dollari | 10,110 + 33,101 dollari |
| Sharpe annuo, senza costi | 0.31 | 0.67 |
| **1.** Sharpe annuo con i costi (contro 0.87) | -0.60 | -0.30 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.04 (gruppi 1) | 0.19 (gruppi 1) |
| t dello Sharpe (da leggere, contro 3) | -1.81 | -0.90 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | -1.55 | -1.29 |
| **4.** Trimestri in guadagno (almeno 60%) | 9 su 32 (28%) | 12 su 32 (38%) |
| Perdita massima dal picco, con i costi | -24.5% | -18.0% |
| **Esito** | **bocciata** | **bocciata** |
