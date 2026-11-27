# Diciottesima revisione del trader AI — versione 8, le correzioni della diciassettesima

Revisore: live-path-reviewer, 27 novembre 2026, mattina (07:27-08:05 UTC). Oggetto: le modifiche non committate su `11ad4c2` (branch
`claude/brave-albattani-1b12fv`), cioè le correzioni della sessione ai problemi della diciassettesima (213-216 del revisore, 230-232 e
234 del secondo cercatore). La differenza l'ho rifatta io dalla copia della diciassettesima (`scratchpad/mut_v8/copia_b/trader_ai`:
`avvio.py` 8ace7619, `conto_simulato.py` c7f7e815, `conto_demo.py` 453e0288) ai file di adesso: per `avvio.py` e `conto_demo.py` le
righe cambiate sono le stesse di `scratchpad/dalla_diciassettesima.diff`. `REGOLE.md` e `README.md` li ho confrontati con le copie
approvate alla diciassettesima (`rev17/revisore_lp/copia_mut_lp`: ec75e77f e 358f4fb5): cambiano solo le righe sulle correzioni.

Prove mie nella cartella `/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/rev18/revisore_lp/`
(sotto: «la cartella»), con un mio blocco e cartelle temporanee di pytest mie. Nessuna richiesta a Binance: il mercato è quello finto dei
test. I dati veri di `trader_ai/avanti/` solo letti: l'ultimo evento è «chiuso tutto a mano» del 26 alle 07:11 UTC, niente aperto.

### Riepilogo e verdetto

**APPROVE con condizioni.** Nessun Bloccante, nessun Alto, nessun Medio. Delle correzioni: 214, 230, 231 e 232 sono chiusi (il 232 sul
conto simulato; sul demo resta una prova da fare); 213, 215 e 216 sono chiusi in parte. Sei problemi nuovi, tutti Bassi (240-245); tre
c'erano già prima (242, 243, 244). Nessuna regressione per la sicurezza; una piccola per il comando «chiudi» (241).

1. **I salvataggi nuovi tengono.** `_chiudi_ora` (`avvio.py:751-760`) salva dopo la chiusura riuscita e richiama dopo la
   registrazione. L'ho provato da ogni punto che lo chiama: protezione, obiettivo già superato, `_esegui` (stop rifiutato, fermo a
   mano mentre l'ordine parte), `_sostituisci`, `_annulla_limite`. In ogni caso: una registrazione sola, il modo giusto, una chiamata
   sola, nessun richiamo che resta (Q1-Q4b, Q7b). Dentro `_esegui` il richiamo salvato da `_chiudi_ora` viene poi sostituito da quello
   di `_esegui`, oppure tolto (fermo a mano: Q2).
2. **Lo stop resta mentre si annulla il limite** (232). `annulla_ordini` toglie il solo limite, sul simulato
   (`conto_simulato.py:433-438`) e sul demo (`conto_demo.py:272-279`). Stop e obiettivo si tolgono solo se il limite non si è eseguito
   (`avvio.py:975`). L'ho provato dal ramo dell'obiettivo, dal «chiudi» e dalla «modifica» del modello, con l'esito che non si legge e
   con la chiusura che fallisce (P1, P2, P4, Q5-Q7b). Contare i minuti due volte sul simulato, prima in `annulla_ordini` e poi in
   `annulla_tutto`, non cambia niente (Q8). Le tre prove vecchie agganciate ad `annulla_ordini` falliscono tutte e tre se si torna ad
   `annulla_tutto`: non hanno perso forza.
3. **Restano piccoli buchi.**
   - Il motivo provvisorio del ramo dell'obiettivo non dice che il 3% non è confermato (240).
   - Il «chiudi» del proprietario ora legge dal conto dentro il blocco e può finire in errore dopo aver chiuso (241).
   - Un limite eseguito e chiuso, con l'esito che non si legge, si perde ancora (242).
   - Due cose c'erano già: 243 e 244.
   - Tre prove mancano ancora (245).
