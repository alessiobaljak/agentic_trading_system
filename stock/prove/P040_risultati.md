# Prova 40 — risultati

Calcolato da `python -m stock.prove.p040` il 2026-11-18 10:38 UTC con le regole di `P040_dividendi_pagati.md` (committate prima). Dal 2017-01-03 al 2024-12-31. Nel conto dell'asticella: 84 serie.

* Dividendi in contanti dei membri 8662, usati 7377 (85%); fuori: {'non membro': 993, 'senza codice': 93, 'senza azioni': 199}. Dentro lo SPY il 39% dei giorni; cambi di posizione 365.
* Giorni scelti nel cambio del mese (ultimo giorno e primi tre): 25%, contro il 19% di tutti i giorni.

| Giorni | Quanti | SPY nel giorno, punti base | Negli altri giorni | Differenza |
|---|---|---|---|---|
| sopra la mediana (la regola) | 782 (39%) | +8.3 | +4.7 | +3.6 (t 0.65) |
| nel quarto più alto | 466 (23%) | +10.4 | +4.8 | +5.6 (t 0.76) |
| fra i 10 più alti | 122 (6%) | +2.8 | +6.3 | -3.5 (t -0.20) |

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +78.2% / +73.1% / +68.0% | +199.4% |
| **1.** Sharpe annuo con i costi | **0.58** (senza costi 0.60) | 0.85 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 30, t 1.63) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.55 | — |
| **4.** Trimestri in guadagno (60%) | 15 su 31 (48%) | — |
| Perdita massima dal picco | -19.6% | -33.8% |
| Anno per anno | 2017: +0.0% 2018: +0.0% 2019: +0.2% 2020: +36.5% 2021: +31.2% 2022: -7.4% 2023: +10.1% 2024: -5.4% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2017-01-03 al 2024-12-31): Sharpe della parte 0.58, con i costi doppi 0.55; correlazione con la miscela 0.56 (soglia 0,3); miscela nuova 1.02 contro 1.07 della miscela e 0.85 del tenere lo SPY; **t dello Sharpe della parte 1.63 (soglia 1,3)**; **miscela nuova più alta nel 33% dei campionamenti (soglia 80%)**. **Esito: non entra**

Differenza fra i giorni sopra e sotto la mediana: +3.6 punti base (t 0.65). Nel conto: 2 prove (97).
