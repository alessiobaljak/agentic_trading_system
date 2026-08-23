# Stato sistema (snapshot)
_Generato: 2026-08-23 01:59 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-23 01:59 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-23 01:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/152 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIGTIMEUSDT, BIOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BTCDOMUSDT, BTCUSDT, CAKEUSDT, CFXUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, CVXUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FORMUSDT, GALAUSDT, GASUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HMSTRUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOTAUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, KAITOUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MELANIAUSDT, MINAUSDT, MOODENGUSDT, MORPHOUSDT, MOVEUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POPCATUSDT, PORTALUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, SQDUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYNUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, USUALUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, ZECUSDT, ZENUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-23 01:41 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-23 00:45 UTC · 1216 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1216 valutazioni, 0 passate (0.00%) · 2026-08-23 00:45 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 1 | 0.1% |
| recovery | 72 | 5.9% |
| trades | 7 | 0.6% |
| consistency | 18 | 1.5% |
| pf_ex_top | 14 | 1.2% |
| total_return | 1059 | 87.1% |
| regime | 45 | 3.7% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 39672 valutazioni, 35 passate (0.09%) · 2026-08-23 01:41 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 4952 | 12.5% |
| recovery | 2880 | 7.3% |
| trades | 661 | 1.7% |
| win_rate | 3 | 0.0% |
| consistency | 867 | 2.2% |
| holdout | 153 | 0.4% |
| pf_ex_top | 477 | 1.2% |
| total_return | 29644 | 74.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-23 01:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.079%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (28) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (28) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
