# Stato sistema (snapshot)
_Generato: 2026-08-17 20:43 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-17 20:43 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-17 20:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/183 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANKUSDT, BASUSDT, BCHUSDT, BEATUSDT, BELUSDT, BICOUSDT, BIGTIMEUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CCUSDT, CHZUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DIAUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, ENSUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, EVAAUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GUNUSDT, GWEIUSDT, HAEDALUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LTCUSDT, LUMIAUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, MUSDT, NEARUSDT, NILUSDT, NXPCUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, ONUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PORTALUSDT, POWERUSDT, PROMUSDT, PUMPUSDT, QUSDT, RAREUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RVNUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOPHUSDT, SPORTFUNUSDT, STABLEUSDT, STBLUSDT, STRKUSDT, SUIUSDT, SYRUPUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TOWNSUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZEREBROUSDT, ZKUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-17 19:19 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-17 18:39 UTC · 1464 coppie valutate, 2 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| XPINUSDT | mean_reversion | 1.483 | 37% | 76 | 50% |
| 2ZUSDT | mean_reversion | 1.523 | 37% | 90 | 46% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1464 valutazioni, 2 passate (0.14%) · 2026-08-17 18:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 20 | 1.4% |
| win_rate | 2 | 0.1% |
| holdout | 1 | 0.1% |
| recovery | 103 | 7.0% |
| regime | 47 | 3.2% |
| pf_ex_top | 12 | 0.8% |
| trades | 32 | 2.2% |
| total_return | 1245 | 85.2% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 36051 valutazioni, 89 passate (0.25%) · 2026-08-17 19:19 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 737 | 2.0% |
| win_rate | 56 | 0.2% |
| recovery | 2576 | 7.2% |
| holdout | 150 | 0.4% |
| regime | 3700 | 10.3% |
| total_return | 25785 | 71.7% |
| trades | 2607 | 7.2% |
| pf_ex_top | 351 | 1.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-17 20:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.243%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `tighten` — budget di falsi positivi SFORATO (1.77 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.50 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.46 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.46 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.60 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
