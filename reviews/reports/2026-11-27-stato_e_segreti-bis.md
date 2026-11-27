# Revisione del 27 novembre 2026, secondo giro: lo «stato» della macchina e l'oscuramento dei segreti dell'agente

Revisore: live-path-reviewer. Base `117d2b9` sul ramo `claude/brave-albattani-1b12fv`, modifiche non committate. Primo giro:
`reviews/reports/2026-11-27-stato_e_segreti.md` (REQUEST CHANGES solo per lo «stato», problema 203).

### Riepilogo e verdetto

**APPROVE con condizioni** per il commit dei cinque file. Nessun riavvio del bot.

- **L'agente della macchina** (`scripts/ops_agent.py`, `tests/test_ops_agent.py`) è identico al primo giro (stesse impronte). Resta
  approvato. I suoi test passano anche con Python 3.12 e 3.13, chiavi vere comprese: 104 su 104 ogni volta.
- **Lo «stato»**: i cinque problemi del primo giro sono corretti, ognuno con il suo test.
  - 203: il battito e il `DRY_RUN` sono in cima, nel blocco «## Il bot (un solo processo: paper, demo e conto vero)», al carattere
    338 su 19.189.
  - 204: i prezzi pubblici si fermano al primo 429 o 418.
  - 205: il ripiego scatta solo sulla macchina, non su GitHub.
  - 206: «in_corso» ha una riga sua e i resti a mercato rifiutati si vedono.
  - 207: il titolo usa la strategia del processo.
- **Un problema nuovo, Medio (218).** La riga del `DRY_RUN` ora sta in cima, ma legge un campo che il bot della copia di lavoro
  smette di riscrivere quando il vecchio sistema è fermo. Dopo il riavvio che carica quella modifica, la riga mostrerà il valore del
  processo di prima. Oggi il valore è giusto, perché `DRY_RUN` è vero e resta vero. Diventa falso solo il giorno in cui si riavvia
  il bot con `DRY_RUN` falso: lo stato direbbe ancora «True», senza avviso. Va corretto prima del riavvio del bot con il vecchio
  sistema fermo (condizione 2).
- Nessun problema Bloccante o Alto. Gli ordini, i limiti fissi e la configurazione non cambiano: `git diff --stat -- bot/risk/
  bot/config.py firebase/` è vuoto.

Numeri dei problemi: il compito chiedeva di partire dal 197, ma il 197 è già del trader AI (`reviews/INDEX.md:15`). Il 203-207 è
del primo giro e il 210-217 della revisione del bot di oggi (`reports/2026-11-27-bot.md`). Ho usato il **218** (domanda aperta 1).

### Oggetto (branch, commit, file toccati, invarianti coinvolti)

- Impronte md5 (prime 8 cifre) al momento di questa revisione:
  - `scripts/ops_agent.py` c8d9f508, uguale al primo giro;
  - `tests/test_ops_agent.py` 3d3c4a62, uguale;
  - `scripts/state_snapshot.py` **e6c2df30** (al primo giro d4e48408);
  - `tests/test_stato_audit.py` **c2855ea6** (al primo giro 847695ea; da 20 a 28 test);
  - `tests/test_pesi_g1_oggi.py` 2771ad7a, uguale.
- Cosa ho rivisto: la differenza fra la copia del primo giro (`.../scratchpad/correzioni/stato/ritocchi/state_snapshot_prima_dei_ritocchi.py`,
  stessa impronta d4e48408) e il file di adesso, più il codice del bot che scrive i campi letti. Rapporto del correttore:
  `.../scratchpad/correzioni/stato.md`, sezione «Ritocchi».
- Come entrano in funzione: l'agente al primo giro del timer dopo il `git pull`. Lo stato alla prima richiesta «stato» e al primo
  giro di GitHub. Il bot non va riavviato: importa lo stato solo per `_EXIT_LABEL`, e a livello di modulo è stata aggiunta solo la
  costante `BATTITO_MASSIMO_S` (`state_snapshot.py:138`).
- Invarianti coinvolti:
  - il pulsante a file del demo arriva con il `git pull` dell'agente: invariato;
  - nessun segreto nelle risposte: invariato, ed è più forte;
  - lo stato legge e basta;
  - si vede in quale ambiente gira il bot (`DRY_RUN`): è il punto del 218.

