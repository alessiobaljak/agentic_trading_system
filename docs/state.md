# Stato sistema (snapshot)
_Generato: 2026-09-01 21:02 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-01 20:59 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-01 20:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/144 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AIOUSDT, ALGOUSDT, ANIMEUSDT, API3USDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AUCTIONUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, BANKUSDT, BANUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CFXUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CVXUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOGSUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ERAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MINAUSDT, MITOUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RUNEUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SOMIUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYRUPUSDT, TACUSDT, TAOUSDT, TIAUSDT, TNSRUSDT, TRUMPUSDT, TRXUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-01 19:43 UTC

### Salute del registro

- composizione: **1873 base** · **123 generate** (di cui 123 con almeno una conferma)
- occupazione: 1996/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-01 18:36 UTC · 1152 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1152 valutazioni, 0 passate (0.00%) · 2026-09-01 18:36 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 76 | 6.6% |
| total_return | 1006 | 87.3% |
| holdout | 2 | 0.2% |
| pf_ex_top | 8 | 0.7% |
| trades | 9 | 0.8% |
| regime | 40 | 3.5% |
| consistency | 11 | 1.0% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 49049 valutazioni, 90 passate (0.18%) · 2026-09-01 19:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 277 | 0.6% |
| pf_ex_top | 620 | 1.3% |
| regime | 6829 | 13.9% |
| total_return | 35104 | 71.7% |
| recovery | 3829 | 7.8% |
| consistency | 1237 | 2.5% |
| trades | 1061 | 2.2% |
| win_rate | 2 | 0.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-01 20:05 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.179%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (28) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
