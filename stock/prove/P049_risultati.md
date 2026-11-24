# Prova 49 — risultati

Calcolato da `python -m stock.prove.p049` il 2026-11-24 02:39 UTC con le regole di `P049_vendite_fuori_borsa.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 101 serie.

* Decisioni nel periodo 470, con il DIX sopra la media di un anno 252 (54%); quota media 75.2%; cambi di quota per anno: 2016 12, 2017 8, 2018 17, 2019 14, 2020 10, 2021 14, 2022 13, 2023 28, 2024 13.
* Lo SPY nelle 4 settimane dopo la decisione (da leggere): dopo il DIX alto +1.37% (t 5.16, 249 settimane); dopo il DIX basso +1.20% (t 3.68, 217 settimane).
* La decisione e lo SPY delle 4 settimane prima (da leggere): correlazione -0.05 (negativa = il DIX alto viene dopo le cadute).
* Lo SPY sempre alla quota media (75.2%): Sharpe 0.84, totale +155.0%. La regola al contrario (98% con il DIX basso): Sharpe 0.81, totale +139.7%.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +155.7% / +154.6% / +153.6% | +235.3% |
| **1.** Sharpe annuo con i costi | **0.79** (senza costi 0.79) | 0.84 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 36, t 2.37) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.79 | — |
| **4.** Trimestri in guadagno (60%) | 23 su 32 (72%) | — |
| Perdita massima dal picco | -23.2% | -33.7% |
| Anno per anno | 2016: +8.2% 2017: +12.0% 2018: +0.1% 2019: +26.6% 2020: +18.6% 2021: +22.1% 2022: -17.0% 2023: +23.2% 2024: +11.9% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.82, con i costi doppi 0.82; correlazione con la miscela 0.83 (soglia 0,3); miscela nuova 1.04 contro 1.08 della miscela e 0.87 del tenere lo SPY; **t dello Sharpe della parte 2.37, senza marzo 2020 2.96 (soglia 1,3 tutti e due)**; **miscela nuova più alta nel 25% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove.
