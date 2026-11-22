# Prova 46 — risultati

Calcolato da `python -m stock.prove.p046` il 2026-11-22 10:04 UTC con le regole di `P046_dimissioni_del_capo.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 94 serie.

* La scelta delle notizie: {'notizie': 1647822, 'con le parole': 2016, 'più di 3 simboli': 64, 'nessun membro': 1518, 'due o più membri': 64, 'doppioni (60 giorni)': 98}. Annunci 245; per anno: 2016 29, 2017 24, 2018 22, 2019 28, 2020 25, 2021 27, 2022 28, 2023 35, 2024 27; per parola: step down 68, departure 22, leaving 19, steps down 18, to leave 17, stepping down 16, resignation 13, resigns 13, fired 10, resign 10, resigned 9, stepped down 9, departs 7, leaves 7, exits 2, ousted 2, departing 1, terminated 1, exiting 1. Fuori: {'senza prezzi': 2, 'uscita oltre il 2024': 0}. Operazioni possibili 243, fatte 243 (le altre saltate per i 10 posti o per una posizione aperta sullo stesso titolo).
* **La risposta alla domanda** (titolo meno SPY, prima dei costi, dalla chiusura del giorno dopo l'annuncio):
  * a 1 sedute: 243 casi, media **-0.00%**, mediana -0.08%, t -0.01, in calo rispetto allo SPY 53%
  * a 5 sedute: 242 casi, media **-0.18%**, mediana -0.52%, t -0.59, in calo rispetto allo SPY 55%
  * a 10 sedute: 242 casi, media **+0.03%**, mediana -0.57%, t 0.06, in calo rispetto allo SPY 54%
  * a 20 sedute: 242 casi, media **-0.15%**, mediana -1.49%, t -0.19, in calo rispetto allo SPY 60%
  * già successo, dalla chiusura prima dell annuncio all ingresso: 243 casi, media **-1.17%**, mediana -0.64%, t -3.02, in calo rispetto allo SPY 63%
* La vendita allo scoperto coperta, prima dei costi, su tutti i casi: media +0.14% (t 0.18); senza il caso migliore -0.02%; con «effective immediately» (7 casi) -2.49%.

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +1.5% / -7.1% / -15.0% | +240.0% |
| **1.** Sharpe annuo con i costi | **-0.10** (senza costi 0.06) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 34, t -0.29) | — |
| **3.** Sharpe con i costi doppi (> 0) | -0.26 | — |
| **4.** Trimestri in guadagno (60%) | 18 su 32 (56%) | — |
| Perdita massima dal picco | -14.5% | -33.8% |
| Anno per anno | 2016: +3.3% 2017: -1.5% 2018: +1.5% 2019: -8.3% 2020: +2.0% 2021: +8.8% 2022: -0.2% 2023: -10.9% 2024: -0.6% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -0.14, con i costi doppi -0.29; correlazione con la miscela -0.02 (soglia 0,3); miscela nuova 1.04 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte -0.29 (soglia 1,3)**; **miscela nuova più alta nel 27% dei campionamenti (soglia 80%)**. **Esito: non entra**

Nel conto: 2 prove.
