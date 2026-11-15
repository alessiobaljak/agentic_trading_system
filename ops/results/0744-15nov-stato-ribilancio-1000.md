# 0744-15nov-stato-ribilancio-1000.req

_eseguito: 2026-11-15 04:20 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 54.5s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-15 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-15 04:19 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-15 03:51 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,462.24** su $10,000 (+4.62%) · costi $8.88 · funding pagato $-363.26
- posizioni: 30 long, 25 short · ultimo ribilancio 2026-11-09
- ordini limite: 179 eseguiti su 179 · tutto a mercato sarebbe costato $30.86 · in attesa del controllo dell'ora: 0
- pesi maggiori: ASTERUSDT -10.4%, WLFIUSDT -9.3%, TRXUSDT +8.0%, XRPUSDT -8.0%, XMRUSDT -8.0%, XLMUSDT +6.6%, HYPEUSDT -6.1%, POLUSDT +6.1%, DOTUSDT +6.1%, ATOMUSDT +6.0%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-15 04:05 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$11,039.17** su $10,000 (+10.39%) · costi $28.14 · funding pagato $-343.53
- posizioni: 25 long, 26 short · ultimo ribilancio 2026-11-15
- ordini limite: 1209 eseguiti su 1216 · tutto a mercato sarebbe costato $76.15 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -9.5%, TRXUSDT +8.7%, XRPUSDT -7.5%, XLMUSDT +7.3%, POLUSDT +6.7%, BCHUSDT +6.7%, XMRUSDT -6.2%, HYPEUSDT -6.0%, ATOMUSDT +6.0%, TAOUSDT -5.7%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-15 04:09 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$10,977.85** su $10,000 (+9.78%) · costi $32.26 · funding pagato $-320.98
- posizioni: 29 long, 24 short · ultimo ribilancio 2026-11-15
- ordini limite: 1282 eseguiti su 1287 · tutto a mercato sarebbe costato $102.73 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.2%, TRXUSDT +7.5%, XMRUSDT -7.3%, HYPEUSDT -7.0%, PENDLEUSDT -6.8%, WIFUSDT -6.6%, RENDERUSDT -6.2%, MUBARAKUSDT -5.9%, POLUSDT +5.7%, ASTERUSDT -5.7%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-15 04:16 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,280.21** su $10,000 (+12.80%) · costi $26.73 · funding pagato $-343.71
- posizioni: 25 long, 26 short · ultimo ribilancio 2026-11-15
- ordini limite: 1104 eseguiti su 1108 · tutto a mercato sarebbe costato $64.88 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -9.1%, TRXUSDT +9.1%, XLMUSDT +7.6%, XRPUSDT -7.2%, POLUSDT +7.0%, BCHUSDT +6.9%, ATOMUSDT +6.2%, XMRUSDT -6.0%, HYPEUSDT -5.8%, SEIUSDT +5.5%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-15 04:01 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-15 04:18 UTC)
- equity: **$1,027.58** su $1,000.00 (+2.76%) · posizioni 25 long, 23 short · ordini limite eseguiti 673 su 714 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,375.49
- ultima decisione 2026-11-15: 40 ordini, eseguiti a limite 38, a mercato 2; sotto il minimo 13 variazioni (5.5% del conto); rifiutati 1: 龙虾USDT POST /fapi/v1/order: 400 {"code":-1121,"msg":"Invalid symbol."}
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): 龙虾USDT -3.31%
- stop sul conto: si chiude tutto sotto $671.97 (il più alto fra −35% dal massimo, $1,033.80, e il 65% del capitale di partenza); ora -0.60% dal massimo
- margine (2026-11-15 04:18 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-15 04:18 UTC): 51 monete, scarto totale 9.4% del conto; oltre il 2%: 龙虾USDT +3.5%
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
| 2026-11-15 | -0.28% | -0.45% | +0.17% | +0.00% |

- dal 2026-11-09 (7 giorni): demo +3.25%, paper +5.49%; differenza media al giorno -0.315%, oscillazione 0.622%

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
| 2026-11-15 | +0.060% | +0.039% | +0.010% | +0.010% |

