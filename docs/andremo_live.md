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

**Zero coppie validate**, e stavolta il numero *conta come verdetto*: le otto coppie
a due conferme sono state ri-testate con la finestra scaduta e non hanno ripassato.
Fonti: `ops/results/0035-verdetto-13set.md` (registro, 05:24 UTC) e
`ops/results/0040-log-dopo-correzione.md` (log della discovery, giro delle 06:12).

### I numeri

| | 6 set | 8 set | 11 set | 12 set | **13 set** |
|---|---|---|---|---|---|
| coppie a 1 conferma | — | 167 | 204 (70 coin) | 220 (73 coin) | **243 (80 coin)** |
| coppie a 2 conferme | 8 | 58 | 81 (32 coin) | 84 (35 coin) | **90 (37 coin)** |
| validate | 0 | 0 | 0 | 0 | **0** |

Il fronte cresce ancora, su più monete: le seconde conferme arrivano, quindi quello
che il gate trova si ripete **almeno una volta**. La terza no, mai, da nessuna coppia.

### Il verdetto, e perché adesso è leggibile

Le otto coppie ORCAUSDT a 2/3 avevano la finestra in scadenza il 13 alle 00:00: da
quel momento un loro passaggio vale la terza conferma. Nel giro delle 05:11 ORCAUSDT
ha avuto **14 coppie passate** — nessuna delle otto. Restano a 2/3.

Prima di chiamarlo verdetto serviva escludere che non fossero state nemmeno
*guardate*, e il conto per saperlo non esisteva. Ora esiste, e dice:

> `[discover] 439 candidate (219 con conferme ri-validate + 110 altre, **0 tagliate
> su 329 note**)`

Le spec note sono **329**, il tetto della ri-valutazione è **500**: il taglio non
mordeva. Tutte e otto sono state ri-testate con la finestra scaduta, e non hanno
ripassato. **Il segnale 1 è arrivato per questa coorte, ed è quello negativo.**

### Il difetto trovato oggi, e quanto è costato: niente (per ora)

Il criterio del taglio era sbagliato — restavano dentro le spec **più vecchie**, e
l'unica protezione era per quelle **già validate**, che sono zero. Una coppia a 2/3
stava dentro o fuori a seconda di quando era stata scoperta, e restare fuori non è
aspettare il giro dopo: nella discovery `judge_window` è chiamato **solo sulle coppie
che passano**, quindi una spec non ri-valutata non prende né conferma né fallimento.
Si ferma, mentre il calendario continua a stamparle accanto una data.

Ma con 329 spec contro un tetto di 500 **non ha ancora tolto niente a nessuno**. Era
una trappola armata per quando le spec avrebbero superato le 500 — cioè fra poche
settimane al ritmo attuale — non un danno già fatto. Vale la pena scriverlo con
questa precisione: la tentazione di far coincidere «ho trovato un difetto» con «ecco
perché non funziona» è esattamente l'errore che ha già prodotto una correzione
pubblica in questo documento.

Resta però la terza volta che un tetto messo per limitare i **tempi** può sacrificare
l'unica cosa che il sistema produce (le altre due: il tetto sulle coppie del registro
il 31 agosto, e la quota morta per le generate senza conferme).

Cosa è cambiato:

* `specs_da_rivalutare` ordina **prima le conferme, poi l'anzianità**, e le spec con
  almeno un passaggio non si tagliano mai — a costo di sforare il cap.
* Ogni giro scrive quanto il taglio morde (`n_specs_note`, `n_specs_rivalutate`,
  `n_specs_tagliate`) e `gate_progress` lo stampa. È il conto che ha permesso di
  scrivere «non ha morso» invece di «forse ha morso».
* Sei test in `tests/test_reeval_priority.py` tengono chiuso il criterio.

### Cosa vuol dire, e cosa NON vuol dire

**Non** vuol dire che il 13 settembre era una scadenza secca. Per una coppia generata
non viene mai registrato un fallimento, quindi le otto restano a 2/3 con la finestra
scaduta e **ogni giorno, con un giorno di dati nuovi, hanno un'altra occasione**. La
prova si accumula: più giorni passano senza che ripassino, più pesa.

**Non** vuol dire nemmeno che il campione sia sufficiente. Otto coppie **su una sola
moneta** (ORCAUSDT) sono la prima coorte, non la popolazione: le altre 90 coppie a
due conferme, sparse su 37 monete, chiudono la finestra nei giorni seguenti — AXSUSDT
il 14, e via così. Concludere adesso su una moneta sola ripeterebbe l'errore
dell'11 settembre, quando avevo dedotto una concentrazione da un elenco troncato.

Vuol dire questo: **la prima prova disponibile è negativa**, e il verdetto pieno
arriva mano a mano che le altre finestre scadono. Se entro fine settimana nessuna
delle 90 arriva a tre pur essendo stata ri-testata, la conclusione del 6 settembre
vale — quello che il gate trova si ripete una volta e non due — e la mossa non è
allentare le soglie, è cambiare cosa si cerca.

---

## 14 settembre: la coorte ORCA si è fermata, e si è capito perché

**Ancora 0 validate.** Fonte: `ops/results/0041-gate-14set.md` e
`ops/results/0042-gate-top-14set.md`, letti alle 05:12 UTC.

| | 12 set | 13 set | **14 set** |
|---|---|---|---|
| coppie a 1 conferma | 220 (73 coin) | 243 (80 coin) | **277 (89 coin)** |
| coppie a 2 conferme | 84 (35 coin) | 90 (37 coin) | **104 (40 coin)** |
| validate | 0 | 0 | **0** |

### Le coppie testate con la finestra scaduta

Cinque coppie su tre monete diverse hanno avuto oggi il loro primo tentativo utile
(`vista 14 Sep 02:24`, finestra chiusa il 14 alle 00:00): `AXSUSDT|gen_b922252e`,
`EGLDUSDT|gen_36b0e335`, e tre su `STXUSDT`. **Nessuna ha ripassato.**

Sommate alle otto di ORCAUSDT del 13, fanno **13 coppie su 4 monete, un tentativo
utile ciascuna, zero terze conferme**. È poca evidenza, non un verdetto: ogni coppia
ha avuto UN solo test su dati nuovi, non cinque.

### Il difetto che il caso ORCA ha reso visibile

Le otto coppie ORCAUSDT hanno `vista 13 Sep 08:36`, mentre tutte le altre hanno
`vista 14 Sep 02:24`. **ORCAUSDT è uscita dall'universo.**

L'universo è il top-N per volume e ruota. Misurato sugli snapshot committati in
`docs/state.md`:

| universo di | coin | ancora dentro il 14 set |
|---|---|---|
| 8 set | 148 | 74% |
| 11 set | 145 | 80% |
| 12 set | 154 | 82% |
| 13 set (sera) | 162 | 96% |

Circa un quarto dell'universo cambia in sei giorni. Ma una coppia ha bisogno di
**almeno due settimane** con la sua coin dentro per arrivare a tre conferme.

E uscire **non è fallire**: nella discovery `judge_window` è chiamato solo sulle
coppie che passano, quindi una coppia che nessuno valuta non prende né conferma né
fallimento. Si ferma a metà strada, e il calendario continua a stamparle accanto una
data di validazione. Le otto di ORCAUSDT hanno avuto **un tentativo, uno solo**, il
giorno in cui la finestra scadeva — e poi il sistema ha smesso di guardarle.

Nel calendario esteso sono già ferme anche `HEIUSDT` (vista l'11), `PLUMEUSDT`
(vista il 12), `SPXUSDT` (vista il 13).

### La correzione

L'universo della discovery non è più solo il top-N: le coin che hanno **una coppia
già avviata** (almeno una conferma, e l'ultima non più vecchia di tre finestre)
vengono riaggiunte, fino a un tetto di 40, **ordinate per vicinanza al traguardo**.
La riaggiunta sta dopo il filtro di contesto: una coin che ha già prodotto conferme
ha già dimostrato di essere informativa.

Sette test in `tests/test_universe_rotation.py`. Suite intera: 730 verdi.

### Cosa NON è ancora dimostrato

Che sia questa la ragione per cui non valida nessuno. ORCAUSDT è **un** caso, per
quanto grosso (otto coppie in un colpo). Le altre 96 coppie a due conferme stanno su
39 monete che l'universo contiene ancora, e le loro finestre scadono nei prossimi
giorni: sono loro a dare la risposta vera, e adesso non potranno più sparire mentre
la aspettiamo.

---

## 14 settembre, ore 08:45: le prime coppie validate

**Sette.** Tutte su ORCAUSDT. Fonte: `ops/results/0054-fine-giro-0626.md`.

```
distribuzione pass: 0 pass: 1744 su 218 coin · 1 pass: 286 su 90 coin
                  · 2 pass: 105 su 41 coin · 3 pass: 7 su 1 coin
VALIDATE ora: 7 su 1 coin distinte
ready dichiarato dal registro: False
```

È la prima volta da quando il registro esiste nella forma attuale. Il segnale 1,
pre-registrato il 6 settembre, è risolto: **quello che il gate trova si ripete anche
la terza volta.** Non era rumore con inerzia.

### E sono proprio quelle che la correzione di stamattina ha salvato

ORCAUSDT era uscita dal top-200 per volume il 13 settembre. Senza la riaggiunta delle
coin in maturazione — scritta questa mattina — nessuno l'avrebbe più guardata, quelle
otto coppie sarebbero rimaste a 2/3 per sempre, e il **19 settembre** la potatura per
anzianità le avrebbe cancellate.

La sequenza, per data:

| | |
|---|---|
| 13 set, 08:36 | ultima valutazione: ORCAUSDT esce dall'universo |
| 14 set, ~05:30 | correzione: le coin con coppie in maturazione rientrano |
| 14 set, 06:26 | il giro riaggiunge 13 coin, fra cui ORCAUSDT |
| 14 set, 08:08 | 7 coppie su 8 ripassano il gate → terza conferma |
| 19 set | *(data in cui sarebbero state cancellate)* |

### Quanto vale, onestamente

**Sette coppie non sono sette prove.** Sono sette strategie sulla **stessa moneta**,
che hanno preso la terza conferma **lo stesso giorno, sugli stessi dati**. È un
evento solo. Se ORCAUSDT ha avuto una settimana favorevole, sette strategie diverse
la vedono tutte.

**E la moneta è uscita dal top-200 per volume.** Una strategia validata su una coin
in calo di liquidità è esattamente lo schema BIRBUSDT: PF 1,51 nel gate e 0,16 nel
paper. Il passo 2 — mesi di paper prima di parlare di denaro — esiste per questo.

**Il bot non parte.** Servono **10 coppie validate su almeno 5 monete diverse**:
`ready: False`. Sette coppie su una moneta sola non fanno partire niente, ed è
giusto così: cinque strategie sulla stessa moneta salgono e scendono insieme.

### Cosa guardare adesso

105 coppie sono a 2/3, su **41 monete**. Sei sono già idonee, 51 lo diventano domani.
La domanda non è più «il meccanismo funziona» — quella ha avuto risposta. È: **su
quante monete DIVERSE arriva la terza conferma?** Cinque monete valgono più di
cinquanta coppie su una.

La regola di stop del 21 settembre resta, ma cambia di significato: non è più «se non
valida niente si cambia approccio», è «se non valida su almeno cinque monete diverse,
quello che troviamo non generalizza».

---

## 15 settembre: undici coppie validate su QUATTRO monete

Fonte: `ops/results/0055-gate-15set.md`.

```
3 pass: 11 su 4 coin  ·  VALIDATE ora: 11 su 4 coin distinte
ready dichiarato dal registro: False
```

| moneta | coppie validate |
|---|---|
| ORCAUSDT | 8 |
| STXUSDT | 1 |
| HEIUSDT | 1 |
| EGLDUSDT | 1 |

### La domanda di ieri ha risposta

Ieri le validate erano 7, tutte su ORCAUSDT, e la domanda era: **è un fatto su quella
moneta o il sistema sa farlo anche altrove?** Tre monete nuove in ventiquattr'ore
dicono che sa farlo altrove. Non stiamo guardando una fortuna locale.

Vale la pena notare che ORCAUSDT e HEIUSDT sono due delle tredici monete che la
correzione del 14 ha rimesso nell'universo: erano uscite dal top-200 per volume e
nessuno le guardava più. Due delle quattro monete coperte oggi sarebbero state
cancellate il 19.

### Quanto manca perché il paper parta

Servono **10 coppie validate su almeno 5 monete distinte**. Le coppie ci sono (11);
le monete no (4). **Manca una moneta sola.**

E il fronte è pieno: **53 coppie a 2/3 su 24 monete diverse hanno già la finestra
scaduta**, cioè si validano al primo giro in cui ripassano il gate. Ieri erano 6 su 4
monete. Non è una questione di settimane.

### Cosa succede quando la quinta arriva

`REQUIRE_GATE1_READY` è `true`, quindi il bot è rimasto piatto finora. Quando il
registro dichiara `ready`, **il paper inizia a operare da solo**, senza che nessuno
prema niente. `DRY_RUN` resta `true`: nessun denaro vero, mai, e non cambia per il
fatto che il gate dica sì.

Ed è lì che comincia la prova che conta davvero: `scripts/gate_vs_paper.py` confronta
quello che il backtest ha promesso con quello che il paper realizza. Il precedente da
tenere a mente è BIRBUSDT — PF 1,51 promesso, 0,16 realizzato. Il gate è una
selezione su storia; il paper è l'unica cosa che assomiglia al vero.

---

## La sonda sui timeframe (15 settembre)

Domanda del proprietario: se certe monete non sono copribili a 15 minuti, forse
servono 1 ora o 5 minuti. Misura in `ops/results/0060-sonda-timeframe-3.md`: le
stesse 20 candidate su tre scale, su 6 monete scoperte e 3 di controllo già coperte.

| scala | gruppo | PF mediano | sopra il pareggio |
|---|---|---|---|
| **1h** | scoperte | **0,910** | **29%** |
| 1h | controllo | 0,949 | 37% |
| 15m | scoperte | 0,826 | 8% |
| 15m | controllo | 0,876 | 8% |
| 5m | scoperte | 0,694 | 2% |
| 5m | controllo | 0,779 | 3% |

### La risposta alla domanda posta: no

Il timeframe **per moneta** non è supportato da questi numeri. A 1 ora le strategie
vanno meglio (+0,084 di PF mediano sulle scoperte), ma vanno meglio **quasi
altrettanto sul controllo** (+0,073). Il guadagno non è specifico delle monete
scoperte: è un fatto sulla **scala**, non sulle monete.

Pagare il costo di portare il timeframe dentro ogni coppia — 28 punti del codice, e
il rischio che gate e vissuto divergano — per un vantaggio che non è specifico
sarebbe spendere molto per niente.

### La risposta alla domanda NON posta, che è più interessante

L'ordine è monotono e non è debole: **più lunga la scala, meglio vanno le
strategie**, su entrambi i gruppi.

* a 5 minuti solo il **2-3%** delle candidate batte il pareggio;
* a 15 minuti l'**8%**;
* a 1 ora il **29-37%**.

La spiegazione economica più semplice è i **costi**: a parità di movimento di
prezzo, più si accorcia l'orizzonte più trade servono, e ogni trade paga fee e
funding. A 15 minuti potremmo star girando a una scala dove i costi si mangiano il
vantaggio — per tutte le monete, non per alcune.

Se è così, la mossa non è un timeframe **per coppia**: è un timeframe **globale
diverso**. Che costa infinitamente meno (un parametro, nessuna divergenza possibile
fra gate e live) ed è esattamente il contrario di quello che la domanda iniziale
suggeriva.

### Perché NON si tocca niente adesso

1. **Cambiare il timeframe globale invalida tutto il registro.** Le 11 coppie
   validate e le 400+ con conferme sono state validate a 15 minuti. A un'altra scala
   non valgono più: si ricomincerebbe da zero, proprio mentre manca **una moneta**
   perché il paper parta.
2. **La sonda misura il PF, non il gate.** Il 73% delle candidate muore su
   `total_return`, non sul PF. A 1 ora ci sono meno trade, quindi il ritorno totale
   sul periodo potrebbe essere più basso anche con un PF migliore. «PF mediano più
   alto» non è «il gate validerebbe di più».
3. **La quota sopra il pareggio va letta con prudenza.** A 1 ora ci sono meno trade
   per candidata, quindi il PF è più rumoroso: una distribuzione più larga sposta più
   massa oltre 1 anche senza un vero vantaggio. Il PF *mediano* è il numero più
   solido dei due.
4. **È una sonda: 9 monete, 20 candidate.** Serve a decidere se vale la pena
   misurare sul serio, non a decidere.

### Cosa farne

Aspettare il paper. Sta per partire e darà l'unica cosa che non abbiamo mai avuto:
il confronto fra quello che il backtest promette e quello che il mercato restituisce.
Se il paper a 15 minuti perde per i costi, questa misura ne è la spiegazione già
pronta — e allora il test su 1 ora si fa in grande e con un motivo.

Buttare il registro adesso per inseguire +0,08 di PF mediano su nove monete
significherebbe scambiare una misura vera per un'ipotesi.

---

## 16 settembre: 31 validate su 16 monete — e una mia correzione sulla soglia

```
3 pass: 31 su 16 coin  ·  VALIDATE ora: 31 su 16 coin distinte
ready dichiarato dal registro: False (via —)
```

In due giorni: 0 → 11 su 4 monete → **31 su 16 monete**. Il meccanismo non solo
funziona, sta accelerando.

### La correzione

Il 15 settembre ho scritto qui e detto al proprietario che «servono 10 coppie
validate su almeno 5 monete distinte» e che «manca una moneta». **Era sbagliato.**

Quella e' la via `READY_MIN_PAIRS`, che in `bot/config` vale **0 di default** — cioe'
e' DISATTIVATA — e sulla macchina non e' impostata. Si vede dal registro stesso:
`ready_by` e' `—`, mentre se la via a conteggio fosse attiva con 31 validate sarebbe
gia' scattata.

La regola davvero in vigore e' l'altra:

```python
base_ok  = universe >= 10 and len(covered) >= 5      # minimi assoluti: soddisfatti
by_coverage = coverage >= READY_FRACTION            # 0.35 sulla macchina
by_count    = READY_MIN_PAIRS > 0 and ...           # spenta
ready = base_ok and (by_coverage or by_count)
```

Serve **il 35% dell'universo scansionato** con almeno una strategia validata: circa
**76 monete su 217**. Ne abbiamo 16, cioe' il 7,4%.

I minimi assoluti (≥10 monete nell'universo, ≥5 coperte) li abbiamo passati: sono
condizione necessaria, non sufficiente. Li avevo scambiati per la soglia.

### Cosa cambia, e cosa no

Non cambia niente di quello che il sistema sta facendo: continua a validare, e in
fretta. Cambia **quando** parte il paper: non «manca una moneta», ma «mancano ~60
monete», e al ritmo di ieri (+12 coperte in un giorno) sono all'incirca una
settimana.

### La scelta, che e' del proprietario

C'e' un interruttore, ed e' stato scritto in anticipo proprio per questo caso — il
commento nel codice dice: *«la copertura diventa irraggiungibile quando il gate e'
severo; READY_MIN_PAIRS e' la via alternativa»*. Impostare
`OPTIMIZER_READY_MIN_PAIRS=10` sulla macchina farebbe partire il paper subito.

**Raccomandazione: aspettare.** Non perche' 35% sia sacro, ma perche' la ragione per
cui quella via alternativa esiste — «con un gate cosi' severo non partiremmo mai» —
ha smesso di essere vera **ieri**. Abbassare l'asticella nel momento esatto in cui
diventa raggiungibile e' la definizione di spostare il traguardo dopo aver visto il
risultato, ed e' l'errore che questo documento esiste per non fare.

Il costo dell'attesa va detto: la cosa piu' importante che non sappiamo — se il
vissuto confermi la promessa del backtest — resta ignota per un'altra settimana.
Se fra qualche giorno il ritmo delle validazioni si fermasse, allora accendere la via
a conteggio sarebbe una decisione presa sui dati e non contro di essi.

---

## 16 settembre, 16:00: il paper opera

```
GATE 1: ✅ SUPERATO — pronti per il paper trading
ready: True (via numero coppie)
deciso il 16 Sep 15:44 su 35 validate / 19 coin coperte / universo 156
  · minimi ok: True · copertura ok: False · conteggio ok: True
DRY_RUN: True
```

Il bot valuta **16 asset** invece di 100: opera solo le coppie validate, come deve.
Prima posizione aperta: **SPXUSDT long**, rischio 0,39% dell'equity, leva 2x.
Nessun trade chiuso ancora, quindi nessun verdetto: i numeri arrivano quando le
posizioni si chiudono.

### La contraddizione di stamattina, e cosa l'ha sciolta

Per due ore il registro ha mostrato 31 coppie validate su 16 monete, la via a
conteggio impostata a 10, e `ready: False`. Con quei numeri il conto dava sì.

Non era un difetto: era un **disallineamento di tempi** invisibile. `ready` lo
calcola la fase OPTIMIZE; la fase DISCOVERY, che gira dopo, riscrive `validated` e
`coins_covered` **senza ricalcolarlo**. Quindi i numeri che si leggevano nel
registro non erano quelli su cui la decisione era stata presa — e nessuno
conservava i secondi.

Ora `_ready_state` registra cosa ha usato, con l'ora. La riga sopra dice «deciso il
16 Sep 15:44 su 35 validate / 19 coin coperte», e la contraddizione si legge invece
di doverla indovinare. È la stessa lezione di ogni difetto trovato in questo
progetto: **un totale non dice mai su cosa è stato calcolato.**

### Da qui in avanti la domanda cambia di nuovo

Finora era «il gate produce qualcosa?». Adesso è: **quello che il gate promette, il
mercato lo conferma?**

La regola di lettura è fissata PRIMA di vedere i numeri, e vale:

> **Non si conclude niente sul gate finché non ci sono almeno 40 trade chiusi** — la
> stessa soglia che il sistema usa per dichiarare una deriva globale. Con meno,
> qualunque risultato è rumore, in bene come in male.

Il precedente da tenere in mente è BIRBUSDT: PF 1,51 promesso dal backtest, 0,16
realizzato dal paper. È per questo che il paper esiste.

`DRY_RUN` resta `true`. Non cambia perché il gate ha detto sì, e non cambierà senza
una richiesta esplicita, ripetuta e consapevole del proprietario.

---

## 17 settembre: i primi tre trade

Fonti: `ops/results/0073-paper-primo-giorno.md` e `0074-trade-chiusi.md`.

```
DRY_RUN: True · equity $997,66 (−0,23%) · GATE 1 pronto: True
3 trade chiusi · 1 vinto (33%) · PnL realizzato −2,34
2 su 3 usciti in stop loss
noi −0,23% vs BTC buy&hold +1,17% nello stesso periodo → sotto il mercato
```

### NON si conclude niente, ed è il punto

La regola fissata prima di vedere i numeri è **40 trade chiusi**. Ne abbiamo **3**.
Tre trade non distinguono una strategia che perde da una che vince avendo avuto una
brutta giornata, in nessuna delle due direzioni. Il momento in cui una regola del
genere conta è esattamente questo: quando il risultato è negativo e sarebbe comodo
leggerlo come un verdetto.

Al ritmo misurato — **1,5 trade al giorno** — servono circa **quattro settimane**.

### Una cosa da tenere d'occhio (non una conclusione)

I costi sono **0,97 USDT su 3 trade**, e il conto è questo:

```
lordo −1,38  →  costi 0,97  →  netto −2,34
break-even 0,10% dell'equity per trade
```

Le strategie hanno perso 1,38 sul mercato; i costi hanno **aggiunto il 70% di
quella perdita**. Con tre trade è un dato senza peso statistico, ma va nella stessa
direzione della sonda sui timeframe del 15 settembre: a 1 ora il PF mediano era
0,910 contro 0,826 a 15 minuti, e la spiegazione economica più semplice era proprio
che orizzonti più corti pagano più costi per lo stesso movimento.

Se fra qualche settimana i costi restassero questa frazione del risultato, le due
misure si sosterrebbero a vicenda e il caso per un timeframe globale più lungo
diventerebbe serio. Oggi sono due indizi, non una prova.

Attenzione a una cosa: i costi sono **stimati dal modello del gate, non misurati dai
fill**. Quindi non sono nemmeno una misura indipendente — è lo stesso modello che
ha prodotto la promessa a dire quanto costa mantenerla.

### Il resto è sano

Il bot valuta 19 asset (solo le coppie validate), tiene al massimo 2 posizioni
contemporanee contro un tetto di 10, e il rischio aperto resta sotto l'1%. Il numero
di trade è limitato dai **segnali**, non dalla liquidità né dal margine: il sistema
non sta forzando operazioni per riempire il portafoglio.

## 18 settembre: due domande del proprietario, e cosa hanno trovato

> «l'ho visto in positivo per quasi 10 ore e alla fine siamo andati in stop loss,
> com'è possibile?» — e — «in una giornata di rialzo abbiamo aperto 4 posizioni su
> 5 short, mi ricordo che vedere il trend era una prerogativa».

Il trade è VETUSDT / `gen_6d06dca0`, short, 06:00 → 16:12, uscito a **−3,24**.
Nessuna delle due cose è un bug. Entrambe sono comportamenti **voluti**, e nessuno
dei due era scritto da qualche parte che si rompesse se qualcuno lo cambiava.

### Perché un trade in profitto esce allo stop pieno

La protezione del profitto si arma quando il prezzo ha percorso metà della distanza
`entry → TP`. Sotto scale-out quel «TP» è **l'ultimo gradino della scala**, non il
primo. VETUSDT ha la scala 2/4/6, quindi:

```
primo incasso parziale ....... 2,0 R
protezione del profitto ...... 3,0 R   (metà di 6 R)
```

Sotto 3R lo stop resta quello di partenza e **tutto** il guadagno non realizzato
può tornare indietro. Non è un margine di sicurezza sottile: è una soglia alta.

Il dato che lo rende grave non è il singolo trade, è la distribuzione sui primi
sette chiusi (`docs/state.md`, 18 set 12:58 UTC):

```
mfe mediana 0,52 R  ·  ≥1R: 14%  ·  ≥3R: 0%
uscite: 6 stop loss pieni su 7 (86%, −17,47)
```

Zero trade oltre 3R significa che **la protezione del profitto non si è mai armata,
e con questi numeri non poteva**. Non è sfortuna su un trade: è una funzione che
finora non è mai entrata in gioco.

La deriva già lo segnala su ogni coppia, con la stessa forma: «mfe mediana 0,52R <
primo TP 1,50R». PF vissuto globale **0,221** contro **1,884** atteso.

**Ma il gate fa esattamente la stessa cosa** (`backtesting/engine.py:712` e
`bot/execution/executor.py:435` passano entrambi `final_target = ladder[-1][0]`).
Quindi il PF 1,63 di VETUSDT è stato misurato CON questa regola dentro: non c'è
divergenza gate↔paper, non è un altro BIRBUSDT. È una regola severa e onesta, che
sta semplicemente incontrando un mercato in cui il prezzo non arriva dove serve.

### Perché tante short in un rialzo

Tre meccanismi, tutti deliberati:

1. **Il regime è per-coin, non macro.** In `BACKTEST_PARITY` il regime si calcola
   sui dati di *quella* moneta (`orchestrator.py:82`). BTC che sale non rende VET
   rialzista; e sotto lo 0,4% di separazione fra le EMA il verdetto è «laterale».
2. **Le strategie generate sono attive in TUTTI i regimi** (`generated.py:216`),
   per costruzione: le valida il gate coppia per coppia, non il filtro di regime.
3. **Il trend modula la size, non mette il veto** (`decide_all`): controtrend apre
   al massimo dimezzato (`size_mult ≥ 0,5`), ma apre.

E soprattutto: metà delle feature generate sono di **ritorno alla media**
(`rsi_extreme`, `bb_touch`, `vwap_reversion`). Un mercato che sale è precisamente
quando l'RSI è alto e il prezzo è sulla banda superiore — cioè quando quelle
feature dicono *short*. Vendere la forza è ciò che quelle strategie **sono**.

Quindi «4 short su 5 in un rialzo» è il comportamento atteso di questo portafoglio,
non una contraddizione. La domanda utile non è *quante* short, è **se stiano
pagando** — e a quella nessun report sapeva rispondere.

### Cosa è cambiato nel codice

Solo strumentazione, niente logica di trading: cambiare le uscite adesso
renderebbe i primi 40 trade non confrontabili con quelli dopo.

* `scripts/trade_stats.py` (già in lista bianca come `trades`): nuovo blocco
  **DIREZIONE** — long vs short con PnL e mfe mediana, la matrice regime×direzione,
  e la riga CONTROTREND col suo PnL. Il criterio di controtrend è importato da
  `Orchestrator._trend_align` invece di essere riscritto: due definizioni che
  divergono sarebbero peggio di nessuna.
* `tests/test_direzione_e_protezione_profitto.py`: fissa che il lock è ancorato
  all'**ultimo** gradino (con la scala 2/4/6 a 1,9R lo stop è ancora quello base;
  con la 1/2/3 lo stesso movimento protegge), e che gate e paper usano lo stesso
  ancoraggio.

774 test passati (9 nuovi).

### Cosa NON ho cambiato, e perché

La soglia del profit-lock ancorata al gradino finale è la candidata ovvia: ancorarla
al **primo** TP la porterebbe da 3R a 1R su VETUSDT, dentro la portata di un mfe
mediano di 0,52R. Ma sarebbe una modifica alle uscite a metà esperimento, e andrebbe
fatta **nel gate prima che nel paper**, altrimenti si rompe la parità — cioè si
ricrea di mano propria il problema più caro di questo progetto.

Se ne riparla col verdetto dei 40 trade. Chiusi: 7 (8 col VET).

## 19 settembre: il registro era a tre giorni dal muro

Il report del gate lo diceva da giorni, in fondo a una riga: `spazio registro: 759
KiB su 879 (86%)`. Tradotto: il registro è **un solo documento Firestore**, il
limite è 1 MiB, e dentro ci sono i **passaggi accumulati** — settimane di attesa.

```
17 set 20:11 ....... 708 KiB  (81%)
19 set 05:28 ....... 759 KiB  (86%)     → ~37 KiB al giorno
margine rimasto .... 120 KiB            → circa TRE giorni
```

Oltre il limite Firestore rifiuta la scrittura. E fino a oggi quella scrittura era
una riga sola, `fb.set_doc(...)`, **senza rete**: il run sarebbe morto lì portandosi
via le conferme appena guadagnate, e da fuori il sintomo sarebbe stato solo un
numero che smette di salire. Esattamente il guasto che non si distingue dalla calma.

### Il difetto nella difesa che c'era già

`slim_registry` esisteva e faceva la cosa giusta — tolglie i campi descrittivi alle
coppie non validate — ma **solo oltre la soglia**. Sembra prudente ed è il
contrario: il documento arriva al muro alla velocità piena, e la rete si apre
nell'istante in cui si sta già cadendo. In tre settimane di vita **non era mai stata
eseguita una volta**.

E c'era un secondo buco: la discovery riscriveva il registro *dopo* optimize con
`encode_pairs` grezzo. Cioè l'ultimo a scrivere disfaceva il lavoro del primo.

### Cosa è cambiato

Quattro cose, nessuna delle quali tocca la logica di trading:

1. **Formato compatto** (`bot/core/firebase_client.py`): nomi di campo di una
   lettera (le chiavi JSON si ripetono 2.600 volte identiche), `symbol` e
   `strategy` tolti perché già dentro la chiave `COIN|strategia`, tempi arrotondati
   al secondo. La compressione vive in **un solo posto**: `decode_pairs` restituisce
   sempre i nomi lunghi, quindi nessun lettore cambia di una riga.
2. **Alleggerimento preventivo**: sempre, non solo quando sfora. Non è solo più
   piccolo — è più *lento a crescere*, perché ogni coppia nuova entra già leggera.
3. **Rete sulla scrittura**: se Firestore rifiuta, si riprova con la sola
   contabilità. Si perdono le metriche descrittive (le riscrive il giro dopo); **non
   si perde un solo passaggio**.
4. **Il report dice quanto manca in coppie**, non in percentuale. L'86% erano tre
   giorni e nessuno lo aveva calcolato.

### Misura

Col codice vero, su un registro sintetico che replica la composizione reale
(2.598 coppie, 47 validate):

```
prima ..... 368 byte/coppia
dopo ...... 138 byte/coppia        −63%
proiezione sul reale: 759 KiB → ~284 KiB = 32% del tetto
```

**MISURATO** dopo il primo giro dell'ottimizzatore col codice nuovo (registro
riscritto alle 06:34 UTC, report ops `gate` delle 11:38):

```
spazio registro ..... 272 KiB su 879   (31%)     [proiezione: ~284 KiB, 32%]
costo per coppia .... 108 byte                   [proiezione: 138]
coppie validate ..... 47 su 24 coin              [invariate: nessun passaggio perso]
distribuzione ....... 0 pass 1704 · 1 pass 397 · 2 pass 133 · 3 pass 47
ci stanno ancora .... ~5.773 coppie oltre le 2.593 di adesso
```

La proiezione era corretta e semmai pessimista. Il controllo che contava davvero non
era la dimensione ma la riga delle **validate**: 47 prima, 47 dopo, con la
distribuzione dei passaggi intatta. La migrazione di formato non ha perso niente —
era il rischio peggiore del cambio, e non si è avverato.

Il limite dei byte **ha smesso di essere il vincolo**: a 108 byte a coppia ce ne
starebbero oltre 8.000, e il tetto dichiarato sul numero di coppie è 3.000. Arriva
prima quello, che è un tetto voluto e visibile.

787 test passati (13 nuovi), `tsc` e `next build` puliti.

### Cosa NON ho fatto

La correzione strutturale sarebbe **spezzare il registro su più documenti**: è
l'unica che scala davvero. Non l'ho fatta perché tocca ogni lettore — bot, learning,
quattro script, due componenti della dashboard — e farla di fretta su un documento
che contiene settimane di attesa, mentre il paper sta girando, è il modo di
trasformare un problema di spazio in una perdita di dati. Con il vincolo spostato a
mesi c'è tempo per farla bene.

## 19 settembre: il paper apre i trade che deve? (e una sonda che misurava un'altra cosa)

Domanda del proprietario, nata guardando una scheda della dashboard: `gen_4465723e`,
+$12.821 su $10.000 nel backtest, e −$4 nel paper. «Come è possibile?»

### Perché quel numero è più piccolo di come appare

Tre cose, tutte verificate nel codice:

1. **Non sono tre settimane.** Il gate parte dal 2022 (minimo un anno di storia per
   moneta), divide in quattro blocchi e testa fuori campione su **tre quarti**. I
   215 trade sono sparsi su ~dieci mesi.
2. **Assume di puntare tutto il capitale su ogni trade.** `pnl = pnl_pct × capital`
   con `capital = 10.000` e `pnl_pct` = la variazione di prezzo
   (`backtesting/engine.py:788`). Il paper mette 200$ su 1.000$: cinque volte meno.
   Gli stessi 215 trade nel paper darebbero **~+25%**, non +128%. Che è comunque
   buono — quindi la size spiega perché il numero è gonfio, **non** la perdita.
3. **215 trade contro 1.** Win rate 46% vuol dire che quella strategia **perde il
   54% delle volte**. Guadagna perché le vincite sono più grandi, e serve tempo.

Con 12 trade e 2 vinti: se il sistema funzionasse come promette, la probabilità di
un risultato così brutto è **3,6%** (una volta su 28). Poco probabile — non abbastanza
per dire «è solo sfortuna, aspetta».

### La sonda misurava una scala diversa da quella su cui il bot opera

`frequenza` ha risposto **22 trade attesi in 7 giorni (~3,1/giorno)** contro i ~3 al
giorno del paper. Messi vicini: «tutto torna». Ed era falso: **contava su candele da
un'ora, il bot gira a quindici minuti.** Candele quattro volte più larghe danno molti
meno segnali, quindi gli "attesi" erano strutturalmente bassi e la coincidenza non
significava nulla.

Non un numero sbagliato: **un numero giusto per un'altra domanda**, messo accanto a
uno che risponde a questa. La stessa forma di difetto di BIRBUSDT.

Il dettaglio che lo rendeva invisibile: la voce in lista bianca non può passare
argomenti (regola voluta, `ops/README.md`), quindi il valore predefinito non era una
comodità — era **l'unica cosa che sarebbe mai stata eseguita**.

### I numeri veri

```
segnali grezzi (15m, 7 giorni) ..... 71   (~10,1/giorno)
di cui APRIBILI dal bot ............ 49   (~7,0/giorno)
paper, davvero aperti .............. ~3-4,5/giorno
```

Il secondo numero è quello confrontabile: il conto grezzo somma ogni strategia per
conto suo, ma il bot tiene **una posizione per moneta** (ORCA ha sei strategie
validate: i segnali sovrapposti non entrano).

### Conclusione, e cosa NON è stato dimostrato

Restano ~7/giorno attesi contro ~3-4,5 aperti. **Non è la prova di un difetto**, per
una ragione precisa: la sonda applica le **47 coppie validate di oggi** a tutti e
sette i giorni, mentre il bot ne aveva 35 il 17 e 43 il 18 — e il paper gira solo da
2,7 giorni dei 7 misurati. Il divario residuo sta dentro ciò che quel disallineamento
spiega.

Quindi: **nessuna prova che qualcosa sopprima i segnali.** Il paper va male per il
motivo semplice, non per un bug — pochi trade, e una strategia che perde più della
metà delle volte ha bisogno di numeri per mostrare il suo vantaggio.

La verifica pulita è ripetere la misura fra sette giorni, quando l'insieme delle
coppie sarà stato stabile per tutta la finestra. Se allora il divario resta, è un
difetto e va cacciato.

797 test passati (10 nuovi).

### 19 settembre, sera: la risposta vera — nessun divario

Il confronto settimanale (7,0 attesi al giorno contro ~3 aperti) era **sbilanciato per
costruzione**, e dire «va verificato fra una settimana» era una resa evitabile: il dato
per rispondere subito c'era già, bastava smettere di guardare la media.

Ora entrambi gli strumenti stampano la ripartizione giorno per giorno. Affiancate:

```
            attesi   aperti
16 set        4        1      (il paper è partito alle 16:00 → 8 ore su 24)
17 set        6        2
18 set        3        6      ← il paper ha aperto il DOPPIO degli attesi
19 set        —        3      (la sonda arriva al 18)

correggendo il 16 per le ore davvero girate:
  attesi 10,3  ·  aperti 9  →  87%
```

**Nessun divario sistematico.** Il "metà dei trade" era un artefatto della media: la
finestra di sette giorni includeva quattro giorni in cui il paper non girava ancora, e
applicava le 47 coppie validate di oggi a un registro che il 17 ne aveva 35.

E il 18 settembre chiude la questione in modo che nessuna media può: il paper ha aperto
**sei** trade contro tre attesi. Un sistema che sopprime i segnali non fa così, mai.

Quindi la risposta alla domanda del proprietario resta quella semplice, e ora è
sostenuta da una misura invece che da un'assenza di prove: **il paper esegue le
strategie che ha validato, con la frequenza giusta.** Va male perché ha fatto 12 trade,
e una strategia che perde il 54% delle volte ha bisogno di numeri per mostrare il suo
vantaggio.

Il campione è piccolo — tre giorni, conteggi a una cifra — e la verifica del 26
settembre resta in calendario come conferma. Ma non è più una domanda aperta.

801 test passati (4 nuovi).

## 19 settembre: il livello AI è progettato ma NON sta girando

Domanda del proprietario: «dove entra realmente in gioco l'AI? mi sembra che stiamo
lavorando nel trading alla vecchia maniera».

Aveva ragione, e la causa è banale: **la chiave API è rifiutata**.

```
Sep 13 06:12  [ai-hypotheses] non disponibile (AuthenticationError: 401
              'invalid x-api-key') -> proseguo senza AI
Sep 14 06:26  stessa riga
```

E la conferma indipendente, oggi: `scripts/shadow_report` dice **«nessuna decisione in
ombra registrata»**. La modalità ombra è accesa per default (`AI_SHADOW_ENABLED=true`)
e il bot decide dal 16 settembre: se la chiave funzionasse, ci sarebbero centinaia di
documenti in `ai_shadow`. Ce ne sono zero.

### Cosa è progettato e cosa gira

| pezzo | nel codice | gira |
|---|---|---|
| AI che propone strategie (20 su 40 candidate/giro) | sì | **no** |
| AI che filtra l'universo | sì | **no** |
| AI in ombra (decide accanto al bot, per misurarla) | sì | **no** |
| AI con potere di veto | sì, spento di proposito | no |
| sentiment (CoinGecko) come riduttore di size | sì | sì |
| Fear&Greed, funding, open interest, long/short | sì | sì |
| notizie, indici macro | **no** | no |
| apprendimento dai trade chiusi | sì | sì, ma «insufficient» |

### Da dove vengono allora le strategie `gen_*`

Da `generate_specs` (combinazioni casuali di mattoncini tecnici) e da `mutate`
(evoluzione attorno ai quasi-passaggi del giro precedente). È ricerca automatica —
casuale, selezione, mutazione — e funziona: le 47 coppie validate vengono da lì. Ma
**non è un modello che ragiona**, è un algoritmo genetico.

Il commento nel codice lo diceva già, e nessuno l'aveva letto come una diagnosi:
«Senza AI la quota resta casuale e il comportamento è identico a prima».

### Cosa cambierebbe rimettendo una chiave valida

Tornerebbero: le ipotesi motivate al posto di altrettante estrazioni casuali, il
filtro dell'universo, e soprattutto **la modalità ombra** — che è l'unica strada per
arrivare a dare all'LLM un ruolo operativo, perché è l'unica che produce numeri.

Cosa NON cambierebbe, ed è voluto: **l'LLM non decide i trade**. Una sua decisione non
è riproducibile, quindi non è backtestabile, quindi non potrebbe mai passare il GATE 1.
La scala progettata è ombra → veto → selezione, e ogni gradino si sblocca solo coi
numeri del precedente. Oggi siamo fermi prima del primo gradino perché il primo
gradino non ha mai potuto girare.

## 21 settembre: il giorno in cui abbiamo letto cosa fanno le strategie

Fino a oggi il gate misurava i **risultati** delle strategie generate; nessuno aveva
letto cosa **fanno**. Il proprietario ha mandato due grafici — MUBARAKUSDT a +37% in
trenta ore con RSI a 88, USELESSUSDT in salita verticale — e la domanda giusta:
*«siamo entrati short lì? siamo stupidi?»*. Stupidi no. Ciechi sì, in quattro punti,
tutti nel codice da luglio.

```
oggi: short 13 trade · 2 vinti · -30,11    long 11 trade · 3 vinti · -15,59
USELESSUSDT|gen_2031005e: mfe mediana 0,20R contro un primo gradino a 2,00R
rischio della posizione aperta: 0,91%  (il freno sul controtrend avrebbe dato ~0,5%)
```

**1. Il freno non frenava.** Il rilevatore di regime chiamava «incertezza» qualunque
cosa con ATR/prezzo sopra il 2,5%, prima ancora di guardare la direzione. Quindi più
una coin correva, meno era «in trend» — e per il freno «incertezza» vale zero. Ora la
direzione si legge prima. Le strategie generate operano in tutti i regimi, quindi i
loro backtest non cambiano: cambia l'etichetta, cioè ciò che il freno legge.

**2. Il tritacarne.** L'anti-whipsaw (un'ora di quarantena sulla coin dopo uno stop)
esisteva nel bot e veniva ignorato in parità, perché il gate non ce l'aveva: il gate
rientrava alla candela dopo, il bot al minuto dopo. Ora ce l'hanno entrambi, con la
stessa `COOLDOWN_HOURS` e una sola conversione ore→barre. Nel bot è per coin, quindi
blocca anche le strategie gemelle che si mettevano in fila.

