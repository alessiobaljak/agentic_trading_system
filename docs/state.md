# Stato sistema (snapshot)
_Generato: 2026-06-18 15:53 UTC_

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
- copertura universo: **32/50 crypto (64%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **38**
- universo scansionato: AAVEUSDT, ADAUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, FLOKIUSDT, FTMUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT
- aggiornato: 2026-06-18 11:59 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TONUSDT | trend_following | 3 | 1.167 | 371% | rsi_hi=75.0, rr=2.5, require_volume=False, atr_mult_stop=2.0 |
| ALGOUSDT | mean_reversion | 4 | 1.949 | 149% | rsi_oversold=25.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| GALAUSDT | mean_reversion | 4 | 1.571 | 102% | rsi_oversold=30.0, atr_mult_stop=1.0, rsi_overbought=70.0 |
| SUIUSDT | mean_reversion | 5 | 1.444 | 74% | rsi_oversold=20.0, atr_mult_stop=1.2, rsi_overbought=75.0 |
| AVAXUSDT | breakout | 4 | 1.189 | 69% | rr=3.0, volume_spike=1.8, compression=0.05 |
| PEPEUSDT | breakout | 3 | 1.218 | 62% | rr=3.0, volume_spike=1.5, compression=0.1 |
| STXUSDT | mean_reversion | 4 | 1.489 | 58% | rsi_oversold=25.0, atr_mult_stop=1.0, rsi_overbought=75.0 |
| SUIUSDT | breakout | 3 | 1.227 | 52% | rr=3.0, volume_spike=1.8, compression=0.1 |
| APTUSDT | mean_reversion | 4 | 1.561 | 51% | rsi_oversold=25.0, atr_mult_stop=1.0, rsi_overbought=75.0 |
| EGLDUSDT | mean_reversion | 3 | 1.532 | 48% | rsi_oversold=20.0, atr_mult_stop=1.0, rsi_overbought=70.0 |
| ATOMUSDT | mean_reversion | 4 | 1.572 | 48% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=75.0 |
| IMXUSDT | mean_reversion | 3 | 1.443 | 47% | rsi_oversold=20.0, atr_mult_stop=1.2, rsi_overbought=70.0 |
| HBARUSDT | mean_reversion | 4 | 1.356 | 44% | rsi_oversold=30.0, atr_mult_stop=1.8, rsi_overbought=75.0 |
| INJUSDT | mean_reversion | 5 | 1.354 | 41% | rsi_oversold=30.0, atr_mult_stop=1.0, rsi_overbought=70.0 |
| ETCUSDT | mean_reversion | 4 | 1.355 | 41% | rsi_oversold=25.0, atr_mult_stop=1.8, rsi_overbought=80.0 |
| UNIUSDT | mean_reversion | 3 | 1.303 | 36% | rsi_oversold=20.0, atr_mult_stop=1.0, rsi_overbought=70.0 |
| AAVEUSDT | mean_reversion | 4 | 1.321 | 35% | rsi_oversold=25.0, atr_mult_stop=1.0, rsi_overbought=75.0 |
| LTCUSDT | mean_reversion | 3 | 1.308 | 35% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| ADAUSDT | mean_reversion | 4 | 1.313 | 35% | rsi_oversold=20.0, atr_mult_stop=1.0, rsi_overbought=80.0 |
| SANDUSDT | mean_reversion | 3 | 1.302 | 35% | rsi_oversold=25.0, atr_mult_stop=1.8, rsi_overbought=80.0 |
| JUPUSDT | breakout | 4 | 1.194 | 35% | rr=2.5, volume_spike=2.5, compression=0.05 |
| XRPUSDT | mean_reversion | 3 | 1.363 | 34% | rsi_oversold=30.0, atr_mult_stop=1.8, rsi_overbought=75.0 |
| AVAXUSDT | mean_reversion | 3 | 1.274 | 33% | rsi_oversold=30.0, atr_mult_stop=1.0, rsi_overbought=80.0 |
| FILUSDT | mean_reversion | 5 | 1.177 | 24% | rsi_oversold=20.0, atr_mult_stop=1.2, rsi_overbought=70.0 |
| ORDIUSDT | mean_reversion | 3 | 1.114 | 22% | rsi_oversold=30.0, atr_mult_stop=1.0, rsi_overbought=75.0 |
| DOGEUSDT | mean_reversion | 3 | 1.138 | 21% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=80.0 |
| OPUSDT | mean_reversion | 3 | 1.128 | 20% | rsi_oversold=20.0, atr_mult_stop=1.0, rsi_overbought=75.0 |
| WIFUSDT | liquidity_grab | 3 | 1.44 | 20% | volume_spike=3.0, atr_mult_stop=1.5 |
| ALGOUSDT | liquidity_grab | 4 | 1.409 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| PYTHUSDT | mean_reversion | 4 | 1.218 | 19% | rsi_oversold=25.0, atr_mult_stop=1.2, rsi_overbought=70.0 |
| ARBUSDT | liquidity_grab | 4 | 1.906 | 19% | volume_spike=3.0, atr_mult_stop=1.5 |
| SEIUSDT | breakout | 4 | 1.349 | 17% | rr=2.0, volume_spike=1.5, compression=0.1 |
| ENAUSDT | breakout | 4 | 1.248 | 14% | rr=2.0, volume_spike=2.5, compression=0.07 |
| PYTHUSDT | liquidity_grab | 4 | 1.27 | 13% | volume_spike=2.5, atr_mult_stop=1.5 |
| ARBUSDT | mean_reversion | 3 | 1.115 | 12% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| ETHUSDT | mean_reversion | 4 | 1.1 | 9% | rsi_oversold=25.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| IMXUSDT | liquidity_grab | 5 | 1.1 | 5% | volume_spike=2.5, atr_mult_stop=0.8 |
| SOLUSDT | liquidity_grab | 5 | 1.105 | 5% | volume_spike=2.5, atr_mult_stop=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-18 11:59 UTC · 350 coppie valutate, 49 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| RUNEUSDT | trend_following | 1.148 | 316% | 1271 | 38% |
| WLDUSDT | trend_following | 1.208 | 230% | 590 | 42% |
| SUIUSDT | trend_following | 1.144 | 185% | 576 | 34% |
| ORDIUSDT | trend_following | 1.178 | 164% | 501 | 33% |
| ALGOUSDT | mean_reversion | 1.949 | 149% | 71 | 41% |
| TIAUSDT | trend_following | 1.13 | 146% | 504 | 36% |
| GALAUSDT | mean_reversion | 1.571 | 102% | 73 | 42% |
| SUIUSDT | mean_reversion | 1.444 | 74% | 64 | 42% |
| AVAXUSDT | breakout | 1.189 | 69% | 456 | 38% |
| PEPEUSDT | breakout | 1.218 | 62% | 249 | 30% |
| STXUSDT | mean_reversion | 1.489 | 58% | 51 | 39% |
| SHIBUSDT | mean_reversion | 1.523 | 54% | 49 | 33% |
| SUIUSDT | breakout | 1.227 | 52% | 224 | 33% |
| APTUSDT | mean_reversion | 1.561 | 51% | 37 | 38% |
| EGLDUSDT | mean_reversion | 1.532 | 48% | 42 | 36% |
| ATOMUSDT | mean_reversion | 1.572 | 48% | 33 | 42% |
| IMXUSDT | mean_reversion | 1.443 | 47% | 43 | 35% |
| WIFUSDT | breakout | 1.213 | 44% | 168 | 36% |
| HBARUSDT | mean_reversion | 1.356 | 44% | 35 | 40% |
| INJUSDT | mean_reversion | 1.354 | 41% | 45 | 36% |
| ETCUSDT | mean_reversion | 1.355 | 41% | 65 | 32% |
| LINKUSDT | breakout | 1.111 | 37% | 379 | 33% |
| AAVEUSDT | mean_reversion | 1.321 | 35% | 41 | 42% |
| ADAUSDT | mean_reversion | 1.313 | 35% | 43 | 44% |
| SANDUSDT | mean_reversion | 1.302 | 35% | 40 | 32% |
| JUPUSDT | breakout | 1.194 | 35% | 172 | 35% |
| XRPUSDT | mean_reversion | 1.363 | 34% | 57 | 35% |
| AVAXUSDT | mean_reversion | 1.274 | 33% | 65 | 31% |
| ENAUSDT | trend_following | 1.122 | 33% | 146 | 32% |
| XLMUSDT | mean_reversion | 1.17 | 29% | 65 | 35% |
| BONKUSDT | mean_reversion | 1.281 | 24% | 34 | 32% |
| FILUSDT | mean_reversion | 1.177 | 24% | 51 | 31% |
| ORDIUSDT | mean_reversion | 1.114 | 22% | 73 | 27% |
| FTMUSDT | momentum_cross_asset | 1.159 | 22% | 134 | 40% |
| VETUSDT | momentum_cross_asset | 1.159 | 22% | 134 | 40% |
| DOGEUSDT | mean_reversion | 1.138 | 21% | 47 | 43% |
| OPUSDT | mean_reversion | 1.128 | 20% | 59 | 30% |
| WIFUSDT | liquidity_grab | 1.44 | 20% | 43 | 65% |
| ALGOUSDT | liquidity_grab | 1.409 | 19% | 79 | 62% |
| PYTHUSDT | mean_reversion | 1.218 | 19% | 36 | 36% |
| ARBUSDT | liquidity_grab | 1.906 | 19% | 39 | 64% |
| JUPUSDT | mean_reversion | 1.196 | 17% | 31 | 29% |
| SEIUSDT | breakout | 1.349 | 17% | 61 | 43% |
| ENAUSDT | breakout | 1.248 | 14% | 68 | 43% |
| PYTHUSDT | liquidity_grab | 1.27 | 13% | 52 | 58% |
| ETHUSDT | mean_reversion | 1.1 | 9% | 99 | 35% |
| BTCUSDT | mean_reversion | 1.184 | 8% | 74 | 35% |
| IMXUSDT | liquidity_grab | 1.1 | 5% | 78 | 53% |
| SOLUSDT | liquidity_grab | 1.105 | 5% | 78 | 53% |
