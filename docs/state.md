# Stato sistema (snapshot)
_Generato: 2026-09-02 00:15 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-02 00:14 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-02 00:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/145 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AIOUSDT, ALGOUSDT, API3USDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AUCTIONUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, BANKUSDT, BANUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CFXUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CVXUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOGSUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ERAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GPSUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MINAUSDT, MITOUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PLUMEUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RUNEUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SOMIUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYRUPUSDT, TACUSDT, TAOUSDT, TIAUSDT, TNSRUSDT, TRUMPUSDT, TRXUSDT, TUTUSDT, TWTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-01 22:53 UTC

### Salute del registro

- composizione: **1865 base** · **128 generate** (di cui 128 con almeno una conferma)
- occupazione: 1993/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-01 21:45 UTC · 1160 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1160 valutazioni, 0 passate (0.00%) · 2026-09-01 21:45 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 8 | 0.7% |
| win_rate | 1 | 0.1% |
| pf_ex_top | 11 | 0.9% |
| consistency | 11 | 0.9% |
| holdout | 3 | 0.3% |
| regime | 39 | 3.4% |
| total_return | 1003 | 86.5% |
| recovery | 84 | 7.2% |

- quasi-passaggi (un solo criterio, di poco): **5** — sono i semi delle mutazioni del run successivo

**strategie generate** — 49735 valutazioni, 100 passate (0.20%) · 2026-09-01 22:53 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 1446 | 2.9% |
| win_rate | 2 | 0.0% |
| pf_ex_top | 705 | 1.4% |
| consistency | 1255 | 2.5% |
| holdout | 325 | 0.7% |
| regime | 7023 | 14.1% |
| total_return | 34767 | 70.0% |
| recovery | 4112 | 8.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-02 00:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.197%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
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
