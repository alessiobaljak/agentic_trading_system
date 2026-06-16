# Stato sistema (snapshot)
_Generato: 2026-06-16 23:49 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$9,999.77**
- ultimo heartbeat: 2026-06-16 23:48 UTC

## Ultima decisione
- esito: **⚪ FLAT** (2026-06-16 23:45 UTC)
- motivo: XRPUSDT già aperto
- asset valutati: 5 · segnali: 1 · miglior segnale XRPUSDT vwap_reversion (conf. 80.0/soglia 30)

## Posizioni aperte
- XRPUSDT: long qty=4122.679245479786 @ 1.2213 uPnL=-14.7621188010821

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **26/39 crypto (67%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **37**
- universo scansionato: AAVEUSDT, ADAUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, BCHUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, SANDUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, WLDUSDT, XRPUSDT
- aggiornato: 2026-06-16 22:10 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TONUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| XRPUSDT | trend_following | 8 | 1.343 | 167% | atr_mult_stop=2.0, require_volume=False, rr=2.5, rsi_hi=75.0 |
| WLDUSDT | trend_following | 8 | 1.175 | 156% | atr_mult_stop=1.0, require_volume=False, rr=2.5, rsi_hi=75.0 |
| PEPEUSDT | trend_following | 8 | 1.112 | 95% | atr_mult_stop=2.0, require_volume=True, rr=1.5, rsi_hi=75.0 |
| LINKUSDT | vwap_reversion | 8 | 1.141 | 92% | atr_mult_stop=1.5, deviation_atr=2.0 |
| LTCUSDT | vwap_reversion | 8 | 1.121 | 70% | atr_mult_stop=1.5, deviation_atr=3.0 |
| INJUSDT | mean_reversion | 8 | 1.652 | 55% | atr_mult_stop=1.0, rsi_overbought=75.0, rsi_oversold=30.0 |
| XRPUSDT | vwap_reversion | 8 | 1.103 | 54% | atr_mult_stop=1.0, deviation_atr=1.5 |
| PEPEUSDT | mean_reversion | 8 | 1.791 | 52% | atr_mult_stop=1.2, rsi_overbought=70.0, rsi_oversold=30.0 |
| GALAUSDT | mean_reversion | 8 | 1.89 | 47% | atr_mult_stop=1.0, rsi_overbought=80.0, rsi_oversold=30.0 |
| ORDIUSDT | mean_reversion | 8 | 1.281 | 43% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=20.0 |
| ARBUSDT | mean_reversion | 8 | 1.652 | 43% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=30.0 |
| ETCUSDT | mean_reversion | 8 | 1.845 | 42% | atr_mult_stop=1.8, rsi_overbought=80.0, rsi_oversold=30.0 |
| PYTHUSDT | mean_reversion | 8 | 1.505 | 41% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=25.0 |
| AVAXUSDT | breakout | 8 | 1.323 | 37% | compression=0.05, rr=2.5, volume_spike=1.8 |
| IMXUSDT | mean_reversion | 8 | 1.469 | 36% | atr_mult_stop=1.2, rsi_overbought=80.0, rsi_oversold=30.0 |
| OPUSDT | breakout | 8 | 1.31 | 33% | compression=0.05, rr=3.0, volume_spike=1.8 |
| ADAUSDT | mean_reversion | 8 | 1.683 | 30% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| ATOMUSDT | mean_reversion | 8 | 1.697 | 30% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=25.0 |
| SUIUSDT | breakout | 8 | 1.223 | 27% | compression=0.1, rr=1.5, volume_spike=1.8 |
| NEARUSDT | breakout | 8 | 1.15 | 25% | compression=0.05, rr=2.5, volume_spike=1.8 |
| AVAXUSDT | mean_reversion | 8 | 1.503 | 23% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=25.0 |
| ARBUSDT | liquidity_grab | 8 | 1.708 | 15% | atr_mult_stop=1.5, volume_spike=2.5 |
| INJUSDT | liquidity_grab | 8 | 1.524 | 15% | atr_mult_stop=0.8, volume_spike=2.0 |
| GALAUSDT | breakout | 8 | 1.143 | 15% | compression=0.05, rr=3.0, volume_spike=1.8 |
| JUPUSDT | mean_reversion | 8 | 1.175 | 14% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=30.0 |
| UNIUSDT | mean_reversion | 8 | 1.241 | 14% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| AAVEUSDT | liquidity_grab | 8 | 1.314 | 13% | atr_mult_stop=1.0, volume_spike=2.0 |
| DOTUSDT | liquidity_grab | 8 | 1.619 | 12% | atr_mult_stop=0.8, volume_spike=2.5 |
| TRXUSDT | breakout | 8 | 1.27 | 12% | compression=0.07, rr=2.5, volume_spike=1.8 |
| APTUSDT | mean_reversion | 8 | 1.126 | 11% | atr_mult_stop=1.2, rsi_overbought=75.0, rsi_oversold=30.0 |
| LTCUSDT | mean_reversion | 8 | 1.202 | 11% | atr_mult_stop=1.2, rsi_overbought=70.0, rsi_oversold=25.0 |
| AAVEUSDT | mean_reversion | 8 | 1.199 | 11% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| LINKUSDT | liquidity_grab | 8 | 1.261 | 9% | atr_mult_stop=1.5, volume_spike=2.0 |
| ICPUSDT | mean_reversion | 8 | 1.129 | 9% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=20.0 |
| PYTHUSDT | liquidity_grab | 8 | 1.121 | 6% | atr_mult_stop=1.0, volume_spike=2.5 |
| TONUSDT | mean_reversion | 5 | 1.117 | 5% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=25.0 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-16 22:10 UTC · 234 coppie valutate, 36 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| TONUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
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
