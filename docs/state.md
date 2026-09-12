# Stato sistema (snapshot)
_Generato: 2026-09-12 22:18 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-12 22:14 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-12 22:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/154 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, ALCHUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARPAUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIGTIMEUSDT, BLURUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CYBERUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOGSUSDT, DOODUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ERAUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRIFFAINUSDT, HBARUSDT, HEMIUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, INJUSDT, IOSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MITOUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, ONDOUSDT, ONGUSDT, OPENUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, POLUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, REZUSDT, RUNEUSDT, RVNUSDT, SAGAUSDT, SAHARAUSDT, SANDUSDT, SEIUSDT, SIRENUSDT, SKYUSDT, SOLUSDT, SOMIUSDT, SOPHUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYRUPUSDT, TAGUSDT, TAOUSDT, TAUSDT, THETAUSDT, THEUSDT, TIAUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UNIUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZROUSDT, ZRXUSDT
- aggiornato: 2026-09-12 21:44 UTC

### Salute del registro

- composizione: **1872 base** · **347 generate** (di cui 347 con almeno una conferma)
- occupazione: 2219/3000 — ok

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-12 21:44 UTC · 1232 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1232 valutazioni, 0 passate (0.00%) · 2026-09-12 21:44 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 1089 | 88.4% |
| regime | 40 | 3.2% |
| consistency | 18 | 1.5% |
| holdout | 1 | 0.1% |
| trades | 7 | 0.6% |
| pf_ex_top | 10 | 0.8% |
| recovery | 67 | 5.4% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 66990 valutazioni, 144 passate (0.21%) · 2026-09-12 20:02 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 2 | 0.0% |
| total_return | 46686 | 69.8% |
| holdout | 443 | 0.7% |
| pf_ex_top | 896 | 1.3% |
| regime | 9951 | 14.9% |
| recovery | 5536 | 8.3% |
| trades | 1497 | 2.2% |
| consistency | 1835 | 2.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-12 22:00 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.211%**

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
