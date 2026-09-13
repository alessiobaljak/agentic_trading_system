# «Il sistema è buono? Andremo mai live?»

Domanda del proprietario, 27 agosto. La risposta onesta è **non lo sappiamo ancora**,
e questo documento dice perché, cosa guardare, e **quando** avremo abbastanza per
decidere. Serve anche a una sessione futura che non ha vissuto questa conversazione.

## Cosa vuol dire lo 0,127%

Di **41.038** combinazioni (coin × strategia) provate in una passata, **52** superano
tutti i criteri del gate. Una su 800.

Da solo quel numero non dice se sia buono o cattivo. Diventa leggibile appena si
chiede: *quante di quelle 52 passerebbero per puro caso?*

| se bastasse | coppie fortunate attese |
|---|---|
| **1 conferma** | 7,4 al giorno — **52 a settimana** |
| **2 conferme** | 0,26 al giorno |
| **3 conferme** (regola attuale) | **0,0094 al giorno — una ogni 106 giorni** |

È la ragione d'essere della regola delle tre conferme distanziate, in una riga: con
una sola, il registro si riempirebbe di rumore alla stessa velocità con cui oggi non
si riempie di niente. Il tasso attuale è **dieci volte sotto** il massimo che il
budget di falsi positivi consentirebbe (1,306%). Quindi:

> Lo 0,127% **non** è un problema di severità del gate. Non stiamo validando fortuna,
> e non stiamo nemmeno stringendo troppo.

## Cosa dice l'evidenza contro

* Le **8 strategie scritte a mano** (breakout, momentum, trend_following, …) fanno
  **0 passaggi su 1.136** valutazioni, e lo fanno da settimane. Non è rumore
  statistico: quelle strategie, così come sono, non superano il gate.
* Il **73%** delle candidate muore su `total_return`: sono profittevoli, ma di troppo
  poco per valere il rischio. Non è che perdono — è che non guadagnano abbastanza.
* Quando il paper ha operato davvero (prima del reset di agosto) ha **perso**: equity
  da $1.000 a $831 in cinque giorni.
* **Zero coppie validate**, mai, da quando il registro esiste nella forma attuale.

## Cosa dice che non possiamo ancora concludere

* **Tutto ciò che è stato misurato prima del 19 agosto è contaminato.** La cache della
  candela oraria serviva la 1h di *bitcoin* a quasi tutte le coin: regime di mercato e
  conferma dual-timeframe erano calcolati sul grafico sbagliato, in ogni finestra e in
  ogni holdout. Le vecchie bocciature e le vecchie promozioni non valgono come prova.
* **La contabilità delle conferme funziona davvero solo dal 21 agosto**, quando le tre
  copie divergenti della stessa regola sono state unificate su `judge_window`.
* Quindi l'esperimento pulito ha **sei giorni**. Non è abbastanza per dire niente.
* E la ricerca **sta migliorando in modo misurabile**: 23 → 52 candidate che passano
  per passata in sei giorni, a valutazioni costanti. È il ciclo delle mutazioni che
  lavora (i quasi-passaggi di oggi sono i semi di domani).

## Il punto di decisione, con una data

Il registro ha **42 coppie con la finestra aperta** — le uniche che stanno contando i
giorni verso la seconda conferma. Quelle finestre si sono aperte fra il 21 e il 26
agosto, quindi **chiudono fra il 28 agosto e il 2 settembre**.

È lì che arriva la prima prova vera, e la domanda è una sola:

> **Una coppia che ha passato il gate riesce a ripassarlo una settimana dopo?**

Perché è questa la domanda: un edge vero si ripete, la fortuna no. Le altre 95 coppie
a un passaggio *vengono valutate a ogni giro e non passano più* — se le 42 si
comportano come loro, la risposta è che non c'è edge da confermare.

**Criteri, scritti prima di vedere il risultato** (altrimenti diventano una scusa):

* **entro il 5 settembre almeno qualche coppia a 2 conferme** → il meccanismo
  funziona, si continua e si aspettano le validate;
