# 0788-28nov-stato-ribilancio-1000.req

_eseguito: 2026-11-28 04:21 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 55.4s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-11-28 04:20 UTC_
- macchina: disco / libero 59G su 75G (usato 19%) · memoria disponibile 14626 MB su 15609, swap usata 0 MB su 0 · orologio sincronizzato (NTP active)

## Il bot (un solo processo: paper, demo e conto vero)
- stato: **running** (🟢 online)
- ultimo heartbeat: 2026-11-28 04:20 UTC
- DRY_RUN: True

## Paper F5 (strategie nuove, eseguito dal bot)
- stato: **acceso** (2026-11-28 03:45 UTC)
- prova a secco (2026-10-25 08:29 UTC, pesi del 2026-10-19): universo 100, 20 long, 20 short; pesi maggiori CRVUSDT -6.3%, ETHFIUSDT -6.2%, LITUSDT -6.0%, MORPHOUSDT -7.9%, POLUSDT +6.3%, TRXUSDT +38.1%, WLFIUSDT -14.2%, XMRUSDT -11.7%, ZECUSDT -5.8%, ZENUSDT -6.6%
- equity: **$11,277.04** su $10,000 (+12.77%) · costi $12.65 · funding pagato $-553.43
- posizioni: 31 long, 28 short · ultimo ribilancio 2026-11-23
- ordini limite: 309 eseguiti su 309 · tutto a mercato sarebbe costato $44.04 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -14.2%, XMRUSDT -7.3%, HYPEUSDT -7.0%, TRXUSDT +7.0%, RENDERUSDT -6.3%, FARTCOINUSDT -5.9%, XPLUSDT -5.6%, XLMUSDT +5.6%, ASTERUSDT -5.5%, BCHUSDT +5.2%

## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)
- stato: **acceso** (2026-11-28 04:06 UTC)
- prova a secco (2026-10-23 20:32 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori 1000BONKUSDT +8.6%, ACEUSDT +7.3%, ALGOUSDT +7.5%, ASTERUSDT -11.2%, ATOMUSDT +7.4%, PENGUUSDT -6.6%, POLUSDT +9.6%, STXUSDT +6.4%, WLFIUSDT -10.5%, XMRUSDT -11.2%
- equity: **$11,152.23** su $10,000 (+11.52%) · costi $37.41 · funding pagato $-534.54
- posizioni: 29 long, 29 short · ultimo ribilancio 2026-11-28
- ordini limite: 1970 eseguiti su 1980 · tutto a mercato sarebbe costato $103.13 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -7.4%, TRXUSDT +7.3%, HYPEUSDT -6.5%, AEROUSDT -6.5%, 1000SHIBUSDT +6.2%, RENDERUSDT -5.8%, XMRUSDT -5.8%, XLMUSDT +5.7%, FARTCOINUSDT -5.6%, BCHUSDT +5.5%

## Paper G11 (G1 con il funding fresco, a confronto con G1)
- stato: **acceso** (2026-11-28 04:11 UTC)
- prova a secco (2026-10-23 20:36 UTC, pesi del 2026-10-23): universo 100, 20 long, 20 short; pesi maggiori ACEUSDT +7.4%, ADAUSDT +9.6%, ASTERUSDT -11.3%, ATOMUSDT +7.4%, AVAXUSDT +8.8%, PENGUUSDT -6.6%, POLUSDT +9.7%, WLFIUSDT -10.5%, XMRUSDT -11.3%, ZENUSDT -6.2%
- equity: **$11,216.64** su $10,000 (+12.17%) · costi $47.67 · funding pagato $-506.09
- posizioni: 29 long, 26 short · ultimo ribilancio 2026-11-28
- ordini limite: 2050 eseguiti su 2057 · tutto a mercato sarebbe costato $142.33 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -8.8%, HYPEUSDT -7.7%, AEROUSDT -7.7%, TRXUSDT +7.1%, XMRUSDT -6.9%, FARTCOINUSDT -6.6%, XPLUSDT -6.1%, MEGAUSDT -5.9%, GRASSUSDT -5.7%, XLMUSDT +5.5%

## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)
- stato: **acceso** (2026-11-28 04:15 UTC)
- prova a secco (2026-10-25 08:33 UTC, pesi del 2026-10-25): universo 100, 20 long, 20 short; pesi maggiori ALGOUSDT +6.1%, ASTERUSDT -8.9%, ATOMUSDT +5.7%, BTCUSDT -15.2%, LABUSDT -4.9%, POLUSDT +8.3%, TRXUSDT +45.0%, WLFIUSDT -9.4%, XMRUSDT -7.8%, ZENUSDT -5.2%
- equity: **$11,440.74** su $10,000 (+14.41%) · costi $37.83 · funding pagato $-538.47
- posizioni: 29 long, 29 short · ultimo ribilancio 2026-11-28
- ordini limite: 1865 eseguiti su 1872 · tutto a mercato sarebbe costato $94.28 · in attesa del controllo dell'ora: 0
- pesi maggiori: WLFIUSDT -7.4%, TRXUSDT +7.3%, HYPEUSDT -6.5%, AEROUSDT -6.5%, 1000SHIBUSDT +6.2%, RENDERUSDT -5.8%, XMRUSDT -5.8%, XLMUSDT +5.7%, FARTCOINUSDT -5.6%, BCHUSDT +5.5%

## Paper N3 ed E4 (eventi, eseguito dal bot)
- stato: **acceso** (2026-11-28 04:03 UTC)
- equity: **$10,313.71** su $10,000 (+3.14%) · aperte N3 0, E4 0 · chiuse 1, media +62.74% a operazione · E4 in attesa 0

## G1 sul conto demo di Binance (ordini veri, soldi finti)
- stato: **acceso** (2026-11-28 04:02 UTC)
- equity: **$1,037.09** su $1,000.00 (+3.71%) · posizioni 27 long, 25 short · ordini limite eseguiti 825 su 877 · in attesa 0
- conto ridotto: il demo lavora come un conto di $1,000 (prova 148, il capitale del proprietario); valore vero del conto demo $5,385.00
- ultima decisione 2026-11-28: 10 ordini, eseguiti a limite 7, a mercato 2; sotto il minimo 42 variazioni (8.6% del conto); monete che sul demo non ci sono: EVAAUSDT, IRYSUSDT, LITUSDT, PIEVERSEUSDT, UAIUSDT
- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): EVAAUSDT -1.00%, IRYSUSDT +2.20%, LITUSDT +3.13%, PIEVERSEUSDT -1.74%, UAIUSDT -1.42%
- stop sul conto: si chiude tutto sotto $688.73 (il più alto fra −35% dal massimo, $1,059.59, e il 65% del capitale di partenza); ora -2.12% dal massimo
- margine (2026-11-28 04:02 UTC): unico su tutte le monete
- posizioni vere contro volute (2026-11-28 04:02 UTC): 53 monete, scarto totale 8.6% del conto; nessuna moneta oltre il 2%
- ultimo errore (2026-11-25 17:36 UTC): `HTTPSConnectionPool(host='demo-fapi.binance.com', port=443): Read timed out. (read timeout=15)`

## G1: il demo contro il paper, giorno per giorno
Equity a fine giorno (l'ultimo valore scritto). Dal 6 novembre il demo lavora come un conto ridotto (280 USDT, dall'8 novembre 1.000), senza gli eventi; le fasi di prima sono in /demo_binance/fasi; con i minimi di Binance la differenza con il paper oscilla di più (prova 148). Gli ultimi 14 giorni: i 6 prima sono nelle risposte «stato» di prima e su Firebase.

