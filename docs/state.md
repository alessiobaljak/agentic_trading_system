# Stato sistema (snapshot)
_Generato: 2026-06-22 18:18 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$9,647.66**
- ultimo heartbeat: 2026-06-22 18:18 UTC

## Ultima decisione
- esito: **⚪ FLAT** (2026-06-22 18:07 UTC)
- motivo: TONUSDT già aperto
- asset valutati: 100 · segnali: 2 · miglior segnale TONUSDT gen_2e4b6e30 (conf. 60.0/soglia 30)

## Posizioni aperte
- FETUSDT: short qty=29097.926543615555 @ 0.1818 uPnL=-32.00771919797762
- JUPUSDT: short qty=24067.427925345608 @ 0.2078 uPnL=-16.847199547741408
- TONUSDT: long qty=4119.699476527342 @ 1.6808 uPnL=75.3905004204503

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **65/80 crypto (81%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **150**
- universo scansionato: 1INCHUSDT, AAVEUSDT, ADAUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, CHZUSDT, COMPUSDT, CRVUSDT, DASHUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, ENAUSDT, ENSUSDT, EOSUSDT, ETCUSDT, ETHUSDT, FETUSDT, FILUSDT, FLOKIUSDT, FLOWUSDT, FTMUSDT, GALAUSDT, GMTUSDT, GRTUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, IOTAUSDT, JUPUSDT, KAVAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MANAUSDT, MASKUSDT, MINAUSDT, MKRUSDT, NEARUSDT, NEOUSDT, OPUSDT, ORDIUSDT, PEOPLEUSDT, PEPEUSDT, PYTHUSDT, RENDERUSDT, ROSEUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SNXUSDT, SOLUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WAVESUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT, YFIUSDT, ZECUSDT
- aggiornato: 2026-06-22 14:41 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| PEPEUSDT | gen_149fa99c | 3 | 1.237 | 484% |  |
| KAVAUSDT | trend_following | 4 | 1.201 | 412% | atr_mult_stop=2.0, rsi_hi=75.0, require_volume=False, rr=2.5 |
| WAVESUSDT | trend_following | 4 | 1.164 | 374% | atr_mult_stop=1.5, rsi_hi=75.0, require_volume=False, rr=2.5 |
| ROSEUSDT | trend_following | 5 | 1.186 | 369% | rr=2.5, rsi_hi=70.0, require_volume=False, atr_mult_stop=2.0 |
| EOSUSDT | gen_2e4b6e30 | 3 | 1.155 | 353% |  |
| FETUSDT | gen_2e4b6e30 | 3 | 1.155 | 353% |  |
| TONUSDT | gen_2e4b6e30 | 3 | 1.155 | 353% |  |
| VETUSDT | gen_2e4b6e30 | 3 | 1.155 | 353% |  |
| MKRUSDT | trend_following | 5 | 1.128 | 313% | rr=2.0, rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0 |
| TONUSDT | trend_following | 4 | 1.124 | 277% | rsi_hi=75.0, rr=2.5, require_volume=False, atr_mult_stop=2.0 |
| FTMUSDT | trend_following | 6 | 1.117 | 264% | rr=2.0, rsi_hi=70.0, require_volume=False, atr_mult_stop=2.0 |
| EOSUSDT | trend_following | 4 | 1.118 | 257% | rsi_hi=75.0, rr=2.5, require_volume=True, atr_mult_stop=2.0 |
| PEPEUSDT | gen_172f5c60 | 3 | 1.262 | 255% |  |
| PEPEUSDT | gen_89720053 | 3 | 1.192 | 252% |  |
| VETUSDT | trend_following | 5 | 1.115 | 243% | rsi_hi=70.0, rr=2.5, require_volume=True, atr_mult_stop=2.0 |
| FETUSDT | trend_following | 5 | 1.106 | 234% | rsi_hi=75.0, rr=2.0, require_volume=False, atr_mult_stop=2.0 |
| FLOKIUSDT | gen_01a17a01 | 3 | 1.203 | 220% |  |
| RUNEUSDT | trend_following | 4 | 1.109 | 217% | atr_mult_stop=2.0, rsi_hi=75.0, require_volume=True, rr=2.5 |
| ORDIUSDT | gen_5ead9d8f | 3 | 1.122 | 196% |  |
| STXUSDT | gen_01a17a01 | 3 | 1.211 | 192% |  |
| ZECUSDT | gen_89720053 | 3 | 1.766 | 157% |  |
| ALGOUSDT | mean_reversion | 5 | 2.038 | 156% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| SUIUSDT | gen_f7d69e95 | 3 | 1.13 | 152% |  |
| LDOUSDT | gen_bf58ca0d | 3 | 1.115 | 141% |  |
| WLDUSDT | trend_following | 5 | 1.109 | 139% | rr=2.0, rsi_hi=75.0, require_volume=False, atr_mult_stop=1.0 |
| KAVAUSDT | gen_1155382d | 3 | 1.238 | 133% |  |
| ROSEUSDT | gen_1155382d | 3 | 1.238 | 133% |  |
| RUNEUSDT | gen_1155382d | 3 | 1.238 | 133% |  |
| WAVESUSDT | gen_1155382d | 3 | 1.238 | 133% |  |
| GRTUSDT | mean_reversion | 5 | 1.846 | 127% | rsi_oversold=20.0, rsi_overbought=75.0, atr_mult_stop=1.2 |
| WLDUSDT | gen_172f5c60 | 3 | 1.128 | 125% |  |
| NEOUSDT | mean_reversion | 5 | 2.262 | 123% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| FLOWUSDT | gen_1155382d | 3 | 1.902 | 121% |  |
| AVAXUSDT | gen_fac646f3 | 3 | 1.118 | 121% |  |
| WLDUSDT | gen_01a17a01 | 3 | 1.131 | 120% |  |
| IOTAUSDT | gen_01a17a01 | 3 | 1.107 | 117% |  |
| RENDERUSDT | gen_149fa99c | 3 | 1.108 | 114% |  |
| SUIUSDT | gen_bf58ca0d | 3 | 1.107 | 114% |  |
| HBARUSDT | gen_89720053 | 3 | 1.12 | 104% |  |
| HBARUSDT | gen_172f5c60 | 3 | 1.116 | 93% |  |
| TIAUSDT | gen_01a17a01 | 3 | 1.112 | 89% |  |
| TIAUSDT | gen_172f5c60 | 3 | 1.101 | 85% |  |
| ENAUSDT | gen_1155382d | 3 | 3.711 | 84% |  |
| MINAUSDT | mean_reversion | 5 | 1.53 | 83% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| FTMUSDT | gen_89720053 | 3 | 1.324 | 82% |  |
| MKRUSDT | gen_89720053 | 3 | 1.324 | 82% |  |
| AVAXUSDT | breakout | 5 | 1.211 | 81% | rr=3.0, volume_spike=1.8, compression=0.05 |
| FILUSDT | mean_reversion | 4 | 1.647 | 80% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| ZECUSDT | gen_149fa99c | 3 | 1.209 | 73% |  |
| 1INCHUSDT | mean_reversion | 6 | 1.744 | 73% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| ARBUSDT | gen_1155382d | 3 | 1.256 | 68% |  |
| IOTAUSDT | mean_reversion | 6 | 1.368 | 67% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| WIFUSDT | breakout | 5 | 1.259 | 66% | rr=3.0, volume_spike=1.8, compression=0.1 |
| STXUSDT | mean_reversion | 5 | 1.563 | 65% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| GALAUSDT | breakout | 3 | 1.15 | 64% | compression=0.07, volume_spike=2.5, rr=2.5 |
| LDOUSDT | mean_reversion | 4 | 1.494 | 61% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| GALAUSDT | mean_reversion | 5 | 1.426 | 60% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| EOSUSDT | gen_f7d69e95 | 3 | 1.217 | 60% |  |
| FETUSDT | gen_f7d69e95 | 3 | 1.217 | 60% |  |
| TONUSDT | gen_f7d69e95 | 3 | 1.217 | 60% |  |
| VETUSDT | gen_f7d69e95 | 3 | 1.217 | 60% |  |
| XLMUSDT | gen_1155382d | 3 | 1.293 | 58% |  |
| SEIUSDT | gen_fac646f3 | 3 | 1.563 | 58% |  |
| EOSUSDT | gen_4cb69695 | 3 | 1.12 | 57% |  |
| FETUSDT | gen_4cb69695 | 3 | 1.12 | 57% |  |
| TONUSDT | gen_4cb69695 | 3 | 1.12 | 57% |  |
| VETUSDT | gen_4cb69695 | 3 | 1.12 | 57% |  |
| EOSUSDT | gen_bf58ca0d | 3 | 1.37 | 57% |  |
| FETUSDT | gen_bf58ca0d | 3 | 1.37 | 57% |  |
| TONUSDT | gen_bf58ca0d | 3 | 1.37 | 57% |  |
| VETUSDT | gen_bf58ca0d | 3 | 1.37 | 57% |  |
| WIFUSDT | gen_1155382d | 3 | 1.257 | 56% |  |
| YFIUSDT | mean_reversion | 5 | 1.539 | 55% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| CRVUSDT | mean_reversion | 3 | 1.324 | 55% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| IMXUSDT | gen_593d4a5d | 3 | 1.568 | 55% |  |
| ZECUSDT | gen_172f5c60 | 3 | 1.299 | 53% |  |
| JUPUSDT | breakout | 5 | 1.234 | 53% | rr=2.0, volume_spike=1.8, compression=0.05 |
| UNIUSDT | gen_1155382d | 3 | 1.18 | 52% |  |
| ZECUSDT | gen_01a17a01 | 3 | 1.291 | 50% |  |
| APTUSDT | mean_reversion | 6 | 1.594 | 49% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| MANAUSDT | mean_reversion | 4 | 1.433 | 48% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.2 |
| PEPEUSDT | breakout | 4 | 1.199 | 48% | rr=2.5, volume_spike=2.5, compression=0.1 |
| IMXUSDT | mean_reversion | 4 | 1.412 | 47% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.2 |
| DOGEUSDT | mean_reversion | 3 | 1.253 | 47% | rsi_overbought=80.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| MINAUSDT | gen_18b88216 | 3 | 1.563 | 45% |  |
| SUIUSDT | mean_reversion | 5 | 1.342 | 45% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| APEUSDT | gen_593d4a5d | 3 | 1.45 | 44% |  |
| EGLDUSDT | mean_reversion | 6 | 1.482 | 44% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| GALAUSDT | gen_1155382d | 3 | 1.116 | 42% |  |
| ORDIUSDT | gen_18b88216 | 3 | 1.38 | 42% |  |
| WIFUSDT | gen_18b88216 | 3 | 1.64 | 41% |  |
| CHZUSDT | mean_reversion | 6 | 1.421 | 41% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| ICPUSDT | gen_1155382d | 3 | 1.124 | 41% |  |
| DASHUSDT | gen_5ead9d8f | 3 | 1.168 | 41% |  |
| 1INCHUSDT | breakout | 5 | 1.11 | 38% | rr=3.0, volume_spike=1.8, compression=0.1 |
| ETCUSDT | mean_reversion | 6 | 1.279 | 38% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| GRTUSDT | gen_1155382d | 3 | 1.109 | 37% |  |
| BONKUSDT | breakout | 4 | 1.245 | 37% | compression=0.07, volume_spike=1.5, rr=3.0 |
| DASHUSDT | breakout | 5 | 1.802 | 36% | rr=2.5, volume_spike=2.5, compression=0.07 |
| LTCUSDT | mean_reversion | 3 | 1.32 | 36% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| ADAUSDT | mean_reversion | 6 | 1.313 | 35% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| ORDIUSDT | mean_reversion | 3 | 1.11 | 33% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| DASHUSDT | trend_following | 3 | 1.211 | 33% | atr_mult_stop=2.0, rsi_hi=70.0, require_volume=True, rr=2.0 |
| XRPUSDT | mean_reversion | 3 | 1.304 | 32% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| MANAUSDT | liquidity_grab | 5 | 1.514 | 32% | volume_spike=3.0, atr_mult_stop=1.5 |
| FLOKIUSDT | mean_reversion | 3 | 1.106 | 31% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| SUIUSDT | breakout | 5 | 1.133 | 31% | rr=2.5, volume_spike=1.8, compression=0.1 |
| ENSUSDT | gen_18b88216 | 3 | 1.331 | 30% |  |
| ATOMUSDT | mean_reversion | 6 | 1.341 | 29% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| FTMUSDT | gen_172f5c60 | 3 | 1.142 | 26% |  |
| MKRUSDT | gen_172f5c60 | 3 | 1.142 | 26% |  |
| DASHUSDT | mean_reversion | 3 | 1.744 | 25% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.2 |
| ZECUSDT | trend_following | 6 | 1.119 | 25% | rr=2.5, rsi_hi=65.0, require_volume=False, atr_mult_stop=1.5 |
| ARBUSDT | mean_reversion | 4 | 1.264 | 25% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| MASKUSDT | mean_reversion | 4 | 1.126 | 24% | rsi_oversold=20.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| ETHUSDT | mean_reversion | 3 | 1.339 | 24% | rsi_overbought=70.0, rsi_oversold=20.0, atr_mult_stop=1.8 |
| LDOUSDT | liquidity_grab | 5 | 1.195 | 24% | volume_spike=2.0, atr_mult_stop=0.8 |
| XLMUSDT | mean_reversion | 3 | 1.189 | 24% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| SEIUSDT | breakout | 4 | 2.008 | 23% | rr=2.5, volume_spike=2.5, compression=0.07 |
| CRVUSDT | gen_18b88216 | 3 | 1.171 | 23% |  |
| XRPUSDT | gen_1155382d | 3 | 1.102 | 22% |  |
| INJUSDT | mean_reversion | 5 | 1.173 | 22% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| DOTUSDT | mean_reversion | 5 | 1.244 | 20% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| FILUSDT | gen_593d4a5d | 3 | 1.169 | 20% |  |
| HBARUSDT | mean_reversion | 5 | 1.173 | 20% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| AAVEUSDT | mean_reversion | 5 | 1.219 | 19% | rsi_oversold=25.0, rsi_overbought=80.0, atr_mult_stop=1.2 |
| ARBUSDT | liquidity_grab | 5 | 1.906 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| ENAUSDT | breakout | 5 | 1.331 | 19% | rr=2.0, volume_spike=2.5, compression=0.07 |
| ALGOUSDT | liquidity_grab | 5 | 1.384 | 18% | volume_spike=3.0, atr_mult_stop=1.5 |
| ADAUSDT | gen_1b74ab2c | 3 | 4.952 | 17% |  |
| WIFUSDT | liquidity_grab | 5 | 1.364 | 17% | volume_spike=3.0, atr_mult_stop=1.5 |
| PYTHUSDT | mean_reversion | 4 | 1.169 | 17% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| 1INCHUSDT | liquidity_grab | 6 | 1.397 | 17% | volume_spike=3.0, atr_mult_stop=1.5 |
| FTMUSDT | gen_01a17a01 | 3 | 1.113 | 16% |  |
| MKRUSDT | gen_01a17a01 | 3 | 1.113 | 16% |  |
| ENSUSDT | liquidity_grab | 5 | 1.169 | 15% | volume_spike=3.0, atr_mult_stop=0.8 |
| JUPUSDT | mean_reversion | 4 | 1.177 | 14% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| TIAUSDT | mean_reversion | 4 | 1.127 | 12% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| MASKUSDT | gen_1b74ab2c | 3 | 2.117 | 11% |  |
| PYTHUSDT | liquidity_grab | 6 | 1.215 | 11% | volume_spike=2.5, atr_mult_stop=1.5 |
| GMTUSDT | gen_1b74ab2c | 3 | 2.012 | 10% |  |
| RENDERUSDT | mean_reversion | 5 | 1.148 | 9% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| TIAUSDT | liquidity_grab | 6 | 1.135 | 8% | volume_spike=2.0, atr_mult_stop=0.8 |
| IMXUSDT | liquidity_grab | 5 | 1.122 | 7% | volume_spike=2.5, atr_mult_stop=0.8 |
| SEIUSDT | gen_1155382d | 3 | 1.201 | 6% |  |
| SOLUSDT | liquidity_grab | 5 | 1.105 | 5% | volume_spike=2.5, atr_mult_stop=1.5 |
| ETCUSDT | gen_1b74ab2c | 3 | 1.792 | 5% |  |
| ZECUSDT | liquidity_grab | 6 | 1.318 | 4% | volume_spike=2.0, atr_mult_stop=0.8 |
| SEIUSDT | gen_18b88216 | 3 | 1.179 | 3% |  |
| BCHUSDT | gen_1b74ab2c | 3 | 1.307 | 2% |  |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-22 14:41 UTC · 560 coppie valutate, 74 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| ROSEUSDT | trend_following | 1.186 | 369% | 1108 | 34% |
| MKRUSDT | trend_following | 1.128 | 313% | 1547 | 36% |
| TONUSDT | trend_following | 1.124 | 277% | 1389 | 34% |
| FTMUSDT | trend_following | 1.117 | 264% | 1429 | 35% |
| EOSUSDT | trend_following | 1.118 | 257% | 1325 | 32% |
| VETUSDT | trend_following | 1.115 | 243% | 1192 | 35% |
| FETUSDT | trend_following | 1.106 | 234% | 1391 | 35% |
| ALGOUSDT | mean_reversion | 2.038 | 156% | 66 | 44% |
| WLDUSDT | trend_following | 1.109 | 139% | 814 | 38% |
| GRTUSDT | mean_reversion | 1.846 | 127% | 65 | 49% |
| NEOUSDT | mean_reversion | 2.262 | 123% | 49 | 51% |
| FILUSDT | breakout | 1.15 | 96% | 646 | 33% |
| MINAUSDT | mean_reversion | 1.53 | 83% | 49 | 45% |
| AVAXUSDT | breakout | 1.211 | 81% | 448 | 35% |
| DOGEUSDT | breakout | 1.198 | 81% | 449 | 30% |
| GRTUSDT | breakout | 1.1 | 76% | 704 | 28% |
| 1INCHUSDT | mean_reversion | 1.744 | 73% | 42 | 45% |
| IOTAUSDT | mean_reversion | 1.368 | 67% | 62 | 40% |
| WIFUSDT | breakout | 1.259 | 66% | 201 | 32% |
| STXUSDT | mean_reversion | 1.563 | 65% | 49 | 39% |
| LDOUSDT | mean_reversion | 1.494 | 61% | 57 | 28% |
| GALAUSDT | mean_reversion | 1.426 | 60% | 46 | 37% |
| YFIUSDT | mean_reversion | 1.539 | 55% | 51 | 35% |
| CRVUSDT | mean_reversion | 1.324 | 55% | 81 | 32% |
| JUPUSDT | breakout | 1.234 | 53% | 226 | 37% |
| APTUSDT | mean_reversion | 1.594 | 49% | 39 | 33% |
| MANAUSDT | mean_reversion | 1.433 | 48% | 43 | 42% |
| PEPEUSDT | breakout | 1.199 | 48% | 226 | 36% |
| UNIUSDT | mean_reversion | 1.442 | 47% | 45 | 33% |
| SUIUSDT | mean_reversion | 1.342 | 45% | 53 | 30% |
| EGLDUSDT | mean_reversion | 1.482 | 44% | 38 | 34% |
| CHZUSDT | mean_reversion | 1.421 | 41% | 45 | 27% |
| 1INCHUSDT | breakout | 1.11 | 38% | 359 | 29% |
| ETCUSDT | mean_reversion | 1.279 | 38% | 83 | 34% |
| MKRUSDT | breakout | 1.161 | 38% | 255 | 34% |
| DASHUSDT | breakout | 1.802 | 36% | 44 | 41% |
| ADAUSDT | mean_reversion | 1.313 | 35% | 43 | 44% |
| ORDIUSDT | mean_reversion | 1.11 | 33% | 112 | 32% |
| XRPUSDT | mean_reversion | 1.304 | 32% | 70 | 34% |
| MANAUSDT | liquidity_grab | 1.514 | 32% | 85 | 52% |
| SUIUSDT | breakout | 1.133 | 31% | 243 | 36% |
| ARUSDT | mean_reversion | 1.155 | 30% | 78 | 28% |
| ATOMUSDT | mean_reversion | 1.341 | 29% | 46 | 35% |
| FLOWUSDT | breakout | 1.117 | 28% | 286 | 37% |
| PYTHUSDT | breakout | 1.118 | 26% | 219 | 33% |
| LINKUSDT | mean_reversion | 1.286 | 25% | 39 | 36% |
| DASHUSDT | mean_reversion | 1.744 | 25% | 13 | 46% |
| ZECUSDT | trend_following | 1.119 | 25% | 113 | 36% |
| ARBUSDT | mean_reversion | 1.264 | 25% | 38 | 26% |
| KAVAUSDT | momentum_cross_asset | 1.317 | 24% | 97 | 42% |
| MASKUSDT | mean_reversion | 1.126 | 24% | 64 | 39% |
| LDOUSDT | liquidity_grab | 1.195 | 24% | 151 | 48% |
| XLMUSDT | mean_reversion | 1.189 | 24% | 62 | 31% |
| SEIUSDT | breakout | 2.008 | 23% | 36 | 47% |
| INJUSDT | mean_reversion | 1.173 | 22% | 42 | 38% |
| DOTUSDT | mean_reversion | 1.244 | 20% | 50 | 32% |
| HBARUSDT | mean_reversion | 1.173 | 20% | 44 | 23% |
| AAVEUSDT | mean_reversion | 1.219 | 19% | 29 | 34% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| ENAUSDT | breakout | 1.331 | 19% | 65 | 38% |
| ALGOUSDT | liquidity_grab | 1.384 | 18% | 78 | 62% |
| WIFUSDT | liquidity_grab | 1.364 | 17% | 44 | 64% |
| PYTHUSDT | mean_reversion | 1.169 | 17% | 34 | 41% |
| 1INCHUSDT | liquidity_grab | 1.397 | 17% | 76 | 68% |
| ENSUSDT | liquidity_grab | 1.169 | 15% | 126 | 49% |
| RENDERUSDT | breakout | 1.165 | 14% | 92 | 32% |
| JUPUSDT | mean_reversion | 1.177 | 14% | 27 | 41% |
| TIAUSDT | mean_reversion | 1.127 | 12% | 34 | 26% |
| PYTHUSDT | liquidity_grab | 1.215 | 11% | 53 | 57% |
| RENDERUSDT | mean_reversion | 1.148 | 9% | 20 | 30% |
| TIAUSDT | liquidity_grab | 1.135 | 8% | 72 | 49% |
| IMXUSDT | liquidity_grab | 1.122 | 7% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
| ZECUSDT | liquidity_grab | 1.318 | 4% | 18 | 50% |
