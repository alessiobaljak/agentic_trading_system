# Prova 27 — risultati

Calcolato da `python -m stock.prove.p027` il 2026-11-12 11:04 UTC con le regole di `P027_dirigenti_aziende_piccole.md` (committate prima). Dal 2016-02-03 al 2024-12-31. Nel conto dell'asticella: 56 serie.

* Titoli con acquisti: 4815; con i prezzi su Alpaca: 4406 (**senza prezzi: 409**, in gran parte aziende sparite o mai quotate in borsa: controllo dei dati).
* Eventi dopo ogni filtro: operazioni 70730; gruppi 23447; gruppi con i prezzi 22144; eventi puliti sopra 100'000 21160; eventi comprabili (5 dollari, 2 milioni al giorno) 11965; titoli con i dati rotti 2.
* Ingressi eseguiti 1801; senza barra 7; rifiutati 1697; **rimasti in mano dopo l'uscita dal listino: 6** (VRX, CRZO, FIII, FGNA, MACQ, SWM).
* Costi pagati: commissioni 8,597, scarto e slittamento 60,412 dollari.

| | Acquisti dei dirigenti, aziende piccole | Tenere l'IWM | Tenere lo SPY |
|---|---|---|---|
| Guadagno medio per evento, con i costi (t) | rispetto all'IWM -0.16% (-0.58); rispetto allo SPY -0.36% (-1.24); eventi 1795; meglio dell'IWM 47% | — | — |
| Guadagno totale senza costi / con i costi / costi doppi | +192.0% / +82.9% / +8.7% | +147.7% | +257.3% |
| **1.** Sharpe annuo con i costi | **0.42** (senza costi 0.62) | 0.56 | 0.91 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 17, t 1.25) | — | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.16 | — | — |
| **4.** Trimestri in guadagno (60%) | 20 su 32 (62%) | — | — |
| Perdita massima dal picco | -49.6% | -41.3% | -33.8% |
| Anno per anno | 2016: +41.7% 2017: +14.9% 2018: -4.0% 2019: +18.5% 2020: -0.7% 2021: +10.3% 2022: -27.1% 2023: +14.5% 2024: +8.1% | — | — |
| **Esito da sola** | **bocciata** | | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.31; correlazione con la miscela 0.64 (soglia 0,3); miscela nuova 0.84 contro 1.08 della miscela e 0.89 del tenere lo SPY; perdita massima -23.3% contro -14.6%. **Esito: non entra**
