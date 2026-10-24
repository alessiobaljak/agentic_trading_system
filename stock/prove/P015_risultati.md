# Prova 15 — risultati

Calcolato da `python -m stock.prove.p015` il 2026-10-24 15:29 UTC con le regole di `P015_calma_e_agitazione.md` (committate prima). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P003_rimbalzo, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY, P006_QQQ, P006_SPY, P007_QQQ, P007_SPY, P008_usciti, P009_QQQ, P009_QQQ_chiuso, P009_SPY, P009_SPY_chiuso, P010_bilanci, P011_rimbalzo_500, P012_bassa_volatilita, P013_momento_12_mesi, P015_QQQ, P015_SPY.

| | SPY | QQQ |
|---|---|---|
| Dal / al | 2016-02-08 / 2024-12-31 | 2016-02-08 / 2024-12-31 |
| Ordini eseguiti (uscite dal mercato) | 126 (59) | 164 (80) |
| Guadagno totale senza costi / con i costi / costi doppi | +282.9% / +236.3% / +194.9% | +379.8% / +347.3% / +312.9% |
| Guadagno del comprare e tenere lo stesso titolo | +268.6% | +466.8% |
| Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo | 0.93 / 0.93 | 0.93 / 0.99 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.95 | 1.08 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.67 (gruppi 9) | 0.79 (gruppi 9) |
| t dello Sharpe (da leggere, contro 3) | 2.82 | 3.21 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | 0.85 | 1.03 |
| **4.** Trimestri in guadagno (almeno 60%) | 24 su 32 (75%) | 24 su 32 (75%) |
| Perdita massima dal picco, con i costi | -24.2% | -23.4% |
| **Esito** | **bocciata** | **bocciata** |
