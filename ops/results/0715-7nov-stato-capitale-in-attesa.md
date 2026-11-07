# 0715-7nov-stato-capitale-in-attesa.req

_eseguito: 2026-11-07 05:50 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 6.6s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-07 05:50 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-07 05:48 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-07 05:45 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,160.25** su $10,000 (+1.60%) · costi $6.38 · funding pagato $-140.78
- posizioni: 26 long, 25 short · ultimo ribilancio 2026-11-02
- ordini limite: 115 eseguiti su 115 · tutto a mercato sarebbe costato $22.22 · in attesa del controllo dell'ora: 0
- pesi maggiori: BTCUSDT -11.9%, ASTERUSDT -9.8%, WLFIUSDT -9.1%, TRXUSDT +9.0%, XLMUSDT +7.7%, XRPUSDT -7.6%, POLUSDT +7.2%, 1000SHIBUSDT -6.7%, XMRUSDT -6.7%, ALGOUSDT +6.6%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-07 05:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,592.92** su $10,000 (+5.93%) · costi $21.42 · funding pagato $-164.52
- posizioni: 27 long, 27 short · ultimo ribilancio 2026-11-07
- ordini limite: 764 eseguiti su 766 · tutto a mercato sarebbe costato $56.07 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -11.1%, BTCUSDT -9.5%, TRXUSDT +8.8%, WLFIUSDT -7.3%, XRPUSDT -6.9%, POLUSDT +6.6%, XMRUSDT -6.4%, ALGOUSDT +5.8%, SEIUSDT +5.2%, HYPEUSDT -5.2%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-07 05:10 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,752.15** su $10,000 (+7.52%) · costi $21.11 · funding pagato $-148.89
- posizioni: 26 long, 23 short · ultimo ribilancio 2026-11-07
- ordini limite: 834 eseguiti su 836 · tutto a mercato sarebbe costato $72.20 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -10.9%, XMRUSDT -9.5%, BNBUSDT +9.3%, TRXUSDT +8.5%, HYPEUSDT -7.7%, TAOUSDT -7.0%, XLMUSDT +6.9%, MUBARAKUSDT -6.2%, FARTCOINUSDT -6.2%, BCHUSDT +5.9%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-07 05:14 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$10,890.60** su $10,000 (+8.91%) · costi $19.90 · funding pagato $-157.55
- posizioni: 27 long, 27 short · ultimo ribilancio 2026-11-07
- ordini limite: 655 eseguiti su 658 · tutto a mercato sarebbe costato $44.32 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -11.2%, BTCUSDT -9.7%, TRXUSDT +8.6%, WLFIUSDT -7.4%, XRPUSDT -7.0%, XMRUSDT -6.5%, POLUSDT +6.5%, ALGOUSDT +5.7%, HYPEUSDT -5.3%, SEIUSDT +5.2%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-07 04:55 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-07 05:03 UTC)
- equity: **$267.05** su $280.00 (-4.63%) · posizioni 27 long, 25 short · ordini limite eseguiti 531 su 560 · in attesa 0
- conto ridotto: il demo lavora come un conto di $280 (prova 148, il capitale del proprietario); valore vero del conto demo $5,347.82
- ultima decisione 2026-11-07: 5 ordini, eseguiti a limite 5, a mercato 0; sotto il minimo 50 variazioni (19.2% del conto); monete che sul demo non ci sono: ICPUSDT
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): ICPUSDT -3.90%
- stop sul conto (−35% dal massimo): massimo $280.00, si chiude tutto sotto $182.00; ora -4.63% dal massimo
- margine (2026-11-07 05:03 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-07 05:03 UTC): 54 monete, scarto totale 23.2% del conto; oltre il 2%: BTCUSDT -7.5%, ICPUSDT +3.9%
- ultimo errore (2026-10-24 09:02 UTC): `POST /fapi/v1/order: 400 {"code":-4116,"msg":"ClientOrderId is duplicated."}`

## G1: il demo contro il paper, giorno per giorno
Equity a fine giorno (l'ultimo valore scritto). Dal 6 novembre il demo lavora come un conto ridotto (280 USDT, dall'8 novembre 1.000), senza gli eventi; le fasi di prima sono in /demo_binance/fasi; con i minimi di Binance la differenza con il paper oscilla di più (prova 148).

| giorno | demo | paper G1 | demo meno paper | eventi nel paper |
|---|---|---|---|---|
| 2026-11-07 | -0.32% | -0.40% | +0.09% | +0.00% |

- dal 2026-11-07 (1 giorni): demo -0.32%, paper -0.40%; differenza media al giorno +0.085%

Funding e spese veri, in % dell'equity del giorno (funding: + incassato; spese: + pagate; nel paper dal 6 novembre).

| giorno | funding demo | funding paper | spese demo | spese paper |
|---|---|---|---|---|
| 2026-11-06 | +0.781% | +0.069% | +1.023% | +0.007% |
| 2026-11-07 | +0.039% | +0.035% | +0.004% | +0.048% |