### Checklist A–F

**A. Limiti fissi e interruttori**
- Valori di `bot/risk/hard_limits.py`: **OK**. Non toccati (differenza vuota).
- Nessun limite spostato in configurazione: **OK**. `BATTITO_MASSIMO_S = 900` (`state_snapshot.py:138`) è la soglia del testo
  «online o offline» ed era già scritta così nella riga di prima. Non è un limite di rischio e non c'è nessuna variabile
  d'ambiente nuova. `GITHUB_ACTIONS` si legge solo per scegliere il ripiego (`:126`).
- Parametri della dashboard: **NON APPLICABILE**. `bot/main.py` non fa parte di questa revisione.
- Limiti di G1 sul demo: **NON APPLICABILE**. `demo_binance.py` non fa parte di questa revisione.
- Pulsante che chiude tutto senza Firebase: **OK**. L'agente è invariato: il `fetch` e l'avanti veloce sono il primo passo del
  giro (`ops_agent.py:543-547`). Righe ricontrollate.

**B. Ordini**: **NON APPLICABILE**.
- Lo stato non scrive su Firebase: `fb.scritture == []` nel test principale.
- Le letture firmate del demo sono le stesse di prima.
- I prezzi pubblici sono letture senza firma (`state_snapshot.py:1020`, `:1038-1039`).

**C. Stato e resilienza**
- Ricostruzione da Binance, flussi in tempo reale, candele chiuse: **NON APPLICABILE**. Lo stato è un resoconto.
- Errori delle interfacce: **OK** (204 chiuso).
  - Al primo 418 o 429 `rendimenti_mark_giornalieri` non manda più richieste (`:1041-1045`). Segna come non lette la moneta e
    tutte quelle dopo, e scrive il motivo con il `Retry-After`. La riga lo riporta (`:1079`).
  - Test: `test_i_prezzi_si_fermano_al_primo_429_o_418`, per tutti e due i codici. Conta le chiamate: 2, poi nessuna.
  - Gli altri errori (rete, 403, 451, 5xx) segnano la sola moneta e passano alla dopo. Sono al massimo 12 richieste da peso 1:
    accettabile.
- Una scrittura su Firebase che fallisce: **OK**. Lo stato non scrive.
  - `sezione_del_bot` non si rompe con un battito illeggibile (`:152-155`). Test `test_un_bot_bloccato_o_un_dry_run_falso_si_vedono`.
  - `strategia_del_processo` è chiusa in un `try` (`:889-892`).
- Orologio della macchina: **OK**, come al primo giro. Lo stato mostra la sincronizzazione; sulla macchina non è provata
  (condizione 3).

**D. Separazione fra paper, demo e conto vero**
- **203: OK, chiuso.**
  - Il blocco «## Il bot» è la quinta riga, subito sotto la macchina (`:99`, `:141-165`).
  - Ha stato, «online» o «offline» con i minuti dall'ultimo battito, l'ora del battito e il `DRY_RUN`.
  - Un `DRY_RUN` che non è vero ha accanto un avviso in grassetto (`:163`).
  - Il vecchio sistema non ha più nessuna di queste righe (test `tests/test_stato_audit.py:295-297`).
  - Mia prova: il `DRY_RUN` è alla riga 7 di 283, carattere 338 su 19.189 (`.../scratchpad/revisione_27nov/test_prove_revisore.py`,
    rilanciata).
- **PROBLEMA (218, Medio).** Il valore mostrato è `/bot_status/dry_run`. Con il vecchio sistema fermo, il bot della copia di
  lavoro non lo riscrive più.
- La richiesta pubblica a `fapi.binance.com`: **OK**. È senza chiave e non può toccare nessun conto.
- La strategia del conto vero (207): **OK, chiuso**.
  - Si usa `/conto_vero/avvio/strategia` solo se quell'avvio è del processo di adesso: il suo `commit_in_esecuzione` deve essere
    uguale a `/conto_vero/versione/commit` (`:797-814`). I due campi li scrive il bot con questi nomi: `conto_vero.py:923` e
    `:515-520`.
  - Se i due sono diversi, la riga lo scrive: «nel codice F5, nel processo G1: manca il riavvio».
  - Test `test_il_titolo_del_conto_vero_legge_la_strategia_del_processo`, con quattro casi.

