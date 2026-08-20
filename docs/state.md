# Stato sistema (snapshot)
_Generato: 2026-08-20 18:59 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-20 18:58 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-20 18:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/143 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SATSUSDT, 1000SHIBUSDT, 1000XECUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOUSDT, ALGOUSDT, ALICEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BIOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRETTUSDT, BRUSDT, BTCDOMUSDT, BTCUSDT, CAKEUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, ICXUSDT, IMXUSDT, INJUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MELANIAUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RUNEUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SPXUSDT, STORJUSDT, STRKUSDT, STXUSDT, SUIUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRBUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TURBOUSDT, TUTUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XMRUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT
- aggiornato: 2026-08-20 18:35 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-20 18:35 UTC · 1144 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1144 valutazioni, 0 passate (0.00%) · 2026-08-20 18:35 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 1 | 0.1% |
| consistency | 12 | 1.0% |
| holdout | 1 | 0.1% |
| regime | 35 | 3.1% |
| total_return | 993 | 86.8% |
| pf_ex_top | 10 | 0.9% |
| recovery | 84 | 7.3% |
| trades | 8 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34320 valutazioni, 20 passate (0.06%) · 2026-08-20 16:36 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 3 | 0.0% |
| consistency | 623 | 1.8% |
| holdout | 88 | 0.3% |
| regime | 3944 | 11.5% |
| total_return | 25934 | 75.6% |
| pf_ex_top | 420 | 1.2% |
| recovery | 2446 | 7.1% |
| trades | 842 | 2.5% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-20 18:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.056%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (30) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