| giorno | demo | paper G1 | demo meno paper | eventi nel paper | senza le monete che il demo non ha |
|---|---|---|---|---|---|
| 2026-11-15 | -0.27% | -0.58% | +0.31% | +0.00% | +0.31% |
| 2026-11-16 | +1.37% | +1.49% | -0.12% | +0.00% | -0.33% |
| 2026-11-17 | -0.79% | -0.17% | -0.62% | +0.00% | -0.64% |
| 2026-11-18 | -0.99% | -1.50% | +0.51% | +0.00% | +0.10% |
| 2026-11-19 | -1.11% | -1.13% | +0.02% | +0.00% | +0.26% |
| 2026-11-20 | +1.88% | +1.16% | +0.72% | +0.00% | +0.21% |
| 2026-11-21 | -3.13% | -3.07% | -0.06% | +0.00% | -0.44% |
| 2026-11-22 | -2.09% | -1.33% | -0.76% | +0.00% | +0.06% |
| 2026-11-23 | +1.71% | +0.96% | +0.74% | +0.00% | +0.18% |
| 2026-11-24 | -0.59% | +0.23% | -0.82% | +0.00% | -0.25% |
| 2026-11-25 | -1.39% | -2.07% | +0.68% | +0.00% | +0.05% |
| 2026-11-26 | +2.87% | +3.01% | -0.14% | +0.00% | -0.12% |
| 2026-11-27 | +2.69% | +3.17% | -0.48% | +0.00% | +0.29% |
| 2026-11-28 | +0.70% | +0.62% | +0.08% | +0.00% | -0.07% |

- dal 2026-11-09 (20 giorni): demo +4.21%, paper +6.57%; differenza media al giorno -0.115%, oscillazione 0.585%
- demo meno paper senza le monete che il demo non ha (ultima colonna; stima: pesi del paper di oggi, prezzi mark giornalieri di Binance, senza funding): in 14 giorni media al giorno -0.027% (con quelle monete +0.005%), oscillazione 0.295% (con 0.540%); quelle di oggi pesano nel paper G1 il 9.47% lordo del conto (5 monete, elenco nella sezione del demo); senza un peso di oggi, non contate: 龙虾USDT

Funding e spese veri, in % dell'equity del giorno (funding: + incassato; spese: + pagate; nel paper dal 6 novembre); gli ultimi 14 giorni.

| giorno | funding demo | funding paper | spese demo | spese paper |
|---|---|---|---|---|
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
| 2026-11-27 | +0.138% | +0.089% | +0.002% | +0.003% |
| 2026-11-28 | +0.030% | +0.026% | +0.005% | +0.018% |

- sul demo, dal 2026-11-07 (22 giorni): funding incassato +33.78 USDT, commissioni pagate 1.81 USDT

## F5 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)
- stato: **spento: manca l'interruttore ops/conto_vero_acceso** (2026-11-27 13:10 UTC)

## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)
- richieste a Binance di questa sezione: 44, peso 310 (userTrades 5, income 30, commissionRate 20); peso usato dall'indirizzo nel minuto 60
Dal 2026-11-23 00:00 a 2026-11-28 04:20 UTC; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa).
- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0400%
Esecuzioni (`userTrades`) lette per 40 monete su 40

| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |
|---|---|---|---|---|---|---|
| 2026-11-23 | 377.03 | 0.1179 | 0.0313% | 58% | 42% | 43 |
| 2026-11-24 | 48.68 | 0.0135 | 0.0277% | 74% | 26% | 11 |
| 2026-11-25 | 75.67 | 0.0350 | 0.0462% | 0% | 100% | 16 |
| 2026-11-26 | 22.67 | 0.0098 | 0.0430% | 23% | 77% | 4 |
| 2026-11-27 | 61.95 | 0.0211 | 0.0340% | 53% | 47% | 8 |
| 2026-11-28 | 126.34 | 0.0547 | 0.0433% | 8% | 92% | 7 |
| 6 giorni | 712.33 | 0.2519 | 0.0354% | 42% | 58% | 89 |
- controllo: commissioni dagli incassi 0.2519 USDT, dalle esecuzioni 0.2519 USDT

Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1.

| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |
|---|---|---|---|---|---|---|
| 2026-11-23 | +2.0388 | +0.4682 | +0.5373 | +0.6150 | +0.4183 | 53/59 |
| 2026-11-24 | +1.4174 | +0.5758 | +0.3850 | +0.2770 | +0.1796 | 53/59 |
| 2026-11-25 | +1.1032 | +0.2652 | +0.2787 | +0.2331 | +0.3262 | 53/59 |
| 2026-11-26 | +1.1537 | +0.2842 | +0.1818 | +0.3731 | +0.3146 | 52/58 |
| 2026-11-27 | +1.4250 | +0.3193 | +0.3491 | +0.2410 | +0.5156 | 52/58 |
| 2026-11-28 (in corso) | +0.3094 | +0.1854 | +0.0000 | +0.0000 | +0.1241 | —/58 |

