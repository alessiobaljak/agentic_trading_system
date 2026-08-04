# Fonti dati (tutte gratuite)

| Agente | Fonte | Chiave | Note |
|--------|-------|--------|------|
| Price & Futures | Binance Futures REST/WS | `BINANCE_API_*` (dati pubblici senza chiave) | klines multi-TF, mark price, funding, OI |
| **Sentiment** | **CoinGecko** | **— (gratis)** | `sentiment_votes_up_percentage` per-coin → 0..1; fonte primaria |
| **On-Chain** | **Binance public futures-data** | **— (gratis)** | open interest, funding, long/short ratio |
| On-Chain | Alternative.me F&G | — | Fear & Greed Index 0..100, senza chiave |
| Macro & News | NewsAPI.org | `NEWSAPI_KEY` | headline crypto (opzionale) |
| Macro & News | Claude | `ANTHROPIC_API_KEY` | classificazione impatto news (low/medium/high) |
| Sentiment (opz.) | LunarCrush API v4 | `LUNARCRUSH_API_KEY` | **a pagamento**; usato solo se la chiave risponde, altrimenti CoinGecko |
| On-Chain (opz.) | Coinglass | `COINGLASS_API_KEY` | **a pagamento**; non necessario, sostituito da Binance public |

> **Tutte le fonti necessarie sono gratuite e senza chiave** (Binance pubblico,
> CoinGecko, Alternative.me). LunarCrush e Coinglass sono opzionali a pagamento e
> NON servono: il sistema degrada con grazia e usa le alternative free.

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


## Macro/news — NON implementato (rimosso 04/08/2026)
`bot/agents/macro_agent.py` esisteva ma non era importato da nessun file, e il
suo `upcoming_high_impact_events()` era un **placeholder che ritornava `[]`**:
collegarlo non avrebbe prodotto alcun effetto. E' stato rimosso perche' codice
morto documentato come protezione e' peggio di una protezione assente — fa
credere che il rischio sia coperto.

**Conseguenza da conoscere**: il bot **non** si mette flat attorno a FOMC/CPI/NFP.
Per implementarlo servirebbe una fonte di calendario economico (Investing.com,
ForexFactory) e poi l'aggancio ai circuit breaker.
