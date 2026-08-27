# Stato sistema (snapshot)
_Generato: 2026-08-27 09:49 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-27 09:49 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-27 09:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/144 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BASUSDT, BBUSDT, BCHUSDT, BEAMXUSDT, BICOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, CAKEUSDT, CATIUSDT, CFXUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CVXUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FIDAUSDT, FILUSDT, GALAUSDT, GASUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, INJUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KMNOUSDT, KOMAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MASKUSDT, MELANIAUSDT, MERLUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NILUSDT, ONDOUSDT, ONGUSDT, ONTUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLAYUSDT, PLUMEUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPBTCUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SUSDT, SXTUSDT, TACUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TUTUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZROUSDT
- aggiornato: 2026-08-27 09:38 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-27 09:38 UTC · 1152 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1152 valutazioni, 0 passate (0.00%) · 2026-08-27 09:38 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 2 | 0.2% |
| total_return | 1000 | 86.8% |
| consistency | 12 | 1.0% |
| pf_ex_top | 11 | 1.0% |
| regime | 41 | 3.6% |
| trades | 12 | 1.0% |
| recovery | 74 | 6.4% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 41606 valutazioni, 39 passate (0.09%) · 2026-08-27 07:35 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 6 | 0.0% |
| consistency | 939 | 2.3% |
| trades | 2175 | 5.2% |
| total_return | 29446 | 70.8% |
| holdout | 189 | 0.5% |
| regime | 5309 | 12.8% |
| recovery | 2995 | 7.2% |
| pf_ex_top | 508 | 1.2% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-27 09:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.091%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (33) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (37) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (35) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
