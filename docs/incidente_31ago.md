# L'incidente del 31 agosto — e cosa recuperiamo

## Cosa è successo, in parole semplici

Immagina un magazzino con 3.000 posti.

Da una parte ci sono le **strategie scritte a mano** (8 per ogni crypto). Da
un'altra le **strategie inventate dal sistema** — e sono le *uniche* che superano
l'esame. Le prime non lo passano mai.

Il magazzino aveva una regola: *«quando è pieno, butta fuori le inventate»*. Sembrava
prudente — le scritte a mano sono il prodotto di un altro processo, non si toccano.

Ma nessuno toglieva mai le scritte a mano di crypto che **non guardiamo più**. La
lista delle crypto cambia ogni giorno, e ogni crypto uscita lasciava 8 posti occupati
per sempre. Sono cresciute fino a **3.041** — cioè hanno riempito il magazzino **da
sole**.

A quel punto la regola faceva il conto: *posti liberi per le inventate = 3.000 − 3.041
= zero*. E le buttava **tutte fuori, a ogni giro**.

Quindi: la ricerca trovava ottanta strategie buone ogni tre ore, le metteva in
magazzino, e il magazzino le buttava un istante dopo. **Nessun errore, nessun
allarme.** Solo un sistema che girava a vuoto.

## Quanto abbiamo perso — con la data, non a sensazione

Il registro ha superato i 3.000 posti **fra il 27 e il 31 agosto**:

| data | coppie nel registro |
|---|---|
| 14 ago | 1.504 |
| 19 ago | 2.615 |
| 21 ago | 2.807 |
| 27 ago | 2.992 |
| **31 ago** | **3.041 — tetto superato** |

**Il danno è di 2-3 giorni, non di due settimane.** Nel messaggio di ieri avevo
scritto «per settimane»: era sbagliato, e il dato lo smentisce. Fino al 27 agosto il
registro accumulava correttamente — c'erano **137 coppie con una conferma**.

Quello che si è perso davvero:

* le **137 prime conferme** accumulate fra il 21 e il 27 agosto, cancellate fra il 29
  e il 31. Ognuna valeva una settimana di attesa;
* la **prova che doveva arrivare fra il 28 agosto e il 2 settembre** — quella che
  doveva dire se una strategia che passa l'esame lo ripassa una settimana dopo. Non
  ha fallito: **non è stata eseguita**, perché le coppie sono state cancellate prima.

Non è "tutto da buttare". È **circa dieci giorni di accumulo**, e la risposta alla
domanda che conta rimandata.

## Perché ce ne siamo accorti solo ora

La risposta onesta è scomoda: **ogni singolo numero che guardavamo era vero.**

* «80 candidate hanno passato il gate» — vero.
* «3.041 coppie nel registro» — vero, e sembrava perfino un segno di crescita.
* «il tasso di passaggio sale da 23 a 80» — vero.

Nessuno confrontava mai **quello che la ricerca produce** con **quello che il registro
conserva**, e nessuno guardava *di che cosa* fosse fatto quel 3.041. Un totale non
dice mai se dentro c'è quello che serve.

E i 716 test erano tutti verdi perché nessuno provava il registro **quando è pieno**.
Le due funzioni, prese singolarmente, facevano esattamente ciò che dicevano.

L'ho trovato solo perché mi sono rifiutato di spiegare il crollo da 137 a 2 con una
storia plausibile: nessuna delle mie ipotesi tornava con i numeri, quindi ho aggiunto
i conteggi che mancavano invece di dedurre. **Quel processo ora è automatico** (vedi
sotto): è il vero rimedio, perché non dipende da me che me ne accorga.

## Cosa ho corretto

1. **La causa** (`scripts/optimize.py`): le coppie base di crypto uscite
   dall'universo da più di sei giorni, e senza conferme, vengono rimosse. Stesso
   criterio già applicato alle generate — non c'era ragione perché ne fossero esenti.
   Chi rientra nella lista viene ricreata al primo giro.
2. **La garanzia** (`scripts/discover_strategies.py`): il tetto **non può più
   cancellare una coppia che ha già una conferma**. Se per tenerle si sfora il tetto,
   si sfora — e lo si scrive nel log. Cancellare conferme vere è il solo prezzo che
   non si paga.
3. **L'allarme** (`scripts/state_snapshot.py`): ogni ora il rapporto committato
   riporta la **composizione** del registro e accende un allarme rosso se le coppie
   generate sono zero, o arancione se le base occupano oltre il 90% del tetto. È il
   confronto che nessuno faceva, ora fatto da solo e leggibile senza entrare sulla
   macchina.

Una quarta difesa che avevo scritto era codice morto e un test l'ha smascherata
subito: proteggeva un insieme sempre vuoto. Tolta.

## Il piano per recuperare il tempo

C'è uno strumento costruito apposta, `scripts/fast_gate.sh`, e **oggi costa quasi
nulla usarlo**.

**Cosa fa.** Un pass conta solo dopo una settimana di dati nuovi, quindi tre conferme
richiedono tre settimane di calendario. Ma non serve aspettare che il tempo passi:
basta far **finire i dati** in tre momenti diversi, distanti più di una settimana. Il
sistema vede tre finestre e tre verifiche finali diverse — esattamente le tre conferme
che avremmo raccolto aspettando. In poche ore invece che in tre settimane.

**Non abbassa nulla.** Stesse soglie, stesso gate, stesse finestre. Una strategia che
passa solo con i dati di oggi e non con quelli di due settimane fa **non si valida**:
è proprio il caso che la regola vuole scartare, e viene scartato subito invece che
fra tre settimane.

**Perché adesso e non prima.** Richiede di azzerare il registro, e finora questo
significava buttare via settimane di conferme accumulate — un prezzo troppo alto. Oggi
le coppie con conferme sono **due**. Il costo dell'azzeramento è praticamente zero, e
non ricapiterà una finestra così.

**Il rischio, detto per intero:** è irreversibile da remoto. Il backup che scrive resta
sul disco della macchina, fuori da git, e non esiste uno script che lo ripristini.
Dura ore. Se si interrompe a metà lascia il registro incompleto.

**Non lo lancio io.** Serve la tua decisione esplicita, ed è la ragione per cui non è
mai stato messo in lista bianca.

### L'ordine giusto

1. **Prima verificare che la correzione funzioni**: al prossimo giro dell'optimizer le
   base morte devono sparire e il registro tornare sotto il tetto. Richiesta già in
   coda. Lanciare `fast_gate` su un registro ancora rotto ributterebbe via tutto.
2. **Poi, e solo se il punto 1 è a posto**, lanciare l'acceleratore:
   ```bash
   tmux new -s fastgate
   bash scripts/fast_gate.sh --yes
   ```
3. **Nel giro di ore** si sa se qualche strategia regge tre verifiche distanziate —
   la risposta che aspettavamo per il 5 settembre.
