# 0756-17nov-stato-ribilancio-1000.req

_eseguito: 2026-11-17 04:20 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 65.5s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-17 04:19 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: high_uncertainty
- DRY_RUN: True
- equity: **$817.25**
- ultimo heartbeat: 2026-11-17 04:19 UTC
- stream prezzi: 🟡 candele REST

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-17 03:20 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$10,754.21** su $10,000 (+7.54%) · costi $11.30 · funding pagato $-402.82
- posizioni: 26 long, 27 short · ultimo ribilancio 2026-11-16
- ordini limite: 245 eseguiti su 245 · tutto a mercato sarebbe costato $39.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -12.2%, TRXUSDT +8.2%, XMRUSDT -7.7%, HYPEUSDT -7.4%, RENDERUSDT -6.7%, XLMUSDT +6.5%, ASTERUSDT -6.3%, POLUSDT +6.2%, BCHUSDT +6.0%, JTOUSDT -5.9%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-17 04:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$11,267.75** su $10,000 (+12.68%) · costi $30.92 · funding pagato $-387.61
- posizioni: 26 long, 30 short · ultimo ribilancio 2026-11-17
- ordini limite: 1329 eseguiti su 1336 · tutto a mercato sarebbe costato $85.88 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -10.9%, TRXUSDT +8.3%, XMRUSDT -7.0%, HYPEUSDT -6.7%, XLMUSDT +6.6%, WIFUSDT -6.5%, POLUSDT +6.2%, RENDERUSDT -6.1%, BCHUSDT +6.0%, ADAUSDT +5.6%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-17 04:10 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$11,241.24** su $10,000 (+12.41%) · costi $34.53 · funding pagato $-363.57
- posizioni: 28 long, 30 short · ultimo ribilancio 2026-11-17
- ordini limite: 1403 eseguiti su 1409 · tutto a mercato sarebbe costato $109.92 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.4%, TRXUSDT +7.8%, XMRUSDT -7.3%, HYPEUSDT -7.0%, PENDLEUSDT -6.8%, RENDERUSDT -6.4%, POLUSDT +5.8%, BCHUSDT +5.7%, JTOUSDT -5.6%, ASTERUSDT -5.4%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-17 04:14 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,527.27** su $10,000 (+15.27%) · costi $29.71 · funding pagato $-389.17
- posizioni: 26 long, 30 short · ultimo ribilancio 2026-11-17
- ordini limite: 1224 eseguiti su 1228 · tutto a mercato sarebbe costato $75.32 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -11.2%, TRXUSDT +8.1%, XMRUSDT -7.2%, HYPEUSDT -6.8%, WIFUSDT -6.6%, XLMUSDT +6.4%, RENDERUSDT -6.3%, POLUSDT +6.1%, BCHUSDT +5.9%, ADAUSDT +5.5%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-17 03:29 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-17 03:30 UTC)
- equity: **$1,049.56** su $1,000.00 (+4.96%) · posizioni 25 long, 27 short · ordini limite eseguiti 716 su 761 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,397.47
- ultima decisione 2026-11-17: 14 ordini, eseguiti a limite 12, a mercato 2; sotto il minimo 41 variazioni (7.6% del conto); rifiutati 3: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; UAIUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -0.87%, LITUSDT +3.31%, UAIUSDT -1.32%
- stop sul conto: si chiude tutto sotto $682.28 (il più alto fra −35% dal massimo, $1,049.66, e il 65% del capitale di partenza); ora -0.01% dal massimo
- margine (2026-11-17 03:30 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-17 03:30 UTC): 56 monete, scarto totale 13.2% del conto; oltre il 2%: LITUSDT -3.3%
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
| 2026-11-17 | +0.75% | +0.71% | +0.04% | +0.00% |

- dal 2026-11-09 (9 giorni): demo +5.46%, paper +7.67%; differenza media al giorno -0.238%, oscillazione 0.569%

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
| 2026-11-17 | +0.067% | +0.047% | +0.008% | +0.008% |

- sul demo, dal 2026-11-07 (11 giorni): funding incassato +18.54 USDT, commissioni pagate 1.40 USDT

## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-16 07:38 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 58, peso 380 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 150
Dal 2026-11-12 00:00 a 2026-11-17 04:19 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 54 monete su 54

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-12 | 95.67 | 0.0250 | 0.0261% | 80% | 20% | 18 |
| 2026-11-13 | 294.91 | 0.0857 | 0.0291% | 63% | 37% | 31 |
| 2026-11-14 | 68.00 | 0.0242 | 0.0355% | 26% | 74% | 6 |
| 2026-11-15 | 407.89 | 0.1077 | 0.0264% | 71% | 29% | 59 |
| 2026-11-16 | 689.13 | 0.1813 | 0.0263% | 67% | 33% | 53 |
| 2026-11-17 | 323.45 | 0.0882 | 0.0273% | 67% | 33% | 37 |
| 6 giorni | 1,879.06 | 0.5121 | 0.0273% | 66% | 34% | 204 |
- controllo: commissioni dagli incassi 0.5121 USDT, dalle esecuzioni 0.5121 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-12 | +1.9193 | +0.5532 | +0.5668 | +0.6022 | +0.1972 | 50/54 |
| 2026-11-13 | +2.5725 | +0.7470 | +1.0759 | +0.5527 | +0.1968 | 49/52 |
| 2026-11-14 | +1.5334 | +0.4308 | +0.5596 | +0.4427 | +0.1003 | 50/53 |
| 2026-11-15 | +1.8414 | +0.5369 | +0.7643 | +0.3195 | +0.2206 | 48/51 |
| 2026-11-16 | +1.3306 | +0.3986 | +0.1989 | +0.3225 | +0.4106 | 49/52 |
| 2026-11-17 (in corso) | +0.8165 | +0.7040 | +0.0000 | +0.0000 | +0.1125 | —/56 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| XMRUSDT | +3.3853 | +1.1167 | +1.4158 | +0.8528 | +0.0000 | -7.00% |
| HUMAUSDT | +1.0011 | +0.2204 | +0.3358 | +0.4448 | +0.0000 | +1.61% |
| ERAUSDT | +0.6650 | +0.0929 | +0.1098 | +0.0942 | +0.3680 | +2.82% |
| BMTUSDT | +0.6161 | +0.1211 | +0.2077 | +0.2872 | +0.0000 | +1.34% |
| LSKUSDT | +0.6007 | +0.2360 | +0.1735 | +0.1912 | +0.0000 | +2.54% |
| BIRBUSDT | +0.4560 | +0.0078 | +0.1271 | +0.0492 | +0.2720 | +1.64% |
| ATOMUSDT | +0.2528 | +0.0744 | +0.0943 | +0.0841 | +0.0000 | — |
| WUSDT | +0.2465 | +0.0974 | +0.0778 | +0.0713 | +0.0000 | — |
| GTCUSDT | +0.2283 | +0.0689 | +0.0907 | +0.0687 | +0.0000 | +2.13% |
| ARIAUSDT | +0.2264 | +0.0276 | +0.0292 | +0.0390 | +0.1306 | -1.72% |

- monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): 龙虾USDT rifiutata 4 giorni dal 2

[... 31997 caratteri omessi (testa e coda conservate) ...]

 | 3 | 1.618 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.5 |
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
| regime | 22 | 1.7% |
| recovery | 64 | 4.8% |
| holdout | 1 | 0.1% |
| total_return | 1207 | 91.4% |
| trades | 6 | 0.5% |
| pf_ex_top | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 589 | 1.7% |
| regime | 2815 | 8.3% |
| total_return | 26463 | 78.0% |
| recovery | 2737 | 8.1% |
| holdout | 153 | 0.5% |
| trades | 936 | 2.8% |
| pf_ex_top | 242 | 0.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-17 04:03 UTC · coppie validate: **278** · GATE 1 pronto: True
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

