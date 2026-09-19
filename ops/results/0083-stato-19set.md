# 0083-stato-19set.req

_eseguito: 2026-09-19 06:01 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 2.9s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-09-19 06:01 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$989.87**
- ultimo heartbeat: 2026-09-19 06:01 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-19 06:01 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 24 · segnali: 0

## Posizioni aperte
- DEXEUSDT: long qty=106.65169071592429 @ 1.863 uPnL=-1.6472819394452745 · rischio 0.21% · leva 2.0x
- VETUSDT: short qty=23961.903015408458 @ 0.008292 uPnL=0.9202503471552438 · rischio 0.53% · leva 2.0x
- **rischio aperto totale: 0.74%** dell'equity su 2 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **24/156 crypto (15%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **47**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACHUSDT, ADAUSDT, AEROUSDT, AINUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AUSDT, AVAUSDT, AVAXUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BCHUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CUSDT, CVCUSDT, DASHUSDT, DOGEUSDT, DOTUSDT, DRIFTUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, FUSDT, GALAUSDT, GPSUSDT, GUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, IOUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KSMUSDT, LAUSDT, LDOUSDT, LINKUSDT, LPTUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MITOUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, MYXUSDT, NEARUSDT, NEIROUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PROMUSDT, PROVEUSDT, PUMPUSDT, PYTHUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, REZUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STGUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SUSDT, SUSHIUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT
- aggiornato: 2026-09-19 05:36 UTC

### Salute del registro

