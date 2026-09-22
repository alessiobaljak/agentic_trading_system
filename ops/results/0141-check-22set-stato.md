# 0141-check-22set-stato.req

_eseguito: 2026-09-22 06:01 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.1s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-09-22 06:01 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$971.35**
- ultimo heartbeat: 2026-09-22 06:01 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-22 06:01 UTC)
- motivo: parita' backtest: 1 segnali validi aperti
- asset valutati: 26 · segnali: 1 · miglior segnale MUBARAKUSDT gen_2053cba6 (conf. 60.0/soglia 30)

## Posizioni aperte
- MUBARAKUSDT: short qty=1946.94632712434 @ 0.05965 uPnL=1.3188382427230423 · rischio 0.71% · leva 2.0x
- **rischio aperto totale: 0.71%** dell'equity su 1 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **26/26 crypto (100%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **56**
- universo scansionato: —
- aggiornato: 2026-09-22 02:52 UTC

### Salute del registro

- composizione: **1944 base** · **908 generate** (di cui 908 con almeno una conferma)
- occupazione: 2852/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 3 | 2.441 | 212% | scale_r_mults=[2.0, 4.0, 6.0] |
| JASMYUSDT | gen_b2f350ff | 3 | 1.603 | 137% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_6d06dca0 | 3 | 1.631 | 126% | scale_r_mults=[2.0, 4.0, 6.0] |
| TUTUSDT | gen_4465723e | 3 | 1.53 | 125% | scale_r_mults=[1.5, 3.0, 5.0] |
| DOTUSDT | gen_da39a23a | 3 | 1.488 | 118% | scale_r_mults=[1.5, 3.0, 5.0] |
| MUBARAKUSDT | gen_1f7ead60 | 3 | 2.776 | 114% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_271ab7ec | 3 | 1.851 | 113% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.859 | 111% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_194e2514 | 3 | 2.036 | 108% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_1bb04e1a | 3 | 2.036 | 108% | scale_r_mults=[2.0, 4.0, 6.0] |
| GPSUSDT | gen_bf1e00d4 | 3 | 1.59 | 103% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 3 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_d85b1f05 | 3 | 1.483 | 102% | scale_r_mults=[1.5, 3.0, 5.0] |
| PROMUSDT | gen_cd5c842f | 3 | 1.628 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.859 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_fa304106 | 3 | 2.06 | 95% | scale_r_mults=[1.5, 3.0, 5.0] |
| GPSUSDT | gen_871647b8 | 3 | 1.491 | 94% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_725cb5f4 | 3 | 1.708 | 92% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.148 | 89% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_b31d8b93 | 3 | 1.892 | 88% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_14e1775b | 3 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 3 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 2.002 | 84% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| ORCAUSDT | gen_9a383fff | 3 | 2.023 | 84% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| SPXUSDT | gen_ba3a671f | 3 | 1.644 | 84% | scale_r_mults=[0.75, 1.5, 3.0] |
| DOTUSDT | gen_919c110c | 3 | 1.462 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 3 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_ff3e4154 | 3 | 1.637 | 78% | scale_r_mults=[2.0, 4.0, 6.0] |
| PROMUSDT | gen_452d4511 | 3 | 2.145 | 75% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_2031005e | 3 | 1.54 | 72% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.967 | 70% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_c61d9322 | 3 | 2.613 | 68% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| TRUMPUSDT | gen_0e000630 | 3 | 2.223 | 66% | scale_r_mults=[2.0, 4.0, 6.0] |
| BICOUSDT | gen_f238d283 | 3 | 1.531 | 61% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_d53c153b | 3 | 1.824 | 58% | scale_r_mults=[1.5, 3.0, 5.0] |
| JTOUSDT | gen_f238d283 | 3 | 1.604 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_f3124a14 | 3 | 1.572 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 3 | 1.455 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_d53c153b | 3 | 1.808 | 49% | scale_r_mults=[1.0, 2.0, 3.0] |
| QUSDT | gen_bf2be656 | 3 | 3.073 | 47% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| SAHARAUSDT | gen_6b94025f | 3 | 2.207 | 46% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_eb2ece0c | 3 | 2.943 | 46% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_98837ec2 | 3 | 2.214 | 44% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SCRUSDT | gen_63712f8e | 3 | 2.302 | 43% | scale_r_mults=[1.0, 2.0, 3.0] |
| QUSDT | gen_18c839a0 | 3 | 2.406 | 43% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_6cf80ae6 | 3 | 1.892 | 40% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| HEMIUSDT | gen_108c996b | 3 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| HEMIUSDT | gen_93131ef1 | 3 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| SYRUPUSDT | gen_af734c68 | 3 | 1.726 | 38% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_2053cba6 | 3 | 1.446 | 28% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_1e2af031 | 3 | 1.771 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_108c996b | 3 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_93131ef1 | 3 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| NEIROUSDT | gen_e132204b | 3 | 1.323 | 21% | scale_r_mults=[1.5, 3.0, 5.0] |
| ZKUSDT | gen_98837ec2 | 3 | 1.439 | 21% | scale_r_mults=[2.0, 4.0, 6.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 6 | 0.5% |
| regime | 22 | 1.7% |
| total_return | 1207 | 91.4% |
| consistency | 17 | 1.3% |
| recovery | 64 | 4.8% |
| holdout | 1 | 0.1% |
| pf_ex_top | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 123078 valutazioni, 248 passate (0.20%) · 2026-09-22 02:52 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 1397 | 1.1% |
| total_return | 92198 | 75.1% |
| regime | 14311 | 11.7% |
| consistency | 3015 | 2.5% |
| holdout | 726 | 0.6% |
| recovery | 10204 | 8.3% |
| pf_ex_top | 979 | 0.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-22 06:01 UTC · coppie validate: **56** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.199%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma

## Trade chiusi — perché usciamo
- totale: **35** · vinti: 13 (37%) · PnL realizzato: **-28.65**
- confronto col mercato: noi -2.86% vs BTC buy&hold +12.81% nello stesso periodo → **sotto** il mercato

- costi: **9.83 USDT** su 35 trade (0.28/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 5.40 · spread 4.47 · funding -0.04
  - lordo -18.81 → netto -28.65 · **break-even 1.01%** dell'equity
  - piu' costose: DEXEUSDT 1.91 · SPXUSDT 0.96 · SYRUPUSDT 0.93 · STXUSDT 0.77 · USELESSUSDT 0.75

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 22 | 63% | -91.62 |
| Scale-out (>=1 TP incassato, residuo a BE) | 5 | 14% | +16.62 |
| Trailing stop | 5 | 14% | +12.09 |
| Take profit (fino all'ultimo gradino) | 2 | 6% | +20.78 |
| Time exit (orizzonte scaduto) | 1 | 3% | +13.48 |

- gradini raggiunti (su 35 trade): 0 TP: 27 (77%) · 1 TP: 5 (14%) · 2 TP: 1 (3%) · 3 TP: 2 (6%)

- **drawdown di portafoglio: 61.78 USDT** (ritorno -28.65 · recovery -0.46) · max 7 posizioni aperte insieme
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 35 trade): mediana **0.85R** · ≥1R: 43% · ≥1.5R: 26% · ≥3R: 9% · ≥5R: 3%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: watch · 35 trade · PF vissuto 0.687 vs 1.878 atteso · mfe mediana 0.85R

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| USELESSUSDT|gen_2031005e | watch | 4 | 0.198 / 1.54 | PF 0.20 vs 1.54 atteso · mfe mediana 0.20R < primo TP 2.00R |
| DEXEUSDT|gen_fa304106 | watch | 4 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| SPXUSDT|gen_ba3a671f | watch | 3 | 0.0 / 1.644 | PF 0.00 vs 1.64 atteso · mfe mediana 0.30R < primo TP 0.75R |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.726 | PF 0.41 vs 1.73 atteso · mfe mediana 0.94R < primo TP 2.00R |
| VETUSDT|gen_6d06dca0 | watch | 2 | 0.0 / 1.631 | PF 0.00 vs 1.63 atteso |
| DEXEUSDT|gen_b31d8b93 | watch | 2 | 0.37 / 1.892 | PF 0.37 vs 1.89 atteso |
| ORCAUSDT|gen_6d06dca0 | watch | 2 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 1.05R < primo TP 1.50R |
| MUBARAKUSDT|gen_1f7ead60 | watch | 1 | 0.0 / 2.776 | PF 0.00 vs 2.78 atteso |
| MUBARAKUSDT|gen_2053cba6 | watch | 1 | 99.0 / 1.446 | mfe mediana 1.05R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | watch | 1 | 99.0 / 2.406 | mfe mediana 0.90R < primo TP 2.00R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **flat** · 35 trade · correlazione 0.0 · influenza applicata **x0.5**
- nessuna relazione tra confidenza ed esito: influenza ridotta

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 11 | 73% | +1.86% |
| 60.0–60.0 | 11 | 27% | -2.38% |
| 60.0–60.0 | 13 | 15% | -1.55% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._


--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