**E. Segreti e sicurezza**
- Nessuna chiave nelle risposte: **OK**.
  - L'oscuramento è invariato e più forte (primo giro).
  - Sullo stato finto di adesso non cambia nessuna riga (mia prova: 0 righe).
  - I testi nuovi contengono solo errori di Binance accorciati a 80 caratteri. I resti rifiutati li scrive il bot con
    `str(exc)[:200]` (`demo_binance.py:1829-1831`), dove `RuntimeError` ha metodo, percorso e risposta, senza firma.
- Chiavi di Binance senza prelievo e limitate all'indirizzo: **da confermare con Alessio**. Non cambia niente.
- Regole di Firebase pubblicate: **da confermare con Alessio**. Non cambia niente.

**F. Test**
- Suite intera:
  `python3 -m pytest tests/ -q -p no:cacheprovider -x --deselect tests/test_demo_binance.py::test_firma_dei_tre_tipi_di_chiave`.
  Esito: **3068 passed, 6 skipped, 1 deselected in 212,56 s** (Python 3.11).
  - Gira su tutta la copia di lavoro, quindi anche sulle modifiche degli altri correttori.
  - Il test escluso e i 6 saltati vogliono la libreria delle chiavi, che qui con Python 3.11 è rotta.
- `tests/test_ops_agent.py` con Python 3.12 e 3.13: **104 passed ogni volta**. pytest è preso dalle librerie del 3.11, la
  libreria delle chiavi dall'interprete.
- Con Python 3.12 e 3.13 i due script **compilano**. I test dello stato con il 3.12 **non li ho potuti lanciare**: mancano le
  librerie del bot per quell'interprete.
- Test dei limiti fissi: sono nella suite e passano (`tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_demo_binance.py`,
  `tests/test_conto_vero.py`).
- I test nuovi coprono 203-207. Il correttore li ha provati anche sul file di prima: 10 falliti su 28
  (`.../correzioni/stato/ritocchi/test_nuovi_col_file_di_prima.txt`).
- Le mie prove:
  - `.../scratchpad/revisione_27nov/test_prove_revisore.py`, 4 passed. Lunghezza 19.189 caratteri: margine 311 al ripiego e
    771 all'agente. Con il conto vero acceso il ripiego scatta, 17.340 caratteri, e la riga scelta è il 2026-11-23, non
    «in_corso». Su GitHub 14.811 caratteri, senza ripiego.
  - `.../scratchpad/revisione_27nov_bis/test_prove_bis.py`, 2 passed: è la prova del 218.
- **Manca**: un test che leghi la riga del `DRY_RUN` al valore del processo di adesso (218).

### Problemi

**218 — Medio — `scripts/state_snapshot.py:141-165` (la riga `:163`), insieme a `bot/main.py:2626-2628` e `:977-983` della copia di lavoro**