Le 10 monete con il funding più grande nei 5 giorni chiusi (peso nel paper G1 di oggi).

| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |
|---|---|---|---|---|---|---|
| BULLAUSDT | +1.4703 | +0.3405 | +0.2040 | +0.2046 | +0.7211 | -1.25% |
| ARIAUSDT | +0.8283 | +0.1372 | +0.1504 | +0.1306 | +0.4101 | -2.48% |
| INITUSDT | +0.6175 | +0.2227 | +0.2414 | +0.1534 | +0.0000 | +0.90% |
| ONEUSDT | +0.4880 | +0.1722 | +0.1599 | +0.1558 | +0.0000 | +1.16% |
| APRUSDT | +0.4385 | +0.0572 | +0.0659 | +0.0866 | +0.2288 | -3.32% |
| GTCUSDT | +0.4198 | +0.1719 | +0.1609 | +0.0870 | +0.0000 | +4.40% |
| LSKUSDT | +0.2841 | +0.0761 | +0.0454 | +0.1625 | +0.0000 | +2.43% |
| XMRUSDT | +0.2517 | +0.0563 | +0.0591 | +0.1362 | +0.0000 | -5.81% |
| BMTUSDT | +0.2379 | +0.0685 | +0.0978 | +0.0715 | +0.0000 | +2.52% |
| BLESSUSDT | +0.2363 | +0.0184 | +0.0469 | +0.0489 | +0.1221 | -1.13% |

- monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): IRYSUSDT mancante sul demo 6 giorni dal 2026-11-23, EVAAUSDT rifiutata 5 giorni dal 2026-11-23, LITUSDT rifiutata 5 giorni dal 2026-11-23, PIEVERSEUSDT rifiutata 5 giorni dal 2026-11-23, UAIUSDT rifiutata 5 giorni dal 2026-11-23, EVAAUSDT mancante sul demo 1 giorni dal 2026-11-28, LITUSDT mancante sul demo 1 giorni dal 2026-11-28, PIEVERSEUSDT mancante sul demo 1 giorni dal 2026-11-28, UAIUSDT mancante sul demo 1 giorni dal 2026-11-28
- il paper G1 di oggi contro il funding del demo, per nome: dopo il regolamento delle 08 UTC (i pesi dei giorni passati del paper non sono su Firebase)

