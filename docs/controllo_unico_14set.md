# Il controllo unico del 14 settembre

Nasce da una frase del proprietario: «ogni volta trovi un problema diverso e la mia
pazienza ha un limite». È una critica giusta, e la risposta non è promettere che non
ce ne saranno altri — è **smettere di trovarli uno alla settimana**.

## Non erano problemi diversi

Erano lo stesso problema, cinque volte: **da qualche parte un limite scarta in
silenzio proprio quello che stiamo aspettando.** E saltavano fuori uno alla volta
perché ognuno diventa visibile solo quando la fila arriva a quel gradino.

| gradino | cosa buttava via le conferme | trovato |
|---|---|---|
| arrivare alla 1ª | il tetto del registro cancellava tutte le generate | 31 ago |
| arrivare alla 2ª | la contabilità rendeva la 3ª irraggiungibile | 21 ago |
| arrivare alla 3ª | il taglio della ri-valutazione, ordinato per anzianità | 13 set |
| arrivare alla 3ª | la coin esce dall'universo, la coppia si congela | 14 set |
| arrivare alla 3ª | …e **sei giorni dopo veniva cancellata** | 14 set, questo controllo |

## L'invariante, scritto una volta sola

> **Una coppia con almeno una conferma recente non viene cancellata da nessuna
> potatura, non viene esclusa dalla ri-valutazione, la sua coin resta nell'universo
> guardato, e non perde i campi che la rendono riconoscibile.**

`tests/test_confirmations_are_never_lost.py` lo verifica su **ogni** percorso che può
romperlo. Chi domani aggiunge un tetto, un filtro o una potatura trova un test rosso.

## Cosa ho trovato, in ordine di gravità

### 1. La potatura cancellava le coppie a metà strada — perdita ATTIVA

```python
r.get("pass_count", 0) < MIN_PASSES and r.get("last_seen_at", 0) < stale_before
```

Una coppia generata a **1 o 2 conferme** non vista per sei giorni veniva
**cancellata**. Non per un verdetto: per non essere stata guardata. E la riga sta
dieci righe sopra un commento che promette «le coppie con almeno una conferma non si
toccano MAI».

Le otto coppie ORCAUSDT a 2/3 sarebbero sparite il **19 settembre**. Quante ne siano
già sparite prima non è ricostruibile: cancellato è cancellato. Oggi ce ne sono
**23** nella finestra di rischio (congelate, con almeno un passaggio).

### 2. La potatura delle base: il commento prometteva il contrario del codice

Stessa condizione in `optimize.py`, stesso commento rassicurante, stesso effetto su
una coppia base con una o due conferme.

### 3. Il flag `generated` non sopravviveva all'alleggerimento

Quando il registro supera la soglia, `slim_registry` toglie i campi non essenziali.
`generated` non era protetto. Perderlo ha **tre** conseguenze tutte silenziose: la
potatura delle base cancella la coppia, il tetto smette di considerarla intoccabile,
e la sua spec perde la priorità nella ri-valutazione. Un campo, tre porte.

### 4. Nessuno guardava quanto spazio resta nei documenti

Firestore rifiuta un documento oltre 1 MiB, e due ci si avvicinano. Se cede quello
delle spec, una coppia entra nel registro ma la sua spec non viene salvata: non sarà
mai più ri-valutata. Ora `gate_progress` stampa l'occupazione e avvisa all'80%.

### 5. Il mio stesso errore, mentre correggevo

La prima versione del criterio confrontava `last_pass_data_end` — che è un tempo dei
**dati** — con `time.time()`, che è l'orologio di **parete**. Due orologi diversi: lo
stesso difetto che `judge_window` esiste per chiudere. Tre test sono diventati rossi
subito e l'hanno mostrato. Ora i criteri sono due, espliciti, sullo stesso orologio:

* `conferme_da_proteggere` — «ha conferme e non è abbandonata»: decide le potature;
* `sta_ancora_progredendo` — «sta ancora avanzando»: decide chi tenere nell'universo,
  che costa tempo di calcolo a ogni giro.

## Cosa NON ho toccato

Le soglie del gate, `DRY_RUN`, il conteggio delle finestre, la severità dei criteri.
Nessuna di queste correzioni rende più facile passare: rendono solo possibile
**arrivare in fondo** a chi passa.

## La regola di stop

**21 settembre.** Se per allora non c'è almeno una coppia validata, si smette di
riparare questa pipeline e si cambia cosa si cerca. Scritto prima di vedere il
risultato, come le volte precedenti.
