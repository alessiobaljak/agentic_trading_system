# Stato sistema (snapshot)
_Generato: 2026-08-15 08:45 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-15 08:44 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-15 08:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/187 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANANAS31USDT, BANKUSDT, BASUSDT, BBUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BICOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CCUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOODUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FOLKSUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GUAUSDT, GUNUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, ILVUSDT, INJUSDT, INXUSDT, IOTXUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MAVIAUSDT, MEGAUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAVEUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SKYUSDT, SLPUSDT, SOLUSDT, STORJUSDT, SUIUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TLMUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, YGGUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-15 07:10 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-15 06:35 UTC · 1496 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| MUBARAKUSDT | mean_reversion | 3.371 | 126% | 46 | 52% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1496 valutazioni, 1 passate (0.07%) · 2026-08-15 06:35 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 50 | 3.3% |
| total_return | 1269 | 84.9% |
| win_rate | 2 | 0.1% |
| recovery | 111 | 7.4% |
| trades | 31 | 2.1% |
| pf_ex_top | 11 | 0.7% |
| holdout | 2 | 0.1% |
| consistency | 19 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 25296 valutazioni, 28 passate (0.11%) · 2026-08-15 07:10 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 1805 | 7.1% |
| total_return | 19650 | 77.8% |
| win_rate | 15 | 0.1% |
| recovery | 1556 | 6.2% |
| trades | 1618 | 6.4% |
| pf_ex_top | 240 | 0.9% |
| holdout | 59 | 0.2% |
| consistency | 325 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-15 08:04 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.108%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 1.8 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.7 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.7 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.7 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.6 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