- **Cosa non va:**
  - La riga «- DRY_RUN» del blocco in cima legge `/bot_status/dry_run`.
  - Quel campo lo scrive solo `refresh_regime` (`bot/main.py:977-983`), una volta l'ora e solo dentro il giro del vecchio
    sistema (`:2680`; anche `:914`, `:918`, dentro la scansione).
  - Il bot della copia di lavoro (revisione `reports/2026-11-27-bot.md`, da riavviare con l'ok di Alessio) salta tutto quel giro
    quando c'è `ops/gate_fermo` e il vecchio paper non ha niente aperto (`_vecchio_sistema_fermo`, `:2550-2573`; `:2626-2628`). Da
    fermo riscrive solo `/bot_status/state` una volta l'ora (`:2588-2590`) e il battito a ogni giro (`:2715`).
  - Il commento della funzione dice che il bot «scrive `/bot_status` e il battito a ogni giro» (`state_snapshot.py:142-143`): non
    è vero nemmeno oggi, perché `/bot_status` si riscrive una volta l'ora.
- **Scenario di guasto:**
  1. Si committa la modifica del bot e si riavvia, con l'ok di Alessio. `ops/gate_fermo` c'è e il vecchio paper non ha niente
     aperto, quindi `refresh_regime` non gira più. `/bot_status/dry_run` resta quello scritto dal processo di prima: vero.
  2. Un giorno, per il conto vero, si riavvia il bot con `DRY_RUN` falso.
  3. Lo stato scrive ancora «- DRY_RUN: True», in cima e senza avviso. Il conto vero, senza interruttore, scrive «spento: manca
     l'interruttore», perché `motivo_spento` guarda prima l'interruttore (`conto_vero.py:421-426`). Nessuna riga dello stato dice
     che il `DRY_RUN` è falso. È proprio il caso che il 203 doveva far vedere.
  4. Lo stesso campo lo legge la dashboard (`dashboard/app/components/ReconcilerStatus.tsx:66`). Se qualcuno cancella
     `/bot_status` (`scripts/reset_paper.py`), la riga resta «—» per sempre.
- **Prova:** `.../scratchpad/revisione_27nov_bis/test_prove_bis.py`.
  - Tre giri veri di `TradingBot.run` con il vecchio sistema fermo e `settings.DRY_RUN` falso: nessuna scrittura su
    `/bot_status` e su `/bot_status/dry_run`, tre battiti.
  - Poi `sezione_del_bot` restituisce «- DRY_RUN: True», senza avviso.
- **Oggi non fa danni.** `DRY_RUN` è vero e il valore rimasto è vero. Il passaggio a falso chiede la richiesta esplicita di
  Alessio e una revisione dell'accensione del conto vero.
- **Correzione suggerita alla sessione principale** (basta una delle due strade per lo stato; la prima sistema anche la
  dashboard):
  1. **Nel bot**, dentro il riavvio già in preparazione: `_publish_avvio` (`bot/main.py:1091-1104`) scrive anche
     `/bot_status/dry_run` = `settings.DRY_RUN` a ogni avvio. Meglio ancora anche una volta l'ora in `_giro_vecchio_fermo`,
     insieme a `state` (`:2588-2590`). Test in `tests/test_main_audit.py`: con il vecchio sistema fermo, dopo l'avvio
     `/bot_status/dry_run` è uguale a `settings.DRY_RUN`. Passa da live-path-reviewer come il resto della modifica del bot.
  2. **Nello stato**, senza riavvio: il valore del processo di adesso si legge da
     `/avvii_config/{int(avviato_at)}/interruttori/DRY_RUN`, con `avviato_at` da `/bot_status/avviato_at`. Lo scrive il bot a
     ogni avvio (`pubblica_versione`, `bot/main.py:376-391`; `bot/learning/cattura.py:44-45`, `:135-141`). Se manca, o se è
     diverso da `/bot_status/dry_run`, la riga lo dice in grassetto. Test con i due valori diversi.
  - In tutti e due i casi va corretto anche il commento di `sezione_del_bot`.

**Note, che non sono problemi**
- La riga «in_corso» del conto vero, una volta scritta, resta in ogni stato: il bot non cancella quella chiave. Mostra la sua ora,
  quindi chi legge vede che è vecchia.
- La riga «ultima decisione» del demo sceglie ancora `max` su tutte le chiavi (`state_snapshot.py:732`), comprese quelle
  «-eventi-HHMM». È così da prima, e gli eventi sul demo sono spenti.
- A mezzanotte lo stato può dire «offline» per un bot che lavora. Il battito si scrive prima dei giri dei paper e del demo
  (`bot/main.py:2715` prima di `:2726-2753`), e ogni paper che ribilancia scarica le candele per 4-5 minuti (audit). Con tre
  paper il battito può superare i 15 minuti. È un falso allarme dalla parte sicura, con la stessa soglia di prima.
- Su GitHub i prezzi pubblici di `fapi.binance.com` probabilmente sono rifiutati, perché Binance blocca alcuni paesi e le
  macchine di GitHub sono quasi tutte negli Stati Uniti. In `docs/state.md` la colonna direbbe «prezzi non letti». Non fa danni.
  Non l'ho verificato.
- Il margine al ripiego è di 311 caratteri. Il ripiego scatterà presto, per esempio con un allarme in più: è il comportamento
  voluto.

### Invarianti modificati

- **Percorso degli ordini: nessuno.** Restano invariati:
  - i limiti fissi;
  - gli ordini, i pulsanti e lo stop sul conto;
  - la sola lettura del demo nello stato;
  - la finestra vietata;
  - il blocco al 429 o 418, che ora vale anche per i prezzi pubblici.
- **Chi parla con Binance (sezione 1 della mappa):** in più c'è la lettura pubblica `GET fapi.binance.com/fapi/v1/markPriceKlines`.
  Al massimo 12 per stato, fuori dalle 23:50-01:45, si ferma al primo 429 o 418 (`state_snapshot.py:1020-1051`).
- **L'oscuramento dell'agente** è più forte (primo giro). Nella mappa ho aggiornato le righe dell'agente (`:419-423`, `:543-547`,
  `:341-373`, `:50-146`).
