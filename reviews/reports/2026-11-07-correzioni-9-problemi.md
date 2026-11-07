# Revisione delle correzioni ai 9 problemi Alti del primo avvio

Data: 7 nov 2026. Revisore: `live-path-reviewer`. Oggetto: il commit `9f47972c` (diff `2928d066..9f47972c`), che vuole chiudere i
9 problemi Alti di `reviews/reports/2026-11-07-primo-avvio.md`.

### Riepilogo e verdetto

**REQUEST CHANGES.** Dei 9 problemi Alti, **8 sono chiusi** (2, 3, 4, 5, 9 corretti; 6, 7, 8 chiusi bloccando il vecchio ramo reale) e
**1 è chiuso solo in parte** (il problema 1). La correzione del problema 1 toglie il doppio invio dopo un errore (provato), ma apre
un'altra strada alla posizione doppia: se l'annullo di un ordine limite viene rifiutato (per esempio «troppe richieste»), il codice va
avanti, manda a mercato tutto il resto e lascia l'ordine limite sul libro; quando quello si esegue, la posizione raddoppia (provato:
BUSDT a −199,972 contro un obiettivo di −99,986). È un problema Alto nuovo (Problema 25), ed è una regressione: prima un annullo
rifiutato fermava il giro e nessun ordine a mercato partiva.

Poi un problema Medio nuovo (26): dopo un «riparti» o dopo la sistemazione del margine nello stesso giorno, i resti a mercato del
secondo ribilancio non partono (identificativo già usato), e una gamba del portafoglio resta vuota fino al giorno dopo (provato).
Cinque problemi Bassi (27-31).

Niente di bloccante per il demo con i soldi finti. **Il passaggio di stanotte a 1.000 USDT funziona con il codice nuovo** (provato con e
senza un timeout dentro `parti_da_zero`: nessuno stop falso, massimo a 1.000, valore mostrato 1.000, resti a mercato giusti).

Test: `2562 passed in 144.60s`, nessun fallimento (17 test nuovi, tutti superati).

Nota sul processo: il commit è già sul branch remoto che la macchina scarica ogni minuto (`git rev-parse HEAD
origin/claude/brave-albattani-1b12fv`: tutti e due `9f47972c` al momento del controllo). Il processo in corsa non lo carica finché non
riparte; ma un riavvio non deciso (un crash con il riavvio automatico, un riavvio della macchina) lo metterebbe in funzione senza l'ok
del proprietario.

### Oggetto (branch, commit, file toccati, invarianti coinvolti)

- **Branch** `claude/brave-albattani-1b12fv`, **commit** `9f47972c` (padre `2928d066`, che cambia solo `ops/heartbeat.md`). Il
  brief parlava di lavoro non committato; il messaggio della sessione principale ha poi confermato che il lavoro è identico in
  `9f47972c`. Tra `b29f5713` (codice della mappa) e `2928d066` nessun cambio in `bot/`, `firebase/`, `tests/` (`git diff --stat`: vuoto).
- Durante la revisione sono arrivati `435c5594` (solo `CLAUDE.md` e `docs/backlog.md`: risposte del proprietario del 7 novembre) e
  `fd887589` (una copia intermedia di questo rapporto, con numeri poi corretti: vale questo file). `git diff --stat 9f47972c HEAD -- bot/
  firebase/ tests/ scripts/`: vuoto, quindi il codice rivisto è quello di `9f47972c`.
- **File toccati** (righe aggiunte e tolte, `git diff --numstat`): `bot/portafoglio/demo_binance.py` (+200 −58, problemi 1-4),
  `bot/config.py` (+57 −6, problemi 5 e 9), `bot/main.py` (+2, problema 9), `bot/execution/executor.py` (+10 −12, problemi 6-8),
  `tests/test_demo_binance.py` (+152 −2: Binance finto con posizioni vive e guasti, 5 test nuovi), `tests/test_sicurezza_avvio.py`
  (nuovo, +57, 12 test). Letti per intero il diff e le funzioni toccate.
- **Non toccati** (verificato con `git diff --stat b29f5713 9f47972c -- bot/risk/ firebase/ bot/core/`: vuoto): limiti fissi,
  interruttori del vecchio bot, regole di Firebase, client di Firebase.
