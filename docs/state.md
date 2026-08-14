# Stato sistema (snapshot)
_Generato: 2026-08-14 05:46 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-14 05:44 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-14 05:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/185 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AKEUSDT, ALGOUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BABYUSDT, BANANAS31USDT, BANKUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BIOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CATIUSDT, CHZUSDT, CLOUSDT, COLLECTUSDT, COOKIEUSDT, COTIUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GRASSUSDT, GUAUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, INJUSDT, INXUSDT, IOTXUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KGENUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LSKUSDT, LTCUSDT, MEGAUSDT, METUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, MYXUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONEUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POWERUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAREUSDT, RAVEUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SKYAIUSDT, SOLUSDT, SQDUSDT, STABLEUSDT, STEEMUSDT, STORJUSDT, STRKUSDT, SUIUSDT, SWARMSUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, TAUSDT, TIAUSDT, TLMUSDT, TRADOORUSDT, TRBUSDT, TRUMPUSDT, TRUSTUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XANUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-14 05:31 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-14 04:59 UTC · 1480 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1480 valutazioni, 0 passate (0.00%) · 2026-08-14 04:59 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 13 | 0.9% |
| total_return | 1249 | 84.4% |
| trades | 39 | 2.6% |
| win_rate | 4 | 0.3% |
| recovery | 105 | 7.1% |
| consistency | 17 | 1.1% |
| regime | 52 | 3.5% |
| holdout | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 20976 valutazioni, 6 passate (0.03%) · 2026-08-14 05:31 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 178 | 0.8% |
| trades | 1736 | 8.3% |
| total_return | 16376 | 78.1% |
| win_rate | 6 | 0.0% |
| recovery | 1327 | 6.3% |
| consistency | 216 | 1.0% |
| regime | 1104 | 5.3% |
| holdout | 27 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-14 05:02 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.036%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 0.7 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.6 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.6 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.5 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.5 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