- **globale**: drift · 69 trade · PF vissuto 0.829 vs 2.02 atteso · mfe mediana 0.6R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.83 vs 2.02 atteso · mfe mediana 0.60R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| TRUMPUSDT|gen_d16d1d02 | watch | 3 | 1.638 / 1.591 | mfe mediana 1.02R < primo TP 2.00R |
| STXUSDT|gen_0aa0d29c | watch | 3 | 0.0 / 1.663 | PF 0.00 vs 1.66 atteso · mfe mediana 0.15R < primo TP 1.00R |
| MYXUSDT|gen_8931b93c | watch | 3 | 0.109 / 1.583 | PF 0.11 vs 1.58 atteso · mfe mediana 0.24R < primo TP 1.50R |
| HEMIUSDT|gen_c1f71d65 | watch | 2 | 0.829 / 1.54 | PF 0.83 vs 1.54 atteso |
| BMTUSDT|gen_be64073c | watch | 2 | 0.366 / 2.843 | PF 0.37 vs 2.84 atteso · mfe mediana 0.99R < primo TP 1.50R |
| UBUSDT|gen_92b77c39 | watch | 2 | 0.178 / 1.502 | PF 0.18 vs 1.50 atteso · mfe mediana 1.20R < primo TP 2.00R |
| EIGENUSDT|gen_1b7827f3 | watch | 2 | 0.262 / 1.475 | PF 0.26 vs 1.48 atteso · mfe mediana 0.84R < primo TP 1.50R |
| JTOUSDT|gen_94062d5f | watch | 2 | 99.0 / 1.351 | mfe mediana 0.68R < primo TP 1.00R |
| PARTIUSDT|gen_64263ae7 | watch | 2 | 0.597 / 1.953 | PF 0.60 vs 1.95 atteso · mfe mediana 1.03R < primo TP 2.00R |
| SAHARAUSDT|gen_c934a6f7 | watch | 2 | 99.0 / 1.687 | mfe mediana 0.52R < primo TP 0.75R |
| USELESSUSDT|gen_e09c5203 | watch | 1 | 0.0 / 1.636 | PF 0.00 vs 1.64 atteso · mfe mediana 0.48R < primo TP 2.00R |
| HUSDT|gen_ccb40454 | watch | 1 | 99.0 / 1.478 | mfe mediana 0.64R < primo TP 1.00R |
| AINUSDT|gen_d926b0fd | watch | 1 | 0.0 / 1.541 | PF 0.00 vs 1.54 atteso · mfe mediana 0.08R < primo TP 1.50R |
| SCRUSDT|gen_0e030446 | watch | 1 | 0.0 / 1.851 | PF 0.00 vs 1.85 atteso |
| SCRUSDT|gen_c934a6f7 | watch | 1 | 0.0 / 1.524 | PF 0.00 vs 1.52 atteso · mfe mediana 0.39R < primo TP 2.00R |
| HYPEUSDT|gen_f19b67e8 | watch | 1 | 0.0 / 1.624 | PF 0.00 vs 1.62 atteso |
| CROSSUSDT|gen_4e6e1ae0 | watch | 1 | 99.0 / 2.69 | mfe mediana 1.00R < primo TP 2.00R |
| HEMIUSDT|gen_acea368d | watch | 1 | 99.0 / 1.784 | mfe mediana 0.80R < primo TP 1.50R |
| IDOLUSDT|gen_931ca7de | watch | 1 | 0.0 / 2.261 | PF 0.00 vs 2.26 atteso |
| SYRUPUSDT|gen_f3b97917 | watch | 1 | 99.0 / 2.064 | mfe mediana 1.06R < primo TP 2.00R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 69 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (69 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 23 | 61% | -0.62% |
| 60.0–60.0 | 23 | 44% | +0.95% |
| 60.0–60.0 | 23 | 61% | -0.44% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-17 04:20 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,049.56 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -10.94/-10.84 · TRXUSDT +8.28/+8.45 · XMRUSDT -7.00/-6.92 · HYPEUSDT -6.69/-6.96 · POLUSDT +6.20/+6.75 · WIFUSDT -6.45/-6.66
- XLMUSDT +6.55/+6.60 · RENDERUSDT -6.12/-6.11 · BCHUSDT +6.03/+5.48 · ADAUSDT +5.62/+5.62 · SANDUSDT +5.45/+5.50 · JTOUSDT -5.34/-5.29
- ASTERUSDT -5.17/-5.22 · FARTCOINUSDT -5.08/-5.11 · SEIUSDT +4.98/+4.98 · NEARUSDT -4.93/-4.96 · XPLUSDT -4.75/-4.96 · ARBUSDT +4.44/+4.87
- ETHFIUSDT -4.63/-4.56 · 1000BONKUSDT +4.25/+4.59 · APTUSDT +4.26/+4.47 · JUPUSDT +4.16/+4.38 · INJUSDT +4.17/+4.35 · TIAUSDT +4.13/+4.31
- GRASSUSDT -3.94/-3.96 · WLDUSDT +3.61/+3.94 · TRUMPUSDT +3.73/+3.93 · 1000PEPEUSDT +3.56/+3.82 · OPUSDT +3.67/+3.70 · BEATUSDT -3.44/-3.31
- LITUSDT +3.31/+0.00 · ERAUSDT +2.82/+3.12 · USELESSUSDT -2.87/-2.90 · ONUSDT -2.26/-2.70 · ICNTUSDT -2.56/-2.65 · BEAMXUSDT -2.64/-2.53
- LSKUSDT +2.54/+2.61 · GTCUSDT +2.13/+2.23 · BRUSDT -2.14/-2.06 · BIRBUSDT +1.64/+1.90 · ARIAUSDT -1.72/-1.64 · APRUSDT -1.62/-1.20
- HUMAUSDT +1.61/+1.49 · MAGMAUSDT -1.60/-1.09 · DOODUSDT -1.43/-1.43 · BMTUSDT +1.34/+1.08 · UAIUSDT -1.32/+0.00 · INITUSDT +1.22/+1.25
- BULLAUSDT -1.10/-0.66 · IDOLUSDT -1.09/-1.05 · EVAAUSDT -0.87/+0.00 · AINUSDT -0.80/-0.77 · AGTUSDT -0.61/-0.62 · QUSDT -0.52/-0.48
- JCTUSDT -0.36/+0.00 · AKEUSDT +0.29/+0.26
- monete: paper 56, demo 52; esposizione lorda paper 200.0%, demo 196.3%; somma delle differenze 14.4% del conto
```
