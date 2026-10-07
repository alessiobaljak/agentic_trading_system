# Fase 0 — I dati di SOLUSDT

Scritto il 2026-10-07 nella sessione di campagna. Fonte: file mensili pubblici di
data.binance.vision (futures USDS-M), scaricati con `research/src/dati.py` solo fino al
2023-12-31, con il checksum SHA-256 pubblicato da Binance verificato su ogni file
(nessun CHECKSUM mancante). Nessun metadato attuale della moneta è stato cercato.

## 1. Periodi

| Periodo | Da | A | Giorni | Nota |
|---|---|---|---|---|
| In-sample (dalla scheda) | 2020-09-14 | 2023-12-31 | 1.204 | la prima candela nei file è del 2020-09-14 00:00 UTC |
| Costruzione (70%) | 2020-09-14 | 2023-01-04 | 843 | calcolato e scritto nel log (SOLUSDT-001) PRIMA di caricare i prezzi |
| Validazione (30%) | 2023-01-05 | 2023-12-31 | 361 | |
| **Periodo utile per i test** | **2021-01-01** | 2023-12-31 | 1.095 | il 2020 è escluso per liquidità (sezione 5): costruzione effettiva 2021-01-01 → 2023-01-04 (734 giorni), validazione invariata |

La data di divisione (2023-01-04) non si sposta: è stata fissata prima di vedere i dati e
la regola del protocollo non prevede di ricalcolarla. L'esclusione del 2020 porta il
rapporto effettivo a circa 67/33 invece di 70/30: lo si dichiara, non lo si corregge.
Storia utile: 3 anni, sopra `storia_minima_anni` (2): la campagna si fa.

## 2. File scaricati

Candele last price (klines) e mark price (markPriceKlines) su tutti i nove timeframe
ammessi (15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d), più il funding storico: 40 mesi
ciascuno, da 2020-09 a 2023-12, nessun mese assente. In tutto 760 file (la serie per gli
stop è il last price, cioè le stesse candele dei segnali). Come riferimento di mercato
sono scaricate anche le candele last di BTCUSDT a 1h e 1d (80 file, stessi mesi): non
fanno parte delle impronte di questa moneta.

Coerenza interna: le candele 1h, 4h e 1d costruite aggregando le 15m coincidono con
quelle native (0 differenze su open/high/low/close in 28.769, 7.192 e 1.198 candele).

## 3. Buchi nei dati (osservati)

Nessuna sospensione di contratto e nessun cambio di contratto o ridenominazione: il
simbolo è `SOLUSDT` per tutto il periodo, nessuna cucitura.

