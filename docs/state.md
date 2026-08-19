# Stato sistema (snapshot)
_Generato: 2026-08-19 14:53 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-19 14:52 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-19 14:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/179 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AEVOUSDT, AIOTUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, ALPINEUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ARIAUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, BANKUSDT, BBUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BIOUSDT, BLESSUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, CAKEUSDT, CCUSDT, CHZUSDT, CLOUSDT, COLLECTUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, CYBERUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, ETHWUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GWEIUSDT, HANAUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JASMYUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MAGMAUSDT, METUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, NEARUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIPPINUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RUNEUSDT, SANDUSDT, SEIUSDT, SIGNUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPACEUSDT, STABLEUSDT, STRKUSDT, SUIUSDT, SUNUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRIAUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZENUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-19 13:21 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-19 12:38 UTC · 1432 coppie valutate, 2 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| USUSDT | trend_following | 1.427 | 78% | 213 | 47% |
| SOONUSDT | momentum_cross_asset | 1.74 | 31% | 45 | 44% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1432 valutazioni, 2 passate (0.14%) · 2026-08-19 12:38 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 2 | 0.1% |
| total_return | 1210 | 84.6% |
| consistency | 23 | 1.6% |
| regime | 47 | 3.3% |
| pf_ex_top | 13 | 0.9% |
| win_rate | 2 | 0.1% |
| recovery | 104 | 7.3% |
| trades | 29 | 2.0% |

- quasi-passaggi (un solo criterio, di poco): **2** — sono i semi delle mutazioni del run successivo

**strategie generate** — 40454 valutazioni, 98 passate (0.24%) · 2026-08-19 13:21 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 211 | 0.5% |
| total_return | 29405 | 72.9% |
| consistency | 956 | 2.4% |
| regime | 4863 | 12.1% |
| pf_ex_top | 491 | 1.2% |
| win_rate | 52 | 0.1% |
| trades | 1213 | 3.0% |
| recovery | 3165 | 7.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-19 14:04 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.239%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.426041 |

**Ultime decisioni:**

- `set_param GATE_WIN_RATE_FLOOR 0.431981 → 0.42604126124999997` — 21 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~11, e il budget la consente (spazio 5x, attese 0.034/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.437906 → 0.43198113182` — 22 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 6x, attese 0.031/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.443912 → 0.43790587064` — 22 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 6x, attese 0.030/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.45 → 0.4439115` — 22 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 6x, attese 0.030/giorno contro un tetto di 1)
- `tighten` — budget di falsi positivi SFORATO (1.71 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
