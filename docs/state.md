# Stato sistema (snapshot)
_Generato: 2026-09-08 04:36 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-08 04:36 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-08 04:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/145 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARKMUSDT, ARUSDT, ASTRUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BIGTIMEUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CATIUSDT, CHILLGUYUSDT, CHZUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOODUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FIDAUSDT, FILUSDT, FORMUSDT, GALAUSDT, GRTUSDT, HBARUSDT, HEMIUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KOMAUSDT, LAUSDT, LAYERUSDT, LDOUSDT, LINKUSDT, LTCUSDT, LUNA2USDT, METISUSDT, MINAUSDT, MITOUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, NAORISUSDT, NEARUSDT, NEIROUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLAYUSDT, PLUMEUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, REZUSDT, SANDUSDT, SEIUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TACUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, YGGUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-08 03:40 UTC

### Salute del registro

- composizione: **1912 base** · **253 generate** (di cui 253 con almeno una conferma)
- occupazione: 2165/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-08 03:40 UTC · 1160 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1160 valutazioni, 0 passate (0.00%) · 2026-09-08 03:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 10 | 0.9% |
| total_return | 1005 | 86.6% |
| trades | 6 | 0.5% |
| consistency | 21 | 1.8% |
| holdout | 3 | 0.3% |
| recovery | 77 | 6.6% |
| regime | 38 | 3.3% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 58359 valutazioni, 97 passate (0.17%) · 2026-09-08 01:55 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 959 | 1.6% |
| recovery | 4982 | 8.6% |
| holdout | 417 | 0.7% |
| total_return | 39862 | 68.4% |
| consistency | 1520 | 2.6% |
| trades | 1928 | 3.3% |
| win_rate | 6 | 0.0% |
| regime | 8588 | 14.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-08 04:00 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.163%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (36) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
