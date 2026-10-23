# Programma 6 — cinquantacinquesima prova: un solo punteggio da F5, K2 e M7 (C3)

Scritto il 23 ottobre 2026, notte, **prima del calcolo**. Idea nuova: le tre strategie migliori del programma (F5 il funding,
K2 il denaro che entra con la leva che costa poco, M7 il modello ad alberi) finora sono state unite **come portafogli**
(F5 + M7 + K2 a rischio uguale, prova 28: Sharpe 2,11, corretto rivisto 0,90). Qui si uniscono **i segnali**: per ogni moneta un
punteggio unico, e un portafoglio solo.

## 1. Perché

Unire tre segnali poco legati in un punteggio solo dà un portafoglio con meno giri (una moneta che due segnali vogliono e uno no
non entra e non esce a ogni cambio) e più diversificato dentro: è il modo standard dei gestori quantitativi di unire i fattori
(per esempio Asness, Moskowitz e Pedersen, «Value and Momentum Everywhere», 2013: la combinazione dei segnali batte i segnali
da soli). Il funding fra monete (F5) e il modello (M7) hanno correlazione 0,31 (prova 25).

## 2. La regola (valori fissati qui)

* **Monete**: l'universo della settimana (le 100 più scambiate, dati corretti).
* **I tre ranghi** fra le monete dell'universo, ognuno fra −0,5 e +0,5 (`terza.ranghi`): −funding dei 7 giorni (F5); il segnale
  di K1 (`dodicesima.segnale_k1`); la previsione di M7 (la media dei ranghi dei 5 semi, `ventitreesima`, come la prova 25).
* **Punteggio** = la media dei ranghi disponibili, con il funding sempre presente e almeno 2 su 3.
* **Portafoglio**: la banda di F5 sul punteggio (entrata nel 20%, uscita oltre il 40%), pesi secondo l'inverso della volatilità
  dei 30 giorni, ogni lato al 100%; costi e funding come F5 (`terza.conto`).
* Dal 3 gennaio 2022 (inizio di M7 e K2) al 5 ottobre 2026. Una prova: nel conto diventano **118**.

## 3. L'esame

`terza.esame` e `terza.esito` sugli anni 2022-2025, con lo Sharpe corretto rivisto (`asticella.py`), soglia 0,95. Si riportano
anche F5 + M7 + K2 a portafogli sulle stesse settimane, il giro medio e le spese, la correlazione con F5.
