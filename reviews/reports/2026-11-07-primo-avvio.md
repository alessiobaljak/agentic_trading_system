# Revisione completa del percorso degli ordini (primo avvio)

Data: 7 nov 2026. Revisore: `live-path-reviewer`. Oggetto: lo stato attuale del branch, non un diff.

### Riepilogo e verdetto

**REQUEST CHANGES.** Nessun problema bloccante per il demo di oggi (soldi finti), ma **9 problemi Alti**: 4 nel codice che oggi
manda ordini al conto demo e da cui nascerà il conto vero, 4 nel vecchio ramo reale (spento da `DRY_RUN`), 1 preesistente già nel
backlog. Per il conto vero i primi quattro sono bloccanti: vanno corretti prima.

In breve, sul demo:
- un errore di rete nell'ora dopo il ribilancio fa **rimandare a mercato lo stesso ordine due volte** (provato: posizione doppia);
- dopo un errore qualsiasi il **pulsante che chiude tutto e lo stop sul conto restano sordi per 30 minuti** (provato);
- se una chiusura viene rifiutata, il demo si dice «fermo» ma **la posizione resta aperta per sempre**, senza nuovi tentativi (provato);
- un «riparti» rimasto vero su Firebase **annulla lo stop sul conto 30 secondi dopo** (provato).

I test: `2545 passed`, nessun fallimento. Nessuno dei sette guasti provati a mano è coperto da un test.

### Oggetto (branch, commit, file toccati, invarianti coinvolti)

- **Branch** `claude/brave-albattani-1b12fv`. **Commit**: `36492509` all'inizio; durante la revisione è arrivato `782a01fc`, che cambia
  solo `docs/SESSION_STATE.md` (verificato con `git diff --stat 36492509 HEAD`). Il codice del percorso è identico a `b29f5713`, il
  commit della mappa del 7 nov (`git diff --stat b29f5713 HEAD -- bot/ firebase/ ops/ ...`: vuoto).
- **File letti**: `bot/portafoglio/demo_binance.py` (tutto), `bot/portafoglio/f5.py` (tutto), `bot/main.py` (avvio, ciclo, pulsante,
  riconciliazione, chiusure), `bot/risk/` (tutti; `portafoglio.py` è una simulazione, non è nel percorso), `bot/execution/executor.py`
  (ramo reale), `reconciler.py`, `error_handler.py` (inizio), `bot/config.py` (voci di modo e rischio), `bot/core/firebase_client.py`
  (lettura e scrittura), `bot/core/models.py:187-196`, `firebase/*.rules*`, `ops/README.md`, `scripts/ops_agent.py` (oscuramento e
  pull), `tests/test_demo_binance.py`, `docs/backlog.md` (voce del conto vero e aggiunte, con grep).
- **Invarianti coinvolti**: tutti quelli della mappa (`reviews/LIVE_PATH_MAP.md`), compresi per la prima volta quelli del demo: leva 5,
  stop sul conto −35% dal massimo, pulsante che chiude tutto, margine unico, una posizione per moneta, capitale ridotto.
