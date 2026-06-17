# Stato sistema (snapshot)
_Generato: 2026-06-17 18:36 UTC_

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
- copertura universo: **31/50 crypto (62%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **45**
- universo scansionato: AAVEUSDT, ADAUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BCHUSDT, BNBUSDT, BONKUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, FLOKIUSDT, FTMUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, VETUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XRPUSDT
- aggiornato: 2026-06-17 18:31 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| TIAUSDT | gen_9258688b | 3 | 1.168 | 208% |  |
| XRPUSDT | trend_following | 6 | 1.211 | 124% | rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0, rr=2.5 |
| TIAUSDT | gen_f822d4c2 | 3 | 1.146 | 115% |  |
| SOLUSDT | gen_f822d4c2 | 3 | 1.178 | 107% |  |
| STXUSDT | trend_following | 5 | 1.1 | 102% | rsi_hi=75.0, require_volume=False, atr_mult_stop=2.0, rr=2.0 |
| ARBUSDT | trend_following | 5 | 1.104 | 92% | rsi_hi=65.0, require_volume=False, atr_mult_stop=1.5, rr=2.5 |
| ALGOUSDT | mean_reversion | 3 | 1.765 | 84% | rsi_oversold=25.0, atr_mult_stop=1.2, rsi_overbought=75.0 |
| INJUSDT | mean_reversion | 6 | 1.812 | 65% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=80.0 |
| SHIBUSDT | breakout | 5 | 1.269 | 58% | volume_spike=1.5, rr=2.0, compression=0.1 |
| BTCUSDT | gen_f822d4c2 | 3 | 1.111 | 43% |  |
| VETUSDT | breakout | 3 | 1.409 | 42% | volume_spike=1.5, rr=2.0, compression=0.1 |
| ETCUSDT | mean_reversion | 6 | 2.067 | 37% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=80.0 |
| PEPEUSDT | mean_reversion | 6 | 1.376 | 36% | rsi_oversold=30.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| SOLUSDT | mean_reversion | 5 | 1.599 | 35% | rsi_oversold=30.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| SEIUSDT | gen_c3a5d579 | 3 | 1.139 | 34% |  |
| UNIUSDT | mean_reversion | 6 | 1.641 | 34% | rsi_oversold=25.0, atr_mult_stop=1.0, rsi_overbought=70.0 |
| ATOMUSDT | mean_reversion | 6 | 1.738 | 32% | rsi_oversold=25.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| SEIUSDT | gen_f822d4c2 | 3 | 1.199 | 31% |  |
| SEIUSDT | breakout | 5 | 1.847 | 30% | volume_spike=2.5, rr=2.5, compression=0.07 |
| PYTHUSDT | breakout | 5 | 1.134 | 29% | volume_spike=1.5, rr=2.0, compression=0.07 |
| JUPUSDT | breakout | 5 | 1.126 | 29% | volume_spike=1.5, rr=3.0, compression=0.05 |
| SEIUSDT | gen_9258688b | 3 | 1.101 | 24% |  |
| SEIUSDT | gen_85f3209a | 3 | 1.112 | 24% |  |
| STXUSDT | mean_reversion | 5 | 1.508 | 22% | rsi_oversold=30.0, atr_mult_stop=1.0, rsi_overbought=80.0 |
| FLOKIUSDT | liquidity_grab | 3 | 1.308 | 21% | volume_spike=2.0, atr_mult_stop=0.8 |
| TIAUSDT | mean_reversion | 5 | 1.224 | 21% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| OPUSDT | liquidity_grab | 5 | 1.29 | 20% | volume_spike=2.0, atr_mult_stop=1.0 |
| ETHUSDT | breakout | 5 | 1.113 | 19% | volume_spike=1.8, rr=3.0, compression=0.05 |
| SOLUSDT | liquidity_grab | 5 | 1.648 | 18% | volume_spike=2.5, atr_mult_stop=1.0 |
| EGLDUSDT | mean_reversion | 3 | 1.238 | 18% | rsi_oversold=30.0, atr_mult_stop=1.2, rsi_overbought=70.0 |
| OPUSDT | breakout | 6 | 1.112 | 17% | volume_spike=1.8, rr=2.5, compression=0.05 |
| GALAUSDT | mean_reversion | 6 | 1.155 | 17% | rsi_oversold=30.0, atr_mult_stop=1.2, rsi_overbought=70.0 |
| APTUSDT | mean_reversion | 6 | 1.228 | 16% | rsi_oversold=20.0, atr_mult_stop=1.8, rsi_overbought=70.0 |
| ARBUSDT | liquidity_grab | 6 | 1.53 | 13% | volume_spike=2.5, atr_mult_stop=1.5 |
| LTCUSDT | mean_reversion | 6 | 1.217 | 12% | rsi_oversold=25.0, atr_mult_stop=1.2, rsi_overbought=70.0 |
| ARBUSDT | mean_reversion | 6 | 1.19 | 12% | rsi_oversold=25.0, atr_mult_stop=1.0, rsi_overbought=70.0 |
| ENAUSDT | breakout | 5 | 1.201 | 9% | volume_spike=2.5, rr=3.0, compression=0.07 |
| TONUSDT | breakout | 5 | 1.285 | 9% | volume_spike=1.5, rr=1.5, compression=0.05 |
| SANDUSDT | liquidity_grab | 5 | 1.22 | 8% | volume_spike=3.0, atr_mult_stop=1.5 |
| LINKUSDT | liquidity_grab | 6 | 1.123 | 7% | volume_spike=2.5, atr_mult_stop=1.5 |
| ATOMUSDT | liquidity_grab | 5 | 1.292 | 7% | volume_spike=3.0, atr_mult_stop=1.5 |
| AAVEUSDT | liquidity_grab | 6 | 1.112 | 5% | volume_spike=2.5, atr_mult_stop=1.0 |
| FTMUSDT | breakout | 3 | 1.139 | 5% | volume_spike=1.5, rr=1.5, compression=0.05 |
| DOTUSDT | liquidity_grab | 6 | 1.113 | 4% | volume_spike=2.5, atr_mult_stop=1.5 |
| BTCUSDT | liquidity_grab | 5 | 1.128 | 4% | volume_spike=3.0, atr_mult_stop=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-17 18:28 UTC · 300 coppie valutate, 37 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| XRPUSDT | trend_following | 1.211 | 124% | 375 | 37% |
| STXUSDT | trend_following | 1.1 | 102% | 553 | 39% |
| ARBUSDT | trend_following | 1.104 | 92% | 516 | 34% |
| ALGOUSDT | mean_reversion | 1.765 | 84% | 39 | 46% |
| INJUSDT | mean_reversion | 1.812 | 65% | 29 | 48% |
| SHIBUSDT | breakout | 1.269 | 58% | 300 | 38% |
| VETUSDT | breakout | 1.409 | 42% | 134 | 45% |
| ETCUSDT | mean_reversion | 2.067 | 37% | 14 | 43% |
| PEPEUSDT | mean_reversion | 1.376 | 36% | 37 | 35% |
| SOLUSDT | mean_reversion | 1.599 | 35% | 43 | 51% |
| UNIUSDT | mean_reversion | 1.641 | 34% | 27 | 26% |
| ATOMUSDT | mean_reversion | 1.738 | 32% | 21 | 29% |
| SEIUSDT | breakout | 1.847 | 30% | 53 | 43% |
| PYTHUSDT | breakout | 1.134 | 29% | 218 | 35% |
| JUPUSDT | breakout | 1.126 | 29% | 229 | 35% |
| STXUSDT | mean_reversion | 1.508 | 22% | 22 | 27% |
| FLOKIUSDT | liquidity_grab | 1.308 | 21% | 100 | 51% |
| TIAUSDT | mean_reversion | 1.224 | 21% | 34 | 32% |
| OPUSDT | liquidity_grab | 1.29 | 20% | 90 | 52% |
| ETHUSDT | breakout | 1.113 | 19% | 242 | 38% |
| SOLUSDT | liquidity_grab | 1.648 | 18% | 59 | 58% |
| EGLDUSDT | mean_reversion | 1.238 | 18% | 27 | 37% |
| OPUSDT | breakout | 1.112 | 17% | 162 | 37% |
| GALAUSDT | mean_reversion | 1.155 | 17% | 42 | 40% |
| APTUSDT | mean_reversion | 1.228 | 16% | 23 | 39% |
| ARBUSDT | liquidity_grab | 1.53 | 13% | 39 | 62% |
| LTCUSDT | mean_reversion | 1.217 | 12% | 33 | 42% |
| ARBUSDT | mean_reversion | 1.19 | 12% | 28 | 21% |
| ENAUSDT | breakout | 1.201 | 9% | 47 | 36% |
| TONUSDT | breakout | 1.285 | 9% | 43 | 46% |
| SANDUSDT | liquidity_grab | 1.22 | 8% | 48 | 60% |
| LINKUSDT | liquidity_grab | 1.123 | 7% | 78 | 64% |
| ATOMUSDT | liquidity_grab | 1.292 | 7% | 35 | 66% |
| AAVEUSDT | liquidity_grab | 1.112 | 5% | 68 | 56% |
| FTMUSDT | breakout | 1.139 | 5% | 43 | 42% |
| DOTUSDT | liquidity_grab | 1.113 | 4% | 53 | 60% |
| BTCUSDT | liquidity_grab | 1.128 | 4% | 82 | 65% |
