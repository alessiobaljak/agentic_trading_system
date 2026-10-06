# Regole di dimensione, leva, margine ed esecuzione del bot (Passo 0)

Fatti della sezione 3.2 del protocollo (versione 4.3), letti dal CODICE del bot il
6 ottobre 2026. Ogni affermazione porta `file:riga` (righe del repository a quella
data). Il test `research/src/tests/test_fatti.py` controlla che ogni riferimento
punti a una riga esistente e che le righe chiave dicano davvero ciò che qui si
afferma: se il bot cambia, il test lo segnala e questo file va riletto.

Cosa è stato aperto: `bot/**`, `backtesting/**`, `scripts/**`, `requirements.txt`,
`scripts/install_optimizer_timer.sh`, `.gitignore`. Cosa NON è stato aperto, per
regola: `.env` e ogni file di segreti, `ops/`, `docs/`, `tests/`, `dashboard/`,
`data_cache/`. Il modello `.env.example` non è stato aperto perché la sessione ne ha
negato la lettura (regola dell'ambiente sui file `*.env*`): i nomi dei parametri
vengono tutti da `bot/config.py`. Nessun valore di segreto compare qui: solo nomi.

Parole usate: «paper» = il bot gira con `DRY_RUN` attivo e non manda ordini
(`bot/config.py:64`, default vero); «live» = il percorso con ordini veri, che esiste
nel codice ma non è mai stato usato; «gate» = il backtest interno del bot che
valida le coppie (moneta, strategia); «last» = ultimo prezzo scambiato; «mark» =
mark price di Binance.

---

## 1. `serie_stop`: quale prezzo fa scattare lo stop

### Nel paper (nessun ordine)

Lo stop si valuta in `ExecutionEngine.update_position(symbol, mark_price, high, low)`
(`bot/execution/executor.py:541-684`). La regola è: per un long lo stop scatta se
`lo <= stop_effettivo`, per uno short se `hi >= stop_effettivo`
(`bot/execution/executor.py:605` con scale-out, `bot/execution/executor.py:664` senza);
`hi`/`lo` sono il range del tick, sempre allargato al `mark_price` passato
(`bot/execution/executor.py:570-571`). Il prezzo di uscita è esattamente il livello
dello stop, senza slippage (`bot/execution/executor.py:618`, `bot/execution/executor.py:667`).

Da dove vengono i tre numeri, nel ciclo di gestione delle posizioni (`bot/main.py:1352-1372`):

* `mark_price` = il **mark price vero di Binance**, letto a ogni tick da
  `/fapi/v1/premiumIndex` campo `markPrice` (`bot/main.py:1353`;
  `bot/agents/price_agent.py:127-136`, riga `bot/agents/price_agent.py:132`). Se manca,
  ripiego sull'ultimo prezzo dello snapshot (`bot/main.py:1354-1356`).
* `high`/`low` = il **percorso del prezzo dall'ultimo tick**, da una di due fonti:
  1. lo stream WebSocket `bookTicker` di Binance Futures, di cui si usa il **mid fra
     miglior bid e miglior ask** (`bot/agents/price_stream.py:16-23`,
     `bot/agents/price_stream.py:253-258`, riga `bot/agents/price_stream.py:258`); i punti
     vengono rigiocati uno per uno nell'ordine di arrivo (`bot/main.py:1362-1364`;
     `bot/execution/executor.py:686-704`) e poi il range aggregato fa da rete
     (`bot/main.py:1367-1369`);
  2. se lo stream non è sano, le **candele 1m REST** (`/fapi/v1/klines`), high e low
     delle ultime 3 (`bot/main.py:728-737`; `bot/config.py:337`): sono candele del
     last price.

Quindi nel paper lo stop scatta su un **misto**: il percorso del mid bid/ask (≈ last)
oppure le ombre delle candele 1m (last), **più** il punto del mark price di quel tick.
Non esiste una serie unica. Il take profit si valuta sullo stesso range
(`bot/execution/executor.py:670-672`); l'uscita a fine orizzonte usa il `mark_price`
(`bot/execution/executor.py:643`, `bot/execution/executor.py:678`).

Prezzo d'ingresso nel paper: `asset.price` (`bot/execution/executor.py:273`), cioè la
chiusura della candela **in formazione** all'ultima lettura delle klines
(`bot/agents/price_agent.py:160`): un last price, non il mark. La regola della
strategia invece decide sulla chiusura dell'ultima candela chiusa
(`bot/core/models.py:99-104`; `bot/strategies/generated.py:625-640`;
`bot/config.py:290`).

### Nel percorso live (ordini veri, mai usato)

* Ingresso: ordine **LIMIT GTC** al prezzo `entry_price`
  (`bot/execution/executor.py:363-366`, riga `bot/execution/executor.py:364`), con attesa
  del fill per `EXEC_FILL_TIMEOUT_S` (default 20 s, `bot/config.py:244`) e rinuncia
  sotto `EXEC_MIN_FILL_FRACTION` (default 0,5, `bot/config.py:248`).
* Stop: ordine **STOP_MARKET** reduce-only (`bot/execution/executor.py:461-464`, riga
  `bot/execution/executor.py:462`), ripiazzato quando lo stop si muove
  (`bot/execution/executor.py:503-507`).
