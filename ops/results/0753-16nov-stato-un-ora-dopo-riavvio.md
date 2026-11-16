# 0753-16nov-stato-un-ora-dopo-riavvio.req

_eseguito: 2026-11-16 08:32 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 61.0s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-16 08:31 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-16 08:31 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-16 08:07 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,631.31** su $10,000 (+6.31%) · costi $11.30 · funding pagato $-385.80
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-16
- ordini limite: 245 eseguiti su 245 · tutto a mercato sarebbe costato $39.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.2%, TRXUSDT +8.2%, XMRUSDT -7.7%, HYPEUSDT -7.4%, RENDERUSDT -6.7%, XLMUSDT +6.5%, ASTERUSDT -6.3%, POLUSDT +6.2%, BCHUSDT +6.0%, JTOUSDT -5.9%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-16 08:11 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$11,093.44** su $10,000 (+10.93%) · costi $29.99 · funding pagato $-367.81
- posizioni: 24 long, 28 short · ultimo ribilancio 2026-11-16
- ordini limite: 1271 eseguiti su 1278 · tutto a mercato sarebbe costato $82.62 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.3%, TRXUSDT +8.9%, XMRUSDT -7.1%, XLMUSDT +7.1%, HYPEUSDT -6.9%, POLUSDT +6.7%, WIFUSDT -6.7%, BCHUSDT +6.5%, RENDERUSDT -6.2%, ATOMUSDT +5.9%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-16 08:16 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$11,082.34** su $10,000 (+10.82%) · costi $33.87 · funding pagato $-344.30
- posizioni: 26 long, 29 short · ultimo ribilancio 2026-11-16
- ordini limite: 1346 eseguiti su 1351 · tutto a mercato sarebbe costato $108.38 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.6%, TRXUSDT +8.3%, XMRUSDT -7.3%, HYPEUSDT -7.0%, PENDLEUSDT -6.8%, RENDERUSDT -6.4%, POLUSDT +6.3%, BCHUSDT +6.1%, ASTERUSDT -5.9%, ADAUSDT +5.6%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-16 08:20 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,334.47** su $10,000 (+13.34%) · costi $28.70 · funding pagato $-368.94
- posizioni: 24 long, 28 short · ultimo ribilancio 2026-11-16
- ordini limite: 1166 eseguiti su 1170 · tutto a mercato sarebbe costato $71.80 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.3%, TRXUSDT +8.9%, XMRUSDT -7.1%, XLMUSDT +7.1%, HYPEUSDT -6.9%, POLUSDT +6.7%, WIFUSDT -6.7%, BCHUSDT +6.5%, RENDERUSDT -6.2%, ATOMUSDT +5.9%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-16 08:24 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-16 08:25 UTC)
- equity: **$1,029.39** su $1,000.00 (+2.94%) · posizioni 24 long, 25 short · ordini limite eseguiti 704 su 747 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,377.29
- ultima decisione 2026-11-16: 33 ordini, eseguiti a limite 31, a mercato 2; sotto il minimo 26 variazioni (6.6% del conto); rifiutati 2: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; UAIUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.90%, UAIUSDT -1.36%
- stop sul conto: si chiude tutto sotto $673.38 (il più alto fra −35% dal massimo, $1,035.97, e il 65% del capitale di partenza); ora -0.64% dal massimo
- margine (2026-11-16 08:25 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-16 08:25 UTC): 52 monete, scarto totale 9.0% del conto; nessuna moneta oltre il 2%
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
| 2026-11-16 | +0.17% | +0.63% | -0.46% | +0.00% |

- dal 2026-11-09 (8 giorni): demo +3.44%, paper +6.01%; differenza media al giorno -0.315%, oscillazione 0.598%

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
| 2026-11-16 | +0.075% | +0.091% | +0.018% | +0.017% |

