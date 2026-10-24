# Prova 5 — risultati

Calcolato da `python -m stock.prove.p005` il 2026-10-24 13:24 UTC con le regole di `P005_tendenza.md` (committate prima). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY.

| | SPY | QQQ |
|---|---|---|
| Dal / al | 2017-01-03 / 2024-12-31 | 2017-01-03 / 2024-12-31 |
| Ordini eseguiti (uscite dal mercato) | 44 (12) | 52 (22) |
| Guadagno totale senza costi / con i costi / costi doppi | +116.1% / +115.8% / +115.6% | +266.1% / +265.7% / +265.6% |
| Guadagno del comprare e tenere lo stesso titolo | +197.2% | +353.1% |
| Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo | 0.85 / 0.85 | 0.85 / 0.94 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.70 | 0.92 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.82 (gruppi 4) | 0.93 (gruppi 4) |
| t dello Sharpe (da leggere, contro 3) | 1.98 | 2.60 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | 0.70 | 0.92 |
| **4.** Trimestri in guadagno (almeno 60%) | 22 su 32 (69%) | 24 su 32 (75%) |
| Perdita massima dal picco, con i costi | -33.1% | -28.0% |
| **Esito** | **bocciata** | **bocciata** |
