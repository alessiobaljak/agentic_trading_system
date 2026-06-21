# Stato sistema (snapshot)
_Generato: 2026-06-21 23:45 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$9,580.02**
- ultimo heartbeat: 2026-06-21 23:45 UTC

## Ultima decisione
- esito: **⚪ FLAT** (2026-06-21 23:44 UTC)
- motivo: nessun segnale dalle strategie attive in questo regime
- asset valutati: 100 · segnali: 0

## Posizioni aperte
- ETCUSDT: long qty=1310.7717966127339 @ 7.267 uPnL=32.62986811931177

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **48/80 crypto (60%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **56**
- universo scansionato: 1INCHUSDT, AAVEUSDT, ADAUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, CHZUSDT, COMPUSDT, CRVUSDT, DASHUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, ENAUSDT, ENSUSDT, EOSUSDT, ETCUSDT, ETHUSDT, FETUSDT, FILUSDT, FLOKIUSDT, FLOWUSDT, FTMUSDT, GALAUSDT, GMTUSDT, GRTUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, IOTAUSDT, JUPUSDT, KAVAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MANAUSDT, MASKUSDT, MINAUSDT, MKRUSDT, NEARUSDT, NEOUSDT, OPUSDT, ORDIUSDT, PEOPLEUSDT, PEPEUSDT, PYTHUSDT, RENDERUSDT, ROSEUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SNXUSDT, SOLUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WAVESUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT, YFIUSDT, ZECUSDT
- aggiornato: 2026-06-21 22:15 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| FTMUSDT | trend_following | 4 | 1.145 | 302% | require_volume=False, rsi_hi=75.0, atr_mult_stop=2.0, rr=2.5 |
| KAVAUSDT | trend_following | 3 | 1.114 | 255% | require_volume=False, rsi_hi=70.0, atr_mult_stop=2.0, rr=2.5 |
| MKRUSDT | trend_following | 4 | 1.114 | 253% | require_volume=True, rsi_hi=75.0, atr_mult_stop=2.0, rr=2.5 |
| ROSEUSDT | trend_following | 3 | 1.116 | 251% | require_volume=False, rsi_hi=75.0, atr_mult_stop=2.0, rr=2.5 |
| WLDUSDT | trend_following | 3 | 1.218 | 249% | require_volume=True, rsi_hi=75.0, atr_mult_stop=1.0, rr=2.5 |
| VETUSDT | trend_following | 3 | 1.121 | 244% | rsi_hi=75.0, require_volume=True, atr_mult_stop=2.0, rr=2.0 |
| WAVESUSDT | trend_following | 3 | 1.114 | 237% | require_volume=True, rsi_hi=70.0, atr_mult_stop=2.0, rr=2.5 |
| FETUSDT | trend_following | 3 | 1.11 | 225% | rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0, rr=2.5 |
| RUNEUSDT | trend_following | 3 | 1.104 | 218% | require_volume=False, rsi_hi=75.0, atr_mult_stop=2.0, rr=2.5 |
| GRTUSDT | mean_reversion | 3 | 1.733 | 89% | rsi_overbought=75.0, atr_mult_stop=1.2, rsi_oversold=20.0 |
| ALGOUSDT | mean_reversion | 3 | 1.622 | 89% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| AVAXUSDT | breakout | 3 | 1.234 | 79% | volume_spike=2.5, compression=0.05, rr=2.5 |
| GALAUSDT | mean_reversion | 3 | 1.599 | 78% | rsi_overbought=80.0, atr_mult_stop=1.0, rsi_oversold=25.0 |
| INJUSDT | mean_reversion | 3 | 1.771 | 76% | rsi_overbought=70.0, atr_mult_stop=1.2, rsi_oversold=30.0 |
| NEOUSDT | mean_reversion | 3 | 1.714 | 73% | rsi_overbought=80.0, atr_mult_stop=1.2, rsi_oversold=30.0 |
| FILUSDT | mean_reversion | 3 | 1.533 | 73% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| SUIUSDT | mean_reversion | 3 | 1.406 | 69% | rsi_overbought=80.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| WIFUSDT | breakout | 3 | 1.262 | 67% | volume_spike=1.8, compression=0.1, rr=3.0 |
| 1INCHUSDT | breakout | 3 | 1.204 | 64% | volume_spike=1.8, compression=0.07, rr=3.0 |
| MINAUSDT | mean_reversion | 3 | 1.348 | 60% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| ZECUSDT | trend_following | 4 | 1.208 | 54% | require_volume=False, rsi_hi=65.0, atr_mult_stop=1.5, rr=2.5 |
| IMXUSDT | mean_reversion | 3 | 1.483 | 50% | rsi_overbought=70.0, atr_mult_stop=1.2, rsi_oversold=20.0 |
| EGLDUSDT | mean_reversion | 4 | 1.591 | 49% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| JUPUSDT | breakout | 3 | 1.202 | 48% | volume_spike=1.5, compression=0.05, rr=2.0 |
| CHZUSDT | mean_reversion | 4 | 1.584 | 48% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| IOTAUSDT | mean_reversion | 4 | 1.313 | 47% | rsi_overbought=70.0, atr_mult_stop=1.2, rsi_oversold=25.0 |
| RENDERUSDT | mean_reversion | 3 | 1.656 | 42% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| ETCUSDT | mean_reversion | 4 | 1.318 | 41% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| 1INCHUSDT | mean_reversion | 4 | 1.304 | 40% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| ADAUSDT | mean_reversion | 4 | 1.463 | 40% | rsi_overbought=80.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| APTUSDT | mean_reversion | 4 | 1.436 | 38% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| YFIUSDT | mean_reversion | 3 | 1.245 | 36% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| LTCUSDT | mean_reversion | 3 | 1.32 | 36% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| SUIUSDT | breakout | 3 | 1.161 | 35% | volume_spike=1.5, compression=0.1, rr=2.5 |
| STXUSDT | mean_reversion | 4 | 1.292 | 34% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| MANAUSDT | liquidity_grab | 3 | 1.514 | 32% | volume_spike=3.0, atr_mult_stop=1.5 |
| FLOKIUSDT | mean_reversion | 3 | 1.106 | 31% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| AAVEUSDT | mean_reversion | 3 | 1.343 | 30% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=25.0 |
| HBARUSDT | mean_reversion | 3 | 1.171 | 25% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| BONKUSDT | breakout | 3 | 1.197 | 25% | volume_spike=2.5, compression=0.1, rr=2.0 |
| ATOMUSDT | mean_reversion | 4 | 1.303 | 25% | rsi_overbought=75.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| DASHUSDT | breakout | 3 | 1.72 | 25% | volume_spike=2.5, compression=0.07, rr=2.5 |
| ENAUSDT | breakout | 3 | 1.478 | 24% | volume_spike=1.8, compression=0.07, rr=2.0 |
| LDOUSDT | liquidity_grab | 3 | 1.191 | 24% | volume_spike=2.0, atr_mult_stop=0.8 |
| DOTUSDT | mean_reversion | 3 | 1.244 | 20% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=25.0 |
| ALGOUSDT | liquidity_grab | 3 | 1.409 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| ARBUSDT | liquidity_grab | 3 | 1.906 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| WIFUSDT | liquidity_grab | 3 | 1.364 | 17% | volume_spike=3.0, atr_mult_stop=1.5 |
| 1INCHUSDT | liquidity_grab | 4 | 1.397 | 17% | volume_spike=3.0, atr_mult_stop=1.5 |
| TIAUSDT | mean_reversion | 3 | 1.137 | 14% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| ENSUSDT | liquidity_grab | 3 | 1.153 | 13% | volume_spike=3.0, atr_mult_stop=0.8 |
| PYTHUSDT | liquidity_grab | 4 | 1.215 | 11% | volume_spike=2.5, atr_mult_stop=1.5 |
| IMXUSDT | liquidity_grab | 3 | 1.148 | 8% | volume_spike=2.5, atr_mult_stop=0.8 |
| TIAUSDT | liquidity_grab | 4 | 1.111 | 6% | volume_spike=2.0, atr_mult_stop=0.8 |
| SOLUSDT | liquidity_grab | 3 | 1.105 | 5% | volume_spike=2.5, atr_mult_stop=1.5 |
| ZECUSDT | liquidity_grab | 4 | 1.318 | 4% | volume_spike=2.0, atr_mult_stop=0.8 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-21 22:15 UTC · 560 coppie valutate, 77 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| EOSUSDT | trend_following | 1.157 | 332% | 1451 | 34% |
| FTMUSDT | trend_following | 1.145 | 302% | 1207 | 36% |
| TONUSDT | trend_following | 1.128 | 260% | 1143 | 35% |
| KAVAUSDT | trend_following | 1.114 | 255% | 1396 | 34% |
| MKRUSDT | trend_following | 1.114 | 253% | 1352 | 32% |
| ROSEUSDT | trend_following | 1.116 | 251% | 1731 | 39% |
| WLDUSDT | trend_following | 1.218 | 249% | 709 | 40% |
| VETUSDT | trend_following | 1.121 | 244% | 1269 | 36% |
| WAVESUSDT | trend_following | 1.114 | 237% | 1236 | 38% |
| FETUSDT | trend_following | 1.11 | 225% | 1247 | 34% |
| RUNEUSDT | trend_following | 1.104 | 218% | 1163 | 34% |
| GALAUSDT | trend_following | 1.101 | 159% | 790 | 38% |
| GRTUSDT | mean_reversion | 1.733 | 89% | 57 | 39% |
| ALGOUSDT | mean_reversion | 1.622 | 89% | 72 | 26% |
| AVAXUSDT | breakout | 1.234 | 79% | 403 | 37% |
| GALAUSDT | mean_reversion | 1.599 | 78% | 53 | 32% |
| INJUSDT | mean_reversion | 1.771 | 76% | 46 | 39% |
| NEOUSDT | mean_reversion | 1.714 | 73% | 54 | 33% |
| FILUSDT | mean_reversion | 1.533 | 73% | 46 | 44% |
| SUIUSDT | mean_reversion | 1.406 | 69% | 68 | 40% |
| WIFUSDT | breakout | 1.262 | 67% | 201 | 32% |
| MASKUSDT | mean_reversion | 1.532 | 65% | 42 | 45% |
| 1INCHUSDT | breakout | 1.204 | 64% | 362 | 32% |
| MINAUSDT | mean_reversion | 1.348 | 60% | 62 | 36% |
| ZECUSDT | trend_following | 1.208 | 54% | 139 | 35% |
| ENSUSDT | mean_reversion | 1.258 | 54% | 80 | 35% |
| IMXUSDT | mean_reversion | 1.483 | 50% | 45 | 33% |
| EGLDUSDT | mean_reversion | 1.591 | 49% | 39 | 36% |
| JUPUSDT | breakout | 1.202 | 48% | 242 | 36% |
| CHZUSDT | mean_reversion | 1.584 | 48% | 33 | 27% |
| IOTAUSDT | mean_reversion | 1.313 | 47% | 63 | 29% |
| RENDERUSDT | mean_reversion | 1.656 | 42% | 24 | 33% |
| ETCUSDT | mean_reversion | 1.318 | 41% | 75 | 33% |
| 1INCHUSDT | mean_reversion | 1.304 | 40% | 52 | 46% |
| ADAUSDT | mean_reversion | 1.463 | 40% | 31 | 42% |
| ARBUSDT | breakout | 1.287 | 39% | 166 | 38% |
| APTUSDT | mean_reversion | 1.436 | 38% | 34 | 35% |
| CRVUSDT | mean_reversion | 1.204 | 38% | 83 | 30% |
| FLOKIUSDT | breakout | 1.256 | 37% | 166 | 38% |
| YFIUSDT | mean_reversion | 1.245 | 36% | 70 | 34% |
| LTCUSDT | mean_reversion | 1.32 | 36% | 74 | 42% |
| MANAUSDT | mean_reversion | 1.348 | 35% | 40 | 40% |
| SUIUSDT | breakout | 1.161 | 35% | 222 | 36% |
| PYTHUSDT | mean_reversion | 1.378 | 35% | 36 | 42% |
| STXUSDT | mean_reversion | 1.292 | 34% | 50 | 32% |
| ARUSDT | mean_reversion | 1.194 | 34% | 68 | 29% |
| XRPUSDT | mean_reversion | 1.195 | 32% | 92 | 36% |
| MANAUSDT | liquidity_grab | 1.514 | 32% | 85 | 52% |
| ORDIUSDT | mean_reversion | 1.116 | 31% | 92 | 33% |
| AAVEUSDT | mean_reversion | 1.343 | 30% | 35 | 40% |
| PYTHUSDT | breakout | 1.128 | 27% | 223 | 38% |
| LDOUSDT | mean_reversion | 1.146 | 26% | 64 | 31% |
| HBARUSDT | mean_reversion | 1.171 | 25% | 42 | 33% |
| BONKUSDT | breakout | 1.197 | 25% | 140 | 39% |
| ATOMUSDT | mean_reversion | 1.303 | 25% | 37 | 32% |
| DASHUSDT | breakout | 1.72 | 25% | 38 | 37% |
| ENAUSDT | breakout | 1.478 | 24% | 60 | 42% |
| LDOUSDT | liquidity_grab | 1.191 | 24% | 151 | 48% |
| JUPUSDT | mean_reversion | 1.305 | 21% | 24 | 42% |
| DOTUSDT | mean_reversion | 1.244 | 20% | 50 | 32% |
| SEIUSDT | breakout | 1.357 | 20% | 64 | 38% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| WIFUSDT | liquidity_grab | 1.364 | 17% | 44 | 64% |
| 1INCHUSDT | liquidity_grab | 1.397 | 17% | 76 | 68% |
| ROSEUSDT | momentum_cross_asset | 1.161 | 16% | 94 | 40% |
| DASHUSDT | trend_following | 1.106 | 16% | 96 | 38% |
| BONKUSDT | mean_reversion | 1.161 | 15% | 34 | 32% |
| AVAXUSDT | mean_reversion | 1.103 | 15% | 66 | 32% |
| TIAUSDT | mean_reversion | 1.137 | 14% | 29 | 31% |
| ENSUSDT | liquidity_grab | 1.153 | 13% | 125 | 49% |
| PYTHUSDT | liquidity_grab | 1.215 | 11% | 53 | 57% |
| IMXUSDT | liquidity_grab | 1.148 | 8% | 79 | 53% |
| TIAUSDT | liquidity_grab | 1.111 | 6% | 71 | 48% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
| ZECUSDT | liquidity_grab | 1.318 | 4% | 18 | 50% |
| FETUSDT | mean_reversion | 1.109 | 1% | 12 | 33% |
