# Stato sistema (snapshot)
_Generato: 2026-06-14 23:38 UTC_

## Bot
- stato: **—** (🔴 offline)
- regime: —
- DRY_RUN: —
- ultimo heartbeat: —

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **22/34 crypto (65%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **48**
- universo scansionato: ADAUSDT, AVAXUSDT, BCHUSDT, BNBUSDT, BSBUSDT, BTCUSDT, CLUSDT, DOGEUSDT, EDGEUSDT, ETHUSDT, FILUSDT, HUSDT, HYPEUSDT, ICPUSDT, JELLYJELLYUSDT, MEGAUSDT, MUUSDT, NEARUSDT, ONDOUSDT, OPGUSDT, PEPEUSDT, PUMPUSDT, SLXUSDT, SOLUSDT, SPCXUSDT, SUIUSDT, TAOUSDT, TONUSDT, TRUMPUSDT, WLDUSDT, XAUUSDT, XLMUSDT, XPLUSDT, XRPUSDT
- aggiornato: 2026-06-14 21:43 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 7 | 1.28 | 228% | rsi_hi=75.0, atr_mult_stop=1.5, require_volume=False, rr=2.0 |
| KATUSDT | vwap_reversion | 3 | 1.268 | 195% | atr_mult_stop=1.0, deviation_atr=2.0 |
| BSBUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| CLUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| EDGEUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| MEGAUSDT | vwap_reversion | 7 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| MUUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| OPGUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SLXUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SPACEUSDT | vwap_reversion | 7 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SPCXUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| XRPUSDT | trend_following | 3 | 1.362 | 180% | rsi_hi=75.0, atr_mult_stop=2.0, require_volume=False, rr=2.5 |
| JELLYJELLYUSDT | vwap_reversion | 3 | 1.869 | 152% | atr_mult_stop=2.0, deviation_atr=1.5 |
| SATSUSDT | trend_following | 7 | 1.197 | 146% | rsi_hi=70.0, atr_mult_stop=2.0, require_volume=False, rr=2.0 |
| WLDUSDT | trend_following | 3 | 1.153 | 139% | rsi_hi=75.0, atr_mult_stop=1.0, require_volume=False, rr=2.0 |
| PENGUUSDT | vwap_reversion | 4 | 1.278 | 114% | atr_mult_stop=1.5, deviation_atr=2.5 |
| NOTUSDT | mean_reversion | 7 | 2.212 | 88% | atr_mult_stop=1.0, rsi_overbought=75.0, rsi_oversold=30.0 |
| TAOUSDT | vwap_reversion | 3 | 1.203 | 83% | atr_mult_stop=2.0, deviation_atr=3.0 |
| DOGEUSDT | trend_following | 6 | 1.124 | 79% | rsi_hi=70.0, atr_mult_stop=1.5, require_volume=False, rr=2.5 |
| SATSUSDT | mean_reversion | 7 | 1.371 | 56% | atr_mult_stop=1.2, rsi_overbought=70.0, rsi_oversold=20.0 |
| XRPUSDT | vwap_reversion | 3 | 1.103 | 54% | atr_mult_stop=1.0, deviation_atr=1.5 |
| SHIBUSDT | breakout | 7 | 1.381 | 53% | rr=2.5, compression=0.05, volume_spike=1.5 |
| PEPEUSDT | mean_reversion | 10 | 1.334 | 50% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=30.0 |
| BOMEUSDT | mean_reversion | 7 | 1.339 | 44% | atr_mult_stop=1.2, rsi_overbought=80.0, rsi_oversold=30.0 |
| BONKUSDT | mean_reversion | 7 | 1.401 | 42% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| BONKUSDT | breakout | 7 | 1.381 | 40% | rr=3.0, compression=0.05, volume_spike=1.5 |
| HMSTRUSDT | liquidity_grab | 7 | 3.31 | 39% | atr_mult_stop=1.5, volume_spike=2.5 |
| GALAUSDT | mean_reversion | 4 | 1.956 | 39% | atr_mult_stop=1.2, rsi_overbought=80.0, rsi_oversold=30.0 |
| HUSDT | vwap_reversion | 3 | 1.499 | 38% | atr_mult_stop=1.0, deviation_atr=1.5 |
| BOMEUSDT | breakout | 7 | 1.279 | 38% | rr=3.0, compression=0.07, volume_spike=1.5 |
| TRUMPUSDT | trend_following | 3 | 1.153 | 36% | rsi_hi=75.0, atr_mult_stop=2.0, require_volume=False, rr=2.5 |
| MEMEUSDT | breakout | 4 | 1.314 | 34% | rr=3.0, compression=0.05, volume_spike=1.8 |
| ADAUSDT | mean_reversion | 3 | 1.806 | 33% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| PUMPUSDT | breakout | 6 | 1.343 | 23% | rr=2.0, compression=0.07, volume_spike=1.5 |
| PUMPUSDT | mean_reversion | 3 | 1.476 | 23% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=30.0 |
| MEMEUSDT | mean_reversion | 3 | 1.152 | 21% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=20.0 |
| SUIUSDT | breakout | 3 | 1.171 | 18% | rr=1.5, compression=0.07, volume_spike=1.8 |
| FLOKIUSDT | liquidity_grab | 7 | 1.248 | 17% | atr_mult_stop=0.8, volume_spike=2.0 |
| GALAUSDT | breakout | 3 | 1.132 | 15% | rr=2.0, compression=0.05, volume_spike=1.8 |
| NOTUSDT | liquidity_grab | 7 | 1.343 | 12% | atr_mult_stop=0.8, volume_spike=2.0 |
| HUSDT | liquidity_grab | 3 | 1.295 | 11% | atr_mult_stop=0.8, volume_spike=2.0 |
| XRPUSDT | mean_reversion | 3 | 1.11 | 11% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=30.0 |
| BONKUSDT | liquidity_grab | 7 | 1.196 | 11% | atr_mult_stop=0.8, volume_spike=2.5 |
| JELLYJELLYUSDT | breakout | 3 | 1.186 | 11% | rr=2.0, compression=0.1, volume_spike=2.5 |
| HYPEUSDT | liquidity_grab | 3 | 1.726 | 9% | atr_mult_stop=0.8, volume_spike=2.0 |
| SOLUSDT | mean_reversion | 3 | 1.176 | 7% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| LINEAUSDT | breakout | 4 | 1.105 | 4% | rr=1.5, compression=0.1, volume_spike=1.5 |
| XAUUSDT | trend_following | 3 | 1.328 | 3% | rsi_hi=75.0, atr_mult_stop=2.0, require_volume=False, rr=2.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-14 21:43 UTC · 204 coppie valutate, 31 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| SPCXUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| MEGAUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| BSBUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| CLUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| OPGUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| MUUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| EDGEUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| SLXUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| XRPUSDT | trend_following | 1.362 | 180% | 318 | 41% |
| JELLYJELLYUSDT | vwap_reversion | 1.869 | 152% | 77 | 26% |
| WLDUSDT | trend_following | 1.153 | 139% | 539 | 34% |
| TAOUSDT | vwap_reversion | 1.203 | 83% | 167 | 29% |
| DOGEUSDT | trend_following | 1.124 | 79% | 461 | 34% |
| XRPUSDT | vwap_reversion | 1.103 | 54% | 406 | 20% |
| PEPEUSDT | mean_reversion | 1.334 | 50% | 56 | 36% |
| AVAXUSDT | breakout | 1.358 | 44% | 155 | 42% |
| HUSDT | vwap_reversion | 1.499 | 38% | 37 | 14% |
| TRUMPUSDT | trend_following | 1.153 | 36% | 172 | 38% |
| ADAUSDT | mean_reversion | 1.806 | 33% | 23 | 48% |
| PUMPUSDT | breakout | 1.343 | 23% | 49 | 43% |
| CLUSDT | breakout | 1.204 | 22% | 128 | 39% |
| TONUSDT | mean_reversion | 1.839 | 22% | 15 | 33% |
| SUIUSDT | breakout | 1.171 | 18% | 130 | 45% |
| HUSDT | liquidity_grab | 1.295 | 11% | 15 | 27% |
| XRPUSDT | mean_reversion | 1.11 | 11% | 41 | 27% |
| JELLYJELLYUSDT | breakout | 1.186 | 11% | 48 | 40% |
| HYPEUSDT | liquidity_grab | 1.726 | 9% | 19 | 42% |
| SOLUSDT | mean_reversion | 1.176 | 7% | 25 | 40% |
| BCHUSDT | mean_reversion | 1.203 | 5% | 13 | 38% |
| XAUUSDT | trend_following | 1.328 | 3% | 21 | 43% |
| XAUUSDT | breakout | 1.68 | 3% | 18 | 61% |
