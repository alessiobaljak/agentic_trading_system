# Prova 21 — risultati

Calcolato da `python -m stock.prove.p021` il 2026-10-25 12:08 UTC con le regole di `P021_notizie_ordini_limite.md` (committate prima). Dal 2016-01-06 al 2024-12-31. Nel conto: 42 serie.

* Giorni in gioco: 8972; ordini limite eseguiti 6349; non eseguiti 214.
* Nei giorni non eseguiti, l'ingresso a mercato (stessi costi) avrebbe dato +1.706% a operazione (su 214): restano fuori i casi migliori.

| | Notizie, ingresso a limite | Tenere lo SPY |
|---|---|---|
| Per operazione con i costi (t) | -0.088% (-2.82); in guadagno 37%; senza costi +0.103% | — |
| Guadagno totale senza costi / con i costi / costi doppi | +87.7% / -44.0% / -86.3% | — |
| Sharpe annuo senza costi | 1.04 | — |
| **1.** Sharpe annuo con i costi | -0.89 | 0.87 (indice a pesi uguali: 0.72) |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.00 (gruppi 12) | — |
| t dello Sharpe (da leggere, contro 3) | -2.66 | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | -3.04 | — |
| **4.** Trimestri in guadagno (almeno 60%) | 10 su 32 (31%) | — |
| Anni in guadagno (da leggere) | 1 su 9 | — |
| Perdita massima dal picco con i costi | -49.0% | — |
| **Esito** | **bocciata** | |
