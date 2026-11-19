# Prova 41 — risultati

Calcolato da `python -m stock.prove.p041` il 2026-11-19 06:28 UTC con le regole di `P041_lazy_prices.md` (committate prima). Dal 2017-02-01 al 2024-12-31. Nel conto dell'asticella: 86 serie.

* Membri dell'indice nelle decisioni 678, senza prezzi 0; con il segnale per mese: mediana 490 (minimo 479); fuori, sommati sui mesi: {'senza prezzo': 158, 'senza codice': 802, 'senza bilancio recente': 443}. Ordini 7628, liquidati 15; commissioni 6,820 dollari, scarto 2,406.
* Somiglianza mediana: comprati 0.9984, venduti 0.9814; di tutti, per anno: 2017: 0.9941 2018: 0.9933 2019: 0.9930 2020: 0.9918 2021: 0.9937 2022: 0.9950 2023: 0.9951 2024: 0.9956. Bilanci annuali (10-K) in media fra i comprati 22%, fra i venduti 22%, fra tutti 22% (la classifica dentro il tipo: le due quote devono essere vicine).
* **Comprati meno venduti, il mese dopo, prima dei costi: +0.17% al mese (t 0.79)**, mesi positivi 57%; prima del 2020 +0.44% (t 1.24), dal 2020 +0.02% (t 0.06). Ogni mese cambia il 17% dei comprati e il 20% dei venduti.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +6.2% / -5.8% / -15.9% | +193.9% |
| **1.** Sharpe annuo con i costi | **-0.19** (senza costi 0.23) | 0.84 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 31, t -0.53) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.58 | — |
| **4.** Trimestri in guadagno (60%) | 14 su 31 (45%) | — |
| Perdita massima dal picco | -17.0% | -33.8% |
| Anno per anno | 2017: +3.4% 2018: +0.6% 2019: -2.1% 2020: -7.4% 2021: -1.3% 2022: -1.1% 2023: -3.5% 2024: +6.0% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2017-02-01 al 2024-12-31): Sharpe della parte -0.19, con i costi doppi -0.58; correlazione con la miscela 0.07 (soglia 0,3); miscela nuova 1.01 contro 1.04 della miscela e 0.84 del tenere lo SPY; **t dello Sharpe della parte -0.53 (soglia 1,3)**; **miscela nuova più alta nel 17% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove (99).
