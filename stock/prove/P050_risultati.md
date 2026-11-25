# Prova 50 — risultati

Calcolato da `python -m stock.prove.p050` il 2026-11-25 02:36 UTC con le regole di `P050_incertezza_politica.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 103 serie.

* Decisioni nel periodo 108, con l'incertezza sopra la media di un anno 47 (44%); quota media 70.2%; cambi di quota per anno: 2016 5, 2017 3, 2018 6, 2019 6, 2020 4, 2022 5, 2023 7, 2024 5.
* Lo SPY dopo la decisione (da leggere; la misura dello studio): nel mese con l'incertezza alta +1.48% (t 1.86, 46 mesi); bassa +1.15% (t 2.34, 61 mesi). Nei 3 mesi alta +3.52% (t 2.71, 46 mesi); bassa +4.03% (t 6.18, 60 mesi) (i 3 mesi si sovrappongono: il t è troppo alto).
* La decisione e lo SPY del mese prima (da leggere): correlazione -0.05 (negativa = l'incertezza alta viene dopo le cadute).
* Lo SPY sempre alla quota media (70.2%): Sharpe 0.84, totale +141.0%. La regola al contrario (98% con l'incertezza bassa): Sharpe 0.91, totale +158.9%.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +137.4% / +137.0% / +136.7% | +235.3% |
| **1.** Sharpe annuo con i costi | **0.71** (senza costi 0.72) | 0.84 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 36, t 2.14) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.71 | — |
| **4.** Trimestri in guadagno (60%) | 25 su 32 (78%) | — |
| Perdita massima dal picco | -33.1% | -33.7% |
| Anno per anno | 2016: +10.7% 2017: +15.2% 2018: -0.4% 2019: +24.2% 2020: +17.3% 2021: +13.4% 2022: -16.9% 2023: +18.3% 2024: +14.9% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.71, con i costi doppi 0.71; correlazione con la miscela 0.80 (soglia 0,3); miscela nuova 1.01 contro 1.08 della miscela e 0.87 del tenere lo SPY; **t dello Sharpe della parte 2.14, senza marzo 2020 2.85 (soglia 1,3 tutti e due)**; **miscela nuova più alta nel 20% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove (116 e 117).
