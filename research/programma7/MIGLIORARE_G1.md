# Migliorare quello che già funziona: G1

Scritto il 5 novembre 2026 alle 20:30 UTC, dopo la decisione del proprietario dello stesso giorno: «si cambia, e sono d'accordo
miglioriamo quello che già funziona». Da oggi il giro delle 4 ore raccoglie i dati sempre e poi lavora qui, una voce alla volta; un'idea
nuova di strategia solo con un perché forte (`research/REGISTRO.md`).

**Perché G1.** È la strategia migliore che abbiamo (F5 decisa ogni giorno: funding fra le monete, long chi paga meno, short chi paga di
più): Sharpe 1,96 sul passato di Binance 2021-2026, ogni anno positivo, Sharpe corretto **0,86** dopo tutte le prove (sotto lo 0,90
della regola del proprietario: lo deve accettare lui, `docs/backlog.md` P26). Gira nel paper del bot dal 23 ottobre e sul conto demo
di Binance con ordini veri dal 24 ottobre. **Migliorarla non vuol dire cercarle parametri migliori sul passato** (sarebbe l'errore del
primo gate): vuol dire misurare quanto il demo si allontana dal paper e dal passato, capire perché, e togliere le cause.

**Regola per ogni voce**: prima la misura, con il numero e la fonte; una modifica al bot passa dai test e, se tocca il demo, si dice al
proprietario prima del riavvio; una modifica alle regole di G1 provata sul passato è una prova nel conto (regole scritte prima, revisore
separato prima del paper).

## Le voci, in ordine

1. **Il demo contro il paper, giorno per giorno** — *in corso dal 5 novembre.* Il paper ipotizza che gli ordini limite al mark si
   riempiano quando il prezzo li tocca e che le spese siano quelle del modello; il demo le paga davvero. La differenza giorno per giorno
   fra i due rendimenti è il costo vero dell'esecuzione (più gli eventi al 5%, sul demo dal 31 ottobre). Misura: sezione «G1: il demo
   contro il paper, giorno per giorno» del rapporto di stato (`scripts/state_snapshot.py`, richiesta «stato» del canale ops). Si guarda
   la media e l'oscillazione della differenza; se la media è sotto zero di più di qualche centesimo al giorno, si passa alla voce 2.
2. **Il prezzo vero degli ordini.** Per ogni ribilancio del demo, il prezzo medio a cui gli ordini sono stati eseguiti contro il mark
   al momento della decisione (con il segno: comprare sopra o vendere sotto è un costo), e quanti ordini finiscono a mercato dopo
   l'ora. Oggi il demo scrive solo quanti sono a limite e quanti a mercato (336 eseguiti a limite su 347 al 2 novembre; il paper 488 su
   489). Serve leggere le esecuzioni del conto demo e scriverle per ribilancio.
3. **Il funding incassato davvero.** Il funding è circa metà del guadagno di G1 sul passato (+27% l'anno su 51,5%, revisione di G1N):
   confrontare il funding che Binance accredita al conto demo con quello che il paper si aspetta sulle stesse posizioni.
4. **Le monete che il demo non ha.** Ogni giorno un ordine rifiutato (龙虾USDT, «Invalid symbol» sul demo, che sul conto vero
   esiste): quanto pesa nello scarto fra posizioni vere e volute (2,4% del conto il 2 novembre) e se va tolta anche dal paper per un
   confronto pulito (solo per il confronto, non per i soldi veri).
5. **Meno scambi, se le spese vere sono più alte.** Solo se le voci 1-2 dicono che l'esecuzione costa più del modello: una banda più
   larga o un ribilancio solo dei pesi che cambiano molto, provati sul passato come prova nel conto, con le regole scritte prima.
6. **L'ora della decisione.** G11 (il funding più fresco) gira nel paper accanto a G1 dal 23 ottobre: si guarda in avanti se decide
   meglio; nessuna prova nuova sul passato (il vantaggio di G11 sul passato stava nel 2021).

## Già fatte (dalla revisione con le skill del 1° novembre, `REVISIONE_SKILL_G1.md`)

* Margine unico impostato e controllato dal codice; stop sulla perdita del conto a −35% dal massimo; il pulsante che chiude tutto;
  il confronto ogni giorno fra posizioni vere e volute (`bot/portafoglio/demo_binance.py`).
* Un minimo di monete per lato (prova 124, G1M): toglie il giorno peggiore ma non la discesa, Sharpe 1,95 contro 1,97: non si mette.
* Un tetto del 10% per moneta (prova 61): peggiora Sharpe e discesa: non si mette.

## Diario delle voci

* **5 novembre 2026, voce 1**: aggiunta la sezione del confronto al rapporto di stato, con due test; prima lettura con la richiesta
  «stato» del canale ops.
