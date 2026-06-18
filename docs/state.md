# Stato sistema (snapshot)
_Generato: 2026-06-18 10:48 UTC_

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
- stato: **🔄 in corso**
- copertura universo: **24/50 crypto (48%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **27**
- universo scansionato: AAVEUSDT, ADAUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, FLOKIUSDT, FTMUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT
- aggiornato: 2026-06-18 09:24 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TONUSDT | trend_following | 3 | 1.167 | 371% | rr=2.5, atr_mult_stop=2.0, require_volume=False, rsi_hi=75.0 |
| ALGOUSDT | mean_reversion | 3 | 1.949 | 149% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| AVAXUSDT | breakout | 3 | 1.255 | 105% | rr=3.0, compression=0.1, volume_spike=2.5 |
| INJUSDT | mean_reversion | 4 | 1.769 | 76% | rsi_overbought=70.0, atr_mult_stop=1.2, rsi_oversold=30.0 |
| GALAUSDT | mean_reversion | 3 | 1.386 | 60% | rsi_overbought=80.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| FILUSDT | mean_reversion | 4 | 1.383 | 57% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| AAVEUSDT | mean_reversion | 3 | 1.931 | 55% | rsi_overbought=75.0, atr_mult_stop=1.0, rsi_oversold=25.0 |
| SUIUSDT | mean_reversion | 4 | 1.435 | 55% | rsi_overbought=80.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| STXUSDT | mean_reversion | 3 | 1.453 | 47% | rsi_overbought=75.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| APTUSDT | mean_reversion | 3 | 1.59 | 47% | rsi_overbought=75.0, atr_mult_stop=1.0, rsi_oversold=25.0 |
| ATOMUSDT | mean_reversion | 3 | 1.487 | 41% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| UNIUSDT | mean_reversion | 3 | 1.303 | 36% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| LTCUSDT | mean_reversion | 3 | 1.308 | 35% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| ADAUSDT | mean_reversion | 3 | 1.313 | 35% | rsi_overbought=80.0, atr_mult_stop=1.0, rsi_oversold=20.0 |
| HBARUSDT | mean_reversion | 3 | 1.213 | 33% | rsi_overbought=70.0, atr_mult_stop=1.2, rsi_oversold=30.0 |
| JUPUSDT | breakout | 3 | 1.133 | 30% | rr=3.0, compression=0.05, volume_spike=1.5 |
| SEIUSDT | breakout | 3 | 1.453 | 26% | rr=2.5, compression=0.1, volume_spike=1.5 |
| ETCUSDT | mean_reversion | 3 | 1.235 | 26% | rsi_overbought=80.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| ENAUSDT | breakout | 3 | 1.503 | 21% | rr=1.5, compression=0.07, volume_spike=2.5 |
| ALGOUSDT | liquidity_grab | 3 | 1.409 | 19% | atr_mult_stop=1.5, volume_spike=3.0 |
| ARBUSDT | liquidity_grab | 3 | 1.906 | 19% | atr_mult_stop=1.5, volume_spike=3.0 |
| ETHUSDT | mean_reversion | 3 | 1.152 | 18% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| PYTHUSDT | mean_reversion | 3 | 1.169 | 15% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| PYTHUSDT | liquidity_grab | 3 | 1.27 | 13% | atr_mult_stop=1.5, volume_spike=2.5 |
| ARBUSDT | mean_reversion | 3 | 1.115 | 12% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| IMXUSDT | liquidity_grab | 4 | 1.1 | 5% | atr_mult_stop=0.8, volume_spike=2.5 |
| SOLUSDT | liquidity_grab | 4 | 1.105 | 5% | atr_mult_stop=1.5, volume_spike=2.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-18 09:24 UTC · 350 coppie valutate, 41 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| FTMUSDT | trend_following | 1.167 | 371% | 1362 | 33% |
| RUNEUSDT | trend_following | 1.17 | 357% | 1540 | 33% |
| VETUSDT | trend_following | 1.145 | 296% | 1121 | 33% |
| ALGOUSDT | mean_reversion | 1.949 | 149% | 71 | 41% |
| XRPUSDT | trend_following | 1.103 | 109% | 678 | 36% |
| AVAXUSDT | breakout | 1.255 | 105% | 454 | 33% |
| INJUSDT | mean_reversion | 1.769 | 76% | 46 | 39% |
| GALAUSDT | breakout | 1.182 | 73% | 411 | 39% |
| GALAUSDT | mean_reversion | 1.386 | 60% | 55 | 36% |
| ENAUSDT | trend_following | 1.181 | 57% | 196 | 34% |
| FILUSDT | mean_reversion | 1.383 | 57% | 61 | 38% |
| AAVEUSDT | mean_reversion | 1.931 | 55% | 30 | 37% |
| SUIUSDT | mean_reversion | 1.435 | 55% | 50 | 40% |
| EGLDUSDT | mean_reversion | 1.591 | 49% | 39 | 36% |
| IMXUSDT | mean_reversion | 1.412 | 47% | 40 | 40% |
| STXUSDT | mean_reversion | 1.453 | 47% | 42 | 38% |
| APTUSDT | mean_reversion | 1.59 | 47% | 36 | 33% |
| ATOMUSDT | mean_reversion | 1.487 | 41% | 36 | 39% |
| UNIUSDT | mean_reversion | 1.303 | 36% | 59 | 30% |
| ADAUSDT | mean_reversion | 1.313 | 35% | 43 | 44% |
| PYTHUSDT | breakout | 1.154 | 34% | 222 | 33% |
| HBARUSDT | mean_reversion | 1.213 | 33% | 43 | 35% |
| SUIUSDT | breakout | 1.14 | 33% | 225 | 29% |
| FTMUSDT | breakout | 1.142 | 32% | 260 | 38% |
| SEIUSDT | breakout | 1.453 | 26% | 70 | 39% |
| ETCUSDT | mean_reversion | 1.235 | 26% | 60 | 35% |
| RUNEUSDT | momentum_cross_asset | 1.159 | 22% | 134 | 40% |
| VETUSDT | momentum_cross_asset | 1.159 | 22% | 134 | 40% |
| ENAUSDT | breakout | 1.503 | 21% | 55 | 44% |
| WIFUSDT | liquidity_grab | 1.44 | 20% | 43 | 65% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| ETHUSDT | mean_reversion | 1.152 | 18% | 148 | 40% |
| PYTHUSDT | mean_reversion | 1.169 | 15% | 35 | 29% |
| PYTHUSDT | liquidity_grab | 1.27 | 13% | 52 | 58% |
| ARBUSDT | mean_reversion | 1.115 | 12% | 36 | 28% |
| VETUSDT | breakout | 1.138 | 7% | 57 | 39% |
| BNBUSDT | mean_reversion | 1.114 | 6% | 87 | 29% |
| IMXUSDT | liquidity_grab | 1.1 | 5% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
| BTCUSDT | mean_reversion | 1.105 | 4% | 67 | 34% |
