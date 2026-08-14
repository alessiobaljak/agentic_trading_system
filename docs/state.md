# Stato sistema (snapshot)
_Generato: 2026-08-14 11:08 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-14 11:08 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-14 11:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/185 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AKEUSDT, ALGOUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BABYUSDT, BANANAS31USDT, BANKUSDT, BASUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BIOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CATIUSDT, CHZUSDT, COLLECTUSDT, COOKIEUSDT, COTIUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GRASSUSDT, GUAUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, INJUSDT, INXUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LSKUSDT, LTCUSDT, MEGAUSDT, METUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, MYXUSDT, NEARUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONEUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, POWERUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAREUSDT, RAVEUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SQDUSDT, STABLEUSDT, STORJUSDT, STRKUSDT, SUIUSDT, SWARMSUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, TAUSDT, TIAUSDT, TRADOORUSDT, TRBUSDT, TRUMPUSDT, TRUSTUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XANUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-14 10:10 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-14 09:39 UTC · 1480 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1480 valutazioni, 0 passate (0.00%) · 2026-08-14 09:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 64 | 4.3% |
| win_rate | 1 | 0.1% |
| pf_ex_top | 15 | 1.0% |
| consistency | 22 | 1.5% |
| holdout | 1 | 0.1% |
| total_return | 1245 | 84.1% |
| trades | 34 | 2.3% |
| recovery | 98 | 6.6% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 22448 valutazioni, 12 passate (0.05%) · 2026-08-14 10:10 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 10 | 0.0% |
| regime | 1465 | 6.5% |
| consistency | 288 | 1.3% |
| pf_ex_top | 123 | 0.5% |
| holdout | 36 | 0.2% |
| total_return | 17296 | 77.1% |
| trades | 2088 | 9.3% |
| recovery | 1130 | 5.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-14 11:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.050%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 0.9 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.9 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.8 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.8 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.8 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
