# Stato sistema (snapshot)
_Generato: 2026-08-15 16:41 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-15 16:41 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-15 16:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/186 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOTUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANANAS31USDT, BANANAUSDT, BANKUSDT, BBUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BICOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CCUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, DUSKUSDT, EDENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FOLKSUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GRASSUSDT, GRIFFAINUSDT, GUNUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, INJUSDT, INXUSDT, IOTXUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MEGAUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIPPINUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QUSDT, RAREUSDT, RAVEUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SANDUSDT, SCRTUSDT, SCRUSDT, SEIUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, STORJUSDT, SUIUSDT, SYNUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TLMUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, YGGUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-15 16:16 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-15 15:40 UTC · 1488 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| MUBARAKUSDT | mean_reversion | 4.041 | 107% | 48 | 58% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1488 valutazioni, 1 passate (0.07%) · 2026-08-15 15:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 1268 | 85.3% |
| trades | 28 | 1.9% |
| consistency | 21 | 1.4% |
| win_rate | 2 | 0.1% |
| holdout | 1 | 0.1% |
| regime | 49 | 3.3% |
| recovery | 105 | 7.1% |
| pf_ex_top | 13 | 0.9% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 26784 valutazioni, 36 passate (0.13%) · 2026-08-15 16:16 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 20274 | 75.8% |
| trades | 1476 | 5.5% |
| consistency | 460 | 1.7% |
| win_rate | 2 | 0.0% |
| holdout | 71 | 0.3% |
| regime | 2294 | 8.6% |
| recovery | 1861 | 7.0% |
| pf_ex_top | 310 | 1.2% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-15 16:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.127%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.398537 |

**Ultime decisioni:**

- `set_param GATE_WIN_RATE_FLOOR 0.415446 → 0.3985373478` — 17 candidate sono fermate SOLO da 'win_rate' (mediana: manca 3.7%). La mossa ne dovrebbe sbloccare ~10, e il budget la consente (spazio 2x, attese 0.355/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.432378 → 0.41544607752` — 17 candidate sono fermate SOLO da 'win_rate' (mediana: manca 3.6%). La mossa ne dovrebbe sbloccare ~10, e il budget la consente (spazio 2x, attese 0.335/giorno contro un tetto di 1)
- `set_param GATE_WIN_RATE_FLOOR 0.45 → 0.43237800000000004` — 17 candidate sono fermate SOLO da 'win_rate' (mediana: manca 3.6%). La mossa ne dovrebbe sbloccare ~10, e il budget la consente (spazio 2x, attese 0.335/giorno contro un tetto di 1)
- `none` — solo 2.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 2.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