- sul demo, dal 2026-11-07 (9 giorni): funding incassato +15.27 USDT, commissioni pagate 1.13 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- spento: nessuno stato scritto (il bot non lo ha ancora fatto girare)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 48, peso 330 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 95
Dal 2026-11-10 00:00 a 2026-11-15 04:19 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 44 monete su 44

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-10 | 113.14 | 0.0421 | 0.0372% | 43% | 57% | 8 |
| 2026-11-11 | 111.32 | 0.0266 | 0.0239% | 83% | 17% | 15 |
| 2026-11-12 | 95.67 | 0.0250 | 0.0261% | 80% | 20% | 18 |
| 2026-11-13 | 294.91 | 0.0857 | 0.0291% | 63% | 37% | 31 |
| 2026-11-14 | 68.00 | 0.0242 | 0.0355% | 26% | 74% | 6 |
| 2026-11-15 | 385.53 | 0.1077 | 0.0279% | 69% | 31% | 55 |
| 6 giorni | 1,068.58 | 0.3113 | 0.0291% | 64% | 36% | 133 |
- controllo: commissioni dagli incassi 0.3113 USDT, dalle esecuzioni 0.3113 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-10 | +2.7297 | +1.0536 | +0.8350 | +0.7082 | +0.1328 | 51/56 |
| 2026-11-11 | +2.0138 | +0.6612 | +0.6133 | +0.4609 | +0.2784 | 51/55 |
| 2026-11-12 | +1.9193 | +0.5532 | +0.5668 | +0.6022 | +0.1972 | 50/54 |
| 2026-11-13 | +2.5725 | +0.7470 | +1.0759 | +0.5527 | +0.1968 | 49/52 |
| 2026-11-14 | +1.5334 | +0.4308 | +0.5596 | +0.4427 | +0.1003 | 50/53 |
| 2026-11-15 (in corso) | +0.6122 | +0.5369 | +0.0000 | +0.0000 | +0.0753 | —/51 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| XMRUSDT | +2.4464 | +0.7887 | +0.9313 | +0.7264 | +0.0000 | -6.25% |
| INITUSDT | +2.0213 | +0.9260 | +0.6867 | +0.4086 | +0.0000 | +1.28% |
| HUMAUSDT | +1.2096 | +0.4365 | +0.4464 | +0.3267 | +0.0000 | +2.63% |
| ERAUSDT | +0.8151 | +0.0632 | +0.1423 | +0.1439 | +0.4657 | +2.93% |
| BMTUSDT | +0.6527 | +0.1369 | +0.2233 | +0.2925 | +0.0000 | +1.41% |
| AEROUSDT | +0.4958 | +0.1650 | +0.2308 | +0.1001 | +0.0000 | +4.53% |
| LSKUSDT | +0.4354 | +0.1837 | +0.1551 | +0.0966 | +0.0000 | +2.62% |
| GTCUSDT | +0.3481 | +0.1305 | +0.1296 | +0.0879 | +0.0000 | +2.09% |
| ATOMUSDT | +0.1898 | +0.0479 | +0.0786 | +0.0634 | +0.0000 | +5.95% |
| JUPUSDT | +0.1859 | +0.0522 | +0.0485 | +0.0853 | +0.0000 | +4.86% |

- monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): 龙虾USDT rifiutata 6 giorni dal 2026-11-10, IRYSUSDT mancante sul demo 3 giorni dal 2026-11-10, ICPUSDT mancante sul demo 1 giorni dal 2026-11-10
- il paper G1 di oggi contro il funding del demo, per nome: dopo il regolamento delle 08 UTC (i pesi dei giorni passati del paper non sono su Firebase)

## Ultima decisione
- esito: **🟢 APERTA** (2026-10-21 07:02 UTC)
- motivo: aperta SYRUPUSDT long (gen_4c6df481), ordine limite riempito a 0.20076
- asset valutati: 80 · segnali: 1 · miglior segn

[... 31395 caratteri omessi (testa e coda conservate) ...]

