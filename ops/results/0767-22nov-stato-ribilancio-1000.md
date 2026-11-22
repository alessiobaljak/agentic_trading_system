# 0767-22nov-stato-ribilancio-1000.req

_eseguito: 2026-11-22 04:21 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 47.4s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-22 04:20 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-22 04:20 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-22 03:52 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,595.84** su $10,000 (+5.96%) · costi $11.30 · funding pagato $-483.77
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-16
- ordini limite: 245 eseguiti su 245 · tutto a mercato sarebbe costato $39.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.2%, TRXUSDT +8.2%, XMRUSDT -7.7%, HYPEUSDT -7.4%, RENDERUSDT -6.7%, XLMUSDT +6.5%, ASTERUSDT -6.3%, POLUSDT +6.2%, BCHUSDT +6.0%, JTOUSDT -5.9%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-22 04:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,748.97** su $10,000 (+7.49%) · costi $33.13 · funding pagato $-466.33
- posizioni: 26 long, 31 short · ultimo ribilancio 2026-11-22
- ordini limite: 1615 eseguiti su 1622 · tutto a mercato sarebbe costato $93.62 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.9%, TRXUSDT +8.1%, 1000SHIBUSDT +7.0%, XLMUSDT +6.5%, XMRUSDT -6.2%, HYPEUSDT -6.0%, BCHUSDT +5.9%, ADAUSDT +5.7%, RENDERUSDT -5.4%, SANDUSDT +5.4%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-22 04:10 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,661.36** su $10,000 (+6.61%) · costi $38.29 · funding pagato $-436.76
- posizioni: 30 long, 27 short · ultimo ribilancio 2026-11-22
- ordini limite: 1703 eseguiti su 1709 · tutto a mercato sarebbe costato $123.09 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -13.8%, XMRUSDT -7.2%, HYPEUSDT -7.0%, TRXUSDT +6.8%, RENDERUSDT -6.3%, JTOUSDT -6.1%, 1000SHIBUSDT +5.8%, FARTCOINUSDT -5.8%, BRUSDT -5.7%, XPLUSDT -5.5%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-22 04:14 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,034.39** su $10,000 (+10.34%) · costi $32.09 · funding pagato $-468.72
- posizioni: 26 long, 31 short · ultimo ribilancio 2026-11-22
- ordini limite: 1510 eseguiti su 1514 · tutto a mercato sarebbe costato $83.66 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.8%, TRXUSDT +8.2%, 1000SHIBUSDT +7.0%, XLMUSDT +6.6%, XMRUSDT -6.1%, HYPEUSDT -6.0%, BCHUSDT +5.9%, ADAUSDT +5.7%, SANDUSDT +5.4%, RENDERUSDT -5.4%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-22 04:18 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-22 04:18 UTC)
- equity: **$1,008.08** su $1,000.00 (+0.81%) · posizioni 24 long, 28 short · ordini limite eseguiti 764 su 811 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,355.99
- ultima decisione 2026-11-22: 4 ordini, eseguiti a limite 4, a mercato 0; sotto il minimo 49 variazioni (9.2% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 3: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; UAIUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.84%, LITUSDT +3.48%, UAIUSDT -1.27%, IRYSUSDT +0.40%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -4.86% dal massimo
- margine (2026-11-22 04:18 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-22 04:18 UTC): 56 monete, scarto totale 14.4% del conto; oltre il 2%: LITUSDT -3.4%
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
| 2026-11-22 | +0.94% | +0.78% | +0.16% | +0.00% |

- dal 2026-11-09 (14 giorni): demo +1.29%, paper +2.72%; differenza media al giorno -0.103%, oscillazione 0.565%

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
| 2026-11-22 | +0.047% | +0.042% | +0.001% | +0.004% |

- sul demo, dal 2026-11-07 (16 giorni): funding incassato +25.28 USDT, commissioni pagate 1.56 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 39, peso 285 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 290
Dal 2026-11-17 00:00 a 2026-11-22 04:20 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 35 monete su 35

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-17 | 323.45 | 0.0882 | 0.0273% | 67% | 33% | 37 |
| 2026-11-18 | 43.45 | 0.0122 | 0.0281% | 73% | 27% | 8 |
| 2026-11-19 | 212.92 | 0.0603 | 0.0283% | 61% | 39% | 27 |
| 2026-11-20 | 110.20 | 0.0255 | 0.0232% | 89% | 11% | 21 |
| 2026-11-21 | 182.63 | 0.0441 | 0.0241% | 85% | 15% | 38 |
| 2026-11-22 | 64.15 | 0.0144 | 0.0224% | 92% | 8% | 13 |
| 6 giorni | 936.80 | 0.2446 | 0.0261% | 74% | 26% | 144 |
- controllo: commissioni dagli incassi 0.2446 USDT, dalle esecuzioni 0.2446 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-17 | +1.4479 | +0.7040 | +0.2906 | +0.1837 | +0.2697 | 52/56 |
| 2026-11-18 | +0.7448 | +0.2069 | +0.0892 | +0.1967 | +0.2521 | 52/56 |
| 2026-11-19 | +1.6187 | +0.3048 | +0.4174 | +0.4832 | +0.4132 | 52/57 |
| 2026-11-20 | +1.6724 | +0.2605 | +0.6450 | +0.3815 | +0.3854 | 52/57 |
| 2026-11-21 | +1.4863 | +0.3935 | +0.3560 | +0.3849 | +0.3519 | 51/56 |
| 2026-11-22 (in corso) | +0.4718 | +0.3770 | +0.0000 | +0.0000 | +0.0948 | —/57 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| HUMAUSDT | +1.1983 | +0.6143 | +0.2381 | +0.3459 | +0.0000 | +1.50% |
| ONUSDT | +0.7914 | +0.1233 | +0.1241 | +0.1495 | +0.3944 | -2.14% |
| BMTUSDT | +0.6013 | +0.1137 | +0.3040 | +0.1836 | +0.0000 | +1.41% |

[... 31169 caratteri omessi (testa e coda conservate) ...]

eakeven=True, profit_lock_keep=0.65 |
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
| holdout | 1 | 0.1% |
| trades | 6 | 0.5% |
| total_return | 1207 | 91.4% |
| pf_ex_top | 3 | 0.2% |
| regime | 22 | 1.7% |
| recovery | 64 | 4.8% |
| consistency | 17 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 153 | 0.5% |
| total_return | 26463 | 78.0% |
| trades | 936 | 2.8% |
| pf_ex_top | 242 | 0.7% |
| regime | 2815 | 8.3% |
| recovery | 2737 | 8.1% |
| consistency | 589 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-22 04:01 UTC · coppie validate: **278** · GATE 1 pronto: True
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
Letto il 2026-11-22 04:20 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,008.08 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -11.90/-11.45 · TRXUSDT +8.13/+8.59 · 1000SHIBUSDT +6.99/+7.28 · XLMUSDT +6.53/+6.71 · HYPEUSDT -6.02/-6.23 · XMRUSDT -6.16/-6.08
- BCHUSDT +5.91/+5.37 · RENDERUSDT -5.43/-5.85 · ADAUSDT +5.71/+5.38 · SANDUSDT +5.38/+5.32 · JTOUSDT -5.24/-5.05 · FARTCOINUSDT -5.00/-5.22
- BRUSDT -4.92/-5.19 · SEIUSDT +5.04/+4.87 · ETHFIUSDT -4.33/-4.78 · XPLUSDT -4.77/-4.51 · ASTERUSDT -4.70/-4.56 · NEARUSDT -4.58/-4.55
- APTUSDT +4.42/+4.52 · WLDUSDT +4.18/+4.30 · 1000BONKUSDT +4.24/+4.27 · TIAUSDT +4.21/+4.02 · GTCUSDT +4.18/+4.16 · TRUMPUSDT +3.70/+4.07
- JUPUSDT +3.95/+3.95 · GRASSUSDT -3.79/-3.90 · OPUSDT +3.82/+3.90 · INJUSDT +3.87/+3.68 · 1000PEPEUSDT +3.81/+3.38 · VVVUSDT -3.61/-3.60
- LITUSDT +3.48/+0.00 · ERAUSDT +3.22/+3.29 · BEATUSDT -3.12/-3.08 · LSKUSDT +2.79/+2.65 · DOODUSDT -2.61/-2.64 · USELESSUSDT -2.57/-2.53
- ONUSDT -2.14/-2.56 · BEAMXUSDT -2.51/-2.37 · ARIAUSDT -2.15/-2.51 · PARTIUSDT -2.09/-2.30 · ICNTUSDT -2.11/-1.78 · MAGMAUSDT -1.97/-1.85
- BIRBUSDT +1.62/+1.70 · APRUSDT -1.66/-1.63 · HUMAUSDT +1.50/+1.47 · BMTUSDT +1.41/+1.14 · BULLAUSDT -1.21/-1.32 · UAIUSDT -1.27/+0.00
- INITUSDT +1.22/+1.15 · IDOLUSDT -1.04/-0.60 · EVAAUSDT -0.84/+0.00 · AINUSDT -0.77/-0.80 · AGTUSDT -0.60/-0.56 · QUSDT -0.50/-0.50
- IRYSUSDT +0.40/+0.00 · JCTUSDT -0.37/+0.00 · AKEUSDT +0.30/+0.07
- monete: paper 57, demo 52; esposizione lorda paper 200.0%, demo 193.3%; somma delle differenze 16.0% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 1,008.08 USDT, paper 10,748.97; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-20 00 | +0.0258% | +0.0231% | +0.0027% | 52/57 |
| 2026-11-20 08 | +0.0640% | +0.0422% | +0.0218% | 52/57 |
| 2026-11-20 16 | +0.0378% | +0.0254% | +0.0125% | 52/57 |
| 2026-11-20 altre | +0.0382% | +0.0940% | -0.0558% | 51/177 |
| 2026-11-21 00 | +0.0390% | +0.0244% | +0.0146% | 52/57 |
| 2026-11-21 08 | +0.0353% | +0.0221% | +0.0132% | 51/56 |
| 2026-11-21 16 | +0.0382% | +0.0244% | +0.0138% | 51/56 |
| 2026-11-21 altre | +0.0349% | +0.0701% | -0.0352% | 51/180 |
| 2026-11-22 00 | +0.0374% | +0.0202% | +0.0172% | 51/56 |
| 2026-11-22 altre | +0.0094% | +0.0219% | -0.0125% | 17/52 |

- regolamento 2026-11-22 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): INITUSDT +0.0161/+0.0012 · 1000BONKUSDT +0.0037/+0.0007 · HUMAUSDT +0.0037/— · JTOUSDT -0.0033/— · ARIAUSDT +0.0022/— · JUPUSDT +0.0021/— · LSKUSDT +0.0019/+0.0007 · ERAUSDT +0.0013/+0.0017 · BCHUSDT +0.0012/+0.0009 · WLDUSDT +0.0001/+0.0011 · ADAUSDT -0.0005/+0.0009 · BMTUSDT +0.0007/+0.0008 · APTUSDT -0.0002/+0.0008 · XMRUSDT +0.0007/+0.0008
```
