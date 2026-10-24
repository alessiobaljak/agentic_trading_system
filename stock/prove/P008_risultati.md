# Prova 8 — risultati

Calcolato da `python -m stock.prove.p008` il 2026-10-24 13:56 UTC con le regole di `P008_usciti_dall_indice.md` (committate prima). Dal 2016-05-02 al 2024-12-31. Nel conto dell'asticella: P001_QQQ, P001_SPY, P002_QQQ, P002_QQQ_chiuso, P002_SPY, P004_QQQ, P004_SPY, P005_QQQ, P005_SPY, P006_QQQ, P006_SPY, P007_QQQ, P007_SPY, P008_usciti.

* Uscite dall'indice nel periodo: 198; titoli senza prezzi su Alpaca: 1; ingressi eseguiti 112; uscite eseguite 109; ordini senza barra 84 (titoli spariti dal listino o senza scambi quel giorno); rimasti in mano: ['LVLT', 'HRS', 'TMK'].
* Costi pagati: commissioni 591, scarto e slittamento 2,950 dollari.

| | Usciti dall'indice |
|---|---|
| Guadagno medio per evento con i costi (t) | -1.56% (-0.81) su 109; in guadagno 35% |
| Guadagno totale senza costi / con i costi / costi doppi | -13.0% / -16.3% / -19.5% |
| Sharpe annuo senza costi | -0.21 |
| **1.** Sharpe annuo con i costi (contro 0.87 del tenere lo SPY) | -0.27 |
| **2.** Sharpe corretto per i tentativi (soglia 0,95) | 0.00 (gruppi 7) |
| t dello Sharpe (da leggere, contro 3) | -0.80 |
| **3.** Sharpe annuo con i costi doppi (> 0) | -0.34 |
| **4.** Trimestri in guadagno (almeno 60%) | 12 su 32 (38%) |
| Perdita massima dal picco con i costi | -22.9% |
| **Esito** | **bocciata** |
