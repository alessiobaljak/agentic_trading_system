# Stato sistema (snapshot)
_Generato: 2026-09-07 04:42 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-07 04:41 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-07 04:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/149 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000000BOBUSDT, 1000BONKUSDT, 1000CATUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CATIUSDT, CHILLGUYUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOODUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, EPICUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FIDAUSDT, FILUSDT, FORMUSDT, GALAUSDT, GMXUSDT, GRTUSDT, HBARUSDT, HEMIUSDT, HOMEUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, IOUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, LAUSDT, LAYERUSDT, LDOUSDT, LINKUSDT, LTCUSDT, METISUSDT, MITOUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, NAORISUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, PNUTUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, ROSEUSDT, SAHARAUSDT, SANDUSDT, SEIUSDT, SOLUSDT, SOLVUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SUSHIUSDT, TACUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WOOUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XVGUSDT, YGGUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-07 03:35 UTC

### Salute del registro

- composizione: **1920 base** · **253 generate** (di cui 253 con almeno una conferma)
- occupazione: 2173/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-07 03:35 UTC · 1192 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1192 valutazioni, 0 passate (0.00%) · 2026-09-07 03:35 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 79 | 6.6% |
| consistency | 20 | 1.7% |
| regime | 36 | 3.0% |
| trades | 7 | 0.6% |
| total_return | 1034 | 86.7% |
| pf_ex_top | 14 | 1.2% |
| win_rate | 1 | 0.1% |
| holdout | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 57663 valutazioni, 86 passate (0.15%) · 2026-09-07 01:58 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 1556 | 2.7% |
| consistency | 1528 | 2.7% |
| recovery | 4598 | 8.0% |
| regime | 8689 | 15.1% |
| total_return | 39951 | 69.4% |
| pf_ex_top | 840 | 1.5% |
| win_rate | 7 | 0.0% |
| holdout | 408 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-07 04:00 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.146%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (38) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (38) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (38) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (38) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (38) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
