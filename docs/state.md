# Stato sistema (snapshot)
_Generato: 2026-08-19 22:41 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-19 22:41 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-19 22:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/138 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIOTUSDT, AIOUSDT, ALGOUSDT, ALICEUSDT, ALPINEUSDT, APTUSDT, ARBUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BIOUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCDOMUSDT, BTCUSDT, CAKEUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, CYBERUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GPSUSDT, GRASSUSDT, HBARUSDT, HEIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LTCUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RSRUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SIGNUSDT, SKYAIUSDT, SOLUSDT, SOONUSDT, SPXUSDT, STRKUSDT, SUIUSDT, SUNUSDT, TAOUSDT, TIAUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, XLMUSDT, XMRUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT
- aggiornato: 2026-08-19 22:16 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-19 21:31 UTC · 1104 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1104 valutazioni, 0 passate (0.00%) · 2026-08-19 21:31 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 8 | 0.7% |
| regime | 38 | 3.4% |
| pf_ex_top | 13 | 1.2% |
| holdout | 2 | 0.2% |
| consistency | 19 | 1.7% |
| recovery | 65 | 5.9% |
| total_return | 958 | 86.8% |
| win_rate | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 32016 valutazioni, 16 passate (0.05%) · 2026-08-19 22:16 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 3740 | 11.7% |
| trades | 912 | 2.9% |
| pf_ex_top | 373 | 1.2% |
| holdout | 79 | 0.2% |
| consistency | 563 | 1.8% |
| recovery | 2191 | 6.8% |
| total_return | 24137 | 75.4% |
| win_rate | 5 | 0.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-19 22:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.241%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `set_param GATE_WIN_RATE_FLOOR 0.402099 → 0.39661436963999996` — 20 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 5x, attese 0.035/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.407659 → 0.40209853124` — 20 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 5x, attese 0.035/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.413296 → 0.40765864256` — 20 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 5x, attese 0.035/giorno contro un tetto di 1)
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (20) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (20) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
