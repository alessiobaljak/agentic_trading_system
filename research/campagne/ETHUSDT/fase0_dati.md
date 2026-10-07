# Fase 0 — I dati di ETHUSDT

Scritto dallo script `codice/fase0_dati.py` sui file scaricati il 7 ottobre 2026 da
data.binance.vision (file mensili, futures USDS-M). Solo dati fino al 2023-12-31: il
caricatore rifiuta oltre. Nessun rendimento di strategia e' stato calcolato qui.

## 1. File scaricati

| Serie | File | Mesi attesi | Mesi assenti |
|---|---|---|---|
| ETHUSDT/klines/15m | 48 | 48 | nessuno |
| ETHUSDT/klines/1d | 48 | 48 | nessuno |
| ETHUSDT/markPriceKlines/15m | 48 | 48 | nessuno |
| ETHUSDT/fundingRate/ | 48 | 48 | nessuno |
| BTCUSDT/klines/15m | 48 | 48 | nessuno |

Checksum remoti mancanti: 0. Ogni zip e' stato confrontato con il
suo CHECKSUM SHA-256 pubblicato da Binance prima di essere scritto su disco.

## 2. Copertura e buchi (candele da 15 minuti)

| Serie | Prima candela | Ultima candela | Candele | Attese | Mancanti | Buchi |
|---|---|---|---|---|---|---|
| ETHUSDT last | 2020-01-01 00:00 | 2023-12-31 23:45 | 140256 | 140256 | 0 | 0 |
| ETHUSDT mark | 2020-01-01 00:00 | 2023-12-31 23:45 | 140062 | 140256 | 194 | 4 |
| BTCUSDT last | 2020-01-01 00:00 | 2023-12-31 23:45 | 140256 | 140256 | 0 | 0 |

**ETHUSDT last**: 0 buchi, di cui 0 di almeno un'ora.

**ETHUSDT mark**: 4 buchi, di cui 2 di almeno un'ora:
* da 2022-10-02 00:00 a 2022-10-03 00:00 UTC: 96 candele mancanti (24.0 ore)
* da 2023-02-24 00:00 a 2023-02-25 00:00 UTC: 96 candele mancanti (24.0 ore)

**BTCUSDT last**: 0 buchi, di cui 0 di almeno un'ora.

Candele last senza candela mark allo stesso istante: 194; candele mark senza last: 0.
Nelle barre senza mark il motore usa la candela last anche per la liquidazione (scelta dichiarata in `codice/comune.py`).

## 3. Sospensioni e cambi di contratto

ETHUSDT non ha avuto ridenominazioni (nessun contratto «1000x») ne' migrazioni nel periodo:
la serie e' unica e non c'e' alcun punto di cucitura. Controllo meccanico: salti fra la
chiusura di una candela e l'apertura della successiva oltre il 5 %: 0.

I buchi della sezione 2 sono le sospensioni (manutenzioni di Binance o dati mancanti nella fonte):
il motore li conta e addebita i funding caduti dentro un buco sull'ultimo mark disponibile.

## 4. Funding

Settlement nel periodo: 4383, dal 2020-01-01 00:00 al 2023-12-31 16:00 UTC.
Intervallo dichiarato dai file (ore), con l'istante da cui vale:
* da 2020-01-01 00:00 UTC: 8 ore

Distanze osservate fra settlement consecutivi (ore: numero di casi): 8: 4382

| Anno | Settlement | Tasso medio per 8h | Tasso mediano | 10° perc. | 90° perc. | Quota positivi |
|---|---|---|---|---|---|---|
| 2020 | 1098 | 0.0250 % | 0.0100 % | 0.0100 % | 0.0680 % | 97 % |
| 2021 | 1095 | 0.0343 % | 0.0100 % | 0.0100 % | 0.0945 % | 96 % |
| 2022 | 1095 | 0.0007 % | 0.0039 % | -0.0101 % | 0.0100 % | 66 % |
| 2023 | 1095 | 0.0075 % | 0.0083 % | 0.0002 % | 0.0100 % | 91 % |

Questi numeri descrivono il costo del funding, non un rendimento di strategia.

## 5. Volume medio giornaliero in USDT (file giornalieri nativi)

| Anno | Giorni | Volume medio (milioni USDT) | Minimo giornaliero | Giorni sotto 20 M |
|---|---|---|---|---|
| 2020 | 366 | 723 | 45.3 | 0 |
| 2021 | 365 | 7,597 | 1,435.7 | 0 |
| 2022 | 365 | 7,581 | 1,464.1 | 0 |
| 2023 | 365 | 5,513 | 671.6 | 0 |

Giorni sotto la soglia di liquidita' (20 milioni USDT al giorno): 0. Nessun periodo da escludere dai test.

Volume medio nel periodo di costruzione: 5,136 M USDT/giorno; in validazione: 5,850 M USDT/giorno.
La fascia di slippage della scheda (0,01 % per lato, volume 2023 oltre 1 miliardo) si applica a tutto l'in-sample.

