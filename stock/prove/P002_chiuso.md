# Prova 2 — il periodo chiuso (QQQ)

Calcolato UNA volta da `python -m stock.prove.p002_chiuso` il 2026-10-24 12:49 UTC, dopo il sì del proprietario del 24 ottobre 2026. Regole ed esame scritti prima (`P002_zona_di_rumore.md`). Giorni dal 2025-01-02 al 2026-09-30 (437).

## I controlli dei prezzi del periodo

* QQQ: 478 giorni, 185520 minuti di seduta; problemi: nessuno; dividendi Alpaca/Yahoo: 2026-09-21 manca a noi
* SPY: 478 giorni, 185520 minuti di seduta; problemi: nessuno; dividendi Alpaca/Yahoo: 2026-09-18 manca a noi

## Il risultato

| | QQQ |
|---|---|
| Giorni con almeno un ordine eseguito | 243 |
| Ordini eseguiti / rifiutati | 752 / 0 |
| Guadagno totale senza costi / con i costi / costi doppi | +17.4% / +10.1% / +3.1% |
| Sharpe annuo senza costi | 1.04 |
| Sharpe annuo del comprare e tenere lo SPY / QQQ | 1.04 / 1.09 |
| **1.** Sharpe annuo con i costi (deve battere tutti e due) | 0.64 → no |
| **2.** Sharpe annuo con i costi doppi (> 0) | 0.24 → sì |
| **3.** Trimestri in guadagno (almeno 4 su 7) | 6 su 7 (+1.7%, +7.2%, -3.7%, +0.8%, +0.5%, +2.3%, +1.2%) → sì |
| Perdita massima dal picco, con i costi | -9.5% |
| **Esito** | **bocciata nel periodo chiuso** |

Nota: i due dividendi che mancano ad Alpaca (QQQ 21 settembre 2026, SPY 18 settembre 2026) sono stati trovati e aggiunti da Yahoo
(`stock/dati/integrazioni.py`) **prima** di questo calcolo, e il comprare e tenere li comprende. Il periodo chiuso è stato aperto
una volta; questo esito è definitivo.