* Take profit: **TAKE_PROFIT_MARKET** reduce-only, uno per gradino della scala
  (`bot/execution/executor.py:479-482`, riga `bot/execution/executor.py:480`).
* Chiusure decise dal software (fette dello scale-out, fine orizzonte, kill switch):
  **MARKET** reduce-only (`bot/execution/executor.py:786-788`,
  `bot/execution/executor.py:798-800`, `bot/execution/executor.py:440-442`).
* `workingType`: **non trovato**. Nessuna chiamata passa `workingType` (cercato in
  `bot/`, `backtesting/`, `scripts/`: zero occorrenze). Vale quindi il default di
  Binance, che la documentazione indica come `CONTRACT_PRICE` = last price (da
  verificare sulla documentazione ufficiale, come chiede il protocollo). Lo stop
  nel live scatterebbe quindi sul **last**, mentre nel paper il mark price entra nel
  range: le due serie **differiscono**, e il protocollo chiede di segnalarlo.

### Nel gate (backtest interno)

Lo stop scatta sulle ombre delle candele del last price (`/fapi/v1/klines`): per un
long se `c.low <= eff_stop`, per uno short se `c.high >= eff_stop`
(`backtesting/engine.py:942`, `backtesting/engine.py:953`; con scale-out
`backtesting/engine.py:895`). Stop prima del take profit nella stessa barra
(`backtesting/engine.py:942-952`, `backtesting/engine.py:894-909`).

**Valore proposto per `serie_stop`: last price** (è la serie del gate e del percorso
live con il default di Binance), con la nota che il paper del bot aggiunge il mark
price al range: va dichiarato nel confronto del Passo 9.

---

## 2. `regole_dimensione_bot`: rischio, leva, margine, limiti

### Rischio per trade

* Parametro utente `risk_per_trade`, frazione del capitale, letto da Firebase
  (`user_risk_settings/current`) prima di ogni trade (`bot/main.py:593-602`); modello
  `RiskSettings.risk_per_trade` default **0,01 = 1 %** (`bot/core/models.py:194`);
  ripiego se Firebase non risponde `DEFAULT_RISK_PER_TRADE = 0.01` (`bot/config.py:162`).
* Tetto assoluto non modificabile `MAX_RISK_PER_TRADE = 0.03` (3 %)
  (`bot/risk/hard_limits.py:18`); dimezzato sopra 3 sigma di volatilità
  (`bot/risk/hard_limits.py:27-28`, `bot/risk/hard_limits.py:53-56`).
* Il rischio effettivo = minimo fra richiesta utente (scalata dall'allocazione), cap
  di volatilità e tetto assoluto (`bot/risk/risk_manager.py:94`), poi moltiplicato
  per il `size_multiplier` della decisione, che può solo ridurre (`bot/risk/risk_manager.py:96-97`).
* La quantità = (equity × rischio) / |prezzo − stop| (`bot/risk/risk_manager.py:124-138`).
  Lo stop viene dalla strategia (`atr_mult_stop` × ATR, `bot/strategies/base.py:99-115`,
  `bot/strategies/generated.py:771`), altrimenti 1,5 ATR con rapporto 2
  (`bot/risk/risk_manager.py:99-107`, `bot/risk/risk_manager.py:187-199`).
* Il nozionale è poi limitato a equity × leva e, se `MAX_POSITION_EQUITY_FRACTION`
  < 1, a equity × leva × frazione (`bot/risk/risk_manager.py:140-153`); default 1,0
  ma **0,10 in parità col backtest** (`bot/config.py:181`; `bot/risk/risk_manager.py:146-147`).
  Con questo cap il rischio davvero corso è spesso sotto l'1 % impostato; il numero
  è esposto come `risk_effective_pct` (`bot/risk/risk_manager.py:155-168`).
* Stop più largo di `MAX_STOP_PCT` (default **0,06 = 6 %** del prezzo) = setup non
  tradabile, sia nel gate sia nel bot, dalla stessa funzione
  (`bot/config.py:693`; `bot/risk/setup_check.py:37-59`; `bot/risk/risk_manager.py:112-123`;
  `backtesting/engine.py:855`).
* Equity del paper: letta da Firebase, default 1.000 (`bot/main.py:604-607`;
  `bot/main.py:758`).

### Leva

* Parametro utente `leverage`, default **2,0** (`bot/core/models.py:193`;
  `bot/config.py:161`), moltiplicato per `lev_mult` dell'allocazione (fra 0,7 e 1,3,
  `bot/learning/adaptation.py:219`), mai sotto 1 (`bot/risk/risk_manager.py:65`).
* Tetto assoluto `MAX_LEVERAGE = 5.0` (`bot/risk/hard_limits.py:17`), riapplicato al
  cancello finale (`bot/risk/risk_manager.py:212-214`).
* Cap di volatilità: oltre 1,5 sigma max 4x, oltre 2 max 3x, oltre 3 max 2x
  (`bot/risk/hard_limits.py:33-37`, `bot/risk/hard_limits.py:40-50`).
