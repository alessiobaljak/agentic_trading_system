# Prova 13 — risultati

Calcolato da `python -m stock.prove.p013` il 2026-10-24 15:00 UTC con le regole di `P013_momento_12_mesi.md` (committate prima). Dal 2017-02-01 al 2024-12-31. Nel conto dell'asticella: 21 serie.

* Titoli dell'indice nel periodo: 693; senza prezzi su Alpaca: 2 (CMCSK (AttributeError), SNDK (AttributeError)).
* Ordini eseguiti 4905 su 510 titoli diversi; senza barra 439; rifiutati 124; rimasti in mano dopo l'uscita dal listino: ['BCR', 'ANDV', 'ESRX', 'RHT', 'TSS', 'AGN', 'NLSN'].
* Costi pagati: commissioni 4,805, scarto e slittamento 5,248 dollari.

| | Le 50 salite di più | Tenere tutto l'indice a pesi uguali | Tenere lo SPY |
|---|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +133.0% / +117.1% / +100.5% | +139.7% | — |
| Sharpe annuo senza costi | 0.63 | — | — |
| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | 0.59 | 0.73 | 0.84 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.28 (gruppi 9) | — | — |
| t dello Sharpe (da leggere, contro 3) | 1.65 | — | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | 0.54 | — | — |
| **4.** Trimestri in guadagno (almeno 60%) | 23 su 32 (72%) | — | — |
| Perdita massima dal picco con i costi | -32.8% | -32.4% | — |
| **Esito** | **bocciata** | | |