**3. Le gemelle.** USELESSUSDT aveva tre coppie validate con PF 1,541 / 1,541 / 1,54;
ORCAUSDT otto. `spec_id` è un hash: due spec che differiscono solo per `rr` — inerte
sotto scale-out — erano «strategie diverse». Ora la discovery scarta le candidate con
la stessa **firma** (feature + soglie arrotondate, `rr` escluso). Quelle già validate
restano: si stampano a ogni giro, la decisione è del proprietario.

**4. Le parole che mancavano.** `rsi_extreme` e `bb_touch` dicono «vendi la forza» e
`min_adx` lascia passare il segnale solo con un trend forte: insieme fanno «vendi i
trend forti», per costruzione. Il vocabolario non aveva modo di dire «questa non è
un'oscillazione». Ora ha `not_stretched` (prezzo entro N ATR dalla media) e
`adx_below` (l'opposto di `min_adx`), più i tre mattoncini di mercato del mattino
(`market_trend`, `market_fade`, `relative_strength`). Sceglie il gate.

**Cosa NON è stato fatto, apposta:** azzerare il registro. Le 56 coppie tengono i
passaggi e vengono rigiudicate con le regole nuove alla prossima finestra di sette
giorni — la stessa migrazione a registro misto usata per la scala dei TP. Le gemelle
già dentro non sono state rimosse. `min_adx` sulle spec esistenti non è stato
toccato.

**La misura dei 40 trade** da qui in poi non è più confrontabile con i primi 24:
scelta del proprietario, motivata — *«non buttiamo via nulla, andiamo avanti, sono
tutte info che ci servono»*. I 24 restano nel registro dei trade con le regole con
cui sono nati.

### 21 settembre, sera: gli stop divisi per come sono morti, e A1

`mfe_report` (ora in lista bianca come `mfe`) sui 27 trade chiusi, 21 in stop:

```
sbagliati dall'inizio (mfe < 0,25R) ..........   7   33%   → ingresso
andati a favore, sotto il 1° gradino .........  13   62%   → uscita
oltre il 1° gradino, poi stop ................   1    5%
fra i «quasi»: mfe mediana 0,69R, massima 1,23R
R medi per trade con la scala piu' corta (1/1.5/2.5): -0,30 — nessuna scala da sola gira in positivo
```

Abbassare il take profit sposta la perdita, non la toglie. La leva per i 13 «quasi»
è la protezione del profitto: era ancorata all'**ultimo** gradino (si armava a 3R su
2/4/6), ora al **primo** (`lock_anchor`, 1R su 2/4/6, 0,75R su 1,5/3/5), nel motore e
nell'executor dalla stessa funzione. Quei trade escono vicino al pareggio invece che
a −1R. Deciso dal proprietario coi numeri sopra. Registro non azzerato.


### 21 settembre, sera: dashboard chiara, e il grafico che mostrava sempre BTC

Richiesta del proprietario: tema chiaro, via la tab Claude (non la usa più), il
grafico dell'Operatività che «mostra sempre BTC», e il grafico anche dei trade
chiusi al click.

* **Tema chiaro.** Token in `globals.css` riscritti (superfici bianche, ombre
  leggere, niente glow), e i colori scritti a mano in 19 componenti sostituiti coi
  token — il grafico a candele, che è un canvas e non legge il CSS, li prende dai
  token a runtime. `color-scheme: light`.