akeven=True, profit_lock_keep=0.5 |
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
| total_return | 1207 | 91.4% |
| pf_ex_top | 3 | 0.2% |
| consistency | 17 | 1.3% |
| regime | 22 | 1.7% |
| recovery | 64 | 4.8% |
| trades | 6 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 153 | 0.5% |
| total_return | 26463 | 78.0% |
| pf_ex_top | 242 | 0.7% |
| consistency | 589 | 1.7% |
| regime | 2815 | 8.3% |
| recovery | 2737 | 8.1% |
| trades | 936 | 2.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-15 04:03 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: drift · 124 trade · PF vissuto 0.852 vs 2.02 atteso · mfe mediana 0.68R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.85 vs 2.02 atteso · mfe mediana 0.68R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| TRUMPUSDT|gen_d16d1d02 | watch | 6 | 3.723 / 1.591 | mfe mediana 1.11R < primo TP 2.00R |
| TAUSDT|gen_01fbe76f | watch | 5 | 0.707 / 1.711 | PF 0.71 vs 1.71 atteso · mfe mediana 0.92R < primo TP 1.50R |
| MYXUSDT|gen_8931b93c | watch | 4 | 0.34 / 1.583 | PF 0.34 vs 1.58 atteso · mfe mediana 0.76R < primo TP 1.50R |
| JTOUSDT|gen_94062d5f | watch | 3 | 0.503 / 1.351 | PF 0.50 vs 1.35 atteso · mfe mediana 0.55R < primo TP 1.00R |
| STXUSDT|gen_0aa0d29c | watch | 3 | 0.0 / 1.663 | PF 0.00 vs 1.66 atteso · mfe mediana 0.15R < primo TP 1.00R |
| XPINUSDT|gen_f311acf9 | watch | 3 | 0.0 / 3.282 | PF 0.00 vs 3.28 atteso |
| SCRUSDT|gen_0e030446 | watch | 3 | 0.344 / 1.851 | PF 0.34 vs 1.85 atteso |
| UBUSDT|gen_92b77c39 | watch | 3 | 0.572 / 1.502 | PF 0.57 vs 1.50 atteso · mfe mediana 1.01R < primo TP 2.00R |
| HOMEUSDT|gen_467d9ee2 | watch | 3 | 0.449 / 1.617 | PF 0.45 vs 1.62 atteso · mfe mediana 0.58R < primo TP 1.00R |
| SAHARAUSDT|gen_c934a6f7 | watch | 3 | 99.0 / 1.687 | mfe mediana 0.52R < primo TP 0.75R |
| SYRUPUSDT|gen_f3b97917 | watch | 3 | 1.697 / 2.064 | mfe mediana 1.06R < primo TP 2.00R |
| EIGENUSDT|gen_1b7827f3 | watch | 2 | 0.262 / 1.475 | PF 0.26 vs 1.48 atteso · mfe mediana 0.84R < primo TP 1.50R |
| BTRUSDT|gen_5a52c06b | watch | 2 | 0.566 / 1.784 | PF 0.57 vs 1.78 atteso |
| PARTIUSDT|gen_64263ae7 | watch | 2 | 0.597 / 1.953 | PF 0.60 vs 1.95 atteso · mfe mediana 1.03R < primo TP 2.00R |
| GPSUSDT|gen_871647b8 | watch | 2 | 2.364 / 1.555 | mfe mediana 1.20R < primo TP 2.00R |
| VELVETUSDT|gen_ff3e4154 | watch | 2 | 0.544 / 2.559 | PF 0.54 vs 2.56 atteso |
| BANKUSDT|gen_7100bb59 | watch | 2 | 0.358 / 1.938 | PF 0.36 vs 1.94 atteso · mfe mediana 0.45R < primo TP 0.75R |
| USELESSUSDT|gen_e09c5203 | watch | 2 | 0.0 / 1.636 | PF 0.00 vs 1.64 atteso · mfe mediana 0.48R < primo TP 2.00R |
| BMTUSDT|gen_be64073c | watch | 2 | 0.366 / 2.843 | PF 0.37 vs 2.84 atteso · mfe mediana 0.99R < primo TP 1.50R |
| HEMIUSDT|gen_c1f71d65 | watch | 2 | 0.829 / 1.54 | PF 0.83 vs 1.54 atteso |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 124 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (124 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 41 | 58% | +0.51% |
| 60.0–60.0 | 41 | 56% | -0.51% |
| 60.0–60.0 | 42 | 60% | -0.07% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-15 04:20 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,027.58 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -9.54/-9.51 · TRXUSDT +8.70/+8.70 · XRPUSDT -7.50/-7.84 · XLMUSDT +7.29/+7.40 · POLUSDT +6.71/+6.89 · BCHUSDT +6.67/+5.53
- XMRUSDT -6.25/-6.51 · HYPEUSDT -6.02/-6.13 · ATOMUSDT +5.95/+6.10 · TAOUSDT -5.73/-5.47 · WIFUSDT -5.63/-5.69 · RENDERUSDT -5.28/-5.35
- SEIUSDT +5.31/+5.00 · ASTERUSDT -4.89/-5.22 · MUBARAKUSDT -5.03/-5.11 · SANDUSDT +5.04/+5.09 · ARBUSDT +4.79/+4.92 · JUPUSDT +4.86/+4.66
- FARTCOINUSDT -4.54/-4.64 · JTOUSDT -4.59/-4.64 · AEROUSDT +4.53/+4.63 · 1000BONKUSDT +4.51/+4.60 · WUSDT +4.44/+4.50 · ZAMAUSDT +4.38/+4.43
- NEARUSDT -4.35/-4.26 · XPLUSDT -4.12/-4.11 · ETHFIUSDT -3.99/-4.07 · TRUMPUSDT +3.95/+4.01 · WLDUSDT +3.91/+4.00 · GRASSUSDT -3.42/-3.58
- 龙虾USDT -3.31/+0.00 · BATUSDT -3.20/-3.23 · ERAUSDT +2.93/+3.08 · USUSDT -2.85/-2.88 · LSKUSDT +2.62/+2.71 · HUMAUSDT +2.63/+2.69
- USELESSUSDT -2.48/-2.52 · GTCUSDT +2.09/+1.61 · ICNTUSDT +2.04/+2.06 · AVAUSDT +1.92/+1.61 · BIRBUSDT +1.73/+1.79 · BRUSDT -1.78/-1.33
- ARIAUSDT -1.52/-1.12 · BMTUSDT +1.41/+1.13 · APRUSDT -1.38/-1.41 · MAGMAUSDT -1.39/-1.39 · INITUSDT +1.28/+1.29 · AGTUSDT -0.50/-0.17
- QUSDT -0.41/+0.00 · AKEUSDT +0.31/+0.26 · JCTUSDT -0.31/+0.00
- monete: paper 51, demo 48; esposizione lorda paper 200.0%, demo 194.9%; somma delle differenze 11.6% del conto
```
