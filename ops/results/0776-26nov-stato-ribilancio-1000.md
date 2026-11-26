# 0776-26nov-stato-ribilancio-1000.req

_eseguito: 2026-11-26 04:20 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 51.0s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-26 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-26 04:19 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-26 03:31 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,698.10** su $10,000 (+6.98%) · costi $12.65 · funding pagato $-529.11
- posizioni: 31 long, 28 short · ultimo ribilancio 2026-11-23
- ordini limite: 309 eseguiti su 309 · tutto a mercato sarebbe costato $44.04 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -14.2%, XMRUSDT -7.3%, HYPEUSDT -7.0%, TRXUSDT +7.0%, RENDERUSDT -6.3%, FARTCOINUSDT -5.9%, XPLUSDT -5.6%, XLMUSDT +5.6%, ASTERUSDT -5.5%, BCHUSDT +5.2%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-26 04:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,555.59** su $10,000 (+5.56%) · costi $35.07 · funding pagato $-514.41
- posizioni: 29 long, 29 short · ultimo ribilancio 2026-11-26
- ordini limite: 1856 eseguiti su 1863 · tutto a mercato sarebbe costato $100.43 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -10.7%, TRXUSDT +7.2%, XMRUSDT -7.0%, HYPEUSDT -6.5%, AEROUSDT -6.4%, 1000SHIBUSDT +6.2%, RENDERUSDT -6.0%, XLMUSDT +5.5%, FARTCOINUSDT -5.5%, BCHUSDT +5.2%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-26 04:10 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,531.96** su $10,000 (+5.32%) · costi $41.80 · funding pagato $-484.22
- posizioni: 29 long, 24 short · ultimo ribilancio 2026-11-26
- ordini limite: 1936 eseguiti su 1942 · tutto a mercato sarebbe costato $135.36 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -13.6%, XMRUSDT -9.0%, HYPEUSDT -8.2%, AEROUSDT -8.1%, FARTCOINUSDT -7.0%, XPLUSDT -6.4%, ETHFIUSDT -6.1%, 1000SHIBUSDT +6.0%, GRASSUSDT -5.6%, XLMUSDT +5.4%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-26 04:15 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$10,858.97** su $10,000 (+8.59%) · costi $34.32 · funding pagato $-517.71
- posizioni: 29 long, 29 short · ultimo ribilancio 2026-11-26
- ordini limite: 1751 eseguiti su 1755 · tutto a mercato sarebbe costato $91.46 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -10.8%, TRXUSDT +7.1%, XMRUSDT -7.1%, HYPEUSDT -6.5%, AEROUSDT -6.5%, 1000SHIBUSDT +6.1%, RENDERUSDT -6.1%, FARTCOINUSDT -5.6%, XLMUSDT +5.5%, ASTERUSDT -5.2%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-26 03:46 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-26 03:46 UTC)
- equity: **$987.27** su $1,000.00 (-1.27%) · posizioni 27 long, 25 short · ordini limite eseguiti 808 su 857 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,335.18
- ultima decisione 2026-11-26: 6 ordini, eseguiti a limite 5, a mercato 1; sotto il minimo 48 variazioni (8.8% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 4: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; PIEVERSEUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.83%, LITUSDT +3.20%, PIEVERSEUSDT -1.73%, UAIUSDT -1.41%, IRYSUSDT +2.13%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -6.83% dal massimo
- margine (2026-11-26 03:46 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-26 03:46 UTC): 57 monete, scarto totale 16.0% del conto; oltre il 2%: LITUSDT -3.2%
- ultimo errore (2026-11-25 17:36 UTC): `HTTPSConnectionPool(host='demo-fapi.binance.com', port=443): Read timed out. (read timeout=15)`

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
| 2026-11-23 | +1.71% | +0.96% | +0.74% | +0.00% |
| 2026-11-24 | -0.59% | +0.23% | -0.82% | +0.00% |
| 2026-11-25 | -1.39% | -2.07% | +0.68% | +0.00% |
| 2026-11-26 | +1.26% | +1.21% | +0.05% | +0.00% |

- dal 2026-11-09 (18 giorni): demo -0.80%, paper +0.87%; differenza media al giorno -0.095%, oscillazione 0.612%

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
| 2026-11-23 | +0.205% | +0.135% | +0.012% | +0.010% |
| 2026-11-24 | +0.143% | +0.107% | +0.001% | +0.002% |
| 2026-11-25 | +0.113% | +0.104% | +0.004% | +0.003% |
| 2026-11-26 | +0.029% | +0.026% | +0.001% | +0.003% |

- sul demo, dal 2026-11-07 (20 giorni): funding incassato +31.18 USDT, commissioni pagate 1.74 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 42, peso 300 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 140
Dal 2026-11-21 00:00 a 2026-11-26 04:19 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 38 monete su 38

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-21 | 182.63 | 0.0441 | 0.0241% | 85% | 15% | 38 |
| 2026-11-22 | 64.15 | 0.0144 | 0.0224% | 92% | 8% | 13 |
| 2026-11-23 | 377.03 | 0.1179 | 0.0313% | 58% | 42% | 43 |
| 2026-11-24 | 56.40 | 0.0135 | 0.0239% | 78% | 22% | 12 |
| 2026-11-25 | 75.67 | 0.0350 | 0.0462% | 0% | 100% | 16 |
| 2026-11-26 | 22.67 | 0.0098 | 0.0430% | 23% | 77% | 4 |
| 6 giorni | 778.54 | 0.2346 | 0.0301% | 62% | 38% | 126 |
- controllo: commissioni dagli incassi 0.2346 USDT, dalle esecuzioni 0.2346 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-21 | +1.4863 | +0.3935 | +0.3560 | +0.3849 | +0.3519 | 51/56 |
| 2026-11-22 | +1.5327 | +0.3770 | +0.4462 | +0.2969 | +0.4126 | 52/57 |
| 2026-11-23 | +2.0388 | +0.4682 | +0.5373 | +0.6150 | +0.4183 | 53/59 |
| 2026-11-24 | +1.4174 | +0.5758 | +0.3850 | +0.2770 | +0.1796 | 53/59 |
| 2026-11-25 | +1.1032 | +0.2652 | +0.2787 | +0.2331 | +0.3262 | 5

[... 31684 caratteri omessi (testa e coda conservate) ...]

0], sl_to_breakeven=True, profit_lock_keep=0.65 |
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
| regime | 22 | 1.7% |
| consistency | 17 | 1.3% |
| recovery | 64 | 4.8% |
| pf_ex_top | 3 | 0.2% |
| total_return | 1207 | 91.4% |
| trades | 6 | 0.5% |
| holdout | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 2815 | 8.3% |
| consistency | 589 | 1.7% |
| pf_ex_top | 242 | 0.7% |
| recovery | 2737 | 8.1% |
| holdout | 153 | 0.5% |
| total_return | 26463 | 78.0% |
| trades | 936 | 2.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-26 04:01 UTC · coppie validate: **278** · GATE 1 pronto: True
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
Letto il 2026-11-26 04:20 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (987.27 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -10.71/-10.57 · TRXUSDT +7.21/+7.18 · XMRUSDT -7.04/-7.21 · HYPEUSDT -6.46/-6.53 · AEROUSDT -6.39/-6.48 · 1000SHIBUSDT +6.17/+6.33
- RENDERUSDT -6.01/-6.04 · XLMUSDT +5.55/+5.85 · BCHUSDT +5.22/+5.81 · FARTCOINUSDT -5.49/-5.68 · ASTERUSDT -5.14/-5.36 · ADAUSDT +5.00/+5.20
- XPLUSDT -5.04/-4.96 · NEARUSDT -4.99/-4.95 · ETHFIUSDT -4.82/-4.48 · SANDUSDT +4.80/+4.75 · GRASSUSDT -4.40/-4.56 · SEIUSDT +4.46/+4.53
- GTCUSDT +4.29/+3.88 · FETUSDT +3.89/+4.06 · 1000BONKUSDT +3.73/+4.02 · WLDUSDT +3.81/+3.94 · APTUSDT +3.81/+3.85 · TIAUSDT +3.68/+3.84
- 1000PEPEUSDT +3.49/+3.65 · JUPUSDT +3.37/+3.60 · VVVUSDT -3.57/-3.29 · BEATUSDT -3.54/-2.98 · OPUSDT +3.41/+3.36 · ERAUSDT +3.38/+3.35
- INJUSDT +3.36/+3.34 · TRUMPUSDT +3.21/+3.31 · LITUSDT +3.20/+0.00 · BEAMXUSDT -2.98/-2.84 · USELESSUSDT -2.93/-2.94 · ARIAUSDT -2.39/-2.75
- BMTUSDT +2.46/+2.17 · LSKUSDT +2.40/+2.23 · MAGMAUSDT -2.39/-2.03 · ICNTUSDT -2.33/-2.18 · APRUSDT -2.17/-2.03 · IRYSUSDT +2.13/+0.00
- HOTUSDT +2.09/+1.98 · BIRBUSDT +2.01/+1.77 · PIEVERSEUSDT -1.73/+0.00 · QUSDT -1.63/-1.60 · UAIUSDT -1.41/+0.00 · HUMAUSDT +1.34/+1.29
- BULLAUSDT -1.28/-1.32 · ONEUSDT +1.15/+1.18 · BLESSUSDT -1.13/-1.15 · IDOLUSDT -1.06/-1.14 · INITUSDT +1.11/+1.11 · AINUSDT -0.97/-0.71
- EVAAUSDT -0.83/+0.00 · AGTUSDT -0.68/-0.47 · JCTUSDT -0.47/+0.00 · AKEUSDT +0.26/+0.04
- monete: paper 58, demo 52; esposizione lorda paper 200.0%, demo 189.9%; somma delle differenze 18.2% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 987.27 USDT, paper 10,555.59; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-24 00 | +0.0583% | +0.0311% | +0.0273% | 53/59 |
| 2026-11-24 08 | +0.0390% | +0.0189% | +0.0201% | 53/59 |
| 2026-11-24 16 | +0.0281% | +0.0211% | +0.0069% | 53/59 |
| 2026-11-24 altre | +0.0182% | +0.0370% | -0.0188% | 54/163 |
| 2026-11-25 00 | +0.0269% | +0.0192% | +0.0076% | 53/59 |
| 2026-11-25 08 | +0.0282% | +0.0151% | +0.0132% | 53/59 |
| 2026-11-25 16 | +0.0236% | +0.0193% | +0.0043% | 53/59 |
| 2026-11-25 altre | +0.0330% | +0.0488% | -0.0158% | 51/150 |
| 2026-11-26 00 | +0.0288% | +0.0160% | +0.0128% | 53/59 |
| 2026-11-26 altre | +0.0099% | +0.0104% | -0.0005% | 17/46 |

- regolamento 2026-11-26 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): BULLAUSDT +0.0081/+0.0039 · ARIAUSDT +0.0038/+0.0007 · XMRUSDT +0.0021/+0.0007 · JUPUSDT +0.0020/— · BCHUSDT +0.0018/— · TRXUSDT -0.0007/+0.0016 · BMTUSDT +0.0013/+0.0005 · WLDUSDT +0.0002/+0.0008 · PIEVERSEUSDT +0.0000/+0.0007 · WLFIUSDT +0.0007/+0.0007 · NEARUSDT +0.0000/+0.0005 · IRYSUSDT +0.0000/+0.0005
```