* **zero coppie a 2 conferme al 5 settembre** → non è un problema di soglie: i
  passaggi non si ripetono, cioè quello che il gate trova è rumore che passa una
  volta. A quel punto la mossa non è allentare il gate — è cambiare cosa si cerca
  (nuove famiglie di strategie, timeframe diverso, costi diversi) o accettare che a
  questa scala l'edge non ci sia.

## E comunque «validato» ≠ «live»

L'ordine non è negoziabile, ed è più lungo di quanto sembri:

1. il GATE 1 valida qualche coppia (siamo qui, non ancora);
2. il **paper** le opera per **mesi**, e si confronta il vissuto con la promessa
   (`scripts/gate_vs_paper.py`);
3. solo se il paper è in utile in modo stabile, e solo con una richiesta esplicita e
   ripetuta del proprietario, si discute di denaro vero.

`DRY_RUN` resta `true`. Non è un parametro di ricerca, e il fatto che il gate un
giorno dica sì non lo cambia: la promessa del backtest e il vissuto sono già stati
diversi una volta (BIRBUSDT, PF 1,51 nel gate e 0,16 nel paper), ed è esattamente il
motivo per cui il passo 2 esiste.

---

## Quando avrà senso «cercare cose diverse» (aggiunto il 6 settembre)

Domanda del proprietario. La risposta è: **non adesso**, e ci sono tre segnali
precisi che lo direbbero. Due non sono ancora arrivati, uno l'ho misurato oggi.

### Segnale 1 — il 13 settembre, se nessuna arriva a tre conferme

Otto coppie sono a 2/3. Le loro finestre chiudono il 13. Se **nessuna** ripassa,
vuol dire che quello che il gate trova si ripete **una volta e non due** — cioè non
è un vantaggio, è rumore con un po' di inerzia. A quel punto insistere con la stessa
ricerca è tempo speso a pescare nello stesso stagno vuoto.

### Segnale 2 — se validano ma il paper perde

È il fallimento **più informativo di tutti**, ed è già successo una volta: BIRBUSDT
prometteva PF 1,51 nel gate e ha fatto 0,16 nel paper. Se si ripete, il problema non
è *cosa* cerchiamo ma *come misuriamo*: il gate starebbe promuovendo cose che il
mercato vero non conferma, e nessuna quantità di ricerca aggiuntiva lo risolve.

### Segnale 3 — se la ricerca converge su poche idee

Il ciclo delle mutazioni cerca **vicino** a ciò che quasi funziona. È efficiente, ma
per costruzione si avvicina a un massimo locale: prima o poi produce solo varianti
della stessa idea, e continuare non aggiunge informazione.

**Misurato oggi: non sta succedendo.** Fra le coppie viste nei risultati ops ci sono
**78 spec distinte su 95 coppie**, sparse su 48 coin. La ricerca è ancora larga.

Un'osservazione che però va tenuta d'occhio: **quasi tutte le spec funzionano su UNA
sola coin.** Solo una (`gen_9a383fff`) compare su cinque. Un vantaggio vero di solito
generalizza — se resta vero che ogni strategia vive su una coin sola, è un indizio
che stiamo adattandoci alla storia di quella coin invece di trovare una regolarità
di mercato. Non è ancora una conclusione: il campione è piccolo.

### Cosa vorrebbe dire, in concreto

Non «altri parametri». Cambiare **la domanda**:

* **materia prima diversa** — oggi si guardano solo prezzo e volume. Funding rate,
  liquidazioni, book, dati on-chain sono segnali che nessuna delle nostre strategie
  vede;
* **orizzonte diverso** — siamo a 15 minuti con un limite di 24 ore per posizione. A
  4 ore o a un giorno il rapporto fra segnale e costi è un'altra cosa;
* **domanda diversa** — invece di «quale schema si ripete?», chiedere «**chi c'è
  dall'altra parte, e perché mi lascia quel soldo?**». Le strategie che sopravvivono
  a lungo hanno quasi sempre una risposta a questa domanda: qualcuno è costretto a
  vendere, o paga per un servizio. È la differenza fra avere un'ipotesi e cercare.

