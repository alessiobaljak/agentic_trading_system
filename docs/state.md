# Stato sistema (snapshot)
_Generato: 2026-06-19 05:25 UTC_

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
- copertura universo: **38/50 crypto (76%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **48**
- universo scansionato: AAVEUSDT, ADAUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, FLOKIUSDT, FTMUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT
- aggiornato: 2026-06-18 21:58 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TONUSDT | trend_following | 4 | 1.166 | 376% | rr=2.5, rsi_hi=75.0, atr_mult_stop=2.0, require_volume=False |
| FTMUSDT | trend_following | 4 | 1.137 | 274% | rr=2.5, rsi_hi=75.0, atr_mult_stop=2.0, require_volume=False |
| VETUSDT | trend_following | 4 | 1.137 | 274% | rr=2.5, rsi_hi=75.0, atr_mult_stop=2.0, require_volume=False |
| RUNEUSDT | trend_following | 3 | 1.137 | 270% | rr=2.5, rsi_hi=70.0, atr_mult_stop=2.0, require_volume=False |
| TIAUSDT | trend_following | 3 | 1.126 | 129% | rr=1.5, rsi_hi=75.0, atr_mult_stop=2.0, require_volume=False |
| ORDIUSDT | trend_following | 3 | 1.107 | 115% | rr=2.5, rsi_hi=65.0, atr_mult_stop=1.0, require_volume=True |
| WIFUSDT | breakout | 4 | 1.263 | 98% | compression=0.1, rr=3.0, volume_spike=1.8 |
| INJUSDT | mean_reversion | 7 | 1.846 | 79% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.8 |
| ALGOUSDT | mean_reversion | 6 | 1.503 | 76% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.8 |
| SUIUSDT | mean_reversion | 7 | 1.444 | 74% | rsi_overbought=75.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| AVAXUSDT | breakout | 6 | 1.186 | 73% | compression=0.05, rr=2.0, volume_spike=1.8 |
| PEPEUSDT | breakout | 3 | 1.218 | 62% | compression=0.1, rr=3.0, volume_spike=1.5 |
| GALAUSDT | mean_reversion | 6 | 1.544 | 60% | rsi_overbought=80.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| FILUSDT | mean_reversion | 7 | 1.344 | 54% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| SUIUSDT | breakout | 5 | 1.275 | 53% | compression=0.1, rr=2.5, volume_spike=1.8 |
| EGLDUSDT | mean_reversion | 5 | 1.532 | 48% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.0 |
| ARBUSDT | mean_reversion | 5 | 1.488 | 43% | rsi_overbought=80.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| UNIUSDT | mean_reversion | 4 | 1.386 | 43% | rsi_overbought=75.0, rsi_oversold=20.0, atr_mult_stop=1.0 |
| APTUSDT | breakout | 3 | 1.134 | 38% | compression=0.05, rr=2.0, volume_spike=1.8 |
| HBARUSDT | mean_reversion | 6 | 1.235 | 35% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| ENAUSDT | breakout | 5 | 1.515 | 34% | compression=0.07, rr=2.5, volume_spike=1.8 |
| XRPUSDT | mean_reversion | 4 | 1.358 | 34% | rsi_overbought=80.0, rsi_oversold=30.0, atr_mult_stop=1.8 |
| IMXUSDT | mean_reversion | 5 | 1.275 | 32% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| STXUSDT | mean_reversion | 6 | 1.236 | 32% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.8 |
| ETCUSDT | mean_reversion | 6 | 1.251 | 32% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.8 |
| BONKUSDT | breakout | 4 | 1.159 | 31% | compression=0.1, rr=2.5, volume_spike=1.5 |
| APTUSDT | mean_reversion | 6 | 1.211 | 29% | rsi_overbought=70.0, rsi_oversold=30.0, atr_mult_stop=1.2 |
| LTCUSDT | mean_reversion | 4 | 1.256 | 28% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| JUPUSDT | breakout | 6 | 1.142 | 28% | compression=0.05, rr=3.0, volume_spike=1.8 |
| AAVEUSDT | mean_reversion | 6 | 1.243 | 28% | rsi_overbought=80.0, rsi_oversold=25.0, atr_mult_stop=1.2 |
| ATOMUSDT | mean_reversion | 6 | 1.396 | 27% | rsi_overbought=75.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| VETUSDT | momentum_cross_asset | 4 | 1.24 | 26% | rr=2.0, btc_move_threshold=0.4, atr_mult_stop=1.0 |
| ORDIUSDT | mean_reversion | 3 | 1.114 | 22% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| DOGEUSDT | mean_reversion | 3 | 1.138 | 21% | rsi_overbought=80.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| OPUSDT | mean_reversion | 3 | 1.128 | 20% | rsi_overbought=75.0, rsi_oversold=20.0, atr_mult_stop=1.0 |
| WIFUSDT | liquidity_grab | 5 | 1.44 | 20% | volume_spike=3.0, atr_mult_stop=1.5 |
| ALGOUSDT | liquidity_grab | 6 | 1.409 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| PYTHUSDT | mean_reversion | 4 | 1.218 | 19% | rsi_overbought=70.0, rsi_oversold=25.0, atr_mult_stop=1.2 |
| ARBUSDT | liquidity_grab | 6 | 1.906 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| DOTUSDT | mean_reversion | 4 | 1.206 | 18% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.2 |
| SEIUSDT | breakout | 6 | 1.38 | 18% | compression=0.1, rr=2.0, volume_spike=1.5 |
| ADAUSDT | mean_reversion | 6 | 1.167 | 17% | rsi_overbought=80.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| SANDUSDT | mean_reversion | 4 | 1.135 | 16% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| AVAXUSDT | mean_reversion | 4 | 1.118 | 14% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| PYTHUSDT | liquidity_grab | 6 | 1.27 | 13% | volume_spike=2.5, atr_mult_stop=1.5 |
| ETHUSDT | mean_reversion | 4 | 1.1 | 9% | rsi_overbought=70.0, rsi_oversold=25.0, atr_mult_stop=1.8 |
| IMXUSDT | liquidity_grab | 7 | 1.1 | 5% | volume_spike=2.5, atr_mult_stop=0.8 |
| SOLUSDT | liquidity_grab | 7 | 1.105 | 5% | volume_spike=2.5, atr_mult_stop=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-18 21:58 UTC · 350 coppie valutate, 46 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| TONUSDT | trend_following | 1.166 | 376% | 1388 | 33% |
| WLDUSDT | trend_following | 1.243 | 279% | 580 | 44% |
| FTMUSDT | trend_following | 1.137 | 274% | 1495 | 38% |
| VETUSDT | trend_following | 1.137 | 274% | 1495 | 38% |
| RUNEUSDT | trend_following | 1.137 | 270% | 1184 | 33% |
| GALAUSDT | trend_following | 1.1 | 158% | 789 | 38% |
| TIAUSDT | trend_following | 1.126 | 129% | 482 | 38% |
| WIFUSDT | breakout | 1.263 | 98% | 285 | 32% |
| DOGEUSDT | breakout | 1.245 | 85% | 419 | 30% |
| INJUSDT | mean_reversion | 1.846 | 79% | 40 | 42% |
| ALGOUSDT | mean_reversion | 1.503 | 76% | 68 | 26% |
| SUIUSDT | mean_reversion | 1.444 | 74% | 64 | 42% |
| AVAXUSDT | breakout | 1.186 | 73% | 501 | 40% |
| GALAUSDT | breakout | 1.189 | 67% | 359 | 38% |
| GALAUSDT | mean_reversion | 1.544 | 60% | 37 | 38% |
| FILUSDT | mean_reversion | 1.344 | 54% | 56 | 39% |
| SUIUSDT | breakout | 1.275 | 53% | 198 | 35% |
| EGLDUSDT | mean_reversion | 1.532 | 48% | 42 | 36% |
| ARBUSDT | mean_reversion | 1.488 | 43% | 42 | 26% |
| UNIUSDT | mean_reversion | 1.386 | 43% | 55 | 33% |
| TONUSDT | momentum_cross_asset | 1.294 | 38% | 135 | 38% |
| APTUSDT | breakout | 1.134 | 38% | 298 | 35% |
| HBARUSDT | mean_reversion | 1.235 | 35% | 41 | 34% |
| FLOKIUSDT | mean_reversion | 1.184 | 35% | 49 | 37% |
| XRPUSDT | mean_reversion | 1.358 | 34% | 55 | 34% |
| IMXUSDT | mean_reversion | 1.275 | 32% | 42 | 36% |
| STXUSDT | mean_reversion | 1.236 | 32% | 49 | 37% |
| ETCUSDT | mean_reversion | 1.251 | 32% | 73 | 36% |
| BONKUSDT | breakout | 1.159 | 31% | 192 | 34% |
| APTUSDT | mean_reversion | 1.211 | 29% | 61 | 34% |
| JUPUSDT | breakout | 1.142 | 28% | 216 | 41% |
| AAVEUSDT | mean_reversion | 1.243 | 28% | 40 | 40% |
| ATOMUSDT | mean_reversion | 1.396 | 27% | 27 | 33% |
| INJUSDT | breakout | 1.111 | 26% | 202 | 31% |
| FTMUSDT | momentum_cross_asset | 1.24 | 26% | 138 | 44% |
| VETUSDT | momentum_cross_asset | 1.24 | 26% | 138 | 44% |
| WIFUSDT | liquidity_grab | 1.44 | 20% | 43 | 65% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| DOTUSDT | mean_reversion | 1.206 | 18% | 46 | 26% |
| SEIUSDT | breakout | 1.38 | 18% | 61 | 44% |
| ADAUSDT | mean_reversion | 1.167 | 17% | 46 | 33% |
| AVAXUSDT | mean_reversion | 1.118 | 14% | 48 | 35% |
| PYTHUSDT | liquidity_grab | 1.27 | 13% | 52 | 58% |
| IMXUSDT | liquidity_grab | 1.1 | 5% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
