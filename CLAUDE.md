# Istruzioni per Claude su questo repo

**RISPONDI SEMPRE IN ITALIANO al proprietario**, in ogni messaggio, anche dopo il riassunto di una conversazione lunga, anche quando i file, i log o gli strumenti sono in inglese, **anche nei giri che partono dalle routine automatiche** (è lì che il 24 ott 2026 sono uscite sette risposte in inglese: il promemoria entrava solo con i messaggi del proprietario). Il proprietario lo ha chiesto più volte («risolvi una volta per tutte»). Tre protezioni: il promemoria a ogni messaggio e a ogni avvio (`.claude/settings.json`, `.claude/hooks/session-start.sh`), il promemoria in cima ai prompt delle due routine, e il **controllo meccanico di chiusura** (`.claude/hooks/controllo_lingua.py`): una risposta che sembra in inglese viene bloccata e va riscritta in italiano.

Chi legge questo file sta rispondendo a una domanda arrivata da una issue di GitHub
(la tab **Claude** della dashboard è stata tolta il 21 set 2026: il proprietario non la
usava più). Chi scrive e' il proprietario, spesso
da un telefono e spesso senza poter lanciare comandi: la risposta dev'essere
autosufficiente.

## Cos'e' questo sistema (oggi)

Bot di trading crypto su Binance Futures (perpetui in USDT), **solo con soldi finti** (`DRY_RUN` vero). Gira su una VPS Hetzner, tiene
lo stato su Firebase, la dashboard Next.js (Vercel) lo mostra. Oggi gira **G1** (il funding fra monete deciso ogni giorno) nel paper
del bot con G11, G1N, F5 ed eventi (`bot/portafoglio/`), e sul **conto demo di Binance** (a 1.000 USDT dall'8 novembre 2026). Il
vecchio sistema (gate, `bot/strategies/`, `backtesting/`) è fermo dal 13 ottobre 2026 (`ops/gate_fermo`). La ricerca segue i
programmi 5, 6 e 7 con il registro unico `research/REGISTRO.md`; da dove cominciare: `research/INDEX.md`.

## Le decisioni del proprietario in vigore (testo intero e storia in `docs/decisioni_del_proprietario.md`)

* **18-19 ottobre**: autonomia — si cerca da soli, senza chiedere permessi, finché ci sono strategie valide; il paper si può usare
  per misurare (`research/programma5/REGOLE.md`, `research/programma6/METODO.md`).
* **20 ottobre**: un solo registro di tutte le prove e di tutte le idee, `research/REGISTRO.md` (coda unica nella sezione 5:
  nessuna idea si perde, ognuna o si prova o si scrive perché no).
* **21 ottobre**: si giudica sul passato di Binance; il paper è una conferma, non una condizione.
* **23 ottobre**: l'obiettivo è il profitto, con qualunque tipo di strategia (in giornata, scalping, a settimana, eventi, nuove
  quotazioni); il trading di ogni giorno non va mai lasciato indietro (`research/programma7/METODO.md`).
* **24 ottobre**: «non bocciare 0,91 se ogni anno si alza la soglia»: una strategia ogni anno positiva, con il t sopra 3 e lo
  Sharpe corretto intorno a 0,90 non si boccia → paper e demo; i soldi veri solo quando il proprietario lo chiede esplicitamente
  (`docs/backlog.md`, P26). **L'8 novembre il proprietario ha chiarito**: lo 0,90 l'ha fissato la sessione, non lui; non è un muro
  («se era di qualche punto sotto potevamo procedere, non essere così severo»): conta il profitto, sul passato e in avanti.
* **1° novembre**: niente attese fisse (né 26, né 52, né 104 settimane); i numeri vanno al proprietario ogni lunedì.
* **5 novembre**: «si cambia, e sono d'accordo miglioriamo quello che già funziona»: ogni giro delle 4 ore raccoglie i dati e
  migliora G1 (`research/programma7/MIGLIORARE_G1.md`); un'idea nuova solo con un perché forte.
* **6-7 novembre**: il capitale per i soldi veri è piccolo (250 euro, poi la prova a 1.000 USDT sul demo); eventi spenti sul demo;
  il conto vero partirà vuoto e comprerà alla mezzanotte, senza copiare a metà giornata il paper (backlog P26).
* **7 novembre**: «chi scrive una strategia non la valuta, chi la valuta non la modifica, e il passaggio di gate lo decido io»; poi
  «decidi tu il passaggio al paper, confermo niente vault e branch, valori per le prove confermati»: il **paper lo decide la sessione
  principale**; demo, soldi veri e ogni riavvio che tocca gli ordini li approva il proprietario. Nelle prove: commissioni 0,05% a
  mercato e 0,02% con ordine limite, scarto di prezzo 0,01% su BTC, ETH e SOL e 0,02% sulle altre; nessun vault per data.