* La leva effettiva = minimo dei tre (`bot/risk/risk_manager.py:83`), arrotondata a
  **intero** con `floor(x + 0,5)`, mai sotto 1 (`bot/risk/risk_manager.py:84-93`).
  Con base 2 le leve ottenibili sono 1x, 2x, 3x.
* Nel live la leva viene impostata per simbolo con `futures_change_leverage`
  (`bot/execution/executor.py:362`).
* Il margine usato = nozionale residuo / leva (`bot/main.py:609-614`); un'apertura che
  porterebbe il margine oltre l'equity viene rifiutata, come farebbe Binance
  (`bot/main.py:1775-1788`).

### Modalità di margine (isolated / cross)

**Non trovata.** Nessuna chiamata a `futures_change_margin_type`, nessuna stringa
`marginType`, `ISOLATED` o `CROSSED` in `bot/`, `backtesting/`, `scripts/`. Il bot
non la imposta: nel live varrebbe il default del conto Binance per quel simbolo (di
norma cross, da verificare sulla documentazione ufficiale). Nel paper la modalità non
entra in nessun calcolo: non esiste un prezzo di liquidazione (vedi punto 5).

### Numero massimo di posizioni e limiti per moneta / direzione

* `MAX_OPEN_POSITIONS` default **5** (`bot/config.py:176`), applicato in
  `bot/main.py:1639-1644` ma **disattivato sotto `BACKTEST_PARITY`** (stessa riga; il
  flag è a `bot/config.py:658`, default falso); in parità il limite diventa il margine
  esaurito (`bot/main.py:1648-1650`).
* **Una posizione per moneta**: le posizioni sono indicizzate per simbolo
  (`bot/execution/executor.py:309`) e un segnale su una moneta già aperta è rifiutato
  (`bot/main.py:1605-1609`); l'orchestratore emette al massimo una decisione per moneta
  (`bot/orchestrator/orchestrator.py:450-453`).
* **Rischio direzionale**: la somma del rischio (distanza dallo stop × quantità
  residua) delle posizioni nello stesso verso, più il nuovo trade, non oltre
  `MAX_DIRECTIONAL_RISK_PCT` = **0,03** dell'equity (`bot/config.py:237`;
  `bot/main.py:650-669`; `bot/main.py:1763-1773`).
* **Tetto di perdita per moneta al giorno**: `RISK_PER_COIN_DAY` = **0,015** dell'equity;
  superato, la moneta non si riapre fino a mezzanotte UTC (`bot/config.py:686`;
  `bot/main.py:1624-1637`; `bot/risk/daily_cap.py:30-40`).
* **Correlazione**: massimo 3 posizioni con correlazione > 0,85 sui rendimenti orari
  delle ultime 24 candele (`bot/config.py:222-230`; `bot/main.py:1691-1698`;
  `bot/risk/correlation_guard.py:1-7`).
* **Cooldown dopo uno stop in perdita**: 4 barre del timeframe sulla moneta
  (`bot/config.py:207-212`; `bot/main.py:1610-1623`), stessa regola nel gate
  (`backtesting/engine.py:1006-1008`); panchina di strategia dopo 3 stop di fila per
  8 barre (`bot/config.py:213-217`).
* Posizioni esplorative aperte insieme: massimo 3 (`bot/config.py:485`).
* Interruttori generali: perdita giornaliera oltre il 5 % ferma tutto, 6 stop di fila
  = pausa di 2 ore (`bot/risk/hard_limits.py:21-26`; `bot/risk/circuit_breakers.py:1-6`);
  kill switch a tre livelli letto da Firebase (`bot/risk/kill_switch.py:1-21`).

### Come il rischio e la size si riducono (solo elenco, con riferimenti)

Tutti i fattori sotto possono solo ridurre; nessuno supera i tetti sopra.

1. Allocazione «convinzione × apprendimento»: `risk_mult` fra 0,5 e 1,5, `lev_mult`
   fra 0,7 e 1,3 (`bot/learning/adaptation.py:184-222`), calibrazione della
   confidenza verso il neutro (`bot/config.py:555-558`).
2. Freno di deriva paper→gate: × `DRIFT_WEIGHT_FACTOR` 0,5 per coppia, per strategia
   e globale, pavimento `DRIFT_WEIGHT_FLOOR` 0,25 (`bot/config.py:440-441`;
   `bot/learning/drift.py:586-623`; applicato in `bot/learning/adaptation.py:228-237`).
3. Freno di serie (4 perdite di fila → × 0,5): **spento** per default
   (`bot/config.py:462-464`).
4. Freno per gruppo (CUSUM sui pool): **spento** per default (`bot/config.py:529-534`).
5. Coppie esplorative (quasi-passaggi del gate): size × `ESPLORATIVA_SIZE_MULT` 0,25
   (`bot/config.py:483`; `bot/main.py:1731-1745`).
6. Coppie declassate dal gate: size × `DECLASSATA_SIZE_MULT` 0,25
   (`bot/config.py:501`; `bot/main.py:315-332`).
7. Pavimento della panchina: peso strategia×regime sotto soglia → size × max(0,25,
   peso) invece del rifiuto (`bot/config.py:545`; `bot/main.py:1746-1752`).
8. Tilt di trend: controtrend × fino a 0,5 (`bot/config.py:674-678`;
   `bot/orchestrator/orchestrator.py:514-522`).
