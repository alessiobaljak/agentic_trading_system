# Stato sistema (snapshot)
_Generato: 2026-09-15 11:44 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-15 11:44 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-15 11:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **4/158 crypto (2%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **11**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, AIOUSDT, ALGOUSDT, ALTUSDT, ANKRUSDT, API3USDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ASTRUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CVCUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GLMUSDT, GPSUSDT, HBARUSDT, HEMIUSDT, HIVEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PNUTUSDT, POLUSDT, POLYXUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, REZUSDT, RONINUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UBUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VANAUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WAXPUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-15 11:30 UTC

### Salute del registro

- composizione: **1968 base** · **440 generate** (di cui 440 con almeno una conferma)
- occupazione: 2408/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 3 | 2.445 | 211% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_271ab7ec | 3 | 1.81 | 110% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.799 | 108% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.84 | 107% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.794 | 106% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 3 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.215 | 100% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.807 | 92% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.89 | 84% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.899 | 67% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 3 | 1.49 | 60% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-15 09:49 UTC · 1264 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1264 valutazioni, 0 passate (0.00%) · 2026-09-15 09:49 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 8 | 0.6% |
| recovery | 54 | 4.3% |
| total_return | 1132 | 89.6% |
| pf_ex_top | 16 | 1.3% |
| consistency | 11 | 0.9% |
| regime | 43 | 3.4% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 77952 valutazioni, 182 passate (0.23%) · 2026-09-15 11:30 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 2238 | 2.9% |
| total_return | 53309 | 68.5% |
| recovery | 6485 | 8.3% |
| pf_ex_top | 1025 | 1.3% |
| win_rate | 9 | 0.0% |
| holdout | 570 | 0.7% |
| consistency | 2150 | 2.8% |
| regime | 11984 | 15.4% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-15 11:04 UTC · coppie validate: **11** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.233%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — solo 0.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
