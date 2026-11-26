# Prova 53 — risultati

Calcolato da `python -m stock.prove.p053` il 2026-11-26 10:38 UTC con le regole di `P053_giudizi_degli_analisti.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 109 serie.

* La scelta delle notizie: {'notizie': 1647822, 'con un lato': 85740, 'più di 3 simboli': 1210, 'nessun membro': 59202, 'due o più membri': 581}. Annunci 24082 (promozioni 11970, bocciature 12112); per anno: 2016 3140, 2017 2693, 2018 2964, 2019 2888, 2020 3179, 2021 2213, 2022 2460, 2023 2431, 2024 2114. Fuori: {'senza prezzi': 19, 'uscita oltre il 2024': 0}. Operazioni possibili 24063, prese 2120.
* Il titolo meno lo SPY (da leggere) | dalla chiusura prima dell'annuncio all'ingresso | 1 seduta dopo | 5 | 20:
  promozioni +1.39% (t 40.76) | +0.02% (t 0.90) | -0.04% (t -0.90) | -0.13% (t -1.73); bocciature -2.12% (t -42.54) | -0.01% (t -0.44) | -0.01% (t -0.14) | -0.04% (t -0.49).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +28.3% / +2.4% / -18.7% | +240.0% |
| **1.** Sharpe annuo con i costi | **0.07** (senza costi 0.48) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 37, t 0.22) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.34 | — |
| **4.** Trimestri in guadagno (60%) | 16 su 32 (50%) | — |
| Perdita massima dal picco | -21.9% | -33.8% |
| Anno per anno | 2016: -4.1% 2017: -2.5% 2018: -8.7% 2019: -5.1% 2020: +5.4% 2021: +7.2% 2022: +5.3% 2023: -0.4% 2024: +6.7% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte 0.18, con i costi doppi -0.23; correlazione con la miscela 0.01 (soglia 0,3); miscela nuova 1.09 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte 0.22, senza marzo 2020 0.21 (soglia 1,3 tutti e due)**; **miscela nuova più alta nel 58% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove (122 e 123).
