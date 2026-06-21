# Stato sistema (snapshot)
_Generato: 2026-06-21 21:43 UTC_

## Bot
- stato: **running** (🔴 offline)
- regime: sideways
- DRY_RUN: True
- equity: **$9,580.02**
- ultimo heartbeat: 2026-06-21 21:39 UTC

## Ultima decisione
- esito: **⚪ FLAT** (2026-06-21 21:43 UTC)
- motivo: nessun segnale dalle strategie attive in questo regime
- asset valutati: 100 · segnali: 0

## Posizioni aperte
- ETCUSDT: long qty=1310.7717966127339 @ 7.267 uPnL=87.82171037305223

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **15/80 crypto (19%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **17**
- universo scansionato: 1INCHUSDT, AAVEUSDT, ADAUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, CHZUSDT, COMPUSDT, CRVUSDT, DASHUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, ENAUSDT, ENSUSDT, EOSUSDT, ETCUSDT, ETHUSDT, FETUSDT, FILUSDT, FLOKIUSDT, FLOWUSDT, FTMUSDT, GALAUSDT, GMTUSDT, GRTUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, IOTAUSDT, JUPUSDT, KAVAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MANAUSDT, MASKUSDT, MINAUSDT, MKRUSDT, NEARUSDT, NEOUSDT, OPUSDT, ORDIUSDT, PEOPLEUSDT, PEPEUSDT, PYTHUSDT, RENDERUSDT, ROSEUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SNXUSDT, SOLUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WAVESUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT, YFIUSDT, ZECUSDT
- aggiornato: 2026-06-21 18:22 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| MKRUSDT | trend_following | 3 | 1.114 | 237% | require_volume=True, rsi_hi=70.0, atr_mult_stop=2.0, rr=2.5 |
| FTMUSDT | trend_following | 3 | 1.104 | 235% | require_volume=False, rsi_hi=70.0, atr_mult_stop=2.0, rr=2.0 |
| 1INCHUSDT | mean_reversion | 3 | 1.659 | 68% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| STXUSDT | mean_reversion | 3 | 1.563 | 65% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| IOTAUSDT | mean_reversion | 3 | 1.42 | 59% | rsi_overbought=80.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| APTUSDT | mean_reversion | 3 | 1.58 | 57% | rsi_overbought=75.0, atr_mult_stop=1.0, rsi_oversold=25.0 |
| EGLDUSDT | mean_reversion | 3 | 1.591 | 49% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| ATOMUSDT | mean_reversion | 3 | 1.64 | 43% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| ADAUSDT | mean_reversion | 3 | 1.313 | 35% | rsi_overbought=80.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| FLOKIUSDT | mean_reversion | 3 | 1.106 | 31% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| ZECUSDT | trend_following | 3 | 1.133 | 29% | require_volume=False, rsi_hi=65.0, atr_mult_stop=1.5, rr=2.5 |
| CHZUSDT | mean_reversion | 3 | 1.172 | 19% | rsi_overbought=80.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| ETCUSDT | mean_reversion | 3 | 1.206 | 18% | rsi_overbought=80.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| 1INCHUSDT | liquidity_grab | 3 | 1.397 | 17% | volume_spike=3.0, atr_mult_stop=1.5 |
| PYTHUSDT | liquidity_grab | 3 | 1.215 | 11% | volume_spike=2.5, atr_mult_stop=1.5 |
| TIAUSDT | liquidity_grab | 3 | 1.111 | 6% | volume_spike=2.0, atr_mult_stop=0.8 |
| ZECUSDT | liquidity_grab | 3 | 1.318 | 4% | volume_spike=2.0, atr_mult_stop=0.8 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-21 16:23 UTC · 560 coppie valutate, 82 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| EOSUSDT | trend_following | 1.149 | 310% | 1426 | 34% |
| RUNEUSDT | trend_following | 1.128 | 273% | 1539 | 34% |
| ROSEUSDT | trend_following | 1.141 | 271% | 1056 | 33% |
| FETUSDT | trend_following | 1.134 | 269% | 1102 | 33% |
| STXUSDT | trend_following | 1.191 | 250% | 609 | 34% |
| TONUSDT | trend_following | 1.113 | 247% | 1325 | 32% |
| MKRUSDT | trend_following | 1.114 | 237% | 1236 | 38% |
| FTMUSDT | trend_following | 1.104 | 235% | 1432 | 35% |
| VETUSDT | trend_following | 1.104 | 235% | 1432 | 35% |
| KAVAUSDT | trend_following | 1.11 | 221% | 1129 | 34% |
| WAVESUSDT | trend_following | 1.101 | 200% | 1104 | 34% |
| ALGOUSDT | mean_reversion | 1.949 | 149% | 71 | 41% |
| GRTUSDT | mean_reversion | 1.846 | 127% | 65 | 49% |
| NEOUSDT | mean_reversion | 1.847 | 105% | 56 | 48% |
| GALAUSDT | mean_reversion | 1.562 | 86% | 70 | 33% |
| SUIUSDT | mean_reversion | 1.441 | 79% | 66 | 42% |
| 1INCHUSDT | mean_reversion | 1.659 | 68% | 43 | 44% |
| STXUSDT | mean_reversion | 1.563 | 65% | 49 | 39% |
| IOTAUSDT | mean_reversion | 1.42 | 59% | 46 | 37% |
| AVAXUSDT | breakout | 1.141 | 59% | 516 | 42% |
| YFIUSDT | mean_reversion | 1.561 | 58% | 50 | 36% |
| MINAUSDT | mean_reversion | 1.383 | 58% | 43 | 40% |
| APTUSDT | mean_reversion | 1.58 | 57% | 49 | 35% |
| LTCUSDT | mean_reversion | 1.444 | 57% | 88 | 40% |
| NEARUSDT | breakout | 1.137 | 50% | 387 | 38% |
| SUIUSDT | breakout | 1.228 | 50% | 222 | 35% |
| EGLDUSDT | mean_reversion | 1.591 | 49% | 39 | 36% |
| FILUSDT | mean_reversion | 1.413 | 49% | 47 | 34% |
| GALAUSDT | breakout | 1.123 | 48% | 360 | 32% |
| DASHUSDT | trend_following | 1.267 | 47% | 99 | 41% |
| INJUSDT | mean_reversion | 1.421 | 46% | 39 | 38% |
| OPUSDT | mean_reversion | 1.256 | 46% | 74 | 35% |
| ATOMUSDT | mean_reversion | 1.64 | 43% | 24 | 42% |
| BONKUSDT | breakout | 1.268 | 43% | 160 | 32% |
| PYTHUSDT | mean_reversion | 1.384 | 42% | 43 | 42% |
| DOGEUSDT | mean_reversion | 1.192 | 38% | 81 | 40% |
| JUPUSDT | breakout | 1.162 | 36% | 211 | 33% |
| CRVUSDT | mean_reversion | 1.201 | 36% | 77 | 29% |
| SNXUSDT | mean_reversion | 1.201 | 36% | 69 | 22% |
| ADAUSDT | mean_reversion | 1.313 | 35% | 43 | 44% |
| SUSHIUSDT | mean_reversion | 1.156 | 33% | 81 | 31% |
| MKRUSDT | breakout | 1.145 | 32% | 262 | 38% |
| AAVEUSDT | mean_reversion | 1.366 | 32% | 38 | 45% |
| MANAUSDT | liquidity_grab | 1.514 | 32% | 85 | 52% |
| FLOKIUSDT | mean_reversion | 1.106 | 31% | 76 | 40% |
| MKRUSDT | momentum_cross_asset | 1.313 | 29% | 96 | 41% |
| ZECUSDT | trend_following | 1.133 | 29% | 113 | 34% |
| LINKUSDT | mean_reversion | 1.309 | 28% | 40 | 38% |
| WIFUSDT | breakout | 1.103 | 27% | 205 | 32% |
| XLMUSDT | mean_reversion | 1.219 | 25% | 58 | 31% |
| FETUSDT | momentum_cross_asset | 1.317 | 24% | 97 | 42% |
| MANAUSDT | mean_reversion | 1.239 | 24% | 37 | 32% |
| LDOUSDT | liquidity_grab | 1.191 | 24% | 151 | 48% |
| IMXUSDT | mean_reversion | 1.204 | 24% | 42 | 33% |
| XRPUSDT | mean_reversion | 1.189 | 22% | 66 | 30% |
| RUNEUSDT | breakout | 1.118 | 21% | 219 | 39% |
| LDOUSDT | mean_reversion | 1.132 | 21% | 58 | 31% |
| DASHUSDT | breakout | 1.68 | 20% | 36 | 47% |
| ROSEUSDT | momentum_cross_asset | 1.147 | 20% | 135 | 40% |
| MASKUSDT | mean_reversion | 1.101 | 20% | 62 | 37% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| CHZUSDT | mean_reversion | 1.172 | 19% | 45 | 27% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| ETCUSDT | mean_reversion | 1.206 | 18% | 39 | 31% |
| WIFUSDT | liquidity_grab | 1.364 | 17% | 44 | 64% |
| 1INCHUSDT | liquidity_grab | 1.397 | 17% | 76 | 68% |
| ARBUSDT | mean_reversion | 1.147 | 16% | 40 | 30% |
| RENDERUSDT | breakout | 1.19 | 16% | 91 | 33% |
| JUPUSDT | mean_reversion | 1.209 | 15% | 25 | 32% |
| DASHUSDT | mean_reversion | 1.268 | 14% | 19 | 37% |
| ENSUSDT | liquidity_grab | 1.153 | 13% | 125 | 49% |
| TONUSDT | momentum_cross_asset | 1.127 | 13% | 95 | 43% |
| ENAUSDT | breakout | 1.242 | 12% | 53 | 32% |
| PYTHUSDT | liquidity_grab | 1.215 | 11% | 53 | 57% |
| ETHUSDT | mean_reversion | 1.122 | 11% | 92 | 39% |
| IMXUSDT | liquidity_grab | 1.148 | 8% | 79 | 53% |
| TIAUSDT | liquidity_grab | 1.111 | 6% | 71 | 48% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
| ZECUSDT | liquidity_grab | 1.318 | 4% | 18 | 50% |
| FTMUSDT | mean_reversion | 1.109 | 1% | 12 | 33% |
| ROSEUSDT | mean_reversion | 1.109 | 1% | 12 | 33% |
| VETUSDT | mean_reversion | 1.109 | 1% | 12 | 33% |
