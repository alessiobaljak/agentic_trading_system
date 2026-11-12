# 0735-12nov-stato-ribilancio-1000.req

_eseguito: 2026-11-12 00:24 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 8.1s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-12 00:24 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-12 00:24 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-11 23:31 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$9,936.07** su $10,000 (-0.64%) · costi $8.88 · funding pagato $-314.99
- posizioni: 30 long, 25 short · ultimo ribilancio 2026-11-09
- ordini limite: 179 eseguiti su 179 · tutto a mercato sarebbe costato $30.86 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -10.4%, WLFIUSDT -9.3%, TRXUSDT +8.0%, XRPUSDT -8.0%, XMRUSDT -8.0%, XLMUSDT +6.6%, HYPEUSDT -6.1%, POLUSDT +6.1%, DOTUSDT +6.1%, ATOMUSDT +6.0%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-12 00:05 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,398.55** su $10,000 (+3.99%) · costi $25.27 · funding pagato $-298.51
- posizioni: 26 long, 28 short · ultimo ribilancio 2026-11-12
- ordini limite: 994 eseguiti su 998 · tutto a mercato sarebbe costato $67.07 · in attesa del controllo dell'ora: 55
- pesi maggiori: ASTERUSDT -9.3%, TRXUSDT +8.7%, WLFIUSDT -7.8%, XRPUSDT -7.2%, BCHUSDT +7.1%, POLUSDT +7.0%, XMRUSDT -6.7%, ATOMUSDT +6.6%, TAOUSDT -5.9%, SEIUSDT +5.9%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-12 00:09 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,581.37** su $10,000 (+5.81%) · costi $26.44 · funding pagato $-274.49
- posizioni: 28 long, 24 short · ultimo ribilancio 2026-11-12
- ordini limite: 1063 eseguiti su 1065 · tutto a mercato sarebbe costato $89.19 · in attesa del controllo dell'ora: 54
- pesi maggiori: ASTERUSDT -11.3%, WLFIUSDT -9.5%, XMRUSDT -8.2%, TRXUSDT +7.5%, TAOUSDT -7.2%, HYPEUSDT -6.9%, XLMUSDT +6.7%, PENDLEUSDT -6.2%, BCHUSDT +6.1%, POLUSDT +6.0%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-12 00:13 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$10,692.46** su $10,000 (+6.92%) · costi $23.50 · funding pagato $-296.72
- posizioni: 26 long, 28 short · ultimo ribilancio 2026-11-12
- ordini limite: 887 eseguiti su 890 · tutto a mercato sarebbe costato $55.65 · in attesa del controllo dell'ora: 55
- pesi maggiori: TRXUSDT +9.0%, ASTERUSDT -8.9%, WLFIUSDT -7.5%, BCHUSDT +7.4%, POLUSDT +7.2%, XRPUSDT -6.9%, ATOMUSDT +6.8%, XMRUSDT -6.4%, SEIUSDT +6.1%, SANDUSDT +5.9%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-12 00:18 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-11 23:47 UTC)
- equity: **$990.11** su $1,000.00 (-0.99%) · posizioni 26 long, 25 short · ordini limite eseguiti 607 su 642 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,338.02
- ultima decisione 2026-11-12: 10 ordini; sotto il minimo 43 variazioni (10.4% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 1: 龙虾USDT POST /fapi/v1/order: 400 {"code":-1121,"msg":"Invalid symbol."}
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): 龙虾USDT -1.86%, IRYSUSDT +0.42%
- stop sul conto: si chiude tutto sotto $658.84 (il più alto fra −35% dal massimo, $1,013.60, e il 65% del capitale di partenza); ora -2.32% dal massimo
- margine (2026-11-11 23:47 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-11 23:47 UTC): 54 monete, scarto totale 12.2% del conto; nessuna moneta oltre il 2%
- ultimo errore (2026-10-24 09:02 UTC): `POST /fapi/v1/order: 400 {"code":-4116,"msg":"ClientOrderId is duplicated."}`

