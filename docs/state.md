# Stato sistema (snapshot)
_Generato: 2026-08-16 16:42 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-16 16:42 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-16 16:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/181 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BICOUSDT, BIGTIMEUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CCUSDT, CETUSUSDT, COOKIEUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, DUSKUSDT, EDENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GMTUSDT, GPSUSDT, GUAUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JCTUSDT, JSTUSDT, JTOUSDT, KAITOUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LIGHTUSDT, LINKUSDT, LITUSDT, LTCUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOMUSDT, NOTUSDT, NXPCUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, ONUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, PORTALUSDT, PROMUSDT, PTBUSDT, PUMPUSDT, QUSDT, RAREUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SANDUSDT, SEIUSDT, SFPUSDT, SKYAIUSDT, SOLUSDT, SPORTFUNUSDT, STABLEUSDT, STORJUSDT, SUIUSDT, SYRUPUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TOWNSUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZEREBROUSDT, 币安人生USDT
- aggiornato: 2026-08-16 16:15 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-16 15:36 UTC · 1448 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| MUBARAKUSDT | mean_reversion | 4.14 | 123% | 47 | 57% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1448 valutazioni, 1 passate (0.07%) · 2026-08-16 15:36 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 36 | 2.5% |
| consistency | 17 | 1.2% |
| total_return | 1233 | 85.2% |
| holdout | 2 | 0.1% |
| recovery | 97 | 6.7% |
| pf_ex_top | 9 | 0.6% |
| regime | 53 | 3.7% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 30227 valutazioni, 75 passate (0.25%) · 2026-08-16 16:15 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 22476 | 74.5% |
| win_rate | 5 | 0.0% |
| pf_ex_top | 373 | 1.2% |
| regime | 2931 | 9.7% |
| holdout | 146 | 0.5% |
| consistency | 581 | 1.9% |
| trades | 1599 | 5.3% |
| recovery | 2041 | 6.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-16 16:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.197%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.398537 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (28) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (28) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (28) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
