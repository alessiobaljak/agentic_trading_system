# Stato sistema (snapshot)
_Generato: 2026-08-10 17:08 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$792.92**
- ultimo heartbeat: 2026-08-10 17:08 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-10 17:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 93 · segnali: 0

## Posizioni aperte
- BTCUSDT: long qty=1.0 @ 100.0 uPnL=0.9079999666715278
- ERAUSDT: long qty=1201.5742783138744 @ 0.06739 uPnL=-0.31793540061091896
- HEIUSDT: short qty=518.4111339690514 @ 0.15755 uPnL=1.1510808463934517
- HUSDT: long qty=718.7008135049573 @ 0.07931 uPnL=1.4930522938826416
- LABUSDT: short qty=684.8511536594757 @ 0.1189 uPnL=-0.34653427352371047
- MIRAUSDT: long qty=1933.6097101520843 @ 0.04224 uPnL=0.2824057739301911
- MYXUSDT: long qty=1090.7925831655225 @ 0.07559 uPnL=0.11237052658252347

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **1/2 crypto (50%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **1**
- universo scansionato: BTCUSDT, ETHUSDT
- aggiornato: 2026-08-10 15:57 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| SOLUSDT | breakout | 3 | 1.2 | 30% | rr=2.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-10 15:57 UTC · 2 coppie valutate, 2 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| BTCUSDT | trend_following | 1.3 | 20% | 40 | 50% |
| ETHUSDT | breakout | 1.3 | 20% | 40 | 50% |

## Trade chiusi — perché usciamo
- totale: **138** · vinti: 46 (33%) · PnL realizzato: **-221.90**

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 84 | 61% | -380.19 |
| Scale-out (>=1 TP incassato, residuo a BE) | 23 | 17% | +82.12 |
| Time exit (orizzonte scaduto) | 9 | 7% | +63.56 |
| Take profit (fino all'ultimo gradino) | 8 | 6% | +35.57 |
| Kill switch | 8 | 6% | +1.52 |
| ? | 5 | 4% | -25.00 |
| Manuale | 1 | 1% | +0.53 |

- gradini raggiunti (su 133 trade): 0 TP: 102 (77%) · 1 TP: 21 (16%) · 2 TP: 9 (7%) · 3 TP: 1 (1%)

- escursione favorevole (mfe_r, 133 trade): mediana **0.55R** · ≥1R: 35% · ≥1.5R: 26% · ≥3R: 7% · ≥5R: 2%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 129 trade · PF vissuto 0.447 vs 1.26 atteso · mfe mediana 0.55R

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **ok** · 129 trade · correlazione 0.126 · influenza applicata **x1.0**
- la confidenza ordina correttamente gli esiti

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 43 | 30% | -4.20% |
| 60.0–60.0 | 43 | 35% | +0.01% |
| 60.0–75.0 | 43 | 28% | -2.27% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