4. **Test.**
   - Trader: 215 passati.
   - Suite della radice come prima: 2825 passati, 1 fallito (lo stesso della ricerca), 1 saltato.
   - Mutazioni della sessione: 72 prese su 72 (la lista ha 72 mutazioni; con la riga di base fanno 73 righe).
   - Mutazioni mie: 13 prese su 21. Delle 8 vive, 4 le prendono le mie prove (Q15-Q17, R11b); 2 contano solo sul demo; 2 non cambiano
     niente.
   - Più le 6 vive della diciassettesima: 5 ora prese, la R3 viva (245).

**Problemi nuovi** (tutti Bassi)
- **240.** Nel ramo dell'obiettivo, se la rilettura del saldo dopo la chiusura fallisce e il conto è sotto il 3%, il modello si chiama
  con «operazione chiusa (obiettivo del giorno (chiusa dal programma))». Il motivo non dice che il 3% non è confermato, mentre il
  messaggio dice «mancano 1.00».
- **241.** I rami nuovi del «chiudi» del proprietario leggono saldo e prezzo dentro il blocco. Se una lettura fallisce, il comando finisce
  con un errore dopo aver chiuso: lo stato non si salva e il controllo finale si salta.
- **242, c'era già.** Il «chiudi» con un limite eseguito e chiuso prima, se l'esito non si legge, perde l'operazione dalla memoria. Sul
  demo l'esito non dice mai «chiusa», quindi quel ramo non registra mai.
- **243, c'era già.** Il modello chiude, la chiusura riesce e la lettura del saldo fallisce: il modello legge «operazione chiusa (chiusa
  da te)» e anche «rifiutata dal conto».
- **244, c'era già.** La protezione chiude e la lettura del saldo dentro `_chiudi_ora` fallisce. Se nello stesso passo chiude una
  candela, il modello si chiama con la posizione già chiusa mostrata come aperta.
- **245.** Mutazioni vive per i test del repository: R3, X8, X15, X16, X22.

**Condizioni**
1. Il riavvio lo approva Alessio, con «riparti» (il trader è fermo a mano). Con lo stesso ok conferma le due scelte della diciassettesima
   (vedi «Decisioni per Alessio»).
2. Al commit il codice deve avere le impronte qui sotto.
   - Se cambiano solo i test, basta che le impronte del codice restino queste. Consigliato prima del commit: il 245, con le prove
     Q15-Q18.
   - Se cambia il codice (240, 241, 243, 244), serve un riesame.
3. Prima di qualunque conto demo per il trader serve una revisione nuova, con:
   - 212 misurato; 198 e 199 corretti; la prova del 234;
   - 242 per il demo;
   - la prova che `DELETE /fapi/v1/allOpenOrders` sul demo lasci stop e obiettivo (ordini «algo»): qui non si può provare.

### Oggetto

* Branch `claude/brave-albattani-1b12fv`, base `11ad4c2`, niente di committato. Fuori da `trader_ai/` non cambia niente:
  `git diff HEAD --stat -- bot/ firebase/ ops/ .claude/ tests/` è vuoto, `bot/risk/hard_limits.py` 841f04e6.
* File cambiati dalla diciassettesima:
  - `avvio.py`:
    - `_ricorda` con `del_giorno` (`:144-155`);
    - `richiama_giorno` letto a inizio passo (`:232`) e nota del giorno (`:281-285`);
    - `fermi_tolti`: tolti a mezzanotte (`:278`), segnati quando il fermo si toglie (`:300-301`), scritti nel resoconto
      (`:1109-1117`, con `OBIETTIVO_GIORNO_QUOTA`);
    - ramo dell'obiettivo: salvataggio dopo la chiusura (`:327`) e motivo provvisorio (`:329-334`);
    - `_chiudi_ora` (`:751-760`);
    - `_annulla_limite` (`:949-985`);
    - «chiudi» del proprietario (`:1054-1066`);
  - `conto_simulato.py`: `annulla_ordini` (`:433-438`);
  - `conto_demo.py`: `annulla_ordini` (`:272-279`);
  - `REGOLE.md`, `README.md`: le regole nuove; 234 e 212 fra gli aperti, solo per il demo;
  - test:
    - `tests/test_diciassettesima.py`, nuovo (37 casi);
    - `tests/test_avvio.py`: `annulla_ordini` del conto finto, due prove agganciate, una asserzione in più sullo stop;
    - `tests/test_controllo_26.py`: una prova agganciata.
  - Nessun test tolto: 178 + 37 = 215.
