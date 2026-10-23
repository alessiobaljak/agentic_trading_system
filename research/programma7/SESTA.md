# Programma 7 — sesta prova: lo short dopo le grandi salite di un giorno (G5)

Scritto il 23 ottobre 2026, **prima del calcolo**. Un'idea nuova della coda (eventi con movimenti grandi, la lezione di G2 e G3).

## 1. Perché

Le salite enormi di un giorno nelle monete piccole sono spesso spinte organizzate o corse alla leva che poi si sgonfiano: lo studio
dei gruppi «pump and dump» (Li, Shin e Wang 2021; Hamrick e altri 2021) trova che il prezzo torna indietro nei giorni dopo. Fra le
nostre prove: le monete nuove scendono dopo la quotazione (N3, prova 32) e le monete col funding alto (dove la folla è long a leva)
rendono meno (F5). Mai provato: vendere il giorno dopo una salita di un giorno molto grande, su monete già quotate da tempo. Il
movimento atteso è grande (decine di punti), quindi i costi pesano poco.

## 2. La regola (valori fissati qui; le uscite e i costi sono quelli di N3, non scelti qui)

* **Monete**: i perpetui USDT di Binance del pannello (esclusi i contratti che non sono monete), con almeno **30 giorni** di vita
  (le più giovani sono il campo di N3) e la mediana del volume dei 30 giorni prima di almeno **2 milioni** di USDT.
* **L'evento**: un giorno con rendimento (apertura → apertura dopo) di almeno **+30%**.
* **L'operazione**: alle 00:00 UTC del giorno dopo, short la moneta e long il Bitcoin per lo stesso valore (come N3); uscita a +30%
  della moneta (candele a 1 ora, 1% di scarto) o dopo 30 giorni; costi e funding come N3 (`trentesima.operazione`).
* Al massimo un evento per moneta ogni 30 giorni (il primo). Dal 4 gennaio 2021 al 10 settembre 2026. Una prova a eventi: nel
  conto diventano **126**.

## 3. L'esame

Come N3 (`trentesima.esame`): media per evento sopra zero con **p ≤ 0,01** (bootstrap sulle settimane d'ingresso), positiva nelle
due metà e senza i 5 eventi migliori. Si riportano anche la versione senza l'uscita a +30% (solo per capire), gli eventi fra le
100 più scambiate e fuori, per anno.
