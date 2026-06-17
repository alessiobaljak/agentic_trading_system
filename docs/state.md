# Stato sistema (snapshot)
_Generato: 2026-06-17 11:17 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$10,000.00**
- ultimo heartbeat: 2026-06-17 11:17 UTC

## Ultima decisione
- esito: **⚪ FLAT** (2026-06-17 11:08 UTC)
- motivo: XRPUSDT già aperto
- asset valutati: 5 · segnali: 1 · miglior segnale XRPUSDT vwap_reversion (conf. 80.0/soglia 30)

## Posizioni aperte
- XRPUSDT: long qty=11768.136618097866 @ 1.1949 uPnL=-69.4320060467776

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **26/39 crypto (67%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **68**
- universo scansionato: AAVEUSDT, ADAUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, BCHUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, SANDUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, WLDUSDT, XRPUSDT
- aggiornato: 2026-06-17 10:31 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| XRPUSDT | gen_d9c198d8 | 3 | 1.335 | 198% |  |
| DOGEUSDT | gen_8b389f8d | 3 | 1.206 | 192% |  |
| XRPUSDT | gen_8b389f8d | 3 | 1.251 | 183% |  |
| TONUSDT | vwap_reversion | 5 | 1.247 | 181% | deviation_atr=2.0, atr_mult_stop=1.0 |
| XRPUSDT | gen_3de5a422 | 3 | 1.196 | 168% |  |
| XRPUSDT | trend_following | 10 | 1.343 | 167% | rr=2.5, rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0 |
| WLDUSDT | trend_following | 10 | 1.175 | 156% | rr=2.5, rsi_hi=75.0, require_volume=False, atr_mult_stop=1.0 |
| APTUSDT | gen_59093452 | 3 | 1.272 | 152% |  |
| XRPUSDT | gen_00c6ed36 | 3 | 1.123 | 120% |  |
| ETCUSDT | gen_59093452 | 3 | 1.223 | 106% |  |
| PEPEUSDT | trend_following | 10 | 1.112 | 95% | rr=1.5, rsi_hi=75.0, require_volume=True, atr_mult_stop=2.0 |
| ADAUSDT | gen_652b0360 | 3 | 1.187 | 92% |  |
| LINKUSDT | vwap_reversion | 10 | 1.141 | 92% | deviation_atr=2.0, atr_mult_stop=1.5 |
| INJUSDT | gen_b59cc83c | 3 | 1.262 | 88% |  |
| LTCUSDT | vwap_reversion | 10 | 1.121 | 70% | deviation_atr=3.0, atr_mult_stop=1.5 |
| UNIUSDT | gen_6be0916c | 3 | 1.222 | 65% |  |
| INJUSDT | gen_c638ed8c | 3 | 1.101 | 59% |  |
| INJUSDT | mean_reversion | 10 | 1.652 | 55% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.0 |
| XRPUSDT | vwap_reversion | 10 | 1.103 | 54% | deviation_atr=1.5, atr_mult_stop=1.0 |
| PEPEUSDT | mean_reversion | 10 | 1.791 | 52% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| BCHUSDT | gen_b59cc83c | 3 | 1.196 | 52% |  |
| UNIUSDT | gen_81303036 | 3 | 1.155 | 51% |  |
| GALAUSDT | mean_reversion | 10 | 1.89 | 47% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| TRXUSDT | gen_e9890da8 | 3 | 1.242 | 47% |  |
| TRXUSDT | gen_d09be067 | 3 | 1.172 | 46% |  |
| ORDIUSDT | mean_reversion | 10 | 1.281 | 43% | rsi_oversold=20.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| ARBUSDT | mean_reversion | 10 | 1.652 | 43% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| ETCUSDT | mean_reversion | 10 | 1.845 | 42% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| PYTHUSDT | mean_reversion | 10 | 1.505 | 41% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| BCHUSDT | gen_81303036 | 3 | 1.166 | 38% |  |
| UNIUSDT | gen_079d4fae | 3 | 1.112 | 38% |  |
| AVAXUSDT | breakout | 10 | 1.323 | 37% | rr=2.5, compression=0.05, volume_spike=1.8 |
| IMXUSDT | mean_reversion | 10 | 1.469 | 36% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.2 |
| TRXUSDT | gen_652b0360 | 3 | 1.182 | 34% |  |
| OPUSDT | breakout | 10 | 1.31 | 33% | rr=3.0, compression=0.05, volume_spike=1.8 |
| INJUSDT | gen_df83684e | 3 | 2.102 | 31% |  |
| TRXUSDT | gen_caab5c2e | 3 | 1.15 | 31% |  |
| ADAUSDT | mean_reversion | 10 | 1.683 | 30% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| ATOMUSDT | mean_reversion | 10 | 1.697 | 30% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| XRPUSDT | gen_b88416ca | 3 | 2.066 | 27% |  |
| SUIUSDT | breakout | 10 | 1.223 | 27% | rr=1.5, compression=0.1, volume_spike=1.8 |
| NEARUSDT | breakout | 10 | 1.15 | 25% | rr=2.5, compression=0.05, volume_spike=1.8 |
| AVAXUSDT | mean_reversion | 10 | 1.503 | 23% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| TRXUSDT | gen_3122b8e7 | 3 | 1.155 | 23% |  |
| ETHUSDT | gen_446a3e00 | 3 | 3.184 | 21% |  |
| DOGEUSDT | gen_446a3e00 | 3 | 2.738 | 20% |  |
| ARBUSDT | liquidity_grab | 10 | 1.708 | 15% | atr_mult_stop=1.5, volume_spike=2.5 |
| INJUSDT | liquidity_grab | 10 | 1.524 | 15% | atr_mult_stop=0.8, volume_spike=2.0 |
| GALAUSDT | breakout | 10 | 1.143 | 15% | rr=3.0, compression=0.05, volume_spike=1.8 |
| JUPUSDT | mean_reversion | 10 | 1.175 | 14% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| UNIUSDT | mean_reversion | 10 | 1.241 | 14% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| AAVEUSDT | liquidity_grab | 10 | 1.314 | 13% | atr_mult_stop=1.0, volume_spike=2.0 |
| NEARUSDT | gen_df83684e | 3 | 1.545 | 13% |  |
| DOTUSDT | liquidity_grab | 10 | 1.619 | 12% | atr_mult_stop=0.8, volume_spike=2.5 |
| TRXUSDT | breakout | 10 | 1.27 | 12% | rr=2.5, compression=0.07, volume_spike=1.8 |
| APTUSDT | mean_reversion | 10 | 1.126 | 11% | rsi_oversold=30.0, rsi_overbought=75.0, atr_mult_stop=1.2 |
| LTCUSDT | mean_reversion | 10 | 1.202 | 11% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| ATOMUSDT | gen_b88416ca | 3 | 1.31 | 11% |  |
| AAVEUSDT | mean_reversion | 10 | 1.199 | 11% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| SUIUSDT | gen_b88416ca | 3 | 1.178 | 10% |  |
| ADAUSDT | gen_446a3e00 | 3 | 1.792 | 10% |  |
| LINKUSDT | liquidity_grab | 10 | 1.261 | 9% | atr_mult_stop=1.5, volume_spike=2.0 |
| ICPUSDT | mean_reversion | 10 | 1.129 | 9% | rsi_oversold=20.0, rsi_overbought=75.0, atr_mult_stop=1.8 |
| AVAXUSDT | gen_b88416ca | 3 | 1.157 | 9% |  |
| BCHUSDT | gen_446a3e00 | 3 | 1.59 | 7% |  |
| PYTHUSDT | liquidity_grab | 10 | 1.121 | 6% | atr_mult_stop=1.0, volume_spike=2.5 |
| AVAXUSDT | gen_446a3e00 | 3 | 1.388 | 6% |  |
| TONUSDT | mean_reversion | 5 | 1.117 | 5% | rsi_oversold=25.0, rsi_overbought=75.0, atr_mult_stop=1.8 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-17 07:03 UTC · 234 coppie valutate, 36 passate in questo run_

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
