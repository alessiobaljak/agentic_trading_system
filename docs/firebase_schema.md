# Schema Firebase

Il sistema usa **Firestore** (storia/memoria queryabile) e **Realtime Database**
(stato live a bassa latenza). Questo documento è il contratto condiviso tra bot
(`bot/core/firebase_client.py`) e dashboard.

## Firestore

### `trades/{trade_id}`
Record completo di un trade chiuso (modello `ClosedTrade`). Campi principali:
`trade_id, symbol, strategy, direction, entry_time, exit_time, entry_price,
exit_price, size, notional, leverage, pnl, pnl_pct, slippage, exit_reason,
regime_at_entry, indicators_at_entry{tf:…}, sentiment_at_entry, fear_greed_at_entry,
funding_at_entry, confidence_at_entry`. Più i derivati `duration_seconds,
hour_bucket, is_win, exit_ts` (ordinamento).

### `memory/{lookback}`  (es. `memory/30`, `memory/60`, `memory/90`)
`MemoryReport` prodotto dal learning loop:
`generated_at, lookback_days, total_trades, overall_win_rate,
win_rate_by_strategy{}, win_rate_by_strategy_regime{"strategy|regime"},
avg_rr_by_strategy{}, pnl_by_asset{}, win_rate_by_hour{},
worst_drawdown_conditions[], confidence_outcome_correlation, weights[], narrative`.
La dashboard usa `memory/30` per la heatmap e gli insight.

### `strategy_weights/current`
`{ weights: [ {strategy, regime, weight(0..1), win_rate, avg_rr, sample_size} ] }`.
Letto dall'`AdaptationEngine` per aggiustare la confidenza dell'orchestratore.

### `user_risk_settings/current`
Parametri **regolabili dall'utente** dalla dashboard:
`{ leverage, risk_per_trade(frazione), updated_at, updated_by }`.
Il bot lo rilegge **prima di ogni nuovo trade**. Gli hard cap (5x/3%) NON stanno
qui: vengono applicati dal `RiskManager` lato bot.

### `insights/{week_id}`  (es. `insights/2026-W23`)
Memoria a lungo termine (RAG): `{ week_id, narrative, overall_win_rate,
total_trades, created_at }`.

### `dashboard/controllo` e `dashboard/gate`  (dal 25 set 2026)
Il **controllo orario** (scritto dal bot ogni ora; ripiego GitHub snapshot e ops
`controllo`) e il **documento del gate** (scritto dalla discovery a ogni giro:
`stato` in_corso/finito/errore, giro, registro, cervello, strategie operate per
coppia). Specchi RTDB `/controllo` e `/gate` per la dashboard. Schema completo, campo
per campo, in `docs/controllo_schema.md`.

### `ai_spesa/{YYYY-MM-DD}`  (dal 29 set 2026, giorno in ora italiana)
La spesa AI **misurata**: ogni chiamata al modello (bot, discovery, runner GitHub,
comandi ops tranne il ping di `ai-stato`) somma qui, con `Increment` atomico e
`merge` (una scrittura, zero letture), i token restituiti dall'API:
`{ ragioni: {etichetta: {n, in, out, cache_w, cache_r, stop: {motivo: n},
modelli: {modello: n}}}, modelli: {modello: n}, ore: {HH: n}, aggiornato_at }`.
I dollari non si salvano: li calcola `scripts/ai_status.py` (voce ops `ai-stato`)
coi prezzi `AI_PREZZO_*` di `bot/config.py`. Codice in `bot/ai/spesa.py`.

## Realtime Database

### `/learning_giorni/{YYYY-MM-DD}` e `/learning_indice/{YYYY-MM-DD}`  (dal 29 set 2026)
La **foto del giorno del learning**, scritta dal bot alla prima pubblicazione del
controllo di ogni giorno italiano (`bot/main.py::foto_learning_giorno`, impronta di
`bot/learning/apprendimento.py::impronta_giorno`): per ogni validata keep, scala,
break-even e declassata; pesi strategia×regime; cooldown; freno globale; ipotesi
attive; esplorative attive; verdetti trailing e proposta del paper. L'indice dice
l'ora della foto. Si tengono 35 giorni. La legge `scripts/controllo.py` (voce ops
`controllo`) per dire cosa è cambiato ieri e stanotte.

### `/bot_status`
`{ state, regime, dry_run, updated_at, heartbeat, avviato_at, errori_ciclo_1h,
btc_close, price_stream, fear_greed }`. La dashboard mostra lo stato e il monitoring
usa `heartbeat` per l'alert "bot offline" (dal 25 set il battito è anche nel dict
riscritto ogni ora da `refresh_regime`, così non sparisce più per un attimo).
Anelli: `/btc_history` (200 punti `{ts, close}`), `/avvii` (ultimi 20 avvii).
`/decision_status` porta anche `rifiuti_ciclo` e `rifiuti_24h` (`[{motivo, n}]`).

### `/positions/{symbol}`
Stato live di una posizione aperta (scritto dall'execution ad ogni update):
`{ position_id, symbol, strategy, direction, entry_price, mark_price, quantity,
leverage, stop_price, take_profit_price, unrealized_pnl, trailing_active,
scaled_out, dry_run, updated_at }`. Cancellato (null) alla chiusura.

### `/risk_state`
Stato dei circuit breaker persistito (sopravvive ai riavvii):
`{ daily_pnl_pct, day_key, consecutive_sl, paused_until_ts, macro_flat_until_ts,
halted_for_day, notes[] }`.

### `/commands/kill_switch`
Booleano. La **dashboard** lo imposta a `true`; il **bot** chiude tutte le
posizioni e lo riporta a `false`.

### `/account/equity`
Equity corrente (numero) usata per il sizing e l'equity curve.

## Regole di sicurezza consigliate (Firestore/RTDB Rules)
- `user_risk_settings` e `commands/kill_switch`: scrivibili solo da utenti
  autenticati (dashboard). **Lato bot** gli hard cap vengono comunque applicati,
  quindi un valore fuori range scritto qui non può causare danni.
- Tutto il resto: scrivibile solo dal service account del bot; lettura per la
  dashboard autenticata.
