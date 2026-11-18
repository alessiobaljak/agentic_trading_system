# 0759-18nov-stato-ribilancio-1000.req

_eseguito: 2026-11-18 04:21 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 64.7s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-18 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-18 04:19 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-18 03:25 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,702.69** su $10,000 (+7.03%) · costi $11.30 · funding pagato $-418.56
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-16
- ordini limite: 245 eseguiti su 245 · tutto a mercato sarebbe costato $39.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.2%, TRXUSDT +8.2%, XMRUSDT -7.7%, HYPEUSDT -7.4%, RENDERUSDT -6.7%, XLMUSDT +6.5%, ASTERUSDT -6.3%, POLUSDT +6.2%, BCHUSDT +6.0%, JTOUSDT -5.9%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-18 04:05 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$11,140.93** su $10,000 (+11.41%) · costi $31.11 · funding pagato $-400.82
- posizioni: 26 long, 30 short · ultimo ribilancio 2026-11-18
- ordini limite: 1385 eseguiti su 1392 · tutto a mercato sarebbe costato $86.56 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.0%, TRXUSDT +8.3%, XMRUSDT -7.2%, HYPEUSDT -6.7%, XLMUSDT +6.5%, WIFUSDT -6.5%, BCHUSDT +6.0%, POLUSDT +6.0%, RENDERUSDT -5.8%, ADAUSDT +5.6%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-18 04:09 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$11,166.64** su $10,000 (+11.67%) · costi $35.26 · funding pagato $-376.20
- posizioni: 31 long, 30 short · ultimo ribilancio 2026-11-18
- ordini limite: 1464 eseguiti su 1470 · tutto a mercato sarebbe costato $112.46 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.5%, XMRUSDT -7.5%, HYPEUSDT -7.0%, TRXUSDT +6.8%, PENDLEUSDT -6.8%, RENDERUSDT -6.0%, 1000SHIBUSDT +5.7%, JTOUSDT -5.6%, ASTERUSDT -5.4%, FARTCOINUSDT -5.3%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-18 04:14 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,396.26** su $10,000 (+13.96%) · costi $29.91 · funding pagato $-402.53
- posizioni: 26 long, 30 short · ultimo ribilancio 2026-11-18
- ordini limite: 1280 eseguiti su 1284 · tutto a mercato sarebbe costato $76.03 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.2%, TRXUSDT +8.2%, XMRUSDT -7.3%, HYPEUSDT -6.8%, WIFUSDT -6.6%, XLMUSDT +6.4%, BCHUSDT +5.9%, POLUSDT +5.9%, RENDERUSDT -5.9%, ADAUSDT +5.6%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-18 03:36 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-18 03:37 UTC)
- equity: **$1,033.31** su $1,000.00 (+3.33%) · posizioni 25 long, 27 short · ordini limite eseguiti 723 su 769 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,381.22
- ultima decisione 2026-11-18: 8 ordini, eseguiti a limite 7, a mercato 1; sotto il minimo 45 variazioni (8.3% del conto); rifiutati 3: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; UAIUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.88%, LITUSDT +3.34%, UAIUSDT -1.33%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -2.48% dal massimo
- margine (2026-11-18 03:37 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-18 03:37 UTC): 56 monete, scarto totale 13.8% del conto; oltre il 2%: LITUSDT -3.3%
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
| 2026-11-18 | -0.02% | -0.25% | +0.23% | +0.00% |

- dal 2026-11-09 (10 giorni): demo +3.83%, paper +6.46%; differenza media al giorno -0.257%, oscillazione 0.565%

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
| 2026-11-18 | +0.020% | +0.027% | +0.001% | +0.002% |