- **Prove a mano** (nessuna rete, il Binance finto dei test): script in
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/primo_avvio/`
  (`prove_demo.py` prove a-c, `prova_riparti.py` prova d, `prove_vecchio.py` prove e-g, `prova_nan.py`).

### Checklist A–F

**A. Limiti fissi e interruttori**
- Valori fissi invariati: **OK**. `bot/risk/hard_limits.py:17-37` come nella mappa del 7 nov; nessun cambio in `bot/` da `b29f5713`.
- Nessun limite critico in configurazione o Firebase: **PROBLEMA**. `BACKTEST_PARITY` (`bot/config.py:672`) spegne fermi e tetto delle
  posizioni (Problema 9); tetto delle posizioni, stop massimo e quota per posizione da variabile d'ambiente (`bot/config.py:176`,
  `:707`, `:181`), `tuning.env` caricato sopra tutto senza elenco delle chiavi ammesse (`:35`); `DRY_RUN` letto in modo che un errore
  di battitura vale falso (`:46-50`, `:64`, Problema 5); il capitale del demo da un file del repo, senza tetto (`demo_binance.py:321-329`, Problema 16).
- Parametri della dashboard controllati contro i limiti: **PROBLEMA**. Oltre il limite si taglia con una nota (`risk_manager.py:77-80`,
  `:212-217`); documento illeggibile → 2x e 1% in silenzio (`main.py:616-619`); un rischio `nan` passa e dà una quantità `nan`
  approvata (provato, `prova_nan.py`; `models.py:187-196` non controlla). Le regole `firestore.rules:32-41` ripetono i limiti. Problema 17.
- Limiti propri di G1 sul demo come costanti: **OK, da segnalare**. `LEVA = 5` (`demo_binance.py:73`), `STOP_CONTO = 0.35` (`:78`),
  fuori da `hard_limits.py`; un test tiene di fatto la soglia (−34% niente, −36% chiude: `tests/test_demo_binance.py:336-352`), nessuno
  tiene la leva a 5. Nessun tetto all'esposizione né per moneta (Problema 10).
- Pulsante che chiude tutto senza Firebase: **PROBLEMA**. Demo: il file `ops/demo_binance_chiudi_tutto` (`:88`, letto a `:491`) non passa
  da Firebase, ma dopo un errore aspetta 30 minuti (`:485-486`, Problema 2), una chiusura rifiutata non si ritenta (Problema 3), e il giro
  può essere ritardato da Firebase lento (Problema 14). Vecchio bot: nessun comando a file; con Firebase muto oltre 300 secondi il
  pulsante non viene nemmeno valutato (`main.py:1568-1576` esce prima di `:1585`, Problema 8).

**B. Ordini**
- Passi e minimi dalle informazioni del simbolo: demo **OK** (`demo_binance.py:119-129`, letti a `:605`; quantità `:153`, prezzo `:157`,
  minimi `:154`), con tre note basse (Problema 22) e i filtri del conto vero da una copia fissa del 6 nov (Problema 16). Vecchio ramo
  reale **PROBLEMA**: `round(x, 6)` invece del passo (`executor.py:624`, `:701`, `:722`, `:740`, `:764-765`, `:1047`, `:1059`; Problema 7).
- Identificativo univoco e riusato nei tentativi: **PROBLEMA**. Demo, ordini limite: identificativo nuovo a ogni tentativo (`:132-138`,
  `:631`) ma gli ordini aperti si annullano e le posizioni si rileggono prima (`:615-620`): niente doppioni. Demo, ordini a mercato del
  resto: nessun identificativo e nuovo invio al tentativo dopo (`:676-685`; Problema 1, provato). Vecchio ramo: nessun identificativo
  (`executor.py:622-625`; Problema 7).
- Solo riduzione e modo di posizione: **OK**. Demo: «solo riduzione» su chiusure e riduzioni (`:158`, `:632-633`, `:374`, `:459`,
  `:566-567`, `:679-680`), una posizione per moneta controllata una volta (`:609-613`). Vecchio ramo: «solo riduzione» su stop, obiettivi e
  chiusure (`executor.py:701`, `:721`, `:739`, `:1047`, `:1059`); il modo non è controllato (in modo a due posizioni Binance rifiuta: sicuro).
- Prezzo che attiva gli stop: demo **NON APPLICABILE** (nessuno stop per posizione; lo stop sul conto usa `totalMarginBalance`, `:545`,
  `:702`). Vecchio ramo **PROBLEMA** (Medio): `STOP_MARKET` senza tipo di prezzo = ultimo prezzo (`executor.py:720-723`), mentre il bot
  gestisce le posizioni sul prezzo mark (`main.py:1455`). Problema 19.
- Leva e margine espliciti: demo **OK** (margine unico `:547-554` prima della leva `:635-640`, controllo ogni ora `:556-578`; la leva
  non si rilegge, Problema 22). Vecchio ramo: leva sì (`executor.py:621`), margine mai (Problema 19).
- Stop per posizione: G1 è a portafoglio, la protezione è lo stop sul conto (`:702`, ogni ora) e il pulsante: **esistono e i test
  passano** (`tests/test_demo_binance.py:311-352`, `:382-399`), ma con i guasti dei Problemi 2, 3 e 4. Nessuno stop su Binance per
  posizione: **decisione per Alessio** (sotto). Vecchio ramo **PROBLEMA**: uno stop rifiutato si stampa e basta (`executor.py:726-727`) e
  la riconciliazione non lo vede se c'è un obiettivo (Problema 6, provato).

**C. Stato e resilienza**
- Ricostruzione da Binance: demo **OK in parte**: posizioni sempre lette dal conto (`:541-545`), ordini aperti annullati prima di ricontare
  (`:615-620`); ma massimo dello stop, capitale ridotto e ordini in corso stanno solo in `data/demo_binance.json` (`:415-425`): un file
  perso azzera il massimo dello stop (Problema 15). Vecchio ramo: posizioni da Firebase (`executor.py:1402`), confronto con Binance
  solo con il riconciliatore, che oggi dà un falso allarme fisso (Problema 6).
- Flussi in tempo reale: demo **NON APPLICABILE** (solo richieste, ogni ora). Vecchio bot: attesa di 2 candele dopo un buco del flusso
  (`main.py:1081-1118`); la riconnessione non l'ho rivista a fondo.
- Candele chiuse: **OK**. G1 decide alle 00:05 UTC su giorni chiusi e aspetta il regolamento delle 00:00 (`f5.py:91-125`, `:516-522`);
  il vecchio bot decide al confine della candela (`main.py:1606-1610`, letto, non provato).
- Errori delle interfacce: **PROBLEMA**. Demo: nessuna gestione di 429 e 418, nessun `Retry-After` (`:290-293`), il giro continua a
  mandare ordini durante un limite di frequenza (`:634-644`); attesa fissa di 30 minuti (`:485-486`, `:536-539`), nessun tentativo
  infinito. Vecchio ramo: `error_handler.py` non è usato da nessuno (grep) e l'esecutore prende tutto con `except Exception`. Problemi 13 e 19.
- Una scrittura su Firebase che fallisce non blocca il rischio: **PROBLEMA**. `set_rtdb` non solleva mai (`firebase_client.py:652-679`),
  bene; ma il valore restituito non si guarda e un comando può restare vero (Problema 4, provato); ogni chiamata può durare fino a 120
  secondi (nessun `httpTimeout`, `firebase_client.py:420-425`; `firebase_admin` 6.5.0) nello stesso giro del demo (Problema 14).
- Orologio della macchina: **OK in parte**. Configurazione del server non nel repo; `systemd-timesyncd` attivo negli elenchi dei processi
  (`ops/results/0196-processi.md`, `ops/results/0413-1ott-processi-col-gate.md`); il codice non legge l'ora di Binance, finestra 5 secondi (`:286`).

**D. Separazione fra paper, demo e conto vero**
- Demo: **OK**. Indirizzo fisso e controllato (`demo_binance.py:64-65`, `:96-100`; test `tests/test_demo_binance.py:89-97`), chiavi sue
  (`BINANCE_DEMO_*`, `:266-272`, `:408-413`); non dipende da `DRY_RUN` per scelta (`:18-19`). Manca un log d'avvio dell'ambiente (Basso).
- Vecchio ramo reale: **PROBLEMA**. `DRY_RUN` e `BINANCE_TESTNET` valgono falso per `si`, per un errore di battitura o per un valore vuoto
  (`config.py:46-50`, `:64`, `:69`; provato); le chiavi del conto vero sono sulla macchina (`docs/backlog.md`, aggiunta del 6 nov alla voce
  del conto vero) con nome non noto; nessun rifiuto all'avvio di combinazioni pericolose. Log d'avvio presente (`main.py:2519`, `:2532`,
  `executor.py:251-252`). Problema 5.

**E. Segreti e sicurezza**
- Nessuna chiave nel codice o nei file versionati del percorso: **OK** (letti; le chiavi arrivano dall'ambiente). Errori con l'indirizzo
  firmato scritti su Firebase e nel log (`demo_binance.py:536-539`): Basso, Problema 21.
- Chiavi senza prelievo e limitate all'indirizzo della macchina: **da confermare con Alessio** (per il demo il backlog dice «niente prelievi»).
- Regole di Firebase: utente ancora `REPLACE_WITH_YOUR_FIREBASE_UID` (`firestore.rules:27`, `database.rules.json:3-24`): **da confermare
  con Alessio** quali sono pubblicate. I comandi del demo accettano solo vero o falso (`database.rules.json:18-25`): OK.

**F. Test**: **OK con lacune**. Comando: `python3 -m pytest tests/ -q -x --no-header` (le due opzioni in più fermano al primo errore e
tolgono l'intestazione). Esito: `2545 passed in 145.92s`, nessun fallimento, nessun saltato. Mancano i test dei guasti a-g qui sotto,
della leva 5 del demo e della lettura di `DRY_RUN`.

### Problemi

**Problema 1 — Alto — `bot/portafoglio/demo_binance.py:665-694` (con `:536-539`): il resto a mercato si rimanda due volte dopo un errore a metà giro.**
- Scenario (provato, prova a): un'ora dopo il ribilancio `chiudi_ordini` manda a mercato il resto di BUSDT; la lettura dell'ordine dopo
  (CUSDT) va in timeout. L'eccezione non è un `RuntimeError`, esce da `tick`, lo stato non si salva e `st["ordini"]` resta. Al tentativo
  dopo (30 minuti) BUSDT risulta annullato con 0 eseguito e il resto parte di nuovo: inviati `BUSDT BUY 99.986` due volte. Lo stesso con un
  `DELETE` rifiutato perché l'ordine si è appena eseguito (`:675` non è protetto). Sul conto vero: posizione doppia, esposizione oltre il 200%.
- Correzione suggerita: calcolare il resto dalla posizione vera (conto) contro l'obiettivo, non dalla quantità pianificata; dare agli
  ordini a mercato un identificativo fisso per ordine e giorno, controllarlo prima di rimandare; salvare lo stato dopo ogni ordine; test con un timeout a metà.

**Problema 2 — Alto — `demo_binance.py:485-486`, `:530-531`, `:75-76`: dopo un errore il pulsante e lo stop sul conto aspettano 30 minuti; lo stop si guarda solo ogni ora.**
- Scenario (provato, prova b): un errore di rete qualsiasi; il proprietario scrive il comando chiudi tutto: per 29,5 minuti nessuna
  chiamata a Binance, poi chiude. Il controllo dell'attesa è prima del pulsante. Lo stop sul conto si valuta solo in `valuta`, ogni ora.
- Correzione: pulsante e stop sul conto a ogni giro, prima e fuori dall'attesa dopo gli errori (lettura del conto leggera); l'attesa vale solo per il ribilancio.

**Problema 3 — Alto — `demo_binance.py:452-471`, `:497-513`: chiudi tutto e stop sul conto non garantiscono il conto vuoto.**
- Scenario (provato, prova c): pulsante premuto, la chiusura di BUSDT rifiutata (per esempio 429): il demo scrive «fermo», l'errore va su
  Firebase, e dopo 4 ore la posizione è ancora aperta; da fermo il codice valuta solo il valore del conto. Lo stesso dopo lo stop a −35%.
  Un errore sull'annullo degli ordini (`:454-455`) ferma tutto prima delle chiusure.
- Correzione: da fermo, a ogni giro, rileggere le posizioni e richiudere quelle rimaste, fino a zero; allarme se dopo qualche tentativo non è vuoto; test.

**Problema 4 — Alto — `demo_binance.py:498-505` (`firebase_client.py:652-679`): un «riparti» rimasto vero riaccende il demo subito dopo lo stop sul conto.**
- Scenario (provato, prova d): «riparti» eseguito, ma la scrittura del falso su Firebase fallisce (`set_rtdb` restituisce `False`, nessuno lo
  guarda). Giorni dopo lo stop sul conto chiude tutto a −40%: 30 secondi dopo il demo legge ancora «riparti» vero, riparte e rimanda gli
  ordini. Lo stop sul conto è annullato senza che nessuno l'abbia deciso.
- Correzione: un comando vale una volta per un identificativo nuovo (ora o numero scritto dalla dashboard, come il file), oppure si
  consuma solo se la scrittura è confermata; test con la scrittura che fallisce.

**Problema 5 — Alto — `bot/config.py:46-50`, `:64`, `:69`: `DRY_RUN` e `BINANCE_TESTNET` letti in modo che un valore sbagliato vale falso.**
- Scenario (provato, prova g): `DRY_RUN=si`, `DRY_RUN=treu` o `DRY_RUN=` vuoto danno falso; lo stesso per `BINANCE_TESTNET`. Con le chiavi
  del conto vero sulla macchina (se si chiamano `BINANCE_API_KEY`/`BINANCE_API_SECRET`, `executor.py:247-249`) il vecchio esecutore
  manderebbe ordini veri al conto vero con un errore di battitura nel `.env` o in `tuning.env` (caricato sopra, `config.py:35`).
- Correzione: per `DRY_RUN` solo un valore esatto e voluto (per esempio `false` scritto per intero) spegne il paper; tutto il resto vale
  vero, con un avviso; lo stesso per la rete di prova; `tuning.env` con l'elenco delle chiavi ammesse; test.

**Problema 6 — Alto (vecchio ramo reale, oggi spento) — `bot/main.py:1215-1226`, `bot/execution/reconciler.py:113-120`, `main.py:1578-1585`: la riconciliazione vede un doppione in ogni posizione protetta, salta il pulsante e non vede lo stop mancante.**
- Scenario (provato, prove e ed f): una posizione con stop e obiettivo ha due ordini di protezione, contati come «ordine duplicato» critico:
  nuove aperture bloccate per sempre e, siccome `trading_cycle` esce a `:1578` prima di `:1585`, il pulsante che chiude tutto non viene mai
  valutato. Al contrario, una posizione con l'obiettivo ma con lo stop rifiutato risulta protetta (nessun allarme).
- Correzione: contare a parte stop e obiettivi; doppione = due stop sulla stessa posizione; allarme se manca lo stop; il pulsante prima di ogni uscita anticipata; test con gli ordini veri.

**Problema 7 — Alto (vecchio ramo reale, oggi spento) — `bot/execution/executor.py:621-636`, `:673-675`, `:719-726`, `:1054-1069`, `:1093`: ordini non arrotondati, senza identificativo, e chiusure che possono lasciare posizioni scoperte.**
- Scenario: lo stop calcolato dalla strategia con 6 decimali viene rifiutato (passo di prezzo), la posizione resta su Binance senza stop
  (solo una stampa). Un timeout sull'ingresso o sulla lettura dell'ordine fa credere «nessun ingresso» mentre l'ordine si esegue: posizione
  sconosciuta e senza stop. Una chiusura rifiutata toglie comunque la posizione dallo stato e annulla i suoi stop: posizione aperta, scoperta, ignota al bot.
- Correzione: arrotondare a passo e passo di prezzo da `exchangeInfo`; identificativo per ordine; dopo un errore rileggere l'ordine; togliere
  la posizione solo con la chiusura confermata. Oppure ritirare questo ramo reale (decisione per Alessio).

**Problema 8 — Alto (vecchio ramo reale, oggi spento) — `bot/main.py:1559-1585`: il pulsante del vecchio bot non viene valutato con Firebase muto, dopo un buco del flusso o con la riconciliazione che blocca, e non ha un comando a file.**
- Scenario: Firebase non risponde da oltre 5 minuti; il proprietario preme STOP: il comando non arriva e, anche con lo specchio in memoria,
  `trading_cycle` esce a `:1568-1576` prima di leggerlo. Dopo un buco del flusso prezzi lo stesso per due candele (`:1559-1566`).
- Correzione: valutare il pulsante per primo; aggiungere un comando a file come il demo.

**Problema 9 — Alto, preesistente — `bot/config.py:672`, `bot/risk/circuit_breakers.py:50-52`, `bot/main.py:1741`: la parità col backtest spegne tutti i fermi e il tetto delle posizioni, e niente ne vieta l'uso con soldi veri.**
- Già nel rapporto del 7 nov (problema 5) e nel backlog (voce del conto vero, aggiunta del 6 nov). Correzione: avvio rifiutato con `DRY_RUN` falso e parità accesa, con log chiaro.

**Problema 10 — Medio — `demo_binance.py:516-520`, `:141-160`, `:73`, `:78`: i pesi di G1 vanno a Binance senza un controllo indipendente.** Nessun controllo che i
pesi siano finiti, che la somma dei valori assoluti non superi 2 (200%), che una moneta non pesi troppo (il backlog cita una moneta al
47,8%), che ogni lato abbia abbastanza monete; leva e stop fuori da `hard_limits.py`. Scenario: un errore nel paper (`f5.py:128-156`) o un
file `data/paper_g1.json` sbagliato porta il conto oltre il 200%. Correzione: controllo prima degli ordini, con rifiuto e allarme; costanti in `hard_limits.py` con test di guardia.

**Problema 11 — Medio — `demo_binance.py` (nessun avviso): stop, pulsante, rifiuti e scarti finiscono solo su Firebase e nel log.** Il modulo non usa
`TelegramNotifier` (`bot/execution/notifier.py`). Scenario: lo stop a −35% scatta di notte e nessuno lo sa fino alla dashboard. Correzione: avviso per stop, pulsante, chiusure non riuscite, rifiuti, scarti oltre soglia.

**Problema 12 — Medio — `demo_binance.py:516-523`: nessun controllo sull'età della decisione di G1.** Se il paper di G1 si ferma (interruttore tolto,
dati di Binance assenti per giorni) il demo tiene le stesse posizioni senza limite e senza avviso. Correzione: decisione più vecchia di circa 30 ore → allarme e niente ordini nuovi.

**Problema 13 — Medio — `demo_binance.py:290-293`, `:634-644`: i limiti di frequenza non sono gestiti.** Un 429 diventa un rifiuto e il ciclo manda
l'ordine dopo; nessun `Retry-After`; rischio di blocco 418 dell'indirizzo, che fermerebbe anche pulsante e stop. Correzione: al primo 429 o 418 fermare il giro, aspettare quanto dice Binance, riprendere.

**Problema 14 — Medio — `bot/main.py:2589-2653`, `bot/core/firebase_client.py:420-425`: il demo gira nello stesso giro del vecchio sistema e dopo di lui.**
Scansione, ciclo del vecchio bot e ogni chiamata a Firebase (fino a 120 secondi l'una) ritardano pulsante e stop del demo; non c'è un
battito del demo. Correzione: per il conto vero un processo o un filo suo, con battito suo e un tempo massimo breve per Firebase.

**Problema 15 — Medio — `demo_binance.py:415-419`, `:701`: il massimo dello stop sul conto vive solo in un file locale.** Un file perso o illeggibile
(`carica` restituisce `{}`) fa ripartire il massimo dal valore di adesso: lo stop si allontana. Correzione: tenerlo anche su Firebase e usare il più alto dei due.

**Problema 16 — Medio — `demo_binance.py:321-329`, `:92`, `:183-203`: capitale senza tetto e filtri del conto vero fissi.** Qualunque numero positivo nel
file `ops/demo_binance_capitale` diventa il capitale, senza confronto con il saldo; i filtri del conto vero sono una copia del 6 nov
(`filtri_conto_vero.json`). Per il conto vero: capitale non oltre il saldo e non oltre un tetto scritto nel codice; filtri letti dal conto vero a ogni ribilancio.

**Problema 17 — Medio, in parte preesistente — `bot/core/models.py:187-196`, `bot/risk/risk_manager.py:63-94`, `:212-217`, `bot/main.py:616-619`: parametri della dashboard.**
Un rischio `nan` dà un ordine approvato con quantità `nan` (provato); fuori limite si taglia con una nota invece di rifiutare con un allarme; documento illeggibile → valori predefiniti in silenzio. Correzione: rifiuto con allarme, test.

**Problema 18 — Medio — `bot/main.py:1240-1246`, `bot/execution/executor.py:1101-1110`: la chiusura d'emergenza di una moneta chiude tutte le posizioni.** `force_close_all` gira su tutte; le altre si registrano al prezzo d'ingresso. Correzione: chiudere solo quella moneta.

**Problema 19 — Medio — `bot/execution/executor.py:621`, `:720-723`, `:746-778`; `bot/execution/error_handler.py`: vecchio ramo reale.** Margine mai impostato; stop
sull'ultimo prezzo mentre il bot ragiona sul mark; spostare lo stop è annulla-e-rimetti (finestra scoperta); la classificazione degli errori esiste ma non è usata.

**Problema 20 — Medio, preesistente — `bot/config.py:176`, `:181`, `:707`, `:35`: limiti del vecchio bot in variabili d'ambiente.** Tetto delle posizioni (5), quota per posizione (1,0 = nessuna), stop massimo (6%), senza limiti fissi sopra; `tuning.env` sovrascrive tutto.

**Problema 21 — Basso — `demo_binance.py:536-539`: messaggi d'errore con l'indirizzo firmato su Firebase e nel log.** Non è la chiave (la firma vale pochi secondi), ma per il conto vero meglio scrivere solo metodo, percorso e codice.

**Problema 22 — Basso — `demo_binance.py:126`, `:374`, `:459`, `:566`, `:678`, `:635-640`.** Valore minimo predefinito 5 scritto a mano se manca il filtro; gli ordini a mercato usano il passo degli ordini limite (`MARKET_LOT_SIZE` e quantità massima ignorati); la leva si imposta una volta e non si rilegge; nessun log d'avvio dell'ambiente.

**Problema 23 — Basso — `demo_binance.py:502`: «riparti» riparte con il massimo di adesso.** Dopo uno stop a −35% e una ripartenza se ne può perdere un altro 35%: la perdita totale non ha un limite. Decisione per Alessio.

**Problema 24 — Basso, preesistente — `bot/main.py:270`, `:1173-1174`; `bot/risk/circuit_breakers.py:88`.** `day_pnl_pct` non esiste (il campo è `state.daily_pnl_pct`); la nota dice «4h» per una pausa di 2 ore.

### Invarianti modificati

Nessuno nel codice da `b29f5713` (7 nov): solo documenti e `reviews/`. Mappati per la prima volta (non cambiati): leva del demo 5
(`demo_binance.py:73`), stop sul conto −35% dal massimo, ogni ora (`:78`, `:702`), pulsante a file e da dashboard (`:84-89`), margine unico
(`:547-554`), una posizione per moneta (`:609-613`), capitale ridotto dal file (`:91`, oggi `1000` in `ops/demo_binance_capitale`).

### Decisioni per Alessio

1. **Stop per posizione su Binance per G1**: oggi non ci sono; proteggono solo lo stop sul conto (del bot, ogni ora) e il pulsante. Se la
   macchina è spenta, sul conto vero resta solo la liquidazione di Binance: va accettato, e conviene tenere nel portafoglio dei future solo il capitale.
2. **Stop sul conto**: −35% dal massimo va bene anche per i soldi veri (il backlog proponeva −20% o −30%)? Deve contare dal massimo di
   sempre o ripartire dopo «riparti»? Serve anche un pavimento sul capitale iniziale?
3. **Limiti da aggiungere come costanti con test di guardia** (in `hard_limits.py` o in un file fisso del conto vero): leva 5, stop sul
   conto, esposizione lorda massima 200%, tetto per moneta e numero minimo di monete per lato (da rimisurare sul passato, come dice il
   backlog), capitale massimo, età massima della decisione di G1.
4. **Il vecchio ramo reale** (`bot/execution/executor.py`, `DRY_RUN` falso): va tenuto? Il conto vero nascerà da G1. Se non serve, meglio
   toglierlo o chiuderlo con un blocco esplicito, così le chiavi vere non hanno un secondo percorso.
5. **«Riparti» con un clic** sulla dashboard dopo uno stop: va bene per i soldi veri o serve una conferma?
6. **Fuori dal codice, da confermare**: chiavi (demo e vero) senza prelievo e limitate all'indirizzo della macchina; quali regole di
   Firebase sono pubblicate (nei file c'è ancora l'utente segnaposto).

**Cosa deve avere il futuro codice del conto vero** (voce del conto vero del backlog e sue aggiunte, più quanto trovato qui):
- *Separazione*: modulo suo, chiavi con nome suo (mai `BINANCE_DEMO_*`), interruttore suo, indirizzo vero ammesso solo lì; il demo continua a
  rifiutare ogni altro indirizzo. Avvio rifiutato se `DRY_RUN` non è il valore esatto voluto, se la parità col backtest è accesa, se
  manca la frase del proprietario nell'interruttore; log e avviso d'avvio con ambiente e capitale.
- *Capitale*: tetto scritto nel codice; capitale non oltre il saldo vero dei future; primo ingresso solo alla mezzanotte, dal conto vuoto
  (aggiunta del 7 nov); prelievi regolari (rischio della borsa, aggiunta del 30 ott).
- *Ordini*: filtri letti dal conto vero a ogni ribilancio (anche `MARKET_LOT_SIZE` e quantità massima); identificativo fisso per ordine,
  riusato e controllato prima di ogni nuovo invio; resto calcolato dalla posizione vera; «solo riduzione» su chiusure; margine unico, leva
  e una posizione per moneta riletti ogni ora.
- *Protezioni*: pulsante (file e dashboard) e stop sul conto a ogni giro, mai dietro un'attesa; chiudi tutto ritentato fino al conto
  vuoto, con allarme; comandi validi una volta sola (Problema 4); controllo dei pesi (finiti, 200%, tetto per moneta, monete per lato)
  con rifiuto e allarme; confronto ogni giorno fra posizioni vere e pesi (aggiunta del 1° nov), con allarme.
- *Resilienza*: stato di Binance per primo all'avvio; massimo dello stop non perdibile; 429 e 418 con l'attesa di Binance; ora di Binance
  in caso di errore d'orario; processo o filo suo con battito suo; tempo massimo breve per Firebase.
- *Avvisi*: Telegram per stop, pulsante, chiusure non riuscite, rifiuti, scarti, errori ripetuti.
- *Test*: un Binance finto con ogni guasto di questo rapporto (prove a-g); prima di ogni ordine vero una lettura del conto vero; partenza con il capitale minimo.

### Domande aperte

1. Con quale nome sono nel `.env` della macchina le chiavi del conto vero? Se sono `BINANCE_API_KEY` e `BINANCE_API_SECRET`, il vecchio
   esecutore le usa appena `DRY_RUN` vale falso (e la rete di prova è spenta): è il motivo per cui il Problema 5 è Alto.
2. Che valori hanno oggi sulla macchina `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY`, e il vecchio paper è fermo con lo STOP? Si vede
   solo dalla macchina (una richiesta in `ops/`, che il mio perimetro non mi fa scrivere: la deve mettere la sessione principale).
3. La modifica proposta del rapporto del 7 nov (leva 10, perdita giornaliera dalla dashboard) non è nel codice: la voce resta aperta o si chiude come «non applicata»?
