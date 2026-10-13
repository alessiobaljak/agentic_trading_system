# Prova degli ordini limite — risultati

Le regole sono in `regole.md` (in vigore dal 2026-10-13 07:13 UTC) e non cambiano. Questo file si scrive in ordine di
tempo: prima le correzioni trovate dopo il lancio (sezione 1, ognuna con cosa è cambiato e perché), poi le impronte
degli strumenti, la parità M, le corse L e (b), le varianti, le misure e l'esito. Nessun numero di L compare prima
che la parità M sia passata su tutte e nove le strategie.

## 1. Correzioni alle regole, trovate dopo il lancio (prima di qualunque numero)

### Correzione 1 — l'ordine in attesa si riempie al suo prezzo, non all'apertura (13 ott 2026, 07:48 UTC)

**Cosa diceva la regola.** La 4.3 dice: «Prezzo di riempimento: P, oppure l'apertura di `k+1` se è già sotto P (il
mercato apre più in basso: si compra meglio)».

**Cosa è sbagliato.** Questo vale per un ordine A MERCATO mandato all'apertura. Un ordine LIMITE messo alla chiusura di
`k` è già nel libro quando la barra `k+1` apre: se il primo scambio avviene sotto P (per un long), l'ordine è stato
eseguito **a P** dal primo venditore che ha attraversato quel prezzo, non all'apertura. Riempirlo all'apertura
avrebbe regalato al trade la differenza fra P e l'apertura, cioè un vantaggio che un ordine limite non ha.

**Cosa cambia.** Nel motore (`riempimento_limite`) e nella variante (c) (uscita «chiudi» a limite): se la barra apre
oltre il prezzo, il riempimento è certo e avviene all'apertura della barra, **ma al prezzo del limite**. Il momento
resta l'apertura: così la regola dei gap del percorso a mercato vale anche qui (se l'apertura è già oltre lo stop,
si esce allo stop all'apertura: perdita oltre 1R, il caso peggiore e quello vero). Con il riempimento sempre a P, il
rischio iniziale vero è sempre quantità × |P − stop| = 1% del capitale, salvo il tetto di leva.

**Perché si corregge e non si lascia.** La regola 4.3 è stata scritta pensando all'ordine a mercato; l'errore è
stato visto scrivendo i test del motore (il caso «la barra apre oltre il limite»), prima di qualunque corsa sui
dati. Lasciarla avrebbe reso la prova ottimista proprio sui trade che partono con un gap a favore.

**Quando.** Trovata e corretta prima del lancio delle corse: nessun numero da rifare.

### Nota 1 — i 30 minuti sono aggregati dai 15 minuti solo per SOLUSDT-023

La sezione 2 dice «30 minuti aggregati da 15 come nelle campagne». Dai log delle campagne: SOLUSDT-023 usava i 30
minuti aggregati dai 15; BTCUSDT-V35, ETCUSDT-033 e AVAXUSDT-V-12 usavano i file nativi a 30 minuti di Binance. La
prova fa come ogni campagna ha fatto (è la condizione della parità M), quindi tre strategie su quattro a 30 minuti
usano i file nativi. Non è una correzione alle regole di esecuzione: è una precisazione sui dati.

## 2. Gli strumenti

* `research/src/motore.py`: ingresso «limite» con validità in barre e condizione «attraversato»/«toccato»,
  commissione maker, uscita «chiudi» a limite (variante (c)); nessun cambiamento al percorso «mercato» (test di
  parità bit per bit con il motore del commit 39bb60b2). Riga nel `CHANGELOG.md` della ricerca del 2026-10-13.
* `research/src/tests/test_motore_ordini_limite.py`: 34 casi su candele sintetiche (eseguito, saltato, apertura
  oltre il limite, stop nella stessa barra, sostituzione, variante (c), parità).
* Lo script delle corse e le impronte SHA-256 al momento del lancio: sezione 3, quando si lancia.

## 3. Impronte al lancio

_(da scrivere al lancio delle corse)_

## 4. Parità M

_(da scrivere: nessun numero di L prima di questa sezione)_
