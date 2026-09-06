# Stato sistema (snapshot)
_Generato: 2026-09-06 18:20 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-06 18:20 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-06 18:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/151 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000000BOBUSDT, 1000BONKUSDT, 1000CATUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 1INCHUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIXBTUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CATIUSDT, CHILLGUYUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOODUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, EPICUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FIDAUSDT, FILUSDT, FORMUSDT, GALAUSDT, GMXUSDT, GOATUSDT, GRTUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, METISUSDT, MITOUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, NAORISUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NMRUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, ROSEUSDT, SAHARAUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SNXUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WOOUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-06 16:58 UTC

### Salute del registro

- composizione: **1872 base** · **250 generate** (di cui 250 con almeno una conferma)
- occupazione: 2122/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-06 15:39 UTC · 1208 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1208 valutazioni, 0 passate (0.00%) · 2026-09-06 15:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 13 | 1.1% |
| regime | 41 | 3.4% |
| holdout | 3 | 0.2% |
| pf_ex_top | 11 | 0.9% |
| total_return | 1059 | 87.7% |
| recovery | 75 | 6.2% |
| trades | 6 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **5** — sono i semi delle mutazioni del run successivo

**strategie generate** — 58437 valutazioni, 93 passate (0.16%) · 2026-09-06 16:58 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 1608 | 2.8% |
| win_rate | 7 | 0.0% |
| recovery | 4882 | 8.4% |
| trades | 864 | 1.5% |
| total_return | 40933 | 70.2% |
| regime | 8706 | 14.9% |
| holdout | 394 | 0.7% |
| pf_ex_top | 950 | 1.6% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-06 18:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.156%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (39) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (39) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (40) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (39) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (39) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
