# Stato sistema (snapshot)
_Generato: 2026-08-19 03:11 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-19 03:11 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-19 03:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/180 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, ALPINEUSDT, APRUSDT, APTUSDT, ARBUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, BABYUSDT, BANKUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BICOUSDT, BLESSUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, CAKEUSDT, CCUSDT, CHZUSDT, CLOUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, ETHWUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GWEIUSDT, HANAUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, JASMYUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, MAGMAUSDT, MEMEUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, ONUSDT, OPENUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIPPINUSDT, PIXELUSDT, PLUMEUSDT, PNUTUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PROVEUSDT, PUMPUSDT, PYTHUSDT, QUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RUNEUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SPORTFUNUSDT, STRKUSDT, SUIUSDT, SUNUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRIAUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WCTUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT
- aggiornato: 2026-08-19 01:31 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-19 00:42 UTC · 1440 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1440 valutazioni, 0 passate (0.00%) · 2026-08-19 00:42 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 3 | 0.2% |
| total_return | 1229 | 85.3% |
| trades | 29 | 2.0% |
| consistency | 18 | 1.2% |
| recovery | 105 | 7.3% |
| win_rate | 2 | 0.1% |
| regime | 45 | 3.1% |
| pf_ex_top | 9 | 0.6% |

- quasi-passaggi (un solo criterio, di poco): **5** — sono i semi delle mutazioni del run successivo

**strategie generate** — 39420 valutazioni, 79 passate (0.20%) · 2026-08-19 01:31 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 165 | 0.4% |
| total_return | 27697 | 70.4% |
| trades | 2327 | 5.9% |
| consistency | 831 | 2.1% |
| recovery | 3204 | 8.1% |
| win_rate | 72 | 0.2% |
| pf_ex_top | 581 | 1.5% |
| regime | 4464 | 11.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-19 03:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.193%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `tighten` — budget di falsi positivi SFORATO (1.22 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.22 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.79 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.79 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.79 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
