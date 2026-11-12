# Prova 28 — risultati

Calcolato da `python -m stock.prove.p028` il 2026-11-12 19:37 UTC con le regole di `P028_tono_delle_notizie.md` (committate prima). Nel conto dell'asticella: 60 serie. Notizie nell'archivio: 1,647,822; che citano da 1 a 3 simboli: 1,457,163.

## A — le 500 grandi, coperte con lo SPY

* Dal 2016-02-01 al 2024-12-31. Titoli ammessi con il tono calcolabile, per mese: mediana 503, minimo 489; titoli scelti: mediana 50; mesi fuori (meno di 25 titoli) 0 su 107. membri senza prezzi 0; salti di prezzo senza spiegazione fra i titoli in mano 0.
* Il quinto con il tono più alto meno il quinto più basso, mese dopo, senza costi: **-0.16% al mese (t -0.67)**, mediana -0.06%, su 107 mesi.
* Ordini eseguiti 9291; senza barra 3; rifiutati 0; rimasti in mano dopo l'uscita dal listino 0; **chiusi all'ultimo prezzo perché spariti dal listino o con il simbolo cambiato: 11**. Costi pagati: commissioni 9,226, scarto e slittamento 4,851 dollari.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -12.6% / -28.2% / -41.5% | +253.0% |
| **1.** Sharpe annuo con i costi | **-1.15** (senza costi -0.47) | 0.90 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 18, t -3.43) | — |
| **3.** Sharpe con i costi doppi (> 0) | -1.79 | — |
| **4.** Trimestri in guadagno (60%) | 6 su 32 (19%) | — |
| Perdita massima dal picco | -28.6% | -33.8% |
| Anno per anno | 2016: -4.1% 2017: -4.4% 2018: -3.0% 2019: -2.0% 2020: -7.0% 2021: -0.8% 2022: +5.2% 2023: -8.9% 2024: -6.9% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -1.09; correlazione con la miscela -0.46 (soglia 0,3); miscela nuova 1.01 contro 1.08 della miscela e 0.89 del tenere lo SPY; perdita massima -11.3% contro -14.6%. **Esito: non entra**

## B — le aziende piccole, coperte con l'IWM

* Dal 2016-03-01 al 2024-12-31. Titoli ammessi con il tono calcolabile, per mese: mediana 713, minimo 0; titoli scelti: mediana 50; mesi fuori (meno di 25 titoli) 1 su 107. candidati fuori dall'indice 8913, di cui fondi esclusi 410, senza prezzi 428, con i dati rotti 10; salti di prezzo senza spiegazione fra i titoli in mano 5.
* Il quinto con il tono più alto meno il quinto più basso, mese dopo, senza costi: **+0.94% al mese (t 3.04)**, mediana +0.95%, su 106 mesi.
* Ordini eseguiti 10367; senza barra 2; rifiutati 0; rimasti in mano dopo l'uscita dal listino 0; **chiusi all'ultimo prezzo perché spariti dal listino o con il simbolo cambiato: 10**. Costi pagati: commissioni 10,320, scarto e slittamento 17,801 dollari.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -0.6% / -31.6% / -54.4% | +245.0% |
| **1.** Sharpe annuo con i costi | **-0.97** (senza costi 0.00) | 0.89 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 18, t -2.87) | — |
| **3.** Sharpe con i costi doppi (> 0) | -1.84 | — |
| **4.** Trimestri in guadagno (60%) | 9 su 32 (28%) | — |
| Perdita massima dal picco | -33.7% | -33.8% |
| Anno per anno | 2016: -1.1% 2017: +1.0% 2018: -3.6% 2019: -3.1% 2020: -5.0% 2021: -5.4% 2022: -7.8% 2023: -4.1% 2024: -7.8% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -1.07; correlazione con la miscela -0.02 (soglia 0,3); miscela nuova 0.92 contro 1.08 della miscela e 0.89 del tenere lo SPY; perdita massima -12.5% contro -14.6%. **Esito: non entra**

