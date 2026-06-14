# Stato sistema (snapshot)
_Generato: 2026-06-14 05:07 UTC_

## Bot
- stato: **—** (🔴 offline)
- regime: —
- DRY_RUN: —
- ultimo heartbeat: —

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **13/20 crypto (65%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **20**
- aggiornato: 2026-06-14 04:38 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 4 | 1.292 | 238% | atr_mult_stop=1.5, rr=2.0, rsi_hi=75.0, require_volume=False |
| KATUSDT | vwap_reversion | 3 | 1.268 | 195% | deviation_atr=2.0, atr_mult_stop=1.0 |
| SPACEUSDT | vwap_reversion | 4 | 1.268 | 195% | deviation_atr=2.0, atr_mult_stop=1.0 |
| SATSUSDT | trend_following | 4 | 1.211 | 156% | atr_mult_stop=2.0, rr=2.0, rsi_hi=70.0, require_volume=False |
| PENGUUSDT | vwap_reversion | 4 | 1.278 | 114% | deviation_atr=2.5, atr_mult_stop=1.5 |
| SATSUSDT | mean_reversion | 4 | 1.38 | 57% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| SHIBUSDT | breakout | 4 | 1.395 | 55% | compression=0.05, rr=2.5, volume_spike=1.5 |
| NOTUSDT | mean_reversion | 4 | 1.816 | 49% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=75.0 |
| BOMEUSDT | mean_reversion | 4 | 1.347 | 45% | atr_mult_stop=1.2, rsi_oversold=30.0, rsi_overbought=80.0 |
| BONKUSDT | mean_reversion | 4 | 1.411 | 43% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=70.0 |
| BONKUSDT | breakout | 4 | 1.391 | 40% | compression=0.05, rr=3.0, volume_spike=1.5 |
| HMSTRUSDT | liquidity_grab | 4 | 3.334 | 39% | atr_mult_stop=1.5, volume_spike=2.5 |
| BOMEUSDT | breakout | 4 | 1.287 | 39% | compression=0.07, rr=3.0, volume_spike=1.5 |
| PUMPUSDT | mean_reversion | 3 | 1.476 | 23% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=70.0 |
| PUMPUSDT | breakout | 3 | 1.619 | 19% | compression=0.07, rr=2.5, volume_spike=1.5 |
| FLOKIUSDT | liquidity_grab | 4 | 1.254 | 18% | atr_mult_stop=0.8, volume_spike=2.0 |
| PEPEUSDT | mean_reversion | 4 | 1.132 | 16% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=70.0 |
| NOTUSDT | liquidity_grab | 4 | 1.349 | 12% | atr_mult_stop=0.8, volume_spike=2.0 |
| BONKUSDT | liquidity_grab | 4 | 1.201 | 11% | atr_mult_stop=0.8, volume_spike=2.5 |
| LINEAUSDT | breakout | 4 | 1.105 | 4% | compression=0.1, rr=1.5, volume_spike=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-14 04:38 UTC · 120 coppie valutate, 28 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 1.292 | 238% | 373 | 36% |
| SPACEUSDT | vwap_reversion | 1.268 | 195% | 625 | 16% |
| MEGAUSDT | vwap_reversion | 1.268 | 195% | 625 | 16% |
| SATSUSDT | trend_following | 1.211 | 156% | 328 | 40% |
| PENGUUSDT | vwap_reversion | 1.278 | 114% | 213 | 16% |
| DOGEUSDT | trend_following | 1.102 | 69% | 456 | 39% |
| SATSUSDT | mean_reversion | 1.38 | 57% | 59 | 37% |
| SHIBUSDT | breakout | 1.395 | 55% | 184 | 35% |
| OLUSDT | vwap_reversion | 3.498 | 49% | 17 | 24% |
| NOTUSDT | mean_reversion | 1.816 | 49% | 25 | 44% |
| BOMEUSDT | mean_reversion | 1.347 | 45% | 42 | 43% |
| BONKUSDT | mean_reversion | 1.411 | 43% | 37 | 35% |
| BONKUSDT | breakout | 1.391 | 40% | 101 | 34% |
| HMSTRUSDT | liquidity_grab | 3.334 | 39% | 45 | 80% |
| BOMEUSDT | breakout | 1.287 | 39% | 113 | 34% |
| GALAUSDT | mean_reversion | 1.712 | 32% | 18 | 39% |
| PENGUUSDT | breakout | 1.266 | 28% | 82 | 30% |
| PUMPUSDT | mean_reversion | 1.476 | 23% | 21 | 38% |
| MEMEUSDT | mean_reversion | 1.17 | 22% | 38 | 32% |
| PUMPUSDT | breakout | 1.619 | 19% | 26 | 42% |
| XPLUSDT | breakout | 1.52 | 18% | 29 | 52% |
| FLOKIUSDT | liquidity_grab | 1.254 | 18% | 74 | 49% |
| PEPEUSDT | mean_reversion | 1.132 | 16% | 42 | 29% |
| PENGUUSDT | mean_reversion | 1.133 | 14% | 38 | 34% |
| NOTUSDT | liquidity_grab | 1.349 | 12% | 55 | 49% |
| BONKUSDT | liquidity_grab | 1.201 | 11% | 50 | 46% |
| LINEAUSDT | breakout | 1.105 | 4% | 41 | 39% |
| OLUSDT | grid_trading | 1.154 | 3% | 47 | 49% |