- sul demo, dal 2026-11-07 (12 giorni): funding incassato +19.49 USDT, commissioni pagate 1.42 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 57, peso 375 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 380
Dal 2026-11-13 00:00 a 2026-11-18 04:20 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 53 monete su 53

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-13 | 294.91 | 0.0857 | 0.0291% | 63% | 37% | 31 |
| 2026-11-14 | 68.00 | 0.0242 | 0.0355% | 26% | 74% | 6 |
| 2026-11-15 | 413.50 | 0.1077 | 0.0260% | 71% | 29% | 60 |
| 2026-11-16 | 683.85 | 0.1813 | 0.0265% | 67% | 33% | 52 |
| 2026-11-17 | 323.45 | 0.0882 | 0.0273% | 67% | 33% | 37 |
| 2026-11-18 | 43.45 | 0.0122 | 0.0281% | 73% | 27% | 8 |
| 6 giorni | 1,827.16 | 0.4993 | 0.0273% | 66% | 34% | 194 |
- controllo: commissioni dagli incassi 0.4993 USDT, dalle esecuzioni 0.4993 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-13 | +2.5725 | +0.7470 | +1.0759 | +0.5527 | +0.1968 | 49/52 |
| 2026-11-14 | +1.5334 | +0.4308 | +0.5596 | +0.4427 | +0.1003 | 50/53 |
| 2026-11-15 | +1.8414 | +0.5369 | +0.7643 | +0.3195 | +0.2206 | 48/51 |
| 2026-11-16 | +1.3306 | +0.3986 | +0.1989 | +0.3225 | +0.4106 | 49/52 |
| 2026-11-17 | +1.4479 | +0.7040 | +0.2906 | +0.1837 | +0.2697 | 52/56 |
| 2026-11-18 (in corso) | +0.2975 | +0.2069 | +0.0000 | +0.0000 | +0.0907 | —/56 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| XMRUSDT | +2.8810 | +1.0867 | +1.2415 | +0.5528 | +0.0000 | -7.21% |
| HUMAUSDT | +1.4207 | +0.5659 | +0.3891 | +0.4657 | +0.0000 | +1.56% |
| BMTUSDT | +0.6158 | +0.1166 | +0.2117 | +0.2875 | +0.0000 | +1.35% |
| LSKUSDT | +0.5997 | +0.2125 | +0.1890 | +0.1982 | +0.0000 | +2.72% |
| ERAUSDT | +0.5680 | +0.0808 | +0.0938 | +0.0817 | +0.3118 | +2.90% |
| BIRBUSDT | +0.5453 | +0.0299 | +0.1408 | +0.0575 | +0.3172 | +1.66% |
| INITUSDT | -0.3945 | -0.0210 | -0.0521 | -0.3214 | +0.0000 | +1.23% |
| ARIAUSDT | +0.2615 | +0.0347 | +0.0336 | +0.0424 | +0.1509 | -1.85% |
| 1000BONKUSDT | +0.2417 | +0.0743 | +0.0909 | +0.0765 | +0.0000 | +4.25% |
| ATOMUSDT | +0.2299 | +0.0752 | +0.0833 | +0.0

[... 33278 caratteri omessi (testa e coda conservate) ...]