- **Come si mostra l'ambiente attivo:** il `DRY_RUN` è di nuovo in cima. Con il bot della copia di lavoro diventa però un valore
  rimasto dal processo di prima (218).
- Ho aggiornato `reviews/LIVE_PATH_MAP.md` (sezioni 1, 10, 11, 13 e la storia), che resta a 300 righe.

### Decisioni per Alessio

1. Nessuna decisione sui limiti.
2. Per il commit di questi cinque file non serve il suo ok: non c'è riavvio e non si toccano gli ordini. L'agente della macchina
   cambia al primo giro dopo il commit.
3. Quando gli si chiede l'ok al riavvio del bot con il vecchio sistema fermo, deve sapere che, senza la correzione del 218, la
   riga del `DRY_RUN` dello stato e della dashboard resta quella del processo di prima.
4. Da confermare fuori dal codice, come al primo giro:
   - accendere su GitHub «secret scanning» e «push protection» del repository pubblico;
   - chiavi di Binance senza permesso di prelievo e, per le vere, limitate all'indirizzo della macchina (oggi non lo sono);
   - regole di Firebase pubblicate con i blocchi del demo e del conto vero.

### Domande aperte

1. **Numeri dei problemi.** Il compito chiedeva di partire dal 197. Il 197 è del trader AI (`reviews/INDEX.md:15`, «194-197
   chiusi»), il 203-207 del primo giro di questa revisione e il 210-217 della revisione del bot di oggi. Il 208 e il 209 non li
   trovo usati, ma non so se sono tenuti da parte. Ho usato il 218. Va bene, o la sessione principale vuole rinumerare?
2. **Il 218: quale strada?** Nel bot, dentro il riavvio già in preparazione e con la revisione del bot, che sistema anche la
   dashboard? Oppure nello stato, subito e senza riavvio? Oppure tutte e due?
3. **La dimensione vera dello stato sulla macchina** (domanda 3 del primo giro) è ancora aperta. Chi chiede la risposta «stato»
   dopo il commit, e chi controlla le righe della condizione 3?

La domanda 2 del primo giro è chiusa. `bot/execution/notifier.py` lo copre la revisione del bot (`reports/2026-11-27-bot.md`,
sezione E, impronta d4fa8c4c, uguale a quella di adesso).

### Condizioni

1. Al commit, le impronte uguali a quelle di questo rapporto: `ops_agent.py` c8d9f508, `test_ops_agent.py` 3d3c4a62,
   `state_snapshot.py` e6c2df30, `test_stato_audit.py` c2855ea6, `test_pesi_g1_oggi.py` 2771ad7a. L'agente si può committare
   anche da solo.
2. **Il 218 va corretto, con il suo test, prima del riavvio del bot che carica `_vecchio_sistema_fermo`**, oppure nello stesso
   commit della modifica del bot. Al più tardi, prima di qualunque riavvio con `DRY_RUN` falso. La correzione passa da un riesame
   breve.
3. Dopo il commit dello stato si chiede una risposta «stato» e si controlla che:
   - non ci sia la scritta «caratteri omessi»;
   - in cima ci sia «## Il bot (un solo processo: paper, demo e conto vero)», con «online» e «DRY_RUN: True»;
   - ci siano le righe «Le 10 monete con il funding più grande», «monete del paper G1 che il demo non ha avuto» e la tabella del
     funding per regolamento;
   - le tre sezioni che leggono il demo non siano «non letto»;
   - la riga della macchina abbia letto disco, memoria e orologio, e l'orologio risulti sincronizzato;
   - la lunghezza sia sotto i 19.500 caratteri, oppure, se il ripiego è scattato, ci sia la sua riga.
4. Dopo il commit dell'agente il battito `ops/heartbeat.md` deve continuare ad andare avanti, e la risposta seguente deve
   arrivare come sempre.
