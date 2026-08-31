# Stato sistema (snapshot)
_Generato: 2026-08-31 05:35 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-31 05:35 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-31 05:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/147 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AEVOUSDT, AIOUSDT, AIXBTUSDT, ALGOUSDT, ANIMEUSDT, APEUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AUCTIONUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, BANDUSDT, BANKUSDT, BBUSDT, BCHUSDT, BEAMXUSDT, BICOUSDT, BIGTIMEUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BROCCOLIF3BUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CHILLGUYUSDT, CHZUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ERAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LISTAUSDT, LTCUSDT, MAGICUSDT, MANAUSDT, MELANIAUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RENDERUSDT, SANDUSDT, SEIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SXTUSDT, TACUSDT, TAOUSDT, TIAUSDT, TNSRUSDT, TRBUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, USUALUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-31 04:48 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-31 03:40 UTC · 1176 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1176 valutazioni, 0 passate (0.00%) · 2026-08-31 03:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 71 | 6.0% |
| trades | 8 | 0.7% |
| total_return | 1021 | 86.8% |
| regime | 53 | 4.5% |
| consistency | 12 | 1.0% |
| pf_ex_top | 11 | 0.9% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 48951 valutazioni, 80 passate (0.16%) · 2026-08-31 04:48 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 1285 | 2.6% |
| recovery | 4154 | 8.5% |
| consistency | 1248 | 2.6% |
| win_rate | 2 | 0.0% |
| holdout | 318 | 0.7% |
| total_return | 34173 | 69.9% |
| regime | 6924 | 14.2% |
| pf_ex_top | 767 | 1.6% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-31 05:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.160%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (39) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
