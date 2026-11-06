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

7. **Da dove viene il guadagno di prezzo** (aggiunta del 6 novembre, dopo le voci 1-4: l'esecuzione è a posto, quindi resta da capire
   la strategia stessa): nei 13 giorni del demo circa due terzi del guadagno vengono dal prezzo. Quanto dal lato comprato e quanto dal
   venduto, e per fascia di moneta (1-10, 11-50, 51-100): dal paper (pesi del giorno e prezzi), senza prove nuove sul passato.
   *Prima lettura il 6 novembre: i due lati e le tre fasce contribuiscono tutti; il lato venduto è quello che nel 2026 perde (diario).*
8. **G1 con poco capitale** (aggiunta del 6 novembre): con meno di circa 10.000 USDT molti ordini sono sotto il minimo di Binance (con
   1.000 USDT il 76%, revisione di G1N). Se il proprietario vorrà partire con una cifra piccola, serve sapere quanto perde G1 tenendo
   solo le monete con il peso più grande: è una prova sul passato, nel conto delle prove, con le regole scritte prima; si fa solo
   quando il proprietario dice con che cifra vuole partire. *Fatta il 6 novembre, prova 148: G1 regge con 280 USDT così com'è (diario).*

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
* **6 novembre 2026, 00:30 UTC, voce 4**: la ricerca sul passato non ha mai avuto 龙虾USDT (l'archivio usato per G1 non ha simboli con
  caratteri non latini: nel pannello di `seconda.pannello()` nessun simbolo non ASCII), mentre il bot la mette in G1 perché la legge dal
  listino vivo; sul demo è rifiutata ogni giorno («Invalid symbol»). Quindi il paper del bot e la ricerca differiscono di questa moneta,
  e il demo ne è privo. Il rapporto di stato ora scrive il peso che il paper G1 le dà (`scripts/state_snapshot.py`, un test); prima
  lettura alla prossima richiesta «stato». Confronto con il passato: le spese di G1 con gli ordini limite erano il 6,5% l'anno
  (`RISULTATI_PRIMA.md`, spread compreso), le commissioni vere del demo in proporzione all'anno circa il 4,7% (solo commissioni).
