# Fonti dati (tutte gratuite)

| Agente | Fonte | Chiave | Note |
|--------|-------|--------|------|
| Price & Futures | Binance Futures REST/WS | `BINANCE_API_*` | klines multi-TF, mark price, funding, OI; WS per liquidation stream (estensione) |
| Sentiment | LunarCrush API v4 | `LUNARCRUSH_API_KEY` | social volume + sentiment, normalizzato 0..1 |
| On-Chain | Coinglass | `COINGLASS_API_KEY` | open interest, liquidation heatmap, funding |
| On-Chain | Alternative.me F&G | — | Fear & Greed Index 0..100, senza chiave |
| On-Chain | CoinMetrics community | — | metriche/prezzi reference rate (anche per il backtest) |
| Macro & News | NewsAPI free | `NEWSAPI_KEY` | headline crypto |
| Macro & News | Claude | `ANTHROPIC_API_KEY` | classificazione impatto news (low/medium/high) |

## Degradazione graceful
Ogni agente ritorna `None`/valori vuoti se la chiave manca o la richiesta
fallisce: il bot salta il ciclo invece di crashare. Questo permette di sviluppare
e testare senza tutte le chiavi.

## Calendario economico (eventi macro high-impact)
`MacroNewsAgent.upcoming_high_impact_events()` è il punto d'estensione per lo
scraping del calendario (FOMC/CPI/NFP). Gli eventi alimentano il circuit breaker
"flat ±2h" (`CircuitBreakers.set_macro_flat_window`). In assenza di feed
configurato ritorna lista vuota (nessun blocco macro).

## Dati per il backtest (GATE 1)
`backtesting/data_loader.py` prova in ordine: **CoinMetrics** (2022→oggi) →
**Binance klines** → **sintetico** (offline/CI). Lo storico CoinMetrics è la fonte
indicata per la validazione 2022–2026.

## Rate limit
Il `MarketScanner` limita gli asset scansionati per ciclo (`max_symbols`, default
60) per non saturare i rate limit pur coprendo l'universo dei più liquidi.
