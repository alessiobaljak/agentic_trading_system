# FASE 0 — AUDIT COMPLETO DEL CODICE ESISTENTE
_Prodotto il 2026-08-11 · 52 moduli Python + 23 componenti dashboard · 295 test verdi_

> Questo documento risponde alla Fase 0 del prompt di upgrade v3. Non modifica
> codice. Affianca `docs/audit.md` (audit precedente, 2026-08-04) senza sostituirlo:
> lì c'è lo stato **per logica**, qui lo stato **per file** più i quattro inventari
> richiesti e la gap analysis.

---

## 0. Premessa — tre cose da sapere prima di leggere

**(a) Molto di ciò che il prompt chiede di aggiungere esiste già.** Il sistema ha
mesi di sviluppo alle spalle: walk-forward con holdout, funding storico reale,
spread per fascia di liquidità, kill switch, circuit breaker, versioning dei pesi,
gate di validazione. Nella gap analysis (§5) distinguo *mancante* da *presente ma
diverso da come il prompt lo descrive* — sono due azioni molto diverse.

**(b) La disparità backtest↔paper è già stata misurata, e la causa NON è quella
che il prompt ipotizza.** Il prompt elenca slippage, funding, timing, logica di
chiusura. Abbiamo verificato riga per riga che questi sono **moduli condivisi**
identici fra gate e paper (`bot/core/costs.py`, `bot/execution/exit_logic.py`,
orizzonte 96 barre in entrambi). La causa misurata è un'altra: **selezione su una
statistica fragile**. Dettaglio in §5.1.

**(c) La Fase 1.1 come specificata oggi non è eseguibile.** Chiede di confrontare
gli ultimi 30 giorni di trade paper con il backtest dello stesso periodo. Ma:
- i 144 trade sono stati **cancellati** ieri con `scripts/reset_paper.py` (esiste
  un export in `trades_backup_20260811.json` sulla VPS);
- il registro ha **0 coppie validate**, quindi non esiste una strategia da
  ri-backtestare su quel periodo;
- un backfill di validazione è **in corso adesso** sulla VPS.

Serve decidere come procedere: vedi §6.

---

## 1. Schede per file

Legenda stato: **✅ funzionante** · **⚠️ parziale / con riserve** · **🔴 difetto** ·
**⛔ non usato in produzione**

### 1.1 `bot/core/` — modelli, dati condivisi

| File | Funzione | Stato | Dipendenze | Problemi rilevati |
|---|---|---|---|---|
| `config.py` (435) | Tutte le impostazioni da env + `.env`; hard cap separati | ✅ | dotenv | `load_dotenv()` bypassato in test via `TRADING_BOT_TEST_MODE` (fix di ieri). Ordine di lettura a *def-time* della classe: cambiare env dopo l'import non ha effetto — trappola nota, documentata in `conftest.py` |
| `models.py` (282) | `Candle`, `AssetSnapshot`, `Position`, `ClosedTrade`, `EffectiveRiskParams`, enum | ✅ | pydantic | `ClosedTrade.pnl_pct` = ritorno **sul margine** (con leva); `SimTrade.pnl_pct` = variazione **di prezzo** (senza leva). Stesso nome, semantica diversa: fonte di errori di lettura |
| `indicators.py` (202) | `compute_indicator_frame` + `snapshot_from_row`: EMA/RSI/ATR/MACD/BB/VWAP/ADX/Stoch | ✅ | pandas | **È già la funzione unica richiesta dalla Fase 1.3**: usata da backtest, paper e live. Usa `shift(1)` dove serve; nessun look-ahead trovato |
| `costs.py` (39) | `liquidity_spread` (4 fasce) + `funding_fraction` con segno | ✅ | — | Spread **misurati** da `measure_spreads.py`. Modulo condiviso gate↔live: è ciò che garantisce la parità sui costi |
| `firebase_client.py` (230) | Wrapper Firestore+RTDB; fallback in-memory; `encode/decode_pairs` | ✅ | firebase-admin | Fallback silenzioso su store in-memory se manca il service account: comodo, ma in produzione un errore di credenziali diventerebbe "tutto funziona e non salva niente" |

