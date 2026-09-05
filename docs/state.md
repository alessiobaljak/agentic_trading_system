# Stato sistema (snapshot)
_Generato: 2026-09-05 15:14 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-05 15:14 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-05 15:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/147 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000CATUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIXBTUSDT, ALGOUSDT, ANKRUSDT, APEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CATIUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, EDUUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LPTUSDT, LTCUSDT, MERLUSDT, MITOUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NAORISUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PTBUSDT, PUMPUSDT, PYTHUSDT, QUSDT, RENDERUSDT, ROSEUSDT, SAHARAUSDT, SANDUSDT, SEIUSDT, SIGNUSDT, SOLUSDT, SOPHUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SUSHIUSDT, SYRUPUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-05 13:58 UTC

### Salute del registro

- composizione: **1864 base** · **228 generate** (di cui 228 con almeno una conferma)
- occupazione: 2092/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-05 12:44 UTC · 1176 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1176 valutazioni, 0 passate (0.00%) · 2026-09-05 12:44 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 15 | 1.3% |
| total_return | 1025 | 87.2% |
| recovery | 71 | 6.0% |
| trades | 7 | 0.6% |
| regime | 43 | 3.7% |
| holdout | 2 | 0.2% |
| pf_ex_top | 13 | 1.1% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 54312 valutazioni, 87 passate (0.16%) · 2026-09-05 13:58 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 3 | 0.0% |
| recovery | 4517 | 8.3% |
| trades | 989 | 1.8% |
| pf_ex_top | 821 | 1.5% |
| consistency | 1414 | 2.6% |
| total_return | 38037 | 70.1% |
| holdout | 365 | 0.7% |
| regime | 8079 | 14.9% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-05 15:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.157%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (36) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (36) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (36) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
