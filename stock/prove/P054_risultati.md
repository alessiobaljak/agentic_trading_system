# Prova 54 — risultati

Calcolato da `python -m stock.prove.p054` il 2026-11-28 10:45 UTC con le regole di `P054_ciclo_banca_centrale.md` (committate prima). SPY rettificato di Yahoo, DTB3 di FRED (il valore del giorno prima, /360 per giorno di calendario). Periodo di ricerca dal 2016-01-04 al 2024-12-31; campione dello studio dal 1994-01-03 al 2015-12-31. Comunicati: 176 riunioni programmate 1994-2015 (`stock/dati/fomc.py`, `COMUNICATI_1994_2015`) e 71 del 2016-2024. Nel conto dell'asticella: 110 serie.

* In mercato nel 2016-2024 il 52.6% dei giorni (222 finestre), nel 1994-2015 il 53.3% (prima del primo comunicato, 4 febbraio 1994, nessun ciclo: 24 giorni fuori). Contanti: circa 2.00% l'anno nel 2016-2024, 2.61% nel 1994-2015.
* Con la riunione senza comunicato del 15 settembre 2003 i giorni in mercato sarebbero gli stessi.

## L'esame da sola

| 2016-2024 (decide) | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +62.6% / +48.0% / +34.7% | +235.3% |
| **1.** Sharpe annuo con i costi | **0.40** (senza costi 0.49) | 0.84 |
| **2.** Sharpe corretto (soglia 0.80) | 0.01 (lo Sharpe annuo del migliore fra prove senza vantaggio 1.21; gruppi 37, di cui 6 perdenti fuori dalla varianza; con tutti i gruppi nella varianza 0.00; t dello Sharpe 1.21) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.32 | — |
| **4.** Trimestri in guadagno (60%) | 23 su 32 (72%) | — |
| Sharpe con i contanti a zero (come le prove prima della 54) | 0.33 (+35.7%) | — |
| Volatilità annua | 12.8% | 17.8% |
| Perdita massima dal picco | -24.1% | -33.7% |
| Giorni in mercato | 52.6% (1190 su 2264) | 100% |
| Anni in guadagno | 7 su 9 | 7 su 9 |
| **Esito da sola** | **non passa** | |

| 1994-2015 (campione dello studio: si legge) | La strategia | Tenere lo SPY |
|---|---|---|
| Guadagno totale senza costi / con i costi / costi doppi | +1625.9% / +1197.2% / +874.9% | +555.7% |
| **1.** Sharpe annuo con i costi | **0.89** (senza costi 0.99) | 0.54 |
| **2.** Sharpe corretto (soglia 0.80) | 0.07 (lo Sharpe annuo del migliore fra prove senza vantaggio 1.21; gruppi 37, di cui 6 perdenti fuori dalla varianza; con tutti i gruppi nella varianza 0.00; t dello Sharpe 4.19) | — |
| **3.** Sharpe con i costi doppi (> 0) | 0.80 | — |
| **4.** Trimestri in guadagno (60%) | 62 su 84 (74%) | — |
| Sharpe con i contanti a zero (come le prove prima della 54) | 0.81 (+887.7%) | — |
| Volatilità annua | 14.2% | 19.2% |
| Perdita massima dal picco | -25.5% | -55.2% |
| Giorni in mercato | 53.3% (2953 su 5540) | 100% |
| Anni in guadagno | 21 su 22 | 18 su 22 |
| **Esito da sola** | **non passa** | |

## Per entrare nella miscela (2016-2024)

Giorni in comune con la miscela della prova 25 dal 2016-11-01 al 2024-12-31 (2054): Sharpe della parte 0.30, con i costi doppi 0.22; correlazione con la miscela **0.68** (soglia 0,3); miscela nuova (3/4 miscela, 1/4 la parte, in memoria: non entra nel conto) **0.91** contro 1.08 della miscela e 0.87 del tenere lo SPY; **t dello Sharpe della parte 1.21, senza marzo 2020 1.68** (soglia 1,3 tutti e due); **miscela nuova più alta nel 2% dei campionamenti** (2000 a blocchi di 20 giorni, soglia 80%). **Esito: non entra**

Nel 1994-2015 l'esame della miscela non si può fare: la miscela della prova 25 esiste solo dal novembre 2016.

## Da leggere accanto (non cambiano l'esito)

Lo SPY (da chiusura a chiusura, senza costi) nei giorni del ciclo: giorni, rendimento medio in punti base al giorno (t), volatilità annua, Sharpe annuo.

| 2016-2024 | Giorni | Media (t) | Volatilità | Sharpe |
|---|---|---|---|---|
| settimane pari (in mercato) | 1190 | +4.07 (t 1.23) | 18.1% | 0.57 |
| settimane dispari 1, 3, 5 | 1020 | +6.92 (t 2.25) | 15.6% | 1.12 |
| tutti i giorni fuori | 1074 | +8.10 (t 2.40) | 17.6% | 1.16 |

| 1994-2015 | Giorni | Media (t) | Volatilità | Sharpe |
|---|---|---|---|---|
| settimane pari (in mercato) | 2953 | +9.66 (t 4.21) | 19.8% | 1.23 |
| settimane dispari 1, 3, 5 | 2483 | -2.12 (t -0.90) | 18.7% | -0.29 |
| tutti i giorni fuori | 2587 | -2.19 (t -0.96) | 18.5% | -0.30 |

