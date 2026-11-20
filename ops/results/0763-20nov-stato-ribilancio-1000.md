# 0763-20nov-stato-ribilancio-1000.req

_eseguito: 2026-11-20 04:20 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 66.8s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-20 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-20 04:18 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-20 03:37 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,591.09** su $10,000 (+5.91%) · costi $11.30 · funding pagato $-452.45
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-16
- ordini limite: 245 eseguiti su 245 · tutto a mercato sarebbe costato $39.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.2%, TRXUSDT +8.2%, XMRUSDT -7.7%, HYPEUSDT -7.4%, RENDERUSDT -6.7%, XLMUSDT +6.5%, ASTERUSDT -6.3%, POLUSDT +6.2%, BCHUSDT +6.0%, JTOUSDT -5.9%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-20 04:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,887.14** su $10,000 (+8.87%) · costi $32.18 · funding pagato $-433.04
- posizioni: 27 long, 30 short · ultimo ribilancio 2026-11-20
- ordini limite: 1501 eseguiti su 1508 · tutto a mercato sarebbe costato $90.30 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.1%, TRXUSDT +8.0%, XMRUSDT -7.2%, 1000SHIBUSDT +6.9%, HYPEUSDT -6.6%, XLMUSDT +6.3%, BCHUSDT +5.9%, JTOUSDT -5.8%, RENDERUSDT -5.7%, ADAUSDT +5.5%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-20 04:11 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,946.24** su $10,000 (+9.46%) · costi $36.98 · funding pagato $-405.38
- posizioni: 28 long, 27 short · ultimo ribilancio 2026-11-20
- ordini limite: 1585 eseguiti su 1591 · tutto a mercato sarebbe costato $118.47 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -13.7%, XMRUSDT -8.2%, TRXUSDT +7.7%, HYPEUSDT -7.5%, JTOUSDT -6.6%, RENDERUSDT -6.4%, ETCUSDT +6.0%, FARTCOINUSDT -5.7%, BCHUSDT +5.7%, POLUSDT +5.6%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-20 04:14 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,163.87** su $10,000 (+11.64%) · costi $31.08 · funding pagato $-434.95
- posizioni: 27 long, 30 short · ultimo ribilancio 2026-11-20
- ordini limite: 1396 eseguiti su 1400 · tutto a mercato sarebbe costato $80.13 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.4%, TRXUSDT +7.8%, XMRUSDT -7.4%, HYPEUSDT -6.8%, 1000SHIBUSDT +6.7%, XLMUSDT +6.1%, JTOUSDT -5.9%, RENDERUSDT -5.8%, BCHUSDT +5.7%, ADAUSDT +5.4%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-20 03:54 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-20 03:53 UTC)
- equity: **$1,013.88** su $1,000.00 (+1.39%) · posizioni 25 long, 27 short · ordini limite eseguiti 742 su 789 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,361.79
- ultima decisione 2026-11-20: 7 ordini, eseguiti a limite 6, a mercato 1; sotto il minimo 47 variazioni (8.7% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 3: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; UAIUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.87%, LITUSDT +3.29%, UAIUSDT -1.33%, IRYSUSDT +0.38%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -4.31% dal massimo
- margine (2026-11-20 03:53 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-20 03:53 UTC): 56 monete, scarto totale 13.9% del conto; oltre il 2%: LITUSDT -3.1%
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
| 2026-11-20 | +0.19% | +0.09% | +0.10% | +0.00% |

- dal 2026-11-09 (12 giorni): demo +1.88%, paper +4.04%; differenza media al giorno -0.180%, oscillazione 0.553%

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
| 2026-11-20 | +0.026% | +0.057% | +0.003% | +0.004% |

- sul demo, dal 2026-11-07 (14 giorni): funding incassato +21.91 USDT, commissioni pagate 1.50 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 58, peso 380 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 120
Dal 2026-11-15 00:00 a 2026-11-20 04:19 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 54 monete su 54

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-15 | 400.99 | 0.1077 | 0.0269% | 70% | 30% | 57 |
| 2026-11-16 | 638.93 | 0.1813 | 0.0284% | 64% | 36% | 51 |
| 2026-11-17 | 323.45 | 0.0882 | 0.0273% | 67% | 33% | 37 |
| 2026-11-18 | 43.45 | 0.0122 | 0.0281% | 73% | 27% | 8 |
| 2026-11-19 | 212.92 | 0.0603 | 0.0283% | 61% | 39% | 27 |
| 2026-11-20 | 110.20 | 0.0255 | 0.0232% | 89% | 11% | 21 |
| 6 giorni | 1,729.94 | 0.4752 | 0.0275% | 68% | 32% | 201 |
- controllo: commissioni dagli incassi 0.4752 USDT, dalle esecuzioni 0.4752 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-15 | +1.8414 | +0.5369 | +0.7643 | +0.3195 | +0.2206 | 48/51 |
| 2026-11-16 | +1.3306 | +0.3986 | +0.1989 | +0.3225 | +0.4106 | 49/52 |
| 2026-11-17 | +1.4479 | +0.7040 | +0.2906 | +0.1837 | +0.2697 | 52/56 |
| 2026-11-18 | +0.7448 | +0.2069 | +0.0892 | +0.1967 | +0.2521 | 52/56 |
| 2026-11-19 | +1.6187 | +0.3048 | +0.4174 | +0.4832 | +0.4132 | 52/57 |
| 2026-11-20 (in corso) | +0.3932 | +0.2605 | +0.0000 | +0.0000 | +0.1327 | —/57 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| HUMAUSDT | +1.4193 | +0.6494 | +0.2754 | +0.4945 | +0.0000 | +1.43% |
| XMRUSDT | +1.1286 | +0.4092 | +0.5398 | +0.1796 | +0.0000 | -7.21% |
| LSKUSDT | +0.6998 | +0.2400 | +0.2455 | +0.2143 | +0.0000 | +2.70% |
| BIRBUSDT | +0.5929 | +0.0341 | +0.1245 | +0.0631 | +0.3712 | +1.58% |
| ERAUSDT | +0.4744 | +0.0695 | +0.0792 | +0.0587 | +0.2670 | +2.98% |
| ARIAUSDT | +0.4274 | +0.0627 | +0.0648 | +0.0744 | +0.2255 | -2.32%

[... 31496 caratteri omessi (testa e coda conservate) ...]

fit_lock_keep=0.65 |
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
| recovery | 64 | 4.8% |
| consistency | 17 | 1.3% |
| holdout | 1 | 0.1% |
| trades | 6 | 0.5% |
| total_return | 1207 | 91.4% |
| pf_ex_top | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 26463 | 78.0% |
| recovery | 2737 | 8.1% |
| regime | 2815 | 8.3% |
| holdout | 153 | 0.5% |
| trades | 936 | 2.8% |
| consistency | 589 | 1.7% |
| pf_ex_top | 242 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-20 04:00 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: watch · 2 trade · PF vissuto 0.676 vs 2.02 atteso · mfe mediana 0.77R

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| PARTIUSDT|gen_64263ae7 | watch | 1 | 0.0 / 1.953 | PF 0.00 vs 1.95 atteso · mfe mediana 0.49R < primo TP 2.00R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 2 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (2 trade, confidenza 60-60)

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-20 04:20 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,013.88 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -12.11/-11.90 · TRXUSDT +7.97/+7.77 · XMRUSDT -7.21/-7.12 · 1000SHIBUSDT +6.88/+6.43 · HYPEUSDT -6.64/-6.74 · XLMUSDT +6.25/+5.85
- BCHUSDT +5.86/+5.55 · JTOUSDT -5.77/-5.55 · RENDERUSDT -5.65/-5.40 · ADAUSDT +5.49/+5.61 · SANDUSDT +5.19/+4.96 · FARTCOINUSDT -5.05/-4.71
- ASTERUSDT -4.89/-4.63 · NEARUSDT -4.78/-4.80 · XPLUSDT -4.74/-4.61 · SEIUSDT +4.73/+4.37 · ETHFIUSDT -4.67/-4.67 · ARBUSDT +4.47/+4.43
- APTUSDT +4.37/+4.03 · TIAUSDT +3.99/+4.19 · 1000BONKUSDT +4.13/+3.76 · GRASSUSDT -3.91/-4.11 · WLDUSDT +4.10/+3.77 · JUPUSDT +3.90/+3.62
- INJUSDT +3.85/+3.55 · BRUSDT -3.84/-3.59 · 1000PEPEUSDT +3.68/+3.56 · BEATUSDT -3.44/-3.68 · TRUMPUSDT +3.63/+3.37 · OPUSDT +3.62/+3.49
- LITUSDT +3.29/+0.00 · ERAUSDT +2.98/+3.18 · GTCUSDT +2.77/+2.97 · USELESSUSDT -2.96/-2.96 · LSKUSDT +2.70/+2.65 · DOODUSDT -2.68/-2.55
- BEAMXUSDT -2.64/-2.35 · ONUSDT -2.27/-2.62 · ARIAUSDT -2.32/-1.93 · ICNTUSDT -2.25/-2.22 · PARTIUSDT -2.20/-2.14 · BIRBUSDT +1.58/+1.94
- MAGMAUSDT -1.57/-1.80 · APRUSDT -1.72/-1.79 · HUMAUSDT +1.43/+1.62 · UAIUSDT -1.33/+0.00 · IDOLUSDT -1.10/-1.32 · BMTUSDT +1.30/+1.16
- INITUSDT +1.18/+1.27 · BULLAUSDT -1.07/-1.19 · EVAAUSDT -0.87/+0.00 · AINUSDT -0.80/-0.81 · AGTUSDT -0.63/-0.59 · QUSDT -0.52/-0.51
- JCTUSDT -0.39/+0.00 · IRYSUSDT +0.38/+0.00 · AKEUSDT +0.29/+0.27
- monete: paper 57, demo 52; esposizione lorda paper 200.0%, demo 189.6%; somma delle differenze 16.2% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 1,013.88 USDT, paper 10,887.14; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-18 00 | +0.0204% | +0.0120% | +0.0084% | 52/56 |
| 2026-11-18 08 | +0.0088% | +0.0142% | -0.0054% | 52/56 |
| 2026-11-18 16 | +0.0194% | +0.0119% | +0.0075% | 52/56 |
| 2026-11-18 altre | +0.0249% | +0.0710% | -0.0462% | 51/162 |
| 2026-11-19 00 | +0.0301% | +0.0149% | +0.0152% | 52/56 |
| 2026-11-19 08 | +0.0412% | +0.0160% | +0.0252% | 52/57 |
| 2026-11-19 16 | +0.0477% | +0.0213% | +0.0263% | 52/57 |
| 2026-11-19 altre | +0.0408% | +0.1045% | -0.0637% | 51/162 |
| 2026-11-20 00 | +0.0257% | +0.0229% | +0.0028% | 52/57 |
| 2026-11-20 altre | +0.0131% | +0.0346% | -0.0215% | 17/48 |

- regolamento 2026-11-20 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): GTCUSDT +0.0056/+0.0026 · HUMAUSDT +0.0041/— · IRYSUSDT +0.0000/+0.0033 · BMTUSDT +0.0030/+0.0015 · ONUSDT +0.0025/— · RENDERUSDT -0.0022/— · ARIAUSDT +0.0020/— · INITUSDT +0.0018/+0.0014 · BIRBUSDT +0.0006/+0.0015 · 1000PEPEUSDT +0.0014/+0.0010 · LSKUSDT +0.0014/+0.0009 · BEATUSDT +0.0011/+0.0012 · WLDUSDT +0.0005/+0.0012 · EVAAUSDT +0.0000/+0.0008
```
