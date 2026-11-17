# Prova 38 — risultati

Calcolato da `python -m stock.prove.p038` il 2026-11-17 10:40 UTC con le regole di `P038_stagionalita.md` (committate prima). Dal 2017-02-01 al 2024-12-31. Nel conto dell'asticella: 80 serie.

* Membri dell'indice nelle decisioni 678, senza prezzi 0; mesi 95, candidati per mese mediana 497. Ordini 15678, rifiutati 0, liquidati 27; commissioni 15,505 dollari, scarto 7,818.
* **Comprati meno venduti, il mese dopo, prima dei costi: -0.11% al mese (t -0.28)**, mesi positivi 56%. Ogni mese cambia il 88% dei comprati e il 87% dei venduti.
* Con un comunicato sui risultati nello stesso mese dell'anno prima: 44% dei comprati, 43% dei venduti; togliendoli, comprati meno venduti -0.31% al mese (t -0.64).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -10.1% / -33.9% / -57.1% | +193.9% |
| **1.** Sharpe annuo con i costi | **-0.78** (senza costi -0.17) | 0.84 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 29, t -2.19) | — |
| **3.** Sharpe con i costi doppi (> 0) | -1.57 | — |
| **4.** Trimestri in guadagno (60%) | 12 su 31 (39%) | — |
| Perdita massima dal picco | -35.3% | -33.8% |
| Senza il 2020 (da leggere) | Sharpe -0.97 | — |
| Anno per anno | 2017: -6.4% 2018: -7.7% 2019: -10.9% 2020: +0.8% 2021: -13.8% 2022: +4.9% 2023: -5.8% 2024: +0.1% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2017-02-01 al 2024-12-31): Sharpe della parte -0.78, con i costi doppi -1.57; correlazione con la miscela 0.01 (soglia 0,3); miscela nuova 0.86 contro 1.04 della miscela e 0.84 del tenere lo SPY; **t dello Sharpe della parte -2.19 (soglia 1,3)**; **miscela nuova più alta nel 0% dei campionamenti (soglia 80%)**. **Esito: non entra**

Limite noto: i comunicati vengono dal file della prova 30 (solo S&P 500, dal 2016). Nel conto: 2 prove (93).