### 1.2 `bot/agents/` — acquisizione dati

| File | Funzione | Stato | Dipendenze | Problemi rilevati |
|---|---|---|---|---|
| `price_agent.py` (174) | Klines/mark price REST da Binance Futures; costruisce `AssetSnapshot` | ✅ | requests, indicators | Retry su 429 + pacing presenti |
| `price_stream.py` (366) | WebSocket `bookTicker`, percorso zigzag ordinato, watchdog, `take()` | ✅ | websocket-client | Dispatch su `"e"` (non su `"a"`, che in bookTicker è l'ask). Fallback a candele REST se lo stream è muto |
| `market_scanner.py` (142) | Universo + filtro liquidità + `select_assets` | ⚠️ | price_agent | Lo scoring è volume-based semplice. La Fase 3.3 chiede scoring multi-fattore: **mancante** |
| `regime_detector.py` (50) | 4 regimi da EMA/MACD/ATR di BTC + Fear&Greed | ⚠️ | price_agent, onchain | Classificazione **binaria senza confidence**. La Fase 3.2 chiede confidence + durata + probabilità di cambio: **mancante** |
| `onchain_agent.py` (86) | Fear&Greed (alternative.me), funding, long/short ratio | ✅ | requests | Coinglass richiede chiave; degrada a `None` senza errori |
| `sentiment_agent.py` | CoinGecko + LunarCrush | ⚠️ | requests | Usato solo per **osservabilità** in dashboard; non entra in nessuna decisione né nel gate |

### 1.3 `bot/strategies/` — 9 strategie + generatore

| File | Funzione | Stato | Problemi rilevati |
|---|---|---|---|
| `base.py` (139) | `Strategy` ASTRATTA, `@register_strategy`, `get_all_strategies`, `_atr_stop_target` | ✅ | `param_grid` NON contiene `atr_mult_stop` per le strategie base: lo stop resta il default di classe, mai ottimizzato |
| `trend_following` / `mean_reversion` / `breakout` / `vwap_reversion` / `momentum` / `momentum_cross_asset` / `liquidity_grab` / `grid_trading` / `funding_arbitrage` | Le 9 strategie classiche | ✅ | Tutte registrate e raggiungibili. Ognuna dichiara `active_regimes` |
| `generated.py` (263) | `GeneratedStrategy`: esegue spec dichiarative; `FEATURE_LIBRARY`; `spec_id` | ✅ | **Nessun `param_grid`** → per le generate la grid search non gira affatto (la scala TP è scelta da un passo dedicato in `discover_strategies`) |
| `generator.py` (139) | `generate_specs(n)` casuale + `mutate` | 🔴 | **Combina feature col dado.** Nessuna candidata ha una ragione per funzionare → fra migliaia testate sopravvivono le fortunate. È la radice del problema misurato (§5.1) |

### 1.4 `bot/execution/` — esecuzione

| File | Funzione | Stato | Problemi rilevati |
|---|---|---|---|
| `executor.py` (773) | Ciclo di vita posizione: apertura, scale-out, break-even, trailing, orizzonte 96 barre, persistenza | ✅ | `_await_fill`/`_flatten_residual` per il live. **Non ha notifier**: i TP parziali non mandano Telegram, solo la chiusura finale |
| `exit_logic.py` (227) | `scale_ladder`, `scale_fills`, `locked_stop`, `mfe_in_r`, `effective_param_grid` | ✅ | Primitivi CONDIVISI gate↔paper: è ciò che garantisce la parità sulle uscite |
| `notifier.py` (66) | Telegram: aperture, chiusure, kill switch, offline | ✅ | Fail-soft: se l'invio fallisce logga e prosegue |

### 1.5 `bot/risk/` — rischio

| File | Funzione | Stato | Problemi rilevati |
|---|---|---|---|
| `hard_limits.py` (57) | `MAX_LEVERAGE=5`, `MAX_RISK_PER_TRADE=3%`, cap per volatilità | ✅ | Non configurabili da env né da LLM: corretto |
| `risk_manager.py` (217) | Leva/size effettive = min(utente×alloc, cap volatilità, hard cap); SL/TP dalla strategia | 🔴 | **Il cap per-posizione al 10% morde su ogni trade**: il sizing non è basato sul rischio ma è un nozionale fisso (~$192). `risk_per_trade` è di fatto inerte. Inoltre con leva base 2, `round()` bancario rende **3x irraggiungibile** |
| `circuit_breakers.py` | Perdita giornaliera, stop consecutivi, perdita settimanale | ✅ | Stato persistito su `/risk_state` |
| `correlation_guard.py` (65) | Correlazione rolling 24h fra posizioni aperte | ✅ | Era codice morto, ora collegato in `main._correlation_blocks` |

### 1.6 `bot/learning/` — apprendimento

| File | Funzione | Stato | Problemi rilevati |
|---|---|---|---|
| `adaptation.py` (305) | Carica registro/pesi/spec; `allocation()`; `is_enabled()`; gate `ready` | ✅ | Fail-safe corretto: senza dati di ottimizzazione resta FLAT |
| `metrics.py` (238) | `compute_weights` strategia×regime su finestra 30g | ⚠️ | **Manca il filtro anti-anomalie della Fase 3.1** (eventi macro, slippage estremo, durata < 60s, WS disconnesso). Manca lo smoothing esponenziale e il minimo di 50 trade |
| `learning_loop.py` | Job notturno: pesi + memory report | ✅ | Stessa aritmetica del refresh orario |
| `trade_logger.py` (39) | Scrive `trades` su Firestore; WAL per i falliti | ✅ | **Mancano i 12 campi di costo della Fase 2.5** (slippage atteso vs eseguito, commissioni per lato, funding pagato) |
| `drift.py` (176) | Paper falsifica il gate: verdetti coppia/strategia/globale | ✅ | Il livello globale ora frena davvero (fix di ieri). Soglie: 8/20/40 trade |
| `calibration.py` | La confidenza predice l'esito? Pearson + monotonicità terzili | ✅ | Ultimo verdetto: `ok`, correlazione 0.125 su 133 trade |

### 1.7 `bot/ai/` — livello AI (nuovo, 2026-08-11)

| File | Funzione | Stato | Problemi rilevati |
|---|---|---|---|
| `client.py` (106) | Unico punto di contatto col modello; fail-open; estrazione JSON bilanciata | ✅ | Senza chiave torna sempre `None`: il sistema si comporta come prima |
| `analyst.py` (168) | Post-mortem su digest aggregato | ✅ | Non tocca registro né posizioni |
| `hypotheses.py` (152) | Spec con meccanismo dichiarato; validazione contro vocabolario chiuso | ✅ | Sostituisce una quota di candidate casuali, non si aggiunge |
| `universe_filter.py` (93) | Scarta coin su cui non vale la pena validare; guardia anti-svuotamento | ✅ | Fail-open |

### 1.8 `bot/orchestrator/`

| File | Funzione | Stato | Problemi rilevati |
|---|---|---|---|
| `orchestrator.py` (265) | Raccoglie segnali, applica pesi, `decide()` (LLM) e `decide_all()` (parità) | ⚠️ | **Con `BACKTEST_PARITY=true` il ramo LLM non viene MAI raggiunto** (`main.py:502`). È il motivo per cui il bot non consuma token |
| `prompt.py` (77) | System prompt + input strutturato | ⚠️ | Manca tutto l'arricchimento della Fase 3.4 (RAG su situazioni simili, performance recente, stato rischio, alert attivi) |

### 1.9 `bot/main.py` (908) — il loop

| Aspetto | Stato | Note |
|---|---|---|
| Loop principale, heartbeat, kill switch, scan, decisione a candela chiusa | ✅ | Decisione allineata al confine dell'orologio, su barre chiuse |
| `_wick_range`, `_price_path`, replay ordinato | ✅ | Parità con le ombre del gate |
| Guardie di portafoglio (correlazione, rischio direzionale) | ✅ | |
| Learning event-driven + orario, drift, calibrazione | ✅ | Ognuno in un `try` proprio: una diagnostica non blocca il learning |
| **File da 908 righe** | ⚠️ | Il singolo punto di maggiore complessità del sistema |

### 1.10 `backtesting/`

| File | Funzione | Stato | Problemi rilevati |
|---|---|---|---|
| `engine.py` (617) | Simulazione: scale-out, ombre, costi, funding, `mfe_r`, `passes_gate`, `pf_without_top` | ⚠️ | **Entry al `close` della candela di segnale** (`entry = snap.price`), non all'open di T+1. Nessuna posizione sovrapposta (`i = j + 1`). `max_drawdown` su trade **sequenziali** → sottostima il DD reale di un portafoglio con 9-12 posizioni |
| `optimizer.py` (230) | Walk-forward, holdout, score con recency, `_holdout_check` | ✅ | Holdout rolling 45g. Finestre: train/test contigue, `n_windows+1` blocchi |
| `data_loader.py` (365) | Klines da Binance/Bybit/OKX + funding storico reale + cache | ✅ | Funding **storico reale** già usato (`/fapi/v1/fundingRate`), non una media |
| `parallel.py` (43) | `parallel_map` multiprocess con initializer | ✅ | |
| `run.py` (84) | Entry point backtest | ✅ | |

### 1.11 `scripts/` (28 file) — operazioni e diagnostica

Raggruppati per funzione, tutti ✅ salvo nota:

- **Gate**: `optimize.py` (463), `discover_strategies.py` (461), `rebuild_gate.sh`,
  `backfill_passes.sh`, `reset-optimizer`
- **Diagnostica**: `gate_vs_paper.py`, `mfe_report.py`, `trade_stats.py`,
  `confidence_analysis.py`, `losing_strategies.py`, `edge_stability.py`,
  `signal_frequency.py`, `survivorship_report.py`, `measure_spreads.py`
- **Operazioni**: `reset_paper.py`, `state_snapshot.py`, `monitor.py`,
  `maintenance.py`, `setup_vps.sh`, `install_optimizer_timer.sh`
- **Connettività**: `connectivity_check.py`, `verify_keys.py`, `diagnose_ws.py`,
  `check_price_stream.py`
- **AI**: `ai_analyst.py`

⚠️ `revalidate_costs.py`, `ab_scale_out.py`, `promote_scale_out.sh`,
`rebuild_clean.sh`, `accelerate_validation.sh`, `consolidate_now.sh`: script di
migrazioni **già eseguite**. Funzionanti ma storici — candidati alla rimozione.

### 1.12 `dashboard/` — 23 componenti React/Next

Tutti funzionanti. Presenti: BotStatus, Positions, EquityCurve, ClosedTrades,
OptimizedStrategies, StrategyWeights, Heatmap, RiskControl, KillSwitch,
DecisionStatus, SentimentAnalysis, TrailingLearning, LearningSummary, Insights,
DailySnapshot, CandleChart, PositionDetail/Metrics/Chart, TopVitals, AuthGate,
DashboardShell, OperativitaTab.

**Mancano** i pannelli della Fase 3.5: Regime Intelligence, Asset Scoring,
Learning Evolution (con rollback), Costi Operativi, Reconciler Status,
Orchestratore. Il Risk Control esiste già.

---

## 2. Mappa delle dipendenze

```
                        ┌──────────────┐
                        │ bot/main.py  │  loop, heartbeat, kill switch
                        └──────┬───────┘
        ┌──────────────┬───────┼────────┬──────────────┬─────────────┐
        ▼              ▼       ▼        ▼              ▼             ▼
   agents/        orchestrator/  risk/   execution/   learning/    core/
   price_agent    orchestrator   risk_   executor     adaptation   firebase
   price_stream   prompt         manager exit_logic   metrics      models
   market_scanner                hard_   notifier     drift        costs
   regime_det.                   limits               calibration  indicators
   onchain                       circuit              trade_logger
   sentiment                     correlation          learning_loop
                                                            │
                          ┌─────────────────────────────────┘
                          ▼
                     bot/ai/ (client → analyst · hypotheses · universe_filter)

   backtesting/engine ──┬── core/indicators   (STESSA funzione del live)
                        ├── core/costs        (STESSO modello di costo)
                        └── execution/exit_logic (STESSI primitivi di uscita)
                              ▲
                              └── è QUI che vive la parità gate↔paper

   scripts/optimize ─┐
   scripts/discover ─┴─→ backtesting/optimizer → engine → Firestore(strategy_registry)
                                                              │
                                                              ▼
                                                    adaptation.load_params()
```

**Il punto architetturale che conta**: gate e paper non hanno due implementazioni
da tenere allineate. Condividono **tre moduli** (`indicators`, `costs`,
`exit_logic`). La Fase 1.3 del prompt — creare una funzione indicatori unica — è
**già soddisfatta** da `bot/core/indicators.py`.

---

## 3. Inventari

### 3.1 Chiamate API esterne

| Servizio | Endpoint | File:riga |
|---|---|---|
| Binance Futures | `/fapi/v1/klines` | `data_loader.py:28`, `price_agent.py:29`, `state_snapshot.py:156`, `connectivity_check.py:96` |
| Binance Futures | `/fapi/v1/fundingRate` | `data_loader.py:29` |
| Binance Futures | ordini/posizioni/balance | `executor.py` (solo `dry_run=False`) |
| Binance Futures | WebSocket `bookTicker` | `price_stream.py` |
| Binance Data | `globalLongShortAccountRatio` | `onchain_agent.py:21`, `connectivity_check.py:103` |
| Binance Vision (S3) | archivi storici | `survivorship_report.py:40` |
| Bybit | `/v5/market/kline` | `data_loader.py:30` (fallback) |
| OKX | `/market/history-candles` | `data_loader.py:31` (fallback) |
| CoinMetrics | `timeseries/asset-metrics` | `data_loader.py:32` |
| Alternative.me | `/fng/` (Fear & Greed) | `onchain_agent.py:19` |
| Coinglass | `/api/futures/...` | `onchain_agent.py:22` |
| CoinGecko | `/api/v3` | `sentiment_agent.py:22` |
| LunarCrush | `/api4/public` | `sentiment_agent.py:23` |
| NewsAPI | `/v2/everything` | solo `verify_keys`/`connectivity_check` |
| Telegram | `sendMessage` | `notifier.py:24`, `discover_strategies.py:290` |
| Anthropic | Messages API | `ai/client.py`, `orchestrator.py:225` |
| Firebase | Firestore + RTDB | `firebase_client.py` |

### 3.2 Stato condiviso (dove si scrive / dove si legge)

**Realtime DB** — stato operativo, alta frequenza:

| Path | Scritto da | Letto da |
|---|---|---|
| `/bot_status` (+`/heartbeat`) | `main` (ogni iterazione) | `monitor`, `state_snapshot`, dashboard |
| `/positions/{symbol}` | `executor` (ogni update) | `executor` (restore al riavvio), dashboard |
| `/account/equity`, `/starting_equity` | `main.account_equity` | dashboard, `state_snapshot` |
| `/risk_state` | `main._persist_risk_state` | `circuit_breakers` al riavvio |
| `/adapt_state` | `main._save_adapt_state` | `main` al riavvio (cooldown) |
| `/commands/kill_switch` | dashboard, `reset_paper` | `main` (ogni ciclo) |
| `/commands/close_position` | dashboard | `main` |
| `/commands/maintenance` | dashboard | `main` |
| `/decision_status` | `main._publish_decision_status` | dashboard |
| `/unlogged_trades/{id}` | `trade_logger` (WAL) | `main` al riavvio |
| `/trailing_keep` | `main` (B2) | `executor` |

**Firestore** — stato durevole:

| Collection/doc | Scritto da | Letto da |
|---|---|---|
| `strategy_registry/validated` | `optimize`, `discover` | `adaptation` (ogni ora), dashboard, `drift` |
| `discovered_strategies/specs` | `discover` | `adaptation.load_generated` |
| `strategy_params/current` | `optimize` | `adaptation` (fallback) |
| `strategy_weights/current` | `metrics`/`learning_loop`/`main` | `adaptation` |
| `trades` | `trade_logger` | learning, drift, calibrazione, dashboard, analista |
| `memory/{30,7,...}` | `learning_loop` | orchestratore |
| `drift/current` | `main._publish_drift` | `adaptation` (freno), `optimize` (purge) |
| `calibration/current` | `main._publish_calibration` | `adaptation` (trust) |
| `insights/{week}` | `learning_loop` | dashboard |
| `ai_reports/{latest,data}` | `ai_analyst` | (dashboard: da fare) |
| `optimize_shards`, `discover_shards` | shard paralleli | passo `--merge` |

**🔴 Race condition potenziale identificata**: `strategy_registry/validated` è
scritto da `optimize` **e** da `discover` (che preserva i campi di copertura
dell'altro) e letto da `adaptation` ogni ora. Se le due passate girano insieme,
l'ultima scrittura vince. Mitigato oggi dal fatto che girano in sequenza nella
stessa unit systemd, **non** da un lock.

### 3.3 Job schedulati

| Job | Dove | Frequenza | Cosa fa |
|---|---|---|---|
| `trading-bot.service` | systemd VPS | loop continuo | Il bot |
| `trading-optimizer.timer` | systemd VPS | 00/08/16 UTC | `optimize` + `discover_strategies` |
| `bot-monitoring` | GitHub Actions | `*/15 * * * *` | Heartbeat → alert Telegram |
| `state-snapshot` | GitHub Actions | `15 */2 * * *` | Committa `docs/state.md` |
| `nightly-learning-loop` | GitHub Actions | `0 2 * * *` | Pesi + memory report |
| `strategy-optimizer` | GitHub Actions | **disabilitato** (cron commentato) | |
| `strategy-discovery` | GitHub Actions | **disabilitato** | |
| `tests`, `connectivity-check`, `backtest`, `reset-optimizer` | GitHub Actions | manuali/push | |
| Loop interni | `main.py` | scan 4h · regime 60min · registro 60min · pesi 60min + a ogni trade chiuso · decisione a ogni candela chiusa | |

⚠️ GitHub Actions è **inaffidabile** per questo uso: misurato che il cron `*/15`
produce ~10 esecuzioni al giorno invece di 96, e il 6 agosto tre run sono state
accodate e cancellate senza mai ricevere un runner (0 ms fatturati).

---

## 4. Gap analysis — ordinata per criticità

### 🔴 CRITICO 1 — Il generatore di strategie è una lotteria
`generator.py` combina indicatori a caso; il gate ne valuta ~1464 per passata e
promuove i migliori. Con quei numeri **~4 strategie prive di edge superano t=2.8
per puro caso a ogni passata**. È la causa misurata della disparità: PF 1.5 nel
gate, 0.46 nel paper su 142 trade.
*Mitigazione parziale già in campo*: `bot/ai/hypotheses.py` (spec motivate),
`pf_without_top` (robustezza), storia minima 365g, pass onesto 168h.

### 🔴 CRITICO 2 — Il sizing non è basato sul rischio
Il cap per-posizione al 10% morde su **ogni** trade: il nozionale è fisso (~$192),
`risk_per_trade` è inerte e il rischio in dollari oscilla con la volatilità.
Inoltre con leva base 2 il gradino 3x è irraggiungibile per l'arrotondamento
bancario di `round(2.5) == 2`.

### 🔴 CRITICO 3 — Nessun reconciler (Fase 2.1)
Non esiste. Oggi è innocuo perché `DRY_RUN=true`, ma è **bloccante per il live**:
senza confronto con `/fapi/v2/positionRisk` una posizione senza SL su Binance non
verrebbe mai rilevata.

### 🔴 CRITICO 4 — Il drawdown del gate sottostima quello reale
`max_drawdown` somma i trade **in sequenza**; il paper ne tiene 9-12 aperti
insieme su coin correlate. `GATE_MIN_RECOVERY=2.0` è calcolato su un denominatore
strutturalmente ottimista.

### ⚠️ IMPORTANTE 5 — Gestione errori Binance non strutturata (Fase 2.2)
C'è retry su 429 e pacing, ma non la tassonomia RETRY/STOP/CRITICAL. Rilevante
solo per il live.

### ⚠️ IMPORTANTE 6 — Learning senza filtro anti-anomalie (Fase 3.1)
`compute_weights` usa tutti i trade della finestra. Mancano: esclusione eventi
macro, slippage anomalo, durata < 60s, periodi di WS disconnesso; manca lo
smoothing esponenziale (α=0.3), il minimo di 50 trade e il safety check sul 40%.
*Presente invece*: versioning e hard limit sui pesi.

### ⚠️ IMPORTANTE 7 — Costi reali non tracciati (Fase 2.5)
Mancano i 12 campi su `ClosedTrade`. In `DRY_RUN` sarebbero **stimati**, non
misurati: hanno senso pieno solo in live.

### ⚠️ IMPORTANTE 8 — Kill switch a un livello solo (Fase 2.4)
Esiste ed è affidabile (letto da RTDB a ogni ciclo, dashboard scrive su Firebase
— l'architettura richiesta dal prompt è già quella), ma è **binario**. Mancano
PAUSE e STOP-AND-PROTECT.

### ⚠️ IMPORTANTE 9 — Regime detector senza confidence (Fase 3.2)
Quattro etichette secche. Manca confidence, durata, probabilità di cambio,
segnali di supporto/conflitto.

### ⚠️ IMPORTANTE 10 — Asset selector senza scoring multi-fattore (Fase 3.3)
Oggi l'universo live = coin validate dal gate; il filtro è la liquidità. Manca lo
scoring a 6 fattori e la blacklist temporanea.

### 🟡 MINORE 11 — LLM scollegato (Fase 3.4)
Il ramo esiste ma `BACKTEST_PARITY=true` non lo raggiunge mai. **Attenzione**:
collegarlo romperebbe la parità gate↔paper, che è l'unica cosa che oggi funziona
con precisione. Va discusso, non fatto d'ufficio.

### 🟡 MINORE 12 — Entry al close di T invece che all'open di T+1
Il gate entra al `close` della candela di segnale; il live entra al mark price
5-35 secondi dopo. Su crypto (mercato continuo) open(T+1) ≈ close(T), quindi
l'effetto è piccolo — ma **è reale e misurabile**, e va quantificato prima di
decidere se correggerlo.

### 🟡 MINORE 13 — Pannelli dashboard mancanti (Fase 3.5)
Sei pannelli su sette da aggiungere; Risk Control già presente.

### 🟡 MINORE 14 — Race condition sul registro
`optimize` e `discover` scrivono lo stesso documento senza lock.

### 🟡 MINORE 15 — Script di migrazione storici
Sei script relativi a migrazioni già completate.

---

## 5. Note su due punti in cui il prompt non combacia col codice

### 5.1 La causa della disparità è già misurata, e non è nell'elenco del prompt

Il prompt elenca sei cause da cercare. Verificate una per una:

| Causa ipotizzata | Verifica | Esito |
|---|---|---|
| Look-ahead negli indicatori | `shift(1)` usato, candela in formazione esclusa | ✅ non presente |
| Timing di esecuzione | close(T) vs mark a T+5..35s | ⚠️ piccolo, da quantificare |
| Slippage hardcodato | modulo `costs.py` **condiviso** | ✅ identico nei due |
| Funding | storico reale in entrambi | ✅ identico |
| Logica di chiusura | `exit_logic.py` **condiviso**, orizzonte 96 barre in entrambi | ✅ identico |
| Candele mancanti | fallback REST + backfill | ✅ gestito |

La causa **misurata** è invece: il gate promette PF 1.5, e quel PF poggia su una
coda sottilissima. Su `BIRBUSDT|gen_472f85b8`: holdout di 94 trade, +29.5%; **7
trade su 94 producevano tutto il profitto** e senza quelli gli altri 87 perdevano
il 22.6%. Selezionando il meglio fra 1464 candidate su una metrica che dipende da
7 osservazioni, si seleziona la coda più fortunata — che in produzione regredisce.
Nel paper: ≥3R il 7% contro il 16% atteso, ≥5R l'1% contro il 7%.

**Implicazione per la Fase 1**: non c'è una disparità di esecuzione da chiudere
sotto lo 0.15%. C'è un problema di **validazione statistica**. Le contromisure
sono già in campo da ieri (robustezza, storia, pass onesto, PF coerente con la
scala); il backfill in corso è il primo test.

### 5.2 Cosa il prompt chiede di creare e che esiste già

| Richiesta | Dove esiste |
|---|---|
| `/bot/indicators/core.py` con funzione unica (1.3) | `bot/core/indicators.py`, già condiviso dai tre contesti |
| Walk-forward con train/test/step (Fase 4) | `backtesting/optimizer.py` |
| Funding storico reale da `/fapi/v1/fundingRate` (Fase 4) | `backtesting/data_loader.py:29` |
| Spread differenziato per liquidità (Fase 4) | `bot/core/costs.py`, valori **misurati** |
| Minimum trade count con warning (Fase 4) | `GATE_MIN_TRADES=30` |
| Gate di validazione semaforo (Fase 4) | `passes_gate` + `ready` (criteri diversi ma stessa funzione) |
| Kill switch via Firebase, non comunicazione diretta (2.4) | già così |
| Versioning e hard limit dei pesi (3.1) | `metrics.py` |
| Test suite (5.1) | 295 test verdi, inclusi look-ahead, wick parity, kill switch, drift |

---

## 6. Blocco da risolvere prima della Fase 1

La Fase 1.1 chiede il confronto trade-per-trade fra paper e backtest sugli stessi
30 giorni. **Oggi non è eseguibile**: i 144 trade sono stati cancellati ieri (c'è
l'export `trades_backup_20260811.json` sulla VPS), il registro ha 0 coppie
validate e un backfill è in corso.

Tre strade possibili:

**A. Ricostruire il confronto dal backup.** I 144 trade esportati hanno symbol,
strategy, prezzi, `mfe_r` ed exit reason. Si può reimportare in memoria e girare
`gate_vs_paper` su ogni coppia. Limite: le coppie sono state purgate, quindi il
"backtest dello stesso periodo" va rieseguito da zero per ciascuna.

**B. Aspettare il backfill e misurare la disparità sul registro nuovo.** Più
pulito metodologicamente — confronti ciò che è validato coi criteri attuali — ma
richiede giorni di paper per avere un campione.

**C. Saltare la 1.1 e prendere per buona la diagnosi già misurata** (§5.1),
passando direttamente alle contromisure delle Fasi 2 e 3.

La mia raccomandazione è **A + B insieme**: A subito (costa poche ore di calcolo
e usa dati che altrimenti restano in un file), B come verifica quando il paper
avrà accumulato trade sul registro nuovo.

---

## 7. Ordine che proporrei, diverso da quello del prompt

Il prompt ordina 1 → 2 → 3 → 4 → 5. Propongo una variante, motivata:

1. **Fase 1 rivista** — quantificare l'entry timing (§ gap 12) e chiudere il
   confronto con la strada A. Non "portare la disparità sotto lo 0.15%", che è un
   obiettivo mal posto per un problema di selezione.
2. **Gap CRITICO 2** (sizing) — è l'unico difetto che degrada **ogni singolo
   trade** in paper, oggi, e si corregge in poche righe.
3. **Gap CRITICO 4** (drawdown di portafoglio nel gate) — rende onesto il
   criterio di continuità.
4. **Fase 3.1** (learning robusto) e **3.2** (regime con confidence).
5. **Fase 2.1/2.2/2.3** (reconciler, errori, WS) — **prima del live**, non prima
   del paper: in `DRY_RUN` non cambiano nulla.
6. **Fase 3.3** (asset scoring), **3.5** (dashboard).
7. **Fase 3.4** (LLM nell'orchestratore) — solo dopo aver deciso cosa fare della
   parità.

Se preferisci l'ordine originale del prompt lo seguo: è una tua scelta, non un
vincolo tecnico. Volevo solo che vedessi il costo/beneficio prima di decidere.

---

_Fine Fase 0. In attesa di conferma prima di procedere._