* **8 novembre**: «non voglio che nessuna delle strategie ora in paper o in demo vada persa [...] devono rimanere tutte in corso»:
  G1 sul demo, G1, G1 neutra, G11, F5 ed eventi restano accese (spegnerne una solo con il suo ok; test
  `tests/test_strategie_restano_accese.py`). Il vault non si pulisce. Due agenti nuovi: chi migliora le strategie in corso e chi
  sceglie quale usare in produzione. La ricerca nuova la fanno gli agenti: la 1:1:1 (una moneta, un intervallo, una strategia) su 4
  ore e un giorno, il riesame delle prove bocciate di poco, le monete nate dopo ottobre, le idee in coda.
* **11 novembre**: «non fermarti a cercarne di nuove [...] dovremmo continuare a provare cose nuove»: la ricerca nuova va avanti a
  ogni giro accanto al miglioramento di G1 (strategy-scout propone, strategy-researcher esegue, backtest-auditor giudica); le aree del
  repository separate (`AREE.md`).
  Lo stesso giorno: lo Sharpe corretto si calcola contando le **famiglie di prove simili** (`research/programma6/asticella.py`), non le
  prove una per una; la miscela F5 + M7 + K2 (prova 28, PASS tecnico al riesame) si misura a tavolino ogni settimana, senza ritocchi.

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

## Le azioni (dal 24 ott 2026)

Il proprietario (24 ott 2026): «apri un'altra sessione che dovrai chiamare trading stock [...] una cartella dedicata alle stock che
non si mischi con tutto quello che stiamo facendo lato crypto, solo la dashboard sarà condivisa [...] il paper lo voglio fare su un
reale conto live demo di una piattaforma (che mi dovrai consigliare tu per il mercato svizzero)». Le azioni stanno **tutte in
`stock/`** (leggere `stock/README.md`) e le segue la sessione **«trading stock»**. Questa sessione (le crypto) non tocca `stock/`; la
sessione delle azioni non tocca le cartelle delle crypto. **In comune c'è solo la dashboard**: le azioni vi entrano con una scheda e
componenti loro (`dashboard/app/components/stock/`); dal 10 novembre la scheda «Azioni» c'è, vuota, e come riempirla (dati su Firebase sotto `/azioni`, mattoni comuni della dashboard) è scritto in `dashboard/GUIDA_SCHEDA_AZIONI.md`. Le regole qui sotto valgono anche per le azioni (niente soldi veri: solo il conto
demo; mai le credenziali del conto demo in un commit).

## Le aree del repository (dall'11 novembre 2026)

