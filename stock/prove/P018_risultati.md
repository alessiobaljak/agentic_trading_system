# Prova 18 — risultati

Calcolato da `python -m stock.prove.p018` il 2026-10-25 08:24 UTC con le regole di `P018_acquisti_dirigenti.md` (committate prima). Dal 2016-01-07 al 2024-12-31. Nel conto: 35 serie.

* Acquisti di dirigenti e consiglieri sopra 100'000 dollari, dopo la pulizia: 3316 (tutte le aziende americane); di aziende dell'S&P 500 quel giorno: 2657.
* Ingressi eseguiti 1457; senza barra 0; rifiutati 82; rimasti in mano dopo l'uscita dal listino: nessuno.

| | Acquisti dei dirigenti | Tenere l'indice a pesi uguali | Tenere lo SPY |
|---|---|---|---|
| Guadagno medio per evento rispetto allo SPY, con i costi (t) | -0.59% (-3.01) su 1457; meglio dello SPY 46% | — | — |
| Guadagno totale senza costi / con i costi / costi doppi | +99.5% / +73.7% / +54.3% | +139.7% | — |
| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | 0.43 | 0.72 | 0.89 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.08 (gruppi 11) | — | — |
| t dello Sharpe (da leggere, contro 3) | 1.28 | — | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | 0.35 | — | — |
| **4.** Trimestri in guadagno (almeno 60%) | 20 su 32 (62%) | — | — |
| Anni in guadagno (da leggere) | 7 su 9 | — | — |
| Perdita massima dal picco con i costi | -42.1% | — | — |
| **Esito** | **bocciata** | | |
