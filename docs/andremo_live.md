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
