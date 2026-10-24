# Prova 3 — risultati

Calcolato da `python -m stock.prove.p003` il 2026-10-24 13:57 UTC con le regole di `P003_rimbalzo.md` (committate prima). Dal 2016-05-02 al 2024-12-31 (2182 giorni). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P003_rimbalzo, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY, P006_QQQ, P006_SPY, P007_QQQ, P007_SPY, P008_usciti.

* Titoli: 33; senza scarto misurato (si usa il più alto, 20.06 punti base): nessuno.
* Scissioni senza prezzo del titolo nuovo (non contate): nessuna.
* Ordini eseguiti 2269; non eseguiti perché il titolo non aveva la barra 0; rifiutati 3; titoli rimasti in mano dopo l'uscita dal listino: nessuno.
* Costi pagati: commissioni 8,348, scarto e slittamento 46,314 dollari; dividendi e scissioni incassati 13,979.

| | Rimbalzo | Tenere le 10 | Tenere lo SPY |
|---|---|---|---|
| Guadagno totale con i costi | +776.9% | +576.8% | — |
| Guadagno totale senza costi / costi doppi | +913.5% / +657.8% | — | — |
| Sharpe annuo senza costi | 0.96 | — | — |
| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | 0.91 | 0.94 | 0.87 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.63 (gruppi 7) | — | — |
| t dello Sharpe (da leggere, contro 3) | 2.67 | — | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | 0.86 | — | — |
| **4.** Trimestri in guadagno (almeno 60%) | 24 su 32 (75%) | — | — |
| Perdita massima dal picco con i costi | -57.9% | -49.6% | — |
| **Esito** | **bocciata** | | |
