# Stato sistema (snapshot)
_Generato: 2026-09-14 19:21 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-14 19:21 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-14 19:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **1/158 crypto (1%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **8**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, ALGOUSDT, ALTUSDT, ANKRUSDT, API3USDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BATUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BLURUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CVCUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GLMUSDT, GPSUSDT, GRASSUSDT, GRIFFAINUSDT, HBARUSDT, HEMIUSDT, HIVEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, IOTXUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KAVAUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PNUTUSDT, POLUSDT, POLYXUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, REZUSDT, RONINUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UBUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WAXPUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-14 18:40 UTC

### Salute del registro

- composizione: **1976 base** · **417 generate** (di cui 417 con almeno una conferma)
- occupazione: 2393/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| ORCAUSDT | gen_271ab7ec | 3 | 1.81 | 110% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.799 | 108% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.84 | 107% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.795 | 106% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.215 | 100% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.807 | 92% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.89 | 84% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.9 | 67% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-14 18:40 UTC · 1264 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1264 valutazioni, 0 passate (0.00%) · 2026-09-14 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 17 | 1.3% |
| regime | 38 | 3.0% |
| trades | 8 | 0.6% |
| total_return | 1114 | 88.1% |
| recovery | 71 | 5.6% |
| pf_ex_top | 13 | 1.0% |
| holdout | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 77064 valutazioni, 174 passate (0.23%) · 2026-09-14 17:14 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 2119 | 2.8% |
| trades | 1776 | 2.3% |
| win_rate | 8 | 0.0% |
| pf_ex_top | 1019 | 1.3% |
| regime | 11757 | 15.3% |
| total_return | 53178 | 69.2% |
| recovery | 6496 | 8.4% |
| holdout | 537 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-14 19:01 UTC · coppie validate: **8** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.222%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — solo 0.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