## G1: il demo contro il paper, giorno per giorno
Equity a fine giorno (l'ultimo valore scritto). Dal 6 novembre il demo lavora come un conto ridotto (280 USDT, dall'8 novembre 1.000), senza gli eventi; le fasi di prima sono in /demo_binance/fasi; con i minimi di Binance la differenza con il paper oscilla di più (prova 148).

| giorno | demo | paper G1 | demo meno paper | eventi nel paper |
|---|---|---|---|---|
| 2026-11-09 | +0.88% | +0.78% | +0.10% | +0.00% |
| 2026-11-10 | -0.13% | -0.22% | +0.08% | +0.00% |
| 2026-11-11 | -1.25% | -1.38% | +0.12% | +0.00% |

- dal 2026-11-09 (3 giorni): demo -0.51%, paper -0.82%; differenza media al giorno +0.103%, oscillazione 0.021%

Funding e spese veri, in % dell'equity del giorno (funding: + incassato; spese: + pagate; nel paper dal 6 novembre).

| giorno | funding demo | funding paper | spese demo | spese paper |
|---|---|---|---|---|
| 2026-11-06 | — | +0.069% | — | +0.007% |
| 2026-11-07 | — | +0.112% | — | +0.048% |
| 2026-11-08 | +0.155% | +0.174% | +0.074% | +0.014% |
| 2026-11-09 | +0.198% | +0.231% | +0.008% | +0.010% |
| 2026-11-10 | +0.272% | +0.418% | +0.004% | +0.004% |
| 2026-11-11 | +0.203% | +0.358% | +0.003% | +0.007% |
| 2026-11-12 | — | +0.020% | — | +0.003% |

- sul demo, dal 2026-11-07 (5 giorni): funding incassato +8.64 USDT, commissioni pagate 0.89 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- spento: nessuno stato scritto (il bot non lo ha ancora fatto girare)

