# 0761-19nov-stato-ribilancio-1000.req

_eseguito: 2026-11-19 04:19 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 64.9s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-19 04:18 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-19 04:18 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-19 03:30 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,726.08** su $10,000 (+7.26%) · costi $11.30 · funding pagato $-434.67
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-16
- ordini limite: 245 eseguiti su 245 · tutto a mercato sarebbe costato $39.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.2%, TRXUSDT +8.2%, XMRUSDT -7.7%, HYPEUSDT -7.4%, RENDERUSDT -6.7%, XLMUSDT +6.5%, ASTERUSDT -6.3%, POLUSDT +6.2%, BCHUSDT +6.0%, JTOUSDT -5.9%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-19 04:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$11,000.82** su $10,000 (+10.01%) · costi $31.73 · funding pagato $-414.36
- posizioni: 28 long, 29 short · ultimo ribilancio 2026-11-19
- ordini limite: 1443 eseguiti su 1450 · tutto a mercato sarebbe costato $88.73 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.3%, TRXUSDT +7.7%, XMRUSDT -7.6%, HYPEUSDT -6.9%, 1000SHIBUSDT +6.5%, XLMUSDT +6.0%, RENDERUSDT -5.9%, JTOUSDT -5.6%, BCHUSDT +5.6%, POLUSDT +5.6%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-19 04:10 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,969.32** su $10,000 (+9.69%) · costi $36.03 · funding pagato $-387.26
- posizioni: 29 long, 28 short · ultimo ribilancio 2026-11-19
- ordini limite: 1526 eseguiti su 1532 · tutto a mercato sarebbe costato $115.17 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.4%, XMRUSDT -7.6%, TRXUSDT +7.4%, HYPEUSDT -7.0%, PENDLEUSDT -6.9%, 1000SHIBUSDT +6.2%, RENDERUSDT -5.9%, JTOUSDT -5.7%, ETCUSDT +5.6%, BCHUSDT +5.4%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-19 04:15 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,251.19** su $10,000 (+12.51%) · costi $30.60 · funding pagato $-416.27
- posizioni: 28 long, 29 short · ultimo ribilancio 2026-11-19
- ordini limite: 1338 eseguiti su 1342 · tutto a mercato sarebbe costato $78.43 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.7%, XMRUSDT -7.8%, TRXUSDT +7.4%, HYPEUSDT -7.1%, 1000SHIBUSDT +6.3%, RENDERUSDT -6.1%, XLMUSDT +5.8%, JTOUSDT -5.8%, BCHUSDT +5.4%, FARTCOINUSDT -5.4%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-19 03:47 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-19 03:46 UTC)
- equity: **$1,023.90** su $1,000.00 (+2.39%) · posizioni 26 long, 26 short · ordini limite eseguiti 736 su 782 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,371.81
- ultima decisione 2026-11-19: 13 ordini, eseguiti a limite 13, a mercato 0; sotto il minimo 41 variazioni (8.4% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 3: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; UAIUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.92%, LITUSDT +3.04%, UAIUSDT -1.39%, IRYSUSDT +0.37%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -3.37% dal massimo
- margine (2026-11-19 03:46 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-19 03:46 UTC): 56 monete, scarto totale 14.0% del conto; oltre il 2%: LITUSDT -3.0%
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
| 2026-11-19 | +0.06% | -0.01% | +0.06% | +0.00% |

- dal 2026-11-09 (11 giorni): demo +2.88%, paper +5.12%; differenza media al giorno -0.202%, oscillazione 0.574%

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
| 2026-11-19 | +0.030% | +0.042% | +0.006% | +0.006% |

- sul demo, dal 2026-11-07 (13 giorni): funding incassato +20.33 USDT, commissioni pagate 1.48 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 57, peso 375 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 270
Dal 2026-11-14 00:00 a 2026-11-19 04:18 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 53 monete su 53

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-14 | 68.00 | 0.0242 | 0.0355% | 26% | 74% | 6 |
| 2026-11-15 | 400.99 | 0.1077 | 0.0269% | 70% | 30% | 57 |
| 2026-11-16 | 638.93 | 0.1813 | 0.0284% | 64% | 36% | 51 |
| 2026-11-17 | 323.45 | 0.0882 | 0.0273% | 67% | 33% | 37 |
| 2026-11-18 | 43.45 | 0.0122 | 0.0281% | 73% | 27% | 8 |
| 2026-11-19 | 212.92 | 0.0603 | 0.0283% | 61% | 39% | 27 |
| 6 giorni | 1,687.73 | 0.4738 | 0.0281% | 65% | 35% | 186 |
- controllo: commissioni dagli incassi 0.4738 USDT, dalle esecuzioni 0.4738 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-14 | +1.5334 | +0.4308 | +0.5596 | +0.4427 | +0.1003 | 50/53 |
| 2026-11-15 | +1.8414 | +0.5369 | +0.7643 | +0.3195 | +0.2206 | 48/51 |
| 2026-11-16 | +1.3306 | +0.3986 | +0.1989 | +0.3225 | +0.4106 | 49/52 |
| 2026-11-17 | +1.4479 | +0.7040 | +0.2906 | +0.1837 | +0.2697 | 52/56 |
| 2026-11-18 | +0.7448 | +0.2069 | +0.0892 | +0.1967 | +0.2521 | 52/56 |
| 2026-11-19 (in corso) | +0.4114 | +0.3048 | +0.0000 | +0.0000 | +0.1065 | —/57 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| XMRUSDT | +1.7339 | +0.6332 | +0.7734 | +0.3273 | +0.0000 | -7.57% |
| HUMAUSDT | +1.2364 | +0.5537 | +0.2595 | +0.4232 | +0.0000 | +1.40% |
| LSKUSDT | +0.6738 | +0.2336 | +0.2256 | +0.2146 | +0.0000 | +2.60% |
| ERAUSDT | +0.5406 | +0.0896 | +0.0922 | +0.0626 | +0.2961 | +2.68% |
| INITUSDT | -0.5382 | -0.1208 | -0.2148 | -0.2026 | +0.0000 | +1.14% |
| BIRBUSDT | +0.4795 | +0.0348 | +0.1165 | +0.0496 | +0.2786 | +1.52% |
| BMTUSDT | +0.4272 | +0.1118 | +0.1991 | +0.1163 | +0.0000 | +1.25% |
| ARIAUSDT | +0.3150 | 

[... 32625 caratteri omessi (testa e coda conservate) ...]

keep=0.75 |
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
| total_return | 1207 | 91.4% |
| holdout | 1 | 0.1% |
| recovery | 64 | 4.8% |
| pf_ex_top | 3 | 0.2% |
| consistency | 17 | 1.3% |
| trades | 6 | 0.5% |
| regime | 22 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| total_return | 26463 | 78.0% |
| holdout | 153 | 0.5% |
| recovery | 2737 | 8.1% |
| pf_ex_top | 242 | 0.7% |
| consistency | 589 | 1.7% |
| regime | 2815 | 8.3% |
| trades | 936 | 2.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-19 04:03 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: watch · 20 trade · PF vissuto 1.077 vs 2.02 atteso · mfe mediana 0.77R

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| BMTUSDT|gen_be64073c | watch | 2 | 0.366 / 2.843 | PF 0.37 vs 2.84 atteso · mfe mediana 0.99R < primo TP 1.50R |
| UBUSDT|gen_92b77c39 | watch | 2 | 0.178 / 1.502 | PF 0.18 vs 1.50 atteso · mfe mediana 1.20R < primo TP 2.00R |
| TRUMPUSDT|gen_d16d1d02 | watch | 1 | 0.0 / 1.591 | PF 0.00 vs 1.59 atteso · mfe mediana 0.39R < primo TP 2.00R |
| JTOUSDT|gen_94062d5f | watch | 1 | 99.0 / 1.351 | mfe mediana 0.55R < primo TP 1.00R |
| EIGENUSDT|gen_1b7827f3 | watch | 1 | 99.0 / 1.475 | mfe mediana 0.84R < primo TP 1.50R |
| STXUSDT|gen_0aa0d29c | watch | 1 | 0.0 / 1.663 | PF 0.00 vs 1.66 atteso · mfe mediana 0.22R < primo TP 1.00R |
| SAHARAUSDT|gen_c934a6f7 | watch | 1 | 99.0 / 1.687 | mfe mediana 0.52R < primo TP 0.75R |
| SCRUSDT|gen_c934a6f7 | watch | 1 | 0.0 / 1.524 | PF 0.00 vs 1.52 atteso · mfe mediana 0.39R < primo TP 2.00R |
| PARTIUSDT|gen_64263ae7 | watch | 1 | 0.0 / 1.953 | PF 0.00 vs 1.95 atteso · mfe mediana 0.49R < primo TP 2.00R |
| IDOLUSDT|gen_931ca7de | watch | 1 | 0.0 / 2.261 | PF 0.00 vs 2.26 atteso |
| IDUSDT|gen_6bc43e03 | watch | 1 | 0.0 / 1.483 | PF 0.00 vs 1.48 atteso |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 20 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (20 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 6 | 50% | -3.05% |
| 60.0–60.0 | 6 | 83% | +1.16% |
| 60.0–60.0 | 8 | 50% | -0.32% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-19 04:19 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,023.90 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -12.31/-12.26 · TRXUSDT +7.67/+7.72 · XMRUSDT -7.57/-7.22 · HYPEUSDT -6.94/-6.85 · 1000SHIBUSDT +6.49/+6.52 · POLUSDT +5.56/+6.05
- XLMUSDT +5.96/+5.97 · RENDERUSDT -5.89/-5.65 · ADAUSDT +5.20/+5.68 · JTOUSDT -5.62/-5.24 · BCHUSDT +5.61/+5.54 · NEARUSDT -5.02/-5.32
- FARTCOINUSDT -5.25/-4.91 · XPLUSDT -4.96/-5.23 · ASTERUSDT -5.14/-4.86 · SANDUSDT +5.02/+5.11 · ETHFIUSDT -4.83/-5.00 · ARBUSDT +4.28/+4.77
- SEIUSDT +4.54/+4.55 · TIAUSDT +3.81/+4.35 · APTUSDT +3.92/+4.30 · GRASSUSDT -4.11/-4.26 · JUPUSDT +3.66/+4.08 · BRUSDT -4.03/-4.01
- WLDUSDT +3.55/+4.01 · 1000BONKUSDT +3.91/+3.94 · 1000PEPEUSDT +3.35/+3.74 · INJUSDT +3.66/+3.67 · OPUSDT +3.42/+3.63 · BEATUSDT -3.61/-3.57
- TRUMPUSDT +3.42/+3.50 · ERAUSDT +2.68/+3.17 · USELESSUSDT -3.03/-3.14 · LITUSDT +3.04/+0.00 · GTCUSDT +2.70/+2.90 · BEAMXUSDT -2.78/-2.44
- LSKUSDT +2.60/+2.67 · ICNTUSDT -2.48/-2.51 · ONUSDT -2.37/-2.50 · ARIAUSDT -2.11/-1.82 · BIRBUSDT +1.52/+1.92 · APRUSDT -1.80/-1.82
- MAGMAUSDT -1.64/-1.74 · DOODUSDT -1.50/-1.49 · HUMAUSDT +1.40/+1.47 · BULLAUSDT -1.12/-1.40 · UAIUSDT -1.39/+0.00 · INITUSDT +1.14/+1.27
- IDOLUSDT -1.15/-1.27 · BMTUSDT +1.25/+1.08 · EVAAUSDT -0.92/+0.00 · AINUSDT -0.84/-0.81 · AGTUSDT -0.65/-0.63 · QUSDT -0.55/-0.52
- JCTUSDT -0.38/+0.00 · IRYSUSDT +0.37/+0.00 · AKEUSDT +0.27/+0.26
- monete: paper 57, demo 52; esposizione lorda paper 200.0%, demo 198.3%; somma delle differenze 16.0% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 1,023.90 USDT, paper 11,000.82; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-17 00 | +0.0688% | +0.0259% | +0.0429% | 49/52 |
| 2026-11-17 08 | +0.0284% | +0.0192% | +0.0092% | 52/56 |
| 2026-11-17 16 | +0.0179% | +0.0159% | +0.0020% | 52/56 |
| 2026-11-17 altre | +0.0263% | +0.0803% | -0.0540% | 51/162 |
| 2026-11-18 00 | +0.0202% | +0.0119% | +0.0084% | 52/56 |
| 2026-11-18 08 | +0.0087% | +0.0140% | -0.0053% | 52/56 |
| 2026-11-18 16 | +0.0192% | +0.0118% | +0.0074% | 52/56 |
| 2026-11-18 altre | +0.0246% | +0.0703% | -0.0457% | 51/162 |
| 2026-11-19 00 | +0.0298% | +0.0147% | +0.0150% | 52/56 |
| 2026-11-19 altre | +0.0104% | +0.0273% | -0.0169% | 17/48 |

- regolamento 2026-11-19 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): HUMAUSDT +0.0132/+0.0013 · BULLAUSDT +0.0049/+0.0009 · INITUSDT +0.0047/+0.0009 · LSKUSDT +0.0029/+0.0015 · WIFUSDT -0.0024/— · ONUSDT +0.0023/— · XMRUSDT +0.0017/+0.0017 · BEATUSDT +0.0004/+0.0010 · WLDUSDT -0.0002/+0.0008 · OPUSDT -0.0004/+0.0008 · ERAUSDT +0.0004/+0.0007 · APTUSDT -0.0002/+0.0007
```
