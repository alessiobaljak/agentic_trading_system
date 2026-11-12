# Prova 27 — risultati con i prezzi corretti (il simbolo di allora): correzione dei dati, non una prova nuova

Calcolato da `python -m stock.prove.p027` il 2026-11-12 15:35 UTC con le regole di `P027_dirigenti_aziende_piccole.md` (committate prima). Dal 2016-02-03 al 2024-12-31. Nel conto dell'asticella: 56 serie.

* Titoli con acquisti: 4818; con i prezzi su Alpaca: 4428 (**senza prezzi: 390**, in gran parte aziende sparite o mai quotate in borsa: controllo dei dati).
* Eventi dopo ogni filtro: operazioni 71140; gruppi 23459; gruppi con i prezzi 22269; eventi puliti sopra 100'000 21535; eventi comprabili (5 dollari, 2 milioni al giorno) 12145; titoli con i dati rotti 2.
* Ingressi eseguiti 2089; senza barra 2; rifiutati 1216; **rimasti in mano dopo l'uscita dal listino: 0** (nessuno).
* Chiusi all'ultimo prezzo perché spariti dal listino o con il simbolo cambiato (5 sedute senza prezzi): **7**. Le serie in `prove/serie/` sono sostituite con queste (stesso conto delle prove).
* Costi pagati: commissioni 10,398, scarto e slittamento 74,789 dollari.

| | Acquisti dei dirigenti, aziende piccole | Tenere l'IWM | Tenere lo SPY |
|---|---|---|---|
| Guadagno medio per evento, con i costi (t) | rispetto all'IWM +0.00% (0.01); rispetto allo SPY -0.24% (-0.90); eventi 2089; meglio dell'IWM 47% | — | — |
| Guadagno totale senza costi / con i costi / costi doppi | +237.3% / +110.2% / +21.1% | +147.7% | +257.3% |
| **1.** Sharpe annuo con i costi | **0.45** (senza costi 0.65) | 0.56 | 0.91 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 17, t 1.34) | — | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.22 | — | — |
| **4.** Trimestri in guadagno (60%) | 20 su 32 (62%) | — | — |
| Perdita massima dal picco | -54.3% | -41.3% | -33.8% |
| Anno per anno | 2016: +46.3% 2017: +12.9% 2018: -10.6% 2019: +27.3% 2020: +10.0% 2021: +23.1% 2022: -37.3% 2023: +21.0% 2024: +8.8% | — | — |
| **Esito da sola** | **bocciata** | | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.35; correlazione con la miscela 0.65 (soglia 0,3); miscela nuova 0.82 contro 1.08 della miscela e 0.89 del tenere lo SPY; perdita massima -25.3% contro -14.6%. **Esito: non entra**
