# Prova 12 — risultati

Calcolato da `python -m stock.prove.p012` il 2026-10-24 15:01 UTC con le regole di `P012_bassa_volatilita.md` (committate prima). Dal 2017-02-01 al 2024-12-31. Nel conto dell'asticella: 22 serie.

* Titoli dell'indice nel periodo: 693; senza prezzi su Alpaca: 2 (CMCSK (AttributeError), SNDK (AttributeError)).
* Ordini eseguiti 3503 su 221 titoli diversi; senza barra 309; rifiutati 136; rimasti in mano dopo l'uscita dal listino: ['TWX', 'COL', 'AET', 'AGN', 'CERN'].
* Costi pagati: commissioni 3,224, scarto e slittamento 2,108 dollari.

| | Le 50 meno nervose | Tenere tutto l'indice a pesi uguali | Tenere lo SPY |
|---|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +97.2% / +90.0% / +80.0% | +139.7% | — |
| Sharpe annuo senza costi | 0.67 | — | — |
| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | 0.64 | 0.73 | 0.84 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.33 (gruppi 9) | — | — |
| t dello Sharpe (da leggere, contro 3) | 1.79 | — | — |
| **3.** Sharpe annuo con i costi doppi (> 0) | 0.59 | — | — |
| **4.** Trimestri in guadagno (almeno 60%) | 21 su 32 (66%) | — | — |
| Perdita massima dal picco con i costi | -33.1% | -32.4% | — |
| **Esito** | **bocciata** | | |
