# 0740-14nov-stato-ribilancio-1000.req

_eseguito: 2026-11-14 04:20 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 50.9s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-14 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-14 04:19 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-14 03:45 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,163.20** su $10,000 (+1.63%) · costi $8.88 · funding pagato $-349.24
- posizioni: 30 long, 25 short · ultimo ribilancio 2026-11-09
- ordini limite: 179 eseguiti su 179 · tutto a mercato sarebbe costato $30.86 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -10.4%, WLFIUSDT -9.3%, TRXUSDT +8.0%, XRPUSDT -8.0%, XMRUSDT -8.0%, XLMUSDT +6.6%, HYPEUSDT -6.1%, POLUSDT +6.1%, DOTUSDT +6.1%, ATOMUSDT +6.0%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-14 04:07 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,733.10** su $10,000 (+7.33%) · costi $26.99 · funding pagato $-330.99
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-14
- ordini limite: 1155 eseguiti su 1162 · tutto a mercato sarebbe costato $72.13 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -9.4%, WLFIUSDT -8.2%, TRXUSDT +7.8%, XRPUSDT -7.6%, XLMUSDT +7.1%, XMRUSDT -6.6%, BCHUSDT +6.5%, POLUSDT +6.5%, TAOUSDT -6.3%, HYPEUSDT -5.9%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-14 04:10 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,681.25** su $10,000 (+6.81%) · costi $29.02 · funding pagato $-307.68
- posizioni: 25 long, 26 short · ultimo ribilancio 2026-11-14
- ordini limite: 1226 eseguiti su 1230 · tutto a mercato sarebbe costato $97.82 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -10.2%, WLFIUSDT -8.9%, TRXUSDT +8.2%, XMRUSDT -7.1%, BCHUSDT +6.9%, POLUSDT +6.8%, HYPEUSDT -6.4%, WIFUSDT -6.3%, GALAUSDT +6.1%, PENDLEUSDT -6.0%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-14 04:14 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$10,989.55** su $10,000 (+9.90%) · costi $24.67 · funding pagato $-330.70
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-14
- ordini limite: 1051 eseguiti su 1054 · tutto a mercato sarebbe costato $60.92 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -9.3%, WLFIUSDT -8.1%, TRXUSDT +8.0%, XRPUSDT -7.5%, XLMUSDT +7.2%, BCHUSDT +6.6%, POLUSDT +6.6%, XMRUSDT -6.4%, TAOUSDT -6.1%, ATOMUSDT +5.9%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-14 03:55 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-14 04:00 UTC)
- equity: **$1,007.27** su $1,000.00 (+0.73%) · posizioni 26 long, 24 short · ordini limite eseguiti 635 su 674 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,355.18
- ultima decisione 2026-11-14: 6 ordini, eseguiti a limite 6, a mercato 0; sotto il minimo 45 variazioni (8.6% del conto); rifiutati 1: 龙虾USDT POST /fapi/v1/order: 400 {"code":-1121,"msg":"Invalid symbol."}
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): 龙虾USDT -3.21%
- stop sul conto: si chiude tutto sotto $658.84 (il più alto fra −35% dal massimo, $1,013.60, e il 65% del capitale di partenza); ora -0.62% dal massimo
- margine (2026-11-14 04:00 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-14 04:00 UTC): 53 monete, scarto totale 11.6% del conto; oltre il 2%: 龙虾USDT +3.1%
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
| 2026-11-14 | -0.04% | +0.19% | -0.23% | +0.00% |

- dal 2026-11-09 (6 giorni): demo +1.21%, paper +2.56%; differenza media al giorno -0.226%, oscillazione 0.486%

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
| 2026-11-14 | +0.049% | +0.042% | +0.002% | +0.003% |

