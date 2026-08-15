# Stato sistema (snapshot)
_Generato: 2026-08-15 12:58 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-15 12:58 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-15 12:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/186 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOTUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANANAS31USDT, BANKUSDT, BBUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BICOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CCUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FOLKSUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GUNUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, INJUSDT, INXUSDT, IOTXUSDT, JASMYUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MAVIAUSDT, MEGAUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAVEUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SKYAIUSDT, SKYUSDT, SLPUSDT, SOLUSDT, STORJUSDT, SUIUSDT, SYNUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TLMUSDT, TREEUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, YGGUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-15 12:39 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-15 12:39 UTC · 1488 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1488 valutazioni, 0 passate (0.00%) · 2026-08-15 12:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 1 | 0.1% |
| consistency | 22 | 1.5% |
| total_return | 1270 | 85.3% |
| regime | 46 | 3.1% |
| pf_ex_top | 19 | 1.3% |
| trades | 31 | 2.1% |
| recovery | 96 | 6.5% |
| holdout | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **7** — sono i semi delle mutazioni del run successivo

**strategie generate** — 25668 valutazioni, 29 passate (0.11%) · 2026-08-15 10:09 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 22 | 0.1% |
| consistency | 413 | 1.6% |
| total_return | 20255 | 79.0% |
| regime | 2143 | 8.4% |
| pf_ex_top | 215 | 0.8% |
| trades | 981 | 3.8% |
| recovery | 1544 | 6.0% |
| holdout | 66 | 0.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-15 12:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.107%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 2.0 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.9 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.9 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.8 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.8 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
