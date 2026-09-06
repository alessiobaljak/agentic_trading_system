# Stato sistema (snapshot)
_Generato: 2026-09-06 15:28 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-06 15:28 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-06 15:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/148 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000000BOBUSDT, 1000BONKUSDT, 1000CATUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 1INCHUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIXBTUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CATIUSDT, CHILLGUYUSDT, COMPUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOODUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, EPICUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GOATUSDT, GRTUSDT, HBARUSDT, HEMIUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, METISUSDT, MITOUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, NAORISUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NMRUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, ROSEUSDT, SAHARAUSDT, SANDUSDT, SEIUSDT, SIGNUSDT, SKYAIUSDT, SNXUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WOOUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-06 13:57 UTC

### Salute del registro

- composizione: **1864 base** · **248 generate** (di cui 248 con almeno una conferma)
- occupazione: 2112/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-06 12:39 UTC · 1184 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1184 valutazioni, 0 passate (0.00%) · 2026-09-06 12:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 1034 | 87.3% |
| holdout | 1 | 0.1% |
| pf_ex_top | 12 | 1.0% |
| trades | 9 | 0.8% |
| recovery | 70 | 5.9% |
| win_rate | 1 | 0.1% |
| regime | 39 | 3.3% |
| consistency | 18 | 1.5% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 58050 valutazioni, 88 passate (0.15%) · 2026-09-06 13:57 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 40874 | 70.5% |
| holdout | 392 | 0.7% |
| pf_ex_top | 911 | 1.6% |
| trades | 831 | 1.4% |
| recovery | 4669 | 8.1% |
| win_rate | 4 | 0.0% |
| regime | 8746 | 15.1% |
| consistency | 1535 | 2.6% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-06 15:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.149%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (39) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (39) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (38) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
