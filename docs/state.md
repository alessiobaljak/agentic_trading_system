# Stato sistema (snapshot)
_Generato: 2026-08-14 19:14 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-14 19:13 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-14 19:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/186 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AINUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AWEUSDT, AXSUSDT, BABYUSDT, BANANAS31USDT, BANKUSDT, BASUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CATIUSDT, CCUSDT, CFXUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOODUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GUAUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, ILVUSDT, INJUSDT, INXUSDT, IOTXUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MEGAUSDT, MIRAUSDT, MITOUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MYXUSDT, NEARUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POWERUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAREUSDT, RAVEUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, STORJUSDT, SUIUSDT, SWARMSUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TRADOORUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-14 19:09 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-14 18:34 UTC · 1488 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1488 valutazioni, 0 passate (0.00%) · 2026-08-14 18:34 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 18 | 1.2% |
| total_return | 1246 | 83.7% |
| pf_ex_top | 12 | 0.8% |
| recovery | 117 | 7.9% |
| win_rate | 2 | 0.1% |
| regime | 55 | 3.7% |
| trades | 34 | 2.3% |
| holdout | 4 | 0.3% |

- quasi-passaggi (un solo criterio, di poco): **5** — sono i semi delle mutazioni del run successivo

**strategie generate** — 23622 valutazioni, 20 passate (0.08%) · 2026-08-14 19:09 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 337 | 1.4% |
| total_return | 17641 | 74.7% |
| pf_ex_top | 254 | 1.1% |
| recovery | 1396 | 5.9% |
| win_rate | 13 | 0.1% |
| regime | 1665 | 7.1% |
| trades | 2247 | 9.5% |
| holdout | 49 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-14 19:04 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.085%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 1.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.1 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
