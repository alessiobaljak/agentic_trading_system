# Stato sistema (snapshot)
_Generato: 2026-08-22 08:47 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-22 08:44 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-22 08:35 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/149 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ADAUSDT, AEROUSDT, ALGOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BTCDOMUSDT, BTCUSDT, CAKEUSDT, CFXUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GASUSDT, GPSUSDT, GRASSUSDT, GRTUSDT, HBARUSDT, HEIUSDT, HMSTRUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, IOTAUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KMNOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MELANIAUSDT, MEMEUSDT, MEUSDT, MOODENGUSDT, MORPHOUSDT, MOVEUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RUNEUSDT, SAHARAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, SSVUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, USUALUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XMRUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-08-22 07:38 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-22 06:41 UTC · 1192 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| GRTUSDT | mean_reversion | 1.727 | 88% | 198 | 46% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1192 valutazioni, 1 passate (0.08%) · 2026-08-22 06:41 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 18 | 1.5% |
| recovery | 79 | 6.6% |
| pf_ex_top | 10 | 0.8% |
| holdout | 1 | 0.1% |
| trades | 6 | 0.5% |
| total_return | 1038 | 87.2% |
| regime | 39 | 3.3% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 37296 valutazioni, 29 passate (0.08%) · 2026-08-22 07:38 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 2818 | 7.6% |
| pf_ex_top | 483 | 1.3% |
| holdout | 141 | 0.4% |
| regime | 4639 | 12.4% |
| consistency | 780 | 2.1% |
| win_rate | 2 | 0.0% |
| trades | 400 | 1.1% |
| total_return | 28004 | 75.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-22 08:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.078%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (31) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
