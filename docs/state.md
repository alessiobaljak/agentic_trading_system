# Stato sistema (snapshot)
_Generato: 2026-08-14 22:41 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-14 22:41 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-14 22:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/186 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AWEUSDT, AXSUSDT, BANANAS31USDT, BANKUSDT, BASUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, CAKEUSDT, CATIUSDT, CCUSDT, CFXUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOODUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GUAUSDT, GUNUSDT, GWEIUSDT, HANAUSDT, HBARUSDT, HEIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDUSDT, ILVUSDT, INJUSDT, INXUSDT, IOTXUSDT, JASMYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MEGAUSDT, MIRAUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, MYXUSDT, NEARUSDT, NILUSDT, NOTUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, RAREUSDT, RAVEUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRTUSDT, SEIUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, STORJUSDT, SUIUSDT, SWARMSUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TRADOORUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-14 22:11 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-14 21:35 UTC · 1488 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| MUSDT | mean_reversion | 2.656 | 138% | 88 | 49% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1488 valutazioni, 1 passate (0.07%) · 2026-08-14 21:35 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 47 | 3.2% |
| consistency | 21 | 1.4% |
| holdout | 1 | 0.1% |
| pf_ex_top | 10 | 0.7% |
| trades | 30 | 2.0% |
| total_return | 1260 | 84.7% |
| win_rate | 1 | 0.1% |
| recovery | 117 | 7.9% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 23622 valutazioni, 23 passate (0.10%) · 2026-08-14 22:11 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 1763 | 7.5% |
| consistency | 351 | 1.5% |
| holdout | 49 | 0.2% |
| pf_ex_top | 172 | 0.7% |
| trades | 1425 | 6.0% |
| total_return | 18447 | 78.2% |
| recovery | 1382 | 5.9% |
| win_rate | 10 | 0.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-14 22:00 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.084%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `none` — solo 1.4 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 1.2 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
