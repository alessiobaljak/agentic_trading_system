# Stato sistema (snapshot)
_Generato: 2026-06-22 12:26 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$9,668.49**
- ultimo heartbeat: 2026-06-22 12:26 UTC

## Ultima decisione
- esito: **⚪ FLAT** (2026-06-22 12:17 UTC)
- motivo: TIAUSDT già aperto
- asset valutati: 100 · segnali: 3 · miglior segnale TIAUSDT mean_reversion (conf. 63.3/soglia 30)

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **55/80 crypto (69%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **70**
- universo scansionato: 1INCHUSDT, AAVEUSDT, ADAUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, CHZUSDT, COMPUSDT, CRVUSDT, DASHUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, ENAUSDT, ENSUSDT, EOSUSDT, ETCUSDT, ETHUSDT, FETUSDT, FILUSDT, FLOKIUSDT, FLOWUSDT, FTMUSDT, GALAUSDT, GMTUSDT, GRTUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, IOTAUSDT, JUPUSDT, KAVAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MANAUSDT, MASKUSDT, MINAUSDT, MKRUSDT, NEARUSDT, NEOUSDT, OPUSDT, ORDIUSDT, PEOPLEUSDT, PEPEUSDT, PYTHUSDT, RENDERUSDT, ROSEUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SNXUSDT, SOLUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WAVESUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT, YFIUSDT, ZECUSDT
- aggiornato: 2026-06-22 09:44 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| KAVAUSDT | trend_following | 4 | 1.201 | 412% | atr_mult_stop=2.0, rsi_hi=75.0, require_volume=False, rr=2.5 |
| WAVESUSDT | trend_following | 4 | 1.164 | 374% | atr_mult_stop=1.5, rsi_hi=75.0, require_volume=False, rr=2.5 |
| EOSUSDT | trend_following | 3 | 1.157 | 331% | rr=2.5, rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0 |
| VETUSDT | trend_following | 4 | 1.15 | 328% | rr=2.5, rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0 |
| FTMUSDT | trend_following | 5 | 1.128 | 313% | atr_mult_stop=2.0, rsi_hi=75.0, require_volume=False, rr=2.0 |
| ROSEUSDT | trend_following | 4 | 1.118 | 270% | atr_mult_stop=2.0, rsi_hi=70.0, require_volume=False, rr=2.0 |
| TONUSDT | trend_following | 3 | 1.118 | 257% | rr=2.5, rsi_hi=75.0, require_volume=True, atr_mult_stop=2.0 |
| MKRUSDT | trend_following | 4 | 1.114 | 253% | require_volume=True, rsi_hi=75.0, atr_mult_stop=2.0, rr=2.5 |
| FETUSDT | trend_following | 4 | 1.109 | 233% | rr=2.0, rsi_hi=75.0, require_volume=True, atr_mult_stop=2.0 |
| RUNEUSDT | trend_following | 4 | 1.109 | 217% | atr_mult_stop=2.0, rsi_hi=75.0, require_volume=True, rr=2.5 |
| WLDUSDT | trend_following | 4 | 1.162 | 192% | atr_mult_stop=1.0, rsi_hi=75.0, require_volume=False, rr=2.5 |
| NEOUSDT | mean_reversion | 4 | 1.847 | 105% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.8 |
| IOTAUSDT | mean_reversion | 5 | 1.477 | 84% | rsi_overbought=80.0, rsi_oversold=30.0, atr_mult_stop=1.8 |
| FILUSDT | mean_reversion | 4 | 1.647 | 80% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| MANAUSDT | mean_reversion | 3 | 1.687 | 69% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.2 |
| MINAUSDT | mean_reversion | 4 | 1.463 | 65% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.8 |
| GALAUSDT | breakout | 3 | 1.15 | 64% | compression=0.07, volume_spike=2.5, rr=2.5 |
| SUIUSDT | breakout | 4 | 1.753 | 62% | compression=0.05, volume_spike=2.5, rr=3.0 |
| GALAUSDT | mean_reversion | 4 | 1.544 | 60% | rsi_overbought=80.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| AVAXUSDT | breakout | 4 | 1.118 | 60% | compression=0.1, volume_spike=2.5, rr=3.0 |
| MASKUSDT | mean_reversion | 3 | 1.437 | 59% | rsi_overbought=75.0, rsi_oversold=20.0, atr_mult_stop=1.0 |
| GRTUSDT | mean_reversion | 4 | 1.513 | 52% | rsi_overbought=75.0, rsi_oversold=20.0, atr_mult_stop=1.0 |
| 1INCHUSDT | breakout | 4 | 1.148 | 50% | compression=0.07, volume_spike=1.8, rr=2.5 |
| WIFUSDT | breakout | 4 | 1.236 | 49% | compression=0.1, volume_spike=2.5, rr=3.0 |
| EGLDUSDT | mean_reversion | 5 | 1.532 | 48% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.0 |
| IMXUSDT | mean_reversion | 4 | 1.412 | 47% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| DOGEUSDT | mean_reversion | 3 | 1.253 | 47% | rsi_overbought=80.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| 1INCHUSDT | mean_reversion | 5 | 1.359 | 46% | rsi_overbought=70.0, rsi_oversold=25.0, atr_mult_stop=1.2 |
| ADAUSDT | mean_reversion | 5 | 1.347 | 44% | rsi_overbought=80.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| PEPEUSDT | breakout | 3 | 1.149 | 43% | compression=0.1, volume_spike=1.5, rr=3.0 |
| JUPUSDT | mean_reversion | 3 | 1.537 | 42% | rsi_overbought=80.0, rsi_oversold=25.0, atr_mult_stop=1.8 |
| ATOMUSDT | mean_reversion | 5 | 1.437 | 41% | rsi_overbought=75.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| JUPUSDT | breakout | 4 | 1.192 | 39% | compression=0.05, volume_spike=1.8, rr=3.0 |
| SUIUSDT | mean_reversion | 4 | 1.265 | 39% | rsi_overbought=80.0, rsi_oversold=30.0, atr_mult_stop=1.8 |
| BONKUSDT | breakout | 4 | 1.245 | 37% | compression=0.07, volume_spike=1.5, rr=3.0 |
| LTCUSDT | mean_reversion | 3 | 1.32 | 36% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| APTUSDT | mean_reversion | 5 | 1.353 | 35% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.0 |
| INJUSDT | mean_reversion | 4 | 1.324 | 35% | rsi_overbought=70.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| ETCUSDT | mean_reversion | 5 | 1.312 | 35% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.8 |
| DASHUSDT | breakout | 4 | 1.687 | 34% | compression=0.07, volume_spike=1.8, rr=2.0 |
| STXUSDT | mean_reversion | 4 | 1.292 | 34% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| DASHUSDT | trend_following | 3 | 1.211 | 33% | atr_mult_stop=2.0, rsi_hi=70.0, require_volume=True, rr=2.0 |
| MANAUSDT | liquidity_grab | 4 | 1.514 | 32% | volume_spike=3.0, atr_mult_stop=1.5 |
| FLOKIUSDT | mean_reversion | 3 | 1.106 | 31% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| YFIUSDT | mean_reversion | 4 | 1.291 | 30% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.8 |
| ALGOUSDT | mean_reversion | 4 | 1.196 | 28% | rsi_overbought=80.0, rsi_oversold=25.0, atr_mult_stop=1.2 |
| RENDERUSDT | mean_reversion | 4 | 1.467 | 28% | rsi_overbought=80.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| PYTHUSDT | mean_reversion | 3 | 1.275 | 27% | rsi_overbought=70.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| SEIUSDT | breakout | 3 | 1.389 | 26% | compression=0.1, volume_spike=1.5, rr=2.5 |
| LDOUSDT | mean_reversion | 3 | 1.146 | 26% | rsi_overbought=75.0, rsi_oversold=25.0, atr_mult_stop=1.0 |
| ZECUSDT | trend_following | 5 | 1.104 | 26% | atr_mult_stop=1.5, rsi_hi=75.0, require_volume=True, rr=1.5 |
| ETHUSDT | mean_reversion | 3 | 1.339 | 24% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| LDOUSDT | liquidity_grab | 4 | 1.195 | 24% | volume_spike=2.0, atr_mult_stop=0.8 |
| AAVEUSDT | mean_reversion | 4 | 1.252 | 24% | rsi_overbought=80.0, rsi_oversold=25.0, atr_mult_stop=1.0 |
| DOTUSDT | mean_reversion | 4 | 1.195 | 21% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.0 |
| ARBUSDT | mean_reversion | 3 | 1.205 | 20% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| HBARUSDT | mean_reversion | 4 | 1.173 | 20% | rsi_overbought=70.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| ARBUSDT | liquidity_grab | 4 | 1.906 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| ALGOUSDT | liquidity_grab | 4 | 1.384 | 18% | volume_spike=3.0, atr_mult_stop=1.5 |
| CHZUSDT | mean_reversion | 5 | 1.162 | 17% | rsi_overbought=75.0, rsi_oversold=30.0, atr_mult_stop=1.0 |
| WIFUSDT | liquidity_grab | 4 | 1.364 | 17% | volume_spike=3.0, atr_mult_stop=1.5 |
| 1INCHUSDT | liquidity_grab | 5 | 1.397 | 17% | volume_spike=3.0, atr_mult_stop=1.5 |
| ENSUSDT | liquidity_grab | 4 | 1.169 | 15% | volume_spike=3.0, atr_mult_stop=0.8 |
| TIAUSDT | mean_reversion | 3 | 1.137 | 14% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| PYTHUSDT | liquidity_grab | 5 | 1.215 | 11% | volume_spike=2.5, atr_mult_stop=1.5 |
| ENAUSDT | breakout | 4 | 1.162 | 11% | compression=0.07, volume_spike=2.5, rr=2.5 |
| TIAUSDT | liquidity_grab | 5 | 1.135 | 8% | volume_spike=2.0, atr_mult_stop=0.8 |
| IMXUSDT | liquidity_grab | 4 | 1.122 | 7% | volume_spike=2.5, atr_mult_stop=0.8 |
| SOLUSDT | liquidity_grab | 4 | 1.105 | 5% | volume_spike=2.5, atr_mult_stop=1.5 |
| ZECUSDT | liquidity_grab | 5 | 1.318 | 4% | volume_spike=2.0, atr_mult_stop=0.8 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-22 06:54 UTC · 560 coppie valutate, 75 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| KAVAUSDT | trend_following | 1.201 | 412% | 1142 | 34% |
| WAVESUSDT | trend_following | 1.164 | 374% | 1576 | 35% |
| EOSUSDT | trend_following | 1.157 | 331% | 1288 | 33% |
| VETUSDT | trend_following | 1.15 | 328% | 1340 | 33% |
| FTMUSDT | trend_following | 1.128 | 313% | 1547 | 36% |
| ROSEUSDT | trend_following | 1.118 | 270% | 1456 | 35% |
| STXUSDT | trend_following | 1.198 | 266% | 736 | 38% |
| TONUSDT | trend_following | 1.118 | 257% | 1325 | 32% |
| FETUSDT | trend_following | 1.109 | 233% | 1346 | 35% |
| RUNEUSDT | trend_following | 1.109 | 217% | 1182 | 32% |
| WLDUSDT | trend_following | 1.162 | 192% | 695 | 32% |
| NEOUSDT | mean_reversion | 1.847 | 105% | 56 | 48% |
| IOTAUSDT | mean_reversion | 1.477 | 84% | 61 | 41% |
| FILUSDT | mean_reversion | 1.647 | 80% | 57 | 40% |
| OPUSDT | mean_reversion | 1.375 | 72% | 81 | 38% |
| MANAUSDT | mean_reversion | 1.687 | 69% | 39 | 49% |
| DOGEUSDT | breakout | 1.165 | 67% | 451 | 31% |
| MINAUSDT | mean_reversion | 1.463 | 65% | 50 | 40% |
| GALAUSDT | breakout | 1.15 | 64% | 409 | 36% |
| SUIUSDT | breakout | 1.753 | 62% | 97 | 36% |
| GALAUSDT | mean_reversion | 1.544 | 60% | 37 | 38% |
| AVAXUSDT | breakout | 1.118 | 60% | 573 | 37% |
| MASKUSDT | mean_reversion | 1.437 | 59% | 47 | 43% |
| GRTUSDT | mean_reversion | 1.513 | 52% | 42 | 33% |
| 1INCHUSDT | breakout | 1.148 | 50% | 382 | 33% |
| WIFUSDT | breakout | 1.236 | 49% | 169 | 36% |
| EGLDUSDT | mean_reversion | 1.532 | 48% | 42 | 36% |
| IMXUSDT | mean_reversion | 1.412 | 47% | 40 | 40% |
| DOGEUSDT | mean_reversion | 1.253 | 47% | 71 | 41% |
| 1INCHUSDT | mean_reversion | 1.359 | 46% | 59 | 39% |
| ADAUSDT | mean_reversion | 1.347 | 44% | 44 | 41% |
| PEPEUSDT | breakout | 1.149 | 43% | 265 | 31% |
| JUPUSDT | mean_reversion | 1.537 | 42% | 26 | 38% |
| ATOMUSDT | mean_reversion | 1.437 | 41% | 40 | 40% |
| ORDIUSDT | mean_reversion | 1.153 | 40% | 91 | 33% |
| JUPUSDT | breakout | 1.192 | 39% | 216 | 39% |
| APTUSDT | breakout | 1.154 | 39% | 303 | 42% |
| LINKUSDT | breakout | 1.116 | 39% | 378 | 33% |
| SUIUSDT | mean_reversion | 1.265 | 39% | 53 | 36% |
| BONKUSDT | breakout | 1.245 | 37% | 153 | 33% |
| APTUSDT | mean_reversion | 1.353 | 35% | 46 | 33% |
| INJUSDT | mean_reversion | 1.324 | 35% | 41 | 37% |
| ETCUSDT | mean_reversion | 1.312 | 35% | 62 | 32% |
| DASHUSDT | breakout | 1.687 | 34% | 50 | 42% |
| DASHUSDT | trend_following | 1.211 | 33% | 95 | 36% |
| MANAUSDT | liquidity_grab | 1.514 | 32% | 85 | 52% |
| YFIUSDT | mean_reversion | 1.291 | 30% | 47 | 34% |
| FETUSDT | breakout | 1.146 | 29% | 210 | 31% |
| FTMUSDT | momentum_cross_asset | 1.313 | 29% | 96 | 41% |
| ALGOUSDT | mean_reversion | 1.196 | 28% | 58 | 33% |
| RENDERUSDT | mean_reversion | 1.467 | 28% | 23 | 35% |
| PYTHUSDT | mean_reversion | 1.275 | 27% | 39 | 38% |
| SEIUSDT | breakout | 1.389 | 26% | 81 | 37% |
| LDOUSDT | mean_reversion | 1.146 | 26% | 64 | 31% |
| ZECUSDT | trend_following | 1.104 | 26% | 127 | 45% |
| ETHUSDT | mean_reversion | 1.339 | 24% | 89 | 36% |
| LDOUSDT | liquidity_grab | 1.195 | 24% | 151 | 48% |
| AAVEUSDT | mean_reversion | 1.252 | 24% | 36 | 33% |
| DOTUSDT | mean_reversion | 1.195 | 21% | 61 | 34% |
| ARBUSDT | mean_reversion | 1.205 | 20% | 33 | 30% |
| HBARUSDT | mean_reversion | 1.173 | 20% | 44 | 23% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| ALGOUSDT | liquidity_grab | 1.384 | 18% | 78 | 62% |
| CHZUSDT | mean_reversion | 1.162 | 17% | 43 | 26% |
| WIFUSDT | liquidity_grab | 1.364 | 17% | 44 | 64% |
| 1INCHUSDT | liquidity_grab | 1.397 | 17% | 76 | 68% |
| VETUSDT | momentum_cross_asset | 1.124 | 15% | 92 | 33% |
| ENSUSDT | liquidity_grab | 1.169 | 15% | 126 | 49% |
| PYTHUSDT | liquidity_grab | 1.215 | 11% | 53 | 57% |
| ENAUSDT | breakout | 1.162 | 11% | 71 | 35% |
| TIAUSDT | liquidity_grab | 1.135 | 8% | 72 | 49% |
| IMXUSDT | liquidity_grab | 1.122 | 7% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
| ZECUSDT | liquidity_grab | 1.318 | 4% | 18 | 50% |
| EOSUSDT | mean_reversion | 1.109 | 1% | 12 | 33% |
