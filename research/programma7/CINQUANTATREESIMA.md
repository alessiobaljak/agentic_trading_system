# Programma 7 — cinquantatreesima prova: il BNB dopo gli annunci di Launchpool e Megadrop (BL)

Scritto il 27 ottobre 2026 alle 20:24 UTC (ora dell'orologio), **prima di qualunque calcolo sul prezzo del BNB intorno agli
annunci**. Fino a qui si sono contati solo gli annunci: 67 fra l'ottobre 2020 e oggi (6 nel 2020, 14 nel 2021, 3 nel 2022, 11 nel 2023,
23 nel 2024, 9 nel 2025, 1 nel 2026). È un'idea nuova, la 83 della coda, ed è una prova a eventi.

## 1. Perché

* **Per avere le monete regalate bisogna tenere BNB.** Con Launchpool e Megadrop, Binance regala la moneta nuova a chi blocca BNB
  durante il periodo di raccolta, che di solito comincia poche ore dopo l'annuncio.
* L'annuncio crea quindi una **domanda di BNB** da parte di chi vuole le monete gratis, e il BNB dovrebbe salire rispetto al Bitcoin nel
  giorno dopo. È «informazione diversa messa insieme con i prezzi»: un annuncio usato per un'altra moneta.
* **I dubbi scritti prima**:
  * il regalo vale poco rispetto al prezzo del BNB, pochi punti l'anno;
  * dal 2024 gli annunci sono frequenti e attesi;
  * chi fa questo mestiere può comprare BNB prima;
  * le distribuzioni HODLer (dal 2024) guardano i BNB tenuti nel passato e non creano domanda dopo l'annuncio, quindi qui non entrano.

## 2. La regola (fissata qui)

* **Eventi**: gli annunci della sezione quotazioni (`research/data/annunci/quotazioni.json`) con «Binance Launchpool» o «Binance Megadrop»
  nel titolo, senza «Launchpad», dal 22 ottobre 2020 al 24 ottobre 2026: 67 annunci. Se un annuncio arriva meno di 24 ore dopo
  l'entrata del precedente, si salta: una posizione alla volta.
* **Entrata**: all'apertura della candela a 1 minuto (archivio di Binance) che comincia **5 minuti** dopo l'ora di pubblicazione
  dell'annuncio. **Long il perpetuo del BNB e short il perpetuo del Bitcoin**, per lo stesso valore (come la prova 43).
* **Uscita**: dopo **24 ore** (1.440 minuti), all'apertura della candela; nessuna uscita di protezione.
* **Costi e funding**: i costi a mercato di ogni moneta del programma 6 (`sc.costi_moneta`, entrata e uscita sulle due gambe); il
  funding del giorno (il long del BNB paga quello del BNB, lo short del Bitcoin riceve quello del Bitcoin).
* **Una prova a eventi**: nel conto delle prove diventano **210**, le prove a eventi **35**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`): media per evento sopra zero con **p ≤ 0,01** (ricampionamento a blocchi delle settimane),
  positiva nelle due metà e senza i 5 eventi migliori. Per dirla valida contando le 35 prove a eventi serve **p ≤ 0,00029**. Con 67
  eventi la prova ha poca forza, e va detto prima.
* **Il controllo**: la stessa operazione in 5 minuti presi a caso per ogni evento, fra i 30 e i 60 giorni prima dell'annuncio, lontani
  almeno 3 giorni da ogni altro annuncio. Il guadagno dell'evento va confrontato con quello del controllo.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: la tenuta di 72 ore; il BNB da solo, senza la copertura del Bitcoin; il primo minuto e i primi
  5 minuti dopo l'annuncio, per vedere quanto del movimento va a chi arriva prima; per anno; Launchpool contro Megadrop.
