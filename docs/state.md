# Stato sistema (snapshot)
_Generato: 2026-09-16 00:20 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-16 00:20 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-16 00:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **4/155 crypto (3%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **11**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, AIOUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARCUSDT, ARKUSDT, ARUSDT, ASTRUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CVCUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, DYMUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, GALAUSDT, GASUSDT, GLMUSDT, GPSUSDT, GUSDT, HBARUSDT, HEMIUSDT, HIVEUSDT, HYPEUSDT, ICPUSDT, IDOLUSDT, IDUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MORPHOUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLAYUSDT, POLUSDT, POLYXUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, REZUSDT, RONINUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOPHUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRBUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VANAUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WAXPUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-15 23:20 UTC

### Salute del registro

- composizione: **1960 base** · **446 generate** (di cui 446 con almeno una conferma)
- occupazione: 2406/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 3 | 2.444 | 211% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_271ab7ec | 3 | 1.81 | 110% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.799 | 108% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.84 | 107% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.794 | 106% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 3 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.214 | 100% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.807 | 92% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.89 | 84% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.899 | 67% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 3 | 1.49 | 60% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-15 21:43 UTC · 1240 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1240 valutazioni, 0 passate (0.00%) · 2026-09-15 21:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 1110 | 89.5% |
| recovery | 67 | 5.4% |
| trades | 7 | 0.6% |
| pf_ex_top | 8 | 0.6% |
| regime | 36 | 2.9% |
| holdout | 1 | 0.1% |
| consistency | 11 | 0.9% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 77522 valutazioni, 175 passate (0.23%) · 2026-09-15 23:20 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 53977 | 69.8% |
| recovery | 6738 | 8.7% |
| trades | 1184 | 1.5% |
| regime | 11691 | 15.1% |
| consistency | 2141 | 2.8% |
| holdout | 554 | 0.7% |
| win_rate | 10 | 0.0% |
| pf_ex_top | 1052 | 1.4% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-16 00:00 UTC · coppie validate: **11** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.222%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — solo 0.7 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.7 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.7 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.6 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.6 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