9. Tilt di sentiment: contro il verso × fino a 0,5 (`bot/config.py:702-704`;
   `bot/main.py:1708-1716`).
10. Cap di volatilità su leva e rischio (`bot/risk/hard_limits.py:27-56`).
11. Cap di nozionale per posizione (`bot/risk/risk_manager.py:140-153`).

Nessuna di queste riduzioni esiste nel gate (vedi punto 5): sono solo del bot vivo.

---

## 3. Costi nel bot e nel gate

### Commissione per trade

* Un solo numero per andata e ritorno: `BACKTEST_COST_PER_TRADE`, default
  **0,0008 = 0,08 % del nozionale, round-trip** (`bot/execution/executor.py:178`;
  `backtesting/engine.py:613-616`). Il commento del motore lo descrive come «taker
  ~0,04 %/lato + slippage» (`backtesting/engine.py:614`).
* Più uno **spread stimato per fascia di volume 24h**, anch'esso round-trip:
  0,012 % sopra 200 M USDT, 0,025 % sopra 50 M, 0,045 % sopra 10 M, 0,08 % sotto
  (`bot/core/costs.py:13-24`). Nel bot la fascia si fissa all'apertura dal volume 24h
  del ticker (`bot/execution/executor.py:280`); nel gate dal volume medio in USDT delle
  ultime 720 candele (`backtesting/engine.py:644-657`).
* Nel bot i costi sono scomposti in commissione, spread e funding e sottratti al PnL
  (`bot/execution/executor.py:857-871`); nel gate sottratti dal rendimento del trade
  (`backtesting/engine.py:972-977`). In paper sono dichiarati «stimati», non misurati
  (`bot/execution/executor.py:928`).

### Funding

* Modello condiviso `funding_fraction`: costo = (ore in posizione / 8) × tasso, col
  segno (long paga a tasso positivo, short incassa) — **continuo e proporzionale alle
  ore**, non ai settlement (`bot/core/costs.py:27-39`, riga `bot/core/costs.py:39`).
* Nel bot il tasso è quello della moneta **all'ingresso** (`lastFundingRate` da
  `premiumIndex`, `bot/agents/price_agent.py:195`; `bot/execution/executor.py:861-864`);
  se manca, `BACKTEST_FUNDING_PER_8H` default 0,0001 (`bot/execution/executor.py:179`).
* Nel gate il tasso è la **media degli ultimi 1.000 settlement storici** della moneta
  da `/fapi/v1/fundingRate` (`backtesting/data_loader.py:37-55`), fissa per tutta la
  storia simulata (`backtesting/engine.py:631-642`, `backtesting/engine.py:974-977`);
  stesso ripiego a 0,0001/8h.
* L'intervallo di funding è sempre considerato di 8 ore: non c'è lettura di
  `fundingIntervalHours` né di intervalli a 4 h o 1 h (nessuna occorrenza in
  `bot/`, `backtesting/`, `scripts/`).

### Slippage

* Non modellato come voce separata: è dentro lo 0,08 % e nello spread per fascia
  (`backtesting/engine.py:644-650`; `bot/core/costs.py:1-9`).
* Nel paper gli stop e i take profit si riempiono esattamente al livello
  (`bot/execution/executor.py:618`, `bot/execution/executor.py:667`,
  `bot/execution/executor.py:672`); l'ingresso avviene al prezzo vivo dello snapshot.
  Lo slippage d'ingresso misurato è la differenza fra prezzo eseguito e chiusura della
  candela del segnale (`bot/execution/executor.py:917-921`; `bot/execution/executor.py:321-337`).

---

## 4. `esecuzione_strategie_bot`: in che forma il bot esegue una strategia

### Le due forme che esistono

1. **Strategie scritte in codice Python.** Classe base astratta `Strategy`
   (`bot/strategies/base.py:36-76`): dichiara `name`, `active_regimes`,
   `default_params`, `param_grid` e implementa `generate_signal(asset, ctx) ->
   StrategySignal | None` (`bot/strategies/base.py:71-76`); il segnale porta direzione,
   confidenza, stop e target (`bot/strategies/base.py:79-97`). Si registra con il
   decoratore `@register_strategy` (`bot/strategies/base.py:124-129`) e con un import in
   `bot/strategies/__init__.py:10-19`; ce ne sono 9 (`bot/strategies/__init__.py:11-19`).
   Il timeframe è quello unico del bot (`bot/strategies/base.py:59-64`).
2. **Strategie generate (spec dichiarative).** `GeneratedStrategy(Strategy)`
   interpreta una spec (dizionario: `features`, `atr_mult_stop`, `rr`, `timeframe`,
   `solo`, `volume_mult`, `min_adx`) e vota long/short se tutte le feature concordano
   (`bot/strategies/generated.py:10-23`, `bot/strategies/generated.py:555-598`,
   `bot/strategies/generated.py:762-773`). Le feature disponibili sono un elenco fisso
   di mattoni su indicatori (`bot/strategies/generated.py:37-156`, sessione oraria
   `bot/strategies/generated.py:183`, contesto di mercato e timeframe superiore
   `bot/strategies/generated.py:272-341`). Le spec sono DATI salvati su Firestore
   (`discovered_strategies/specs`), lette dal bot ogni ora
   (`bot/learning/adaptation.py:401-404`); le esplorative in
   `strategy_registry/esplorative` (`bot/learning/adaptation.py:408-411`).

