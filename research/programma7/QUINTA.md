# Programma 7 — quinta prova: il tetto del 10% per moneta in F5 e in G1 (F5T, G1T)

Scritto il 23 ottobre 2026, mattina, **prima del calcolo**. Voce P19 del backlog, trovata dal revisore indipendente
(`programma6/CONTROLLO_PARITA.md`): con i pesi secondo l'inverso della volatilità TRX arriva al 32,5% del lato long di F5 ed è
sopra l'8% in 111 settimane su 302. Una moneta sola che crolla peserebbe troppo. F5 e G1 sono nel paper del bot e i primi cambi
veri sono stanotte (G1, 24 ottobre) e lunedì (F5, 26 ottobre): la decisione va presa prima.

## 1. La regola (valori fissati qui)

* F5 (prova 24, con le parità corrette) e G1 (prova 57) **come sono**, con un solo cambio: dopo i pesi secondo l'inverso della
  volatilità, **nessuna moneta può pesare più del 10% del suo lato**; quello che supera va alle altre monete dello stesso lato in
  proporzione ai loro pesi, e si ripete finché nessuna supera il 10%. Se un lato ha meno di 10 monete, pesi uguali.
* Esecuzione: F5T a mercato come F5 (prova 24), G1T con gli ordini limite come G1 (prova 57). Periodo e costi come le prove di
  partenza. Due prove: nel conto diventano **125**.

## 2. L'esame e la decisione (fissati qui)

* `terza.esame` e `terza.esito`, Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95 (come sempre).
* **Per il bot**: il tetto serve a togliere un rischio, non a guadagnare di più. Se la versione con il tetto ha uno Sharpe **non più
  basso di 0,05** di quella senza, sulle stesse settimane, e una discesa massima non peggiore, F5 e G1 nel bot prendono il tetto
  prima del primo cambio; altrimenti restano come sono e il rischio di concentrazione resta scritto.
