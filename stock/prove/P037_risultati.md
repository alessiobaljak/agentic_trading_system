# Prova 37 — risultati

Calcolato da `python -m stock.prove.p037` il 2026-11-16 10:39 UTC con le regole di `P037_ribilanciamento.md` (committate prima). Dal 2016-01-04 al 2024-12-31, 2264 giorni; prezzi di Yahoo (seconda fonte: rendimenti di SPY contro Alpaca, correlazione 0.9955, differenza mediana 0.15 punti base). Nel conto dell'asticella: 78 serie.

* Peso medio |w| 0.27, massimo 1.09 (limitato a 1 nell'esame: giorni oltre il limite 2); giorni con la parte di calendario accesa 648; correlazione fra le due parti 0.18.
* Asimmetria dei rendimenti 5.77; dai 10 giorni migliori viene il 126% del guadagno (in logaritmi).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +76.1% / +46.6% / +21.0% | +240.0% |
| **1.** Sharpe annuo con i costi | **0.56** (senza costi 0.80) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 28, t 1.67) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.30 | — |
| **4.** Trimestri in guadagno (60%) | 16 su 32 (50%) | — |
| Perdita massima dal picco | -15.2% | -33.8% |
| Fino al 17 marzo 2023 (dentro il campione dell'articolo) / dopo | Sharpe 0.57 / 0.53 (+40.1% / +4.6%) | — |
| Senza marzo 2020 | Sharpe 0.02 | — |
| Anno per anno | 2016: +1.5% 2017: -1.6% 2018: +1.5% 2019: -4.0% 2020: +32.3% 2021: +3.2% 2022: +5.3% 2023: +3.2% 2024: +1.4% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.53, con i costi doppi 0.28; correlazione con la miscela -0.00 (soglia 0,3); miscela nuova 1.18 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte 1.67 (soglia 1,3)**; **miscela nuova più alta nel 85% dei campionamenti (soglia 80%)**. **Esito: entra nella miscela (prima il revisore)**

**Da leggere accanto (non cambiano l'esito):**

| Versione | Sharpe | Guadagno totale | Perdita massima |
|---|---|---|---|
| costi doppi | 0.30 | +21.0% | -20.7% |
| senza costi | 0.80 | +76.1% | -13.0% |
| articolo, senza limite | 0.56 | +47.4% | -15.3% |
| solo fascia | 0.56 | +56.2% | -11.2% |
| solo calendario | 0.14 | +8.6% | -25.6% |
| un giorno di ritardo | -0.54 | -35.6% | -45.7% |
| con TLT | 0.79 | +119.6% | -20.7% |

Nel conto: 2 prove (91).
