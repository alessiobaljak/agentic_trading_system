# 0785-27nov-stato-tre-ore-dopo-il-riavvio.req

_eseguito: 2026-11-27 16:23 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 52.6s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-27 16:22 UTC_
- macchina: disco / libero 59G su 75G (usato 18%) · memoria disponibile 14610 MB su 15609, swap usata 0 MB su 0 · orologio sincronizzato (NTP active)

## Il bot (un solo processo: paper, demo e conto vero)
- stato: **running** (🟢 online)
- ultimo heartbeat: 2026-11-27 16:22 UTC
- DRY_RUN: True

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-27 15:41 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$11,092.46** su $10,000 (+10.92%) · costi $12.65 · funding pagato $-549.00
- posizioni: 31 long, 28 short · ultimo ribilancio 2026-11-23
- ordini limite: 309 eseguiti su 309 · tutto a mercato sarebbe costato $44.04 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -14.2%, XMRUSDT -7.3%, HYPEUSDT -7.0%, TRXUSDT +7.0%, RENDERUSDT -6.3%, FARTCOINUSDT -5.9%, XPLUSDT -5.6%, XLMUSDT +5.6%, ASTERUSDT -5.5%, BCHUSDT +5.2%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-27 16:09 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$10,948.10** su $10,000 (+9.48%) · costi $35.36 · funding pagato $-530.77
- posizioni: 29 long, 29 short · ultimo ribilancio 2026-11-27
- ordini limite: 1914 eseguiti su 1921 · tutto a mercato sarebbe costato $101.43 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -10.4%, TRXUSDT +7.3%, HYPEUSDT -6.4%, AEROUSDT -6.3%, 1000SHIBUSDT +6.2%, XMRUSDT -6.1%, RENDERUSDT -5.8%, XLMUSDT +5.7%, BCHUSDT +5.5%, FARTCOINUSDT -5.4%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-27 16:14 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$11,036.07** su $10,000 (+10.36%) · costi $42.92 · funding pagato $-502.10
- posizioni: 31 long, 22 short · ultimo ribilancio 2026-11-27
- ordini limite: 1993 eseguiti su 1999 · tutto a mercato sarebbe costato $139.28 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -14.1%, HYPEUSDT -8.7%, AEROUSDT -8.6%, XMRUSDT -8.3%, FARTCOINUSDT -7.3%, XPLUSDT -6.7%, TRXUSDT +6.7%, GRASSUSDT -6.2%, BEATUSDT -5.3%, XLMUSDT +5.1%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-27 16:18 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,275.40** su $10,000 (+12.75%) · costi $34.62 · funding pagato $-534.58
- posizioni: 29 long, 29 short · ultimo ribilancio 2026-11-27
- ordini limite: 1809 eseguiti su 1813 · tutto a mercato sarebbe costato $92.50 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -10.5%, TRXUSDT +7.3%, HYPEUSDT -6.4%, AEROUSDT -6.3%, 1000SHIBUSDT +6.2%, XMRUSDT -6.1%, RENDERUSDT -5.8%, XLMUSDT +5.6%, BCHUSDT +5.5%, FARTCOINUSDT -5.4%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-27 15:59 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-27 15:58 UTC)
- equity: **$1,019.09** su $1,000.00 (+1.91%) · posizioni 27 long, 25 short · ordini limite eseguiti 818 su 867 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,367.00
- ultima decisione 2026-11-27: 10 ordini, eseguiti a limite 10, a mercato 0; sotto il minimo 43 variazioni (7.2% del conto); monete che sul demo non ci sono: IRYSUSDT; rifiutati 4: EVAAUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"; LITUSDT POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening ; PIEVERSEUSDT margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -1.02%, LITUSDT +3.23%, PIEVERSEUSDT -1.68%, UAIUSDT -1.37%, IRYSUSDT +2.19%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -3.82% dal massimo
- margine (2026-11-27 15:58 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-27 15:58 UTC): 57 monete, scarto totale 13.8% del conto; oltre il 2%: LITUSDT -3.4%
- ultimo errore (2026-11-25 17:36 UTC): `HTTPSConnectionPool(host='demo-fapi.binance.com', port=443): Read timed out. (read timeout=15)`

