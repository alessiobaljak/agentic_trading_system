# Prova 45 — risultati

Calcolato da `python -m stock.prove.p045` il 2026-11-21 10:49 UTC con le regole di `P045_ultima_mezzora_gamma.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 92 serie.

* Giorni con la copertura del giorno prima sotto zero 256, sopra o uguale 2007; giorni esclusi dal controllo dei minuti 1; operazioni 255, saltate per la leva 0; per anno: 2016 21, 2017 2, 2018 38, 2019 19, 2020 31, 2021 16, 2022 104, 2023 23, 2024 1.
* Prima dei costi, nei giorni sotto zero (la regola): 255 operazioni, **+7.58 punti base** a operazione (t 1.91), in guadagno 57%; dopo i costi +5.95 punti base sul conto.
* Da leggere: nei giorni sopra o uguale a zero: 2004 operazioni, **+0.05 punti base** a operazione (t 0.10), in guadagno 49%; in tutti i giorni: 2259 operazioni, **+0.90 punti base** a operazione (t 1.39), in guadagno 50%.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +20.2% / +15.8% / +11.6% | +240.0% |
| **1.** Sharpe annuo con i costi | **0.51** (senza costi 0.64) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 33, t 1.53) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.39 | — |
| **4.** Trimestri in guadagno (60%) | 14 su 32 (44%) | — |
| Perdita massima dal picco | -4.1% | -33.8% |
| Anno per anno | 2016: +1.3% 2017: +0.2% 2018: +2.4% 2019: +0.7% 2020: +8.8% 2021: -2.0% 2022: +4.0% 2023: -0.2% 2024: -0.0% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.50, con i costi doppi 0.38; correlazione con la miscela 0.04 (soglia 0,3); miscela nuova 1.12 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte 1.53 (soglia 1,3)**; **miscela nuova più alta nel 94% dei campionamenti (soglia 80%)**. **Esito: entra nella miscela (prima il revisore)**

Nel conto: 2 prove.
