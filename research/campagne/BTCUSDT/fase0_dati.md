# Fase 0 — I dati di BTCUSDT (in-sample, 2020-01-01 → 2023-12-31)

Scritto dalla sessione di campagna il 2026-10-07. Tutto cio' che c'e' qui viene dai file
scaricati in `research/data/insample/BTCUSDT/` (fuori da git) e dall'analisi in
`codice/fase0_analisi.py` (esito salvato in `codice/fase0_analisi.json`). Nessun dato oltre il
2023-12-31 e' stato richiesto, scaricato o elencato.

## Periodi

| Periodo | Da | A | Giorni |
|---|---|---|---|
| In-sample | 2020-01-01 | 2023-12-31 | 1.461 |
| Costruzione (70%) | 2020-01-01 | 2022-10-19 | 1.023 |
| Validazione (30%) | 2022-10-20 | 2023-12-31 | 438 |

Le date sono state calcolate e registrate nel log (voce `BTCUSDT-F0-01`) PRIMA di caricare i prezzi.
I mesi settembre-dicembre 2019 (listing 2019-09-08) restano fuori: l'archivio mensile parte da
gennaio 2020 (decisione 5 del Passo 0). Storia utile: 4 anni, sopra i 2 richiesti.

## Cosa e' stato scaricato

Fonte: data.binance.vision, file mensili `futures/um`, 48 mesi per serie, ognuno con il CHECKSUM
remoto verificato (nessun CHECKSUM mancante).

| Serie | Uso | File | Barre attese | Barre presenti |
|---|---|---|---|---|
| klines 15m (last price) | segnali e stop; aggregata a 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d | 48 | 140.256 | 140.256 |
| klines 1d (last price) | solo controllo dell'aggregazione | 48 | 1.461 | 1.461 |
| markPriceKlines 15m | liquidazioni | 48 | 140.256 | 139.486 |
| fundingRate | funding storico | 48 | — | 4.383 settlement |

## Buchi nei dati

* **Last price 15m: nessun buco** (140.256 barre su 140.256, dal 2020-01-01 00:00 al 2023-12-31 23:45).
* **Last price 1d: nessun buco** (1.461 giorni).
* **Mark price 15m: 770 barre mancanti in 7 buchi**, tutti assenti dai file di Binance (non e' un errore di scarico):

| Da (UTC) | A (UTC) | Barre mancanti |
|---|---|---|
| 2020-01-19 13:15 | 2020-01-19 13:15 | 1 |
| 2021-07-01 00:00 | 2021-07-01 23:45 | 96 |
| 2021-07-24 00:00 | 2021-07-27 23:45 | 384 |
| 2022-07-31 00:00 | 2022-07-31 23:45 | 96 |
| 2022-10-02 00:00 | 2022-10-02 23:45 | 96 |
| 2023-02-24 00:00 | 2023-02-24 23:45 | 96 |
| 2023-11-10 03:45 | 2023-11-10 03:45 | 1 |

**Regola adottata (dichiarata qui e nel log, voce `BTCUSDT-F0-03`):** le barre mark mancanti si
riempiono con la barra last dello stesso istante, prima dell'aggregazione (`codice/dati_btc.py`,
`riempi_mark_con_last`). Motivi: il mark serve solo alla liquidazione, che con leva massima 2 e
margine di mantenimento 2,5% dista circa il 47% dall'ingresso; lo scarto fra close mark e close
last e' mediano 0.0073%, 99° percentile 0.120%, massimo 3.37%.
Lo stop scatta sulla serie last (`serie_stop` approvata), quindi il riempimento non tocca gli stop.
Il motore di `src/` non e' stato modificato: il riempimento e' nel codice della campagna.

## Controllo dell'aggregazione

Le candele 1d aggregate dalle 15m coincidono con le 1d native di Binance su open, high, low e close
in tutti i 1461 giorni. Il volume differisce in 2 giorni
(2023-08-16: aggregato 280.543 contro nativo 272.023; 2023-11-10: 267.169 contro 299.374, in moneta base):
sono incoerenze dei file di Binance, non dell'aggregazione, e il volume non entra in nessuna regola
di prezzo. Si dichiara e basta.

## Sospensioni e cambi di contratto

Nessun cambio di contratto per BTCUSDT (nessuna cucitura). Nessuna sospensione visibile nella serie
last (nessun buco). I buchi del mark price coincidono con giorni interi e sembrano file di archivio
mancanti, non sospensioni del mercato.

## Funding

* Disponibile dal 2020-01-01 00:00 al 2023-12-31 16:00 UTC: 4.383 settlement.
* Intervallo: **8 ore per tutto il periodo** (dichiarato dai file e osservato: 4.382 distanze su 4.382 pari a 8 ore).
* Tasso: mediana 0.0100%, medio 0.0137%, min -0.30%, max 0.30% per settlement.
* Medio per anno e quota di settlement positivi (long paga):

