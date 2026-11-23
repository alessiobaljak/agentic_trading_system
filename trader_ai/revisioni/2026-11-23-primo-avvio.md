# Trader AI: revisione prima del primo avvio (23 novembre 2026)

Nota: scritto nella cartella di lavoro perché il blocco delle aree (`.claude/hooks/aree.py`) impedisce a questa sessione («trader_ai»)
di scrivere in `reviews/` (area «crypto»). Va copiato in `reviews/reports/2026-11-23-trader-ai-primo-avvio.md`.

## Riepilogo e verdetto

**REQUEST CHANGES.** 1 Bloccante, 3 Alti, 7 Medi, 9 Bassi.

Il collegamento al conto è scritto con cura (un solo indirizzo ammesso, firma corretta, errori senza firma, margine separato,
arrotondamenti dai filtri del simbolo, stop sul prezzo mark come i prezzi che vede il modello). Ma quattro cose impediscono il primo
avvio:
* **95 Bloccante**: il codice non può sapere se la chiave è davvero di un conto diverso da quello di G1. Confronta solo il testo delle
  chiavi; una seconda chiave creata sullo stesso conto demo di G1 passa tutti i controlli, e allora il trader adotta la posizione BTC
  di G1, le cambia la leva, annulla gli ordini BTC di G1 e la chiude quando «il conto» (che è quello di G1) sale di 50 USDT. Provato.
* **96 Alto**: se lo stop viene rifiutato da Binance dopo l'apertura (il prezzo ha già superato lo stop mentre il modello pensava), la
  posizione resta **senza stop** e il programma si blocca: ogni 30 secondi riprova lo stesso stop, va in errore e non arriva mai né
  all'obiettivo del giorno né al modello. Provato: 39 passi su 39 in errore, nessuno stop sul conto.
* **97 Alto**: il tetto di spesa **non conta** le risposte fuori schema, tagliate o in errore di rete: vengono registrate a costo zero,
  ma sono pagate. Il diario oltre i 600 caratteri e la risposta tagliata finiscono proprio lì (provato con l'SDK installato:
  0,116 dollari a chiamata persi dal conto della spesa).
* **98 Alto**: il salvataggio di ogni ora fa `git pull` nella stessa cartella da cui gira il programma: ogni modifica spinta sul branch
  entra nel codice che il servizio caricherà al primo riavvio automatico (crash, riavvio della macchina), senza revisione né ok del
  proprietario.

Test: `python -m pytest trader_ai/tests -q` → **34 passed in 1.02s** (eseguito il 23 nov su `a6ff73a`). Il conto finto dei test
accetta ogni ordine: nessun test copre un rifiuto di Binance, il nome vero dei campi della risposta degli ordini condizionati o la
spesa di una risposta fuori schema.

## Oggetto

* Branch `claude/brave-albattani-1b12fv`, commit `a6ff73a` (padre `9681398`). Il commit tocca `trader_ai/avvio.py`,
  `trader_ai/conto_demo.py`, `trader_ai/tests/test_avvio.py`, `trader_ai/vps/installa.sh`, `trader_ai/vps/salva.sh`. Rivisti anche,
  come chiesto, `giro.py`, `limiti.py`, `costi.py`, `modello.py`, `sveglia.py` (e `schema.py`, perché decide la validazione) e le regole
  `trader_ai/REGOLE.md` versione 3.
* Nessun file del bot, di `bot/risk/`, di Firebase o di `ops/` toccato: i limiti fissi del bot e gli invarianti delle sezioni 1-14 della
  mappa sono invariati.
* Invarianti nuovi (sezione 15 proposta per la mappa): solo `demo-fapi.binance.com`; chiavi `TRADER_AI_DEMO_*`; leva 1-10; margine
  separato; stop obbligatorio sul conto; obiettivo di 50 USDT dalla mezzanotte UTC poi fermo; tetto di 5 dollari al giorno prima di ogni
  chiamata.

## Checklist A–F

La checklist è scritta per il bot; qui la applico al trader AI, che per scelta del proprietario non ha perdita massima.

### A. Limiti fissi e interruttori
* Limiti fissi del bot (`bot/risk/hard_limits.py`): **NON APPLICABILE** (non toccati, `git show --stat a6ff73a`; il trader non li
  importa: test `test_niente_dati_ne_codice_dell_altra_sessione`).