## G1: il demo contro il paper, giorno per giorno
Equity a fine giorno (l'ultimo valore scritto). Dal 6 novembre il demo lavora come un conto ridotto (280 USDT, dall'8 novembre 1.000), senza gli eventi; le fasi di prima sono in /demo_binance/fasi; con i minimi di Binance la differenza con il paper oscilla di più (prova 148). Gli ultimi 14 giorni: i 5 prima sono nelle risposte «stato» di prima e su Firebase.

| giorno | demo | paper G1 | demo meno paper | eventi nel paper | senza le monete che il demo non ha |
|---|---|---|---|---|---|
| 2026-11-14 | +2.26% | +3.51% | -1.25% | +0.00% | -1.25% |
| 2026-11-15 | -0.27% | -0.58% | +0.31% | +0.00% | +0.31% |
| 2026-11-16 | +1.37% | +1.49% | -0.12% | +0.00% | -0.33% |
| 2026-11-17 | -0.79% | -0.17% | -0.62% | +0.00% | -0.65% |
| 2026-11-18 | -0.99% | -1.50% | +0.51% | +0.00% | +0.09% |
| 2026-11-19 | -1.11% | -1.13% | +0.02% | +0.00% | +0.26% |
| 2026-11-20 | +1.88% | +1.16% | +0.72% | +0.00% | +0.19% |
| 2026-11-21 | -3.13% | -3.07% | -0.06% | +0.00% | -0.44% |
| 2026-11-22 | -2.09% | -1.33% | -0.76% | +0.00% | +0.07% |
| 2026-11-23 | +1.71% | +0.96% | +0.74% | +0.00% | +0.18% |
| 2026-11-24 | -0.59% | +0.23% | -0.82% | +0.00% | -0.25% |
| 2026-11-25 | -1.39% | -2.07% | +0.68% | +0.00% | +0.06% |
| 2026-11-26 | +2.87% | +3.01% | -0.14% | +0.00% | -0.11% |
| 2026-11-27 | +1.61% | +1.91% | -0.30% | +0.00% | +0.38% |

- dal 2026-11-09 (19 giorni): demo +2.40%, paper +4.62%; differenza media al giorno -0.116%, oscillazione 0.595%
- demo meno paper senza le monete che il demo non ha (ultima colonna; stima: pesi del paper di oggi, prezzi mark giornalieri di Binance, senza funding): in 14 giorni media al giorno -0.107% (con quelle monete -0.076%), oscillazione 0.446% (con 0.627%); quelle di oggi pesano nel paper G1 il 9.48% lordo del conto (5 monete, elenco nella sezione del demo); senza un peso di oggi, non contate: 龙虾USDT

Funding e spese veri, in % dell'equity del giorno (funding: + incassato; spese: + pagate; nel paper dal 6 novembre); gli ultimi 14 giorni.

| giorno | funding demo | funding paper | spese demo | spese paper |
|---|---|---|---|---|
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
| 2026-11-26 | +0.115% | +0.094% | +0.001% | +0.003% |
| 2026-11-27 | +0.104% | +0.083% | +0.002% | +0.003% |

- sul demo, dal 2026-11-07 (21 giorni): funding incassato +33.11 USDT, commissioni pagate 1.76 USDT

