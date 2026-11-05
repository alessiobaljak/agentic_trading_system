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

1. **Il demo contro il paper, giorno per giorno** — *prima lettura il 5 novembre: il demo segue il paper (vedi il diario qui sotto).* Il paper ipotizza che gli ordini limite al mark si
   riempiano quando il prezzo li tocca e che le spese siano quelle del modello; il demo le paga davvero. La differenza giorno per giorno
   fra i due rendimenti è il costo vero dell'esecuzione (più gli eventi al 5%, sul demo dal 31 ottobre). Misura: sezione «G1: il demo
   contro il paper, giorno per giorno» del rapporto di stato (`scripts/state_snapshot.py`, richiesta «stato» del canale ops). Si guarda
   la media e l'oscillazione della differenza; se la media è sotto zero di più di qualche centesimo al giorno, si passa alla voce 2.
2. **Il prezzo vero degli ordini** (*meno urgente dopo la prima lettura della voce 1: in 12 giorni non si vede un costo nascosto*). Per ogni ribilancio del demo, il prezzo medio a cui gli ordini sono stati eseguiti contro il mark
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
* **5 novembre 2026, 21:15 UTC, voce 1, prima lettura** (`ops/results/0698-5nov-stato-demo-contro-paper.md`): dal 25 ottobre al
  5 novembre, 12 giorni, **demo +6,80%, paper +6,92%**; differenza media al giorno −0,011%, oscillazione 0,62% al giorno. Con 12 giorni
  l'incertezza sulla media è circa ±0,18% al giorno (0,62 diviso la radice di 12): **nessun costo nascosto misurabile**, il demo esegue
  come il paper. Quasi tutta l'oscillazione sta in due giorni che si compensano (29 ottobre +1,21%, 30 ottobre −1,54%): probabilmente
  l'ora diversa dell'ultimo valore scritto nel giorno, non l'esecuzione; senza quei due giorni la differenza giornaliera sta fra −0,31% e
  +0,39%. Ordini limite eseguiti sul demo 435 su 453 (96%); scarto fra posizioni vere e volute 2,0% del conto. Equity del demo
  5.277,11 USDT dal capitale di 4.992,87 (+5,69% dal 24 ottobre). **Conseguenza**: la voce 5 (meno scambi) non ha motivo per ora;
  le voci 2 e 3 servono a scomporre il guadagno (spese e funding veri), non a correggere un buco.
* **5 novembre 2026, sera, voci 2-3 (sì del proprietario: «ok procedi pure con le due letture e il riavvio»)**: il demo legge ogni ora
  dal conto le entrate vere (`/fapi/v1/income`: funding incassato e commissioni pagate) e le scrive in `/demo_binance/diario/{giorno}/entrate`,
  con i giorni chiusi recuperati dal 24 ottobre (`bot/portafoglio/demo_binance.py`, `entrate_del_conto`; solo lettura, un errore non
  tocca gli ordini); il paper scrive nel diario del giorno i totali di spese e funding (`bot/portafoglio/f5.py`); il rapporto di stato
  ha una seconda tabella, funding e spese del demo contro il paper in % dell'equity (`scripts/state_snapshot.py`). Quattro test
  nuovi, 2.496 test passano. Riavvio del bot chiesto alla macchina (ops 0699).
* **5 novembre 2026, 22:56 UTC, voci 2-3, prima lettura** (`ops/results/0703-6nov-stato-entrate-dal-24-ottobre.md`): dal 24 ottobre al
  5 novembre (13 giorni) il demo ha **incassato 72,54 USDT di funding** e **pagato 8,42 USDT di commissioni**, su un guadagno totale di
  239,92 USDT (equity 5.232,79 da 4.992,87). Quindi, sul capitale iniziale: funding +1,45%, commissioni −0,17%, prezzo circa +3,5%
  (il resto, per differenza). In proporzione all'anno (13 giorni sono pochi): funding circa +41%, commissioni circa −4,7%. Il funding
  del giorno è salito da 0,02-0,07% a fine ottobre a 0,16-0,23% dal 30 ottobre. Le commissioni pesano più nei giorni dei ribilanci
  grandi (0,043% il 24 ottobre, il primo giorno). **Capito**: la parte del funding di G1 sul conto vero c'è (circa un terzo del guadagno
  di questi giorni), e le commissioni sono piccole. Il confronto con il funding atteso dal paper parte dal 6 novembre.
