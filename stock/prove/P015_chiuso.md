# Prova 15 — il periodo chiuso

Calcolato UNA volta da `python -m stock.prove.p015_chiuso` il 2026-10-24 19:02 UTC, dopo il sì del proprietario del 24 ottobre 2026 (eccezione: la prova non aveva passato l'asticella corretta per i tentativi). Regole ed esame scritti prima (`P015_calma_e_agitazione.md`).

| | SPY | QQQ |
|---|---|---|
| Giorni | 2025-01-02 / 2026-09-30 (437 giorni; prima esecuzione 2025-01-06) | 2025-01-02 / 2026-09-30 (437 giorni; prima esecuzione 2025-01-06) |
| Ordini eseguiti / rifiutati | 39 / 0 | 32 / 0 |
| Guadagno totale senza costi / con i costi / costi doppi | +24.3% / +21.2% / +18.2% | +34.1% / +32.9% / +31.8% |
| Guadagno del tenere lo stesso titolo | +32.7% | +45.9% |
| Sharpe del tenere lo SPY / lo stesso titolo | 1.04 / 1.04 | 1.04 / 1.09 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.76 → no | 1.05 → no |
| **2.** Sharpe con i costi doppi (> 0) | 0.67 → sì | 1.02 → sì |
| **3.** Trimestri in guadagno (almeno 4 su 7) | 5 su 7 (-7.6%, +3.7%, +11.2%, +2.6%, -6.0%, +14.8%, +2.7%) → sì | 5 su 7 (-9.0%, +8.2%, +11.5%, +2.5%, -5.7%, +21.8%, +2.9%) → sì |
| Perdita massima dal picco: regola / tenere | -18.9% / -18.8% | -17.0% / -22.8% |
| Da leggere: Sharpe con l'interesse all'8% | 0.73 | 1.04 |
| **Esito** | **bocciata nel periodo chiuso** | **bocciata nel periodo chiuso** |