- sul demo, dal 2026-11-07 (10 giorni): funding incassato +17.27 USDT, commissioni pagate 1.32 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 54, peso 360 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 220
Dal 2026-11-11 00:00 a 2026-11-16 08:31 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 50 monete su 50

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-11 | 111.32 | 0.0266 | 0.0239% | 83% | 17% | 15 |
| 2026-11-12 | 95.67 | 0.0250 | 0.0261% | 80% | 20% | 18 |
| 2026-11-13 | 294.91 | 0.0857 | 0.0291% | 63% | 37% | 31 |
| 2026-11-14 | 68.00 | 0.0242 | 0.0355% | 26% | 74% | 6 |
| 2026-11-15 | 385.53 | 0.1077 | 0.0279% | 69% | 31% | 55 |
| 2026-11-16 | 680.64 | 0.1813 | 0.0266% | 67% | 33% | 52 |
| 6 giorni | 1,636.08 | 0.4505 | 0.0275% | 67% | 33% | 177 |
- controllo: commissioni dagli incassi 0.4505 USDT, dalle esecuzioni 0.4505 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-11 | +2.0138 | +0.6612 | +0.6133 | +0.4609 | +0.2784 | 51/55 |
| 2026-11-12 | +1.9193 | +0.5532 | +0.5668 | +0.6022 | +0.1972 | 50/54 |
| 2026-11-13 | +2.5725 | +0.7470 | +1.0759 | +0.5527 | +0.1968 | 49/52 |
| 2026-11-14 | +1.5334 | +0.4308 | +0.5596 | +0.4427 | +0.1003 | 50/53 |
| 2026-11-15 | +1.8414 | +0.5369 | +0.7643 | +0.3195 | +0.2206 | 48/51 |
| 2026-11-16 (in corso) | +0.7674 | +0.3986 | +0.1989 | +0.0000 | +0.1698 | 49/52 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| XMRUSDT | +3.3286 | +1.0606 | +1.4155 | +0.8525 | +0.0000 | -7.14% |
| HUMAUSDT | +0.8754 | +0.2280 | +0.3467 | +0.3007 | +0.0000 | +2.74% |
| ERAUSDT | +0.8449 | +0.0671 | +0.1420 | +0.1431 | +0.4927 | +2.99% |
| INITUSDT | +0.8213 | +0.4097 | +0.4266 | -0.0151 | +0.0000 | +1.31% |
| BMTUSDT | +0.6423 | +0.1367 | +0.2187 | +0.2869 | +0.0000 | +1.44% |
| LSKUSDT | +0.5028 | +0.1598 | +0.1800 | +0.1630 | +0.0000 | +2.63% |
| WUSDT | +0.2404 | +0.0720 | +0.0916 | +0.0769 | +0.0000 | — |
| GTCUSDT | +0.2389 | +0.0676 | +0.0939 | +0.0774 | +0.0000 | +2.13% |
| ATOMUSDT | +0.2255 | +0.0664 | +0.0851 | +0.0739 | +0.0000 | +5.92% |
| AEROUSDT | +0.1948 | +0.0908 | +0.1074 | -0.0033 | +0.0000 | +4.66% |

- monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): 龙虾USDT rifiutata 5 giorni dal 2026-11-11, IRYSUSDT mancante sul demo 2 giorni dal 2026-11-11, EVAAUSDT rifiutata 1 giorni dal 2026-11-16, UAIUSDT rifiutata 1 giorni dal 2026-11-16
- nel paper G1 di oggi ma senza funding sul demo dalle 0

[... 31772 caratteri omessi (testa e coda conservate) ...]