* **6 novembre 2026, 00:27 UTC, voce 4, lettura** (`ops/results/0704-6nov-stato-peso-moneta-rifiutata.md`): 龙虾USDT pesa **−1,41%**
  nel paper G1 (venduta); il demo ne è privo. È poco (meno di un cinquantesimo dell'esposizione di 2): **si lascia così**, il confronto
  fra demo e paper la porta dentro la sua oscillazione; con i soldi veri il conto vero la può scambiare. Nella decisione del 6 novembre
  il demo segnala anche **ICPUSDT** come moneta che sul demo non c'è: il rapporto ora scrive il peso anche delle monete mancanti, non
  solo di quelle rifiutate. Il primo dato del funding del paper (6 novembre, dopo il regolamento delle 00:00): +0,016% dell'equity,
  spese +0,007%; il confronto giorno per giorno con il demo parte da qui.
* **6 novembre 2026, 04:30 UTC, voce 3, confronto sui totali** (`ops/results/0704-6nov-stato-peso-moneta-rifiutata.md`, sezioni del
  paper): il paper G1 dal 23 ottobre ha incassato **155,21 USDT di funding su 10.000 (1,55%)** e pagato **16,34 USDT di spese (0,16%)**; il
  demo dal 24 ottobre **72,54 su 4.992,87 (1,45%)** e **8,42 di commissioni (0,17%)**. Il paper ha un giorno in più (il 23 ottobre).
  **Funding e spese del demo combaciano con quelli del paper**: la voce 3 è chiusa per ora; il confronto giorno per giorno resta nel
  rapporto di stato. Con le voci 1-4 la conclusione è che **G1 sul conto vero fa quello che il paper calcola**: niente da correggere
  nell'esecuzione.
* **6 novembre 2026, voce 6, prima lettura**: nel paper dal 23 ottobre **G1 +4,14%, G11 +6,81%** (G11 decide con il funding più fresco);
  G1N +7,08% dal 25 ottobre. G11 è avanti di 2,7 punti in 14 giorni, ma G1 e G11 tengono quasi le stesse monete e 14 giorni sono pochi:
  non si conclude niente; si guarda ogni settimana. Sul passato il vantaggio di G11 stava nel 2021 (revisione di G11).
* **6 novembre 2026, 06:10 UTC, voce 8** (il proprietario: «voglio partire con 250 euro»; prova 148, regole in `OTTANTASEIESIMA.md`
  spinte prima del calcolo, risultati in `RISULTATI_OTTANTASEIESIMA.md`): 250 euro sono 280 USDT (cambio 1,1209). Con i minimi veri di
  Binance di oggi (5 USDT per quasi tutti i perpetui, 20 per ETH, BCH, LTC, ETC e LINK, 50 per il Bitcoin con il passo di 0,001), sul
  passato 2021-2026 a capitale fisso: **G1 come lo esegue il bot oggi fa Sharpe 1,90 contro 1,98 senza minimi**, +57,8% l'anno contro
  +54,5%, discesa −26,8% contro −28,7%, ogni anno positivo; fa 6,6 ordini al giorno invece di 55,7, perché il minimo fa da banda.
  Permettere le chiusure sotto il minimo peggiora (1,83: le posizioni scendono e non risalgono); 10 monete per lato peggiora (1,72,
  discesa −39,5%). **Il bot non va toccato.** Il limite: sotto i 220 USDT circa G1 rende chiaramente meno (200 USDT 1,66, 150 USDT 1,49),
  e una discesa come la peggiore del passato porterebbe 280 USDT a circa 205. Prossimo passo, se il proprietario dice di sì: il demo
  con un capitale di 280 USDT, per vedere gli ordini veri a quella cifra prima dei soldi veri.
* **6 novembre 2026, 07:00 UTC, voce 8, il demo da 280 USDT** (il proprietario: «spegni eventi»; prima aveva chiesto se il bot si
  adatta al valore del conto: sì, a ogni ribilancio le posizioni si calcolano sul valore del conto letto in quel momento): il demo
  lavora come un conto di 280 USDT (`ops/demo_binance_capitale`; `bot/portafoglio/demo_binance.py`, `conto_ridotto`): il valore usato
  per le posizioni, lo stop a −35% e i rapporti è 280 più il guadagno da quando è partito; i filtri degli ordini severi almeno come
  quelli del conto vero (`filtri_conto_vero.json`: il Bitcoin con il passo di 0,001 e il minimo di 50, BCH, LTC, ETC e LINK con 20);
  la fase a 5.000 passa in `/demo_binance/fasi/` su RTDB; eventi spenti sul demo (il paper degli eventi resta). Tre test nuovi.
  Si misura da qui: la differenza giornaliera con il paper G1 (a 10.000, senza minimi) attesa intorno allo 0,7% (prova 148).

* **6 novembre 2026, voce 6, la domanda del proprietario** («perchè non G1N che è quella che sta facendo meglio o G11?»): nel paper,
  dal 23 ottobre, G1 +6,22% e G11 +8,22%; G1N +9,31% dal 25 ottobre (`ops/results/0707-6nov-stato-demo-280.md`). Sul passato (2021 – 4 ottobre
  2026, `revisione_g1n/nucleo.py`, ricalcolo di oggi): G1 Sharpe 1,98, G1N 1,93; nelle 2.087 finestre di 14 giorni **G1N è avanti di 3
  punti o più nel 5,8% dei casi e indietro di 3 o più nel 7,3%**, e la differenza di due settimane oscilla di 2,4 punti. Per anno, G1 contro
  G1N: 2021 +110,3% e +124,4%, 2022 +31,4% e +17,5%, 2023 +8,2% e +11,6%, 2024 +69,5% e +67,9%, 2025 +67,6% e +54,1%, 2026 +26,8% e +22,4%.
  G11: il vantaggio sul passato sta nel 2021 (`REVISIONE_G11.md`). **Capito**: tre punti in due settimane sono il rumore normale fra
  versioni così simili; il paper delle tre continua e i numeri vanno al proprietario ogni lunedì.
* **6 novembre 2026, 09:00 UTC, voce 7, prima lettura** (`g1_guadagno_prezzo.py`, numeri in `risultati_g1_guadagno_prezzo.json`; i pesi
  di G1 di `revisione_g1n/nucleo.py`, il rendimento da un'apertura all'altra). **Sul passato** (4 gennaio 2021 – 4 ottobre 2026) il
  guadagno di prezzo di G1 è **+32,9% l'anno** (il resto del netto di +54,5% è funding meno spese). Rispetto alla media dell'universo
  del giorno: le comprate fanno **+14,2% l'anno** meglio della media, le vendute **18,7%** peggio (cioè guadagno per chi vende): 43% e
  57%. Per fascia (posto per volume nell'universo del lunedì), rispetto alla media: monete 1-10 +7,3%, 11-50 +14,5%, 51-100 +11,1%.
  In media il lato venduto ha il 54% del peso nelle monete 51-100 (il comprato il 43%): G1 è venduta di circa l'11% del capitale sulle
  monete piccole, e lo è di più nei giorni in cui il mercato poi scende (la parte «di mercato» della fascia 51-100 vale +17,1% l'anno).
  **Anno per anno** (comprate sopra la media; vendute sotto la media): 2021 +28,4 e +56,3; 2022 +8,3 e +2,1; 2023 −15,8 e +12,1; 2024
  +26,1 e +35,0; 2025 +24,9 e +17,7; **2026 +13,1 e −20,2** (fino al 4 ottobre: le vendute fanno meglio della media, il prezzo totale
  −7,1%, e G1 guadagna solo con il funding). **Nei giorni del paper** (24 ottobre – 4 novembre, ricostruiti con la ricerca: combaciano con
  il paper nella maggior parte dei giorni ma non il 30 ottobre, 1,31% contro 3,41%): prezzo +1,3%, comprate +3,7% sopra la media,
  vendute −2,4% (come nel 2026). **Capito**: i due lati e le tre fasce lavorano tutti, e si danno il cambio negli anni (2023 il comprato
  perde, 2026 il venduto); togliere un lato o una fascia non ha un perché. Il punto debole di adesso è il lato venduto del 2026: da
  guardare in avanti, senza una prova nuova.
* **6 novembre 2026, il buco del 28 ottobre** (trovato con la voce 7): nell'archivio pubblico di Binance il 28 ottobre 2026 manca per
  tutte le monete (il file del giorno risponde 404; il file mensile di ottobre del Bitcoin ha 30 righe). Il pannello della ricerca aveva
  quel giorno vuoto. Riempito dall'interfaccia pubblica di Binance per le candele giornaliere (`research/programma6/buchi_archivio.py`,
  878 monete, `buchi_archivio.json`) e per quelle da 1 minuto delle 100 monete del programma 5
  (`research/programma5/strumenti/buchi_archivio_minuti.py`); l'archivio vince sempre dove c'è (due test). Il bot non ne risente (legge i
  prezzi in diretta). Il conto a tavolino del programma 6 è cambiato nella settimana dal 26 ottobre (per esempio M1 da −2,40% a −0,35%,
  M6 da +1,84% a +3,53%, F3 da +0,33% a −0,43%); la prova in avanti del programma 5 è stata rifatta.

* **6 novembre 2026, 12:30 UTC, voce 8, il demo da 280 dopo cinque ore** (`ops/results/0708-6nov-stato-demo-280-dopo-5-ore.md`; le copie
  di `docs/state.md` delle 07:48 e delle 08:46): 28 long e 25 short, margine unico, scarto fra posizioni vere e volute **14,3% del conto**
  (la prova 148 si aspettava circa il 14%: il 93% dell'esposizione di 2); il Bitcoin non si compra (G1 ne vuole il 7%, 20 USDT; il passo
  vero è 0,001, circa 78 USDT), ICPUSDT manca sul demo (4,2%). Il valore è sceso da 278,17 (07:04) a **267,08** (alle 08:00 circa)
  **nell'ora del passaggio** da 5.000 a 280 (ordini alle 06:57, chiusi alle 07:57): il movimento e le spese delle posizioni vecchie,
  circa 10.000 USDT, sono finiti sul conto ridotto. Dopo il passaggio, dalle 08:00 a mezzogiorno, demo +0,34% e paper +0,19%. **La fase
  da 280 si misura dal valore delle 08:00 (267,08)**; il confronto giorno per giorno con il paper parte dal 7 novembre ed è pulito. Con i
  soldi veri non succede (il conto parte senza posizioni). Lo stop resta a 182 USDT (−32% da 267).
* **6 novembre 2026, 12:50 UTC, voce 7, il lato venduto nel 2026** (`g1_venduto_2026.py`, `risultati_g1_venduto_2026.json`; dal 1°
  gennaio al 4 ottobre 2026, somme non in proporzione all'anno): le vendute fanno **13,8% meglio della media** (perdita per G1), le comprate
  11,3% meglio della media (guadagno). La perdita sta in tre mesi: **giugno −9,9%, luglio −8,5%, agosto −10,4%**; settembre +15,3% ne
  riprende metà. È concentrata: le 12 vendute che costano di più fanno insieme **−50,6%** (HUSDT −7,6%, DEXEUSDT −5,2%, VVVUSDT, LITUSDT,
  BASUSDT −5,2% ciascuna, HYPEUSDT −4,3%, XMRUSDT −4,2%, ...), tutte le altre vendute insieme **+36,8%**. Sono monete con il funding alto
  (molti comprano a leva) che hanno continuato a salire. Il funding nel 2026 arriva soprattutto dal lato comprato (+27,9%) e meno dal
  venduto (+9,4%). **Capito**: il lato venduto funziona sulla maggior parte delle monete e perde su poche che salgono molto; un tetto per
  moneta era già stato provato e peggiorava (prova 61). Nessuna prova nuova: si guarda in avanti se le perdite del venduto restano
  concentrate su poche monete.
* **6 novembre 2026, 16:40 UTC, voce 8, la misura dei minimi sul demo**: a ogni ribilancio il demo scrive quante variazioni volute
  restano sotto la quantità o il valore minimo e quanto valgono (`bot/portafoglio/demo_binance.py`, `sotto_il_minimo`;
  `/demo_binance/ribilanciamenti/{giorno}/sotto_il_minimo`; nel rapporto di stato accanto all'ultima decisione). Solo lettura: gli ordini
  non cambiano. Un test, 2.509 test passano. La prova 148 si aspetta con 280 USDT circa 9 variazioni su 10 sotto il minimo e 6-7 ordini
  al giorno dopo il primo; prima lettura dopo il ribilancio del 7 novembre.
