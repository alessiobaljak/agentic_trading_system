# Prova 33 — risultati

Calcolato da `python -m stock.prove.p033` il 2026-11-14 21:48 UTC con le regole di `P033_momento_dei_settori.md` (committate prima). Dal 2016-02-01 al 2024-12-31. Nel conto dell'asticella: 70 serie.

* 107 decisioni. Mesi comprato / venduto per settore: XLB 11/24, XLE 31/51, XLF 36/31, XLI 28/18, XLK 65/5, XLP 27/45, XLU 38/40, XLV 14/24, XLY 25/23, XLRE 17/43, XLC 29/17.
* Comprati meno venduti, mese dopo, senza costi: **+0.03% al mese (t 0.07)**, mediana +0.22%, su 107 mesi. Correlazione con lo SPY -0.04; **con QQQ meno SPY 0.25**.
* Ordini eseguiti 759; senza barra 0; rifiutati 0. Costi pagati: commissioni 976, scarto e slittamento 1,586 dollari (il prestito è nel valore del conto).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -2.4% / -7.2% / -11.7% | +253.0% |
| **1.** Sharpe annuo con i costi | **-0.06** (senza costi 0.01) | 0.90 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 24, t -0.19) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.13 | — |
| **4.** Trimestri in guadagno (60%) | 15 su 32 (47%) | — |
| Perdita massima dal picco | -16.9% | -33.8% |
| Anno per anno | 2016: -8.0% 2017: -1.7% 2018: -2.4% 2019: -3.5% 2020: +6.1% 2021: -7.8% 2022: +20.5% 2023: -6.7% 2024: -0.8% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.03, con i costi doppi -0.04; correlazione con la miscela 0.10 (soglia 0,3); miscela nuova 1.03 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte -0.19 (soglia 1,3)**; **miscela nuova più alta nel 29% dei campionamenti (soglia 80%)**; perdita massima -9.5% contro -14.6%. **Esito: non entra**

Nel conto: 2 prove (83).