* Limiti del trader come costanti nel codice: **OK**. `trader_ai/limiti.py:13-19` (`OBIETTIVO_GIORNO_USDT = 50`, `LEVA_MAX = 10`,
  `ORDINE_MIN_VALORE = 100`, `MARGINE_LIQUIDAZIONE = 0.9`), `trader_ai/costi.py:19` (`TETTO_GIORNO_DOLLARI = 5.00`), `:22`
  (`MAX_TOKENS`). Nessuno in configurazione, ambiente o Firebase (`config.json` ha solo moneta e intervalli). Stanno fuori da
  `hard_limits.py`, come deve essere per un'area separata. Nessun test li fissa a quei valori: Basso 112.
* Parametri dalla dashboard: **NON APPLICABILE** (il trader non legge Firebase).
* Pulsante che chiude tutto: **PROBLEMA** (Medio 104). C'è solo `installa.sh ferma` (`trader_ai/vps/installa.sh:61-62`), che ferma il
  programma e lascia aperte le posizioni; nessun comando che chiude e annulla tutto sul conto del trader.

### B. Ordini
* Arrotondamenti dai filtri del simbolo: **OK** con un Basso. `conto_demo.py:116-126` legge `PRICE_FILTER`, `MARKET_LOT_SIZE` (o
  `LOT_SIZE`), `minQty`, `MIN_NOTIONAL.notional` da `exchangeInfo`; `avvio.py:203-205` arrotonda per difetto e controlla i minimi;
  prezzi al passo (`avvio.py:191,193,208,214,216,237`). Per l'ordine limite usa il passo del mercato (Basso 109).
* Identificativo dell'ordine: **PROBLEMA** (Medio 102). Nessun `newClientOrderId` (`conto_demo.py:159-164`) né `clientAlgoId`
  (`:166-170`). Non c'è un tentativo automatico che duplichi, ma un ordine limite con la risposta persa resta sul libro senza che il
  programma lo sappia.
* Chiusure con «solo riduzione»: **OK** in modalità a una posizione (`conto_demo.py:186-188`; stop e obiettivo con `closePosition`,
  `:168-170`). Modalità di posizione mai letta né impostata: Medio 101.
* Prezzo che attiva gli stop: **OK**. `workingType=MARK_PRICE` (`conto_demo.py:169`), e il «prezzo» del modello e dei controlli è il
  prezzo mark (`conto_demo.py:113`, `avvio.py:74`). Non c'è una prova storica da confrontare (decide il modello).
* Leva e margine espliciti: **OK**. `prepara` (`conto_demo.py:151-157`) prima di ogni apertura (`avvio.py:206`), `ISOLATED` con `-4046`
  tollerato, leva intera.
* Stop su Binance per ogni posizione: **PROBLEMA**. L'intenzione c'è (`avvio.py:213-216`, `_protezione` `:173-194` ogni 30 s), ma uno
  stop rifiutato lascia la posizione senza stop per sempre (Alto 96); la modifica dello stop può essere rifiutata (Medio 99); i campi
  della risposta degli ordini condizionati non sono verificati (Medio 100).

### C. Stato e resilienza
* Stato da Binance all'avvio: **OK in parte**. A ogni passo posizione e ordini condizionati si rileggono da Binance (`avvio.py:71-73`,
  `:182`); il piano (stop, obiettivo) viene da `stato.json`. Una posizione trovata senza piano viene adottata (`:176-181`): giusto sul
  conto suo, pericoloso su un conto altrui (Bloccante 95). L'ordine limite in attesa non si rilegge mai (Medio 102).
* Flussi in tempo reale: **NON APPLICABILE** (solo richieste ogni 30 s, `avvio.py:34`).
* Candele chiuse: **OK**. `conto_demo.py:95-108` toglie la candela con chiusura dopo l'ora della chiamata; test
  `test_nessuna_candela_dopo_l_ora_della_chiamata`.
* Errori delle interfacce: **PROBLEMA in parte**. `-1021` con l'ora di Binance (`conto_demo.py:89-90`); nessuna attesa dopo 429/418
  (Basso 110); nessun tentativo infinito nello stesso passo, ma uno stop rifiutato si ritenta ogni 30 s per sempre e blocca tutto (Alto
  96). Margine insufficiente: rifiuto preso e mostrato al modello (`avvio.py:129-134`).
