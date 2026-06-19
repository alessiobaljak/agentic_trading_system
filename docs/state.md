# Stato sistema (snapshot)
_Generato: 2026-06-19 10:57 UTC_

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
- coppie validate (>= 3 pass OOS): **50**
- universo scansionato: AAVEUSDT, ADAUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, FLOKIUSDT, FTMUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT
- aggiornato: 2026-06-19 06:01 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TONUSDT | trend_following | 5 | 1.198 | 404% | atr_mult_stop=2.0, rr=2.5, rsi_hi=75.0, require_volume=False |
| VETUSDT | trend_following | 5 | 1.173 | 362% | atr_mult_stop=2.0, rr=2.5, rsi_hi=75.0, require_volume=False |
| RUNEUSDT | trend_following | 4 | 1.146 | 318% | atr_mult_stop=2.0, rr=2.5, rsi_hi=70.0, require_volume=False |
| FTMUSDT | trend_following | 5 | 1.151 | 313% | atr_mult_stop=1.5, rr=2.5, rsi_hi=75.0, require_volume=True |
| WLDUSDT | trend_following | 3 | 1.129 | 141% | atr_mult_stop=1.0, rr=2.5, rsi_hi=75.0, require_volume=True |
| TIAUSDT | trend_following | 3 | 1.126 | 129% | atr_mult_stop=2.0, rr=1.5, rsi_hi=75.0, require_volume=False |
| ORDIUSDT | trend_following | 3 | 1.107 | 115% | atr_mult_stop=1.0, rr=2.5, rsi_hi=65.0, require_volume=True |
| GALAUSDT | mean_reversion | 7 | 1.65 | 98% | atr_mult_stop=1.8, rsi_oversold=25.0, rsi_overbought=80.0 |
| WIFUSDT | breakout | 5 | 1.222 | 91% | compression=0.1, rr=2.5, volume_spike=1.8 |
| ALGOUSDT | mean_reversion | 7 | 1.538 | 81% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=70.0 |
| AVAXUSDT | breakout | 7 | 1.18 | 66% | compression=0.05, rr=3.0, volume_spike=1.8 |
| APTUSDT | mean_reversion | 7 | 1.643 | 63% | atr_mult_stop=1.0, rsi_oversold=25.0, rsi_overbought=70.0 |
| SUIUSDT | mean_reversion | 8 | 1.505 | 60% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=70.0 |
| AAVEUSDT | mean_reversion | 7 | 1.885 | 53% | atr_mult_stop=1.0, rsi_oversold=25.0, rsi_overbought=80.0 |
| SUIUSDT | breakout | 6 | 1.184 | 51% | compression=0.1, rr=2.5, volume_spike=1.8 |
| INJUSDT | mean_reversion | 8 | 1.448 | 48% | atr_mult_stop=1.0, rsi_oversold=25.0, rsi_overbought=75.0 |
| ATOMUSDT | mean_reversion | 7 | 1.8 | 47% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=75.0 |
| DOGEUSDT | mean_reversion | 4 | 1.253 | 47% | atr_mult_stop=1.8, rsi_oversold=20.0, rsi_overbought=80.0 |
| EGLDUSDT | mean_reversion | 6 | 1.395 | 44% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=80.0 |
| UNIUSDT | mean_reversion | 5 | 1.34 | 41% | atr_mult_stop=1.0, rsi_oversold=20.0, rsi_overbought=80.0 |
| PEPEUSDT | breakout | 4 | 1.163 | 39% | compression=0.1, rr=2.5, volume_spike=2.5 |
| APTUSDT | breakout | 3 | 1.134 | 38% | compression=0.05, rr=2.0, volume_spike=1.8 |
| DOTUSDT | mean_reversion | 5 | 1.528 | 37% | atr_mult_stop=1.2, rsi_oversold=25.0, rsi_overbought=75.0 |
| HBARUSDT | mean_reversion | 7 | 1.236 | 36% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=70.0 |
| XRPUSDT | mean_reversion | 4 | 1.358 | 34% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=80.0 |
| JUPUSDT | breakout | 7 | 1.159 | 33% | compression=0.05, rr=2.5, volume_spike=1.5 |
| STXUSDT | mean_reversion | 7 | 1.236 | 32% | atr_mult_stop=1.8, rsi_oversold=30.0, rsi_overbought=75.0 |
| ETCUSDT | mean_reversion | 7 | 1.309 | 31% | atr_mult_stop=1.8, rsi_oversold=25.0, rsi_overbought=80.0 |
| BONKUSDT | breakout | 4 | 1.159 | 31% | compression=0.1, rr=2.5, volume_spike=1.5 |
| IMXUSDT | mean_reversion | 6 | 1.236 | 29% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| ORDIUSDT | mean_reversion | 4 | 1.104 | 29% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=80.0 |
| LTCUSDT | mean_reversion | 4 | 1.256 | 28% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| ENAUSDT | breakout | 6 | 1.575 | 26% | compression=0.07, rr=1.5, volume_spike=2.5 |
| VETUSDT | momentum_cross_asset | 4 | 1.24 | 26% | atr_mult_stop=1.0, rr=2.0, btc_move_threshold=0.4 |
| SEIUSDT | breakout | 7 | 2.155 | 25% | compression=0.07, rr=2.5, volume_spike=2.5 |
| FILUSDT | mean_reversion | 8 | 1.177 | 24% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| OPUSDT | mean_reversion | 4 | 1.13 | 23% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=70.0 |
| ADAUSDT | mean_reversion | 7 | 1.215 | 23% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=75.0 |
| WIFUSDT | liquidity_grab | 6 | 1.44 | 20% | atr_mult_stop=1.5, volume_spike=3.0 |
| ALGOUSDT | liquidity_grab | 7 | 1.409 | 19% | atr_mult_stop=1.5, volume_spike=3.0 |
| ARBUSDT | liquidity_grab | 7 | 1.906 | 19% | atr_mult_stop=1.5, volume_spike=3.0 |
| PYTHUSDT | mean_reversion | 5 | 1.164 | 17% | atr_mult_stop=1.0, rsi_oversold=25.0, rsi_overbought=70.0 |
| RUNEUSDT | momentum_cross_asset | 3 | 1.161 | 16% | atr_mult_stop=2.0, rr=1.5, btc_move_threshold=0.4 |
| SANDUSDT | mean_reversion | 4 | 1.135 | 16% | atr_mult_stop=1.2, rsi_oversold=20.0, rsi_overbought=70.0 |
| ARBUSDT | mean_reversion | 6 | 1.128 | 15% | atr_mult_stop=1.8, rsi_oversold=25.0, rsi_overbought=80.0 |
| AVAXUSDT | mean_reversion | 4 | 1.118 | 14% | atr_mult_stop=1.0, rsi_oversold=30.0, rsi_overbought=75.0 |
| PYTHUSDT | liquidity_grab | 7 | 1.27 | 13% | atr_mult_stop=1.5, volume_spike=2.5 |
| ETHUSDT | mean_reversion | 4 | 1.1 | 9% | atr_mult_stop=1.8, rsi_oversold=25.0, rsi_overbought=70.0 |
| IMXUSDT | liquidity_grab | 8 | 1.1 | 5% | atr_mult_stop=0.8, volume_spike=2.5 |
| SOLUSDT | liquidity_grab | 8 | 1.105 | 5% | atr_mult_stop=1.5, volume_spike=2.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-19 06:01 UTC · 350 coppie valutate, 45 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| TONUSDT | trend_following | 1.198 | 404% | 1138 | 34% |
| VETUSDT | trend_following | 1.173 | 362% | 1272 | 33% |
| RUNEUSDT | trend_following | 1.146 | 318% | 1325 | 33% |
| FTMUSDT | trend_following | 1.151 | 313% | 1426 | 34% |
| WLDUSDT | trend_following | 1.129 | 141% | 658 | 33% |
| FILUSDT | breakout | 1.169 | 113% | 667 | 33% |
| GALAUSDT | mean_reversion | 1.65 | 98% | 55 | 40% |
| WIFUSDT | breakout | 1.222 | 91% | 308 | 32% |
| ALGOUSDT | mean_reversion | 1.538 | 81% | 65 | 42% |
| FLOKIUSDT | breakout | 1.168 | 72% | 376 | 31% |
| AVAXUSDT | breakout | 1.18 | 66% | 457 | 38% |
| APTUSDT | mean_reversion | 1.643 | 63% | 48 | 35% |
| SUIUSDT | mean_reversion | 1.505 | 60% | 43 | 40% |
| DOGEUSDT | breakout | 1.157 | 56% | 408 | 30% |
| AAVEUSDT | mean_reversion | 1.885 | 53% | 33 | 39% |
| SUIUSDT | breakout | 1.184 | 51% | 275 | 32% |
| INJUSDT | mean_reversion | 1.448 | 48% | 40 | 38% |
| ATOMUSDT | mean_reversion | 1.8 | 47% | 28 | 32% |
| DOGEUSDT | mean_reversion | 1.253 | 47% | 71 | 41% |
| EGLDUSDT | mean_reversion | 1.395 | 44% | 44 | 36% |
| UNIUSDT | mean_reversion | 1.34 | 41% | 53 | 36% |
| PEPEUSDT | breakout | 1.163 | 39% | 211 | 33% |
| DOTUSDT | mean_reversion | 1.528 | 37% | 43 | 35% |
| HBARUSDT | mean_reversion | 1.236 | 36% | 43 | 35% |
| JUPUSDT | breakout | 1.159 | 33% | 208 | 35% |
| STXUSDT | mean_reversion | 1.236 | 32% | 49 | 37% |
| ETCUSDT | mean_reversion | 1.309 | 31% | 51 | 28% |
| IMXUSDT | mean_reversion | 1.236 | 29% | 42 | 38% |
| ORDIUSDT | mean_reversion | 1.104 | 29% | 97 | 32% |
| ENAUSDT | breakout | 1.575 | 26% | 57 | 44% |
| SEIUSDT | breakout | 2.155 | 25% | 36 | 50% |
| FILUSDT | mean_reversion | 1.177 | 24% | 51 | 31% |
| OPUSDT | mean_reversion | 1.13 | 23% | 73 | 30% |
| ADAUSDT | mean_reversion | 1.215 | 23% | 46 | 37% |
| WIFUSDT | liquidity_grab | 1.44 | 20% | 43 | 65% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| PYTHUSDT | mean_reversion | 1.164 | 17% | 43 | 33% |
| RUNEUSDT | momentum_cross_asset | 1.161 | 16% | 94 | 40% |
| ARBUSDT | mean_reversion | 1.128 | 15% | 40 | 30% |
| PYTHUSDT | liquidity_grab | 1.27 | 13% | 52 | 58% |
| TIAUSDT | mean_reversion | 1.121 | 13% | 31 | 29% |
| IMXUSDT | liquidity_grab | 1.1 | 5% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
| VETUSDT | mean_reversion | 1.109 | 1% | 12 | 33% |
