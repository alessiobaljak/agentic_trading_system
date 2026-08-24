# Stato sistema (snapshot)
_Generato: 2026-08-24 16:55 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-24 16:55 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-24 16:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/146 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BTCUSDT, BUSDT, CAKEUSDT, CFXUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ERAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, GRTUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MELANIAUSDT, MEUSDT, MINAUSDT, MOODENGUSDT, MORPHOUSDT, MOVEUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, OGUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POPCATUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RUNEUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, STORJUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SYRUPUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, USUALUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-24 16:36 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-24 15:39 UTC · 1168 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1168 valutazioni, 0 passate (0.00%) · 2026-08-24 15:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 3 | 0.3% |
| regime | 40 | 3.4% |
| total_return | 1016 | 87.0% |
| recovery | 73 | 6.2% |
| pf_ex_top | 12 | 1.0% |
| trades | 9 | 0.8% |
| consistency | 15 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 39690 valutazioni, 39 passate (0.10%) · 2026-08-24 16:36 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 5112 | 12.9% |
| trades | 1202 | 3.0% |
| consistency | 885 | 2.2% |
| pf_ex_top | 554 | 1.4% |
| total_return | 28688 | 72.4% |
| holdout | 158 | 0.4% |
| recovery | 3047 | 7.7% |
| win_rate | 5 | 0.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-24 16:04 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.099%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
