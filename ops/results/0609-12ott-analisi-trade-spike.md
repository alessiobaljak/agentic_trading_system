# 0609-12ott-analisi-trade-spike.req

_eseguito: 2026-10-12 18:41 UTC_

**richiesta:** `spike`
**eseguito:** `.venv/bin/python -m scripts.spike_response`
**esito:** codice 0 in 559.5s

```
[backtest] dati da cache: 167521 candele (BTCUSDT 15m)
[spike] soglia 10% in 24h · timeframe 15m · da 2022-01-01
[spike] ORIZZONTE del motore: 96 barre (24h) — oltre, il trade e' chiuso d'ufficio

=== BTCUSDT ===
  eventi: 50 (dal 20 Jan 2022 al 20 Aug 2026)
  regime al momento dello spike: bull_trending 26 · bear_trending 20 · high_uncertainty 4
  MAI ACCESE durante gli spike: grid_trading
  accese (su quanti eventi): breakout 50/50 · funding_arbitrage 50/50 · trend_following 46/50 · vwap_reversion 46/50 · momentum_cross_asset 46/50 · momentum 46/50 · mean_reversion 4/50 · liquidity_grab 4/50
  REGIME GATE vs LIVE: discordano su 0/50 eventi (0%). Il gate usa il regime della coin, il bot dal vivo quello di bitcoin per tutte.
  trade aperti durante gli spike:
    trend_following         247 trade ·   +32.1% · win   68% · 0 chiusi per scadenza
    momentum                220 trade ·   +11.2% · win   62% · 0 chiusi per scadenza
    breakout                260 trade ·    +3.0% · win   56% · 0 chiusi per scadenza
    liquidity_grab          104 trade ·    -4.2% · win   56% · 0 chiusi per scadenza
    grid_trading            152 trade ·    -7.9% · win   53% · 1 chiusi per scadenza
    mean_reversion           96 trade ·   -21.2% · win   43% · 0 chiusi per scadenza
    vwap_reversion          491 trade ·   -95.2% · win   48% · 1 chiusi per scadenza
  QUANTO PESANO: 3% del profitto totale del periodo arriva da questi trade,
  che coprono il 5% delle barre.

[backtest] dati da cache: 167521 candele (ETHUSDT 15m)
=== ETHUSDT ===
  eventi: 111 (dal 05 Jan 2022 al 20 Aug 2026)
  regime al momento dello spike: bull_trending 54 · bear_trending 42 · high_uncertainty 14 · sideways 1
  accese (su quanti eventi): funding_arbitrage 111/111 · breakout 110/111 · vwap_reversion 97/111 · trend_following 96/111 · momentum_cross_asset 96/111 · momentum 96/111 · mean_reversion 15/111 · liquidity_grab 15/111 · grid_trading 1/111
  REGIME GATE vs LIVE: discordano su 24/111 eventi (22%). Il gate usa il regime della coin, il bot dal vivo quello di bitcoin per tutte.
  trade aperti durante gli spike:
    momentum                524 trade ·  +165.3% · win   69% · 1 chiusi per scadenza
    trend_following         574 trade ·   +79.5% · win   64% · 0 chiusi per scadenza
    breakout                559 trade ·   +53.7% · win   61% · 0 chiusi per scadenza
    liquidity_grab          199 trade ·   -14.3% · win   53% · 0 chiusi per scadenza
    grid_trading            388 trade ·   -22.3% · win   48% · 0 chiusi per scadenza
    mean_reversion          204 trade ·   -53.5% · win   47% · 0 chiusi per scadenza
    vwap_reversion         1105 trade ·  -264.1% · win   49% · 1 chiusi per scadenza
  QUANTO PESANO: 2% del profitto totale del periodo arriva da questi trade,
  che coprono il 11% delle barre.

[backtest] dati da cache: 167521 candele (SOLUSDT 15m)
=== SOLUSDT ===
  eventi: 279 (dal 04 Jan 2022 al 17 Sep 2026)
  regime al momento dello spike: bull_trending 136 · bear_trending 100 · high_uncertainty 37 · sideways 6
  accese (su quanti eventi): funding_arbitrage 279/279 · breakout 273/279 · vwap_reversion 242/279 · trend_following 236/279 · momentum_cross_asset 236/279 · momentum 236/279 · mean_reversion 43/279 · liquidity_grab 43/279 · grid_trading 6/279
  REGIME GATE vs LIVE: discordano su 103/279 eventi (37%). Il gate usa il regime della coin, il bot dal vivo quello di bitcoin per tutte.
  trade aperti durante gli spike:
    trend_following        1503 trade ·  +164.2% · win   62% · 0 chiusi per scadenza
    momentum               1271 trade ·   +65.1% · win   60% · 0 chiusi per scadenza
    breakout               1217 trade ·   +40.9% · win   58% · 0 chiusi per scadenza
    liquidity_grab          368 trade ·   -32.6% · win   55% · 0 chiusi per scadenza
    grid_trading            822 trade ·   -95.2% · win   49% · 2 chiusi per scadenza
    mean_reversion          377 trade ·  -102.4% · win   44% · 0 chiusi per scadenza
    vwap_reversion         2542 trade ·  -733.5% · win   49% · 1 chiusi per scadenza
  QUANTO PESANO: 22% del profitto totale del periodo arriva da questi trade,
  che coprono il 27% delle barre.
```