Ogni area ha la sua sessione e scrive solo nelle sue cartelle e nei file in comune: crypto (questa sessione: tutto ciò che non è di
un'altra area), azioni (`stock/`, sessione «trading stock»), in comune la dashboard, `.claude/`, `.github/` e i file di regole. La mappa
è `AREE.md` (`AREE.json` per il blocco nel codice, `.claude/hooks/aree.py`); un'area nuova (per esempio Forex) si aggiunge come scritto
lì.

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

## I protocolli di ricerca e le campagne (chiusi)

I protocolli 1-4 e le campagne (BTC51, LINK6, i branch `research/campagna/*`, il guardiano `research/src/guardiano.py` acceso solo
con `research/.sessione`) sono chiusi; il vault di BTC dal 2024 è stato aperto il 17 ottobre 2026. Per riaprire una campagna, o per
le regole delle sessioni di campagna (modello e ultracode), leggi `docs/decisioni_del_proprietario.md`.

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

## Subagent: quando usarli (`.claude/agents/`, dal 7 novembre 2026)

Principio del proprietario: chi scrive una strategia non la valuta, chi la valuta non la modifica; il paper lo decide la sessione principale, demo e soldi veri il proprietario.

* **strategy-researcher** (modello medio): esegue UNA prova del registro, con le regole già scritte e committate; più istanze in
  parallelo su prove diverse (al massimo 3 insieme).
* **backtest-auditor** (modello più potente): attacca ogni prova promettente prima di proporre paper, demo o soldi veri; verdetto PASS / FAIL / INCONCLUSIVE.
* **gate2-reconciler** (modello medio; prima dei soldi veri si chiama con il modello più potente): confronta ogni settimana paper e
  demo con la ricerca sugli stessi giorni, e sempre prima dei soldi veri.
* **live-path-reviewer** (modello più potente): rivede ogni modifica al percorso degli ordini (`bot/execution/`, `bot/risk/`, `bot/portafoglio/`,
  `bot/config.py`, `bot/main.py`, `firebase/`, il futuro conto vero) prima del commit e del riavvio.
* **strategy-improver** (modello medio; dall'8 novembre): migliora le strategie in corso secondo i piani (per G1
  `research/programma7/MIGLIORARE_G1.md`); una variante entra accanto all'originale, mai al suo posto. La sessione principale lo chiama
  nel giro delle 4 ore quando c'è un passo vero da fare, non per scrivere «niente di nuovo».
* **strategy-scout** (modello medio; dall'11 novembre): cerca idee nuove con un perché forte (dato mai usato, studio serio, fatto
  visto in avanti, idea del proprietario), controlla che non siano già provate e scrive le regole prima di ogni calcolo; una o due idee
  al giorno (giro delle 08:17) o quando la coda resta senza prove pronte. Non calcola e non giudica.
* **portfolio-allocator** (modello medio; prima dei soldi veri il più potente; dall'8 novembre): ogni lunedì dopo gate2-reconciler,
  e prima di ogni proposta di demo combinato o di soldi veri, dice quale strategia o miscela usare in produzione e con quale
  capitale, con regole scritte prima (`allocazione/REGOLE.md`, da far approvare al proprietario). Propone, non esegue.
* Dashboard, documentazione, raccolta dei dati e implementazione: la sessione principale. I subagent non si chiamano fra loro.

Flusso: idea con un perché forte (strategy-scout o sessione principale) → regole scritte prima (committate dalla sessione principale, riga nel registro) → strategy-researcher in modalità verifica (le ambiguità delle regole si chiudono e si ricommittano prima del calcolo; dal 12 novembre) → strategy-researcher → se
promettente, backtest-auditor → se PASS, paper (lo decide la sessione principale) → ok del proprietario → demo → gate2-reconciler
ogni settimana → portfolio-allocator → ok del proprietario → soldi veri. Le strategie in corso: strategy-improver → (se una variante
passa il suo esame) backtest-auditor → paper accanto all'originale. Ogni modifica al percorso degli ordini: live-path-reviewer → ok del proprietario → riavvio. La sessione principale
aggiorna `research/INDEX.md` e `research/REGISTRO.md` dopo ogni gruppo di ricercatori.

## Regole dei token (per la sessione principale e per tutti i subagent)

* Si legge prima l'indice della propria cartella (`research/INDEX.md`, `audits/INDEX.md`, `reviews/INDEX.md`, `gate2/INDEX.md`) e
  poi solo i file che servono; mai «tutto all'inizio».
* File che non si leggono mai interi: `docs/andremo_live.md` (il diario: si scrive in coda, si legge con `tail` o `grep`),
  `research/REGISTRO.md` (`python3 -m research.src.registro --riepilogo`), `docs/backlog.md` e `docs/state.md` (`grep` sulla
  sezione), le risposte della macchina in `ops/results/` (`grep` sulle righe che servono). Mai: `research/data/`, `dashboard/node_modules`,
  `dashboard/.next`, gli archivi in `ops/results/archivio_*`, file binari e lockfile (le letture sono vietate in `.claude/settings.json`).
* Prima si cerca (Grep, Glob), poi si leggono solo le righe necessarie; un file non modificato non si rilegge.
* Dati di mercato, risultati e registri si guardano con script; le prove stampano a schermo al massimo 20 righe e scrivono il resto
  su file. Test: solo riepilogo e fallimenti (`-q`). Log del bot: solo errori, avvisi e righe del periodo in esame.
* Registri degli agenti: voci aperte e ultime 10 nel file principale, il resto in `ARCHIVE.md`; nessun file di memoria oltre le 300
  righe. Unica eccezione: i registri delle varianti in `research/trials/` non si troncano, non si archiviano e non si riassumono mai.
* Rapporto completo su file; alla sessione principale al massimo 30 righe, con i problemi Bloccanti e Alti e le domande aperte sempre
  testuali e completi.
* Il brief a un subagent contiene richiesta, vincoli, criteri di accettazione e percorsi dei file, mai contenuti che può leggere da
  solo; a backtest-auditor non si passano la motivazione né giudizi sul risultato.
* Modifiche mirate, mai riscritture intere; nelle risposte al proprietario niente file ristampati: esito, cosa è stato fatto, cosa
  serve da lui, dove sono i dettagli.
* `docs/SESSION_STATE.md` (compito in corso, decisioni, prossimi passi) si aggiorna a ogni tappa; a compito chiuso o con un contesto
  molto lungo si suggerisce al proprietario di compattare la conversazione.
* Ogni subagent nuovo segue queste regole; quando se ne crea uno, si adatta il suo file e si dice al proprietario cosa è cambiato.

## Regole che non si toccano, qualunque sia il risparmio di token

* La checklist di backtest-auditor si esegue sempre per intero; ogni modifica al percorso degli ordini passa da live-path-reviewer.
* Nessun PASS, APPROVE o test superato su ciò che non è stato eseguito davvero; nessuna compressione di problemi Bloccanti, Alti e
  domande aperte; nessuna lettura saltata quando serve per una decisione su limiti fissi, ordini, segreti o soldi veri.
* I registri delle prove e delle varianti non si troncano, non si archiviano e non si riassumono.
* Demo, soldi veri e ogni riavvio che tocca gli ordini richiedono l'ok esplicito del proprietario (il paper lo decide la sessione
  principale, 7 novembre).
* Nessuna strategia del paper o del demo si spegne, si sostituisce o si perde senza l'ok del proprietario (8 novembre).
* I segreti sono bloccati nel codice (`.claude/hooks/segreti.py` e le regole `deny` di `.claude/settings.json`); le modifiche ai limiti
  fissi (`bot/risk/hard_limits.py`, `circuit_breakers.py`, `kill_switch.py`) chiedono conferma (`ask`).