## G1 oggi, moneta per moneta: paper e demo (sola lettura)
Letto il 2026-11-28 04:21 UTC. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` (l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity del conto ridotto (1,037.09 USDT). La differenza mescola esecuzione e movimento dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo.
- WLFIUSDT -7.44/-7.33 · TRXUSDT +7.32/+7.30 · HYPEUSDT -6.51/-6.46 · AEROUSDT -6.49/-6.43 · 1000SHIBUSDT +6.20/+6.03 · RENDERUSDT -5.82/-6.05
- XMRUSDT -5.81/-5.59 · XLMUSDT +5.68/+5.45 · FARTCOINUSDT -5.56/-5.28 · BCHUSDT +5.54/+5.56 · XPLUSDT -5.13/-4.60 · ASTERUSDT -5.11/-5.11
- ADAUSDT +5.03/+4.92 · MEGAUSDT -4.98/-4.93 · ETHFIUSDT -4.87/-4.88 · GRASSUSDT -4.83/-4.77 · SANDUSDT +4.58/+4.68 · GTCUSDT +4.40/+4.49
- BEATUSDT -4.02/-3.78 · 1000PEPEUSDT +3.92/+3.46 · WLDUSDT +3.81/+3.78 · 1000BONKUSDT +3.80/+3.74 · APTUSDT +3.78/+3.73 · TIAUSDT +3.75/+3.57
- FETUSDT +3.55/+3.67 · JUPUSDT +3.33/+3.64 · SEIUSDT +3.59/+3.49 · VVVUSDT -3.51/-3.54 · ERAUSDT +3.50/+3.10 · OPUSDT +3.43/+3.20
- INJUSDT +3.37/+3.27 · APRUSDT -3.32/-2.96 · TRUMPUSDT +3.27/+3.06 · LITUSDT +3.13/+0.00 · USELESSUSDT -2.97/-2.81 · BEAMXUSDT -2.97/-2.62
- QUSDT -2.94/-2.89 · BMTUSDT +2.52/+2.06 · ARIAUSDT -2.48/-2.49 · MAGMAUSDT -2.46/-2.34 · LSKUSDT +2.43/+2.02 · ICNTUSDT -2.33/-2.12
- IRYSUSDT +2.20/+0.00 · HOTUSDT +2.11/+1.96 · BIRBUSDT +2.05/+2.02 · PIEVERSEUSDT -1.74/+0.00 · AINUSDT -1.56/-1.50 · UAIUSDT -1.42/+0.00
- HUMAUSDT +1.40/+1.14 · BULLAUSDT -1.25/-1.29 · IDOLUSDT -1.19/-1.14 · ONEUSDT +1.16/+1.13 · BLESSUSDT -1.13/-0.89 · EVAAUSDT -1.00/+0.00
- INITUSDT +0.90/+0.52 · AGTUSDT -0.69/-0.39 · JCTUSDT -0.47/+0.00 · AKEUSDT +0.27/+0.03
- monete: paper 58, demo 52; esposizione lorda paper 200.0%, demo 183.2%; somma delle differenze 18.7% del conto

## G1: il funding per regolamento, demo contro paper (sola lettura)
Equity di oggi: demo 1,037.09 USDT, paper 11,152.23; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del 16 novembre 2026), demo dagli incassi di Binance.

| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |
|---|---|---|---|---|
| 2026-11-26 00 | +0.0274% | +0.0151% | +0.0123% | 53/59 |
| 2026-11-26 08 | +0.0175% | +0.0125% | +0.0050% | 52/58 |
| 2026-11-26 16 | +0.0360% | +0.0191% | +0.0168% | 52/58 |
| 2026-11-26 altre | +0.0303% | +0.0436% | -0.0133% | 51/147 |
| 2026-11-27 00 | +0.0308% | +0.0212% | +0.0096% | 52/58 |
| 2026-11-27 08 | +0.0337% | +0.0173% | +0.0163% | 52/58 |
| 2026-11-27 16 | +0.0232% | +0.0096% | +0.0136% | 52/58 |
| 2026-11-27 altre | +0.0497% | +0.0407% | +0.0090% | 51/140 |
| 2026-11-28 00 | +0.0179% | +0.0116% | +0.0062% | 52/58 |
| 2026-11-28 altre | +0.0120% | +0.0147% | -0.0027% | 18/44 |

- regolamento 2026-11-28 00, le monete più grandi in % del conto, demo/paper (— = non fra le 10 più grandi pubblicate dal paper): BULLAUSDT +0.0039/+0.0017 · GTCUSDT +0.0021/— · APRUSDT +0.0019/+0.0007 · ARIAUSDT +0.0018/— · BMTUSDT +0.0017/— · ONEUSDT +0.0017/+0.0005 · TRXUSDT -0.0005/+0.0015 · BCHUSDT +0.0012/+0.0005 · 1000SHIBUSDT +0.0010/+0.0006 · SANDUSDT -0.0000/+0.0007 · XMRUSDT +0.0005/+0.0005 · INITUSDT -0.0001/+0.0005 · NEARUSDT +0.0005/+0.0005

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
| consistency | 17 | 1.3% |
| holdout | 1 | 0.1% |
| pf_ex_top | 3 | 0.2% |
| total_return | 1207 | 91.4% |
| trades | 6 | 0.5% |
| recovery | 64 | 4.8% |
| regime | 22 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 589 | 1.7% |
| recovery | 2737 | 8.1% |
| pf_ex_top | 242 | 0.7% |
| holdout | 153 | 0.5% |
| trades | 936 | 2.8% |
| total_return | 26463 | 78.0% |
| regime | 2815 | 8.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-11-28 04:01 UTC · coppie validate: **278** · GATE 1 pronto: True
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
