# Programma 7 — cinquantunesima prova: le monete nuove distribuite gratis (N3G)

Scritto il 27 ottobre 2026 alle 12:50 UTC, **prima di qualunque calcolo di rendimento su questa divisione**. È l'idea 79 della coda di
`research/REGISTRO.md`. È una prova a eventi sulle monete appena quotate.

## 1. Perché

* **Chi riceve una moneta senza pagarla la vende appena può.** Con HODLer Airdrops, Launchpool e Megadrop, Binance regala la moneta
  nuova a chi tiene BNB, e poi la quota. Chi l'ha ricevuta non ha un prezzo d'acquisto da difendere, quindi vende.
* La regola delle monete nuove, N3, vende dal 7° giorno di vita con l'uscita a +30% (prove 30 e 32, ed è nel paper del bot). Su queste
  monete dovrebbe rendere di più che sulle altre.
* **Il dubbio scritto prima**: sono monete scelte da Binance, con molta pubblicità, e chi fa mercato le può sostenere nelle prime
  settimane.

## 2. Cosa si è già visto (riserve)

* **La media di N3 su tutte le 613 monete** (+4,29% a evento, prova 32) è nota.
* **L'idea 56 del 25 ottobre** ha diviso le stesse monete secondo la quotazione a pronti, e ne ho visto le medie per gruppo:
  * quotate a pronti prima del perpetuo: +8,4%;
  * quotate a pronti insieme al perpetuo: +5,1%;
  * con il solo perpetuo: +3,3%.
* **Il controllo di fattibilità di oggi** (conta solo le monete, nessun rendimento) dice che **83 delle 87** monete gratis stavano nel
  gruppo «solo perpetuo», insieme ad altre 381. Di quel gruppo si conosce solo la media di tutte le 464 monete insieme, non quella
  delle monete gratis.

## 3. I dati e la divisione (fissati qui)

* **Gli eventi**: le 613 operazioni della prova 32 (`programma6/risultati_trentaduesima/eventi_N3B.csv`), così come sono. Non si
  ricalcola niente.
* **Moneta gratis**: il perpetuo è abbinato (`annunci.perpetuo`) a una sigla fra parentesi nel titolo di un annuncio della sezione
  quotazioni (`research/data/annunci/quotazioni.json`).
  * Il titolo contiene «Binance HODLer Airdrops», «Binance Launchpool» o «Binance Megadrop», ma non «Launchpad», che è una vendita e
    non un regalo.
  * L'annuncio è pubblicato fra 60 giorni prima e il giorno dell'entrata (il 7° giorno di vita).

  Sono **87 eventi**: 2 nel 2021, 2 nel 2022, 7 nel 2023, 26 nel 2024, 49 nel 2025 e 1 nel 2026. Le altre monete sono 526.

## 4. L'esame

* **La differenza fra i due gruppi, nello stesso periodo.**
  * Per ogni trimestre in cui ci sono tutti e due i gruppi si calcola la media delle gratis meno la media delle altre.
  * Si fa la media delle differenze, pesata con il numero delle gratis del trimestre. Così il risultato non dipende da quali anni
    sono andati bene per tutte le monete nuove.
  * La probabilità si misura **mescolando a caso l'etichetta «gratis» fra le monete dello stesso trimestre**, 10.000 volte, e
    contando quante volte la differenza è almeno quella vera.
  * Serve **p ≤ 0,01**.
* **Le monete gratis da sole**: la media per evento deve essere sopra zero con p ≤ 0,01 (`trentesima.esame`), positiva nelle due
  metà e senza i 5 eventi migliori.
* **Per dirla valida contando le 34 prove a eventi**, la differenza deve avere **p ≤ 0,0003**. Con 87 eventi serve una differenza
  molto grande, e va detto prima: la prova ha poca forza.
* **Se regge**, passa da un revisore separato. La regola N3 del bot non cambia prima del giudizio del revisore.
* **Per capire, senza decidere niente**: HODLer Airdrops contro Launchpool; per anno; la quota delle uscite a +30%; i rendimenti senza
  l'uscita (la colonna `r_senza`).
* **Una prova a eventi**: nel conto delle prove diventano **208**, le prove a eventi **34**.
