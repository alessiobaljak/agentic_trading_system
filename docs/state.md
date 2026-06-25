# Stato sistema (snapshot)
_Generato: 2026-06-25 09:45 UTC_

## Bot
- stato: **—** (🔴 offline)
- regime: —
- DRY_RUN: —
- equity: **$10,000.00**
- ultimo heartbeat: —

## Ultima decisione
- esito: **⚪ FLAT** (2026-06-23 05:21 UTC)
- motivo: WLDUSDT già aperto
- asset valutati: 67 · segnali: 9 · miglior segnale WLDUSDT gen_41456656 (conf. 60.0/soglia 30)

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **12/73 crypto (16%)** · obiettivo ≥ 60%
- coppie validate (>= 1 pass OOS): **14**
- universo scansionato: 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ADAUSDT, ALICEUSDT, ALLOUSDT, APTUSDT, ARBUSDT, ASTERUSDT, AVAXUSDT, BASUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BLESSUSDT, BNBUSDT, BTCUSDT, CLOUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, ENAUSDT, ESPORTSUSDT, ETCUSDT, ETHUSDT, EVAAUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GUSDT, HEIUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, INJUSDT, JTOUSDT, JUPUSDT, LABUSDT, LINKUSDT, LITUSDT, LTCUSDT, MMTUSDT, MUSDT, NEARUSDT, ONDOUSDT, OPUSDT, PAXGUSDT, PENGUUSDT, POPCATUSDT, PUMPUSDT, RESOLVUSDT, SAHARAUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SUIUSDT, SYNUSDT, TAOUSDT, TIAUSDT, TRUMPUSDT, TRXUSDT, UBUSDT, UNIUSDT, VVVUSDT, WLDUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT
- aggiornato: 2026-06-25 06:05 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| LABUSDT | mean_reversion | 1 | 1.472 | 116% | rsi_oversold=30.0, rsi_overbought=70.0, atr_mult_stop=1.8 |
| ESPORTSUSDT | vwap_reversion | 1 | 1.46 | 103% | deviation_atr=1.5, atr_mult_stop=1.5 |
| MMTUSDT | trend_following | 1 | 1.392 | 67% | rsi_hi=65.0, require_volume=False, rr=2.5, atr_mult_stop=1.5 |
| SUIUSDT | breakout | 1 | 1.293 | 60% | compression=0.07, volume_spike=1.5, rr=3.0 |
| SUIUSDT | mean_reversion | 1 | 1.477 | 46% | rsi_oversold=20.0, rsi_overbought=70.0, atr_mult_stop=1.0 |
| ENAUSDT | breakout | 1 | 1.458 | 42% | compression=0.07, volume_spike=2.5, rr=3.0 |
| XPLUSDT | breakout | 1 | 1.533 | 39% | compression=0.1, volume_spike=2.5, rr=2.5 |
| LINKUSDT | breakout | 1 | 1.383 | 38% | compression=0.05, volume_spike=2.5, rr=3.0 |
| AVAXUSDT | mean_reversion | 1 | 1.333 | 34% | rsi_oversold=30.0, rsi_overbought=80.0, atr_mult_stop=1.0 |
| VVVUSDT | breakout | 1 | 1.357 | 26% | compression=0.1, volume_spike=2.5, rr=1.5 |
| ESPORTSUSDT | breakout | 1 | 1.307 | 18% | compression=0.1, volume_spike=1.5, rr=3.0 |
| BLESSUSDT | grid_trading | 1 | 1.255 | 18% | low_band=0.15, high_band=0.75, stop_pad=0.25 |
| HUSDT | grid_trading | 1 | 1.265 | 17% | low_band=0.35, high_band=0.75, stop_pad=0.25 |
| ETCUSDT | liquidity_grab | 1 | 1.459 | 16% | volume_spike=2.5, atr_mult_stop=1.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-06-25 06:05 UTC · 511 coppie valutate, 14 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| LABUSDT | mean_reversion | 1.472 | 116% | 65 | 52% |
| ESPORTSUSDT | vwap_reversion | 1.46 | 103% | 229 | 66% |
| MMTUSDT | trend_following | 1.392 | 67% | 141 | 57% |
| SUIUSDT | breakout | 1.293 | 60% | 252 | 45% |
| SUIUSDT | mean_reversion | 1.477 | 46% | 47 | 49% |
| ENAUSDT | breakout | 1.458 | 42% | 115 | 53% |
| XPLUSDT | breakout | 1.533 | 39% | 79 | 54% |
| LINKUSDT | breakout | 1.383 | 38% | 164 | 48% |
| AVAXUSDT | mean_reversion | 1.333 | 34% | 59 | 46% |
| VVVUSDT | breakout | 1.357 | 26% | 94 | 55% |
| ESPORTSUSDT | breakout | 1.307 | 18% | 45 | 47% |
| BLESSUSDT | grid_trading | 1.255 | 18% | 156 | 60% |
| HUSDT | grid_trading | 1.265 | 17% | 179 | 57% |
| ETCUSDT | liquidity_grab | 1.459 | 16% | 91 | 78% |
