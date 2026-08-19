# Stato sistema (snapshot)
_Generato: 2026-08-19 16:47 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-19 16:45 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-19 16:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/179 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AEVOUSDT, AIOTUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, ALPINEUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ARIAUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, BANKUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BIOUSDT, BLESSUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, CAKEUSDT, CCUSDT, CHZUSDT, CLOUSDT, COLLECTUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, CYBERUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, ETHWUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GWEIUSDT, HANAUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MAGMAUSDT, METUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, NEARUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIPPINUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RSRUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SIGNUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPACEUSDT, STABLEUSDT, SUIUSDT, SUNUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TREEUSDT, TRIAUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZENUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-19 16:19 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-19 15:31 UTC · 1432 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| USUSDT | trend_following | 1.38 | 75% | 239 | 51% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1432 valutazioni, 1 passate (0.07%) · 2026-08-19 15:31 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 27 | 1.9% |
| total_return | 1203 | 84.1% |
| trades | 31 | 2.2% |
| holdout | 3 | 0.2% |
| regime | 49 | 3.4% |
| pf_ex_top | 9 | 0.6% |
| win_rate | 3 | 0.2% |
| recovery | 106 | 7.4% |

- quasi-passaggi (un solo criterio, di poco): **5** — sono i semi delle mutazioni del run successivo

**strategie generate** — 40633 valutazioni, 100 passate (0.25%) · 2026-08-19 16:19 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 980 | 2.4% |
| total_return | 29483 | 72.7% |
| trades | 1154 | 2.8% |
| win_rate | 32 | 0.1% |
| regime | 4908 | 12.1% |
| holdout | 229 | 0.6% |
| pf_ex_top | 483 | 1.2% |
| recovery | 3264 | 8.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-19 16:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.236%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.413296 |

**Ultime decisioni:**

- `set_param GATE_WIN_RATE_FLOOR 0.420183 → 0.41329620062999994` — 22 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.5%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 5x, attese 0.033/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.426041 → 0.42018293624999997` — 21 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~11, e il budget la consente (spazio 5x, attese 0.034/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.431981 → 0.42604126124999997` — 21 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~11, e il budget la consente (spazio 5x, attese 0.034/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.437906 → 0.43198113182` — 22 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 6x, attese 0.031/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.443912 → 0.43790587064` — 22 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 6x, attese 0.030/giorno contro un tetto di 1)

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