### Come una strategia viene caricata e abilitata nell'orchestratore

* A ogni candela chiusa l'orchestratore costruisce la lista: tutte le classi
  registrate (`get_all_strategies`, con i parametri ottimizzati per la moneta) +
  le generate validate per quella moneta + le esplorative
  (`bot/orchestrator/orchestrator.py:302-308`). Le strategie generate nascono dalla
  spec in `bot/learning/adaptation.py:483-491`.
* Una coppia (moneta, strategia) opera **solo se è nel registro validato**:
  `is_enabled` richiede `"SIMBOLO|nome"` in `_passed` (`bot/learning/adaptation.py:498-510`,
  riga `bot/learning/adaptation.py:510`), che viene da `strategy_registry/validated`
  (`bot/learning/adaptation.py:284-289`). Senza registro il bot resta fermo
  (`REQUIRE_VALIDATED_PAIRS`, default vero, `bot/config.py:195`).
* Il registro lo scrive **solo il gate**: `scripts/optimize.py` per le strategie in
  codice (`scripts/optimize.py:1493-1500`, `scripts/optimize.py:1549`) e
  `scripts/discover_strategies.py` per le spec (`scripts/discover_strategies.py:1-12`).
  La regola «validata» = `pass_count >= OPTIMIZER_MIN_PASSES` (default 3) e vista da
  meno di 3 giorni (`bot/core/registry.py:31-33`, `bot/core/registry.py:67-85`).
  **Non esiste un percorso per registrare a mano una coppia**: cercato in
  `scripts/optimize.py` (le sole scritture di `strategy_registry/validated` sono il
  reset e il risultato del giro, `scripts/optimize.py:356`, `scripts/optimize.py:454`,
  `scripts/optimize.py:1549`, `scripts/optimize.py:1559`) e in `bot/core/registry.py`.
* Il gate valida le strategie in codice iterando `STRATEGY_REGISTRY`
  (`backtesting/optimizer.py:229`) e **salta quelle senza `param_grid`**
  (`backtesting/optimizer.py:233-235`).
* Filtro di robustezza: una strategia in codice è operabile solo se validata su
  almeno `MIN_COINS_PER_STRATEGY` = **3 monete** distinte; le `gen_*` sono esentate
  (`bot/config.py:603`; `bot/learning/adaptation.py:255-272`).
* Il bot scarica indicatori solo per i timeframe `1m, 5m, 15m, 1h`
  (`bot/config.py:281`; `bot/agents/price_agent.py:151-165`); `timeframe_hours` conosce
  solo `1m…4h` (`bot/config.py:38-42`); l'orchestratore filtra le strategie sul loro
  orologio con una mappa che arriva a `1d` (`bot/orchestrator/orchestrator.py:35`,
  `bot/orchestrator/orchestrator.py:322-326`). Una strategia a 4h o 1d oggi non
  troverebbe i suoi indicatori nello snapshot.

### Risposta: il bot può eseguire una strategia scritta come codice?

**Sì, tecnicamente**: l'interfaccia esiste ed è chiara (una sottoclasse di `Strategy`
con `generate_signal`, registrata con il decoratore e importata). **No, in pratica,
senza un'aggiunta**: la coppia opera solo se passa il gate del bot (3 passaggi del
walk-forward con holdout), su almeno 3 monete, e la ricerca del protocollo non vuole
che il gate del bot riottimizzi o giudichi i candidati (regole congelate al Passo 0,
vault già usato). Serve quindi un percorso che abiliti una coppia «del protocollo»
senza passare dal gate del bot e senza toccare le strategie già operate.

Stima di cosa toccare (solo elenco, nessuna modifica fatta):

1. `bot/strategies/<nome>.py`: la strategia tradotta in codice (classe, `name`,
   `generate_signal`, stop e target); `bot/strategies/__init__.py:10-19`: l'import.
2. Abilitazione senza gate: un documento o un campo del registro «coppie del
   protocollo» letto in `bot/learning/adaptation.py:498-510` (`is_enabled`) e nel
   filtro di robustezza `bot/learning/adaptation.py:255-272`, con i suoi test; oppure,
   più semplice ma più grezzo, `MIN_COINS_PER_STRATEGY=1` nell'ambiente
   (`bot/config.py:603`) e un record del registro scritto con `pass_count` sopra
   soglia — che però il giro del gate riscriverebbe ogni 3 ore
   (`scripts/install_optimizer_timer.sh:64`, `scripts/optimize.py:1549`).
3. Se il timeframe della strategia non è fra `1m, 5m, 15m, 1h`, due casi:
   * **30m o 4h**: `timeframe_hours` e `_TF_SECS` li conoscono già
     (`bot/config.py:42`, `bot/orchestrator/orchestrator.py:35`); mancano solo
     `bot/config.py:281` (`TIMEFRAMES`), `bot/agents/price_agent.py:151-165`
     (snapshot) e `bot/main.py:534` (intervallo di decisione).
   * **2h, 6h, 8h, 12h o 1d**: oltre ai tre file qui sopra, `bot/config.py:42`
     (`timeframe_hours`, che si ferma a 4h) e, tranne che per 1d, `_TF_SECS`
     (`bot/orchestrator/orchestrator.py:35`, che il 1d lo ha già).
   In entrambi i casi va rivisto l'orizzonte di 96 barre
   (`bot/execution/executor.py:180-188`).