| Anno | Tasso medio per settlement | Quota positivi |
|---|---|---|
| 2020 | 0.0157% | 86% |
| 2021 | 0.0280% | 93% |
| 2022 | 0.0038% | 78% |
| 2023 | 0.0072% | 90% |

## Volume e liquidita'

Stima del volume giornaliero in USDT = volume in moneta base × close del giorno (la candela del
motore non porta il quote volume; l'approssimazione basta per la soglia).

| Anno | Volume medio al giorno (milioni USDT) | Giorno minimo (milioni USDT) |
|---|---|---|
| 2020 | 3.126 | 409 |
| 2021 | 17.579 | 6.182 |
| 2022 | 12.806 | 1.387 |
| 2023 | 11.523 | 1.321 |

Giorni sotto la soglia di 20 milioni di USDT: **0**. Nessun periodo da escludere dai test.
Fascia di slippage: 0,01% per lato (scheda, volume medio 2023 sopra 1 miliardo); anche il 2020, l'anno
piu' sottile, sta sopra 1 miliardo in media.

## Prezzo per anno (descrizione dei dati, non un risultato)

| Anno | Primo open | Ultimo close | Minimo | Massimo |
|---|---|---|---|---|
| 2020 | 7.189 | 28.952 | 3.622 | 29.377 |
| 2021 | 28.948 | 46.211 | 27.800 | 69.199 |
| 2022 | 46.211 | 16.538 | 15.443 | 48.200 |
| 2023 | 16.538 | 42.314 | 16.488 | 44.779 |

## Impronte SHA-256 dei file scaricati

Da qui in poi queste sono la verita' della campagna: a ogni sessione i file si riscaricano e
`dati.verifica_impronte` li confronta; una differenza e' uno STOP.

| File | SHA-256 |
|---|---|
| `fundingRate/BTCUSDT-fundingRate-2020-01.zip` | `7f81b2f3694d13779e7e896b69d60cd61e9444d7b9f9e90df761935e1c1b76e2` |
| `fundingRate/BTCUSDT-fundingRate-2020-02.zip` | `6599466d108d120c64a078824326c063ed2d4335b3292e52c5e572f79166533a` |
| `fundingRate/BTCUSDT-fundingRate-2020-03.zip` | `eee845fde6336e29d25889563cba3d2cff2d4d640e51fb1f82ae9b28cedaee77` |
| `fundingRate/BTCUSDT-fundingRate-2020-04.zip` | `d009ce034d08c3dcf3e7f874b0f8b0ec76ba507bc6bb4e007e541df537bafbce` |
| `fundingRate/BTCUSDT-fundingRate-2020-05.zip` | `3f2b56dd6b9a42457009bb367d0adadd3cf7e2216cd325172d0089e3883125a8` |
| `fundingRate/BTCUSDT-fundingRate-2020-06.zip` | `30b3470ff98576578973d75e3c157a5cbf1778b11e4c26b4b4ff70a3cbb348ec` |
| `fundingRate/BTCUSDT-fundingRate-2020-07.zip` | `18dae7b11075fc0fba79ad47df46683415cba5d027caa69c66bc2a5c9d9b459a` |
| `fundingRate/BTCUSDT-fundingRate-2020-08.zip` | `e6f6d1749f674c85d4766e0eb36af6ea40d91a0674234d30df80eb9876b094e3` |
| `fundingRate/BTCUSDT-fundingRate-2020-09.zip` | `7ae9a3b6afb2dc06e46080582908ec8c27063b707a14c7f1e679dc991ff48032` |
| `fundingRate/BTCUSDT-fundingRate-2020-10.zip` | `4c55b191c101f39c7fb193a6529665dd9e83302ca21876521e4c93b3902e9fb1` |
| `fundingRate/BTCUSDT-fundingRate-2020-11.zip` | `676356a2d075caa51b4f8ada026e9430dc320ffd23d2343b13b7aa25324ed6d1` |
| `fundingRate/BTCUSDT-fundingRate-2020-12.zip` | `d7390f90edf54cc4ad9bbe78e2f6b291ae06ad9539f591a2d0fce445873bbd63` |
| `fundingRate/BTCUSDT-fundingRate-2021-01.zip` | `cff916dc4b638ec3de97828e8911cd91cf7d7a3d0836ec0175869c374e66823d` |
| `fundingRate/BTCUSDT-fundingRate-2021-02.zip` | `819a7b107443686adb313fc5fc223302a29f3981e1d1bd9828ad0ade65a8a8af` |
| `fundingRate/BTCUSDT-fundingRate-2021-03.zip` | `2125fd300848938c7b992b8f7b7b5007d5b277a4ff1ebda7da083b40242729da` |
| `fundingRate/BTCUSDT-fundingRate-2021-04.zip` | `9cd888e3b0a1954813d0062c2e60426fdc8e34a7f258f6838371ec67f535b028` |
| `fundingRate/BTCUSDT-fundingRate-2021-05.zip` | `ed934afb9cf84df6ecae742e755147333a84244836a66b51523abc66dd5f63af` |
| `fundingRate/BTCUSDT-fundingRate-2021-06.zip` | `7b8d9bfb8816636b800764dafb2aa2307d19166c695bfa245adbf7d01d61f766` |
| `fundingRate/BTCUSDT-fundingRate-2021-07.zip` | `8ab3df641d3bcf40527491f8e26d046ad2b662d1950ead9555ad32975571b7fe` |
| `fundingRate/BTCUSDT-fundingRate-2021-08.zip` | `7eb681cc45b94176f4b9192a62c3a1925d79031ba001cea2d8dec6ff6e5b9c35` |
| `fundingRate/BTCUSDT-fundingRate-2021-09.zip` | `03f25a7c25eef18d5f5b5b7bb0b664cab7a210b409f37e95a54e141808a0752d` |
| `fundingRate/BTCUSDT-fundingRate-2021-10.zip` | `f25820d6add687addbca3ef43bee58f70853a6da53832a0c1bc22d00dc8ec64a` |
| `fundingRate/BTCUSDT-fundingRate-2021-11.zip` | `e2e6b2d7218607e7e4a38137d50f553c2cfb901275c19edf567024c1cc6de85f` |
| `fundingRate/BTCUSDT-fundingRate-2021-12.zip` | `bf3ce484faf41d7dccfd38c5cc3d8de34d8297df30ab10784e874cc10fd1b310` |
| `fundingRate/BTCUSDT-fundingRate-2022-01.zip` | `22ee19079b620f5c6d820e7d7f8bafa7fde866d89bd664863b8bd527749c12cb` |
| `fundingRate/BTCUSDT-fundingRate-2022-02.zip` | `fa95088258a905c79ab79e8984d2f6f66933ec2e814dbab4ef9da89b01ab484a` |
| `fundingRate/BTCUSDT-fundingRate-2022-03.zip` | `4cf0883bc07f4ed4cdd3b0d8c0d166b4d15d21e666ab752f9f44401af4d6172f` |
| `fundingRate/BTCUSDT-fundingRate-2022-04.zip` | `57e2776cc68b3169fc9f8632dad67278f470cd453407a8ebe6c87963c8a31357` |
| `fundingRate/BTCUSDT-fundingRate-2022-05.zip` | `bced8a5013d09742b96682e6fd01ad4456213515a03d7586ec2b1f2689af5255` |
| `fundingRate/BTCUSDT-fundingRate-2022-06.zip` | `0cd0708f8903829eb46f98cf60f4b2516c986e1ccddf6620a5912b48e16baf93` |
| `fundingRate/BTCUSDT-fundingRate-2022-07.zip` | `29d58cce0cd45f74c6a112039835c6d9ee5a7e60e7c38c2503beb7930453a4fe` |
| `fundingRate/BTCUSDT-fundingRate-2022-08.zip` | `6f4f0c6c84c05694b4b4a5c085776730fd4059723eecd98ee6ffeb3fde4da811` |
| `fundingRate/BTCUSDT-fundingRate-2022-09.zip` | `d62cd4e13009de37add446dc4f63ead4c56dcc4955a1e60f6726bcadc5a68fa9` |
| `fundingRate/BTCUSDT-fundingRate-2022-10.zip` | `ad9efed10d4ca1567b865d7a158790977cec1b925395634217069df6696c8bc9` |
| `fundingRate/BTCUSDT-fundingRate-2022-11.zip` | `8febe5bec1a029e993bbf27490761f8c47c32849bf7dd13441b2b2f6ec1ffb51` |
| `fundingRate/BTCUSDT-fundingRate-2022-12.zip` | `4218c78331bcc4dbeb5768fa112242a880971c1f2cfd1d3f32aaa26ca34069af` |
| `fundingRate/BTCUSDT-fundingRate-2023-01.zip` | `05e3df32f28d0d50f4c5a280adee9368b4a66fc68c6ddca1b3277087ac0d19f5` |
| `fundingRate/BTCUSDT-fundingRate-2023-02.zip` | `5227accd9aaa59f71f5e682abffb58be5f99573ed208ab968b1704c81ac11345` |
| `fundingRate/BTCUSDT-fundingRate-2023-03.zip` | `ab022adff9b853d2f33cf80154e77c770f57c3392f0bbc36564b2e2cdbd0e872` |
| `fundingRate/BTCUSDT-fundingRate-2023-04.zip` | `2931039d26818edc65d4faefba84945fd1ba52989dd58fb127dc3cd7a12c7fbf` |
| `fundingRate/BTCUSDT-fundingRate-2023-05.zip` | `5d026fece46df86293054c8c56c2c8de575d30161b82979b11831831217a246e` |
| `fundingRate/BTCUSDT-fundingRate-2023-06.zip` | `3ffdde6f1dc9c3c065d77ae43f3ba64d19d4cb76512d4bc1d541933d4fb2e6f7` |
| `fundingRate/BTCUSDT-fundingRate-2023-07.zip` | `0304baed9fd407293a8a8040b30a1b68bd344803b630d33530375b421733a930` |
| `fundingRate/BTCUSDT-fundingRate-2023-08.zip` | `516a8f50631c6ede6a9642f6d1590b6a22c33ba09935501d2ace8dc1396501fd` |
| `fundingRate/BTCUSDT-fundingRate-2023-09.zip` | `3fd9df6fd1eef33cf5fe625c27012359bc6d64a68c109305d7b44a0354f533c2` |
| `fundingRate/BTCUSDT-fundingRate-2023-10.zip` | `03105cc140150bffca834bcccbddc6cfee245e079d2df1759653243bd6e92448` |
| `fundingRate/BTCUSDT-fundingRate-2023-11.zip` | `8015d2997f8d5e757ff3707ee87800ca30a74da0129daa747b64117f07bcc186` |
| `fundingRate/BTCUSDT-fundingRate-2023-12.zip` | `8f02fdd2a2da261bbf13ab301c74bdb57fae005f19d5088e9ece5f8824c1a2a7` |
| `klines/15m/BTCUSDT-15m-2020-01.zip` | `604e91a9db89202e87f10b610cf11d805a2a7915e28a07c53fc7d3921e384480` |
| `klines/15m/BTCUSDT-15m-2020-02.zip` | `a89e0dfaf3bf187d4c86c0e96c2052110682f5980c370ece041184b4615b86d6` |
| `klines/15m/BTCUSDT-15m-2020-03.zip` | `da4596277f7e914e04497d36a733722b42a6c84b5710734e4076d50c0a6675b0` |
| `klines/15m/BTCUSDT-15m-2020-04.zip` | `ebfe6813862b72c33b9defbc32317b89c0b59e03ec7d8b1a6cf4ff161716c100` |
| `klines/15m/BTCUSDT-15m-2020-05.zip` | `8ef7d076102b7d7d5f0bbd6b0ac6b36d24c6194a4c51aa239ac68e614c1824b6` |
| `klines/15m/BTCUSDT-15m-2020-06.zip` | `5674187f592088659d55aaabc8d684ba8b504e5bc7f9863b2a79ad91d46d21c3` |
| `klines/15m/BTCUSDT-15m-2020-07.zip` | `82c2528648b7202e329e4eb42f59fa2972ee4f59ea4720139160a4e683535193` |
| `klines/15m/BTCUSDT-15m-2020-08.zip` | `c3b8d9ff137e32f20b2793c4f7f7eed8bfd45648674f051cb51ce9e4ab366044` |
| `klines/15m/BTCUSDT-15m-2020-09.zip` | `b23fd2d1b8d09f8d2b10308539bbc1023b29452f2ff5365fce5bb08b7888072a` |
| `klines/15m/BTCUSDT-15m-2020-10.zip` | `723f3a5297b718ac1ea766933c12042f422ceb43f3dbfb1430e0ea5f55fa1e39` |
| `klines/15m/BTCUSDT-15m-2020-11.zip` | `9442ac3d7c5aba02bfacfe0a35ce05756263e4f462a5a694941f27dfcd76f15d` |
| `klines/15m/BTCUSDT-15m-2020-12.zip` | `c824e54aec2b63ace61d29166fcf12ac15729021b13bd1b5355f3825ecb50523` |
| `klines/15m/BTCUSDT-15m-2021-01.zip` | `3aa4530f2afd42d8cae441d2634e81a6d733a49fd33970c705afee325e4aee2c` |
| `klines/15m/BTCUSDT-15m-2021-02.zip` | `f0c941a7ecf452a3448e4a8951948518dd47e51ad7158629d5efcf410431939f` |
| `klines/15m/BTCUSDT-15m-2021-03.zip` | `d1c4cfa8137848dc3373753f8d0437eddf8db43b0e835efbc4a6da3af6935286` |
| `klines/15m/BTCUSDT-15m-2021-04.zip` | `124fab2a0fe7525a5e7b2a1dbb2b776ce12e6003770dd930a10bbd56db4cdc79` |
| `klines/15m/BTCUSDT-15m-2021-05.zip` | `f7ef372e125f87339f45fffaa329ea386d9e8be74998577fd75f807a90abae16` |
| `klines/15m/BTCUSDT-15m-2021-06.zip` | `9853eae293ad9c5b4a1395fe6d5e6257bfd2ff27433c4ef00b0169b54853b7a2` |
| `klines/15m/BTCUSDT-15m-2021-07.zip` | `86ef554b5c3c392cff96180db24268d9273905f3e8c2ed4d5e63904b0d798096` |
| `klines/15m/BTCUSDT-15m-2021-08.zip` | `f6e0c79d84839f34de1c41993624b76b1c738101cf39622d31c926300681fc5a` |
| `klines/15m/BTCUSDT-15m-2021-09.zip` | `5c74e804831937235287f424a0c34eddf525b3a366249037a34288c69b2cc6ed` |
| `klines/15m/BTCUSDT-15m-2021-10.zip` | `6fbc1ced80b2d5b722114394ce145bfe4fbc40ad233b2ec0316d3bd45b8abcaa` |
| `klines/15m/BTCUSDT-15m-2021-11.zip` | `8c3170955683fc914da107d67d8ebde0cda6f3a6250e9b4b5f6ceb94f5593712` |
| `klines/15m/BTCUSDT-15m-2021-12.zip` | `a216bab60744f399e55561df822644029178827b352d1878fd6116082f70273d` |
| `klines/15m/BTCUSDT-15m-2022-01.zip` | `46e0bc4607df992e4de6a6e76e2bf60b3a19db2b11f7b07d4a4bac4e26c6c35d` |
| `klines/15m/BTCUSDT-15m-2022-02.zip` | `7b615ec48c6bc9f4a723e08d9990136554406640055c2fd084e0c0b63d405d74` |
| `klines/15m/BTCUSDT-15m-2022-03.zip` | `2ddcc24fbcf2661020a218f2251b1cb3af03bf32633efed028c0d0921468cafe` |
| `klines/15m/BTCUSDT-15m-2022-04.zip` | `911e220f50a2a1798d35b31fce321cc4e61932a0a370c9e6837c27ff4dd8f0a8` |
| `klines/15m/BTCUSDT-15m-2022-05.zip` | `31a46b1ac257f1690e6b16c606b2fde22aebf2d605047943d885bf28fe813389` |
| `klines/15m/BTCUSDT-15m-2022-06.zip` | `7115895dc1e8425ee5ecedb18258e293decfc7769213362d928c42a29d8b6127` |
| `klines/15m/BTCUSDT-15m-2022-07.zip` | `6cd98667f9b7a127a413bd061103800f2707921a9a231e18f47d71816ef86ac8` |
| `klines/15m/BTCUSDT-15m-2022-08.zip` | `517e241a31c2062c50ca9861eb832fa9b3505b0ae67350135d5a74d812228eab` |
| `klines/15m/BTCUSDT-15m-2022-09.zip` | `776bd8021ee4b7dd8dd6530bd8b0d4f4a3287df2a72810f5dcb26e35714c8903` |
| `klines/15m/BTCUSDT-15m-2022-10.zip` | `bff25dbfad92e9c551ab77b6411e29462dbde298636144041a775330a126cd1b` |
| `klines/15m/BTCUSDT-15m-2022-11.zip` | `7f74daa2a5f1631e5b60d0dd035dfb60c0d8e5f0105820484fde8b8914d07986` |
| `klines/15m/BTCUSDT-15m-2022-12.zip` | `acf8b92a5cea478f7c32ab863b977836f629d4ff3373d20bb2b15673b57b87ae` |
| `klines/15m/BTCUSDT-15m-2023-01.zip` | `7d9c643f940a65eaae7f8618a5f997ada493076a5f91b02bdd77b559d2ab2514` |
| `klines/15m/BTCUSDT-15m-2023-02.zip` | `3d2bf498800e0526d9e7503d8f20f7dbd4fd1908e90570053a7ec5803b31118e` |
| `klines/15m/BTCUSDT-15m-2023-03.zip` | `843bdaf3f134e74e6f0efecf46dbd92952c61b9d57c6ce8b556392d81526ec48` |
| `klines/15m/BTCUSDT-15m-2023-04.zip` | `4a9416010259d5219c25ba8d29eac0928ecf6876fc4d6cc751228110e97f5138` |
| `klines/15m/BTCUSDT-15m-2023-05.zip` | `f584af353ef1a3bef7f45aa17d8826c622d04a2a817fe0c6289e37b933959b54` |
| `klines/15m/BTCUSDT-15m-2023-06.zip` | `8fb734f8a60a161b2f17b5458ed3659017a61d2a5dd24d2d810243ce1f621032` |
| `klines/15m/BTCUSDT-15m-2023-07.zip` | `c8df4ff96d804f2f57e51049bf94c11bf8bfa2f9333c0af29ab8f2504471966d` |
| `klines/15m/BTCUSDT-15m-2023-08.zip` | `8ba91ecc5bf5573c3840a2f22f4b0b6d307fc659a9e11df3c3a6e7bcf332150f` |
| `klines/15m/BTCUSDT-15m-2023-09.zip` | `f1f628bb4b1976ba632150bf999fde302ddcfc8899ff369a5119bdd5dba1e0d5` |
| `klines/15m/BTCUSDT-15m-2023-10.zip` | `bf3f1b7d22b67155373cbc0334ec44c34c8861bf2127ccd432698d95aa31ead6` |
| `klines/15m/BTCUSDT-15m-2023-11.zip` | `e70b84bec57cc0a76f9066cf5277b8c2ea3f4f4f03771f478a350160fa81b564` |
| `klines/15m/BTCUSDT-15m-2023-12.zip` | `f6b191e620d269d229dee0c5b9abfb6e9610bd0a8e6718d2a96e0e820a013bb0` |
| `klines/1d/BTCUSDT-1d-2020-01.zip` | `83f80bb879d556dc26e10bd8dca5d6a1d4484247dd1a536431fad767f7978268` |
| `klines/1d/BTCUSDT-1d-2020-02.zip` | `222261bba40db8b35ace2cf48e4b031acc262959afe51606d6006f85e80b7afb` |
| `klines/1d/BTCUSDT-1d-2020-03.zip` | `5995a21df99508a3d3605c9aa7a54acf8bfa08d8dd5f1d1ed79031baf41e953a` |
| `klines/1d/BTCUSDT-1d-2020-04.zip` | `ece152d49d8dadf02e6d3f3193071ba94a71bf571a4565374255f91624122c3d` |
| `klines/1d/BTCUSDT-1d-2020-05.zip` | `2b9c8f3955539dc29dcb25d6915e35f434c82eddca4483e9c062310e6cd85acd` |
| `klines/1d/BTCUSDT-1d-2020-06.zip` | `d52e253535b75f5af2442d620d3eb3d1e06e1e565c8ed92fb93a96b449bce7b5` |
| `klines/1d/BTCUSDT-1d-2020-07.zip` | `03a84112408f3ce5beedd98af8195cd53482b5271b434e1c48e5ea3c629ddb23` |
| `klines/1d/BTCUSDT-1d-2020-08.zip` | `92cca88204659005d28e1c6b49ab0a06051adea7d2ba7e918b4d8e4b178d86f5` |
| `klines/1d/BTCUSDT-1d-2020-09.zip` | `33dfb6af799a004f676b8cf9c81f6db3cbdb4e9183d256a626c24a8e4adf80e5` |
| `klines/1d/BTCUSDT-1d-2020-10.zip` | `22fefc0b40cec702ff683c2ef9d25c1e249677ca8055cef4d07d83839e480ad8` |
| `klines/1d/BTCUSDT-1d-2020-11.zip` | `15297014b7d6ee07dd90d97e4192e0949817da3c53ed26ef467857a53f29e0c4` |
| `klines/1d/BTCUSDT-1d-2020-12.zip` | `6cba4bb0135c45c8be87a88d0ea712455aa805b36faa431ebf30937b12d52c1d` |
| `klines/1d/BTCUSDT-1d-2021-01.zip` | `6a4dbacb435eac93e60896bd62a2320d313e6578f295a62f77cbee0d706a9981` |
| `klines/1d/BTCUSDT-1d-2021-02.zip` | `294d0696237dc225217df26103e78ac640850c34b0b6c2d44aa64a2f84a67884` |
| `klines/1d/BTCUSDT-1d-2021-03.zip` | `80d5f940649faa70cf374a2a7646d032eeb22582966125db4d24cf973c7cf899` |
| `klines/1d/BTCUSDT-1d-2021-04.zip` | `ec58d64320061a7a5b57238490b787e7376e72131d3d06e768120e2f5cd0c8c8` |
| `klines/1d/BTCUSDT-1d-2021-05.zip` | `12f232d27edb5c507bd8686108bfbe4cb6c6959960f1ff3b39a5ac831ffaf2b1` |
| `klines/1d/BTCUSDT-1d-2021-06.zip` | `10000897f2df8f86b2b6a8b218b7b5b9132fc0f25bd930c2444d458d843a00d9` |
| `klines/1d/BTCUSDT-1d-2021-07.zip` | `c3a7cd0aeda605a8b5ff327a0c596c9d60d2457d8673c3607757c9837c282178` |
| `klines/1d/BTCUSDT-1d-2021-08.zip` | `baf5fe9492f95a56f91bf80e17548294c992983e495017358be23b4c1174d214` |
| `klines/1d/BTCUSDT-1d-2021-09.zip` | `5ed176eb237c35110cd48dd219fe2d5acc59dbee1c7eb431643b1a3e14709976` |
| `klines/1d/BTCUSDT-1d-2021-10.zip` | `04be35f0945d02265243f1d7b42efc9bf3814d6c576bb629a8eac4a20ab1e032` |
| `klines/1d/BTCUSDT-1d-2021-11.zip` | `17814825202c6e1bf932c9d0b3e0fc682c73eb5dd0df23be323d3fa72909722c` |
| `klines/1d/BTCUSDT-1d-2021-12.zip` | `fa6f4fa8893ae41c856eab979d83baea8c09ac94a2d84d7942bef4c047c995d8` |
| `klines/1d/BTCUSDT-1d-2022-01.zip` | `6a345421a9e4146b8d352356c38c0c2cc21628c34e6a3f6668cf04d37de79f45` |
| `klines/1d/BTCUSDT-1d-2022-02.zip` | `2741e3ec53804c9d4b3c57f22845923e72249f63f075525c8be875f7c0db286f` |
| `klines/1d/BTCUSDT-1d-2022-03.zip` | `191cf0aba3059eacf6454b83ff803f485838be410e35910de0d38457590e9d19` |
| `klines/1d/BTCUSDT-1d-2022-04.zip` | `4bcb1a9e65a403b34f198b588a74de469863b33ddd1236133683df32e9ffe843` |
| `klines/1d/BTCUSDT-1d-2022-05.zip` | `aa39198db26d5807ff161bd10f0d3b16e5d4b9be69625d578f7634cbad55b37d` |
| `klines/1d/BTCUSDT-1d-2022-06.zip` | `9119db08b2dc695ee1d5a2921783268d06f2ac10afba2f05cba9593b42a3236b` |
| `klines/1d/BTCUSDT-1d-2022-07.zip` | `2232be04f9d396322450c5767efd273a3f87baf14760810bcfe2349c204a5f3a` |
| `klines/1d/BTCUSDT-1d-2022-08.zip` | `44418c0424e55351148f9fdc5d63523dfeb8ca1a7ec52d44cba7b90501720d8c` |
| `klines/1d/BTCUSDT-1d-2022-09.zip` | `d37049af761f66e66db0b0548f0fce7e31c24a10f9fc119ccead302884af6e76` |
| `klines/1d/BTCUSDT-1d-2022-10.zip` | `2682556173f1e1182dadc6b3cbcb8d8f84a9b717d650afbaca93cc1b93799918` |
| `klines/1d/BTCUSDT-1d-2022-11.zip` | `62f762325984c36ab67cb12112a329b935dd8a646198bc0d44700b1553e9cfe1` |
| `klines/1d/BTCUSDT-1d-2022-12.zip` | `2f8916fa91c619ab58450ad358fba3b2349c879c5f9f029aaffba0e3acf2cbd0` |
| `klines/1d/BTCUSDT-1d-2023-01.zip` | `3de9bef6b4cc6efcd32e4620aff1f27921432003184ca65f43cb03f943b085a1` |
| `klines/1d/BTCUSDT-1d-2023-02.zip` | `c2567987f8ceaa7fbaf9b5889eb7052d858e7e33707aa1e353a8c777111cee4a` |
| `klines/1d/BTCUSDT-1d-2023-03.zip` | `73c38a0c2ca448fe651c9242f62835d5fc2b3392d9b3878974cf469c6a9f147b` |
| `klines/1d/BTCUSDT-1d-2023-04.zip` | `7af72bedeca7eb147f40c909c5085c30bf5003c033e680b94efca0240f8486bf` |
| `klines/1d/BTCUSDT-1d-2023-05.zip` | `14c96d7ddea968e43e220b8e1e3f358265b89253442d98557904149c6f7d7002` |
| `klines/1d/BTCUSDT-1d-2023-06.zip` | `cda8a12d152f6c772c809ead7c780e2349239f2561f2758c50081b255784dcdb` |
| `klines/1d/BTCUSDT-1d-2023-07.zip` | `3ee0f86ac09a7bf062831a8ec84d70ec509e77ba403a73ffca049b7285223c13` |
| `klines/1d/BTCUSDT-1d-2023-08.zip` | `41b24c62e3d1faffb51c0ac9be01d771a6bfb2e3867b8dbe05786d3f700ed8c4` |
| `klines/1d/BTCUSDT-1d-2023-09.zip` | `1e96a90b3df6f41b55ab34fdfadc77d1837eae039155e1f0a4e7629fdbe019de` |
| `klines/1d/BTCUSDT-1d-2023-10.zip` | `35af8f19a76011935111104919ed535c63a225b1334f36eaa9e488e7a228dd67` |
| `klines/1d/BTCUSDT-1d-2023-11.zip` | `eae4a133704d6b3a2c2c796bffce6aff605d72cb9a0e974e0fc16adf23c150f6` |
| `klines/1d/BTCUSDT-1d-2023-12.zip` | `417fd4410cdeede8bb0f473bdece4c856a27c737e95ef3370c8333fbe9fa0023` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-01.zip` | `ae477d3d9a3259ef7f4be198038bd13def265fa548ff17c222c9dc61b9114368` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-02.zip` | `166208d28a3ce654d74baf8bdb6982c47b5b7bd9b8afcc50a9279b4735a72842` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-03.zip` | `4cf0c52b93957f682ad2ee74dc46717eb84c4083b96af5c20a129d704e68f6f7` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-04.zip` | `a42c16d75369807af013d94da6095b2346b865d8780b441e8d15144c3341f039` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-05.zip` | `1148b492d6af7dbe242942055694a3fba8017a89e3bc39b4cefe146fd8f28cf1` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-06.zip` | `b2311ef141dae561b81838fefcc36d7f7a63bd4f858f56deb4250cbbd20c0828` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-07.zip` | `89e363023c36433417803d5f814552145f8b284aaf5fadc19716a5575e6200a2` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-08.zip` | `456b8e29b27003996e7f8e3a950bc34f4ea4848595609a4f3bfb00c5c5195dce` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-09.zip` | `1575df7681f3da0007827487a5c4f4a55f4a3cda8bb7640da46e33f1fb044ac6` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-10.zip` | `d7c55a131901ff707aebe85efed075ff9b868aec793de1d131656f9991dad892` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-11.zip` | `7c33dfc25ce9e80253bfa40698e1a64d17c09e91149ab95cfbaba57bc8ed06cb` |
| `markPriceKlines/15m/BTCUSDT-15m-2020-12.zip` | `0e3a59e3d4d79573434184e10ac86eda55cd958f90eefdb00443fda020683614` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-01.zip` | `97f228e0bb783b6e06dc00cee5470f37356b24d52bb90061577e931e9c6521ce` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-02.zip` | `265c3c795aed9677d36b16506620b8e1c68ddcf46b28c76a25e47df7e5ebf60e` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-03.zip` | `b0befa74387d14ab7815b363b0200777c6a62c2619f356d26b1ed22d9262e21f` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-04.zip` | `3a49d3b7b00e1d7fe0fdb2ee470a9f1b572eb20f0d714486df45e1860bf1b55e` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-05.zip` | `73eb001945de9ed0a089e2aa0f2889c38ebcae716b96e11bd6794388fecb6fa4` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-06.zip` | `b1a5b5d5fb91c36e42bcb28d6d84fe91e886cd56b0a8c812f913de3005ce8f75` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-07.zip` | `0fff16c59a91d579af0bdb9295e57c7aa7196fd17d4d149d77b1b3207d43d8cb` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-08.zip` | `231b83497c347116290d367c4570b7f54861b9fac5e94fda9d47574e4b40406c` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-09.zip` | `e7e68be1c845d9a7b9fed994b8b7120807d87f370b189d7baab45e1265434b46` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-10.zip` | `0223a32f4f1943a7bb5b00f15c8c0f3556ba3e28256a880b1c0861bd8b01b214` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-11.zip` | `c42a58dbc1a43d5ec340bd7b1e0701be208ad7432ac77e581fa48c4c768051ac` |
| `markPriceKlines/15m/BTCUSDT-15m-2021-12.zip` | `8aa10d3e6304034141137c2bc5d1beabb5e47b1ab8dcadf54bfccfc9ec7b363b` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-01.zip` | `0350f9fa5e33701bf0def8eb254bb041c8e61b5c1df90c2b285812cd13eda602` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-02.zip` | `d22530553220679a2e52a4ce2a35a13399a98adef08db9bb4fc20916a3f2ae4b` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-03.zip` | `d1a2a1bc268d2a7d4f3e20bc08d7efa8985c639d82e9cc8ac033f433dbebe5d1` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-04.zip` | `d065b9c799edc8b04c50c6618abea27532d2784a1cc4d96126577c506aa862ee` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-05.zip` | `5b4d09ee30b1002e6573de6dba5b43c2882c8568cd242da85707fcc444d21ac9` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-06.zip` | `98dede19969b73963e0bdaed0cf29ded9b086c614cd086be88d7ac8767aef543` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-07.zip` | `74f17381ea278153afd675b8409bbd70f496e9f7c24b8c89690ff1754184a2eb` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-08.zip` | `abddac4d42620870ea9d09565ba494e3ab2a7eaba3351b0e894338aa677b8cbb` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-09.zip` | `5966f922c4b23494dcc004dd4c7c58a94b7ba090ab5c99d835830aae552c81ec` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-10.zip` | `1e118bcd1aabba4374beff493dc20da1662599e9517d6efbc670f42a82748e5d` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-11.zip` | `1e0739bb5693750c4008925435872118d8d6afafac3be4ba6e0e1226c2c90aad` |
| `markPriceKlines/15m/BTCUSDT-15m-2022-12.zip` | `590addd6f3a896d3eef9ee3f75492699c025fafed0f88e1212c19eef6c7b7e52` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-01.zip` | `fdb3ed021855551bb5047072965319f1e40e10eed6c466e487f5eb888c888b9e` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-02.zip` | `fe22c79e61fa72b17e64d58209d6cc890ae752c7b8ae8d8b5594379f3f516fe7` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-03.zip` | `40336862e8e8a5097c5a4113adb81ebffefb31a489c4c4966ce6aa9f9b210601` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-04.zip` | `514bd65df49b55ec1e038d2a792d063bccbb1f8eb154cddc0fe8300f5bb26772` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-05.zip` | `e0156dce8b6a42eac03a0e46709fcdec9a5537b997b68ee5579b32b0488c3d75` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-06.zip` | `06f22871cf4b82f364aadb84d5ca50671fcd853efc3af037d4168750afea1777` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-07.zip` | `dd2aec59c5e48cfdf316296dfb1aaf9de45dc5064e714cac4e082b2d47add62d` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-08.zip` | `d2a56ce8417f92bc903953d8c8f4635b211ed47ca904932603819e571b99cc9c` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-09.zip` | `a600291b3109e0eeb783947dbffd550354b24dd3f9fac2612f1d76ef215d50e0` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-10.zip` | `25e235ee566fda3cc24261aea3667ff33376c21774b3428fe34a4d7274a7bc59` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-11.zip` | `b6b090c627a53849db3ba6657e0ad767cd15e1fdef5f15465b273d0c2584f74f` |
| `markPriceKlines/15m/BTCUSDT-15m-2023-12.zip` | `f1c827e6dd177777eda8a1db09829d84732f708223a18890766f2b47740a88f8` |
