# 0765-21nov-stato-ribilancio-1000.req

_eseguito: 2026-11-21 04:20 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 59.0s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-21 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-21 04:19 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-21 03:43 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,721.97** su $10,000 (+7.22%) · costi $11.30 · funding pagato $-470.30
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-16
- ordini limite: 245 eseguiti su 245 · tutto a mercato sarebbe costato $39.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.2%, TRXUSDT +8.2%, XMRUSDT -7.7%, HYPEUSDT -7.4%, RENDERUSDT -6.7%, XLMUSDT +6.5%, ASTERUSDT -6.3%, POLUSDT +6.2%, BCHUSDT +6.0%, JTOUSDT -5.9%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-21 04:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,966.34** su $10,000 (+9.66%) · costi $32.75 · funding pagato $-451.33
- posizioni: 26 long, 30 short · ultimo ribilancio 2026-11-21
- ordini limite: 1558 eseguiti su 1565 · tutto a mercato sarebbe costato $92.29 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.6%, TRXUSDT +8.3%, 1000SHIBUSDT +7.1%, XMRUSDT -7.0%, XLMUSDT +6.6%, HYPEUSDT -6.3%, BCHUSDT +6.1%, ADAUSDT +5.7%, RENDERUSDT -5.6%, JTOUSDT -5.5%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-21 04:09 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,973.07** su $10,000 (+9.73%) · costi $37.84 · funding pagato $-422.82
- posizioni: 30 long, 27 short · ultimo ribilancio 2026-11-21
- ordini limite: 1645 eseguiti su 1651 · tutto a mercato sarebbe costato $121.50 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.9%, XMRUSDT -7.8%, HYPEUSDT -7.0%, TRXUSDT +7.0%, RENDERUSDT -6.2%, JTOUSDT -6.2%, 1000SHIBUSDT +5.9%, FARTCOINUSDT -5.8%, BRUSDT -5.6%, XPLUSDT -5.5%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-21 04:14 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,252.02** su $10,000 (+12.52%) · costi $31.70 · funding pagato $-453.26
- posizioni: 26 long, 30 short · ultimo ribilancio 2026-11-21
- ordini limite: 1453 eseguiti su 1457 · tutto a mercato sarebbe costato $82.28 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.6%, TRXUSDT +8.4%, 1000SHIBUSDT +7.1%, XMRUSDT -7.0%, XLMUSDT +6.6%, HYPEUSDT -6.3%, BCHUSDT +6.1%, ADAUSDT +5.7%, RENDERUSDT -5.6%, JTOUSDT -5.5%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-21 04:01 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-21 03:59 UTC)
- equity: **$1,030.92** su $1,000.00 (+3.09%) · posizioni 24 long, 27 short · ordini limite eseguiti 760 su 807 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,378.83
- ultima decisione 2026-11-21: 18 ordini, eseguiti a limite 18, a mercato 0; sotto il minimo 35 variazioni (9.2% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 3: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; UAIUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.88%, LITUSDT +3.44%, UAIUSDT -1.34%, IRYSUSDT +0.41%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -2.71% dal massimo
- margine (2026-11-21 03:59 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-21 03:59 UTC): 55 monete, scarto totale 14.3% del conto; oltre il 2%: LITUSDT -3.2%
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
| 2026-11-21 | -0.01% | -0.34% | +0.33% | +0.00% |

- dal 2026-11-09 (13 giorni): demo +3.59%, paper +4.79%; differenza media al giorno -0.093%, oscillazione 0.596%

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
| 2026-11-21 | +0.038% | +0.043% | +0.004% | +0.005% |

- sul demo, dal 2026-11-07 (15 giorni): funding incassato +23.71 USDT, commissioni pagate 1.55 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 51, peso 345 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 130
Dal 2026-11-16 00:00 a 2026-11-21 04:19 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 47 monete su 47

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-16 | 615.17 | 0.1813 | 0.0295% | 63% | 37% | 51 |
| 2026-11-17 | 323.45 | 0.0882 | 0.0273% | 67% | 33% | 37 |
| 2026-11-18 | 43.45 | 0.0122 | 0.0281% | 73% | 27% | 8 |
| 2026-11-19 | 212.92 | 0.0603 | 0.0283% | 61% | 39% | 27 |
| 2026-11-20 | 110.20 | 0.0255 | 0.0232% | 89% | 11% | 21 |
| 2026-11-21 | 182.63 | 0.0441 | 0.0241% | 85% | 15% | 38 |
| 6 giorni | 1,487.81 | 0.4115 | 0.0277% | 68% | 32% | 182 |
- controllo: commissioni dagli incassi 0.4115 USDT, dalle esecuzioni 0.4115 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-16 | +1.3306 | +0.3986 | +0.1989 | +0.3225 | +0.4106 | 49/52 |
| 2026-11-17 | +1.4479 | +0.7040 | +0.2906 | +0.1837 | +0.2697 | 52/56 |
| 2026-11-18 | +0.7448 | +0.2069 | +0.0892 | +0.1967 | +0.2521 | 52/56 |
| 2026-11-19 | +1.6187 | +0.3048 | +0.4174 | +0.4832 | +0.4132 | 52/57 |
| 2026-11-20 | +1.6724 | +0.2605 | +0.6450 | +0.3815 | +0.3854 | 52/57 |
| 2026-11-21 (in corso) | +0.5340 | +0.3935 | +0.0000 | +0.0000 | +0.1405 | —/56 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| HUMAUSDT | +1.4088 | +0.6566 | +0.2507 | +0.5015 | +0.0000 | +1.52% |
| ONUSDT | +0.6279 | +0.0822 | +0.0989 | +0.1273 | +0.3194 | -2.27% |
| BIRBUSDT | +0.5989 | +0.0371 | +0.1304 | +0.0592 | +0.3723 | +1.66% |
| LSKUSDT | +0.5712 | +0.2371 | +0.2006 | +0.1336 | +0.0000 | +2.85% |
| BMTUSDT | +0.5274 | +0.0706

[... 31022 caratteri omessi (testa e coda conservate) ...]

0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
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
| holdout | 1 | 0.1% |
| total_return | 1207 | 91.4% |
| recovery | 64 | 4.8% |
| regime | 22 | 1.7% |
| trades | 6 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 589 | 1.7% |
| pf_ex_top | 242 | 0.7% |
| holdout | 153 | 0.5% |
| total_return | 26463 | 78.0% |
| recovery | 2737 | 8.1% |
| regime | 2815 | 8.3% |
| trades | 936 | 2.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-21 04:04 UTC · coppie validate: **278** · GATE 1 pronto: True
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
Letto il 2026-11-21 04:20 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,030.92 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -11.57/-11.17 · TRXUSDT +8.35/+8.26 · 1000SHIBUSDT +7.09/+6.78 · XMRUSDT -6.99/-6.12 · XLMUSDT +6.60/+6.27 · HYPEUSDT -6.29/-5.74
- BCHUSDT +6.09/+4.92 · ADAUSDT +5.73/+5.00 · RENDERUSDT -5.58/-5.29 · JTOUSDT -5.53/-4.80 · SANDUSDT +5.34/+5.04 · FARTCOINUSDT -5.17/-4.87
- BRUSDT -5.02/-4.47 · ASTERUSDT -4.95/-4.38 · SEIUSDT +4.93/+4.65 · XPLUSDT -4.90/-4.34 · NEARUSDT -4.77/-4.11 · ETHFIUSDT -4.58/-4.12
- APTUSDT +4.43/+4.14 · 1000BONKUSDT +4.30/+4.09 · WLDUSDT +4.25/+3.96 · TIAUSDT +4.23/+3.77 · JUPUSDT +4.03/+3.77 · GRASSUSDT -3.94/-3.47
- INJUSDT +3.90/+3.68 · 1000PEPEUSDT +3.86/+3.19 · TRUMPUSDT +3.81/+3.64 · OPUSDT +3.81/+3.58 · LITUSDT +3.44/+0.00 · BEATUSDT -3.27/-2.90
- GTCUSDT +3.20/+3.08 · ERAUSDT +3.19/+3.02 · LSKUSDT +2.85/+2.33 · DOODUSDT -2.73/-2.38 · USELESSUSDT -2.72/-2.18 · BEAMXUSDT -2.65/-2.12
- ARIAUSDT -2.24/-2.30 · ONUSDT -2.27/-2.27 · ICNTUSDT -2.27/-1.90 · PARTIUSDT -2.24/-2.16 · APRUSDT -1.75/-1.54 · BIRBUSDT +1.66/+1.63
- MAGMAUSDT -1.60/-1.54 · HUMAUSDT +1.52/+1.41 · IDOLUSDT -1.11/-1.42 · BMTUSDT +1.40/+1.06 · UAIUSDT -1.34/+0.00 · INITUSDT +1.25/+1.08
- BULLAUSDT -1.25/-1.20 · EVAAUSDT -0.88/+0.00 · AINUSDT -0.81/-0.78 · AGTUSDT -0.63/-0.52 · QUSDT -0.53/-0.48 · IRYSUSDT +0.41/+0.00
- JCTUSDT -0.39/+0.00 · AKEUSDT +0.30/+0.13
- monete: paper 56, demo 51; esposizione lorda paper 200.0%, demo 177.1%; somma delle differenze 23.7% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 1,030.92 USDT, paper 10,966.34; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-19 00 | +0.0296% | +0.0148% | +0.0148% | 52/56 |
| 2026-11-19 08 | +0.0405% | +0.0158% | +0.0246% | 52/57 |
| 2026-11-19 16 | +0.0469% | +0.0212% | +0.0257% | 52/57 |
| 2026-11-19 altre | +0.0401% | +0.1037% | -0.0636% | 51/162 |
| 2026-11-20 00 | +0.0253% | +0.0227% | +0.0026% | 52/57 |
| 2026-11-20 08 | +0.0626% | +0.0413% | +0.0212% | 52/57 |
| 2026-11-20 16 | +0.0370% | +0.0249% | +0.0121% | 52/57 |
| 2026-11-20 altre | +0.0374% | +0.0921% | -0.0547% | 51/177 |
| 2026-11-21 00 | +0.0382% | +0.0239% | +0.0143% | 52/57 |
| 2026-11-21 altre | +0.0136% | +0.0188% | -0.0052% | 17/51 |

- regolamento 2026-11-21 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): BMTUSDT +0.0053/+0.0032 · INITUSDT +0.0050/— · 1000BONKUSDT +0.0040/+0.0011 · ONUSDT +0.0040/— · TRXUSDT +0.0006/+0.0036 · WLDUSDT +0.0004/+0.0022 · GTCUSDT +0.0021/+0.0008 · HUMAUSDT +0.0020/— · LSKUSDT +0.0016/+0.0009 · ADAUSDT +0.0008/+0.0015 · XMRUSDT +0.0008/+0.0007 · ERAUSDT +0.0003/+0.0008 · SEIUSDT -0.0004/+0.0007
```