- sul demo, dal 2026-11-06 (2 giorni): funding incassato +2.20 USDT, commissioni pagate 2.75 USDT

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
| STXUSDT | gen_00e50229 | 3 | 1.339 | 111% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_5032e290 | 3 | 1.594 | 111% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_e6dd479a | 3 | 1.594 | 111% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_331ef268 | 3 | 1.785 | 107% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_871647b8 | 4 | 2.221 | 107% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PTBUSDT | gen_684d7623 | 3 

[... 25881 caratteri omessi (testa e coda conservate) ...]

_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
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
| consistency | 17 | 1.3% |
| pf_ex_top | 3 | 0.2% |
| recovery | 64 | 4.8% |
| trades | 6 | 0.5% |
| total_return | 1207 | 91.4% |
| holdout | 1 | 0.1% |
| regime | 22 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 589 | 1.7% |
| pf_ex_top | 242 | 0.7% |
| recovery | 2737 | 8.1% |
| trades | 936 | 2.8% |
| total_return | 26463 | 78.0% |
| holdout | 153 | 0.5% |
| regime | 2815 | 8.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-07 05:04 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: drift · 363 trade · PF vissuto 0.723 vs 2.02 atteso · mfe mediana 0.66R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.72 vs 2.02 atteso · mfe mediana 0.66R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| TAUSDT|gen_01fbe76f | drift | 10 | 0.509 / 1.711 | PF 0.51 vs 1.71 atteso · mfe mediana 0.87R < primo TP 1.50R |
| USELESSUSDT|gen_e09c5203 | drift | 9 | 0.628 / 1.636 | PF 0.63 vs 1.64 atteso · mfe mediana 0.48R < primo TP 2.00R |
| MYXUSDT|gen_8931b93c | drift | 9 | 0.26 / 1.583 | PF 0.26 vs 1.58 atteso · mfe mediana 0.24R < primo TP 1.50R |
| TRUMPUSDT|gen_d16d1d02 | drift | 8 | 1.003 / 1.591 | mfe mediana 1.08R < primo TP 2.00R |
| STXUSDT|gen_0aa0d29c | watch | 7 | 0.566 / 1.663 | PF 0.57 vs 1.66 atteso · mfe mediana 0.51R < primo TP 1.00R |
| PTBUSDT|gen_684d7623 | watch | 7 | 0.591 / 1.871 | PF 0.59 vs 1.87 atteso · mfe mediana 0.50R < primo TP 1.00R |
| QUSDT|gen_5905e08d | watch | 7 | 0.628 / 1.856 | PF 0.63 vs 1.86 atteso · mfe mediana 0.80R < primo TP 1.50R |
| BANKUSDT|gen_7100bb59 | watch | 6 | 0.475 / 1.938 | PF 0.47 vs 1.94 atteso · mfe mediana 0.45R < primo TP 0.75R |
| HEMIUSDT|gen_acea368d | watch | 6 | 1.303 / 1.784 | mfe mediana 0.95R < primo TP 1.50R |
| XPINUSDT|gen_f311acf9 | watch | 5 | 0.029 / 3.282 | PF 0.03 vs 3.28 atteso · mfe mediana 0.40R < primo TP 1.00R |
| GPSUSDT|gen_871647b8 | watch | 5 | 0.402 / 1.555 | PF 0.40 vs 1.55 atteso · mfe mediana 0.62R < primo TP 2.00R |
| JTOUSDT|gen_94062d5f | watch | 4 | 0.238 / 1.351 | PF 0.24 vs 1.35 atteso · mfe mediana 0.55R < primo TP 1.00R |
| HUMAUSDT|gen_da39a23a | watch | 4 | 1.618 / 2.258 | mfe mediana 0.70R < primo TP 1.00R |
| SYRUPUSDT|gen_f3b97917 | watch | 4 | 0.662 / 2.064 | PF 0.66 vs 2.06 atteso · mfe mediana 1.06R < primo TP 2.00R |
| DEXEUSDT|gen_3d4be8c7 | watch | 4 | 1.299 / 1.545 | mfe mediana 0.89R < primo TP 1.50R |
| SYRUPUSDT|gen_4c6df481 | watch | 4 | 0.058 / 1.544 | PF 0.06 vs 1.54 atteso · mfe mediana 0.79R < primo TP 2.00R |
| ZECUSDT|gen_e6ddc613 | watch | 4 | 0.557 / 1.46 | PF 0.56 vs 1.46 atteso · mfe mediana 0.60R < primo TP 1.00R |
| HOMEUSDT|gen_467d9ee2 | watch | 4 | 0.206 / 1.617 | PF 0.21 vs 1.62 atteso · mfe mediana 0.58R < primo TP 1.00R |
| HYPEUSDT|gen_f19b67e8 | watch | 4 | 0.237 / 1.624 | PF 0.24 vs 1.62 atteso · mfe mediana 0.51R < primo TP 1.00R |
| BMTUSDT|gen_be64073c | watch | 4 | 0.142 / 2.843 | PF 0.14 vs 2.84 atteso · mfe mediana 0.51R < primo TP 1.50R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_f311acf9** (4 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 363 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (363 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 121 | 57% | -0.05% |
| 60.0–60.0 | 121 | 53% | -0.54% |
| 60.0–60.0 | 121 | 60% | -0.14% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
