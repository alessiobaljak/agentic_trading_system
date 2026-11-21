# Prova 44 — risultati

Calcolato da `python -m stock.prove.p044` il 2026-11-21 02:34 UTC con le regole di `P044_volatilita_rovesciata.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 90 serie.

* Chiusure rovesciate 162 su 2264 giorni; episodi 51; ordini 96; commissioni 2,291 dollari, scarto 5,613. Segnale del 31 dicembre 2015: normale.
* Episodi in guadagno 19 su 51; i 5 migliori: 2020-02-25 → 2020-04-27 +129.5%; 2016-06-23 → 2016-06-24 +12.8%; 2024-12-19 → 2024-12-20 +11.8%; 2016-01-14 → 2016-01-20 +9.9%; 2018-10-19 → 2018-10-23 +9.1%; i 5 peggiori: 2024-08-05 → 2024-08-09 -16.3%; 2016-11-03 → 2016-11-10 -15.0%; 2024-11-05 → 2024-11-07 -14.7%; 2016-06-27 → 2016-06-29 -13.4%; 2020-10-27 → 2020-11-05 -10.3%.
* Senza il 2020: -51.7%. Correlazione giornaliera con lo SPY -0.48.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +5.1% / -2.7% / -10.0% | +240.0% |
| **1.** Sharpe annuo con i costi | **0.14** (senza costi 0.17) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 33, t 0.43) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.12 | — |
| **4.** Trimestri in guadagno (60%) | 4 su 32 (12%) | — |
| Perdita massima dal picco | -66.8% | -33.8% |
| Anno per anno | 2016: -12.0% 2017: -2.4% 2018: +1.7% 2019: -19.1% 2020: +101.5% 2021: +0.3% 2022: -13.1% 2023: +0.0% 2024: -21.6% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.13, con i costi doppi 0.10; **correlazione con la miscela -0.37 (soglia 0,3)**; miscela nuova 1.06 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte 0.43 (soglia 1,3)**; **miscela nuova più alta nel 44% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove.
