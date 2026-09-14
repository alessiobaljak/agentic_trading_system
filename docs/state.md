# Stato sistema (snapshot)
_Generato: 2026-09-14 12:47 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-14 12:44 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-14 12:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **1/161 crypto (1%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **8**
- universo scansionato: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AGLDUSDT, AINUSDT, ALGOUSDT, ALTUSDT, ANKRUSDT, API3USDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAUSDT, AVAXUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BATUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BLURUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CVCUSDT, CYBERUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GLMUSDT, GMTUSDT, GPSUSDT, GRASSUSDT, GRIFFAINUSDT, HBARUSDT, HEMIUSDT, HIVEUSDT, HUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, IOTXUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KAVAUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MAVIAUSDT, MINAUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, POLUSDT, POLYXUSDT, PORTALUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, REZUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WAXPUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZETAUSDT, ZILUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-14 12:46 UTC

### Salute del registro

- composizione: **1952 base** · **413 generate** (di cui 413 con almeno una conferma)
- occupazione: 2365/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| ORCAUSDT | gen_271ab7ec | 3 | 1.81 | 110% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.799 | 108% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.84 | 107% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.795 | 106% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.215 | 100% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.807 | 92% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.891 | 84% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.9 | 67% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-14 12:46 UTC · 1288 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1288 valutazioni, 0 passate (0.00%) · 2026-09-14 12:46 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 14 | 1.1% |
| pf_ex_top | 14 | 1.1% |
| total_return | 1141 | 88.6% |
| regime | 39 | 3.0% |
| recovery | 73 | 5.7% |
| trades | 7 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 78260 valutazioni, 177 passate (0.23%) · 2026-09-14 11:28 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 54256 | 69.5% |
| regime | 11958 | 15.3% |
| consistency | 2163 | 2.8% |
| pf_ex_top | 1052 | 1.3% |
| holdout | 553 | 0.7% |
| trades | 1754 | 2.2% |
| win_rate | 9 | 0.0% |
| recovery | 6338 | 8.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-14 12:00 UTC · coppie validate: **8** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.223%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — solo 0.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (36) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