- sul demo, dal 2026-11-07 (8 giorni): funding incassato +13.62 USDT, commissioni pagate 1.03 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- spento: nessuno stato scritto (il bot non lo ha ancora fatto girare)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 45, peso 315 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 160
Dal 2026-11-09 00:00 a 2026-11-14 04:19 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 41 monete su 41

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-09 | 296.20 | 0.0800 | 0.0270% | 72% | 28% | 42 |
| 2026-11-10 | 113.14 | 0.0421 | 0.0372% | 43% | 57% | 8 |
| 2026-11-11 | 104.77 | 0.0266 | 0.0254% | 82% | 18% | 14 |
| 2026-11-12 | 95.67 | 0.0250 | 0.0261% | 80% | 20% | 18 |
| 2026-11-13 | 294.91 | 0.0857 | 0.0291% | 63% | 37% | 31 |
| 2026-11-14 | 68.00 | 0.0242 | 0.0355% | 26% | 74% | 6 |
| 6 giorni | 972.70 | 0.2836 | 0.0292% | 64% | 36% | 119 |
- controllo: commissioni dagli incassi 0.2836 USDT, dalle esecuzioni 0.2836 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-09 | +1.9929 | +0.4001 | +0.7955 | +0.6235 | +0.1739 | 51/56 |
| 2026-11-10 | +2.7297 | +1.0536 | +0.8350 | +0.7082 | +0.1328 | 51/56 |
| 2026-11-11 | +2.0138 | +0.6612 | +0.6133 | +0.4609 | +0.2784 | 51/55 |
| 2026-11-12 | +1.9193 | +0.5532 | +0.5668 | +0.6022 | +0.1972 | 50/54 |
| 2026-11-13 | +2.5725 | +0.7470 | +1.0759 | +0.5527 | +0.1968 | 49/52 |
| 2026-11-14 (in corso) | +0.4901 | +0.4308 | +0.0000 | +0.0000 | +0.0593 | —/53 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| INITUSDT | +2.2846 | +0.9512 | +0.8021 | +0.5313 | +0.0000 | +1.14% |
| XMRUSDT | +1.8329 | +0.5813 | +0.6906 | +0.5610 | +0.0000 | -6.55% |
| HUMAUSDT | +1.4283 | +0.3974 | +0.5863 | +0.4445 | +0.0000 | +2.40% |
| ERAUSDT | +0.8971 | +0.0877 | +0.1678 | +0.1468 | +0.4948 | +2.65% |
| AEROUSDT | +0.7106 | +0.2460 | +0.3024 | +0.1621 | +0.0000 | +4.03% |
| BMTUSDT | +0.5452 | +0.0848 | +0.1873 | +0.2732 | +0.0000 | +1.27% |
| LSKUSDT | +0.5412 | +0.2238 | +0.1823 | +0.1351 | +0.0000 | +2.40% |
| GTCUSDT | +0.5380 | +0.1848 | +0.2470 | +0.1061 | +0.0000 | +1.87% |
| ATOMUSDT | +0.2273 | +0.0654 | +0.0997 | +0.0621 | +0.0000 | +5.74% |
| AGTUSDT | +0.1932 | +0.0673 | +0.0332 | +0.0928 | +0.0000 | -0.40% |

- monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): 龙虾USDT rifiutata 6 giorni dal 2026-11-09, IRYSUSDT mancante sul demo 4 giorni dal 2026-11-09, ICPUSDT mancante sul demo 2 giorni dal 2026-11-09
- il paper G1 di oggi contro il funding del demo, per nome: dopo il regolamento delle 08 UTC (i pesi dei giorni passati del paper non sono su Firebase)

## Ultima decisione
- esito: **🟢 APERTA** (2026-10-21 07:02 UTC)
- motivo: aperta SYRUPUSDT long (gen_4c6df481), ordine limite riempito a 0.20076
- asset valutati: 80 · segnali: 1 · miglior segnale SYRUPUSDT gen_4c6df481 (conf. 55.6/soglia 30)

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti

[... 29595 caratteri omessi (testa e coda conservate) ...]

