# Prova 48 — risultati

Calcolato da `python -m stock.prove.p048` il 2026-11-23 10:35 UTC con le regole di `P048_settimana_della_scadenza.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 99 serie.

* Settimane della scadenza 108; giorni dentro 637 su 2264.
* Lo SPY per settimana (da leggere): della scadenza -0.06% (t -0.25, 108 settimane); la settimana dopo +0.38% (t 1.60, 108 settimane); le altre +0.39% (t 2.71, 255 settimane).
* Prima del 2020: della scadenza +0.40% (t 1.64, 48 settimane); dopo +0.10% (t 0.43, 48 settimane); altre +0.28% (t 1.64, 114 settimane). Dal 2020: della scadenza -0.43% (t -1.14, 60 settimane); dopo +0.60% (t 1.57, 60 settimane); altre +0.47% (t 2.16, 142 settimane).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -9.1% / -10.3% / -11.6% | +235.3% |
| **1.** Sharpe annuo con i costi | **-0.11** (senza costi -0.09) | 0.84 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 36, t -0.32) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.13 | — |
| **4.** Trimestri in guadagno (60%) | 20 su 32 (62%) | — |
| Perdita massima dal picco | -31.7% | -33.7% |
| Anno per anno | 2016: +6.0% 2017: +5.3% 2018: -3.2% 2019: +10.1% 2020: -9.7% 2021: -5.7% 2022: -16.1% 2023: +5.3% 2024: +0.1% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -0.19, con i costi doppi -0.21; correlazione con la miscela 0.40 (soglia 0,3); miscela nuova 0.91 contro 1.08 della miscela e 0.87 del tenere lo SPY; **t dello Sharpe della parte -0.32, senza marzo 2020 0.32 (soglia 1,3 tutti e due)**; **miscela nuova più alta nel 2% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove.
