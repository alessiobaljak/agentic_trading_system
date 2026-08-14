# Stato sistema (snapshot)
_Generato: 2026-08-14 17:11 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-14 17:11 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-14 17:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/185 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACTUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AINUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AWEUSDT, AXSUSDT, BABYUSDT, BANANAS31USDT, BANKUSDT, BASUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CATIUSDT, CCUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GRASSUSDT, GUAUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, INJUSDT, INXUSDT, IOTXUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, LUNA2USDT, MEGAUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MYXUSDT, NEARUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POWERUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAREUSDT, RAVEUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, STORJUSDT, SUIUSDT, SWARMSUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, TAUSDT, TIAUSDT, TLMUSDT, TRADOORUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XANUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-14 16:06 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-14 15:34 UTC · 1480 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1480 valutazioni, 0 passate (0.00%) · 2026-08-14 15:34 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 4 | 0.3% |
| consistency | 25 | 1.7% |
| regime | 54 | 3.6% |
| total_return | 1249 | 84.4% |
| recovery | 98 | 6.6% |
| pf_ex_top | 14 | 0.9% |
| trades | 36 | 2.4% |

- quasi-passaggi (un solo criterio, di poco): **5** — sono i semi delle mutazioni del run successivo

**strategie generate** — 23125 valutazioni, 21 passate (0.09%) · 2026-08-14 16:06 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 297 | 1.3% |
| recovery | 1601 | 6.9% |
| total_return | 17705 | 76.6% |
| win_rate | 12 | 0.1% |
| holdout | 38 | 0.2% |
| regime | 1622 | 7.0% |
| pf_ex_top | 331 | 1.4% |
| trades | 1498 | 6.5% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-14 17:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.085%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 1.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
