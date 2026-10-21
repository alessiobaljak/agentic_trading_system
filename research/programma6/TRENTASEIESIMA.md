# Programma 6 — trentaseiesima prova: la tendenza a 1 giorno nel verso del funding (T5)

Scritto il 21 ottobre 2026, mattina, **prima del calcolo**. Idea 14 della coda di `research/REGISTRO.md`.

## 1. Perché

A 4 ore gli indicatori non battono i costi (prove 34 e 35). A 1 giorno le tendenze durano di più e i costi pesano meno: la
regola di tendenza pubblicata (A1, Zarattini e altri 2025: la media di 9 canali di Donchian, con il peso secondo la
volatilità) fa Sharpe 0,53 long sulle 20 più scambiate, 0,25 long e short (A2). Qui la tendenza si prende **solo nel verso
che il funding dice giusto**: long quando la tendenza sale e a pagare sono gli short (funding basso), short quando scende e
pagano i long (funding alto).

## 2. La regola

* **Monete**: ogni giorno l'universo della settimana (le 100 più scambiate, terza prova, dati corretti).
* **Segnale** di ogni moneta alla chiusura del giorno: quello della regola pubblicata con il lato short (`seconda.segnale_moneta`
  con `short=True`, da −1 a +1) per il moltiplicatore della volatilità (`seconda.moltiplicatore`: 25% l'anno, al massimo 2).
* **Filtro**: la parte long del segnale vale solo se il funding dei 7 giorni è nel **40% più basso** dell'universo di quel
  giorno, la parte short solo se è nel **40% più alto**; altrimenti zero.
* **Peso** di una moneta: segnale × moltiplicatore / **40** (al massimo 40 monete per lato passano il filtro).
* Si opera all'apertura del giorno dopo; costi e funding come la seconda prova (`seconda.portafoglio`).
* Una prova: nel conto del programma 6 diventano **60**.

## 3. L'esame

Dal **1 gennaio 2021**, l'esame giornaliero della seconda prova (`seconda.esame_a`, `seconda.esito_a` senza la condizione
sull'articolo) con lo Sharpe corretto sulle **60** prove (365 periodi l'anno). Si riportano anche la stessa regola senza il
filtro (A2 sull'universo delle 100, solo per capire) e la correlazione con F5.
