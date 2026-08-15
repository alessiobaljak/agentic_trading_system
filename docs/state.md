# Stato sistema (snapshot)
_Generato: 2026-08-15 01:49 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-15 01:49 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-15 01:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/186 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AWEUSDT, AXSUSDT, BANANAS31USDT, BANKUSDT, BASUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CATIUSDT, CCUSDT, CFXUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOODUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GUAUSDT, GUNUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, ILVUSDT, INJUSDT, INXUSDT, IOTXUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, LUNA2USDT, MEGAUSDT, MIRAUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MYXUSDT, NEARUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POWERUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAVEUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, STORJUSDT, SUIUSDT, SWARMSUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TRADOORUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-15 01:24 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-15 00:50 UTC · 1488 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1488 valutazioni, 0 passate (0.00%) · 2026-08-15 00:50 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 31 | 2.1% |
| regime | 47 | 3.2% |
| pf_ex_top | 11 | 0.7% |
| recovery | 123 | 8.3% |
| consistency | 23 | 1.5% |
| total_return | 1250 | 84.0% |
| holdout | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 24684 valutazioni, 25 passate (0.10%) · 2026-08-15 01:24 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 1733 | 7.0% |
| trades | 1168 | 4.7% |
| win_rate | 13 | 0.1% |
| pf_ex_top | 217 | 0.9% |
| recovery | 1327 | 5.4% |
| consistency | 304 | 1.2% |
| total_return | 19837 | 80.4% |
| holdout | 60 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-15 01:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.092%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 1.5 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.5 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.4 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.4 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
