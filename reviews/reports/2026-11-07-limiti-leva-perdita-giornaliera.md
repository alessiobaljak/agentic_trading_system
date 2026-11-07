# Revisione: leva massima a 10 e perdita giornaliera dalla dashboard (modifica proposta)

Data: 7 nov 2026. Revisore: `live-path-reviewer`.

### Riepilogo e verdetto

**REQUEST CHANGES.** Tre problemi bloccanti:
1. la leva massima fissa passa da 5 a 10 senza motivazione nel commit e senza l'ok di Alessio, e il motivo scritto nel
   commento («per G1») è sbagliato: G1 sul demo usa una leva sua e non legge questo limite;
2. la riga nuova degli interruttori usa un attributo che non esiste (`self.user_settings`): a ogni chiusura di un trade
   parte un errore, e così il fermo per la perdita del giorno e la pausa dopo 6 stop di fila non scattano più;
3. anche correggendo l'attributo, il limite della perdita giornaliera finirebbe su Firebase senza alcun controllo: con
   `1.0` o `nan` il fermo del giorno sparisce, con un valore negativo il bot si ferma al primo trade.

I test lo confermano: nella copia con la modifica falliscono 5 test di guardia dei limiti (dettaglio in F).

### Oggetto (branch, commit, file toccati, invarianti coinvolti)

