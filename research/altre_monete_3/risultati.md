# Prova su altre monete del protocollo 3: V-020 della campagna BTC51 (Passo 6)

Scritto dal coordinamento il 17 ottobre 2026, sul branch principale, dopo l'unica esecuzione
(`python3 research/altre_monete_3/passo6_btc51.py esegui`; ora d'inizio in `giro_iniziato.json`, esiti completi e
trade uno per uno in `esito.json`). Il sì del proprietario: «ok sì, fai la prova sulle altre monete». Questa prova
serve a capire se l'idea vale fuori da BTC: non cambia l'esito del vault (V-020 l'ha già fallito,
`research/vault/BTC51_risultati.md`).

## Esito: V-020 NON si trasferisce

Regge su **1 moneta su 9** (LTCUSDT); per trasferirsi ne servivano almeno 3, contate dopo l'unione di quelle con
correlazione sopra 0,5. Il protocollo lo dice così (sezione 14): «Con p-value 0,10, per caso si attende meno di 1
moneta su 9»; una moneta sola è compatibile con il caso.

## Le monete (scelte solo con i dati del 2023)

Le 9 con il volume in USDT più alto nel 2023 fra i contratti perpetui in USDT di Binance, escluso BTCUSDT
(`selezione.json`, commit 4d32d6ee, scritto prima di scaricare i dati del vault di queste monete):

| Moneta | Volume medio giornaliero 2023 (milioni di USDT) | Giorni nel 2023 | Slippage per lato |
|---|---|---|---|
| ETHUSDT | 5.513 | 365 | 0,01% |
| SOLUSDT | 1.104 | 365 | 0,01% |
| XRPUSDT | 811 | 365 | 0,02% |
| DOGEUSDT | 519 | 365 | 0,02% |
| APTUSDT | 410 | 365 | 0,02% |
| BNBUSDT | 401 | 365 | 0,02% |
| LTCUSDT | 382 | 365 | 0,02% |
| MATICUSDT (delistata nel 2024) | 374 | 365 | 0,02% |
| BCHUSDT | 339 | 365 | 0,02% |

Seguono OPUSDT 330, ARBUSDT 324 e LINKUSDT 319.

Due cose trovate e decise prima dell'esecuzione (scelte scritte nel programma, commit 4d32d6ee e a593f3b4):

1. **La tabella dei volumi del 7 ottobre era incompleta per questo uso.** `research/universo/candidate.csv`
   calcolava il volume 2023 solo per i contratti quotati prima del 2022 (il filtro del protocollo 1). Gli altri 127
   contratti con dati nel 2023 (APT, ARB, OP, PEPE, ORDI…) sono stati calcolati ora dalle candele giornaliere del
   2023, con il CHECKSUM di Binance. APT entra fra le 9 e LINK esce.
2. **«Volume medio giornaliero nel 2023» = volume di tutto il 2023 diviso 365.** La media sui soli giorni in cui il
   contratto esisteva avrebbe messo fra le prime 9 contratti quotati a fine 2023, con 20-68 giorni di vita nell'anno
   (ORDI, 1000SATS, GAS, TIA, 1000BONK). Con la regola del 7 ottobre (almeno 350 giorni di dati nel 2023) le 9
   sarebbero le stesse di questa scelta.
3. **MATICUSDT smette di scambiare il 4 settembre 2024 alle 08:00 UTC** (passaggio da MATIC a POL). Dopo, l'archivio
   ha altre 169 candele orarie a prezzo fermo e volume zero, e candele mark e funding fino al 2026-09 senza scambi. La
   serie finisce all'ultima candela con scambi: lì si chiude la posizione aperta e il test finisce (punto 3 del
   Passo 6).

Altre scelte: serie caricata dal 2023-12-01 per avere l'ATR(14) già calcolato al 2024-01-01; decisioni solo dal
2024-01-01 00:00; regole del motore come nel vault di BTC (leva 2, rischio 1%); commissioni come per BTC; funding
vero della moneta; entrate casuali come in BTC (1.000, seme 2026, stessa larghezza di stop). Dati: candele last e
mark a 1h e funding, 34 mesi per serie (2023-12 → 2026-09; MATICUSDT 10 mesi di candele last), tutti con il
CHECKSUM verificato. Su ogni moneta tranne MATICUSDT manca il mark per un giorno (2026-06-29, come per BTC),
sostituito dal last (sezione 9.6).

## Risultati per moneta (periodo del vault, 2024-01-01 → 2026-09-30)

Condizioni del punto 4: almeno 100 trade, R medio positivo, profit factor almeno 1,10, p-value contro le entrate
casuali 0,10 o meno.

