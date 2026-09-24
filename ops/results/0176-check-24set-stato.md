# 0176-check-24set-stato.req

_eseguito: 2026-09-24 06:13 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.0s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-09-24 06:13 UTC_

## Bot
- stato: **running** (🔴 offline)
- regime: bear_trending
- DRY_RUN: True
- equity: **$950.85**
- ultimo heartbeat: —
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-24 06:01 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 27 · segnali: 0

## Posizioni aperte
- DOTUSDT: long qty=86.53586057611031 @ 1.1007 uPnL=2.1458028048716233 · leva 1.0x

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **27/200 crypto (14%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **59**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 4USDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, AKEUSDT, ALGOUSDT, ALLOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARIAUSDT, ARKUSDT, ARUSDT, ASTERUSDT, ATHUSDT, ATOMUSDT, AVAUSDT, AVAXUSDT, AXSUSDT, B2USDT, BANKUSDT, BBUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BIOUSDT, BLESSUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BSVUSDT, BTCUSDT, BTRUSDT, BTWUSDT, CAKEUSDT, CAPUSDT, CCUSDT, CELRUSDT, CHIPUSDT, CHRUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CVCUSDT, CYSUSDT, DASHUSDT, DATAIPUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DRIFTUSDT, EDENUSDT, EDGEUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, EVAAUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FIGHTUSDT, FILUSDT, FLOCKUSDT, FLOWUSDT, FOLKSUSDT, FORMUSDT, GALAUSDT, GENIUSUSDT, GIGGLEUSDT, GPSUSDT, GRAMUSDT, GRASSUSDT, GRTUSDT, GUSDT, HBARUSDT, HEMIUSDT, HOLOUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KERNELUSDT, KITEUSDT, KMNOUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LUNA2USDT, MAGMAUSDT, MARSCOINUSDT, METUSDT, MINAUSDT, MONUSDT, MOODENGUSDT, MORPHOUSDT, MOVEUSDT, MUBARAKUSDT, MYXUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, PIEVERSEUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PTBUSDT, PUMPUSDT, PYTHUSDT, RAYSOLUSDT, RENDERUSDT, REUSDT, RIVERUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SKYUSDT, SNXUSDT, SOLUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SUSDT, SUSHIUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRIAUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZESTUSDT, ZETAUSDT, ZKUSDT, ZROUSDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-09-24 06:03 UTC

### Salute del registro

- composizione: **1728 base** · **1194 generate** (di cui 1194 con almeno una conferma)
- occupazione: 2922/3000 — ok

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
| ORCAUSDT | gen_bbe21d3f | 3 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_b31d8b93 | 3 | 1.881 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| STXUSDT | gen_14e1775b | 3 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 3 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_ba3a671f | 3 | 1.644 | 84% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_9a383fff | 4 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| DOTUSDT | gen_919c110c | 3 | 1.462 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 3 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_e6ddc613 | 4 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| USELESSUSDT | gen_2031005e | 3 | 1.54 | 72% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.967 | 70% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_eb2ece0c | 3 | 3.897 | 68% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| TRUMPUSDT | gen_0e000630 | 3 | 2.223 | 66% | scale_r_mults=[2.0, 4.0, 6.0] |
| SKYAIUSDT | gen_6cf80ae6 | 3 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_c202787e | 3 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SPXUSDT | gen_d53c153b | 3 | 1.824 | 58% | scale_r_mults=[1.5, 3.0, 5.0] |
| BICOUSDT | gen_f238d283 | 3 | 1.484 | 57% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| NEIROUSDT | gen_f3124a14 | 3 | 1.572 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 3 | 1.455 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| JTOUSDT | gen_f238d283 | 3 | 1.554 | 50% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| NEIROUSDT | gen_d53c153b | 3 | 1.808 | 49% | scale_r_mults=[1.0, 2.0, 3.0] |
| SKYAIUSDT | gen_c61d9322 | 4 | 2.085 | 45% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| QUSDT | gen_bf2be656 | 3 | 2.953 | 44% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_98837ec2 | 3 | 2.214 | 44% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SCRUSDT | gen_63712f8e | 3 | 2.302 | 43% | scale_r_mults=[1.0, 2.0, 3.0] |
| SAHARAUSDT | gen_6b94025f | 3 | 2.029 | 42% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| HEMIUSDT | gen_108c996b | 3 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| HEMIUSDT | gen_93131ef1 | 3 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| QUSDT | gen_18c839a0 | 3 | 2.584 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| JTOUSDT | gen_35632db9 | 3 | 1.522 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| MUBARAKUSDT | gen_ff3e4154 | 4 | 1.495 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| PROMUSDT | gen_452d4511 | 3 | 1.888 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| MUBARAKUSDT | gen_2053cba6 | 3 | 1.446 | 28% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_1e2af031 | 3 | 1.771 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_108c996b | 3 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_93131ef1 | 3 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| NEIROUSDT | gen_e132204b | 3 | 1.323 | 21% | scale_r_mults=[1.5, 3.0, 5.0] |
| ZKUSDT | gen_98837ec2 | 3 | 1.439 | 21% | scale_r_mults=[2.0, 4.0, 6.0] |
| SYRUPUSDT | gen_af734c68 | 3 | 1.557 | 19% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| BULLAUSDT | gen_7ac562e3 | 3 | 1.839 | 17% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 3 | 0.2% |
| holdout | 1 | 0.1% |
| consistency | 17 | 1.3% |
| trades | 6 | 0.5% |
| total_return | 1207 | 91.4% |
| recovery | 64 | 4.8% |
| regime | 22 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 445 valutazioni, 1 passate (0.22%) · 2026-09-24 06:03 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 8 | 1.8% |
| consistency | 13 | 2.9% |
| trades | 33 | 7.4% |
| total_return | 283 | 63.7% |
| recovery | 79 | 17.8% |
| regime | 28 | 6.3% |

- quasi-passaggi (un solo criterio, di poco): **0** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-24 06:04 UTC · coppie validate: **59** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.057%**

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
- totale: **44** · vinti: 16 (36%) · PnL realizzato: **-49.15**
- confronto col mercato: noi -4.92% vs BTC buy&hold +11.10% nello stesso periodo → **sotto** il mercato

- costi: **11.30 USDT** su 44 trade (0.26/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 6.34 · spread 5.02 · funding -0.06
  - lordo -37.85 → netto -49.15 · **break-even 1.19%** dell'equity
  - piu' costose: DEXEUSDT 2.02 · SPXUSDT 1.24 · USELESSUSDT 0.94 · SYRUPUSDT 0.93 · VETUSDT 0.78

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 28 | 64% | -123.29 |
| Trailing stop | 8 | 18% | +23.26 |
| Scale-out (>=1 TP incassato, residuo a BE) | 5 | 11% | +16.62 |
| Take profit (fino all'ultimo gradino) | 2 | 5% | +20.78 |
| Time exit (orizzonte scaduto) | 1 | 2% | +13.48 |

- gradini raggiunti (su 44 trade): 0 TP: 36 (82%) · 1 TP: 5 (11%) · 2 TP: 1 (2%) · 3 TP: 2 (5%)

- **drawdown di portafoglio: 61.78 USDT** (ritorno -49.15 · recovery -0.80) · max 7 posizioni aperte insieme
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 44 trade): mediana **0.84R** · ≥1R: 41% · ≥1.5R: 25% · ≥3R: 7% · ≥5R: 2%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 44 trade · PF vissuto 0.601 vs 1.885 atteso · mfe mediana 0.84R

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SPXUSDT|gen_ba3a671f | watch | 5 | 0.0 / 1.644 | PF 0.00 vs 1.64 atteso · mfe mediana 0.30R < primo TP 0.75R |
| DEXEUSDT|gen_fa304106 | watch | 5 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| USELESSUSDT|gen_2031005e | watch | 5 | 0.146 / 1.54 | PF 0.15 vs 1.54 atteso · mfe mediana 0.20R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | watch | 3 | 0.392 / 2.584 | PF 0.39 vs 2.58 atteso · mfe mediana 0.90R < primo TP 1.50R |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.557 | PF 0.41 vs 1.56 atteso · mfe mediana 0.94R < primo TP 1.50R |
| ORCAUSDT|gen_6d06dca0 | watch | 2 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 1.05R < primo TP 1.50R |
| DEXEUSDT|gen_b31d8b93 | watch | 2 | 0.37 / 1.881 | PF 0.37 vs 1.88 atteso |
| MUBARAKUSDT|gen_1f7ead60 | watch | 1 | 0.0 / 2.776 | PF 0.00 vs 2.78 atteso |
| MUBARAKUSDT|gen_ff3e4154 | watch | 1 | 0.0 / 1.495 | PF 0.00 vs 1.50 atteso · mfe mediana 0.84R < primo TP 1.50R |

- **freno di serie** (size x0.5): **gen_ba3a671f** (5 perdite di fila), **gen_fa304106** (5 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **ok** · 44 trade · correlazione 0.0 · influenza applicata **x1.0**
- la confidenza ordina correttamente gli esiti

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 14 | 50% | -1.93% |
| 60.0–60.0 | 14 | 36% | -1.13% |
| 60.0–60.0 | 16 | 25% | -1.44% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._


--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
