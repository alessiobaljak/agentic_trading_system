# Stato sistema (snapshot)
_Generato: 2026-06-14 15:58 UTC_

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
| TURBOUSDT | trend_following | 7 | 1.28 | 228% | rr=2.0, atr_mult_stop=1.5, rsi_hi=75.0, require_volume=False |
| KATUSDT | vwap_reversion | 3 | 1.268 | 195% | deviation_atr=2.0, atr_mult_stop=1.0 |
| MEGAUSDT | vwap_reversion | 4 | 1.247 | 181% | deviation_atr=2.0, atr_mult_stop=1.0 |
| SPACEUSDT | vwap_reversion | 7 | 1.247 | 181% | deviation_atr=2.0, atr_mult_stop=1.0 |
| SATSUSDT | trend_following | 7 | 1.197 | 146% | rr=2.0, atr_mult_stop=2.0, rsi_hi=70.0, require_volume=False |
| PENGUUSDT | vwap_reversion | 4 | 1.278 | 114% | deviation_atr=2.5, atr_mult_stop=1.5 |
| DOGEUSDT | trend_following | 4 | 1.147 | 106% | rr=2.5, atr_mult_stop=1.5, rsi_hi=75.0, require_volume=False |
| NOTUSDT | mean_reversion | 7 | 2.212 | 88% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| SATSUSDT | mean_reversion | 7 | 1.371 | 56% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| SHIBUSDT | breakout | 7 | 1.381 | 53% | volume_spike=1.5, compression=0.05, rr=2.5 |
| BOMEUSDT | mean_reversion | 7 | 1.339 | 44% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.2 |
| BONKUSDT | mean_reversion | 7 | 1.401 | 42% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| BONKUSDT | breakout | 7 | 1.381 | 40% | volume_spike=1.5, compression=0.05, rr=3.0 |
| HMSTRUSDT | liquidity_grab | 7 | 3.31 | 39% | volume_spike=2.5, atr_mult_stop=1.5 |
| GALAUSDT | mean_reversion | 4 | 1.956 | 39% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.2 |
| BOMEUSDT | breakout | 7 | 1.279 | 38% | volume_spike=1.5, compression=0.07, rr=3.0 |
| MEMEUSDT | breakout | 4 | 1.314 | 34% | volume_spike=1.8, compression=0.05, rr=3.0 |
| PUMPUSDT | mean_reversion | 3 | 1.476 | 23% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| MEMEUSDT | mean_reversion | 3 | 1.152 | 21% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| PUMPUSDT | breakout | 3 | 1.619 | 19% | volume_spike=1.5, compression=0.07, rr=2.5 |
| FLOKIUSDT | liquidity_grab | 7 | 1.248 | 17% | volume_spike=2.0, atr_mult_stop=0.8 |
| PEPEUSDT | mean_reversion | 7 | 1.125 | 15% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| GALAUSDT | breakout | 3 | 1.132 | 15% | volume_spike=1.8, compression=0.05, rr=2.0 |
| NOTUSDT | liquidity_grab | 7 | 1.343 | 12% | volume_spike=2.0, atr_mult_stop=0.8 |
| BONKUSDT | liquidity_grab | 7 | 1.196 | 11% | volume_spike=2.5, atr_mult_stop=0.8 |
| LINEAUSDT | breakout | 4 | 1.105 | 4% | volume_spike=1.5, compression=0.1, rr=1.5 |

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
