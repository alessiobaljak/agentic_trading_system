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
che gira ogni 3 ore e alimenta il registro `strategy_registry/validated`.

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
versione 4.4, testo approvato dal proprietario l'8 ott 2026 alle 05:08 UTC): idee con un perche', periodo chiuso
(«vault», 2024-01-01 → 2026-09-30) che si apre una volta sola, un branch per campagna e un
guardiano meccanico (`research/src/guardiano.py`, attivo solo se esiste `research/.sessione`).
Chi lavora in una sessione di campagna legge solo i percorsi ammessi dal Passo 3 del
protocollo e non scrive ipotesi o risultati in questo file. Il gate attuale resta acceso come
gruppo di controllo finche' il proprietario non decide altrimenti.

**Ogni sessione di campagna si apre con il modello `claude-opus-5-5` e con ultracode attivo** (richiesta
del proprietario, 8 ott 2026). Nella creazione si passa `model: "claude-opus-5-5"`, la sorgente del
repository e il branch principale; ultracode passa dalla sessione che crea: dopo la creazione si
controlla con `get_session` che `flag_settings.ultracode` sia `true`, e se no la sessione si archivia e
si riapre da una sessione che ce l'ha.

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
