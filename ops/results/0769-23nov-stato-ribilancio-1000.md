# 0769-23nov-stato-ribilancio-1000.req

_eseguito: 2026-11-23 04:19 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 47.0s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-23 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-23 04:18 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-23 04:05 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,527.83** su $10,000 (+5.28%) · costi $12.65 · funding pagato $-496.78
- posizioni: 31 long, 28 short · ultimo ribilancio 2026-11-23
- ordini limite: 309 eseguiti su 309 · tutto a mercato sarebbe costato $44.04 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -14.2%, XMRUSDT -7.3%, HYPEUSDT -7.0%, TRXUSDT +7.0%, RENDERUSDT -6.3%, FARTCOINUSDT -5.9%, XPLUSDT -5.6%, XLMUSDT +5.6%, ASTERUSDT -5.5%, BCHUSDT +5.2%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-23 04:10 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,442.08** su $10,000 (+4.42%) · costi $34.21 · funding pagato $-479.17
- posizioni: 30 long, 29 short · ultimo ribilancio 2026-11-23
- ordini limite: 1678 eseguiti su 1685 · tutto a mercato sarebbe costato $97.42 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -13.8%, TRXUSDT +7.3%, XMRUSDT -7.1%, HYPEUSDT -6.8%, 1000SHIBUSDT +6.3%, RENDERUSDT -6.2%, XLMUSDT +5.8%, FARTCOINUSDT -5.7%, XPLUSDT -5.5%, BCHUSDT +5.4%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-23 04:14 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,394.94** su $10,000 (+3.95%) · costi $39.35 · funding pagato $-449.26
- posizioni: 32 long, 26 short · ultimo ribilancio 2026-11-23
- ordini limite: 1766 eseguiti su 1772 · tutto a mercato sarebbe costato $126.79 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -15.8%, XMRUSDT -8.1%, HYPEUSDT -7.8%, RENDERUSDT -7.1%, FARTCOINUSDT -6.6%, TRXUSDT +6.4%, XPLUSDT -6.3%, ETHFIUSDT -5.6%, 1000SHIBUSDT +5.6%, GRASSUSDT -5.0%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-23 03:19 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$10,739.84** su $10,000 (+7.40%) · costi $33.36 · funding pagato $-480.63
- posizioni: 30 long, 29 short · ultimo ribilancio 2026-11-23
- ordini limite: 1573 eseguiti su 1577 · tutto a mercato sarebbe costato $88.10 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -14.3%, XMRUSDT -7.3%, HYPEUSDT -7.0%, TRXUSDT +7.0%, RENDERUSDT -6.4%, 1000SHIBUSDT +6.0%, FARTCOINUSDT -5.9%, XPLUSDT -5.7%, XLMUSDT +5.6%, ASTERUSDT -5.5%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-23 03:24 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-23 03:24 UTC)
- equity: **$975.30** su $1,000.00 (-2.47%) · posizioni 28 long, 25 short · ordini limite eseguiti 791 su 838 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,323.21
- ultima decisione 2026-11-23: 27 ordini, eseguiti a limite 27, a mercato 0; sotto il minimo 31 variazioni (7.0% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 4: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; PIEVERSEUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.87%, LITUSDT +3.15%, PIEVERSEUSDT -1.82%, UAIUSDT -1.45%, IRYSUSDT +1.46%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -7.95% dal massimo
- margine (2026-11-23 03:24 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-23 03:24 UTC): 58 monete, scarto totale 14.5% del conto; oltre il 2%: LITUSDT -3.1%
- ultimo errore (2026-10-24 09:02 UTC): `POST /fapi/v1/order: 400 {"code":-4116,"msg":"ClientOrderId is duplicated."}`

## G1: il demo contro il paper, giorno per giorno
Equity a fine giorno (l'ultimo valore scritto). Dal 6 novembre il demo lavora come un conto ridotto (280 USDT, dall'8 novembre 1.000), senza gli eventi; le fasi di prima sono in /demo_binance/fasi; con i minimi di Binance la differenza con il paper oscilla di più (prova 148).

| giorno | demo | paper G1 | demo meno paper | eventi nel paper |
|---|---|---|---|---|
| 2026-11-09 | +0.88% | +0.78% | +0.10% | +0.00% |
| 2026-11-10 | -0.13% | -0.22% | +0.08% | +0.00% |
| 2026-11-11 | -1.25% | -1.38% | +0.12% | +0.00% |
| 2026-11-12 | +0.08% | +0.37% | -0.29% | +0.00% |
| 2026-11-13 | +1.69% | +2.84% | -1.15% | +0.00% |
| 2026-11-14 | +2.26% | +3.51% | -1.25% | +0.00% |
| 2026-11-15 | -0.27% | -0.58% | +0.31% | +0.00% |
| 2026-11-16 | +1.37% | +1.49% | -0.12% | +0.00% |
| 2026-11-17 | -0.79% | -0.17% | -0.62% | +0.00% |
| 2026-11-18 | -0.99% | -1.50% | +0.51% | +0.00% |
| 2026-11-19 | -1.11% | -1.13% | +0.02% | +0.00% |
| 2026-11-20 | +1.88% | +1.16% | +0.72% | +0.00% |
| 2026-11-21 | -3.13% | -3.07% | -0.06% | +0.00% |
| 2026-11-22 | -2.09% | -1.33% | -0.76% | +0.00% |
| 2026-11-23 | -0.26% | -0.78% | +0.52% | +0.00% |

- dal 2026-11-09 (15 giorni): demo -2.00%, paper -0.22%; differenza media al giorno -0.123%, oscillazione 0.590%

Funding e spese veri, in % dell'equity del giorno (funding: + incassato; spese: + pagate; nel paper dal 6 novembre).

| giorno | funding demo | funding paper | spese demo | spese paper |
|---|---|---|---|---|
| 2026-11-06 | — | +0.069% | — | +0.007% |
| 2026-11-07 | — | +0.112% | — | +0.048% |
| 2026-11-08 | +0.155% | +0.174% | +0.074% | +0.014% |
| 2026-11-09 | +0.198% | +0.231% | +0.008% | +0.010% |
| 2026-11-10 | +0.272% | +0.418% | +0.004% | +0.004% |
| 2026-11-11 | +0.203% | +0.358% | +0.003% | +0.007% |
| 2026-11-12 | +0.194% | +0.121% | +0.003% | +0.004% |
| 2026-11-13 | +0.255% | +0.162% | +0.009% | +0.012% |
| 2026-11-14 | +0.149% | +0.115% | +0.002% | +0.003% |
| 2026-11-15 | +0.179% | +0.168% | +0.010% | +0.010% |
| 2026-11-16 | +0.128% | +0.220% | +0.017% | +0.017% |
| 2026-11-17 | +0.140% | +0.139% | +0.009% | +0.008% |
| 2026-11-18 | +0.073% | +0.108% | +0.001% | +0.002% |
| 2026-11-19 | +0.160% | +0.157% | +0.006% | +0.006% |
| 2026-11-20 | +0.162% | +0.180% | +0.002% | +0.004% |
| 2026-11-21 | +0.149% | +0.142% | +0.004% | +0.005% |
| 2026-11-22 | +0.157% | +0.126% | +0.001% | +0.004% |
| 2026-11-23 | +0.048% | +0.039% | +0.012% | +0.010% |

- sul demo, dal 2026-11-07 (17 giorni): funding incassato +26.80 USDT, commissioni pagate 1.68 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 38, peso 280 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 280
Dal 2026-11-18 00:00 a 2026-11-23 04:19 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 34 monete su 34

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-18 | 43.45 | 0.0122 | 0.0281% | 73% | 27% | 8 |
| 2026-11-19 | 212.92 | 0.0603 | 0.0283% | 61% | 39% | 27 |
| 2026-11-20 | 110.20 | 0.0255 | 0.0232% | 89% | 11% | 21 |
| 2026-11-21 | 182.63 | 0.0441 | 0.0241% | 85% | 15% | 38 |
| 2026-11-22 | 64.15 | 0.0144 | 0.0224% | 92% | 8% | 13 |
| 2026-11-23 | 377.03 | 0.1179 | 0.0313% | 58% | 42% | 43 |
| 6 giorni | 990.37 | 0.2743 | 0.0277% | 70% | 30% | 150 |
- controllo: commissioni dagli incassi 0.2743 USDT, dalle esecuzioni 0.2743 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-18 | +0.7448 | +0.2069 | +0.0892 | +0.1967 | +0.2521 | 52/56 |
| 2026-11-19 | +1.6187 | +0.3048 | +0.4174 | +0.4832 | +0.4132 | 52/57 |
| 2026-11-20 | +1.6724 | +0.2605 | +0.6450 | +0.3815 | +0.3854 | 52/57 |
| 2026-11-21 | +1.4863 | +0.3935 | +0.3560 | +0.3849 | +0.3519 | 51/56 |
| 2026-11-22 | +1.5327 | +0.3770 | +0.4462 | +0.2969 | +0.4126 | 52/57 |
| 2026-11-23 (in corso) | +0.5733 | +0.4682 | +0.0000 | +0.0000 | +0.1051 | —/59 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| INITUSDT | +0.8675 | +0.2652 | +0.3615 | +0.2408 | +0.00

[... 31384 caratteri omessi (testa e coda conservate) ...]

, profit_lock_keep=0.65 |
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
| pf_ex_top | 3 | 0.2% |
| holdout | 1 | 0.1% |
| consistency | 17 | 1.3% |
| recovery | 64 | 4.8% |
| regime | 22 | 1.7% |
| trades | 6 | 0.5% |
| total_return | 1207 | 91.4% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 242 | 0.7% |
| consistency | 589 | 1.7% |
| holdout | 153 | 0.5% |
| recovery | 2737 | 8.1% |
| regime | 2815 | 8.3% |
| trades | 936 | 2.8% |
| total_return | 26463 | 78.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-23 04:03 UTC · coppie validate: **278** · GATE 1 pronto: True
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
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-23 04:19 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (975.30 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -13.79/-13.75 · TRXUSDT +7.27/+7.30 · XMRUSDT -7.06/-7.13 · HYPEUSDT -6.79/-6.69 · 1000SHIBUSDT +6.27/+6.29 · RENDERUSDT -6.15/-6.16
- XLMUSDT +5.84/+5.83 · FARTCOINUSDT -5.71/-5.48 · BCHUSDT +5.38/+5.58 · XPLUSDT -5.45/-5.57 · ASTERUSDT -5.31/-4.91 · ETHFIUSDT -4.87/-5.22
- NEARUSDT -5.18/-4.93 · ADAUSDT +5.09/+5.11 · SANDUSDT +4.83/+4.88 · SEIUSDT +4.49/+4.48 · GRASSUSDT -4.36/-4.05 · TIAUSDT +3.73/+4.30
- GTCUSDT +3.98/+4.27 · VVVUSDT -4.10/-4.00 · APTUSDT +3.89/+3.92 · FETUSDT +3.92/+3.92 · WLDUSDT +3.86/+3.87 · 1000BONKUSDT +3.80/+3.86
- JUPUSDT +3.51/+3.63 · BEATUSDT -3.54/-3.50 · 1000PEPEUSDT +3.45/+3.53 · OPUSDT +3.41/+3.44 · INJUSDT +3.42/+3.43 · TRUMPUSDT +3.30/+3.32
- ERAUSDT +3.29/+3.28 · LITUSDT +3.15/+0.00 · ARIAUSDT -2.45/-3.03 · USELESSUSDT -2.96/-2.68 · BEAMXUSDT -2.91/-2.50 · LSKUSDT +2.49/+2.82
- ONUSDT -2.45/-2.64 · ICNTUSDT -2.42/-1.96 · MAGMAUSDT -2.38/-2.02 · HOTUSDT +2.09/+2.08 · APRUSDT -1.91/-1.74 · BIRBUSDT +1.87/+1.74
- PIEVERSEUSDT -1.82/+0.00 · HUMAUSDT +1.34/+1.48 · IRYSUSDT +1.46/+0.00 · UAIUSDT -1.45/+0.00 · BMTUSDT +1.28/+1.26 · BLESSUSDT -1.19/-1.26
- IDOLUSDT -1.09/-1.22 · BULLAUSDT -1.20/-1.11 · ONEUSDT +1.16/+1.19 · INITUSDT +1.11/+1.11 · SOPHUSDT +1.04/+1.05 · AINUSDT -0.88/-0.80
- EVAAUSDT -0.87/+0.00 · AGTUSDT -0.69/-0.59 · QUSDT -0.57/-0.56 · JCTUSDT -0.43/+0.00 · AKEUSDT +0.26/+0.07
- monete: paper 59, demo 53; esposizione lorda paper 200.0%, demo 190.6%; somma delle differenze 16.5% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 975.30 USDT, paper 10,442.08; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-21 00 | +0.0404% | +0.0251% | +0.0152% | 52/57 |
| 2026-11-21 08 | +0.0365% | +0.0228% | +0.0137% | 51/56 |
| 2026-11-21 16 | +0.0395% | +0.0251% | +0.0144% | 51/56 |
| 2026-11-21 altre | +0.0361% | +0.0722% | -0.0361% | 51/180 |
| 2026-11-22 00 | +0.0387% | +0.0208% | +0.0178% | 51/56 |
| 2026-11-22 08 | +0.0457% | +0.0231% | +0.0226% | 52/57 |
| 2026-11-22 16 | +0.0304% | +0.0144% | +0.0160% | 52/57 |
| 2026-11-22 altre | +0.0423% | +0.0686% | -0.0262% | 51/183 |
| 2026-11-23 00 | +0.0480% | +0.0204% | +0.0276% | 52/57 |
| 2026-11-23 altre | +0.0108% | +0.0190% | -0.0082% | 18/53 |

- regolamento 2026-11-23 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): INITUSDT +0.0145/+0.0013 · BULLAUSDT +0.0056/+0.0016 · ONUSDT +0.0033/— · ARIAUSDT +0.0029/— · SANDUSDT +0.0027/+0.0015 · GTCUSDT +0.0026/+0.0013 · 1000SHIBUSDT +0.0023/+0.0011 · LSKUSDT +0.0018/+0.0010 · BCHUSDT +0.0017/+0.0012 · SEIUSDT -0.0005/+0.0013 · XLMUSDT -0.0007/+0.0008 · 1000PEPEUSDT +0.0008/+0.0006
```
