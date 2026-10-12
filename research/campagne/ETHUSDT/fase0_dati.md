# ETHUSDT — Fase 0: i dati della moneta

Scritto l'8 ottobre 2026 dalla sessione di campagna (protocollo 4.4). Tutti i numeri
vengono da `codice/fase0.py`, che legge solo i file in-sample gia' scaricati (fino al
2023-12-31); l'uscita completa e' in `data/insample/ETHUSDT/lavoro/fase0.json` (fuori da
git, si rifa' con lo script).

## Periodi (scritti nel log prima di caricare i prezzi, voce ETHUSDT-N002)

| | Dal | Al | Giorni |
|---|---|---|---|
| In-sample | 2020-01-01 | 2023-12-31 | 1461 |
| Costruzione | 2020-01-01 | 2022-10-18 (23:59:59.999 UTC, `fine_costruzione_ts` = 1666137599999) | 1022 |
| Validazione | 2022-10-19 | 2023-12-31 | 439 |

Fonte: `periodi_campagna(date(2020, 1, 1))` di `src/dati.py`, con il primo mese di dati
della scheda. La validazione gira sulla serie dal 2020-01-01 al 2023-12-31 (indicatori
caldi) e conta solo i trade entrati dal 2022-10-19 00:00 UTC.

## Cosa e' stato scaricato

Da data.binance.vision (file mensili USDS-M), mesi dal 2020-01 al 2023-12, con
`scarica_mese` di `src/dati.py` (blocco del vault e confronto con il CHECKSUM pubblicato):

* ETHUSDT, candele last price (klines) su 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d: 432 file;
* ETHUSDT, candele mark price (markPriceKlines) sugli stessi timeframe: 432 file;
* ETHUSDT, funding (fundingRate): 48 file;
* BTCUSDT, candele last price sugli stessi timeframe, solo come riferimento di mercato: 432 file.

1344 file richiesti, 1344 presenti, nessun mese assente. Ogni file e' stato poi
ricontrollato contro il CHECKSUM remoto: 1344 su 1344 uguali, nessun CHECKSUM mancante.
Gli URL si costruiscono mese per mese: nessun elenco remoto e' stato letto, e nessun file
oltre il 2023-12 e' stato chiesto.

La serie su cui scatta lo stop e' il last price (`serie_stop` di `parametri.yaml`): per
gli stop non serve una serie a parte.

## Impronte

Le impronte SHA-256 di ogni zip (912 di ETHUSDT, 432 di BTCUSDT) stanno in
`impronte.json`, accanto a questo file. L'impronta di `impronte.json` e':

`7bd946cf24a2774dc5db63bceae0960af5f9e582a439d20ab43a6ac7ef673ab0`

A ogni nuova sessione i dati si riscaricano e si confrontano con `verifica_impronte`: se
una impronta cambia, STOP (sezione 5).

## Buchi nei dati

* **Last price**: nessun buco su nessun timeframe (15m: 140.256 barre su 140.256 attese;
  1d: 1461 su 1461).
* **Mark price**: due giorni interi mancanti, uguali su tutti i timeframe: **2022-10-02**
  (in costruzione) e **2023-02-24** (in validazione). In piu' a 15 minuti mancano due barre
  singole: 2020-01-19 13:15 e 2023-11-10 03:45 UTC.
* Nessuna barra ha il mark senza il last.

**Scelta (scritta prima di ogni test, uguale per tutte le varianti):** il motore vuole le
serie allineate barra per barra, quindi si tengono solo le barre presenti sia nel last sia
nel mark (`carica` di `codice/comune.py`). Barre tolte dal last per timeframe: 15m 194,
30m 96, 1h 48, 2h 24, 4h 12, 6h 8, 8h 6, 12h 4, 1d 2. I buchi che restano li conta il
motore (`n_buchi_dati`), e il funding caduto in un buco con posizione aperta si addebita
sull'ultimo mark disponibile (regola del motore).

## Sospensioni e cambi di contratto

Nessun cambio di contratto: il simbolo e' `ETHUSDT` per tutto l'in-sample, e nessuna
chiusura giornaliera differisce di oltre il 50% da quella del giorno prima (controllo per
ridenominazioni o riscalature). Le sole interruzioni visibili sono i due giorni senza mark
price qui sopra; il last price non ha interruzioni. Nessun punto di cucitura.

## Funding

* 4383 settlement dal 2020-01-01 00:00 al 2023-12-31 16:00 UTC, uno ogni 8 ore per tutto
  il periodo: tutte le 4382 distanze fra settlement consecutivi sono 8 ore, e la colonna
  dell'intervallo (quando c'e') dice 8. Nessun buco nel funding.
* Tasso medio per settlement: 2020 0,0250%; 2021 0,0343%; 2022 0,0007%; 2023 0,0075%.
  Quota di settlement positivi: 2020 97%, 2021 96%, 2022 66%, 2023 91%. Minimo e massimo:
  2020 da -0,282% a +0,367%; 2021 da -0,356% a +0,375%; 2022 da -0,302% a +0,010%;
  2023 da -0,017% a +0,071%.

## Volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere)

| Anno | Volume medio giornaliero |
|---|---|
| 2020 | 0,72 miliardi |
| 2021 | 7,60 miliardi |
| 2022 | 7,58 miliardi |
| 2023 | 5,51 miliardi |

Mese piu' basso: gennaio 2020, 112 milioni al giorno. Il volume per mese e' in
`fase0.json`.

## Mesi sotto la liquidita' minima (20 milioni di USDT al giorno)

**Nessuno.** Il filtro dei mesi esclusi esiste nel codice comune (`MESI_ESCLUSI`, uguale per
`conta_trade`, per il test, per la (a) e per le barre vietate della (b)), ma e' vuoto. Le
date di costruzione e validazione non cambiano.

## Storia utile

Quattro anni di in-sample (2020-2023), sopra `storia_minima_anni` (2): la campagna si fa.

## Avvertenze sui dati (da tenere presenti nei risultati)

* **Slippage del 2020 probabilmente ottimista.** La fascia della scheda (0,01% per lato)
  viene dal volume del 2023 (5,5 miliardi al giorno). Nel 2020 il volume medio era 0,72
  miliardi, che con le fasce del protocollo varrebbe 0,02%, e a gennaio 2020 (112 milioni)
  0,05%. Il 2020 e' circa un terzo del periodo di costruzione: i risultati di quell'anno
  sono un po' troppo favorevoli, e la prova a costi doppi copre solo in parte.
* Il funding del 2020 e del 2021 e' quasi sempre positivo (i long pagano): pesa sulle
  varianti long che restano aperte a lungo e aiuta le short. Il motore lo conta al
  settlement con il tasso vero.
