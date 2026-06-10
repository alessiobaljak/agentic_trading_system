# Agentic Crypto Futures Trading System

Sistema di trading algoritmico **agentico** e **auto-apprendente** per crypto futures su Binance.

> ⚠️ **DISCLAIMER**: Il trading di futures con leva è ad altissimo rischio e può portare alla
> perdita totale del capitale. Questo software è fornito a scopo educativo e di ricerca.
> Usalo **solo** in modalità `DRY_RUN=True` (paper trading) finché non hai validato a fondo
> ogni componente. L'autore non è responsabile di perdite finanziarie.

Il cuore del progetto **non** è un insieme di regole fisse: è un **motore di apprendimento**
che analizza continuamente i risultati dei trade chiusi, riconosce quali strategie funzionano
in quali condizioni di mercato (regime) e **adatta autonomamente** i pesi delle strategie nel
tempo, senza intervento manuale.

---

## 1. Architettura cloud (nessun componente sul computer dell'utente)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                   CLOUD                                        │
│                                                                                │
│  GitHub (questo repo)            VPS Hetzner                 Firebase          │
│  ├─ codice                       ├─ bot core 24/7            ├─ Firestore       │
│  └─ GitHub Actions               │  (python -m bot.main)     │  (trades,        │
│     ├─ learning notturno 02:00   │                           │   memory_report, │
│     └─ monitoring/heartbeat      │                           │   weights,       │
│                                  │                           │   risk_settings) │
│                                  │                           └─ Realtime DB     │
│  Vercel (Next.js dashboard)      │                              (posizioni,     │
│  ├─ stato bot / regime           │                               bot_status)    │
│  ├─ equity curve                 │                                              │
│  ├─ heatmap strategia×regime     └──────────► Binance Futures API               │
│  ├─ pesi strategie nel tempo                                                    │
│  ├─ pannello RISK CONTROL                     Anthropic Claude API              │
│  └─ KILL SWITCH                               LunarCrush / Coinglass / ...      │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Componente            | Dove gira          | Cosa fa                                              |
|-----------------------|--------------------|------------------------------------------------------|
| Codice                | questo repo GitHub | sorgente di verità                                   |
| Bot core 24/7         | VPS Hetzner        | processo Python persistente (`bot/main.py`)          |
| Database e stato      | Firebase           | Firestore (storia/memoria) + Realtime DB (live)      |
| Dashboard             | Vercel             | Next.js 14, legge Firebase                           |
| Learning notturno     | GitHub Actions     | `scripts/` workflow ogni notte 02:00 UTC             |
| Secrets               | GitHub Secrets / env| mai hardcoded                                        |

---

## 2. Struttura del repository

```
/bot                  Core Python del sistema
  /agents             Agenti di analisi (price, sentiment, onchain, macro)
  /strategies         Le 8 strategie (modulari, espandibili via classe base astratta)
  /risk               Risk management (hard cap hardcoded, non bypassabile)
  /execution          Esecuzione ordini Binance (riusabile in DRY_RUN / live)
  /orchestrator       Orchestratore LLM Claude
  /learning           Motore di apprendimento e adattamento (il cuore)
  /core               Modelli dati, client Firebase, indicatori, util condivisi
  config.py           Configurazione centrale
  main.py             Entry point del bot
/dashboard            Next.js 14 per Vercel (incl. pannello risk control + kill switch)
/scripts              GitHub Actions workflows (learning notturno + monitoring)
/backtesting          Simulatore storico (GATE 1)
/docs                 Documentazione architettura
/tests                Test unitari
README.md             Questo file
requirements.txt
.env.example          Template variabili d'ambiente
```

---

## 3. I layer del sistema

### Layer 1 — Agenti dati (fonti gratuite)
- **Price & Futures Agent** (`bot/agents/price_agent.py`): WebSocket Binance Futures,
  candele multi-timeframe (1m/5m/15m/1h), mark price, funding rate, liquidation stream.
  Calcola EMA, RSI, MACD, Bollinger, ATR, VWAP per ogni asset.
- **Sentiment Agent** (`bot/agents/sentiment_agent.py`): LunarCrush (social volume + sentiment).
- **On-Chain Agent** (`bot/agents/onchain_agent.py`): Coinglass (OI, funding, liquidation
  heatmap), Alternative.me (Fear & Greed), CoinMetrics community.
- **Macro & News Agent** (`bot/agents/macro_agent.py`): calendario economico, NewsAPI free,
  classificazione impatto news via Claude.

### Layer 2 — Asset scanning & selection
- **Market Scanner** (`bot/agents/market_scanner.py`): ogni 4h scansiona **TUTTO** l'universo
  futures Binance, calcola punteggio composito (momentum tecnico, social, volume, funding, vol).