## 6. Controllo dell'aggregazione (15m -> 1d contro i file 1d nativi)

Giorni aggregati dalle 15m (solo giorni completi): 1461; giorni nativi: 1461; giorni confrontati: 1461;
identici in open/high/low/close: 1461; diversi: 0.

Tutti i timeframe della campagna (30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d) si costruiscono dalle 15m con
`aggrega_candele` (gruppi allineati all'UTC, solo gruppi completi): un giorno con un buco nelle 15m
non produce la candela aggregata, e lo stesso vale per le candele piu' corte che lo contengono.

Candele disponibili per timeframe (intero in-sample): 30m: 70128, 1h: 35064, 2h: 17532, 4h: 8766, 6h: 5844, 8h: 4383, 12h: 2922, 1d: 1461

## 7. Storia utile

Dal 2020-01-01 al 2023-12-31: 4.00 anni, sopra `storia_minima_anni` = 2. La campagna si fa.
Costruzione 2020-01-01 -> 2022-10-19 (1.023 giorni), validazione 2022-10-20 -> 2023-12-31 (438 giorni):
fissate nel log (voce ETHUSDT-N003) prima di caricare i prezzi.

## 8. Impronte SHA-256 dei file in-sample di ETHUSDT

192 file. A ogni sessione i file si riscaricano e si confrontano con questa lista
(`dati.verifica_impronte`): una differenza e' uno STOP.

| File | SHA-256 |
|---|---|
| `fundingRate/ETHUSDT-fundingRate-2020-01.zip` | `0ce8da3b2ee7eceb6616efa215a2a1b1aab7b5b04becebe73634a95ec0abfa90` |
| `fundingRate/ETHUSDT-fundingRate-2020-02.zip` | `5a1de843dc3f098e86ca3c0979b38591d57d18664a1079588e61def93224fa06` |
| `fundingRate/ETHUSDT-fundingRate-2020-03.zip` | `0b9edb31ec6aedad0248d54e89b7ea5ff3cc4ab719519751db3de334caf54303` |
| `fundingRate/ETHUSDT-fundingRate-2020-04.zip` | `ce2208113358208182eaae41971fb5762e1794a04b4a606368416d08eea2d41b` |
| `fundingRate/ETHUSDT-fundingRate-2020-05.zip` | `77f5790ae26f95caee52b58317ee65d13b0eeb61f73d83482fd5d3aa153ab300` |
| `fundingRate/ETHUSDT-fundingRate-2020-06.zip` | `2e6af078edbe3e0df30d12d0d381652949572ce514222a257efe1f4eb145dae0` |
| `fundingRate/ETHUSDT-fundingRate-2020-07.zip` | `1983ad90e1d1f98eefd2c23b9eb209d26e4e2efba2f4e8b5e662e8a7d563bc56` |
| `fundingRate/ETHUSDT-fundingRate-2020-08.zip` | `d4e766270a078741387ba564103d285ad9a2c05c7e6df9ad0b03619248bb041f` |
| `fundingRate/ETHUSDT-fundingRate-2020-09.zip` | `cdee5c299c22dda85a5d5449e19250f7bc66c0d52759f9de0a49cc233520510d` |
| `fundingRate/ETHUSDT-fundingRate-2020-10.zip` | `47749a38b41b185d786af96bf41c796edf8ea517cf76d6d61402974c629e0239` |
| `fundingRate/ETHUSDT-fundingRate-2020-11.zip` | `9b02376eaa04be4ec2e201b492ef2a3c34dc61542492c715b5cea5dec5f01d36` |
| `fundingRate/ETHUSDT-fundingRate-2020-12.zip` | `f99267a3fef35dd201e76c8338be877fb52883376b4cd0acb890a1387de0b0d4` |
| `fundingRate/ETHUSDT-fundingRate-2021-01.zip` | `4c18c1df8904dea9770aeba5326d26b3fa9a3ffac4891f5f7125d4be2da847c0` |
| `fundingRate/ETHUSDT-fundingRate-2021-02.zip` | `15e9a939f253a11fc1af2858bb3844f3d39019ccf7efa66a9456f0f60afba3dd` |
| `fundingRate/ETHUSDT-fundingRate-2021-03.zip` | `2bcaadc8206cb8d76a26f0f3cbf97020b747545b0e75c3dd8a3b195b435478a5` |
| `fundingRate/ETHUSDT-fundingRate-2021-04.zip` | `2fee34e8b9b6e828d01bab0df1c67104f7a98f3c063668c8db627b802ffa5a95` |
| `fundingRate/ETHUSDT-fundingRate-2021-05.zip` | `21809ef6691a1441bd55ba4af4494a038d1a399ae0ae432e80cb41b47d71f3bd` |
| `fundingRate/ETHUSDT-fundingRate-2021-06.zip` | `8e58ccf8f52c69c55754492daafadab92d4ca8c8bd027f4532582d06e9f36063` |
| `fundingRate/ETHUSDT-fundingRate-2021-07.zip` | `f8f538bedf642052e428cd25f3134784de6e62a136e76f6a07ea6e79dfc9c39d` |
| `fundingRate/ETHUSDT-fundingRate-2021-08.zip` | `0120b284bde23d077e1e26e5e4b56fd3e2d1d82a3a7fe0e9de26825b9fc9c0db` |
| `fundingRate/ETHUSDT-fundingRate-2021-09.zip` | `4b4a94cdafbb8fea7762c266aa79b183700b7c9dcf7e981f7fdbe9372f2eec66` |
| `fundingRate/ETHUSDT-fundingRate-2021-10.zip` | `4dfb8698f6951b2c66229e1c687977eae0778bb703d6268232da2ceb3e9b5e6d` |
| `fundingRate/ETHUSDT-fundingRate-2021-11.zip` | `d9a7e22a237717f23d4b0505f14613359b7ea7831b23a78653a891cbbe3d521c` |
| `fundingRate/ETHUSDT-fundingRate-2021-12.zip` | `788d5c57e7cbc8e6b94ed4d7672618a85311edf1d7f0888083410d0d3389d811` |
| `fundingRate/ETHUSDT-fundingRate-2022-01.zip` | `9f5bd01450b05a8c5e48cdc99fa147e85c82ecf7ee7919fa543a4e6039a2b98d` |
| `fundingRate/ETHUSDT-fundingRate-2022-02.zip` | `9c35e30327ac8915cc1333415b7d5018425781c81918e349d26b734525fcdfe5` |
| `fundingRate/ETHUSDT-fundingRate-2022-03.zip` | `3de0714a2b2582029b32147815298b6e67e972e776ca3f68a4208823b4109404` |
| `fundingRate/ETHUSDT-fundingRate-2022-04.zip` | `7c306ac8b6275a857b064916080e0b6ec502b25a4501c84c3fd2c0b077425de3` |
| `fundingRate/ETHUSDT-fundingRate-2022-05.zip` | `c458330243c9d8e048ffc7168c9e3c077c01bb82b1644097a4893fee34069b78` |
| `fundingRate/ETHUSDT-fundingRate-2022-06.zip` | `f6f3a69b656b91500b41501a230e663ccc3c1a65f46273595b00682d8f6fabb1` |
| `fundingRate/ETHUSDT-fundingRate-2022-07.zip` | `17826e5591af8660a7fed74d60e24eee77c822cf0d901dd8af355a10a36699aa` |
| `fundingRate/ETHUSDT-fundingRate-2022-08.zip` | `a2680549de5e087566f4d323b3a812c2b9863528c6bc49b0e551cb42c381bb4d` |
| `fundingRate/ETHUSDT-fundingRate-2022-09.zip` | `816e4de946d9f854cc457c86ca396b9cb49b46e80cf44941b59b9ad2124f2ef8` |
| `fundingRate/ETHUSDT-fundingRate-2022-10.zip` | `e434c29eb544cc57ff574e38685535bb7d04703aee54bc5d52f53cea372810e6` |
| `fundingRate/ETHUSDT-fundingRate-2022-11.zip` | `4f4e52f176f69e99353959d287874a4d4a135b5bb4ea85514dd5a3e65958b2d7` |
| `fundingRate/ETHUSDT-fundingRate-2022-12.zip` | `8cd0e885d63b85ee602d80eaae956f9ee3e0e25db264eb5c74026a9ae0d71f4e` |
| `fundingRate/ETHUSDT-fundingRate-2023-01.zip` | `5647d5978092d220eb14e11c7854d86815d0eb6204197e37b4808cc599e986f3` |
| `fundingRate/ETHUSDT-fundingRate-2023-02.zip` | `7da37820c15fb08600ae668551d0b724326b8f71d761582990721059280a221b` |
| `fundingRate/ETHUSDT-fundingRate-2023-03.zip` | `5110b60cbbc5f26048ce02575c26444ea2ed497baed9a5609e118359e1ca3b51` |
| `fundingRate/ETHUSDT-fundingRate-2023-04.zip` | `fa3a3cf7c3b8285687ae8c8014eed8bc58ad3ceb33ccb62ff4298048213c0e6c` |
| `fundingRate/ETHUSDT-fundingRate-2023-05.zip` | `bf890ea68d979942ed296b058390eb98b0b495547fee2117d3b76d5e7f629b24` |
| `fundingRate/ETHUSDT-fundingRate-2023-06.zip` | `b3ddac1309f9a684f4e811776a6c09fb2239bb8d1ae0ff4bd342a1c32a5e171f` |
| `fundingRate/ETHUSDT-fundingRate-2023-07.zip` | `82577976d8acd886fda84179ee38c9e7ef445732c3b6a062d6ffd2a9e3cc30bf` |
| `fundingRate/ETHUSDT-fundingRate-2023-08.zip` | `cf749429c366cef3302a804b3e702937e5f1a77aeddc5b628dca7da547a8935a` |
| `fundingRate/ETHUSDT-fundingRate-2023-09.zip` | `41ac7eb67a46d14d97daec4c37e8229df5ac6b165639ad4b2c54bc7374930341` |
| `fundingRate/ETHUSDT-fundingRate-2023-10.zip` | `ccaf4474f0dc94adedd4330c14995f338186caa2cc9fd0d2e2c55f74cf263a5c` |
| `fundingRate/ETHUSDT-fundingRate-2023-11.zip` | `153ec1450eb5d999ce253e2c7ca2e81b79a523ff52dd18b14faefab8212b999b` |
| `fundingRate/ETHUSDT-fundingRate-2023-12.zip` | `91bdf41566cebb86c6f0e3646b0037de9c22e14ee2f592c5722c7e4a19c91119` |
| `klines/15m/ETHUSDT-15m-2020-01.zip` | `be850bcde4421807ca925375f9f529a94e132be473382202f57ea49ff124c8d6` |
| `klines/15m/ETHUSDT-15m-2020-02.zip` | `1ee452ca7e0874b3170e7e170c39516da1b4cbbc7760a715733fd47fcc79187c` |
| `klines/15m/ETHUSDT-15m-2020-03.zip` | `5c16b4231cc0366d246b60c4daafc3c7fc7127aed43a7401b7b4743d1898f505` |
| `klines/15m/ETHUSDT-15m-2020-04.zip` | `4fd06af73bdabdf6eb668dc738550a337cb8647a0c7c60b586abb39a9e3ba6ac` |
| `klines/15m/ETHUSDT-15m-2020-05.zip` | `7095867a2ea3a9123469ec2bb13ea4865b7b092f6f2edf6c67c8a406852c1607` |
| `klines/15m/ETHUSDT-15m-2020-06.zip` | `6e91d9437b28a7f6e47b43ccace4377456ca6cf75164affbbf1b5f33687f630b` |
| `klines/15m/ETHUSDT-15m-2020-07.zip` | `323cdc8f50a1822c421d15f715d9d514d513c2c4ec479d4f656228b2e0f3944e` |
| `klines/15m/ETHUSDT-15m-2020-08.zip` | `817d409f95802453bb62d34cb3a76475d863695429b3f62304a47dc858dacb98` |
| `klines/15m/ETHUSDT-15m-2020-09.zip` | `44cb7ac27035e1abbfb0877d7a32e707c8bc9b1e8c5c31e4efed45007db8715a` |
| `klines/15m/ETHUSDT-15m-2020-10.zip` | `9c65599b32eb9439f6ee80dcc052c111c9d1eea2fc64f858a2b78d47a516b62c` |
| `klines/15m/ETHUSDT-15m-2020-11.zip` | `3d5347a1174a5f641220d589877a1104241eadac7ee4a459a6b6b269329961ec` |
| `klines/15m/ETHUSDT-15m-2020-12.zip` | `5790ffe90d9808ed526b274f78f3534f7516f38d2dab69184a4d26f0846dab4a` |
| `klines/15m/ETHUSDT-15m-2021-01.zip` | `8949195778e2b05370e9082dc60c8f7a9c83631252eb9491c3c3c84b07c0bec7` |
| `klines/15m/ETHUSDT-15m-2021-02.zip` | `779cc2fbd39b028049c038233b9d3c1fcfa41ea9d1c9883f33dbf7ccc3dbc847` |
| `klines/15m/ETHUSDT-15m-2021-03.zip` | `26b21140c3dc70d0df78db60ca98ab1be8d5a874eefc74c72b037f720167d0c4` |
| `klines/15m/ETHUSDT-15m-2021-04.zip` | `60b7d0bfbed9bf1bbf9554dcf08f9c676740ef7161fddcc0fa408846a8072878` |
| `klines/15m/ETHUSDT-15m-2021-05.zip` | `77c8ca3914321c8e59c34ba7d23a3c7d63f5e83c219e55c767ce9953022dcbf2` |
| `klines/15m/ETHUSDT-15m-2021-06.zip` | `913546ade2f9425e89989e839ca3d3d14ac29838eb83e2fc735ea2438e2eb141` |
| `klines/15m/ETHUSDT-15m-2021-07.zip` | `c5c52ba14f8964e3669c7c147358981b2d31e0b7982b0567f1ffc24ec857831d` |
| `klines/15m/ETHUSDT-15m-2021-08.zip` | `95981cb8a9dda8d51be3a0d323d8d89ee4410f6e4ee3ea74e41d54b8152770b0` |
| `klines/15m/ETHUSDT-15m-2021-09.zip` | `7e9db70488fe7324c7c58a905638bf81437f11c61018238190ca6723a828e9e9` |
| `klines/15m/ETHUSDT-15m-2021-10.zip` | `755a29a1a30d7c18f6932a5ceb16288a61968fb2e1ada5611b58c5aad46947da` |
| `klines/15m/ETHUSDT-15m-2021-11.zip` | `016ce492025483e69485963f4d503ef0b04b7d961f2c89f2fd455d6bb15169fc` |
| `klines/15m/ETHUSDT-15m-2021-12.zip` | `88eda6c9262c4322022ed9017232756e9ba0aca6a3d4d34c23850da6f241812d` |
| `klines/15m/ETHUSDT-15m-2022-01.zip` | `f34e867abd33f17c4c9722338d1e6098da86ceb1ed7e68da704de4a1a6fc0b62` |
| `klines/15m/ETHUSDT-15m-2022-02.zip` | `c4e6259d3d5bab4e1d2349c42d6ac0af6514237b55683a36364672b9be5ec77e` |
| `klines/15m/ETHUSDT-15m-2022-03.zip` | `763c04742dd6d47f2c01b3215bededcf606c07e7df0af78c341fe9590c5d7d65` |
| `klines/15m/ETHUSDT-15m-2022-04.zip` | `cbab8ad431d7c56272aee8eb21be74c33933e63aebeb45fdc0a51d71e3342a29` |
| `klines/15m/ETHUSDT-15m-2022-05.zip` | `89f651e2e396166ab54a66e53fab3061eb82f7c1bdd33352752c9956da586aae` |
| `klines/15m/ETHUSDT-15m-2022-06.zip` | `14a2d341f726acda252f3cd17b20a21bc75b8566fe5a4d060afbc3c763922dd6` |
| `klines/15m/ETHUSDT-15m-2022-07.zip` | `c248a49cae33740d26b9ba7f3828630fdf0428ad36c68c8752c276e11f4146d0` |
| `klines/15m/ETHUSDT-15m-2022-08.zip` | `6a9e64b652806493ec753eec55780cad6420e8fd0daf007778641368d1d4ccc9` |
| `klines/15m/ETHUSDT-15m-2022-09.zip` | `e3c24622eff11720bd241a37a09eee904424d5f095bed163803faaec1f8094b5` |
| `klines/15m/ETHUSDT-15m-2022-10.zip` | `8406a50b9db5e1b2c2753e8496372f9199193041c698aea959faf40e7786fcba` |
| `klines/15m/ETHUSDT-15m-2022-11.zip` | `353bbe11f3aa0dbcd0772c78232e2ec104b02d105ea4173e1f619eed943b5971` |
| `klines/15m/ETHUSDT-15m-2022-12.zip` | `d311ac52d3a542b126e1b6574498609c32c5f0adf566d9f6a5b69c0b72f5a059` |
| `klines/15m/ETHUSDT-15m-2023-01.zip` | `4b94b8078f553d56986966a816ab1888b57f1c4ac4be9385aa8eb4a0f5d0b5bf` |
| `klines/15m/ETHUSDT-15m-2023-02.zip` | `181f161c13de3e1918f987845d0d7a3e698634d98e5ca83d2a46baaa8602feba` |
| `klines/15m/ETHUSDT-15m-2023-03.zip` | `1402dfca8c6b948335ab7500cae23093e734a112c11474fab8f10bc93bdc07e9` |
| `klines/15m/ETHUSDT-15m-2023-04.zip` | `55fc2dcc0749ab4b21d12aa9f8d08148a148dc520fc0cf430409189ade9d26c1` |
| `klines/15m/ETHUSDT-15m-2023-05.zip` | `3b28964792ad73c04a2c95a40704b426b1ebb2d90e215531406d7b029f6b5c3c` |
| `klines/15m/ETHUSDT-15m-2023-06.zip` | `14cf1b27bb9325e34df4dd0cb2d2b05ae63a6d5706dbf5e0cb6b8f7e92e4cbe9` |
| `klines/15m/ETHUSDT-15m-2023-07.zip` | `7a9c96acb0a88270fd79f7ac5b154ba34467d33c600bec63438bbefaf13e1660` |
| `klines/15m/ETHUSDT-15m-2023-08.zip` | `b8e1882d9bf4ca6755794b20e8631fe2f030a05e252d0c94d14d4f0638aa33bf` |
| `klines/15m/ETHUSDT-15m-2023-09.zip` | `a4f6804bd2edb66ff385d70a029a52447e68f31d94cccc803aafe34bb537d8ce` |
| `klines/15m/ETHUSDT-15m-2023-10.zip` | `ecd769121c93962daf9cd5ebfc251e44466db72cf9e1487ce343888056dfadd4` |
| `klines/15m/ETHUSDT-15m-2023-11.zip` | `cd0ddd41ffd597a7c886cc84406c7e12d8de1d1a330680e9f47fe50f474f46ec` |
| `klines/15m/ETHUSDT-15m-2023-12.zip` | `8df8f98f81eda3ffc0a3514d9b643c0701c433fb2ee2241dac4e04abe6d312c1` |
| `klines/1d/ETHUSDT-1d-2020-01.zip` | `1c447c2d1ee892420395690ae6365ecc3ae24f091e17807ccb3be93fe850f58c` |
| `klines/1d/ETHUSDT-1d-2020-02.zip` | `1403c48c73b5f8c8e21c16f6ad2074941ebecd665fccb6ec5bbf8a959c7c6b23` |
| `klines/1d/ETHUSDT-1d-2020-03.zip` | `37d8680fd6388dd6e5016094a93a0408279422747a442a24f8a0446e0c69fc79` |
| `klines/1d/ETHUSDT-1d-2020-04.zip` | `8b563aa55b8b7ad384ef7686866a603425a0e7ebd553930a1cfd72ee1a5e5617` |
| `klines/1d/ETHUSDT-1d-2020-05.zip` | `a2168590a401c001e536907d2493a68ea0f82e9e9fab99b07bc6dd188398ebb5` |
| `klines/1d/ETHUSDT-1d-2020-06.zip` | `797f29c89d00ffd397fca4000e69269abbbb5a039834e636bfc14333566d3d6d` |
| `klines/1d/ETHUSDT-1d-2020-07.zip` | `ec32dd63bdccebc9bd4ace7cafddd024c41b17fc03f528b2f3d1f08030438af4` |
| `klines/1d/ETHUSDT-1d-2020-08.zip` | `50a82930975079187ddb0836b9a4014691f4caa47f3618ebc9d9b2a050d9c3a6` |
| `klines/1d/ETHUSDT-1d-2020-09.zip` | `671c9b85dd6e525f6c98239d8b63b0c64c1478210d238ba47de86b54c64eaa1a` |
| `klines/1d/ETHUSDT-1d-2020-10.zip` | `f140c378b5e55560ac01fc48e1d2885a8e23e7e15b258ed778c003684532953e` |
| `klines/1d/ETHUSDT-1d-2020-11.zip` | `764d33511032c34be8b563591d7730bd09858dcde8588ffb5ef548c4c728a894` |
| `klines/1d/ETHUSDT-1d-2020-12.zip` | `1a53353c7ad246ccccdb37df0162f0add0cd9529c974edf077b3f4aa64bcbe88` |
| `klines/1d/ETHUSDT-1d-2021-01.zip` | `2e2ccf271a78446c410d6617c093b8b0693f5e2cb7341518c6d7567fffca4e15` |
| `klines/1d/ETHUSDT-1d-2021-02.zip` | `f5e4db8529bc89c792a0a78e791d0e90d613be6eff4041a5a024106a88a2d0a3` |
| `klines/1d/ETHUSDT-1d-2021-03.zip` | `fdf66b48c460eeb873b7c567b129c9f93fe14c50e1dbe5afb769881b01846e95` |
| `klines/1d/ETHUSDT-1d-2021-04.zip` | `ab57d26d80cfb3e29deb5204cd04c812dd5f53a1c07b669266cf93ee74f8114f` |
| `klines/1d/ETHUSDT-1d-2021-05.zip` | `5e438213128dd75c42a40ab6fb637c6d261ff10cf2d453177d9a13a7178b25e5` |
| `klines/1d/ETHUSDT-1d-2021-06.zip` | `99dbca88b4fb842ed40d312ac82cbfa33e8e3e147dc02896ca6f910c77a39269` |
| `klines/1d/ETHUSDT-1d-2021-07.zip` | `c36924e39814cdcab057c2abd9efedccb7dfd0b4ac2e5ed86346b52d8ce24489` |
| `klines/1d/ETHUSDT-1d-2021-08.zip` | `5caa2fca456e28deff2e39cd7ee2c85946fe3d8be3d23624c67b91fd2da9257b` |
| `klines/1d/ETHUSDT-1d-2021-09.zip` | `cdca161399a79cb2eb5958cd11a6b976f3a0fd7cadd561dd423a30a17d9af050` |
| `klines/1d/ETHUSDT-1d-2021-10.zip` | `0c8f6b52c608751b9f56aa7663d53364d2f87d51ded005380b2fb2cb6a28c3af` |
| `klines/1d/ETHUSDT-1d-2021-11.zip` | `dccb3f8867a5672fc18b285b963f61e43ef1a3c9c0cf2bea654d1f214ec95aa4` |
| `klines/1d/ETHUSDT-1d-2021-12.zip` | `fb0cc2d6b5b61c303cf766274a44bc77e0851dde0492f275f557c4fbc22fa021` |
| `klines/1d/ETHUSDT-1d-2022-01.zip` | `c41822818408e353b1dccb10eb9660f946a28c9aea5c007fa33df7b002423a5d` |
| `klines/1d/ETHUSDT-1d-2022-02.zip` | `a294d9cfd32f2f269ebbd00b1ee1ffa5c2aa86186853afcf6aa89a839d45b407` |
| `klines/1d/ETHUSDT-1d-2022-03.zip` | `3f381d3b20087be90992ee6095df84410f316caaeb3507d354b5d622621b327c` |
| `klines/1d/ETHUSDT-1d-2022-04.zip` | `981a55b337e8e4fcc4d4709d241d09ee9c49467e36fa506f66b82a8254ba09b2` |
| `klines/1d/ETHUSDT-1d-2022-05.zip` | `feecae43defd8555f7dc07ce6748857933f60b388c41700a766ba9fda50820a7` |
| `klines/1d/ETHUSDT-1d-2022-06.zip` | `b11ed08bd062f5c1110bc3c0e39be6101e53f258be0910d58d2f8b7ca3aa5c00` |
| `klines/1d/ETHUSDT-1d-2022-07.zip` | `27722df479d5f0b4a01744afc961482ff3f423d01832f41c96cb669b4f09ba98` |
| `klines/1d/ETHUSDT-1d-2022-08.zip` | `d9dca0a01cc50266277c8add1e23d47543d8663d4263c983aaf5149aa7f3617b` |
| `klines/1d/ETHUSDT-1d-2022-09.zip` | `63b81d8592a90989c55beacee91ed69d1b417c750bc7e4fa2ca733607e38290b` |
| `klines/1d/ETHUSDT-1d-2022-10.zip` | `cbf3d0d9e2a8a2178bc700109a68287a6642d210539bff51bc591ee86be01796` |
| `klines/1d/ETHUSDT-1d-2022-11.zip` | `f95a3203f726f6dde1caeb5ed1bd2cab4749c52b808fee48054caafc3696f62c` |
| `klines/1d/ETHUSDT-1d-2022-12.zip` | `3edd3c381d1ee51d4c58921645c12d2a5862910f5294c5703055b116ed33481f` |
| `klines/1d/ETHUSDT-1d-2023-01.zip` | `3d3fcbf5ffbca73de14355c7214252d0a7b5e36a504f51635c2cfd6c276c13ee` |
| `klines/1d/ETHUSDT-1d-2023-02.zip` | `11d6ed63254c4134a4951e765bd8b136c3c5424fe8868bb50fb0f398ca96b998` |
| `klines/1d/ETHUSDT-1d-2023-03.zip` | `e52713b6f21b7da1f9208b44b4917a4bf06baff3501b18e6e95ce3ca0abc60e7` |
| `klines/1d/ETHUSDT-1d-2023-04.zip` | `62dba6202277441943d2e7e0dd5c80c0366d6f20a528fbe870e1900d6dc583ea` |
| `klines/1d/ETHUSDT-1d-2023-05.zip` | `74fff9b141ccabc48377e9247607f7e2fc6427ed9ccbfc31a82f61ab7ad983ff` |
| `klines/1d/ETHUSDT-1d-2023-06.zip` | `92de632c4c78c77201b0eb9325ad8deb0cfb22fda6c6fa8e51c8414662fa10ae` |
| `klines/1d/ETHUSDT-1d-2023-07.zip` | `94d6cba75f179498ae673a748186ce36533c1dedfa04ae5ac53e5a8bf2a30051` |
| `klines/1d/ETHUSDT-1d-2023-08.zip` | `a280e5e94456ab8798b0a0e5525dba985221fd3624a17a96b2d2e19591e6426f` |
| `klines/1d/ETHUSDT-1d-2023-09.zip` | `4b5e61f95fe3af03d3cc765f0e2187e8bd49596dfc23be9f961100ab1af14695` |
| `klines/1d/ETHUSDT-1d-2023-10.zip` | `bbc7261b0100b34f6d0ceb8cbe8938b46ea35cafad5270168e97565283e1e77d` |
| `klines/1d/ETHUSDT-1d-2023-11.zip` | `ee9dfe21148fa778f8144bec8633109ef597e70c3ff304318eef3a575845d0fc` |
| `klines/1d/ETHUSDT-1d-2023-12.zip` | `3b6125b2a9ca673ab1f121112bd3951726c496287d52320d19ae6ad153f2ec11` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-01.zip` | `973749bfe6e4154fbfceea8580af5c97f528b548ae72f08f37740a789b43abdc` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-02.zip` | `3eb2380123e908c6faed02915d554aa462ea93fcabe34487967cd166fef4ed5c` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-03.zip` | `2eca68d9de71c7211ce693fb0518f50edebd867cd50c3a5e8b8decb696f4aff2` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-04.zip` | `de51d097af40ed164babf630412ead67e26a664ed9feb768b08415ba33052866` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-05.zip` | `caca3a4df79b27c7764908ea5d777763c4f12d2f71eaa85b07e9b390c9678c9a` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-06.zip` | `f6fd4d6ed4746369af2ca95eeb16c46d4580c64798f9d1276f60b01a2a1c88e5` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-07.zip` | `54afe4e5d7c824b43a82e5b7655dff15a2dc4e01d5257c273491c48de11f87a6` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-08.zip` | `308f163537048f9b7fb7a8efa09a8ef01c09e9e854fea878ee8b04073bca26b8` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-09.zip` | `79d61a0988649ec0eca0e7c17eea83c93b4e4ce659ac8e06a25d6ee24e446b94` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-10.zip` | `97b4a965cc3e35a068dbcde17e1ac9aa996bf37dd72d48e3f318c27f8c95c879` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-11.zip` | `07ffbad0dcab21a652e85cada0d01b27af59ea698d6bc8132679762acfd674df` |
| `markPriceKlines/15m/ETHUSDT-15m-2020-12.zip` | `7ab4f73171defa6488e7de67413d0e045027d3c03e7cf95ea2789ec168339369` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-01.zip` | `148d08b33404e1ed0f8480884f74beadbb5ef961b39fd233d28e06189bb80031` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-02.zip` | `d571bfb5a165a44769ff98af922e74ec2e84f3846d76503e2d75b523cdffd39e` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-03.zip` | `c3a48417f7b47a3272c3526c7e99a27a7695ea58d8663f1ed972c323edfa8993` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-04.zip` | `a3b8a82296defe753d68e385c1aa5f5e6c19adea485f6481b98adb8e57429a39` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-05.zip` | `3d93614773caf6ecf6590081b371074706dc608b6bb7f1b4c06203dcbd0fd99f` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-06.zip` | `7f354813c0504e6c8747ad77a02be9fe3093faa293b7cd1dc6d9977211009529` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-07.zip` | `cbd1371f86cd854d21cf6ae3dfeaff2f0c19a7ebb6bd26548fa7f246a06fd7af` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-08.zip` | `2960da28e985a4626248b75636c50c0ae32cb08d6a014801d6b18826c6e9aaf7` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-09.zip` | `66e2b5b2a897c5c2549fc8c40cb6840fb7c294b5053f994b454d3459096aafaa` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-10.zip` | `e5ee5378cd29a3382fd0185b773ca02ccc8e08eb79842548651d4170c0766db7` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-11.zip` | `b07f44992826b5f12a8fe58d3db139fab060f3174672cf950d08e664c8ce4395` |
| `markPriceKlines/15m/ETHUSDT-15m-2021-12.zip` | `5dd2c75b8710c1f5376f3bceae3a746949078f35d215ab22c68a5c339119a8a4` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-01.zip` | `5a84ec85e452106f20be0e683f6897d19157c792899248ecab180bc226ce221a` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-02.zip` | `7d93158a3b3f84809f96d4a7ee515e2cc78a2999c6b3f0006e0e5e980de96f3a` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-03.zip` | `798bbc9e7c7417ca6c0b405b24b19606cef7de94ddcf1658f33d5eb151eab821` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-04.zip` | `cb18d501cc74db55fa5f44b06d7c9cace9fe067d7646a7340bf4b09d96a09704` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-05.zip` | `0827eb9f9290d1da0f7979af251d29f57fef6b6f7829bacc3fb77b0de7c98825` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-06.zip` | `6c8f3b8491a082e47849d54b7951aa32b70eebcbbbc43500eb038ae72ea2aa58` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-07.zip` | `c8b13295c978120840231aabec0089fc8e127845232222611a48d65fab2a575b` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-08.zip` | `01192574b8a110b9f92b8ff455aed6955f85f05a57cabfbb5902d979056e41e6` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-09.zip` | `894d405aa5893aefb571638103216e689efb3554dc15de3cfc57f700650fce0a` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-10.zip` | `f3825895cfb98ea05a2c03d4c2ec0237a64bf4dde55f871dba0106b078e480e8` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-11.zip` | `4b4e20ce9d81beea8e76da626951d93abf081a0782cf37c2ad02a53d1a4ae856` |
| `markPriceKlines/15m/ETHUSDT-15m-2022-12.zip` | `f93888f23346b09883826e7a9d38fa84c9efb0d97e9be493909f974efd706651` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-01.zip` | `0974619d42073a6b1a72cb74f055132e07927f8702a3586ed8e0d767e427fe00` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-02.zip` | `e9e70c79491a3d39e9edea3fb66203290b0ce28e81c4d46adb8e5e14e8e94344` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-03.zip` | `41df508614d71c57c118a12730a3d6460c7ed719c59c18c10828535d039e82ad` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-04.zip` | `baf2585fd095431b66dd76136f076b6211ddca4dbe8ec26ffc8a7b5e6a61ee53` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-05.zip` | `0d28092a6daaa00faa14d7b8ceff28defb990599c748b792c742a911be5f2079` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-06.zip` | `05fff86356cc984c2db1606409088e8d80038d03fcc82508d4d1d01fd798263e` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-07.zip` | `4a911c68f70a41c783bf8973b1fdb3ae458d3d437da63a5e5928c2dd06e4e690` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-08.zip` | `96743ff0dd53ac6cefbead2937bc08d41bc4b0ce0b05d4bb1823d4aaa1bd4e8c` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-09.zip` | `5a52d9ffa24e78eb962edd54b0ed2e41b0418ac4c64a9d3770f791b25c815efd` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-10.zip` | `975477f1ca4325bdd481dc7520bf568323fadf9d930028ac2cc63b43137c6630` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-11.zip` | `47b33624fce1af21f61634dbd94cb41205af1b3462ec2f42088fbd5993509004` |
| `markPriceKlines/15m/ETHUSDT-15m-2023-12.zip` | `3d90278357edb4a23f172633fe17d55aa221ba8c5652064e997d99b1f07e1a85` |
