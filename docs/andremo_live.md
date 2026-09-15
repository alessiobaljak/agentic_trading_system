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
