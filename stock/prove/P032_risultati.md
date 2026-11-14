# Prova 32 — risultati

Calcolato da `python -m stock.prove.p032` il 2026-11-14 11:07 UTC con le regole di `P032_poco_vendute_piccole.md` (committate prima, con l'aggiunta sui dati). Dal 2018-02-01 al 2024-12-31. Nel conto dell'asticella: 68 serie.

* Candidati (simboli di FINRA fuori dall'indice) 20038, fondi esclusi 4262, senza prezzi 5441, con i dati rotti 10. Titoli ammessi per mese: mediana 2305, minimo 2117; scelti: mediana 50; mesi fuori 0 su 83.
* Mese dopo, senza costi, da chiusura a chiusura: il quinto con meno giorni per ricomprare meno il quinto con più giorni **-0.18% al mese (t -0.65)**, mediana +0.03%; il quinto basso meno l'IWM **-0.42% al mese (t -1.71)**; su 83 mesi. Correlazione con lo SPY -0.49.
* Ordini eseguiti 6134; senza barra 27; rifiutati 1; chiusi all'ultimo prezzo perché spariti dal listino 101. Costi pagati: commissioni 5,325, scarto e slittamento 6,660 dollari.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -58.5% / -66.7% / -73.7% | +133.0% |
| **1.** Sharpe annuo con i costi | **-1.83** (senza costi -1.47) | 0.73 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 23, t -4.81) | — |
| **3.** Sharpe con i costi doppi (> 0) | -2.20 | — |
| **4.** Trimestri in guadagno (60%) | 2 su 27 (7%) | — |
| Perdita massima dal picco | -67.5% | -33.8% |
| Anno per anno | 2018: -5.1% 2019: -9.3% 2020: -14.5% 2021: -23.1% 2022: -13.9% 2023: -20.9% 2024: -13.7% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2018-02-01 al 2024-12-31): Sharpe della parte -1.83, con i costi doppi -2.20; correlazione con la miscela -0.42 (soglia 0,3); miscela nuova 0.42 contro 0.86 della miscela e 0.73 del tenere lo SPY; **t dello Sharpe della parte -4.81 (soglia 1,3)**; **miscela nuova più alta nel 0% dei campionamenti (soglia 80%)**; perdita massima -13.7% contro -14.6%. **Esito: non entra**

Nel conto: 2 prove (81).
