# Programma 7 — ottava prova: il long dopo una salita enorme, su Gate.io (G7)

Scritto il 23 ottobre 2026, **prima del calcolo**. Idea 30 della coda di `research/REGISTRO.md`.

## 1. Perché, e da dove viene

G5 (prova 62) vendeva il giorno dopo una salita di almeno +30% in un giorno sui perpetui di Binance: −2,71% a evento, perché nella
metà dei casi la moneta saliva di un altro 30%; senza uscita lo short perdeva il 6,6% a evento. **L'ipotesi è nata guardando quei
dati**: le salite enormi continuano (la corsa alla leva e l'attenzione portano altri compratori). Per questo si prova **su dati che
quell'idea non ha visto**: i perpetui di Gate.io sulle monete che quel giorno **non avevano il perpetuo su Binance**. Riserva: una
parte di queste monete (nei loro giorni 30-37 di vita) è entrata nella prova 30 (N3 su Gate.io); il resto non è mai stato usato.

## 2. La regola (valori fissati qui; le uscite sono lo specchio di quelle di N3 e G5)

* **Contratti**: i perpetui USDT di Gate.io che sono monete (`tipi_gate`, niente monete stabili, niente `seconda.ESCLUSI`), con
  almeno **30 giorni** di candele prima dell'evento, **senza il perpetuo su Binance** alla data d'ingresso (o con il primo giorno
  su Binance dopo), volume non zero il giorno dell'evento.
* **L'evento**: un giorno con rendimento (apertura → apertura dopo) di almeno **+30%**. Al massimo un evento per moneta ogni 30
  giorni (il primo).
* **L'operazione**: all'apertura del giorno dopo, **long la moneta e short il Bitcoin** (perpetuo di Gate.io) per lo stesso
  valore; uscita se il minimo di un giorno va sotto il **−30%** dall'entrata (a −30% con l'1% di scarto), altrimenti all'apertura
  dopo **30 giorni**; costi come N3 su Gate.io (`ventunesima.COSTO_MONETA` e `COSTO_BTC`), funding vero di Gate.io (il long paga il
  funding positivo della moneta, lo short del Bitcoin lo incassa).
* Ingressi dal 1 febbraio 2023 al 31 agosto 2026 (i dati di Gate.io vanno dal gennaio 2023 al settembre 2026). Una prova a eventi:
  nel conto diventano **129**.

## 3. L'esame

Come N3 (`trentesima.esame`): media per evento sopra zero con **p ≤ 0,01** (bootstrap sulle settimane d'ingresso), positiva nelle
due metà e senza i 5 eventi migliori. Si riportano anche la versione senza l'uscita a −30% e per anno.
