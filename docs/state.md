# Stato sistema (snapshot)
_Generato: 2026-06-15 18:47 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- ultimo heartbeat: 2026-06-15 18:47 UTC

## Posizioni aperte
- ETHUSDT: long qty=2.409785426961468 @ 1826.42 uPnL=8.62703182852188
- SOLUSDT: long qty=52.778333477594366 @ 75.23 uPnL=21.111333391037295
- XRPUSDT: long qty=1904.8459155057085 @ 1.2788 uPnL=6.285991521168992

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **26/39 crypto (67%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **36**
- universo scansionato: AAVEUSDT, ADAUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, BCHUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, SANDUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, WLDUSDT, XRPUSDT
- aggiornato: 2026-06-15 13:24 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| XRPUSDT | trend_following | 3 | 1.343 | 167% | rr=2.5, require_volume=False, atr_mult_stop=2.0, rsi_hi=75.0 |
| WLDUSDT | trend_following | 3 | 1.175 | 156% | rr=2.5, require_volume=False, atr_mult_stop=1.0, rsi_hi=75.0 |
| PEPEUSDT | trend_following | 3 | 1.112 | 95% | rr=1.5, require_volume=True, atr_mult_stop=2.0, rsi_hi=75.0 |
| LINKUSDT | vwap_reversion | 3 | 1.141 | 92% | deviation_atr=2.0, atr_mult_stop=1.5 |
| LTCUSDT | vwap_reversion | 3 | 1.121 | 70% | deviation_atr=3.0, atr_mult_stop=1.5 |
| INJUSDT | mean_reversion | 3 | 1.652 | 55% | rsi_overbought=75.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| XRPUSDT | vwap_reversion | 3 | 1.103 | 54% | deviation_atr=1.5, atr_mult_stop=1.0 |
| PEPEUSDT | mean_reversion | 3 | 1.791 | 52% | rsi_overbought=70.0, atr_mult_stop=1.2, rsi_oversold=30.0 |
| GALAUSDT | mean_reversion | 3 | 1.89 | 47% | rsi_overbought=80.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| ORDIUSDT | mean_reversion | 3 | 1.281 | 43% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| ARBUSDT | mean_reversion | 3 | 1.652 | 43% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| ETCUSDT | mean_reversion | 3 | 1.845 | 42% | rsi_overbought=80.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| PYTHUSDT | mean_reversion | 3 | 1.505 | 41% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| AVAXUSDT | breakout | 3 | 1.323 | 37% | volume_spike=1.8, rr=2.5, compression=0.05 |
| IMXUSDT | mean_reversion | 3 | 1.469 | 36% | rsi_overbought=80.0, atr_mult_stop=1.2, rsi_oversold=30.0 |
| OPUSDT | breakout | 3 | 1.31 | 33% | volume_spike=1.8, rr=3.0, compression=0.05 |
| ADAUSDT | mean_reversion | 3 | 1.683 | 30% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| ATOMUSDT | mean_reversion | 3 | 1.697 | 30% | rsi_overbought=70.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| SUIUSDT | breakout | 3 | 1.223 | 27% | volume_spike=1.8, rr=1.5, compression=0.1 |
| NEARUSDT | breakout | 3 | 1.15 | 25% | volume_spike=1.8, rr=2.5, compression=0.05 |
| AVAXUSDT | mean_reversion | 3 | 1.503 | 23% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |
| ARBUSDT | liquidity_grab | 3 | 1.708 | 15% | volume_spike=2.5, atr_mult_stop=1.5 |
| INJUSDT | liquidity_grab | 3 | 1.524 | 15% | volume_spike=2.0, atr_mult_stop=0.8 |
| GALAUSDT | breakout | 3 | 1.143 | 15% | volume_spike=1.8, rr=3.0, compression=0.05 |
| JUPUSDT | mean_reversion | 3 | 1.175 | 14% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=30.0 |
| UNIUSDT | mean_reversion | 3 | 1.241 | 14% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| AAVEUSDT | liquidity_grab | 3 | 1.314 | 13% | volume_spike=2.0, atr_mult_stop=1.0 |
| DOTUSDT | liquidity_grab | 3 | 1.619 | 12% | volume_spike=2.5, atr_mult_stop=0.8 |
| TRXUSDT | breakout | 3 | 1.27 | 12% | volume_spike=1.8, rr=2.5, compression=0.07 |
| APTUSDT | mean_reversion | 3 | 1.126 | 11% | rsi_overbought=75.0, atr_mult_stop=1.2, rsi_oversold=30.0 |
| LTCUSDT | mean_reversion | 3 | 1.202 | 11% | rsi_overbought=70.0, atr_mult_stop=1.2, rsi_oversold=25.0 |
| AAVEUSDT | mean_reversion | 3 | 1.199 | 11% | rsi_overbought=70.0, atr_mult_stop=1.0, rsi_oversold=30.0 |
| LINKUSDT | liquidity_grab | 3 | 1.261 | 9% | volume_spike=2.0, atr_mult_stop=1.5 |
| ICPUSDT | mean_reversion | 3 | 1.129 | 9% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=20.0 |
| PYTHUSDT | liquidity_grab | 3 | 1.121 | 6% | volume_spike=2.5, atr_mult_stop=1.0 |
| TONUSDT | mean_reversion | 3 | 1.117 | 5% | rsi_overbought=75.0, atr_mult_stop=1.8, rsi_oversold=25.0 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-15 13:24 UTC · 234 coppie valutate, 36 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| XRPUSDT | trend_following | 1.343 | 167% | 310 | 38% |
| WLDUSDT | trend_following | 1.175 | 156% | 513 | 34% |
| PEPEUSDT | trend_following | 1.112 | 95% | 506 | 40% |
| LINKUSDT | vwap_reversion | 1.141 | 92% | 325 | 26% |
| LTCUSDT | vwap_reversion | 1.121 | 70% | 381 | 28% |
| INJUSDT | mean_reversion | 1.652 | 55% | 33 | 39% |
| XRPUSDT | vwap_reversion | 1.103 | 54% | 406 | 20% |
| PEPEUSDT | mean_reversion | 1.791 | 52% | 30 | 33% |
| GALAUSDT | mean_reversion | 1.89 | 47% | 20 | 45% |
| ORDIUSDT | mean_reversion | 1.281 | 43% | 45 | 44% |
| ARBUSDT | mean_reversion | 1.652 | 43% | 32 | 34% |
| ETCUSDT | mean_reversion | 1.845 | 42% | 24 | 38% |
| PYTHUSDT | mean_reversion | 1.505 | 41% | 30 | 43% |
| AVAXUSDT | breakout | 1.323 | 37% | 128 | 38% |
| IMXUSDT | mean_reversion | 1.469 | 36% | 40 | 30% |
| OPUSDT | breakout | 1.31 | 33% | 117 | 42% |
| ADAUSDT | mean_reversion | 1.683 | 30% | 26 | 46% |
| ATOMUSDT | mean_reversion | 1.697 | 30% | 16 | 38% |
| SUIUSDT | breakout | 1.223 | 27% | 142 | 45% |
| NEARUSDT | breakout | 1.15 | 25% | 157 | 32% |
| AVAXUSDT | mean_reversion | 1.503 | 23% | 24 | 42% |
| ARBUSDT | liquidity_grab | 1.708 | 15% | 34 | 65% |
| INJUSDT | liquidity_grab | 1.524 | 15% | 49 | 59% |
| GALAUSDT | breakout | 1.143 | 15% | 96 | 30% |
| JUPUSDT | mean_reversion | 1.175 | 14% | 32 | 38% |
| UNIUSDT | mean_reversion | 1.241 | 14% | 27 | 22% |
| AAVEUSDT | liquidity_grab | 1.314 | 13% | 63 | 54% |
| DOTUSDT | liquidity_grab | 1.619 | 12% | 31 | 48% |
| TRXUSDT | breakout | 1.27 | 12% | 87 | 37% |
| APTUSDT | mean_reversion | 1.126 | 11% | 34 | 32% |
| LTCUSDT | mean_reversion | 1.202 | 11% | 22 | 50% |
| AAVEUSDT | mean_reversion | 1.199 | 11% | 26 | 31% |
| LINKUSDT | liquidity_grab | 1.261 | 9% | 53 | 66% |
| ICPUSDT | mean_reversion | 1.129 | 9% | 27 | 26% |
| PYTHUSDT | liquidity_grab | 1.121 | 6% | 49 | 41% |
| TONUSDT | mean_reversion | 1.117 | 5% | 23 | 35% |
