# Stato sistema (snapshot)
_Generato: 2026-08-30 08:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-30 08:19 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-30 08:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/140 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AIXBTUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AVAXUSDT, BANDUSDT, BANKUSDT, BCHUSDT, BEAMXUSDT, BICOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BROCCOLIF3BUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INITUSDT, INJUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KNCUSDT, KOMAUSDT, LDOUSDT, LINKUSDT, LISTAUSDT, LSKUSDT, LTCUSDT, MANAUSDT, MASKUSDT, MELANIAUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PNUTUSDT, POLUSDT, PROMPTUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RUNEUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-30 07:32 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-30 06:32 UTC · 1120 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1120 valutazioni, 0 passate (0.00%) · 2026-08-30 06:32 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 8 | 0.7% |
| holdout | 2 | 0.2% |
| consistency | 18 | 1.6% |
| total_return | 971 | 86.7% |
| trades | 6 | 0.5% |
| recovery | 64 | 5.7% |
| regime | 51 | 4.6% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 44897 valutazioni, 62 passate (0.14%) · 2026-08-30 07:32 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 1088 | 2.4% |
| holdout | 249 | 0.6% |
| regime | 6198 | 13.8% |
| win_rate | 2 | 0.0% |
| recovery | 3468 | 7.7% |
| trades | 1324 | 3.0% |
| total_return | 31883 | 71.1% |
| pf_ex_top | 623 | 1.4% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-30 08:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.135%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
