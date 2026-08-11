# Stato sistema (snapshot)
_Generato: 2026-08-11 02:27 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$785.51**
- ultimo heartbeat: 2026-08-11 02:27 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-11 02:18 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## Posizioni aperte
- BTCUSDT: long qty=1.0 @ 100.0 uPnL=0.9079999666715278
- ERAUSDT: long qty=1201.5742783138744 @ 0.06739 uPnL=0.6766147756369123
- HUSDT: long qty=718.7008135049573 @ 0.07931 uPnL=1.8268223948308244

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **0/185 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **0**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000CATUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACTUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AKEUSDT, ALGOUSDT, ALLOUSDT, ALTUSDT, APTUSDT, ARBUSDT, ARCUSDT, ARIAUSDT, ASTERUSDT, ATOMUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BABYUSDT, BANANAS31USDT, BANKUSDT, BBUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BIOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, C98USDT, CAKEUSDT, CCUSDT, CGPTUSDT, CHZUSDT, CLOUSDT, COAIUSDT, COOKIEUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CVXUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, EVAAUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FHEUSDT, FILUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GUAUSDT, GUNUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HMSTRUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, INXUSDT, IOTXUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KGENUSDT, KITEUSDT, LABUSDT, LAUSDT, LDOUSDT, LIGHTUSDT, LINKUSDT, LISTAUSDT, LITUSDT, LTCUSDT, MAGMAUSDT, MEUSDT, MMTUSDT, MONUSDT, MORPHOUSDT, MUBARAKUSDT, MUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, PIPPINUSDT, PNUTUSDT, POLUSDT, PROMUSDT, PTBUSDT, PUMPUSDT, QUSDT, RAVEUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SHELLUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SQDUSDT, STRKUSDT, SUIUSDT, SUSHIUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, THEUSDT, TIAUSDT, TRADOORUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELODROMEUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XANUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZENUSDT, ZROUSDT, 币安人生USDT, 我踏马来了USDT
- aggiornato: 2026-08-11 02:17 UTC

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-11 02:17 UTC · 1480 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Trade chiusi — perché usciamo
- totale: **142** · vinti: 46 (32%) · PnL realizzato: **-229.31**

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 88 | 62% | -387.60 |
| Scale-out (>=1 TP incassato, residuo a BE) | 23 | 16% | +82.12 |
| Time exit (orizzonte scaduto) | 9 | 6% | +63.56 |
| Take profit (fino all'ultimo gradino) | 8 | 6% | +35.57 |
| Kill switch | 8 | 6% | +1.52 |
| ? | 5 | 4% | -25.00 |
| Manuale | 1 | 1% | +0.53 |

- gradini raggiunti (su 137 trade): 0 TP: 106 (77%) · 1 TP: 21 (15%) · 2 TP: 9 (7%) · 3 TP: 1 (1%)

- escursione favorevole (mfe_r, 137 trade): mediana **0.58R** · ≥1R: 36% · ≥1.5R: 26% · ≥3R: 7% · ≥5R: 1%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 133 trade · PF vissuto 0.439 vs 1.544 atteso · mfe mediana 0.58R

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **ok** · 133 trade · correlazione 0.125 · influenza applicata **x1.0**
- la confidenza ordina correttamente gli esiti

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 44 | 27% | -4.20% |
| 60.0–60.0 | 44 | 34% | -0.49% |
| 60.0–75.0 | 45 | 29% | -1.78% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
