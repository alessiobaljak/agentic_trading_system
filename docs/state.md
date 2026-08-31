# Stato sistema (snapshot)
_Generato: 2026-08-31 11:22 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-31 11:22 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-31 11:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/145 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AEVOUSDT, AIOUSDT, ALGOUSDT, ANIMEUSDT, APEUSDT, APTUSDT, ARBUSDT, ATOMUSDT, AUCTIONUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, BANKUSDT, BBUSDT, BCHUSDT, BICOUSDT, BIGTIMEUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BROCCOLIF3BUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ERAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LISTAUSDT, LTCUSDT, MAGICUSDT, MANAUSDT, MELANIAUSDT, MINAUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RENDERUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SXTUSDT, TACUSDT, TAOUSDT, TIAUSDT, TNSRUSDT, TRBUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-31 10:53 UTC

### Salute del registro

- composizione: **3041 base** · **0 generate** (di cui 0 con almeno una conferma)
- occupazione: 3041/3000 — ⚠️ SOPRA IL TETTO
- 🔴 **ZERO coppie generate**: sono le uniche che passano il gate. Il registro non puo' accumulare niente, per quante candidate la ricerca trovi.

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-31 09:43 UTC · 1160 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1160 valutazioni, 0 passate (0.00%) · 2026-08-31 09:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 1 | 0.1% |
| trades | 7 | 0.6% |
| regime | 44 | 3.8% |
| pf_ex_top | 9 | 0.8% |
| consistency | 15 | 1.3% |
| total_return | 1013 | 87.3% |
| recovery | 71 | 6.1% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 48720 valutazioni, 89 passate (0.18%) · 2026-08-31 10:53 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 301 | 0.6% |
| trades | 1411 | 2.9% |
| regime | 6727 | 13.8% |
| pf_ex_top | 689 | 1.4% |
| win_rate | 1 | 0.0% |
| total_return | 34518 | 71.0% |
| consistency | 1223 | 2.5% |
| recovery | 3761 | 7.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-31 11:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.178%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
