# 0017-spike.req

_eseguito: 2026-08-21 05:32 UTC_

**richiesta:** `spike`
**eseguito:** `.venv/bin/python -m scripts.spike_response`
**esito:** codice 0 in 419.5s

```
[backtest] dati da cache: 162529 candele (BTCUSDT 15m)
[spike] soglia 10% in 24h · timeframe 15m · da 2022-01-01
[spike] ORIZZONTE del motore: 96 barre (24h) — oltre, il trade e' chiuso d'ufficio

=== BTCUSDT ===
  eventi: 49 (dal 20 Jan 2022 al 19 Aug 2026)
  regime al momento dello spike: bull_trending 22 · bear_trending 17 · high_uncertainty 10
  MAI ACCESE durante gli spike: grid_trading
  accese (su quanti eventi): breakout 49/49 · funding_arbitrage 49/49 · trend_following 39/49 · vwap_reversion 39/49 · momentum_cross_asset 39/49 · momentum 39/49 · mean_reversion 10/49 · liquidity_grab 10/49
  REGIME GATE vs LIVE: discordano su 0/49 eventi (0%). Il gate usa il regime della coin, il bot dal vivo quello di bitcoin per tutte.
  trade aperti durante gli spike:
    momentum                146 trade ·   +74.5% · win   53% · 4 chiusi per scadenza
    trend_following         135 trade ·   +58.9% · win   53% · 3 chiusi per scadenza
    grid_trading             97 trade ·    +3.4% · win   41% · 5 chiusi per scadenza
    liquidity_grab          102 trade ·    -1.5% · win   37% · 0 chiusi per scadenza
    mean_reversion          139 trade ·    -9.9% · win   34% · 0 chiusi per scadenza
    breakout                258 trade ·   -12.3% · win   40% · 0 chiusi per scadenza
    vwap_reversion          396 trade ·  -191.5% · win   27% · 5 chiusi per scadenza
  QUANTO PESANO: 3% del profitto totale del periodo arriva da questi trade,
  che coprono il 5% delle barre.

[backtest] dati da cache: 162529 candele (ETHUSDT 15m)
=== ETHUSDT ===
  eventi: 110 (dal 05 Jan 2022 al 18 Aug 2026)
  regime al momento dello spike: bull_trending 48 · bear_trending 38 · high_uncertainty 23 · sideways 1
  accese (su quanti eventi): funding_arbitrage 110/110 · breakout 109/110 · vwap_reversion 87/110 · trend_following 86/110 · momentum_cross_asset 86/110 · momentum 86/110 · mean_reversion 24/110 · liquidity_grab 24/110 · grid_trading 1/110
  REGIME GATE vs LIVE: discordano su 25/110 eventi (23%). Il gate usa il regime della coin, il bot dal vivo quello di bitcoin per tutte.
  trade aperti durante gli spike:
    momentum                354 trade ·  +190.0% · win   53% · 6 chiusi per scadenza
    trend_following         319 trade ·  +155.9% · win   53% · 3 chiusi per scadenza
    breakout                531 trade ·   +73.0% · win   49% · 0 chiusi per scadenza
    grid_trading            334 trade ·    +9.8% · win   36% · 5 chiusi per scadenza
    liquidity_grab          179 trade ·   -20.4% · win   33% · 0 chiusi per scadenza
    mean_reversion          261 trade ·   -85.0% · win   30% · 1 chiusi per scadenza
    vwap_reversion          832 trade ·  -438.7% · win   25% · 12 chiusi per scadenza
  QUANTO PESANO: 4% del profitto totale del periodo arriva da questi trade,
  che coprono il 12% delle barre.

[backtest] dati da cache: 162529 candele (SOLUSDT 15m)
=== SOLUSDT ===
  eventi: 276 (dal 04 Jan 2022 al 18 Aug 2026)
  regime al momento dello spike: bull_trending 107 · high_uncertainty 90 · bear_trending 73 · sideways 6
  accese (su quanti eventi): funding_arbitrage 276/276 · breakout 270/276 · vwap_reversion 186/276 · trend_following 180/276 · momentum_cross_asset 180/276 · momentum 180/276 · mean_reversion 96/276 · liquidity_grab 96/276 · grid_trading 6/276
  REGIME GATE vs LIVE: discordano su 127/276 eventi (46%). Il gate usa il regime della coin, il bot dal vivo quello di bitcoin per tutte.
  trade aperti durante gli spike:
    trend_following         750 trade ·  +276.9% · win   50% · 7 chiusi per scadenza
    momentum                786 trade ·  +227.9% · win   49% · 5 chiusi per scadenza
    breakout               1176 trade ·   +64.4% · win   45% · 0 chiusi per scadenza
    grid_trading            659 trade ·   -18.0% · win   39% · 7 chiusi per scadenza
    liquidity_grab          397 trade ·   -47.1% · win   38% · 0 chiusi per scadenza
    mean_reversion          577 trade ·  -210.3% · win   31% · 4 chiusi per scadenza
    vwap_reversion         1733 trade ·  -821.4% · win   30% · 17 chiusi per scadenza
  QUANTO PESANO: 18% del profitto totale del periodo arriva da questi trade,
  che coprono il 27% delle barre.
```
