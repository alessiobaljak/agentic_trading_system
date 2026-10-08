# SOLUSDT — Fase 0: i dati

Tutti i numeri vengono da `codice/fase0.py` (eseguito l'8 ott 2026) sui file mensili di
data.binance.vision fino al 2023-12, scaricati con `src/dati.py` (`codice/scarica.py`).

## Date (scritte nel log prima di caricare i prezzi: voce SOLUSDT-N002)

| | Valore |
|---|---|
| Primo mese di dati (scheda) | 2020-09-01 |
| Giorni fino al 2023-12-31 | 1217 |
| Costruzione | 2020-09-01 → 2022-12-30 (851 giorni), fine `1672444799999` ms |
| Validazione | 2022-12-31 → 2023-12-31 (366 giorni) |

La prima candela last price del file è del **2020-09-14 07:00 UTC** (il mark comincia il
2020-09-13 11:45): i primi 13 giorni di settembre non hanno dati. Le date non si spostano.

## Fonte e integrità

* Scaricati: klines 15m e 1d, markPriceKlines 15m, fundingRate di SOLUSDT (2020-09 → 2023-12,
  40 file per tipo); klines 15m e 1d di BTCUSDT (2020-01 → 2023-12, 48 file per tipo), solo come
  riferimento di mercato.
* Ogni file ha avuto il controllo col CHECKSUM remoto: **nessun file senza CHECKSUM**.
* Impronte SHA-256: `impronte.json` (160 file di SOLUSDT, impronta del file
  `457be740fd8eb2d65c5114959b0569254a8c03cb123b05a738435e8923f8e654`) e
  `impronte_btcusdt.json` (96 file, impronta
  `30ad54d1eaf231bfb1717ad5aaa189c04dedcff6ab941530888668a6b481c8a9`). A ogni nuova sessione si
  riscarica e si confronta con `verifica_impronte`: se cambia, STOP.

## Buchi

| Serie (15m) | Barre | Buchi | Barre mancanti |
|---|---|---|---|
| last price | 115.076 | 2: 2022-02-26 (3 giorni, 288 barre), 2022-04-01 (2 giorni, 192 barre) | 480 |
| mark price | 114.960 | 5: 2021-07-01 (1 giorno), 2021-07-24 (4 giorni), 2022-10-02 (1 giorno), 2023-02-24 (1 giorno), 2023-11-10 03:45 (1 barra) | 673 |
| BTCUSDT last | 140.256 | nessuno | 0 |

I buchi del last coincidono con giorni mancanti anche nelle candele 1d (febbraio 2022: 25 giorni;
aprile 2022: 28): sono buchi dell'archivio, non sospensioni note. Nessuna candela incoerente
(high sotto open/close, low sopra, prezzi non positivi) né nel last né nel mark.

**Scelta (lezione di metodo «il mark ha buchi che il last non ha»), fissata qui prima di ogni
test:** il motore usa l'INTERSEZIONE delle barre a 15 minuti di last e mark. Tolte 673 barre dal
last (i giorni dei buchi del mark: 2021-07-01, 2021-07-24…27, 2022-10-02, 2023-02-24, una barra
del 2023-11-10) e 557 dal mark (le barre senza last). I timeframe da 30m a 1d si costruiscono da
queste barre a 15 minuti con `aggrega_candele` (solo gruppi completi): una candela di 1h, 4h o 1d
che cade in un buco non esiste, e il motore conta il buco. Lo stop scatta sul last
(`serie_stop` di `parametri.yaml`), la liquidazione sul mark.

## Cambi di contratto e sospensioni

Nessun cambio di contratto nell'in-sample: un solo simbolo, `SOLUSDT`, dalla prima all'ultima
candela. Nessuna sospensione dichiarata dalla fonte oltre ai buchi sopra.

## Funding

* 3.688 settlement dal 2020-09-13 16:00 al 2023-12-31 16:00.
* Intervallo dichiarato dai file: 8 ore, salvo dal 2022-11-09 al 2022-11-18 (4 ore, poi 2 ore,
  poi di nuovo 8 dal 2022-11-18 16:00). Distanze fra settlement: 3.586 di 8 ore, 3 di 4 ore, 98 di
  2 ore. Il motore usa i settlement veri, quindi l'intervallo variabile è già dentro.
* Tasso medio −0,0032% a settlement; minimo −2,0000%, massimo +0,3325%. Il periodo a 2 ore
  di novembre 2022 ha tassi molto negativi: gli short in quei giorni pagano molto.

## Volume (colonna `quote_volume` delle candele 1d, in USDT)

| Anno | Volume medio giornaliero | Giorni |
|---|---|---|
| 2020 (da set) | 16 milioni | 109 |
| 2021 | 1.075 milioni | 365 |
| 2022 | 982 milioni | 360 |
| 2023 | 1.104 milioni | 365 |

Mesi sotto `liquidita_minima_usdt_giorno` (20 milioni): **2020-09 (16,5), 2020-10 (12,5),
2020-12 (14,8)**. Il 2020-11 (21,8) è sopra. Da gennaio 2021 nessun mese è sotto i 70 milioni.

**Filtro (uguale per `conta_trade`, test e baseline (a)):** nessun ingresso su segnali di barre
che aprono in quei tre mesi (il mese è quello dell'apertura della barra di segnale); una posizione
già aperta esce con la sua uscita. Le stesse barre vanno fra le `barre_vietate` della (b). Le date
di costruzione e validazione non si spostano: in pratica la costruzione utile è novembre 2020 più
gennaio 2021 → 30 dicembre 2022 (circa 2,1 anni), contro gli 851 giorni nominali.

**Slippage.** La fascia della scheda (0,01% per lato) viene dal volume del 2023 (1.104 milioni al
giorno). Nel 2020 il volume era 16 milioni al giorno e nei primi mesi del 2021 tra 70 e 600
milioni: per quei mesi 0,01% è ottimista (la fascia sarebbe stata 0,05%–0,10%). Lo copre solo in
parte il test a costi doppi; si dichiara.

## Storia utile

Dal 2020-09-14 al 2023-12-31, tolti i tre mesi sotto la soglia: circa 3,1 anni, sopra
`storia_minima_anni` (2). La campagna prosegue.

## Codice

`codice/comune.py` contiene queste scelte (intersezione, aggregazione, filtro dei mesi,
parametri del motore) ed è lo stesso per tutte le varianti.
