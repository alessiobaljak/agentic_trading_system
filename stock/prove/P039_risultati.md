# Prova 39 — risultati

Calcolato da `python -m stock.prove.p039` il 2026-11-18 02:59 UTC con le regole di `P039_emissione_netta.md` (committate prima). Dal 2017-02-01 al 2024-12-31. Nel conto dell'asticella: 82 serie.

* Membri dell'indice nelle decisioni 678, senza prezzi 0; con il segnale per mese: mediana 466 (minimo 451); fuori, sommati sui mesi: {'senza codice': 802, 'senza due dichiarazioni': 2798, 'senza prezzo': 158}. Ordini 6551, liquidati 5; commissioni 5,523 dollari, scarto 1,451.
* Emissione mediana in un anno: comprati -7.4%, venduti +7.4% (in logaritmi).
* **Comprati meno venduti, il mese dopo, prima dei costi: +0.14% al mese (t 0.53)**, mesi positivi 57%. Ogni mese cambia il 10% dei comprati e il 9% dei venduti. Correlazione con QQQ meno SPY: -0.25.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +4.2% / -4.9% / -13.0% | +193.9% |
| **1.** Sharpe annuo con i costi | **-0.12** (senza costi 0.14) | 0.84 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 30, t -0.33) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.36 | — |
| **4.** Trimestri in guadagno (60%) | 14 su 31 (45%) | — |
| Perdita massima dal picco | -14.6% | -33.8% |
| Anno per anno | 2017: +2.2% 2018: -4.5% 2019: -1.1% 2020: -3.5% 2021: +1.8% 2022: +1.1% 2023: -1.2% 2024: +0.4% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2017-02-01 al 2024-12-31): Sharpe della parte -0.12, con i costi doppi -0.36; correlazione con la miscela -0.06 (soglia 0,3); miscela nuova 1.02 contro 1.04 della miscela e 0.84 del tenere lo SPY; **t dello Sharpe della parte -0.33 (soglia 1,3)**; **miscela nuova più alta nel 36% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove (95).
