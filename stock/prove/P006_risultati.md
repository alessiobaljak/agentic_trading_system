# Prova 6 — risultati

Calcolato da `python -m stock.prove.p006` il 2026-10-24 13:26 UTC con le regole di `P006_cambio_del_mese.md` (committate prima). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY, P006_QQQ, P006_SPY.

| | SPY | QQQ |
|---|---|---|
| Dal / al | 2016-01-28 / 2024-12-31 | 2016-01-28 / 2024-12-31 |
| Ordini eseguiti (uscite dal mercato) | 215 (107) | 213 (106) |
| Guadagno totale senza costi / con i costi / costi doppi | +49.8% / +47.2% / +44.6% | +60.6% / +57.2% / +53.9% |
| Guadagno del comprare e tenere lo stesso titolo | +261.4% | +436.9% |
| Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo | 0.91 / 0.91 | 0.91 / 0.96 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.57 | 0.54 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.43 (gruppi 5) | 0.39 (gruppi 5) |
| t dello Sharpe (da leggere, contro 3) | 1.70 | 1.61 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | 0.55 | 0.52 |
| **4.** Trimestri in guadagno (almeno 60%) | 24 su 32 (75%) | 20 su 32 (62%) |
| Perdita massima dal picco, con i costi | -11.2% | -12.9% |
| **Esito** | **bocciata** | **bocciata** |