- **Asset Selector**: seleziona i 3–5 asset col miglior setup per le strategie favorevoli.
- **Correlation Guard** (`bot/risk/correlation_guard.py`): max 3 posizioni correlate >0.85.
- **Regime Detector** (`bot/agents/regime_detector.py`): Bull/Bear Trending, Sideways,
  High Uncertainty — aggiornato ogni ora.

### Layer 3 — Strategy engine (8 strategie, espandibile)
Tutte derivano da `bot/strategies/base.py::Strategy` (classe astratta). Ogni strategia
**dichiara in quali regimi è attiva**. Aggiungere la strategia #9 = un nuovo file, nient'altro.

1. Trend Following · 2. Mean Reversion · 3. Breakout · 4. Funding Rate Arbitrage ·
5. VWAP Reversion · 6. Momentum Cross-Asset · 7. Liquidity Grab · 8. Grid Trading

### Layer 4 — Risk management → vedi sezione dedicata sotto.

### Layer 5 — Orchestratore LLM (`bot/orchestrator/`)
Chiamato ad ogni candela 15m chiusa. Riceve indicatori, sentiment, F&G, funding, eventi macro,
**il memory_report del motore di apprendimento** e gli ultimi 20 trade. Output JSON validato
Pydantic (`asset, strategy, direction, size_multiplier, confidence, reasoning`).

### Layer 6 — Execution (`bot/execution/`)
Binance Futures REST, limit orders, TP+SL piazzati subito, trailing stop a +1 ATR, scale-out
parziale 50%. Scrive lo stato su Firebase Realtime DB. **Lo stesso codice** gira in `DRY_RUN`.

---

## 4. Risk management — parametri regolabili vs limiti hardcoded

Questa distinzione è implementata in modo esplicito ed è il cuore della sicurezza.

### Parametri REGOLABILI dall'utente (dashboard → Firebase `user_risk_settings` → bot)
| Parametro      | Range UI    | Hard cap (codice) | Note                                              |
|----------------|-------------|-------------------|---------------------------------------------------|
| Leverage       | 1x – 5x     | **5x**            | il bot lo riduce automaticamente in alta volatilità |
| Risk per trade | 0.5% – 3%   | **3%**            | sizing ATR-based; Kelly suggerito dopo 100+ trade |

### Limiti di sicurezza HARDCODED (né utente né LLM possono superarli)
Definiti in `bot/risk/hard_limits.py` — **mai** su Firebase, **mai** nel prompt dell'LLM:
- `MAX_LEVERAGE = 5`
- `MAX_RISK_PER_TRADE = 0.03` (3%)
- Circuit breakers:
  - stop totale se **daily loss > 5%**
  - **pausa 4h** dopo 3 SL consecutivi
  - **flat obbligatorio 2h prima/dopo** eventi macro high-impact
  - **size dimezzata** se volatilità > 3σ

### Logica di precedenza (implementata in `bot/risk/risk_manager.py::resolve_effective_params`)
Per **ogni** trade, leverage e size effettivi sono calcolati così:

1. **Parti** dal valore impostato dall'utente sulla dashboard (`user_risk_settings`).
2. **Applica** le riduzioni di sicurezza del sistema (alta volatilità → riduce).
3. **Applica** l'hard cap assoluto (mai oltre 5x / 3%).
4. **Risultato = il valore più conservativo** (il minimo) tra tutti i precedenti.

```
effective = min( user_value, system_safety_value, HARD_CAP )
```

Il **final risk gate** (`bot/risk/risk_manager.py::final_gate`) è l'**ultimo** controllo prima
dell'invio di qualunque ordine: qualsiasi richiesta (utente, LLM o strategia) lo attraversa e
viene clampata o rifiutata. Nessun percorso di codice invia ordini bypassandolo.

---

## 5. Il motore di apprendimento (il cuore)

### Trade Logger (`bot/learning/trade_logger.py`)
Ogni trade chiuso → Firestore con **ogni** dettaglio: timestamp in/out, asset, strategia,
direction, **tutti** gli indicatori all'entrata, sentiment, F&G, funding, regime, size, leverage,
PnL, slippage, motivo di exit, durata.

### Learning Loop notturno (`bot/learning/learning_loop.py`, GitHub Action 02:00)
1. Legge i trade degli ultimi 30/60/90 giorni.
2. Calcola metriche segmentate: win rate per strategia, **per strategia × regime**, R:R medio,
   performance per asset/fascia oraria, condizioni dei peggiori drawdown, correlazione
   confidenza-dichiarata ↔ risultato reale.
3. Genera un **`memory_report`** JSON.
4. Calcola **pesi dinamici** per strategia × regime (chi perde → peso basso in quel regime).
5. Salva `memory_report` + pesi su Firebase.
6. Il giorno dopo l'orchestratore riceve il report e adatta le decisioni.

