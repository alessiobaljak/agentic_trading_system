# Stato sistema (snapshot)
_Generato: 2026-06-14 09:57 UTC_

## Bot
- stato: **—** (🔴 offline)
- regime: —
- DRY_RUN: —
- ultimo heartbeat: —

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **13/15 crypto (87%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **23**
- aggiornato: 2026-06-14 07:39 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 5 | 1.263 | 208% | rsi_hi=70.0, atr_mult_stop=2.0, require_volume=False, rr=2.0 |
| KATUSDT | vwap_reversion | 3 | 1.268 | 195% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SPACEUSDT | vwap_reversion | 5 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SATSUSDT | trend_following | 5 | 1.197 | 146% | rsi_hi=70.0, atr_mult_stop=2.0, require_volume=False, rr=2.0 |
| PENGUUSDT | vwap_reversion | 4 | 1.278 | 114% | atr_mult_stop=1.5, deviation_atr=2.5 |
| DOGEUSDT | trend_following | 3 | 1.147 | 106% | rsi_hi=75.0, atr_mult_stop=1.5, require_volume=False, rr=2.5 |
| SATSUSDT | mean_reversion | 5 | 1.371 | 56% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| SHIBUSDT | breakout | 5 | 1.381 | 53% | volume_spike=1.5, compression=0.05, rr=2.5 |
| NOTUSDT | mean_reversion | 5 | 1.802 | 49% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=75.0 |
| BOMEUSDT | mean_reversion | 5 | 1.339 | 44% | atr_mult_stop=1.2, rsi_oversold=30.0, rsi_overbought=80.0 |
| BONKUSDT | mean_reversion | 5 | 1.401 | 42% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=70.0 |
| BONKUSDT | breakout | 5 | 1.381 | 40% | volume_spike=1.5, compression=0.05, rr=3.0 |
| HMSTRUSDT | liquidity_grab | 5 | 3.31 | 39% | volume_spike=2.5, atr_mult_stop=1.5 |
| GALAUSDT | mean_reversion | 3 | 1.956 | 39% | atr_mult_stop=1.2, rsi_oversold=30.0, rsi_overbought=80.0 |
| BOMEUSDT | breakout | 5 | 1.279 | 38% | volume_spike=1.5, compression=0.07, rr=3.0 |
| PUMPUSDT | mean_reversion | 3 | 1.476 | 23% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=70.0 |
| MEMEUSDT | mean_reversion | 3 | 1.152 | 21% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=70.0 |
| PUMPUSDT | breakout | 3 | 1.619 | 19% | volume_spike=1.5, compression=0.07, rr=2.5 |
| FLOKIUSDT | liquidity_grab | 5 | 1.248 | 17% | volume_spike=2.0, atr_mult_stop=0.8 |
| PEPEUSDT | mean_reversion | 5 | 1.125 | 15% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=70.0 |
| NOTUSDT | liquidity_grab | 5 | 1.343 | 12% | volume_spike=2.0, atr_mult_stop=0.8 |
| BONKUSDT | liquidity_grab | 5 | 1.196 | 11% | volume_spike=2.5, atr_mult_stop=0.8 |
| LINEAUSDT | breakout | 4 | 1.105 | 4% | volume_spike=1.5, compression=0.1, rr=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-14 07:39 UTC · 90 coppie valutate, 19 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 1.263 | 208% | 318 | 38% |
| SPACEUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| MEGAUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| SATSUSDT | trend_following | 1.197 | 146% | 328 | 40% |
| DOGEUSDT | trend_following | 1.147 | 106% | 465 | 39% |
| SATSUSDT | mean_reversion | 1.371 | 56% | 59 | 37% |
| SHIBUSDT | breakout | 1.381 | 53% | 184 | 35% |
| NOTUSDT | mean_reversion | 1.802 | 49% | 25 | 44% |
| BOMEUSDT | mean_reversion | 1.339 | 44% | 42 | 43% |
| BONKUSDT | mean_reversion | 1.401 | 42% | 37 | 35% |
| BONKUSDT | breakout | 1.381 | 40% | 101 | 34% |
| HMSTRUSDT | liquidity_grab | 3.31 | 39% | 45 | 80% |
| GALAUSDT | mean_reversion | 1.956 | 39% | 18 | 44% |
| BOMEUSDT | breakout | 1.279 | 38% | 113 | 34% |
| MEMEUSDT | mean_reversion | 1.152 | 21% | 41 | 32% |
| FLOKIUSDT | liquidity_grab | 1.248 | 17% | 74 | 49% |
| PEPEUSDT | mean_reversion | 1.125 | 15% | 42 | 29% |
| NOTUSDT | liquidity_grab | 1.343 | 12% | 55 | 49% |
| BONKUSDT | liquidity_grab | 1.196 | 11% | 50 | 46% |
