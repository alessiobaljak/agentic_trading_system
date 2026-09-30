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
