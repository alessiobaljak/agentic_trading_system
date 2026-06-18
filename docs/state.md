# Stato sistema (snapshot)
_Generato: 2026-06-18 18:36 UTC_

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
- copertura universo: **36/50 crypto (72%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **45**
- universo scansionato: AAVEUSDT, ADAUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, FLOKIUSDT, FTMUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT
- aggiornato: 2026-06-18 18:24 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TONUSDT | trend_following | 3 | 1.167 | 371% | rsi_hi=75.0, atr_mult_stop=2.0, rr=2.5, require_volume=False |
| VETUSDT | trend_following | 3 | 1.141 | 312% | rsi_hi=70.0, atr_mult_stop=2.0, rr=2.5, require_volume=False |
| FTMUSDT | trend_following | 3 | 1.141 | 308% | rsi_hi=75.0, atr_mult_stop=2.0, rr=2.5, require_volume=False |
| ALGOUSDT | mean_reversion | 5 | 2.045 | 158% | atr_mult_stop=1.8, rsi_oversold=25.0, rsi_overbought=70.0 |
| ORDIUSDT | trend_following | 3 | 1.107 | 115% | rsi_hi=65.0, atr_mult_stop=1.0, rr=2.5, require_volume=True |
| WIFUSDT | breakout | 3 | 1.303 | 93% | volume_spike=1.5, compression=0.1, rr=3.0 |
| AVAXUSDT | breakout | 5 | 1.305 | 89% | volume_spike=1.8, compression=0.05, rr=3.0 |
| GALAUSDT | mean_reversion | 5 | 1.519 | 77% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=80.0 |
| AAVEUSDT | mean_reversion | 5 | 2.225 | 68% | atr_mult_stop=1.0, rsi_oversold=20.0, rsi_overbought=70.0 |
| JUPUSDT | breakout | 5 | 1.295 | 62% | volume_spike=1.5, compression=0.05, rr=2.0 |
| PEPEUSDT | breakout | 3 | 1.218 | 62% | volume_spike=1.5, compression=0.1, rr=3.0 |
| FILUSDT | mean_reversion | 6 | 1.595 | 61% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=80.0 |
| ADAUSDT | mean_reversion | 5 | 1.714 | 60% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=80.0 |
| INJUSDT | mean_reversion | 6 | 1.591 | 58% | atr_mult_stop=1.0, rsi_oversold=20.0, rsi_overbought=70.0 |
| EGLDUSDT | mean_reversion | 4 | 1.526 | 49% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=75.0 |
| SUIUSDT | breakout | 4 | 1.17 | 48% | volume_spike=1.8, compression=0.1, rr=3.0 |
| STXUSDT | mean_reversion | 5 | 1.453 | 47% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=75.0 |
| APTUSDT | mean_reversion | 5 | 1.59 | 47% | atr_mult_stop=1.0, rsi_oversold=25.0, rsi_overbought=75.0 |
| IMXUSDT | mean_reversion | 4 | 1.385 | 45% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| HBARUSDT | mean_reversion | 5 | 1.298 | 44% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=70.0 |
| ATOMUSDT | mean_reversion | 5 | 1.595 | 39% | atr_mult_stop=1.0, rsi_oversold=20.0, rsi_overbought=75.0 |
| UNIUSDT | mean_reversion | 3 | 1.303 | 36% | atr_mult_stop=1.0, rsi_oversold=20.0, rsi_overbought=70.0 |
| SUIUSDT | mean_reversion | 6 | 1.218 | 35% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| ENAUSDT | breakout | 5 | 1.515 | 34% | volume_spike=1.8, compression=0.07, rr=2.5 |
| XRPUSDT | mean_reversion | 3 | 1.363 | 34% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=75.0 |
| AVAXUSDT | mean_reversion | 3 | 1.274 | 33% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=80.0 |
| ARBUSDT | mean_reversion | 4 | 1.336 | 33% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=80.0 |
| ETCUSDT | mean_reversion | 5 | 1.251 | 32% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=75.0 |
| DOTUSDT | mean_reversion | 3 | 1.412 | 32% | atr_mult_stop=1.2, rsi_oversold=25.0, rsi_overbought=70.0 |
| SEIUSDT | breakout | 5 | 1.559 | 30% | volume_spike=1.5, compression=0.1, rr=3.0 |
| LTCUSDT | mean_reversion | 4 | 1.256 | 28% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| VETUSDT | momentum_cross_asset | 3 | 1.24 | 26% | atr_mult_stop=1.0, btc_move_threshold=0.4, rr=2.0 |
| ORDIUSDT | mean_reversion | 3 | 1.114 | 22% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=75.0 |
| DOGEUSDT | mean_reversion | 3 | 1.138 | 21% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=80.0 |
| BONKUSDT | breakout | 3 | 1.104 | 20% | volume_spike=1.8, compression=0.07, rr=3.0 |
| OPUSDT | mean_reversion | 3 | 1.128 | 20% | atr_mult_stop=1.0, rsi_oversold=20.0, rsi_overbought=75.0 |
| WIFUSDT | liquidity_grab | 4 | 1.44 | 20% | atr_mult_stop=1.5, volume_spike=3.0 |
| ALGOUSDT | liquidity_grab | 5 | 1.409 | 19% | atr_mult_stop=1.5, volume_spike=3.0 |
| PYTHUSDT | mean_reversion | 4 | 1.218 | 19% | atr_mult_stop=1.2, rsi_oversold=25.0, rsi_overbought=70.0 |
| ARBUSDT | liquidity_grab | 5 | 1.906 | 19% | atr_mult_stop=1.5, volume_spike=3.0 |
| SANDUSDT | mean_reversion | 4 | 1.135 | 16% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| PYTHUSDT | liquidity_grab | 5 | 1.27 | 13% | atr_mult_stop=1.5, volume_spike=2.5 |
| ETHUSDT | mean_reversion | 4 | 1.1 | 9% | atr_mult_stop=1.8, rsi_oversold=25.0, rsi_overbought=70.0 |
| IMXUSDT | liquidity_grab | 6 | 1.1 | 5% | atr_mult_stop=0.8, volume_spike=2.5 |
| SOLUSDT | liquidity_grab | 6 | 1.105 | 5% | atr_mult_stop=1.5, volume_spike=2.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-18 17:04 UTC · 350 coppie valutate, 41 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| VETUSDT | trend_following | 1.141 | 312% | 1352 | 33% |
| FTMUSDT | trend_following | 1.141 | 308% | 1337 | 33% |
| ALGOUSDT | mean_reversion | 2.045 | 158% | 66 | 47% |
| ORDIUSDT | trend_following | 1.107 | 115% | 577 | 34% |
| TIAUSDT | trend_following | 1.102 | 112% | 639 | 34% |
| WIFUSDT | breakout | 1.303 | 93% | 237 | 32% |
| AVAXUSDT | breakout | 1.305 | 89% | 388 | 39% |
| FILUSDT | breakout | 1.119 | 78% | 681 | 33% |
| GALAUSDT | mean_reversion | 1.519 | 77% | 64 | 33% |
| AAVEUSDT | mean_reversion | 2.225 | 68% | 36 | 47% |
| LINKUSDT | breakout | 1.159 | 66% | 438 | 33% |
| JUPUSDT | breakout | 1.295 | 62% | 220 | 38% |
| FILUSDT | mean_reversion | 1.595 | 61% | 34 | 41% |
| ADAUSDT | mean_reversion | 1.714 | 60% | 41 | 37% |
| INJUSDT | mean_reversion | 1.591 | 58% | 40 | 40% |
| EGLDUSDT | mean_reversion | 1.526 | 49% | 41 | 39% |
| SUIUSDT | breakout | 1.17 | 48% | 272 | 29% |
| STXUSDT | mean_reversion | 1.453 | 47% | 42 | 38% |
| APTUSDT | mean_reversion | 1.59 | 47% | 36 | 33% |
| IMXUSDT | mean_reversion | 1.385 | 45% | 41 | 39% |
| HBARUSDT | mean_reversion | 1.298 | 44% | 41 | 39% |
| ATOMUSDT | mean_reversion | 1.595 | 39% | 29 | 31% |
| XLMUSDT | mean_reversion | 1.184 | 36% | 82 | 33% |
| SUIUSDT | mean_reversion | 1.218 | 35% | 59 | 39% |
| FLOKIUSDT | mean_reversion | 1.184 | 35% | 49 | 37% |
| ENAUSDT | breakout | 1.515 | 34% | 74 | 36% |
| ARBUSDT | mean_reversion | 1.336 | 33% | 44 | 25% |
| ETCUSDT | mean_reversion | 1.251 | 32% | 73 | 36% |
| DOTUSDT | mean_reversion | 1.412 | 32% | 49 | 33% |
| SEIUSDT | breakout | 1.559 | 30% | 61 | 36% |
| LTCUSDT | mean_reversion | 1.256 | 28% | 70 | 37% |
| VETUSDT | momentum_cross_asset | 1.24 | 26% | 138 | 44% |
| PYTHUSDT | breakout | 1.111 | 23% | 205 | 34% |
| BONKUSDT | breakout | 1.104 | 20% | 183 | 32% |
| WIFUSDT | liquidity_grab | 1.44 | 20% | 43 | 65% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| SANDUSDT | mean_reversion | 1.135 | 16% | 45 | 33% |
| PYTHUSDT | liquidity_grab | 1.27 | 13% | 52 | 58% |
| IMXUSDT | liquidity_grab | 1.1 | 5% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
