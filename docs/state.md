# Stato sistema (snapshot)
_Generato: 2026-08-16 20:38 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-08-16 20:38 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-16 20:33 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/181 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 1000BONKUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACUUSDT, ADAUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANKUSDT, BARDUSDT, BCHUSDT, BEATUSDT, BELUSDT, BERAUSDT, BICOUSDT, BIGTIMEUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CCUSDT, CETUSUSDT, COOKIEUSDT, COTIUSDT, COWUSDT, CROSSUSDT, CRVUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOLOUSDT, DOTUSDT, DUSKUSDT, EDENUSDT, ENAUSDT, ENSOUSDT, EPICUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GMTUSDT, GPSUSDT, GUAUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOLOUSDT, HOMEUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, JCTUSDT, JSTUSDT, JTOUSDT, KAITOUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LIGHTUSDT, LINKUSDT, LITUSDT, LTCUSDT, MMTUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NILUSDT, NOMUSDT, NOTUSDT, NXPCUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, ONUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIEVERSEUSDT, PIXELUSDT, PLUMEUSDT, PORTALUSDT, PROMUSDT, PUMPUSDT, QUSDT, RAREUSDT, REDUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, RONINUSDT, RVNUSDT, SANDUSDT, SEIUSDT, SFPUSDT, SKYAIUSDT, SOLUSDT, SPORTFUNUSDT, STABLEUSDT, STORJUSDT, SUIUSDT, SYRUPUSDT, TAGUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TOWNSUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZEREBROUSDT, ZKUSDT, 币安人生USDT
- aggiornato: 2026-08-16 19:15 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-16 18:37 UTC · 1448 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1448 valutazioni, 0 passate (0.00%) · 2026-08-16 18:37 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 100 | 6.9% |
| win_rate | 1 | 0.1% |
| total_return | 1227 | 84.7% |
| trades | 34 | 2.3% |
| holdout | 7 | 0.5% |
| consistency | 19 | 1.3% |
| regime | 50 | 3.5% |
| pf_ex_top | 10 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **7** — sono i semi delle mutazioni del run successivo

**strategie generate** — 31675 valutazioni, 80 passate (0.25%) · 2026-08-16 19:15 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 2034 | 6.4% |
| win_rate | 7 | 0.0% |
| total_return | 23635 | 74.8% |
| trades | 1704 | 5.4% |
| holdout | 159 | 0.5% |
| consistency | 606 | 1.9% |
| regime | 3147 | 10.0% |
| pf_ex_top | 303 | 1.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-08-16 20:03 UTC · coppie validate: **0** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.241%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.398537 |

**Ultime decisioni:**

- `tighten` — budget di falsi positivi SFORATO (1.55 coppie fortunate attese al giorno, tetto 1): non si allenta nulla, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.42 coppie fortunate attese al giorno, tetto 1): non si allenta nulla, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.46 coppie fortunate attese al giorno, tetto 1): non si allenta nulla, si riducono le estrazioni
- `tighten` — budget di falsi positivi SFORATO (1.46 coppie fortunate attese al giorno, tetto 1): non si allenta nulla, si riducono le estrazioni
- `none GATE_MIN_PF_EX_TOP 1.0 → None` — le candidate piu' vicine al passaggio (29) sono fermate da GATE_MIN_PF_EX_TOP, che e' gia' al pavimento (1): sotto il pareggio senza i colpi migliori si valida la fortuna. Non si scende oltre: quello che manca non e' una soglia piu' bassa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
