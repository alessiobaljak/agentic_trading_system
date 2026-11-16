# Prova 36 — risultati

Calcolato da `python -m stock.prove.p036` il 2026-11-16 03:02 UTC con le regole di `P036_dirigenti_subito.md` (committate prima). Dal 2016-01-04 al 2024-12-31. Nel conto dell'asticella: 76 serie.

* Moduli 5559 (scartati dalla pulizia del prezzo 39); titoli con i prezzi 538 (rotti 0); **segnali 2644**; operazioni possibili 2644, fuori {'senza ingresso': 0, 'uscita oltre il 2024 o senza prezzo': 0}; **scelte 2615** (al massimo 10 insieme), in guadagno prima dei costi 61%; **a operazione prima dei costi +0.223%** (t 5.43).
* **Lo scarto misurato** (campione di 500 ingressi a caso): in seduta 152 misure, mediana 7.6 punti base (media 21.4, 90° percentile 46.7); fuori seduta 294 misure, mediana 103.6 (media 344.6, 90° percentile 562.6).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +77.3% / -44.3% / -84.4% | +240.0% |
| **1.** Sharpe annuo con i costi | **-0.89** (senza costi 0.95) | 0.87 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 27, t -2.68) | — |
| **3.** Sharpe con i costi doppi (> 0) | -2.82 | — |
| **4.** Trimestri in guadagno (60%) | 7 su 32 (22%) | — |
| Perdita massima dal picco | -44.4% | -33.8% |
| Coperta con lo SPY (da leggere) | Sharpe -2.59, -53.7% | — |
| Anno per anno | 2016: -2.9% 2017: -7.0% 2018: -5.5% 2019: -3.4% 2020: -18.2% 2021: -3.9% 2022: -5.9% 2023: -4.9% 2024: -4.0% | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela** (giorni in comune dal 2016-11-01 al 2024-12-31): Sharpe della parte -0.91, con i costi doppi -2.82; correlazione con la miscela 0.24 (soglia 0,3); miscela nuova 0.80 contro 1.08 della miscela e 0.89 del tenere lo SPY; **t dello Sharpe della parte -2.68 (soglia 1,3)**; **miscela nuova più alta nel 0% dei campionamenti (soglia 80%)**. **Esito: non entra**

**Da leggere accanto (non cambiano l'esito).** Per fascia dell'ingresso:

| Fascia | Operazioni | A operazione prima dei costi | Meno lo SPY negli stessi minuti | Dopo scarto e slittamento | Dalla chiusura prima del deposito all'ingresso |
|---|---|---|---|---|---|
| tutte | 2615 | +0.223% (t 5.43) | +0.221% (t 7.37) | -0.187% | +0.289% |
| in seduta | 802 | +0.128% (t 1.36) | +0.217% (t 2.98) | +0.050% | +0.218% |
| dopo la chiusura | 1247 | +0.317% (t 5.47) | +0.261% (t 7.09) | -0.241% | +0.326% |
| prima dell'apertura | 566 | +0.153% (t 3.34) | +0.138% (t 3.14) | -0.404% | +0.306% |

Con altri ritardi dopo l'accettazione: 1 min: 2616 operazioni, a operazione prima dei costi +0.232%, Sharpe con i costi -0.85; 2 min: 2615 operazioni, a operazione prima dei costi +0.223%, Sharpe con i costi -0.89; 5 min: 2615 operazioni, a operazione prima dei costi +0.213%, Sharpe con i costi -0.94; 15 min: 2616 operazioni, a operazione prima dei costi +0.215%, Sharpe con i costi -0.90; 60 min: 2614 operazioni, a operazione prima dei costi +0.180%, Sharpe con i costi -1.10.

Limite noto: gli orari d'accettazione vengono dagli elenchi dei depositi delle aziende dell'S&P 500 in cache (25 moduli senza ora). Nel conto: 2 prove (89).
