# Stato sistema (snapshot)
_Generato: 2026-08-30 14:52 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-30 14:52 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-30 14:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/143 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AIXBTUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AUCTIONUSDT, AVAXUSDT, BANDUSDT, BANKUSDT, BBUSDT, BCHUSDT, BEAMXUSDT, BICOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BROCCOLIF3BUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CHILLGUYUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ERAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INITUSDT, INJUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LISTAUSDT, LTCUSDT, MAGICUSDT, MANAUSDT, MELANIAUSDT, MINAUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, POLUSDT, PROMPTUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RENDERUSDT, RIFUSDT, RUNEUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SOLVUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, USUALUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-30 13:39 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-30 12:35 UTC · 1144 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1144 valutazioni, 0 passate (0.00%) · 2026-08-30 12:35 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 998 | 87.2% |
| recovery | 70 | 6.1% |
| consistency | 12 | 1.0% |
| regime | 46 | 4.0% |
| pf_ex_top | 7 | 0.6% |
| holdout | 3 | 0.3% |
| trades | 8 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 46800 valutazioni, 82 passate (0.18%) · 2026-08-30 13:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 3749 | 8.0% |
| total_return | 33265 | 71.2% |
| consistency | 1148 | 2.5% |
| pf_ex_top | 680 | 1.5% |
| win_rate | 5 | 0.0% |
| regime | 6453 | 13.8% |
| holdout | 256 | 0.5% |
| trades | 1162 | 2.5% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-30 14:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.171%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
