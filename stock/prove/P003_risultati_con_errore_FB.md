# Prova 3 — risultati

Calcolato da `python -m stock.prove.p003` il 2026-10-24 13:57 UTC con le regole di `P003_rimbalzo.md` (committate prima). Dal 2016-05-02 al 2024-12-31 (2182 giorni). Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P003_rimbalzo, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY, P006_QQQ, P006_SPY, P007_QQQ, P007_SPY, P008_usciti.

* Titoli: 34; senza scarto misurato (si usa il più alto, 20.06 punti base): nessuno.
* Scissioni senza prezzo del titolo nuovo (non contate): nessuna.
* Ordini eseguiti 1963; non eseguiti perché il titolo non aveva la barra 134; rifiutati 191; titoli rimasti in mano dopo l'uscita dal listino: ['FB'].
* Costi pagati: commissioni 7,309, scarto e slittamento 36,414 dollari; dividendi e scissioni incassati 14,373.

| | Rimbalzo | Tenere le 10 | Tenere lo SPY |
|---|---|---|---|
| Guadagno totale con i costi | +681.3% | +578.1% | — |
| Guadagno totale senza costi / costi doppi | +813.0% / +499.2% | — | — |
| Sharpe annuo senza costi | 0.99 | — | — |
| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | 0.93 | 0.97 | 0.87 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.66 (gruppi 7) | — | — |
| t dello Sharpe (da leggere, contro 3) | 2.73 | — | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | 0.83 | — | — |
| **4.** Trimestri in guadagno (almeno 60%) | 24 su 32 (75%) | — | — |
| Perdita massima dal picco con i costi | -45.6% | -47.3% | — |
| **Esito** | **bocciata** | | |
