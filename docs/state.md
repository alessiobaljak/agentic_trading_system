# Stato sistema (snapshot)
_Generato: 2026-09-13 04:48 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-13 04:48 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-13 04:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/158 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALCHUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARPAUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIGTIMEUSDT, BLURUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CVCUSDT, CYBERUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOGSUSDT, DOODUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GLMUSDT, GPSUSDT, GRIFFAINUSDT, HBARUSDT, HEMIUSDT, HIVEUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, INJUSDT, IOSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MITOUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, ONDOUSDT, ONGUSDT, OPENUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, POLUSDT, POLYXUSDT, PORTALUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, REZUSDT, RUNEUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOMIUSDT, SOPHUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TAGUSDT, TAOUSDT, TAUSDT, THETAUSDT, THEUSDT, TIAUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZORAUSDT, ZROUSDT, ZRXUSDT
- aggiornato: 2026-09-13 03:44 UTC

### Salute del registro

- composizione: **1888 base** · **355 generate** (di cui 355 con almeno una conferma)
- occupazione: 2243/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-13 03:44 UTC · 1264 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1264 valutazioni, 0 passate (0.00%) · 2026-09-13 03:44 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 6 | 0.5% |
| regime | 35 | 2.8% |
| holdout | 1 | 0.1% |
| win_rate | 1 | 0.1% |
| total_return | 1121 | 88.7% |
| pf_ex_top | 11 | 0.9% |
| consistency | 18 | 1.4% |
| recovery | 71 | 5.6% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 68172 valutazioni, 130 passate (0.19%) · 2026-09-13 02:16 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 1522 | 2.2% |
| regime | 10132 | 14.9% |
| holdout | 469 | 0.7% |
| win_rate | 3 | 0.0% |
| total_return | 46972 | 69.0% |
| pf_ex_top | 1037 | 1.5% |
| consistency | 1964 | 2.9% |
| recovery | 5943 | 8.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-13 04:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.187%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
