# Stato sistema (snapshot)
_Generato: 2026-09-13 16:17 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-13 16:15 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-13 16:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/161 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AGLDUSDT, ALCHUSDT, ALGOUSDT, ANKRUSDT, API3USDT, APTUSDT, ARBUSDT, ARKUSDT, ARPAUSDT, ARUSDT, ATOMUSDT, AVAUSDT, AVAXUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BATUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BLURUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CATIUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CVCUSDT, CYBERUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOGSUSDT, DOTUSDT, DYMUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GASUSDT, GLMUSDT, GMTUSDT, GPSUSDT, GRIFFAINUSDT, HBARUSDT, HEMIUSDT, HIVEUSDT, HUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, INJUSDT, IOSTUSDT, IOTXUSDT, JTOUSDT, JUPUSDT, KAVAUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MANAUSDT, MINAUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, ONDOUSDT, ONGUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PHAUSDT, POLUSDT, POLYXUSDT, PORTALUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, QTUMUSDT, RAYSOLUSDT, RENDERUSDT, REZUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TAOUSDT, TAUSDT, THETAUSDT, TIAUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WAXPUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZORAUSDT, ZROUSDT, ZRXUSDT
- aggiornato: 2026-09-13 15:48 UTC

### Salute del registro

- composizione: **1952 base** · **364 generate** (di cui 364 con almeno una conferma)
- occupazione: 2316/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-13 15:48 UTC · 1288 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1288 valutazioni, 0 passate (0.00%) · 2026-09-13 15:48 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 35 | 2.7% |
| total_return | 1143 | 88.7% |
| trades | 6 | 0.5% |
| holdout | 1 | 0.1% |
| win_rate | 1 | 0.1% |
| recovery | 70 | 5.4% |
| pf_ex_top | 17 | 1.3% |
| consistency | 15 | 1.2% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 70400 valutazioni, 95 passate (0.13%) · 2026-09-13 14:26 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 10355 | 14.7% |
| total_return | 49266 | 70.1% |
| trades | 1537 | 2.2% |
| holdout | 423 | 0.6% |
| win_rate | 4 | 0.0% |
| recovery | 5874 | 8.4% |
| pf_ex_top | 929 | 1.3% |
| consistency | 1917 | 2.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-13 16:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.133%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
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
