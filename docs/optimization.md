# Ottimizzazione autonoma delle strategie (test → learn → iterate)

Estende il motore di apprendimento: non solo *pesa* strategie fisse, ma **cerca i
parametri migliori per ogni asset, validandoli out-of-sample, e ri-itera nel
tempo** — senza validazione manuale.

## Pezzi
- **Strategie parametrizzate** (`bot/strategies/*`): ogni strategia espone
  `default_params` e `param_grid` (i valori da provare). Legge i parametri con
  `self.p("chiave")`.
- **Walk-forward optimizer** (`backtesting/optimizer.py`): per ogni asset divide
  lo storico in finestre sequenziali; su ogni *train* fa grid search, applica i
  migliori sulla finestra *test* successiva (mai vista) e aggrega le metriche
  **out-of-sample** (pf, pnl, n. trade, win rate). Una coppia (asset, strategia)
  "passa" se OOS pf ≥ 1.10, pnl > 0 e abbastanza trade.
- **Job autonomo** (`scripts/optimize.py` + `.github/workflows/optimize.yml`):
  gira **ogni giorno alle 03:00 UTC**, ri-ottimizza su dati freschi e scrive su
  Firebase `strategy_params/current`. Nessun gate manuale.
- **Lettura lato bot** (`AdaptationEngine`): carica i parametri per-asset; il bot
  istanzia le strategie con quei parametri e **opera solo le coppie che hanno
  passato l'OOS** (`is_enabled`). Ricarica i parametri ogni 6h senza riavvio.

## Perché evita l'overfitting / cattura il cambiamento nel tempo
- Si misura **solo fuori campione** (i parametri scelti sul train sono giudicati
  sul test successivo). Niente curve-fitting sul passato.
- Gira **in continuo**: i parametri migliori vengono ricalcolati ogni giorno, quindi
  ciò che vale oggi per BTC può cambiare domani — il sistema si adegua da solo.
- Resta il **20% baseline non adattato** (`BASELINE_CAPITAL_FRACTION`) come
  riferimento anti-collasso.

## Flusso giornaliero
```
03:00 UTC  optimize.yml ──► walk-forward per asset ──► strategy_params/current (Firebase)
   │
   └► il bot (entro 6h) ricarica i parametri e opera solo le coppie validate OOS
02:00 UTC  learning loop ──► pesi strategia×regime + memory_report
```

## Esecuzione manuale
```bash
python -m scripts.optimize --symbols BTCUSDT,ETHUSDT,SOLUSDT --windows 3
```

## Stato
Prima versione del motore: parametrizzate e ottimizzabili breakout, trend_following,
mean_reversion, vwap_reversion, grid_trading, liquidity_grab. `funding_arbitrage` e
`momentum_cross_asset` non sono ottimizzabili sul backtest mono-asset (richiedono
funding reale / contesto multi-asset simultaneo) e restano sui default.