Anno per anno, la strategia con i costi (lo SPY fra parentesi):

* 2016-2024: 2016 +16.7% (+12.0%), 2017 +9.4% (+21.7%), 2018 -14.0% (-4.6%), 2019 +16.6% (+31.2%), 2020 -14.0% (+18.3%), 2021 +9.5% (+28.7%), 2022 +0.3% (-18.2%), 2023 +11.4% (+26.2%), 2024 +9.9% (+24.9%).
* 1994-2015: 1994 +8.7% (+0.4%), 1995 +10.0% (+38.0%), 1996 +14.1% (+22.5%), 1997 +22.3% (+33.5%), 1998 +35.5% (+28.7%), 1999 +23.9% (+20.4%), 2000 +18.4% (-9.7%), 2001 +9.9% (-11.8%), 2002 -6.2% (-21.6%), 2003 +30.7% (+28.2%), 2004 +2.7% (+10.7%), 2005 +5.5% (+4.8%), 2006 +0.8% (+15.8%), 2007 +6.1% (+5.1%), 2008 +4.6% (-36.8%), 2009 +17.2% (+26.4%), 2010 +26.3% (+15.1%), 2011 +5.5% (+1.9%), 2012 +9.4% (+16.0%), 2013 +11.6% (+32.3%), 2014 +6.2% (+13.5%), 2015 +18.0% (+1.2%).

* **I giorni in avanti** (da leggere; il periodo chiuso non si apre: di settembre 2026 solo le date dal 16 e la chiusura del 2026-09-30): dal 2026-10-01 al 2026-11-27, 41 giorni di borsa, in mercato 21. La strategia con i costi **-2.32%** (costi doppi -2.51%), tenere lo SPY **-4.50%**. Lo SPY nei giorni delle settimane pari -11.7 punti base al giorno (21 giorni), negli altri -8.5 (20 giorni). Comunicati usati: 2026-09-16 e 2026-10-28.

## Ambiguità chiuse così (la lettura più letterale delle regole; scelte nel programma prima della prima esecuzione)

* **Le riunioni senza comunicato.** Fino al marzo 1999 la banca centrale non pubblicava un comunicato dopo le riunioni senza cambi (30 delle 48 riunioni del 1994-1999): il giorno 0 è comunque l'ultimo giorno della riunione programmata, come nello studio.
* **Il 15 settembre 2003.** La pagina della Fed elenca una riunione il 15 e una il 16; il comunicato e i documenti per la decisione sono del 16: il 15 resta fuori (con il 15 dentro i giorni in mercato sono gli stessi, controllato sopra).
* **Prima del 4 febbraio 1994** (il primo comunicato della storia) non c'è un «comunicato più recente»: quei giorni sono fuori, tranne il 3 febbraio (giorno −1). Nessuna riunione del 1993 aggiunta.
* **I contanti.** Rende il tasso anche il 2% non investito nei giorni in mercato (`METODO.md`: «i contanti di una prova»). «Il valore del giorno prima» è l'ultimo DTB3 pubblicato con data prima del giorno di borsa; interesse semplice, DTB3/360 per ogni giorno di calendario dalla chiusura di borsa prima.
* **Il 98%** si applica al rendimento di ogni giorno (0,98 × lo SPY), come le prove 49-52; si paga solo quando la quota passa da 0 a 98% o al contrario.
* **Le settimane dispari** da leggere sono le settimane 1, 3 e 5 (d da 4 a 8, da 14 a 18, da 24 a 28, tolti i giorni −1); accanto, tutti i giorni fuori (anche d da 34 in su e i giorni senza ciclo).
* **Nel conto 1 prova**, come scritto nelle regole: si salva solo `serie/P054_ciclo.csv`; la miscela nuova (3/4 e 1/4) si calcola in memoria e non entra nel conto (le prove 48-53 salvavano anche la miscela e contavano 2).
* **Il 1994-2015 «con lo stesso esame»**: le stesse quattro condizioni con le stesse funzioni; lo Sharpe corretto con lo stesso conto delle serie (tutte del 2016-2024); i trimestri dalle finestre che avanzano dal 1994 (primo trimestre di prova il 1995). L'esame della miscela non si può fare (la miscela della prova 25 parte nel novembre 2016).
* **L'inizio e la fine dei campioni**: il conto parte prima (dal 1993 e dal giugno 2015) e si taglia al primo giorno del campione, come la prova 52: il primo giorno la posizione è già quella della regola, senza il costo d'ingresso; l'ultimo giorno nessuna vendita forzata.
* **I giorni in avanti** partono dal rendimento del 1° ottobre 2026 (dalla chiusura del 30 settembre), senza posizione e con il costo d'ingresso; d si conta dal comunicato del 16 settembre 2026 con le date dei giorni di borsa di Yahoo. Nessun rendimento del periodo chiuso è calcolato.
* **Tenere lo SPY** è lo SPY rettificato di Yahoo sugli stessi giorni (come la prova 52).

Nel conto: 1 prova (SPY, una variante).