- **Invarianti coinvolti**: stop sul conto del demo (frequenza), pulsante che chiude tutto, fermo e «riparti», resti a mercato e
  identificativi, lettura di `DRY_RUN` e della rete di prova, file delle tarature, parità col backtest, vecchio ramo reale.
- **Prove a mano** (nessuna rete, il Binance finto dei test), in
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/correzioni/`:
  `prove_demo_nuove.py` (a, b, c, d, d2 rifatte; h, i nuove), `prova_stop_in_attesa.py` (b2), `prova_mezzanotte.py` (j1, j2),
  `prove_vecchio_nuove.py` (g, k, e/f, 9).

### Stato dei 9 problemi Alti

| N. | Problema | Stato | Evidenza |
|---|---|---|---|
| 1 | resto a mercato rimandato due volte dopo un errore | **chiuso in parte** | `demo_binance.py:777-836`: resto dalla posizione vera, identificativo fisso controllato prima (`:813-814`, `:642-651`), stato salvato dopo ogni ordine (`:794`, `:826`). Prova (a) rifatta: un solo ordine a mercato per moneta, posizioni giuste; test `tests/test_demo_binance.py:569`. **Ma** l'annullo rifiutato ora si ingoia (`:788-791`): Problema 25. |
| 2 | pulsante e stop sordi 30 minuti dopo un errore; stop solo ogni ora | **chiuso** | protezioni prima e fuori dall'attesa (`:488-502`), stop ogni minuto (`:544-550`, `:77`). Prova (b): fermo 30 s dopo l'errore; prova (b2): stop a −36% 90 s dopo l'errore, conto vuoto. Test `:587`, `:605`. |
| 3 | chiudi tutto senza garanzia di conto vuoto | **chiuso** | da fermo, ogni minuto, posizioni rilette e richiuse (`:566-579`); errori di annullo e di lettura degli ordini presi moneta per moneta (`:589-610`); allarme dopo 3 tentativi su `/demo_binance/allarme` e nel log (`:574-578`). Prova (c): chiusura rifiutata, conto vuoto un minuto dopo. Test `:616`. L'avviso resta solo su Firebase e nel log (Problema 11, aperto). |
| 4 | «riparti» rimasto vero riaccende il demo | **chiuso** | all'entrata nel fermo il «riparti» vecchio si pulisce (`:469`, `:612-625`); poi vale solo se il falso è scritto davvero (`:627-640`; `set_rtdb` restituisce falso se non arriva, `bot/core/firebase_client.py:652-679`, e aggiorna sempre lo specchio, quindi un vero vecchio non torna dalla memoria). Prova (d): nessuna ripartenza. Test `:662`. Nota: Problema 27. |
| 5 | `DRY_RUN` e rete di prova falsi con un errore di battitura | **chiuso** | `config.py:78-90`, `:105`, `:110`: solo «false» (maiuscole e spazi ignorati) spegne; vuoto, «si», «treu», «0», «no», «off» valgono vero con un avviso (prova g). Le tarature non possono più cambiare `DRY_RUN`, rete di prova, parità né chiavi che sembrano segreti (`:30-52`, `:61`). Test `tests/test_sicurezza_avvio.py:14-38`. Le tarature usano un elenco di chiavi vietate, non di chiavi ammesse: gli altri limiti del vecchio bot restano regolabili (Problema 20, aperto). Le tarature del supervisore sono tutte `GATE_*` (`bot/learning/supervisor.py:73-90`): nessuna scartata per sbaglio. |
| 6 | riconciliazione: doppione fisso, pulsante saltato, stop mancante non visto | **chiuso per blocco** | il vecchio esecutore non crea mai il client del conto vero e resta in prova anche con `DRY_RUN` falso (`executor.py:243-253`); prova (k), test `tests/test_sicurezza_avvio.py:49`. Senza client il riconciliatore vede Binance «irraggiungibile» e aspetta, senza azioni (`main.py:1204-1206`, `reconciler.py:93-100`). Il codice difettoso resta, raggiungibile solo dai test con un client finto. |
| 7 | ordini non arrotondati, senza identificativo, chiusure scoperte | **chiuso per blocco** | come sopra. |
| 8 | pulsante del vecchio bot dietro tre uscite anticipate | **chiuso per blocco** | come sopra: senza ordini veri, il pulsante del vecchio bot chiude solo posizioni di prova. |
| 9 | parità col backtest con soldi veri | **chiuso** | `config.py:787-794` chiamato in `main.py:2657-2658` prima di creare il bot: avvio rifiutato con `DRY_RUN` falso e parità accesa (prova 9, test `tests/test_sicurezza_avvio.py:40`). L'unico avvio è `python -m bot.main` (`main.py:13`, `:2662-2663`; nessun altro `TradingBot()` fuori dai test). |

**Il passaggio di stanotte** (`prova_mezzanotte.py`): conto demo vero a 5.000, conto ridotto a 280 dal 6 novembre, file del capitale a
1000, decisione nuova alla mezzanotte, un giro ogni 30 secondi per due ore e mezza.
- j1, senza guasti: `parti_da_zero` chiude le 2 posizioni, conto ridotto a 1000, massimo 1000, valore sulla dashboard 1000, nessun fermo;
  dopo un'ora i resti a mercato partono una volta sola dalla posizione vera. Le quantità intere (AUSDT 4 contro 4,9998) vengono dai filtri
  del conto vero (passo 1 per quelle due monete in `filtri_conto_vero.json`): comportamento atteso a capitale piccolo.
- j2, con un timeout sulla lettura del conto dentro `parti_da_zero`: errore, nuovo tentativo dopo 30 minuti, stesso risultato; nessun giro
  da fermo, nessuno stop falso nella mezz'ora con il conto ridotto vecchio.
- Lo stato vecchio è compatibile: gli ordini in corso salvati dal codice di prima (senza `controllato` e `mercato_fatto`) passano dalla
  fase 1 come nuovi, e gli `obiettivi` li scriveva già il ribilancio di prima (`:758-762`).

### Checklist A–F (sulla modifica)

**A. Limiti fissi e interruttori**
- Valori fissi di `bot/risk/hard_limits.py`: **OK**, invariati (`:17-21`; `git diff --stat b29f5713 9f47972c -- bot/risk/` vuoto).
- Nessun limite critico spostato in configurazione: **OK, in meglio**. Modo, rete di prova e parità non si cambiano più dal file delle
  tarature (`config.py:30-52`). Restano in variabili d'ambiente i limiti del vecchio bot (Problema 20, invariato).
- Parametri della dashboard: **NON APPLICABILE** (non toccati; Problema 17 aperto).
- Limiti propri di G1 sul demo come costanti: **OK, da segnalare**. Due costanti nuove fuori da `hard_limits.py`:
  `OGNI_CONTROLLO_STOP_S = 60` e `TENTATIVI_PRIMA_DELL_ALLARME = 3` (`demo_binance.py:77-78`). `LEVA = 5` (`:73`) e `STOP_CONTO = 0.35`
  (`:80`) invariati; la leva resta senza test di guardia.
- Pulsante senza Firebase: **OK** per il demo: il file `ops/demo_binance_chiudi_tutto` si legge a ogni giro, anche dopo un errore
  (`:490-498`, `:535-541`; prova b). Il ritardo del giro dietro il vecchio bot resta (Problema 14). Vecchio bot: **NON APPLICABILE** (ramo
  reale bloccato).

**B. Ordini**
- Passi e minimi dalle informazioni del simbolo: **OK**. I resti a mercato usano `exchangeInfo` e i filtri del conto vero (`:795-797`),
  quantità al passo verso zero, quantità e valore minimi (`:807-812`).
- Identificativo univoco e riusato nei tentativi: **PROBLEMA**. Fisso per ordine a mercato e controllato prima dell'invio (`:813-814`,
  `:642-651`): bene. Ma la chiave è solo la data del giorno (`:764`, `:801`): un secondo ribilancio nello stesso giorno riusa lo stesso
  identificativo e salta il resto (Problema 26). La protezione principale contro il doppio è il calcolo dalla posizione vera, che però non
  basta se l'ordine limite è ancora vivo (Problema 25).
- Solo riduzione e modo di posizione: **OK**. Chiusure con «solo riduzione» (`:604`); resti con «solo riduzione» quando riducono (`:815-819`,
  stessa regola di `ordini_del_giorno` `:167`); una posizione per moneta invariata (`:721-725`).
- Prezzo che attiva gli stop: **NON APPLICABILE** (nessuno stop per posizione; lo stop sul conto usa `totalMarginBalance`, `:657`).
- Leva e margine espliciti: **OK**, invariati (`:747-752`).
- Protezione per G1: **OK**. Stop sul conto ogni minuto (`:544-550`) e pulsante a ogni giro, provati (b, b2, c) e con test (`:587`, `:605`,
  `:616`). Nessuno stop per posizione su Binance: resta decisione per Alessio (primo avvio, decisione 1).
- Annullo prima del mercato: **PROBLEMA** (Problema 25, Alto).

**C. Stato e resilienza**
- Ricostruzione da Binance: **OK, in meglio**. Resti dalla posizione vera (`:799-811`); da fermo le posizioni si rileggono ogni minuto
  (`:569`). Il massimo dello stop resta solo nel file locale (Problema 15, aperto).
- Flussi in tempo reale: **NON APPLICABILE** (il demo fa solo richieste).
- Candele chiuse: **NON APPLICABILE** (non toccato).
- Errori delle interfacce: **PROBLEMA**. Un annullo rifiutato si stampa e si va avanti (`:788-791`, Problema 25). Le protezioni ora non
  aspettano dopo un errore (giusto), ma riprovano ogni 30-60 secondi senza attese crescenti e senza leggere l'attesa chiesta da Binance
  su 429 e 418 (Problema 28 Basso, dentro il Problema 13 aperto). Nessun tentativo infinito sul ribilancio (attesa di 30 minuti
  invariata, `:501-502`, `:526-529`).
- Una scrittura su Firebase che fallisce non blocca il rischio: **OK**. Le protezioni non dipendono dalle scritture; il «riparti» vale solo
  con la scrittura confermata (`:623`, `:635`). Con Firebase che non conferma, anche il «riparti» a file resta fermo (Problema 27, Basso,
  direzione sicura).
- Orologio: **NON APPLICABILE** (non toccato).

**D. Separazione fra paper, demo e conto vero**
- **OK, in meglio.** `DRY_RUN` e rete di prova: solo «false» li spegne (`config.py:78-90`; prova g). Avvio rifiutato con la parità e
  `DRY_RUN` falso, con il log dell'ambiente a ogni avvio (`config.py:787-794`, `main.py:2657-2658`). Il vecchio esecutore non crea mai il
  client del conto vero (`executor.py:243-253`; prova k). Il demo continua a rifiutare ogni indirizzo diverso dal demo (`demo_binance.py:98-102`,
  test invariato). Nota: con `DRY_RUN` falso lo stato del vecchio bot diventa incoerente (Problema 29, Basso).

**E. Segreti e sicurezza**
- Nessuna chiave nel codice, nei file versionati, nei log o negli errori: **OK.** Nessuna chiave nel diff (letto per intero). Le tarature
  rifiutano ogni chiave con KEY, SECRET, TOKEN, PASSWORD, CREDENTIAL o FIREBASE nel nome (`config.py:31`, `:46-48`). I messaggi d'errore
  nuovi tagliano la risposta a 150-200 caratteri come prima; l'indirizzo firmato nei messaggi resta (Problema 21, Basso, aperto).
- Chiavi senza prelievo e limitate all'indirizzo della macchina: **PROBLEMA fuori dal codice, già nel backlog**. Il proprietario ha
  risposto il 7 novembre che le chiavi del conto vero **non sono limitate all'indirizzo della macchina** (`docs/backlog.md`, aggiunta del
  commit `435c5594`: «da fare prima dei soldi veri: limite all'indirizzo della macchina e niente prelievi»); il permesso di prelievo non è
  detto. Con il vecchio ramo reale bloccato da questa modifica, nel bot non resta nessun percorso che usi quelle chiavi per mandare ordini
  (`scripts/verify_keys.py` le usa solo per leggere il conto).
- Regole di Firebase: **da controllare con Alessio**. Il proprietario dice di non averle mai toccate (stessa aggiunta al backlog): le regole
  del repo, con l'utente segnaposto, non sono pubblicate; quali regole valgono oggi si vede solo nella console. Per il demo conta: se il
  database accetta scritture da chiunque, chiunque può premere «chiudi tutto» o «riparti».

**F. Test**
- **OK con lacune.** 17 test nuovi: 5 in `tests/test_demo_binance.py` (`:569`, `:587`, `:605`, `:616`, `:662`), 12 in
  `tests/test_sicurezza_avvio.py` (`:14` con 8 casi, `:19`, `:24`, `:40`, `:49`). Comando: `python3 -m pytest tests/ -q -p no:cacheprovider`
  (l'opzione in più evita di scrivere la cartella della cache nel repo). Esito: `2562 passed in 144.60s`, nessun fallimento, nessun
  saltato; dentro anche i test dei limiti fissi (`tests/test_risk.py`, `tests/test_sizing.py`), superati. Mancano i test di: annullo
  rifiutato con l'ordine ancora aperto (prova h), secondo ribilancio nello stesso giorno (prova i), «riparti» a file con Firebase che non
  conferma (prova d2). Il Binance finto non toglie dagli ordini aperti un ordine annullato con `DELETE /fapi/v1/order`
  (`tests/test_demo_binance.py`, ramo `DELETE`): per questo nessun test poteva vedere il Problema 25.

### Problemi

**Problema 25 — Alto (nuovo, regressione) — `bot/portafoglio/demo_binance.py:788-794` con `:795-826`: un annullo rifiutato lascia
l'ordine limite sul libro e parte anche il mercato per tutto il resto.**
- Scenario (provato, prova h): ordine limite SELL BUSDT 99,986, ancora aperto dopo un'ora. L'annullo riceve 429 (o un 5xx con esito
  sconosciuto, o un errore d'orario): il codice stampa «annullo non riuscito», segna l'ordine come controllato (`:792-794`) e, leggendo la
  posizione vera (ancora 0), manda a mercato SELL 99,986. L'ordine limite resta sul libro (valido fino all'annullo). Quando il prezzo torna
  al limite: BUSDT a −199,972 contro l'obiettivo −99,986. Il confronto orario lo scrive solo su Firebase (`:692-713`); resta così fino al
  ribilancio del giorno dopo, che annulla gli ordini aperti. Sul conto vero: esposizione doppia su una moneta, oltre il 200% del
  capitale, fino al peso della moneta più pesante (il backlog ne cita una al 47,8%). Prima della modifica un annullo rifiutato faceva
  uscire il giro e nessun ordine a mercato partiva.
- Correzione suggerita alla sessione principale: dopo un annullo rifiutato rileggere l'ordine e andare avanti solo se il suo stato è
  finale (FILLED, CANCELED, EXPIRED, REJECTED); altrimenti sollevare senza segnarlo controllato, così il giro riprova al tentativo dopo.
  In più, prima della fase a mercato, controllare con `/fapi/v1/openOrders` che per quella moneta non resti nessun ordine aperto. Test:
  annullo rifiutato con 429 e l'ordine che resta aperto nel Binance finto (il finto va corretto: oggi un `DELETE` riuscito non toglie
  l'ordine dagli aperti).

**Problema 26 — Medio (nuovo) — `demo_binance.py:143-147`, `:764`, `:801`, `:813-814`, con `:561` e `:686`: il secondo ribilancio dello
stesso giorno salta i resti a mercato.**
- Scenario (provato, prova i): ribilancio del giorno, resto di BUSDT a mercato con l'identificativo `g1m-<data>-BUSDT`. Poi chiudi tutto e
  «riparti» (o la sistemazione del margine, `:686`): `ultimo_giorno` torna a 0 e il ribilancio si rifà con lo stesso giorno e la stessa
  chiave. Dopo un'ora il resto di BUSDT trova l'ordine di prima con lo stesso identificativo (`_ordine_esiste`) e non parte: BUSDT a 0
  contro l'obiettivo −99,986, AUSDT aperto. Il portafoglio resta da un lato solo (netto lungo) fino al ribilancio del giorno dopo; il
  confronto lo segnala solo su Firebase. Direzione: meno esposizione lorda, ma una gamba mancante su una strategia che deve essere
  bilanciata.
- Correzione: una chiave per ribilancio, non per giorno (per esempio la data più l'ora di `piazzati`, accorciata per stare nei 36
  caratteri); test con «riparti» nello stesso giorno.

**Problema 27 — Basso (nuovo) — `demo_binance.py:557-559`, `:612-625`: con Firebase che non conferma le scritture il «riparti» a file
non funziona, e un testo scritto durante il buco si perde.**
- Scenario (provato, prova d2): Firebase non conferma (`set_rtdb` falso, anche con il client in sola memoria): `riparti_pulito` resta
  falso, quindi anche il comando a file (che dovrebbe funzionare senza Firebase) non viene letto; ogni nuovo tentativo di pulizia segna
  come già visto il testo attuale del file, quindi un «riparti» scritto durante il buco va riscritto. Direzione sicura (il demo resta fermo).
- Correzione: pulire il testo del file una volta sola, all'entrata nel fermo; il «riparti» a file non deve dipendere da Firebase; un log
  quando un «riparti» viene ignorato.

**Problema 28 — Basso (nuovo, dentro il Problema 13) — `demo_binance.py:490-498`, `:566-579`: protezioni senza attese crescenti.** Dopo
un errore le protezioni riprovano a ogni giro (lettura del conto ogni 30-60 secondi) e da fermo le chiusure ogni minuto, senza limite e
senza leggere l'attesa chiesta da Binance su 429 e 418. È giusto non aspettare 30 minuti, ma sotto un blocco per frequenza si insiste.
Correzione con il Problema 13.

**Problema 29 — Basso (nuovo) — `bot/main.py:957`, `bot/execution/reconciler.py:232`, `bot/execution/executor.py:253`: con `DRY_RUN`
falso lo stato del vecchio bot è incoerente.** La dashboard riceve `dry_run` falso, il riconciliatore parte e vede Binance
«irraggiungibile» (aspetta e avvisa, `reconciler.py:93-100`), l'esecutore resta in prova. Nessun rischio per i soldi, ma un quadro che
inganna. Correzione: finché il codice del conto vero non c'è, rifiutare l'avvio con `DRY_RUN` falso in `controlla_avvio`, oppure
pubblicare il modo vero dell'esecutore.

**Problema 30 — Basso (nuovo) — documentazione ferma.** `demo_binance.py:33-34` dice ancora «controllo a ogni valutazione, ogni ora» per lo
stop sul conto; `executor.py:11-14` dice ancora «Per andare live: DRY_RUN=False».

**Problema 31 — Basso (nuovo) — `demo_binance.py:569-583`: da fermo, senza posizioni, gli ordini aperti non si riannullano.** Un ordine il
cui annullo è fallito in `chiudi_tutto` resta sul libro; se si esegue, la posizione si richiude al minuto dopo (esposizione per al più
un minuto, più le spese). Correzione: da fermo annullare anche gli ordini aperti quando le posizioni sono vuote.

Problemi aperti del primo avvio non toccati da questa modifica: 10-24 (Medi e Bassi), invariati, salvo il 22 in parte (log d'avvio
dell'ambiente aggiunto per il vecchio bot, non per il demo).

### Invarianti modificati

Nessun valore di `bot/risk/hard_limits.py`, `circuit_breakers.py`, `kill_switch.py` né delle regole di Firebase. Cambiano questi
invarianti del percorso (aggiornati in `reviews/LIVE_PATH_MAP.md`):
1. **Stop sul conto del demo**: da ogni ora (dentro `valuta`) a **ogni minuto** (`demo_binance.py:544-550`, `OGNI_CONTROLLO_STOP_S = 60`
   `:77`), anche durante l'attesa dopo un errore. Anche il massimo da cui si misura il −35% si aggiorna ogni minuto: lo stop scatta un po'
   prima di come si misurava ogni ora. Soglia invariata (`STOP_CONTO = 0.35`, `:80`).
2. **Pulsante che chiude tutto**: letto a ogni giro, anche dopo un errore (`:490-498`, `:535-541`).
3. **Fermo**: posizioni rilette e richiuse ogni minuto finché il conto è vuoto, allarme dopo 3 tentativi (`:566-579`, `:78`).
4. **«Riparti»**: vale solo dopo la pulizia all'entrata nel fermo e con il comando consumato davvero (`:557-565`, `:612-640`).
5. **Resti a mercato**: dalla posizione vera contro l'obiettivo, con identificativo fisso controllato prima, stato salvato dopo ogni
   ordine (`:777-836`).
6. **`DRY_RUN` e rete di prova**: solo «false» li spegne (`config.py:78-90`, `:105`, `:110`).
7. **File delle tarature**: non cambia modo, rete di prova, parità e chiavi che sembrano segreti (`config.py:30-52`, `:61`).
8. **Avvio**: rifiutato con la parità e `DRY_RUN` falso (`config.py:787-794`, `main.py:2657-2658`).
9. **Vecchio ramo reale**: bloccato, l'esecutore resta sempre in prova (`executor.py:243-253`).

### Decisioni per Alessio

1. **Il vecchio ramo reale è stato bloccato** invece che corretto (era la decisione 4 del primo avvio, presa qui dalla sessione
   principale). È la direzione sicura e si torna indietro facilmente; il conto vero nascerà dal codice di G1. Con le chiavi vere non limitate
   all'indirizzo della macchina, il blocco toglie l'unico percorso del bot che poteva usarle per ordini. Va bene così?
2. **Lo stop sul conto ora si guarda ogni minuto**, e ogni minuto si aggiorna anche il massimo. È più vicino a «−35% dal massimo», ma scatta
   un po' prima di prima. Va bene così? E con quale frequenza misurava la ricerca che ha scelto −35%? Se misurava sui giorni chiusi,
   conviene che lo sappia chi valuta le prove.
3. **Riavvio**: il mio verdetto resta REQUEST CHANGES finché il Problema 25 non è corretto e provato. La correzione è piccola. Per il demo
   di stanotte nessuno dei due codici muove soldi veri: il codice nuovo protegge meglio (pulsante e stop sempre attivi, chiusure ritentate),
   ma porta il Problema 25; il codice in corsa ha i problemi 1-4 del primo avvio. Il passaggio a 1.000 funziona con tutti e due. Decide lui
   se e quando riavviare.
4. **Fuori dal codice**: le chiavi del conto vero non sono limitate all'indirizzo della macchina (sua risposta del 7 novembre, già nel backlog
   come da fare prima dei soldi veri); hanno il permesso di prelievo? Se sì, conviene toglierlo subito, non solo prima dei soldi veri: le
   chiavi sono sulla macchina e non servono a nessun codice attivo. Regole di Firebase: controllare nella console quali valgono e
   pubblicare quelle del repo con il suo identificativo.

### Domande aperte

1. Il commit `9f47972c` è già sul branch remoto che la macchina scarica ogni minuto. Sulla macchina il bot si riavvia da solo (riavvio
   automatico dopo un crash, riavvio della macchina, un timer)? Se sì, queste correzioni, Problema 25 compreso, possono entrare in funzione
   senza l'ok del proprietario. Si vede solo dalla macchina: la richiesta in `ops/` la deve mettere la sessione principale (il mio
   perimetro non me lo permette).
2. Restano aperte le domande 1 e 2 del primo avvio: con quale nome sono nel `.env` della macchina le chiavi del conto vero; che valori hanno
   oggi sulla macchina `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY`. Ora conta anche così: con `BACKTEST_PARITY=true` e `DRY_RUN=false`
   il bot non partirebbe più; con `DRY_RUN` scritto in un modo diverso da «true» (per esempio «1») parte in prova ma stampa un avviso a ogni
   avvio.
3. Resta aperta la domanda 3 del primo avvio: la voce della modifica proposta del 7 novembre (leva 10, perdita giornaliera dalla
   dashboard), mai applicata, si chiude come «non applicata»?
4. Le chiavi del conto vero hanno il permesso di prelievo? La risposta del 7 novembre dice solo che non sono limitate all'indirizzo.
