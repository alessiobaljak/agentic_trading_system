# Prova 17 — risultati

Calcolato da `python -m stock.prove.p017` il 2026-10-25 08:35 UTC con le regole di `P017_prima_candela.md` (committate prima). Nel conto dell'asticella: 38 serie.

| | SPY 5 min | QQQ 5 min | SPY 15 min | QQQ 15 min |
|---|---|---|---|---|
| Giorni con un ingresso | 2219 | 2227 | 2233 | 2230 |
| Uscite: stop / obiettivo / chiusura | 1769 / 71 / 379 | 1676 / 52 / 499 | 1569 / 30 / 634 | 1437 / 25 / 768 |
| Guadagno senza costi / con i costi / costi doppi | +21.7% / -15.3% / -41.7% | +106.2% / +32.9% / -14.5% | +0.7% / -30.4% / -52.8% | +48.6% / -4.5% / -39.6% |
| Sharpe annuo senza costi | 0.36 | 0.88 | 0.05 | 0.46 |
| Sharpe del tenere lo SPY / lo stesso titolo | 0.87 / 0.87 | 0.87 / 0.92 | 0.87 / 0.87 | 0.87 / 0.92 |
| **1.** Sharpe annuo con i costi | -0.24 | 0.38 | -0.48 | 0.01 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 11) | 0.07 (gruppi 11) | 0.00 (gruppi 11) | 0.01 (gruppi 11) |
| **3.** Sharpe con i costi doppi (> 0) | -0.85 | -0.13 | -1.03 | -0.47 |
| **4.** Trimestri in guadagno (60%) | 13 su 32 (41%) | 18 su 32 (56%) | 15 su 32 (47%) | 17 su 32 (53%) |
| Anni in guadagno (da leggere) | 4 su 9 | 6 su 9 | 3 su 9 | 5 su 9 |
| Robustezza, Sharpe con i costi: obiettivo 5R / 20R / nessuno (da leggere) | -0.45 / -0.34 / -0.34 | 0.28 / 0.36 / 0.36 | -0.41 / -0.46 / -0.45 | 0.01 / 0.05 / 0.06 |
| **Esito** | **bocciata** | **bocciata** | **bocciata** | **bocciata** |
