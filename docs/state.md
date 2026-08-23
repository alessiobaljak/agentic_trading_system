# Stato sistema (snapshot)
_Generato: 2026-08-23 16:43 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-23 16:43 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-23 16:36 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/149 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BTCUSDT, CAKEUSDT, CFXUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CVXUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GASUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, KAITOUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MELANIAUSDT, MOODENGUSDT, MORPHOUSDT, MOVEUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, OGUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POPCATUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, RIFUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, SQDUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYNUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-23 16:36 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-23 15:41 UTC · 1192 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1192 valutazioni, 0 passate (0.00%) · 2026-08-23 15:41 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 11 | 0.9% |
| trades | 6 | 0.5% |
| consistency | 15 | 1.3% |
| holdout | 1 | 0.1% |
| recovery | 79 | 6.6% |
| regime | 36 | 3.0% |
| total_return | 1043 | 87.5% |
| win_rate | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 39336 valutazioni, 34 passate (0.09%) · 2026-08-23 16:36 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 509 | 1.3% |
| trades | 1209 | 3.1% |
| consistency | 860 | 2.2% |
| holdout | 160 | 0.4% |
| recovery | 2953 | 7.5% |
| regime | 5025 | 12.8% |
| total_return | 28583 | 72.7% |
| win_rate | 3 | 0.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-23 16:00 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.076%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
