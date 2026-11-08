# Revisione: fase 2 del conto vero (G1 su `fapi.binance.com`, nato spento) — 8 novembre 2026

## Riepilogo e verdetto

**REQUEST CHANGES.** Nessun Bloccante, 2 Alti (53, 54), 6 Medi (55-60), 3 Bassi (61-63).

Il codice nuovo fa quello che la specifica chiede nel caso normale: parla solo con `fapi.binance.com`, con `DRY_RUN` vero o senza
interruttore non fa nessuna richiesta e non legge le chiavi, senza il tag o senza un capitale valido non apre niente (il freno del
cliente rifiuta ogni ordine che non sia «solo riduzione»), compra solo alla decisione di G1 dopo l'accensione, usa i filtri veri,
ha limiti come costanti con un test di guardia, niente eventi. Il demo non cambia comportamento (verificato riga per riga e con i
suoi test, che passano tutti con il solo attributo `HOST` aggiunto al finto). Con `DRY_RUN` falso niente fuori da `ContoVeroG1` può
mandare ordini o chiudere posizioni sul conto vero (domanda 6, sotto).

Non va però verso i soldi veri così com'è: spegnere il conto vero con le posizioni aperte toglie ogni protezione e con `DRY_RUN`
falso senza interruttore il bot non riparte (53); il «codice approvato» non copre tutto il codice dei soldi veri e il tag lo
sposta chiunque spinga (54). Più sei Medi (55-60, quasi tutti provati con il Binance finto o con git).

Oggi il rischio di caricare questo codice è basso (interruttore assente, `DRY_RUN` vero: il conto vero scrive solo «spento» una
volta per avvio), ma **non è approvato per il commit né per un riavvio**.

## Oggetto

- Branch `claude/brave-albattani-1b12fv`, modifiche **non committate** su HEAD `8ec65db` (codice del percorso = `1a8522f`, fase 1
  in funzione dalle 19:02 UTC; il `1a8522f` è identico alla copia rivista al quarto giro, `fase1/giro4/`, verificato con `diff`).
- File: `bot/portafoglio/conto_vero.py` (nuovo, 310 righe); `demo_binance.py` (attributi di classe, `_ordini_nuovi_ammessi`
  `:852-855`, `_ordini_del_giro` `:857-887`, `_filtri_degli_ordini` `:1274-1287`, `_ambiente` `:932-938`); `config.py` (`:787-813`);
  `main.py` (`:43`, `:503-506`, `:2651-2654`); `state_snapshot.py` (`:675-703`); `tests/test_conto_vero.py` (nuovo, 18 funzioni,
  31 casi); `tests/test_sicurezza_avvio.py`; `tests/test_demo_binance.py` (`:34`, `:52`).
- Le righe citate sono del working tree. Non toccati: `bot/risk/`, `bot/execution/`, `firebase/`, `dashboard/`, `ops/`, `scripts/ops_agent.py`.
- Invarianti coinvolti: separazione paper/demo/conto vero, avvio con `DRY_RUN` falso; nuovi: limiti, pulsante, stop e codice approvato.

## Checklist A–F

### A. Limiti fissi e interruttori
- **Valori fissi di `hard_limits.py` invariati: OK.** `git diff HEAD -- bot/risk` vuoto; `MAX_LEVERAGE = 5.0` `:17`,
  `MAX_RISK_PER_TRADE = 0.03` `:18`, `DAILY_LOSS_LIMIT = 0.05` `:21`, `CONSECUTIVE_SL_LIMIT = 6` `:25` (la mappa diceva `:16`: righe
  corrette di uno). Test di guardia `tests/test_risk.py`, `tests/test_sizing.py` passati.
- **Nessun limite critico in configurazione, ambiente o Firebase: OK.** Limiti del conto vero come costanti `conto_vero.py:70-77`
  (leva 5, capitale 300, valore 600, stop 35%, pavimento 65%, pesi 200%, peso 60%, età 26 ore), riportati sulla classe `:143-146`,
  fissati da `tests/test_conto_vero.py:67-87`; il codice ereditato usa quelli della classe (`demo_binance.py:534-537`, `:567`,
  `:871-872`, `:922`, `:1065`, `:1229-1232`, `:1331`; prova `test_la_leva_e_quella_della_classe_del_conto_vero`). Il capitale viene da
  un file (`ops/conto_vero_capitale`) ma è tagliato dalla costante 300 (`demo_binance.py:567`). Versamenti fino a 600: problema 58.
