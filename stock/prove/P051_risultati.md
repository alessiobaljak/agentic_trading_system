# Prova 51 — risultati

Calcolato da `python -m stock.prove.p051` il 2026-11-25 10:39 UTC con le regole di `P051_arbitraggio_acquisizioni.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 105 serie.

* La scelta: {'notizie': 1647822, 'accordi in contanti letti': 582, 'fuori periodo': 0, 'senza bersaglio unico': 140, 'doppioni': 24, 'senza prezzi': 0, 'filtri (5 dollari, 2 milioni)': 139, 'scarto ≤ 0': 44, 'scarto > 50%': 3}. Affari possibili 232, presi 231 (fuori per i posti 1); per anno: 2016 32, 2017 27, 2018 24, 2019 17, 2020 14, 2021 28, 2022 31, 2023 31, 2024 27.
* Scarto medio all'ingresso 3.46% (mediana 1.59%); giorni medi di tenuta 162. Affari chiusi (titolo sparito entro 365 giorni): 178, media +2.56% (t 5.68); gli altri: 53, media -3.80% (t -1.24).
* Nei mesi con lo SPY in perdita (31): correlazione mensile con lo SPY +0.58. Marzo 2020 da solo: -8.85%.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +12.6% / +11.4% / +10.3% | +240.0% |
| **1.** Sharpe annuo con i costi | **0.28** (senza costi 0.31) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 36, t 0.85) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.26 | — |
| **4.** Trimestri in guadagno (60%) | 20 su 32 (62%) | — |
| Perdita massima dal picco | -18.3% | -33.8% |
| Anno per anno | 2016: +1.9% 2017: -0.3% 2018: +1.9% 2019: +5.6% 2020: -4.8% 2021: +6.9% 2022: -1.4% 2023: +5.2% 2024: -3.5% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.29, con i costi doppi 0.27; correlazione con la miscela 0.39 (soglia 0,3); miscela nuova 1.05 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte 0.85, senza marzo 2020 2.12 (soglia 1,3 tutti e due)**; **miscela nuova più alta nel 40% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove (118 e 119).