04106 | 3 | 1.537 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
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
| recovery | 64 | 4.8% |
| trades | 6 | 0.5% |
| consistency | 17 | 1.3% |
| regime | 22 | 1.7% |
| total_return | 1207 | 91.4% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 242 | 0.7% |
| holdout | 153 | 0.5% |
| total_return | 26463 | 78.0% |
| trades | 936 | 2.8% |
| recovery | 2737 | 8.1% |
| regime | 2815 | 8.3% |
| consistency | 589 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-18 04:02 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: watch · 38 trade · PF vissuto 1.031 vs 2.02 atteso · mfe mediana 0.68R

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| MYXUSDT|gen_8931b93c | watch | 2 | 0.0 / 1.583 | PF 0.00 vs 1.58 atteso · mfe mediana 0.24R < primo TP 1.50R |
| HEMIUSDT|gen_c1f71d65 | watch | 2 | 0.829 / 1.54 | PF 0.83 vs 1.54 atteso |
| UBUSDT|gen_92b77c39 | watch | 2 | 0.178 / 1.502 | PF 0.18 vs 1.50 atteso · mfe mediana 1.20R < primo TP 2.00R |
| BMTUSDT|gen_be64073c | watch | 2 | 0.366 / 2.843 | PF 0.37 vs 2.84 atteso · mfe mediana 0.99R < primo TP 1.50R |
| JTOUSDT|gen_94062d5f | watch | 2 | 99.0 / 1.351 | mfe mediana 0.68R < primo TP 1.00R |
| PARTIUSDT|gen_64263ae7 | watch | 1 | 0.0 / 1.953 | PF 0.00 vs 1.95 atteso · mfe mediana 0.49R < primo TP 2.00R |
| VELVETUSDT|gen_e933160c | watch | 1 | 0.0 / 2.559 | PF 0.00 vs 2.56 atteso · mfe mediana 0.60R < primo TP 1.50R |
| SAHARAUSDT|gen_c934a6f7 | watch | 1 | 99.0 / 1.687 | mfe mediana 0.52R < primo TP 0.75R |
| AINUSDT|gen_d926b0fd | watch | 1 | 0.0 / 1.541 | PF 0.00 vs 1.54 atteso · mfe mediana 0.08R < primo TP 1.50R |
| TAUSDT|gen_543186c5 | watch | 1 | 99.0 / 2.012 | mfe mediana 1.00R < primo TP 2.00R |
| UBUSDT|gen_15837112 | watch | 1 | 0.0 / 1.678 | PF 0.00 vs 1.68 atteso · mfe mediana 0.41R < primo TP 1.50R |
| STXUSDT|gen_0aa0d29c | watch | 1 | 0.0 / 1.663 | PF 0.00 vs 1.66 atteso · mfe mediana 0.22R < primo TP 1.00R |
| IDUSDT|gen_6bc43e03 | watch | 1 | 0.0 / 1.483 | PF 0.00 vs 1.48 atteso |
| IDOLUSDT|gen_931ca7de | watch | 1 | 0.0 / 2.261 | PF 0.00 vs 2.26 atteso |
| CROSSUSDT|gen_4e6e1ae0 | watch | 1 | 99.0 / 2.69 | mfe mediana 1.00R < primo TP 2.00R |
| HEMIUSDT|gen_acea368d | watch | 1 | 99.0 / 1.784 | mfe mediana 0.80R < primo TP 1.50R |
| SCRUSDT|gen_c934a6f7 | watch | 1 | 0.0 / 1.524 | PF 0.00 vs 1.52 atteso · mfe mediana 0.39R < primo TP 2.00R |
| DEXEUSDT|gen_3d4be8c7 | watch | 1 | 0.0 / 1.545 | PF 0.00 vs 1.54 atteso · mfe mediana 0.31R < primo TP 1.50R |
| HYPEUSDT|gen_f19b67e8 | watch | 1 | 0.0 / 1.624 | PF 0.00 vs 1.62 atteso |
| TRUMPUSDT|gen_d16d1d02 | watch | 1 | 0.0 / 1.591 | PF 0.00 vs 1.59 atteso · mfe mediana 0.39R < primo TP 2.00R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 38 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (38 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 12 | 67% | -0.94% |
| 60.0–60.0 | 12 | 58% | -0.19% |
| 60.0–60.0 | 14 | 43% | +0.07% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-18 04:21 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,033.31 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -11.01/-11.04 · TRXUSDT +8.32/+8.68 · XMRUSDT -7.21/-7.21 · HYPEUSDT -6.74/-6.90 · XLMUSDT +6.51/+6.74 · WIFUSDT -6.45/-6.72
- BCHUSDT +6.03/+5.56 · POLUSDT +6.02/+5.98 · RENDERUSDT -5.77/-5.71 · ADAUSDT +5.65/+5.67 · SANDUSDT +5.39/+5.55 · JTOUSDT -5.36/-5.23
- NEARUSDT -4.80/-5.26 · ASTERUSDT -5.16/-5.05 · FARTCOINUSDT -5.11/-4.93 · SEIUSDT +4.93/+5.08 · XPLUSDT -4.74/-5.08 · ARBUSDT +4.52/+4.84
- ETHFIUSDT -4.60/-4.62 · 1000BONKUSDT +4.25/+4.62 · INJUSDT +4.04/+4.45 · APTUSDT +4.29/+4.35 · TIAUSDT +4.14/+4.30 · GRASSUSDT -3.87/-4.08
- TRUMPUSDT +3.72/+3.99 · WLDUSDT +3.60/+3.98 · JUPUSDT +3.96/+3.95 · 1000PEPEUSDT +3.61/+3.73 · OPUSDT +3.71/+3.62 · BEATUSDT -3.45/-3.60
- LITUSDT +3.34/+0.00 · ERAUSDT +2.90/+3.20 · USELESSUSDT -2.89/-2.93 · LSKUSDT +2.72/+2.63 · BEAMXUSDT -2.66/-2.65 · ICNTUSDT -2.46/-2.60
- ONUSDT -2.27/-2.31 · GTCUSDT +2.22/+2.20 · BRUSDT -2.15/-2.22 · BIRBUSDT +1.66/+1.91 · ARIAUSDT -1.85/-1.75 · APRUSDT -1.72/-1.75
- MAGMAUSDT -1.58/-1.65 · HUMAUSDT +1.56/+1.23 · DOODUSDT -1.44/-1.45 · BMTUSDT +1.35/+1.11 · UAIUSDT -1.33/+0.00 · INITUSDT +1.23/+1.31
- BULLAUSDT -1.08/-1.21 · IDOLUSDT -1.10/-1.13 · EVAAUSDT -0.88/+0.00 · AINUSDT -0.80/-0.81 · AGTUSDT -0.62/-0.65 · QUSDT -0.52/-0.51
- JCTUSDT -0.37/+0.00 · AKEUSDT +0.30/+0.25
- monete: paper 56, demo 52; esposizione lorda paper 200.0%, demo 198.0%; somma delle differenze 13.7% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 1,033.31 USDT, paper 11,140.93; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-16 00 | +0.0386% | +0.0247% | +0.0139% | 48/51 |
| 2026-11-16 08 | +0.0193% | +0.0308% | -0.0116% | 49/52 |
| 2026-11-16 16 | +0.0312% | +0.0243% | +0.0069% | 49/52 |
| 2026-11-16 altre | +0.0397% | +0.1414% | -0.1017% | 45/156 |
| 2026-11-17 00 | +0.0681% | +0.0256% | +0.0426% | 49/52 |
| 2026-11-17 08 | +0.0281% | +0.0189% | +0.0092% | 52/56 |
| 2026-11-17 16 | +0.0178% | +0.0157% | +0.0021% | 52/56 |
| 2026-11-17 altre | +0.0261% | +0.0793% | -0.0532% | 51/162 |
| 2026-11-18 00 | +0.0200% | +0.0117% | +0.0083% | 52/56 |
| 2026-11-18 altre | +0.0088% | +0.0148% | -0.0060% | 17/48 |

- regolamento 2026-11-18 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): LSKUSDT +0.0040/+0.0013 · HUMAUSDT +0.0037/+0.0007 · ONUSDT +0.0028/+0.0006 · 1000BONKUSDT +0.0019/— · JUPUSDT +0.0018/— · BEATUSDT +0.0018/+0.0010 · ERAUSDT +0.0011/+0.0011 · WLDUSDT +0.0008/+0.0007 · XMRUSDT +0.0007/+0.0007 · WLFIUSDT +0.0005/+0.0005 · NEARUSDT +0.0005/+0.0005 · ADAUSDT -0.0001/-0.0005
```
