# Stato sistema (snapshot)
_Generato: 2026-09-09 00:15 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-09 00:14 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-09 00:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/148 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000CATUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARKMUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CATIUSDT, CHZUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOGSUSDT, DOODUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, GRTUSDT, GUSDT, HAEDALUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KSMUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NAORISUSDT, NEARUSDT, NEIROUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLAYUSDT, PNUTUSDT, POLUSDT, PROMUSDT, PROVEUSDT, PUMPUSDT, PYTHUSDT, RAYSOLUSDT, RENDERUSDT, SAFEUSDT, SAHARAUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYRUPUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-08 22:57 UTC

### Salute del registro

- composizione: **1904 base** · **257 generate** (di cui 257 con almeno una conferma)
- occupazione: 2161/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-08 21:39 UTC · 1184 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1184 valutazioni, 0 passate (0.00%) · 2026-09-08 21:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 19 | 1.6% |
| recovery | 80 | 6.8% |
| trades | 5 | 0.4% |
| win_rate | 1 | 0.1% |
| total_return | 1033 | 87.2% |
| pf_ex_top | 8 | 0.7% |
| regime | 36 | 3.0% |
| holdout | 2 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 59496 valutazioni, 115 passate (0.19%) · 2026-09-08 22:57 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 1544 | 2.6% |
| pf_ex_top | 973 | 1.6% |
| trades | 1757 | 3.0% |
| win_rate | 8 | 0.0% |
| total_return | 40938 | 68.9% |
| regime | 8661 | 14.6% |
| recovery | 5074 | 8.5% |
| holdout | 426 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-09 00:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.190%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