- composizione: **2024 base** · **577 generate** (di cui 577 con almeno una conferma)
- occupazione: 2601/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 3 | 2.441 | 212% | scale_r_mults=[2.0, 4.0, 6.0] |
| JASMYUSDT | gen_b2f350ff | 3 | 1.603 | 137% | scale_r_mults=[2.0, 4.0, 6.0] |
| TUTUSDT | gen_4465723e | 3 | 1.538 | 128% | scale_r_mults=[1.5, 3.0, 5.0] |
| VETUSDT | gen_6d06dca0 | 3 | 1.631 | 126% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_d85b1f05 | 3 | 1.552 | 122% | scale_r_mults=[1.5, 3.0, 5.0] |
| DOTUSDT | gen_da39a23a | 3 | 1.493 | 120% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.867 | 113% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.914 | 113% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.864 | 111% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_6cf80ae6 | 3 | 3.072 | 111% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_271ab7ec | 3 | 1.81 | 110% | scale_r_mults=[1.0, 2.0, 3.0] |
| GPSUSDT | gen_bf1e00d4 | 3 | 1.557 | 107% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 3 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| PROMUSDT | gen_cd5c842f | 3 | 1.665 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.23 | 101% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_c61d9322 | 3 | 2.502 | 98% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_725cb5f4 | 3 | 1.512 | 97% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.864 | 97% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_919c110c | 3 | 1.492 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_b31d8b93 | 3 | 1.873 | 94% | scale_r_mults=[1.5, 3.0, 5.0] |
| SPXUSDT | gen_ba3a671f | 3 | 1.504 | 93% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_fa304106 | 3 | 1.954 | 90% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_14e1775b | 3 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 3 | 1.749 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.923 | 86% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_98837ec2 | 3 | 2.46 | 85% | scale_r_mults=[2.0, 4.0, 6.0] |
| PROMUSDT | gen_452d4511 | 3 | 2.347 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_ff3e4154 | 3 | 1.668 | 81% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_194e2514 | 3 | 1.568 | 81% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_1bb04e1a | 3 | 1.568 | 81% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 3 | 1.808 | 79% | scale_r_mults=[2.0, 4.0, 6.0] |
| BICOUSDT | gen_f238d283 | 3 | 1.518 | 76% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_2031005e | 3 | 1.569 | 75% | scale_r_mults=[2.0, 4.0, 6.0] |
| SKYAIUSDT | gen_eb2ece0c | 3 | 3.289 | 72% | scale_r_mults=[2.0, 4.0, 6.0] |
| JTOUSDT | gen_f238d283 | 3 | 1.426 | 72% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.967 | 70% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 3 | 1.467 | 58% | scale_r_mults=[1.5, 3.0, 5.0] |
| SPXUSDT | gen_d53c153b | 3 | 1.824 | 58% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_f3124a14 | 3 | 1.572 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_d53c153b | 3 | 1.808 | 49% | scale_r_mults=[1.0, 2.0, 3.0] |
| QUSDT | gen_18c839a0 | 3 | 2.532 | 47% | scale_r_mults=[1.0, 1.5, 2.5] |
| SAHARAUSDT | gen_6b94025f | 3 | 2.173 | 43% | scale_r_mults=[1.0, 2.0, 3.0] |
| HEMIUSDT | gen_108c996b | 3 | 2.089 | 42% | scale_r_mults=[2.0, 4.0, 6.0] |
| HEMIUSDT | gen_93131ef1 | 3 | 2.089 | 42% | scale_r_mults=[2.0, 4.0, 6.0] |
| SYRUPUSDT | gen_af734c68 | 3 | 1.79 | 42% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_2053cba6 | 3 | 1.446 | 28% | scale_r_mults=[2.0, 4.0, 6.0] |
| ZKUSDT | gen_98837ec2 | 3 | 1.476 | 22% | scale_r_mults=[2.0, 4.0, 6.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-19 03:45 UTC · 1248 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1248 valutazioni, 0 passate (0.00%) · 2026-09-19 03:45 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 1100 | 88.1% |
| recovery | 72 | 5.8% |
| regime | 34 | 2.7% |
| holdout | 1 | 0.1% |
| pf_ex_top | 18 | 1.4% |
| consistency | 17 | 1.4% |
| trades | 6 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 99294 valutazioni, 293 passate (0.30%) · 2026-09-19 05:36 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 21 | 0.0% |
| total_return | 67995 | 68.7% |
| recovery | 8655 | 8.7% |
| regime | 15831 | 16.0% |
| holdout | 862 | 0.9% |
| pf_ex_top | 1348 | 1.4% |
| consistency | 2982 | 3.0% |
| trades | 1307 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-19 06:00 UTC · coppie validate: **47** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.291%**

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
- totale: **10** · vinti: 2 (20%) · PnL realizzato: **-10.13**
- confronto col mercato: noi -1.01% vs BTC buy&hold +6.97% nello stesso periodo → **sotto** il mercato

- costi: **3.12 USDT** su 10 trade (0.31/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 1.59 · spread 1.52 · funding +0.00
  - lordo -7.01 → netto -10.13 · **break-even 0.32%** dell'equity
  - piu' costose: SYRUPUSDT 0.63 · GPSUSDT 0.34 · NEIROUSDT 0.32 · DEXEUSDT 0.32 · SPXUSDT 0.32

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 8 | 80% | -24.30 |
| Take profit (fino all'ultimo gradino) | 1 | 10% | +10.30 |
| Scale-out (>=1 TP incassato, residuo a BE) | 1 | 10% | +3.87 |

- gradini raggiunti (su 10 trade): 0 TP: 8 (80%) · 1 TP: 1 (10%) · 3 TP: 1 (10%)

- **drawdown di portafoglio: 16.84 USDT** (ritorno -10.13 · recovery -0.60) · max 4 posizioni aperte insieme
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 10 trade): mediana **0.74R** · ≥1R: 30% · ≥1.5R: 30% · ≥3R: 10% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: watch · 10 trade · PF vissuto 0.583 vs 1.897 atteso · mfe mediana 0.74R

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SYRUPUSDT|gen_af734c68 | watch | 2 | 0.0 / 1.79 | PF 0.00 vs 1.79 atteso · mfe mediana 0.94R < primo TP 2.00R |
| ORCAUSDT|gen_6d06dca0 | watch | 1 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| SPXUSDT|gen_ba3a671f | watch | 1 | 0.0 / 1.504 | PF 0.00 vs 1.50 atteso · mfe mediana 0.30R < primo TP 1.50R |
| VETUSDT|gen_6d06dca0 | watch | 1 | 0.0 / 1.631 | PF 0.00 vs 1.63 atteso |
| STXUSDT|gen_b9bf5d01 | watch | 1 | 0.0 / 1.54 | PF 0.00 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| TUTUSDT|gen_4465723e | watch | 1 | 0.0 / 1.538 | PF 0.00 vs 1.54 atteso · mfe mediana 0.69R < primo TP 1.50R |
| DEXEUSDT|gen_fa304106 | watch | 1 | 0.0 / 1.954 | PF 0.00 vs 1.95 atteso · mfe mediana 0.52R < primo TP 1.50R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 10 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 10

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 3 | 33% | +1.16% |
| 60.0–60.0 | 3 | 0% | -3.13% |
| 60.0–60.0 | 4 | 25% | -1.06% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._


--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