lts=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.5 |
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
| total_return | 1207 | 91.4% |
| trades | 6 | 0.5% |
| regime | 22 | 1.7% |
| holdout | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 589 | 1.7% |
| pf_ex_top | 242 | 0.7% |
| total_return | 26463 | 78.0% |
| recovery | 2737 | 8.1% |
| trades | 936 | 2.8% |
| regime | 2815 | 8.3% |
| holdout | 153 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-16 08:05 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: drift · 96 trade · PF vissuto 0.846 vs 2.02 atteso · mfe mediana 0.66R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.85 vs 2.02 atteso · mfe mediana 0.66R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| TRUMPUSDT|gen_d16d1d02 | watch | 5 | 3.035 / 1.591 | mfe mediana 1.11R < primo TP 2.00R |
| MYXUSDT|gen_8931b93c | watch | 4 | 0.34 / 1.583 | PF 0.34 vs 1.58 atteso · mfe mediana 0.76R < primo TP 1.50R |
| STXUSDT|gen_0aa0d29c | watch | 3 | 0.0 / 1.663 | PF 0.00 vs 1.66 atteso · mfe mediana 0.15R < primo TP 1.00R |
| SAHARAUSDT|gen_c934a6f7 | watch | 3 | 99.0 / 1.687 | mfe mediana 0.52R < primo TP 0.75R |
| SCRUSDT|gen_0e030446 | watch | 3 | 0.344 / 1.851 | PF 0.34 vs 1.85 atteso |
| IDOLUSDT|gen_5ad54558 | watch | 2 | 0.18 / 2.23 | PF 0.18 vs 2.23 atteso · mfe mediana 0.82R < primo TP 1.50R |
| HEMIUSDT|gen_c1f71d65 | watch | 2 | 0.829 / 1.54 | PF 0.83 vs 1.54 atteso |
| RENDERUSDT|gen_b028553e | watch | 2 | 0.0 / 1.617 | PF 0.00 vs 1.62 atteso · mfe mediana 0.59R < primo TP 1.50R |
| BMTUSDT|gen_be64073c | watch | 2 | 0.366 / 2.843 | PF 0.37 vs 2.84 atteso · mfe mediana 0.99R < primo TP 1.50R |
| BTRUSDT|gen_5a52c06b | watch | 2 | 0.566 / 1.784 | PF 0.57 vs 1.78 atteso |
| JTOUSDT|gen_94062d5f | watch | 2 | 99.0 / 1.351 | mfe mediana 0.68R < primo TP 1.00R |
| UBUSDT|gen_92b77c39 | watch | 2 | 0.178 / 1.502 | PF 0.18 vs 1.50 atteso · mfe mediana 1.20R < primo TP 2.00R |
| TAUSDT|gen_01fbe76f | watch | 2 | 0.161 / 1.711 | PF 0.16 vs 1.71 atteso · mfe mediana 0.79R < primo TP 1.50R |
| EIGENUSDT|gen_1b7827f3 | watch | 2 | 0.262 / 1.475 | PF 0.26 vs 1.48 atteso · mfe mediana 0.84R < primo TP 1.50R |
| SYRUPUSDT|gen_f3b97917 | watch | 2 | 0.744 / 2.064 | PF 0.74 vs 2.06 atteso · mfe mediana 1.06R < primo TP 2.00R |
| PARTIUSDT|gen_64263ae7 | watch | 2 | 0.597 / 1.953 | PF 0.60 vs 1.95 atteso · mfe mediana 1.03R < primo TP 2.00R |
| TAUSDT|gen_543186c5 | watch | 1 | 99.0 / 2.012 | mfe mediana 1.00R < primo TP 2.00R |
| KERNELUSDT|gen_96ed157e | watch | 1 | 0.0 / 3.627 | PF 0.00 vs 3.63 atteso · mfe mediana 0.02R < primo TP 2.00R |
| TAUSDT|gen_6e8a4220 | watch | 1 | 0.0 / 2.152 | PF 0.00 vs 2.15 atteso · mfe mediana 0.41R < primo TP 1.00R |
| BANKUSDT|gen_7100bb59 | watch | 1 | 0.0 / 1.938 | PF 0.00 vs 1.94 atteso · mfe mediana 0.10R < primo TP 0.75R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 96 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (96 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 32 | 59% | -0.32% |
| 60.0–60.0 | 32 | 50% | +0.34% |
| 60.0–60.0 | 32 | 59% | -0.12% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-16 08:32 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,029.39 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -11.35/-11.05 · TRXUSDT +8.90/+8.56 · XLMUSDT +7.06/+7.37 · XMRUSDT -7.14/-6.95 · HYPEUSDT -6.89/-6.68 · POLUSDT +6.69/+6.78
- WIFUSDT -6.67/-6.63 · BCHUSDT +6.48/+5.52 · ASTERUSDT -5.80/-6.31 · RENDERUSDT -6.23/-6.13 · ATOMUSDT +5.92/+6.12 · JTOUSDT -5.47/-5.38
- SEIUSDT +5.32/+5.06 · FARTCOINUSDT -5.21/-4.64 · SANDUSDT +5.09/+4.99 · NEARUSDT -5.05/-4.94 · ARBUSDT +4.72/+4.92 · XPLUSDT -4.89/-4.76
- ETHFIUSDT -4.81/-4.65 · JUPUSDT +4.71/+4.66 · AEROUSDT +4.66/+4.34 · 1000BONKUSDT +4.56/+4.51 · APTUSDT +4.52/+4.54 · TIAUSDT +4.39/+4.26
- GRASSUSDT -4.05/-4.07 · TRUMPUSDT +4.01/+3.88 · WLDUSDT +3.87/+4.00 · 1000PEPEUSDT +3.80/+3.69 · BEATUSDT -3.56/-3.49 · ERAUSDT +2.99/+2.92
- USELESSUSDT -2.97/-2.42 · BEAMXUSDT -2.73/-2.92 · HUMAUSDT +2.74/+2.54 · LSKUSDT +2.63/+2.64 · ONUSDT -2.38/-2.41 · BRUSDT -2.17/-2.05
- GTCUSDT +2.13/+2.13 · BIRBUSDT +1.76/+2.02 · ARIAUSDT -1.81/-1.76 · APRUSDT -1.65/-1.29 · MAGMAUSDT -1.64/-1.16 · DOODUSDT -1.47/-1.43
- BMTUSDT +1.44/+1.08 · UAIUSDT -1.36/+0.00 · INITUSDT +1.31/+1.26 · BULLAUSDT -1.18/-0.53 · IDOLUSDT -1.12/-1.09 · EVAAUSDT -0.90/+0.00
- AGTUSDT -0.62/-0.14 · QUSDT -0.49/-0.49 · JCTUSDT -0.37/+0.00 · AKEUSDT +0.32/+0.28
- monete: paper 52, demo 49; esposizione lorda paper 200.0%, demo 191.4%; somma delle differenze 12.5% del conto
```
