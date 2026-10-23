# Programma 7 — quindicesima prova: vendere i perpetui annunciati in chiusura (G13)

Scritto il 23 ottobre 2026, sera, **prima del calcolo**. Idea 35 della coda di `research/REGISTRO.md`.

## 1. Perché

Quando Binance annuncia che chiuderà un perpetuo, chi ha posizioni deve chiuderle entro la data, i market maker si ritirano e la
moneta perde un posto dove si scambia con la leva: il prezzo tende a scendere fino alla chiusura (la revisione di G12 ha visto due
monete crollare nelle ultime ore). **Il rischio opposto è noto**: dopo gli annunci di chiusura a volte gli short affollati vengono
schiacciati (ALPACA nel 2025; E2, prova 21, vendere dopo la rimozione a pronti perdeva il 21% a evento per qualche salita enorme).
Per questo lo short ha l'uscita di protezione a +30% di N3. Mai provato sui future.

## 2. La regola (valori fissati qui)

* **Gli eventi**: gli annunci «Binance Futures Will Delist …» nei nostri annunci (`research/data/annunci`), con le sigle scritte
  nel titolo (gli annunci «Multiple …» senza sigle nel titolo non si usano: si conta quanti sono). Per ogni sigla il perpetuo USDT
  del pannello; la **chiusura** è l'ultima candela da 1 ora del contratto nell'archivio dopo l'annuncio, se cade **entro 21 giorni**
  dall'annuncio (lo scarico copre 32 giorni: un'ultima candela più tardi vuol dire che il contratto non ha chiuso, o che l'annuncio
  non è suo); altrimenti l'evento non si usa.
* **L'operazione**: all'apertura dell'ora dopo l'annuncio, short la moneta e long il Bitcoin per lo stesso valore; uscita
  all'apertura dell'ora **prima** dell'ultima candela (un'ora prima della chiusura), o prima se la moneta sale del **30%**
  dall'entrata (candele a 1 ora, 1% di scarto). Se fra annuncio e chiusura ci sono meno di 3 ore, l'evento non si usa.
* Costi come N3 (`ventunesima.COSTO_MONETA` e `COSTO_BTC`), funding vero dei giorni di tenuta per le due gambe. Una prova a eventi:
  nel conto diventano **136**.

## 3. L'esame

Come N3 (`trentesima.esame`): media per evento sopra zero con **p ≤ 0,01** (bootstrap sulle settimane dell'annuncio), positiva nelle
due metà e senza i 5 eventi migliori. Si riportano anche la versione senza l'uscita a +30%, la durata media e per anno.
