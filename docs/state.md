# Stato sistema (snapshot)
_Generato: 2026-08-16 06:59 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-16 06:59 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-16 06:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/182 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AIOTUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, BANANAUSDT, BANKUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BICOUSDT, BIGTIMEUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CCUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, DUSKUSDT, EDENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FOLKSUSDT, FUSDT, GALAUSDT, GIGGLEUSDT, GMTUSDT, GPSUSDT, GRASSUSDT, GUNUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JCTUSDT, JTOUSDT, KAITOUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOMUSDT, NOTUSDT, NXPCUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDERUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PTBUSDT, PUMPUSDT, QUSDT, RAREUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RVNUSDT, SCRTUSDT, SCRUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SOMIUSDT, SOPHUSDT, SPORTFUNUSDT, STORJUSDT, SUIUSDT, SYNUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZEREBROUSDT, 币安人生USDT
- aggiornato: 2026-08-16 06:36 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-16 06:36 UTC · 1456 coppie valutate, 2 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| MUBARAKUSDT | mean_reversion | 4.041 | 107% | 48 | 58% |
| USUSDT | trend_following | 1.304 | 57% | 231 | 53% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1456 valutazioni, 2 passate (0.14%) · 2026-08-16 06:36 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 53 | 3.6% |
| trades | 30 | 2.1% |
| pf_ex_top | 10 | 0.7% |
| holdout | 4 | 0.3% |
| consistency | 16 | 1.1% |
| recovery | 94 | 6.5% |
| win_rate | 2 | 0.1% |
| total_return | 1245 | 85.6% |

- quasi-passaggi (un solo criterio, di poco): **5** — sono i semi delle mutazioni del run successivo

**strategie generate** — 27846 valutazioni, 44 passate (0.16%) · 2026-08-16 04:16 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 2300 | 8.3% |
| trades | 2800 | 10.1% |
| pf_ex_top | 214 | 0.8% |
| win_rate | 2 | 0.0% |
| recovery | 1651 | 5.9% |
| holdout | 89 | 0.3% |
| consistency | 418 | 1.5% |
| total_return | 20328 | 73.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-16 06:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.150%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.398537 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (27) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (27) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (32) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
