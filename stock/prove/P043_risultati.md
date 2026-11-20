# Prova 43 — risultati

Calcolato da `python -m stock.prove.p043` il 2026-11-20 02:34 UTC con le regole di `P043_carry_valute.md` (committate prima). Dal 2016-02-01 al 2024-12-31. Nel conto dell'asticella: 88 serie.

* Decisioni 107; giorni senza prezzo per fondo {'FXA': 0, 'FXB': 0, 'FXC': 0, 'FXE': 0, 'FXF': 0, 'FXY': 0}. Ordini 411, liquidati 0; commissioni 414 dollari, scarto 397.
* Mesi comprati / venduti per fondo: FXA 62/0, FXB 56/0, FXC 96/0, FXE 0/80, FXF 0/107, FXY 0/27. Differenza media dei tassi fra comprati e venduti 2.17 punti percentuali l'anno.
* **Comprati meno venduti, il mese dopo, prima dei costi: +0.02% al mese (t 0.13)**, mesi positivi 55%; marzo 2020 -5.17%, agosto 2024 -0.45%. Correlazione giornaliera con lo SPY 0.42.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +0.3% / -2.6% / -5.6% | +253.0% |
| **1.** Sharpe annuo con i costi | **-0.07** (senza costi 0.03) | 0.90 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 32, t -0.21) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.17 | — |
| **4.** Trimestri in guadagno (60%) | 17 su 32 (53%) | — |
| Perdita massima dal picco | -10.0% | -33.8% |
| Anno per anno | 2016: -2.3% 2017: -0.4% 2018: -2.6% 2019: +1.8% 2020: -1.3% 2021: +2.0% 2022: -4.2% 2023: +2.2% 2024: +2.3% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.02, con i costi doppi -0.09; **correlazione con la miscela 0.37 (soglia 0,3)**; miscela nuova 1.04 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte -0.21 (soglia 1,3)**; **miscela nuova più alta nel 8% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove.