* **«Sempre BTC»** era un difetto vero: il default veniva scelto al primo render,
  quando posizioni e trade non erano ancora arrivati da Firebase, quindi cadeva su
  BTCUSDT e da lì non si muoveva più. Ora la scelta automatica segue la prima
  posizione aperta (o l'ultimo trade chiuso) finché l'utente non ne fa una sua.
* **Trade chiusi sul grafico.** Il click passa il trade intero, non il simbolo: il
  grafico sceglie il timeframe che lo mostra intero, centra la finestra sul trade e
  disegna entry/exit come linee e come marker sul tempo (IN/OUT), più SL e TP.
* **Tab Claude e rotta `/api/claude` rimosse.** Il canale con Claude resta quello
  delle issue di GitHub (`CLAUDE.md` aggiornato).


### 21 settembre, sera: copertura — via le base dal giro, più semi

Copertura ferma a 26 coin su 165 (`gate`, 18:55). Due leve sulla ricerca, nessuna sul
trading: le 8 strategie scritte a mano (0 validate su 1312 valutazioni) non vengono
più valutate (`OPTIMIZER_SKIP_BASE`, default acceso: il timer sulla VPS resta
uguale), e i semi di mutazione — che già danno precedenza alle coin non coperte —
passano da 10 a 30 (`DISCOVERY_SEEDS`). Metro: le 74 coin a 2/3 entro il 28 set.


### 21 settembre, notte: A2, B2bis, D3, tetto per coin, referto settimanale

* **A2** — il break-even dopo il primo gradino lo sceglie il gate per coppia: una
  passata in più sulla scala scelta (l'alternativa al default), non il doppio della
  ricerca. La scelta viaggia in `last_params` e il bot la legge già.
* **B2bis** — `rr` non è più richiesto né controllato: sotto scale-out non fa
  niente, e scartava proposte AI sensate.
* **D3** — modello AI `claude-opus-5` di default.
* **Tetto di perdita per coin al giorno** (`RISK_PER_COIN_DAY`, 1,5% dell'equity,
  `bot/risk/daily_cap.py`): persa quella frazione su una coin, la coin non si riapre
  fino a mezzanotte UTC. Regola di portafoglio, diverge dal gate nella direzione
  sicura. Le vincite non compensano: il tetto è sulle perdite, non sul netto.
* **Referto settimanale**: una routine ogni domenica alle 09:00 (ora italiana)
  raccoglie `trades`, `mfe`, `confronto`, `gate`, `ai-stato` e risponde alle
  domande fisse — il lock taglia vincitori? le gemelle rientrano? la copertura si
  muove? quanto dura il giro?


### 21 settembre, notte: B3, D2, E3

* **B3** — i quasi-passaggi vanno all'AI: schema, ipotesi, consigli; i consigli
  entrano nelle proposte dello stesso giro. Prima si contavano i morti, ora si
  chiede perché. L'AI suggerisce, il gate decide.
* **D2** — dati sintetici spenti per default; solo i test li accendono.
* **E3** — via i quattro workflow GitHub che non potevano avere dati veri (451).


### 22 settembre, sera: la conferma a 1 ora (`htf_confirm`)

Idea del proprietario: guardare la moneta con due occhi, 15 minuti per operare e
1 ora per confermare. Fatta come mattoncino direzionale, non come regola: il gate
misura coin per coin. Le strategie senza conferma continuano a operare; quelle con
conferma entrano solo se reggono il gate anche con meno segnali. Sul caso MUBARAK
(RSI 88 a 15 minuti, medie orarie in salita) lo short non nascerebbe. Misura di
riferimento: sui 35 trade del 22 set la conferma avrebbe tolto 11 trade (-31%), il
cui netto era +5,87 — ma con le etichette di regime vecchie; il gate decide.


### 22 settembre, notte: strategie native a 1 ora, per ora solo BTC (C1, seconda metà)

Chiesto dal proprietario: «facciamola solo su BTC, poi se funziona si allarga».
La spec porta il suo timeframe (e l'id lo include: una logica a 15m e a 1h sono due
strategie), il motore chiama la riga base col suo intervallo, `optimize` lancia a
ogni giro una discovery a 1h su BTCUSDT come sottoprocesso con un tempo massimo
(nessuna modifica alla unit sulla VPS), il bot fa decidere ogni strategia sul suo
orologio (una a 1h decide una volta l'ora), e i trade portano il timeframe della
strategia così il learning non li mescola. Le prime coppie BTC@1h servono le
solite 3 conferme. Allargare = cambiare `DISCOVERY_EXTRA`.


### 23 settembre: il controllo del setup prima, il referto dopo

MUBARAK long dopo un pump del +37%: stop a −15,3%, primo incasso a +31%, lock che si
armava a +15%. Ore in positivo al 3-6% (0,3R), poi stop pieno, −9,8. Il trailing non
poteva scattare: il metro (R = ATR gonfiato) era sbagliato, non il lock.

Da oggi, dalla stessa aritmetica (`bot/risk/setup_check.py`): PRIMA, uno stop più
largo di `MAX_STOP_PCT` (6% del prezzo) rende il setup non tradabile — il motore lo
salta, il risk manager lo rifiuta col motivo visibile nello stato delle decisioni;
DOPO, ogni trade chiuso riceve un referto scritto nel suo documento (classe della
morte, stop largo, lock mai armato, controtrend, verdetto), stampato e contato da
`trades`. Richiesta del proprietario: «queste analisi il sistema le deve fare prima,
e per ogni trade perso devono essere scritte e usate».


### 23 settembre, pomeriggio: il cervello, primo pezzo

Il proprietario, davanti a 40 trade chiusi con 6 giornate su 8 in perdita e −50,88
realizzato (dashboard, 23 set): «il sistema deve imparare da tutto quello che fa e
adattarsi tutti i giorni; questa schermata dimostra che non si sta adattando».

Ha ragione sul fatto: fino a oggi ciò che impara modulava solo size e uscite (pesi,
deriva, scala dei TP, keep del trailing), e con soglie alte (50 trade per i pesi, 20
per strategia per la deriva). Sugli ingressi, niente. Da oggi il ciclo è chiuso in
tre pezzi, tutti sotto la regola «il paper propone, il gate decide»:

1. **Referti aggregati** (`bot/learning/referti.py`, documento `learning/referti`,
   stampati da `trades`): i referti dei trade chiusi sommati per strategia, coin e
   direzione. Da regole scritte PRIMA scattano le ipotesi: tre short tutte perse →
   «solo long»; tre perdite controtrend o mai andate a favore → «con conferma a 1
   ora»; due stop larghi → «stop più stretto».
2. **Varianti nel gate** (B8, prima metà): ogni ipotesi diventa una variante della
   stessa strategia che entra nel gate al posto di una candidata casuale. Stesse 3
   conferme, stesso holdout, il giro non si allunga. Se passa, opera; se no, muore
   lì, e il paper non ha tarato niente.
3. **Freno di serie** (`STREAK_BRAKE_LOSSES=4`, `STREAK_BRAKE_FACTOR=0,5`): quattro
   perdite di fila su una strategia, su qualunque coin, dimezzano size e leva fino al
   primo guadagno. Frena, non spegne: il 4 è ragionato (con un win rate del 45%
   capita circa il 9% delle volte per sequenza), non misurato — e lo dice il commento.

Cosa NON è cambiato: nessuna soglia d'ingresso tarata sul paper, nessuna regola del
gate (le 3 conferme restano), `DRY_RUN` true. La proposta del gate a due livelli
(candidata a size ridotta / validata a size piena) è in backlog come F2 e aspetta il
sì del proprietario.

Il metro per giudicare: nei prossimi giri di `log-gate` le righe «varianti dai
referti del paper (B8)» e, tra due settimane, quante varianti hanno passato il gate
rispetto ai genitori; in `log-bot` le righe «FRENO x0.50 (serie N perdite)».


### 24 settembre: le tre conferme nello stesso giro, per le varianti

Domanda del proprietario: «se impari e vuoi rivalidare, perché non rivalidi
dall'inizio fino a oggi e, se passa, la riprovi? Sei sicuro che i sistemi
intelligenti aspettino davvero?». Risposta: no, non aspettano. Le tre conferme
distanziate di una settimana sono nate contro la lotteria delle migliaia di
candidate casuali; l'ingrediente non è il calendario ma i dati che finiscono in
momenti diversi (`scripts/backfill_passes.sh` lo diceva già a settembre). Una
variante dai referti è una modifica mirata a una spec nota: da oggi la discovery
la valuta con i dati fino a oggi, a 8 e a 16 giorni fa nello stesso giro. Tutte e
tre più l'holdout → validata subito e operata dal giro dopo; solo quella di oggi →
scartata subito. Le due date arretrate stanno prima del periodo in cui il paper ha
formulato l'ipotesi: sono la parte della prova che il paper non ha mai visto.
Costo: due valutazioni in più per variante passata, su al massimo 10 spec. Il
metro: in `log-gate` le righe «conferme retroattive n/2».


### 24 settembre, sera: il cervello prende forma (selettore passi 0-1, intorno)

Richiesta: «procedi con tutto come da tuo suggerimento». Tre pezzi, nessuno tocca
il bot.

* **Dataset del selettore (passo 0).** Ogni trade simulato dal gate porta ora le
  variabili all'ingresso (RSI, ADX, stocastico, volatilità, distanza dalla media,
  posizione nelle bande, volume, larghezza dello stop, primo gradino, ora, BTC
  sopra/sotto la media oraria). A ogni giro la discovery scrive i trade OOS delle
  coppie passate in `data/selettore/` sulla VPS e un riepilogo in
  `selector/dataset`. Primo numero da leggere: quante righe e quante famiglie con
  almeno 500.
* **Addestramento e confronto (passo 1).** `bot/learning/selettore.py`:
  regressione logistica (numpy/scipy, nessuna dipendenza nuova), walk-forward nel
  tempo con soglia scelta sul train, confronto «apri tutto» contro «selettore» per
  finestra. Il comando ops `selettore` stampa il verdetto per famiglia (va
  aggiunto alla lista bianca sulla VPS). Il bot NON lo usa: l'ombra è il passo 2.
* **L'intorno (punto 1).** Nel giro completo, fino a 10 coppie validate a notte
  vengono riprovate con ogni soglia spostata di un gradino, solo sulla loro coin.
  La figlia sostituisce la madre solo con le conferme retroattive e un margine del
  10% sul ritorno OOS; la madre resta nel registro ma non si opera più. Il metro:
  in `log-gate` le righe «intorno: N coppie … figlie» e «[intorno] … sostituisce».
  Il cronometro del giro completo dice se il tetto può salire a 40.


### 24 settembre, notte: rischio per direzione, statistica t, meno casuali, portafoglio

* **Tetto per direzione** (`MAX_RISK_PER_DIRECTION=3%`): con tre posizioni a
  size piena nella stessa direzione la quarta non si apre. Il motivo compare nello
  stato delle decisioni («tetto per direzione»). Riavvio del bot in coda (0174).
* **Statistica t** nel registro e in `gate`: misurata, non ancora regola.
* **Candidate casuali** a 40 per giro (erano 100): le fonti ragionate sono quattro.
* **Backtest di portafoglio** (`portafoglio`, chiave da aggiungere): le validate
  insieme con i limiti veri, con e senza tetto per direzione. È il numero che
  manca per tarare G1 e il massimo di posizioni.


### Controllo del 24 settembre (08:20)

Fonti: ops 0175-0183 (06:02-06:13 UTC), stato delle 08:13.

* **Guasto**: il modello AI sulla VPS è `claude-opus-4.8`, id inesistente
  (`ai-stato`: «model: claude-opus-4.8 was not found. Did you mean
  claude-opus-4-8?»). Dalle 23:12 di ieri proposte, autopsia e filtro universo
  saltano (fail-open: il giro prosegue senza AI). Da correggere nel `.env`.
* Trade 44 in 9 giorni · netto −49,15 (lordo −37,85, costi 11,30 = 1,19% dell'equity)
  · equity 950,85 · DRY_RUN True · long 18 (6 vinti, −16,28) · short 26 (10 vinti,
  −32,87) · deriva globale PF 0,60 contro 1,89.
* Validate 59 su 27 coin (universo 200) · 213 coppie a 2/3, 75 con finestra
  scaduta su 40 coin (ieri 72).
* Giro «solo urgenti» delle 05:11: **1h54**, sopra la soglia di 1h30 (atteso ~1h):
  da rimisurare al giro delle 09:00. Passata a 1 ora: 1 minuto, 445 valutazioni,
  **prima coppia a 1h passata: ADAUSDT**.
* Cervello: referti 5 (3 in perdita); freno di serie attivo su gen_ba3a671f e
  gen_fa304106 (5 perdite di fila): lo short DEXEUSDT delle 02:16 è partito a leva
  1x invece di 2x e ha perso 1,50. Due ipotesi → due varianti nel giro delle 08:03
  (gen_54d1beed «solo short» da gen_ba3a671f, gen_9998083f «solo long» da
  gen_fa304106): esito delle conferme retroattive al prossimo giro. Dataset del
  selettore: 165 righe (ADA a 1h). Chiave `selettore` non ancora in lista (0183
  rifiutata). L'intorno gira per la prima volta stanotte.
* Stop per classe (`mfe`, 28 su 44): 8 ingresso / 19 uscita / 1 protezione (ieri
  7/13/1 su 21). Frequenza: 23 set attesi 9, aperti 5.
* Tetto per direzione attivo dal riavvio delle 08:12 (0174).

Proposta del giorno: correggere il modello AI, aggiungere le chiavi `selettore` e
`portafoglio`, e lanciare `portafoglio` per tarare il tetto per direzione e il
massimo di posizioni sui numeri, non a occhio.


### Portafoglio del 24 settembre (08:36, ops 0184)

59 coppie validate insieme sugli ultimi 60 giorni, con i limiti del bot (5
posizioni, una per coin, tetto per coin, cooldown, 1% per trade): 526 trade aperti
su 771 candidati, 8,6 al giorno, 2,5 posizioni contemporanee in media (max 5), il
51% delle altre aperte nella stessa direzione, 39 giorni in utile e 22 in perdita,
drawdown 16%. **Il PnL (+104% in 60 giorni) NON è una previsione**: le coppie sono
state scelte perché hanno passato il gate proprio su questo periodo (l'holdout è
negli ultimi 45 giorni), quindi il livello è gonfiato dalla selezione. Valgono la
forma e il confronto: il paper apre 4,9 trade al giorno contro 8,6 simulati, un
divario da capire (frequenza: attesi 9, aperti 5 il 23). Tetto per direzione al 3%:
ferma 23 trade su 526 (11 short, 12 long), PnL e drawdown invariati, posizioni
nella stessa direzione da 5 a 4: quasi neutro, non stringe né protegge molto.

`selettore` (0185): 165 righe da una sola coppia (ADA a 1 ora), campione
insufficiente come atteso; le righe delle 59 coppie a 15m arrivano col giro delle
08:00. `ai-stato` (0186): chiave ok, modello `claude-opus-4-8`; le proposte AI
risultano ferme al 22 set 20:14, da verificare in `log-gate` («[ai-hypotheses]»).


### 24 settembre, sera: l'audit del cervello

Domanda del proprietario: «hai fatto un check di tutto il codice appena creato,
coerenza con quello che esisteva, quasi un audit completo rispetto ai sistemi
seri e all'obiettivo del profitto?». No, non completo: fatto adesso, con quattro
revisori indipendenti (integrazione, correttezza, regole, disegno) sulle 4.400
righe dei due giorni. Nessun bloccante, ma parecchio da correggere, e due errori
miei da dire chiaramente:

* **il tetto per direzione esisteva già dall'8 settembre** (`MAX_DIRECTIONAL_RISK_PCT`,
  stesso 3%): ne avevo scritta una seconda copia. Tolta.
* **il freno di serie scatta per caso**: con 17 strategie e ~9 trade al mese
  l'una, quattro perdite di fila capitano al 30-44% delle strategie ogni mese; e
  sommato alla deriva globale portava la size a un quarto. Spento, finché
  `portafoglio` non misura sui trade del gate se dopo 4 perdite si vince davvero
  meno.

Corretto lo stesso giorno: le bocciature chiudono la finestra (causa del giro
«solo urgenti» da 1h54: 223 spec restavano urgenti per sempre), le varianti senza
conferme retroattive muoiono davvero, una sola figlia per madre, confronto
figlia/madre nello stesso giro su ritorno − drawdown e per finestra, la variante
dai referti si valida solo su dati precedenti all'ipotesi e sostituisce la madre,
`portfolio/backtest` si pubblica, il selettore vede anche i quasi-passaggi e dà
«batte» solo oltre il 95° percentile di 200 permutazioni, dedup delle gemelle,
interazione direzione × mercato. Da decidere (backlog H): t ≥ 3 nel gate, holdout
non condiviso, stop giornaliero di portafoglio, e la misura che separa mercato da
esecuzione (4,9 trade al giorno nel paper contro 8,6 simulati).


### Portafoglio dopo l'audit, 24 settembre (09:20, ops 0188)

Quattro colonne cumulative sulle 59 validate, ultimi 60 giorni (PnL gonfiato dalla
selezione: vale la forma): senza limiti 526 trade, +10.386, drawdown 16,3%, 39/22
giorni; tetto direzione 3% (regola del bot) −64 trade, +9.664, dd 17,0%; + stop
giornaliero 3% −44 trade, 9 giorni fermati, +7.638, dd 14,9%, giorno peggiore da
−832 a −187; + netto 2R −80 trade, PnL uguale, dd 16,2%. Win rate dopo 4 perdite di
fila: 33% su **6 casi** (incondizionato 63,7%, t −1,55): campione inesistente, il
freno di serie resta spento. Diversification ratio 0,17: le coppie si compensano
molto, non sono una scommessa sola. `portfolio/backtest` ora si pubblica.


### 24 settembre, 14:50: due giri del gate uccisi dalla memoria, colpa mia

I giri delle 11:00 e delle 14:06 sono stati uccisi dal sistema per memoria
esaurita (OOM, `log-gate` 0195, 14:11). Causa: dall'audit il dataset del
selettore raccoglieva anche le righe dei quasi-passaggi, e con 264 coin per 314
spec quelle righe venivano portate tutte in memoria nel processo principale.
Correzione: i worker scrivono le righe su un file per processo e restituiscono
solo i conteggi; le righe dei quasi-passaggi entrano solo nel giro completo delle
02:00 e al massimo per 2 spec per coin; i file più vecchi di 14 giorni si
cancellano. Il registro non è stato toccato (le validate restano 59); il prossimo
giro parte col timer delle 17:04. Da verificare: che finisca, e in quanto tempo.

**15:50, la causa vera dell'OOM:** anche il giro delle 17:04 è morto (15:12 UTC).
Misurato in locale su una serie da 165k candele a 15 minuti: valutare una
variante dai referti su dati troncati in mezzo alle altre spec fa ricostruire la
cache degli snapshot del motore e porta il picco di memoria del worker da 0,9 a
1,5 GB; per 8 worker sono 12 GB su 15. Correzione: le varianti troncate si
valutano per ultime per ogni coin, con la cache svuotata prima e dopo (picco
misurato 0,97 GB). Il prossimo giro parte col timer delle 20:04.


### 24 settembre, 21:30: le due misure

* **A5 (ops 0210):** il livello strutturale delle 24 ore sta in mediana a 3,96R,
  raggiunto nel 2% dei trade contro l'11% del primo gradino. Ipotesi smentita in
  questa forma: i bersagli non sono messi male, è il prezzo che non va lontano.
* **H5 (ops 0211):** dal 16 set, segnali del gate aperti dal paper 15 (PF 0,50),
  non aperti 9 (PF 1,23, 6 short). Indizio, non prova: campione di 9.
* **Gate lanciato a mano alle 21:11:** 6 worker, 9 GB usati su 15 dopo 11 minuti,
  vivo. Fine attesa verso le 23:00.

**23:26, il giro lanciato a mano è finito bene:** 2h07 (21:13 → 23:20) con 6 worker,
70.560 valutazioni, 135 coppie passate, 380 coppie a 2 conferme su 3 (erano 213) e
nessuna con finestra scaduta (le bocciature la chiudono davvero); statistica t
misurata su 5 validate (1 regge t ≥ 2, mediana 1,47). Dataset del selettore: 9.740
righe da 135 coppie. Memoria di picco per worker: 2,28 GB (per questo 8 worker
morivano: 8 × 2,3 > 15). Il timer delle 23:04 è saltato perché il giro era in
corso; il prossimo è il giro completo delle 02:04, con l'intorno per la prima volta.


### 25 settembre, 07:05: il giro completo notturno e il salto delle validate

* **Giro completo delle 02:04** (primo con l'intorno: 10 madri, 53 figlie): finito;
  il giro «solo urgenti» delle 05:30 è durato **1h09** con **8 spec urgenti su 529**
  (erano 223): la correzione dell'audit ha svuotato la coda. Memoria di picco per
  worker 2,29 GB, 6 worker, nessun OOM. Dataset del selettore: +1.558 righe.
* **Validate 59 → 160 su 52 coin (copertura 26%)**, quasi tutto nella sera del 24.
  Causa: la stessa correzione. Una coppia che passa dentro la sua finestra di 7
  giorni guadagna la conferma alla chiusura della finestra; prima la chiusura
  avveniva solo se la coppia ripassava DOPO la scadenza, quindi decine di conferme
  già guadagnate restavano sospese (i 75 «a 2/3 con finestra scaduta» del 24
  mattina). Ora si registrano, come optimize faceva da sempre per le base. Non è
  un abbassamento del gate: 3 passaggi in 3 finestre diverse, come prima. Le scale
  delle nuove validate sono le fisse (2/4/6 e 1,5/3/5), non quella dal vissuto.
* Conseguenza da guardare: il bot opera 160 coppie invece di 59 → più segnali al
  giorno, con gli stessi limiti (5 posizioni, una per coin, tetto per coin, tetto
  per direzione). Il controllo delle 08:00 misura il salto.
* Statistica t: 9 validate con misura, 3 reggono t ≥ 2, mediana 1,47.
* 1 ora: un'unica candidata (ADAUSDT, prima conferma il 24), nessuna validata.


### 25 settembre, 07:30: check end-to-end del learning (otto revisori) e i trade con 160 coppie

Domanda del proprietario: «con 160 coppie i limiti reggono? il salto a 52 coin è un
errore? il learning impara dai trailing? c'è qualcosa che ci perdiamo?». Risposte:

* **Limiti**: non si sfonda il conto (margine e 3% per direzione sono invalicabili),
  ma il cap di 5 posizioni è spento in parità (il paper ha già toccato 7). Oggi
  fino alle 07:13: 3 aperture, 4 posizioni aperte, rischio 1,48% (ops 0227-0228);
  attesi ~19-24 segnali apribili al giorno con 160 coppie (ops 0229) contro 11 il
  24. `portafoglio` sulle 160 in coda.
* **Salto 59→160**: legittimo, otto revisori su otto; 116 coppie a 3 passaggi e 44
  a 4 (ops 0224). Nessuna via nel codice alza le conferme senza un passaggio vero.
* **Trailing**: i verdetti si scrivono, il keep per strategia non è mai scattato
  (servono 8 verdetti, ci sono 14 uscite trailing su 21 strategie); i referti
  «sotto TP1» e «lock mai armato» sono contati ma non generano ipotesi.
* **Corretto subito**: etichetta «FRENO attivo» falsa in `trades`, contatore
  dell'ombra AI («0/60» era una chiave sbagliata), calibrazione con confidenza
  costante ora dice «costante», rifiuti d'ingresso nel log (righe «[rifiuto]»:
  finalmente contabili, H5), freno globale scritto in `stato`, esito di intorno e
  varianti salvato a ogni giro e letto da `gate`, `last_pf` conservato
  dall'alleggerimento. Sezione I del backlog con le sei cose da decidere.


### 25 settembre, 08:10: il portafoglio sulle 160 coppie, e la risposta a H5

Ops 0232, 60 giorni, 160 coppie: 974 trade (16 al giorno, contro 8,6 con 59
coppie), massimo 5 posizioni contemporanee (limite della simulazione), drawdown
14,8%, 34 giorni in utile e 27 in perdita, PnL gonfiato dalla selezione. **Dal 16
settembre anche il portafoglio simulato perde: −1.516 su 10.000, 8 giorni su 10 in
perdita, contro −46,65 del paper.** È il mercato di queste due settimane, non
l'esecuzione: il paper ha perso un terzo di quello che avrebbe perso il simulato,
grazie alla size dimezzata dal freno e ai tetti. Dopo 4 perdite di fila il win
rate è 56% su 16 casi (t −0,58): il freno di serie resta spento. Bot riavviato
alle 07:57 con le righe «[rifiuto]» nel log; chiave ops `rifiuti` da aggiungere.

### 25 settembre, 08:30: i verdetti del trailing arrivano al cervello — il keep lo sceglie il gate

Il proprietario: «il learning impara dal trailing ok, ma fai in modo che venga
usato e consumato e venga presa una decisione; ogni dato raccolto deve arrivare
al cervello, altrimenti raccogliamo dati a fare». Aveva ragione: il keep del
lock (quanta parte del miglior guadagno si blocca) si adattava per strategia
solo dopo 8 verdetti, e in 10 giorni ne sono usciti 14 su 21 strategie — non
sarebbe mai scattato. E se fosse scattato, il gate avrebbe continuato a simulare
0,5: paper e gate divergenti, il caso BIRBUSDT in un altro vestito.

Da oggi il keep è un **parametro per coppia scelto dal gate**, come la scala dei
TP e il break-even: `evaluate_spec` prova 0,35 / 0,5 / 0,65 sulla scala già
scelta (3 backtest in più per ogni spec che passa, nessuno per le bocciate), il
vincitore va in `last_params.profit_lock_keep`, e motore e bot lo leggono con la
stessa funzione (`lock_keep`). Il paper entra come per la scala dei TP:
`keep_dal_paper` somma i verdetti di tutte le coppie e con almeno 8 propone un
quarto candidato (0,25 se ≥ 60% prematuri, 0,75 se ≥ 60% protetti): **il paper
propone, la storia decide.** La scelta fra scale, break-even e keep pesa i trade
recenti (emivita 180 giorni, G6): prima sette giorni nuovi su 4,6 anni valevano
lo 0,42% dell'evidenza e la scelta non si spostava mai. I criteri per PASSARE
restano non pesati: il tasso di passaggio non cambia per costruzione.

Le coppie non ancora rigiudicate continuano col keep con cui sono state validate
(chiave assente = comportamento di prima); ognuna riceve il suo alla chiusura
della sua finestra. Si vede in `gate` (riga «keep del lock») e nel log del giro
(`[paper] N verdetti trailing…`, `[cervello] keep…`). Bot riavviato per leggere
la chiave. Suite completa: 1249 test verdi (1214 prima, 35 nuovi). Il trade chiuso registra ora anche quale keep lo ha governato, così un verdetto «prematuro» si legge col suo numero. Non verificato: un giro reale della discovery col nuovo parametro (il primo giro utile lo dirà nel log: riga `[paper] N verdetti trailing…` e `[cervello] keep…`).

### Controllo del 25 settembre (08:10 ora italiana, ops 0234-0239 più 0227-0232 delle 07:10-07:53)

**Numeri.** 55 trade chiusi in 10 giorni (2 oggi alle 08:10), 4 aperte (HEI e
PROM long, TUT e XPL short, rischio aperto 1,48%), realizzato −46,65, equity
953,35, DRY_RUN True, costi stimati 12,64 su 54 trade (lordo −34,01), massimo 7
posizioni insieme (ops 0234, 0227); giornate del paper: 4 in utile e 6 in perdita
su 10 dal 16 set, e il 24 e il 25 in utile di poco (+1,17 e +0,92, ops 0232). Uscite:
31 stop (−128,57), 14 trailing (+29,97), 6 scale-out (+17,69), 2 TP pieni, 1 time
exit (ops 0227). Direzione: long 24 trade, 9 vinti, −17,93; short 31, 14 vinti,
−32,19 (ops 0234): E1 resta aperta. Il freno globale è attivo (PF vissuto 0,64
contro 1,89). Gate: 160 validate su 52 coin, copertura 26%, 403 coppie a 2/3
(5 con finestra già scaduta), statistica t misurata su 9 validate: 3 reggerebbero
t ≥ 2, mediana 1,47 (ops 0235): troppo poche misure per decidere H1. **Giro
completo notturno 1h09** (03:30-04:40 UTC), «solo urgenti» 8 spec su 529, passata
a 1 ora 440 valutazioni e 0 passate (ops 0235). Nessun Traceback né OOM nei log
(ops 0236, 0239). Bot riavviato alle 07:58: da allora nessun rifiuto d'ingresso
nel log e ultimo esito «flat» (ops 0239, 0234); la chiave `rifiuti` NON è ancora
nella lista bianca della VPS (ops 0238: rifiutata). Frequenza: 24 apribili al
giorno negli ultimi 7 giorni su 52 coin, contro 5,5 aperti al giorno di media
(ops 0229, 0234): il collo resta il bot, non i segnali (una posizione per coin,
tetti, freno). AI: chiave ok, 20/20 proposte accettate alle 05:31 italiane, ombra
0/60 d'accordo (ops 0230, letto prima dell'aggiornamento del contatore: si
ricontrolla domani). Selettore: NON BATTE, 1 finestra su 3 batte con p 0,035, le
altre due no (ops 0231). Portafoglio: dal 16 set il simulato perde −1.516 contro
−46,65 del paper (è il mercato), dopo 4 perdite WR 56% su 16, diversification
ratio 0,11 (ops 0232). Stop: 20 su 32 andati a favore ma sotto il primo gradino
(mfe mediana 0,67R), livello strutturale a 4,04R raggiunto nel 2% dei trade (ops
0237): A5 resta confutata.

**Proposta del giorno: alzare il tetto dell'intorno da 10 a 40 coppie a notte
(B8 seconda metà, `DISCOVERY_INTORNO_CAP`).** Perché: era la condizione scritta
nel disegno («si attiva solo con il giro completo sotto 1h30»), e il giro
completo di stanotte ha fatto 1h09 con il tetto a 10 e 6 worker (ops 0235); con
160 validate a 10 coppie a notte ogni coppia rivede le sue soglie ogni 16 notti,
a 40 ogni 4, cioè entro il riposo di 7 giorni previsto. Cosa cambia: ~30 coppie
in più a notte, ~8 figlie l'una, quindi ~240 valutazioni in più su ~90.000 e le
conferme retroattive per le figlie che passano; una figlia entra solo se passa il
gate, batte la madre del 10% su 2 finestre su 3 e passa l'holdout. Cosa NON
cambia: il paper, le soglie del gate, il vocabolario. Metro: il tempo del giro
completo (deve restare sotto 1h30; se sfora le 2h si torna a 10) e la riga
«intorno: madri/figlie/promosse» in `gate` per due settimane. **Serve il sì.**

### 25 settembre, 08:40: sì all'intorno a 40, chiave `rifiuti` aggiunta

Il proprietario ha detto sì alla proposta del giorno: il tetto dell'intorno
passa da 10 a 40 coppie a notte (`DISCOVERY_INTORNO_CAP`, default nel codice).
Metro: il giro completo (1h09 il 25 set con tetto 10, ops 0235) deve restare
sotto 1h30; se sfora le 2h si torna a 10. Vale dal prossimo giro completo
(03:30 UTC). La chiave `rifiuti` è ora nella lista bianca della VPS; la lista
bianca va messa in ordine: `ops/allowlist.example` ha le stesse 45 chiavi della
macchina (confronto con la risposta ops 0238), raggruppate per sezione, e
aggiunge `lista` (sola lettura della lista stessa) per poter confrontare le due.

### 25 settembre, 10:40: il controllo orario e la dashboard nuova

Il proprietario: «hai tutte le capacità per fare check di status, learning,
paper, gate, strategie in automatico? fai in modo che le evidenze mi arrivino in
dashboard ogni ora; la dashboard deve evolvere in un sistema serio: togli il
rumore, aggiungi quello che dà una situazione chiara». Sì, con una scelta: il
controllo orario lo calcola **il bot** sulla VPS (GitHub Actions ha buchi
misurati di 3-7 ore: lo snapshot resta solo come ripiego), da ciò che è già su
Firebase, e lo scrive in `dashboard/controllo` (schema in
`docs/controllo_schema.md`): due semafori («è rotto?» e «perde?»), 27 anomalie
con codice e soglia, una frase di lettura per sezione da regole (niente AI), e
per il learning la foto di ciò che decide ORA più «cosa è cambiato nelle ultime
24 ore». La discovery scrive `dashboard/gate` a ogni giro: stato in corso /
finito / errore, composizione delle candidate, il cervello (intorno dell'ultimo
giro completo, varianti, keep scelto nel giro e nelle validate), e le strategie
operate per coppia con PF promesso contro vissuto. Per averli sono stati aggiunti
i dati che mancavano: battito nel dict di `/bot_status` (spariva per un attimo a
ogni ora), avvio e riavvii, errori del ciclo, chiusura BTC oraria (benchmark a
costo zero), equity iniziale e data d'inizio del paper, data d'ingresso del freno
globale, contatori dei rifiuti d'ingresso per motivo in `/decision_status`.

La dashboard passa da 6+1 tab a 4+1: Controllo (prima pagina: semafori,
«aggiornato N minuti fa» rosso oltre 2 ore, quattro tessere, lettura, anomalie,
poi paper / learning / gate chiusi), Operatività, Gate (con la tabella per
coppia), Learning (attivo contro misurato), Impostazioni. Tolti 16 pannelli che
facevano rumore o leggevano dati che nessuno scrive più (sentiment, punteggio
asset, insight, heatmap, trailing adattivo, costi per coin, snapshot giornaliero,
modale posizione, evoluzione learning, strategie per strategia, ombra AI e
rischio di portafoglio come pannelli a sé). Verificato: 1407 test Python verdi
(erano 1249), TypeScript pulito, build Next ok, e un test di parità che confronta
campo per campo lo schema, ciò che scrive Python e ciò che legge TypeScript. Non
verificato dal vivo: né Firebase né un browser da qui (backlog J4). Il primo
controllo arriva al riavvio del bot; il primo documento del gate al prossimo
giro. Cosa resta su richiesta via ops: portafoglio simulato, selettore, righe
`[rifiuto]` per coppia.

### 25 settembre, 13:45: il controllo si era fermato dopo il primo giro

Screenshot del proprietario: «sistema ok (vecchio)» e «controllo fermo: l'ultimo
è di 2 h 43 fa» col bot vivo. Causa: il ramo orario del loop usava l'orologio
dei pesi, che il ricalcolo dopo ogni chiusura azzera; con una chiusura all'ora
(69 trade a 30 giorni, ops 0248) il ramo non partiva mai, e con lui il
controllo. Ora il ramo orario ha un orologio suo (`last_orario`). Il learning
non si era fermato: nel log i pesi e i referti si ricalcolano a ogni chiusura
(11:07, 11:13, 11:38 UTC). Riavvio ops 0247, primo controllo alle 11:42 UTC.
Trovato anche il rischio effettivo perso al riavvio (ops 0245, commit 04147c7).

### 25 settembre, 14:15: imparare di più da ogni chiusura — scala per strategia, ipotesi «uscita», selettore in ombra

Il proprietario: «non voglio limitare la quantità, voglio trade migliori;
impara il più possibile da ogni chiusura; in paper puoi rischiare di più per
validare ipotesi». Tre cose:
1. **Scala di TP per strategia dal vissuto**: ogni strategia con ≥ 5 trade in
   paper propone al gate la propria scala (quantili del suo mfe), e il gate la
   prova sulle sue coppie accanto alle fisse e a quella globale del paper.
2. **Quinta ipotesi «scala_stretta»** (I4): 3 perdite «andate a favore ma sotto
   il primo gradino» sulla stessa strategia → ipotesi nel referto e le sue spec
   rigiudicate al giro successivo (cap 10 strategie); nel doc del gate
   `giro.ipotesi_uscita`. Limite noto: la freschezza usa la data del primo trade
   (backlog I4bis).
3. **Selettore in ombra** (passo 2 del disegno): `selettore_report` pubblica il
   modello in `selector/current`; il bot lo carica ogni ora e a ogni apertura
   scrive p e soglia sul trade e nel log, senza decidere. `trades` stampa
   «SELETTORE IN OMBRA». Si accende solo con il verdetto «batte» e la
   calibrazione sul paper non piatta.
H3 parcheggiata (va contro «non limitare»). Proposto il «paper esplorativo»
(F1bis), aspetta il sì. Suite: 1451 test verdi (1409 prima), TypeScript ok.
Non verificato dal vivo: il primo `[selettore]` nel log arriva dopo il prossimo
report `selettore` e il riavvio del bot.

### 25 settembre, 14:50: il paper esplorativo è acceso (F1bis, sì del proprietario)

Le coppie che passano il gate per un pelo (quasi-passaggi, mancato più piccolo,
una per coin, al massimo 20, mai le validate né le strategie base) finiscono in
`strategy_registry/esplorative` a ogni giro della discovery, con una storia
(validata poi / scartata). Il bot le opera in paper a **un quarto della size**,
al massimo 3 aperte insieme, marcate `esplorativa`; una validata sulla stessa
coin vince sempre. Pesi, freno da deriva e calibrazione le ignorano; referti,
scala e keep dal vissuto le includono (più chiusure da cui imparare: è lo
scopo). I numeri del paper nel controllo restano quelli delle validate; la riga
«Paper esplorativo» sta a parte. Fuori dal paper (DRY_RUN false) è spento
comunque. Metro: dopo 100 trade esplorativi, quante coppie sono poi passate
contro quante scartate (`gate`, riga ESPLORATIVE; `trades`, sezione PAPER
ESPLORATIVO). Suite 1483 test verdi, TypeScript ok. Non verificato dal vivo: il
primo giro del gate scrive il documento; fino ad allora il bot non ha
esplorative e lo dice.

### 25 settembre, 22:10: la memoria completa di ogni trade chiuso

Domanda del proprietario: «per ogni trade chiuso il sistema memorizza TP e SL
configurati e le condizioni d'ingresso?». Quasi tutto sì (foto degli indicatori,
regime, referto, costi, mfe, keep, p del selettore), con due buchi: lo stop
salvato era quello FINALE spostato dal trailing, e la scala dei TP non c'era.
Ora ogni trade chiuso porta anche `orig_stop`, `scale_r_mults`,
`sl_to_breakeven`, `tp_prices` (i prezzi dei gradini), `feats_at_entry` (le 10
variabili d'ingresso del selettore) e `regola` (la regola della strategia in
chiaro). Sopravvivono al riavvio con la posizione. Nessun effetto sulle
decisioni. Suite 1485 test verdi.

### Controllo del 26 settembre (08:20 ora italiana, ops 0258-0270)

**Il guasto trovato, prima di tutto.** Il giro «completo» del gate (tutte le
spec, intorno, varianti) **non girava da giorni**: la regola lo faceva partire
solo se la discovery iniziava prima delle 03:00 UTC, ma il timer è a catena (3
ore dall'attivazione precedente) e la discovery partiva alle 03:30-03:48. Per
questo `gate` mostrava «intorno 0 madri» e le validate «non ancora rivalutate»
erano 167 su 182 (ops 0261). Il «giro completo di 1h09» del 25 era un giro
urgenti. Correzione: il giro è completo anche se l'ultimo completo è di più di 20
ore fa (`completa_at` in `discovered_last_run`); vale dal prossimo giro, verso le
11:00. Suite 1491 test verdi. Il tempo del primo completo con intorno a 40 lo si
misura domani.

**Numeri.** 84 trade in 11 giorni, 46% vinti, −63,73 USDT (−6,4%), equity
936,27, DRY_RUN True, 2 posizioni (0,30% a rischio), max 8 insieme, costi
stimati; giornate del paper: il 25 −13,90, il 26 −2,25 (ops 0258, 0259, 0267).
Uscite: 45 stop (−165,54), 29 trailing (+48,10), 7 scale-out, 2 TP, 1 time exit.
Direzione: long 30 trade −18,78; short 54 −44,95 (E1 aperta). Stop: 18 sbagliati
dall'inizio, 26 andati a favore sotto il primo gradino (mfe mediana 0,65R), 1
oltre (ops 0264). Controllo orario puntuale ogni ora nella notte (ops 0262);
semafori sistema giallo (registro 2859/3000, 6 riavvii miei) e paper giallo
(freno globale PF 0,61 vs 2,09; 115 validate su 182 senza promessa). Gate:
182 validate su 62 coin, copertura 31%, 421 a 2/3, statistica t su 18 (8
reggerebbero t ≥ 2, mediana 1,97); keep scelto su 15 coppie: 0,35 ×6, 0,5 ×1,
0,65 ×2, **0,75 ×6** (il candidato del paper: 24 verdetti, 15 protetti, ha
vinto 6 volte); scala dal vissuto 0,75/1,25/2 e scale per 4 strategie proposte
(ops 0261, 0263). Esplorative: 43 attive, 9 scartate, 0 trade chiusi.
Selettore in ombra: 12 trade, p vinti 0,70 vs persi 0,68 (ops 0258); verdetto
NON BATTE, modello ripubblicato su 54.912 righe (ops 0266). Rifiuti nel log:
18 «posizione già aperta», 17 cooldown, 3 confidenza sotto soglia, 0 per peso
(ops 0268): i pesi non stanno spegnendo niente (I1 non è un problema oggi).
AI: 20/20 proposte, ombra d'accordo 7/100 (ops 0260). Portafoglio: dopo 4
perdite WR 61% su 18; diversification ratio 0,11 (ops 0267). Frequenza: 30
trade il 25 (ops 0258).

**Proposta del giorno: nessuna voce nuova.** L'azione del giorno è la
correzione del giro completo, che rimette in moto intorno a 40, varianti e la
rivalutazione di tutte le 548 spec: prima di proporre altro serve vederlo girare
(tempo, madri/figlie, keep sulle 167 non rivalutate). H1 aspetta ancora numeri
(18 misure); il selettore non batte; C2 il 28.

### 26 settembre, 11:30: i dati che mancavano al learning, e le strategie a 1 ora

Domanda del proprietario: «come vanno le strategie a 1 ora, e c'è qualche dato
che non tracciamo?». Revisione di sola lettura (19 lacune trovate), poi cinque
misure chiuse subito, nessuna decisione cambiata:
1. **Ombra dei segnali rifiutati** (`bot/learning/rifiutati.py`, ops
   `rifiutati`): ogni segnale non aperto (cooldown, posizione già aperta, peso,
   tetti, veto) viene registrato con prezzo, stop, scala e motivo; 24-96 ore
   dopo si simula com'è andata con le regole del motore (senza costi). Regola:
   un freno si ritara solo se per un motivo i rifiutati hanno R medio maggiore
   degli aperti su almeno 30 casi. «Posizione già aperta» ora è una classe sua
   (era «altro», ed è il motivo più frequente: 18 su 39, ops 0268).
2. **Controfattuale dopo uno stop e MAE**: `post_stop_verdict` («rumore» se il
   prezzo tocca il primo gradino prima di andare un altro R contro,
   «inversione» altrimenti), `post_stop_mfe_r`, `mae_r` (massima escursione
   avversa in R). 45 uscite su 84 sono stop: senza questo il referto
   `stop_stretto` era cieco sui vincitori.
3. **Direzione × contesto BTC** nei referti (`per_contesto`) e settima ipotesi
   `controtrend_btc` → variante con conferma a 1 ora. Il contesto c'è solo sui
   trade dal 25 sera (`feats_at_entry.market_up`): i vecchi sono «ignoto».
4. **Storia delle ipotesi per tipo** (`learning/ipotesi_storia`, riga «IPOTESI
   PER TIPO» in `gate`): nate, varianti, passate, validate, bocciate per ogni
   regola dei referti, contro il tasso delle candidate casuali. Così una regola
   che non produce nulla si può spegnere con un numero.
5. **Sul trade chiuso**: fattori di size applicati (peso, freno, tilt,
   esplorativa), rischio effettivo, contesto di portafoglio all'ingresso,
   candela del segnale e latenza, tempo al primo gradino e al massimo
   favorevole, barre tenute, fette con prezzo e ora, momento del break-even;
   `mae_r` anche nel dataset del selettore. Calibrazione di regime e Fear &
   Greed a fasce (misurata, non usata).

**1 ora.** Zero validate e zero operate: l'unica candidata è ADAUSDT@1h con 1
conferma (24 set), la seconda non prima del 1° ottobre. La revisione ha trovato
tre rotture di parità che avrebbero colpito la prima validata a 1 ora, corrette
oggi: orizzonte del bot 24 h contro 96 del gate (ora per timeframe della
posizione), cooldown in barre del bot (ora ×4 a 1 ora), finestra del verdetto
trailing (ora in barre del trade). Aspetta il sì: allargare la discovery a 1 ora
da 5 a ~30 coin (stima 12 minuti a giro, da misurare; metro: tasso di passaggio
a 1 ora su 2 settimane contro lo 0,22% dei 15 minuti). Suite 1596 test verdi.

### 26 settembre, 11:35: verifica pulita «attesi contro aperti» (routine)

Sonda `frequenza` (ops 0265, coppie validate di OGGI: 182 su 62 coin) contro i
trade aperti per giorno (ops 0258). Dal 17 al 25: attesi 199, aperti 82 (41%),
ma la sonda usa il registro di oggi su tutta la finestra e a inizio settimana le
validate erano 59 (160 dal 24 sera, 182 il 26): gli attesi dei primi giorni sono
gonfiati di circa tre volte. Sui due giorni confrontabili col registro simile
(24 e 25 set): attesi 46, aperti 41, **89%**. Nessun divario sistematico:
confermato quanto misurato il 19 (87%). Da rifare fra una settimana con il
registro stabile a 182.

### 26 settembre, 14:20: il primo giro completo sfora le 3 ore (in corso)

Partito alle 09:04 UTC, alle 12:18 UTC era ancora in valutazione (274 coin ×
549 spec, ~150.000 valutazioni, contro le 15.900 di un giro urgenti; memoria a
8 GB su 15, ops 0279-0281). Non è un guasto: è il costo vero della
rivalutazione di tutte le spec, che non girava da giorni. Il timer a catena non
sovrappone giri (il servizio è ancora attivo), ma i giri urgenti del giorno
slittano. Correzione: la regola delle 20 ore fa partire il completo solo nella
finestra notturna (prima delle 08:00 UTC), con una rete a 30 ore; di giorno si
resta sugli urgenti. Il tempo del completo con intorno a 40 si legge a fine
giro.

### 26 settembre, 15:15: il primo giro completo è finito — e dice una cosa scomoda

Ops 0282-0284. Giro completo 09:06-12:55 UTC, **3h48**, modalità completa:
134.994 valutazioni su 239 coin, 358 coppie passate. Intorno a 40: 40 madri
riprovate, 5 figlie passate, 0 promosse (1 senza margine sulla madre, 4 senza
le conferme retroattive). Varianti dai referti: 2 create, 2 bocciate. Passata a
1 ora: 460 valutazioni, 1 passata (ADAUSDT, sempre lei). Esplorative: 34
attive, 31 scartate. Nessun errore, memoria a 8 GB su 15. Il tempo non è
l'intorno (320 valutazioni su 135.000): è la rivalutazione di tutte le spec, e
da stanotte gira solo nella finestra notturna.

**La cosa scomoda.** Il keep per coppia resta scritto su 15 validate e «non
ancora rivalutate» restano 167: il merge scrive i parametri d'uscita a ogni
coppia che PASSA, quindi 167 validate su 182 **non hanno passato il gate oggi**
sui dati aggiornati. Il fallimento si registra solo alla chiusura della finestra
(7 giorni) e la purga scatta dopo due finestre: fino ad allora il bot le opera
come validate. È il gate che dice, sui suoi numeri, quello che il paper dice col
PF 0,61: queste strategie in questo mercato non reggono. Proposta al
proprietario (cambia il gate, serve il sì): una validata che fallisce il giro
completo passa in «sospesa» (nessuna nuova apertura, posizioni aperte gestite
fino alla fine) finché non ripassa; il paper aprirebbe solo sulle 15 che
passano più le esplorative. Metro: PF vissuto delle sospese contro delle
attive nei 7 giorni successivi.

### 26 settembre, 19:30: il piano 1-5 è in produzione

Sì del proprietario a tutti e cinque i punti. Cosa è entrato (suite 1701 test
verdi, TypeScript e build puliti, nessun parametro tarato sul paper):
1. **Autopsia delle validate** (`scripts/autopsia_validate.py`, ops
   `autopsia-validate`): ogni validata rigiudicata come oggi, con la sua
   configurazione, e sugli ultimi 45/120/180 giorni. Da lanciare quando la
   chiave è in lista.
2. **Il gate giudica le validate sulla configurazione che operano** (scala,
   break-even, keep dal registro, con isteresi del 10% prima di cambiarla) e
   restituisce anche le bocciate: una figlia dell'intorno può ora sostituire
   una madre bocciata. **Declassate**: una validata bocciata in due giri
   completi di fila opera a un quarto della size finché non ripassa
   (`declassata`, `bocciata_notti` nel registro; riga DECLASSATE in `gate`,
   `[declassata]` nel log, sezione in `trades`). Non tocca passaggi né purga.
3. **Giro completo ridotto**: le spec note si rivalutano solo sulle coin dove
   hanno una coppia viva più un settimo dell'universo a rotazione (tutte in 7
   giorni); le candidate nuove restano su tutte le coin. Atteso 35-50.000
   valutazioni contro 134.994 (riga «GIRO RIDOTTO» in `gate`). Il bot ricarica
   il registro entro un minuto dalla scrittura del gate, non più ogni ora.
