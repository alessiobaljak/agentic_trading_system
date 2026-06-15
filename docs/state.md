# Stato sistema (snapshot)
_Generato: 2026-06-15 05:28 UTC_

## Bot
- stato: **—** (🔴 offline)
- regime: —
- DRY_RUN: —
- ultimo heartbeat: —

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **21/35 crypto (60%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **50**
- universo scansionato: ADAUSDT, AVAXUSDT, BCHUSDT, BNBUSDT, BSBUSDT, BTCUSDT, BZUSDT, CLUSDT, DOGEUSDT, ETHUSDT, FILUSDT, HUSDT, HYPEUSDT, JELLYJELLYUSDT, MEGAUSDT, MUUSDT, NEARUSDT, ONDOUSDT, OPGUSDT, PEPEUSDT, PUMPUSDT, SNDKUSDT, SOLUSDT, SOXLUSDT, SPCXUSDT, SUIUSDT, TAOUSDT, TONUSDT, TRUMPUSDT, WLDUSDT, XAGUSDT, XAUUSDT, XLMUSDT, XPLUSDT, XRPUSDT
- aggiornato: 2026-06-15 05:25 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TURBOUSDT | trend_following | 7 | 1.28 | 228% | atr_mult_stop=1.5, rr=2.0, require_volume=False, rsi_hi=75.0 |
| KATUSDT | vwap_reversion | 3 | 1.268 | 195% | atr_mult_stop=1.0, deviation_atr=2.0 |
| WLDUSDT | trend_following | 4 | 1.213 | 182% | atr_mult_stop=2.0, rr=1.5, require_volume=True, rsi_hi=75.0 |
| BSBUSDT | vwap_reversion | 4 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| CLUSDT | vwap_reversion | 4 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| EDGEUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| MEGAUSDT | vwap_reversion | 8 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| MUUSDT | vwap_reversion | 4 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| OPGUSDT | vwap_reversion | 4 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SLXUSDT | vwap_reversion | 3 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SPACEUSDT | vwap_reversion | 7 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| SPCXUSDT | vwap_reversion | 4 | 1.247 | 181% | atr_mult_stop=1.0, deviation_atr=2.0 |
| JELLYJELLYUSDT | vwap_reversion | 4 | 1.869 | 152% | atr_mult_stop=2.0, deviation_atr=1.5 |
| XRPUSDT | trend_following | 4 | 1.289 | 147% | atr_mult_stop=2.0, rr=2.5, require_volume=False, rsi_hi=75.0 |
| SATSUSDT | trend_following | 7 | 1.197 | 146% | atr_mult_stop=2.0, rr=2.0, require_volume=False, rsi_hi=70.0 |
| PENGUUSDT | vwap_reversion | 4 | 1.278 | 114% | atr_mult_stop=1.5, deviation_atr=2.5 |
| DOGEUSDT | trend_following | 7 | 1.165 | 114% | atr_mult_stop=2.0, rr=2.0, require_volume=False, rsi_hi=75.0 |
| NOTUSDT | mean_reversion | 7 | 2.212 | 88% | atr_mult_stop=1.0, rsi_overbought=75.0, rsi_oversold=30.0 |
| TAOUSDT | vwap_reversion | 4 | 1.203 | 83% | atr_mult_stop=2.0, deviation_atr=3.0 |
| SATSUSDT | mean_reversion | 7 | 1.371 | 56% | atr_mult_stop=1.2, rsi_overbought=70.0, rsi_oversold=20.0 |
| XRPUSDT | vwap_reversion | 4 | 1.103 | 54% | atr_mult_stop=1.0, deviation_atr=1.5 |
| SHIBUSDT | breakout | 7 | 1.381 | 53% | rr=2.5, volume_spike=1.5, compression=0.05 |
| PEPEUSDT | mean_reversion | 11 | 1.334 | 50% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=30.0 |
| BOMEUSDT | mean_reversion | 7 | 1.339 | 44% | atr_mult_stop=1.2, rsi_overbought=80.0, rsi_oversold=30.0 |
| TRUMPUSDT | trend_following | 4 | 1.186 | 44% | atr_mult_stop=2.0, rr=2.0, require_volume=False, rsi_hi=70.0 |
| BONKUSDT | mean_reversion | 7 | 1.401 | 42% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| BONKUSDT | breakout | 7 | 1.381 | 40% | rr=3.0, volume_spike=1.5, compression=0.05 |
| HMSTRUSDT | liquidity_grab | 7 | 3.31 | 39% | atr_mult_stop=1.5, volume_spike=2.5 |
| GALAUSDT | mean_reversion | 4 | 1.956 | 39% | atr_mult_stop=1.2, rsi_overbought=80.0, rsi_oversold=30.0 |
| HUSDT | vwap_reversion | 4 | 1.499 | 38% | atr_mult_stop=1.0, deviation_atr=1.5 |
| BOMEUSDT | breakout | 7 | 1.279 | 38% | rr=3.0, volume_spike=1.5, compression=0.07 |
| MEMEUSDT | breakout | 4 | 1.314 | 34% | rr=3.0, volume_spike=1.8, compression=0.05 |
| AVAXUSDT | breakout | 3 | 1.356 | 32% | rr=2.0, volume_spike=1.8, compression=0.05 |
| SUIUSDT | breakout | 4 | 1.216 | 25% | rr=2.0, volume_spike=1.8, compression=0.07 |
| PUMPUSDT | mean_reversion | 3 | 1.476 | 23% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=30.0 |
| MEMEUSDT | mean_reversion | 3 | 1.152 | 21% | atr_mult_stop=1.8, rsi_overbought=70.0, rsi_oversold=20.0 |
| FLOKIUSDT | liquidity_grab | 7 | 1.248 | 17% | atr_mult_stop=0.8, volume_spike=2.0 |
| GALAUSDT | breakout | 3 | 1.132 | 15% | rr=2.0, volume_spike=1.8, compression=0.05 |
| NOTUSDT | liquidity_grab | 7 | 1.343 | 12% | atr_mult_stop=0.8, volume_spike=2.0 |
| HUSDT | liquidity_grab | 4 | 1.295 | 11% | atr_mult_stop=0.8, volume_spike=2.0 |
| XRPUSDT | mean_reversion | 3 | 1.11 | 11% | atr_mult_stop=1.8, rsi_overbought=75.0, rsi_oversold=30.0 |
| BONKUSDT | liquidity_grab | 7 | 1.196 | 11% | atr_mult_stop=0.8, volume_spike=2.5 |
| JELLYJELLYUSDT | breakout | 3 | 1.186 | 11% | rr=2.0, volume_spike=2.5, compression=0.1 |
| PUMPUSDT | breakout | 7 | 1.146 | 10% | rr=2.0, volume_spike=1.8, compression=0.1 |
| HYPEUSDT | liquidity_grab | 4 | 1.726 | 9% | atr_mult_stop=0.8, volume_spike=2.0 |
| ADAUSDT | mean_reversion | 4 | 1.126 | 8% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| SOLUSDT | mean_reversion | 4 | 1.176 | 7% | atr_mult_stop=1.0, rsi_overbought=70.0, rsi_oversold=30.0 |
| XAUUSDT | breakout | 3 | 2.02 | 5% | rr=3.0, volume_spike=1.8, compression=0.07 |
| LINEAUSDT | breakout | 4 | 1.105 | 4% | rr=1.5, volume_spike=1.5, compression=0.1 |
| XAUUSDT | trend_following | 4 | 1.318 | 2% | atr_mult_stop=2.0, rr=2.5, require_volume=False, rsi_hi=70.0 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-15 05:25 UTC · 210 coppie valutate, 31 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| WLDUSDT | trend_following | 1.213 | 182% | 400 | 42% |
| SPCXUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| OPGUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| CLUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| MEGAUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| BSBUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| XAGUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| MUUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| SNDKUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| SOXLUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| BZUSDT | vwap_reversion | 1.247 | 181% | 625 | 16% |
| JELLYJELLYUSDT | vwap_reversion | 1.869 | 152% | 77 | 26% |
| XRPUSDT | trend_following | 1.289 | 147% | 318 | 39% |
| DOGEUSDT | trend_following | 1.165 | 114% | 412 | 39% |
| TAOUSDT | vwap_reversion | 1.203 | 83% | 167 | 29% |
| XRPUSDT | vwap_reversion | 1.103 | 54% | 406 | 20% |
| PEPEUSDT | mean_reversion | 1.334 | 50% | 56 | 36% |
| TRUMPUSDT | trend_following | 1.186 | 44% | 183 | 38% |
| HUSDT | vwap_reversion | 1.499 | 38% | 37 | 14% |
| AVAXUSDT | breakout | 1.356 | 32% | 116 | 41% |
| SUIUSDT | breakout | 1.216 | 25% | 128 | 40% |
| SNDKUSDT | breakout | 1.204 | 22% | 128 | 39% |
| TAOUSDT | mean_reversion | 1.374 | 18% | 17 | 35% |
| XPLUSDT | breakout | 1.237 | 13% | 35 | 37% |
| HUSDT | liquidity_grab | 1.295 | 11% | 15 | 27% |
| PUMPUSDT | breakout | 1.146 | 10% | 45 | 33% |
| HYPEUSDT | liquidity_grab | 1.726 | 9% | 19 | 42% |
| ADAUSDT | mean_reversion | 1.126 | 8% | 27 | 48% |
| SOLUSDT | mean_reversion | 1.176 | 7% | 25 | 40% |
| XAUUSDT | breakout | 2.02 | 5% | 17 | 47% |
| XAUUSDT | trend_following | 1.318 | 2% | 15 | 53% |
