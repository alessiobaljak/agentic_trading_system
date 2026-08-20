# Stato sistema (snapshot)
_Generato: 2026-08-20 22:45 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-20 22:44 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-20 22:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/143 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SATSUSDT, 1000SHIBUSDT, 1000XECUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOUSDT, ALGOUSDT, ALICEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRETTUSDT, BRUSDT, BTCDOMUSDT, BTCUSDT, CAKEUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GASUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, ICXUSDT, IMXUSDT, INJUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MELANIAUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RUNEUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SPXUSDT, STORJUSDT, STRKUSDT, STXUSDT, SUIUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XMRUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZROUSDT
- aggiornato: 2026-08-20 22:25 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-20 21:37 UTC · 1144 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1144 valutazioni, 0 passate (0.00%) · 2026-08-20 21:37 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 10 | 0.9% |
| trades | 10 | 0.9% |
| holdout | 3 | 0.3% |
| regime | 34 | 3.0% |
| recovery | 76 | 6.6% |
| pf_ex_top | 15 | 1.3% |
| total_return | 996 | 87.1% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34463 valutazioni, 21 passate (0.06%) · 2026-08-20 22:25 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 399 | 1.2% |
| trades | 1308 | 3.8% |
| regime | 3876 | 11.3% |
| consistency | 607 | 1.8% |
| holdout | 87 | 0.3% |
| recovery | 2404 | 7.0% |
| win_rate | 3 | 0.0% |
| total_return | 25758 | 74.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-20 22:00 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.053%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