* Firebase: **NON APPLICABILE**. Orologio della macchina: **NON APPLICABILE** (nessuna configurazione nel repo; `-1021` gestito).

### D. Separazione fra conti
* Solo il conto demo: **OK** per l'indirizzo. `HOST` fisso (`conto_demo.py:25-26`), `_url` rifiuta ogni altro nome (`:31-35`), tutti i
  percorsi sono testi fissi; test `test_solo_il_conto_demo`. Le richieste seguono i reindirizzamenti (Basso 106).
* Chiavi distinte: **PROBLEMA, Bloccante 95**. Il controllo confronta solo il testo delle chiavi (`installa.sh:33-42`,
  `conto_demo.py:42-52`); quello del programma non vede mai le chiavi del bot sotto systemd (Basso 107).
* `DRY_RUN`: **NON APPLICABILE** per scelta (il trader non lo legge; lo protegge l'indirizzo fisso).
* Log dell'ambiente attivo: **OK in parte**: `avvio.py:279` scrive la moneta, non l'indirizzo né il saldo; `controlla` (`:269-273`) li
  mostra all'installazione.

### E. Segreti
* Chiavi in codice, log, diario: **OK**. Nessuna chiave nei file; l'intestazione con la chiave non si stampa; la firma si toglie dagli
  errori (`conto_demo.py:38-39`, `:87`, `:91`); il diario contiene risposte del modello, stato e testi d'errore di Binance o dell'SDK,
  senza chiavi; `salva.sh:9` aggiunge solo `trader_ai/avanti`. `/etc/trader-ai.env` scritto con `umask 077` e `chmod 600`
  (`installa.sh:46-53`), chiavi lette senza eco (`:30-31`), mai stampate; il `.env` del bot solo letto (`:23-26`, `:34`, `:39`, `:43-44`).
  L'indirizzo del remoto non si stampa (`:78-79`).
* Permessi della chiave del demo (niente prelievi, indirizzo della macchina): **da confermare con Alessio**.
* Regole di Firebase: **NON APPLICABILE**.

### F. Test
* `python -m pytest trader_ai/tests -q` → **34 passed in 1.02s**. Mie prove in
  `/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/trader_ai/test_prove.py`
  (2 passed: confermano i guasti 95 e 96) e prova della spesa persa con `anthropic==2.12.0` (97).
* Copertura: **PROBLEMA** (Medio 105).

## Problemi

### 95 Bloccante — nessuna prova che il conto sia quello del trader e non quello di G1 (richiesta a)
* Dove: `trader_ai/vps/installa.sh:33-42` e `trader_ai/conto_demo.py:42-52` confrontano soltanto il testo delle chiavi;
  `trader_ai/avvio.py:176-181` adotta qualunque posizione BTCUSDT trovata sul conto; `:99-100` chiude tutto quando il conto supera la
  mezzanotte di 50; `conto_demo.py:151-157` cambia margine e leva del simbolo; `:175-180` annulla tutti gli ordini del simbolo.
* Scenario: il proprietario crea la chiave del trader dallo stesso accesso a Binance con cui c'è il demo di G1 (il demo di Binance è
  legato all'utente: una chiave nuova può essere una seconda chiave dello **stesso** conto demo). Le chiavi sono diverse, quindi passano
  tutti i controlli. Al primo passo il trader trova la posizione BTC di G1 (BTCUSDT è fra le monete di G1 e degli eventi,
  `bot/portafoglio/demo_binance.py:337-340`), la adotta «senza piano» e le mette uno stop con chiusura totale a 0,9/leva dall'entrata;
  al primo «apri», se G1 non ha BTC in quel momento, porta la leva BTC del conto di G1 a 10 e il margine a separato; dopo ogni chiusura
  annulla gli ordini limite BTC di G1 (`avvio.py:169`); quando il conto di G1 (circa 1.000 USDT) sale di 50 dalla mezzanotte chiude la
  posizione BTC di G1 a mercato. Provato con il conto finto (`test_posizione_altrui_adottata`: stop messo, posizione chiusa).
* Correzione suggerita: (1) all'avvio e a ogni passo leggere le posizioni di tutto il conto (`GET /fapi/v2/account`, già letto) e
  rifiutare di partire, o fermarsi con un messaggio chiaro, se c'è una posizione o un ordine aperto su un simbolo diverso dalla moneta del
  trader (G1 ne tiene sempre molti); (2) al primo avvio (nessun `stato.json`) rifiutare di partire se c'è già una posizione o un ordine
  su BTCUSDT, invece di adottarli; (3) scrivere nel registro all'avvio indirizzo, saldo e numero di posizioni, e far confermare al
  proprietario che il conto è separato (domanda 1). Test con un conto finto che ha posizioni su altri simboli.

### 96 Alto — stop rifiutato dopo l'apertura: posizione senza stop e programma bloccato (richieste b, e)
* Dove: `trader_ai/avvio.py:203-216` (stop controllato sul prezzo letto **prima** della chiamata al modello, `:74`, `:119`; lo stop si
  mette dopo l'ordine a mercato); `:132-134` prende l'errore; `:89-90` e `:185-191` riprovano lo stesso stop a ogni passo, e l'eccezione
  esce da `passo` prima dell'obiettivo (`:98`) e della chiamata al modello (`:108`).
* Scenario: alle 10:15 il prezzo mark è 90.000; il modello impiega 60-120 secondi e chiede un lungo con leva 10 e stop a 89.900. Quando
  arriva l'ordine il prezzo è 89.850: l'ordine a mercato si esegue, lo stop viene rifiutato perché scatterebbe subito (-2021). Ogni 30
  secondi `_protezione` riprova lo stesso stop e riceve lo stesso rifiuto: nessuno stop sul conto, nessuna chiamata al modello, nessun
  controllo dell'obiettivo, finché la posizione non si chiude da sola o va in liquidazione (con margine separato si perde fino a tutto il
  margine, che può essere l'intero conto). Lo stesso con un ordine limite eseguito oltre lo stop, con lo stop di ripiego di una posizione
  adottata già superato, o se il servizio degli ordini condizionati non risponde. Provato (`test_stop_rifiutato_dopo_apertura`: 39 passi
  su 39 in errore, 1 chiamata, nessuno stop).
* Correzione suggerita: (1) subito prima dell'ordine rileggere il prezzo mark e rifare `controlla` su quel prezzo; (2) se dopo
  un'apertura lo stop non si mette, chiudere subito la posizione a mercato con «solo riduzione» (ciò che lo stop avrebbe fatto) e scriverlo
  nel diario; (3) in `_protezione`: se il prezzo mark ha già superato lo stop, chiudere a mercato invece di mettere lo stop; ogni altro
  errore si scrive nel diario e il passo continua (obiettivo e modello non devono dipendere da `_protezione`); dopo pochi errori di fila,
  chiusura a mercato; (4) test con un conto finto che rifiuta lo stop con -2021 e con un errore di rete.

### 97 Alto — il tetto di spesa non conta le chiamate fuori schema, tagliate o in errore (richiesta c)
* Dove: `trader_ai/modello.py:46-49` restituisce `Esito` **senza** `usage` per `pydantic.ValidationError` e `anthropic.APIError`;
  `trader_ai/giro.py:37-39` registra quindi 0 dollari. Il ramo della risposta tagliata (`modello.py:54`) non si raggiunge mai: l'SDK
  valida il testo dentro `messages.parse` (`anthropic/lib/_parse/_response.py`, `parse_text` → `validate_json`) e un testo tagliato
  solleva `ValidationError` prima. L'SDK sposta `max_length` nella descrizione (`anthropic/lib/_parse/_transform.py:223-228`): il servizio
  non lo impone, lo controlla solo pydantic da noi (`trader_ai/schema.py:20,23`).
* Scenario: il modello scrive un diario di 700 caratteri oppure arriva ai 12.000 token: la chiamata è pagata (circa 0,12 dollari con
  9.000 token in entrata e 4.000 in uscita, fino a circa 0,30 con la risposta più lunga), il conto della spesa registra 0. Se succede
  spesso, con 96 candele al giorno più le chiusure la spesa vera supera i 5 dollari senza che il tetto scatti. Lo stesso per un errore di
  rete o il tempo scaduto dopo 300 secondi (`modello.py:30`), che il servizio può aver fatto pagare, e per i ritentativi automatici
  dell'SDK (2 per difetto, non contati). Provato con `anthropic==2.12.0`: diario di 700 caratteri e risposta tagliata → `ValidationError`,
  0,116 dollari non registrati.
* Correzione suggerita: prenotare la spesa **prima** della chiamata (registrare `costo_massimo` in `giro.py` prima di `chiama_modello`)
  e correggerla con il costo vero solo se la risposta dichiara `usage`; oppure `messages.create` e validazione a parte, tenendo sempre
  `usage`; `max_retries=0` nel client (`modello.py:30`) o ogni tentativo prenotato. Test: fuori schema, tagliata e in errore consumano il
  massimo dal budget.

### 98 Alto — il codice che gira si aggiorna da solo ogni ora (richiesta f)
* Dove: `trader_ai/vps/salva.sh:5,13` fa `git pull --rebase --autostash` in `/opt/trader-ai`, la stessa cartella da cui il servizio
  carica il codice (`installa.sh:99,102`); il servizio riparte da solo (`installa.sh:103-104`, `Restart=always`).
* Scenario: la sessione «trading AI» spinge una modifica a `conto_demo.py`, `avvio.py` o `config.json` (per esempio la moneta) non
  ancora rivista; al salvataggio delle :07 entra in `/opt/trader-ai`; al primo riavvio (errore all'avvio, la macchina che riparte, un
  aggiornamento di sistema) gira il codice nuovo, senza revisione e senza ok del proprietario. Una modifica spinta a metà rompe il servizio,
  che riparte ogni 30 secondi.
* Correzione suggerita: tenere i dati fuori dal codice che gira: una seconda copia solo per i dati (per esempio `/opt/trader-ai-dati`,
  dove `salva.sh` copia `avanti/` e fa commit e push), mai un `pull` nella cartella del codice. Il codice di `/opt/trader-ai` si aggiorna
  solo con `installa.sh` dopo revisione e ok; all'avvio il programma scrive nel registro il commit da cui gira.

### 99 Medio — la modifica dello stop può essere rifiutata (richiesta g)
* Dove: `trader_ai/avvio.py:229-241` mette il nuovo stop con chiusura totale **prima** di togliere il vecchio.
* Scenario: Binance rifiuta un secondo stop con `closePosition` sullo stesso lato mentre il primo è aperto (errore -4130 sul percorso
  classico degli ordini; da verificare sul servizio degli ordini condizionati del demo). Ogni «modifica» fallisce: il vecchio stop resta
  (nessun pericolo), ma il modello non riesce mai a spostare stop o obiettivo. Il test
  `test_modifica_mette_il_nuovo_stop_prima_di_togliere_il_vecchio` passa perché il conto finto accetta tutto.
* Correzione suggerita: provarlo sul demo prima dell'avvio; se rifiuta, mettere il nuovo stop con quantità e «solo riduzione» (non
  `closePosition`) e poi togliere il vecchio; oppure togliere e rimettere subito, chiudendo a mercato se il nuovo è rifiutato.

### 100 Medio — percorsi e campi del servizio degli ordini condizionati mai provati sul demo (richiesta g)
* Dove: `conto_demo.py:146-148` (`GET /fapi/v1/openAlgoOrders`, lista o `orders`), `avvio.py:182` e `:239` (campo `orderType` o `type`,
  `algoId`), `conto_demo.py:166-180` (`POST` e `DELETE /fapi/v1/algoOrder`, `DELETE /fapi/v1/algoOpenOrders`). I nomi corrispondono a
  quello che conosco della documentazione, ma non li ho potuti provare e `controlla` (`avvio.py:269-273`) non li tocca.
* Scenario: se il campo del tipo ha un altro nome o il demo non offre il servizio, `tipi` è `{None}` e `_protezione` aggiunge uno stop
  ogni 30 secondi (o, con il rifiuto del secondo stop, si blocca come nel 96).
* Correzione suggerita: estendere `controlla` con `GET /fapi/v1/openAlgoOrders` e `GET /fapi/v1/positionSide/dual` (sola lettura) e
  stampare la forma della risposta; prima del primo avvio una prova manuale sul demo con la quantità minima (apertura, stop e obiettivo,
  lettura, modifica, annullamento, chiusura), con l'ok del proprietario; nel codice, se un ordine condizionato aperto non ha un tipo
  riconosciuto, fermarsi con un messaggio invece di aggiungerne altri.

### 101 Medio — modalità di posizione mai controllata
* Dove: `conto_demo.py:151-188` non leggono la modalità e non mandano `positionSide`.
* Scenario: il conto nuovo è nella modalità a due posizioni: aperture e stop rifiutati (-4061); con un'apertura riuscita e lo stop
  rifiutato si torna al 96.
* Correzione suggerita: all'avvio leggere `GET /fapi/v1/positionSide/dual` e rifiutare di partire se è `true`.

### 102 Medio — ordine limite non seguito: ordini sconosciuti, posizione doppia, «in attesa» fantasma (richiesta e)
* Dove: `avvio.py:207-212` (nessun identificativo, `st["aperta"]` scritto solo se `apri` risponde), `:85-88` (l'attesa non si rilegge
  mai da `openOrders`), `:220-223`.
* Scenari: (i) l'ordine limite parte ma la risposta si perde: il programma non lo sa, il modello alla candela dopo apre un altro ordine;
  quando il limite vecchio si esegue la posizione è più grande di quella voluta (lo stop con chiusura totale la copre, ma il rischio è
  doppio). (ii) il limite si esegue e lo stop scatta fra due passi (meno di 30 s): la posizione non si vede mai, l'attesa resta «in attesa»
  per sempre e il modello non può più aprire finché non dice «chiudi». (iii) un'esecuzione parziale lascia il resto del limite sul libro
  dopo che lo stop ha chiuso la parte eseguita, fino al passo dopo.
* Correzione suggerita: `newClientOrderId` per ogni decisione, salvato nello stato prima dell'invio e cercato dopo un errore; prima di
  ogni apertura annullare (o rifiutare se ci sono) gli ordini aperti; a ogni passo, con un limite «in attesa», rileggere `openOrders`.

### 103 Medio — il salvataggio fa `git` sui file che il programma sta scrivendo
* Dove: `salva.sh:9-13` (`add`, `commit`, `pull --rebase --autostash`) su `trader_ai/avanti/stato.json`, `diario.jsonl`, `spesa.json`,
  scritti ogni 30 secondi (`avvio.py:56-65`, `costi.py:72-78`).
* Scenario: durante il `pull --rebase --autostash` git rimette i file alla versione del commit e poi riapplica le modifiche; se il
  programma scrive in mezzo, la riapplicazione fallisce o il programma legge la versione vecchia: si perdono righe del diario, `ultima`
  (una chiamata in più), `fermo_fino`, `aperta`, o la spesa di oggi (`spesa.json` riportato indietro = tetto contato meno).
* Correzione suggerita: la stessa del 98; in più `spesa.json` scritto con file temporaneo e sostituzione, come `stato.json`.

### 104 Medio — nessun comando che chiude tutto sul conto del trader
* Dove: `installa.sh:61-62` (`ferma` lascia le posizioni); nessun file o pulsante letto da `avvio.py`.
* Scenario: il modello apre e chiude in continuazione con leva 10: l'unico modo di chiudere è fermare il servizio e chiudere a mano dal
  sito del demo.
* Correzione suggerita: `installa.sh chiudi` (o un file letto a ogni passo) che annulla gli ordini, chiude con «solo riduzione» e ferma
  il trader fino a un comando di ripartenza. Decisione 3.

### 105 Medio — test che non possono fallire sui guasti veri
* Dove: `trader_ai/tests/test_avvio.py:16-65` (il conto finto accetta tutto, con campi inventati); nessun test di spesa con
  `ValidationError`.
* Correzione suggerita: test per 95, 96, 97, 99, 101, 102 e un test che fissa `LEVA_MAX`, `OBIETTIVO_GIORNO_USDT`, `TETTO_GIORNO_DOLLARI`.

### Bassi
* **106** `conto_demo.py:85`: `requests` segue i reindirizzamenti e rimanda l'intestazione con la chiave al nuovo indirizzo (toglie solo
  `Authorization`). Correzione: `allow_redirects=False`, ogni 3xx è un errore.