- **Parametri della dashboard controllati: NON APPLICABILE** (il conto vero non legge `user_risk_settings`; vecchio bot invariato,
  punti 17 e 20 del primo avvio ancora aperti).
- **Limiti propri di G1 come costanti: OK, fuori da `hard_limits.py`** (come il demo): stanno in `conto_vero.py`, dentro i percorsi
  del tag, con test di guardia. Da confermare con Alessio (decisione 3).
- **Pulsante che chiude tutto senza Firebase: PROBLEMA.** Il file `ops/conto_vero_chiudi_tutto` funziona anche senza Firebase e
  anche con il codice bloccato (prova p6 e `test_codice_diverso_dal_tag_niente_ordini_nuovi_ma_stop_e_pulsante`), ma **non funziona
  per niente con l'interruttore tolto o `DRY_RUN` vero** (`conto_vero.py:187-191`; prova p1: 0 richieste, posizioni ancora aperte):
  problema 53. Nessun pulsante in dashboard e nessuna regola per i due comandi: problema 60.

### B. Ordini
- **Passi, minimi, valori dalle informazioni del simbolo: OK.** `conto_vero.py:293-302`: solo `exchangeInfo` di `fapi.binance.com`,
  riletto a ogni ribilancio e a ogni resto a mercato, mai la copia fissa; senza filtri leggibili errore e niente ordini. Prova
  `test_filtri_dal_vero_exchange_info_riletti_ogni_giorno` (passo cambiato da un giorno all'altro).
- **Identificativo univoco e riusato: OK (come il demo approvato).** Resti a mercato con `id_mercato` fisso e controllato prima
  dell'invio (`demo_binance.py:1409-1410`); ordini limite con un identificativo nuovo a ogni tentativo, dopo l'annullo degli aperti e
  la rilettura delle posizioni (`:1301-1306`, `:1323`). Un guasto di rete nel primo ribilancio costa commissioni: problema 62.
- **Chiusure con «solo riduzione», modo delle posizioni: OK.** `_chiudi_moneta` `:1120-1121`; una posizione per moneta impostata al
  primo ribilancio (`:1295-1299`) e riletta ogni ora (`:1236-1242`). Il freno del cliente lascia passare solo «solo riduzione»
  (`conto_vero.py:130-134`). Il modo del conto vero di Alessio va confermato (domanda 3).
- **Prezzo che attiva lo stop: OK, da tenere presente.** Lo stop è sul valore del conto (`totalMarginBalance`, prezzi mark,
  `demo_binance.py:1190-1197`), controllato a ogni giro (al massimo ogni minuto). La coerenza con la prova la giudica backtest-auditor.
- **Leva e margine espliciti: OK.** Margine unico e leva della classe prima del primo ordine di ogni moneta (`:1327-1332`), riletti
  ogni ora (`:1208-1249`). Modalità «multi-assets» e «portfolio margin» non controllate: domanda 3.
- **Stop per posizione: NON APPLICABILE (strategia a portafoglio).** Protezione = stop sul conto (`demo_binance.py:961-967`,
  `:1441-1442`; livello `:230-234`) e pulsante; esistono e funzionano con il conto acceso, anche con il codice bloccato; non con il
  conto spento (53). L'assenza di stop per posizione resta una decisione di Alessio.

### C. Stato e resilienza
- **Stato di Binance che prevale: OK in parte.** Posizioni e ordini riletti da Binance a ogni stop, ribilancio, resto e chiusura;
  ma il fermo vive solo nel file locale: con il file perso o rotto il conto riapre alla mezzanotte senza «riparti» (problema 57).
- **Flussi in tempo reale: NON APPLICABILE** (solo richieste REST).
- **Candele chiuse: OK** (decisione di G1 alle 00:05 UTC su giorni chiusi, `f5.py`; età massima 26 ore `conto_vero.py:77`).
- **429, 418, errori d'orario, margine insufficiente: OK** (ereditati, `demo_binance.py:455-495`, `:889-911`). Nota: il conto vero
  condivide il limite per indirizzo di `fapi.binance.com` con gli scaricamenti pubblici dei paper (`f5.py:47`, `:163-168`, pausa 0,1 s),
  e alla mezzanotte gira dopo di loro nello stesso filo (problema 14 del primo avvio, aperto): lo stop «ogni minuto» lì può tardare di
  minuti. Un 418 provocato dai paper fermerebbe anche le protezioni del conto vero.
- **Firebase che fallisce: OK** (`set_rtdb` non solleva; comandi letti con `try`), con la vecchia nota che una chiamata può durare
  fino a 120 secondi (mappa, sezione 2).
- **Orologio: OK** (`-1021` con l'ora di Binance; `systemd-timesyncd` attivo negli elenchi dei processi).

### D. Separazione fra paper, demo e conto vero
- **In paper e sul demo nessun ordine al conto vero: OK.** Senza interruttore o con `DRY_RUN` vero nessuna richiesta e nessuna chiave
  letta (`conto_vero.py:173-191`; `test_senza_una_delle_quattro_condizioni_nessun_ordine`, `finto.chiamate == []`;
  `test_le_chiavi_del_conto_vero_non_si_leggono_da_spento`). `DRY_RUN` letto con `_get_bool_sicuro` (solo «false» lo spegne). Il
  client del demo resta sul demo (`demo_binance.py:116-120`), quello vero solo su `https://fapi.binance.com` (`conto_vero.py:80-85`,
  rifiuta `http`, altri host, `@`), e `ContoVeroG1` rifiuta il client del demo (`:153-154`). Stati, rami, comandi e file separati
  (test `:83-87`).
- **Controllo all'avvio: OK con un invariante cambiato.** `controlla_avvio` (`config.py:801-813`) con `DRY_RUN` falso ora parte, se
  la parità è spenta e c'è l'interruttore, e lo scrive nel log; senza interruttore rifiuta (che è però la seconda metà del 53).
- **Domanda 6 (cosa cambia con `DRY_RUN` falso nel vecchio sistema): nessun ordine e nessuna chiusura sul conto vero fuori da
  `ContoVeroG1`.** Il vecchio esecutore non crea il client e rimette `dry_run` vero (`executor.py:244-254`); tutte le sue chiamate a
  Binance passano da `self.dry_run`/`self._client` (`:620-761`, `:1036-1070`). Il riconciliatore parte (`reconciler.py:230-239`,
  `main.py:2520`), ma `_exchange_state` senza client dà «irraggiungibile» (`main.py:1209-1210`) e allora `reconcile` restituisce solo
  `exchange_down`/`wait`, non critico, prima di ogni altra regola (`reconciler.py:93-100`); `_apply_reconciliation` agisce solo su
  `CLOSE_NOW` e `DROP_LOCAL` con una moneta (`main.py:1240-1260`) e comunque solo sul vecchio paper. `ops/gate_fermo` ferma solo la
  ricerca del gate (`bot/core/gate_fermo.py:1-17`), non il giro del vecchio bot. Effetti visibili: `/reconciliation` scritto ogni 60
  secondi da un filo in più; un Telegram «exchange_down» ogni 5 minuti se il vecchio paper ha posizioni (`reconciler.py:210-227`,
  `config.py:673-674`); le operazioni del vecchio paper annunciate «🔴 LIVE» (`main.py:1447`, `:1493`, `:1553`, `:1981`);
  `/bot_status/dry_run` falso; il paper esplorativo del vecchio bot spento (`adaptation.py:427`); la testata della dashboard dice
  sempre «DRY_RUN · paper» (`DashboardShell.tsx:416-419`). Nessuno di questi manda ordini.

### E. Segreti e sicurezza
- **Nessuna chiave nel codice, nei log, negli errori, su Firebase: OK.** Chiavi da `BINANCE_API_KEY`/`BINANCE_API_SECRET`
  nell'ambiente (`conto_vero.py:63`, `:180-185`), lette solo acceso; i testi di errore senza la firma (`senza_firma`); i test usano
  testi finti. `ops/conto_vero_capitale` sarebbe pubblico (non è un segreto).
- **Chiave senza prelievo e limitata all'indirizzo: da confermare con Alessio** (il 7 novembre non era limitata; `docs/conto_vero.md:20-24`).
- **Regole di Firebase: da confermare con Alessio** (mai pubblicate; nel repo `REPLACE_WITH_YOUR_FIREBASE_UID` e nessuna regola per
  `/commands/conto_vero_*`): con le regole aperte chiunque riaccende il conto vero dopo uno stop (problema 60).
- **Chi controlla l'interruttore, il capitale e il tag**: chiunque spinga sul branch (anche le sessioni): problema 54 e decisione 2.

### F. Test
- `python3 -m pytest tests/ -q`: **2656 passed, 1 failed** in 211 s; il fallito è `test_firma_dei_tre_tipi_di_chiave` (libreria
  `cryptography` del contenitore rotta: `_cffi_backend` mancante), che con
  `PYTHONPATH=/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/cripto` passa (1 passed).
- Mirati (conto vero, demo, avvio, limiti fissi, pulsante, strategie accese): 169 passed + il test della firma a parte.
- Coperti: le quattro condizioni, chiavi, partenza alla decisione dopo, leva della classe, pesi, codice diverso dal tag con stop e
  pulsante, codice dell'avvio, capitale, versamento oltre 600, filtri veri, freno del cliente, git e tag veri, avvio.
- **Non coperti**: conto spento con posizioni (53), conto a metà dopo un blocco (56), stato perso dopo un fermo (57), versamenti
  sotto 600 e prelievi (58), posizioni non del bot (59), il tag sulla macchina (55), il conto vero insieme al demo nel giro di
  `main.py` (solo un controllo sul testo, `tests/test_conto_vero.py:375-380`).
- Prove a mano: `fase2/prove_fase2*.py` (p1-p9) e `fase2/git_tag/` nella cartella di lavoro; esiti citati nei problemi.

## Problemi

### 53 — Alto — Spegnere il conto vero con le posizioni aperte toglie ogni protezione; con `DRY_RUN` falso senza interruttore il bot non riparte (domande 1 e 7)
- Dove: `conto_vero.py:187-191` (senza interruttore o con `DRY_RUN` vero `tick` esce prima di `DemoG1.tick`: niente stop, niente
  pulsante, niente chiusure da fermo), `:197-214` (lo scrive: «da spento il bot non le protegge»), `config.py:804-809`.
- Prova p1: posizioni aperte, interruttore tolto, valore del conto a 100 (stop a 182), file `chiudi` scritto: **0 richieste**,
  posizioni ancora aperte. Prova p1b: stesso esito rimettendo `DRY_RUN` vero.
- Scenario: G1 gira con 280 USDT e 38 posizioni; Alessio, o una sessione a cui ha chiesto «spegni il conto vero», toglie
  `ops/conto_vero_acceso` con un commit; un minuto dopo la macchina lo scarica e il conto vero smette di leggere conto, stop e pulsante
  (dashboard e file). Un crollo del mercato porta il conto oltre il −35% senza che il bot chiuda: resta solo la liquidazione di
  Binance, fino a tutto il portafoglio dei future. Al primo riavvio (un crash: `Restart=always`) `controlla_avvio` rifiuta l'avvio
  perché `DRY_RUN` è falso senza interruttore: il servizio riparte e si ferma ogni 10 secondi, **si fermano anche il demo e i paper
  F5, G1, G11, G1 neutra ed eventi** (contro la decisione dell'8 novembre) e il conto vero resta scoperto.
- Correzione suggerita: l'interruttore e `DRY_RUN` fermano solo gli **ordini nuovi**; finché Binance non dice il conto vuoto
  (posizioni e ordini) restano attivi stop, pulsante (Firebase e file) e chiusure da fermo, con soli ordini «solo riduzione» e annulli
  (il freno del cliente c'è già), con un allarme «conto vero spento con posizioni aperte»; spento del tutto solo dopo il «vuoto». In
  `controlla_avvio`, con `DRY_RUN` falso e senza interruttore, non uscire: avviare con il conto vero in sole protezioni e tutto il
  resto acceso, con un log chiaro. Test: interruttore tolto con posizioni → lo stop e il pulsante a file chiudono; avvio con `DRY_RUN`
  falso senza interruttore → non esce e il demo gira. Con `DRY_RUN` vero le sole protezioni sono ordini al conto vero mentre il bot è
  «in paper»: va deciso da Alessio (decisione 1).

### 54 — Alto — Il «codice approvato» non copre tutto il codice dei soldi veri e il tag lo sposta chiunque possa spingere
- Dove: `conto_vero.py:65` (`PERCORSI_DEGLI_ORDINI`: 5 percorsi), `:88-113`; `.claude/settings.json:84-90` (nessuna regola su tag);
  nessuna protezione del tag nel repository.
- (i) Fuori dal controllo restano file che decidono gli ordini veri: `research/programma6/esclusi.py` (l'elenco delle monete escluse
  dall'universo di G1, importato da `bot/portafoglio/f5.py:41` e usato a `:201`), `bot/core/firebase_client.py` (lettura dei comandi,
  conferma del «riparti»), e ogni altro modulo caricato nello stesso processo (`bot/core`, `bot/agents`, `bot/learning`,
  `bot/orchestrator`), che ha nell'ambiente le chiavi vere (`config.py:108-109`, `load_dotenv`).
- (ii) Il tag `conto-vero-approvato` lo crea o lo sposta chiunque possa spingere sul repository, comprese le sessioni (`git tag -f`,
  `git push -f origin conto-vero-approvato`): «si sposta solo con l'ok del proprietario» è una regola scritta, non un controllo.
- Scenario (i): una sessione toglie `XAUUSDT` o `TSLAUSDT` da `esclusi.py` per una prova del paper; il conto vero non si blocca e alla
  mezzanotte G1 può comprare con soldi veri contratti che la ricerca non ha mai provato. Scenario (ii): una sessione, per sbloccare il
  conto vero dopo una sua modifica, sposta il tag da sola; codice mai rivisto manda ordini veri (oggi il tag non arriva sulla macchina,
  problema 55, ma la correzione di quel problema apre proprio questa strada).
- Correzione suggerita: confrontare con il tag **tutti i file del repository caricati nel processo** (i `__file__` di `sys.modules`
  dentro la radice, più i file di dati che il percorso legge, come `filtri_conto_vero.json`), alla partenza e poi ogni minuto; un tag
  **firmato** con una chiave che ha solo Alessio e verificato dal bot (`git verify-tag` con la sua chiave pubblica sulla macchina),
  oppure una regola di GitHub per cui solo lui può creare o spostare quel tag (basta solo se la sessione non spinge con la sua stessa
  identità: domanda 1).

### 55 — Medio — La macchina non scarica il tag e non lo sposta (domanda 5)
- Dove: `scripts/ops_agent.py:473` (`git fetch origin <branch>`), `:474`.
- Prova (`fase2/git_tag/`, git 2.43): dopo `git fetch origin <branch>` il tag non c'è; `git fetch origin` porta un tag nuovo ma non
  sposta quello già presente quando il remoto lo sposta.
- Scenario: Alessio approva, il tag viene spinto, il conto vero resta per sempre con l'allarme «manca il tag conto-vero-approvato» (o
  con il tag vecchio dopo uno spostamento): niente ordini, senza un perché chiaro. Nessun rischio per i soldi (resta chiuso), ma la
  fase 4 fallirebbe e la correzione più ovvia, `fetch --tags --force` ogni minuto, senza il 54 (ii) rende il tag spostabile da chiunque.
- Correzione suggerita: un passo esplicito che porta il tag (firmato) sulla macchina, deciso da Alessio (una voce in lista bianca o un
  suo comando), scritto in `docs/conto_vero.md` (fase 4).

### 56 — Medio — Un blocco a metà ribilancio lascia il conto con un lato solo fino alla mezzanotte dopo lo sblocco (domanda 4)
- Dove: `conto_vero.py:222-225` (file sul disco diversi dal tag ogni minuto), `:251-257` (annullo degli ordini in corso, niente resto
  a mercato), `:258-263` (allo sblocco si aspetta la decisione di G1 dopo).
- Prova p2: AUSDT eseguito a limite, BUSDT sul libro, blocco per due minuti: BUSDT annullato, nessun ordine a mercato in 1 ora e 40,
  conto al **50% netto lungo**, `ultimo_giorno` spinto alla decisione dopo.
- Scenario: ribilancio alle 00:05; alle 00:20 arriva sulla macchina un commit del paper in `bot/portafoglio/f5.py` (strategy-improver
  aggiunge varianti lì a ogni giro); il minuto dopo gli ordini limite non eseguiti si annullano e il conto resta con un lato solo per
  uno o più giorni (fino allo spostamento del tag e alla decisione dopo): un'esposizione diretta al mercato che la prova di G1 a due
  lati non misura. Il codice in memoria era quello approvato all'avvio; la modifica del disco conta solo al prossimo riavvio, che
  `_codice_all_avvio` già ferma.
- Correzione suggerita: se il codice dell'avvio è approvato, un cambio sul disco scrive un allarme («al prossimo riavvio niente
  ordini veri») e non annulla il ribilancio in corso (o lo completa a mercato); tenere il codice della decisione di G1 usata dal conto
  vero separato dalle varianti del paper, così una modifica al paper non ferma i soldi veri.

### 57 — Medio — Il fermo si perde con il file di stato: il conto vero riapre alla mezzanotte senza «riparti»
- Dove: `demo_binance.py:691-695` (`carica` dà `{}` sia per il file mancante sia per quello illeggibile), `:816-820` (lo stato nuovo
  sovrascrive il file), `conto_vero.py:258-263` (`acceso_dal` mancante = prima accensione).
- Prova p3c: pulsante della dashboard a 290 USDT, poi `data/conto_vero.json` cancellato: alla decisione dopo **due ordini limite di
  apertura**, con `/conto_vero/fermo` ancora scritto su Firebase. (Dopo uno stop a −35% il conto resta sotto il capitale e il
  controllo del saldo blocca per caso, prova p3; con il comando a file il testo vecchio lo richiude per caso, prova p3b.)
- Scenario: Alessio preme «chiudi tutto» perché Binance ha un problema; la macchina viene ripristinata senza `data/` o il file si rompe
  in scrittura; alla mezzanotte il conto vero ricompra con soldi veri senza che nessuno lo abbia chiesto.
- Correzione suggerita: per il conto vero, file mancante con `/conto_vero/acceso_dal` o `/conto_vero/fermo` su Firebase, oppure file
  illeggibile → fermo (sole chiusure) con allarme fino al «riparti»; distinguere la prima accensione dal file perso.

### 58 — Medio — Versamenti e prelievi cambiano il valore visto dal bot (domanda 2)
- Dove: `demo_binance.py:1190-1197` (valore = `totalMarginBalance` − scarto), `:620`, `conto_vero.py:236-242` (tetto a 600 sul valore
  ridotto).
- Prova p4b: 280 USDT, versati 250 → al ribilancio dopo AUSDT +1,25 e BUSDT −2,5, cioè posizioni per 530 USDT, nessun allarme.
- Scenario: Alessio versa 250 USDT «per avere margine»; il bot li conta come guadagno e li mette a rischio: soldi veri a rischio oltre
  la costante di 300. Al contrario, i «prelievi regolari» del piano (`docs/backlog.md:707`, punto 6) contano come perdite: un prelievo
  di un terzo dal massimo fa scattare lo stop e chiude tutto.
- Correzione suggerita: leggere i trasferimenti (`/fapi/v1/income`, tipo `TRANSFER`) e spostarli nello scarto e nel massimo, oppure
  fermare gli ordini nuovi con un allarme a ogni trasferimento; più un tetto sul valore vero del portafoglio dei future (per esempio
  2 × 300) che faccia rispettare il «conto solo del bot».

### 59 — Medio — Il bot chiude ogni posizione e annulla ogni ordine del conto, anche quelli non suoi (domanda 2)
- Dove: `demo_binance.py:645-655` (`parti_da_zero`), `:1078-1105` (`_chiudi_posizioni`, usata da «chiudi tutto» e da fermo),
  `:1208-1225` (`controlla_margine` chiude ogni posizione con il margine separato).
- Prova p5: una posizione di CUSDT non del bot → chiusa a mercato alla prima decisione di G1.
- Scenario: nel conto c'è una posizione aperta a mano da Alessio o un residuo: la prima mezzanotte la chiude a mercato senza chiedere.
- Correzione suggerita: alla prima accensione (nessun `acceso_dal`) con posizioni o ordini nel conto, niente ordini e allarme «il
  conto non è vuoto» finché Alessio non lo svuota; obbligo da confermare con lui (decisione 4).

### 60 — Medio — Pulsante, stato e «riparti» del conto vero fuori dalla dashboard e dalle regole; «riparti» in un passo
- Dove: nessun riferimento a `conto_vero` in `dashboard/app` (ricerca); `firebase/database.rules.json` senza
  `conto_vero_chiudi_tutto` e `conto_vero_riparti`; `DashboardShell.tsx:416-419` (sempre «DRY_RUN · paper»); «riparti» in un passo
  (`demo_binance.py:978-997`, comandi `conto_vero.py:59-62`), mentre il piano chiede di preparare la scelta più prudente, «riparti» in
  due passi (`docs/conto_vero.md:28-32`).
- Scenario: dal telefono Alessio non ha un pulsante per chiudere i soldi veri (solo la console di Firebase o un commit); la testata
  della dashboard dice «paper» mentre girano soldi veri; con le regole di Firebase mai pubblicate, chi può scrivere nel database
  riaccende il conto vero dopo uno stop.
- Correzione suggerita, prima della fase 4: pulsante, stato e allarmi del conto vero in dashboard; regole per i due comandi (solo
  vero/falso, solo il proprietario); «riparti» del conto vero in due passi (richiesta e conferma) e, finché le regole non sono
  pubblicate, solo dal file.

### 61 — Basso — Il codice dell'avvio si controlla nel costruttore, non quando i moduli si caricano
- Dove: `conto_vero.py:158-160`, `main.py:506` (dopo Firebase e i quattro paper). Se l'agente aggiorna i file in quella finestra, il
  processo gira con il codice di prima e il controllo vede quello di dopo. Correzione: impronta dei file caricati letta all'import e
  confrontata con il tag (va con il 54).

### 62 — Basso — Un guasto di rete nel primo ribilancio fa richiudere e riaprire tutto 30 minuti dopo
- Dove: `demo_binance.py:627-674` (`parti_da_zero` non salva lo stato), `:876-880`. Prova p9: risposta dell'ordine di BUSDT persa →
  30 minuti dopo AUSDT richiuso a mercato e riaperto a limite. Solo commissioni (gli aperti si annullano prima, nessun doppio ordine).
  Ereditato dal demo. Correzione: salvare lo stato subito dopo `parti_da_zero`.

### 63 — Basso — Testi del demo sul conto vero e messaggi con `DRY_RUN` falso
- `valore_vero_del_conto_demo` (`demo_binance.py:1452`), «il demo resta fermo» (`:1071`), l'avviso di un `DRY_RUN` scritto male
  stampato a ogni giro (`conto_vero.py:176` → `config.py:88-89`); con `DRY_RUN` falso le operazioni del vecchio paper annunciate
  «🔴 LIVE» e il Telegram «exchange_down» del riconciliatore (domanda 6). Correzione: testi propri del conto vero; etichette e
  riconciliatore del vecchio bot legati all'esecutore (`self.executor.dry_run`), non a `settings.DRY_RUN`.

## Invarianti modificati

- **Cambiato (non committato)**: con `DRY_RUN` falso il bot ora **parte**, se la parità col backtest è spenta e c'è
  `ops/conto_vero_acceso` (`config.py:801-813`); prima non partiva mai (problema 29). Va approvato da Alessio insieme al 53.
- **Nuovi (non committati)**: G1 sul conto vero, solo `https://fapi.binance.com` (`conto_vero.py:80-85`); quattro condizioni
  (`:173-178`, `:217-243`); freno del cliente (`:130-134`); limiti come costanti con test (`:70-77`, test `:67-87`); niente eventi
  (`:166-170`, `:284-285`); capitale fissato fino a 300 come seconda difesa del ribilancio (`:286-290`); filtri veri (`:293-302`);
  stato, ramo e comandi propri (`:56-62`); partenza alla decisione di G1 dopo ogni accensione o blocco (`:258-266`).
- **Invariati**: `bot/risk/hard_limits.py`; vecchio ramo reale bloccato (`executor.py:244-254`); limiti, comandi e comportamento del
  demo (spostati in attributi di classe con gli stessi valori; test del demo invariati e passati).

## Decisioni per Alessio

1. **Spegnere il conto vero**: con posizioni aperte, togliere l'interruttore o rimettere `DRY_RUN` vero deve lasciare attive le sole
   protezioni (ordini «solo riduzione» e annulli) fino al conto vuoto? Raccomando sì (problema 53). Con `DRY_RUN` vero è un'eccezione
   alla regola «in paper nessun ordine al conto vero»: serve il suo sì esplicito. E all'avvio con `DRY_RUN` falso senza interruttore:
   partire con il conto vero in sole protezioni invece di fermare tutto il bot?
2. **Chi approva il codice**: tag firmato da lui con una sua chiave e verificato dal bot (raccomandato), oppure una regola di GitHub
   sul tag; come il tag arriva sulla macchina (problemi 54, 55).
3. **I limiti del conto vero**: capitale 300 USDT, valore massimo 600 prima di fermare gli ordini nuovi, somma dei pesi 200%, peso per
   moneta 60%, leva 5, stop −35% dal massimo con pavimento al 65% del capitale, età della decisione 26 ore. Domanda 3
   dell'implementatore: il 200% vale solo per G1; G1 neutra ha i lati da 0,5 a 1,5 (fino al 300%) e il conto vero legge solo
   `data/paper_g1.json` (`conto_vero.py:150`): se lunedì si sceglie G1 neutra serve una modifica e una revisione nuova.
4. **Conto dei future solo del bot**: farlo controllare dal codice (niente ordini se il conto non è vuoto alla prima accensione, tetto
   sul valore vero)? E i prelievi regolari del piano: come (fermo e capitale nuovo, oppure trasferimenti letti dal bot)? (58, 59)
5. **Quando cambia il codice sul disco**: annullare il ribilancio in corso (oggi) o finirlo e solo avvisare? Tenere il codice di G1
   per i soldi veri separato dalle varianti del paper? (56; domanda 4 dell'implementatore: oggi sì, ogni modifica in
   `bot/portafoglio/`, anche al paper, blocca gli ordini veri fino allo spostamento del tag)
6. **Quando G1 non decide o il codice è bloccato** il conto vero tiene le posizioni di ieri senza limite di tempo (protette solo
   dallo stop): va bene o dopo un certo tempo si chiude? Il conto vero dipende anche dal paper di G1 acceso (`ops/paper_g1_acceso`).
7. **«Riparti» del conto vero**: in due passi, e solo dal file finché le regole di Firebase non sono pubblicate (60).
8. **Pulsante e stato del conto vero in dashboard** prima della fase 4 (60).
9. **Fuori dal codice, da confermare**: chiave del conto vero senza prelievo e limitata all'indirizzo della macchina; regole di
   Firebase pubblicate con il suo identificativo (anche per i due comandi nuovi); conto dei future con una posizione per moneta, un
   solo attivo di margine (USDT, niente «multi-assets»), non «portfolio margin».
10. **Riavvio**: caricare questo codice tocca il demo: solo con il suo ok e dopo le correzioni; il conto vero resta spento.
11. Restano quelle di prima: stop per posizione assente per scelta, avvisi sul telefono, lo Sharpe corretto 0,86 di G1 (piano, punto
    3), «almeno 10 monete per lato» della revisione con le skill (`docs/backlog.md:707`, punto 4) non applicato al conto vero.

## Domande aperte

1. Con quale identità la sessione spinge su GitHub (il token è di Alessio o di un'applicazione)? Serve per sapere se una regola di
   GitHub sul tag basta o serve la firma.
2. Sulla macchina il servizio del bot e l'agente `ops` girano con lo stesso utente, e quell'utente può eseguire `git` nella cartella
   del repository? Altrimenti `codice_approvato` darà sempre «manca il tag» (sicuro ma muto); si verifica con una richiesta in `ops/`.
3. Il conto dei future di Alessio: modalità a una posizione per moneta, un solo attivo di margine (USDT), niente «portfolio margin»,
   nessun'altra posizione o ordine aperto?
4. Lunedì l'allocatore sceglie G1 o G1 neutra? Con G1 neutra il conto vero va cambiato (file della decisione e somma dei pesi).
5. Dalle domande dell'implementatore: 1 → no, non accettabile così (53); 2 → sì, il codice lo dà per scontato senza controllarlo
   (58, 59); 3 → da decidere (decisione 3); 4 → sì, confermato (56); 5 → no, provato (55); 6 → nessun ordine né chiusura fuori da
   `ContoVeroG1`, solo effetti di messaggi e di stato (sezione D); 7 → confermato (53).
6. Resta aperta dal 7 novembre: la modifica proposta della leva a 10 e della perdita giornaliera dalla dashboard (mai applicata) si
   chiude come «non applicata»?