## F5 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-27 13:10 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 41, peso 295 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 120
Dal 2026-11-22 00:00 a 2026-11-27 16:22 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 37 monete su 37

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-22 | 64.15 | 0.0144 | 0.0224% | 92% | 8% | 13 |
| 2026-11-23 | 377.03 | 0.1179 | 0.0313% | 58% | 42% | 43 |
| 2026-11-24 | 48.68 | 0.0135 | 0.0277% | 74% | 26% | 11 |
| 2026-11-25 | 75.67 | 0.0350 | 0.0462% | 0% | 100% | 16 |
| 2026-11-26 | 22.67 | 0.0098 | 0.0430% | 23% | 77% | 4 |
| 2026-11-27 | 61.95 | 0.0211 | 0.0340% | 53% | 47% | 8 |
| 6 giorni | 650.14 | 0.2116 | 0.0325% | 54% | 46% | 95 |
- controllo: commissioni dagli incassi 0.2116 USDT, dalle esecuzioni 0.2116 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-22 | +1.5327 | +0.3770 | +0.4462 | +0.2969 | +0.4126 | 52/57 |
| 2026-11-23 | +2.0388 | +0.4682 | +0.5373 | +0.6150 | +0.4183 | 53/59 |
| 2026-11-24 | +1.4174 | +0.5758 | +0.3850 | +0.2770 | +0.1796 | 53/59 |
| 2026-11-25 | +1.1032 | +0.2652 | +0.2787 | +0.2331 | +0.3262 | 53/59 |
| 2026-11-26 | +1.1537 | +0.2842 | +0.1818 | +0.3731 | +0.3146 | 52/58 |
| 2026-11-27 (in corso) | +1.3030 | +0.3193 | +0.3491 | +0.2410 | +0.3936 | 52/58 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| BULLAUSDT | +1.1312 | +0.2135 | +0.1409 | +0.1814 | +0.5953 | -1.21% |
| INITUSDT | +1.0620 | +0.3964 | +0.4387 | +0.2269 | +0.0000 | +0.91% |
| ARIAUSDT | +0.8540 | +0.1297 | +0.1551 | +0.1434 | +0.4258 | -2.40% |
| GTCUSDT | +0.4354 | +0.1653 | +0.1802 | +0.0900 | +0.0000 | +4.42% |
| APRUSDT | +0.3462 | +0.0479 | +0.0518 | +0.0688 | +0.1777 | -3.19% |
| ONEUSDT | +0.3363 | +0.1321 | +0.0804 | +0.1239 | +0.0000 | +1.16% |
| LSKUSDT | +0.3324 | +0.0916 | +0.0676 | +0.1731 | +0.0000 | +2.43% |
| BMTUSDT | +0.2606 | +0.0707 | +0.1147 | +0.0752 | +0.0000 | +2.51% |
| 1000BONKUSDT | +0.2402 | +0.0785 | +0.0988 | +0.0629 | +0.0000 | +3.76% |
| ERAUSDT | +0.2399 | +0.0396 | +0.0450 | +0.0472 | +0.1081 | +3.47% |

- monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): EVAAUSDT rifiutata 6 giorni dal 2026-11-22, IRYSUSDT mancante sul demo 6 giorni dal 2026-11-22, LITUSDT rifiutata 6 giorni dal 2026-11-22, UAIUSDT rifiutata 6 giorni dal 2026-11-22, PIEVERSEUSDT rifiutata 5 giorni dal 2026-11-23
- nel paper G1 di oggi ma senza funding sul demo dalle 02 UTC: 6 monete su 58, peso lordo 9.94%: LITUSDT +3.23%, IRYSUSDT +2.19%, PIEVERSEUSDT -1.68%, UAIUSDT -1.37%, EVAAUSDT -1.02%, JCTUSDT -0.46%

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-27 16:23 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,019.09 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -10.39/-9.20 · TRXUSDT +7.34/+6.88 · HYPEUSDT -6.36/-6.58 · AEROUSDT -6.29/-6.12 · 1000SHIBUSDT +6.23/+6.10 · XMRUSDT -6.10/-5.41
- RENDERUSDT -5.77/-6.05 · XLMUSDT +5.65/+5.59 · BCHUSDT +5.53/+5.54 · FARTCOINUSDT -5.35/-5.40 · ASTERUSDT -4.97/-5.17 · ADAUSDT +5.03/+5.05
- NEARUSDT -4.90/-4.73 · XPLUSDT -4.89/-4.68 · SANDUSDT +4.59/+4.74 · ETHFIUSDT -4.69/-4.22 · GRASSUSDT -4.56/-4.39 · GTCUSDT +4.42/+4.33
- BEATUSDT -3.89/-3.90 · WLDUSDT +3.85/+3.83 · APTUSDT +3.81/+3.74 · 1000BONKUSDT +3.76/+3.79 · FETUSDT +3.63/+3.76 · TIAUSDT +3.73/+3.60
- JUPUSDT +3.38/+3.67 · 1000PEPEUSDT +3.65/+3.48 · SEIUSDT +3.58/+3.49 · ERAUSDT +3.47/+3.16 · OPUSDT +3.45/+3.27 · INJUSDT +3.37/+3.35
- VVVUSDT -3.36/-3.15 · TRUMPUSDT +3.27/+3.10 · LITUSDT +3.23/+0.00 · APRUSDT -3.19/-2.95 · BEAMXUSDT -2.88/-2.69 · USELESSUSDT -2.85/-2.83
- ARIAUSDT -2.40/-2.51 · BMTUSDT +2.51/+2.06 · LSKUSDT +2.43/+2.07 · QUSDT -2.43/-2.35 · ICNTUSDT -2.28/-2.43 · MAGMAUSDT -2.39/-2.42
- IRYSUSDT +2.19/+0.00 · HOTUSDT +2.12/+1.92 · BIRBUSDT +2.05/+1.59 · PIEVERSEUSDT -1.68/+0.00 · AINUSDT -1.51/-1.53 · BULLAUSDT -1.21/-1.40
- HUMAUSDT +1.39/+1.17 · UAIUSDT -1.37/+0.00 · ONEUSDT +1.16/+1.19 · BLESSUSDT -1.10/-1.01 · IDOLUSDT -1.03/-1.07 · EVAAUSDT -1.02/+0.00
- INITUSDT +0.91/+0.66 · AGTUSDT -0.67/-0.40 · JCTUSDT -0.46/+0.00 · AKEUSDT +0.27/+0.03
- monete: paper 58, demo 52; esposizione lorda paper 200.0%, demo 183.7%; somma delle differenze 20.2% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 1,019.09 USDT, paper 10,948.10; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-25 00 | +0.0260% | +0.0185% | +0.0075% | 53/59 |
| 2026-11-25 08 | +0.0274% | +0.0145% | +0.0128% | 53/59 |
| 2026-11-25 16 | +0.0229% | +0.0186% | +0.0043% | 53/59 |
| 2026-11-25 altre | +0.0320% | +0.0471% | -0.0151% | 51/150 |
| 2026-11-26 00 | +0.0279% | +0.0154% | +0.0125% | 53/59 |
| 2026-11-26 08 | +0.0178% | +0.0127% | +0.0051% | 52/58 |
| 2026-11-26 16 | +0.0366% | +0.0195% | +0.0171% | 52/58 |
| 2026-11-26 altre | +0.0309% | +0.0445% | -0.0136% | 51/147 |
| 2026-11-27 00 | +0.0313% | +0.0216% | +0.0098% | 52/58 |
| 2026-11-27 08 | +0.0343% | +0.0177% | +0.0166% | 52/58 |
| 2026-11-27 16 | +0.0237% | +0.0098% | +0.0139% | 52/58 |
| 2026-11-27 altre | +0.0386% | +0.0338% | +0.0049% | 34/97 |