* **107** `conto_demo.py:28,48-51`: sotto systemd l'ambiente contiene solo `/etc/trader-ai.env`, quindi il confronto con le chiavi del bot
  non trova mai nulla; il controllo vero è solo all'installazione (`installa.sh:33-42`), che salta in silenzio se nel `.env` del bot la
  riga è scritta con `export` o spazi (`:23-26`).
* **108** `avvio.py:218-228` e `conto_demo.py:182-188`: «chiudi» annulla stop e obiettivo **prima** della chiusura; se la chiusura è
  rifiutata la posizione resta senza stop fino al passo dopo (30 s). Correzione: chiudere con «solo riduzione» prima, annullare dopo.
* **109** `conto_demo.py:122-123`, `avvio.py:203`: l'ordine limite usa il passo di `MARKET_LOT_SIZE`; per un limite vale `LOT_SIZE`.
* **110** `conto_demo.py:88-91`: nessuna attesa dopo 429 o 418; lo stesso indirizzo della macchina usa il demo anche per G1: un blocco
  418 allungato dai tentativi fermerebbe anche G1. Correzione: rispettare `Retry-After` e non chiedere nulla fino ad allora.
* **111** `limiti.py:16,78-79` contro `REGOLE.md` sezione 6: le regole dicono che con il conto sotto l'ordine minimo il trader «si ferma
  da solo e lo scrive»; il codice scarta e continua a chiamare il modello ogni 15 minuti, spendendo.
