# Stato sistema (snapshot)
_Generato: 2026-08-18 20:41 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-18 20:40 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-18 20:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/180 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, ALPINEUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BICOUSDT, BLESSUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CCUSDT, CHZUSDT, CLOUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DIAUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, ETHWUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GWEIUSDT, HANAUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MEMEUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, ONUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIPPINUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PROVEUSDT, PUMPUSDT, QUSDT, RAREUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOPHUSDT, STRKUSDT, SUIUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TRIAUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT
- aggiornato: 2026-08-18 19:19 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-18 18:33 UTC · 1440 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| USUSDT | trend_following | 1.518 | 77% | 170 | 45% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1440 valutazioni, 1 passate (0.07%) · 2026-08-18 18:33 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 26 | 1.8% |
| consistency | 14 | 1.0% |
| total_return | 1238 | 86.0% |
| win_rate | 1 | 0.1% |
| recovery | 102 | 7.1% |
| holdout | 3 | 0.2% |
| regime | 41 | 2.8% |
| pf_ex_top | 14 | 1.0% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 38700 valutazioni, 93 passate (0.24%) · 2026-08-18 19:19 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 2248 | 5.8% |
| consistency | 818 | 2.1% |
| total_return | 27673 | 71.7% |
| win_rate | 66 | 0.2% |
| recovery | 2770 | 7.2% |
| holdout | 156 | 0.4% |
| regime | 4446 | 11.5% |
| pf_ex_top | 430 | 1.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-18 20:05 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.234%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `tighten` — budget di falsi positivi SFORATO (1.76 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (2.55 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (2.50 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (2.50 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (2.40 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