- regolamento 2026-11-27 16, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): BULLAUSDT +0.0069/+0.0036 · XMRUSDT +0.0044/+0.0016 · ONEUSDT +0.0031/+0.0010 · GTCUSDT +0.0025/+0.0004 · APRUSDT +0.0023/+0.0005 · ARIAUSDT +0.0021/— · WLFIUSDT +0.0005/-0.0009 · RENDERUSDT -0.0002/-0.0008 · NEARUSDT -0.0004/-0.0007 · XLMUSDT -0.0006/+0.0007 · TRXUSDT -0.0007/+0.0007

## Vecchio sistema (fermo dal 13 ottobre)
- regime: bull_trending
- equity: **$817.25**
- stream prezzi: 🟡 candele REST
- GATE 1: 249 coppie validate (>= 3 pass OOS) su 2435 nel registro, copertura 80/200 crypto; aggiornato 2026-10-13 18:40 UTC

## Ultima decisione
- esito: **🟢 APERTA** (2026-10-21 07:02 UTC)
- motivo: aperta SYRUPUSDT long (gen_4c6df481), ordine limite riempito a 0.20076
- asset valutati: 80 · segnali: 1 · miglior segnale SYRUPUSDT gen_4c6df481 (conf. 55.6/soglia 30)

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 6 | 0.5% |
| consistency | 17 | 1.3% |
| regime | 22 | 1.7% |
| total_return | 1207 | 91.4% |
| recovery | 64 | 4.8% |
| pf_ex_top | 3 | 0.2% |
| holdout | 1 | 0.1% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 936 | 2.8% |
| total_return | 26463 | 78.0% |
| regime | 2815 | 8.3% |
| consistency | 589 | 1.7% |
| pf_ex_top | 242 | 0.7% |
| recovery | 2737 | 8.1% |
| holdout | 153 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-27 16:03 UTC · coppie validate: **278** · GATE 1 pronto: True
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
```
