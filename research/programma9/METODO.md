# Programma 9 — esplorazione larga: mettere insieme le informazioni per vedere il quadro

Scritto il 24 ottobre 2026, alle 15:40 UTC, **prima di costruire i dati e prima di qualunque calcolo**. Il proprietario: «amplia
notevolmente la ricerca [...] non seguire le regole standard su internet [...] è la tua capacità di leggere informazioni diverse e
metterle insieme, vedere il quadro generale, che sto cercando» (24 ottobre). E: nessuna moneta si esclude perché è andata male in
una prova.

## 1. Il quadro da cui si parte

Le strategie che reggono non vengono dai libri ma dai nostri dati, e hanno un filo comune: **guadagnano quando la leva è affollata
da una parte** (F5 e G1: il funding fra monete; N3: le monete nuove; E4: il funding al tetto). Le prove fallite dicono dove sta il
rischio: gli short sulle monete piccole perdono quando la salita continua (prove 21, 62, 75: le code verso l'alto). Il programma
cerca dove queste informazioni, **messe insieme**, danno qualcosa che da sole non danno: per esempio una fiammata con i long
affollati (funding alto, interesse aperto che sale) contro una fiammata con gli short affollati (funding negativo: chi è short viene
costretto a ricomprare).

## 2. I dati (una riga per moneta e giorno)

* Universo: le 100 monete più scambiate della settimana (`terza.pannello_settimane`, U), ogni giorno, dal 1° gennaio 2022 (da quando
  ci sono i dati sulle posizioni, `programma6/scarico_metrics`).
* **Gli ingredienti** (tutti noti alla chiusura del giorno t, niente dal futuro): funding del giorno, dei 7 giorni, la sua
  variazione; interesse aperto: variazione a 1, 7 e 30 giorni, rispetto al volume; rapporto long/short dei conti grandi e di tutti, e
  la loro differenza; quota di acquisti a mercato a 1 e 7 giorni; rendimenti a 1, 3, 7 e 30 giorni; il giorno migliore e il peggiore
  dei 30; volatilità a 30 giorni; età del contratto; distanza dal massimo e dal minimo dei 30 giorni; volume rispetto ai 30 giorni;
  quota del volume a pronti; ampiezza del giorno; e il contesto del mercato (Bitcoin a 7 e 30 giorni, funding medio di tutte).
* **Cosa si misura**: il rendimento della moneta nei 1, 3 e 7 giorni dopo, **meno la media dell'universo** nello stesso tratto (così
  non conta se il mercato sale o scende).

## 3. Due periodi, separati per legge

* **Esplorazione: 2022 e 2023.** Qui si guarda tutto: ogni ingrediente da solo (in cinque fasce, per giorno) e **ogni coppia** di
  ingredienti (tre fasce per tre), su ogni orizzonte. Per ogni casella: la media del rendimento in più, e il t calcolato sui giorni
  (una media per giorno, poi il t fra i giorni), con almeno 200 giorni con monete nella casella.
* **Conferma: dal 1° gennaio 2024 al 26 giugno 2026**, che il programma di esplorazione **non legge** (il codice taglia i dati prima).
* Dall'esplorazione si scelgono **al massimo 5 combinazioni**, ognuna con il suo perché scritto (un meccanismo, non solo un numero),
  e si scrivono come strategie prima di guardare la conferma: ogni giorno long (o short) le monete della casella contro la media
  dell'universo, l'orizzonte della casella, i costi veri. **Ognuna è una prova nel conto.**
* Il periodo dopo il 26 giugno 2026 resta per la prova in avanti.

## 4. L'esame della conferma

* Come le prove del programma 7: Sharpe settimanale, ogni anno, Sharpe corretto con l'aggiunta, t sopra 3; vale la decisione del
  proprietario del 24 ottobre (da 0,90 in su, ogni anno positiva e t sopra 3: si porta sul demo e nel paper).
* Si riporta anche quanto la combinazione aggiunge rispetto a ciascuno dei suoi due ingredienti da solo: se non aggiunge, non è un
  quadro nuovo ma un ingrediente già noto.
