# Prova 29 — risultati (periodo chiuso, aperto una volta)

Calcolato da `python -m stock.prove.p029` il 2026-11-13 04:06 UTC con le regole di `P029_notizie_cattive_piccole.md` (committate prima). Periodo chiuso dal 2025-01-02 al 2026-09-30.

* Candidati fuori dall'indice con il tono 5381, fondi esclusi 208, senza prezzi 88, con i dati rotti 16; titoli scelti per mese: mediana 50, mesi fuori 0 su 21.
* Ordini eseguiti 1976; senza barra 4; rifiutati 0; **chiusi all'ultimo prezzo perché spariti dal listino: 12**. Costi pagati: commissioni 1,947, scarto e slittamento 3,460 dollari (il prestito è nel valore del conto).
* Il quinto con le notizie peggiori meno l'IWM, mese dopo, senza costi: **-0.59% al mese (t -1.08)**, mediana -0.75%, su 21 mesi (negativo = le notizie cattive scendono, è quello che la vendita allo scoperto guadagna).

| | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | -12.8% / -20.1% / -26.9% | +32.7% |
| **1.** Sharpe annuo con i costi (più alto dello SPY) | **-0.13** (senza costi -0.00) | 1.04 |
| **2.** Sharpe con i costi doppi (> 0) | -0.27 | — |
| **3.** Trimestri in guadagno (almeno 4 su 7) | 3 su 7 | — |
| Perdita massima dal picco | -37.2% | -18.8% |
| Anno per anno | 2025: -19.3% 2026: -0.9% | — |
| Prestito annuo che azzera il guadagno (approssimato) | -6.9% (usato: 3%) | — |
| **Esito da sola** | **bocciata** | |

**Per entrare nella miscela:** Sharpe con i costi -0.13 e con i costi doppi -0.27 (sopra zero); correlazione con lo SPY sul periodo chiuso 0.02 e con la miscela sul 2016-2024 0.02 (soglia 0,3). **Esito: non entra**

**Già visto, non conta** (2016-2024, gli stessi dati da cui è nata l'idea): Sharpe con i costi 0.01, senza costi 0.84, senza prestito 0.27; quinto basso meno IWM -0.63% al mese (t -1.76); perdita massima -20.1%.

Nel conto: 1 prova più 1 apertura del periodo chiuso = 2. Il periodo chiuso ora è usato per la famiglia «notizie».
