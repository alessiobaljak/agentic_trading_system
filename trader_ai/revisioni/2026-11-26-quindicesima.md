# Quindicesima revisione del trader AI — versione 7 (correzioni del controllo del 26 novembre)

Revisore: live-path-reviewer, 26 novembre 2026. Modifiche non committate su `0de9328` (branch `claude/brave-albattani-1b12fv`; il
`a94db04` porta solo il rapporto del controllo). Le prove sono nella cartella di lavoro
`/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/revisione_v7/` (sotto: «la cartella»).

### Riepilogo e verdetto

**REQUEST CHANGES.** Un Bloccante (188), un Alto (189), due Medi (190, 193) e due Bassi (191, 192).

1. **188 (Bloccante, regressione).** Quando un ordine limite si esegue fra la lettura delle posizioni e quella degli ordini, il
   programma lo crede «mai eseguito» (o, sul demo, «eseguito e chiuso»), **toglie lo stop dalla posizione aperta**, la dimentica, dice al
   modello «nessuna operazione aperta» e al passo dopo si ferma come davanti a una posizione d'altri, senza più toccarla. Provato con il
   codice vero sul conto simulato (il prezzo passa sotto il vecchio stop e la posizione resta aperta) e con la semantica del demo. Con il
   codice committato la stessa corsa lascia lo stop al suo posto: la modifica di oggi lo toglie.
2. **189 (Alto).** Un errore nella lettura dell'esito dell'ordine vale «mai eseguito»: un limite eseguito e chiuso fra due controlli
   sparisce di nuovo dalla memoria (il difetto 2.2 del controllo), senza nuovo tentativo.
3. **190 (Medio).** La ricostruzione della memoria, se la lettura del conto fallisce una volta, si segna come fatta, non si rifà più e
   i resoconti dicono «rifatto con le uscite vere» con le uscite vecchie.
4. **Il resto regge.** Sui dati veri della macchina la ricostruzione torna (14 operazioni, l'operazione delle 15:01 aggiunta, somma dei
   netti −59,84 contro −59,86 del conto, nessun doppione); il fermo a mano e il conto estraneo fermano ogni ordine come prima; lo stato
   si salva prima dell'invio; il tetto dei 5 dollari non si può sforare (calcolo nella checklist A); nessun conto vero, nessun segreto.
   I problemi 184-186 della quattordicesima sono chiusi nel `f7fe784` (tempo massimo 600 secondi, testi, operazioni in pari).