| Moneta | Trade | Al mese | R medio | Profit factor | Vincenti | Drawdown | p-value | R medio delle casuali | Regge |
|---|---|---|---|---|---|---|---|---|---|
| ETHUSDT | 217 | 6,6 | −0,033 | 0,94 | 41,9% | −22,2 R | 0,466 | −0,036 | no |
| SOLUSDT | 393 | 11,9 | −0,120 | 0,80 | 37,7% | −58,2 R | 0,906 | −0,048 | no |
| XRPUSDT | 341 | 10,3 | −0,085 | 0,85 | 37,0% | −46,7 R | 0,588 | −0,070 | no |
| DOGEUSDT | 307 | 9,3 | −0,064 | 0,89 | 39,4% | −32,8 R | 0,552 | −0,055 | no |
| APTUSDT | 405 | 12,3 | −0,086 | 0,85 | 38,8% | −45,3 R | 0,302 | −0,114 | no |
| BNBUSDT | 167 | 5,1 | −0,020 | 0,96 | 41,3% | −12,7 R | 0,318 | −0,063 | no |
| **LTCUSDT** | 242 | 7,3 | **+0,062** | **1,12** | 44,6% | −24,0 R | **0,020** | −0,098 | **sì** |
| BCHUSDT | 489 | 14,8 | −0,018 | 0,97 | 38,9% | −58,7 R | 0,166 | −0,070 | no |
| *(BTCUSDT, vault)* | *180* | *5,5* | *−0,007* | *0,99* | *36,7%* | *−21,8 R* | *0,337* | *−0,047* | *no* |

Nessuna violazione di liquidazione su nessuna moneta.

### Moneta delistata (separata)

| Moneta | Periodo | Trade | R medio | Profit factor | p-value | Regge |
|---|---|---|---|---|---|---|
| MATICUSDT | 2024-01-01 → 2024-09-04 08:00 | 35 | −0,333 | 0,51 | 0,808 | no (meno di 100 trade) |

### R medio a trade per anno (trade per anno fra parentesi)

| Moneta | 2024 | 2025 | 2026 (gen-set) |
|---|---|---|---|
| ETHUSDT | +0,254 (22) | −0,186 (97) | +0,054 (98) |
| SOLUSDT | −0,011 (58) | −0,041 (173) | −0,245 (162) |
| XRPUSDT | +0,099 (47) | −0,020 (140) | −0,200 (154) |
| DOGEUSDT | +0,094 (59) | −0,025 (129) | −0,186 (119) |
| APTUSDT | +0,096 (47) | −0,069 (189) | −0,155 (169) |
| BNBUSDT | +0,050 (86) | −0,115 (75) | +0,151 (6) |
| LTCUSDT | +0,471 (27) | +0,111 (105) | −0,086 (110) |
| BCHUSDT | +0,125 (167) | +0,062 (174) | −0,275 (148) |
| *BTCUSDT* | *+0,331 (33)* | *+0,005 (63)* | *−0,150 (84)* |

Fonte: i trade dell'esecuzione unica (`esito.json`; BTC da `research/vault/BTC51_vault.json`).

## Correlazioni (punto 5)

Rendimento giornaliero = somma degli R dei trade chiusi nel giorno UTC, zero nei giorni senza chiusure.
Correlazione fra le 36 coppie: media 0,26, massima 0,44 (SOL-XRP), minima 0,05; nessuna sopra 0,5. Con una sola
moneta che regge non c'è niente da unire: 1 gruppo indipendente.

## Cosa si vede (osservato)

1. **L'idea perde quasi ovunque nel periodo del vault:** R medio negativo su 7 monete su 8 con il periodo intero, e
   sulla delistata. Solo LTC resta positiva, e anche lì il 2026 è negativo (−0,086 su 110 trade).
2. **Sulle altre monete il funding è sotto zero molto più spesso che su BTC:** da 5 a 15 trade al mese contro 5,5
   (BCH 14,8, APT 12,3, SOL 11,9). Più segnali non vuol dire più guadagno: le monete con più trade sono fra le
   peggiori.
3. **Il 2026 è negativo su 6 monete su 8, come su BTC**; il 2024 è positivo su 7 su 8. Lo stesso andamento su monete
   diverse, con correlazioni dei rendimenti basse (media 0,26), fa pensare a un cambiamento del mercato più che al
   caso di una moneta.
4. **Il confronto con le entrate casuali:** su 5 monete su 8 V-020 fa meglio delle sue entrate casuali (ETH, APT,
   BNB, LTC, BCH), ma tranne LTC perdono tutte e due dopo i costi; su SOL, XRP e DOGE fa peggio. Solo su LTC la
   differenza è grande (+0,062 contro −0,098, p 0,020).

Lettura (inferita, non dimostrata): la logica «funding negativo = short affollati da spremere entro 24 ore» non
regge come regola generale nel 2024-2026. Il risultato di LTC, da solo, non basta a dire il contrario.

## Prossimo passo (STOP)

Il Passo 6 finisce con lo STOP: decide il proprietario. Resta il Passo 9 (chiusura): `lezioni.md` della campagna
(errori di metodo, trappole dei dati, idee provate e cosa ne è stato, cosa cambiare nel prossimo protocollo) e
`STATO.md`.
