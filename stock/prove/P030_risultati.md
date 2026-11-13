# Prova 30 — risultati

Calcolato da `python -m stock.prove.p030` il 2026-11-13 10:53 UTC con le regole di `P030_premio_del_comunicato.md` (committate prima). Dal 2017-01-03 al 2024-12-31. Nel conto dell'asticella: 64 serie.

* Membri dell'indice nel periodo 684, con le date dei comunicati 669, senza prezzi 0. Titoli con la data prevista per settimana: mediana 12, massimo 179; scelti: mediana 12; settimane fuori (meno di 10) 176 su 418. **Scelte che hanno depositato davvero un comunicato nella settimana: 68%.**
* Tutti i titoli con la data prevista meno lo SPY, dall'apertura all'apertura, senza costi: **-0.130% a settimana (t -1.19)**, mediana -0.144%, su 406 settimane. Beta della strategia rispetto allo SPY -0.02.
* Ordini eseguiti 15711; senza barra 3; rifiutati 0; chiusi all'ultimo prezzo perché spariti dal listino 2. Costi pagati: commissioni 15,734, scarto e slittamento 12,807 dollari.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +7.0% / -26.2% / -51.8% | +197.2% |
| **1.** Sharpe annuo con i costi | **-0.83** (senza costi 0.21) | 0.85 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 21, t -2.35) | — |
| **3.** Sharpe con i costi doppi (> 0) | -1.92 | — |
| **4.** Trimestri in guadagno (60%) | 10 su 31 (32%) | — |
| Perdita massima dal picco | -28.8% | -33.8% |
| Anno per anno | 2017: -7.6% 2018: -4.3% 2019: -0.3% 2020: -4.2% 2021: -8.7% 2022: +3.0% 2023: -6.1% 2024: -1.1% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2017-01-03 al 2024-12-31): Sharpe della parte -0.83, con i costi doppi -1.92; correlazione con la miscela -0.14 (soglia 0,3); miscela nuova 0.96 contro 1.07 della miscela e 0.85 del tenere lo SPY; perdita massima -10.9% contro -14.6%. **Esito: non entra**

Nel conto: 2 prove (77).
