# Prova 2 — risultati

Calcolato da `python -m stock.prove.p002` il 2026-10-24 12:13 UTC con le regole di `P002_zona_di_rumore.md` (committate prima). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_SPY.

| | SPY | QQQ |
|---|---|---|
| Giorni in cui la regola poteva operare | 2229 | 2230 |
| Giorni con almeno un'operazione | 661 | 681 |
| Ordini eseguiti (in media per giorno operato) | 4075 (6.2) | 3973 (5.8) |
| Ordini rifiutati | 0 | 0 |
| Guadagno totale, senza costi | +73.4% | +201.4% |
| Guadagno totale, con i costi | +23.9% | +102.8% |
| Guadagno totale, costi doppi | -11.7% | +36.5% |
| Costi pagati (commissioni + scarto) | 6,296 + 28,190 dollari | 11,586 + 42,118 dollari |
| Sharpe annuo, senza costi | 1.01 | 1.62 |
| Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo | 0.87 / 0.87 | 0.87 / 0.92 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.41 | 1.05 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.77 (gruppi 2) | 1.00 (gruppi 2) |
| t dello Sharpe (da leggere, contro 3) | 1.23 | 3.14 |
| **3.** Sharpe annuo, costi doppi (deve essere > 0) | -0.19 | 0.48 |
| **4.** Trimestri in guadagno (almeno 60%) | 17 su 32 (53%) | 25 su 32 (78%) |
| Perdita massima dal picco, con i costi | -12.9% | -9.6% |
| **Esito** | **bocciata** | **passa la ricerca** |