4. **Freno per gruppo con uscita** (`bot/learning/drift.py`): CUSUM sugli
   R-multipli e SPRT sul «tocca il primo gradino» per famiglia × regime e
   direzione × contesto BTC, soglie dichiarate nel codice, allarme → size ×0,5
   sul gruppo, ripresa automatica; si combina col freno globale prendendo il
   minimo. La panchina «peso sotto soglia» non rifiuta più: size con pavimento
   0,25 (`[panchina]` nel log). Ops `replay`: in che giorno avrebbe suonato sui
   trade del paper contro il freno globale, e i falsi allarmi sulla storia.
5. **1 ora su 30 coin** (`DISCOVERY_EXTRA=1h:auto30`: le 5 fisse, le coin con
   coppie a 1 ora, quelle con validate a 15 minuti, poi per volume; la vecchia
   lista di 5 nell'ambiente vale come auto30). Tetto 40 minuti invariato.
Metri e date: `docs/backlog.md` A4, I1, I2, J10, C1. Prima lettura utile: il
giro completo di stanotte (durata, valutazioni, declassate nuove, passate solo
con la propria configurazione) e il `replay`. Non verificato dal vivo: nessun
giro reale né Firebase da qui.

### Controllo del 27 settembre (08:00-08:31 ora italiana, ops 0286-0302)

Sola lettura su richiesta del proprietario: nessuna modifica al codice.

**Autopsia delle validate (ops 0290), la notizia del giorno.** 194 validate
esaminate su 212 (18 fuori tempo). Col gate di oggi ne passano 17; giudicate
sulla configurazione che operano, 23: l'artefatto della scala globale spiega
solo 6 bocciature su 177. Le 171 bocciate in entrambi i modi cadono sulla storia
lunga: recupero 37, consistenza 33, rendimento totale 32, holdout 30, regime 28,
pf senza i migliori 11. In simulazione, sugli ultimi 120 giorni, solo 24 su 190
hanno PF sotto 1, ma sono giorni che il gate ha già usato per sceglierle; la
prova indipendente è il paper (PF 0,62 contro 2,10 promesso). Lettura: la porta
d'ingresso è larga. `judge_window` (scripts/optimize.py) conta una finestra come
conferma se la coppia passa almeno UNA volta nei 7 giorni, anche su molte
valutazioni: una coppia al limite prima o poi passa per caso. Valutata una volta
sola, oggi ne passa una su otto.

**Freno per gruppo, replay (ops 0288).** Suona dopo il freno globale in 6 gruppi
su 7 (0-1,8 giorni dopo), l'unico «prima» è nello stesso giorno; falsi allarmi
sulla storia sana 3,5 ogni 100 trade (reggono). Per la regola dichiarata prima di
accenderlo, come allarme anticipato non serve. Il gruppo peggiore: ritorno alla
media in trend rialzista, 32 trade, R medio −0,24, dopo l'allarme 24 trade −10,50.

**Ombra dei rifiutati (ops 0289).** 34 registrati, 28 simulati: cooldown 11, R
−1,00, 0% vincenti (tutti stop); posizione già aperta 16, R −0,68, 19%; campione
sotto 30, nessun verdetto. Difetto del report: gli aperti a «R medio −6,80» sono
un errore (legge `post_mortem.stop_pct`, che è una frazione, come percentuale);
il valore giusto è −0,17R (ops 0291). Da correggere prima dei 30 casi, perché il
confronto è la regola per ritarare i freni.

**Numeri.** 110 trade delle validate più 1 esplorativo, 48% vinti, −73,79 USDT
(−7,4%), equity 927,56, oggi +3,59; 4 posizioni aperte, tutte short, 0,92% a
rischio (ops 0291, 0292, 0300). Uscite: 58 stop −191,35, 40 trailing +55,89, 10
scale-out +27,41; 34 stop su 58 andati a favore sotto il primo gradino (mfe
mediana 0,62R, ops 0297). Long 44 trade −22,40, short 66 −51,00. Costi 20,58 sul
lordo −53,21. Giornate del paper dal 16 set: 4 in utile e 8 in perdita (ops
0302). Gate: 212 validate su 68 coin, copertura 34% su 35%, 508 a 2/3, t su 29
misure (15 ≥ 2, mediana 2,12); keep per coppia su 27 (0,75 ×13, il candidato del
paper); esplorative 55 attive, 64 scartate, 1 poi validata, 1 trade (−0,39);
declassate 0 (serve il secondo completo) (ops 0294). Ultimo giro 05:06-06:19,
urgenti, 1h13, 22.560 valutazioni, 59 passate; giro notturno dedotto dal log del
bot: finito alle 03:47, partito verso le 02:02, completo ridotto di circa 1h45
(non letto direttamente). 1 ora su 19 coin: 1.577 valutazioni in 6 minuti, 5
passate (0,32% contro 0,26% a 15 minuti). Il giro partito alle 08:10 ha avuto 2
worker invece di 6 perché l'autopsia occupava la memoria. Selettore (ops 0301):
68.151 righe, NON BATTE (tutte 0/3, reversion 1/3, momentum 0/3, breakout
campione insufficiente), ripubblicato in ombra con soglia 0,50; in ombra sul
paper 38 trade con p, 0,65 vinti contro 0,63 persi, soglia che tiene tutto.
Portafoglio a 60 giorni (ops 0302): +25.444 su 10.000 senza limiti, drawdown
19,6%; col tetto per direzione +28.339, drawdown 12,7%; long 463 trade +24.997,
short 686 trade +447: gli short sono peso morto anche in simulazione (E1).
Periodo del paper: simulato −4.784,58 con 3 giorni in utile su 12, paper −73,79.
Dopo 4 perdite WR 63,6% su 22 (t −0,15): freno di serie resta spento.
Diversification ratio 0,10. Rifiuti 24 h: 21 posizione già aperta, 12 cooldown,
1 stop largo, 0 per peso. Frequenza: 25-26 set 51 attesi, 51 aperti. Ombra AI
d'accordo 10 su 123.

**Proposta del giorno (serve il sì):** una finestra vale come conferma solo se la
coppia passa la maggioranza delle valutazioni della settimana, non una volta
sola. Metro: quota di validate che passano una valutazione singola, oggi 12% (23
su 194), obiettivo sopra il 50% in tre settimane. In attesa del sì anche:
spegnere il freno per gruppo (bocciato dal replay) e correggere il report dei
rifiutati.

### 27 settembre, 09:00: i tre sì del mattino

Il proprietario ha detto sì alle tre voci del controllo:
1. **Conferma a maggioranza** (backlog J11): una finestra di 7 giorni vale come
   conferma solo se la coppia ha passato più della metà delle valutazioni di
   quella settimana; prima bastava una volta. È la porta da cui entravano le
   coppie al limite (autopsia, ops 0290: una su otto passa una valutazione
   singola). Le finestre già aperte chiudono con la regola vecchia, una volta.
2. **Freno per gruppo spento** (I2): bocciato dal replay con la regola scritta
   prima. Oggi non aveva effetto (il freno globale dimezza già tutto).
3. **Report dei rifiutati corretto** (J6): R medio degli aperti −0,17, non −6,80.
Suite 1709 test verdi. Il gate usa la regola nuova dal prossimo giro; il bot
riavviato per leggere il freno spento.

### Referto settimanale del 27 settembre (09:10 ora italiana)

Fonti: ops 0304-0307 (confronto, gate, servizi, log-gate delle 09:09) e il
controllo delle 08:00 (ops 0286-0302) per trades, mfe, stato, ai-stato, rifiuti.
1. **Quanto e come.** Settimana 21-27 set: 91 trade, −55,75 USDT (dalla tabella
   del periodo del paper, ops 0302). Totale: 110 trade delle validate più 1
   esplorativo, −73,79 USDT, equity 927,56, DRY_RUN True, costi 20,58 sul lordo
   −53,21 (ops 0291, 0292).
2. **Il lock taglia vincitori?** No: 30 verdetti trailing, 11 prematuri e 19
   protetti (log-gate); uscite trailing 40 per +55,89 contro 58 stop per −191,35.
   Nessuna proposta di allentare il keep; il gate sceglie anzi 0,75 su 13 coppie.
3. **Come muoiono gli stop.** 58 stop: 23 ingresso, 34 uscita, 1 protezione
   (ops 0297); il 21 set erano 7 / 13 / 1 su 21. Le proporzioni restano simili:
   sei stop su dieci erano andati a favore sotto il primo gradino.
4. **Il paper entra dove entra il gate?** 20 su 37 trade delle 8 coppie
   rigirate hanno un ingresso del gate entro 2 barre (54%, scarto mediano 16
   minuti); il 21 set 10 su 17 (59%). **Sotto il 60%: problema da aprire.**
5. **Le serie di perdite.** Il paper ha fatto 8 perdite di fila; il gate, sulle
   stesse 8 coppie e 2.256 trade dal 2023, non è mai andato oltre 7 (0 finestre
   di 8 su 2.249). Sulle stesse coppie, nel periodo del paper, i segnali del
   gate aperti dal paper hanno PF 0,45 e quelli non aperti 0,66: il gate ha
   promesso su un regime che non c'è più (ops 0304).
6. **Le gemelle.** 8 gruppi di due validate con la stessa logica sulla stessa
   coin (USELESS, SKYAI, MUBARAK, HEMI due volte, TRUMP, Q due volte); le
   candidate scartate come gemelle non compaiono nelle ultime 90 righe del log.
7. **La copertura.** 212 validate su 68 coin, universo 200, copertura 34% su
   35%; coin a 2/3: 124 (508 coppie), a 1/3: 132 (651 coppie). Il 21 set: 56
   coppie su 26 coin, universo 165. Sopra le 40 coin: C2 non serve per quel
   criterio (ma l'autopsia del 27 dice che una validata su otto passa una
   valutazione singola).
8. **Durata del giro.** Ultimo finito 05:06-06:19, urgenti, 1h13; il completo
   di ieri 3h48, quello di stanotte circa 1h45 (dedotto); il 21 set 2h22. Il
   giro partito alle 08:10 non compare fra i finiti: alle 08:51 ne è partito un
   altro con 6 worker (il log non dice perché; possibile un arresto per memoria
   mentre giravano le analisi del mattino). Prossimo avvio alle 11:01.
9. **Le vite.** Nessuna riga «[vite]» nelle ultime 90 righe del log.
10. **L'AI.** 20 ipotesi su 20 accettate alle 08:10; nel giro 20 ipotesi AI
    motivate e 40 casuali; ombra d'accordo 10 volte su 123.
11. **Il tetto per coin.** Zero blocchi nelle ultime 24 ore (rifiuti: 21
    posizione già aperta, 12 cooldown, 1 stop largo).

Migliorato: copertura (212 validate su 68 coin), controllo orario, misure sui
rifiuti e sugli stop, il lock protegge più di quanto tagli. Peggiorato: −55,75
nella settimana, ingressi del paper allineati al gate solo nel 54%, una serie di
8 perdite mai vista nel gate. Proposta: aprire il problema degli ingressi, trade
per trade (quale segnale, quale candela, perché il gate non entra), prima di
qualsiasi altra modifica alle uscite.

### 27 settembre, 11:20: il problema degli ingressi, aperto (ops 0308)

Prima lettura dello strumento `ingressi` (17 coppie su 58 nei 12 minuti del
canale; 41 coppie «tempo (budget)»). 70 trade del paper classificati: abbinati
36 (51%; 53% rigirando il motore «come il bot», da 200 barre prima del paper).
I 34 non abbinati:
- **15 «senza motore»**: sono TUTTI i trade dal 26 set 15:45 in poi. La cache
  delle candele sulla VPS finisce lì (lo script legge solo la cache, non
  scarica): non è una classe vera, è un limite dello strumento. Tolti questi,
  gli abbinati sono 36 su 55 (65%).
- **5 «motore in posizione» + 3 «cooldown»**: il gate era ancora dentro un
  trade precedente o nel cooldown dopo uno stop. Cascata di un'uscita diversa,
  non della regola d'ingresso.
- **5 «prezzo vivo»** (tutti su DEXEUSDT|gen_fa304106 e GPSUSDT): indicatori
  identici, ma il bot decide col prezzo dell'ultimo tick (`price_agent.
  build_snapshot`: `price = candles[-1].close` della candela ancora aperta)
  mentre il motore decide con la chiusura della candela precedente. Differenze
  di 1-4 decimillesimi bastano a far scattare la regola da una parte sola.
- **5 «ignoto»**, tutti di `gen_6d06dca0` su ORCAUSDT e VETUSDT: la regola non
  scatta nemmeno sui valori registrati dal paper stesso, e il motore non ha
  aperto NESSUN trade su quelle coppie nel periodo del paper (0 contro 6 del
  bot). È il caso da cercare per primo: stessa spec, stessi indicatori, due
  decisioni diverse. Sono i trade che il proprietario aveva già notato il 21
  set (VETUSDT short in profitto per 10 ore poi stop).
- 1 «segnale senza trade» (SUIUSDT: due trade del paper in 15 minuti sullo
  stesso segnale).
Per coppia: JTOUSDT, QUSDT, SYRUPUSDT 100%; SPXUSDT 5/6; ORCAUSDT e VETUSDT
con `gen_6d06dca0` 0/3; HUMAUSDT|gen_fca11c08 0/4 (3 senza cache).
Da fare (proposte, nessuna modifica fatta): (1) capire `gen_6d06dca0`: stampare
la regola e i valori barra per barra sui 6 trade; (2) decidere se il bot deve
valutare la regola sulla chiusura della candela (parità col motore) invece che
sul prezzo vivo; (3) far aggiornare la cache delle candele allo strumento, o
lanciarlo dopo un giro del gate; (4) rilanciare con `--budget 0` per le altre 41
coppie.

### 27 settembre, 15:30: il bug della sessione oraria (J13)

Il dettaglio sugli ingressi (ops 0310, 0311) ha spiegato i 5 «ignoto»: la
feature `session` leggeva l'ora dall'orologio del computer, non dalla candela.
Nel gate ogni candela storica era giudicata con l'ora del giro (di notte tutta
la storia «fuori sessione» = solo short, di giorno = solo long); nel bot con
l'ora della decisione: alle 03:30 UTC lo short era permesso e con RSI 76 il bot
vendeva, mentre lo strumento alle 13:00 vedeva «dentro» e vietava lo short.
Corretto (commit 803a99f, 1761 test verdi, bot riavviato alle 15:27): motore e
bot leggono l'ora dall'apertura dell'ultima candela chiusa, stesso valore.
**47 validate su 212 usano la sessione** (ops 0314): i loro passaggi sono stati
guadagnati su una regola valutata male. Decisione aperta per il proprietario:
lasciarle (il gate le rigiudica con la regola giusta e le finestre faranno il
loro corso), declassarle subito a un quarto, o azzerare i loro passaggi.

### 27 settembre, 19:40: la sessione diventa un filtro, le 47 ripartono da zero

Sì del proprietario: la feature `session` non sceglie più il lato (dentro la
fascia solo long, fuori solo short: nessuna ragione economica), diventa un
filtro che vale per entrambi i lati (dentro si opera, fuori no). Le 47 validate
che la usano ripartono da zero passaggi al primo giro della discovery: il bot
smette di aprirle entro un minuto, le posizioni aperte si chiudono da sole; la
loro coin resta fra le «proprie» del giro ridotto e vengono rigiudicate sopra
il cap, protette dalla potatura per 3 settimane. Metro: quante delle 47
ripassano entro 3 settimane col filtro a due lati (riga «FEATURE session» di
`gate`); sotto un quarto, vincevano solo grazie al difetto.
Trovato anche che `--sfondo` non sopravvive al servizio ops (systemd uccide il
gruppo, ops 0315): la chiave `ingressi-completo` ora usa `systemd-run`.

### 27 settembre, 21:00: il keep proposto per strategia dai verdetti trailing (I3)

Domanda del proprietario: «impariamo anche dai trailing prematuri?». Sì, ma
solo in aggregato: la proposta di keep era una per tutte le coppie (30
verdetti: 11 prematuri, 19 protetti → 0,75, scelto su 13 coppie). Ora ogni
strategia con almeno 5 verdetti trailing propone al gate il SUO keep: 0,25 se
almeno il 60% sono prematuri e almeno metà di questi «da rumore» (ritracciamento
sotto 1 ATR), 0,75 se almeno il 60% sono protetti. Il gate la prova sulle
coppie di quella strategia accanto ai tre valori fissi e alla proposta globale.
Nel log la riga «[paper] keep per strategia dal vissuto»; in `trades` il blocco
«KEEP PER STRATEGIA» con anche il tragitto lasciato sul tavolo (frazione del
percorso entry→TP, misurata e basta). Metro a due settimane: quota di
«prematuri» sulle coppie il cui keep viene dalla proposta per strategia
contro le altre. Suite 1789 test verdi; vale dal prossimo giro del gate,
nessun riavvio del bot necessario.

### 27 settembre, 22:50: l'analisi completa degli ingressi (ops 0318-0320)

Girata con `systemd-run` (50 minuti, 66 coppie, 135 trade del paper), col
codice nuovo: sessione come filtro e ora della candela. Abbinati 62 su 135
(46%); non abbinati 73, di cui 67 «ignoto» (la regola non scatta nemmeno sui
valori del paper). **Non è un difetto nuovo: è l'effetto atteso delle
correzioni di oggi.** Le coppie con la sessione hanno cambiato comportamento
nel motore: SUIUSDT|gen_490a90e5 da 782 a 292 trade sulla storia,
USELESSUSDT|gen_2031005e da 266 a 105, ORCAUSDT|gen_fca11c08 da 484 a 222
(stesse coppie, ops 0308 contro 0320); i trade del paper su quelle coppie
erano stati decisi con la regola vecchia (lato scelto dall'ora
dell'orologio) e la regola nuova non li riproduce: 0 su 7, 0 su 7, 0 su 5. Le
coppie senza sessione non cambiano: SPXUSDT 6 su 6 (214 → 215 trade del
motore), DEXEUSDT|gen_fa304106 137 → 137. Quindi la parità vera si misura solo
sui trade aperti DOPO le correzioni del 27 (chiusura della candela dalle
14:22, ora della candela dalle 15:27, sessione come filtro dalle 21:40 ora
italiana). Proposta: un filtro di data nello strumento (di default, i trade
dopo l'ultima modifica delle regole) e rilanciarlo fra una settimana.

### 28 settembre, 07:40: primo giorno in utile, e cosa è cambiato (ops 0321-0329)

Il 27 settembre è il primo giorno chiuso in utile di poco (+3,25) e il 28
parte bene (+4,82 alle 07:34, ops 0328). Totale: 142 trade delle validate più
2 esplorativi, 52% vinti (era 46-48%), −69,10 USDT, equity 930,69; freno
globale ancora acceso (PF 0,67 contro 2,10). Uscite: 69 stop −211,29, 58
trailing +72,11, 14 scale-out +35,61 (ops 0322). Cosa è cambiato nel registro:
la sessione ha azzerato 347 coppie (le 47 validate comprese), le validate
sono 192 su 66 coin, e **121 validate su 192 sono declassate a un quarto della
size** (bocciate in due giri completi di fila, ops 0324): la maggior parte del
paper oggi rischia un quarto. Il portafoglio simulato ora dà +7.190 dal 16
set (ieri −4.785): non è il mercato che è cambiato, è l'insieme di coppie
simulate (quelle validate oggi, gonfiate dalla selezione). 1 ora: 16 passate
su 2.310 (0,69%) contro 49 su 23.086 a 15 minuti (0,21%). Ombra dei
rifiutati: «posizione aperta» −0,20R su 31 casi contro −0,26R degli aperti:
la regola dice «ritarabile», ma la differenza (0,06R) è sotto il vantaggio
dei rifiutati simulati senza costi (0,1-0,2R): nessuna azione. Giro urgente
1h48, nessun errore; selettore in ombra 70 trade, p 0,65 vinti contro 0,63
persi, non seleziona.

**Nota del 28 set (il proprietario):** in dashboard il 27 settembre risulta
+1,26, non +3,25. Sono due conti diversi: il +3,25 viene dal report
`portafoglio`, che somma TUTTI i trade chiusi quel giorno (anche gli
esplorativi e le uscite non decise dalla strategia: manuali, kill switch,
circuit breaker); il +1,26 della dashboard (controllo orario) conta solo i
trade delle validate chiusi dalla strategia. Entrambi per giorno UTC di
uscita. La differenza (1,99) sta quindi in trade esplorativi o in uscite
esterne del 27: da verificare trade per trade al prossimo controllo.

### Controllo del 28 settembre (08:20 ora italiana, ops 0321-0333)

**Guasto, prima di tutto: quota di letture Firestore esaurita.** Alle 06:18 UTC
`mfe` e `frequenza` sono falliti con «429 Quota exceeded» (RESOURCE_EXHAUSTED,
ops 0331, 0332); alle 05:34 tutto funzionava. Il piano gratuito di Firestore
concede 50.000 letture al giorno (si azzera alle 09:00 italiane). Stima delle
letture del bot (dal codice, non misurate): verdetti trailing a ogni candela
(100 trade × 96 = ~9.600), pesi dopo ogni chiusura e ogni ora (~150 trade ×
~55 = ~8.200), controllo orario (ombra AI 200 + tutti i trade, × 24 = ~8.900),
ombra dei rifiutati a ogni candela su una finestra di 17 giorni che cresce di
~30 documenti al giorno (~5.300 oggi, ~24.000 fra una settimana), registro
ogni minuto (1.440), stop recenti, referti, report ops e dashboard. Totale
stimato oltre 50.000, e cresce coi trade. Finché la quota è esaurita il bot
non rilegge registro, pesi e trade (lavora con quello che ha in memoria);
le scritture hanno una quota separata. Proposta (serve il sì): una cache dei
trade in memoria nel bot aggiornata solo coi trade nuovi, finestra
dell'ombra dei rifiutati ridotta all'orizzonte vero, controllo orario che
riusa i trade già letti, e un contatore delle letture stampato ogni ora.
Atteso: sotto 15.000 letture al giorno.

**Numeri** (ops 0321-0330, 0333): 142 trade delle validate più 2 esplorativi,
52% vinti, −69,10 USDT, equity 930,69; 27 set in utile (+3,25 sul conto, +1,26
sulle sole validate), 28 set +4,82 alle 07:34. Uscite: 69 stop −211,29, 58
trailing +72,11. Long 54 −25,83, short 88 −43,27. Validate 192 su 66 coin,
121 declassate; 347 coppie azzerate per la sessione. Giro urgente 1h48. 1 ora:
16 passate su 2.310 (0,69%) contro 0,21% a 15 minuti. Selettore NON BATTE su
81.490 righe (ops 0333). AI: 20/20 proposte, ombra d'accordo 15 su 148.
`mfe` e `frequenza` non disponibili (quota).

### 28 settembre, 09:20: letture Firestore sotto controllo, giornate in ora italiana (J14)

Sì del proprietario. Quattro pezzi: (1) contatore delle letture nel client
Firebase, per chiamante, stampato ogni ora nel log del bot e pubblicato nel
controllo orario (`salute.letture_firestore_24h`, anomalia LETTURE_FIRESTORE
gialla sopra 25.000, rossa sopra 40.000); (2) cache dei trade nel bot,
aggiornata solo coi trade nuovi, ricaricata una volta al giorno e verificata
col conteggio di Firestore; (3) ombra dei rifiutati con finestra pari
all'orizzonte vero (26 ore a 15 minuti) e passata giornaliera che chiude come
«scaduto» ciò che è in attesa da più di 5 giorni; (4) controllo orario che
riusa i trade della cache e legge 50 decisioni dell'ombra AI invece di 200.
Stima dal codice: ~7.300 letture al giorno dal bot (erano oltre 50.000),
più ~2.000 da snapshot, ops e dashboard. Metro: la console di Firebase sotto
15.000 al giorno il 30 set e il 1 ott; altrimenti piano a consumo (Blaze).
Giornate: un solo helper (`bot/core/tempo.py`, Europe/Rome) per controllo,
portafoglio, trade_stats, frequenza e dashboard, con due totali per giorno
(conto = tutti i trade; validate = solo quelle decise dalla strategia).
Suite 1832 test verdi. Bot da riavviare.

### Controllo del 29 settembre (08:20 ora italiana, ops 0338-0350)

**Nessun guasto.** Letture Firestore del bot: 3.946 dal riavvio delle 22:00 del
28 (circa 10 ore; ~9.400 al giorno a questo ritmo), per il 58% dall'ombra dei
rifiutati (2.274), poi registro 645 e controllo 620 (log del bot, ops 0344).
Sotto la soglia gialla di 25.000; la console va letta il 30 set e il 1 ott.
Controllo orario pubblicato ogni ora (ultimo 08:06), sistema verde, paper
giallo, due anomalie: FRENO_GLOBALE (PF 0,70 contro 2,04) e SENZA_PROMESSA
(125 validate su 199 senza `last_pf`); nessun cambiamento del learning (ops 0338).
Nessun Traceback né OOM nei log.

**Numeri.** 174 trade chiusi (168 delle validate + 6 esplorativi), 96 vinti
(55%), −67,34 USDT, equity 932,66, DRY_RUN True, costi 28,16 su un lordo di
−39,18, 1 posizione aperta (XPL, 0,14% a rischio), massimo 9 contemporanee
(ops 0340, 0341). Giornate del conto (ora italiana, ops 0339): 27 set +1,26,
28 set +8,06, 29 set +1,27 alle 08:05 (validate +0,24); dal 16 al 28: 5 in
utile e 8 in perdita. BTC dal primo giorno +9,8% contro −6,7% nostro (controllo;
`stato` dà +10,63% su un periodo diverso). Uscite: 78 stop −228,42, 75 trailing
+83,23, 18 scale-out +43,59; 88% dei trade non tocca il primo TP; mfe mediana
0,88R. Stop per classe (ops 0346): 34 ingresso, 43 uscita, 1 protezione.
Validate 199 su 69 coin, copertura 34,5%, 492 coppie a 2/3; statistica t su 38:
25 reggono t ≥ 2, mediana 2,23 (ops 0343). Declassate 142 (erano 121). Giri:
03:05-05:08 solo urgenti (2h03), passata a 1 ora 29 su 2.520 (1,15%) contro 57
su 25.984 a 15 minuti (0,22%). Nessuna validata usa ancora la sessione (le 347
azzerate non hanno ripassato). Esplorative: 6 chiuse, 5 vinte, +1,78; 56 attive.
Declassate sul paper 18 trade R +0,045 contro attive 111 R −0,102 (metro al
3 ott). Selettore NON BATTE su 87.490 trade (0 finestre su 3). AI: 20/20
proposte, 38 delle 637 passate vengono dall'AI, ombra d'accordo 22 su 166.
Rifiutati (ops 0350): «posizione aperta» R −0,10 su 40 contro −0,21 degli
aperti: differenza 0,11, sotto lo 0,2R che serve (i rifiutati sono senza
costi), quindi nessuna ritaratura (il report dice «si può ritarare» perché non
applica il margine). Direzione (ops 0340): long 66 −29,38, short 102 −39,74;
dal 25 set, col contesto BTC noto, short +5,20 su 48 e long −10,60 su 36.

**Proposta del giorno (serve il sì): H2, prima metà — l'holdout chiede almeno
10 trade invece di 5.** Il paper rende PF 0,70 contro 2,04 promesso: il gate
promuove troppi fortunati. Oggi l'ultimo esame (45 giorni mai visti) si passa
con PF ≥ 1,05 su 5 trade, e con 5 trade il caso lo passa circa una volta su
due. Cambia: `GATE_HOLDOUT_MIN_TRADES` da 5 a 10, per le nuove candidate e per
le validate al prossimo giro completo. Non cambia: il bot, le size, le uscite,
il paper (mai usato per scegliere). Prima, sola lettura: capire perché un
gruppo numeroso di quasi-passaggi si ferma sull'holdout con scarto esattamente
0,000 (autopsia AI del 25 e del 29 set). Metro: `autopsia-validate` prima e
dopo (quante delle 199 reggono) e, fra due settimane, PF del paper delle
coppie che reggono contro quelle che non reggono.

### 29 settembre, 10:30: il gate e i 10 trade; il report del mattino impara a raccontare il learning e la spesa AI

**La proposta H2 del mattino (holdout a 10 trade) è ritirata.** Il proprietario ha chiesto cosa
volesse dire e che impatto avesse sulle tempistiche. Misurato e simulato (dettaglio in backlog H2):
il gate è permissivo (paper PF 0,70 contro 2,04 promesso; l'holdout lo passa il 46% di chi supera le
finestre a 15 minuti, ops 0322), ma chiedere 10 trade invece di 5 non toglie i fortunati: una
strategia senza vantaggio passa il 31% delle volte con 5 trade e il 37% con 10 (simulazione, non
codice del repo). Toglierebbe soprattutto le coppie che fanno pochi trade (70% delle validate sotto
10 trade in 45 giorni, ops 0290). Il giro non si allungherebbe, ma le validate a size piena
scenderebbero da 57 a ~15-32 (stima). Trovato strada facendo: lo «scarto 0,000» letto dall'AI è un
segnaposto del codice, non una misura.

**Il report del mattino ha tre sezioni nuove** (richiesta del proprietario), senza chiavi ops nuove:
* `controllo` stampa STORIA DEL LEARNING, COME IMPARA IL TRAILING (cosa ha visto il paper, cosa
  propone al gate e quanto manca, cosa ha scelto il gate per le validate e cosa è cambiato ieri e
  stanotte coppia per coppia, esito per keep in uso) e COSA IMPARANO LE STRATEGIE (ieri e stanotte:
  ipotesi, varianti, promosse, rimosse, declassate, esplorative, panchina; le 10 strategie più attive).
  Il «cosa è cambiato» viene da una foto giornaliera che il bot scrive su RTDB alla prima ora di ogni
  giorno (`/learning_giorni`): la prima foto la scatta il bot al riavvio di oggi, quindi domattina
  il confronto «ieri» copre da quell'ora a mezzanotte; dal 1 ottobre la giornata intera. Gli eventi
  datati (ipotesi, varianti, promosse, declassate, esplorative) valgono già da domattina.
* `ai-stato` stampa SPESA AI: token restituiti dall'API × 5/25 $ per milione, per ragione, ieri e
  oggi, media dei giorni interi, risposte troncate («pagate e buttate»). Il conto parte dal riavvio
  del bot e dal prossimo giro del gate; la fattura vera resta la console Anthropic.
* Corretto: la narrativa AI della domenica falliva sempre sul runner GitHub (blocco di ragionamento
  in testa alla risposta). Da ora i verdetti del trailing portano l'ora in cui sono stati dati.
Suite 1892 test verdi (senza `test_allowlist_runnable`, che lancia comandi di rete). Firestore: zero
letture in più nel bot, ~1 scrittura per chiamata AI, 9 letture in `ai-stato`. Bot da riavviare.

### Controllo del 30 settembre (08:20 ora italiana, ops 0358-0370)

**Da correggere prima di tutto: il filtro monete AI toglie monete alla passata a 1 ora.** Col
cambio del 29 sera (5000 token, D7) il filtro ha smesso di essere tagliato e ha cominciato a
escludere davvero: alle 06:10 UTC 10 monete su 30 della passata a 1 ora (UB, HEMI, SKYAI, MUBARAK,
BULLA, SAHARA, AVAAI, USELESS, HEI, TRUMP: «listing recente, storia troppo corta», ops 0365). Il
modello riceve solo i simboli, senza storia né volumi (`discover_strategies.py:3660`), quindi
giudica a memoria. Nel giro a 15 minuti la riaggiunta delle coin con coppie in corso lo neutralizza
(`coin_in_maturazione`, riaggiunta dopo il filtro), ma la passata a 1 ora usa `--symbols` e salta la
riaggiunta: le coppie a 1 ora in corso su quelle monete si fermano. Proposta (serve il sì): con un
elenco scelto apposta (`--symbols`) il filtro non si applica.

**Nessun guasto.** Bot vivo (PID dal 29 set 10:12), controllo ogni ora, foto del learning del 30
set scritta alle 00:20. Letture Firestore del bot: 8.621 in 21 ore (~9.800 al giorno), 63% dai
rifiutati (ops 0364). Giro del gate 05:08-07:09, 2h01, solo urgenti (ops 0363).

**Numeri.** 189 trade chiusi (182 validate + 7 esplorativi), 106 vinti (56%), −68,65 USDT, equity
931,35, DRY_RUN True, costi 29,66 su un lordo di −38,99; 2 posizioni aperte (MUBARAK long, STX
short, 0,28% a rischio); max 9 contemporanee (ops 0360, 0361). 29 set chiuso a −0,17 (conto); dal
16 al 29 set 5 giorni in utile e 9 in perdita (ops 0359). BTC dal primo giorno +9,9% contro −6,9%
nostro (ops 0358). Uscite: 83 stop −236,68, 84 trailing +89,30, 19 scale-out +44,48; 88% senza
primo TP; mfe mediana 0,87R. Stop per classe: 39 ingresso, 43 uscita, 1 protezione; i 5 stop nuovi
tutti «mai andati a favore» (ops 0366). Validate 202 su 70 coin, copertura 35,0% (obiettivo
raggiunto), 562 coppie a 2/3, 181 idonee il 1 ott; t ≥ 2 per 26 su 42 (ops 0363). Declassate 160.
Passata a 1 ora 0,94% contro 0,20% a 15 minuti. Declassate sul paper 27 trade R +0,065 contro
attive 116 R −0,119 (metro al 3 ott). Esplorative 7 chiuse, 6 vinte, +2,67. Selettore NON BATTE
(0 su 3, 92.257 trade, ops 0368). Rifiutati «posizione aperta» −0,15R contro −0,21R: +0,06R, sotto
lo 0,2R, nessuna ritaratura (ops 0370). Frequenza: 29 set 24 apribili contro 23 chiusi. Direzione:
long 76 −31,76, short 106 −39,56; col contesto BTC noto (dal 25 set) long −12,98 su 46, short
+5,39 su 52 (ops 0360).

**Come impara il trailing** (ops 0358, primo confronto fra foto: 29 set 10:12 → 30 set 00:20):
70 verdetti sulle uscite trailing = 29 prematuri + 41 protetti; ieri +4 prematuri e +5 protetti.
La proposta di keep 0,75 si allontana: 58,6% di protetti, mancano 3 protetti (ieri 1). Nessuna
strategia arriva a 5 verdetti. Il gate ha scelto keep per 43 validate su 202 (0,35 ×14, 0,5 ×10,
0,65 ×6, 0,75 ×13); cambiate stanotte 2 coppie (AVAAI e PLUME, tornate piene). Per keep in uso:
0,5 → 122 trade, R −0,06; gli altri gruppi hanno 3-5 trade.

**Cosa imparano le strategie:** ieri 10 promosse, 0 rimosse, 23 nuove declassate, 50 esplorative
entrate e 60 scartate, 1 strategia in panchina (gen_c5194ce4 in alta incertezza); stanotte 5
promosse, 20 declassate, 2 tornate piene. Numeri da capire: la foto dice «validate +5 / −2» ma
nessuna rimozione nel diario delle vite; le esplorative entrate il 29 sono 50 nel conto di oggi e
53 in quello di ieri alle 10:13.

**Spesa AI** (ops 0362, prima misura; 29 set dalle 10 in poi, giornata non intera): 1,88 $ in 43
chiamate: idee di strategie 0,95 $ (50%), filtro monete 0,38 $ (20%, 4 risposte su 10 tagliate
prima del cambio), autopsia 0,34 $, ombra 0,21 $. Oggi fino alle 08:12: 0,87 $ in 18 chiamate, nessuna
tagliata. A ~0,33 $ per giro del gate più l'ombra, circa 3 $ al giorno (stima).

**Proposta del giorno (serve il sì): H5, «dove perde il paper», misurato FUORI CAMPIONE.** Il numero
che il `portafoglio` usa per dire «esecuzione o mercato» misura la selezione: sugli stessi giorni
16-24 set il simulato fa −1.357 con le coppie del 25 set (ops 0232) e +8.465 con quelle di oggi
(ops 0359). Cambia: una sezione FUORI CAMPIONE nel `portafoglio` (già lanciato ogni mattina): per
ogni validata solo i trade del motore entrati DOPO la sua validazione (`validated_at`; il 21 set per
le più vecchie), accanto ai trade del paper sulle stesse coppie e negli stessi giorni (senza
esplorativi né coppie azzerate), con R medio, % vinti, mfe e primo target, differenza e 2 errori
standard. Nessun backtest né lettura Firestore in più. Non cambia: bot, gate, registro, size,
uscite, numero di trade. Metro: prima lettura il 1 ott, decisione il 7 ott con la regola scritta
ora: motore fuori campione a R ≤ 0 → il divario è la selezione del gate e la prossima leva va nel
gate; motore > 0 e sopra il paper di 2 errori standard → è esecuzione e la leva va sul bot;
altrimenti si rilegge il 14 ott. Verificato sul codice (`portafoglio_backtest.py:102-160`,
`optimize.py:1000-1014`); con ~150 trade del motore e ~100 del paper si legge una differenza di
~0,28R. Scartate: I5 (si sta chiudendo da sola), B4 (nessun metro in 3 ore), I7 (contare gli
incassi parziali porta i protetti al 55%, più lontani dal 60%), I8 (29% di «rumore» dopo gli stop è
nel range del caso, 26-55%), I9 (seconda: pronta, ma agisce su 5 trade), H1 (t misurata su 42
validate su 202).

### 30 settembre: voci tolte dal backlog (sì del proprietario: «rimuovendo le scartate»)

Regola d'uscita del backlog: una voce si toglie quando si decide di non farla, scrivendo perché.
* **A5 — take profit presi dal grafico:** smentita. Il livello del grafico sta in mediana a 3,35R e
  lo raggiunge il 7% dei trade, contro l'11% del primo gradino (ops 0366; già il 24 set, ops 0210).
  I take profit restano multipli dello stop; la strada rimasta (un primo gradino più basso) è già
  fra le scale che il gate prova.
* **C2 — universo fermo al top 200:** la voce diceva di allargare solo se la copertura restava
  sotto 40 coin: sono 70 (ops 0363).
* **C3 — la copertura non arriverà al 35%:** smentita, 35,0% il 30 set (ops 0363).
* **D4 — LunarCrush:** già tolta il 23 set per decisione del proprietario (i dati esterni si fanno
  tutti insieme in una sessione dedicata); restava solo il titolo.
* **I7 — contare le uscite con incasso parziale nelle proposte di keep:** contandole, i protetti
  scendono dal 58,6% al 55,1% (49 su 89, conto del 30 set): la proposta si allontana e oggi non
  cambierebbe nessuna scelta. Il report del mattino le mostra comunque a parte.
* **I8 — usare i verdetti dopo gli stop («rumore» = il prezzo è poi tornato al primo target):**
  23 «rumore» su 79 stop = 29%, dentro l'intervallo che darebbe il caso (26-55% per stop di
  1,5-2,5 ATR e primo target a 1,5-2R, simulazione del 30 set): nessuna base per una regola «stop
  più largo». Il report continua a contarli.
Restano: **I9** (isteresi della proposta keep 0,75: pronta, seconda dopo H5) e **B4, I5, H1**, che
il 30 set erano state scartate solo come proposta del giorno, non come voci.

### 30 settembre, 09:40: filtro monete fuori dalla passata a 1 ora; la misura fuori campione (H5)

Sì del proprietario a tutte e due. (1) Con un elenco di monete scelto apposta (`--symbols`, la
passata a 1 ora) il filtro AI non si applica più: stanotte ne aveva tolte 10 su 30 giudicandole dal
nome (ops 0365). Senza `--symbols` il giro principale resta identico. (2) Il `portafoglio` stampa la
sezione FUORI CAMPIONE: i trade del motore nati dopo la validazione di ogni coppia contro i trade del
paper sulle stesse coppie, con la regola scritta prima dei numeri (backlog H5): decisione il 7 ott,
con almeno 80 trade del motore. Revisione avversaria su tre fronti (validità statistica, codice,
lettore): 14 rilievi, tutti corretti; il più importante, le coppie senza data di validazione
partono dal 25 set 12:00 UTC e non dal 21 (prima di allora la data non era scritta per le generate,
quindi una parte della misura sarebbe rimasta in campione). Suite 1928 test verdi (senza
`test_allowlist_runnable`). Il bot non va riavviato: la discovery e il `portafoglio` prendono il
codice dal repo al giro successivo.
**Prima lettura FUORI CAMPIONE (ops 0371, 30 set 09:50):** 202 coppie; motore dopo la validazione
117 trade, R medio +0,12, vinti 69%; paper sulle stesse coppie e negli stessi istanti 77 trade, R
+0,001, vinti 65%; differenza +0,12R con margine ±0,25R: dentro il margine, non si decide (servono
~824 trade in tutto se resta così). Scomposizione: stessi segnali 62 trade, motore +0,05R contro
paper +0,01R; segnali del motore che il paper non ha preso 55, R +0,20. La cosa nuova: il paper
sulle 25 coppie che NON sono più validate (azzerate il 27 set, sostituite, rimosse) fa 45 trade a
R −0,23: la perdita del paper sta soprattutto lì, su coppie che il gate ha già tolto o ridotto.
Rimosse dal 16 set: 0 (bias di sopravvivenza piccolo per ora). Config diversa da oggi: 3 trade su
77. Il minimo di 80 trade del motore è già raggiunto; si rilegge il 7 ott con la regola scritta.

### 30 settembre, pomeriggio: le regole delle letture di ottobre, scritte PRIMA dei numeri (K1) e il gruppo di controllo (K3)

Sì del proprietario («parti da A e C insieme, poi B»). **Regole, fissate oggi 30 set:**
* **7 e 14 ott, «selezione»** (la promessa non regge dopo la validazione): motore fuori campione
  con R medio ≤ 0 su almeno 80 SEGNALI unici (stessa moneta, candela e direzione contano una
  volta: le gemelle non contano doppio), sulla riga «tutte le coppie operate» (le coppie uscite
  dal registro rigiocate fino al giorno dell'uscita, per togliere il bias dei sopravvissuti).
* **7 e 14 ott, «esecuzione»** (è il bot): SOLO sulla riga «stessi segnali» (paper e motore
  entrano sullo stesso segnale: stesso mercato, così si misura l'esecuzione e non ciò che il paper
  non poteva prendere), con almeno 30 trade accoppiati e la differenza oltre il margine.
* **Margine:** 2 errori standard, il più largo fra quello per giornata (le giornate nere
  colpiscono tutti insieme) e quello trade per trade; almeno 2 giornate.
* I segnali non presi dal paper si confrontano con quelli presi dal portafoglio del motore (anche
  lui una posizione per moneta): stampati, ma non sono un verdetto sul bot.
* Tre letture (3, 7, 14 ott): la probabilità che almeno una suoni per caso sale da ~2,5% a ~7%
  (stima della revisione); un verdetto isolato si conferma il 14.
* **3 ott, declassate contro attive** (in `trades`): solo trade entrati dal 27 set 19:40 UTC (fine
  del difetto della sessione); «diverso» se la differenza supera il margine; «uguale» solo se
  differenza + margine sta sotto 0,15R; altrimenti «non si decide».
La prima lettura (ops 0371) resta valida come riassunto; da ora la regola è questa.
**Gruppo di controllo (K3), acceso:** a ogni giro ~50 bocciate a caso con la spec intera e, una
volta al giorno, la foto delle conferme, in file locali sulla VPS (`data/gruppo_controllo/`).
Il rigioco e le sue regole dopo il 7 ott. Suite 1961 test verdi (senza `test_allowlist_runnable`).

### 30 settembre, sera: il voto t di ogni validata (K2) — fatto, controllato, riverificato

Sì del proprietario («poi B»). Il voto t (quanto il guadagno medio di una strategia è grande
rispetto a quanto oscilla) si salva nel registro e si fissa al giorno della promozione; una passata
una tantum lo calcola per tutte le validate sui dati tagliati al giorno della loro validazione, in un
file locale sulla VPS; il `portafoglio` divide il fuori campione per voto. Controllo avversario: 30
agenti, 22 difetti confermati, 19 corretti (il più grave: la t del walk-forward della passata usava
i dati di oggi; poi il rischio di sovrapporsi al giro del gate, l'arrotondamento che faceva passare
1,997 per 2, un segnale contato in due gruppi); riverifica delle correzioni: 252 valutazioni del
gate identiche, merge del registro identici salvo i campi nuovi, nessuna scrittura Firebase dalla
passata. Suite 2001 verdi. Restano al proprietario: la regola H1 (quale t, soglia, minimo) prima
del 7 ott, e aggiungere sulla VPS le due righe `voto-t-completo` e `voto-t-esito`.

### 30 settembre, sera: regola H1 decisa, filtro monete e ombra AI spenti, F2 e J12 chiuse

Decisioni del proprietario («H1: ultimo esame, soglia 1,5, minimo 80: sì, filtro spegnilo tu, ombra
spegnilo tu, F2 e J12 chiudile»), prese PRIMA che il `portafoglio` stampasse i risultati divisi per t.
* **Regola H1 (scritta prima dei numeri):** decide solo la t dell'ultimo esame (45 giorni), soglia
  1,5; almeno 80 segnali per gruppo; «proposta» se la t alta rende più della bassa oltre il margine,
  «chiusa» se differenza + margine < 0,25R, altrimenti «non si sa ancora» (metà novembre). La
  passata del voto (ops 0383): 213 coppie votate in 647 s, t del gate ≥ 2 in 47 su 213, t
  dell'ultimo esame ≥ 2 in 18 su 183.
* **Filtro monete AI spento** (default `AI_UNIVERSE_FILTER=false`): giudicava dal nome (ha escluso
  QUSDT, 393 giorni di storia), non ripetibile, nessun effetto misurabile sui trade; ~0,45 $/giorno.
* **Ombra AI spenta** (default `AI_SHADOW_ENABLED=false`, serve il riavvio del bot): nessuno la
  usava, veto sull'85% dei trade, non passa dal gate; 0,3-0,75 $/giorno e ~1.200 letture Firebase.
  Le 229 decisioni registrate restano.
* **F2 chiusa, non si fa** (strategie in paper dopo 1 conferma a un quarto di size): il 70-77% delle
  coppie a 1-2 conferme non ripassa; il quarto di size non limita il rischio (K5); toglierebbe posto
  alle validate. La domanda «servono 3 conferme?» la risponde il gruppo di controllo (K3) verso
  metà ottobre: se 1 conferma bastasse, si riapre con quel numero.
* **J12 chiusa, obiettivo raggiunto** («il paper entra dove entra il motore?»): 81% dei trade del
  paper con un ingresso del motore vicino (64 su 79, ops 0373), contro l'80% richiesto. Il filtro di
  data nello strumento `ingressi`, tenuto in memoria dal 28 set, non serve più.

### 1 ottobre: pulizia del backlog (sì del proprietario: «pulisci il registro»)

Il backlog teneva come memoria anche voci già fatte, contro la sua regola d'uscita. Tolte, col verdetto (il testo intero resta nella storia di git):

**Fatte (12):**
* **A1** — la protezione del profitto si arma prima (21 set).
* **A2** — il break-even lo sceglie il gate anche per le generate (21 set).
* **B2** — le strategie scritte a mano tolte dalla ricerca: 0 validate su 1.312 valutazioni (21 set).
* **B2bis** — tolto il controllo su `rr` che scartava 14 proposte AI su 19 (21 set).
* **B3** — l'AI legge perché le candidate vengono bocciate (autopsia, 21 set).
* **G1** — tetto di rischio per direzione (3%) attivo nel bot.
* **G2** — il portafoglio delle coppie insieme è il comando `portafoglio`, gira ogni mattina.
* **G4** — 40 candidate casuali a giro invece di 100 (24 set); misurato dopo: 0,21-0,26% di passaggio contro 0,3% prima, nessun miglioramento visibile.
* **D2** — i dati sintetici non entrano più di nascosto quando Binance non risponde.
* **D3** — il modello AI è configurabile; sulla VPS lo sceglie il proprietario.
* **E2** — le proposte AI non vengono più scartate (20 su 20 accettate).
* **E3** — Binance 451 dai runner GitHub: aggirato.

**Non servono (10, dalla revisione del 30 set, `docs/revisione_sospese_30set.md`):**
* **A3** — il rischio per trade che dipende dalla volatilità non cambia nessun risultato in R; è una scelta neutra (revisione del 30 set).
* **B1** — far inventare formule all'AI: lo stesso vocabolario a 1 ora passa lo 0,94% contro lo 0,20% a 15 minuti (ops 0363): il limite sono i costi, non le parole.
* **B4** — l'AI che legge i referti: la stessa domanda su 92.257 trade storici non trova condizioni utili (ops 0368), e su 143 referti anche il caso produce un «filo comune» apparente.
* **F1** — accendere il selettore: NON BATTE «apri tutto» su 92.257 trade, 0 finestre su 3 (ops 0368); resta in ombra e si misura in F1ter.
* **G5** — sopravvivenza dell'universo: nessuna correzione semplice; resta un avvertimento quando si leggono i backtest.
* **H1** — t ≥ 3 sulle finestre: la mediana delle validate è 2,23 e la misura è sui dati usati per scegliere; sostituita da K2 (t dell'ultimo esame, regola decisa il 30 set).
* **H2** — holdout diverso per ogni candidata: non riduce la fortuna della singola e toglie l'esame sul mercato recente; la soglia a 10 trade ritirata il 29 set; l'artefatto dello «scarto 0,000» passa in K7.
* **I2** — spegnere il freno globale in paper non cambia nessun R; il difetto vero (uscita irraggiungibile) è K6.
* **I6** — il tetto di 5 posizioni toglierebbe trade in ordine d'arrivo, non i peggiori; 0 rifiuti per rischio su 71 (ops 0370).
* **I9** — isteresi del keep 0,75: 5 trade in tutto a −0,14R (ops 0358), e il gate sceglie il keep alto anche su un prezzo casuale.
* **E4, parte del filtro `min_adx`** — l'ADX è la variabile che conta meno, ultima su 18 (ops 0368); E4 resta solo per le strategie gemelle.

**Chiuse dopo (1 ott), senza lavoro da fare:**
* **J1** — nessun lavoro finché i trade sono pochi (oggi ~190): il costo lo sorveglia da sola l'anomalia `CONTROLLO_LENTO` del controllo orario (oltre 2 s), che dirà quando servono le somme incrementali.
* **J3** — non si fa, per scelta: un controllo vecchio È l'avviso che il bot è fermo, e il battito lo dice già; un timer in più non aggiunge informazione.
* **J4** — fatta: il proprietario ha guardato la dashboard con dati veri (il 28 set ha trovato +1,26 contro +3,25 del 27 set, spiegato e corretto con i due totali «conto» e «validate»).
* **J5** — non si fa: persistere i contatori costerebbe una scrittura per rifiuto; i rifiuti che contano sono già salvati e misurati dall'ombra dei rifiutati (J6, `rifiutati_report`).

### Controllo del 1 ottobre (08:15 ora italiana, ops 0386-0398)

**Da guardare per primo: il giro completo del gate è durato 2h58** (03:53-06:52, ops 0391), a 2 minuti
dalle 3 ore; nelle stesse ore il semaforo SISTEMA è stato giallo con una terza anomalia (03:18-06:20,
ops 0392; codice non visibile nel log, probabilmente l'anomalia del gate in corso: non verificato).
Alle 08:05 era verde. Il giro completo ha fatto 41.419 valutazioni e 356 passate (0,86%).
**Spazio del registro:** 476 KiB su 879, «ci stanno ancora ~1.380 coppie» (ops 0391), a ~+99 coppie al
giorno ~14 giorni: il lavoro K2 è in corso. **Filtro monete e ombra AI spenti:** nessuna «[ai-shadow]»
dopo il riavvio (ultima decisione 30 set 17:47, ops 0390, 0392); 8 chiamate AI fino alle 08:13, quante ne
fanno 2 giri senza filtro (deduzione: col filtro sarebbero 10). Letture Firestore 4.185 in ~11 ore.
**Numeri:** 204 trade (196 validate + 8 esplorativi), 57% vinti, −70,82 USDT, equity 929,18, DRY_RUN
True; 4 posizioni aperte tutte short (0,55% a rischio); 30 set chiuso a −2,18; dal 16 al 30 set 5 giorni
in utile e 10 in perdita (ops 0387-0389). BTC dal primo giorno +11,4% contro −7,1% nostro. **In R dal
27 set** (nuovo, ops 0388): +0,042R netti a trade su 61, +0,118R lordi, costi 0,076R; short +0,21R, long
−0,09R. **Fuori campione** (letture stampate, regole del 30 set): «Selezione: il motore guadagna ancora
dopo la validazione (+0.06R, margine ±0.18R per giornata, 89 segnali): nessun verdetto contro il gate.
Esecuzione: non si decide (differenza +0.05R, margine ±0.16R)»; «H1: non si sa ancora: 18 e 65
segnali, ne servono 80 per gruppo». Regola del 3 ott in anteprima: declassate +0,041R contro attive
+0,042R, NON SI DECIDE. Validate 208 su 71 coin; 613 coppie a 2/3; declassate 162; t ≥ 2 per 35 su 51.
Passata a 1 ora 1,77% contro 0,86% a 15 minuti (30 coin: filtro saltato). Selettore NON BATTE. Spesa AI
del 30 set (primo giorno intero, quasi tutto prima dello spegnimento): 2,80 $ in 57 chiamate (idee 55%).
Rifiutati «posizione aperta» −0,13R su 45: il report dice ancora «RITARARE» per un confronto su periodi
diversi (vedi la proposta). **Proposta del giorno (serve il sì): J6, confrontare rifiutati e aperti
nello stesso periodo** in `rifiutati_report` (solo report; la regola non cambia). Trovato anche: la
storia delle esplorative tagliata a 200 voci rompe la loro misura (backlog K11).

### 1 ottobre, mattina: il report dei rifiutati confronta lo stesso periodo (J6)

Sì del proprietario («correggi il report»). Scritto PRIMA del primo report nuovo, perché il verdetto
su «posizione aperta» probabilmente si gira: gli aperti ora partono dall'istante del primo rifiutato
registrato (26 set), per ora d'ingresso, con R netto e lordo; la regola resta quella scritta (almeno
30 casi valutati e R dei rifiutati maggiore di R degli aperti); il margine si stampa solo come
informazione (calcolato caso per caso, quindi probabilmente più stretto del vero). Lo 0,2R che il
controllo del mattino aggiungeva a mano non serve più: la causa era il periodo diverso.

### 1 ottobre, mattina: lato gate delle voci aperte (K2 spazio, K7, D6-IPOTESI) — fatto; I4bis rinviata

Parte della richiesta «fai tutte quelle 15 aperte». Il lavoro era stato interrotto alle 07:49 ora
italiana a test già verdi e restava non salvato: riletto, suite rilanciata (2099 test verdi) e salvato
alle ~11 ora italiana. **Nessun verdetto del gate cambia:** `passed` resta `hold.get("ok")` e i quattro
controlli dell'holdout sono gli stessi; cambiano solo i campi descrittivi. **Nessun riavvio del bot:**
tutto gira nel giro del gate (timer), che prende il codice nuovo da solo.
* **K2, spazio del registro.** I quattro campi del voto t restano nel nucleo solo per le coppie a 2
  conferme o più (`nucleo_registro`, stessa regola nei tre alleggerimenti). Chi arriva alla
  promozione ha sempre la t dell'ultimo passaggio (test: stessa vita con e senza la regola, stessi
  `val_*`). Misura su un registro finto con la distribuzione delle conferme di ops 0391 (1.630
  coppie): da 435 a 401 KB nel nucleo, −34 KB (−8%), ~42 byte in meno per coppia sotto le 2 conferme.
  Stima mia: lo spazio passa da ~14 a ~17-18 giorni a +99 coppie al giorno. Si controlla nella riga
  «ci stanno ancora ~N coppie» di `gate` dopo il primo giro.
* **K7, dati all'AI.** (1) Una caduta sull'holdout porta lo scarto vero della soglia che l'ha
  fermata (`holdout_verdict`) e i numeri dell'holdout, non più «scarto 0,000» coi numeri delle
  finestre; è «quasi-passaggio» solo con una soglia mancata di meno del 10%, come le altre. Effetto
  voluto: meno cadute sull'holdout fra i quasi-passaggi, quindi cambiano i semi delle mutazioni e la
  scelta delle esplorative; le righe del selettore restano come prima. Anche il gruppo di controllo
  (K3) dal 1 ott registra il «quasi-passaggio» con la regola nuova. (2) La riga GATE delle prove
  all'AI viene dall'autopsia del giro precedente dello stesso timeframe, solo se ha meno di 12 ore
  (prima: «su 1320 valutazioni ne passano 0», fermo al 21 set). (3) Un'autopsia per timeframe:
  la passata a 1 ora scrive `gate_autopsy/discover_1h`, il giro a 15 minuti legge solo la sua.
* **D6-IPOTESI, le idee AI servono?** Nuova riga «ORIGINI» in `gate`: coppie nel registro, validate e
  declassate per origine della spec (AI, casuali e mutazioni, varianti dai referti, intorno), più le
  candidate dell'ultimo giro per origine. Si contano le coppie, non l'R (regola del 30 set). Le
  candidate per origine compaiono dal primo giro finito col codice nuovo.
* **I4bis rinviata.** `da_ts` decide anche il taglio della pre-registrazione (la validazione della
  figlia finisce prima del primo trade del paper): spostarlo alla data dell'ipotesi metterebbe giorni
  del paper dentro la validazione. Serve un campo separato scritto dal bot, cioè un riavvio, e il
  backlog dice di farlo solo se i numeri mostrano che l'urgenza serve: oggi nessun numero lo mostra.

### 1 ottobre, mezzogiorno: K10 (conteggio), K11, scritta della panchina — fatti

Sì del proprietario («procedi k10-k11 e la scritta fuorviante»). Nessuna soglia, uscita, size o freno
cambia.
* **K10, solo un conteggio.** Nuova sezione «SOGLIA DEL WIN RATE (K10)» nel report `trades`: le
  validate divise per ultimo win rate del gate (≥ 0,45; fra la soglia di oggi e 0,45 = «allentata»,
  cioè esistono solo perché il supervisore l'ha abbassata; sotto; non salvato) e l'R netto del paper
  delle stesse coppie, tutto e dal 27 set. Approssimazione dichiarata: conta l'ultimo passaggio, non
  tutti. Una lettura del registro in più per report. Rimettere la soglia resta dopo il 7-14 ott.
* **K11.** Nel taglio a 200 voci della storia delle esplorative le «validata» restano per sempre e le
  scartate tolte si sommano in `scartate_tolte`: «validate poi» e «scartate» non scendono più da soli.
  La validata uscita fra ops 0363 e 0391 non si recupera (la chiave non è salvata altrove).
* **Scritta del log.** In parità la riga dice «3 stop consecutivi (panchina spenta in parità: continua
  a operare)» invece di «in panchina». Codice del bot: vale dal prossimo riavvio, che non serve
  anticipare per questo.
Test: 2105 verdi due volte di fila; una volta prima un test del voto t (`test_un_errore_su_una_coin_
non_butta_le_coin_gia_votate`, coi processi) è caduto e ripassato da solo: da tenere d'occhio.
**Primo conteggio K10 (ops 0403, 11:51 ora italiana):** 7 validate «allentate» (paper +0,244R su 11
trade), 72 a ≥ 0,45 (−0,054R su 50), 129 senza win rate salvato (−0,137R su 57). Nessun segno contro
la soglia bassa, ma il campione è minimo e il 62% delle validate non si può classificare: si rilegge.

### 1 ottobre, primo pomeriggio: I4bis fatta, D7 chiusa, backlog rifatto

* **I4bis** (sì del proprietario: «fai i4bis»). Il bot scrive in ogni ipotesi `scala_stretta` anche
  `scattata_ts`: la chiusura della terza perdita sotto il primo gradino (`MIN_SCALA_STRETTA`). La
  corsia urgente del gate (`strategie_scala_stretta`, 7 giorni) guarda quella data; senza (referti di
  prima) usa `da_ts` come prima. **`da_ts` non cambia:** è il primo trade del paper e decide il taglio
  della pre-registrazione delle figlie (`ipotesi_da`); spostarlo avrebbe messo giorni del paper nella
  validazione. Effetto atteso: una strategia in paper da più di 7 giorni con l'ipotesi appena
  scattata entra nel giro «solo urgenti». Codice del bot: vale dal riavvio. Test 2108 verdi.
* **D7 chiusa:** il proprietario ha riempito il segreto `ANTHROPIC_MODEL` su GitHub. Da verificare nel
  prossimo `ai-stato`: l'avviso «modello diverso» del lunedì deve sparire.
* **Backlog rifatto** (richiesta del proprietario: solo le voci da fare o in attesa). `docs/backlog.md`
  ha 6 gruppi e 21 voci; il file di prima, con le voci fatte e in misura e tutti i numeri, è
  `docs/backlog_archivio.md`, invariato salvo l'intestazione e le due voci chiuse oggi.

### 1 ottobre, pomeriggio: R1, il gate rigiocato nel passato — REGOLA scritta PRIMA dei numeri

Sì del proprietario («vai con R1»). Domanda: il gate sceglie strategie con un vantaggio vero, o
soprattutto fortuna? Si rifà il gate nel passato e si guarda cosa succede DOPO la sua scelta.
* **Date:** 26, una ogni 14 giorni all'indietro; la più recente è l'ultima che lascia 14 giorni interi
  di dati dopo di sé (verso metà settembre 2026), la più vecchia circa un anno prima.
* **A ogni data D:** il gate, con le stesse soglie di oggi (senza AI e senza la vita del registro),
  giudica candidate nuove usando SOLO i dati fino a D (caricati fino a oggi e tagliati in memoria:
  nessuna scrittura nel registro, in Firebase o nella cache del gate).
* **Dopo:** i trade del motore delle stesse candidate entrati nei 14 giorni dopo D, in R netto
  (costi del motore), con la configurazione d'uscita scelta dal gate.
* **Gruppi:** «passate» (superano tutto il gate, holdout compreso, alla data D) contro «bocciate».
* **Misura:** R medio a trade di ogni gruppo e differenza passate − bocciate; margine = 2 errori
  standard, il più largo fra quello calcolato per data (26 differenze) e quello trade per trade.
* **Esiti:** almeno 80 trade delle passate nei 14 giorni dopo, altrimenti «non si sa». Differenza
  oltre il margine → **il gate ha un vantaggio vero** (il problema è il mercato o il bot). Differenza +
  margine sotto 0,10R → **il gate sceglie soprattutto fortuna** (la prossima modifica va nel gate).
  Altrimenti → **non si sa**.
* **Solo informativo, non decide:** le coppie che passano a D, D − 7 e D − 14 giorni (come le
  validate a 3 conferme), se il calcolo lo permette.
* **Limiti dichiarati:** monete di oggi (le sopravvissute), motore senza scivolamento, niente AI:
  alzano il livello di tutti, pesano poco sul confronto fra passate e bocciate. Non è il gate di
  produzione: la vita del registro (finestre, declassate, purga) non c'è.
* **Come gira:** prima una prova piccola (1-2 date), si controlla che i numeri abbiano senso, poi il
  resto nelle pause del gate (mai insieme al giro, la memoria non basta). Due righe nuove nella lista
  bianca della VPS, da aggiungere a mano dal proprietario.

### 1 ottobre, pomeriggio: stop giornaliero (H3) e freno di serie (H4) rigiocati — restano parcheggiati

Domanda del proprietario: avrebbero avuto senso? Rigioco dei trade veri del paper (`trades`, ops 0404,
trade delle validate, −81,11 USDT) e del portafoglio del motore sulle 208 validate di oggi, 60 giorni
(`portafoglio`, ops 0405), una regola alla volta. **Paper:** stop 2% +5,09 · stop 3% +2,00 · serie 4
della strategia +0,49 · serie 3 della strategia +2,61 · serie 4 del bot +9,28 · serie 3 del bot +15,62
(drawdown da 8,11% a 6,56%). **Gate:** stop 2% −17.456 (drawdown da 11,74% a 17,02%) · stop 3% −11.615
(20,31%) · serie 4 della strategia −116 · serie 3 −2.227 · serie 4 del conto −2.416 · serie 3 del conto
−3.957. Lettura: sul paper ogni riduzione aiuta perché il paper perde (meno esposizione a un sistema in
perdita, non un vantaggio delle regole); sul portafoglio del gate, che guadagna, tolgono soprattutto i
rimbalzi. Il win rate dopo 4 perdite di fila non cambia (62,5% su 8 contro 68,2%, t −0,34, ops 0387).
Limite: il portafoglio del gate usa coppie scelte anche su quei giorni (livello ottimista); conta la
differenza fra le righe. Nessuna regola cambia: H3 e H4 restano parcheggiate.
**R1, lo strumento (1 ott, pomeriggio):** `scripts/replay_gate.py`, test in `tests/test_replay_gate.py`
(suite 2138 verdi). Usa il verdetto del gate di produzione (`evaluate_spec`) con scale e keep fissi
(niente dal paper), candele caricate fino a oggi e tagliate in memoria, 0 letture e 0 scritture
Firebase, registro non toccato; scrive solo `data/replay_gate/`. 50 candidate per data (non 100: la
misura in locale dava 22-28 ore con 100), 4 processi (misurati ~2,3 GB ciascuno). Ogni lancio lavora
al massimo 2,5 ore nelle pause del gate e il successivo riprende; il primo fa solo 2 date (prova
piccola). Stima totale (da una misura in locale, non sulla VPS): circa 20-25 ore di calcolo con 4
processi, quindi più lanci. Limite in più rispetto alla regola: il costo del funding usa la media
dell'ultimo periodo, anche dopo la data. Righe della lista bianca: `replay-gate`, `replay-gate-esito`.

### 1 ottobre, sera: «le funzioni servono?» — verifica e misura (punto 3 della richiesta)

Verifica in sola lettura su ops 0386-0405. Quasi ogni funzione ha un CONTATORE (quante volte
scatta), poche un confronto d'ESITO. **Misurate e non servono:** selettore (0/3 finestre, ops 0396;
correlazione p/esito +0,063 su 130 trade, 0403), freno per gruppo (dopo il freno globale in 6 pool su 7,
0288), freno di serie (0387, 0404-0405). **Misurata e serve, ma sul motore:** tetto per direzione (PnL
+48.444 → +56.445, drawdown 11,74% → 10,75%, 0387); nel paper non è mai scattato. **Troppo presto:**
declassate (3 ott), esplorative (100 trade), varianti e intorno (0 promosse), cooldown e una per coin
(segno a favore dentro il margine), voto t, fuori campione, sessione, passata a 1 ora, conferma a
maggioranza. **Non misurate fino a oggi:** freno globale, panchina dei pesi, pesi→leva (K9), tilt,
keep e scala per coppia, idee e autopsia AI, ombra AI, esplorative in R, rischio vero delle declassate.
**Fatto:** `bot/learning/contributi.py` (regola dei verdetti scritta prima dei numeri: meno di 10 trade
per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso
opposto «va contro»; altrimenti «non si vede ancora») e la sezione «LE FUNZIONI SERVONO?» nel report
`trades`: freno globale, panchina, pesi alti, leva > 1, tilt, declassate (anche rischio effettivo
medio e USDT), esplorative, ombra AI (vetati contro accordi, legati per id), R per origine della
strategia. Restano da misurare: keep e scala per coppia (rigioco degli stessi trade con i valori di
default), autopsia AI (giri alterni), conferma a maggioranza (autopsia-validate settimanale).
**Prima lettura (ops 0409, 18:xx ora italiana):** nessuna funzione ha ancora un verdetto oltre il
margine. Freno globale: frena trade a −0,093R contro −0,173R dei non frenati (non si vede), ma in USDT
ha risparmiato +12,90 su 48 trade. Declassate: −0,101R contro −0,123R (non si vede), +20,24 USDT
risparmiati; rischio effettivo medio 0,12% contro 0,21% (il quarto agisce, a metà: K5). Pesi alti
−0,083R contro −0,326R; leva > 1 −0,020R contro −0,138R (segno giusto, dentro il margine). Tilt: zero
differenza. Ombra AI: i trade che avrebbe vetato −0,100R (85) contro +0,226R (27) dove era d'accordo,
diff −0,326 ±0,360 — vicino al margine, a favore dell'AI. Origine: tutti i 164 trade da strategie
casuali o mutate (nessun trade da un'idea AI, una variante o l'intorno).

### 1 ottobre, pomeriggio: stella polare, backlog in dashboard (J2), report giornaliero

Richiesta del proprietario in 5 punti, uno alla volta.
1. **Stella polare** in CLAUDE.md: oltre a massimizzare i profitti, ogni giorno il sistema deve
   essere un passo più vicino, anche in ciò che abbiamo CAPITO; ogni azione risponde a «cosa ci
   avvicina?» e «cosa abbiamo capito oggi?»; una funzione senza misura del contributo non è utile.
2. **J2:** `bot/learning/backlog_doc.py` legge `docs/backlog.md` (nuovo gruppo 0 «Aspettano il tuo
   sì»), `scripts/report_giornaliero.py --pubblica` lo scrive in `dashboard/backlog` e `/backlog`
   dopo ogni giro del gate (lanciato dalla discovery in un processo a parte, 10 minuti al massimo).
   Riquadro «Aspettano il tuo sì» nella scheda Controllo. Nessuna copia da aggiornare a mano.
3. **Le funzioni servono?** (vedi la sezione di stasera sopra).
5. **Report giornaliero:** `bot/learning/report.py`, nove sezioni FISSE (in breve; il paper ieri;
   come va il gate; cosa ci dicono i dati — ingressi, uscite e trailing, stop, rischio, direzione;
   le funzioni servono?; cosa abbiamo capito; cosa è cambiato nel sistema; aspetta il tuo sì e
   prossime letture; salute e costi), pubblicato dopo ogni giro del gate in
   `dashboard/report_giornaliero`, `/report_giornaliero` e `report_giornaliero/{giorno}` (storia).
   Prima scheda della dashboard («Report»). Fonti nuove: `docs/capito.md` (cosa abbiamo capito,
   scritto ogni mattina dal controllo) e `docs/letture.md` (il calendario delle letture). Letture
   Firestore in più: ~1.700 al giorno (stima, quota 50.000). La routine del mattino segue la stessa
   struttura, scrive `docs/capito.md` e mette le proposte nel gruppo 0 del backlog. Non verificato
   ancora sulla macchina: la prima pubblicazione arriva alla fine del prossimo giro del gate; la
   riga `report-giornaliero` per ripubblicare subito va aggiunta a mano alla lista bianca.

### 1 ottobre, sera: i dati che non raccoglievamo (punto 4) — scritti, attendono il riavvio

Verifica in sola lettura del codice, poi implementazione di 12 dati nuovi (backlog D8), SOLO
raccolta: nessuna decisione di trading cambia. Prova: `tests/test_dati_parita.py` confronta il motore
di prima e di dopo su dati fissi e 20 trade paper scriptati (aperture, uscite, PnL, gradini, equity
identici). Suite 2240 verdi, due volte di fila. Nuovi campi del trade: `versione`, `promessa_gate`,
`trailing_verdict_gate`, `post_exit_*`, `motore_*`, `lock_armed_at_s`, `stop_moves`, `t_mae_s`,
`mae_before_tp1_r`, `close_segnale`, `ingresso_vs_segnale_r`, `snapshot_ts`, `open_interest_at_entry`,
`regime_globale_at_entry`; per avvio `/avvii_config`; per giorno `giorni/{data}`; nel motore
`SimTrade.exit_reason`; storia del gate in `data/gate_storia/`. Nota: `entry_slippage_pct` ora
confronta l'ingresso con la chiusura del segnale (prima era sempre 0); è solo un campo registrato.
Letture Firestore in più: nessuna; scritture: ~1 per trade chiuso in più e 1 al giorno (stima). Non
verificato sulla macchina: arriva col riavvio del bot (punti 1-10) e col prossimo giro (11-12).

### 1 ottobre, sera: R1 al posto di un giro del gate al giorno (sì del proprietario)

Il primo lancio di R1 (13:49) ha aspettato 4 ore senza trovare una pausa: ogni giro del gate dura
~3 ore e il timer scatta ogni 3 ore (ops 0410-0411). Insieme non stanno in memoria: col gate in corso
10 GB occupati su 15, 4 liberi, 6 processi al 100% (ops 0412-0413); R1 con 2 processi ne chiede ~4,6
(stima). Deciso dal proprietario: «procedi con R1 al posto di un giro del gate al giorno». Fatto:
`bot/core/finestra_r1.py` — finché esiste `data/replay_gate/attivo` (lo crea R1 al lancio e lo toglie
quando le 26 date sono fatte) il giro delle 12:00 UTC (14:00 italiane) di optimize e discovery esce
subito con la riga «[gate] giro delle 12:00 UTC SALTATO»; R1 conta come prossimo giro quello delle 15
UTC, aspetta fino a 8 ore (lanciato dal controllo del mattino), e nell'ora saltata ricontrolla dopo 20 s
un gate «in corso» (il servizio parte ed esce subito; un giro delle 09 che sfora resta un giro vero).
Il giro completo di notte resta. Cosa si perde: ~1/8 delle candidate nuove al giorno e 3 ore di
ritardo per le ipotesi urgenti una volta al giorno, per ~6-8 giorni (stima). Spegnimento a mano:
cancellare il file `attivo` o `R1_SALTA_GIRO=0`. Possibile effetto collaterale: l'anomalia
GATE_IN_RITARDO può diventare gialla nel pomeriggio (6 ore fra due giri). Prima lettura completa di R1
stimata verso il 9 ottobre.

### 2 ottobre, mattina: T2, la curva del vantaggio del segnale — REGOLA scritta PRIMA dei numeri

Sì del proprietario («fai la misura del punto 1… la mia idea alla fine è operare più come un quant»).
Domanda: i segnali delle strategie hanno un vantaggio sul caso, e per quanto tempo dura?
* **Campione pulito (decide):** i trade VERI del paper (mai usati per scegliere niente), ingresso e
  verso registrati. Per ognuno, il movimento del prezzo dopo 1, 4, 12 e 24 ore dall'ingresso (4, 16,
  48, 96 candele da 15 minuti), col segno della direzione, misurato in «mosse tipiche di 24 ore»
  della moneta (calcolate sui 30 giorni PRIMA dell'ingresso, senza guardare avanti).
* **Confronto:** ingressi a caso sulla stessa moneta negli stessi giorni (stessa direzione), stessa
  misura. Vantaggio = media dei segnali − media del caso, a ogni durata.
* **Margine:** intervallo al 95% con ricampionamento a blocchi di giornate (i trade dello stesso giorno
  non sono indipendenti).
* **Esiti:** se a TUTTE le durate il vantaggio sta dentro il margine → «nessun vantaggio misurabile»:
  il lavoro sui TP si ferma, il problema è l'ingresso (o il gate: R1). Se a qualche durata è sopra il
  margine → «c'è un vantaggio»: il TP va dove la curva smette di salire, e si passa a T1 dopo le
  letture del 7-14 ott. Se è sotto il margine → «i segnali fanno peggio del caso»: lo si dice per primo.
* **Solo informativo, non decide:** la stessa curva sui segnali del motore delle coppie validate negli
  ultimi giorni (scelte anche su quei giorni: misura ottimista).
* Limiti dichiarati: il paper ha ~220 trade su ~16 giorni di un solo mercato; le uscite di oggi non
  toccano la misura (si guarda il prezzo, non il trade).
**T2, come la regola si applica (scritto PRIMA del primo lancio sui dati veri, revisione del 2 ott):**
«ingressi a caso negli stessi giorni» = nelle 12 ore DOPO il segnale, non prima: la direzione del
segnale è decisa coi prezzi fino al segnale, e un ingresso a caso precedente con quella direzione
conoscerebbe il proprio futuro (su prezzi a caso, con la direzione che segue le ultime 4 ore, il caso a
±12 ore dava «peggio del caso» 100 volte su 100). «Dove la curva smette di salire» = dalla prima durata
col margine sopra lo 0, la prima dopo cui il passo successivo non sale oltre il margine. Limite noto:
su prezzi a caso la regola dice «nessun vantaggio» ~75-81 volte su 100 (4 durate, 16 giornate): un
esito a una sola durata va letto con cautela. Corretto anche un difetto che toccava la tabella dei TP
del 2 ott (ops 0419): la lettura della cache prendeva i file corti scritti dalla sezione A5 invece della
storia del gate (HEMI 601 ingressi invece di 8640, SYRUP 1653).

### 2 ottobre, mattina: i costi per trade contro Binance (richiesta del proprietario)

Verifica in sola lettura, poi un secondo revisore ha ricontrollato codice, tariffe e conti. Commissioni:
0,08% andata e ritorno nel modello contro 0,10% di Binance USDⓈ-M base da taker (0,05% a lato; 0,09%
con lo sconto BNB): +4,77 USDT sui 222 trade del paper, ~+0,012R a trade (`docs/state.md` del 2 ott
05:37 UTC: costi 33,21 = commissioni 19,07 + spread 14,16 + funding −0,01). Funding: il tasso per
scadenza è trattato come «per 8 ore», ma molte monete piccole scadono ogni 4 ore e quelle al limite ogni
ora (Binance, dal 2 mag 2025): sottostima ×2/×8 dove conta. Stop senza scivolamento (K8). Spread:
quattro fasce misurate una volta, a mercato calmo. Gate e paper allineati fra loro (stessa variabile,
stesso `costs.py`), salvo la finestra di volume dello spread e la fonte del funding. Nota del
revisore: l'ingresso vero sarebbe un ordine limite (in parte «maker», più economico), ma il paper
riempie sempre subito: 0,10% è l'unico valore coerente con come riempie il paper. Proposta in backlog
C5 (aspetta il sì): correggere dopo le letture del 14 ott, bot e gate insieme.

### 2 ottobre, mattina: T2, primo esito — NESSUN VANTAGGIO MISURABILE (ops 0437)

Con la regola scritta prima dei numeri: 201 trade del paper misurati su 15 giornate (23 saltati: 7
senza candela chiusa subito prima, 16 col futuro oltre i dati), 20 ingressi a caso per segnale nelle 12
ore DOPO. Vantaggio sul caso, in mosse tipiche di 24 ore: 1 ora −0,080 [−0,205; +0,029] · 4 ore −0,001
[−0,129; +0,127] · 12 ore +0,026 [−0,217; +0,253] · 24 ore −0,068 [−0,341; +0,179]; in %: −0,25 · +0,04
· −0,07 · −0,27. Tutte le durate dentro il margine: **«nessun vantaggio misurabile»**. Per la regola il
lavoro sui TP si ferma (T1 congelata): il problema è l'ingresso o il gate (R1 lo dirà). Per verso
(informativo): long e short entrambi dentro il margine. Limite: 15 giornate di un solo mercato; su
prezzi a caso la regola dà «nessun vantaggio» ~3 volte su 4 anche quando il vantaggio manca davvero, e
non dice quanto piccolo potrebbe essere un vantaggio vero (il margine a 4 ore è ±0,13 mosse tipiche,
cioè circa ±0,5%).

### Controllo del 2 ottobre (mattina)

**Da guardare per primo: un giro del gate è durato 3 h 04 (anomalia gialla GATE_SFORA, «gate lento»).** L'avviso
è nel controllo orario delle 07:30, ristampato in coda al report nel log del gate alle 07:50 (ops 0425, 0435). Non è
l'ultimo giro (solo urgenti, 05:47-07:50, 2 h 03, ops 0423): l'avviso legge la durata dell'ultimo giro *finito*, e
durante un giro il documento del gate tiene quella del precedente (codice di controllo.py e discover_strategies.py).
Probabilmente è il completo di stanotte: il report scrive «intorno 7 madri», un dato che i giri urgenti ricopiano dal
completo (ieri il completo ne aveva 3, ops 0391), e le declassate sono cambiate stanotte (+2 −1, ops 0432). L'ora di
fine non è nei file: non verificato. Semafori giallo/giallo con 3 anomalie, una di sistema, in tutti i controlli
orari visibili dalle 04:29 alle 07:30 (il log parte alle 04:13, ops 0424); SISTEMA verde alle 08:17 (ops 0432).
Nessun errore nelle righe di log lette. Letture Firestore 4.016 in ~14 ore dal riavvio (ops 0424). Spazio per ~1.289
coppie (ops 0423). Spesa AI del 1 ott 2,07 $ in 31 chiamate (ops 0422). **Numeri:** 224 trade, 55%
vinti, −77,22 USDT, equity 922,78, DRY_RUN True (ops 0421). Il 1 ott −9,57 (motore −3.570,11, secondo
giorno peggiore su 60, ops 0429). Fino al 1 ott 5 giorni in utile e 11 in perdita (calcolo mio). BTC
+13,56% contro il nostro −7,72%. In R dal 27 set: −0,065 netti su 81 (ieri +0,042 su 61), +0,013 lordi
(ieri +0,118), costi 0,078 (ops 0420, 0388). Long −0,171 su 43, short +0,056 su 38, regime neutro
−0,317 su 39. Dei 20 trade nuovi, i 15 delle declassate fanno −8,12R e i 5 delle attive +0,35R (calcolo mio).
**Fuori campione** (anteprima, ops 0429): «Selezione: la promessa non regge dopo la validazione:
motore -0.03R (margine ±0.21R per giornata) su 106 segnali … Per la regola la prossima modifica va nel gate»
(ieri +0,06 su 89, ops 0387). Esecuzione: «non si decide», +0,03 ±0,13 su 95. H1: 20 e 78 segnali, «non si sa ancora».
Regola del 3 ott in anteprima: declassate −0,127R su 52 contro attive +0,047R su 29, differenza −0,174 ±0,389, NON SI
DECIDE (ops 0420). **T2** (ops 0437): «nessun vantaggio misurabile» a 1, 4, 12 e 24 ore; T1 congelata. Validate 212 su
71 coin (+4), declassate 163, 665 a 2/3, t ≥ 2 per 39 su 57. Le strategie AI hanno 0 validate su 103 nel registro
(ops 0423). Trailing: 49 protetti su 87 (56,3%), ne mancano 8 (ops 0432). Selettore NON BATTE «apri tutto», 0/3
finestre (ops 0428); la sua soglia è passata a 0,50, pubblicata dalla stessa ops 0428. R1: 0 date su 26, 85 unità su
5.200, rilanciato alle 08:17 (ops 0433-0434). Restano ~45,8 ore di lavoro (stima in ops 0433): a 2,5 ore al giorno
servirebbero ~18 giorni (calcolo mio), quindi la lettura del 9 ott non sembra raggiungibile. Report giornaliero
pubblicato con 9 sezioni (ops 0435). Difetti veri: testo del fuori campione troncato (taglio a 400 caratteri) e D8
«attende il riavvio» (il titolo in backlog.md non è aggiornato). Numeri che sembrano sbagliati ma misurano altro:
«registro 1421» = coppie nel tetto (1 base + 1.420 con conferme), non le 1.761 totali; «intorno 7» = ultimo giro
completo; trailing 110 contro 108, probabilmente gruppi di trade diversi (non verificato). Salute, 6 posizioni ed equity
924,91 vengono dal controllo delle 07:30. Il riquadro «aspetta il sì» ha letto il backlog della versione 3377efb (08:04),
prima del commit di C5 (08:13). **Proposta del giorno (serve il sì): C5.** Commissioni a 0,10% e funding con la scadenza
vera, nel bot e nel gate insieme, dopo le letture del 14 ott (+0,012R di costi a trade, stima).
**R1, tempi:** l'avanzamento vero (ops 0433: 85 unità su 5.200, 129 s a unità, ~45,8 ore rimaste con 4
processi) sposta la prima lettura completa verso il 20 ott a 2,5 ore al giorno (stima). La stima del 1 ott
(13-17 ore) contava 120-150 monete; il piano ne ha 200. Proposta al proprietario: limitare R1 alle monete
che il bot opera davvero (71), circa 3 volte più veloce. Corretti nel report: taglio del testo del
fuori campione a fine parola, titolo di D8.


### 2 ottobre: sì a C5 (dopo il 14 ott) e R1 sulle sole monete operate

Sì del proprietario: «sì C5, e limita R1 alle 71 monete». **C5** va nel gruppo «dopo le letture»: commissioni
0,10% e funding con la scadenza vera, nel bot e nel gate insieme, dopo il 14 ott, con la data scritta e il
controllo del campo `versione` dei trade. **R1**: al prossimo lancio il piano si restringe UNA volta alle
monete delle coppie validate (una lettura del registro; `restringi_alle_operate` in
`scripts/replay_gate.py`). Date, semi e candidate restano; le unità già fatte di quelle monete restano, le
altre stanno su disco ma non entrano nella lettura. La regola di R1 non cambia (scritta prima dei numeri,
nessuna lettura ancora fatta); cambia solo l'insieme delle monete: «le monete che il bot opera» invece di
«le prime 200 per volume». Stima: ~1/3 del lavoro, prima lettura verso il 9-10 ott (stima, da misurare).

### 2 ottobre, 14:45: prima finestra di R1 — il gate ha saltato il giro, R1 lavora; 0 passate finora

Il giro delle 12 UTC è stato saltato alle 12:09 UTC (optimize e discovery, ops 0440); il giro delle 09
UTC era finito alle 11:13. R1 lavora con 4 processi: memoria 7 GB usati su 15, 7 liberi (ops 0441), nessun
errore. Avanzamento (ops 0439, piano ancora a 200 monete: la restrizione alle operate parte dal prossimo
lancio): 1 data completa su 26 e una in corso, 358 unità su 5.200, 110 s a unità. **Prova piccola, i
numeri hanno senso a metà:** 14.150 candidate giudicate, 570.092 trade dopo la data delle bocciate a
−0,11R (plausibile: strategie a caso che pagano i costi), ma **0 passate** (bocciate soprattutto su
total_return 12.622). Senza passate la regola non può leggere niente («ne servono 80» trade). Da guardare
nei prossimi giorni: se dopo ~5 date le passate restano ~0, R1 finirà «non si sa» per costruzione, e
servirà più candidate per data (più tempo) o le candidate che il gate ha già visto passare (da decidere
col proprietario, PRIMA di guardare il risultato). Che il giro delle 15 UTC riparta è da verificare nel
controllo di domani.
**R1, punto di verifica fissato (2 ott, 16:xx, sì del proprietario), scritto PRIMA dei numeri:** dopo 5
date complete (circa 2 giorni con le 71 monete) si contano le promosse. Se sono meno di 10, il piano
cambia (più candidate per data, oppure anche le strategie che il gate vero ha già visto passare): la scelta
si fa allora, ma il criterio è questo. Se sono abbastanza, si va fino in fondo. Domani si verifica se lo
0 su 14.150 (ops 0439: bocciate per criterio total_return 12.622, trades 706, recovery 486) è plausibile
per candidate casuali nuove o un difetto di R1 (storia minima alle date vecchie, severità dell'holdout).
Fino ad allora R1 resta com'è (un giro del gate al giorno, 4 processi).

### 2 ottobre, sera: affollamento misurato; idee AI e varianti dai referti SPENTE (decisione del proprietario)

Alle 20:47 il bot ha aperto 10 long in 20 secondi (ops 0442-0443): in parità apre tutti i segnali validi
del ciclo, il tetto di 5 posizioni è spento e il tetto per direzione (3% in rischio) con le puntate ridotte
(freno ×0,5, declassate ×0,25) ammetteva 1,55%; il filtro di correlazione ha fermato solo RSR. Non è un
guasto, è il rischio «un'unica scommessa sul mercato» (I6). **Fatto:** sezione «AFFOLLAMENTO» nel
report `trades` (posizioni nello stesso verso all'ingresso, per fascia 1-2 / 3-5 / 6+ con n, vinti, PnL, R
medio; e le «ondate» di 6+ aperture entro 5 minuti). Solo misura: si decide dopo le letture del 7-14 ott.
**Spente** (sì del proprietario, «se pensi che non diano valore»): le idee dell'AI con l'autopsia
(`AI_HYPOTHESES_ENABLED=false`: 0 validate su 103 spec AI, ops 0423; ~2,1 $ al giorno fra idee 1,54 e
autopsia 0,56, ops 0390) e le varianti dai referti (`DISCOVERY_VARIANTI_REFERTI=false`: 0 promosse da
quando esistono, ops 0391/0423; e il taglio di pre-registrazione era spento, B8). Restano: le ipotesi dei
referti scritte nella storia (J9), la corsia urgente `scala_stretta` (I4/I4bis), il contatore ORIGINI.
Partono dal prossimo giro del gate (nessun riavvio). Spesa AI attesa: ~0 $ al giorno sulla VPS. Si
riaccendono quando ci sarà un vantaggio misurato su cui lavorare, o se R1 dice che il gate sceglie bene.

### Controllo del 3 ottobre (mattina)

Nessun guasto: bot vivo, controllo del bot 30 min prima (ops 0457), letture Firestore 6.832/24 h (ops 0449), spazio per ~1.157 coppie (ops 0448), ultimo giro 1 h 56 (ops 0448; il log dice 2 h 57, ops 0450, scarto non spiegato), nessun errore nelle righe lette. Le righe «SPENTE» non sono nelle 80 righe lette (ops 0450); prova indiretta: varianti 0 create, idee AI nuove 0 (ops 0448), chiamate AI oggi 0 (ops 0447); spesa di ieri 1,86 $ in 29 chiamate, tutte prima dello spegnimento (ultima 20:18). **Numeri:** 246 trade, 56%, −73,68 USDT, equity 929,04, DRY_RUN True (ops 0446). Il 2 ott 23 trade +3,48 USDT, −0,168R a trade (ops 0460); 7 giorni in utile / 11 in perdita (ops 0454). Dal 27 set −0,048R netti su 103, +0,030 lordi, costi 0,078 (ops 0445); sul totale lordo −37,93 e costi 35,76 (ops 0446). Regime neutro −0,219R su 53. Stop: 51 su 107 ingressi sbagliati dall'inizio (ops 0451). **Lettura ufficiale del 3 ott (declassate contro attive): NON SI DECIDE** — −0,131R su 70 contro +0,127R su 33, differenza −0,258R, margine ±0,458R (ops 0445); riga aggiornata in letture.md. **Stella polare:** motore post-validazione −0,03R su 130 ±0,18 (ops 0454; ieri −0,03 su 106 ±0,21). **R1:** piano ancora a 200 monete (il lancio di ieri 08:17 precede il commit 5d66c09 delle 09:33); ieri ha lavorato le sue 2,5 ore di budget (315 unità) e si è fermato alle 15:04; rilanciato 08:19 (ops 0458-0459). 2 date su 26 (17 e 3 set), 400 unità, 0 passate su 16.000. Plausibilità: il gate vero passa 44/22.632 = 0,19% di un mix di 92 strategie (39 casuali, 28 mutazioni, 25 rivalutate; ops 0448/0450), senza divisione delle 44 per origine → attese ~31 solo se le casuali passassero come la media; osservate 0 → **sospetto, non dimostrato**; le date complete sono recenti, quindi non è storia corta; proposta R2 (stesse candidate nel gate vero) in backlog gruppo 0. **Ondata delle 20:47:** riga stampata «8 aperture PnL +4.27» = le 8 chiuse delle 10 (ops 0445/0443), DOT e BMT aperte (ops 0446); ARC, HOME, GPS, UB chiuse fuori dalla finestra del log (ops 0449). Fascia 6+ 11 trade +0,026R. Difetto: ora UTC con etichetta «italiana» (`trade_stats.py:1146-1147`, `astimezone()` sulla VPS in UTC). Rifiuti 23 nelle 24 h (ieri 12, ops 0455/0430): 7 ri-segnali sulle coin dell'ondata e 3 correlazioni causate da essa. Validate 216/72 coin, declassate 173, prima validata AI (1/113), t ≥ 2 per 42 su 61 (ieri 39 su 57) (ops 0448). Nessuna validata né trade a 1 ora trovati (ops 0448/0445). Trailing: 51 protetti su 95 (53,7%), ne mancano 15 (ops 0457). Selettore piatto: correlazione +0,003 su 166 (ops 0445). T2 su 207 trade: ancora dentro il margine (ops 0451). Funzioni: tutte «non si vede ancora» (ops 0445). Report giornaliero pubblicato, versione 2363f87 (ops 0460); difetto: riga di letture.md «R1 dal 2 ott sulle operate» anticipata. Un secondo riavvio del bot il 2 ott (pid 1975598 → 2005927, ops 0424/0443; «riavvii 1», ops 0460), ora non nei file, stima ~08:20 dal pid vicino a quello di R1.

### 3 ottobre, mattina: R2 scritta (sì del proprietario)

R2 vive dentro `scripts/replay_gate.py`: all'inizio del primo lancio che la trova non fatta, PRIMA delle
unità di R1, le stesse 50 candidate del 17 set (seme della data) vengono giudicate dal gate di produzione
con tutte le candele fino a oggi, sulle monete del piano, una moneta per file in `data/replay_gate/r2/`;
niente registro, niente Firebase. Regola (scritta prima dei numeri): ≥ 3 passate → R1 è più severo del
gate, si ferma da solo (file «attivo» tolto, il gate torna a 8 giri) finché non è corretto; 0-1 → lo 0 di
R1 è vero e scatta il cambio di piano del 2 ott (lo decide il proprietario); 2 → non si decide.
`replay-gate-esito` stampa R2 prima di R1. Il lancio di oggi (08:19) gira col codice di prima: R2 parte
col lancio del 4 ott (finestra delle 14:00, ~30-35 min stimati su 72 monete), esito verso le 14:45.

### Controllo del 4 ottobre (mattina)

**Prima di tutto.** Il giro del gate finito alle 07:38 è durato 3 h 09 (anomalia GATE_SFORA, ops 0470): il servizio era partito verso le 04:29 e il giro successivo è partito alle 08:04, subito dopo; la discovery a 15 minuti ne ha usate 1 h 45 e la passata a 1 ora 9 minuti (ops 0468), il resto del tempo non è nei file letti. I giri sono ormai attaccati l'uno all'altro: è anche il motivo per cui il lancio di R1 di ieri mattina (08:19) ha trovato uno spazio di pochi minuti verso le 10:10, è partito e si è fermato alle 10:13 senza unità nuove (ops 0463), e alle 14:05 il gate ha saltato il suo giro con R1 fermo (ops 0464). Stamattina NON ho messo in coda `replay-gate`: un lancio delle 08:xx rifarebbe lo stesso giro a vuoto; il lancio è programmato alle 13:10 (promemoria della sessione), così parte nella finestra delle 14:00, con R2 all'inizio.

**Numeri.** 264 trade, 57% vinti, −62,59 USDT (lordo −24,56, costi 38,03), equity 937,41, DRY_RUN True, 3 aperte con rischio 0,62% (ops 0466); massimo 12 posizioni insieme (ops 0465). Il 3 ott: 17 trade +18,85 USDT sul conto, 16 delle validate con 15 vinti e +0,869R a trade (ops 0479). Giornate complete dal 16 set: 7 in utile, 11 in perdita; oggi fin qui −4,38 (ops 0474). BTC dal primo giorno +12,1%, noi −6,3% (ops 0477). Dal 27 set +0,015R netti su 119, lordi +0,097, costi 0,082 (ops 0465; ieri −0,048 su 103). Direzione: long −0,143R su 104, short +0,008 su 111; dal 27 set long −0,073 su 69, short +0,137 su 50; regime neutro −0,108R su 64 dal 27 set (ops 0465). Stop: 52 su 111 sbagliati dall'inizio, 58 morti sotto il primo gradino (ops 0471).

**Stella polare:** motore dopo la validazione **+0,006R su 156 segnali ±0,17** (ops 0474; ieri −0,03 su 130 ±0,18); stessi segnali motore +0,02R, paper −0,009R, differenza +0,03 ±0,10. Lettura stampata: nessun verdetto contro il gate, esecuzione non si decide; si legge il 7 e il 14 ott. Declassate dal 27 set: −0,058R su 84 contro attive +0,190R su 35, differenza −0,247 ±0,480 → non si decide (ops 0465; la lettura ufficiale era ieri). H1: 31 e 107 segnali, ne servono 80 per gruppo (ops 0474).

**Gate.** Validate 223 su 76 coin, copertura 38%, declassate 169, 747 coppie a 2/3, spazio per ~1.021 coppie, t ≥ 2 per 48 su 71 (ieri 42 su 61) (ops 0468). Ultimo giro 20.667 valutazioni, 25 passate; passata a 1 ora 9.840 valutazioni, 218 passate (ops 0468). Nessuna validata e nessun trade a 1 ora ancora (attese dall'8 ott). Righe «idee AI e autopsia SPENTE» e «varianti dai referti SPENTE» presenti, varianti 0 create (ops 0470). Selettore: NON BATTE 0/3 (ops 0473); in ombra correlazione +0,002 su 182 (ops 0465).

**R1:** fermo dalle 10:13 di ieri, 2 date su 26, 144 unità su 1.872 (piano a 72 monete), 0 promosse; R2 non ancora fatta (ops 0478). Il punto di verifica a 5 date non è raggiunto.

**Funzioni:** primo «contribuisce», il paper esplorativo (10 trade +0,385R contro −0,065R delle validate, +0,450 ±0,419); tutte le altre «non si vede ancora» o «campione piccolo» (ops 0465). T2 su 240 trade: nessun vantaggio misurabile, a 1 ora −0,080 [−0,184; +0,013] (ops 0471). Trailing: 55 protetti su 104 (52,9%), ne mancano 19 per la proposta (ops 0477). Rifiutati: «posizione aperta» +0,01R contro aperti −0,03R su 73 (margine ±0,27, solo informazione; i rifiutati non hanno costi) (ops 0476).

**Salute e costi.** Bot vivo, battito 30 s, controllo orario regolare (ops 0477); letture Firestore 7.763 nelle 24 h (ops 0469); nessun errore nelle righe lette; spesa AI di ieri: nessuna chiamata (ops 0467). Report giornaliero ripubblicato alle 08:20, versione 2966a58 (ops 0479).

**Proposta del giorno:** G7, il gate sul prezzo casuale (gruppo 0 del backlog): quante candidate passa il gate su prezzi rimescolati, a 1 ora e a 15 minuti, contro le quote vere (2,2% e 0,12%). Aspetta il sì.

**In parallelo (solo analisi, niente nel sistema):** il proprietario sta rivedendo una proposta di protocollo di ricerca per moneta con vault 2024-2026 (versione 2 in PDF, consegnata il 3 ott, non nel repo).

### 4 ottobre, mattina: G7 scritta (sì del proprietario)

Il proprietario ha detto «sì G7, procedi». Scrivendola ho visto un difetto della proposta, corretto PRIMA di
qualunque numero: la quota a 1 ora del giro vero (2,2%) contiene soprattutto spec già note a 1 ora (259 su 328
nella riga ORIGINI, ops 0468), cioè coppie che erano già passate; quella a 15 minuti (0,12%) è quasi tutta di
candidate nuove. Il «diciotto volte» del controllo di stamattina era soprattutto composizione (corretto in
capito.md). Quindi G7 confronta a parità di tutto: 100 candidate NUOVE (generatore del gate, seme 20261004)
sulle 72 monete del piano di R1, giudicate dal gate di produzione a 1 ora sulle candele vere e sulle stesse
candele rimescolate candela per candela (forma e volume di ogni candela uguali, ordine casuale; stesso inizio e
stessa fine). Il rimescolamento a blocchi di un giorno è stato scartato: dentro il giorno terrebbe gli schemi
veri. **Regola (scritta prima dei numeri):** quota sul caso ≥ metà di quella vera → a 1 ora il gate passa
soprattutto rumore (la prossima modifica va nelle soglie del gate, con R1); ≤ un quinto → il gate filtra il
rumore (il problema del paper è altrove); in mezzo → non si sa; meno di 10 passate sulle candele vere → non si
sa. Codice: `scripts/gate_sul_caso.py`, dentro il lancio di R1 dopo R2 e prima delle unità di R1, solo file in
`data/replay_gate/g7/1h/`; esito in `replay-gate-esito`. Misurato in locale su candele finte: ~30 s per unità
di 100 candidate, 144 unità → ~20 min con 4 worker (stima). Nessuna riga nuova nella lista bianca. Gira nel
lancio delle 13:10. Due test di R1 legati alla data (serie finta ferma al 1 ott, «delistata» da oggi) sistemati;
suite: 2282 passati.

### Referto settimanale del 4 ottobre (09:30 ora italiana)

Fonti: ops 0481-0482 (confronto, servizi delle 09:19) e il controllo delle 08:00 (ops 0465-0479) per trades,
mfe, gate, ai-stato, log-gate, rifiuti.
1. **Quanto e come.** Settimana 28 set-4 ott: 119 trade delle validate (21+23+14+15+23+16+7 per giorno, ops
   0465), **+14,09 USDT** sul conto (colonna paper del periodo, ops 0474): la prima settimana in utile. Totale:
   264 trade, −62,59 USDT, equity 937,41, DRY_RUN True, costi 38,03 su un lordo di −24,56 (ops 0466).
2. **Il lock taglia vincitori?** Verdetti del trailing a 15 minuti: 104 = 49 prematuri + 55 protetti (ops
   0477); il 27 set 30 = 11 + 19. Nella settimana quindi 38 prematuri contro 36 protetti: **la prima settimana
   con i prematuri sopra**, di 2. La regola chiede due settimane di fila prima di proporre: si riguarda domenica
   prossima. Stop: 51 su 144 nei 7 giorni (ops 0479).
3. **Come muoiono gli stop.** 111 stop: 52 ingresso, 58 uscita, 1 protezione (ops 0471); il 27 set 58: 23 /
   34 / 1. Nella settimana 53 stop: **29 ingresso**, 24 uscita, 0 protezione: si è spostato verso gli ingressi
   sbagliati dall'inizio.
4. **Il paper entra dove entra il gate?** Sulle 8 coppie rigirate: 33 su 51 trade (65%, scarto mediano 16-18
   minuti) (ops 0481); il 27 set 20 su 37 (54%). **Sopra il 60%.** Due coppie a 0 su 7: USELESSUSDT|gen_2031005e
   e SUIUSDT|gen_490a90e5 (le altre sei fra 4/5 e 7/7): da guardare.
5. **Le serie di perdite.** Paper: 8 di fila al massimo su 265 trade. Gate, tutte le coppie insieme in ordine
   di tempo: 2.135 trade dal maggio 2023, serie più lunga 10, finestre di 8 tutte perse 3 su 2.128 (0,1%) (ops
   0481). Sulle 8 coppie, nel periodo del paper: segnali del gate aperti dal paper PF 1,36 su 33, non aperti PF
   0,80 su 28: «non distinguibile» (ops 0481; il 27 set 0,45 contro 0,66).
6. **Le gemelle.** 1 candidata scartata come gemella nel giro delle 08:04; 8 gruppi di validate con la stessa
   logica stampati (IDUSDT 3, USELESS, SKYAI due volte, MUBARAK, HEMI due volte, TRUMP) (ops 0470); il 27 set 8
   gruppi. La stampa si ferma a 8: non si vede se crescono.
7. **La copertura.** 223 validate su 76 coin, universo 200, copertura 38%; a 2/3 140 coin (747 coppie), a 1/3
   112 coin (625 coppie) (ops 0468); il 27 set 212 su 68 coin, 124 coin a 2/3 (508), 132 a 1/3 (651).
8. **Durata del giro.** Il giro finito alle 07:38 è durato **3 h 09** (anomalia GATE_SFORA; discovery 1 h 45,
   passata a 1 ora 9 minuti) (ops 0470, 0468); quello partito alle 08:04 era ancora in corso alle 09:19, e per
   questo il timer non mostra il prossimo avvio (ops 0482). Il 27 set: urgenti 1 h 13, completo 3 h 48. I giri
   sono attaccati uno all'altro: è anche ciò che ha lasciato R1 senza spazio il 3 ott.
9. **Le vite.** Nessuna riga «[vite]» nelle 80 righe del log lette (ops 0470).
10. **L'AI.** Spenta dal 2 ott sera: ultime 20 proposte su 20 accettate il 2 ott alle 20:18; origine AI 1
    validata su 223 (115 nel registro); chiave funzionante, nessuna chiamata ieri (ops 0467, 0468).
11. **Il tetto per coin.** Zero blocchi: nelle 24 ore 6 «posizione già aperta», 1 correlazione, 1 veto di
    regime (ops 0475); nei rifiutati dei 30 giorni nessun motivo «tetto» (ops 0476).

Migliorato: prima settimana in utile (+14,09), ingressi allineati al gate al 65%, copertura a 76 coin.
Peggiorato: giri del gate oltre le 3 ore e senza pause, stop della settimana soprattutto d'ingresso (29 su 53),
prematuri del trailing sopra i protetti per la prima volta. Proposta (non fatta): guardare trade per trade
perché su USELESSUSDT|gen_2031005e e SUIUSDT|gen_490a90e5 il paper entra dove il gate non entra (0 su 7).

### 4 ottobre, 10:40: USELESS e SUI trade per trade (sì del proprietario, ops 0483)

Lo strumento `ingressi` (sola lettura, 736 s; 18 coppie rigirate su 127, le altre 109 fuori per il tempo) dice,
per i 14 trade di USELESSUSDT|gen_2031005e e SUIUSDT|gen_490a90e5: tutti **short**, tutti fra il 21 set 08:30 e
il 27 set 11:15 UTC, tutti «la regola non scatta» con sotto-motivo IGNOTO: il motore non li riproduce nemmeno
sui valori degli indicatori registrati dal paper, nello stesso regime. È la stessa firma dei 5 trade di
`gen_6d06dca0` che il 27 set hanno fatto trovare il difetto della sessione oraria (J13, corretto il 27 set alle
19:40 UTC: la feature `session` leggeva l'ora del processo, e fuori sessione ammetteva solo lo short). Su tutte
le 18 coppie rigirate i trade non riprodotti visibili sono 20, tutti short, tutti prima della correzione
(anche HUMAUSDT|gen_fca11c08 ×4, PROM ×1, SYRUP ×1); dopo la correzione 8 trade rigirati: 7 abbinati e 1 col
motore ancora dentro il trade precedente, nessuno «regola che non scatta». Quei 20 trade fanno −33,57 USDT
(USELESS −24,39, HUMA −13,47, SUI +1,22, PROM +4,48, SYRUP −1,41), circa metà della perdita totale del paper
(−62,59, ops 0466). **Non verificato:** che le due spec usino `session` (la spec non è stampata; il dettaglio
feature per feature `--dettaglio` in lista bianca c'è solo per ORCA e VET). Conseguenza: nessuna modifica da
fare; conferma che le misure «dal 27 set 19:40» (declassate, fuori campione, R dal 27/9) partono dal punto
giusto. Allineamento ingressi sulle 8 coppie del confronto senza i 14 trade di prima della correzione: 33 su 37.

### 4 ottobre, 13:55: R2 fatta, G7 rimandata per un mio difetto (ops 0484-0485)

R1 lanciato alle 13:12 (ops 0484). **R2: 0 passate su 3.600** coppie (50 candidate del 17 set × 72 monete,
gate di oggi; bocciate soprattutto su total_return 3.175, poi recovery 150, trades 146) → per la regola del 3
ott **lo 0 di R1 è vero** e il cambio di piano lo decide il proprietario (voce R1b nel gruppo 0, con le opzioni
del 2 ott e una terza: fermare R1 dopo G7 e leggere la scelta del gate nel fuori campione del 7 e 14 ott).
R1 intanto ha la prima promossa: data 20 ago, 1 su 9.050 giudizi, 2 trade dopo a +0,89R (190 unità su 1.872).

**G7 non ha fatto nessuna prova**: «monete a confronto 0/72, 0 prove» (ops 0485). Causa (dedotta, il referto non
mostra le righe [g7]): sulla VPS R1 gira come `python -m scripts.replay_gate`, cioè come modulo `__main__`; lo
stato dei worker (`_S`) lo riempie `__main__._init`, mentre l'unità di G7 importava `scripts.replay_gate`, un
SECONDO modulo con lo stato vuoto → errore a ogni unità. Nei test non si vedeva perché lì il modulo è uno solo.
Corretto: il pool riceve `replay_gate._una_unita_g7`, che passa il proprio modulo (`sys.modules[__name__]`); test
nuovo che lo controlla; la lettura di G7 ora stampa gli stati delle unità e il primo errore. Le unità in errore
(1 tentativo) si rifanno al prossimo lancio. Suite: 2283 passati. G7 gira nel lancio di domani alle 13:10.

### 4 ottobre, 15:50: R1 fermata (opzione c, decisione del proprietario); da +18 a −10

Il proprietario ha scelto (c): «fermala dopo la prova di domani». Fatto nel codice (`R1_FERMATA` in
`scripts/replay_gate.py`): il lancio del 5 ott fa la prova sul prezzo casuale; quando è completa toglie il
file «attivo» (il gate torna a 8 giri al giorno) e non fa unità di R1; se non è completa il file resta per
rifarla nella finestra del giorno dopo, ma R1 non lavora comunque. Test nuovo; suite 2284 passati. Le 190
unità fatte restano su disco e `replay-gate-esito` le legge come prima (lettura: NON SI SA, 2 trade delle
promosse su 80). Richiesta del proprietario, scritta in CLAUDE.md: niente sigle nelle risposte.

**Da +18,85 (3 ott) a −10 (4 ott, 15:48).** Realizzato −62,59 alle 08:20 con il 4 ott a −4,38 (ops 0466, 0474)
→ −68,35 alle 15:48 (ops 0488): oggi −10,14 USDT su 17 trade aperti (ops 0486). Dai log (ops 0469, 0487; manca
il tratto 06:00-13:17, fuori dalle 120 righe): 7 stop (ZORA, STX, SOPH, PNUT, SYRUP −3,24, PLUME, TA) e 4
uscite trailing piccole (UB, GRIFFAIN, ZORA, MUBARAK). Dei 7 stop, 2 «direzione sbagliata» (SOPH mfe 0,23R,
PNUT 0,10R) e 5 «a favore ma sotto il primo gradino» (SYRUP fino a 0,81R, poi stop pieno). Ieri 16 trade delle
validate, 15 vinti, +0,869R a trade (ops 0479), quasi tutti chiusi dal trailing. È la forma del sistema, non un
evento: le vincite sono piccole (massimo a favore mediano 0,84R contro un primo incasso a 1,5-2R), gli stop
sono interi (−1R), e nei 19 giorni del paper le giornate vanno da −17,66 a +18,85 (ops 0474). Senza vantaggio
all'ingresso (curva del vantaggio: nessuno misurabile), il segno del giorno lo decide il mercato.

### 4 ottobre, 16:30: «abbassare il primo incasso a 0,8R?» — una colonna in più, nessun cambio

Risposta al proprietario: non prima delle letture del 7-14 ott (regola del 30 set e di T2). Numeri (ops 0471):
modello semplificato 1/1,5/2,5 −0,35R contro 2/4/6 −0,85R; 58 stop su 111 sotto il primo gradino, mfe mediana
0,49R; 68% dei trade a 0,5R, 42% a 1R. Il gate ha già 0,75/1,25/1,75 fra le candidate (scelta per 5 coppie).
Fatto, col suo sì: colonna 0,8/1,6/2,4 nella tabella «R medi incassati per scala» del report `mfe`,
dichiarata SOLO MISURA (`SCALE_SOLO_MISURA` in `scripts/mfe_report.py`): il gate non la prova, il bot non la
opera. Test `tests/test_scala_solo_misura.py`. Si legge col controllo del 7 ott.

### Controllo del 5 ottobre (mattina)

Nessun guasto: bot vivo (battito 23 s, ops 0501), controllo orario regolare, letture Firestore 7.201/24 h (ops 0493), spesa AI di ieri 0,10 $ (1 chiamata: il riassunto settimanale della domenica, ops 0491), nessun errore nelle righe lette; le righe «SPENTE» non sono nelle 80 righe del log del gate (solo candele del giro in corso, ops 0494); prova indiretta: nuove AI 0 e varianti 0 nella riga ORIGINI (ops 0492). **Giro completo della notte 3 h 22** (anomalia GATE_SFORA, ops 0501): 42.274 valutazioni, 421 passate, 213 figlie dell'intorno (ops 0492). **Numeri:** 291 trade, 57%, −76,08 USDT (lordo −33,61, costi 42,47), equity 923,92, DRY_RUN True, 2 aperte con 0,16% (ops 0490). Il 4 ott: 20 trade delle validate −8,92 USDT, −0,417R a trade (ops 0503); conto −9,65; oggi fin qui −8,08 (ops 0498). Giornate del paper: 7 in utile, 13 in perdita su 20. Dal 27 set −0,039R netti su 145 (lordo +0,052, costi 0,091; ops 0489; ieri +0,015 su 119). Regime neutro −0,170R su 86 dal 27 set. Stop: 124, 58 ingresso / 65 uscita / 1 (ops 0495). **Stella polare:** motore dopo la validazione −0,03R su 182 ±0,17 (ops 0498; ieri +0,006 su 156); stessi segnali motore −0,03, paper −0,05, differenza +0,02 ±0,08; lettura stampata: «la promessa non regge … la prossima modifica va nel gate»; decide il 7 ott. Declassate dal 27 set: −0,091R su 100 contro +0,076 su 45, −0,166 ±0,383 → non si decide (ops 0489). T2 su 291: nessun vantaggio (ops 0495). Scale, modello semplificato: 0,8/1,6/2,4 −0,20R (migliore), 1/1,5/2,5 −0,37, 2/4/6 −0,86 (ops 0495). Funzioni: tutte «non si vede ancora», compreso il paper esplorativo (11 trade, ops 0489). **Gate:** 235 validate su 77 coin, 760 a 2/3, spazio ~912, t ≥ 2 per 61 su 85, declassate 173 (ops 0492); passata a 1 ora 253 su 11.250; nessuna validata né trade a 1 ora. Selettore NON BATTE (ops 0497). Rifiutati: «posizione aperta» e «cooldown» sopra gli aperti, solo informazione (ops 0500). Trailing: 63 protetti su 141 verdetti, prematuri 65 (ops 0503). D8: ingresso rispetto al segnale +0,031R, latenza 156 s (ops 0503). **Gate rigiocato nel passato (fermato ieri):** 8 date su 26, 597 unità, 6 promosse, 45 trade a −0,22R contro −0,14R, non decide (ops 0502). **Prova sul prezzo casuale:** 144 unità in errore «'cfg'» (ops 0502), causa confermata e corretta (commit 0dc9e38); gira alle 13:10 e poi il file «attivo» va via. Report pubblicato alle 08:21, versione 2671584 (ops 0503). **Proposta del giorno:** P0, il Passo 0 del protocollo di ricerca per moneta (versione 4.2 consegnata al proprietario stamattina), nel gruppo 0.

### 5 ottobre, 13:56: la prova sul prezzo casuale è fatta (ops 0505-0506)

Lancio alle 13:13, finito alle 13:48 (35 minuti: solo la prova, niente unità del gate rigiocato nel passato,
fermato ieri). 144 unità ok (72 monete × vero/caso). **Candele vere: 8 passate su 7.200 prove (0,11%). Candele
rimescolate: 16 su 7.200 (0,22%). Rapporto 2,0.** Esito per la regola del 4 ott: **NON SI SA**, perché sul vero
passano meno di 10 candidate. Bocciate per criterio simili nei due mondi (total_return 4.364 contro 4.141).
Osservato: il gate promuove il doppio sui prezzi senza vantaggio possibile. Inferito, non deciso dalla regola:
il gate a 1 ora non distingue il rumore; con numeri così piccoli il doppio può essere caso. Quota sul vero
(0,11%) uguale a quella delle candidate nuove a 15 minuti nel giro vero (25 su 20.667, 0,12%, ops 0470) e
coerente con R2 (0 su 3.600): il 2,2% della passata a 1 ora è composizione (spec già note), come scritto il 4.
Da verificare col `log-gate` dopo le 14:04: che il giro delle 14:00 sia partito (file «attivo» tolto).

### 5 ottobre, 14:20: il giro delle 14:00 è tornato (ops 0507)

Il lancio delle 13:13 ha aspettato la fine del giro in corso (finito 13:28, 2 h 10, 63 passate) e ha fatto la
prova sui prezzi mescolati dalle 13:28 alle 13:48: 20 minuti per 144 unità, come stimato. Alle 14:05 il gate è
partito regolarmente, senza la riga «giro delle 12:00 UTC SALTATO»: il file «attivo» è stato tolto, il gate è
tornato a 8 giri al giorno. Il gate rigiocato nel passato è chiuso: 8 date su 26 restano su disco.

### Controllo del 6 ottobre (mattina)

Nessun guasto: bot vivo (battito 12 s, ops 0520), controllo orario regolare, letture Firestore 8.444/24 h (ops 0512), spesa AI di ieri 0 (ops 0510), nessun errore nelle righe lette; le 80 righe del log del gate sono solo candele del giro in corso (ops 0513): prova indiretta di AI e varianti spente dalla riga ORIGINI (nuove AI 0, varianti 0, ops 0511). Nessuna riga «giro delle 12:00 UTC SALTATO». **Giro completo della notte 3 h 28** (anomalia GATE_SFORA, ops 0520): 43.147 valutazioni, 429 passate, 204 figlie dell'intorno (ops 0511). **Numeri:** 309 trade, 57%, −77,42 USDT (lordo −33,02, costi 44,40), equity 922,58, DRY_RUN True, 3 aperte con 0,50% (ops 0509). Il 5 ott: 23 trade delle validate −6,52 USDT, −0,135R a trade (ops 0521); conto −6,38; oggi fin qui −2,40 (ops 0517). Giornate del paper: 7 in utile, 14 in perdita su 21. Dal 27 set −0,057R netti su 162 (lordo +0,037, costi 0,093; ops 0508). Long −0,110R su 85, short +0,002 su 77, regime neutro −0,182R su 93 (dal 27 set). Stop: 132, 61 ingresso / 70 uscita / 1 (ops 0514). **Stella polare:** motore dopo la validazione −0,04R su 202 ±0,16 (ops 0517; ieri −0,03 su 182); stessi segnali motore −0,04, paper −0,08, differenza +0,04 ±0,07; lettura stampata: «la promessa non regge … la prossima modifica va nel gate»; **domani 7 ott la lettura ufficiale**. Declassate dal 27 set: −0,119R su 114 contro +0,092 su 48, −0,211 ±0,353 → non si decide (ops 0508). Curva del vantaggio su 309: nessun vantaggio (ops 0514). Scale: 0,8/1,6/2,4 −0,21R (migliore), 2/4/6 −0,86 (ops 0514). Funzioni: tutte «non si vede ancora» (7, ops 0508). **Gate:** 257 validate su 82 coin, 781 a 2/3, spazio ~758, t ≥ 2 per 79 su 112, declassate 173 (ops 0511); passata a 1 ora 281 su 12.810; nessuna validata né trade a 1 ora. Selettore NON BATTE (ops 0516). Rifiuti 24 h: 7 «posizione già aperta», 1 cooldown (ops 0518). Trailing 7 giorni: 38 prematuri, 26 protetti (ops 0521). D8: ingresso +0,027R rispetto al segnale, latenza 159 s (ops 0521). Report pubblicato alle 08:21, versione ecc5247 (ops 0521). **Proposta del giorno:** nessuna nuova: nel gruppo 0 aspetta ancora il sì il Passo 0 del protocollo di ricerca (versione 4.3 rivista il 5-6 ott).

### 6 ottobre, sera: Passo 0 del protocollo di ricerca (sì del proprietario: «sì alla 4.3, sì ai branch, vai col Passo 0»)

Fatto in giornata, con cinque agenti in parallelo e quattro revisori avversari (36 difetti confermati e corretti,
elenco in `research/CHANGELOG.md`). Nel repo: `research/PROTOCOLLO.md` (4.3 con i due ritocchi: branch
`research/…` e guardiano), `research/src/motore.py` (motore di backtest secondo la sezione 7: barre chiuse,
ingresso all'apertura successiva, stop prima del target nella barra, gap in apertura, funding ai settlement con
la regola della stessa candela, costi per lato e moltiplicatore, dimensione e leva con riduzione al tetto,
liquidazione isolated/cross sul mark, ritardo di una barra, cucitura dei contratti, fine dati), `src/dati.py`
(caricatore da data.binance.vision con il blocco del vault prima di ogni accesso, impronte SHA-256, aggregazione
dei timeframe, elenco contratti), `src/statistica.py` (bootstrap a blocchi, differenza «netta», p-value con
correzione, Benjamini-Hochberg, entrate casuali, criterio del vault), `src/guardiano.py` (hook PreToolUse
registrato in `.claude/settings.json`, attivo solo con `research/.sessione`), `src/fatti.py` (controllo dei
riferimenti file:riga di `config/regole_dimensione.md`), `config/regole_dimensione.md` (548 righe, 303
riferimenti al codice del bot), `config/percorsi_vietati.txt`, `config/parametri.yaml` (bozza, stato
`bozza_passo_0`). Test: 371 nella cartella `research/src/tests` più i 2.286 del repo, tutti passati.
**Verifiche sulla rete vera** (dopo che il proprietario ha aperto gli host nell'ambiente): BTCUSDT 1h gennaio
2023 scaricato (744 candele, 744 mark, 93 settlement), checksum remoto uguale allo SHA-256 locale; il blocco del
vault ha rifiutato una richiesta fino al 2024-01-01 PRIMA di toccare la rete; buy and hold di gennaio 2023 a mano
16537,5 → 23119,4 = +39,80% lordo, il motore dà +39,80% lordo e +39,62% netto; una strategia banale sui dati veri
gira con mark e funding (9 trade). L'archivio mensile parte da gennaio 2020; i delistati ci sono (LUNA, FTT, SRM,
BTCST, RAY); fapi.binance.com risponde 451 dalla regione del server, www.binance.com/fapi/v1/exchangeInfo no
(924 contratti); l'indice del bucket sta su s3-ap-northeast-1.amazonaws.com (1000 simboli a pagina). Non
verificabili dalla sessione: tabella commissioni e documentazione (pagine costruite dal browser).
**STOP del Passo 0:** sei decisioni aperte in `parametri.yaml` (commissione taker, serie dello stop e workingType,
modalità di margine, porta d'ingresso nel bot per le strategie in codice, coda del 2019, percorsi vietati).

### 7 ottobre, 07:45: Passo 0 approvato, Passo 1 fatto (sì del proprietario: «ok a tutte, vai col Passo 1»)

Parametri congelati (`research/config/parametri.yaml`, stato `congelato`, approvato il 7 ott con i valori
proposti). **Passo 1**, sul branch `research/coordinamento`: criterio scritto prima dei numeri in
`universo/selezione_log.md`; modulo `research/src/selezione.py` + `passo1.py` con 10+1 test, revisione avversaria
(12 difetti, 1 grave: la scheda rivelava il delisting; tutti corretti, 444 test verdi nella cartella research,
2286 nel repo); eseguito due volte (la seconda col codice corretto, stesso esito). Numeri: 895 contratti perpetui
in USDT con dati; 100 idonee; 759 esclusi per listing dal 2022, 12 per dati finiti prima del 2024, 26 per volume;
24 idonee non più negoziate oggi; 20 di campagna (BTC, ETH, SOL, XRP, DOGE, BNB, LTC, MATIC, BCH, LINK, AVAX, ADA,
TRB, FIL, 1000SHIB, DYDX, MASK, FTM, GALA, ETC), di cui MATIC e FTM non più negoziate con quel simbolo. Nessuna
cucitura applicata: 9 contratti spariti nel 2022-2023 non toccano le 20. Schede delle 20 sul branch principale
(`research/campagne/<SIMBOLO>/scheda_moneta.md`, solo informazioni al 2023-12-31). Dati del 2023 (candele
giornaliere) in `research/data/`, fuori da git. Nota di processo: in questa sessione, che fa anche il controllo
del mattino, il marcatore `research/.sessione` è stato creato solo durante i due giri della selezione e tolto
subito dopo, per non bloccare le letture del controllo. **STOP del Passo 1:** conferma della lista dal proprietario.

### Controllo del 7 ottobre (mattina)

**Lettura ufficiale del fuori campione (regola del 30 set):** SELEZIONE → «la prossima modifica va nel gate»: motore dopo la validazione −0,05R su 230 segnali, ±0,14R per giornata (≥ 80 segnali, ≤ 0; ops 0532). ESECUZIONE → non si decide: stessi 200 segnali, paper −0,09R contro motore −0,04R, differenza +0,05 ±0,07 (ops 0532). Scritto in letture.md; seconda lettura il 14 ott. Nessun guasto: bot vivo (battito 32 s, ops 0535), controllo orario regolare, letture Firestore 8.674/24 h (ops 0527), spesa AI di ieri 0 (ops 0525), nessun errore nelle righe lette; le righe «SPENTE» non sono nelle 80 righe del log (solo candele del giro in corso, ops 0528): prova indiretta dalla riga ORIGINI (nuove AI 0, varianti 0, ops 0526). Nessuna riga «giro delle 12:00 UTC SALTATO». **Giro completo della notte 3 h 21** (GATE_SFORA, ops 0535): 45.069 valutazioni, 456 passate, 238 figlie dell'intorno (ops 0526). **Numeri:** 345 trade, 56%, −88,03 USDT (lordo −38,62, costi 49,41), equity 912,77, DRY_RUN True, **13 aperte** con 2,05% a rischio (ops 0524, 0535; massimo precedente 12). Il 6 ott: 25 trade delle validate −7,80 USDT, −0,303R a trade (ops 0536); oggi fin qui −5,99 (ops 0532). Giornate: 7 in utile, 15 in perdita su 22 (dalla colonna paper, ops 0532). Dal 27 set −0,091R netti su 197 (lordo +0,007, costi 0,098; ops 0523). Long −0,163R su 112, short +0,004 su 85, regime neutro −0,149R su 102 (dal 27 set). Stop: 150, 70 ingresso / 79 uscita / 1 (ops 0529). Declassate dal 27 set: −0,129R su 139 contro −0,001 su 58, −0,128 ±0,305 → non si decide (ops 0523). Curva del vantaggio su 345: nessun vantaggio (ops 0529). Scale: 0,8/1,6/2,4 −0,24R (migliore), 2/4/6 −0,86 (ops 0529). Funzioni: tutte «non si vede ancora» (7, ops 0523). **Gate:** 279 validate su 84 coin, 797 a 2/3, **spazio ~603** (ieri 758: allarme dei 400 fra 1-2 giorni), t ≥ 2 per 98 su 137, declassate 182 (ops 0526); passata a 1 ora 317 su 14.250; nessuna validata né trade a 1 ora. Selettore NON BATTE (ops 0531). Rifiuti 24 h: 48 «posizione già aperta», 2 margine insufficiente, 4 cooldown (ops 0533). Trailing 7 giorni: 36 prematuri, 31 protetti (ops 0536). D8: ingresso +0,028R rispetto al segnale, latenza 161 s (ops 0536). Report pubblicato alle 08:23, versione f26a4be (ops 0536). **Proposta del giorno:** nessuna nuova: il protocollo è allo STOP del Passo 1 (conferma della lista delle 20 monete). Da tenere d'occhio: lo spazio del registro (voce D1 nel gruppo 5: «solo se serve», e sta per servire).

### 7 ottobre, 08:40: lista confermata, aperta la sessione di campagna BTCUSDT

Il proprietario: «confermo la lista, apri tu in autonomia la sessione BTC e poi quando lo ritieni opportuno le
altre». Aperta dal coordinamento una sessione separata nello stesso ambiente (session_01RiExzKeGEKfRUjT3ggDfyA,
titolo «Campagna BTCUSDT — protocollo di ricerca (prova di processo)») con il solo messaggio: leggere il protocollo
e `CAMPAGNA BTCUSDT`, più le note pratiche (branch `research/campagna/BTCUSDT` dal principale, push frequenti
perché la macchina è temporanea, marcatore e test del guardiano, strumenti in `research/src/`, log solo in
aggiunta, STOP nella sua sessione). ETHUSDT e SOLUSDT partono quando la campagna BTC mostra che il processo regge
(è la prova di processo). Le 80 idonee non di campagna diventano monete di verifica al Passo 6.

### 7 ottobre, 10:05: i test di GitHub tornano verdi

Il proprietario riceveva molte email di job falliti. Causa: dal commit delle 07:38 (5ca2c8e) il file
`research/src/tests/test_selezione_revisione.py` importava `yaml`, che non è fra le dipendenze del repo; il test
`tests/test_allowlist_runnable.py` lancia davvero la voce `test` della lista bianca (`pytest -q` dalla radice),
che raccoglie anche i test della ricerca, e moriva in raccolta. Localmente non si vedeva perché `pyyaml` è
installato nell'ambiente di lavoro. Dodici esecuzioni rosse (su tre branch, compresa la campagna BTC che pusha
spesso). Corretto con 45e664d: `pyyaml==6.0.1` in `requirements.txt`, il test del revisore si salta se la
libreria manca, e la CI esegue anche `research/src/tests`. Verificato: esecuzione verde sul principale (45e664d)
e sul coordinamento (9b43703); il branch della campagna BTC ha ricevuto l'unione del principale.

### 7 ottobre, 10:45: la campagna BTC ha consegnato; aperte ETH e SOL

Controllo del coordinamento sulla sessione BTC (session_01RiExzKeGEKfRUjT3ggDfyA): ferma allo STOP della
consegna dalle 09:34, stato «aspetta indicazioni», contesto usato 312k token, costo 15,8 $. Branch
`research/campagna/BTCUSDT`: 6 commit di campagna (Fase 0, strumenti, Fase 1, secondo blocco, consegna) in
circa 2 ore e mezza. Log: 92 voci (28 registrazioni di cui 16 varianti e 12 verifiche, 28 risultati, 11 scarti
per stima dei trade, 25 note; 2 note citano un errore, nessuna il guardiano). Consegna: «nessuna strategia valida
trovata per questa moneta», periodo di validazione mai toccato, nessun candidato al vault. Nessuna correzione a
`src/` dalla campagna. Ipotesi NON lette dal coordinamento (regola 7). Il processo regge: aperte alle 10:43 le
sessioni ETHUSDT (session_01QrieoTra2fHED872FVjnVs) e SOLUSDT (session_01HuCxs6U8hiZkZiv6uR6bYJ) con lo stesso
messaggio (simbolo cambiato, divieto esplicito di leggere le altre campagne). Prossimo controllo alle 14:43; a
tre consegne fatte, il rapporto della prova di processo (Passo 2, punto 4) sul branch di coordinamento.

### 7 ottobre, 12:35: SOL ha consegnato, ETH va riaperta

Controllo a richiesta del proprietario. **SOLUSDT** (session_01HuCxs6U8hiZkZiv6uR6bYJ): consegna alle 11:39, in
meno di un'ora; log 56 voci (20 registrazioni, 17 varianti, 11 scarti, 1 correzione), «nessuna strategia valida
trovata», 8 proposte di metodo in `lezioni_metodo_proposte.md` (da leggere nel rapporto della prova); costo
equivalente 17,8 $. **ETHUSDT** (session_01QrieoTra2fHED872FVjnVs): bloccata alle 11:00 su `git push` 403: la
sessione era nata SENZA il repo fra le sorgenti autorizzate (la stessa chiamata di creazione aveva funzionato per
BTC e SOL: un'incostanza della piattaforma); 17 minuti di lavoro locale persi, 5,8 $. Rimedio: nuova sessione ETH
aperta alle 12:35 con il repo indicato esplicitamente come sorgente e l'istruzione di fermarsi se il primo push
fallisce. Lezione per il coordinamento: passare sempre la sorgente alla creazione e controllare il primo push
entro mezz'ora.

### 7 ottobre, 16:55: tre consegne, nessuna strategia, il rapporto della prova di processo

ETHUSDT ha consegnato alle 15:32 (seconda sessione, session_01Tutf22KnSqe6bmwQBThmF9; commit a60898c):
«nessuna strategia valida trovata per questa moneta», 23 varianti su 30, 22 scarti per stima dei trade, 81 voci
di log, 3 ore di orologio, 22,7 $ (più i 5,8 $ della prima sessione persa). Con BTC (16 varianti, 55 minuti,
15,8 $) e SOL (17 varianti, 56 minuti, 17,8 $) la prova di processo è completa: 56 varianti testate, 44 scarti,
34 varianti di budget non spese, 0 candidati arrivati alla validazione, 62 $ in tutto. Rapporto scritto in
`research/prova_processo/rapporto.md` sul branch `research/coordinamento` (commit bbfaf55), leggendo solo
conteggi, date, campi di processo dei log, prime righe delle consegne, lezioni di metodo proposte e CHANGELOG:
le ipotesi restano chiuse fino al Passo 7. Diagnosi del rapporto: la ricerca per moneta singola con 100 trade
minimi per direzione scarta le idee lente prima di provarle (34 scarti su 44 a 4 ore o più lente, 28 stime fra
50 e 99) e non ha i trade per confermare i segnali (8 varianti su 56 sopra il 96-97° percentile delle entrate
casuali, circa 2 attese per caso, nessuna oltre 2 errori standard a blocchi); le campagne si fermano per
mancanza di idee con fonte, non per budget. Dodici proposte al protocollo, la prima è la campagna di gruppo
(trade contati su più monete, regola scritta prima dei numeri, già prevista dalla sezione 11). Problemi di
strumenti: una sessione nata senza il repo fra le sorgenti (push 403), nove rifiuti del guardiano su ETH tutti
su forme della shell, il mark price con buchi risolto tre volte in tre codici diversi. STOP del Passo 2: decide
il proprietario (campagna di gruppo, regole uniche di stima e di «nettamente», se rifare le tre campagne — il
rapporto raccomanda di no — e se fermare le altre 17 campagne singole finché il protocollo non cambia). Il
marcatore di coordinamento è stato creato per scrivere il rapporto e rimosso subito dopo: durante quel tempo il
guardiano ha rifiutato, giustamente, una lettura di `docs/` dal branch di coordinamento.

### 7 ottobre, 17:20: rifare le tre campagne con regole cambiate, prima del gruppo

Domande del proprietario: le varianti non spese sono state provate? No: 14 su Bitcoin, 7 su Ethereum e 13 su
Solana non sono state usate (note di chiusura dei tre log), e nessuna variante di una moneta è stata provata
sulle altre (le campagne sono cieche fra loro fino al confronto finale). Perché la campagna di gruppo invece di
cambiare le regole e rifare le tre? Correzione del coordinamento: si possono rifare, e conviene farlo PRIMA. Il
periodo di validazione delle tre monete non è mai stato toccato (zero candidati), quindi rifarle con il
protocollo 4.4 non porta nessun conto in sospeso (Passo 2: branch vecchi in archivio, branch nuovi dal
principale). Regole da cambiare, nessuna scelta sui risultati di una strategia: stima dei trade unica (su Solana
la stessa idea dava 83 o 105 trade), lettura unica di «nettamente» (su Solana una variante era netta a un
campione e non netta a due), minimo in costruzione da 100 a 70 per direzione (70 è il minimo coerente con i 30
in validazione, perché la validazione ha circa il 43% dei trade della costruzione; entrerebbero 16 idee
scartate con stime fra 70 e 99), budget pieno con i ritocchi delle idee vicine ammessi nella sola costruzione.
Il rapporto raccomandava di non rifarle: superato da questa analisi. Trasparenza: leggendo le note di processo
del log BTC il coordinamento ha visto la sintesi di una variante (nota F5-01); non entra in nessun documento
del protocollo. Il proprietario ha anche chiesto di non parlare più di costi: regola aggiunta a `CLAUDE.md`.

### 7 ottobre, 23:30: la versione 4.4 è scritta e rivista; manca il sì del proprietario

Il proprietario ha detto «sì, rifalle con queste quattro modifiche». Il coordinamento ha scritto la versione 4.4 del
protocollo e gli strumenti comuni, poi due giri di revisione avversaria (cinque revisori e cinque verificatori per
giro) e un agente dedicato al guardiano. Primo giro: la regola «nettamente» fatta in modo semplice dava troppi falsi
positivi; il guardiano lasciava leggere la storia dei commit, gli hash dell'archivio e gli strumenti GitHub; la
scheda con la data di listing diceva se una moneta è delistata. Secondo giro: R asimmetrici, costi doppi e ritardo
senza criterio vero, ordine di avvio della campagna, `git fetch` che stampa gli archivi, ingressi persi nella baseline
casuale, date in virgola mobile. Corretto tutto tranne due punti del guardiano, che aspettano il rapporto di un
attaccante dedicato. Commit sul principale: b9659df, c4248a3, f989853, 3cffbae; rapporto della prova aggiornato sul
coordinamento (aa05619). Test: 710 della ricerca passano. Prossimo passo: il testo al proprietario; dopo il suo ok,
archiviazione dei tre branch e riapertura delle tre campagne.

### Controllo dell'8 ottobre (mattina)

**Nessun guasto.** Bot vivo (battito 2 s, ops 0550), controllo orario regolare (03:24 UTC, ops 0542), letture Firestore
12.109 nelle 24 ore (rifiutati 8.456; ieri 8.674, ops 0542), spesa AI di ieri 0 (nessuna chiamata, ops 0540), nessun
errore nelle righe lette. Le righe «SPENTE» non sono nelle 80 righe del log del gate (solo candele del giro in corso,
ops 0543): prova indiretta dalla riga ORIGINI (nuove AI 0, varianti 0, ops 0541). **Giro della notte 4 h 47**
(GATE_SFORA, 21:18-02:06 UTC): 81.788 valutazioni (il giro prima 45.069), 228 passate, 254 coin (ops 0541). **Spazio
del registro ~496 coppie** (ieri ~603): sotto 400 domani. **Numeri:** 377 trade, 55%, −98,04 USDT (lordo −45,16),
equity 902,30, DRY_RUN True, 8 aperte con 1,24% a rischio, massimo 15 insieme (ops 0539; nei trade 14, ops 0538).
Ieri 40 trade delle validate, −10,39 USDT, −0,191R a trade (lordo −0,093, costi 0,098); 7 giorni −0,144R su 162
(ops 0551). Giornate: dal 16 set 7 in utile e 16 in perdita sulla colonna paper (ops 0547). Dal 27 set −0,101R
netti su 227 (lordo −0,004, costi 0,097); long −0,190R su 134, short +0,027 su 93; regime neutro −0,110 su 111
(ops 0538). **Fuori campione:** motore −0,08R su 279 segnali ±0,14 (ieri −0,05 su 230); stessi segnali paper −0,11
contro motore −0,08, differenza +0,03 ±0,06 → la lettura stampata resta «la prossima modifica va nel gate»,
esecuzione non si decide; seconda lettura ufficiale il 14 ott (ops 0547). Stop: 167, sbagliati dall'inizio 75, sotto
il primo gradino 91 (ops 0544). Curva del vantaggio: nessun vantaggio (ops 0544). Scale: 0,8/1,6/2,4 −0,26R
(migliore), 2/4/6 −0,86. Declassate dal 27 set −0,129R su 158 contro −0,036 su 69: −0,094 ±0,281 → non si decide
(ops 0538). Funzioni: tutte «non si vede ancora» o campione piccolo (ops 0538). Selettore: non batte (ops 0546).
Rifiuti: soprattutto «posizione già aperta» e cooldown (ops 0548); i rifiutati per cooldown +0,04R contro aperti
−0,10 su 56, ma sono prezzo puro senza costi (ops 0549). **Gate:** 279 validate su 84 coin, 855 a 2/3, t ≥ 2 per
98 su 137, declassate 182; passata a 1 ora 328 su 15.360; nessuna validata né trade a 1 ora stampati. Una strategia
(gen_fa304106) ha 10 perdite di fila, freno di serie spento (ops 0539). Protocollo: le tre campagne della prova
sono ferme alla consegna (ultimi commit del 7 ott); il testo della 4.4 aspetta il sì del proprietario. **Proposta del
giorno:** nessuna voce nuova (il protocollo è allo STOP: approvazione della 4.4). Da tenere d'occhio: lo spazio del
registro, che domani scende sotto 400 (voce D1, gruppo 5).

### 8 ottobre, 07:15: versione 4.4 approvata; archivi fatti, cancellazione dei nomi vecchi bloccata

Il proprietario: «ok alla 4.4, archivia e riapri le tre campagne» (05:08 UTC). Scritto l'istante nell'intestazione del
protocollo, in `parametri.yaml` e in CLAUDE.md (commit 632671e). Archiviazione secondo il Passo 2: per BTCUSDT,
ETHUSDT e SOLUSDT copia del branch in `research/archivio/campagna/<SIMBOLO>`, con l'hash controllato uguale
(b60dd84, a60898c, d1955b4). La cancellazione dei nomi vecchi `research/campagna/<SIMBOLO>` è rifiutata dal canale
git della sessione (HTTP 403: politica, non rete); non si riprova per altre vie. Serve che il proprietario li
cancelli da GitHub; un controllo in background apre le tre campagne appena i nomi spariscono. Archiviate anche le
quattro sessioni di campagna della prova (BTC, SOL, le due ETH), così nessuna può riscrivere sui nomi vecchi.

### 8 ottobre, 07:15: le tre campagne riaperte con la versione 4.4

Il proprietario ha cancellato da GitHub i tre nomi vecchi `research/campagna/<SIMBOLO>` (verificato: restano solo i
tre archivi, con gli stessi hash, e il coordinamento). Aperte alle 05:13 UTC tre sessioni di campagna con il
repository come sorgente esplicita e il messaggio di apertura della 4.4 (ordine di avvio della sezione 9, regole
pratiche del guardiano, strumenti comuni, budget per intero, nessun accenno alla prova): BTCUSDT
session_017QE4DEoPbuHDKpzc3gh9m3, ETHUSDT session_01HEDsRZbsCXFwsg5pwrfzgw, SOLUSDT session_016DsPdvdJrgz2v1tiYadgKj.
Controllo del primo push entro 35 minuti; il coordinamento non legge le ipotesi fino al Passo 7.

### 8 ottobre, 07:25: Bitcoin e Solana riaperte

Alle 05:18 UTC la sessione ETHUSDT lavorava (branch creato, test del guardiano), mentre BTCUSDT e SOLUSDT risultavano
ancora ferme all'istante di creazione. Il coordinamento le ha archiviate alle 05:19 e riaperte una alla volta:
BTCUSDT session_01U7S57s6evHNkcLaH2xfzLE (05:19 UTC), SOLUSDT session_01PU8tnr13mv82SqNMA2VNY7 (05:20 UTC). Errore
del coordinamento: SOLUSDT stava partendo proprio in quel momento (aggiornata alle 05:19:03); non aveva fatto nulla
(nessun branch, nessuna memoria usata), quindi non si è perso lavoro. Lezione: una sessione nel cloud può metterci
più di 5 minuti ad avviarsi; si giudica ferma solo dopo 20-25 minuti senza aggiornamenti.

### 8 ottobre, 10:35: Bitcoin consegna con un candidato; Solana ferma su una domanda

**BTCUSDT** (session_01U7S57s6evHNkcLaH2xfzLE) ha consegnato alle 06:47 UTC: 30 varianti (5 ritocchi, 25 famiglie),
57 verifiche, una in validazione; dalla consegna, riga dell'esito: «Un candidato va al vault, con esito provvisorio:
BTCUSDT-V10», che passa l'asticella con p-value 0,048 perché è l'unico candidato. È il primo candidato del
protocollo. Il riassunto automatico della sessione diceva «none survived»: fa fede la consegna. Il vault si apre
solo dopo le consegne di tutte le monete di campagna (Passo 5). La campagna ha trovato e corretto un errore del
caricatore (il funding di Binance arriva fino a 47 ms dopo l'ora piena: 2.233 settlement su 4.383 per BTCUSDT 2020-
2023, e il motore non lo riconosceva come momento ambiguo): commit 2fedf41, portato sul principale (adfb831, 1026
test della ricerca passati) e unito nel branch di SOLUSDT (87ff673). ETHUSDT e SOLUSDT hanno usato il caricatore
vecchio: effetto atteso piccolo (incassi di funding all'ingresso contati quando sono ambigui), da elencare fra i test
da rieseguire al Passo 4. **SOLUSDT** (session_01PU8tnr13mv82SqNMA2VNY7) è ferma dalle 05:51 UTC su una domanda
all'utente, che nessuno vedeva: una variante batte nettamente le due baseline ma ha R medio dopo i costi negativo;
entra o no nell'ordine dei ritocchi? La regola 6 esclude le varianti che battono le due baseline «perché sono
candidati», ma dalla 4.4 un candidato deve anche avere R medio positivo: il caso non è scritto. Lo decide il
proprietario. Ritocchi e uso del budget: ETHUSDT 30 varianti senza ritocchi (consegnata alle 05:58 UTC).

- 8 ott, 11:37: SOLUSDT ancora ferma sulla domanda delle 05:51 UTC (22 varianti, nessun ritocco); il proprietario ha il testo da incollare. BTCUSDT ed ETHUSDT consegnate.

- 8 ott, 12:16: il proprietario ha risposto «sì» a SOLUSDT: una variante che batte le due baseline ma ha R medio dopo i costi non positivo entra nell'ordine dei ritocchi con il suo t contro la baseline (b). La regola va scritta nella 4.5 (backlog P1, punto 1). La sessione si è riattivata alle 10:14 UTC.

- 8 ott, 12:25: il proprietario chiede che ogni nuova sessione di campagna usi Opus 5.5 con ultracode. Scritto in CLAUDE.md (sezione del protocollo) e nel backlog P1 per la 4.5. Le tre campagne aperte oggi lo rispettano già (get_session: modello claude-opus-5-5, ultracode attivo).

### 8 ottobre, 13:40: tre consegne con la versione 4.4, un candidato

SOLUSDT ha consegnato alle 11:19 UTC (session_01PU8tnr13mv82SqNMA2VNY7): «Nessuna strategia valida trovata per questa
moneta»; 30 varianti (8 ritocchi, 22 famiglie), 41 verifiche, nessun candidato in validazione; 22 voci di
correzione = ricalcolo delle varianti già fatte dopo la correzione del caricatore del funding. Riepilogo delle tre
(conteggi dai log e righe dell'esito delle consegne): BTCUSDT 30 varianti, 5 ritocchi, 25 famiglie, 57 verifiche, 1
candidato in validazione → «un candidato va al vault, con esito provvisorio» (p-value 0,048, unico candidato);
ETHUSDT 30 varianti, 0 ritocchi, 30 famiglie, 6 verifiche, nessun candidato → nessuna strategia valida; SOLUSDT come
sopra. Durate (ora di Roma): BTC 07:19-08:47; ETH 07:13-07:58; SOL 07:20-13:19, di cui 4 ore e 20 ferma sulla
domanda dei ritocchi. Test da rieseguire prima del vault (Passo 4): le 30 varianti di ETHUSDT con il caricatore del
funding corretto (BTC lo aveva già corretto nei suoi dati, SOL ha ricalcolato). STOP: decide il proprietario.

- 8 ott, 15:40: il proprietario chiede di ricalcolare prima Ethereum. Unito il principale (con la correzione del caricatore del funding) nel branch della campagna ETHUSDT (8f908c5). Prima sessione di ricalcolo (session_01VXzCWnuWAtgxRXF9T3bpoA) aperta passando il modello in modo esplicito: get_session mostra che così ultracode NON passa. Archiviata e riaperta alle 15:34 ora di Roma senza passare il modello (session_01UE1EnkhKiumXfxCM55DcrZ), riparte dal suo commit di apertura b717e22. Controllo alle 16:25 ora di Roma.

- 8 ott, 15:52: CORREZIONE della riga sopra. Anche la sessione aperta senza passare il modello (session_01UE1EnkhKiumXfxCM55DcrZ) e' partita senza ultracode, come una terza aperta alle 15:50 ora di Roma (session_013mDbySX9tAwMCiq4iwoJDH, quella che lavora ora; la seconda e' archiviata, aveva solo riscaricato i dati e pushato il commit di ripresa 1a91400). Le sessioni di stamattina (07:12-07:20 ora di Roma), create con gli stessi identici parametri, avevano ultracode dalla creazione (get_session: flag_settings ultracode true anche in quella mai partita). Quindi passare il modello NON era la causa; la causa non e' nota. Cosa abbiamo capito: l'eredita' di ultracode non e' affidabile e va controllata a ogni apertura; regola riscritta in CLAUDE.md e nel backlog.

- 8 ott, 16:10: ricalcolo di ETHUSDT finito (session_013mDbySX9tAwMCiq4iwoJDH, Opus 5.5 SENZA ultracode, 15:50-16:07 ora di Roma; commit f66fcf0 sul branch della campagna). Dati riscaricati con impronte uguali; 72 voci di correzione nel log (che ora conta 36 registrazioni, 36 risultati, 4 scarti, 27 note, 72 correzioni). Dalla sezione aggiunta in fondo a consegna.md, l'unica letta: 38 risultati su 72 cambiano (le 30 varianti, il controllo positivo, le 6 verifiche), i 34 conteggi dei trade sono identici; la differenza piu' grande in R medio e' -0,0075; l'R medio scende sempre un poco perche' il funding al settlement in apertura di barra ora si conta solo quando e' un costo. Nessun esito cambia: «Nessuna strategia valida trovata per questa moneta». Fuga dichiarata: quella sezione nomina il candidato di ETHUSDT e le due verifiche in cui cade; non tocca il candidato di BTCUSDT che va al vault. Cosa abbiamo capito: l'errore del caricatore del funding pesava meno di un centesimo di R per trade su ETHUSDT; i test da rifare prima del vault ora sono zero.

- 8 ott, sera: il proprietario chiede «aprire le altre 17 o rilanciare queste 3 con più varianti e più tempo?». Analisi con tre letture indipendenti (protocollo, statistica e dati delle 20 monete, storia del processo), tre giudizi (rigore, obiettivo, capire) e una critica avversaria: tutti e tre i giudizi e la critica dicono aprire le 17 e non rilanciare le 3, con una giornata di preparazione (dettagli e numeri nel backlog, voce P1). Cosa abbiamo capito: il tempo non è mai stato il limite (6 campagne su 6 in 45-180 minuti, mediana circa 72; l'attesa sui blocchi ha superato il lavoro); il limite è la potenza (pochi trade per moneta); il candidato di BTC da solo non si distingue dal caso (1 su 90 varianti; con p 0,048 la probabilità che sia vero è stimata 31-63% partendo da una fiducia del 10-30%): lo decide il vault. Nota su ultracode: in questo turno la sessione di coordinamento ha ultracode acceso, nel pomeriggio no; ipotesi da verificare alla prossima apertura: la sessione figlia eredita lo stato del turno di chi la crea.