4. Se le regole usano dati che il bot non ha (mark price storico, funding a
   settlement, candele oltre le 200 per chiamata `bot/agents/price_agent.py:152`):
   lavoro ulteriore, da stimare sul candidato.
5. Test in `tests/` per ogni punto sopra (cartella non aperta, per regola).

Alternativa: tradurre le regole in una **spec** di `GeneratedStrategy`, se i mattoni
disponibili bastano (`bot/strategies/generated.py:37-156`). Anche la spec però deve
entrare nel registro, e lo scrive solo la discovery: il punto 2 resta.

---

## 5. `backtest_interno`: il motore di backtest del bot

**Esiste**: `backtesting/engine.py`, classe `Backtester` (`backtesting/engine.py:606-629`),
metodo `run_strategy(strategy, symbol, candles)` (`backtesting/engine.py:798-1009`), che
accetta qualunque oggetto `Strategy` (in codice o generata) e restituisce la lista dei
trade simulati `SimTrade` con prezzo d'ingresso e uscita, istante d'ingresso, barre
tenute, motivo d'uscita, MFE e MAE in R (`backtesting/engine.py:489-500`,
`backtesting/engine.py:978-996`). CLI: `python -m backtesting.run`
(`backtesting/run.py:1-11`, `backtesting/run.py:26-40`).

Cosa fa, con i riferimenti:

* **Serie**: solo candele last da `/fapi/v1/klines` (`backtesting/data_loader.py:28`);
  nessuna candela del mark price (cercato `markPriceKlines`, `premiumIndexKlines`:
  zero occorrenze in `backtesting/`).
* **Timeframe**: `--interval`, default `ORCHESTRATOR_TIMEFRAME` (`backtesting/run.py:31`;
  `scripts/optimize.py:317`); il job sulla macchina parte da `2022-01-01`
  (`scripts/install_optimizer_timer.sh:48-49`; `scripts/optimize.py:318`).
* **Segnali solo su barre chiuse** (`backtesting/engine.py:732-743`,
  `bot/agents/price_agent.py:155-165`).
* **Ingresso alla chiusura della barra del segnale** per default
  (`backtesting/engine.py:833`); con `BACKTEST_ENTRY_NEXT_OPEN` (default falso,
  `bot/config.py:667-668`) all'apertura della barra successiva, con stop e target
  traslati (`backtesting/engine.py:846-849`).
* **Stop prima del take profit nella stessa barra** (`backtesting/engine.py:942-952`).
* **Profit-lock** (stop che sale a metà strada verso il target, tiene metà del
  miglior guadagno): `bot/execution/exit_logic.py:21-49`, `bot/config.py:301-303`,
  usato in `backtesting/engine.py:937`.
* **Scale-out** su multipli di R con break-even dopo il primo gradino: percorso
  `backtesting/engine.py:878-930`, ma `SCALE_OUT_ENABLED` è **falso** per default
  (`bot/config.py:314`).
* **Orizzonte**: `HORIZON_BARS = 96` (`backtesting/engine.py:43`, `backtesting/engine.py:873`),
  chiusura forzata alla chiusura della barra.
* **Cooldown** dopo uno stop in perdita, come il bot (`backtesting/engine.py:1006-1008`).
* **Costi e funding**: punto 3 (`backtesting/engine.py:803`, `backtesting/engine.py:972-977`).
* **Dimensione e leva: assenti.** Il rendimento è la variazione di prezzo sul
  nozionale (`backtesting/engine.py:971`, commento a `backtesting/engine.py:495`) e il
  PnL = rendimento × capitale fisso 10.000 (`backtesting/engine.py:982`;
  `backtesting/optimizer.py:106`): nessun rischio per trade, nessuna leva, nessun cap.
* **Liquidazione: non simulata.** Si conta solo, a posteriori, quante volte l'escursione
  avversa avrebbe superato 1/leva − 0,005 per leve 2, 3, 5, 10, 20
  (`backtesting/engine.py:35`, `backtesting/engine.py:485`, `backtesting/engine.py:597-603`).
* **Walk-forward e holdout** (nel gate, sopra il motore): 3 finestre, holdout di 45
  giorni mai visto dalla selezione (`backtesting/optimizer.py:100-131`;
  `bot/config.py:392-396`), soglie del gate (`bot/config.py:379-382`,
  `backtesting/engine.py:377-445`).

