# Prova 31 — risultati

Calcolato da `python -m stock.prove.p031` il 2026-11-14 02:42 UTC con le regole di `P031_redditivita_lorda.md` (committate prima). Dal 2016-07-01 al 2024-12-31. Nel conto dell'asticella: 66 serie.

* Membri dell'indice nelle decisioni 680, senza prezzi 0. Aziende con la redditività, per anno: 2016 276, 2017 306, 2018 322, 2019 333, 2020 335, 2021 337, 2022 332, 2023 338, 2024 341. Fuori nell'ultimo anno: {'senza codice': 5, 'finanziarie': 95, 'senza conti': 62, 'senza barra': 0}.
* Comprati meno venduti, da giugno a giugno, senza costi: 2016 -8.7%, 2017 +13.5%, 2018 +7.6%, 2019 +14.0%, 2020 +0.4%, 2021 -5.3%, 2022 -4.8%, 2023 +2.0%, 2024 +7.6%; media +2.9% l'anno (t 1.06). Beta rispetto allo SPY -0.03; **correlazione con QQQ meno SPY 0.30**.
* Ordini eseguiti 988; senza barra 1; rifiutati 0; chiusi all'ultimo prezzo perché spariti dal listino 16. Costi pagati: commissioni 946, scarto e slittamento 422 dollari (il prestito è nel valore del conto).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +6.8% / +3.0% / +0.2% | +222.2% |
| **1.** Sharpe annuo con i costi | **0.09** (senza costi 0.18) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 22, t 0.27) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.03 | — |
| **4.** Trimestri in guadagno (60%) | 19 su 32 (59%) | — |
| Perdita massima dal picco | -12.7% | -33.8% |
| Anno per anno | 2016: -1.8% 2017: -1.0% 2018: +6.6% 2019: -1.1% 2020: +7.7% 2021: -1.6% 2022: -6.0% 2023: -0.9% 2024: +1.9% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.09, con i costi doppi 0.03; correlazione con la miscela -0.01 (soglia 0,3); miscela nuova 1.09 contro 1.08 della miscela e 0.89 del tenere lo SPY; perdita massima -11.7% contro -14.6%. **Esito: entra nella miscela (prima il revisore, poi il periodo chiuso e la misura in avanti)**

Nel conto: 2 prove (79).