* **112** nessun test fissa i valori delle costanti dei limiti (vedi 105).
* **113** `avvio.py:178-180`: una posizione adottata prende come «conto prima» il conto di mezzanotte (risultato sbagliato);
  `avvio.py:158-163`: «stop» o «obiettivo» indovinati dal prezzo con lo 0,3%.
* **114** `costi.py:72-78`: `spesa.json` senza file temporaneo; un file rotto blocca ogni chiamata (sicuro per il tetto) ma senza
  allarme; `modello.py:4` dice «fra 30 minuti», sono 15.

## Invarianti modificati

Nessun invariante del bot (sezioni 1-14 della mappa). Invarianti **nuovi** dell'area del trader AI (sezione 15 proposta): indirizzo unico
`demo-fapi.binance.com` (`conto_demo.py:25-35`), chiavi `TRADER_AI_DEMO_*` (`:42-52`), leva 1-10 (`limiti.py:14`, `:72-73`), margine
separato (`conto_demo.py:153`), stop obbligatorio sul conto (`avvio.py:213-216`, `:173-194`), obiettivo di 50 USDT e fermo fino a
mezzanotte UTC (`limiti.py:13`, `avvio.py:99-106`), tetto di 5 dollari al giorno controllato prima di ogni chiamata (`costi.py:19`,
`giro.py:34`), nessuna perdita massima (scelta del proprietario).