* Uguali alla diciassettesima: `limiti.py`, `messaggio.py`, `giro.py`, `ripara.py`, `istruzioni.md`, `operazioni.py`, `costi.py`,
  `sveglia.py`, `config.json` e gli altri file di test.
* Invarianti coinvolti (sezione 15 della mappa): lo stop per ogni posizione (rafforzato dal 232); il pulsante che chiude tutto (216,
  241); l'obiettivo del giorno e il fermo (solo resoconto e motivi).

### Stato dei problemi della diciassettesima

| Problema | Esito | Dove | Prova |
|---|---|---|---|
| 213 revisore | **chiuso in parte** | `avvio.py:327`, `:329-334` | Il modo resta e la registrazione è una sola: P5 (quattro casi, prima falliva), `test_213_...`; mutazioni O3, O4, O5, X21 prese. Resta il motivo provvisorio che non dice del 3%: **240**. |
| 214 revisore | **chiuso** | `avvio.py:278`, `:300-301`, `:1109-1117` | `test_214_...` (tre casi), mia Q16 (ore diverse: «alle 10:06 UTC, il 3% era arrivato ma il fermo si è tolto alle 10:20 UTC»); O10-O12, X17 prese; X16 viva per i test del repository (**245**). |
| 215 revisore | **chiuso in parte** | `tests/test_diciassettesima.py` | R1, R2, R4, R5, R6 della diciassettesima ora prese dai test del repository (`esito_mut18b.txt`). La R3 è viva: la P17 portata controlla solo l'inizio del motivo, che ha anche il motivo provvisorio nuovo (**245**). |
| 216 revisore | **chiuso in parte** | `avvio.py:1054-1066` | Operazione chiusa da sola sul conto: si registra con l'esito del conto (`test_216_...`, quattro casi; O13-O15, X14 prese). Restano: il limite con esito non letto si perde (**242**, c'era già); sul demo il ramo del limite non registra mai (**242**); il ramo nuovo può finire in errore (**241**). |
| 230 secondo cercatore | **chiuso** | `avvio.py:751-760`, `:257-263` | `test_230_...` (tre casi); mie Q1-Q4b e Q7b da tutti i punti che chiamano `_chiudi_ora`; O1, O2, X11, X23 prese. Accanto resta il **244** (c'era già). |
| 231 secondo cercatore | **chiuso** | `avvio.py:144-155`, `:232`, `:281-285` | `test_231_...` (tre casi), mie Q12 e Q15; O8, O9, O16, O20, X9, X19 prese; X8 viva per i test del repository, presa da Q15 (**245**). |
| 232 secondo cercatore | **chiuso sul simulato** | `avvio.py:954`, `:975`, `:979-985`; `conto_simulato.py:433-438`; `conto_demo.py:272-279` | P1, P2, P4, `test_232_...` (tre casi); mie Q5 (chiusura che fallisce dal «chiudi» del modello: posizione con il suo stop), Q6, Q7, Q7b, Q8; O6, O7, O17-O19, X1-X5, X25 prese. Le tre prove vecchie agganciate falliscono ciascuna da sola se si torna ad `annulla_tutto` (`tre_prove_vecchie.txt`). Sul demo: da provare che `allOpenOrders` lasci gli ordini «algo». |
| 234 secondo cercatore (solo demo) | **rinviato, il rinvio regge** | `README.md` | Il demo è spento; scritto fra gli aperti. |
| 212 secondo cercatore (solo demo) | **rinviato, il rinvio regge** | `README.md` | Come sopra. |

### Checklist A–F

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py` invariato (841f04e6). `git diff HEAD` vuoto su `bot/`, `firebase/`, `ops/`, `.claude/`, `tests/`. **OK**
* Limiti nel codice, non in configurazione: `limiti.py` (06ad62e4), `costi.py` (2b1e9f30) e `config.json` (6ad5da2d) sono invariati. Il
  resoconto ora usa `OBIETTIVO_GIORNO_QUOTA` (`avvio.py:1109`). **OK**
* Parametri dalla dashboard: **NON APPLICABILE** (il trader non legge Firebase).
* Limiti di G1 sul demo: **NON APPLICABILE**.
* Pulsante che chiude tutto:
  - il fermo a file si legge per primo (`avvio.py:190`) e prima di ogni ordine (`:801`, `:865`, `:880`);
  - «chiudi» scrive il fermo e chiude prima del blocco (`:1036-1050`), senza Firebase. **OK**
  - i rami nuovi (`:1058-1066`) registrano, ma leggono dal conto dentro il blocco: **PROBLEMA 241**; e perdono ancora il limite con
    esito non letto: **PROBLEMA 242**.

**B. Ordini**
* Passi, minimi, leva e margine non toccati (`avvio.py:842-849`, `:864`). **NON APPLICABILE**
* Identificativo dell'ordine: `_chiudi_ora` usa `_cid(ora, "x")` (`:754`), una chiusura per passo. **OK**
* Solo riduzione: chiusure del simulato (`conto_simulato.py:440-451`) e `reduceOnly` del demo (`conto_demo.py:283-287`), invariate.
  **OK**
* Prezzo che attiva gli stop: il mark (`conto_demo.py:255`; il simulato usa le candele mark), invariato. **OK**
* Stop per ogni posizione: più forte di prima.
  - Annullando un limite lo stop resta finché non si sa se il limite si è eseguito (P2, Q5: posizione aperta con il suo stop anche se
    la chiusura fallisce). **OK**
  - Sul demo è da provare che `DELETE /fapi/v1/allOpenOrders` lasci gli ordini «algo» (condizione 3).

**C. Stato e resilienza**
* Posizioni, ordini ed esito riletti dal conto: `_annulla_limite` rilegge dopo l'annullamento (`avvio.py:955-970`). **OK**
* Flussi in tempo reale: **NON APPLICABILE**. Candele chiuse: non toccate. **OK**
* Errori:
  - salvataggi subito dopo le chiusure (`:327`, `:332-334`, `:756`, `:759`);
  - l'esito non letto in `_annulla_limite` interrompe il passo, e il passo dopo lo risolve con `_limite_sparito` (P1, Q7). Nessun
    tentativo infinito nuovo;
  - restano tre cose: il motivo provvisorio (**PROBLEMA 240**) e due che c'erano già (**243**, **244**).
* Firebase e orologio: **NON APPLICABILE**.

**D. Separazione fra simulato, demo e conto vero**
* Il trader gira sul conto simulato (`config.json`: «simulato»).
* `annulla_ordini` del demo passa da `chiedi` e `_url` (`conto_demo.py:41-45`, `:109-121`), solo verso `demo-fapi.binance.com`.
* `annulla_ordini` del simulato non fa richieste nuove: le candele da un minuto, come `annulla_tutto`. **OK**

**E. Segreti**
* Differenza letta tutta: nessuna chiave, nessun percorso di file segreti. Gli eventi e lo stato nuovi scrivono solo ore, guadagni e
  motivi. **OK**
* Chiavi del demo: **NON APPLICABILE** (demo spento).

**F. Test** (comandi ed esiti; tutto nella cartella)
* Trader: `TRADER_AI_BLOCCO=<cartella>/lp.lock python -m pytest trader_ai/tests -q -p no:cacheprovider --basetemp=<cartella>/bt_suite`:
  **215 passed** in 11,8 s. `git status` uguale a prima e dopo (`git_status_prima.txt`).
* Radice: `python3 -m pytest tests/ -q -p no:cacheprovider --basetemp=<cartella>/bt_radice` (`suite_radice.txt`): **2825 passed,
  1 failed, 1 skipped** in 201 s. Il fallito è lo stesso della diciassettesima
  (`tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore`, ricerca). I test dei limiti fissi passano.
* Test nuovi della sessione sul codice della diciassettesima (`prima18_lp.py`, `prima18_esito.txt`): **19 falliti su 37**, come detto
  dalla sessione.
* Mutazioni (`mutazioni18.py`, `esito_mut18.txt`; copia, blocco e cartella temporanea miei):
  - **sessione: 72 prese su 72**;
  - **mie: 13 prese su 21**. Le 8 vive (`esito_mut18_vive.txt`):
    - X8, X15, X16 e X22: le prendono le mie prove Q15, Q17, Q16 e R11b;
    - X7 e X20 (esito «eseguito»): contano solo sul demo, perché il simulato non lo dà mai;
    - X10 e X24: non cambiano niente in pratica.
  - **Le 6 vive della diciassettesima** (`mutazioni18b.py`, `esito_mut18b.txt`): R1, R2, R4, R5, R6 ora prese dai test del repository;
    R3 viva, presa dalla mia Q18.
* Mie prove (`prove/test_prove18.py`, 23 casi; il primo stampa quali `avvio.py` e `conto_simulato.py` importa):
  - sul codice di adesso (00cded62): **22 passate, 1 fallita**. La fallita è la Q11, cioè il problema 240;
  - sul codice della diciassettesima (8ace7619): 10 fallite. Sono le prove del comportamento nuovo, più la Q11
    (`prima18_esito.txt`).
  - Le R10, R13 e R14 passano su tutti e due i codici: quei comportamenti c'erano già.
* Le mie prove della diciassettesima sul codice di adesso (`test_prove17_vecchie.py`): 19 passate, 4 fallite. Le 4 fallite chiedevano il
  comportamento di prima, cambiato apposta: P1, P2, P4 (ora lo stop resta) e il testo del resoconto (214).

### Problemi

**240 — Basso — `trader_ai/avvio.py:329-334` (resto del 213).**
* **Che cosa succede.**
  - Nel ramo dell'obiettivo, dopo la chiusura e la registrazione, il motivo provvisorio è `sveglia.motivo(ora, None, come)`, cioè
    «operazione chiusa (obiettivo del giorno (chiusa dal programma))».
  - Se la rilettura del saldo (`:338`) fallisce e il conto è sotto il 3%, al passo dopo il modello si chiama con quel motivo. Il motivo
    dice «obiettivo del giorno» e non dice che il 3% non è confermato, mentre nello stesso messaggio il conto dice «mancano 1.00».
  - Se il passo dopo arriva dopo mezzanotte, lo stesso motivo entra nel giorno nuovo senza la nota del 231.
* **Quando.** Raro sul simulato: la lettura del saldo deve fallire proprio lì. Sul demo ogni lettura del saldo è una richiesta.
* **Prova** (eseguita).
  - `test_Q11_...` fallisce. Motivo: «operazione chiusa (obiettivo del giorno (chiusa dal programma))». Riga del conto: «... 30.00:
    mancano 1.00».
  - `test_R11b_...` passa: alle 00:00:20 arriva lo stesso motivo, senza nota.
  - Mutazione X22 viva per i test del repository.
* **Correzione** (sessione principale). Motivo provvisorio come proposto nella diciassettesima, salvato con `del_giorno=True`:
  «operazione chiusa (<modo>; il guadagno dopo la chiusura non si è potuto leggere: guarda il conto)». Test: Q11, e R11b adattata.

**241 — Basso — `trader_ai/avvio.py:1058-1066` con `:1072-1076`.**
* **Che cosa succede.**
  - I due rami nuovi del «chiudi» del proprietario registrano con `self.c.saldo()` e `self.c.mercato()` dentro il blocco (sul simulato
    `mercato` è una richiesta pubblica). Se una di queste letture fallisce:
    - il comando finisce con un errore invece di «chiudi: fatto»;
    - lo stato non si salva;
    - il controllo finale si salta: è quello che richiude un ordine partito durante il comando.
  - Prima della correzione, senza posizione, il comando non leggeva niente lì e arrivava sempre in fondo.
* **Effetto.**
  - Il fermo e la chiusura sono già fatti. Il proprietario vede un errore e può credere che la chiusura non sia riuscita.
  - L'operazione resta nello stato: la registra il passo dopo «riparti».
  - Il controllo finale saltato conta solo se un ordine parte proprio durante il comando. Per quel caso c'è anche il controllo del fermo
    in `_esegui` (`:880-888`).
* **Prova** (eseguita, `test_R9_...`). Chiusura sul conto non ancora vista, prezzo che non si legge. Il comando solleva «premiumIndex»,
  il fermo è scritto, `aperta` resta nello stato, il controllo finale non si fa e manca l'evento «chiuso tutto a mano». Sul codice della
  diciassettesima la stessa prova finisce senza errore.
* **Correzione.**
  - Registrare dentro un `try/except` che scrive l'errore e lascia `aperta` com'è (la registra il passo dopo «riparti»).
  - Poi salvare e fare il controllo finale comunque.
  - Test: R9 con il comportamento corretto.

**242 — Basso, c'era già (resto del 216) — `trader_ai/avvio.py:1062-1066`; `trader_ai/conto_demo.py:162-182`.**
* **Che cosa succede.**
  - Simulato: un limite in attesa si è eseguito e chiuso prima del «chiudi». Se l'esito non si legge (`_esito_o_niente` dà None; sul
    simulato l'esito rilegge le candele), il comando mette `aperta` a vuoto. L'operazione sparisce dalla memoria per sempre, anche dopo
    «riparti»: non entra nel bilancio di oggi né nel resoconto.
  - Demo: l'esito del demo non dice mai «chiusa», solo «eseguito». Il ramo del limite non registra mai, e per il demo il 216 non è
    corretto.
* **Prova** (eseguita, `test_R10_...`): 0 operazioni dopo «riparti», uguale sul codice della diciassettesima. Mutazioni X7 e X20 vive:
  sul simulato «eseguito» non arriva mai.
* **Correzione.** Con l'esito non letto, o «eseguito» senza posizione, lasciare `aperta` nello stato: dopo «riparti» il passo la
  risolve con `_limite_sparito`, che rilegge. Sul demo va rifatto insieme al 198, prima del demo.

**243 — Basso, c'era già — `trader_ai/avvio.py:919-923` con `:441-444`.**
* **Che cosa succede.**
  - Il modello chiude e la chiusura riesce, ma la lettura del saldo per registrare fallisce.
  - L'errore arriva a `_decidi_ed_esegui`, che scrive «rifiutata dal conto: GET /fapi/v2/account: 429: pausa».
  - Al passo dopo l'operazione si registra bene: «chiusa da te», una volta sola. Il modello si chiama con «operazione chiusa (chiusa da
    te)», ma lo stesso messaggio contiene anche «rifiutata dal conto: ...»: due cose opposte.
* **Prova** (eseguita, `test_R13_...`): motivo «operazione chiusa (chiusa da te)» e, nel messaggio, la riga «rifiutata dal conto: GET
  /fapi/v2/account: 429: pausa». Passa anche sul codice della diciassettesima.
* **Correzione.** Chiudere con `_chiudi_ora(st, pos, prezzo, ora, "chiusa da te")`. Se la registrazione fallisce dopo una chiusura
  riuscita, l'ultimo scarto deve dire che la chiusura è riuscita e che la registrazione arriva al passo dopo.

**244 — Basso, c'era già — `trader_ai/avvio.py:251-259` con `:751-760`.**
* **Che cosa succede.**
  - La protezione chiude (stop sparito, prezzo oltre) e la lettura del saldo dentro `_chiudi_ora` fallisce.
  - L'errore si scrive («protezione non riuscita») e il passo va avanti con la posizione letta prima.
  - Se nello stesso passo chiude una candela, il modello si chiama e il messaggio dice «posizione aperta: lungo 0.005 BTC ...» per una
    posizione già chiusa. È una chiamata sprecata, con un'informazione sbagliata.
  - Al passo dopo la chiusura si registra e il modello si richiama. Una decisione presa su quella chiamata non parte: `_esegui` rilegge
    il conto.
* **Prova** (eseguita, `test_R14_...`): «posizione aperta: lungo 0.005 BTC, entrata 90000.0 ...» con motivo «candela da 15 minuti
  chiusa». Passa anche sul codice della diciassettesima.
* **Correzione.** Dopo l'errore della protezione, se `aperta` ha `chiusa_da` (chiusura riuscita), salvare e finire il passo: la
  registra il passo dopo.

**245 — Basso — `trader_ai/tests/test_diciassettesima.py:486-509` e altri (resto del 215).**
* **Che cosa manca.** Cinque mutazioni passano tutti i 214 test del repository (`esito_mut18.txt`, `esito_mut18b.txt`):
  - R3 della diciassettesima: il motivo intero «sotto il 3%» non salvato (`avvio.py:364`). La P17 portata controlla solo l'inizio del
    motivo, che ha anche il motivo provvisorio nuovo. Così il motivo che arriva al modello dopo un passo interrotto perde il guadagno
    e il «non raggiunto».
  - X8: `_ricorda` non toglie `richiama_giorno` dalla memoria (`:155`). Se il fermo si toglie, la chiamata parte nello stesso passo e
    il modello apre e chiude subito, il richiamo di `_esegui` porta la nota di ieri.
  - X15: il «chiudi» registra il limite senza `_eseguito` (`:1065`), cioè senza ora d'esecuzione e senza 1 R.
  - X16: l'ora del 3% uguale a quella del fermo tolto (`:300`). Nei test le due ore cadono nello stesso minuto.
  - X22: il testo del motivo provvisorio (`:332`), da sistemare con il 240.
* **Prova** (eseguita): `esito_mut18_vive.txt`. Le mie prove le prendono: R3 da Q18, X8 da Q15, X15 da Q17, X16 da Q16, X22 da R11b.
* **Correzione.** Portare nei test del repository Q15, Q16, Q17 e Q18 (da `prove/test_prove18.py`; gli aiuti sono gli stessi di
  `test_diciassettesima.py`). La P17 deve controllare il motivo intero.

### Invarianti modificati

* **Stop per ogni posizione, rafforzato.** Prima, annullando un ordine limite si toglievano insieme limite, stop e obiettivo. Adesso si
  toglie prima il solo limite. Stop e obiettivo restano finché non si sa se il limite si è eseguito, e si tolgono solo se non si è
  eseguito.
  - Vale in tutti i casi: obiettivo del giorno, «chiudi» o «modifica» del modello, fermo a mano mentre l'ordine parte.
  - Codice: `avvio.py:954`, `:975`; `conto_simulato.py:433-438`; `conto_demo.py:272-279`.
  - Se il limite si esegue proprio in quel momento e la chiusura fallisce, la posizione tiene il suo stop.
* **Pulsante che chiude tutto.** Ora registra nella memoria l'operazione chiusa da sola sul conto e il limite eseguito e chiuso prima
  (`avvio.py:1058-1066`). Per farlo legge saldo, prezzo ed esito dentro il blocco: il problema 241. Il fermo a file e la chiusura
  restano prima di tutto.
* **Invariati:** il tetto di 5 dollari, la leva fino a 10, il 3%, il fermo e la sua rimozione (come alla diciassettesima), lo stop
  obbligatorio, il conto simulato, `bot/risk/hard_limits.py`.

### Decisioni per Alessio

* Il riavvio con la versione 8 sul conto simulato, e il «riparti», sono suoi.
* Restano da confermare le due scelte della diciassettesima, prese dalla sessione dalla sua frase del 26 novembre:
  - sotto il 3% dopo la chiusura del programma si continua;
  - il fermo si toglie se durante il fermo il conto scende sotto il 3%.

  Da adesso il resoconto della sera dice quando il fermo si è tolto e con che guadagno (214): così vede quanto spesso succede.
* Prima di un conto demo per il trader:
  - 212 misurato; 198 e 199 corretti; 234;
  - la prova che `DELETE /fapi/v1/allOpenOrders` lasci stop e obiettivo;
  - il 242 sul demo;
  - una revisione nuova.

### Domande aperte

* La memoria del revisore (`reviews/`) da quest'area non si scrive. Le righe sono qui sotto, per la sessione delle crypto. Chi le
  applica? Restano da applicare anche quelle della diciassettesima, della sedicesima, del suo riesame e di
  `trader_ai/revisioni/righe_per_reviews.patch`.
* Nella cartella `rev18/` c'è anche `cacciatore_casi/`, di un altro processo; io ho usato solo `rev18/revisore_lp/`. Se anche quel
  processo numera i problemi da 240, chi riallinea i numeri?
* `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore` fallisce ancora, come alla diciassettesima. È fuori dal
  percorso degli ordini: lo guarda la sessione della ricerca?
* Il brief parlava di 73 mutazioni: la lista `mutazioni_v8c.py` ne ha 72 (73 righe con quella di base, anche in `esito_v8c.txt`). È
  solo un conto, o ne manca una?

### Impronte md5 (primi 8 caratteri) dei file approvati

* Codice cambiato dalla diciassettesima: `trader_ai/avvio.py` 00cded62, `trader_ai/conto_simulato.py` e04ab2a5,
  `trader_ai/conto_demo.py` 8b34c79b, `trader_ai/REGOLE.md` 6aca6c7c, `trader_ai/README.md` a1e5a085.
* Uguali alla diciassettesima: `limiti.py` 06ad62e4, `messaggio.py` f5201c43, `giro.py` 32156f63, `ripara.py` 392908eb,
  `istruzioni.md` cc36e981, `operazioni.py` 3120d09a, `costi.py` 2b1e9f30, `sveglia.py` 6fd9d573, `config.json` 6ad5da2d.
* Test:
  - cambiati o nuovi: `tests/test_diciassettesima.py` c93b26fd (nuovo), `tests/test_avvio.py` e4b41837, `tests/test_controllo_26.py`
    d5799de7;
  - uguali: `tests/test_obiettivo_riesame.py` cc2b1f5d, `tests/test_obiettivo_netto.py` 24f039ce, `tests/test_trader_ai.py` 73aa19e2,
    `tests/test_simulato.py` 5d0acfe5, `tests/test_corse_188.py` f759675a, `tests/test_secondo_riesame.py` b372138c.
* `bot/risk/hard_limits.py` 841f04e6, invariato.
* Impronte rilette alla fine della revisione (08:00 UTC): uguali.

### Righe per `reviews/` (da applicare dalla sessione delle crypto)

* `reviews/REVIEW_LOG.md`, riga nuova in fondo (poi le voci chiuse più vecchie delle ultime 10 vanno in `ARCHIVE.md`):
  `| 2026-11-27 | claude/brave-albattani-1b12fv | non committato su 11ad4c2 (md5 avvio.py 00cded62, conto_simulato.py e04ab2a5, conto_demo.py 8b34c79b) | trader AI versione 8, correzioni della diciassettesima: stato salvato dopo ogni chiusura del programma, annullando un limite lo stop resta finché non si sa se si è eseguito, «chiudi» che registra le chiusure non viste, fermo tolto nel resoconto, motivo di ieri detto | APPROVE con condizioni (214, 230-232 chiusi; 213, 215, 216 in parte; Bassi 240-245, 242-244 c'erano già) | aperta: riavvio con l'ok di Alessio (conferma delle scelte 204 e fermo tolto); prima di un demo 212, 198, 199, 234, 242 e la prova di allOpenOrders | trader_ai/revisioni/2026-11-27-diciottesima.md |`
* `reviews/INDEX.md`:
  - riga «Numeri dei problemi»: «trader AI fino al 245 (`trader_ai/revisioni/2026-11-27-diciottesima.md`): i nuovi partono da 246»;
  - nella riga «Trader AI»: «diciottesima (correzioni della diciassettesima): APPROVE con condizioni (240-245 Bassi; lo stop resta
    mentre si annulla il limite; prima di un demo provare che `allOpenOrders` lasci gli ordini «algo»)».
* `reviews/LIVE_PATH_MAP.md`:
  - sezione 15, riga dello stop obbligatorio: «annullando un ordine limite si toglie prima il solo limite (`avvio.py:954`;
    `conto_simulato.py:433-438`; `conto_demo.py:272-279`); stop e obiettivo si tolgono solo se il limite non si è eseguito
    (`avvio.py:975`); se si è eseguito si chiude con `_chiudi_ora` (`avvio.py:979-985`)»;
  - sezione 15, riga nuova del pulsante: «`chiudi` del trader: fermo a file, chiusura, poi nel blocco registra anche l'operazione
    chiusa da sola sul conto e il limite eseguito e chiuso (`avvio.py:1033-1076`); letture dentro il blocco: problema 241»;
  - in «Storia degli invarianti»: «27 nov, trader AI diciottesima (non committato, APPROVE con condizioni): **invariante rafforzato**,
    lo stop resta mentre si annulla un ordine limite; il pulsante del trader registra le chiusure non viste. Tetto, leva, 3%, fermo e
    limiti fissi invariati».
