# Stato sistema (snapshot)
_Generato: 2026-08-17 13:05 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-17 13:05 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-17 13:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/182 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANKUSDT, BARDUSDT, BASUSDT, BCHUSDT, BEATUSDT, BELUSDT, BICOUSDT, BIGTIMEUSDT, BLESSUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CCUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DIAUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, EVAAUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JASMYUSDT, JCTUSDT, JTOUSDT, KAITOUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LIGHTUSDT, LINKUSDT, LITUSDT, LTCUSDT, LUMIAUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, NOMUSDT, NXPCUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, ONUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, QUSDT, RAREUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RVNUSDT, SANDUSDT, SEIUSDT, SFPUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOPHUSDT, SPORTFUNUSDT, STABLEUSDT, STBLUSDT, STRKUSDT, SUIUSDT, SYRUPUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TOWNSUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZEREBROUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-17 12:35 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-17 12:35 UTC · 1456 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| 2ZUSDT | mean_reversion | 1.523 | 37% | 90 | 46% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1456 valutazioni, 1 passate (0.07%) · 2026-08-17 12:35 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 2 | 0.1% |
| total_return | 1242 | 85.4% |
| recovery | 91 | 6.3% |
| win_rate | 5 | 0.3% |
| consistency | 22 | 1.5% |
| regime | 47 | 3.2% |
| pf_ex_top | 12 | 0.8% |
| trades | 34 | 2.3% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34034 valutazioni, 79 passate (0.23%) · 2026-08-17 10:17 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 129 | 0.4% |
| total_return | 25818 | 76.0% |
| win_rate | 46 | 0.1% |
| recovery | 2242 | 6.6% |
| trades | 1428 | 4.2% |
| regime | 3345 | 9.9% |
| pf_ex_top | 309 | 0.9% |
| consistency | 638 | 1.9% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-17 13:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.225%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `tighten` — budget di falsi positivi SFORATO (1.44 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.48 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.48 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.12 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.06 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
