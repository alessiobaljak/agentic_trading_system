# Istruzioni per Claude su questo repo

Chi legge questo file sta rispondendo a una domanda arrivata da una issue di GitHub
(la tab **Claude** della dashboard è stata tolta il 21 set 2026: il proprietario non la
usava più). Chi scrive e' il proprietario, spesso
da un telefono e spesso senza poter lanciare comandi: la risposta dev'essere
autosufficiente.

## Cos'e' questo sistema

Bot di trading crypto autonomo, in **paper trading**. Gira su una VPS Hetzner, tiene
lo stato su Firebase, e la dashboard Next.js (Vercel) lo mostra. La ricerca delle
strategie e' un job separato (`scripts/optimize.py`, `scripts/discover_strategies.py`)
che girava ogni 3 ore e alimentava il registro `strategy_registry/validated`. **Dal 13 ott 2026 la ricerca
automatica del gate è FERMA** (file `ops/gate_fermo`, sì del proprietario): il paper resta acceso come banco di
misura, con gli ingressi a ordine limite (`bot/execution/executor.py`, misure in RTDB `/paper/ordini_limite`).
La ricerca riparte con il **protocollo 3** (`research/PROTOCOLLO_3.md`: la versione 5.1 su BTC scritta dal
proprietario, con il collaudo del metodo; approvato il 16 ott 2026 alle 19:26 UTC). Prima si collauda il metodo
(Passo 0, sezione 13bis: tre prove), poi una sessione di ricerca sul branch `research/campagna/BTC51` cerca le
strategie su BTCUSDT; il paper è l'esame finale. La seconda edizione (`research/PROTOCOLLO_2.md`) è chiusa.
**Il vault 3 è stato aperto il 17 ott 2026** (frase del proprietario): l'unico candidato, V-020, non lo supera
(`research/vault/BTC51_risultati.md`), e sulle altre monete regge solo su 1 di 9 (`research/altre_monete_3/risultati.md`).
**La campagna BTC51 è chiusa** (17 ott 2026, nessuna strategia valida): lezioni e proposte per il prossimo protocollo
in `research/campagne/BTC51/lezioni.md`. **Dal 17 ott 2026 vale il protocollo 4** (`research/PROTOCOLLO_4.md`, versione 6,
approvato alle 20:12 UTC): ricerca su LINKUSDT con 9 monete di controllo, campagna `LINK6` sul branch
`research/campagna/LINK6` (rientra nell'eccezione dei branch di ricerca), vault con la frase esatta «APRI IL VAULT 4»
scritta al coordinamento. Decisioni e motivazioni in `research/protocollo_4_note.md`. **La campagna LINK6 è chiusa** (18 ott
2026, nessuna strategia valida: 33 varianti su 40, nessun candidato, vault 4 mai aperto): lezioni e proposte in
`research/campagne/LINK6/lezioni.md`. **Decisione del proprietario (18 ott 2026, ~08:40 UTC):** «dobbiamo continuare
fino a quando non trovi delle strategie valide... se serve riscriviamo totalmente il gate», ma prima va scritta la storia
completa del progetto (dati raccolti, cosa abbiamo imparato, cosa abbiamo cambiato, errori da evitare) in `docs/storia/`,
da leggere prima di ripartire (`docs/backlog.md`, P11). **Delega del proprietario (18 ott 2026, sera):** «non continuare a
chiedermi le autorizzazioni, procedi ad oltranza fino a che non avrai trovate delle strategie profittevoli che devono valere
le crypto ad oggi in corso, continua a lavorare in background se un job finisce e non ottieni risultati, registra e passa
ad un'altra idea e così via.. scrivimi solo quando avrai trovate diverse strategie che si possono applicare a diverse crypto
anche se ci volessero dei giorni». È il **programma 5** (`research/programma5/`: regole in `REGOLE.md`, stato e coda delle
idee in `STATO.md`): il coordinamento lavora da solo, non chiede permessi e non scrive al proprietario finché non ci sono
più strategie valide su più monete; restano ferme le regole che non si negoziano (`DRY_RUN` vero, niente soldi veri, niente
segreti, paper mai usato come training set) e il metodo (regole scritte prima, confronto con il caso, periodi usati una
volta, conferma sui dati recenti). Il proprietario, 18 ott 2026 ~17:15 UTC: «non chiedermi ogni volta di continuare, procedi in
autonomia fino a quando non mi presenterai delle strategie validate e in profitto ... devi analizzare l'intero universo o
almeno le top 100 su binance future ... se ci vogliono giorni va bene» (`research/programma5/REGOLE.md`, sezioni 7 e 7bis:
fase 2 sui dati recenti, universo delle 100 monete più scambiate). Il proprietario, 19 ott 2026: «comprare e tenere 12 ore non è trading
[...] trovare delle strategie [...] partendo dagli indicatori tecnici [...] il passato è pubblico [...] riprovare con metodo e
non a caso [...] non voglio aspettare dati nuovi [...] usa limit o margin, tutte le crypto del future binance»: è il
**programma 6** (`research/programma6/METODO.md`): strategie a indicatori con stop, obiettivo e stop che segue il prezzo,
provate con le finestre che avanzano (scelta su 12 mesi, prova sui 3 dopo, dal 2020 a oggi) e le correzioni per i tentativi. Il
proprietario, 19 ott 2026 sera: «continua a cercare in autonomia, non fermarti se pensi serva misurare in paper procedi hai
campo libero fino a che non trovi cosa funziona»: il coordinamento cerca da solo e può misurare in paper (`DRY_RUN` vero,
niente soldi veri) le strategie candidate; registro delle prove in `research/programma6/STATO.md`. Il proprietario, 20 ott
2026: «continua a cercare in autonomia ed in continuazione, fai girare modelli su modelli [...] traccia tutto quello che stai
facendo e provando in un log o diario così da non ripetere le stesse cose ma soprattutto traccia anche i vari risultati [...]
l'unico motivo per cui ti puoi fermare è se abbiamo strategie per tutte le crypto e nel momento in cui queste hanno lo stesso
riscontro nel paper»: **il registro unico è `research/REGISTRO.md`** (si guarda prima di ogni idea nuova, ogni prova ha la
sua riga prima e il risultato dopo, con la coda delle idee). Il proprietario, 21 ott 2026: «io non farò trading su [Gate.io] [...] perché devo aspettare il 2 novembre o fine novembre? non è quello che avevo chiesto» e «forse è meglio che il paper con il vecchio gate si fermi e la dashboard venga pulita [...] parti con il paper nuovo»: si giudica sul passato di Binance (il paper è una conferma, non una condizione); la dashboard parte dalla scheda «Strategie nuove» e le schede del vecchio sistema stanno sotto «Vecchio sistema (fermo)»; il vecchio paper si ferma con il pulsante STOP della dashboard (il kill switch). Il proprietario, 22 ott 2026: «accendi f5 [...] la
decisione di portare le strategie in paper anche questa falla in autonomia senza che io ti dica nulla nel momento in cui
pensi sia giusto»: F5 gira nel bot in paper (`bot/portafoglio/f5.py`, interruttore `ops/paper_f5_acceso`), e il
coordinamento decide da solo quali strategie portare in paper e quando (sempre `DRY_RUN` vero, niente soldi veri), e lo
scrive nel diario. **Delega del
proprietario (17 ott, 21:10 UTC):** il coordinamento va avanti da solo con i passi (correzioni del collaudo, apertura
della sessione di ricerca, STOP, via libera alla validazione) senza chiedere il permesso, e lo informa; il vault no.

Il documento da leggere per primo e' **`docs/state.md`**: e' lo stato aggiornato, con
cosa e' fatto e cosa e' aperto. Poi `docs/architecture.md` per la mappa, e
`docs/audit_backtesting.md` per l'ultima revisione del motore di backtest.

**`docs/backlog.md`** tiene le cose TROVATE E NON FATTE, col motivo del rinvio e il
numero misurato che le ha fatte emergere. Va letto prima di proporre una modifica —
molto probabilmente e' gia' li', con scritto perche' non e' stata fatta. E va
AGGIORNATO ogni volta che si scopre qualcosa che vale la pena valutare ma non si fa
subito: senza, quelle scoperte vivono solo dentro una conversazione e spariscono con
lei. E' gia' successo per settimane.

## L'obiettivo finale, detto dal proprietario il 23 set 2026

Fare in modo che questo sistema **massimizzi vincite e profitti giorno dopo giorno**,
come farebbe un esperto di trading crypto — ma **tutto con criterio, logica e
precisione**: un numero va con la sua fonte, una modifica passa dal gate, il paper
non si usa mai come training set. Ogni mattina il controllo giornaliero, oltre ai
soliti numeri, **propone la voce del backlog più importante da attivare**, con il
perché e cosa si aspetta prima di farla (`docs/backlog.md`).

**I report della mattina sono FERMI dall'11 ott 2026, fino a nuovo ordine del proprietario**
(«ferma del tutto i report della mattina fino a nuovo ordine»). Le routine «Paper: controllo
giornaliero + proposta dal backlog» e «Paper: referto settimanale» sono spente: non si
riaccendono, non si eseguono a mano e non si sostituiscono con altro finché il proprietario non lo
chiede esplicitamente. Un «non farlo domattina» vale per TUTTI i report del mattino, non solo per
quello nominato (l'11 ott il referto settimanale è partito lo stesso: errore). Anche il controllo
orario della campagna di gruppo è spento dall'11 ott: la campagna ha consegnato.

**La stella polare e il passo di ogni giorno (aggiunto dal proprietario il 1 ott
2026).** L'obiettivo qui sopra è la stella polare: ci si punta con tutte le forze. Ma
non basta puntarla: **ogni giorno il sistema deve essere un passo più vicino**, e
bisogna poterlo dimostrare. Il passo non si misura solo in profitto. Conta anche ciò
che abbiamo CAPITO, per esempio:
* come e perché il sistema perde nei trade (direzione sbagliata, uscita, stop);
* perché entriamo in ritardo;
* perché il trailing chiude troppo presto;
* quali strategie e quali idee funzionano davvero dopo il gate, e quali no.

Quindi ogni azione, ogni modifica e ogni report deve rispondere a due domande:
«cosa ci avvicina all'obiettivo?» e «cosa abbiamo capito oggi che ieri non
sapevamo?», sempre con un numero e la sua fonte. Ogni giorno va scritto cosa
abbiamo capito, nel diario (`docs/andremo_live.md`) e nel report giornaliero in
dashboard. Una giornata senza niente di nuovo capito va detta, non nascosta. Una
funzione che non ha una misura del suo contributo non si può dire utile: va misurata
o tolta.

## Regole che non si negoziano

* **`DRY_RUN` resta `true`.** Il sistema non ha mai toccato denaro vero e non deve
  iniziare senza una richiesta esplicita, ripetuta e consapevole del proprietario.
  Non e' un parametro di ricerca.
* **Non si lavora su altri branch.** Lo sviluppo va sul branch di default di questo
  repo. Non aprire pull request se non e' stato chiesto. **Unica eccezione (si' del
  proprietario del 6 ott 2026):** i branch del protocollo di ricerca,
  `research/coordinamento`, `research/campagna/<SIMBOLO>` e
  `research/archivio/campagna/<SIMBOLO>`, come descritto in `research/PROTOCOLLO.md`
  (sezione 5). Il bot, la macchina e la dashboard leggono solo il branch di default.
* **Mai un segreto in un commit.** Niente chiavi, token, `.env`, output di
  `git remote -v` o `git config --list` (il token puo' essere dentro l'URL del
  remoto). Un segreto finito in un repo pubblico e' compromesso per sempre, anche se
  il commit viene poi rimosso. **Questo repo e' pubblico.**
* **Il trailer dei commit** e' quello che trovi negli ultimi commit: copialo da li'
  invece di inventarlo.
* **Non dichiarare fatto cio' che non e' verificato.** Se i test non girano, dillo.
  Se una cosa e' stata saltata, dillo. Questa e' la regola che il proprietario ha
  chiesto piu' volte.

## Il protocollo di ricerca (dal 6 ott 2026)

Le strategie nuove nascono dal **protocollo di ricerca per moneta** (`research/PROTOCOLLO.md`,
versione 4.5, testo approvato dal proprietario il 9 ott 2026 alle 12:06 UTC): idee con un perche', periodo chiuso
(«vault», 2024-01-01 → 2026-09-30) che si apre una volta sola, un branch per campagna e un
guardiano meccanico (`research/src/guardiano.py`, attivo solo se esiste `research/.sessione`).
Chi lavora in una sessione di campagna legge solo i percorsi ammessi dal Passo 3 del
protocollo e non scrive ipotesi o risultati in questo file. Il gate attuale resta acceso come
gruppo di controllo finche' il proprietario non decide altrimenti.
Dalla 4.5 (sì del proprietario del 9 ott 2026) le sessioni delle campagne rimanenti le apre il coordinamento su
delega, al massimo tre campagne in corso, con il messaggio di apertura approvato (`research/apertura/campagna.md`
sul branch di coordinamento), un controllo ogni ora e le domande delle campagne girate subito al proprietario
(Passo 4 del protocollo). La prova a placebo dell'esame (`research/taratura/placebo/`, branch di coordinamento)
dice che l'esame regge sui prezzi veri.
**Dal 16 ott 2026 vale il protocollo 3** (`research/PROTOCOLLO_3.md`): una sola campagna, `BTC51`, su BTCUSDT.
Il Passo 0 (strumenti e collaudo del metodo) e i Passi 5-8 li fa il coordinamento sul branch principale; i Passi 1-4
una sessione di ricerca sul branch `research/campagna/BTC51`, con il marcatore `{"tipo": "campagna", "simbolo":
"BTC51"}`, aperta solo dopo il sì del proprietario agli esiti del Passo 0. Il vault si apre solo con la frase
esatta «APRI IL VAULT 3». Il branch `research/campagna/BTC51` rientra nell'eccezione dei branch di ricerca.

**Ogni sessione di campagna si apre con il modello `claude-opus-5-5` e con ultracode attivo** (richiesta
del proprietario, 8 ott 2026). Nella creazione si passano la sorgente del repository e il branch principale;
modello e ultracode si ereditano dalla sessione che crea (per ultracode non c'e' un parametro). L'eredita'
non e' sicura: l'8 ott le sessioni create fra le 05:12 e le 05:20 UTC avevano ultracode dalla creazione, le
tre create fra le 13:24 e le 13:50 UTC no, con o senza `model` passato, con gli stessi parametri; la causa
non e' nota. Dopo la creazione si controlla con `get_session` che il modello sia `claude-opus-5-5` e che
`external_metadata.flag_settings.ultracode` sia `true`; se manca, non si riapre a ripetizione: si dice al
proprietario, che decide se lasciarla lavorare o fermarla.

## Non hai accesso alla VPS — ma hai un canale

Non puoi entrare sulla macchina ne' leggere Firebase. Puoi pero' **chiedere alla VPS
di eseguire un comando** dal repo: si scrive un file in `ops/requests/`, l'agente
sulla macchina lo esegue contro una lista bianca locale e ricommitta la risposta in
`ops/results/` col nome corrispondente. Leggi `ops/README.md` prima di usarlo.

Regola pratica: se la domanda richiede di sapere cosa sta succedendo **adesso** sulla
macchina, metti in coda una richiesta, dillo nella risposta, e spiega che l'esito
arriva entro qualche minuto in `ops/results/`. Non inventare numeri.

Il battito della macchina e' in `ops/heartbeat.md`: se e' fermo da ore, la VPS o
l'agente sono giu', ed e' un'informazione che vale la pena dare subito.

## Come rispondere

* **In italiano**, e semplice. Il proprietario lo ha chiesto esplicitamente: niente
  gergo se una frase normale basta.
* **Niente sigle.** Non usare i codici del backlog (R1, G7, T2, C5...) parlando col proprietario: non
  li ricorda (4 ott 2026). Si dice cosa fa la cosa, in parole semplici («la prova sui prezzi mescolati»);
  la sigla, se serve, va solo nei file.
* **Niente costi.** Non parlare del costo in dollari delle sessioni o delle campagne: il proprietario ha
  l'abbonamento e le campagne non consumano API a pagamento (7 ott 2026). Contano il tempo e i limiti d'uso,
  e solo se fermano il lavoro.
* **Prima la risposta, poi il perche'.** Se la risposta e' "no", che sia la prima
  parola.
* **Un numero va con la sua fonte.** "224 coppie a 1 pass" va bene se viene da un
  file o da un risultato ops; se viene da una stima, dillo.
* Se la domanda e' una richiesta di modifica al codice, falla davvero: leggi, cambia,
  lancia `python -m pytest tests/ -q`, committa. Poi riassumi cosa e' cambiato.