Condizioni per l'APPROVE: correggere 188 e 189 con i test delle corse descritte sotto; 190 e 193 consigliati nello stesso giro; nuova
revisione prima del riavvio (che chiede comunque l'ok di Alessio).

### Oggetto

* Branch `claude/brave-albattani-1b12fv`, base `0de9328`, modifiche non committate (`git diff HEAD -- trader_ai/`: 17 file, +1.325 −307)
  più i file nuovi `operazioni.py`, `calendario.py`, `ripara.py`, `tests/test_controllo_26.py` (21 test). Impronte md5 (primi 8
  caratteri) dei file rivisti, da confrontare al commit: `avvio.py` 89497691, `conto_simulato.py` b76a4e29, `conto_demo.py` 453e0288,
  `limiti.py` ea69db16, `schema.py` 58dacc4f, `modello.py` d965bfac, `costi.py` 2b1e9f30, `giro.py` 0b813210, `messaggio.py` c23b2878,
  `operazioni.py` 1afc3fe1, `ripara.py` ef2b2fc6, `calendario.py` f4ba1a70, `tests/test_controllo_26.py` 837537b0.
* Percorso degli ordini toccato: `avvio.py` (`passo` :163-279, `_decidi_ed_esegui` :281-336, `_esito` :421-425, `_eseguito` :427-443,
  `_registra_chiusura` :454-508, `_ripara_memoria` :510-543, `_esegui` :582-706, `resoconto` :814-897), `conto_simulato.py`
  (`esito_ordine` :310-331, stop e obiettivo per lato :225-229, conti per posizione :272-298, `candele` :301-302), `conto_demo.py`
  (`candele_da_klines` :84-97, `esito_ordine` :162-182, `interesse_aperto_storia` :154-160), `limiti.py` (:82-89, :111-121),
  `ripara.py`, `schema.py`, `modello.py`, `costi.py`, `giro.py`.
* Invarianti coinvolti (sezione 15 di `reviews/LIVE_PATH_MAP.md`): stop obbligatorio sul conto, fermo a mano, conto estraneo, tetto di
  spesa, una sola operazione alla volta.

### Checklist A–F

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py`: invariato (`git diff HEAD -- bot/risk/hard_limits.py` vuoto); `bot/`, `firebase/`, `ops/` non toccati. OK.
* Limiti del trader, costanti nel codice, valori invariati: leva 10 (`trader_ai/limiti.py:15`), obiettivo 3% (`:14`), valore minimo 100
  (`:17`), tetto 5 dollari (`trader_ai/costi.py:22`), 16.000 token (`:25`). `config.json` porta solo moneta e tipo di conto. OK.
* Tetto di spesa: il costo massimo ora conta 1,5 caratteri per token e il prezzo più caro, 8 dollari al milione (`costi.py:28`,
  `:48-52`); si registra prima della chiamata e si corregge dopo (`trader_ai/giro.py:35-44`). Con il messaggio vero di oggi (24.066
  caratteri: 3.923 di istruzioni, 6.402 di memoria stabile, 13.741 del resto; passo vero rifatto in `la cartella/passo_vero`) il costo
  massimo è 0,448 dollari. Il costo vero più alto possibile (istruzioni e memoria scritte in cache a 8, il resto a 4, 16.000 token
  d'uscita a 20) resta sotto quel valore per qualunque rapporto sopra circa 1,1 caratteri per token (a 1,2: 0,435); misurato 1,8. OK.
* Parametri della dashboard, limiti di G1 sul demo, Firebase: NON APPLICABILE (il trader non li usa).
* Pulsante che chiude tutto: `python -m trader_ai.avvio chiudi` e file `fermo` (`avvio.py:775-808`), senza Firebase; fermo letto a
  inizio passo (`:165`) e prima di ogni ordine (`:583`, `:640`, `:645`). Le vie nuove (`:231-234`, `:598-610`) annullano soltanto. OK.

**B. Ordini**
* Passi di quantità e prezzo da `exchangeInfo` (`conto_simulato.py:107-117`, `conto_demo.py:184-194`, `avvio.py:611-624`): invariati. OK.
* Identificativo `tai<tipo><ms>` (`avvio.py:140-141`), salvato con l'intenzione prima dell'invio (`:629-638`), nessun ritentativo
  automatico. OK.
* Chiusure con «solo riduzione» sul demo (`conto_demo.py:276-279`); stop e obiettivo `closePosition` sul prezzo mark (`:252-257`);
  modalità a una posizione controllata (`avvio.py:146-147`). OK.
* Prezzo che attiva gli stop: mark, nel demo e nel simulato (`conto_simulato.py:184-191`, `:232-244`). OK.
* Leva e margine separato impostati prima di ogni apertura (`conto_demo.py:237-243`). OK.
* Stop di ogni posizione sul conto: **PROBLEMA 188** (lo stop viene tolto da una posizione aperta) e **PROBLEMA 193** (limite che
  incrocia il prezzo: stop rifiutato e solo scritto nel diario).

**C. Stato e resilienza**
* Stato riletto dal conto a ogni passo e prima di ogni ordine: sì, ma la decisione sull'ordine limite sparito non rilegge la posizione:
  **PROBLEMA 188**; un errore di lettura dell'esito vale «mai eseguito»: **PROBLEMA 189**.
* «Inviata» e stato salvato prima dell'ordine: invariati (`avvio.py:629-638`, `:215-221`). Una chiusura registrata e poi persa per un
  errore più avanti nel passo si rifà una volta sola al passo dopo (lo stato non salvato si rilegge dal file); il diario può avere
  l'evento «operazione chiusa» due volte. OK.
* Candele: gli indicatori solo sulle chiuse (`messaggio.py:408`, `:427`, `:443-445`); la candela in corso si mostra a parte (`:424-426`),
  scelta scritta in `REGOLE.md` §4 versione 7. OK.
* Errori delle interfacce: pause per 429 e 418 invariate (`conto_simulato.py:69-75`, `conto_demo.py:124-130`); storia dell'interesse
  aperto in errore = lista vuota (`avvio.py:286-289`). OK.
* Ricostruzione della memoria (`ripara.py`, `avvio.py:510-543`): sui dati veri torna (prova 190 bis); se i conti non tornano non tocca
  niente (`ripara.py:95-99`, eccezione presa a `avvio.py:525-527`) e non blocca il passo in un giro senza fine (la versione sale e il
  passo continua); con la lettura del conto in errore: **PROBLEMA 190**.
* Flussi in tempo reale, Firebase, orologio: NON APPLICABILE.

**D. Separazione fra simulato, demo e conto vero**
* Il simulato fa solo GET pubblici su `fapi.binance.com`, senza chiave (`conto_simulato.py:62-78`); il demo solo `demo-fapi.binance.com`
  (`conto_demo.py:30-45`); `config.json` dice `"conto": "simulato"`. Le richieste nuove (`GET /fapi/v1/order` firmata sul demo,
  `/futures/data/openInterestHist` pubblica) passano dagli stessi controlli. Il trader non usa `DRY_RUN` e non tocca il conto vero. OK.

**E. Segreti e sicurezza**
* Nessuna chiave nel diff (ricerca su indirizzi, «key», «secret», «token», variabili `BINANCE_` e `ANTHROPIC_`). OK.
* I messaggi interi e il riassunto del ragionamento non contengono segreti, ma possono finire nel repository pubblico: **PROBLEMA 191**.
* Chiavi senza permesso di prelievo: da confermare con Alessio (invariato; oggi il trader non usa chiavi).

**F. Test**
* `cd /home/user/agentic_trading_system && TRADER_AI_BLOCCO=<cartella>/x.lock python -m pytest trader_ai/tests -q` → **113 passed**.
* Suite intera del repository (`python3 -m pytest tests/ -q`): **1 failed, 2825 passed, 1 skipped** in 205 s; il fallito è della ricerca
  (`tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore`: file non toccati dal 20 novembre, nessun legame
  con `trader_ai/`, nessun file fuori da `trader_ai/` modificato), estraneo a questa modifica.
* Test dei limiti fissi: `python3 -m pytest tests/test_risk.py tests/test_sizing.py tests/test_strategie_restano_accese.py -q` → 23 passed.
* Prove mie, tutte eseguite e passate (provano i difetti): `test_prove_v7.py` (4), `test_prove_v7_b.py` (3), `test_prove_v7_c.py` (1),
  `test_prove_v7_d.py` (2), lanciate dalla radice con `TRADER_AI_BLOCCO=<cartella>/x.lock python -m pytest <file> -q -p no:cacheprovider`;
  `prova_188_vecchio.py` sul codice committato (estratto con `git archive HEAD trader_ai` in `<cartella>/vecchio`).
* Mancano i test delle corse (188), dell'esito in errore (189), della ricostruzione con il conto non letto (190), del limite che
  incrocia (193): vedi i problemi.

### Problemi

**188 — Bloccante — `trader_ai/avvio.py:222-234` (passo) e `:596-610` (`_esegui`), con `conto_demo.py:175-182`.**
* Cosa succede. Il passo legge prima le posizioni e poi gli ordini (`avvio.py:171-172`; in `_esegui` `:585-586` e `:596-597`). Se il
  limite si esegue fra le due letture, la posizione risulta assente e l'ordine pure. Il programma chiede l'esito (`:225`, `:598`) e:
  * sul simulato l'esito è `{"stato": "aperta"}`, che non è fra «chiusa» ed «eseguito» → ramo «mai eseguito»: `st["aperta"] = None` e
    `self.c.annulla_tutto()` (`:232-233`, `:600-601`): **lo stop della posizione appena aperta viene cancellato**;
  * sul demo l'esito è `{"stato": "eseguito"}` anche con la posizione aperta (lo dice il suo commento, `conto_demo.py:164-165`) → il
    programma la registra come chiusa con un'uscita inventata e chiama `annulla_tutto` dentro `_registra_chiusura` (`avvio.py:506`).
  Poi il modello riceve «nessuna operazione aperta e nessun ordine in attesa» (oppure «la tua operazione si è chiusa»: dati falsi) e al
  passo dopo il controllo del conto trova «una posizione che il trader non ha aperto» (`:155-156`) e si ferma **senza toccare niente**:
  la posizione resta aperta, senza stop, finché qualcuno non interviene.
* Quando. Sul simulato la lettura delle posizioni fa girare il mercato (`conto_simulato.py:167-173`) e quella degli ordini la rifà solo
  se sono passati 5 secondi dall'inizio della prima: serve una lettura lenta (tre richieste a Binance, 15 secondi di tempo massimo
  l'una) a cavallo di un minuto in cui il limite si esegue. Raro. Sul demo basta che l'esecuzione cada fra due richieste HTTP: con 13
  aperture a limite su 15 del primo giorno, una finestra di qualche decimo di secondo ogni 30 secondi, è questione di giorni.
* Prova (eseguita). `la cartella/test_prove_v7.py`:
  * `test_188_simulato_...`: conto simulato vero, limite lungo a 89.500 e stop a 89.000; la prima lettura dura 6 secondi e la seconda
    vede il minuto delle 10:04 (minimo 89.400) → posizione lunga a 89.500 sul conto, `algo` vuoto, `aperta` None, evento «ordine limite
    non più sul conto e mai eseguito»; il passo dopo `estraneo` = «una posizione che il trader non ha aperto»; dieci minuti dopo il
    prezzo è sceso a 88.870, sotto il vecchio stop, e la posizione è ancora aperta senza stop. Stampato: `dopo 10 minuti: posizione lungo
    89500.0 stop sul conto [] minimo dei minuti contati 88870 estraneo: una posizione che il trader non ha aperto`.
  * `test_188_demo_...`: il vero `ContoDemo.esito_ordine` con un ordine FILLED dà «eseguito»; con quell'esito e l'esecuzione fra le
    due letture il programma registra un'operazione chiusa (uscita stimata), toglie lo stop e la posizione resta aperta.
  * `test_188_esegui_...[aperta|eseguito]`: lo stesso dentro `_esegui`; al modello arriva «mentre decidevi il tuo ordine limite è
    sparito senza eseguirsi» o «la tua operazione si è chiusa (chiusa sul conto ...)»: entrambi falsi.
  * Regressione: `python -I la cartella/prova_188_vecchio.py la cartella/vecchio` (codice committato) → `posizione True | stop sul conto
    [89000.0] | aperta nel programma None`: prima lo stop restava.
* Correzione suggerita alla sessione principale. Prima di dichiarare «mai eseguito» o «chiuso», rileggere la posizione
  (`self.c.posizioni_simbolo()`) **dopo** aver visto che l'ordine non è più sul libro: con una posizione presente →
  `_eseguito(a, esito, ora, pos)` e protezione; esito «aperta» o «eseguito» senza posizione → chiusa; nessun esito e nessuna posizione
  → solo allora `annulla_tutto`. Lo stesso in `_esegui`. Test: le quattro corse qui sopra (lettura delle posizioni prima
  dell'esecuzione, degli ordini dopo), con la semantica del simulato e con quella del demo.

**189 — Alto — `trader_ai/avvio.py:421-425` (`_esito`), usato a `:225-234` e `:598-603`.**
* Cosa succede. `_esito` prende ogni eccezione e restituisce None; None vale «mai eseguito». Un ordine limite eseguito e chiuso fra due
  controlli (il caso 2.2 del controllo) si perde di nuovo se in quel momento la lettura dell'esito fallisce: `aperta` va a None, l'evento
  dice «mai eseguito», il modello non viene chiamato per la chiusura, e al passo dopo non c'è più niente da ritentare.
* Quando. Sul demo basta un errore della richiesta `GET /fapi/v1/order` (rete, pausa per 429 o 418, che `conto_demo.py:169-174` rilancia);
  sul simulato l'esito rifà girare il mercato solo dopo 5 secondi (`conto_simulato.py:316`, `:167-170`), quindi serve una lettura lenta.
* Prova (eseguita). `la cartella/test_prove_v7_b.py::test_189_...`: limite eseguito e fermato fra due controlli (conto −5,35), esito in
  errore → `operazioni registrate: 0 | ultimo evento: ordine limite non più sul conto e mai eseguito | chiamate: 1`; al passo dopo,
  con l'esito di nuovo leggibile, l'operazione resta persa.
* Correzione suggerita. Distinguere l'errore da «mai eseguito»: con l'errore lasciare `aperta` com'è, scrivere un evento e riprovare al
  passo dopo (con un conto dei tentativi e un evento visibile dopo qualche fallimento); mai `annulla_tutto` su uno stato sconosciuto.
  Test: esito in errore una volta, poi «chiusa» → operazione registrata una volta.

**190 — Medio — `trader_ai/avvio.py:513-543` (`_ripara_memoria`) e `:829-832` (intestazione del resoconto rifatto).**
* Cosa succede. La versione della memoria sale a 7 per prima cosa (`:513`). Se la lettura del conto fallisce (`:518-521`;
  `storia()` fa girare il mercato con richieste a Binance), si scrive «memoria non ricostruita: conto non letto» e si va avanti lo
  stesso con `storia = None`: `ricostruisci` si limita a numerare (`ripara.py:90`, `:149-153`), il diario scrive anche «memoria
  ricostruita dal conto e dal diario» (`avvio.py:538`) e i resoconti dei giorni passati si riscrivono con l'intestazione «rifatto ...
  uscite vere e un'operazione che mancava» (`:829-832`) ma con le uscite vecchie. Se `saldo()` subito dopo riesce, lo stato si salva
  con la versione 7: la ricostruzione non si rifà mai più e il modello continua a vedere le uscite sbagliate e a non vedere
  l'operazione delle 15:01 (i difetti 2.2 e 2.4 del controllo).
* Quando. Solo al primo passo dopo il riavvio, con un errore di rete passeggero proprio su quella lettura (che deve recuperare tutti i
  minuti del fermo).
* Prova (eseguita). `la cartella/test_prove_v7_b.py::test_190_...` sulla copia dei dati veri (`trader_ai/avanti/`, sola lettura) con
  un errore alla prima lettura: `versione 7 | operazioni 13 (nel conto: 14) | prima uscita 59124.55402899 (nel conto 59015.9)`; eventi
  `['memoria non ricostruita: conto non letto', 'memoria ricostruita dal conto e dal diario (...)']`; il resoconto del 25 comincia con
  «Rifatto ... uscite vere e un'operazione che mancava»; al passo dopo niente si rifà. Controllo di parità `test_190_bis_...`: con il
  conto letto bene 14 operazioni, somma dei netti −59,84 contro −59,86 del conto, numeri da 1 a 14, stabili al passo dopo.
* Correzione suggerita. Con il conto non letto non alzare la versione (si riprova al passo dopo; dopo qualche tentativo un evento e la
  rinuncia scritta); l'intestazione «rifatto con le uscite vere» solo se `rapporto` dice almeno una correzione o un'aggiunta.

**191 — Basso — `trader_ai/vps/salva.sh:19` con `trader_ai/avanti/.gitignore` (riga nuova) e `trader_ai/vps/installa.sh:111-114`.**
* Cosa succede. I messaggi interi al modello e il ragionamento (`avvio.py:389-402`, 1-2 MB al giorno) devono restare sulla macchina:
  la regola è la riga `messaggi/` aggiunta a `trader_ai/avanti/.gitignore` nel commit del codice. Ma la copia dei dati sulla macchina
  (`/opt/trader-ai-dati`) non si aggiorna con `installa.sh` (`:111-114` la clona una volta sola): riceve il `.gitignore` nuovo solo con
  il rebase di `salva.sh`, **dopo** `git add trader_ai/avanti` (`salva.sh:19`). Se la prima chiamata dopo il riavvio arriva prima di un
  salvataggio, il file dei messaggi del giorno va nel repository pubblico, resta tracciato e si rispinge ogni ora finché esiste.
* Prova (eseguita). `la cartella/test_prove_v7_c.py`: git vero in cartelle temporanee, `salva.sh` del repository; dopo il primo
  salvataggio l'albero remoto contiene `trader_ai/avanti/messaggi/2026-11-26.jsonl`; aggiunta una riga, il secondo salvataggio la spinge.
  Nessun segreto dentro (dati di mercato, memoria, ragionamento): è un difetto di riservatezza voluta e di peso del repository.
* Correzione suggerita. In `salva.sh` escludere i messaggi (`git add trader_ai/avanti ':(exclude)trader_ai/avanti/messaggi'`), oppure
  scriverli fuori dalla copia dei dati, oppure aggiornare la copia dei dati prima del riavvio.

**192 — Basso — `trader_ai/avvio.py:684-685` con `:463-464`.**
* Cosa succede. Per un «chiudi» del modello `chiusa_da = "chiusa da te"` si scrive **prima** di `self.c.chiudi(...)`. Se la chiusura è
  rifiutata, la posizione resta; quando poi la chiude lo stop, `_registra_chiusura` dà la precedenza a `chiusa_da` sul «come» letto dal
  conto: in memoria «chiusa da te» per un'uscita allo stop. L'ordine è vecchio, ma da oggi il conto dice il modo vero e il codice lo
  ignora.
* Prova (eseguita). `la cartella/test_prove_v7_d.py::test_192_...` → `come registrato: chiusa da te | uscita 87991.2` con l'esito del
  conto «stop».
* Correzione suggerita. Scrivere `chiusa_da` dopo che `chiudi` è riuscita, oppure preferire il modo del conto quando è stop, obiettivo
  o liquidazione.

**193 — Medio (preesistente, non introdotto oggi) — `trader_ai/limiti.py:96-102` con `trader_ai/avvio.py:654-658`.**
* Cosa succede. Per un ordine limite lo stop si controlla solo sul prezzo limite. Un limite lungo sopra il prezzo (o corto sotto) si
  esegue subito a mercato (`conto_simulato.py:390-396`; sul demo come ordine che prende dal libro); uno stop fra il prezzo e il limite
  passa il controllo, viene rifiutato perché scatterebbe subito, e per un limite il rifiuto è solo scritto nel diario: la posizione è
  aperta **senza stop** e il programma la crede «in attesa» fino al passo dopo (30 secondi), che la chiude a mercato. Le istruzioni al
  modello dicono che una decisione così viene scartata («ogni apertura ha uno stop, dalla parte giusta del prezzo d'entrata»,
  `istruzioni.md:28`).
* Prova (eseguita). `la cartella/test_prove_v7_d.py::test_193_...`: lungo a limite 90.100 con il prezzo a 90.000 e stop 90.050 →
  `posizione 90009.0 | stop sul conto [] | in attesa nel programma True`.
* Correzione suggerita. In `controlla`, per un limite che incrocia il prezzo di adesso, controllare lo stop anche sul prezzo di adesso;
  oppure in `_esegui`, se la risposta dell'ordine dice eseguito, trattarlo come un ordine a mercato (stop rifiutato → chiusura subito).

### Invarianti modificati

* **Ordine limite sparito dal libro**: prima `aperta` a None e basta (lo stop restava sul conto), ora esito dal conto e
  `annulla_tutto` (`avvio.py:224-234`): da qui il 188.
* **Stop e obiettivo del simulato solo per il loro lato** (`conto_simulato.py:225-229`); ogni posizione tiene nome dell'ordine, spese,
  funding, uscita e modo (`:272-298`), letti da `esito_ordine` (`:310-331`).
* **Memoria dal conto**: uscita, modo, spese e funding dall'esito (`avvio.py:454-508`); ricostruzione una volta sola (`:510-543`).
* **Controlli delle decisioni**: apertura con un limite in attesa scartata con motivo suo, `prezzo_limite` senza `tipo_ordine` limite
  scartato (`limiti.py:82-89`); «modifica» di un limite in attesa controllata sul prezzo limite e sul prezzo di adesso (`:111-121`);
  leva intera nello schema (`schema.py:19`); lunghezze dei testi non più controllate dallo schema, tagliate al salvataggio.
* **Chiamate**: richiamo subito dopo un «chiudi» o un annullamento del modello (`avvio.py:213`, `:682`, `:687`).
* **Tetto**: stesso valore (5 dollari); costo massimo più prudente (1,5 caratteri per token invece di 2, prezzo 8 invece di 5).
* Nessun valore dei limiti cambiato; `bot/risk/hard_limits.py` invariato.

### Decisioni per Alessio

* Il riavvio con questa versione tocca gli ordini simulati: serve il suo ok, **dopo** le correzioni di 188 e 189 e una revisione nuova.
* Il passaggio al conto demo (`"conto": "demo"`) con questo codice renderebbe il 188 probabile: non va fatto senza la correzione e una
  prova sul demo dell'esito degli ordini.
* I messaggi interi e il ragionamento del modello: vuole che restino solo sulla macchina, come scritto, o gli va bene che finiscano
  anche nel repository pubblico (191)?
* Restano sue le scelte 5.1-5.3 del controllo (tetto di spesa, maiuscole, 3% prima delle spese): non toccate da questa revisione.

### Domande aperte

* Il rapporto fra caratteri e token del messaggio nuovo (24.066 caratteri) non è misurato: il tetto regge per qualunque rapporto sopra
  circa 1,1 (checklist A), ma dopo il riavvio vanno guardati nelle prime chiamate `usage`, durata ed esiti «troncata» o «errore».
* Le istruzioni da sole (3.923 caratteri, circa 2.200 token) superano la lunghezza minima che la cache accetta per questo modello? Se no,
  conta solo il secondo punto di cache (istruzioni più memoria): è una questione di costo, non di ordini.
* Sul demo, per un ordine eseguito e già chiuso, `GET /fapi/v1/order` dice solo «eseguito»: uscita e spese restano stimate. Va provato
  sul demo prima di usarlo, insieme alla correzione del 188.
* La memoria del revisore (`reviews/`) è dell'area crypto e da qui non si scrive: le righe nuove sono pronte in
  `la cartella/righe_per_reviews.patch` (indice, registro, archivio, mappa, sezione 15) per la sessione che può applicarle.

## Riesame (26 novembre 2026, pomeriggio, sul codice di adesso)

Revisore: live-path-reviewer. Stesso branch e stessa base (`0de9328`), modifiche ancora non committate. Prove nuove nella cartella
`/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/riesame_v7/` (sotto: «la cartella del
riesame»), file `test_riesame_*.py`. I file `test_riesame.py`, `rendi_vero.py`, `esito_verifica_istruzioni_codice_attuale.txt` e le cartelle `msg/`,
`vero/`, `script/` lì dentro non sono miei: li ha scritti un altro controllo nello stesso momento. Lancio di ogni prova: `cd /home/user/agentic_trading_system &&
TRADER_AI_BLOCCO=<cartella del riesame>/x.lock python -m pytest <file> -q -s -p no:cacheprovider`. Nessuna rete; i dati veri di
`trader_ai/avanti/` solo copiati e letti (`git status` di `trader_ai/avanti` vuoto dopo tutte le prove).

### Riepilogo e verdetto del riesame

**APPROVE con condizioni** per il riavvio sul conto simulato (il riavvio resta da approvare da Alessio). I sei problemi 188-193 sono
corretti: ogni prova della quindicesima, rifatta sul codice di adesso, dà il comportamento giusto, e le vecchie prove che mostravano i
difetti adesso falliscono. Una prova lunga a caso con guasti di rete (8 prove da 30 ore di mercato, 350-430 guasti l'una, circa un passo
su dieci fallito) non trova nessuna posizione senza stop per due passi riusciti, nessuna posizione sconosciuta al programma, nessun fermo
per conto estraneo, nessuna operazione persa o doppia, e la somma della memoria uguale al conto. Problemi nuovi: 194, 195 e 197 Bassi
(memoria del modello), 196 Medio solo per il conto demo (oggi spento). Nessun Bloccante, nessun Alto.

Condizioni:
1. Riavviare con il trader fermo e **nessuna operazione aperta nello stato**: nei dati salvati alle 08:07 (commit `8a7b513`) è così
   (`aperta` vuota, conto simulato senza posizione né ordini, ultima riga del diario: chiuso tutto a mano alle 07:11). Con un'operazione
   aperta la ricostruzione la scriverebbe due volte (195).
2. Prima del commit, copiare nei test del repository le corse del 188 che mancano (oggi c'è solo quella nel passo con l'esito «aperta»):
   dentro `_esegui` con «aperta» ed «eseguito», nel passo con l'esito «eseguito» del demo, sul conto simulato vero con la lettura lenta.
   Sono pronte in `test_riesame_188.py` (5 prove).
3. Committare i file con le impronte qui sotto. Dopo il primo passo controllare nel diario: «memoria ricostruita» con 13 corrette e 1
   aggiunta, 14 operazioni, somma dei netti −59,84 contro −59,86 del conto (rifatto sulla copia dei dati: `rapporto_ricostruzione.py`).
4. Il conto demo resta spento finché 196 non è corretto e provato sul demo, con una revisione nuova. 194 e 197 nel prossimo giro.

### Oggetto del riesame

* Impronte md5 (primi 8 caratteri) da confrontare al commit: `avvio.py` 97c2750e, `conto_simulato.py` c7f7e815, `conto_demo.py` 453e0288
  (invariato), `limiti.py` 19144b5b, `schema.py` 58dacc4f, `modello.py` 46038db6, `costi.py` 2b1e9f30, `giro.py` 0b813210, `messaggio.py`
  68cd3e83, `operazioni.py` 3120d09a, `ripara.py` b4628098, `calendario.py` f9540623, `trader_ai/.gitignore` 86892b11,
  `tests/test_controllo_26.py` 2d857f22; `vps/salva.sh` 76a65754 e `vps/installa.sh` dbfd1986 invariati. Ricontrollate uguali alla fine.
* Cambiati dopo la quindicesima: `avvio.py`, `conto_simulato.py`, `limiti.py`, `modello.py`, `messaggio.py`, `operazioni.py`, `ripara.py`,
  `calendario.py`, i test; nuovo `trader_ai/.gitignore`. Nessun file fuori da `trader_ai/` modificato; `bot/risk/hard_limits.py` invariato.

### Esito dei problemi della quindicesima

| Problema | Esito | Dove nel codice | Prova rifatta (cartella del riesame) |
|---|---|---|---|
| 188 Bloccante | **chiuso** | `avvio.py:445-473` (`_limite_sparito`: esito, poi rilettura della posizione; con la posizione → eseguito, poi protezione), chiamato dal passo `:215-218` e da `_esegui` `:670-680` | `test_riesame_188.py`, 5 passate: simulato con lettura lenta (lo stop 89.000 resta; dieci minuti dopo lo stop chiude: «stop iniziale», −2,86); simulato con un altro processo fra le due letture; esito «eseguito» del demo nel passo; dentro `_esegui` con «aperta» ed «eseguito» (la modifica dello stop vale sulla posizione: 89.100). Il passo dopo: nessun conto estraneo. |
| 189 Alto | **chiuso** | `avvio.py:433-436` (l'errore non diventa «mai eseguito»), `:451-455` (nessun annullo, si riprova), `:679-680` | `test_riesame_189.py`, 4 passate: errore una volta, poi «chiusa» → una sola operazione e modello richiamato con «operazione chiusa (stop iniziale)»; simulato con candele in errore → al passo dopo registrata una volta; errore dentro `_esegui` → «lo stato del tuo ordine limite non si è potuto leggere», poi registrata una volta. |
| 190 Medio | **chiuso** | `avvio.py:568-578` (versione non alzata, fino a 5 tentativi), `:603-604` (resoconti rifatti solo con correzioni) | `test_riesame_190.py` sulla copia dei dati veri, 2 passate: un errore → versione ferma, resoconto del 25 non toccato; al passo dopo 14 operazioni, somma −59,84 contro −59,86, numeri 1-14 stabili; cinque errori → rinuncia scritta, resoconto non toccato. Resta un testo: 197 a. |
| 191 Basso | **chiuso** | `avvio.py:56`, `:1025` (messaggi in `/opt/trader-ai-dati/trader_ai/messaggi_modello`), `trader_ai/.gitignore` | `test_riesame_191.py`, 2 passate: con `TRADER_AI_DATI` della macchina la cartella è fuori da `avanti/`; con git vero e `salva.sh` del repository l'albero remoto non ha mai i messaggi, prima e dopo l'arrivo del `.gitignore` nuovo. Resta il valore predefinito del costruttore: 197 b. |
| 192 Basso | **chiuso** | `avvio.py:772-773` («chiusa da te» solo dopo una chiusura riuscita), `:611-616` | `test_riesame_192_193.py` e `test_riesame_192_193_bis.py`: chiusura rifiutata e poi stop → «stop iniziale», uscita 87.991,2; corsa senza errori (lo stop scatta nel minuto contato da `chiudi`) → «stop iniziale». |
| 193 Medio | **chiuso** | `limiti.py:109-113` (limite che incrocia: stop e obiettivo anche sul prezzo di adesso), `avvio.py:723-731` (eseguito subito → come a mercato) | 3 passate: limite oltre il prezzo con lo stop in mezzo → scartato «dalla parte sbagliata del prezzo di adesso»; prezzo che scende fra il controllo e l'invio (stop rifiutato) → chiusura subito e richiamo; prezzo oltre lo stop mentre il modello pensa → scartato. Mai una posizione senza stop. |

Prove vecchie rifatte sul codice di adesso: `revisione_v7/test_prove_v7*.py` → le 8 prove dei difetti falliscono (cioè i difetti non ci
sono più); passano il controllo di parità del 190 e la prova vecchia del 191 (mette i file in `avanti/messaggi`, dove il codice non
scrive più). `revisione_v7/verifica_ordini/` → le 10 prove dei difetti falliscono, le 7 di controllo passano. Prova lunga senza guasti
`revisione_v7/scenari/test_s11_prova_lunga.py` → 6 passate.

### Parti nuove rilette

* `_esito`, `_esito_o_niente`, `_limite_sparito`, `_eseguito` (`avvio.py:433-493`): OK sul conto simulato. Sul demo l'esito «eseguito»
  non distingue un'operazione aperta da una chiusa e tutto dipende da una sola rilettura delle posizioni: **196**.
* Ramo «limite già oltre il prezzo» (`avvio.py:723-731`): OK (prova 193 b). Sul demo un resto non eseguito si annulla prima dello stop
  (`:727-728`; l'annullo del demo non lancia errori): da provare sul demo.
* Richiamo con il motivo intero (`:205`, `:281-282`, `:674`, `:683`, `:755`, `:769-770`, `:775`, `:792-793`): OK; il testo va solo nel
  messaggio (`messaggio.py:465`). Ogni richiamo è una chiamata con il tetto controllato prima.
* `_chiudi_ora` e `_protezione` che ritornano il modo (`:611-636`): OK; con la posizione già chiusa dallo stop vale il modo del conto.
* `_obiettivo_sul_conto` (`:638-654`): OK. Prova sul conto simulato vero (`test_riesame_nuovi.py`): limite eseguito alle 10:04, prezzo
  oltre l'obiettivo prima del passo → chiusura a mercato registrata «obiettivo», +1,64, modello richiamato.
* Obiettivo di un limite in attesa solo nello stato (`:787-788`): OK, scelta (b). Il conto simulato di adesso non ha ordini: nessun
  obiettivo vecchio rimasto al riavvio.
* Cambio di giorno dopo le chiusure (`:234-248`): OK; prima non si usa niente del giorno nuovo.
* `_ripara_memoria` con i tentativi (`:561-609`): OK per il 190; con un'operazione aperta che si chiude prima del primo passo: **195**.
* `limiti.py:96-99` (margine più commissione) e `:109-113` (limite che incrocia): OK, coerenti con il conto simulato (`conto_simulato.py:393`).
* `conto_simulato.annulla_tutto` che conta prima i minuti chiusi (`:426-431`): giusto come su Binance, ma in un caso raro una operazione
  si perde: **194**.
* `modello.chiama` (`modello.py:54-89`), provato con l'SDK vero (2.12.0, come `requirements.txt`) e un trasporto finto, senza rete
  (`test_riesame_modello.py`, 10 passate): la richiesta porta `output_config.format` di tipo `json_schema`, sforzo «high», ragionamento
  adattivo riassunto, cache da un'ora sulle istruzioni e sul primo blocco, 16.000 token al massimo. Risposta valida → «ok»; tagliata nel
  JSON o nel ragionamento → «troncata» con i token dichiarati; rifiuto → «rifiuto»; JSON fuori schema o vuoto → «fuori_schema» con i
  token; 400, 529, tempo scaduto, rete → «errore», un solo tentativo. Con il tempo massimo esplicito di 600 secondi l'SDK non applica il
  suo blocco delle richieste lunghe (vale solo con il tempo predefinito).

### Checklist A–F (riesame)

* **A.** `bot/risk/hard_limits.py` invariato; leva 10 (`limiti.py:15`), obiettivo 3% (`:14`), tetto 5 dollari (`costi.py:22`), 16.000 token
  (`:25`) invariati. Tetto: il messaggio costruito con il codice di adesso (copia `wt` della cartella di lavoro, `v7b/messaggio_v7.txt`)
  ha 27.247 caratteri (istruzioni 3.939, memoria stabile 9.444, il resto 13.864): costo massimo riservato 0,465 dollari; il costo vero
  più alto possibile resta sotto per qualunque rapporto sopra circa 1,15 caratteri per token (misurato 1,8). Fermo a mano a inizio
  passo, all'inizio di `_esegui`, prima e dopo l'invio (`avvio.py:171`, `:657`, `:717`, `:732`); `chiudi` senza Firebase (`:869-902`). OK.
* **B.** Passi e minimi da `exchangeInfo` invariati; identificativo `tai…` salvato con l'intenzione prima dell'invio (`:706-715`);
  chiusure «solo riduzione» sul demo (`conto_demo.py:272-281`); stop e obiettivo sul prezzo mark; leva e margine separato prima di ogni
  apertura. Stop di ogni posizione sul conto: OK sul simulato; sul demo **196**.
* **C.** Stato riletto dal conto a ogni passo e prima di ogni ordine; esito in errore = nessuna azione; ricostruzione rimandata; candele
  chiuse e pause per 429 e 418 invariate. Memoria: **194**, **195**, **197**.
* **D.** Simulato: solo GET pubblici su `fapi.binance.com`, senza chiave; demo: solo `demo-fapi.binance.com`; `config.json` «simulato». OK.
* **E.** Nessuna chiave nel diff; messaggi interi fuori da git (191 chiuso). Chiavi senza prelievo: da confermare con Alessio (oggi il
  trader non usa chiavi di Binance). OK.
* **F.** `TRADER_AI_BLOCCO=<cartella del riesame>/x.lock python -m pytest trader_ai/tests -q` → **129 passed**. Suite intera
  `python3 -m pytest tests/ -q` → **2825 passed, 1 skipped, 1 deselected** in 198 s (escluso
  `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore`, che da solo fallisce come alla quindicesima: ricerca,
  nessun legame con `trader_ai/`). Test dei limiti (`tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_strategie_restano_accese.py`)
  → 23 passed. Le mie prove del riesame (i 12 file `test_riesame_*.py`): **42 passate**; quelle di 194-197 passano perché mostrano il
  difetto. Nei test del repository mancano: tre delle quattro corse del 188 (condizione 2) e i casi 194-196.

### Problemi nuovi

**194 — Basso — `trader_ai/avvio.py:804-814` (`_annulla_limite`) con `trader_ai/conto_simulato.py:426-431`.**
* Cosa succede. Il modello annulla un limite («chiudi»). `annulla_tutto` del simulato conta prima i minuti chiusi: se nel minuto appena
  chiuso il prezzo è passato oltre il limite **e** oltre lo stop, il limite si esegue e lo stop lo chiude nello stesso minuto. Poi
  `_annulla_limite` non trova né posizione né ordine e scrive «ordine limite annullato da te»: l'operazione c'è sul conto (perdita nel
  portafoglio) ma non nella memoria, e il richiamo dice «nessuna operazione». È il difetto 2.2 del controllo, in un caso raro.
* Quando. Il minuto deve finire nel mezzo secondo fra l'aggiornamento all'inizio di `_esegui` e l'annullo (in mezzo c'è la lettura del
  prezzo) e quel minuto deve attraversare limite e stop. Raro sul simulato; sul demo la stessa corsa c'è per natura.
* Prova (eseguita). `test_riesame_nuovi.py::test_annullo_di_un_limite_eseguito_e_fermato_nel_minuto_appena_chiuso`: limite lungo 89.500,
  stop 89.000, minuto 10:14 con minimo 88.900 contato durante l'annullo → `conto: chiuse [('stop', 88991.1)] | portafoglio 1000.0 ->
  997.14 | memoria: operazioni 0 | richiama ordine limite annullato da te (nessuna operazione)`.
* Correzione suggerita alla sessione principale. In `_annulla_limite`, quando non resta né posizione né ordine, chiedere `_esito(a)`: con
  «chiusa» o «eseguito» → `_eseguito(a, esito, ora)` e `_registra_chiusura`; con un errore → lasciare `aperta` e riprovare (come il 189).
  Test: la corsa qui sopra.

**195 — Basso — `trader_ai/avvio.py:196-197` (ricostruzione prima delle chiusure) con `trader_ai/ripara.py:103-117`.**
* Cosa succede. Al primo passo della versione 7 la ricostruzione aggiunge alla memoria ogni posizione chiusa del conto che trova
  un'apertura nel diario. Se nello stato c'è un'operazione aperta che si è chiusa sul conto prima di quel passo, la ricostruzione la
  aggiunge e subito dopo il passo la registra di nuovo (`avvio.py:215-220`): la stessa operazione due volte, con due numeri.
* Quando. Solo al primo passo dopo il riavvio con la versione 7, e solo se nello stato c'è un'operazione aperta. Con i dati di adesso
  (nessuna operazione aperta) non succede: condizione 1.
* Prova (eseguita). `test_riesame_ripara_aperta.py`: apertura a mercato, memoria riportata alla versione 6, stop scattato durante il
  fermo del servizio → `operazioni in memoria [(1, 'stop iniziale', 90009.0, -5.54), (2, 'stop iniziale', 90009.0, -5.54)]`.
* Correzione suggerita. In `ricostruisci` saltare la posizione con il nome d'ordine di `st["aperta"]["cid"]`, oppure rimandare la
  ricostruzione a un passo con `aperta` vuota.

**196 — Medio, solo per il conto demo (oggi spento) — `trader_ai/avvio.py:456-466` con `trader_ai/conto_demo.py:175-182`.**
* Cosa succede. Sul demo `esito_ordine` dice «eseguito» sia per un'operazione aperta sia per una già chiusa. La correzione del 188 decide
  con una sola rilettura delle posizioni: se la posizione non si vede, «eseguito e chiuso» → chiusura inventata (uscita stimata),
  `annulla_tutto` toglie lo stop e al passo dopo, quando la posizione si vede, il programma si ferma come davanti a una posizione d'altri,
  senza toccarla: **posizione senza stop**. Basta che la lettura delle posizioni del demo arrivi in ritardo rispetto allo stato
  dell'ordine.
* Quando. Solo sul demo, se quel ritardo esiste (va misurato sul demo). Sul simulato l'esito dice «aperta» o «chiusa» e non succede.
* Prova (eseguita). `test_riesame_demo_ritardo.py`: il vero `ContoDemo.esito_ordine` con un ordine FILLED e due letture delle posizioni
  in ritardo → `operazioni [('chiusa sul conto (stop, obiettivo o liquidazione)', True)] | aperta None | stop sul conto []`, poi
  `posizione True | stop [] | estraneo: una posizione che il trader non ha aperto`.
* Correzione suggerita (prima del demo). Con «eseguito» e nessuna posizione non registrare e non annullare nello stesso passo: riprovare
  al passo dopo e registrare solo se la posizione manca ancora, oppure confermare la chiusura dagli scambi dell'ordine sul conto
  (`GET /fapi/v1/userTrades`); test con la semantica del demo.

**197 — Basso — tre rifiniture.**
* a) `avvio.py:576-577` e `:601-602`: dopo cinque letture fallite il diario scrive «rinuncio» e subito dopo «memoria ricostruita dal
  conto e dal diario» (0 corrette, 0 aggiunte). Prova: `test_riesame_190.py::test_190_b_cinque_errori_rinuncia` (eventi stampati).
  Correzione: con il conto non letto scrivere «memoria solo numerata: conto non letto».
* b) `avvio.py:117`: senza `messaggi` il costruttore scrive i messaggi in `<dati>/messaggi`, cioè dentro `avanti/` sulla macchina, che
  `salva.sh` porta nel repository. Oggi solo `main()` chiama il modello e passa la cartella giusta (`:1025`): un punto d'ingresso nuovo
  ricadrebbe nel 191. Prova: `test_riesame_rifiniture.py::test_cartella_dei_messaggi_predefinita_dentro_avanti` →
  `/opt/trader-ai-dati/trader_ai/avanti/messaggi`. Correzione: predefinita `self.cartella.parent / "messaggi_modello"`.
* c) `avvio.py:208-210`: un ordine a mercato eseguito con la risposta persa si adotta al passo dopo senza `_eseguito`: entrata al prezzo
  della decisione, nessuna ora di esecuzione, nessun 1 R e nessuna spesa d'entrata in memoria (lo stop invece si rimette). Prova:
  `test_riesame_rifiniture.py::test_risposta_persa_di_un_ordine_a_mercato_senza_i_dati_dell_esecuzione` → `entrata nel programma
  90000.0 (posizione 90050) | eseguita None | R None`. Correzione: in quel ramo `_eseguito(a, self._esito_o_niente(a), ora, pos)`.

### Invarianti modificati (dalla quindicesima)

* Ordine limite sparito dal libro: esito dal conto **e** rilettura della posizione; posizione presente → eseguito e protezione; esito in
  errore o letture che non tornano → nessuna azione, si riprova; «chiusa» o «eseguito» senza posizione → registrata; nessun esito →
  annullo (`avvio.py:445-473`).
* Limite che incrocia il prezzo: la decisione si controlla anche sul prezzo di adesso (`limiti.py:109-113`); un limite eseguito subito
  diventa un'operazione a mercato, con lo stop subito o la chiusura (`avvio.py:723-756`).
* Obiettivo di un limite in attesa solo nello stato, sul conto all'esecuzione; già superato → chiusura a mercato come «obiettivo»
  (`avvio.py:638-654`, `:787-788`).
* Margine più commissione d'entrata dentro il disponibile (`limiti.py:96-99`).
* Messaggi interi fuori da `avanti/` (`avvio.py:56`); cambio di giorno dopo le chiusure (`:234-248`); ricostruzione con al massimo 5
  tentativi (`:568-578`); annullo del simulato che conta prima i minuti chiusi (`conto_simulato.py:426-431`).
* Nessun valore dei limiti cambiato; `bot/risk/hard_limits.py` invariato.

### Decisioni per Alessio

* Il riavvio con questa versione sul conto simulato: è suo, con le condizioni 1-3 qui sopra.
* Il passaggio al conto demo: non con questo codice; prima la correzione del 196, una prova sul demo dell'esito degli ordini e una
  revisione nuova.
* Restano sue le scelte 5.1-5.3 del controllo (tetto di spesa, maiuscole, 3% prima delle spese): non toccate dal riesame.

### Domande aperte

* Sul demo la lettura delle posizioni può arrivare in ritardo rispetto allo stato di un ordine eseguito? Da misurare sul demo prima di
  usarlo (196).
* Dopo il riavvio vanno guardati nelle prime chiamate `usage`, durata ed esiti «troncata» o «errore»: il tetto regge sopra circa 1,15
  caratteri per token (misurato 1,8), ma il rapporto del messaggio nuovo (27.247 caratteri) non è ancora misurato.
* La memoria del revisore (`reviews/`) da quest'area non si scrive: le righe nuove della quindicesima e del riesame (indice, registro,
  archivio, mappa con la sezione 15 aggiornata) sono in `<cartella del riesame>/righe_per_reviews.patch` (solo i quattro file, si
  applica con `git apply`), per la sessione che può applicarle.

## Secondo riesame (26 novembre 2026, sera, sulla copia con le correzioni del riesame)

Revisore: live-path-reviewer. Base: il codice del riesame, committato come `c52fbab` (`avvio.py` 97c2750e). Oggetto: la copia
`/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/wt2/trader_ai` (sotto: «la copia»), con
le correzioni di 194-197 e dei punti N1-N5 del verificatore. Prove mie in
`/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/riesame2_v7/` (sotto: «la cartella del
secondo riesame»). Lancio di ogni prova dalla copia: `cd <copia>/.. && TRADER_AI_BLOCCO=<cartella del secondo riesame>/x.lock
PYTHONPATH=<copia>/.. python -m pytest <file> -q -s -p no:cacheprovider` (per `verifica_altri/` anche
`revisione_v7/scenari` nel `PYTHONPATH`); in ogni cartella di prove un `conftest.py` controlla che
`trader_ai` venga dalla copia. Nessuna rete; i dati veri di `trader_ai/avanti/` solo copiati e letti; `git status` del repository vuoto
alla fine; la copia non è cambiata (impronte rilette alla fine).

Attenzione per chi rifà le prove del verificatore: `riesame_v7/verifica_altri/rete_finta.py` mette la radice del repository in testa a
`sys.path` e `test_n3_n5.py` legge l'espressione da `trader_ai/avvio.py` del repository: lanciate così provano il codice del repository
anche con `PYTHONPATH` sulla copia. Le ho rifatte da copie che puntano alla copia (`<cartella del secondo riesame>/verifica_altri/`,
`prove_riesame/` per le mie del riesame, `verifica_ordini/` per quelle dell'altro verificatore).

### Riepilogo e verdetto del secondo riesame

**APPROVE con condizioni** per il commit della copia e per il riavvio sul conto simulato (il riavvio resta da approvare da Alessio).
194, 195, 196, 197 (a, b, c) e N1-N5 sono corretti sul conto simulato: ogni prova che mostrava un difetto, rifatta sulla copia, adesso
fallisce (cioè il difetto non c'è più), e le prove di controllo passano. Una prova lunga a caso con guasti di rete sulla copia (14 prove
da 30 ore di mercato, 6 con l'8% delle richieste in errore, fino a 1.062 guasti l'una) non trova nessuna posizione senza stop per due
passi riusciti, nessuna posizione sconosciuta, nessun ordine del trader più vecchio della posizione sotto di lei, nessun fermo per
conto estraneo, nessuna operazione doppia o persa (contate per nome d'ordine), la somma della memoria uguale al conto, nessuna uscita
stimata rimasta; le strade nuove sono passate davvero (32 annullamenti falliti dopo una chiusura, 33 ripresi al passo dopo).
Nessun Bloccante, nessun Alto. Nuovi: **198 Medio, solo demo** (la radice del 196 su un'altra strada: `_annulla_limite`), **202 Medio**
(sei correzioni su quattordici senza un test che se ne accorga), 199 Basso solo demo, 200 Basso preesistente, 201 Basso (solo al
passaggio dalla versione 6 con un limite in attesa: operazione persa, regressione della correzione del 195).

Condizioni:
1. Riavviare con il trader fermo e **nessuna operazione aperta nello stato**. Nei dati delle 08:07 (`8a7b513`) è così: `aperta` vuota,
   conto simulato senza posizione né ordini, ultima riga del diario «chiuso tutto a mano» alle 07:11. Adesso serve per il 201 (e
   perché un'operazione aperta dalla versione 6 resterebbe con l'uscita stimata per sempre: riga del 195).
2. **Prima del commit**, nei test del repository le prove che mancano (202): annullamento prima di aprire, ricostruzione con
   l'operazione aperta passata da `_ripara_memoria`, N2 con arrotondamenti diversi, N4, 197 b, 197 c. Sono pronte (vedi 202).
3. Committare il codice con le impronte qui sotto (`avvio.py` c19205d2, `messaggio.py` 0ca870c9, `ripara.py` 4e1e13a9; i file di test
   cambiano per la condizione 2). Dopo il primo passo, nel diario: «memoria ricostruita dal conto e dal diario» con 13 corrette,
   1 aggiunta, 0 lasciate, 11 lezioni; 14 operazioni; somma dei netti −59,84 contro −59,86 del conto (rifatto con la copia sulla copia
   dei dati: `rapporto_ricostruzione.py` nella cartella del secondo riesame).
4. Il conto demo resta spento: prima le correzioni di 198 e 199, la misura sul demo del ritardo della lettura delle posizioni, una
   revisione nuova.

### Oggetto del secondo riesame

* File cambiati rispetto a `c52fbab`: `avvio.py`, `messaggio.py`, `ripara.py`, `tests/test_controllo_26.py` (7 test nuovi, uno cambiato);
  tutti gli altri file di `trader_ai/` uguali al repository (confronto byte per byte). Nessun file fuori da `trader_ai/`;
  `bot/risk/hard_limits.py` invariato.
* **Impronte md5 (primi 8 caratteri) della copia approvata**: `avvio.py` c19205d2, `messaggio.py` 0ca870c9, `ripara.py` 4e1e13a9,
  `tests/test_controllo_26.py` 3b7fc12a; invariati: `conto_simulato.py` c7f7e815, `conto_demo.py` 453e0288, `limiti.py` 19144b5b,
  `schema.py` 58dacc4f, `modello.py` 46038db6, `costi.py` 2b1e9f30, `giro.py` 0b813210, `operazioni.py` 3120d09a, `calendario.py`
  f9540623, `trader_ai/.gitignore` 86892b11, `tests/test_corse_188.py` f759675a, `vps/salva.sh` 76a65754, `vps/installa.sh` dbfd1986.
* Invarianti coinvolti: stop sul conto per ogni posizione; nessun ordine del trader sotto un'operazione nuova; memoria uguale al conto;
  fermo a mano; conto estraneo.

### Esito dei problemi

| Problema | Esito | Dove nel codice (copia) | Prova rifatta sulla copia |
|---|---|---|---|
| 194 | **chiuso** sul simulato | `avvio.py:865-877` | `prove_riesame/test_riesame_nuovi.py::test_annullo_di_un_limite...` ora fallisce: `memoria: operazioni 1 \| richiama operazione chiusa (stop iniziale)`. `verifica_ordini/test_v194_annullo.py`: le due prove del difetto (simulato e demo) falliscono, l'operazione è in memoria. Sul demo, con la posizione letta in ritardo: **198**. |
| 195 | **chiuso** per l'operazione doppia | `ripara.py:86-109`, `avvio.py:624` | `test_riesame_ripara_aperta.py` ora fallisce: 1 operazione (era 2). Passaggio vero in due processi (`verifica_ordini/v195_migrazione.py`: versione 6, poi la copia): `memoria: [(1, 'stop iniziale', 90009.0, 88900, True, -5.54)]`, «corrette 0, aggiunte 0». Restano: uscita stimata per sempre (88.900 contro 88.991,1; il netto è giusto) perché la posizione della versione 6 non ha il nome d'ordine; con un limite in attesa: **201**. |
| 196 | **chiuso** in `_limite_sparito` | `avvio.py:472-477` | `test_riesame_demo_ritardo.py` ora fallisce: dopo il primo passo nessuna operazione e lo stop 89.000 resta; al passo dopo `posizione True \| stop [89000.0] \| estraneo: None`. `verifica_ordini/test_v196_demo.py[1]` fallisce allo stesso modo (classe `ContoDemo` vera). La stessa radice resta in `_annulla_limite`: **198**. |
| 197 a | **chiuso** | `avvio.py:646-651` | `test_riesame_190.py::test_190_b`: dopo «rinuncio» il diario scrive «memoria solo numerata: conto non letto». `verifica_ordini/test_v197.py::test_a` fallisce. |
| 197 b | **chiuso** | `avvio.py:117-119` | `test_riesame_rifiniture.py::test_cartella...` ora fallisce: `/opt/trader-ai-dati/trader_ai/messaggi_modello`. Nessun test nel repository (202). |
| 197 c | **chiuso** | `avvio.py:217-219` | `test_riesame_rifiniture.py::test_risposta_persa...` fallisce: `entrata 90050.0 (posizione 90050) \| eseguita 10:01:30 \| R 10.7391`, stop rimesso; `test_v197.py::test_c` fallisce: in memoria entrata 90.009 vera, uscita 88.991,1, −1,00 R. Nessun test nel repository (202). |
| N1 | **chiuso** sul simulato | `avvio.py:574-579`, `:200-205`, `:742-745` | `verifica_altri/test_n1.py`: le 4 prove del difetto falliscono. Con il 429 sulle candele dell'escursione: «operazione chiusa» nel diario, `richiama: operazione chiusa (chiusa da te)`, nessuno scarto, modello richiamato appena finisce la pausa (10:17:05); rete giù nell'annullamento: nessuno scarto; chiusa mentre il modello pensa: richiamo; protezione: motivo «operazione chiusa (obiettivo)». Prova mia: con l'annullamento in errore la nuova non si apre (`rifiutata dal conto: GET /fapi/v1/klines: 429: pausa`). Sul demo l'annullamento non lancia errori: **199**. |
| N2 | **chiuso** | `messaggio.py:132` | Dati veri: `lunghi 5 (1 vinte, 4 perse, -11.92), corti 9 (1 vinte, 8 perse, -47.94)`, netto −59,86 (prima −11,91 e −47,93). Prova mia con tre operazioni da −1,004: `netto -3.01 ... lunghi 3 (0 vinte, 3 perse, -3.01)`; con la formula di prima −3,00. La prova del repository non distingue le due formule (202). |
| N3 | **chiuso** | `avvio.py:344-345` | `test_n3_n5.py`: «0.42%», «89.500», «1.25 R» restano interi (anche nella nota del messaggio); «10:15» si toglie; «60699.5», «1.5 R», «30m» restano. |
| N4 | **chiuso** | `avvio.py:642-645` | `test_n2_n4_dati_veri.py::test_n4_con_guasto` ora fallisce: 12 lezioni (11 vecchie e quella scritta durante l'attesa, una volta sola), come senza guasto. Nessun test nel repository (202). Un perché oltre 380 caratteri comparirebbe due volte (tagli diversi in `_lezioni` e in `ripara.py:172`): nel diario vero il più lungo è 217. |
| N5 | **chiuso** sul simulato | `avvio.py:211`, `:582-602` | `test_n3_n5.py::test_n5` fallisce: al passo dopo uscita 88.991,1, chiusa 10:18, prezzo −5,09, spese −0,45, netto −5,54, nel messaggio «uscita 88991.1: stop iniziale». Prove lunghe: nessuna uscita stimata rimasta. Sul demo l'esito non dà mai l'uscita (scelta scritta in `conto_demo.py:162-166`): resta stimata. |

Altre prove rifatte sulla copia: le mie del riesame (`prove_riesame/`, 42) → 37 passate e 5 fallite, esattamente le 5 che mostravano i
difetti 194, 195, 196, 197 b, 197 c (la 197 a stampava gli eventi senza controllarli); quelle del verificatore (`verifica_altri/`, 21) →
11 fallite (i difetti) e 10 passate (i controlli, più due prove che non controllano il difetto: N2 calcola i lati con la sua
formula, la protezione con il 429 stampa e basta); quelle dell'altro verificatore (`verifica_ordini/`, 8) → 5 fallite (difetti) e 3
passate: i due controlli e `test_v196_annullo_demo.py[1]`, che mostra il 198.

### Parti nuove rilette

* `_annulla_limite` che legge l'esito (`avvio.py:854-887`): OK sul simulato. Con l'esito non letto si lascia l'operazione «in attesa»
  con limite e stop già annullati: il passo dopo decide con `_limite_sparito` e nessuna posizione può nascere (il limite non c'è più);
  il modello legge «rifiutata dal conto: lo stato del tuo ordine limite non si è potuto leggere» anche se l'annullamento è riuscito
  (solo testo). Sul demo «eseguito» senza posizione diventa una chiusura: 198.
* `_limite_sparito` con la conferma al passo dopo per «eseguito» (`:472-477`): OK. La seconda lettura può arrivare nello stesso passo
  dentro `_esegui`, dopo la risposta del modello (secondi o minuti dopo): basta per un ritardo di lettura breve. Il segno resta
  sull'operazione ma vale solo per quell'ordine. Sul simulato «eseguito» non esiste: strada mai presa (prove lunghe: 0 volte).
* `_registra_chiusura` con l'annullamento che non fa fallire la chiusura e `da_annullare` (`:574-579`): OK. Il segno non si toglie
  dopo un annullamento riuscito più avanti: innocuo (un annullamento in più con il conto senza operazione). Se dopo la chiusura il
  passo si interrompe per un altro errore: 200.
* Annullamento all'inizio del passo (`:200-205`): OK; dopo il fermo a mano e il controllo del conto estraneo; un errore interrompe il
  passo quando non c'è nessuna operazione (e quindi nessuna posizione: il controllo del conto estraneo viene prima).
* Annullamento degli ordini rimasti prima di aprire (`:742-745`): OK sul simulato (prova mia, nelle due varianti); sul demo l'esito
  non si controlla: 199. Nessun test nel repository: 202.
* `_correggi_uscite_stimate` (`:582-602`): OK; al massimo le ultime 5 operazioni e 20 tentativi; nessun ordine; non ricalcola
  «favore» e «contro» (dettaglio della memoria).
* `ricostruisci` con l'operazione aperta esclusa (`ripara.py:106-109`): OK per il doppio; 201.
* Cartella dei messaggi predefinita (`:117-119`): OK; resta dentro `avanti/` solo con un percorso diverso ma uguale (relativo o con
  un collegamento), caso non usato da nessun punto d'ingresso.
* Risposta persa adottata con `_eseguito` (`:217-219`): OK; lo stop si rimette con la protezione come prima.
* Mutazioni (`mutazioni.py`, 14 correzioni tolte una alla volta da una copia della copia): 8 prese dai test della copia, 6 vive: 202.

### Checklist A–F (secondo riesame)

* **A.** `bot/risk/hard_limits.py` invariato (ultimo commit `41ee966`); `limiti.py` (leva 10, obiettivo 3%) e `costi.py` (tetto di 5
  dollari, 16.000 token) uguali al repository. Fermo a mano: i due annullamenti nuovi stanno dopo il controllo del fermo (`:173`,
  `:706`); `chiudi` senza Firebase invariato (`:935-968`). OK.
* **B.** Ordini: annullamento nuovo prima di aprire (OK sul simulato; demo 199); nomi d'ordine, «solo riduzione», prezzo mark, leva e
  margine separato invariati (`conto_demo.py` uguale). Stop di ogni posizione sul conto: OK sul simulato (prove lunghe); demo **198**.
* **C.** Stato letto dal conto: 194, 196, N1, N5 OK; ricostruzione: **201**; stato a metà dopo una chiusura: **200**. 429 e 418: la
  pausa del conto simulato si rispetta (prova N1 con il 429 vero di `MercatoPubblico`). Candele chiuse invariate.
* **D.** Invariato: `config.json` «simulato»; il demo solo su `demo-fapi.binance.com` (le mie prove del demo controllano l'indirizzo
  a ogni richiesta). OK.
* **E.** Nessuna chiave nella differenza; il nome d'ordine scritto nel diario non è un segreto. Chiavi senza prelievo: da confermare
  con Alessio (oggi il simulato non usa chiavi). OK.
* **F.** Copia: `trader_ai/tests` → **140 passed, 1 failed** (`test_il_fermo_non_entra_mai_in_git`: la copia non è un repository
  git); repository `c52fbab`: `trader_ai/tests` → **134 passed** (141 = 134 + 7 nuovi). Suite intera `python3 -m pytest tests/ -q`
  (escluso `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore`, ricerca) → **2825 passed, 1 skipped,
  1 deselected**. Limiti (`tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_strategie_restano_accese.py`) → **23 passed**.
  Prove mie: `test_secondo_riesame.py` → 7 passed (le prove di 198-200 passano perché mostrano il difetto); `test_lunga_eventi.py`
  → 14 passed. Mutazioni: **202**.

### Problemi nuovi

**198 — Medio, solo per il conto demo (oggi spento) — `trader_ai/avvio.py:865-877` con `trader_ai/conto_demo.py:175-182`.**
* Cosa succede. Il modello annulla il suo limite («chiudi»). Se il limite si esegue proprio prima dell'annullamento e la rilettura delle
  posizioni del demo arriva in ritardo, l'esito «eseguito» del demo (che vale anche per una posizione aperta) diventa «eseguito e
  chiuso»: chiusura inventata in memoria, e lo stop è già stato annullato da `annulla_tutto`. Al passo dopo la posizione si vede e il
  programma si ferma come davanti a una posizione d'altri, senza toccarla: **posizione senza stop**. È la radice del 196 su un'altra
  strada (la correzione del 196 c'è solo in `_limite_sparito`). Non è una regressione: sul codice di `c52fbab` lo stesso caso finisce
  uguale, con la memoria vuota invece della chiusura inventata.
* Quando. Solo sul demo, con il limite eseguito nell'istante dell'annullamento e la lettura delle posizioni in ritardo (lo stesso
  ritardo da misurare del 196). Letto e non provato: la stessa radice, più rara, nel ramo dell'obiettivo del giorno (`avvio.py:266-270`:
  con un limite «in attesa» `chiudi` senza posizione annulla anche lo stop).
* Prova (eseguita). `test_secondo_riesame.py::test_198_...` con la classe `ContoDemo` vera e un Binance finto sotto: ritardo 0 → «il
  limite si era eseguito mentre lo annullavo: chiudo a mercato», posizione chiusa; ritardo 1 → «il limite si era eseguito e chiuso prima
  dell'annullamento», poi `posizione vera sul demo {'q': 0.005, 'e': 89500.0, 'lato': 'lungo'} | ordini condizionati [] | estraneo una
  posizione che il trader non ha aperto`. Stesso esito nella prova dell'altro verificatore (`verifica_ordini/test_v196_annullo_demo.py[1]`).
* Correzione suggerita alla sessione principale (prima del demo). In `_annulla_limite`, con l'esito «eseguito» (non «chiusa») e nessuna
  posizione letta, non registrare: lasciare l'operazione come eseguita da confermare (non più «in attesa», con il segno «da chiudere»)
  e alzare l'errore «riprovo»; al passo dopo, se la posizione c'è, la protezione rimette lo stop e il programma la chiude a mercato come
  chiesto; se non c'è, si registra la chiusura. Test con la semantica del demo: la prova qui sopra.

**199 — Basso, solo per il conto demo — `trader_ai/conto_demo.py:265-270` con `trader_ai/avvio.py:574-579` e `:742-745`.**
* Cosa succede. Sul demo `annulla_tutto` scrive l'errore e va avanti: `da_annullare` non si mette mai e l'annullamento prima di aprire
  non controlla l'esito. Se l'annullamento fallisce (rete, errore 5xx di Binance), l'obiettivo o lo stop dell'operazione chiusa resta
  sotto l'operazione nuova, e il programma non lo sa. Non toglie protezione (gli ordini «chiudi tutto» possono solo ridurre), ma può
  chiudere l'operazione nuova al livello di quella vecchia. Preesistente: la correzione N1 vale solo dove l'annullamento lancia l'errore.
* Prova (eseguita). `test_secondo_riesame.py::test_199_...` (classe `ContoDemo` vera, Binance finto che risponde 500 agli annullamenti):
  `ordini condizionati sul demo [('tait', 'TAKE_PROFIT_MARKET', '91000'), ('tais', 'STOP_MARKET', '88000')] | da_annullare None`;
  l'operazione nuova non ha obiettivo nello stato. Uguale sul codice di `c52fbab`.
* Correzione suggerita (prima del demo). Dopo `annulla_tutto` (alla chiusura e prima di aprire) rileggere gli ordini del simbolo: se ne
  resta uno del trader, `da_annullare` alla chiusura e nessuna apertura prima di aprire; oppure far lanciare l'errore a
  `ContoDemo.annulla_tutto`.

**200 — Basso, preesistente — `trader_ai/avvio.py:233-241` (e ogni lettura del conto dopo una chiusura nello stesso passo).**
* Cosa succede. Una chiusura registrata (memoria del processo e diario) si perde dallo stato se il passo si interrompe dopo, per
  esempio con `saldo()` in errore (`:241`): lo stato non si salva e il passo dopo registra di nuovo la stessa operazione dal conto. In
  memoria resta una volta sola (giusto), ma con il modo letto dal conto invece di quello del programma («stop iniziale» invece di
  «chiusa: senza stop valido sul conto»; «chiusa a mercato» invece di «obiettivo») e nel diario ci sono due «operazione chiusa». Con N1
  l'evento si scrive prima dell'annullamento, quindi succede anche quando a fallire sono l'annullamento e poi un'altra lettura (prova del
  verificatore, protezione con il 429: 2 eventi, prima 1).
* Prova (eseguita). `test_secondo_riesame.py::test_200_...`: `errore del passo: GET /fapi/v2/account: rete: Read timed out | sul disco
  dopo l'errore: aperta True, operazioni 0` → `operazioni [(1, 'stop iniziale')] | «operazione chiusa» nel diario 2 | modi scritti
  ['chiusa: senza stop valido sul conto', 'stop iniziale']`. Prove lunghe: da 1 a 9 doppioni per prova sulla copia (14 prove), da 2 a 6 sul
  codice di `c52fbab` (le 6 prove all'8%).
* Correzione suggerita. Salvare lo stato subito dopo ogni chiusura registrata, con il richiamo del modello già messo, così un errore
  dopo non la fa rifare; oppure scrivere l'evento solo quando lo stato è salvato.

**201 — Basso, solo al primo passo della versione 7 con un limite in attesa nello stato — `trader_ai/ripara.py:106-109` con
`trader_ai/avvio.py:455-489`.**
* Cosa succede. La correzione del 195 toglie dalla ricostruzione la posizione dell'operazione aperta, perché «la registra il passo». Ma
  il conto della versione 6 non scriveva il nome d'ordine nella posizione: se il limite si è eseguito sotto la versione 6 senza che il
  programma lo vedesse e poi si è chiuso, il passo non lo trova (`esito_ordine` → nessuno) e scrive «ordine limite non più sul conto e
  mai eseguito». L'operazione, con la sua perdita sul conto, non entra mai in memoria. Sul codice di `c52fbab` la ricostruzione la
  aggiungeva: regressione.
* Quando. Solo se si riavvia con un limite in attesa nello stato; con i dati di adesso (nessuna operazione aperta) no: condizione 1.
  Dopo il primo passo della versione 7 la ricostruzione non gira più.
* Prova (eseguita). `v195_limite.py` lanciato da `lancia_v195_limite.py` (due processi: codice della versione 6 di `a94db04`, poi il
  codice da provare): copia → `memoria: [] | aperta None`, eventi «corrette 0, aggiunte 0» e «ordine limite non più sul conto e mai
  eseguito», conto −2,86; `c52fbab` → `memoria: [(1, 'stop iniziale', 89500.0, -2.86)]`, «aggiunte 1».
* Correzione suggerita. Rimandare la ricostruzione al primo passo senza operazione aperta (la seconda proposta del 195): il passo
  registra la chiusura come può e la ricostruzione dopo la trova e la corregge, o la aggiunge. Toglie anche l'uscita stimata per sempre
  dell'operazione aperta dalla versione 6.

**202 — Medio — `trader_ai/tests/test_controllo_26.py` (copia): test che non coprono sei correzioni.**
* Cosa succede. Sei correzioni su quattordici si possono togliere senza che un test del repository se ne accorga, fra cui una guardia
  del percorso degli ordini (l'annullamento prima di aprire).
* Prova (eseguita). `mutazioni.py`: base 140 passed + 1 (git); prese 8 (N1 due volte, 196, 194, 195 in `ripara.py`, N3, N5, 197 a);
  vive 6: annullamento prima di aprire (`avvio.py:743`), passaggio dell'operazione aperta a `ricostruisci` (`:624`), N2 (la prova usa
  −1,998 contro −2,00: le due formule danno lo stesso testo), N4, 197 b, 197 c.
* Correzione suggerita (prima del commit, condizione 2). Aggiungere `test_annullo_prima_di_aprire` e
  `test_n2_lati_e_netto_con_arrotondamenti_diversi` (`test_secondo_riesame.py`; controllato: colgono le loro mutazioni), la corsa intera
  del 195 (`riesame_v7/test_riesame_ripara_aperta.py` con l'asserzione girata: un'operazione), N4
  (`riesame_v7/verifica_altri/test_n2_n4_dati_veri.py::test_n4_con_guasto` girata: 12 lezioni, senza doppioni), 197 b e 197 c
  (`riesame_v7/test_riesame_rifiniture.py` girate).

### Invarianti modificati (dal riesame)

* Una chiusura resta registrata e detta al modello anche se l'annullamento degli altri ordini fallisce; l'annullamento si riprova
  all'inizio del passo dopo (`avvio.py:574-579`, `:200-205`). Vale dove l'annullamento lancia l'errore (simulato), non sul demo (199).
* Prima di aprire, gli ordini del trader rimasti senza operazione si annullano; se l'annullamento lancia un errore l'operazione non si
  apre (`:742-745`).
* Sul demo «eseguito» senza posizione si conferma al passo dopo prima di registrare e annullare (`:472-477`); non in `_annulla_limite`
  (198).
* Un limite annullato che si era già eseguito e chiuso si registra (`:865-877`).
* La ricostruzione salta la posizione dell'operazione aperta (`ripara.py:106-109`; 201).
* L'uscita stimata si corregge dal conto, ultime 5 operazioni, al massimo 20 tentativi (`avvio.py:582-602`).
* Nessun valore dei limiti cambiato; `bot/risk/hard_limits.py` invariato.

### Decisioni per Alessio

* Il riavvio con questa versione sul conto simulato: è suo, con le condizioni 1-3.
* Il conto demo: non con questo codice; prima 198 e 199, la misura del ritardo delle posizioni sul demo e una revisione nuova.

### Domande aperte

* Sul demo la lettura delle posizioni può arrivare in ritardo rispetto allo stato di un ordine eseguito? (Già del 196; adesso vale
  anche per il 198.) Da misurare sul demo prima di usarlo.
* La memoria del revisore (`reviews/`) da quest'area non si scrive: le righe nuove del secondo riesame (con quelle del riesame, non
  ancora applicate) sono in `<cartella del secondo riesame>/righe_per_reviews.patch` (solo i quattro file di `reviews/`, si applica con
  `git apply`), per la sessione che può applicarle.
