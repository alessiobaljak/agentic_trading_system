# Stato sistema (snapshot)
_Generato: 2026-08-10 22:56 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$785.51**
- ultimo heartbeat: 2026-08-10 22:56 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-08-10 22:48 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## Posizioni aperte
- BTCUSDT: long qty=1.0 @ 100.0 uPnL=0.9079999666715278
- ERAUSDT: long qty=1201.5742783138744 @ 0.06739 uPnL=0.4837799729603645
- HUSDT: long qty=718.7008135049573 @ 0.07931 uPnL=1.9283303200624926

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **1/185 crypto (0%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **1**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000CATUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 4USDT, AAVEUSDT, ACEUSDT, ACTUSDT, ADAUSDT, AEROUSDT, AIOUSDT, AIXBTUSDT, AKEUSDT, ALGOUSDT, ALLOUSDT, ALTUSDT, APTUSDT, ARBUSDT, ARCUSDT, ASTERUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BABYUSDT, BANANAS31USDT, BANKUSDT, BBUSDT, BCHUSDT, BEATUSDT, BICOUSDT, BIOUSDT, BLESSUSDT, BLUAIUSDT, BMTUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BTCUSDT, BTRUSDT, BULLAUSDT, C98USDT, CATIUSDT, CCUSDT, CGPTUSDT, CHZUSDT, CLOUSDT, COAIUSDT, COOKIEUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CYSUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EIGENUSDT, ENAUSDT, EPICUSDT, ERAUSDT, ESPORTSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FHEUSDT, FILUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GUAUSDT, GUNUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HMSTRUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, INXUSDT, IOTXUSDT, JOEUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KERNELUSDT, KGENUSDT, KOMAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LISTAUSDT, LITUSDT, LTCUSDT, MAGMAUSDT, MAVUSDT, MEMEUSDT, MEUSDT, MMTUSDT, MONUSDT, MOODENGUSDT, MORPHOUSDT, MUBARAKUSDT, MUSDT, MYXUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONUSDT, OPUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PIPPINUSDT, PNUTUSDT, POLUSDT, PTBUSDT, PUMPUSDT, QUSDT, RAVEUSDT, RENDERUSDT, RIFUSDT, RIVERUSDT, SAGAUSDT, SEIUSDT, SHELLUSDT, SIRENUSDT, SKYAIUSDT, SOLUSDT, SOLVUSDT, SQDUSDT, STOUSDT, STRKUSDT, SUIUSDT, SUSHIUSDT, SYNUSDT, TAKEUSDT, TAOUSDT, THEUSDT, TIAUSDT, TRADOORUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, TURBOUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELODROMEUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, XANUSDT, XLMUSDT, XMRUSDT, XNYUSDT, XPINUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZBTUSDT, ZECUSDT, ZENUSDT, ZROUSDT, 币安人生USDT, 我踏马来了USDT
- aggiornato: 2026-08-10 18:54 UTC

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| SOLUSDT | breakout | 3 | 1.2 | 30% | rr=2.5 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-08-10 17:27 UTC · 1480 coppie valutate, 0 passate in questo run_

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
