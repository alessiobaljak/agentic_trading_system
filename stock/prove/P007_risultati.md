# Prova 7 — risultati

Calcolato da `python -m stock.prove.p007` il 2026-10-24 13:32 UTC con le regole di `P007_prima_della_fed.md` (committate prima). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY, P006_QQQ, P006_SPY, P007_QQQ, P007_SPY.

| | SPY | QQQ |
|---|---|---|
| Eventi tenuti / saltati | 71 / 0 | 71 / 0 |
| Guadagno medio per evento con i costi (t) | +0.230% (2.93); in guadagno 65% | +0.344% (2.97); in guadagno 65% |
| Guadagno totale senza costi / con i costi / costi doppi | +18.2% / +16.8% / +15.5% | +27.9% / +26.1% / +24.4% |
| Sharpe annuo senza costi | 0.90 | 0.95 |
| Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo | 0.87 / 0.87 | 0.87 / 0.92 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.84 | 0.89 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.75 (gruppi 6) | 0.81 (gruppi 6) |
| t dello Sharpe (da leggere, contro 3) | 2.53 | 2.68 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | 0.78 | 0.84 |
| **4.** Trimestri in guadagno (almeno 60%) | 20 su 32 (62%) | 22 su 32 (69%) |
| **Esito** | **bocciata** | **bocciata** |
