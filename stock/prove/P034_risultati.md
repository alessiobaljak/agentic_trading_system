# Prova 34 — risultati

Calcolato da `python -m stock.prove.p034` il 2026-11-15 04:18 UTC con le regole di `P034_deriva_piccole.md` (committate prima). Dal 2016-03-01 al 2024-12-31. Nel conto dell'asticella: 72 serie.

* Comunicati (senza le società vuote) 142763, ammessi con i filtri e i prezzi 67191; fondi esclusi 105, titoli con i dati rotti 7. Comunicati per mese: mediana 580, minimo 0; scelti: mediana 50; mesi fuori 1 su 107.
* Mese dopo, senza costi, da chiusura a chiusura: il quinto con la reazione più alta meno il quinto più basso **-0.33% al mese (t -0.41)**, mediana +0.63%; il quinto alto meno l'IWM **-0.27% al mese (t -1.20)**; su 106 mesi. Correlazione con lo SPY 0.14.
* Ordini eseguiti 9140; senza barra 5; rifiutati 0; chiusi all'ultimo prezzo perché spariti dal listino 4. Costi pagati: commissioni 9,159, scarto e slittamento 17,341 dollari.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -12.9% / -39.3% / -60.3% | +245.0% |
| **1.** Sharpe annuo con i costi | **-0.96** (senza costi -0.25) | 0.89 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 25, t -2.86) | — |
| **3.** Sharpe con i costi doppi (> 0) | -1.71 | — |
| **4.** Trimestri in guadagno (60%) | 8 su 32 (25%) | — |
| Perdita massima dal picco | -40.7% | -33.8% |
| Anno per anno | 2016: -5.9% 2017: +0.3% 2018: -5.4% 2019: -3.7% 2020: -2.1% 2021: -3.7% 2022: -8.4% 2023: -11.5% 2024: -7.6% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -0.98, con i costi doppi -1.73; correlazione con la miscela 0.20 (soglia 0,3); miscela nuova 0.85 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte -2.86 (soglia 1,3)**; **miscela nuova più alta nel 0% dei campionamenti (soglia 80%)**; perdita massima -13.7% contro -14.6%. **Esito: non entra**

Nel conto: 2 prove (85).
