# Prova 11 — risultati

Calcolato da `python -m stock.prove.p011` il 2026-10-24 15:02 UTC con le regole di `P011_rimbalzo_500.md` (committate prima). Dal 2016-01-19 al 2024-12-31. Nel conto dell'asticella: 23 serie.

* Titoli dell'indice nel periodo: 693; senza prezzi su Alpaca: 2 (CMCSK (AttributeError), SNDK (AttributeError)).
* Ordini eseguiti 16883 su 651 titoli diversi; senza barra 596; rifiutati 487; rimasti in mano dopo l'uscita dal listino: ['NFX', 'DISCA', 'DISCK'].
* Costi pagati: commissioni 24,534, scarto e slittamento 93,247 dollari.

| | Rimbalzo sulle 500 | Tenere tutto l'indice a pesi uguali | Tenere lo SPY |
|---|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +418.5% / +152.9% / +21.9% | +139.7% | — |
| Sharpe annuo senza costi | 0.80 | — | — |
| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | 0.51 | 0.72 | 0.91 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.21 (gruppi 9) | — | — |
| t dello Sharpe (da leggere, contro 3) | 1.54 | — | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | 0.22 | — | — |
| **4.** Trimestri in guadagno (almeno 60%) | 22 su 32 (69%) | — | — |
| Perdita massima dal picco con i costi | -61.3% | -32.4% | — |
| **Esito** | **bocciata** | | |
