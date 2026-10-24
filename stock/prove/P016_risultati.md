# Prova 16 — risultati

Calcolato da `python -m stock.prove.p016` il 2026-10-24 20:59 UTC con le regole di `P016_ampiezza.md` (committate prima). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P003_rimbalzo, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY, P006_QQQ, P006_SPY, P007_QQQ, P007_SPY, P008_usciti, P009_QQQ, P009_QQQ_chiuso, P009_SPY, P009_SPY_chiuso, P010_bilanci, P011_rimbalzo_500, P012_bassa_volatilita, P013_momento_12_mesi, P014_QQQ, P014_QQQ_chiuso, P014_SPY, P014_SPY_chiuso, P015_QQQ, P015_QQQ_chiuso, P015_SPY, P015_SPY_chiuso, P016_QQQ, P016_SPY.

| | SPY | QQQ |
|---|---|---|
| Dal / al | 2016-11-01 / 2024-12-31 | 2016-11-01 / 2024-12-31 |
| Ordini eseguiti (uscite dal mercato) | 15 (7) | 15 (7) |
| Guadagno totale senza costi / con i costi / costi doppi | +154.1% / +154.0% / +153.7% | +254.1% / +253.9% / +253.7% |
| Guadagno del comprare e tenere lo stesso titolo | +219.0% | +367.9% |
| Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo | 0.89 / 0.89 | 0.89 / 0.95 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.94 | 0.96 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.62 (gruppi 10) | 0.65 (gruppi 10) |
| t dello Sharpe (da leggere, contro 3) | 2.68 | 2.75 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | 0.94 | 0.96 |
| **4.** Trimestri in guadagno (almeno 60%) | 25 su 32 (78%) | 25 su 32 (78%) |
| Perdita massima dal picco, con i costi | -22.3% | -34.1% |
| **Esito** | **bocciata** | **bocciata** |
