# Programma 7 — sessantaquattresima prova: vendere alla fine delle gare di trading di Binance (GT)

Scritto il 29 ottobre 2026 alle 12:47 UTC (ora dell'orologio), **prima di qualunque calcolo dei rendimenti**. Fino a qui si sono solo
contati gli abbinamenti fra le gare e i perpetui (vedi la sezione 2). È l'idea 96 della coda.

## 1. Perché

* **Le gare di trading di Binance** («Trading Competition», «Trading Tournament», «Trading Challenge») premiano chi scambia più volume
  su una moneta per una o due settimane. Chi gareggia compra e vende per il premio, non per il valore della moneta.
* **L'ipotesi**: la gara gonfia gli scambi e la domanda della moneta, e quando finisce la domanda sparisce; il prezzo scende nei giorni
  dopo. È la famiglia di N3 e di N3G: chi compra per un motivo che non è il valore paga troppo.
* **I dubbi scritti prima**:
  * le date della gara sono scritte nell'annuncio, quindi la fine è nota a tutti in anticipo e qualcuno può vendere prima;
  * il 74% delle gare utilizzabili è del 2026: la prova misura soprattutto un anno solo;
  * il 19% delle monete ha il perpetuo da meno di 30 giorni alla fine della gara, quindi una parte del calo può essere quello delle
    monete nuove (N3), già noto. Il controllo sulle stesse monete serve a questo.

## 2. I dati e gli abbinamenti (già contati, senza rendimenti)

* **Gli annunci**: la sezione delle attività di Binance (catalogo 93), 3.215 annunci letti il 29 ottobre; 463 hanno nel titolo
  «Trading Competition», «Trading Tournament» o «Trading Challenge». I testi sono salvati in `research/data/annunci/gare/`, fuori da git.
* **Il periodo**: il primo «Period: inizio to fine» del testo (anche le forme vecchie con la barra e con AM/PM), in UTC.
* **La moneta**: la sigla fra parentesi nel titolo, o la prima parola in maiuscolo del titolo, o «USDⓈ-M XYZ», o «in XYZ»; tolte UTC,
  USDT, BNB, USD, BUSD, USDC, BTC ed ETH (premi o gare generiche). Il perpetuo è `XYZUSDT` di Binance, o `1000XYZUSDT`.
* **Un evento entra se**: il perpetuo esiste dal giorno della fine della gara o prima, scambia il giorno dopo, e ci sono almeno 8 giorni
  di dati dopo la fine. Se la stessa moneta ha due gare che finiscono a meno di 14 giorni l'una dall'altra, conta solo la prima.
* **Il conto fatto**: 169 gare con periodo, moneta e perpetuo (2020: 6, 2021: 14, 2022: 3, 2023: 2, 2024: 3, 2025: 16, 2026: 125), su
  125 monete diverse; durata mediana della gara 7 giorni. Le altre: 109 senza una moneta nel titolo, 88 senza perpetuo, 48 con il
  perpetuo nato dopo la fine, 48 senza periodo leggibile.

## 3. La regola (fissata qui)

* **Come la prova 105** (`quarantatreesima.operazione`): short il perpetuo della moneta e long il Bitcoin per lo stesso valore,
  dall'apertura del giorno dopo quello in cui la gara finisce (00:00 UTC); uscita quando il massimo orario della moneta sale del 30%
  sopra l'entrata (con lo scarto dell'1%), oppure dopo 7 giorni. Costi a mercato della moneta e del Bitcoin, funding dei giorni tenuti.
  Candele orarie del perpetuo.
* **Una prova a eventi**: nel conto delle prove diventano **222**, le prove a eventi **36**.

## 4. L'esame (scritto prima)

* **Come la prova 105** (`trentesima.esame`, ricampionamento per settimana): media per evento sopra zero con **p ≤ 0,01**, positiva
  nelle due metà e senza i 5 eventi migliori, **e sopra il controllo** sulle stesse monete (differenza con p ≤ 0,05). Contando le 36
  prove a eventi la soglia è **0,00028**.
* **Il controllo**: la stessa operazione sulla stessa moneta in 20 giorni presi a caso (seme 2026) fra 30 e 365 giorni prima o dopo la
  fine della gara, lontani almeno 30 giorni dalla fine e dall'inizio di ogni gara della stessa moneta, dentro la vita del perpetuo e dei
  dati.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: la moneta contro il Bitcoin durante la gara (dall'apertura del giorno dell'inizio a quella del
  giorno dopo la fine); le tenute di 3 e di 14 giorni; per anno; le monete con il perpetuo da meno di 60 giorni contro le altre; le gare
  di Binance Alpha contro le altre; l'operazione aperta il giorno dell'inizio della gara invece che alla fine.
