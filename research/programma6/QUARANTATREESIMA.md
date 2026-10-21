# Programma 6 — quarantatreesima prova: entrare pochi minuti dopo l'annuncio (Q1, Q2)

Scritto il 21 ottobre 2026, pomeriggio, **prima di qualunque calcolo sui prezzi**. Prima di scriverla si è contato solo
quanti annunci ci sono (titoli e date, nessun prezzo): 61 per Q1.

## 1. Perché

Le prove 21 e 41 dicono la stessa cosa: dopo una notizia il grosso del movimento avviene subito (gli annunci cattivi di
Binance: −11% e −18% il giorno stesso; l'arrivo su Upbit: +26,6% fra il giorno prima e l'entrata), e noi entravamo tardi
(il giorno dopo, o 2 ore dopo). Un bot che legge gli annunci di Binance (l'elenco pubblico si raggiunge dalla macchina)
può entrare in pochi minuti. La domanda: **quanto del movimento resta dopo i primi 5 minuti?**

* **Q1 — long dopo l'annuncio di quotazione a pronti su Binance di una moneta che ha già il perpetuo.** Quando Binance
  annuncia che quoterà la moneta a pronti (anche con le distribuzioni HODLer, Launchpool, Megadrop), arrivano compratori
  nuovi che non usano i perpetui; chi lo sa per primo compra il perpetuo. Eventi **mai guardati**.
* **Q2 — short dopo l'annuncio cattivo** (l'etichetta di monitoraggio, E1, e la rimozione dal mercato a pronti, E2, gli
  stessi eventi della prova 21). **Riserva**: l'idea nasce dalla prima reazione vista nella prova 21, quindi questi eventi non
  sono vergini; se passa, va confermata in avanti nel paper prima di contare.

## 2. La regola (valori fissati qui)

* **Eventi Q1**: gli annunci della sezione quotazioni (`scarico_annunci.py`) che cominciano con «Binance Will List» (non i
  token a leva, non i titoli con «Futures» o «Margin») o con «Introducing … on Binance HODLer Airdrops / Launchpool /
  Megadrop», dal 1 gennaio 2021 al 10 ottobre 2026; ogni sigla fra parentesi del titolo. **Eventi Q2**: `annunci.eventi_
  monitoraggio` ed `eventi_rimozione`, nello stesso periodo.
* La moneta deve avere il perpetuo USDT-M (`annunci.perpetuo`) con la prima candela giornaliera almeno **3 giorni** prima
  del giorno dell'annuncio e il volume del giorno prima sopra zero; esclusi il Bitcoin e i contratti esclusi del programma.
* **Entrata**: all'apertura della candela a 1 minuto (archivio di Binance) che comincia **5 minuti** dopo l'ora di
  pubblicazione dell'annuncio; long (Q1) o short (Q2) la moneta, e il verso opposto sul Bitcoin per lo stesso valore.
* **Uscita**: dopo **24 ore** (1.440 minuti) all'apertura della candela; uscita di protezione se la moneta va contro del
  **30%** (al livello, con l'1% di scarto, come N3).
* **Costi**: per la moneta commissione 0,05% più **0,30%** di scarto all'entrata e all'uscita (minuti di mercato agitato);
  per il Bitcoin `ventunesima.COSTO_BTC`; il funding delle ore tenute (quello del giorno diviso 24, per ogni ora), con il
  segno del verso, per la moneta e per il Bitcoin.
* Due prove a eventi (la **ottava** e la **nona** del programma) e due portafogli (nel conto del programma 6 diventano **67**).

## 3. L'esame (per Q1 e Q2, separate)

* **Per evento**: media netta sopra zero con **p ≤ 0,0011** (0,01 diviso le 9 prove a eventi; bootstrap sugli annunci),
  positiva nelle due metà e senza i 5 eventi migliori.
* **Come portafoglio**: il 5% a operazione, al massimo 20 aperte, la settimana somma le operazioni chiuse; `terza.esame` e
  `terza.esito` con lo Sharpe corretto sulle **67** prove.
* **VALIDA** solo se passa tutte e due; per Q2, con la riserva, resta comunque da confermare in avanti.
* Si riportano anche (per capire, non per scegliere): il movimento dei 5 minuti persi (dall'annuncio all'entrata) e
  dell'ora prima dell'annuncio (per vedere se l'ora di pubblicazione è giusta), il risultato entrando dopo 1 minuto, a 1 ora
  e a 4 ore, quante uscite di protezione, per anno.
