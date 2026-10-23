# Programma 7 — decima prova: il giorno migliore del mese fra le monete (MAX)

Scritto il 23 ottobre 2026, **prima del calcolo**. Idea 26 della coda di `research/REGISTRO.md` (a settimana, per alternare i tipi).

## 1. Perché

Ozdamar, Akdeniz e Sensoy (2021, *Financial Innovation*) trovano fra le cripto un legame **positivo** fra il rendimento giornaliero
più alto del mese prima (MAX) e il rendimento della settimana dopo: +3,03% a settimana fra il decile più alto e il più basso, al
contrario delle azioni (dove le «lotterie» rendono meno). È un fattore pubblicato mai provato da noi. Probabilità bassa, scritta
nella coda: è un parente del momento, che fra i perpetui dal 2021 non regge (X1, prova 49), e le monete appena salite hanno spesso
il funding alto, che F5 vende.

## 2. La regola (valori fissati qui, il verso è quello pubblicato)

* Ogni lunedì, fra le 100 monete della settimana: MAX = il rendimento giornaliero (apertura → apertura dopo) più alto dei 30 giorni
  prima del lunedì (almeno 20 giorni con il dato).
* **Long** il 20% con il MAX più alto, **short** il 20% con il più basso, con la banda di F5 (si esce oltre il 40%), pesi secondo
  l'inverso della volatilità dei 30 giorni, ogni lato al 100%; costi e funding come F5 (a mercato).
* Dal 4 gennaio 2021 al 5 ottobre 2026. Una prova: nel conto diventano **131**. Il verso opposto si riporta solo per capire, non si
  giudica.

## 3. L'esame

`terza.esame` e `terza.esito`, Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95; correlazione con F5.