Buchi nelle candele **last price**, uguali su tutti i timeframe (giorni interi mancanti
nei file dell'archivio):

| Da (UTC) | A (UTC) | Durata |
|---|---|---|
| 2022-02-26 00:00 | 2022-03-01 00:00 | 3 giorni |
| 2022-04-01 00:00 | 2022-04-03 00:00 | 2 giorni |

Buchi nelle candele **mark price**, in date diverse:

| Da (UTC) | A (UTC) | Durata |
|---|---|---|
| 2021-07-01 00:00 | 2021-07-02 00:00 | 1 giorno |
| 2021-07-24 00:00 | 2021-07-28 00:00 | 4 giorni |
| 2022-10-02 00:00 | 2022-10-03 00:00 | 1 giorno |
| 2023-02-24 00:00 | 2023-02-25 00:00 | 1 giorno |
| 2023-11-10 03:45 | 2023-11-10 04:00 | 1 candela da 15 minuti (solo nel file 15m) |

Il funding non ha buchi in nessuna di queste date e la moneta non era sospesa: sono
giorni mancanti nei file dell'archivio, non del mercato. Trattamento: il motore vuole le
tre serie allineate barra per barra, quindi per ogni timeframe si usano solo le barre
presenti sia nel last sia nel mark (il caricatore della campagna fa l'intersezione e
dichiara quante barre toglie: a 1h sono 168 + 140 = 308 su 28.769). I buchi restano buchi:
il motore li conta (`n_buchi_dati`) e non si inventano barre. Un settlement di funding
caduto in un buco con posizione aperta si addebita sull'ultimo mark disponibile, come
previsto dal motore.

## 4. Funding (osservato)

3.688 settlement dal 2020-09-13 16:00 UTC al 2023-12-31 16:00 UTC, senza buchi
(nessuna distanza oltre 8 ore). Intervallo:

| Da (UTC) | Intervallo |
|---|---|
| inizio | 8 ore (00:00, 08:00, 16:00) |
| 2022-11-09 20:00 | 4 ore |
| 2022-11-10 04:00 | 2 ore |
| 2022-11-18 16:00 | di nuovo 8 ore, fino alla fine |

Nella parentesi 9–18 novembre 2022 il tasso ha toccato il minimo di −2% per settlement
(il tetto di Binance) per 7 settlement di fila, cioè uno short pagava circa il 2% del
nozionale ogni 2–4 ore. Il motore usa il tasso e l'intervallo veri di ogni settlement.

| Anno | Settlement | Media per settlement | Minimo | Massimo | Quota positivi |
|---|---|---|---|---|---|
| 2020 (da set.) | 328 | −0,0114% | −0,419% | +0,130% | 75% |
| 2021 | 1.095 | +0,0261% | −0,750% | +0,333% | 95% |
| 2022 | 1.170 | −0,0325% | −2,000% | +0,010% | 54% |
| 2023 | 1.095 | +0,0012% | −0,927% | +0,086% | 72% |

Lettura: nel 2021 il funding è stato quasi sempre positivo (costo per i long, incasso
per gli short, in media circa +0,08% al giorno); nel 2022 la media è negativa per via
di novembre; nel 2023 è vicina a zero.

## 5. Volume e liquidità (osservato)

Volume medio giornaliero in USDT (colonna `quote_volume` dei file 1d):

| Anno | Giorni | Media | Mediana | Minimo | Giorni sotto 20 M |
|---|---|---|---|---|---|
| 2020 (da set.) | 109 | 16,3 M | 14,0 M | 7,8 M | 89 |
| 2021 | 365 | 1.075 M | 450 M | 29,0 M | 0 |
| 2022 | 360 | 982 M | 860 M | 63,1 M | 0 |
| 2023 | 365 | 1.104 M | 710 M | 134 M | 0 |

Il volume medio del 2023 (1.104 M) conferma la fascia di slippage della scheda: sopra 1
miliardo, 0,01% per lato.

**Periodo sotto `liquidita_minima_usdt_giorno`:** dal 2020-09-14 al 2020-12-31. Tre dei
quattro mesi del 2020 hanno media mensile sotto 20 M (settembre 16,5 M, ottobre 12,5 M,
dicembre 14,8 M) e novembre (21,8 M) ha comunque giorni sotto soglia. **Regola, scritta
qui prima di qualunque test:** i test usano solo dal 2021-01-01 in poi; dal 2021 nessun
giorno è sotto soglia. Il mese più sottile dopo il 2020 è gennaio 2021 (70 M, fascia
0,05%); i test non cambiano la fascia nel tempo, usano quella della scheda per tutto il
periodo, e la prova a costi doppi copre la differenza.

## 6. Ambiente di prezzo (osservato, per dichiarare le baseline)

| Anno | Apertura | Chiusura | Minimo | Massimo |
|---|---|---|---|---|
| 2020 (da set.) | 3,20 | 1,50 | 1,07 | 4,91 |
| 2021 | 1,50 | 169,98 | 1,49 | 260,06 |
| 2022 | 170,01 | 9,97 | 7,78 | 179,65 |
| 2023 | 9,97 | 101,78 | 9,68 | 126,94 |

Tre anni con tre regimi opposti: il 2021 moltiplica per oltre 100, il 2022 divide per 17,
il 2023 moltiplica per 10. Le baseline buy and hold e il suo opposto saranno estreme e di
segno diverso anno per anno: ogni risultato va letto per anno, mai sul totale.

## 7. Impronte SHA-256 dei file (la verità della campagna)

760 file in `data/insample/SOLUSDT/`, registrate con `dati.registra_impronte`. A ogni
sessione si riscaricano e si confrontano con questa tabella: una differenza è uno STOP.

| File | SHA-256 |
|---|---|
| `fundingRate/SOLUSDT-fundingRate-2020-09.zip` | `14fcf2b6183131263ea740f60641948076853ab273b030463934f6a81e01797b` |
| `fundingRate/SOLUSDT-fundingRate-2020-10.zip` | `a7712335a1ad285ef1a2a4a25309fb44c5562819f666ffd60e16b2112ca5ee2a` |
| `fundingRate/SOLUSDT-fundingRate-2020-11.zip` | `f359a0f2355b4c9d4523ac28d4b006e5ff3c1c192baeba471bbaa3cb8928db40` |
| `fundingRate/SOLUSDT-fundingRate-2020-12.zip` | `925301315c1928ded7c81a816c82a8b01c52712fcd4fd842ff68199950856b17` |
| `fundingRate/SOLUSDT-fundingRate-2021-01.zip` | `69ceaed5037e3560bd6f31651ba0214de913af8f0c4c25712c95cbbe1308cb97` |
| `fundingRate/SOLUSDT-fundingRate-2021-02.zip` | `88363d90b2bb922736556118610a8b1ddadc679b474950b69b07eb3ca9eb0253` |
| `fundingRate/SOLUSDT-fundingRate-2021-03.zip` | `256b24b3655ef98daa5080a509c0674fc11e7c83774869b0ae2a794cbbf2a05a` |
| `fundingRate/SOLUSDT-fundingRate-2021-04.zip` | `3a7fa828be00e3e352cef39ca5856c0d86077724f8d1ce576be79f302c21dd71` |
| `fundingRate/SOLUSDT-fundingRate-2021-05.zip` | `f9a657f15d4753cb73bf8ffd0d62405d480044162c19e1f7437608e2c1bb6694` |
| `fundingRate/SOLUSDT-fundingRate-2021-06.zip` | `5d97dc076126d6df30eb68185be0613a08391b18d6046da006c790b3674b0d40` |
| `fundingRate/SOLUSDT-fundingRate-2021-07.zip` | `d5cc6efda2474a0ea47626b8ec17b40f8b2cc21aa1338e55796f402c9173e125` |
| `fundingRate/SOLUSDT-fundingRate-2021-08.zip` | `36028dd0bcfa30c6be842f0ee066ffa1ae3d93082cf4aafd302d1c0a3a386ecd` |
| `fundingRate/SOLUSDT-fundingRate-2021-09.zip` | `2b1bbc144fed66818841e7af5f5e310adf8e2cb3b1d7643e0c1b2bb30bf421e8` |
| `fundingRate/SOLUSDT-fundingRate-2021-10.zip` | `0ac3fe161fe23ac8479a4a6e5fbfc38e91ae1515663d93a3fe767c351ee81187` |
| `fundingRate/SOLUSDT-fundingRate-2021-11.zip` | `16996f42bf6d48a5569bfecd8af6027de2298b30dca1d95381c595893de8e2e8` |
| `fundingRate/SOLUSDT-fundingRate-2021-12.zip` | `0ea2c59cde9362715dea398bd66d3325d5bdb40c39db0370977bcad0b0f67533` |
| `fundingRate/SOLUSDT-fundingRate-2022-01.zip` | `f3be14b01356f33f6cbde6d12ee30311ae91fc521dc78d72a0aa39db8c295053` |
| `fundingRate/SOLUSDT-fundingRate-2022-02.zip` | `d622a4a5cfb461e81d9cb13ebdd34b02e2d221c2ddb8d708dc4047d2f499fa96` |
| `fundingRate/SOLUSDT-fundingRate-2022-03.zip` | `10d3d16d74340850c2148553261dfdad7ffeb0b705f014c869fa807a1e7ddc84` |
| `fundingRate/SOLUSDT-fundingRate-2022-04.zip` | `f07052472753f04eb8e7fb818cf60e90e187e712f63a577741ca7ae59c63bc9e` |
| `fundingRate/SOLUSDT-fundingRate-2022-05.zip` | `ed42b50666e40e1489f01730f85e5efe919b9a94344e043369a459c66492a940` |
| `fundingRate/SOLUSDT-fundingRate-2022-06.zip` | `78249fec5212753b19ce01c2fb23ffdc3deecd29bd3ab61fb7cf70ba6c395edc` |
| `fundingRate/SOLUSDT-fundingRate-2022-07.zip` | `ce4c96d62e020d4b3c53bc31c248e5800a4a6eb3a6809c36509238122aa02a3a` |
| `fundingRate/SOLUSDT-fundingRate-2022-08.zip` | `1604d1993d0c6a7e37e2ff81a6944d7b5c0e81475e3fe475bdbdf0deaff4d847` |
| `fundingRate/SOLUSDT-fundingRate-2022-09.zip` | `673b50b2daec4a34da7d8a8095995ddbafa6f66bf8c2d499ba48f8050cf68565` |
| `fundingRate/SOLUSDT-fundingRate-2022-10.zip` | `d0436ed57e674ae3c00eeff3aa46f6e65c596892b80e5b6e8183d487c6ef3168` |
| `fundingRate/SOLUSDT-fundingRate-2022-11.zip` | `73fbada102584d8e19cb9594f04471f589ff37404b0cf64c0bd7cb4ac4d4a157` |
| `fundingRate/SOLUSDT-fundingRate-2022-12.zip` | `b9b8d803d985679959d21a55d08b14db331cf961442f8446eb18d723ea154567` |
| `fundingRate/SOLUSDT-fundingRate-2023-01.zip` | `12a401fc459341834a0d3c2f207d55e7aced058b62838f296028885ee2e52612` |
| `fundingRate/SOLUSDT-fundingRate-2023-02.zip` | `1173c36ad296e152ed9f954ce49fd65b7ffd8a03f270906a1e816fdbb7929f57` |
| `fundingRate/SOLUSDT-fundingRate-2023-03.zip` | `6a950dfbe4e75ce7e28a174d1432fed82fe08964053c618bec2be70f83ae6b61` |
| `fundingRate/SOLUSDT-fundingRate-2023-04.zip` | `88d1b03da4cd68774d846d5a9b7a9ba3d165a7b03855cad84a181820a2f7b297` |
| `fundingRate/SOLUSDT-fundingRate-2023-05.zip` | `b644431236540c0fa4573e96b9357077755d53440427fb2419e68272ea653137` |
| `fundingRate/SOLUSDT-fundingRate-2023-06.zip` | `63de6ffcbab1fec0b83807efde188fdafb06d4ed0f947c4df86d757f894d88c9` |
| `fundingRate/SOLUSDT-fundingRate-2023-07.zip` | `7323f1cf79a8dfeb78dd7bd8cd2940a7db00ee023739430435b1cc25cecadcae` |
| `fundingRate/SOLUSDT-fundingRate-2023-08.zip` | `87ce0395cf9d1fa9ea4849b4811d366c1867d4159f3c1a2b4a3e0656972be2a0` |
| `fundingRate/SOLUSDT-fundingRate-2023-09.zip` | `7a8c1135aa165e9399a274acf1f330bbf6bae594266582fc1cfc91b950f73e75` |
| `fundingRate/SOLUSDT-fundingRate-2023-10.zip` | `a56852237de6b69483565853858901ce7e4c611d3950d485a064bf90069958ba` |
| `fundingRate/SOLUSDT-fundingRate-2023-11.zip` | `1cbd9c6b802cdf035ba408c03e82aab678c2a994c2c6860386a4226ba104e252` |
| `fundingRate/SOLUSDT-fundingRate-2023-12.zip` | `debe51eb20a3b7d6093baec3b609e7a9f746c64635cfa77aa761e88e84454902` |
| `klines/12h/SOLUSDT-12h-2020-09.zip` | `dd780f6e98ff0ba2430aa844db4e7e67f820ea3f871241f2e29bb77e8fc8f59d` |
| `klines/12h/SOLUSDT-12h-2020-10.zip` | `c5eea0a9dc6e8ce8875c353c316e071602440fe54aceb56fc656e4660ee0c4de` |
| `klines/12h/SOLUSDT-12h-2020-11.zip` | `dc5050ce34db9769cfb22381632d4f3805eb1cf86c084ff992019e7d8aae00dd` |
| `klines/12h/SOLUSDT-12h-2020-12.zip` | `8b941aea6289f683571033995502b77893e0471aeae0c572c2e3afc12b9a3415` |
| `klines/12h/SOLUSDT-12h-2021-01.zip` | `b726a47a0a2ea0a4165525b8f1ae5e507d9cb1225c093c700b5fe9c46cc3f5d4` |
| `klines/12h/SOLUSDT-12h-2021-02.zip` | `b90561a57c0e5c8a7b1e847a1e46a0e14aa5412fff9cf33888b93a056c4ac6c7` |
| `klines/12h/SOLUSDT-12h-2021-03.zip` | `c2ea613437bde19e32ae08c6abe53319fa9017a85a2c225460813ceeda04ba4f` |
| `klines/12h/SOLUSDT-12h-2021-04.zip` | `f0c27a822cee7fcaa593875eaea6ea8646759bcefda7d9731fdc8c864cfd5f66` |
| `klines/12h/SOLUSDT-12h-2021-05.zip` | `ff936162fb9fe1bee8ed473e88c945040a9128b978b3d99bcafc105d8a1f525c` |
| `klines/12h/SOLUSDT-12h-2021-06.zip` | `b66d0de01f74976f3becde80c67eeedea1a54bc8d1dc79e2861c418ab9edd3bf` |
| `klines/12h/SOLUSDT-12h-2021-07.zip` | `1cba415c6f4c635e687b80217bd18b3b57c0f0e1b2b23a35fd349e9655d4bfb3` |
| `klines/12h/SOLUSDT-12h-2021-08.zip` | `808a9f415c2014859f7408745bfec7d6171de9ad94a1b1292673d201272ab45c` |
| `klines/12h/SOLUSDT-12h-2021-09.zip` | `f8a42314f70bc1175d34af658755e3cb0fb3181b9567790b0f081a93a1fe27ee` |
| `klines/12h/SOLUSDT-12h-2021-10.zip` | `a70b079e12ba2c83040e7bf98afdcce908b5b0eb452f9b591bbf656bc146f5ec` |
| `klines/12h/SOLUSDT-12h-2021-11.zip` | `35cf8f57d209b658a703e2f23b0cdf4e8c3bee347b4de30041418cabe1039048` |
| `klines/12h/SOLUSDT-12h-2021-12.zip` | `5be717b5cde1ca397de8fe062cd49c19630b0f44e63fac36a72d061a22201cfd` |
| `klines/12h/SOLUSDT-12h-2022-01.zip` | `c2498a1863118618f725caa6658b168349b68e029da0937fbc7909133ec2eb14` |
| `klines/12h/SOLUSDT-12h-2022-02.zip` | `3f838e842ed721e4e7cf98c8657e8d59d3aed1d8bc01dff681669ff89d7db138` |
| `klines/12h/SOLUSDT-12h-2022-03.zip` | `20dd0951397d3ba82efb59d45497e83488d1a1c87e81ffcb627f8c70e4b4d8c0` |
| `klines/12h/SOLUSDT-12h-2022-04.zip` | `1a1d965f4284ae16a362a9baed205df6b4a14061e328e499c9dc290bd9f62556` |
| `klines/12h/SOLUSDT-12h-2022-05.zip` | `e5a4a4c8b48dc2f7ef52e1fc6915f572878a9858a62a525a1da4ec06d1aa3577` |
| `klines/12h/SOLUSDT-12h-2022-06.zip` | `e5543665084118d8f4848f6d8788f67e4f7c21289fdcf6cf5600fa0a0f3a3745` |
| `klines/12h/SOLUSDT-12h-2022-07.zip` | `33e07338e2207bfd63b758d2e61a9f4c032219191a476e3aecca831457334466` |
| `klines/12h/SOLUSDT-12h-2022-08.zip` | `9cc8a18f67b0e7a29ad088e320df1d02802f4c5c2a531aa48419c68341bbcb03` |
| `klines/12h/SOLUSDT-12h-2022-09.zip` | `a717911f7e00d7425523cb0118f7cb1e4f2479cf883f59e46458a681ca26fca9` |
| `klines/12h/SOLUSDT-12h-2022-10.zip` | `496357a2af23b055786282997a0cbde70f78d9842761e72cb3756803f32a3aa9` |
| `klines/12h/SOLUSDT-12h-2022-11.zip` | `8b266b958e3b1f21163f278630ff7fc7d250184167161e1f0f52acb059c559fd` |
| `klines/12h/SOLUSDT-12h-2022-12.zip` | `d29cdbe0dfb8b773e4f78e3631b26bc9d67e48d5a079a5bf96fdc2dfe179dc98` |
| `klines/12h/SOLUSDT-12h-2023-01.zip` | `270b890ba978e3e969bceb513e412cd51f5fc1ef9acdf512c934d13a606e3376` |
| `klines/12h/SOLUSDT-12h-2023-02.zip` | `7bc0975833d1f08243104b0e8dade773c7a16302042bda6dedba85e1f8c7bacc` |
| `klines/12h/SOLUSDT-12h-2023-03.zip` | `b372a6435ce6e7df804d228e4f9336d59b2d615b7a04f27dcf366cc2797f6cdb` |
| `klines/12h/SOLUSDT-12h-2023-04.zip` | `aed0cb2bf46bb00339f88022d37cb2ab7025345eb2e99e6af3902858be293a74` |
| `klines/12h/SOLUSDT-12h-2023-05.zip` | `4f7547fec9b61bb9bbb3449cae7f6f8e364827dd9c316f8687b36b5c7bdcd54a` |
| `klines/12h/SOLUSDT-12h-2023-06.zip` | `af96152885549df002e81c44f8c912f6895dd2fce5114cebb8451fc729ed01b9` |
| `klines/12h/SOLUSDT-12h-2023-07.zip` | `9bc60cf35f06adcc1a810cfd2cf691d4fb557aff88546047ed49c8a5a90ca6c5` |
| `klines/12h/SOLUSDT-12h-2023-08.zip` | `c9414b1bf27bdacf3b8cfba84b49c523c9d2bcce7d61b16ce38d87003108f74b` |
| `klines/12h/SOLUSDT-12h-2023-09.zip` | `c1a7a91da3b2bf70eaac012ac4ea6f6fbbe50d9a70858182ea9eef7ff479640e` |
| `klines/12h/SOLUSDT-12h-2023-10.zip` | `a22f82589849c88cd52b9a009c09cf3092fa2fbbe4b5e8a09ea3ac1355defacc` |
| `klines/12h/SOLUSDT-12h-2023-11.zip` | `85113a1c381f5b8afb3f169026751238aa6968eff132a7891df958629e94339c` |
| `klines/12h/SOLUSDT-12h-2023-12.zip` | `20599c0d446b93c45003021a88a858539bbcf48a1d4b8e86f308c0d93d752067` |
| `klines/15m/SOLUSDT-15m-2020-09.zip` | `d2604ec2627cae4e8f7016031b4b7b9077e8c3fcc1846af2b6985e75ce0902dd` |
| `klines/15m/SOLUSDT-15m-2020-10.zip` | `f30d33a0a7d7a5ab4834a071593567906ba3eef86bf6b4f431a7de8ba6621349` |
| `klines/15m/SOLUSDT-15m-2020-11.zip` | `68375b21496770c02eacdedb4645d222f707c37a3b38a47faa86fdc6c04ce784` |
| `klines/15m/SOLUSDT-15m-2020-12.zip` | `2c0ad294ff78c1fbf6b111841afda0ea9d8cdd33d5af6b4d70f327db516f750b` |
| `klines/15m/SOLUSDT-15m-2021-01.zip` | `3c1bf44d6135fe8de4b0dcd6dc6dfd1ff1840dde00c8e40e7a1b3cd73c06b6c4` |
| `klines/15m/SOLUSDT-15m-2021-02.zip` | `938508ed7d0ff4033904ed3aa5707289ac8de5754db08b52832545c95fc797d1` |
| `klines/15m/SOLUSDT-15m-2021-03.zip` | `f075e5f39e1889fe8afb1c4138fed6698db86c454498c606851bdc59dc18a85d` |
| `klines/15m/SOLUSDT-15m-2021-04.zip` | `1055bbe7caea4849399c0a4c6bba1800daa3c2c610ff32258c12009480f80b80` |
| `klines/15m/SOLUSDT-15m-2021-05.zip` | `05c66e4aec64efa0d53890de2774c0ae8474565e38bd12a9f0faa59e43d9d62a` |
| `klines/15m/SOLUSDT-15m-2021-06.zip` | `4be111b3c9f5394bd66ef698cb358f24787267f7f10a55530d47e2a5e8ac9808` |
| `klines/15m/SOLUSDT-15m-2021-07.zip` | `e5ef0d1a6b42383faa577fb0fdbbe3bb9f84a357923daf21158469e0dcb8ac85` |
| `klines/15m/SOLUSDT-15m-2021-08.zip` | `db4820123b7d4aef29ea4051b32dd4c4b6ba47468504afee2c5a4af0de51b396` |
| `klines/15m/SOLUSDT-15m-2021-09.zip` | `3d5a2bc5c22531ae5189d3f046cb9688ad22dd6ec9a71a66476222e4e60f3567` |
| `klines/15m/SOLUSDT-15m-2021-10.zip` | `98d0479ef53c3d6ecb1e0c5f64133b1c9dd1f80c1ea3774419966e67b4a32fb3` |
| `klines/15m/SOLUSDT-15m-2021-11.zip` | `e0acf781c3cc131e9cddb1652dfd5920bbc5364d0894165b256c7982ee4d2432` |
| `klines/15m/SOLUSDT-15m-2021-12.zip` | `8efe0dc4b8152ab7f3dd3e667eda4ec6f7739639b3ae35c88fc861e765fdff0e` |
| `klines/15m/SOLUSDT-15m-2022-01.zip` | `660261bde927dd371bb08ac24f0b666b9982ab165c781488652715e3f0b5bbc1` |
| `klines/15m/SOLUSDT-15m-2022-02.zip` | `fac5a884ae3cb71e9a04c298c0734c962d51c150d8cabec22c6e396093077759` |
| `klines/15m/SOLUSDT-15m-2022-03.zip` | `6ffb9bb3e8d6330749d1ba13931eac2d689f427bdabe477d2000f5d84e2f0610` |
| `klines/15m/SOLUSDT-15m-2022-04.zip` | `fcc0dfbbdb5391007ad9155a56ee92bd415d2958d0216ec25209e9ddf66d6030` |
| `klines/15m/SOLUSDT-15m-2022-05.zip` | `1609383c40657c6b53fed908e300cfb402677fb9c5960e92a40af0b4c2603f7d` |
| `klines/15m/SOLUSDT-15m-2022-06.zip` | `4e9df1cba8e3a5a497454c42b50a6ab83f7a98988edcee335be01feb3f94c3e7` |
| `klines/15m/SOLUSDT-15m-2022-07.zip` | `8da00cc69f43d60e32669d8275e23f7cabeeb6bda47f0225fa092ef21fe0e9c8` |
| `klines/15m/SOLUSDT-15m-2022-08.zip` | `4a0340d12ec92bc21957e83a52df97e10bf74f3a8b125e017dff18a45364446c` |
| `klines/15m/SOLUSDT-15m-2022-09.zip` | `33cd2afdb10152a5a55809fbbc131067b358feddbdfb9a65ab709b39e8fa0daf` |
| `klines/15m/SOLUSDT-15m-2022-10.zip` | `24132af49dd06a5c169fb975ed524f693cc64cb71d79fb88261ef3abfe9b20a2` |
| `klines/15m/SOLUSDT-15m-2022-11.zip` | `23525dc1ac2fc5914e60a329b2ab89789d4d2f84624c04c449dc85c3b7d7ed05` |
| `klines/15m/SOLUSDT-15m-2022-12.zip` | `53f2c92d1b4ac1a57414f71e5d531767abdc6bc9bee2a5bb564be31281bc3d3b` |
| `klines/15m/SOLUSDT-15m-2023-01.zip` | `c4d60c90a36a3648396985c7ec4cfb866abe5c1f684679d2824c40b893c39245` |
| `klines/15m/SOLUSDT-15m-2023-02.zip` | `de258fcf7798066d19e5bbab2b8faa9d6bef1b894f88d373e5de40f213b7db8c` |
| `klines/15m/SOLUSDT-15m-2023-03.zip` | `862bf0706b86e22e3858b571642ac8c8e0b045948d08f623f6b2b8f4b4fc1335` |
| `klines/15m/SOLUSDT-15m-2023-04.zip` | `e35934cdd903c2c686175719fa78991de2bd8e5649111ce75a923409c8de5583` |
| `klines/15m/SOLUSDT-15m-2023-05.zip` | `0538d1a3e9c7c38254874bd4f974e392fa0e369f41614fe7fefb05f240b26e7e` |
| `klines/15m/SOLUSDT-15m-2023-06.zip` | `f0ea4a081b6648c2495cebc705081dee20ceebb217e18fe3b6dae3a2b2a308c1` |
| `klines/15m/SOLUSDT-15m-2023-07.zip` | `5d2551f132f081192614548766b6d0d3567bc5090769669a870cf3aa4fb16e90` |
| `klines/15m/SOLUSDT-15m-2023-08.zip` | `d66b0de833d742925f40ae4bc422890ff61d45da6a29581623c84c6601acc20c` |
| `klines/15m/SOLUSDT-15m-2023-09.zip` | `c77b930acf0e251fc09681e4fbd3fbddd9905052feb885b4479df4ad1be47ee7` |
| `klines/15m/SOLUSDT-15m-2023-10.zip` | `04b46012450cd337fd3dab6074e777673550340985d68e56ac488244f534d0fb` |
| `klines/15m/SOLUSDT-15m-2023-11.zip` | `35540a230761ad740fdfaca15e691f19c9f256d0c1b207bbe869e3e4add6a8e9` |
| `klines/15m/SOLUSDT-15m-2023-12.zip` | `974345ee6c620457780c7484093c8c6cfbd4719dd4adbd865d8f15e42d075977` |
| `klines/1d/SOLUSDT-1d-2020-09.zip` | `6861639415400dcd4f092ead7cfd52dc28c29dc2211a0d0320e9620c2a7f3b5e` |
| `klines/1d/SOLUSDT-1d-2020-10.zip` | `906008ffddc290b36df435b260e1e3719d37ff48881f39cfd0886907173d7d55` |
| `klines/1d/SOLUSDT-1d-2020-11.zip` | `da84f9524a5975ffbd14fd8dfe1dd2cbd8b41ef225dace30c8622a90d041472f` |
| `klines/1d/SOLUSDT-1d-2020-12.zip` | `2f065d3c0bedaec97394e9a86b63d676e03d574bd03ef10f6df4c09d31020e09` |
| `klines/1d/SOLUSDT-1d-2021-01.zip` | `6a2e5e1de776ddc49f65aba7bf7b4e9be797efb9fc80597b3c7312d922d3a6d2` |
| `klines/1d/SOLUSDT-1d-2021-02.zip` | `b91615ed64e9eed76f500d2aad01f9bc5ae13b637ab4d49c0ed345638368d9ea` |
| `klines/1d/SOLUSDT-1d-2021-03.zip` | `423cb46d4df1785c3dbec5687be2304c0e81f0bb678d5e68d7b5100fe3e84937` |
| `klines/1d/SOLUSDT-1d-2021-04.zip` | `f4bc5eafa7a8a39f9538f5aca6010bc69f6db843280042c4c69ffcdd5869ef22` |
| `klines/1d/SOLUSDT-1d-2021-05.zip` | `88e2c1f54b71cee950cab1ba7a1613640717152e2d1e9ab2575c3ca04c117116` |
| `klines/1d/SOLUSDT-1d-2021-06.zip` | `2ffcec73e63dc090ed0c760a5362e46439caf0aeec72b10be6774e2d5dd288c5` |
| `klines/1d/SOLUSDT-1d-2021-07.zip` | `7e63ae66eafec9eea56b1f18aa55fb4cc3be51042c0737c1c534269e23a582ab` |
| `klines/1d/SOLUSDT-1d-2021-08.zip` | `31c7fb7fa0c41fee9d90b3020df40bfeb66e1838b80e75b7c523b157e9f9c937` |
| `klines/1d/SOLUSDT-1d-2021-09.zip` | `ae275ed46f010297d0fa893e159589d70a26da28ab1b0e8469127a44ead1b0cb` |
| `klines/1d/SOLUSDT-1d-2021-10.zip` | `1b340af6575c47080916008450c87709aa99e59419cbbfcb9cb177122535a6c7` |
| `klines/1d/SOLUSDT-1d-2021-11.zip` | `237f6c0d5c0d7f1a695fff66968212642d8472767d87a70b453c2ebb13592ce3` |
| `klines/1d/SOLUSDT-1d-2021-12.zip` | `f8ecb54e26be8e3fdee22e03f46f5af838b068e2fe97727cf3aae9c4cf16c635` |
| `klines/1d/SOLUSDT-1d-2022-01.zip` | `10eddb9c49c622b8b02f428f4a9fd6103f7220adb679f4613ec748119b0816a9` |
| `klines/1d/SOLUSDT-1d-2022-02.zip` | `da808ec7a636e7010b47079c4565cdc9640f9b7f4f4314b785f135a10551184b` |
| `klines/1d/SOLUSDT-1d-2022-03.zip` | `5d7541aad646061c18988b2945141b29c91955cd018e069542fcbf199ccf7605` |
| `klines/1d/SOLUSDT-1d-2022-04.zip` | `44cb227457e39eea8b025e04a6d8e9f9ff2e766a4e101bb848c7befa8251de0c` |
| `klines/1d/SOLUSDT-1d-2022-05.zip` | `c32baca074778909bda6f84db05336fce93904c331e3a5394309a587cc0c6f95` |
| `klines/1d/SOLUSDT-1d-2022-06.zip` | `1e39b5a375af9279ed17c18ac5d9005571892f1510775f1865f1a12bd8259408` |
| `klines/1d/SOLUSDT-1d-2022-07.zip` | `c8b1996b853236c0fb95b71708be47478a5b96197acf33aba3a8ad56c276fc55` |
| `klines/1d/SOLUSDT-1d-2022-08.zip` | `76a3bd2881484326be2be87df70784e8076e8fdc64b8dfa66a5c8b76ad7a409d` |
| `klines/1d/SOLUSDT-1d-2022-09.zip` | `f9e2ea178252991aaeff0ba5775b9f70ec66f1af311f4081d671b334c95b179b` |
| `klines/1d/SOLUSDT-1d-2022-10.zip` | `3ce57cd2c35103f332cc47ef81dcd957bd5a0230dc8d202cfdce06c59912979f` |
| `klines/1d/SOLUSDT-1d-2022-11.zip` | `fcf21ba1c36283f43eb863185c305ff340a613f5c6f2401c5421468ad22c9014` |
| `klines/1d/SOLUSDT-1d-2022-12.zip` | `c6a3047de97783dd1e7202ba4fc9922325681bfa29b7c031c33d43e5baf2de82` |
| `klines/1d/SOLUSDT-1d-2023-01.zip` | `10d1fe109d45c9d0b4d7e36b6b08cd5652182637a746bbac0345d145a988759b` |
| `klines/1d/SOLUSDT-1d-2023-02.zip` | `a7d003a503fb0dd1534e579fa0d8a481da37b28049dd5c839c86105dc66d0866` |
| `klines/1d/SOLUSDT-1d-2023-03.zip` | `100fbd533c7f2b391de5d8f81da11bc64b08d230c1f85406956b7205907f7589` |
| `klines/1d/SOLUSDT-1d-2023-04.zip` | `d826c0610ad0e51efd6edc0a4ee8e6bae5214c920d4f9ac89234dae667a07d06` |
| `klines/1d/SOLUSDT-1d-2023-05.zip` | `1271af8bfc473b791e580c681bc6fc55eed672873bd2d05ad98be1db5818b781` |
| `klines/1d/SOLUSDT-1d-2023-06.zip` | `bb37ab01500f7b0f29aed2b5f2176ca2853cb8f7d2c18bb153a12406eccc5989` |
| `klines/1d/SOLUSDT-1d-2023-07.zip` | `977e080f5a6e823a84b3f153fab3dae933de075e26d077c7124e9d98f61535ae` |
| `klines/1d/SOLUSDT-1d-2023-08.zip` | `925f728cd2f2b98f7536e5826e5f3298077b023bded1fceadc79663ad3e21c16` |
| `klines/1d/SOLUSDT-1d-2023-09.zip` | `92ca1592631e5cce1aa7a0c6ee0c37bebcca72cd7fd0f07151e1662f6b51f679` |
| `klines/1d/SOLUSDT-1d-2023-10.zip` | `bf8cd3ca2e13fe1310fb72814a3abfdb46f865626b60418bb454813b67299bfc` |
| `klines/1d/SOLUSDT-1d-2023-11.zip` | `5784081017ef244acf6109420504ca9b46c1050c40e485c3f5da8bea2f14afde` |
| `klines/1d/SOLUSDT-1d-2023-12.zip` | `a3fe7c78e0be0af5aecbd26a7707836a1d24d076dc5ec31bb449e3ced3872579` |
| `klines/1h/SOLUSDT-1h-2020-09.zip` | `bc926b98121dcb870999c4c8b0cdb72551bbb7ac9d6e00047bba34156fce3bb2` |
| `klines/1h/SOLUSDT-1h-2020-10.zip` | `5f6131a244d980d631388ee504922b2bb09848e42cf6e3e59c933679887f5975` |
| `klines/1h/SOLUSDT-1h-2020-11.zip` | `348047e07a306d93694a6c6cf0273a31e4b735740759e78ec9d39678e02d53a8` |
| `klines/1h/SOLUSDT-1h-2020-12.zip` | `bd5f75cc091658b0794eb80777914b3d7e8940438da77980bd659a935f6bbd5d` |
| `klines/1h/SOLUSDT-1h-2021-01.zip` | `fef310549a5baf8fcdb67a2c6c97a0ec05f25dbc87afbb2a0ba0f08842a52c27` |
| `klines/1h/SOLUSDT-1h-2021-02.zip` | `029ec118946bf80d43f27baec8a80004265134c9540e7f9a04e440e453a43f99` |
| `klines/1h/SOLUSDT-1h-2021-03.zip` | `94eaba4252ae9189c9be07ea2d40e3f016ee924a761462303882ffc9bb4e4e4c` |
| `klines/1h/SOLUSDT-1h-2021-04.zip` | `21d8b0ffa824a3d4845f4e0103f9739a9931e4788a5da3958a0c8e4552552965` |
| `klines/1h/SOLUSDT-1h-2021-05.zip` | `efb32d5fd15525744c959ce9685e20af8227b6104ea3b279faae0dc8d73cd4a3` |
| `klines/1h/SOLUSDT-1h-2021-06.zip` | `8fe15facd01ac0eec8d23b04bc606f2c56344c1ee2aa88c3758c07a6cfeb5765` |
| `klines/1h/SOLUSDT-1h-2021-07.zip` | `b1d3d3064ad1c48ee3db89da36f402ba27ed8764c14f5f8725db8c2d44412826` |
| `klines/1h/SOLUSDT-1h-2021-08.zip` | `13a75507c7c6396782ca02659d2738a668a5b16a438d239b64199f19c69f81a0` |
| `klines/1h/SOLUSDT-1h-2021-09.zip` | `11ee5441a6a3d72b10b501b1ac246bff97ee0673def1954d116ecd2b09f584ff` |
| `klines/1h/SOLUSDT-1h-2021-10.zip` | `400e88409c92a5a01eb4c4b7b6e4f5fddfef93dd4a3d9c8f89cc35d51cc298ac` |
| `klines/1h/SOLUSDT-1h-2021-11.zip` | `4939d7a971e30ac1d7b87c6c0352375bf8a0a539cd13bbf3e3920969a24bb42e` |
| `klines/1h/SOLUSDT-1h-2021-12.zip` | `61d5be6bdb0fb8007898c8f61375a83fe466cd18f1fc67c53e6f42b8b8a34d07` |
| `klines/1h/SOLUSDT-1h-2022-01.zip` | `bbe2ad04379133e2ca7b68cb5351b5ba610523c6a0d53b4ecfd628b972165cc3` |
| `klines/1h/SOLUSDT-1h-2022-02.zip` | `36b1e2ff3ffe162718e61bb23ef84a104dc2cc5591c18cd8ce4c04e96655b84c` |
| `klines/1h/SOLUSDT-1h-2022-03.zip` | `044c37d917fea58900c8ddf4086b9fc71fcadd55215a10680e1e7461ffa78265` |
| `klines/1h/SOLUSDT-1h-2022-04.zip` | `1e4464fee6301816ff2efa7696d8cf53f34684b9b60616cf6af26e8cd75cfefc` |
| `klines/1h/SOLUSDT-1h-2022-05.zip` | `6a8888b3d3d5a856d44eff5907210c30cc81fe210364f8b611726ad24b6846ba` |
| `klines/1h/SOLUSDT-1h-2022-06.zip` | `0a550357320ba4954437b15b85f01bf0cc0c455f07f19e27ca91ddda19f1f147` |
| `klines/1h/SOLUSDT-1h-2022-07.zip` | `05fc6f96bc940ae0d290b1039387c3a223b5159596819998563f34508594719a` |
| `klines/1h/SOLUSDT-1h-2022-08.zip` | `971ab9bee4ad830767c285d3af6df5357af1bfa2ddb084fa49596cf9b5276036` |
| `klines/1h/SOLUSDT-1h-2022-09.zip` | `41699bac620ac3f15318dd9238392fc5782d4321660e5c7986925eee3d172381` |
| `klines/1h/SOLUSDT-1h-2022-10.zip` | `bc6bb18da0f2e30171cefad3d2df55a70d12e7eafed7b566225ae67e737be6cd` |
| `klines/1h/SOLUSDT-1h-2022-11.zip` | `e156bc7231bfe31e21aaf5628260062aa9d59184ef075412ab0fa546dea1fd80` |
| `klines/1h/SOLUSDT-1h-2022-12.zip` | `8f1fa76f20f0cd161f238d4e7014274969df3d3ab5e8b6c9e1dc8327e02ec2d5` |
| `klines/1h/SOLUSDT-1h-2023-01.zip` | `0d7bc47dc3b49cbadd29274b63c02af8f23af40fe241412d357903ae945aa79d` |
| `klines/1h/SOLUSDT-1h-2023-02.zip` | `1dc1a4ad1c82935fbe8b4c218f22087470b3a20cc2c1a394574ad1587ba5a828` |
| `klines/1h/SOLUSDT-1h-2023-03.zip` | `c41bd78088a2bb8547f1b3bf5c89fcadd7606397d2a74f0961c47cf6754f8f8a` |
| `klines/1h/SOLUSDT-1h-2023-04.zip` | `34aca0062513dbb81e99b4b6e2e0e2dd29b453e33c629c8cea1beeff9faf7543` |
| `klines/1h/SOLUSDT-1h-2023-05.zip` | `4c5b1305d4395bb122f85b60520db8995c810357a2c189158b2beae2d116b1bc` |
| `klines/1h/SOLUSDT-1h-2023-06.zip` | `023229af2e8a8900ee79ba088837b174acc52512f2e8296b02aa279cf97a82f5` |
| `klines/1h/SOLUSDT-1h-2023-07.zip` | `e45b525229f485463a33f3c59f4dc3eafa2de1f9fbca8f2126cd3c074f62b6bb` |
| `klines/1h/SOLUSDT-1h-2023-08.zip` | `d509bcda20054981e3f738ef1a33090dc12ddaea5593932e2545a285ee4987c9` |
| `klines/1h/SOLUSDT-1h-2023-09.zip` | `99ac300173c437de0b735ca04ff7ac55512431eedd381795f2ba069edd9020c6` |
| `klines/1h/SOLUSDT-1h-2023-10.zip` | `e9046fe166dd07107386312716030e66aad44136d40712b17b976ff9dd905bef` |
| `klines/1h/SOLUSDT-1h-2023-11.zip` | `96c7b5324c80818622477b6d3fa71b82f62ae2266ec42f763433a11eef7494bb` |
| `klines/1h/SOLUSDT-1h-2023-12.zip` | `5d7fea512037fe238b6133df8bec56231cf086b73a44bdff89e5dcdfb991d62f` |
| `klines/2h/SOLUSDT-2h-2020-09.zip` | `dd6fdde8f4781e7d45283d7d06520c8cb97ecd437c33e5d4e3e12bfcfce94e42` |
| `klines/2h/SOLUSDT-2h-2020-10.zip` | `27f7355a180445b73a1a0b74eb2bf16dfd336b06fd1baf5f28a3591dcb145d91` |
| `klines/2h/SOLUSDT-2h-2020-11.zip` | `925a5963ecb330b6d940b03cf98bce8fa43993ff7be03aae3df433618ec9bbc4` |
| `klines/2h/SOLUSDT-2h-2020-12.zip` | `6ee9d0c5b1cedab856c5dd41a7b56a5eaa1c5307ec0cca1557e30b2140902141` |
| `klines/2h/SOLUSDT-2h-2021-01.zip` | `eb9f6865fb78f2c0ef8fc7c3274a7c665976feb50753f6368e98c96bf46b2a16` |
| `klines/2h/SOLUSDT-2h-2021-02.zip` | `85e9eae8d744b691783c8e3163e3a3befd3c64c5f7f2d86b789b49d8f059a8f6` |
| `klines/2h/SOLUSDT-2h-2021-03.zip` | `c66d38020a94bd3624cc9e1e52f7bba669da7d7a16d0cab78600f4286ba40e27` |
| `klines/2h/SOLUSDT-2h-2021-04.zip` | `69781bd80c7c36287c022054fc8a8d166e3987ed761883ec61716a9603509b7a` |
| `klines/2h/SOLUSDT-2h-2021-05.zip` | `ab84cecd0b58c540a25c92688689a87b3ede9e454468b1b98a1ebe0ac34843db` |
| `klines/2h/SOLUSDT-2h-2021-06.zip` | `2c542dd3b1c9b970502abb05258d82b9424fde62da6414d7cd8b687db944b9a9` |
| `klines/2h/SOLUSDT-2h-2021-07.zip` | `08ea67afc69b83b3c89dd515ea1c033e39342c730ea8b369f05e6eb94850266c` |
| `klines/2h/SOLUSDT-2h-2021-08.zip` | `1002a24af9b94986bac1f9c20b69292507bd078cae9559da4638c49cc29bda5f` |
| `klines/2h/SOLUSDT-2h-2021-09.zip` | `36c0fd2c068af314a868fee8c09000e7c18d2aae22d105b9f1aa2486d6cd9119` |
| `klines/2h/SOLUSDT-2h-2021-10.zip` | `4a8483eb39a941d89a32fc31a82fd7847faa8a492ed368e4ebb73f579ec2ab6e` |
| `klines/2h/SOLUSDT-2h-2021-11.zip` | `51f0d2a3719b7d3b3037a3ccc86f4e3ef73620f3c92037c6fdadd3cae9aa0ba0` |
| `klines/2h/SOLUSDT-2h-2021-12.zip` | `05cfd1de686c1218a38b7d9579d454a03a9285fa05ade5d4570a493c13c11528` |
| `klines/2h/SOLUSDT-2h-2022-01.zip` | `1ad6b809f25a7eb829a7256e7b539803db6b366331c43c790ccb0c2ef6a1cfc1` |
| `klines/2h/SOLUSDT-2h-2022-02.zip` | `a52fdf8e7414e813df23dbc31b57e4fb4d00fe83154a041a5f922d2b3b76eae1` |
| `klines/2h/SOLUSDT-2h-2022-03.zip` | `95edbe966e483869dd5413e8b025f799dd9671c440f2ad44399b236ad43dad37` |
| `klines/2h/SOLUSDT-2h-2022-04.zip` | `05691bee1b0c80ceaf421d2e45fc8f6457c2a11d4c7396f34735375951683d24` |
| `klines/2h/SOLUSDT-2h-2022-05.zip` | `2fa5593e2d9e6f3eea2d6297860c81632dd57c8f93808c4895fc8335bd7f3f44` |
| `klines/2h/SOLUSDT-2h-2022-06.zip` | `7828b2c82fd8c05bc0739a07d7fadf6b2c90e784f8236684cbc09a42c387c378` |
| `klines/2h/SOLUSDT-2h-2022-07.zip` | `3e74a9cece5653cbf3e699a7f24ce1b3960acbe7aee2781aa46dd10e217a0222` |
| `klines/2h/SOLUSDT-2h-2022-08.zip` | `3af60d7746755b89f8a706ddb1c04f9dcd69b310aa42e814005c1682c7a0fc80` |
| `klines/2h/SOLUSDT-2h-2022-09.zip` | `5516209e6dc8b6f2db3cf47a5db293fae1bdb3029ce1239512f0b569a0d66269` |
| `klines/2h/SOLUSDT-2h-2022-10.zip` | `cab8017552b50eceaf8ffb69637be1ac9811503c300560f7a864e5e7f2b02df8` |
| `klines/2h/SOLUSDT-2h-2022-11.zip` | `b1801e87d71fab5f8a2fb31ef4c24172b166b528f42db1e7b3bd31c7454730fe` |
| `klines/2h/SOLUSDT-2h-2022-12.zip` | `f728cb202f330d004a6ffd3ee5a5bbc940a341a3b52b0cbfadfc5fb38acb2442` |
| `klines/2h/SOLUSDT-2h-2023-01.zip` | `6895428fac5fb8543a3b71250e8f4372d74e35f070bc9d53789e6c4e8743837e` |
| `klines/2h/SOLUSDT-2h-2023-02.zip` | `01ee5bb1c3d5ebdbfba0f31640774ed2a4f4bbff0b64978aa69e6410666b0fe8` |
| `klines/2h/SOLUSDT-2h-2023-03.zip` | `2848f24111bb309a97c85dc0a718efacbeb94a9636a08606826f8e8154af7e1e` |
| `klines/2h/SOLUSDT-2h-2023-04.zip` | `1535e2d631e0c54c5819de608d5ba7cdf06833677cb82f8bafbabf26eaef9028` |
| `klines/2h/SOLUSDT-2h-2023-05.zip` | `a8b9330b72c999a020784dc510e3ea4d6996d982f5f50a817d0ee4c09ea168d0` |
| `klines/2h/SOLUSDT-2h-2023-06.zip` | `4a4677cdaf98061e2dcda2f5b8105cc1d3766132e71082320f49aecfe3978ebd` |
| `klines/2h/SOLUSDT-2h-2023-07.zip` | `4f2d39fd397757f56f55f309efb712348805aa4ee0c9f5359d516593203bd9ef` |
| `klines/2h/SOLUSDT-2h-2023-08.zip` | `d6a75c40c6ef5b8222e6debd8e0318943e462074ab8b4499289772d1ad7e3113` |
| `klines/2h/SOLUSDT-2h-2023-09.zip` | `668b53b14f4561476527b690d3ee2f637e3053c5be6acc61122fa1ed7847943c` |
| `klines/2h/SOLUSDT-2h-2023-10.zip` | `88a53f88d2c2bb847a45ad64d25d6138b65761ee223c02fba6d69fe04f504d5c` |
| `klines/2h/SOLUSDT-2h-2023-11.zip` | `894864aa7fc5a180955da6d4bdc3752a724b176b6bc818c0b09a072e3194de65` |
| `klines/2h/SOLUSDT-2h-2023-12.zip` | `20f1ff74540b417b17662a04952c0047a95c9e87299ecd4e2ea8c22af548165e` |
| `klines/30m/SOLUSDT-30m-2020-09.zip` | `2270e2be985b241d3eb1f825146fd58b061f0d62e1f2e1487aa36cd7efc79877` |
| `klines/30m/SOLUSDT-30m-2020-10.zip` | `305131dcb0123c365f7cbb25defab3b8500371f0ccbfc77130ce749bb4caa9e7` |
| `klines/30m/SOLUSDT-30m-2020-11.zip` | `d92c6cf7a723ce8a78b876ec745fc731d142724cda977471470d5c0a3f575d92` |
| `klines/30m/SOLUSDT-30m-2020-12.zip` | `51efea74dd7e64e7e24f4f970165fca75f278a1b2611128fcae70af4b283b11f` |
| `klines/30m/SOLUSDT-30m-2021-01.zip` | `e4dc1804a772abd9f587ad4b4c35db55953bb608f2f9a328a58f6276049cdd89` |
| `klines/30m/SOLUSDT-30m-2021-02.zip` | `1de997e9a201dd055cde9dce3377ba4c66a0b04c1aeb2bb22177856631d3d797` |
| `klines/30m/SOLUSDT-30m-2021-03.zip` | `e699208e32eb1254b52e7b87a076164f4e27eaa5515bb4cc7b2c5b9cc32ac86b` |
| `klines/30m/SOLUSDT-30m-2021-04.zip` | `6aede0201ce3ad54a388a645e84f148dc77196aaa082f1159670ac6230e9233c` |
| `klines/30m/SOLUSDT-30m-2021-05.zip` | `4a09ce53cbede34a501c8259c7a8f4286d49debb88344e5ca8886f25fce536ec` |
| `klines/30m/SOLUSDT-30m-2021-06.zip` | `27af6eb946873a6b7e6200f4a04692eccafb0052748c84145a31be752699cec0` |
| `klines/30m/SOLUSDT-30m-2021-07.zip` | `3808081451c1c4c24445f6728f8392e57f617405f75bcf661bcbfbd5192b7076` |
| `klines/30m/SOLUSDT-30m-2021-08.zip` | `915b4f93c5d815630c4dac939f5f67f7b046a986cb0bf37686a18596d944123b` |
| `klines/30m/SOLUSDT-30m-2021-09.zip` | `bf5ff69783f62568b9f6330d04f04243a9948cc9aee624cbf6e1fe9064d910ef` |
| `klines/30m/SOLUSDT-30m-2021-10.zip` | `d154f70a5b16dd33197ab564a35f0017dfde826c8ba70be20098f8d8c24351b3` |
| `klines/30m/SOLUSDT-30m-2021-11.zip` | `d310c587d36ceb012ef4ddec15cc0eeab49a5adfd0acb8195497a67c35a93276` |
| `klines/30m/SOLUSDT-30m-2021-12.zip` | `835648bebedd3f816165dd3c4b131f09098e00842645f4d32d3aeb052eb077a2` |
| `klines/30m/SOLUSDT-30m-2022-01.zip` | `4ed7e0986ccf859b9cdd0a7ac7b1c2f2d01dbab028a86727a942828b0940ebae` |
| `klines/30m/SOLUSDT-30m-2022-02.zip` | `89f30da9436b26ad701786ceb5f11b2d1b8cf92153df1956f13e73f869e17c65` |
| `klines/30m/SOLUSDT-30m-2022-03.zip` | `7f4468806594341d5248d2bf9bc1aab78a87c4c5dd4dc9646a68b1e537b6aad0` |
| `klines/30m/SOLUSDT-30m-2022-04.zip` | `03d482a3358546a862b09d4a7d84d1d8f089a8a2eab78213a68fa8506d884246` |
| `klines/30m/SOLUSDT-30m-2022-05.zip` | `7ac64b18bc783b47bfd4c1e2da1290bd7570b60ad5a8272cb7e494970984c770` |
| `klines/30m/SOLUSDT-30m-2022-06.zip` | `0cb1b43c1bd96b7398f5d434f80cfa88576a643b27376f5090d9911b36d27738` |
| `klines/30m/SOLUSDT-30m-2022-07.zip` | `c3cb43ab630a54b60580a53da8b1e1915749f12d28d72ce74963fbfcba983a1d` |
| `klines/30m/SOLUSDT-30m-2022-08.zip` | `22101441387b1989e9b755daf977fdf726f1bf54d86795015922264ed7854e53` |
| `klines/30m/SOLUSDT-30m-2022-09.zip` | `5161da0fcd72ef014528d28fd111ba3b4a034f4aed04ad0890e1311de9628baf` |
| `klines/30m/SOLUSDT-30m-2022-10.zip` | `b86d4943e72ad546cf20c69f40228d80163e0e9bca8c177af4a2b892cff49457` |
| `klines/30m/SOLUSDT-30m-2022-11.zip` | `0abc7f9ecb2d9d887fa93e513028d8e2106a8d1052d3fb6e78fb8861c1ef0421` |
| `klines/30m/SOLUSDT-30m-2022-12.zip` | `1b6229eef8de05ea5093ff0cc9746bff296a654d84cc57ae6c036e74743ab2fd` |
| `klines/30m/SOLUSDT-30m-2023-01.zip` | `7f4539dd0d07acc969e3e2122f4700ba9340d07f8e5fd1db1eac3a8bf693a80b` |
| `klines/30m/SOLUSDT-30m-2023-02.zip` | `1ef2eaa7cb59fb63385cbc49131e661194862ad3d9bde5c7d510d46221c63ece` |
| `klines/30m/SOLUSDT-30m-2023-03.zip` | `12cc575f79fc50385bb940b81e400baf25f2b3771e6799fcf0a28df564907332` |
| `klines/30m/SOLUSDT-30m-2023-04.zip` | `98ac962e9ff69166dd84750b526cef353beefe03f34c3b4970bb697d538bbbce` |
| `klines/30m/SOLUSDT-30m-2023-05.zip` | `967ec78fe9f04f7b95be2fc6903d20cd06eb2f4ce19eabf2ef01cba8b1ee77db` |
| `klines/30m/SOLUSDT-30m-2023-06.zip` | `ffe77cbc3efdcdf2984c7255792b5c5366dc060dda9971f0c740ce04c408ee4b` |
| `klines/30m/SOLUSDT-30m-2023-07.zip` | `df04effa09813894c6faeaa41a7995c3fecff61954b7468c99f52db2f1299c9d` |
| `klines/30m/SOLUSDT-30m-2023-08.zip` | `798f4c95a9cda883d5aee43473a9753a43585fc03f741ca37fcf417eb377bf60` |
| `klines/30m/SOLUSDT-30m-2023-09.zip` | `59999e05d7ec31f1adb8ad4da61e8ca257561689daabc51beae54dc45957e04b` |
| `klines/30m/SOLUSDT-30m-2023-10.zip` | `0b0f3e11a3feda12d93c87e0b09265314872e2011ff0217b79a30796e073e256` |
| `klines/30m/SOLUSDT-30m-2023-11.zip` | `f62ed5cf17b15f9e4f1bca78bb6cf2ae5268406b1603ac6c33e04378184b492e` |
| `klines/30m/SOLUSDT-30m-2023-12.zip` | `1aa16920f129c4181b2b130900036e3a6bfbb02848fdc40111509c02a1ba33ff` |
| `klines/4h/SOLUSDT-4h-2020-09.zip` | `cd5a527845845024b7c996e3dd1c3485e9facefd291233f318e268166547dfbd` |
| `klines/4h/SOLUSDT-4h-2020-10.zip` | `348b8d58d5d9742286e49e7fd2b16c7122d080633ae1660a3990b5b3143ef537` |
| `klines/4h/SOLUSDT-4h-2020-11.zip` | `8020c860845bbb4b397a54231864657cee5e8a8f7d0f475b0d7719d5ada47f62` |
| `klines/4h/SOLUSDT-4h-2020-12.zip` | `2d496be8eac72faa6d59fe8b42ecfbfef45dfe7125cd7cde627f8f786ce032c7` |
| `klines/4h/SOLUSDT-4h-2021-01.zip` | `6224eaa53f25406fde98702994d59f279febab53a8c6937b74f78bf44760fc26` |
| `klines/4h/SOLUSDT-4h-2021-02.zip` | `fd2b906ae93d7872a05b13707aa9abdb5394d54107c2b94562d570e7e2a1bad5` |
| `klines/4h/SOLUSDT-4h-2021-03.zip` | `04b047be0c86561e5b6eaacc4a0434467d1bd2c1c2d894522b294c872a00213d` |
| `klines/4h/SOLUSDT-4h-2021-04.zip` | `0dea5a0b17ee27cd2c0abc6348c9508dd7d2a9f4a249a5de433f8b08dc1c2db6` |
| `klines/4h/SOLUSDT-4h-2021-05.zip` | `60c716bb65046d35d2684cf4c816be09989b6b448b6b79cc78f4c0dcd9ab95e0` |
| `klines/4h/SOLUSDT-4h-2021-06.zip` | `298a97058aa6bedfdfcdbf2b57bfc4cfe7a1b3838e47715690f5a6c9023bdfca` |
| `klines/4h/SOLUSDT-4h-2021-07.zip` | `eea38ad1bea1ee0b6247297be1f9ea0afc3ec1c49f1f7dbc5715e5d93a4bbd5d` |
| `klines/4h/SOLUSDT-4h-2021-08.zip` | `0008999b3edb3d63058c97f35827238a40a21cd89ba87e351dbfed1abc35eeea` |
| `klines/4h/SOLUSDT-4h-2021-09.zip` | `ad78ee832df97f8b5cfe0a348a5cb7261de05af8bdad2b2b02a4b317be20539d` |
| `klines/4h/SOLUSDT-4h-2021-10.zip` | `f893b9218e8d90b8ae6c32991321665b4e57e8eba8ac2e280e2ac4e08e908f78` |
| `klines/4h/SOLUSDT-4h-2021-11.zip` | `033dcdaec0fa031b610cd18f47a528f683c27d600a3a2545c19e56aeba7bea76` |
| `klines/4h/SOLUSDT-4h-2021-12.zip` | `19d70d1ecc8dcfcf8e507a4e763391019b5dff2fc4295c24e9ce3b0031f0e4b9` |
| `klines/4h/SOLUSDT-4h-2022-01.zip` | `09ac48ccfe09bd21c95001c9eabe7e21a70f3fc4fb82f16564b1f43461ea17da` |
| `klines/4h/SOLUSDT-4h-2022-02.zip` | `b33cb8a26f1f626463c9a0e67e26f2297db4f7d1d40ed2c22000536247769808` |
| `klines/4h/SOLUSDT-4h-2022-03.zip` | `480525a29697d856be20ee3c303a65990a512b6958277e6a7c54ecf5fea258da` |
| `klines/4h/SOLUSDT-4h-2022-04.zip` | `de83fde163031147c7cb272e3cb9b4ef655d3dcdd32bcee85848c3572c501b36` |
| `klines/4h/SOLUSDT-4h-2022-05.zip` | `ebd963b2d1c3fbd35817a1d1f3061b39884fbc89aaff7933045d0dec280da953` |
| `klines/4h/SOLUSDT-4h-2022-06.zip` | `9a91fc3dbd441f50158cbb6e11356f97e06c4f26accb8b86f6801f657681f9ad` |
| `klines/4h/SOLUSDT-4h-2022-07.zip` | `a8399d0c3d7fe4810f916b88accfb464bb49e134e9a7ede26dc50a2851b10b72` |
| `klines/4h/SOLUSDT-4h-2022-08.zip` | `5409d8049ccc33f3510128572d0e255e48e392d67b5a8c73b080998aa705180a` |
| `klines/4h/SOLUSDT-4h-2022-09.zip` | `89f4d53418242c838a8bde68cc5a5fc90a597637e3189723f22a60f6d5ed43b6` |
| `klines/4h/SOLUSDT-4h-2022-10.zip` | `bcf380ac6330202b2066c465533287a131cba7fc0a46906bc1df3033ae206b6c` |
| `klines/4h/SOLUSDT-4h-2022-11.zip` | `4216a614245c46c747257b28a996e13449fd8b456648afe8bd02d0ca416b9166` |
| `klines/4h/SOLUSDT-4h-2022-12.zip` | `6dbe77ebd5a0047c8e82bc8698aedd858d88f74aff5d6059e66bacb5a5f18593` |
| `klines/4h/SOLUSDT-4h-2023-01.zip` | `5765482ec4fe53e94b725b1c21a47347572e1618bd2c2c712fb7383629e8aec8` |
| `klines/4h/SOLUSDT-4h-2023-02.zip` | `8fd7d87348f206097808cb7ede6f4da806b77e2c93624bc2284f125ce3b15781` |
| `klines/4h/SOLUSDT-4h-2023-03.zip` | `e8e05760d99677dbd6ce79aad852f545319c5346c223e889ccc4f4dc30a578ad` |
| `klines/4h/SOLUSDT-4h-2023-04.zip` | `348e8a177cb19014647cb3df556974ebc8fc8086897a64d3c9510e0517664dff` |
| `klines/4h/SOLUSDT-4h-2023-05.zip` | `18abcd226da28da3d2d3b8059cf5cad2ba9f06af2db7853bfc1dab7e92e68530` |
| `klines/4h/SOLUSDT-4h-2023-06.zip` | `d0d6e6a5d6253f19953fc1918b6a74a9290019a45bd7b23d0e41eab6b3f1c95f` |
| `klines/4h/SOLUSDT-4h-2023-07.zip` | `be14ee66574b87b44060d20c91a1d46087216bdf4656129c18187429daa82063` |
| `klines/4h/SOLUSDT-4h-2023-08.zip` | `47d0e1deb25adc23009229d52f02635d0ee0ce6bce8266d41ed5b158a1e26e1d` |
| `klines/4h/SOLUSDT-4h-2023-09.zip` | `60abebde410415a0b0e0f0fd20937c7a7b063bd4c09bbe5b71b4eae6cd758e54` |
| `klines/4h/SOLUSDT-4h-2023-10.zip` | `fc4368eb56fd373dbf87b0d57d299f5cbb0a059f58668500150906f9b028b173` |
| `klines/4h/SOLUSDT-4h-2023-11.zip` | `1dcf714ba191d7a3ce5c3a54be38930272c7163b16e8cabfa0834a8707f5dd3c` |
| `klines/4h/SOLUSDT-4h-2023-12.zip` | `25922d15deea6eac8d890422077eaff6ddfa29fe4cca0947718ba067dc5d6fdd` |
| `klines/6h/SOLUSDT-6h-2020-09.zip` | `1daa217679ecd7ca170255ef399466ecba93d69fad788b35cd566cf55f7eb867` |
| `klines/6h/SOLUSDT-6h-2020-10.zip` | `2399bc4c9c64edcf8c9740141893a154025765ce04678b21f2843fd59877d1b2` |
| `klines/6h/SOLUSDT-6h-2020-11.zip` | `2c33ad8178f943822b37dfe350eb400195da76cb97791b333fedc989b7687373` |
| `klines/6h/SOLUSDT-6h-2020-12.zip` | `8c9ce87bda461d72fb732452a4b7d29763843b256c747976647ca2a8617ccc30` |
| `klines/6h/SOLUSDT-6h-2021-01.zip` | `433bb31eb97b29b9b6c4753cafcdd8cccbda3302693ca186baa2fb8342ca3323` |
| `klines/6h/SOLUSDT-6h-2021-02.zip` | `aef12c7f0bec33589852c05dd89a969e2f70ab1e394417db5204ab864914f1d7` |
| `klines/6h/SOLUSDT-6h-2021-03.zip` | `44030988d3a94b639d915b085c9b8d75fb8abbef07eae6d317562368fb739d7f` |
| `klines/6h/SOLUSDT-6h-2021-04.zip` | `7ed890a68c5a9f696f797c4f88769f6e4a54e7eac2a8ea969e8e47d7ea9bb5fe` |
| `klines/6h/SOLUSDT-6h-2021-05.zip` | `8297b420961abb9016927bf11a968a1c2b8c8df6aea611954cecd12673b32fae` |
| `klines/6h/SOLUSDT-6h-2021-06.zip` | `0d321f0b09671a361561522c68ee22a7bdcf16dce5067e2d191e426ee1a09672` |
| `klines/6h/SOLUSDT-6h-2021-07.zip` | `38c352d8d1773553c59c06f8a8a3dd23384d879b7de0923850e35991b5db712d` |
| `klines/6h/SOLUSDT-6h-2021-08.zip` | `aa5b485047f29154a0f834c7b90b43d06f1b8f1f875563e154bf7d53eb91e774` |
| `klines/6h/SOLUSDT-6h-2021-09.zip` | `763788edaa3392ed537a016ac1d8a51c4f66cd1ea34f3df2b24742cc63c9dd4a` |
| `klines/6h/SOLUSDT-6h-2021-10.zip` | `6f576f061efee2820a2caf6eeeed55ae51c3f77391c57a301ed5f4afda9d50a7` |
| `klines/6h/SOLUSDT-6h-2021-11.zip` | `79d316793d03f881a4f6134eef1a0a793b0cf88ba7b03ffee788d51d6afe56ca` |
| `klines/6h/SOLUSDT-6h-2021-12.zip` | `d06cbc91b2dc57c578de61357ef06fecab7cb6a40fb56a2a8b4d65669ce560ff` |
| `klines/6h/SOLUSDT-6h-2022-01.zip` | `5ec67b84bf154be2a4be635b5125dfa7ef9db7221742aaa2c05b013909131b04` |
| `klines/6h/SOLUSDT-6h-2022-02.zip` | `401f43737399762922da085a896a65e72ef3aa6afd92592e741f447fc5e3cd74` |
| `klines/6h/SOLUSDT-6h-2022-03.zip` | `320f3a29b42c774007f11effd7dceaa341a38b74d05f04551c693650a4c37338` |
| `klines/6h/SOLUSDT-6h-2022-04.zip` | `fabca664cabfbadae1d4eb8113d41cb0f668f5e439427565d0c459a04ad6b422` |
| `klines/6h/SOLUSDT-6h-2022-05.zip` | `facd95b3ec74f62f946812b2130d3592b7c6f96ceaf2e47a9d71077595aa3b5f` |
| `klines/6h/SOLUSDT-6h-2022-06.zip` | `126c78617ba81147518f3e2da6bc66eb7f07d9472b8949c7d41ebff06651fc6c` |
| `klines/6h/SOLUSDT-6h-2022-07.zip` | `8d376a1e14ca4d76e924c880250015f2ed8daac8c403464603bcb6c1a5bae4e4` |
| `klines/6h/SOLUSDT-6h-2022-08.zip` | `d7a27df7bf25ea94f4f71b2641a33138ce75ece668b846503d29c5a07b945642` |
| `klines/6h/SOLUSDT-6h-2022-09.zip` | `5acd1872300c5c9c0e2b73e68e142b16af4f4860be5f27fd7535524a1194e889` |
| `klines/6h/SOLUSDT-6h-2022-10.zip` | `f5fb679e74d19850ae284789bb6f9f50a9307f75b65378635a7c21ee3d1e3749` |
| `klines/6h/SOLUSDT-6h-2022-11.zip` | `226f168c7a507aa8f6ff8f00787a66ce85e428f9fb4560da3d5c8b99dbf7f8f9` |
| `klines/6h/SOLUSDT-6h-2022-12.zip` | `4a9be41e2642006ed61718fa982298d5433e242841aae5494160953094b2b62f` |
| `klines/6h/SOLUSDT-6h-2023-01.zip` | `ee8953995d2bcc1ced6d1b27f7fdb0ada5490c35580aefef81ca3d8c7c8a4016` |
| `klines/6h/SOLUSDT-6h-2023-02.zip` | `61eec6ae53b50a2afafde4a8b5b9f00e2a0eccc743c6a66b932d943fc44da9e6` |
| `klines/6h/SOLUSDT-6h-2023-03.zip` | `97f1043c8bd591982e8dbb3cac26415e9e20f078eb254053d6ccd09e0b4783dd` |
| `klines/6h/SOLUSDT-6h-2023-04.zip` | `b5b068afea2c6ffb7f4c92ed512ece57380f89ac498031e18fdba2edd1ac9d99` |
| `klines/6h/SOLUSDT-6h-2023-05.zip` | `2e7e3a4b0c112918a1db1bb774ed62d54f2a604ab5e11bbc2a994fcb2332f48b` |
| `klines/6h/SOLUSDT-6h-2023-06.zip` | `017beb4b8542fa959e7f75cc6defcd65361570f968808b765e4c1c1a92c0f5f0` |
| `klines/6h/SOLUSDT-6h-2023-07.zip` | `c6320d08da95c624b4afd4f33b81cd54f49e3dfc3a19b770a79aadd4c6c560c5` |
| `klines/6h/SOLUSDT-6h-2023-08.zip` | `25015f798921aac7b47272f739f32f36a25719881a63c834f7205a252aed9a17` |
| `klines/6h/SOLUSDT-6h-2023-09.zip` | `64b28b800c4da264071c5ab820d5de447066051f3061288463078b12a4581697` |
| `klines/6h/SOLUSDT-6h-2023-10.zip` | `6074c416ed34625d4bd775c97fb7ed702b3eb6ddb1155d8ada3fadf36e4d0268` |
| `klines/6h/SOLUSDT-6h-2023-11.zip` | `e1f8c4801ff764ce81fd7a75da20c5c881e30b38f2a6589e88415d5991fd62fc` |
| `klines/6h/SOLUSDT-6h-2023-12.zip` | `e7b06c72de4f5292e9259710ef6d94216c9febba42c0d8774172dce2f5b5c518` |
| `klines/8h/SOLUSDT-8h-2020-09.zip` | `eff7f46223321fcac74d5f9446f0cfe47d95d079435244b621fb789a65b0db3c` |
| `klines/8h/SOLUSDT-8h-2020-10.zip` | `ec3a57411870bca95b6dfc3511a1524b6e69e10e4f03963e3e1057951a488583` |
| `klines/8h/SOLUSDT-8h-2020-11.zip` | `0aae376a11e185d61b00b84aa6f2b8f0351def2c6000107d1ac03f858cfe693f` |
| `klines/8h/SOLUSDT-8h-2020-12.zip` | `8528afb6eccba2e51d7e8989ab6439fcf986aa99a5a4dde5fb2fea783cb63f9c` |
| `klines/8h/SOLUSDT-8h-2021-01.zip` | `77dc188f45fdfe5703fde950611ac7d5e9565443263ac3ca4359076d615401bf` |
| `klines/8h/SOLUSDT-8h-2021-02.zip` | `db75a50abe99cb520ff92daec60238e52e4ecfbcb10ccac13b66b93f19efe46c` |
| `klines/8h/SOLUSDT-8h-2021-03.zip` | `53f05fca2b08cfd9f7a61479eab1366e54d9a32b1ff4df6dae958dc57ca5e429` |
| `klines/8h/SOLUSDT-8h-2021-04.zip` | `74eb2c08833a3fa06ffff2e957556f93d3c8430d2d8721076c93569728331687` |
| `klines/8h/SOLUSDT-8h-2021-05.zip` | `4d920da6947db689bba0280a5b71dbf8e5c9d360d13a9962455bd1a08287b3c7` |
| `klines/8h/SOLUSDT-8h-2021-06.zip` | `3fb4b0e4c6cfcabfbc46a235714032e9573a7842f5a4cdd89b93c0e18d5f6ff3` |
| `klines/8h/SOLUSDT-8h-2021-07.zip` | `127f9684844795dd7019bb5eb1b9a261d5f4be6f0e35d5d6a3b382455270bcd2` |
| `klines/8h/SOLUSDT-8h-2021-08.zip` | `5444b000c35a41720d9ea1591bf01ccc926b9b3e34d7a57aa783c94893a4d50e` |
| `klines/8h/SOLUSDT-8h-2021-09.zip` | `a837f84088ed962875e46e1ac44de75bb9c7785e376cf78b344bd09d35b6ae32` |
| `klines/8h/SOLUSDT-8h-2021-10.zip` | `10511146c67c5b8c804799323d551dd4eecea385d0fc06a744b8c771476e78a8` |
| `klines/8h/SOLUSDT-8h-2021-11.zip` | `f7efb401142697d6bbdde7fcacdf2080f046ce266abc486a70172c1a7c463e4d` |
| `klines/8h/SOLUSDT-8h-2021-12.zip` | `f2700fbaa4a2b44bb34728c0c66c2f4504f711cbe0fb6c39fa4a546daa94a769` |
| `klines/8h/SOLUSDT-8h-2022-01.zip` | `91e4f9f018a0e60d1acf7168b831368309822bf45c9af71462dea63fc99aadd7` |
| `klines/8h/SOLUSDT-8h-2022-02.zip` | `dc00f80eb4280bf6d2b52791da73c9ba5f1e32e88f271bee82c1e87252a63464` |
| `klines/8h/SOLUSDT-8h-2022-03.zip` | `a271bdd09c1ccb46ff4fa799196f82c8bda6b12b5c9b4b2c572083eb732ae5bd` |
| `klines/8h/SOLUSDT-8h-2022-04.zip` | `99e7a58a0b4e961bcbee944e8fca1e995b482d1c505e57ee892d29e17247c7f6` |
| `klines/8h/SOLUSDT-8h-2022-05.zip` | `e1940e05b52f1f540221452f81d1e61084970affe71e15f7c142c3d9f57f2459` |
| `klines/8h/SOLUSDT-8h-2022-06.zip` | `8502b4a235274ec9cea725b4f17a13c3d751f6624ce0b430780357aa57f7af78` |
| `klines/8h/SOLUSDT-8h-2022-07.zip` | `f9043b24a9e4aa57d7d0e8f5e33b0ac9bc9b8a7ecafc61a822383a83441f2ebd` |
| `klines/8h/SOLUSDT-8h-2022-08.zip` | `a2de04b74f8bbb828a80e8a091555977796253bfc75fcf941cd5cae253111c06` |
| `klines/8h/SOLUSDT-8h-2022-09.zip` | `3b75b5cf05230f65e75f414e0e7ce7851384faf25fa43aa4e8896249860fe110` |
| `klines/8h/SOLUSDT-8h-2022-10.zip` | `7dd1141a24f4d5d32078a77b9674ea7d699a0649d96e76acf62b75b8fcc56c4a` |
| `klines/8h/SOLUSDT-8h-2022-11.zip` | `f6266d09d7521ee3e721af8238e63e575de708b3d2c26a614372a6372aa5282c` |
| `klines/8h/SOLUSDT-8h-2022-12.zip` | `403f6f125c43f105a50bc7981b5acd1fb3f90f9ed86c581fe26effa9db52c601` |
| `klines/8h/SOLUSDT-8h-2023-01.zip` | `7226f3ccb89d88f0e8cb7d885e0029a1048827e97a9cd2fd279807af7b98af5a` |
| `klines/8h/SOLUSDT-8h-2023-02.zip` | `8eaee1079d6f00b1173651f18875029e41138adc82dbda5a1f5157dbc02ab967` |
| `klines/8h/SOLUSDT-8h-2023-03.zip` | `2e237765e5da472d547f2f0ad1f369333730e12b5960a31df3f0ffb08ab490a8` |
| `klines/8h/SOLUSDT-8h-2023-04.zip` | `f4cd67eecc3f20b81bcbc9d827d8b557b43f63476f3dfa82380e59fb29c28afc` |
| `klines/8h/SOLUSDT-8h-2023-05.zip` | `2c28acd5eebc035c75c9043c847d526ae859f47952f97b16fe9190dd27b4e975` |
| `klines/8h/SOLUSDT-8h-2023-06.zip` | `9c17054ced9017459a00b993e99f25baac1fee65c331d7c5614c011a7c519170` |
| `klines/8h/SOLUSDT-8h-2023-07.zip` | `221c6ba325929e5128cf4a2ff4e02bc7060bcf1c5bbacdc458f0a8ec80504302` |
| `klines/8h/SOLUSDT-8h-2023-08.zip` | `42d2c597af4c970baaeade58509aedacb7bf616e170e929b3db9da3aec98ee74` |
| `klines/8h/SOLUSDT-8h-2023-09.zip` | `3d72acdf0bafece69abb01745b9e4ed222870a929d5804f936301f50a37ad86c` |
| `klines/8h/SOLUSDT-8h-2023-10.zip` | `02fce087aa196e89ac96e2d598a1ccd5aaf998613b670f9041c928031a7d6fff` |
| `klines/8h/SOLUSDT-8h-2023-11.zip` | `58bd52693aa7a0ce28f8f634875546bb549c90266a99ef4949fdb23f857c5103` |
| `klines/8h/SOLUSDT-8h-2023-12.zip` | `b70d054cb7b484ca1bfa893695da3bb8347166bedde7c038ef66474b9017f0c3` |
| `markPriceKlines/12h/SOLUSDT-12h-2020-09.zip` | `f8da66ed2c010be02a7ddba76eaf516137caef0b14f5b64e24b5640128aa1492` |
| `markPriceKlines/12h/SOLUSDT-12h-2020-10.zip` | `f5d263b15730a2eda84cc1607390fa5e10b9883c961c68501876481c9e326170` |
| `markPriceKlines/12h/SOLUSDT-12h-2020-11.zip` | `1f027e44b9d85ffc4577ec7ad87b0df255996b0f6105bcfc79c0fd09448975df` |
| `markPriceKlines/12h/SOLUSDT-12h-2020-12.zip` | `8026ca4a20e5149d34216966903ee767fcd34a88ea0980104f6aa87981d996d7` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-01.zip` | `1f17749d15bdb38d6778deceac18084a1872f97a36e31e25d9730a080d7cb348` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-02.zip` | `cc0b25fca279ecead1ffd3807a013d1ed6e9cd64d536de4973a8e16b1af6514e` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-03.zip` | `e49209fb13e05b6287faaf54c9b072936b8601b47f48fc07f28de561dca63f8b` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-04.zip` | `1e1a347351c76747ec311d2eb08b01c795807739a7388bfe4cc4ff2ca6e72268` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-05.zip` | `b95ccb4117e057123638e0766ebb59843d4e70b8ac416aa958d19ae8e28917a6` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-06.zip` | `e93e8daa530f561091c5cfbdeed133fa3a6301b85ed4a7d2f4045ffb8d8b131e` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-07.zip` | `a836327120d893f404b8f57e9cf73bba852c1577226283e2ac6261dc7bfef0a8` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-08.zip` | `a2ce48af48aa181d607ba0e9893351d44b5c735da6f67be28520dbf5979d73e0` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-09.zip` | `6dc35420741ddb5e5cb70c57b80509df38125d3cfff4e331cecfbd6c95d3bfc6` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-10.zip` | `9106655e40ba57233a0ea010de26b86575d649fdc550df0f7ab8342fdfdb3e3a` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-11.zip` | `b5685382491e5c70821f449d681d6227fa9eae2b981dfb17ba5ad94e4d84954c` |
| `markPriceKlines/12h/SOLUSDT-12h-2021-12.zip` | `361a1caeb2de9e20617271a70cedd860eb08929466a0f785f64004c1099d41dd` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-01.zip` | `9c9f6da28d757bf58bdba341d5651085fc07ec3857d64e5cf0500028dd2db864` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-02.zip` | `cad74e74b4dd7254777efe6793fecba2c59a5a579e14644f9d69d8fcb0d88fd6` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-03.zip` | `d0f450399a7212caebdb43ea00c105f377bd6bc0c4690b617245f6ef8b566c14` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-04.zip` | `ebd72a3a813461be69c6cd64976f9e06b0d7fb5434488fc8ef2316ec9211ee49` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-05.zip` | `bdf4e46c772d7f649e0d73986897e17ce235c22b1fd63e152e63f2598d6b2889` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-06.zip` | `c7f4feb21f7648235cf3d4ae6397830e7e8fb59609957126224f6655edf03411` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-07.zip` | `633558f9e987622158315a4870e4ca609e9dd9a029ea89e825a03f07ee77ebac` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-08.zip` | `7cec18d1ab9f6b4428208448bfe91b98dc5d548ff58212ceacfd51151a80640e` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-09.zip` | `eb54763ae6aa41eba343685335e48b307438eff0e75cf3f931bf0e2135fb79c9` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-10.zip` | `f4f0cfc95436888bf77e740b172d47e57f1ddcf69f0ccc213577418f492d9984` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-11.zip` | `9e22b0301f6a8feb56e9b842ec1a1239f8b26039766c6779786c2c0ab5e40578` |
| `markPriceKlines/12h/SOLUSDT-12h-2022-12.zip` | `57e3095fc82ed6e97f6b90b8c629f62a0b0b60f97aa069afdd2433fc63299400` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-01.zip` | `89dee8ddb6f8b128b778d3564b52873da7d54a13158cbac6827c95e5b4027202` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-02.zip` | `2032d9aa5b5c387b73a2e51808dabe9c92b4d335615afc36c42420b2e7146e04` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-03.zip` | `41830a6308b6c37a4067ca7422bea824570ea90e9d5080e2c970dbe581ff5f93` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-04.zip` | `ef1c0c188db66ffe95b7a13b74069c66e994c445a70b3ebb69f37e1b9ed4e359` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-05.zip` | `5a1b822c3b8b088b83c45905d78c119976901dc2ce41c3506a031d26666bc345` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-06.zip` | `44aeda5f4ab114f83a0956d9fd1f39807f1c089e7531120976e7caa1ae9c62b5` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-07.zip` | `1f373bde11b7f67128ee5d67659f537ff06399bd535e240d56eb04a75201a107` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-08.zip` | `d2e1a37a21a7e965345fcc7cd7319a2c3b5adf79b0e224f6cd6dc46894ae5e76` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-09.zip` | `d65ed9bfc429b68eb639db94170dcc88a664ce9587e52ef942e874b4013336b1` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-10.zip` | `c15ac3ad1657bf2ce183ca776f8f1e9a36727b0ef45ce4cae6af38074dd357f0` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-11.zip` | `0f90d95d794ff1d7db01d73a5955e9dcd991fffcd8876ab0a50150c9292ee5d5` |
| `markPriceKlines/12h/SOLUSDT-12h-2023-12.zip` | `e6f82fece21ed10856cef17571e3585cb5cfd0a9de9f0e4bb848c0facd93d4f1` |
| `markPriceKlines/15m/SOLUSDT-15m-2020-09.zip` | `d0fe8edc49ae687191575f9ffea7fdd44cffc5104bc449d7595697fba7d9f164` |
| `markPriceKlines/15m/SOLUSDT-15m-2020-10.zip` | `4240c6009c1b25978948bfa0fdbbb134ee66f4cd367c9224699671c8b2cb7493` |
| `markPriceKlines/15m/SOLUSDT-15m-2020-11.zip` | `5ca297cab1fa4da461264d1b322dc446aeb7f82fe3872c54179ec26e454b43d8` |
| `markPriceKlines/15m/SOLUSDT-15m-2020-12.zip` | `3ccb35eaf4d980177c9556159fb0614cacda055b48d61ab35a268e281b06f80d` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-01.zip` | `4d25be7bb18f58d7c334b3964b6719f3f393bd815c7150c191e545dfdb0d9bd1` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-02.zip` | `98c2cc2eb3faba42f5aea9c95e11e2ec1a2053a5689e015a31ed507538ece2ed` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-03.zip` | `25e6592aaf94d66a86bed8141d935c8be5c21935e3540de5d22a2270dd4cf82a` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-04.zip` | `901d2ac838734fabf60bab738ae78a47fe9f14f9118ef176e1b3f95d76ac906e` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-05.zip` | `8f8ad78b0f8f716d1909c76cd60f0e4669b3d3cd5b2a7da74702a3c3a0a64a6e` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-06.zip` | `03287d472f59f84253c0ee41ff03c5f80b235101edddaae3f1dbd001514f1690` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-07.zip` | `a8f556c3785386248e8334a47796a1f2b9a1b6af9fcb8d0815cbfb433f780e3e` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-08.zip` | `d6f949544e40f0d855e38f63218db6457591eaeffd28b47cc2fa690f82055b9e` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-09.zip` | `ddc7c63b2e5dfb343f260b833171f488706bbb6f62611d4f2dd653c9111b5989` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-10.zip` | `f919a0651410f353c564e08e3304a53c55ede5559c9225384c1fd1184cf1d11a` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-11.zip` | `3b81721c8489033a52a00c7439cc3cd44892ca9aa59c5c5fd60e8280ae54d9a5` |
| `markPriceKlines/15m/SOLUSDT-15m-2021-12.zip` | `ce67f55d8e9554ecdf16b934b50411fc2748368876f9fe5c50fa886bbf015548` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-01.zip` | `8d02b56bf3306be6ce68d1063e84d59b51c8583fb531dc05e7d8dc536a18afee` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-02.zip` | `47768ab4b15ec3e7030da09c1513bd4ff5d5642c00c0d36f1e4fd8b55c6e3579` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-03.zip` | `924330f31da920684261624d239e794595f70ded2410437221b4d4d19621b4d0` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-04.zip` | `656b9364a3a1f43cb00fa3687291d6e3dceca834a1408f2da5ca58938bf731af` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-05.zip` | `938508f3a74be9077cfd84ada8623880799c0d5ac9c08c6b744ea167dc5f3cd9` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-06.zip` | `d80f8423b395fe2da03dbbfea29afeba9ab98c91fd2a506db4c2771a216d8803` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-07.zip` | `8f943b69e93130cfc717e43f6e21dd01433753b1db9ff9f9e541fb466d15f89f` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-08.zip` | `a6ac87bab36f49e2b019f62b100e7776edc0d79fb0a840374babd479414bec6f` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-09.zip` | `94e461abc3ff900edaa72cbb7008961432a3d0faaf0cb99d714f8e7a841bf011` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-10.zip` | `e4b1d166c7bdaa9c1b911af5aeab575b41f207fdfa1420df4768b5eace00914b` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-11.zip` | `712fcfaa2a0b0578a54ff2a0c0e23624f8467341c0b53fa922e826861ae9114d` |
| `markPriceKlines/15m/SOLUSDT-15m-2022-12.zip` | `826b89733adb957bb2c0dd77d6c6c97a45d0a6630fd294c767cc374a9a35a6d8` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-01.zip` | `b4cf34585e048fc81d514fdf9568823dec797e50571d5ccc9b6e23fdaea27a79` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-02.zip` | `91c820d170a0cfbd6a165bd0d55784b1613785b24edb00a4ed514b9aa1a0453b` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-03.zip` | `a8647e11557c62dbb7a9f0b8dc923649d96c03aef5c0feded6462973bde95d53` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-04.zip` | `34a5e077cef4f91126fdc75050d68a1bd0a96a5abbe0d9889963634aff2ab9c3` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-05.zip` | `2018d03e77ff868ac3c06f1c7118babb47d935c8d4804f0b42ff89ff5b6ff391` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-06.zip` | `a40cc23aa75f205daafe39b38fe52a7aa25a3893fb59491a101e265b1285e94c` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-07.zip` | `e3684b6fcd9dd53e5134c9334433d3ec0b5968cc2634e5c6201b6a3b79947e15` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-08.zip` | `4a219806b2b07b2bf74d780efbb47598a4085ded4b50a33eb5604420f4762054` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-09.zip` | `85e2e1dfd5dac2b40bed0a8388cd1aad6a8449f0fd50dc3e1f53d92176d2d2c9` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-10.zip` | `d60b273948a2085f7c0b48e915fae060bdd54865d853df1c35a0e9d01990d43a` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-11.zip` | `cabca357356858eb22d86dc7cb312d3ef33f236154ead99958ca2f8b91000e25` |
| `markPriceKlines/15m/SOLUSDT-15m-2023-12.zip` | `4da490a1e7a41e46fc8826af84bb9f86756b6c2f6533869aa95ab8f49cb88319` |
| `markPriceKlines/1d/SOLUSDT-1d-2020-09.zip` | `439fd633a6dc757cd085b768ad3441f7e9fe92e1186be97a6d1cf3222238f2f2` |
| `markPriceKlines/1d/SOLUSDT-1d-2020-10.zip` | `33ca314a0afc419a756dbc4ba16728816e4550a6c13d005057e85262f83ad484` |
| `markPriceKlines/1d/SOLUSDT-1d-2020-11.zip` | `9e69ab62121c116ddf8794dddf845700c2aabbd0ccfc1af3acdda88829f03f64` |
| `markPriceKlines/1d/SOLUSDT-1d-2020-12.zip` | `6d0a728118a4d6217a3148a951febbd561aed6e773ddb7e6f69066eba93e0919` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-01.zip` | `82e14b91ac114873464bfcd8eb210612536f8a72b0d64d49a3a4e0bb384ac2c0` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-02.zip` | `37b093bdd52c526be28a0f548a156b1f9d34100caef957fd259f669733d66c87` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-03.zip` | `3bb4616ebf755252f36e9c0f9bc633e0926c0ef06ed0d0ebf630340768b23857` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-04.zip` | `7e881e3dd2db860ad61a54e0fe35942eec96a73e91a3fffe49fe343acd1a0f8a` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-05.zip` | `9a302793f4b6545cf95f542c2e3bf6e0f40ee055ad6a0f66080f8c498cffa886` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-06.zip` | `564fe2292264f95548632d7173a1eb0450755abfff55e079e465e624990c7b6b` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-07.zip` | `0c4c1293e06a2aee6c58bf06bc7db6a7f8bfb2dbab3cc358674854b7f9e581ea` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-08.zip` | `b936d7ecf6777bcfec98843184a1dd929b3242d7a66e6a5d29c204deece0c67a` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-09.zip` | `e91505c39a2be8a1960bb342b455de7ff319e78c138c39d9c8e884bd8611d020` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-10.zip` | `0f7739102c275f98cefe0492cdbde04d2c4f5efd1f0eb91beca0fffefab3d6fd` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-11.zip` | `a2161e0ba9c55f21118fe253a174d7b6a5a5d43baa4cbb3b4736b8c30d2047fb` |
| `markPriceKlines/1d/SOLUSDT-1d-2021-12.zip` | `5f142c91e90fe9fbe1346ceaf946112468ba453dcf8f484f5d3ecdbb26e3e800` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-01.zip` | `59c78cec3f957523e412cdbec4a7f95060f216c86839b1b346b90b9c167c0151` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-02.zip` | `a2b1afd783f4a7870dd98410c6a0b922a9ef7b4549e7013fbfda4e545fe760c7` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-03.zip` | `fc77860147212b9172643e2731af87fb62c5f5e729fddefa6a4cbf5b7fe85f50` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-04.zip` | `c37d209e674488ec039ba6e3c532825e2df0c3ce6251c1b51dea955799bdfb04` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-05.zip` | `514f397920ab38a46ce61e76fd91601b8649b76eeae69f7b1c79955b496512c8` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-06.zip` | `649e0d1de87277890e35f9e046338c6c16c78fd120fce4c27f15a061a225f192` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-07.zip` | `5ac3cd89910a2302ab367eb8fc97eb695b9138de1e50e495d31cf3b6abb5f8c6` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-08.zip` | `6f0b84993eea3966d4ad6f595df80225785e31cf3f386685eeeffe95707360a4` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-09.zip` | `a5abbbd8ef267d490d66675a2c8cbc333bb7d25557f09387620616ef897d82b8` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-10.zip` | `713da489bd322076b2e4df331bda22afad5af61ea21342f692dbd2aac4b86516` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-11.zip` | `32def335d5e9ae1ad0f934f8931091392ca21f00f9ea88da09adec8559fd1dca` |
| `markPriceKlines/1d/SOLUSDT-1d-2022-12.zip` | `09f7067b773deab071a76ce3fb5fdf09ea73633e5ba19b72d0906f6b2bef5537` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-01.zip` | `beb0569c2b0203c514fcd15e2b6f1e7983d00c635421ab77b224fea919fb0f61` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-02.zip` | `4d9a70a6bb581ad5da3aa129a12dc2a7a0d5c047ee55c1c7df00a85e575ba6b1` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-03.zip` | `96803c32ba1164efff3a750a129d5f533e131b2a6333a19d9d7dcbd4fd0c39ab` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-04.zip` | `2920fbb8a92d7d1c85696af2d4c0bb318c5a806ece4bf5b41ede5ddb6272fdec` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-05.zip` | `9ab35481d8a5bef1f0d27f63c17f7c1e139ded438870ffb345f60c9696f557d4` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-06.zip` | `9b27d32ae3ae2c4daa68a67d5fb90fe6db5e115e4bcc62c725a14dce8e96cfff` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-07.zip` | `5eeb13a3a643e02d4373009fdbd35a0d8b33b6df2ef84fe4b51059c250732942` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-08.zip` | `c0ac3684fd8f7a34694f0a20ca3fcc76b7f440355fad1e01fa4806df11957d13` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-09.zip` | `453a9365c79e53c7258033e7d489dd4714f15241df02198a42c720b29fd487c8` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-10.zip` | `aba655bc9e401873065feda41c48b319c95b098cd65f0ecef0c1d896d309a547` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-11.zip` | `6929069b7d2061a0420703874a178156eee033ccade0609a1af1c6ddc6100f3d` |
| `markPriceKlines/1d/SOLUSDT-1d-2023-12.zip` | `739814cfb513f8e54a2fd4ac8f4f6cf06c0ccca70e79b5cab6113fcf49722c78` |
| `markPriceKlines/1h/SOLUSDT-1h-2020-09.zip` | `b3da220297e38718693c6d3270db9f058a06caeac5bbb61a8a7a13bb77b2cf79` |
| `markPriceKlines/1h/SOLUSDT-1h-2020-10.zip` | `a182e4f55ffa9ddc1b64f40e8cc5356085b4ff3f4d03ddfbbbdec53fdac6047d` |
| `markPriceKlines/1h/SOLUSDT-1h-2020-11.zip` | `420b029056f6f9269b3b235962058ed136c69cfa3a53a54e930343a4dfe91027` |
| `markPriceKlines/1h/SOLUSDT-1h-2020-12.zip` | `4252057392bf2e6e6b5f089fc21b44c6643fbb7b44af12ed090ff4fd844a710f` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-01.zip` | `57bad9fb5d6576af86e8adf1a4f8f7ef35122cda93af305c197245ac40af645e` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-02.zip` | `9a15c15d8883f691f0379d3491fc5e97248fd4dcf0f7246b1a1f45a60f133640` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-03.zip` | `062fb63e19022804a3a4522f52d8e133f8e539cb82b0f36f3888be154dbd2b8f` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-04.zip` | `4d6e097172ec56d0f5d13f19e67e919c6c8af632bc6a0bf3c4aff4bbdf25b854` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-05.zip` | `338d77655f5b7c1702b743b6a0b8247555bdc1db0f3aad81266737d981445f7f` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-06.zip` | `b6d5d7d9cf8ba0d06916f62ca73d5abcaf4b95130b1f82399b2133d4ea178407` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-07.zip` | `3c946109f19db3329a0306619c9d34f49add4b3907253383b4b8230d9cc69701` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-08.zip` | `e88f41e312db96ee771bda27ac701b8cc4f8098b3b79adf4420b718bb8584915` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-09.zip` | `cc51fbbd28e1fd2de210f0d2728bbb328c420c9f4220dc6536e2e3d17eb929f3` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-10.zip` | `e388be161ccddfd2a6e88f8ae3c480a9df84b97babdbe9b13d6decc3838238d6` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-11.zip` | `80a1d81417bfc0d01235f2752b0c6b72627f9cdefd72dd76977c5a7b0b6bb267` |
| `markPriceKlines/1h/SOLUSDT-1h-2021-12.zip` | `d5fee35101c3e4ea6741652e71875e810f0da4c6af9263958a9dc5fbca729d7c` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-01.zip` | `6c85571fc2e2172bcdae45cdc3a46e8e4167b21c61edea8888f94096e05d5c0c` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-02.zip` | `1531c45b25f052eb2efc81ed60aa55b6424f3598aeb516055bae44930aed7aaa` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-03.zip` | `49e77a42787a5a4aed2ac0a2e528e71fe0d852c5f088867a30a07a6438737f30` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-04.zip` | `679e3f7b13b456620360f7935933ea4782858cda3239f8a5a098200dca6bfb3b` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-05.zip` | `7f46493130fe4b34e084377bf2d92582c12be3ae5e6046a9762208bc5c1b1ecd` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-06.zip` | `bee6259a08db515e4bd55f248b2883615b2676ea42527a46d2eccfff8ca3f51e` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-07.zip` | `33912547c1207b734dbe849b9728d9e50f6a5a023298e5846bc58a0cb046aa10` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-08.zip` | `48198b926de2382a54ca7b2c452e6c358653492558190170ea9b89b0de548065` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-09.zip` | `60c7b2428567b97d22c00ab300a19de3e52e9e0107be95a036e2ef2ff1968738` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-10.zip` | `4d137c5553bff5a2a2cba5a8702f6da0c4e7b741fa9464055a330c8df6951334` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-11.zip` | `b5b44f3fbde48248b476f843567f0dce2a72a5b1d63f14d6d94527710a7c0aba` |
| `markPriceKlines/1h/SOLUSDT-1h-2022-12.zip` | `d1a32494d1013de7016f991afe666e5ec204735c542b50584f45464031267fc7` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-01.zip` | `5119096a903299268d5fbd22fb89c8503afe71b944b2b5c2895459868df26fb3` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-02.zip` | `2bb2d49cac17d9b397811c17e5a23a6ee79b30c7c666a997eee340828b999845` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-03.zip` | `a3e5fa73282bce4cad34a3743645815590e49c4c569dd87adc0d2273fc2fb6f2` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-04.zip` | `c50e8d7833ed159069c4d07f12d4e723a4d5269333e6a708ab2b6b94fc9f2a47` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-05.zip` | `1c6887d6ae001da3bde5465b9c43760f64297604e01bfd2697331045791afaa1` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-06.zip` | `18b35840c45e233e1e04d69d129b3a143e57d5d9eb74af7d5e2b718e157e3d01` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-07.zip` | `2300bcbeecb2e795266e5b39d9aa35b0802a4c828dbfaf354f66bb63c22fb8bb` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-08.zip` | `0e2b28ce42fb9ceb8da7f8cfa12cb6c621167fc61267eb98ea36b50e38ea02c0` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-09.zip` | `24535d2446ea2549bb255f9b147be3b967a1411cda7e8a475a011b50bdfbbc2d` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-10.zip` | `e46a477e554a32b318311fd071cbdf640f77e9d595e76f2b2ee1e99240b39a80` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-11.zip` | `062e5e60502dd8f85ad54c6444a99251f96b6ea6cfe3034dee2c959ab79aafea` |
| `markPriceKlines/1h/SOLUSDT-1h-2023-12.zip` | `fc3eb1fb13deada67d2950b662d255a00ff0ebe6afe92686decab7e559c59cf1` |
| `markPriceKlines/2h/SOLUSDT-2h-2020-09.zip` | `e618dd0ec2e669e396acc5c8f6fa94fdac209bdcb1f8db62d861f90105966d46` |
| `markPriceKlines/2h/SOLUSDT-2h-2020-10.zip` | `68d3277db752f72595ed0ff7cbe0755c48dfc583008d4fb9a109ad0dba3f5b9b` |
| `markPriceKlines/2h/SOLUSDT-2h-2020-11.zip` | `617212d161403664c66ee28215fa787e9706b2d18c3e859ddc4f6c744044978f` |
| `markPriceKlines/2h/SOLUSDT-2h-2020-12.zip` | `d851e7da974803093ffc89507b5dc777b05c0e61aad569623aba6101a02b9370` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-01.zip` | `87966da96de34c45bbafaadbe029235b349278c30f3a3c8a5fbc647fb8fc8578` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-02.zip` | `ef3487a7e8760cb26f3540d3839733cf9d59e4457d73f9518d9b63c1fa37e876` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-03.zip` | `ca59c4c8b5c100f5efca7eeb72b7bc62abebb8c5de254ab9a118debf22056d65` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-04.zip` | `eaed0ce7889a89244b1bf641e03f7335df2013d8cf6e95f96b65e2840ef57922` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-05.zip` | `df6e6930f708b81c763d03ee270cba056f36dd8ae5bedd11fd3e31b3b8447a7f` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-06.zip` | `39b4d9698995b75439d8c0cde30b8136dc9e2c349f76af3e124b24820961b2c5` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-07.zip` | `c27fa2eceb11215f06d79e98973a3dfcd22f393a567b302a6f5e13c8291a0f17` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-08.zip` | `99d85de913ca3c8bedd20ce485920a0ab88c636c320532d41bb0da18dc7eef83` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-09.zip` | `b1c4510c62de6fb0d8bfa29641626df7aec0cec59b4d6dfb03ba553aa8567437` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-10.zip` | `0da7429a2b8f6ce4ce4a26642378b917cf14804df4adbd9da7253a55e0c8b9e3` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-11.zip` | `ddcac6157761d793725c1554c54166001b6b49af2639f70124ef7d6a3148be4a` |
| `markPriceKlines/2h/SOLUSDT-2h-2021-12.zip` | `4e9278730ba9e6604912253ea25d8555e2e42a0f54f8203bb057fa659e1d664e` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-01.zip` | `c6e9d3dccd1d97c79ac14e210e7360c547b417dcc7be5756234dbd37171e89e2` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-02.zip` | `c0947adf0b214ee460c39581ea87dfcbf1cc37e5d08306cd9ebb4291d1b91281` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-03.zip` | `23e040928ac8e4355a768b3b1d1bd36e2a1fba9be9eccb12b73f57e3a5986d68` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-04.zip` | `b348a02e9b8a1a99ee90113ec42dbf8c6f9ae609ad2d6f397a180e8807a08ef3` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-05.zip` | `ff79afcb9fb85a805dcb3a2692e508045857e8217fe65799ad95b99a4b93dc76` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-06.zip` | `2a547be23ce83dfd5f0e5406deaf191079942f6f7c33e898971c6228e5e22dd6` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-07.zip` | `f3721a6c47601aeb481c6e994f1a995fd259f1dea86b59969699d20c863011e0` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-08.zip` | `7cee4d805fe463b695fe013c44388f882d252ca4db35916271170c3518c39084` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-09.zip` | `d357867396df8587c3998f470390a83c65800450cc1e323033accc776f18a000` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-10.zip` | `73efbdf61194f4ea77a26153b43348b68288b87c71b2ecbb74664c601c383a83` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-11.zip` | `7f9b9609be912e679edd4e74902daa9d566215fef86fdc8686cd3b3df2bffe41` |
| `markPriceKlines/2h/SOLUSDT-2h-2022-12.zip` | `062ed08f58be8cd9c96ca4e38095f038ee4697abd64237c195e1c585b2755188` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-01.zip` | `257047b254e25777079a06e17c30a8613e2d7f9dea4eafd3471eb839903965ba` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-02.zip` | `537af2619daaf51f9c3d82fa6a968a366718d74eb769b715f91437ba16a570bd` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-03.zip` | `ae13e03eb322047f017fa98931a8b324707c3fe05c90b2d126a0dacf43eb1154` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-04.zip` | `e4d00b0e2cee699dc6fc15f22950d4f9f324d43f9d25122ac7d7d340c3a3cbfb` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-05.zip` | `99ddcd02a41cb3868f597e2b4456809272656d7613778b382a736fc8f2d6dd40` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-06.zip` | `99f81cadafa8d5015c415f66f1e4cb4d76676f66c2b1a1c3817a7b4e4badbfdb` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-07.zip` | `e62739f629f68ff29ba8fc14a81068ae60ed42831ff220d79b6c6a27733def2d` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-08.zip` | `439ddd7e13faede033facae197e964ae07f821fee97daf77ccccf54ec1dd2365` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-09.zip` | `a12b5104a204db0c0ee23ad4eac4104afed136f10126a3dc8d29b1b1f015dd19` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-10.zip` | `e584fd9d75c24ed6241e6305c255eef32c9d116e513e173f157c5b5bc93f24e9` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-11.zip` | `ea705094112c7fc001c0c94f001271f1c6663f2d1166d1d1ac3b621e50f0610f` |
| `markPriceKlines/2h/SOLUSDT-2h-2023-12.zip` | `3cf0824d1468a982ad5c1940f2dc1241d275e44b56f18d54915b28b7cbb8eb32` |
| `markPriceKlines/30m/SOLUSDT-30m-2020-09.zip` | `0258919195d6c8c23aa8b672c98899f2ae033c218425edbd212cfbea4d1ec433` |
| `markPriceKlines/30m/SOLUSDT-30m-2020-10.zip` | `0d026d47ddc95ceb4c24944059d18b6dcc2bc3d8afc6f05513e5271bdea76184` |
| `markPriceKlines/30m/SOLUSDT-30m-2020-11.zip` | `b302c51d045450b11afc49f40ce6340373cf101578fa14be1d88549590dae279` |
| `markPriceKlines/30m/SOLUSDT-30m-2020-12.zip` | `5c0244472577c6755e2373be44727dbda753b279c9d9cc1029cc87a6d9560e97` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-01.zip` | `38c78221ba46061d163dcb4880d72145fa3e21ad0d2ca59239d8764fb0af8dd4` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-02.zip` | `5ca457454284b335decffeeef1ac553a4cc6a2370e177ac552a18755b406d325` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-03.zip` | `9784c3a54a273132ec357cab3ee6b6554c8ff45dad280278e4b3a616dd1bb782` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-04.zip` | `dced56eec1b75ced18147025c7e1de169bcad52165af255eced50132c5830feb` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-05.zip` | `85798bc6ebfcd1e7bb55f4fe76480299870e21ae5256a8eaa5db5f069ede428f` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-06.zip` | `a9d51aacea504a611381cc7056a0fa4872304da7df415802ee2abed2513f8266` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-07.zip` | `9040edeea54e173518d21aa5237d20f4d2231a6d1a46575c1b1aa2b33fc6cade` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-08.zip` | `f4ca9dcb6260294104e27f3acc3e68d9700270a0a14b07c45f3db882e9cac7d3` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-09.zip` | `d347fd00d59c2ee64f0c8e59e80f09fed6329baa0c4561f2d7f904b8fc1afe25` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-10.zip` | `544abcc3bb7fcb3d38c86d7393e868fcfac91a160d5c3c0b70443ebe57375efe` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-11.zip` | `b61949e0cc292048a9d84455ac30bcfca247731e0a8b563c39b5add06001f943` |
| `markPriceKlines/30m/SOLUSDT-30m-2021-12.zip` | `d8120356e27e2691e1f0997f4963e91395c25657d5227c6b4cd282ca41383ae4` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-01.zip` | `036bae1029ac33dbc96aad95749c49657ebcc68007e2627e382be5bd023d2d93` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-02.zip` | `bacac3b17f852ae63efecddeef468a0a4a8d489f0bb0d52bd2b13aca4fd3fccb` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-03.zip` | `24d43a616fb33ca1e7f5a1265795398b2297da14cae002d1fe625783d1cd1325` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-04.zip` | `3a178cbb7ff419e4285141d376a938aa8b71df7ddf71ef1965805426634a2328` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-05.zip` | `8d740233fb06778e9f4dbe31c1636baa76c71a68bd6ba819d4cc44255225b51b` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-06.zip` | `ebf89e794717cf0eac292c7e2c4342c0a82f9244e804a49f311aa40bd1b470ad` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-07.zip` | `f268633a5e1e82c975094a10688b53c80c266e85498be3be51eccb0e2eb82569` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-08.zip` | `3662d15aa3647c29e9980382b86b1bc46af60cec63d98befba6b300a401ecfd8` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-09.zip` | `8c46e33c67c1aafeefacb108d97e8d68b98e7439bfaffb6cb0b4142076499702` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-10.zip` | `2d84cc6fc9b8446a954cd8544e0a6d5d2e738c1e4211f5197d84b7440f93a813` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-11.zip` | `19397b9e4357a9905e2b6c6ad28332f7d034749ddcc25b0603dcb9b7e4a8160a` |
| `markPriceKlines/30m/SOLUSDT-30m-2022-12.zip` | `35e75302139bacbb5f95451a16a635bbe447bf028d890a08196dcdedf03d6bbe` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-01.zip` | `c49e1b96ac328f6021b5597df4b253b7e74e680781115aa28973b6928cebf0f5` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-02.zip` | `4522793465c00d3e39b2a69ac497d77b1b1eda5d64181e349d8b71e9f72b346e` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-03.zip` | `32d46c72f0317d2ecadbb20d0ee243c6985540c58b6a33a300946a21448b4edd` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-04.zip` | `622c780eaacb0c0c7615d3ff5c6beeef63ce4ef6021d7a4095e50041bea5128d` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-05.zip` | `846f8e0e38746b591576eb585e13ab29d1e937225948da4c7346c7f7e4f3a1dd` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-06.zip` | `a7f883e109499c755c347708a0f57cde558a98676cf02ca5dbbac3b1934cb526` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-07.zip` | `4a2e4c8fd391befd8ca14bc87d9b3c27b91f0335ff474b7f6e771ab56a89f6a1` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-08.zip` | `7d97e6fd0a435ab5c068b7fc5c4b423f5d3adf929da3127d274e6768a520e039` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-09.zip` | `dd38790fee40b3e53e637bcfa468e3a087582798942812b4f8c68e8f75586a64` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-10.zip` | `1247b601788b6ca2d1ebba50a057254a8169edc6ce61d3d30c858682090236b0` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-11.zip` | `809dde4f79244d3beb4d7738155c6ec274222f10af95f502262f3f604968216c` |
| `markPriceKlines/30m/SOLUSDT-30m-2023-12.zip` | `8d3b8a11f997f8d1f8edf950a491469453d83e22a1530233ba90bf45b4ba81b1` |
| `markPriceKlines/4h/SOLUSDT-4h-2020-09.zip` | `c3864fee9ff226c9672ce5df103319132fbf0b741d1403c937b8decfa448c6c1` |
| `markPriceKlines/4h/SOLUSDT-4h-2020-10.zip` | `bb73b16a91c2eb7a693539e60b3b2a058b9f52b8f2562f48f5a2d56321043f3e` |
| `markPriceKlines/4h/SOLUSDT-4h-2020-11.zip` | `7c77b957251c99fd91b1b9efcced74a9ead695a642f3989e7f44637ff9c10e2f` |
| `markPriceKlines/4h/SOLUSDT-4h-2020-12.zip` | `ef777b2f091fde6cc564afad491b4dbc4cfa7d2caf5bc34a0685574ad446146b` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-01.zip` | `9d55d2297c68a2669c2c8e71f81063faebccacb412654f1cf6b9a8a255bc935a` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-02.zip` | `d87ad80ee6fa825632ddc38caedb782d16bea15493688b24c057d52713c1c0ff` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-03.zip` | `ef7c1cb5286feb72501698b549de98d4264b079d55d7f465269a6fdbac6f8599` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-04.zip` | `b103f432c211ff33aa4f89949ec454d77b72b4e2b1a8466a170a08f533a0d031` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-05.zip` | `c6e2d2c20368a3d7daf76e36dd8a3a134591b68a64e5d8b3954797c4794aa947` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-06.zip` | `00ae5205f5a087fb8e74ca1ba2d134189ad334bc964dc3908374f168be0d7293` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-07.zip` | `f15c537e328102f8a2c7bf5e2cc84559a6c3d249ec67c1b3ebd08c378dbd3687` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-08.zip` | `da344db2aaaa1ca635de449e49f0ca394c397af66ec691ed44897616c5cd87bb` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-09.zip` | `fc72be7ad9e19c245357c17cb2ff702b25fcec6fa241ddce541752691e2cd0f4` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-10.zip` | `0845fd1f987a0a8db5b48fc864dfc8d8fd91468e8c4c8e2836f4f0b43e1c6c91` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-11.zip` | `0fd35813a93f1c967db15c507aa5eb18127e03a174f2321637effa4e315a97cc` |
| `markPriceKlines/4h/SOLUSDT-4h-2021-12.zip` | `deb509daeb988eab79d5e7fd978efeb3e765b41b7c55b6f9a77eac2bdac4b173` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-01.zip` | `68026abb1dbbfc7584776a1ce9ed521d06fa8748706db546366b2ccbf3d4a4a3` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-02.zip` | `f50908a9857f9d424ab032e0c699cfcefa1dd655c3b4d3c94e6d7eb76456904d` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-03.zip` | `5ba1a015f47f0b1ee01dce93191f208b39fb6b03c7f7c58af5ce4afdcb822c1c` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-04.zip` | `b4cda037c4ddb80e7e23a9b4f051b2c749aa818750f0ed304d9c665d6e5101bf` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-05.zip` | `4cc8ecca11789318bbdf0e42836a6c9c02ca34d2f1b187a874280e2e558cae12` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-06.zip` | `d3a18ae463c6092f9308bc815f844e0ff630b0f5e01c2aef30110c74418f79d5` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-07.zip` | `91f0bdf0b50570595dbb0bae07f30bef7f3ba0df6e5d1bee375b40a559927d0c` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-08.zip` | `9464d3cdd3ec5f8483e4d1667876ddcb942f6ed4304a486ca060f11acdfd99a6` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-09.zip` | `06e53740b51065c3b1fbb49ddd90bb76d2252fd3e59e2fad2a315acf84b5a7c0` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-10.zip` | `4d959ebd623a943ddeea10eabc34fa8ddaeeae9246b238f9dc74917e46b44bff` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-11.zip` | `c2216e728e7b308a9f64a0dfe7a3a6619927b8cfcb57e38879d4f99fc806a2fa` |
| `markPriceKlines/4h/SOLUSDT-4h-2022-12.zip` | `ff353469115afe2fd41c71f4304cc70a11f9b5220250b490d10f98a99da508a1` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-01.zip` | `3aa982887c3f5339a04ea607b211ee02770122d2521a637346da95e747e42d8f` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-02.zip` | `b8d88f31f839daafc3eb52c0d8f5300fbcaa4a37de0c2aa3314af7241666c6a4` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-03.zip` | `a6b13e869dc826fd659e606d91e897ed0bccb68b8e251606475a97db47edf2a1` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-04.zip` | `428f81e33dfba72ba33d8542b6b5f3f04ab477a309dcdf3fdc2874f2ad5f0489` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-05.zip` | `8b6ecf418c372655a589ca3f1474299ca72e07cc5876e3b99e0b13b2c2d49b4c` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-06.zip` | `77ab9399238f9c23c4857a3037edab5522c0e4b9c704b1ea0b7d3d7894b53913` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-07.zip` | `c2c979241612076c44b57a668336fcbcfe6433606ba5adc50511ef6c41f2e6d2` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-08.zip` | `26cd251017feefcf7ffd5d3d8778a8717e626156c8bb9e5dd3bcedb828cfa29c` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-09.zip` | `31c7c8dbb5c9d61cc6123cf8d6b1d87f4e19cf51d0546279fce446a1cac501a2` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-10.zip` | `9ae878003cba1bbc274b5ed85f33730acc842d70a3ea009c685c122c67ac5813` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-11.zip` | `4f1dadbeafffb4a4650979f593c29fc7e9d6dbd50ecd52a094fee7c045c4e79d` |
| `markPriceKlines/4h/SOLUSDT-4h-2023-12.zip` | `1f895467c9fd2bfac32d5ae6b399baa7aa8d024de85696d8254cce83a7d35dce` |
| `markPriceKlines/6h/SOLUSDT-6h-2020-09.zip` | `24d4358e6e5ab0e75c316cec11656298a9de6ec0f77546e4199971f94c684185` |
| `markPriceKlines/6h/SOLUSDT-6h-2020-10.zip` | `4f3045150e8eabfbfd19c6fe51aa544e492caccf6d6e97ef51788c681baa523f` |
| `markPriceKlines/6h/SOLUSDT-6h-2020-11.zip` | `ec89a41a7b967c699337f7db1065910c3c6bf96b377118caaf795c14fe44ca67` |
| `markPriceKlines/6h/SOLUSDT-6h-2020-12.zip` | `7a32b45336170a3fa406f082de4c7f3c6c7abafba77ac11622ab596c200242d7` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-01.zip` | `82df1151d45bbc9cd2dfe6ae3916e37cd0971b77a21d46e9a38b70a77133e6ec` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-02.zip` | `b1016bd4237165ae7748cf743681d8b59220cd766c60748caadfd8c2c197fbf1` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-03.zip` | `48144e51f3c9aaee8d0ee5166e097a65fc5299f96a2b5c8671abd8465c754a5b` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-04.zip` | `b4aa513e3acb509cbba882f575ec92cc8be3ffd69f0571fa20349d058a7cef3e` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-05.zip` | `5926f01b62efed64835fb51c0b3a6be78d4001451b19271616b5bedbf2c6f346` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-06.zip` | `0ba9e9eaefd15e262ab8871746a352d90cc3575a72326e7233244f582f739fbd` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-07.zip` | `b0d7f06618add53ae4516cb080816f73814bc86f421ea3e030d1730521597a7e` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-08.zip` | `86efff50da542a66147b4830a08f570228aa59734ac5a116aaa3e0782b6d8751` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-09.zip` | `67b6139b8033a261ff519bf02cc49809c4d67c2c19f33269863eb965b05c4b13` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-10.zip` | `d0b3dc2b3e27b4530e39ab8dc3585500a7ec848d21b11b70c2574f187130f927` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-11.zip` | `1d69ca1b729ee096c24d31be0991911bb90250930504a83ab2b3fd6954e162bd` |
| `markPriceKlines/6h/SOLUSDT-6h-2021-12.zip` | `6b94d68fde25bab72dcdf7b066ed28563b4f3dd3fd2746f8e44c0091363afa2e` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-01.zip` | `ab3f385907add6989c528a65b462b2dd96b0ccb19ff2d1d39102c471caf55f45` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-02.zip` | `07467b5a72dbe4a14649c9211774b3ea0c4e07cbf4efe9ced2ee77cc8ab41beb` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-03.zip` | `93dc72a87cf1d4b91b6f447096936d6f75fcffac061466f9ddb1c8c176327b5b` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-04.zip` | `ce676c366a279c22cca284555a6bb22fa72428c8049cf8b0ee6b1c33b33808ea` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-05.zip` | `ccf04cab8917b9696bf95db36f627c6a3bea2db6aa382f7bed012a5254f43c00` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-06.zip` | `e13e2e9a23ae6086863eb4fdfb67a5349e4898696033684448b748a98a6e0a95` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-07.zip` | `c1970ad7fb9955f6a30ca0da46525c048d6b196f19cbf6d04a752e72cb8b7fad` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-08.zip` | `9f48d5ef0a8219bcacbcba2ed526818be0bd889f6fc81247d8e81a146bf91420` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-09.zip` | `ed0eaf5c80d9e9cfa2014134f696b90f83112f65041f7b9207c0b636c4d1d784` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-10.zip` | `2264ca19179cccfe460497af5dfef30b879b196199d8dde9b3a04d647c1dae6d` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-11.zip` | `db1664d8c6fe6931ec6cc30c36c8bb9578c832360fe4d3a9c342a64622dbdfaa` |
| `markPriceKlines/6h/SOLUSDT-6h-2022-12.zip` | `ecd3b5c58cbc87488860be509f405990582fff9ccd77a7311abdc8261274e7b7` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-01.zip` | `a55fe3f633250c80a27b409da0cc7b6a4f5ef7d67f88bef31f595d64c6dd7b05` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-02.zip` | `0fe1ba7920cb25d4dd730653e1df66c83019dc7784775008a0d7bd5ac2846eac` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-03.zip` | `cc18e64b7fe2e376ca026ccc2ea47b9e981d87632b14d79ff90195943dd860e5` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-04.zip` | `25ff42d8a531a2a36451e0cfa007062a5bdbf6c29c044e34f06ed821ecd6a187` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-05.zip` | `9e4167a46bc2bd7712c2f6af27f611a81e344c32126c32b5173ca1fe5c49a24c` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-06.zip` | `477b31cbc3df1eb19b59838146821e369483399bffc22447b730671e175bec5a` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-07.zip` | `e19194270d98e77d715ff4b57f2d06d2fc0e0e840e96ebf5b4857c512cdcacf7` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-08.zip` | `e489d9fba30ee19b900e5fa63224dcfc03a941520c87e027202c341c85bae85d` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-09.zip` | `b369cec055df70b0a3037819a4746a2032510062668fef2485df723a96af1d48` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-10.zip` | `dc90b95510108d865e25991045f36310682f08c9c1f075b3c9a68ff234268c78` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-11.zip` | `656aec195fc2f637c00a0aef0d41156a4238bf4e9d9b0ecc0aac4416440af2ec` |
| `markPriceKlines/6h/SOLUSDT-6h-2023-12.zip` | `e0acedfcbe7219cd80390674e8a87be9590a5abb42beb4fd303807652be75f94` |
| `markPriceKlines/8h/SOLUSDT-8h-2020-09.zip` | `62c938708efd9af151b0097ea16751733e6e8d3884c9285d60290b1c925ea298` |
| `markPriceKlines/8h/SOLUSDT-8h-2020-10.zip` | `7f9703ac54803b75fc65035d0f9ffc65848408a0ed3f89e1a32319c7e5a750f9` |
| `markPriceKlines/8h/SOLUSDT-8h-2020-11.zip` | `1e4ceb977fac5d9ccf6b3ae309057344219f612d4cebaf20f2b61faf03fba849` |
| `markPriceKlines/8h/SOLUSDT-8h-2020-12.zip` | `2d7a6a8b368cdce49089ca37e026d4a5f4aeb5ae6be567c10ee59e524a793049` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-01.zip` | `a066a338bb4d2bf869ddd639a7b50c68450739988960586539ac4abb98775c69` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-02.zip` | `377d9ea283ce4be91397e21c2af11b83ea1ca053497771e013a4bbfa5b0957e1` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-03.zip` | `a2fdb390dcbb0c499c8bd3f22c669a06b30f295ebcfa7af6a7eee1c1cd9d2a9a` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-04.zip` | `7d2365bb979a7b79d463e7a5e7823d9da4e5b253c6aa8e5beb44c1b40f88dfd3` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-05.zip` | `36de06848ff67adb1ea811bdff2a4bf04631e465f2aa5a53c34cee2dcd5898b4` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-06.zip` | `6b3b0e0295baa7b40f1e2d7e71d4f294cb89023f0bbfca325f724edaba4a1e5d` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-07.zip` | `cdfc3c0cd44586e9e00d91fe35a7e5ed5726da035de1b179b74730755a9e586f` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-08.zip` | `eeec9be602e107cb4e6246c0f6f0b667cee758f5d4fe806c495612f0f5f556a1` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-09.zip` | `c65bb17e25e6dc6b08851ef72baab8c523ecc94873b4559bf5a1b789de229072` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-10.zip` | `1ab3f472f5b1879be82fc5360133f463da667329e671096b99ca5a31fab28ee0` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-11.zip` | `c61b2092a0b7dc18461939d821a1f6d80c5a1bd9ee1fcff91df082698fb0f509` |
| `markPriceKlines/8h/SOLUSDT-8h-2021-12.zip` | `7871330dcf9a867c4c9a80e48fa209fba874a4f73db6369de951be16cd71045b` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-01.zip` | `1667e905e0655a31d89a9a8ff40aa6b32ba2c9f43ab5627c7e3b4bd8a83a61a3` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-02.zip` | `52cbfc7981141bb58c8d9a04bf5dd7a107db88d160ed1a00bf63ee7a38de23db` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-03.zip` | `21612cfc014b71228d1339da8c635b901cbaf979ce05e319d51896a78dec74e7` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-04.zip` | `db67092b4b66f4228110976fdc1a58aff3fdfab48af6dacd9be86e65e0aa15f8` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-05.zip` | `4ea2ea28fce55a8f1b0700fa6dcb4af86fa07b37bc839f7c461fd773079c34a8` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-06.zip` | `80a0234c27b5584686e136ed658667f94db5e9a9867bc7640e7d9b48372e80dd` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-07.zip` | `52b9396e57772c818a6839f5f14bc50738493ff463c98ac809fccb204b269f72` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-08.zip` | `b1a99abec46bc80679c3d85753bb4e01c1a2178d9b575e2a9cd8b2dcacdfa051` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-09.zip` | `d917e3ee26110000fdd6943a0a692571d3261cf7edca2d18ea063cc921cce88f` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-10.zip` | `ebb04e79133e425527f30ad2f9fbc0ada3459bb9d4d502e22f95e65ae58adb27` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-11.zip` | `a9c697358ba0ac8eb1732822c630abb6c19c00a6efb317036d16151a185b6232` |
| `markPriceKlines/8h/SOLUSDT-8h-2022-12.zip` | `14e98f469cbfb1894c1fa1722ce93bd2606d339a240f1ddc529b4267bea1e96c` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-01.zip` | `a6fc9da89215dcad1ea6d06254d260848230de50586a4df396627e623b427af5` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-02.zip` | `20f576e40d4ead9a543c82c31e083511e43e125bcb4186fff1ceb4238b3d2a7e` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-03.zip` | `cda1e17d59ac2c1c1a6ab40b5b4005639b8a1ac2421a6621a429e1ff7577ab87` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-04.zip` | `1afe1a404930b963d5b5b40a533b599a6b3f784ed73264f6c1bd1d4b10d5446b` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-05.zip` | `551c73ccf7b219e0f6799de6d2ffb9e91891b4ce1f6563b0869f0770613fb5ec` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-06.zip` | `7ff06c10d32b8fa8058ae74cdaa6920e7d1e007c039132339d0820790cd7821f` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-07.zip` | `830d6357ab7c4da57fd0f766d0dee9dd2410a106464fbdab8980363280044c5e` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-08.zip` | `653460c94066e26f38db10c2b7f7b6542ae7ece122b1f5468940dea8fc5a2c96` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-09.zip` | `4c8823de5ac2526ed645a14a3660cd14b220eb51b337846bf90ab7043d527eba` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-10.zip` | `13b15388583b64938481c9eb02374ae29a0b435c47b8fb43e5048f344085282a` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-11.zip` | `84710bede532a2ee0e879f3e82a4e566377317bc1d3d5dec148d44c996c8a938` |
| `markPriceKlines/8h/SOLUSDT-8h-2023-12.zip` | `8848363c9980755643fae0990db5aa5134ad39d82b5f5159bc5e0c8dbfdef37c` |
