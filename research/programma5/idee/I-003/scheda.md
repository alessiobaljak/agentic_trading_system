# I-003 — Continuazione quando l'esplosione arriva con posizioni nuove

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo su questa idea** (REGOLE.md, sezione 6).

## Perché

Un'esplosione in cui l'interesse aperto **cresce** non è fatta di chiusure forzate ma di posizioni nuove: denaro che entra
con una direzione e spesso con un'informazione (una notizia, un ordine grande). Se è così, il movimento continua nei
minuti dopo, al contrario dei crolli fatti di liquidazioni (I-001). La prima analisi dello scalping non distingueva i due
casi e trovava, in media, nessuna direzione.

## La regola

* **Esplosione** alla chiusura del minuto t: |ln(chiusura_t / chiusura_{t−5})| **maggiore di L volte** la mediana di |r5|
  delle 24 ore prima, in tutte e due le direzioni.
* **Posizioni nuove**: variazione dell'interesse aperto fra le ultime due rilevazioni note nel **5% più positivo** dei 30
  giorni prima.
* **Ingresso** nella direzione dell'esplosione (long se è salito, short se è sceso) all'apertura del minuto t+1, a
  mercato; **uscita** a tempo (vedi varianti); pausa per moneta pari alla durata del trade; costi del programma con lo
  scarto doppio; funding.

## Le varianti (3)

| Variante | L | Uscita |
|---|---|---|
| I-003a | 8 | 15 minuti |
| I-003b | 8 | 60 minuti |
| I-003c | 16 | 60 minuti |