fit_lock_keep=0.65 |
| KERNELUSDT | gen_c647ead7 | 3 | 2.131 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MYXUSDT | gen_8931b93c | 3 | 1.583 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
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
| pf_ex_top | 3 | 0.2% |
| regime | 22 | 1.7% |
| trades | 6 | 0.5% |
| holdout | 1 | 0.1% |
| consistency | 17 | 1.3% |
| total_return | 1207 | 91.4% |
| recovery | 64 | 4.8% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 242 | 0.7% |
| regime | 2815 | 8.3% |
| total_return | 26463 | 78.0% |
| trades | 936 | 2.8% |
| consistency | 589 | 1.7% |
| holdout | 153 | 0.5% |
| recovery | 2737 | 8.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-14 04:02 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: drift · 143 trade · PF vissuto 0.85 vs 2.02 atteso · mfe mediana 0.61R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.85 vs 2.02 atteso · mfe mediana 0.61R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| TRUMPUSDT|gen_d16d1d02 | watch | 7 | 1.439 / 1.591 | mfe mediana 1.08R < primo TP 2.00R |
| TAUSDT|gen_01fbe76f | watch | 5 | 0.707 / 1.711 | PF 0.71 vs 1.71 atteso · mfe mediana 0.92R < primo TP 1.50R |
| BMTUSDT|gen_be64073c | watch | 4 | 0.142 / 2.843 | PF 0.14 vs 2.84 atteso · mfe mediana 0.51R < primo TP 1.50R |
| BANKUSDT|gen_7100bb59 | watch | 4 | 0.967 / 1.938 | PF 0.97 vs 1.94 atteso · mfe mediana 0.46R < primo TP 0.75R |
| MYXUSDT|gen_8931b93c | watch | 4 | 0.34 / 1.583 | PF 0.34 vs 1.58 atteso · mfe mediana 0.76R < primo TP 1.50R |
| SYRUPUSDT|gen_f3b97917 | watch | 3 | 1.697 / 2.064 | mfe mediana 1.06R < primo TP 2.00R |
| STXUSDT|gen_0aa0d29c | watch | 3 | 0.0 / 1.663 | PF 0.00 vs 1.66 atteso · mfe mediana 0.15R < primo TP 1.00R |
| HEMIUSDT|gen_acea368d | watch | 3 | 0.517 / 1.784 | PF 0.52 vs 1.78 atteso · mfe mediana 0.80R < primo TP 1.50R |
| HOMEUSDT|gen_467d9ee2 | watch | 3 | 0.449 / 1.617 | PF 0.45 vs 1.62 atteso · mfe mediana 0.58R < primo TP 1.00R |
| XPINUSDT|gen_f311acf9 | watch | 3 | 0.0 / 3.282 | PF 0.00 vs 3.28 atteso |
| SAHARAUSDT|gen_c934a6f7 | watch | 3 | 99.0 / 1.687 | mfe mediana 0.52R < primo TP 0.75R |
| UBUSDT|gen_92b77c39 | watch | 3 | 0.572 / 1.502 | PF 0.57 vs 1.50 atteso · mfe mediana 1.01R < primo TP 2.00R |
| JTOUSDT|gen_94062d5f | watch | 3 | 0.503 / 1.351 | PF 0.50 vs 1.35 atteso · mfe mediana 0.55R < primo TP 1.00R |
| SCRUSDT|gen_0e030446 | watch | 3 | 0.344 / 1.851 | PF 0.34 vs 1.85 atteso |
| TAUSDT|gen_6e8a4220 | watch | 2 | 0.282 / 2.152 | PF 0.28 vs 2.15 atteso · mfe mediana 0.61R < primo TP 1.00R |
| EIGENUSDT|gen_1b7827f3 | watch | 2 | 0.262 / 1.475 | PF 0.26 vs 1.48 atteso · mfe mediana 0.84R < primo TP 1.50R |
| BTRUSDT|gen_5a52c06b | watch | 2 | 0.566 / 1.784 | PF 0.57 vs 1.78 atteso |
| HYPEUSDT|gen_f19b67e8 | watch | 2 | 0.171 / 1.624 | PF 0.17 vs 1.62 atteso · mfe mediana 0.51R < primo TP 1.00R |
| IDOLUSDT|gen_5ad54558 | watch | 2 | 0.18 / 2.23 | PF 0.18 vs 2.23 atteso · mfe mediana 0.82R < primo TP 1.50R |
| USELESSUSDT|gen_e09c5203 | watch | 2 | 0.0 / 1.636 | PF 0.00 vs 1.64 atteso · mfe mediana 0.48R < primo TP 2.00R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 143 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (143 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 47 | 53% | +0.21% |
| 60.0–60.0 | 47 | 60% | -0.28% |
| 60.0–60.0 | 49 | 59% | +0.08% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
