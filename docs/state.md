# Stato sistema (snapshot)
_Generato: 2026-06-13 21:38 UTC_

## Bot
- stato: **—** (🔴 offline)
- regime: —
- DRY_RUN: —
- ultimo heartbeat: —

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **13/20 crypto (65%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **18**
- aggiornato: 2026-06-13 19:54 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 3 | 1.258 | 208% | atr_mult_stop=1.5, rr=2.5, require_volume=False, rsi_hi=75.0 |
| KATUSDT | vwap_reversion | 3 | 1.268 | 195% | deviation_atr=2.0, atr_mult_stop=1.0 |
| SPACEUSDT | vwap_reversion | 3 | 1.268 | 195% | deviation_atr=2.0, atr_mult_stop=1.0 |
| SATSUSDT | trend_following | 3 | 1.211 | 156% | atr_mult_stop=2.0, rr=2.0, require_volume=False, rsi_hi=70.0 |
| PENGUUSDT | vwap_reversion | 3 | 1.278 | 114% | deviation_atr=2.5, atr_mult_stop=1.5 |
| SATSUSDT | mean_reversion | 3 | 1.38 | 57% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| SHIBUSDT | breakout | 3 | 1.395 | 55% | rr=2.5, compression=0.05, volume_spike=1.5 |
| NOTUSDT | mean_reversion | 3 | 1.816 | 49% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.8 |
| BONKUSDT | mean_reversion | 3 | 1.411 | 43% | rsi_overbought=70.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| BOMEUSDT | mean_reversion | 3 | 1.3 | 42% | rsi_overbought=70.0, rsi_oversold=25.0, atr_mult_stop=1.0 |
| BONKUSDT | breakout | 3 | 1.391 | 40% | rr=3.0, compression=0.05, volume_spike=1.5 |
| HMSTRUSDT | liquidity_grab | 3 | 3.334 | 39% | volume_spike=2.5, atr_mult_stop=1.5 |
| BOMEUSDT | breakout | 3 | 1.287 | 39% | rr=3.0, compression=0.07, volume_spike=1.5 |
| FLOKIUSDT | liquidity_grab | 3 | 1.254 | 18% | volume_spike=2.0, atr_mult_stop=0.8 |
| PEPEUSDT | mean_reversion | 3 | 1.132 | 16% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| NOTUSDT | liquidity_grab | 3 | 1.349 | 12% | volume_spike=2.0, atr_mult_stop=0.8 |
| BONKUSDT | liquidity_grab | 3 | 1.201 | 11% | volume_spike=2.5, atr_mult_stop=0.8 |
| LINEAUSDT | breakout | 3 | 1.106 | 4% | rr=1.5, compression=0.1, volume_spike=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-13 19:54 UTC · 120 coppie valutate, 22 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 1.258 | 208% | 355 | 35% |
| SPACEUSDT | vwap_reversion | 1.268 | 195% | 625 | 16% |
| KATUSDT | vwap_reversion | 1.268 | 195% | 625 | 16% |
| SATSUSDT | trend_following | 1.211 | 156% | 328 | 40% |
| PENGUUSDT | vwap_reversion | 1.278 | 114% | 213 | 16% |
| SATSUSDT | mean_reversion | 1.38 | 57% | 59 | 37% |
| SHIBUSDT | breakout | 1.395 | 55% | 184 | 35% |
| NOTUSDT | mean_reversion | 1.816 | 49% | 25 | 44% |
| BONKUSDT | mean_reversion | 1.411 | 43% | 37 | 35% |
| BOMEUSDT | mean_reversion | 1.3 | 42% | 46 | 44% |
| BONKUSDT | breakout | 1.391 | 40% | 101 | 34% |
| HMSTRUSDT | liquidity_grab | 3.334 | 39% | 45 | 80% |
| BOMEUSDT | breakout | 1.287 | 39% | 113 | 34% |
| MEMEUSDT | breakout | 1.173 | 34% | 172 | 38% |
| PUMPUSDT | mean_reversion | 1.476 | 23% | 21 | 38% |
| PUMPUSDT | breakout | 1.619 | 19% | 26 | 42% |
| FLOKIUSDT | liquidity_grab | 1.254 | 18% | 74 | 49% |
| PEPEUSDT | mean_reversion | 1.132 | 16% | 42 | 29% |
| GALAUSDT | breakout | 1.151 | 16% | 96 | 30% |
| NOTUSDT | liquidity_grab | 1.349 | 12% | 55 | 49% |
| BONKUSDT | liquidity_grab | 1.201 | 11% | 50 | 46% |
| LINEAUSDT | breakout | 1.106 | 4% | 36 | 39% |
