# Fase 0 — I dati di MASKUSDT

Scritto il 2026-10-09 (UTC), prima di qualunque test di variante. Fonte: data.binance.vision,
file mensili USDS-M (klines, markPriceKlines, fundingRate), scaricati con `src/dati.py`
(`codice/scarica.py`) solo da 2021-08 a 2023-12. Il dettaglio numerico è in
`fase0_dettaglio.json` (prodotto da `codice/fase0.py`).

## Periodi (punto 1, scritti nel log prima dei prezzi: voce `MASKUSDT-F0-PERIODI`)

| | |
|---|---|
| Inizio (primo giorno del primo mese della scheda) | 2021-08-01 |
| Giorni fino al 2023-12-31 | 883 |
| Costruzione | 2021-08-01 → 2023-04-10 (618 giorni), fine 1681171199999 ms |
| Validazione | 2023-04-11 → 2023-12-31 |

**Dichiarazione.** I file di agosto 2021 cominciano il 2021-08-26 (mark) e il 2021-08-27 (last
allineato): i primi 25 giorni del mese non hanno dati. Le date restano quelle scritte prima dei
prezzi (regola di `lezioni/metodo.md`): la costruzione utile è di 592 giorni, non 618. Storia
utile dal 2021-08-27 al 2023-12-31: 2,35 anni, sopra il minimo di 2 (punto 4: la campagna si fa).

## Impronte (sezione 5)

* `impronte.json` (551 file di MASKUSDT): SHA-256 del file `8c2a1b020c9023d329047f772d52bccf2fd75de1da1ff79dda8edb0a2a6f4ea7`.
* `impronte_btcusdt.json` (261 file di BTCUSDT, solo last, riferimento di mercato): SHA-256 `6574f3d8558afc108da3257d0ac59175cf86076684aaf8909789b89c025c6cfc`.
* Il confronto con il CHECKSUM pubblicato da Binance è fatto da `scarica_mese` prima di scrivere
  ogni file (nessun errore di integrità: lo scarico è finito senza eccezioni). L'elenco dei CHECKSUM
  mancanti stampato dallo script non è stato letto (l'uscita dei processi in background sta fuori
  dai percorsi ammessi): da dichiarare come non verificato.

## Last e mark allineati (`carica_serie_allineate`, punto 2)

Stesse barre tolte su tutti i timeframe, in giorni interi:

* **Mark presente, last assente** (`tolte_mark`): 2021-08-26 (inizio dei file), 2022-02-26 → 2022-02-28,
  2022-04-01 → 2022-04-02.
* **Last presente, mark assente** (`tolte_last`): 2022-10-02, 2023-02-24 (e a 15 minuti una barra del
  2023-11-10 03:45, in validazione).

| Timeframe | Barre tenute | di cui costruzione | Tolte last | Tolte mark | Buchi dopo l'allineamento | ATR14 / prezzo, mediana (10°-90° percentile) |
|---|---|---|---|---|---|---|
| 15m | 81.585 | 56.146 | 193 | 581 | 5 | 0,86% (0,44-1,66%) |
| 30m | 40.793 | 28.073 | 96 | 291 | 4 | 1,23% (0,65-2,36%) |
| 1h | 20.397 | 14.037 | 48 | 145 | 4 | 1,79% (0,96-3,34%) |
| 2h | 10.199 | 7.019 | 24 | 72 | 4 | 2,63% (1,41-4,71%) |
| 4h | 5.100 | 3.510 | 12 | 36 | 4 | 3,82% (2,15-6,86%) |
| 6h | 3.400 | 2.340 | 8 | 24 | 4 | 4,71% (2,73-8,43%) |
| 8h | 2.550 | 1.755 | 6 | 18 | 4 | 5,60% (3,22-10,0%) |
| 12h | 1.700 | 1.170 | 4 | 12 | 4 | 6,95% (4,12-12,3%) |
| 1d | 850 | 585 | 2 | 6 | 4 | 10,2% (6,33-18,1%) |

I 4 buchi sono i 4 intervalli di giorni sopra (in costruzione: febbraio, aprile e ottobre 2022,
febbraio 2023). Nessuna barra tenuta senza volume in USDT. BTCUSDT ha tutte le barre di MASKUSDT
su ogni timeframe (0 barre di MASK senza la barra di BTC con lo stesso istante).

## Sospensioni e cambi di contratto

Nessun cambio di simbolo fino al 2023-12-31 secondo la scheda; nessuna cucitura. I giorni senza
last (sopra) sono le sole interruzioni viste.

## Funding

2.573 settlement dal 2021-08-26 08:00 al 2023-12-31 16:00, sempre a 8 ore (intervallo dichiarato
nei file e ricavato dalle distanze: un solo segmento). Tasso mediano 0,0100% (il tasso base).
Copertura completa: 857 giorni × 3 ≈ 2.571.

## Volume e liquidità (punto 3)

Volume medio giornaliero in USDT (colonna `quote_volume` dei file `1d` del last, tutti i giorni):
2021 (da agosto) 97,5 milioni; 2022 121,6 milioni; 2023 199,3 milioni. La fascia di slippage della
scheda (0,05%, da 50 a 200 milioni nel 2023) è coerente anche col 2021-2022.

**Mesi sotto 20 milioni al giorno: 2022-09 (12,0 milioni).** Vicini alla soglia: 2022-07 (20,08) e
2022-08 (22,08), sopra. **Filtro** (uguale per `conta_trade`, test e baseline (a); le stesse barre
vanno nelle barre vietate della (b)): nessun ingresso su segnali di barre il cui istante d'apertura
cade nel settembre 2022 (UTC). Una posizione già aperta esce con la sua uscita. Codice:
`codice/quadro.py`, `periodo()` (`permesse`) e `vietate_liquidita()`.

## Costi in R (per le previsioni, `lezioni/metodo.md`)

Un giro costa 0,20% del nozionale (commissione 0,05% e slippage 0,05% per lato). Con lo stop a k
ATR mediano: a 1 ora 2 ATR ≈ 3,6% → circa 0,06 R; 1,5 ATR ≈ 2,7% → 0,07 R; 3 ATR ≈ 5,4% → 0,04 R.
A 4 ore 2 ATR ≈ 7,6% → 0,03 R; 3 ATR ≈ 11,5% → 0,02 R. A 8 ore 2 ATR ≈ 11% → 0,02 R.

**Tetto di stop del bot (6%).** A 4 e 8 ore uno stop di 2 ATR è più largo del 6% nella maggior
parte delle barre: una variante a 4 o 8 ore con questi stop il bot non la può eseguire così com'è
(da dichiarare per ogni candidato; il motore non lo impone).

## Controllo positivo degli strumenti

Fatto prima di qualunque variante (voci `MASKUSDT-CP-1` e `MASKUSDT-CP-2`): superato.
