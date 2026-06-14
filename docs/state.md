# Stato sistema (snapshot)
_Generato: 2026-06-14 17:48 UTC_

## Bot
- stato: **—** (🔴 offline)
- regime: —
- DRY_RUN: —
- ultimo heartbeat: —

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **14/15 crypto (93%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **26**
- aggiornato: 2026-06-14 14:30 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 7 | 1.28 | 228% | atr_mult_stop=1.5, rr=2.0, require_volume=False, rsi_hi=75.0 |
| KATUSDT | vwap_reversion | 3 | 1.268 | 195% | atr_mult_stop=1.0, deviation_atr=2.0 |
| MEGAUSDT | vwap_reversion | 4 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SPACEUSDT | vwap_reversion | 7 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SATSUSDT | trend_following | 7 | 1.197 | 146% | atr_mult_stop=2.0, rr=2.0, require_volume=False, rsi_hi=70.0 |
| PENGUUSDT | vwap_reversion | 4 | 1.278 | 114% | atr_mult_stop=1.5, deviation_atr=2.5 |
| DOGEUSDT | trend_following | 4 | 1.147 | 106% | atr_mult_stop=1.5, rr=2.5, require_volume=False, rsi_hi=75.0 |
| NOTUSDT | mean_reversion | 7 | 2.212 | 88% | atr_mult_stop=1.0, rsi_overbought=75.0, rsi_oversold=30.0 |
| SATSUSDT | mean_reversion | 7 | 1.371 | 56% | atr_mult_stop=1.2, rsi_overbought=70.0, rsi_oversold=20.0 |
| SHIBUSDT | breakout | 7 | 1.381 | 53% | rr=2.5, volume_spike=1.5, compression=0.05 |
| BOMEUSDT | mean_reversion | 7 | 1.339 | 44% | atr_mult_stop=1.2, rsi_overbought=80.0, rsi_oversold=30.0 |
| BONKUSDT | mean_reversion | 7 | 1.401 | 42% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| BONKUSDT | breakout | 7 | 1.381 | 40% | rr=3.0, volume_spike=1.5, compression=0.05 |
| HMSTRUSDT | liquidity_grab | 7 | 3.31 | 39% | atr_mult_stop=1.5, volume_spike=2.5 |
| GALAUSDT | mean_reversion | 4 | 1.956 | 39% | atr_mult_stop=1.2, rsi_overbought=80.0, rsi_oversold=30.0 |
| BOMEUSDT | breakout | 7 | 1.279 | 38% | rr=3.0, volume_spike=1.5, compression=0.07 |
| MEMEUSDT | breakout | 4 | 1.314 | 34% | rr=3.0, volume_spike=1.8, compression=0.05 |
| PUMPUSDT | mean_reversion | 3 | 1.476 | 23% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=30.0 |
| MEMEUSDT | mean_reversion | 3 | 1.152 | 21% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=20.0 |
| PUMPUSDT | breakout | 3 | 1.619 | 19% | rr=2.5, volume_spike=1.5, compression=0.07 |
| FLOKIUSDT | liquidity_grab | 7 | 1.248 | 17% | atr_mult_stop=0.8, volume_spike=2.0 |
| PEPEUSDT | mean_reversion | 7 | 1.125 | 15% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=20.0 |
| GALAUSDT | breakout | 3 | 1.132 | 15% | rr=2.0, volume_spike=1.8, compression=0.05 |
| NOTUSDT | liquidity_grab | 7 | 1.343 | 12% | atr_mult_stop=0.8, volume_spike=2.0 |
| BONKUSDT | liquidity_grab | 7 | 1.196 | 11% | atr_mult_stop=0.8, volume_spike=2.5 |
| LINEAUSDT | breakout | 4 | 1.105 | 4% | rr=1.5, volume_spike=1.5, compression=0.1 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-14 14:30 UTC · 90 coppie valutate, 18 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 1.28 | 228% | 373 | 36% |
| SPACEUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| MEGAUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| SATSUSDT | trend_following | 1.197 | 146% | 328 | 40% |
| NOTUSDT | mean_reversion | 2.212 | 88% | 38 | 47% |
| SATSUSDT | mean_reversion | 1.371 | 56% | 59 | 37% |
| SHIBUSDT | breakout | 1.381 | 53% | 184 | 35% |
| BOMEUSDT | mean_reversion | 1.339 | 44% | 42 | 43% |
| BONKUSDT | mean_reversion | 1.401 | 42% | 37 | 35% |
| BONKUSDT | breakout | 1.381 | 40% | 101 | 34% |
| HMSTRUSDT | liquidity_grab | 3.31 | 39% | 45 | 80% |
| BOMEUSDT | breakout | 1.279 | 38% | 113 | 34% |
| MEMEUSDT | breakout | 1.314 | 34% | 94 | 33% |
| FLOKIUSDT | liquidity_grab | 1.248 | 17% | 74 | 49% |
| PEPEUSDT | mean_reversion | 1.125 | 15% | 42 | 29% |
| GALAUSDT | breakout | 1.132 | 15% | 99 | 30% |
| NOTUSDT | liquidity_grab | 1.343 | 12% | 55 | 49% |
| BONKUSDT | liquidity_grab | 1.196 | 11% | 50 | 46% |
