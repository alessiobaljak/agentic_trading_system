# Prova 47 — risultati

Calcolato da `python -m stock.prove.p047` il 2026-11-23 02:31 UTC con le regole di `P047_prima_candela_gamma.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 97 serie.

* Giorni con la copertura del giorno prima sotto zero 256; ingressi 251; uscite: stop 183, obiettivo 4, chiusura 64; ordini rifiutati 0.
* Prima dei costi: nei giorni sotto zero (la regola): 251 giorni, **-4.30 punti base** al giorno sul conto (t -0.75), in guadagno 25%; da leggere, nei giorni sopra o uguale a zero: 1981 giorni, **+0.74 punti base** al giorno sul conto (t 0.79), in guadagno 27%.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -11.2% / -14.8% / -18.2% | +240.0% |
| **1.** Sharpe annuo con i costi | **-0.35** (senza costi -0.25) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 35, t -1.04) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.44 | — |
| **4.** Trimestri in guadagno (60%) | 11 su 32 (34%) | — |
| Perdita massima dal picco | -21.7% | -33.8% |
| Anno per anno | 2016: -0.0% 2017: -0.3% 2018: -6.1% 2019: +2.7% 2020: -10.8% 2021: +0.4% 2022: -0.3% 2023: -0.5% 2024: -0.3% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -0.37, con i costi doppi -0.46; correlazione con la miscela 0.01 (soglia 0,3); miscela nuova 1.01 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte -1.04, senza marzo 2020 -0.44 (soglia 1,3 tutti e due)**; **miscela nuova più alta nel 10% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove.
