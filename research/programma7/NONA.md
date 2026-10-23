# Programma 7 — nona prova: le monete nuove al 7° giorno con l'entrata scelta dentro la giornata (G8)

Scritto il 23 ottobre 2026, **prima del calcolo**. Idea 4 di `METODO.md` («le monete nuove al 7° giorno con l'entrata scelta dentro
la giornata»), con la lezione di G2 e G3.

## 1. Perché

N3 (prova 32) vende le monete nuove di Binance all'apertura del 7° giorno di vita: +4,29% a evento su 613. G2 e G3 (prove 58 e 60)
hanno mostrato che dentro la giornata, dopo la prima ora che chiude oltre l'apertura del giorno, il prezzo tende a tornare indietro
(la continuazione perde già prima dei costi). Per uno short questo vuol dire: **aspettare la prima ora che chiude sopra l'apertura
e vendere lì** dà un prezzo d'entrata più alto e un ritorno indietro a favore. **Riserva:** N3, G2 e G3 sono stati visti; questa è
una variante di N3 nata da quello che abbiamo visto, e si giudica come una prova nuova nel conto.

## 2. La regola (valori fissati qui; il resto come N3)

* **Gli eventi**: gli stessi 613 di N3 su Binance (`risultati_trentaduesima/eventi_N3B.csv`: moneta e 7° giorno di vita).
* **L'entrata**: il 7° giorno, la prima candela da 1 ora (fra quella delle 00:00 e quella delle 19:00) che **chiude sopra
  l'apertura delle 00:00**; short la moneta e long il Bitcoin all'apertura dell'ora dopo. Se non succede, all'apertura delle 21:00.
* **L'uscita**: +30% della moneta dall'entrata (candele a 1 ora, 1% di scarto) o dopo 30 giorni dall'entrata; costi e funding come N3.
* Una prova a eventi: nel conto diventano **130**.

## 3. L'esame e la decisione (fissati qui)

Come N3 (`trentesima.esame`): media per evento sopra zero con **p ≤ 0,01**, positiva nelle due metà e senza i 5 eventi migliori.
Accanto, evento per evento, N3 com'è. **Per il bot**: se G8 passa l'esame e sugli stessi eventi rende almeno **0,5 punti** in più di
N3, l'entrata di N3 nel bot cambia così; altrimenti resta all'apertura del 7° giorno.
