# Stato sistema (snapshot)
_Generato: 2026-09-03 00:16 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-03 00:14 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-03 00:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/145 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALGOUSDT, ANKRUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AUCTIONUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BEAMXUSDT, BERAUSDT, BICOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, COWUSDT, CRVUSDT, CVXUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICNTUSDT, ICPUSDT, INJUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MANAUSDT, MINAUSDT, MITOUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, REDUSDT, RENDERUSDT, SAFEUSDT, SANDUSDT, SEIUSDT, SIGNUSDT, SKYAIUSDT, SOLUSDT, SOMIUSDT, SOPHUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYRUPUSDT, TACUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-02 22:42 UTC

### Salute del registro

- composizione: **1896 base** · **171 generate** (di cui 171 con almeno una conferma)
- occupazione: 2067/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-02 21:37 UTC · 1160 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1160 valutazioni, 0 passate (0.00%) · 2026-09-02 21:37 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 63 | 5.4% |
| pf_ex_top | 13 | 1.1% |
| regime | 32 | 2.8% |
| holdout | 3 | 0.3% |
| consistency | 20 | 1.7% |
| win_rate | 1 | 0.1% |
| trades | 5 | 0.4% |
| total_return | 1023 | 88.2% |

- quasi-passaggi (un solo criterio, di poco): **6** — sono i semi delle mutazioni del run successivo

**strategie generate** — 50750 valutazioni, 105 passate (0.21%) · 2026-09-02 22:42 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 4381 | 8.7% |
| pf_ex_top | 732 | 1.4% |
| regime | 7282 | 14.4% |
| holdout | 344 | 0.7% |
| consistency | 1268 | 2.5% |
| win_rate | 7 | 0.0% |
| trades | 1535 | 3.0% |
| total_return | 35096 | 69.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-03 00:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.202%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (36) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (36) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