**Si può usare per il test di parità del Passo 9?** Sì, per **segnali e trade**
(istante d'ingresso, prezzo d'ingresso, prezzo e motivo d'uscita): basta costruire
la strategia tradotta e chiamare `run_strategy` sulle stesse candele
(`backtesting/engine.py:798`), come fa `scripts/gate_vs_paper.py:215`. Non per i
risultati in R o in denaro: il motore del bot non ha dimensione, leva, liquidazione,
settlement del funding né slippage per fascia, e per default entra alla chiusura
della barra del segnale invece che all'apertura della successiva. Per il confronto
si userà `BACKTEST_ENTRY_NEXT_OPEN=true` (`bot/config.py:667`) e si confronteranno
solo le liste dei trade.

---

## 6. Dati: candele storiche e funding

### Il bot dal vivo

* Base REST `https://fapi.binance.com` (o il testnet se `BINANCE_TESTNET` è vero:
  default **vero** nel codice, `bot/config.py:69`; `bot/agents/price_agent.py:29`; il
  valore sulla macchina è nell'ambiente, non letto).
* Candele: `/fapi/v1/klines`, 200 per chiamata, timeframe `1m, 5m, 15m, 1h`
  (`bot/agents/price_agent.py:96-116`, `bot/agents/price_agent.py:152`; `bot/config.py:281`);
  l'ultima candela (in formazione) esclusa dagli indicatori (`bot/agents/price_agent.py:160-165`).
* Mark price e funding: `/fapi/v1/premiumIndex` (`markPrice`, `lastFundingRate`)
  (`bot/agents/price_agent.py:119-121`, `bot/agents/price_agent.py:194-195`).
* Volume 24h: `/fapi/v1/ticker/24hr` (`bot/agents/price_agent.py:123-125`,
  `bot/agents/price_agent.py:197`); open interest `/fapi/v1/openInterest`
  (`bot/agents/price_agent.py:138-142`); universo `/fapi/v1/exchangeInfo`
  (`bot/agents/price_agent.py:60-71`).
* Stream WebSocket `wss://fstream.binance.com`, `bookTicker` (`bot/agents/price_stream.py:46-47`,
  `bot/config.py:369`).
* Snapshot rinfrescato ogni ciclo (`bot/main.py:1330-1344`); ciclo ogni 30 s
  (`bot/main.py:2397`).

### Il gate (storico)

* Fonte primaria `https://fapi.binance.com/fapi/v1/klines`, paginata a 1.500 candele
  (`backtesting/data_loader.py:28`, `backtesting/data_loader.py:68-80`); ripieghi Bybit e
  OKX (`backtesting/data_loader.py:29-31`, `backtesting/data_loader.py:99`,
  `backtesting/data_loader.py:137`); dati sintetici **spenti** per default
  (`backtesting/data_loader.py:398-405`).
* Periodo: `start` default `2022-01-01`, `end` default oggi
  (`backtesting/data_loader.py:382-389`, `backtesting/data_loader.py:406-407`).
* Cache su disco in `.cache/candles` (variabile `BACKTEST_CACHE_DIR`), riusata ed
  estesa, cancellata dopo 3 giorni (`backtesting/data_loader.py:226-231`,
  `backtesting/data_loader.py:361`, `backtesting/data_loader.py:419-464`).
* Funding: `https://fapi.binance.com/fapi/v1/fundingRate`, ultimi 1.000 settlement,
  media (`backtesting/data_loader.py:29`, `backtesting/data_loader.py:37-55`).
* `data.binance.vision` è usato altrove nel repo per open interest e per l'elenco dei
  simboli storici, **tramite l'origine S3** perché l'hostname non sempre risponde
  (`backtesting/metrics_loader.py:22-23`, `backtesting/metrics_loader.py:45`;
  `scripts/survivorship_report.py:40-41`): è la strada da provare per `fonte_dati` se
  l'host diretto è bloccato (lo era il 6 ott, appendice 2 del protocollo).

---

## 7. Timeframe del bot e orizzonte massimo di una posizione

* Timeframe unico `ORCHESTRATOR_TIMEFRAME`, default **15m** (`bot/config.py:165-169`);
  le strategie generate possono dichiarare il proprio (`bot/strategies/generated.py:566-571`),
  dal 22 set 2026 anche 1h.
* La decisione avviene una volta per candela chiusa, al confine dell'orologio, almeno
  5 s dopo (`bot/main.py:1500-1508`; intervallo `bot/main.py:534`); l'orchestratore
  valuta ogni strategia solo sulle chiusure del suo timeframe
  (`bot/orchestrator/orchestrator.py:313-326`).
* Orizzonte massimo: `EXEC_MAX_HOLD_HOURS` se impostato nell'ambiente, altrimenti
  **96 barre del timeframe della posizione** (24 h a 15m, 96 h a 1h)
  (`bot/execution/executor.py:180-188`, riga `bot/execution/executor.py:185`;
  `bot/execution/executor.py:521-532`); la chiusura d'ufficio è a `bot/execution/executor.py:640-643`
  e `bot/execution/executor.py:674-678`. Stesso numero nel gate (`backtesting/engine.py:43`).
* Cooldown: 4 barre dopo uno stop sulla moneta, 8 barre di panchina per la strategia
  (`bot/config.py:211-217`).

---

## Incoerenze con i valori di partenza del protocollo

1. **Commissione.** Il bot usa 0,08 % round-trip tutto compreso (≈0,04 %/lato, con
   lo slippage dentro) più uno spread per fascia (0,012–0,08 % round-trip)
   (`bot/execution/executor.py:178`; `bot/core/costs.py:13-24`). Il protocollo parte da
   0,05 %/lato taker (0,10 % round-trip) più slippage per fascia 0,01–0,10 %/lato: è
   più prudente del bot. Il percorso live entra con un ordine **limit**
   (`bot/execution/executor.py:364`) ma esce sempre a mercato
   (`bot/execution/executor.py:462`, `bot/execution/executor.py:480`,
   `bot/execution/executor.py:798-800`): contare tutto come taker è prudente ma non
   troppo, perché metà degli ordini lo sono davvero e il paper non modella il maker.
   Da verificare la tabella attuale di Binance.
2. **Funding.** Bot e gate usano un tasso fisso per moneta (all'ingresso nel paper,
   media degli ultimi 1.000 settlement nel gate), continuo in ore/8, sempre su 8 ore
   (`bot/core/costs.py:39`; `backtesting/data_loader.py:37-55`). Il protocollo chiede il
   tasso storico vero a ogni settlement, con l'intervallo vero (8h, 4h, 1h): il motore
   di ricerca sarà diverso dal bot su questo punto, e la differenza va dichiarata al
   Passo 9.
3. **Serie dello stop.** Tre comportamenti diversi: gate = candele last; paper =
   mid bid/ask (o candele 1m last) più il punto del mark; live = default di Binance
   (`CONTRACT_PRICE`, last, perché `workingType` non è passato). Proposta: `serie_stop`
   = last price; la serie delle liquidazioni resta il mark (da verificare sulla
   documentazione di Binance). Nel paper il mark può far scattare uno stop che sul
   last non sarebbe scattato: differenza attesa, da contare al Passo 9.
4. **Dimensione, leva, liquidazione.** Le regole del bot (rischio 1 %, leva 2 con
   tetto 5 e cap di volatilità, cap di nozionale 10 % dell'equity in parità, stop
   massimo 6 %) esistono solo nel bot vivo: il suo backtest non applica né dimensione
   né leva né liquidazione. Il motore di ricerca deve implementarle da sé (sezione 7
   del protocollo) prendendo i numeri dal punto 2, non dal gate.
5. **Modalità di margine.** Non impostata nel codice. Per il prezzo di liquidazione il
   motore di ricerca deve scegliere: proposta **cross** (default del conto Binance, da
   verificare sulla documentazione), segnalando che con cross la liquidazione dipende
   da tutto il conto e il calcolo per singolo trade è un'approssimazione prudente solo
   se si considera il margine della sola posizione (cioè come se fosse isolated). La
   decisione spetta all'utente al Passo 0.
6. **Esecuzione di codice.** Il bot può eseguire codice Python, ma una coppia opera
   solo se è nel registro scritto dal gate del bot, su almeno 3 monete, e con
   timeframe fra quelli che scarica (1m–1h). Per il Passo 9 serve un'aggiunta
   (punto 4): va decisa al Passo 0, come chiede il protocollo.
7. **Timeframe ammessi.** Il protocollo ammette 15m…1d; il bot dal vivo ha
   indicatori solo per 1m, 5m, 15m, 1h (`bot/config.py:281`) e `timeframe_hours`
   arriva a 4h (`bot/config.py:42`). Un candidato a 2h, 4h, 6h, 8h, 12h o 1d richiede
   le modifiche del punto 4.3 prima del paper.
8. **Durata delle posizioni.** Il protocollo la lascia libera; il bot chiude d'ufficio
   dopo 96 barre (`bot/execution/executor.py:185`). Un candidato con posizioni più
   lunghe non si può portare in paper così com'è: o si dichiara l'orizzonte nelle sue
   regole, o si rivede `EXEC_MAX_HOLD_HOURS` (configurazione live: non si tocca senza
   il sì dell'utente).
9. **Momento d'ingresso.** Il gate del bot entra alla chiusura della barra del segnale
   (`backtesting/engine.py:833`); il protocollo all'apertura della successiva. Il paper
   invece entra al prezzo vivo dopo il confine di candela (`bot/main.py:1500-1508`,
   `bot/execution/executor.py:273`), cioè come il protocollo. Per il test di parità si
   userà `BACKTEST_ENTRY_NEXT_OPEN=true`.
10. **Numero massimo di posizioni.** Il tetto di 5 è spento in parità
    (`bot/main.py:1639`), dove conta solo il margine (10 % dell'equity per posizione →
    circa 10 posizioni). Il motore di ricerca prova una moneta alla volta: i limiti di
    portafoglio (direzione, perdita per moneta, correlazione) non entrano nelle
    campagne e vanno dichiarati nei limiti noti (sezione 11).
11. **Fonte dati.** Il bot non usa `data.binance.vision` per le candele ma l'API REST
    `fapi.binance.com`; il repo raggiunge `data.binance.vision` solo via S3
    (`backtesting/metrics_loader.py:45`). Se la rete della sessione blocca l'host
    diretto, l'origine S3 è la prima alternativa da provare; se bloccata anche quella,
    STOP come da appendice 2 del protocollo.
12. **Riempimento intra-barra.** Coerente: stop prima del target nel gate
    (`backtesting/engine.py:942-952`) e nel paper (`bot/execution/executor.py:602-605`).
    Nessuna incoerenza.
