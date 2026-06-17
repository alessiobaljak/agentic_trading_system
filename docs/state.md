# Stato sistema (snapshot)
_Generato: 2026-06-17 16:05 UTC_

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
- copertura universo: **14/40 crypto (35%)** · obiettivo ≥ 60%
- coppie validate (>= 3 pass OOS): **15**
- universo scansionato: AAVEUSDT, ADAUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, BCHUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ENAUSDT, ETCUSDT, ETHUSDT, FILUSDT, GALAUSDT, HBARUSDT, ICPUSDT, IMXUSDT, INJUSDT, JUPUSDT, LINKUSDT, LTCUSDT, NEARUSDT, OPUSDT, ORDIUSDT, PEPEUSDT, PYTHUSDT, SANDUSDT, SEIUSDT, SHIBUSDT, SOLUSDT, STXUSDT, SUIUSDT, TIAUSDT, TONUSDT, TRXUSDT, UNIUSDT, WLDUSDT, XRPUSDT
- aggiornato: 2026-06-17 15:47 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| XRPUSDT | trend_following | 3 | 1.211 | 124% | rsi_hi=75.0, rr=2.5, atr_mult_stop=2.0, require_volume=False |
| INJUSDT | mean_reversion | 3 | 1.812 | 65% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| ETCUSDT | mean_reversion | 3 | 2.067 | 37% | rsi_oversold=20.0, rsi_overbought=80.0, atr_mult_stop=1.8 |
| PEPEUSDT | mean_reversion | 3 | 1.376 | 36% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| UNIUSDT | mean_reversion | 3 | 1.641 | 34% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| ATOMUSDT | mean_reversion | 3 | 1.738 | 32% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| OPUSDT | breakout | 3 | 1.112 | 17% | compression=0.05, rr=2.5, volume_spike=1.8 |
| GALAUSDT | mean_reversion | 3 | 1.155 | 17% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| APTUSDT | mean_reversion | 3 | 1.228 | 16% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| ARBUSDT | liquidity_grab | 3 | 1.53 | 13% | volume_spike=2.5, atr_mult_stop=1.5 |
| LTCUSDT | mean_reversion | 3 | 1.217 | 12% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.2 |
| ARBUSDT | mean_reversion | 3 | 1.19 | 12% | rsi_oversold=25.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| LINKUSDT | liquidity_grab | 3 | 1.123 | 7% | volume_spike=2.5, atr_mult_stop=1.5 |
| AAVEUSDT | liquidity_grab | 3 | 1.112 | 5% | volume_spike=2.5, atr_mult_stop=1.0 |
| DOTUSDT | liquidity_grab | 3 | 1.113 | 4% | volume_spike=2.5, atr_mult_stop=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-17 15:47 UTC · 240 coppie valutate, 32 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| XRPUSDT | trend_following | 1.211 | 124% | 375 | 37% |
| STXUSDT | trend_following | 1.1 | 102% | 553 | 39% |
| ARBUSDT | trend_following | 1.104 | 92% | 516 | 34% |
| INJUSDT | mean_reversion | 1.812 | 65% | 29 | 48% |
| SHIBUSDT | breakout | 1.269 | 58% | 300 | 38% |
| ETCUSDT | mean_reversion | 2.067 | 37% | 14 | 43% |
| PEPEUSDT | mean_reversion | 1.376 | 36% | 37 | 35% |
| SOLUSDT | mean_reversion | 1.599 | 35% | 43 | 51% |
| UNIUSDT | mean_reversion | 1.641 | 34% | 27 | 26% |
| ATOMUSDT | mean_reversion | 1.738 | 32% | 21 | 29% |
| SEIUSDT | breakout | 1.847 | 30% | 53 | 43% |
| PYTHUSDT | breakout | 1.134 | 29% | 218 | 35% |
| JUPUSDT | breakout | 1.126 | 29% | 229 | 35% |
| STXUSDT | mean_reversion | 1.508 | 22% | 22 | 27% |
| TIAUSDT | mean_reversion | 1.224 | 21% | 34 | 32% |
| OPUSDT | liquidity_grab | 1.29 | 20% | 90 | 52% |
| ETHUSDT | breakout | 1.113 | 19% | 242 | 38% |
| SOLUSDT | liquidity_grab | 1.648 | 18% | 59 | 58% |
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
| DOTUSDT | liquidity_grab | 1.113 | 4% | 53 | 60% |
| BTCUSDT | liquidity_grab | 1.128 | 4% | 82 | 65% |
