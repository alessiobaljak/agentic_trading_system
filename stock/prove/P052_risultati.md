# Prova 52 — risultati

Calcolato da `python -m stock.prove.p052` il 2026-11-26 02:36 UTC con le regole di `P052_vendere_volatilita.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 107 serie.

* Giorni dentro 93%; cambi per anno: 2016 15, 2017 2, 2018 29, 2019 15, 2020 10, 2021 4, 2022 18, 2024 10.
* Il giorno peggiore -31.4% (2018-02-05); il mese peggiore -39.5% ((2018, 2)); febbraio 2018 -39.5%; marzo 2020 +0.0%.
* Prima del cambio del fondo (27 febbraio 2018): Sharpe 1.23, +206.8%; dopo: Sharpe 0.31, +37.6%.
* SVXY tenuto sempre: Sharpe 0.40, -0.8%, perdita massima -95.2%.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +338.6% / +322.1% / +306.2% | +235.3% |
| **1.** Sharpe annuo con i costi | **0.61** (senza costi 0.62) | 0.84 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 36, t 1.84) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.60 | — |
| **4.** Trimestri in guadagno (60%) | 22 su 32 (69%) | — |
| Perdita massima dal picco | -60.2% | -33.7% |
| Anno per anno | 2016: +88.5% 2017: +162.0% 2018: -57.1% 2019: +41.7% 2020: -0.5% 2021: +57.4% 2022: -21.6% 2023: +74.4% 2024: -34.2% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.50, con i costi doppi 0.48; correlazione con la miscela 0.65 (soglia 0,3); miscela nuova 0.84 contro 1.08 della miscela e 0.87 del tenere lo SPY; **t dello Sharpe della parte 1.84, senza marzo 2020 1.84 (soglia 1,3 tutti e due)**; **miscela nuova più alta nel 13% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove (120 e 121).
