# Prova 4 — risultati

Calcolato da `python -m stock.prove.p004` il 2026-10-24 13:23 UTC con le regole di `P004_notte.md` (committate prima). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P004_QQQ, P004_SPY.

| | SPY | QQQ |
|---|---|---|
| Notti tenute | 2263 | 2263 |
| Uscite in ritardo (barra mancante) | 0 | 0 |
| Ordini rifiutati | 0 | 0 |
| Dividendi incassati | 18,065 dollari | 8,793 dollari |
| Guadagno totale senza costi / con i costi / costi doppi | +138.9% / +64.6% / +13.3% | +196.3% / +88.8% / +20.3% |
| Costi pagati (commissioni + scarto) | 8,146 + 37,326 dollari | 13,074 + 46,903 dollari |
| Sharpe annuo senza costi | 0.90 | 0.98 |
| Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo | 0.87 / 0.87 | 0.87 / 0.92 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.54 | 0.60 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.71 (gruppi 4) | 0.77 (gruppi 4) |
| t dello Sharpe (da leggere, contro 3) | 1.62 | 1.80 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | 0.18 | 0.22 |
| **4.** Trimestri in guadagno (almeno 60%) | 24 su 32 (75%) | 24 su 32 (75%) |
| Perdita massima dal picco, con i costi | -28.4% | -28.1% |
| **Esito** | **bocciata** | **bocciata** |