## Ultima decisione
- esito: **🟢 APERTA** (2026-10-21 07:02 UTC)
- motivo: aperta SYRUPUSDT long (gen_4c6df481), ordine limite riempito a 0.20076
- asset valutati: 80 · segnali: 1 · miglior segnale SYRUPUSDT gen_4c6df481 (conf. 55.6/soglia 30)

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **80/200 crypto (40%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **249**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, AKEUSDT, ALGOUSDT, ALTUSDT, APEUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ARUSDT, ARXUSDT, ASTERUSDT, ATOMUSDT, AVAUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, AZTECUSDT, BANKUSDT, BASEDUSDT, BATUSDT, BCHUSDT, BEAMXUSDT, BEATUSDT, BILLUSDT, BLURUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BTWUSDT, CAKEUSDT, CAPUSDT, CCUSDT, CFXUSDT, CHIPUSDT, CHZUSDT, CKBUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTKUSDT, CTRUSDT, CTSIUSDT, CTUSDT, CYBERUSDT, DASHUSDT, DATAIPUSDT, DODOXUSDT, DOGEUSDT, DOSUSDT, DOTUSDT, DUSKUSDT, EIGENUSDT, ENAUSDT, ERAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, GALAUSDT, GPSUSDT, GRAMUSDT, GRASSUSDT, GTCUSDT, GWEIUSDT, HBARUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INITUSDT, INJUSDT, IOUSDT, JASMYUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, KAITOUSDT, KGENUSDT, LABUSDT, LDOUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LUMIAUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANTAUSDT, MARSCOINUSDT, MEGAUSDT, METISUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, OGNUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPNUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, RIVERUSDT, RLCUSDT, RSRUSDT, RVNUSDT, SAFEUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SFPUSDT, SKLUSDT, SKYUSDT, SOLUSDT, SOMIUSDT, SOONUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRUTHUSDT, TRXUSDT, UNIUSDT, USELESSUSDT, USUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-13 18:40 UTC

### Salute del registro

- composizione: **0 base** · **2435 generate** (di cui 2100 con almeno una conferma)
- occupazione: 2435/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| QUSDT | gen_f1e7ff62 | 3 | 2.383 | 192% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_0aa0d29c | 3 | 1.663 | 148% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| RUNEUSDT | gen_434083c5 | 3 | 1.701 | 146% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_d2a9f9ab | 3 | 3.318 | 138% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| STXUSDT | gen_afa705ab | 3 | 1.576 | 136% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| CAKEUSDT | gen_b4111d27 | 3 | 1.649 | 120% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| JTOUSDT | gen_94062d5f | 3 | 1.351 | 116% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT 

[... 26469 caratteri omessi (testa e coda conservate) ...]

 MYXUSDT | gen_8931b93c | 3 | 1.583 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| OPENUSDT | gen_46f0717f | 3 | 2.477 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_7b4a474b | 3 | 2.213 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PENGUUSDT | gen_5b9ed454 | 3 | 2.232 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PHAUSDT | gen_bd109329 | 3 | 1.725 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PTBUSDT | gen_630b2a40 | 3 | 2.368 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PTBUSDT | gen_73033c73 | 3 | 2.067 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_13cc61f2 | 3 | 3.302 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_5905e08d | 3 | 1.856 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_603e7c77 | 3 | 2.565 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_f9f8d28d | 3 | 1.783 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| RENDERUSDT | gen_fe8925b6 | 3 | 2.027 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_4e1e404e | 3 | 1.445 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SAHARAUSDT | gen_9d07c7b7 | 3 | 1.618 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_49c2f657 | 3 | 2.112 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_b0e86c70 | 3 | 2.477 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c08c5114 | 3 | 2.962 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c647ead7 | 3 | 2.023 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TUTUSDT | gen_17b6b561 | 3 | 1.602 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_77900c80 | 3 | 3.014 | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| USELESSUSDT | gen_96c1ed1b | 3 | 2.06 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| USELESSUSDT | gen_e09c5203 | 3 | 1.636 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| VELVETUSDT | gen_fa304106 | 3 | 1.537 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| XMRUSDT | gen_5642c3d7 | 3 | 1.624 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XVGUSDT | gen_51d26c6b | 3 | 1.711 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 6 | 0.5% |
| recovery | 64 | 4.8% |
| regime | 22 | 1.7% |
| holdout | 1 | 0.1% |
| total_return | 1207 | 91.4% |
| consistency | 17 | 1.3% |
| pf_ex_top | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 936 | 2.8% |
| recovery | 2737 | 8.1% |
| regime | 2815 | 8.3% |
| consistency | 589 | 1.7% |
| total_return | 26463 | 78.0% |
| holdout | 153 | 0.5% |
| pf_ex_top | 242 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-12 00:01 UTC · coppie validate: **278** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.320%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma

## Trade chiusi — perché usciamo
- totale: **784** · vinti: 433 (55%) · PnL realizzato: **-182.75**
- confronto col mercato: noi -18.28% vs BTC buy&hold +7.54% nello stesso periodo → **sotto** il mercato

- costi: **92.60 USDT** su 784 trade (0.12/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 52.35 · spread 39.87 · funding +0.38
  - lordo -90.15 → netto -182.75 · **break-even 11.33%** dell'equity
  - piu' costose: UBUSDT 4.45 · DEXEUSDT 4.26 · SYRUPUSDT 3.79 · HEMIUSDT 2.92 · XPINUSDT 2.90
  - ⚠️ Costi operativi elevati: servono 11.33% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 344 | 44% | -645.04 |
| Trailing stop | 339 | 43% | +254.72 |
| Scale-out (>=1 TP incassato, residuo a BE) | 74 | 9% | +133.32 |
| Time exit (orizzonte scaduto) | 16 | 2% | +37.10 |
| Take profit (fino all'ultimo gradino) | 7 | 1% | +36.61 |
| Kill switch | 4 | 1% | +0.55 |

- gradini raggiunti (su 784 trade): 0 TP: 695 (89%) · 1 TP: 69 (9%) · 2 TP: 13 (2%) · 3 TP: 7 (1%)

- **drawdown di portafoglio: 192.12 USDT** (ritorno -182.75 · recovery -0.95) · max 15 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.95
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 784 trade): mediana **0.76R** · ≥1R: 33% · ≥1.5R: 13% · ≥3R: 3% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 238 trade · PF vissuto 0.695 vs 2.02 atteso · mfe mediana 0.6R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.70 vs 2.02 atteso · mfe mediana 0.60R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| TAUSDT|gen_01fbe76f | drift | 8 | 0.558 / 1.711 | PF 0.56 vs 1.71 atteso · mfe mediana 0.92R < primo TP 1.50R |
| TRUMPUSDT|gen_d16d1d02 | drift | 8 | 1.003 / 1.591 | mfe mediana 1.08R < primo TP 2.00R |
| MYXUSDT|gen_8931b93c | drift | 8 | 0.19 / 1.583 | PF 0.19 vs 1.58 atteso · mfe mediana 0.24R < primo TP 1.50R |
| QUSDT|gen_5905e08d | watch | 7 | 0.628 / 1.856 | PF 0.63 vs 1.86 atteso · mfe mediana 0.80R < primo TP 1.50R |
| PTBUSDT|gen_684d7623 | watch | 6 | 0.367 / 1.871 | PF 0.37 vs 1.87 atteso · mfe mediana 0.50R < primo TP 1.00R |
| USELESSUSDT|gen_e09c5203 | watch | 5 | 0.585 / 1.636 | PF 0.59 vs 1.64 atteso · mfe mediana 0.48R < primo TP 2.00R |
| BANKUSDT|gen_7100bb59 | watch | 5 | 1.236 / 1.938 | mfe mediana 0.45R < primo TP 0.75R |
| HEMIUSDT|gen_acea368d | watch | 4 | 1.998 / 1.784 | mfe mediana 0.95R < primo TP 1.50R |
| SYRUPUSDT|gen_f3b97917 | watch | 4 | 0.662 / 2.064 | PF 0.66 vs 2.06 atteso · mfe mediana 1.06R < primo TP 2.00R |
| HOMEUSDT|gen_467d9ee2 | watch | 4 | 0.206 / 1.617 | PF 0.21 vs 1.62 atteso · mfe mediana 0.58R < primo TP 1.00R |
| JTOUSDT|gen_94062d5f | watch | 4 | 0.238 / 1.351 | PF 0.24 vs 1.35 atteso · mfe mediana 0.55R < primo TP 1.00R |
| XPINUSDT|gen_f311acf9 | watch | 4 | 0.0 / 3.282 | PF 0.00 vs 3.28 atteso · mfe mediana 0.40R < primo TP 1.00R |
| BMTUSDT|gen_be64073c | watch | 4 | 0.142 / 2.843 | PF 0.14 vs 2.84 atteso · mfe mediana 0.51R < primo TP 1.50R |
| EIGENUSDT|gen_1b7827f3 | watch | 3 | 0.58 / 1.475 | PF 0.58 vs 1.48 atteso · mfe mediana 0.84R < primo TP 1.50R |
| UBUSDT|gen_92b77c39 | watch | 3 | 0.572 / 1.502 | PF 0.57 vs 1.50 atteso · mfe mediana 1.01R < primo TP 2.00R |
| STXUSDT|gen_0aa0d29c | watch | 3 | 0.0 / 1.663 | PF 0.00 vs 1.66 atteso · mfe mediana 0.15R < primo TP 1.00R |
| SCRUSDT|gen_0e030446 | watch | 3 | 0.344 / 1.851 | PF 0.34 vs 1.85 atteso |
| SAHARAUSDT|gen_c934a6f7 | watch | 3 | 99.0 / 1.687 | mfe mediana 0.52R < primo TP 0.75R |
| IDOLUSDT|gen_5ad54558 | watch | 3 | 0.741 / 2.23 | PF 0.74 vs 2.23 atteso · mfe mediana 0.82R < primo TP 1.50R |
| GPSUSDT|gen_871647b8 | watch | 3 | 0.526 / 1.555 | PF 0.53 vs 1.55 atteso · mfe mediana 0.62R < primo TP 2.00R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_f311acf9** (4 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 238 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (238 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 79 | 57% | +0.02% |
| 60.0–60.0 | 79 | 58% | -0.11% |
| 60.0–60.0 | 80 | 50% | -0.76% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