- **Branch**: `claude/brave-albattani-1b12fv`. **Commit di base**: `a988d5dd` (HEAD all'inizio della revisione); durante la
  revisione è arrivato `b29f5713`, che cambia solo `.gitignore` (verificato con `git diff --stat a988d5dd b29f5713`):
  la base è la stessa per i file toccati. Gli indici del diff (`1f2d5dc`, `a6c7e59`) coincidono con i file attuali
  (`git hash-object`).
- **Oggetto**: modifica PROPOSTA, non applicata al repo, in
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/prova_revisore/modifica.diff`.
  Nessun messaggio di commit, nessun ok di Alessio registrato (nessuna traccia in `docs/backlog.md` né in `docs/state.md`).
- **File toccati**: `bot/risk/hard_limits.py` (riga 17), `bot/risk/circuit_breakers.py` (righe 79-81 dopo la modifica).
- **Invarianti coinvolti**: leva massima (`hard_limits.py:17`); perdita giornaliera massima (`hard_limits.py:21`, usata a
  `circuit_breakers.py:79`); di fatto anche la pausa dopo gli stop di fila (`circuit_breakers.py:83-90`) e la tempestività
  del pulsante che chiude tutto del vecchio bot (`bot/main.py:1585`).

### Checklist A–F

**A. Limiti fissi e interruttori**
- Valori fissi invariati: **PROBLEMA**. `hard_limits.py:17` `MAX_LEVERAGE` 5.0 → 10.0, senza motivazione né ok. → Problema 1.
- Nessun limite critico spostato in configurazione o Firebase: **PROBLEMA**. `circuit_breakers.py:79-81` (dopo la modifica)
  legge il limite della perdita giornaliera da Firestore `user_risk_settings`. → Problema 3. Preesistente, fuori dal diff:
  `BACKTEST_PARITY` da variabile d'ambiente spegne tutti gli interruttori (`circuit_breakers.py:50-52`). → Problema 5.
- Parametri della dashboard controllati contro i limiti fissi, con rifiuto e allarme: **PROBLEMA**. Il campo nuovo non ha
  nessun controllo (Problema 3); le regole `firebase/firestore.rules:32-41` controllano solo `leverage` e `risk_per_trade`
  e non vietano campi in più; con la modifica il codice direbbe 10x mentre regole (`:37`) e dashboard
  (`dashboard/app/lib/hardLimits.ts:13`) dicono 5x. Preesistente: oltre il limite il bot taglia con una nota invece di
  rifiutare con un allarme (`risk_manager.py:77-80`, `:212-217`). → Problema 6.
- Limiti propri di G1 sul demo come costanti: **OK** ma da segnalare: `LEVA = 5` (`bot/portafoglio/demo_binance.py:73`),
  `STOP_CONTO = 0.35` (`:78`) sono costanti nel codice, fuori da `hard_limits.py`. Nessun file in `bot/portafoglio/` importa
  `hard_limits` (ricerca con grep): la modifica non li tocca.
- Pulsante che chiude tutto funzionante anche senza Firebase: **PROBLEMA** (effetto indiretto). Con l'errore del Problema 2,
  in ogni ciclo in cui si chiude un trade la parte del pulsante (`bot/main.py:1585`) viene saltata e aspetta il ciclo dopo.
  La prova completa del pulsante senza Firebase non è in questa revisione (rinviata alla revisione completa); il demo ha il
  file `ops/demo_binance_chiudi_tutto` (`demo_binance.py:88`), che non passa da Firebase.

**B. Ordini**: **NON APPLICABILE**. Il diff non tocca l'invio degli ordini, gli arrotondamenti, gli identificativi o gli stop
su Binance. Nota sulla leva: il vecchio paper è simulato (`DRY_RUN` vero) e non simula la liquidazione (nessuna occorrenza
in `bot/execution/executor.py`); con la leva più alta il margine fra stop e liquidazione si accorcia (Problema 1).

**C. Stato e resilienza**: **PROBLEMA**. L'errore in `register_trade_result` interrompe `trading_cycle` (Problema 2): lo stato
del rischio non si salva (`bot/main.py:1524`, `:1551`), le altre posizioni aperte e le chiusure manuali di quel ciclo
aspettano il ciclo dopo. Gli altri punti (ricostruzione da Binance, flussi, candele chiuse, errori delle interfacce):
**NON APPLICABILE** al diff.

**D. Separazione fra paper, demo e conto vero**: **NON APPLICABILE**. Il diff non tocca `DRY_RUN` (`bot/config.py:64`), le
chiavi o gli indirizzi (`demo_binance.py:96-99` invariato).

**E. Segreti e sicurezza**: **OK** per i segreti: il diff non contiene chiavi né indirizzi con token. Per le regole di
Firebase vedi A (il campo nuovo non è protetto). Quali regole siano pubblicate resta «da confermare con Alessio»
(`firebase/firestore.rules:27` ha ancora `REPLACE_WITH_YOUR_FIREBASE_UID`).

**F. Test**: **PROBLEMA**. La modifica non porta test nuovi e ne rompe 5 che fanno da guardia. Eseguiti in una copia
temporanea (`git worktree` fuori dal repo, poi rimossa):
- I test che toccano `bot/risk` (11 file: `test_giorno_locale`, `test_kill_switch_levels`, `test_learning`, `test_portafoglio`,
  `test_portfolio_risk`, `test_regole_portafoglio`, `test_risk`, `test_setup_check`, `test_sizing`, `test_tetto_per_coin`,
  `test_whatif_stop_e_serie`), comando `python3 -m pytest <quei file> -q`:
  - senza la modifica: `120 passed`;
  - con la modifica: `5 failed, 115 passed`:
    - `tests/test_risk.py::test_hardcap_leverage_cannot_be_exceeded` — `assert 10.0 == 5.0`
    - `tests/test_risk.py::test_circuit_breaker_daily_loss_halts` — `AttributeError: 'CircuitBreakers' object has no attribute 'user_settings'` (`bot/risk/circuit_breakers.py:80`)
    - `tests/test_risk.py::test_circuit_breaker_does_not_halt_on_small_equity_losses` — stesso errore
    - `tests/test_risk.py::test_circuit_breaker_consecutive_sl_pause` — stesso errore
    - `tests/test_sizing.py::test_leverage_never_below_one_nor_above_the_hard_cap` — `assert 7.0 == 5.0`
- Suite intera con la modifica, `python3 -m pytest tests/ -q`: `6 failed, 2538 passed, 1 skipped in 139.45s`. Il sesto
  fallimento, `tests/test_allowlist_runnable.py::test_an_allowlisted_command_starts_without_extra_arguments[test]`, fallisce
  anche senza la modifica nella copia temporanea (il pacchetto `research/` viene risolto dal percorso del repo principale):
  dipende dalla copia, non dal diff. La suite intera senza la modifica non l'ho lanciata.
- Prova a mano nella copia con la modifica, impostando `cb.user_settings` a un dizionario (per vedere il comportamento se
  l'attributo esistesse), perdita del giorno −30%: limite `1.0` → nessun fermo; `"nan"` → nessun fermo; `0.05` → fermo;
  `"abc"` → `ValueError` e contatore degli stop rimasto a 0. Con `RiskSettings(**{..., "daily_loss_limit": 0.5})` il campo
  sparisce (campi restanti: `leverage`, `risk_per_trade`, `updated_at`, `updated_by`) e il modello non ha `.get`.

### Problemi

**Problema 1 — Bloccante — `bot/risk/hard_limits.py:17`: leva massima fissa da 5 a 10 senza motivazione né ok.**
- Le regole del revisore: un valore fisso che cambia è bloccante salvo motivazione esplicita nel commit e ok di Alessio
  registrato. Qui non c'è nessuno dei due.
- Il motivo nel commento («alzata per G1: più rendimento») non regge: G1 sul demo manda a Binance la sua costante
  `LEVA = 5` (`bot/portafoglio/demo_binance.py:73`, usata a `:639`) e nessun file di `bot/portafoglio/` legge `hard_limits`.
  La modifica non cambia G1; allarga solo il vecchio percorso (`RiskManager`).
- Scenario di guasto: nel vecchio paper l'utente ha la leva 5 (il massimo concesso da dashboard e regole), l'allocazione dà
  il moltiplicatore massimo 1,3 (`bot/learning/adaptation.py:219`), la volatilità è sotto 1,5σ, quindi
  `safety_leverage_cap` restituisce `MAX_LEVERAGE` (`hard_limits.py:46-50`). Risultato: leva intera 7x invece di 5x
  (`risk_manager.py:93`; il test `tests/test_sizing.py:106` lo mostra: `assert 7.0 == 5.0`). Se il documento di Firestore
  contiene una leva sopra 5 (il bot usa l'Admin SDK e le regole non lo limitano, `firebase/firestore.rules:6-8`), si arriva
  a 10x: il nozionale massimo per posizione (`risk_manager.py:141-149`) raddoppia, e il margine fra stop e liquidazione si
  dimezza (a 10x la liquidazione è a meno del 10% dall'ingresso; lo stop massimo è `MAX_STOP_PCT` 6%, da variabile
  d'ambiente, `bot/config.py:707`; il paper non simula la liquidazione).
- Lascia incoerenti: `risk_manager.py:9` e `:214` (testo «5x»), `dashboard/app/lib/hardLimits.ts:5,13`,
  `firebase/firestore.rules:31,37`, `README.md:128`, `tests/test_risk.py:37`.
- Correzione suggerita alla sessione principale: ritirare la riga. Se Alessio vuole più leva per G1, il valore da discutere
  è `LEVA` in `demo_binance.py:73`, con la sua decisione scritta nel commit; un eventuale aumento del tetto fisso va fatto
  insieme a test, regole, dashboard e testi, nello stesso commit.

**Problema 2 — Bloccante — `bot/risk/circuit_breakers.py:80` (dopo la modifica): attributo inesistente, il fermo del giorno e
la pausa dopo gli stop di fila smettono di funzionare.**
- `CircuitBreakers.__init__` (`:35-37`) crea solo `self.state`; nessuna parte del repo assegna `user_settings` a un
  `CircuitBreakers` (ricerca con grep: `user_settings` esiste solo come parametro di `RiskManager`). La riga
  `(self.user_settings or {})` lancia `AttributeError` a ogni chiamata.
- Scenario di guasto: il vecchio paper chiude un trade allo stop (`bot/main.py:1523`). In `register_trade_result` la
  perdita si somma (`:77`), poi parte l'errore: `halted_for_day` non diventa mai vero, quindi il bot continua ad aprire dopo
  −5%, −10%, −30% del giorno; il contatore degli stop di fila (`:83-90` originali) non si raggiunge mai, quindi la pausa
  dopo 6 stop non scatta; `_persist_risk_state` (`bot/main.py:1524`) salta. L'errore esce da `trading_cycle` ed è preso solo
  dal ciclo principale (`bot/main.py:2603-2607`, stampato e contato; l'avviso parte oltre 3 errori in un'ora): nello stesso
  ciclo saltano la gestione delle posizioni aperte non ancora visitate (`bot/main.py:1454`), le chiusure manuali
  (`bot/main.py:1526-1552`) e il pulsante che chiude tutto (`bot/main.py:1585`). Lo stesso succede a ogni chiusura manuale
  (`bot/main.py:1549`): il comando resta in RTDB e le altre monete richieste aspettano il ciclo dopo.
- Dimostrato da 3 test che falliscono con `AttributeError` a `circuit_breakers.py:80` (sezione F).
- Correzione suggerita: ritirare la modifica (vedi Problema 3). Comunque, nessuna lettura di dati esterni dentro
  `register_trade_result`: è il punto che deve funzionare sempre.

**Problema 3 — Bloccante — `bot/risk/circuit_breakers.py:79-81` (dopo la modifica): limite della perdita giornaliera spostato su
Firebase, senza controllo né allarme.**
- Le regole del revisore: nessun limite critico in configurazione, variabili d'ambiente o Firebase; un valore fuori limite
  si rifiuta con un allarme, mai accettato in silenzio.
- Scenario di guasto (anche con l'attributo corretto, provato nella copia): `daily_loss_limit: 1.0` → nessun fermo nemmeno a
  −30% del giorno; `"nan"` → il confronto è sempre falso, nessun fermo; `-0.01` → fermo appena il giorno è sotto +1%, cioè
  in pratica al primo trade; `"abc"` → `ValueError`, stesso guasto del Problema 2. Le regole di Firestore
  (`firebase/firestore.rules:32-41`) non limitano i campi in più, quindi la dashboard può scrivere qualunque valore, e il
  bot con l'Admin SDK non passa dalle regole.
- La catena non esiste nemmeno: `RiskSettings` (`bot/core/models.py:187-196`) non ha il campo e scarta i campi in più, e non
  ha `.get`; `read_user_risk` (`bot/main.py:610-619`) quindi non lo porterebbe mai al bot, e un `cb.user_settings =
  read_user_risk()` darebbe di nuovo `AttributeError`.
- Il messaggio di blocco (`circuit_breakers.py:57-58`) scrive ancora `hard_limits.DAILY_LOSS_LIMIT`: con un limite diverso
  direbbe un numero falso.
- Correzione suggerita: il limite resta la costante di `hard_limits.py:21`. Se Alessio vuole una manopola sulla dashboard,
  che possa solo **stringere**: limite usato = minimo fra il valore della dashboard e `DAILY_LOSS_LIMIT`; un valore non
  numerico, non finito, ≤ 0 o sopra il limite fisso si rifiuta con un allarme e si usa la costante; il campo entra in
  `RiskSettings` con il suo controllo; le regole ripetono gli stessi limiti e chiudono l'elenco dei campi; il messaggio usa
  il valore applicato; test per ogni caso (`1.0`, `nan`, negativo, testo, campo assente, valore valido più stretto).

**Problema 4 — Medio — nessun test nella modifica.** Una modifica ai limiti fissi senza test nuovi, che rompe 5 test di guardia
(sezione F). I test che falliscono hanno ragione: non vanno aggiornati per farli passare, va ritirata la modifica.

**Problema 5 — Alto, preesistente (non introdotto dal diff) — `bot/risk/circuit_breakers.py:50-52`, `bot/main.py:1741`,
`bot/config.py:672`.** `BACKTEST_PARITY=true` (variabile d'ambiente) spegne tutti gli interruttori (perdita del giorno, pausa
dopo gli stop, finestra macro) e il tetto delle posizioni. Scenario: la variabile resta vera quando si passa al conto vero
(il commento a `bot/config.py:670-671` dice che va rimessa a falso, ma nessun controllo lo impone) e il bot gira senza
fermo giornaliero. Correzione suggerita: rifiutare l'avvio con `DRY_RUN` falso e `BACKTEST_PARITY` vero, con log chiaro. Da
approfondire nella revisione completa.

**Problema 6 — Medio, preesistente — `bot/risk/risk_manager.py:77-80`, `:212-217`; `bot/main.py:616-619`.** Una leva o un
rischio della dashboard oltre i limiti viene tagliato con una nota invece di essere rifiutato con un allarme; un documento
illeggibile diventa in silenzio 2x/1%. Scenario: Alessio imposta un valore che crede applicato e il bot ne usa un altro senza
avvisarlo. Da approfondire nella revisione completa.

**Problema 7 — Basso, preesistente — `bot/main.py:270`, `:1173-1174`; `bot/risk/circuit_breakers.py:88`.** Il bot legge
`circuit_breakers.day_pnl_pct`, che non esiste (il campo è `state.daily_pnl_pct`): il risultato del giorno nel registro dei
trade è sempre vuoto e quello passato all'ombra sempre 0. La nota della pausa dice «4h» ma la pausa è di 2 ore
(`hard_limits.py:26`).

### Invarianti modificati

- **Leva massima**: 5.0 → 10.0 (`bot/risk/hard_limits.py:17`). Effetto su `safety_leverage_cap` (`:46`), sulla precedenza
  (`risk_manager.py:77,83,93`) e sull'ultimo cancello (`risk_manager.py:212-213`). Non tocca G1 sul demo.
- **Perdita giornaliera massima**: da costante (`hard_limits.py:21`) a valore di Firestore senza limiti
  (`circuit_breakers.py:79-81` dopo la modifica); il messaggio (`:57-58`) resta sulla costante.
- **Pausa dopo 6 stop di fila**: testo invariato, ma di fatto spenta dall'errore del Problema 2.

Nessun invariante è cambiato nel codice del repo: la modifica non è applicata.

### Decisioni per Alessio

1. Vuoi alzare la leva? Se è per G1, il numero è la leva del demo (`LEVA = 5`, `bot/portafoglio/demo_binance.py:73`: oggi i
   due lati insieme fanno il 200% del capitale), non il tetto fisso del vecchio bot. Qualunque aumento va con il tuo ok
   scritto nel commit.
2. Vuoi regolare il limite della perdita giornaliera dalla dashboard? Proposta: solo per stringerlo (sotto il 5%), mai per
   allargarlo; un valore fuori limite si rifiuta con un avviso.
3. I limiti di G1 sul demo (leva 5, stop sul conto −35%) devono entrare in `hard_limits.py`, con gli stessi test di guardia?
   Oggi sono costanti in un altro file e nessun test li tiene fermi come i limiti fissi.
4. La parità col backtest (`BACKTEST_PARITY`) spegne tutti gli interruttori: va vietata fuori dal paper (avvio rifiutato con
   `DRY_RUN` falso)? È accesa oggi sulla macchina? Si vede solo dalla macchina.
5. Da confermare fuori dal codice: quali regole di Firestore sono pubblicate (nel repo l'utente è ancora
   `REPLACE_WITH_YOUR_FIREBASE_UID`: pubblicate così, la dashboard non potrebbe scrivere nulla); le chiavi del demo e del
   conto vero sono senza permesso di prelievo e limitate all'indirizzo della macchina?

### Domande aperte

1. Chi ha scritto la modifica proposta e con quale motivo? Non c'è traccia in `docs/backlog.md` né in `docs/state.md`, e il
   commento («per G1») non corrisponde a cosa cambia davvero.
2. Il vecchio paper (il percorso di `RiskManager`) gira ancora sulla macchina, o è fermo con il pulsante STOP? Se è fermo, i
   Problemi 1 e 2 non hanno effetto oggi, ma restano nel codice che un giorno muoverà soldi veri. Non verificato: serve una
   richiesta in `ops/`.
3. La revisione completa del percorso (primo avvio, passo 2) non è stata fatta in questa invocazione: la mappa copre solo i
   limiti fissi e i parametri della dashboard. Quando va fatta?
