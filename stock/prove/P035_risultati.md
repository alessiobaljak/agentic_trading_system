# Prova 35 — risultati

Calcolato da `python -m stock.prove.p035` il 2026-11-15 12:26 UTC con le regole di `P035_azioni_in_gioco.md` (committate prima, con l'aggiunta sul minuto dell'ingresso). Dal 2016-01-25 al 2024-12-31. Nel conto dell'asticella: 74 serie.

* Titoli con i prezzi 10791; che passano i filtri del giorno: mediana 868; scelti al giorno: mediana 20. **Operazioni 36520**, allo stop 85%, in guadagno prima dei costi 14%; **a operazione prima dei costi +0.140%** (t 11.03).
* **Lo scarto misurato** su 488 ingressi e 490 uscite (campione di 500 operazioni a caso): all'ingresso mediana 16.2 punti base (media 25.9, 90° percentile 59.6); all'uscita mediana 13.0 (media 22.4). Lo stop è a 34.5 punti base dall'ingresso (mediana; media 45.8). **Costo a operazione senza commissioni: 0.242%.**

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con le sole commissioni / con i costi / costi doppi | +1658988.0% / +103601.6% / -100.0% / -100.0% | +264.3% |
| **1.** Sharpe annuo con i costi | **-5.58** (senza costi 3.51, con le sole commissioni 2.55) | 0.92 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 26, t -16.68) | — |
| **3.** Sharpe con i costi doppi (> 0) | -4.73 | — |
| **4.** Trimestri in guadagno (60%) | 0 su 32 (0%) | — |
| Perdita massima dal picco | -100.0% | -33.8% |
| Senza leva (al massimo un ventesimo del capitale a operazione) | Sharpe -8.83, -99.8% | — |
| Anno per anno | 2016: -70.6% 2017: -86.9% 2018: -98.4% 2019: -40.3% 2020: -29.0% 2021: -7.3% 2022: -3.3% 2023: +0.0% 2024: -0.7% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -5.85, con i costi doppi -3.55; correlazione con la miscela 0.01 (soglia 0,3); miscela nuova -1.59 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte -16.68 (soglia 1,3)**; **miscela nuova più alta nel 0% dei campionamenti (soglia 80%)**. **Esito: non entra**

Limite noto: i titoli vengono dall'archivio delle prove 28-34 (simboli di FINRA dal 2018 e membri dell'S&P 500): per il 2016-2017 mancano i titoli spariti prima del 2018. Nel conto: 2 prove (87).
