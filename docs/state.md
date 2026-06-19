# Stato sistema (snapshot)
_Generato: 2026-06-19 13:38 UTC_

## Bot
- stato: **running** (🔴 offline)
- regime: bear_trending
- DRY_RUN: True
- equity: **$10,000.00**
- ultimo heartbeat: 2026-06-17 14:13 UTC

## Ultima decisione
- esito: **🟢 APERTA** (2026-06-17 14:02 UTC)
- motivo: aperta WLDUSDT short (trend_following)
- asset valutati: 30 · segnali: 1 · miglior segnale WLDUSDT trend_following (conf. 60.6/soglia 30)

## Posizioni aperte
- WLDUSDT: short qty=4376.5831623312115 @ 0.6543 uPnL=-15.584706280240159

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **39/50 crypto (78%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **53**
- universo scansionato: AAVEUSDT, ADAUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, FLOKIUSDT, FTMUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT
- aggiornato: 2026-06-19 12:07 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| FTMUSDT | trend_following | 5 | 1.151 | 313% | rr=2.5, rsi_hi=75.0, require_volume=True, atr_mult_stop=1.5 |
| VETUSDT | trend_following | 6 | 1.115 | 263% | rr=2.5, rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0 |
| TONUSDT | trend_following | 6 | 1.101 | 236% | rr=2.0, rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0 |
| RUNEUSDT | trend_following | 5 | 1.104 | 230% | rr=2.0, rsi_hi=70.0, require_volume=False, atr_mult_stop=2.0 |
| ALGOUSDT | mean_reversion | 8 | 2.038 | 156% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| WLDUSDT | trend_following | 3 | 1.129 | 141% | rr=2.5, rsi_hi=75.0, require_volume=True, atr_mult_stop=1.0 |
| TIAUSDT | trend_following | 3 | 1.126 | 129% | rr=1.5, rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0 |
| ORDIUSDT | trend_following | 3 | 1.107 | 115% | rr=2.5, rsi_hi=65.0, require_volume=True, atr_mult_stop=1.0 |
| SUIUSDT | mean_reversion | 9 | 1.695 | 108% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| AVAXUSDT | breakout | 8 | 1.268 | 103% | rr=2.5, compression=0.05, volume_spike=1.8 |
| GALAUSDT | mean_reversion | 8 | 1.469 | 89% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| FILUSDT | breakout | 3 | 1.134 | 88% | rr=3.0, compression=0.1, volume_spike=1.5 |
| STXUSDT | mean_reversion | 8 | 1.787 | 77% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| WIFUSDT | breakout | 6 | 1.299 | 76% | rr=3.0, compression=0.1, volume_spike=2.5 |
| INJUSDT | mean_reversion | 9 | 1.754 | 67% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| SUIUSDT | breakout | 7 | 1.791 | 66% | rr=3.0, compression=0.05, volume_spike=2.5 |
| PEPEUSDT | breakout | 5 | 1.158 | 58% | rr=3.0, compression=0.1, volume_spike=1.5 |
| APTUSDT | breakout | 4 | 1.121 | 50% | rr=2.5, compression=0.07, volume_spike=1.8 |
| IMXUSDT | mean_reversion | 7 | 1.455 | 50% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| EGLDUSDT | mean_reversion | 7 | 1.532 | 48% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| ATOMUSDT | mean_reversion | 8 | 1.572 | 48% | rsi_oversold=20.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| GALAUSDT | breakout | 3 | 1.11 | 47% | rr=3.0, compression=0.07, volume_spike=1.8 |
| FILUSDT | mean_reversion | 9 | 1.357 | 46% | rsi_oversold=20.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| APTUSDT | mean_reversion | 8 | 1.415 | 41% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| ETCUSDT | mean_reversion | 8 | 1.318 | 41% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| UNIUSDT | mean_reversion | 5 | 1.34 | 41% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| HBARUSDT | mean_reversion | 8 | 1.259 | 40% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| DOTUSDT | mean_reversion | 6 | 1.528 | 37% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.2 |
| ENAUSDT | trend_following | 3 | 1.111 | 36% | rr=2.5, rsi_hi=75.0, require_volume=False, atr_mult_stop=1.5 |
| ADAUSDT | mean_reversion | 8 | 1.355 | 33% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| OPUSDT | mean_reversion | 5 | 1.202 | 32% | rsi_oversold=20.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| DOGEUSDT | mean_reversion | 5 | 1.161 | 31% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| XRPUSDT | mean_reversion | 5 | 1.264 | 31% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| ARBUSDT | mean_reversion | 7 | 1.348 | 31% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| BONKUSDT | breakout | 4 | 1.159 | 31% | rr=2.5, compression=0.1, volume_spike=1.5 |
| JUPUSDT | breakout | 8 | 1.128 | 31% | rr=1.5, compression=0.05, volume_spike=1.5 |
| ORDIUSDT | mean_reversion | 4 | 1.104 | 29% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| LTCUSDT | mean_reversion | 4 | 1.256 | 28% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| RUNEUSDT | momentum_cross_asset | 4 | 1.199 | 28% | rr=2.5, atr_mult_stop=2.0, btc_move_threshold=0.4 |
| PYTHUSDT | mean_reversion | 6 | 1.277 | 26% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| AAVEUSDT | mean_reversion | 8 | 1.261 | 22% | rsi_oversold=25.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| SEIUSDT | breakout | 8 | 1.395 | 21% | rr=2.5, compression=0.1, volume_spike=1.5 |
| VETUSDT | momentum_cross_asset | 5 | 1.147 | 20% | rr=1.5, atr_mult_stop=2.0, btc_move_threshold=0.4 |
| WIFUSDT | liquidity_grab | 7 | 1.44 | 20% | volume_spike=3.0, atr_mult_stop=1.5 |
| ALGOUSDT | liquidity_grab | 8 | 1.409 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| ARBUSDT | liquidity_grab | 8 | 1.906 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| SANDUSDT | mean_reversion | 4 | 1.135 | 16% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| ENAUSDT | breakout | 7 | 1.379 | 16% | rr=2.0, compression=0.07, volume_spike=2.5 |
| AVAXUSDT | mean_reversion | 5 | 1.12 | 15% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| PYTHUSDT | liquidity_grab | 8 | 1.27 | 13% | volume_spike=2.5, atr_mult_stop=1.5 |
| ETHUSDT | mean_reversion | 4 | 1.1 | 9% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| IMXUSDT | liquidity_grab | 9 | 1.1 | 5% | volume_spike=2.5, atr_mult_stop=0.8 |
| SOLUSDT | liquidity_grab | 9 | 1.105 | 5% | volume_spike=2.5, atr_mult_stop=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-19 12:07 UTC · 350 coppie valutate, 49 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| VETUSDT | trend_following | 1.115 | 263% | 1412 | 34% |
| TONUSDT | trend_following | 1.101 | 236% | 1453 | 35% |
| RUNEUSDT | trend_following | 1.104 | 230% | 1404 | 35% |
| ALGOUSDT | mean_reversion | 2.038 | 156% | 66 | 44% |
| XRPUSDT | trend_following | 1.125 | 125% | 650 | 37% |
| SUIUSDT | mean_reversion | 1.695 | 108% | 59 | 48% |
| AVAXUSDT | breakout | 1.268 | 103% | 438 | 34% |
| GALAUSDT | mean_reversion | 1.469 | 89% | 74 | 40% |
| FILUSDT | breakout | 1.134 | 88% | 627 | 30% |
| STXUSDT | mean_reversion | 1.787 | 77% | 42 | 45% |
| WIFUSDT | breakout | 1.299 | 76% | 190 | 35% |
| INJUSDT | mean_reversion | 1.754 | 67% | 32 | 47% |
| SUIUSDT | breakout | 1.791 | 66% | 98 | 37% |
| FLOKIUSDT | breakout | 1.175 | 60% | 306 | 33% |
| PEPEUSDT | breakout | 1.158 | 58% | 319 | 29% |
| ORDIUSDT | breakout | 1.289 | 56% | 172 | 36% |
| APTUSDT | breakout | 1.121 | 50% | 410 | 34% |
| IMXUSDT | mean_reversion | 1.455 | 50% | 40 | 38% |
| IMXUSDT | breakout | 1.1 | 49% | 419 | 30% |
| EGLDUSDT | mean_reversion | 1.532 | 48% | 42 | 36% |
| ATOMUSDT | mean_reversion | 1.572 | 48% | 33 | 42% |
| GALAUSDT | breakout | 1.11 | 47% | 420 | 34% |
| FILUSDT | mean_reversion | 1.357 | 46% | 40 | 35% |
| APTUSDT | mean_reversion | 1.415 | 41% | 49 | 33% |
| ETCUSDT | mean_reversion | 1.318 | 41% | 75 | 33% |
| HBARUSDT | mean_reversion | 1.259 | 40% | 44 | 39% |
| DOTUSDT | mean_reversion | 1.528 | 37% | 43 | 35% |
| ENAUSDT | trend_following | 1.111 | 36% | 204 | 40% |
| SHIBUSDT | breakout | 1.104 | 34% | 435 | 32% |
| ADAUSDT | mean_reversion | 1.355 | 33% | 35 | 37% |
| OPUSDT | mean_reversion | 1.202 | 32% | 62 | 32% |
| DOGEUSDT | mean_reversion | 1.161 | 31% | 89 | 38% |
| XRPUSDT | mean_reversion | 1.264 | 31% | 83 | 34% |
| ARBUSDT | mean_reversion | 1.348 | 31% | 34 | 29% |
| JUPUSDT | breakout | 1.128 | 31% | 242 | 36% |
| RUNEUSDT | momentum_cross_asset | 1.199 | 28% | 134 | 39% |
| PYTHUSDT | mean_reversion | 1.277 | 26% | 36 | 36% |
| AAVEUSDT | mean_reversion | 1.261 | 22% | 29 | 34% |
| SEIUSDT | breakout | 1.395 | 21% | 64 | 39% |
| TONUSDT | momentum_cross_asset | 1.279 | 21% | 98 | 45% |
| VETUSDT | momentum_cross_asset | 1.147 | 20% | 135 | 40% |
| WIFUSDT | liquidity_grab | 1.44 | 20% | 43 | 65% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| ENAUSDT | breakout | 1.379 | 16% | 48 | 40% |
| AVAXUSDT | mean_reversion | 1.12 | 15% | 50 | 36% |
| PYTHUSDT | liquidity_grab | 1.27 | 13% | 52 | 58% |
| IMXUSDT | liquidity_grab | 1.1 | 5% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