### Meccanismo di adattamento (`bot/learning/adaptation.py`)
- L'orchestratore **moltiplica** la propria confidenza per il peso strategia×regime.
- Strategie che performano male → peso progressivamente → 0 (disattivate) finché le condizioni
  cambiano. Strategie buone → più capitale.
- **Anti-overfitting**: il **20% del capitale** resta sempre su una configurazione *baseline*
  non adattata (vedi `BASELINE_CAPITAL_FRACTION` in `config.py`).

### Auto-analisi continua
Report settimanale che l'orchestratore legge e commenta; gli insight diventano **memoria a lungo
termine (RAG)** su Firebase, recuperabile per situazioni storiche simili.

---

## 6. I due GATE di validazione

- **GATE 1 — Backtesting** (`/backtesting`): simulazione pura su dati storici CoinMetrics
  2022–2026, **PRIMA** dell'execution. Testa ogni strategia in ogni regime, simula liquidazioni
  con leva 2x/3x/5x/10x/20x, valida il learning loop. Se le strategie non sono profittevoli qui,
  **ci si ferma**.
- **GATE 2 — Paper trading** (`DRY_RUN=True`, default): riusa lo **stesso** codice di execution
  in modalità simulata su dati live, accumula trade reali su Firebase (il learning gira già).
  Va mantenuto per **settimane** di risultati positivi prima di `DRY_RUN=False`.

---

## 7. Setup passo-passo

### 7.1 GitHub Secrets da creare manualmente
Repo → Settings → Secrets and variables → Actions → *New repository secret*:

| Secret                     | Descrizione                                              |
|----------------------------|---------------------------------------------------------|
| `BINANCE_API_KEY`          | API key Binance Futures (abilitare *Futures*, NO *withdraw*) |
| `BINANCE_API_SECRET`       | API secret Binance                                      |
| `ANTHROPIC_API_KEY`        | API key Claude (orchestratore + classificazione news)   |
| `LUNARCRUSH_API_KEY`       | API key LunarCrush                                       |
| `COINGLASS_API_KEY`        | API key Coinglass                                       |
| `FIREBASE_SERVICE_ACCOUNT` | JSON service account Firebase (intero file, una riga)   |
| `TELEGRAM_BOT_TOKEN`       | token bot Telegram (alert)                              |
| `TELEGRAM_CHAT_ID`         | chat id destinatario alert                              |
| `NEWSAPI_KEY`              | API key NewsAPI free tier                               |

> Sulla **VPS Hetzner** le stesse chiavi vanno in un file `.env` (vedi `.env.example`),
> mai committato. Su **Vercel** servono solo le variabili `NEXT_PUBLIC_FIREBASE_*` (client).

### 7.2 Bot core sulla VPS Hetzner
```bash
git clone <repo> && cd agentic_trading_system
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # poi compila .env con le tue chiavi
python -m bot.main     # parte in DRY_RUN=True (paper trading)
```
Per girare 24/7 usa systemd (vedi `docs/deployment.md`).

### 7.3 Backtesting (GATE 1) — prima di tutto
```bash
python -m backtesting.run --start 2022-01-01 --end 2026-01-01
# genera report HTML + Excel in backtesting/output/
```

### 7.4 Dashboard su Vercel
```bash
cd dashboard && npm install && npm run dev   # locale
# deploy: collega il repo a Vercel, root = /dashboard, imposta le NEXT_PUBLIC_FIREBASE_*
```

### 7.5 Firebase
1. Crea un progetto Firebase, abilita **Firestore** e **Realtime Database**.
2. Genera un *service account* (Project settings → Service accounts) → metti il JSON nel secret
   `FIREBASE_SERVICE_ACCOUNT` e nella VPS `.env`.
3. Le collezioni/percorsi usati sono documentati in `docs/firebase_schema.md`.

### 7.6 Claude Code on the web (sessionStart hook)
`.claude/settings.json` contiene un hook che installa dipendenze Python e Node ad ogni sessione.

---

## 8. Ordine di costruzione (work order)
1. Struttura repo + README → 2. Config + interfaccia strategie → 3. Layer dati →
4. Risk management + gate finale → 5. Le 8 strategie → 6. Scanner + regime detector →
**7. GATE 1 backtesting** → 8. Orchestratore → **9. Motore di apprendimento** →
10. Execution (DRY_RUN) → **11. GATE 2 paper trading** → 12. Dashboard → 13. GitHub Actions.

Vedi `docs/architecture.md` per le scelte architetturali in dettaglio.

---

## 9. Sicurezza operativa
- Le API key Binance **non** devono avere il permesso di *withdraw*.
- Tieni `DRY_RUN=True` finché non hai settimane di paper trading positivo.
- Il **kill switch** della dashboard chiude tutte le posizioni in emergenza.
- Gli alert Telegram avvisano: bot offline, liquidazione, daily loss > 3%.
