# Stato sistema (snapshot)
_Generato: 2026-09-12 15:32 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-12 15:29 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-12 15:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/149 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BLURUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CATIUSDT, CHZUSDT, COTIUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOGSUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ERAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, GRIFFAINUSDT, HBARUSDT, HEMIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KNCUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MITOUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, REZUSDT, RUNEUSDT, RVNUSDT, SAGAUSDT, SAHARAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOPHUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SUSHIUSDT, SYRUPUSDT, TAGUSDT, TAOUSDT, TAUSDT, THETAUSDT, TIAUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-12 14:08 UTC

### Salute del registro

- composizione: **1840 base** · **334 generate** (di cui 334 con almeno una conferma)
- occupazione: 2174/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-12 12:42 UTC · 1192 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1192 valutazioni, 0 passate (0.00%) · 2026-09-12 12:42 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 62 | 5.2% |
| regime | 39 | 3.3% |
| total_return | 1055 | 88.5% |
| pf_ex_top | 10 | 0.8% |
| consistency | 16 | 1.3% |
| trades | 8 | 0.7% |
| holdout | 2 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 64500 valutazioni, 126 passate (0.20%) · 2026-09-12 14:08 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 5143 | 8.0% |
| total_return | 45236 | 70.3% |
| trades | 1372 | 2.1% |
| holdout | 420 | 0.7% |
| win_rate | 2 | 0.0% |
| consistency | 1728 | 2.7% |
| pf_ex_top | 805 | 1.3% |
| regime | 9668 | 15.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-12 15:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.192%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (34) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
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
