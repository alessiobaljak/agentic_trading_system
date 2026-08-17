# Stato sistema (snapshot)
_Generato: 2026-08-17 07:16 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-17 07:14 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-17 07:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/180 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANKUSDT, BARDUSDT, BCHUSDT, BEATUSDT, BELUSDT, BICOUSDT, BIGTIMEUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CCUSDT, CHZUSDT, COOKIEUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DIAUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, DUSKUSDT, DYDXUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, EVAAUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JASMYUSDT, JCTUSDT, JTOUSDT, KAITOUSDT, KASUSDT, KOMAUSDT, LABUSDT, LDOUSDT, LIGHTUSDT, LINKUSDT, LITUSDT, LTCUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, ONUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, QUSDT, RAREUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SANDUSDT, SEIUSDT, SFPUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOPHUSDT, SPORTFUNUSDT, STABLEUSDT, STBLUSDT, STRKUSDT, SUIUSDT, SYRUPUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TOWNSUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZEREBROUSDT, ZROUSDT, 币安人生USDT
- aggiornato: 2026-08-17 07:15 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-17 06:34 UTC · 1440 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1440 valutazioni, 0 passate (0.00%) · 2026-08-17 06:34 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 5 | 0.3% |
| regime | 45 | 3.1% |
| trades | 32 | 2.2% |
| total_return | 1232 | 85.6% |
| consistency | 18 | 1.2% |
| recovery | 96 | 6.7% |
| win_rate | 1 | 0.1% |
| pf | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **7** — sono i semi delle mutazioni del run successivo

**strategie generate** — 33485 valutazioni, 68 passate (0.20%) · 2026-08-17 07:15 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 147 | 0.4% |
| regime | 3437 | 10.3% |
| trades | 1622 | 4.9% |
| total_return | 24646 | 73.8% |
| consistency | 695 | 2.1% |
| recovery | 2422 | 7.2% |
| win_rate | 50 | 0.1% |
| pf_ex_top | 398 | 1.2% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-17 07:01 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.245%**
- nessun parametro modificato: il gate gira coi valori di partenza

**Ultime decisioni:**

- `tighten` — budget di falsi positivi SFORATO (1.66 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.66 coppie fortunate attese al giorno, tetto 1) e nessuna mia modifica da disfare: il tasso viene dalla ricerca, si riducono le estrazioni
- `revert` — budget SFORATO (1.66 coppie fortunate attese al giorno contro un tetto di 1): disfo le mie modifiche (GATE_WIN_RATE_FLOOR) e rimisuro. Prima si annulla la propria mossa, poi semmai si accusa il mondo
- `tighten` — budget di falsi positivi SFORATO (1.64 coppie fortunate attese al giorno, tetto 1): non si allenta nulla, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.64 coppie fortunate attese al giorno, tetto 1): non si allenta nulla, si riducono le estrazioni

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
