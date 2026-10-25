# Prova 21 — risultati

Calcolato da `python -m stock.prove.p021` il 2026-10-25 11:51 UTC con le regole di `P021_notizie_ordini_limite.md` (committate prima). Dal 2016-01-06 al 2024-12-31. Nel conto: 42 serie.

* Giorni in gioco: 8972; ordini limite eseguiti 6333; non eseguiti 230.
* Nei giorni non eseguiti, l'ingresso a mercato (stessi costi) avrebbe dato +1.558% a operazione (su 230): restano fuori i casi migliori.

| | Notizie, ingresso a limite | Tenere lo SPY |
|---|---|---|
| Per operazione con i costi (t) | -0.330% (-9.77); in guadagno 38%; senza costi +0.102% | — |
| Guadagno totale senza costi / con i costi / costi doppi | +86.3% / -88.0% / -99.8% | — |
| Sharpe annuo senza costi | 1.00 | — |
| **1.** Sharpe annuo con i costi | -2.99 | 0.87 (indice a pesi uguali: 0.72) |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.00 (gruppi 12) | — |
| t dello Sharpe (da leggere, contro 3) | -8.96 | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | -6.44 | — |
| **4.** Trimestri in guadagno (almeno 60%) | 3 su 32 (9%) | — |
| Anni in guadagno (da leggere) | 0 su 9 | — |
| Perdita massima dal picco con i costi | -88.4% | — |
| **Esito** | **bocciata** | |