### La raccomandazione

**Aspettare il 13 settembre.** Mancano sei giorni ed è un test decisivo che costa
zero: sta già girando. Cambiare la ricerca adesso butterebbe via l'esperimento a metà
e ci lascerebbe senza la risposta alla domanda che aspettiamo da tre settimane.

---

## Il 13 settembre: cos'è successo davvero

**Zero coppie validate.** Il numero è quello di `ops/results/0035-verdetto-13set.md`,
letto alle 05:24 UTC. Ma il segnale 1, scritto il 6 settembre, non si può ancora
dichiarare né passato né fallito — e la ragione è un difetto trovato oggi, non una
scusa costruita dopo.

### Cosa dicono i numeri di oggi

| | 6 set | 8 set | 11 set | 12 set | **13 set** |
|---|---|---|---|---|---|
| coppie a 1 conferma | — | 167 | 204 (70 coin) | 220 (73 coin) | **243 (80 coin)** |
| coppie a 2 conferme | 8 | 58 | 81 (32 coin) | 84 (35 coin) | **90 (37 coin)** |
| validate | 0 | 0 | 0 | 0 | **0** |

Il fronte cresce ancora, su più monete. Le seconde conferme arrivano: quello che il
gate trova si ripete almeno una volta. Il terzo passaggio no, e finora nemmeno una
coppia lo ha raggiunto.

### Perché la data non ha ancora deciso niente

Le otto coppie ORCAUSDT a 2/3 avevano la finestra in scadenza oggi alle 00:00: da
quel momento un loro passaggio varrebbe la terza conferma. Nel run delle 05:11
ORCAUSDT ha avuto **14 coppie passate** — ma nessuna delle otto. Restano a 2/3, con
la finestra ancora aperta.

Questo, da solo, sarebbe una risposta legittima (non hanno ripassato). Il punto è che
non si poteva sapere se fossero state nemmeno *guardate*:

> la discovery ri-valuta al massimo `--reeval-cap` spec già note per run (500 in
> produzione). Restavano dentro **le più vecchie**, e l'unica protezione dal taglio
> era per le spec **già validate** — che sono zero. Quindi una coppia a 2/3 stava
> dentro o fuori a seconda di quando era stata scoperta.

E restare fuori non vuol dire aspettare il giro dopo. Nella discovery `judge_window`
è chiamato **solo sulle coppie che passano**: una spec non ri-valutata non passa,
quindi non prende né la conferma né il fallimento. Non matura — si ferma, mentre il
calendario continua a stamparle accanto una data di validazione.

È la terza volta che un tetto messo per limitare i **tempi** finisce per sacrificare
l'unica cosa che il sistema produce (le altre due: il tetto sulle coppie del registro
il 31 agosto, e la quota morta per le generate senza conferme).

### Cosa è cambiato oggi

* `specs_da_rivalutare` ordina **prima le conferme, poi l'anzianità**, e le spec con
  almeno un passaggio non vengono tagliate mai — a costo di sforare il cap.
* Il run scrive quanto il taglio morde (`n_specs_note`, `n_specs_rivalutate`,
  `n_specs_tagliate`), e `gate_progress` lo stampa. Senza quei numeri, «il registro
  non accumula» e «metà del registro non viene più guardata» sono indistinguibili da
  fuori — ed è esattamente com'è andata finora.
* Sei test in `tests/test_reeval_priority.py` tengono chiuso il criterio.

### La nuova data, e cosa la renderebbe onesta

Il segnale 1 si giudica **quando le otto coppie a 2/3 sono state ri-valutate almeno
una volta con la finestra scaduta**, cioè dal primo run dopo che questa correzione
è in produzione. Se dopo due o tre giri nessuna delle 90 coppie a due conferme
arriva a tre, allora il segnale è arrivato per davvero, e la conclusione del 6
settembre vale: quello che il gate trova si ripete una volta e non due.
