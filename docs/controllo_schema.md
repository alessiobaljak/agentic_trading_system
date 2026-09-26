# Il controllo automatico — schema dei due documenti (25 set 2026)

Richiesta del proprietario: «check di status, learning, paper, gate, strategie, tutto in
automatico, e le evidenze in dashboard ogni ora». Questo file è il **contratto**
fra chi scrive (bot, gate) e chi legge (dashboard, comando ops `controllo`): i nomi
dei campi qui sono quelli veri. Cambiare un nome qui vuol dire cambiarlo in tre
posti (`bot/learning/controllo.py`, `scripts/discover_strategies.py`,
`dashboard/app/lib/controllo.ts` + `gate.ts`).

## Perché due documenti, e chi li scrive

| documento | scritto da | quando | contenuto | dimensione |
|---|---|---|---|---|
| Firestore `dashboard/controllo` + specchio RTDB `/controllo` | il **bot** (`TradingBot._publish_controllo`, gancio orario accanto ai pesi); ripiego: GitHub snapshot ogni 2 h e comando ops `controllo --publish` | ogni ora (≥ 3300 s dall'ultimo), mai a ogni trade | `meta`, `salute`, `paper`, `learning`, `manca` | < 30 KB (test) |
| Firestore `dashboard/gate` + specchio RTDB `/gate` | la **discovery** (`scripts/discover_strategies.py`, all'inizio del giro `stato: in_corso`, a fine giro tutto) e `scripts/optimize.py` (solo `stato` all'avvio dell'unit) | a ogni giro del gate (ogni 3 h; completo alle 03:30 UTC) | `meta`, `giro`, `registro`, `cervello`, `strategie` | < 200 KB (test) |

Il bot NON ricalcola il registro ogni ora: il suo documento porta solo l'età del
gate e le validate (dal registro che ha già in RAM). GitHub Actions non regge
l'ora (buchi misurati di 3-7 h): il bot è la fonte, GitHub e ops sono ripieghi.

Regole comuni:
* timestamp in **secondi** epoch (float), come `exit_ts` e `updated_at`;
* frazioni 0-1 salvo i campi che finiscono in `_pct` (già in percento);
* `null` = «non misurato / fonte assente», MAI zero al posto di un dato che manca;
* niente `NaN`/`inf` (→ `null`), niente liste di liste (Firestore le rifiuta), niente
  `. # $ [ ] /` nelle chiavi (RTDB le rifiuta): le distribuzioni sono liste
  `[{valore, n}]`, la scala è una stringa `"1.5/3/5"`;
* ogni sezione porta la testata `computed_at`, `fonti` (lista di stringhe tipo
  `"rtdb:/bot_status"`, `"fs:drift/current"`), `lettura` (≤ 140 caratteri, da
  regole, niente LLM), `dettaglio` (facoltativo, più lungo), `errore` (stringa se
  la sezione è fallita: fail-open per sezione, il resto del documento esce);
* il PF senza perdite è `null` (non 99, non inf), con il campo gemello `perdite: 0`.

---

## 1. `dashboard/controllo` (orario, dal bot)

### 1.1 `meta`
| campo | tipo | note |
|---|---|---|
| `versione_schema` | int | `1` |
| `generato_at` | float | `time.time()` |
| `generato_da` | `"bot" \| "github" \| "ops"` | chi ha scritto |
| `durata_ms` | int | misurata |
| `precedente_at` | float\|null | `generato_at` del documento precedente (letto da RTDB `/controllo/meta/generato_at`, pochi byte) |
| `semaforo_sistema` | `"verde" \| "giallo" \| "rosso"` | «è rotto?»: massima gravità delle anomalie con `famiglia: "sistema"` |
| `semaforo_paper` | idem | «perde?»: massima gravità delle anomalie con `famiglia: "paper"` |
| `errori` | list[str] | sezioni fallite (`salute`, `paper`, `learning.attivo`, `learning.misurato`, `anomalie`) + una voce `lettura: <fonte>: <errore>` per ogni lettura Firebase fallita in `carica_dati` |
| `fonte_impostazioni` | `"processo bot" \| "default repo"` | i `settings.*` letti valgono per la VPS solo se scritti dal bot |

### 1.2 `salute`
| campo | tipo | fonte |
|---|---|---|
| `bot_stato` | str\|null | `rtdb:/bot_status.state` |
| `heartbeat_at` | float\|null | `rtdb:/bot_status/heartbeat` (letto come FIGLIO, chiamata a parte; se il figlio non risponde si ripiega sul campo `heartbeat` del dict `/bot_status`, che `refresh_regime` scrive dal 25 set) |
| `heartbeat_eta_s` | int\|null | `now - heartbeat_at` |
| `soglia_online_s` | int | `900` — la dashboard calcola «online» da sola con questa soglia; il bot non scrive `online` (scriverebbe sempre true) |
| `avviato_at` | float\|null | `rtdb:/bot_status/avviato_at` (nuovo: figlio scritto all'avvio, non riscritto da `refresh_regime`) |
| `riavvii_24h` | int\|null | dall'anello `rtdb:/avvii` (lista degli ultimi 20 `avviato_at`) |
| `errori_ciclo_1h` | int\|null | contatore in RAM del bot pubblicato in `rtdb:/bot_status/errori_ciclo_1h` |
| `price_stream` | bool\|null | `rtdb:/bot_status.price_stream` |
| `dry_run` | bool\|null | `rtdb:/bot_status.dry_run` |
| `kill_switch` | bool | `rtdb:/commands/kill_switch` |
| `manutenzione` | bool | `rtdb:/commands/maintenance` |
| `regime` | str\|null | `rtdb:/bot_status.regime` |
| `fear_greed` | int\|null | `rtdb:/bot_status.fear_greed` (solo numero, non decide nulla) |
| `btc_24h_pct` / `btc_7g_pct` | float\|null | dall'anello `rtdb:/btc_history` (nuovo: `refresh_regime` aggiunge `{ts, close}` ogni ora, tiene 200 punti) |
| `ultima_decisione_at` | float\|null | `rtdb:/decision_status.ts` |
| `ultima_decisione_esito` | `"flat" \| "aperta" \| null` | `outcome`: `decided` → `"aperta"` |
| `ultima_decisione_motivo` | str\|null | `.reason` |
| `asset_valutati` / `segnali_trovati` | int\|null | `rtdb:/decision_status` |
| `rifiuti_ciclo` | list[{motivo, n}]\|null | `rtdb:/decision_status.rifiuti_ciclo` (nuovo, §3) |
| `rifiuti_24h` | list[{motivo, n}]\|null | `rtdb:/decision_status.rifiuti_24h` (nuovo, §3; contatore scorrevole in RAM, azzerato al riavvio: lo dice `rifiuti_24h_dal`) |
| `rifiuti_24h_dal` | float\|null | inizio della finestra |
| `gate_ultimo_giro_at` / `gate_ultimo_giro_eta_s` | float\|null / int\|null | `fs:dashboard/gate.meta.generato_at` (ripiego `fs:strategy_params/discovered_last_run.started_at + duration_s`) |
| `gate_stato` | `"in_corso" \| "finito" \| "errore" \| null` | `fs:dashboard/gate.meta.stato` |
| `gate_modalita` | str\|null | `"completa" \| "solo urgenti"` |
| `gate_pronto` | bool\|null | `fs:strategy_registry/validated.ready` — ATTIVO: con `REQUIRE_GATE1_READY` e `ready=false` il bot resta flat |
| `registro_at` / `pesi_at` / `deriva_at` / `calibrazione_at` / `referti_at` / `supervisore_at` | float\|null | `updated_at` dei rispettivi doc |
| `freno_globale` | bool | `fs:drift/current.global.verdict == "drift"` |
| `freno_globale_dal` | float\|null | `drift/current.global.dal` (nuovo, §3) |
| `circuit_breaker` | {halted_for_day, paused_until_ts, macro_flat_until_ts, consecutive_sl, daily_pnl_pct} | `rtdb:/risk_state` |
| `cooldown_coin` / `cooldown_strategie` | list[{nome, fino_a}] | `rtdb:/adapt_state` filtrati `> now` |
| `posizioni_aperte` | int | `rtdb:/positions` |
| `posizioni` | list[{coin, direzione, rischio_pct, upnl}] | ≤ 12, solo questi 4 campi (la dashboard è già abbonata a `/positions` per il resto) |
| `upnl_totale` | float | Σ `unrealized_pnl` |
| `tetto_posizioni` / `tetto_posizioni_attivo` | int / bool | `settings.MAX_OPEN_POSITIONS`; attivo solo fuori parità (`not settings.BACKTEST_PARITY`) |
| `rischio_aperto_pct` / `rischio_long_pct` / `rischio_short_pct` / `tetto_direzione_pct` | float | Σ `risk_effective_pct` ×100; `daily_cap.rischio_direzione(...)` ×100 (stima: il tetto del bot usa lo stop ORIGINALE e la quantità residua; nota nel `dettaglio`) |
| `wal_non_vuoto` | int | numero di figli in `rtdb:/unlogged_trades` |
| `rtdb_degradato_s` | float\|null | `fb.degraded_for()` (solo nel bot) |
| `controllo_precedente_eta_s` | int\|null | `now - meta.precedente_at` |
| `anomalie` | list[{codice, famiglia, gravita, testo, valore, soglia}] | vedi §1.6 |

### 1.3 `paper`
| campo | tipo | fonte / funzione |
|---|---|---|
| `equity` | float\|null | `rtdb:/account/equity` |
| `equity_iniziale` / `equity_iniziale_fonte` | float / `"rtdb" \| "default 1000"` | `rtdb:/account/starting_equity` (nuovo: `reconcile_equity` la scrive se assente) |
| `paper_dal` / `paper_dal_fonte` / `giorni_paper` | float\|null / `"rtdb" \| "primo trade"` / int\|null | `rtdb:/account/paper_started_at` (nuovo), ripiego `entry_time` minimo |
| `rendimento_pct` | float\|null | `(equity/equity_iniziale - 1) × 100` |
| `trades` / `vinti` / `perdite` / `win_rate` | int / int / int / float\|null | trade all-time escludendo gli esiti esterni (`ESITI_ESTERNI` di `bot/learning/referti.py`). Dal bot arrivano i trade di `refresh_weights` (30 g) finché il paper è più giovane di 30 giorni; oltre, `_publish_controllo` rilegge l'all-time |
| `pnl_realizzato` / `pf_vissuto` / `expectancy` | float / float\|null / float\|null | inline; `pnl_realizzato` su TUTTI i trade chiusi (com'è nell'equity, esiti esterni compresi), `pf_vissuto`/`expectancy` sui soli decisi dalla strategia; `pf_vissuto = null` se `perdite == 0` |
| `ultimi_30g` | {trades, pnl, pf, win_rate} | `fs:drift/current.global.{trades, live_pf, pnl}` (pf 99 → null) |
| `oggi` | {trades, vinti, pnl, migliore:{coin,pnl}\|null, peggiore:{...}\|null} | giorno **UTC** |
| `giornate` | {con_trade, positive, negative, migliore:{data,pnl}, peggiore:{data,pnl}, ultime_7: list[{data, trades, pnl}]} | pura `giornate(trades, now)` |
| `uscite` | list[{motivo, etichetta, trades, quota, pnl}] | `Counter(exit_reason)` + etichette di `state_snapshot._EXIT_LABEL` |
| `gradini` | list[{gradino, n}] | `scale_stage_reached` |
| `mfe` | {n, mediana_r, quota_1r, quota_1_5r, quota_3r} | `mfe_r` (`n` = trade che lo portano; il resto `null` se 0) |
| `stop` | {totale, sbagliati, quasi, oltre_primo_tp, quasi_durata_mediana_h, primo_gradino_r, nota} | `metrics.classi_stop(trades, first_rung)` (pura, NUOVA in `bot/learning/metrics.py`; `mfe_report` la usa); `first_rung` per coppia da `last_params.scale_r_mults[0]` se il registro è in mano, altrimenti globale e `nota` lo dice |
| `direzione` | {long:{trade, vinti, pnl, mfe_mediana}, short:{...}} | `trade_stats.direction_report(trades)["per_direzione"]` (le chiavi vere: `trade`, non `trades`) |
| `allineamento` | {in_trend:{trade,pnl}, contro:{...}, neutro:{...}, ignoto:{...}} | `direction_report(...)["allineamento"]` |
| `costi` | {totale, per_trade, commissioni, spread, funding, lordo, netto, break_even_pct, stimati: true, avvisi: list[str]} | `metrics.cost_report`, `metrics.cost_alerts` |
| `drawdown_portafoglio` / `max_posizioni_insieme` | float\|null / int\|null | `backtesting.engine.portfolio_drawdown`, `max_concurrent` |
| `trailing` | {verdetti_totali, prematuri, protetti, neutri, verdetti_per_proposta, prematuri_tf, protetti_tf, proposta_paper, soglia} | tutti i verdetti (anche scale_out) nei primi 4; SOLO `exit_reason == trailing_stop` e timeframe del bot negli `_tf`; `proposta_paper = metrics.proposta_keep(n, prem, prot)` (stessa regola di `keep_dal_paper`) |
| `benchmark` | {btc_24h_pct, btc_7g_pct, nota, portafoglio: {lettura, updated_at}\|null} | dall'anello BTC (§3); `portafoglio` = `fs:portfolio/backtest.{lettura, updated_at}` se esiste (manuale, con la sua età) |
| `esplorative` | {trades, vinti, pnl, aperte, coppie_attive} | il PAPER ESPLORATIVO (25 set, backlog F1bis): i trade con `esplorativa: true` (quasi-passaggi del gate operati a un quarto della size), fuori dagli esiti esterni; `aperte` = posizioni RTDB con `esplorativa`; `coppie_attive` = `fs:strategy_registry/esplorative.pairs` (null senza documento). TUTTI gli altri numeri di `paper` (trades, pnl_realizzato, pf_vissuto, uscite, stop, costi, …) ESCLUDONO i trade esplorativi: sono i numeri delle validate. `equity` invece è quella del conto e li comprende (lo dice il `dettaglio`; `EQUITY_NON_TORNA` somma `esplorative.pnl`) |
| `declassate` | {trades, pnl, aperte} | LE DECLASSATE (26 set, passo 2 del piano del 26 set 15:xx): i trade con `declassata: true` (validate che il gate ha declassato dopo `DECLASSATA_NOTTI` giri completi bocciati: `declassata`/`declassata_at`/`bocciata_notti` sul record del registro; il bot le opera a `DECLASSATA_SIZE_MULT` della size, riga `[declassata]` nel log), fuori dagli esiti esterni; `aperte` = posizioni RTDB con `declassata`. A differenza delle esplorative RESTANO dentro tutti gli altri numeri di `paper` (sono validate): qui si contano a parte per leggere il loro vissuto contro le attive (`trades`, sezione DECLASSATE) |

### 1.4 `learning` — `attivo` (cambia decisioni ORA) e `misurato` (solo osservato)
`learning` porta la sua testata (`computed_at`, `fonti` = unione, `lettura`, `errore`)
e dentro `attivo` e `misurato`, ciascuno con la propria testata e il proprio try
(uno può fallire senza l'altro).

`attivo`:
| campo | tipo | fonte |
|---|---|---|
| `freno_globale` | {attivo, verdetto, trades, pf_vissuto, pf_atteso, pf_atteso_nota: "media semplice dei last_pf del registro", soglia_uscita_pf, size_x, leva_x_min: 0.5, motivo, dal} | `fs:drift/current.global`; `size_x = settings.DRIFT_WEIGHT_FACTOR` |
| `gate_pronto` | bool\|null | come in salute (interruttore attivo) |
| `pesi` | {at, aggiornato_da_nota: "bot orario o notturno GitHub", versione, campioni_sommati, combinazioni, soglia_panchina: 0.5, in_panchina_n, spente_n, in_panchina: list[≤10 {strategia, regime, peso, campione, win_rate}]} | `fs:strategy_weights/current` (panchina = peso < 0.5; spenta = peso ≤ 0) |
| `tilt` | {trend_enabled, trend_strength, trend_floor, sentiment_enabled, sentiment_strength} | `settings.*` |
| `keep_per_coppia` | {distribuzione: list[{valore, n}], non_rivalutate: int} | dal registro in RAM (`last_params.profit_lock_keep`), stessa forma di `gate.cervello.keep_validate` |
| `freno_serie` | {enabled, perdite_soglia, fattore, serie: list[≤5 {strategia, perdite}]} | `settings.STREAK_BRAKE_*`; `fs:drift/current.serie` |
| `tetti` | {coin_giorno_pct, direzione_pct, max_posizioni, max_posizioni_attivo, correlate_max} | `settings.*` |
| `cooldown_attivi` | int | come salute |
| `calibrazione_trust` | float\|null | `calibration.confidence_trust(doc)` |
| `impronta` | {freno: bool, panchina: list[str "strat\|regime"], cooldown: list[str], keep: list[{valore,n}], validate: int, gate_pronto: bool} | la foto di ciò che decide |
| `cambiamenti_24h` | list[str] | differenze fra `impronta` e quella del documento precedente (letta da RTDB `/controllo/learning/attivo/impronta`): es. «freno globale ACCESO», «gen_x\|sideways in panchina», «validate 160 → 172». Vuota = «nessun pezzo del learning ha cambiato decisione» |

`misurato`:
| campo | tipo | fonte |
|---|---|---|
| `deriva` | {at, coppie_ok, coppie_watch, coppie_drift, soglia_coppia, soglia_strategia, max_trades_coppia, top: list[≤10 {coppia, verdetto, trades, pf_vissuto, pf_atteso, motivo}]} | `fs:drift/current.pairs` |
| `calibrazione` | {at, verdetto, trades, correlazione, trust, nota} | `fs:calibration/current` (niente fasce) |
| `trailing` | = `paper.trailing` | |
| `referti` | {n_con_referto, persi_con_referto, ingresso, uscita, protezione, stop_largo, lock_mai, controtrend, ipotesi: list[≤5 str]} | `fs:learning/referti` (somma `per_direzione.long + short`); `referti.riassunto_ipotesi(doc)` |
| `selettore` | {at, verdetti: {famiglia: str}, nota}\|null | `fs:selector/report` se esiste |
| `ombra_ai` | {n, agree, ultimo_at}\|null | `fs:ai_shadow` (query con `order_by="at"`, limit 200) |
| `ipotesi_ai` | {proposte, accettate, at}\|null | `fs:ai_hypotheses/last` |
| `notturno_at` | float\|null | `fs:memory/30.generated_at` |

### 1.5 `manca`
Lista `[{evidenza, perche, come_avere}]` di ciò che il controllo NON può dare
oggi, scritta dal codice (non inventare numeri): battito ops (in git),
benchmark su Binance, «cosa aspetta il sì» (vive in `docs/backlog.md`).

### 1.6 Anomalie
`{codice, famiglia: "sistema"|"paper", gravita: "rosso"|"giallo"|"info", testo, valore, soglia}`.

| codice | famiglia | condizione | gravità |
|---|---|---|---|
| `BOT_FERMO` | sistema | `heartbeat_eta_s > 900` e non in manutenzione | rosso |
| `KILL_SWITCH_ATTIVO` | sistema | `commands/kill_switch` true | giallo |
| `MANUTENZIONE` | sistema | `commands/maintenance` true | info |
| `WAL_NON_VUOTO` | sistema | `unlogged_trades` ha figli | rosso |
| `CICLO_IN_ERRORE` | sistema | `errori_ciclo_1h > 3` | giallo |
| `RIAVVII` | sistema | `riavvii_24h > 3` | giallo |
| `GATE_IN_RITARDO` | sistema | `gate_ultimo_giro_eta_s > 3h + durata`; rosso se > 6 h | giallo/rosso |
| `GATE_SFORA` | sistema | `durata_s > 3h` | giallo |
| `GATE_FALLITO` | sistema | `gate_stato == "errore"` | rosso |
| `GATE_NON_PRONTO` | sistema | `gate_pronto == false` | rosso (il bot resta flat) |
| `CONTROLLO_VECCHIO` | sistema | `controllo_precedente_eta_s > 7200` | giallo |
| `REGISTRO_CALATO` | sistema | validate < 0.7 × precedente → rosso; < 0.8 → giallo | |
| `REGISTRO_PIENO` | sistema | `occupazione ≥ 0.8 × limite` (dal doc gate) | giallo |
| `PESI_SOSPESI` | sistema | `pesi_at > 2h` E `deriva_at < 2h` | giallo |
| `STREAM_PREZZI_OFF` | sistema | `price_stream == false` | giallo |
| `RTDB_DEGRADATO` | sistema | `rtdb_degradato_s > 60` | giallo |
| `EQUITY_NON_TORNA` | sistema | `abs(equity − (iniziale + Σpnl + Σ realized_partial aperte)) > 1` | giallo |
| `PF_VISSUTO_BASSO` | paper | `ultimi_30g.trades ≥ 20` e `pf < 0.5` | rosso |
| `FRENO_GLOBALE` | paper | verdetto drift | giallo |
| `RISCHIO_ALTO` | paper | `rischio_aperto_pct > 6` | rosso |
| `DIREZIONE_AL_TETTO` | paper | long o short ≥ tetto | giallo |
| `OLTRE_TETTO_POSIZIONI` | paper | `posizioni_aperte > tetto` (cap spento in parità: I6) | giallo |
| `CIRCUIT_BREAKER` | paper | halted/paused/macro flat | giallo |
| `NESSUN_TRADE_48H` | paper | nessuna chiusura né apertura da 48 h e `segnali_trovati > 0` (approssimata) | giallo |
| `SENZA_PROMESSA` | paper | `n_senza_promessa / n_operate > 0.3` (dal doc gate) | giallo |
| `CONTROLLO_LENTO` | sistema | `durata_ms > 5000` (2000 era troppo stretta: 2002 ms da ops a freddo il 25 set) | giallo |

Il semaforo di famiglia = rosso se una rossa, giallo se una gialla, verde altrimenti;
le `info` non colorano. `BOT_FERMO` scatta anche col battito MAI visto (valore
`null`): un bot senza battito non è «non misurato», è fermo. Se il calcolo delle
anomalie stesso fallisce, la lista porta la sola `ANOMALIE_NON_CALCOLATE`
(sistema, giallo) e `meta.errori` contiene `anomalie`.

### 1.7 Letture (una frase ≤ 140 caratteri per sezione, da regole)
* salute: «Bot vivo (battito 22 s fa), gate 1 h 30 fa (solo urgenti), 4 posizioni, 1,5% a rischio. 1 avviso: freno globale.»
* paper: «55 trade in 10 giorni, 42% vinti, −46,65 USDT (−4,7%). Stop nel 57% delle uscite. Oggi +0,92.» + «Numeri piccoli» se `trades < 20`
* learning: «Attivo: freno globale, 6 strategie in panchina, keep per coppia 0,5 ×31. Solo misurato: deriva, calibrazione, 14 verdetti trailing.»
Ogni numero della frase esiste anche come campo.

---

## 2. `dashboard/gate` (a ogni giro, dalla discovery)

### 2.1 `meta`
| campo | tipo |
|---|---|
| `versione_schema` | int `1` |
| `stato` | `"in_corso" \| "finito" \| "errore"` |
| `fase` | `"optimize" \| "discover" \| "passata_1h" \| null` |
| `errore` | str\|null |
| `iniziato_at` / `generato_at` / `durata_s` | float / float\|null / int\|null |
| `modalita` | `"completa" \| "solo urgenti"` |
| `generato_da` | `"discovery"` |

Chi scrive `in_corso`: `scripts/optimize.py` all'avvio dell'unit (`fase: optimize`) e
`discover_strategies.py` all'avvio (`fase: discover`); chi scrive `finito`: la
discovery a fine giro (dopo la passata extra a 1 h, se c'è) con tutte le sezioni;
`errore`: un `except` di alto livello in `main()` della discovery (rilancia dopo).
Scrivere `in_corso` senza cancellare le sezioni del giro precedente (merge del solo
`meta`): il controllo orario e la dashboard continuano a mostrare l'ultimo giro finito.

### 2.2 `giro` (l'ultimo giro)
| campo | tipo | fonte |
|---|---|---|
| `coin_valutate` / `valutazioni` / `passate` | int | `discovered_last_run` |
| `passate_lista` | list[≤10 {coin, id, pf, pnl}] | |
| `spec_note` / `spec_rivalutate` / `spec_con_conferme` / `spec_tagliate` / `tetto_rivalutazione` | int | modalità urgenti |
| `candidate` | {totale, ai, varianti_referti, intorno, casuali, semi, gemelle_scartate, rivalutate}\|null | composizione: ai/varianti/casuali/semi contate all'assemblaggio (prima della de-dup), `totale` = lista comune davvero valutata su ogni coin (nuove + rivalutate, dopo de-dup e gemelle), `intorno` = figlie valutate solo sulla coin della madre; `null` nel merge degli shard (non contabile) |
| `passata_1h` | {at, durata_s, coin, valutazioni, passate}\|null | `discovered_last_run_1h` |
| `worker` / `rss_max_mb` | int / float\|null | se noti |
| `paper_propone` | {scala: str\|null, keep: float\|null, verdetti_trailing: int} | `scala_dal_paper`, `keep_dal_paper` |
| `ipotesi_uscita` | {strategie: int, con_scala: int} | strategie rigiudicate nel giro per un'ipotesi `scala_stretta` fresca nei referti (`strategie_scala_stretta`, ≤ 10) e quante con una scala propria dal vissuto (`scale_per_strategia`); 0/0 nel merge degli shard |
| `passate_solo_con_propria_config` | int\|null | (26 set 2026) quante coppie GIÀ validate sono passate SOLO grazie alla propria configurazione d'uscita: dal 26 set `_disc_one` giudica ogni validata sulla scala/BE/keep che il bot opera (`config_iniziale` di `evaluate_spec`, letta da `last_params` con `ladder_multiples`/`breakeven_after_tp1`/`lock_keep`) e, se passa con una configurazione diversa dalla globale, rifà il solo passo 1 sulla globale: bocciata lì = contata qui (`discovered_last_run.passate_solo_con_propria_config`). Misura dell'artefatto trovato dall'autopsia del 26 set, non una decisione. `null` se il giro non l'ha contata (merge degli shard, codice precedente) |
| `esplorative` | {attive, validate_poi, scartate}\|null | il PAPER ESPLORATIVO (25 set, F1bis): `discover_strategies.pubblica_esplorative` sceglie a fine giro le `ESPLORATIVE_MAX` (20) coppie fra i quasi-passaggi (mancato più piccolo, una per coin, non validate, spec generata nota, coin nell'universo) e scrive `fs:strategy_registry/esplorative` = {updated_at, pairs: {"SYM\|spec_id": {symbol, strategy, since, last_seen, shortfall, binding, pf, trades, esito: in_corso}}, specs: {spec_id: spec} (solo delle attive), storia: {"SYM\|spec_id": {since, fine, esito: validata\|scartata}} (≤ 200)}; una coppia resta finché è quasi-passaggio o vista entro 8 h (2 giri), validata → storia «validata», assente > 2 giri → «scartata». `attive` = coppie in `pairs`, `validate_poi`/`scartate` = conteggi della storia (il metro dell'esperimento). `null` se il giro non le ha aggiornate (shard, passata 1h, errore: fail-open) |
| `riduzione` | {spec_note: int, coin_proprie: int, fetta: str, valutazioni_stimate: int}\|null | il GIRO COMPLETO RIDOTTO (26 set 2026, backlog J10): nel giro completo le spec NOTE (`discover_strategies.riduci_spec_note`) si valutano solo sulle coin dove hanno una coppia viva nel registro (pass_count ≥ 1) e su una fetta rotante di 1/7 dell'universo (giorno UTC modulo 7 su ordine alfabetico: `fetta` = «g/7»), le candidate nuove su tutte; `spec_note` = spec note ridotte, `coin_proprie` = coin con almeno una coppia viva di una spec nota, `valutazioni_stimate` = nuove × coin + le liste per coin (da confrontare con `valutazioni`). Da `discovered_last_run.riduzione`; `null` se il giro non era ridotto (urgenti, `--symbols`, shard, `DISCOVERY_RIDUZIONE=false`) |

### 2.3 `registro`
| campo | tipo | fonte |
|---|---|---|
| `validate` / `coin_coperte` / `universo` / `copertura` / `obiettivo_copertura` | int/int/int/float/float | doc `validated` |
| `pronto` / `pronto_per` | bool / `"copertura" \| "numero coppie" \| null` | `ready`, `ready_by` |
| `distribuzione_pass` | list[{pass, coppie, coin}] | `registry.distribuzione_pass(pairs, now)` (estratta in `bot/core/registry.py`, `gate_progress` la usa per stampare) |
| `congelate` / `a_un_passo` / `finestre_scadute` | int | idem |
| `coppie` / `base` / `generate` / `generate_con_conferme` / `occupazione` / `limite` / `alleggerito` | int/int/int/int/int/int/bool | `registry.salute_registro(pairs)` (estratta in `bot/core/registry.py`, gemella di `state_snapshot._salute_registro`); `occupazione` = base + generate con conferme, cioe' la parte del tetto che nessuno pota (il difetto del 31 agosto: al tetto le candidate nuove non hanno posto); `limite` = `OPTIMIZER_MAX_PAIRS` letto nel processo del gate (e scritto anche nel doc `validated` come `max_pairs`); `alleggerito` = almeno una validata senza i campi descrittivi (`last_pnl_pct`) |
| `senza_promessa` | int | validate senza `last_pf` |
| `statistica_t` | {misurate, sopra_2, sopra_3, mediana, piu_basse: list[3 {coppia, t}]} | `registry.statistica_t(pairs)` (estratta; misurata, non decide; `mediana` non arrotondata, come la stampa) |
| `validate_delta_giro` | int\|null | vs documento precedente |
| `declassate` | int | (26 set 2026) validate con `declassata: true` sul record (`registry.conta_declassate(pairs, validated)`): bocciate dal giro COMPLETO del gate per `DECLASSATA_NOTTI` (2) notti di fila (`bocciata_notti`, scritto da `discover_strategies.aggiorna_declassate` nel merge; i giri «solo urgenti» non lo toccano; `declassata_at` la data). Il bot le opera ancora, a `DECLASSATA_SIZE_MULT` (0,25) della size; tornano piene (`bocciata_notti` 0, `declassata` false) al primo giro completo in cui ripassano. Mai pass_count, finestre o purga. L'esito del giro (nuove, tornate piene) sta in `discovered_last_run.declassate` e nella riga `[cervello] declassate` del log |

### 2.4 `cervello`
| campo | tipo | fonte |
|---|---|---|
| `riga` | str | `riga_cervello(diag)` |
| `intorno` | {madri, figlie_passate, promosse: list[≤10 str], senza_margine, madre_non_valutata, scartate, ultimo_completo_at}\|null | dell'ULTIMO GIRO COMPLETO (l'intorno gira solo lì): se questo giro non è completo, ricopiato dal documento precedente con il suo `ultimo_completo_at`; `null` se non c'è un documento precedente |
| `varianti` | {create, passate, retro_ok, promosse: list[≤10 str], scartate, sostituzioni: list[≤10 {figlia, madre}]} | `esito["varianti"]` |
| `keep_giro` | {scelti: list[{valore, n}], non_scelto, dal_paper: float\|null, dal_paper_n: int} | `discover_strategies.conta_keep_giro(out, passed_keys, keep_paper)`: gli stessi numeri che `riga_cervello_keep` stampa |
| `keep_validate` | {distribuzione: list[{valore, n}], non_rivalutate: int} | `registry.conta_keep(pairs, validated)` (estratta in `bot/core/registry.py`) |
| `scala_validate` | list[{scala, n}] | `last_params.scale_r_mults` |
| `breakeven_validate` | int | `last_params.sl_to_breakeven` |
| `autopsia` | {at, valutazioni, passate, quota, criterio_principale, quota_criterio, quasi_passaggi} | `gate_autopsy/discover` |
| `autopsia_base_congelata_da_s` | int\|null | `gate_autopsy/current.updated_at` |
| `supervisore` | {at, ultima_decisione: {kind, reason}, decisioni_none_di_fila} | `supervisor/state` |

### 2.5 `strategie`
| campo | tipo | fonte |
|---|---|---|
| `n_operate` / `n_con_paper` / `n_senza_promessa` / `n_sostituite` / `n_nate_intorno` / `n_da_referto` / `n_scadute_dal_giro` | int (`n_con_paper` null senza trade) | `registry.coppie_operate(pairs, now)` = `registry.coppie_validate` (spostata in `bot/core/registry.py`; `optimize` e `discovery` la importano da lì) + `registry.coppie_robuste` (la regola di `adaptation._robust_only`, copiata); `n_sostituite` = coppie a soglia con `sostituita_da` (le madri: NON stanno fra le validate); `n_scadute_dal_giro` = validate nel doc − operate |
| `operate` | list[≤300 {chiave, coin, strategia, famiglia, origine, genitore, ipotesi, pass, validata_at, ultimo_pass_at, pf_promesso, pnl_promesso_pct, t, holdout_ok, scala, breakeven, keep, direzione_pf: {long, short}, paper: {trades, vinti, pnl, pf_vissuto, perdite, verdetto, motivo}}] | registro + spec (`famiglia_spec`; `famiglia`/`origine` = `"base"` per le strategie scritte a mano, null se la spec non è nota) + trade raggruppati per `symbol\|strategy` (fetch UNICO dei trade nel main della discovery, `trades_del_paper`, riusato da `scala_dal_paper`/`keep_dal_paper`); `verdetto`/`motivo` (≤60 car.) da `drift/current.pairs` se presenti; `t`, `holdout_ok`, `direzione_pf` `null` se assenti; `paper` null senza trade per la coppia. NIENTE `sostituita_da`: una coppia operata non è mai sostituita (sarebbe sempre null; 300 voci devono stare in 200 KB). Ordine: prima chi ha trade nel paper, poi PF promesso decrescente; oltre 300 si tronca e `operate_troncate` lo dice |
| `operate_troncate` | int | quante coppie operate sono rimaste fuori da `operate` (oltre le 300, o dopo il dimezzamento se il documento supera i 200 KB); `0` = lista completa |
| `per_famiglia` | list[{famiglia, coppie, coin, pf_promesso_mediano, paper_trades, paper_pnl, paper_pf}] | aggregato |
| `per_coin` | list[≤10 {coin, coppie, paper_trades, paper_pnl}] | aggregato |
| `promessa_vs_vissuto` | {pf_promesso_mediano_operate, pf_atteso_media_registro, pf_vissuto_30g} | registro; `drift.global` |
| `vite` | {promosse_7g, rimosse_7g, parziale: bool} | `gate_history/lifecycle` (`registra_vite` chiamata anche da `merge_into_registry` della discovery, via `_segna_promozione`: solo l'attraversamento della soglia); `parziale: true` (e conteggi null) solo se il documento manca |

Chi scrive il documento: `discover_strategies.costruisci_doc_gate(...)` (pura) tramite `pubblica_doc_gate(fb, ...)`; la scrittura (`scrivi_doc_gate`: Firestore poi RTDB, mai un'eccezione), la fusione del solo `meta` (`aggiorna_meta_gate`) e la guardia di serializzazione (`pulisci_per_firestore`) stanno in `bot/core/registry.py`, così anche `optimize.py` le usa senza importare la discovery. La passata a 1 ora (`--interval` diverso dal timeframe del bot) scrive solo `meta: {stato: in_corso, fase: passata_1h}`; il documento intero lo scrive il giro sul timeframe del bot, che è l'ultimo passo della unit. Nel merge degli shard (GitHub) il documento esce con `candidate: null` e l'intorno ricopiato.

---

## 3. Cosa i writer aggiungono (file esatti)
1. `bot/main.py::refresh_regime`: `"heartbeat": now` nel dict di `/bot_status` (oggi il nodo viene riscritto senza il figlio e il battito sparisce per un attimo); `btc_close` nel dict e anello `rtdb:/btc_history` (200 punti `{ts, close}`).
2. `bot/main.py` all'avvio: `rtdb:/bot_status/avviato_at` (figlio) + anello `rtdb:/avvii` (ultimi 20); contatore `errori_ciclo_1h` pubblicato come figlio `/bot_status/errori_ciclo_1h` dal gancio orario.
3. `bot/main.py::reconcile_equity`: scrive `/account/starting_equity` e `/account/paper_started_at` se assenti (oggi solo `reset_paper.py`).
4. `bot/main.py::_publish_drift`: `global.dal` = data del primo verdetto `drift` consecutivo (letto dal doc precedente).
5. `bot/orchestrator/orchestrator.py::_rifiuto` + `bot/main.py::_try_open`: contatori `rifiuti_ciclo` {motivo: n} e scorrevole `rifiuti_24h` pubblicati in `/decision_status` (come liste `[{motivo, n}]`). I motivi sono le prime parole della riga `[rifiuto]` normalizzate (`orchestrator.motivo_rifiuto`): `cooldown`, `tetto per coin`, `peso sotto soglia`, `strategia spenta`, `veto di regime`, `margine`, `rischio direzionale`, `stop troppo largo`, `esplorative al tetto` (25 set, F1bis: segnale esplorativo con `ESPLORATIVE_MAX_APERTE` posizioni esplorative già aperte), `posizione aperta` (26 set, J6: «posizione gia' aperta su questa coin», prima in `altro`), `altro`. Il contatore è uno solo, nell'orchestratore: `conta_scarto(motivo)` lo incrementa (lo chiama anche `_try_open`), `nuovo_ciclo()` azzera quello del ciclo all'inizio di `decide`/`decide_all`, `rifiuti_ciclo()`/`rifiuti_24h()` lo leggono come liste; `rifiuti_24h_dal` è l'avvio del processo.
6. `scripts/optimize.py`: `dashboard/gate.meta = {stato: in_corso, fase: optimize, iniziato_at}` all'avvio (merge del solo meta); `max_pairs` nel doc `validated`; `registra_vite` richiamata anche da `merge_into_registry` della discovery.
7. `scripts/discover_strategies.py`: `stato: in_corso, fase: discover` all'avvio; a fine giro il documento intero (§2); `except` di alto livello → `stato: errore`.
8. `scripts/state_snapshot.py`: dopo lo snapshot, `--publish-controllo --se-vecchio 5400` (ripiego GitHub: pubblica con `generato_da: "github"` solo se il controllo del bot è più vecchio di 90 minuti).
9. `scripts/controllo.py` (nuovo, voce ops `controllo`): stampa i due semafori, le anomalie e le letture; `--publish` scrive (voce ops separata e commentata).
10. (26 set, passo 4) `bot/main.py::_publish_drift` → `bot/learning/drift.py::compute_drift`: in `fs:drift/current` le chiavi `pool` = {"fam:<famiglia>|<regime>" / "dir:<long|short>|<btc_su|btc_giu>": {n, r_medio, cusum, allarme, ripresa, dal, riferimento, riferimento_nota, coppie_riferimento, cusum_ripresa, allarmi, sprt, sprt_llr, tp1_n, tp1_hit}} e `pool_famiglie` = {strategia: famiglia}. R = pnl / (|entry − orig_stop| × size) (ripiego `post_mortem.stop_pct`, altrimenti il trade si salta); riferimento = media di (1 − wr)(PF − 1) delle validate del pool (0.0 e la nota lo dice se non derivabile); il bucket «ignoto» del contesto BTC non forma un pool. `weight_factor(..., regime, contesto, direzione)` frena ×`POOL_BRAKE_FACTOR` un pool in `allarme` senza `ripresa`, combinato col globale col MINIMO. Soglie costanti (`POOL_CUSUM_H` 4, `POOL_CUSUM_RIPRESA` 2,5, SPRT 0,45/0,25): il replay ops `replay` puo' solo bocciarle.
11. (26 set, passo 4) `bot/orchestrator/orchestrator.py::decide_all`: un peso sotto soglia non rifiuta piu' («peso sotto soglia» resta come classe, scatta solo con `PANCHINA_PAVIMENTO` ≤ 0): la decisione porta `peso_size = max(PANCHINA_PAVIMENTO, peso)` e il log una riga `[panchina] SYM strat: peso 0.26 -> size x0.26` (non contata fra i rifiuti). `bot/main.py::_try_open` la applica alla size e la scrive in `size_factors_at_entry.peso_size`; `size_factors_at_entry.declassata` e la riga `[declassata] SYM strat dir size x0.25` per le declassate (passo 2).

## 4. Cosa resta fuori (e dove sta)
* righe `[rifiuto]` per coppia: journal (ops `rifiuti`); qui solo i conteggi per motivo;
* portafoglio simulato, selettore, confronto: comandi ops sulla VPS (servono le candele);
* «cosa aspetta il sì»: `docs/backlog.md`;
* battito dell'agente ops: `ops/heartbeat.md`.