## Decisioni per Alessio

1. **Conto separato davvero** (95): il conto demo del trader va creato da un accesso a Binance diverso da quello del demo di G1. Serve la
   sua conferma, oltre al controllo nel codice.
2. **Prova manuale sul demo prima del primo avvio** (99, 100): una posizione minima su BTC con stop e obiettivo, una modifica, un
   annullamento e una chiusura, sul conto del trader; ordini sul demo suo, quindi con il suo ok.
3. **Comando che chiude tutto** per il trader (104): lo vuole? Oggi c'è solo «ferma», che lascia la posizione aperta con il suo stop.
4. **Margine di una singola operazione fino a tutto il conto** (nessuna perdita massima, sua scelta): il 96 va corretto comunque; resta
   sua la scelta di non avere un tetto.
5. Permessi della chiave del demo del trader: senza prelievi e limitata all'indirizzo della macchina, se il demo lo consente.

## Domande aperte

1. Il conto demo del trader AI è stato (o sarà) creato con un accesso a Binance diverso da quello del conto demo di G1? Se è lo stesso
   accesso, la chiave nuova opera sul conto di G1 e nessun controllo del codice attuale lo vede.
2. Il trader è già installato sulla macchina (il messaggio del commit dice «installato ma non avviato»)? Se sì, il timer del salvataggio
   è spento (si accende solo con `avvia`) e `/opt/trader-ai` è fermo al commit `a6ff73a`? Dopo le correzioni va reinstallato.
3. Il servizio degli ordini condizionati di `demo-fapi.binance.com` risponde con il campo `orderType` e accetta due stop con chiusura
   totale sullo stesso lato? Solo la prova manuale della decisione 2 lo dice.
4. Chi scrive in `reviews/` per il trader AI? Il blocco delle aree impedisce a questa sessione di salvare rapporto, registro e mappa:
   vanno copiati dalla sessione crypto, oppure `reviews/` (o una sua sottocartella del trader) va resa scrivibile dall'area «trader_ai».
