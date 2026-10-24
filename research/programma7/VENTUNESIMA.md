# Programma 7 — ventunesima prova: comprare le monete piccole crollate, in giornata (G19)

Scritto il 24 ottobre 2026, alle 13:45 UTC, **prima di scaricare le candele e prima di qualunque calcolo**. Idea 44 della coda di
`research/REGISTRO.md`: il lato long del trader da copiare n. 2 (`research/trader_copiati/trader_2.md`: 75 long su monete scese in
mediana del 19% nelle 24 ore e ancora in calo nel quarto d'ora prima, uscita a +3%).

## 1. Perché

Quando una moneta piccola crolla, chi vende di corsa (liquidazioni, paura) spinge il prezzo sotto il giusto e chi compra in quel
momento fa da controparte (lo stesso perché della prova 75, dall'altra parte). **La differenza che conta**: lo short sulle fiammate
può perdere il 1.500% (COAI, ottobre 2025), il long su un crollo perde al massimo il valore della moneta, e la protezione lo taglia
prima. **Il dubbio scritto prima**: le monete che crollano spesso continuano a scendere (notizie vere, sblocchi, tolte dal listino),
e la nostra prova sui rimbalzi dopo i crolli (prova 4) andava bene solo quando crollava tutto il mercato, non la moneta da sola.

## 2. Dati e periodo (fissati qui)

* **Periodo e universo come la prova 75**: dal 1° gennaio 2025 al 26 giugno 2026, tutti i perpetui USDT-M tranne le 30 monete con
  più volume medio nel periodo.
* Giorni candidati: il minimo del giorno almeno il 20% sotto l'apertura del giorno prima; candele a 1 minuto del giorno, di quello
  prima e di quello dopo (archivio pubblico di Binance).

## 3. La regola (valori vicini alle mediane del trader)

* **Il segnale al minuto t**: (a) la chiusura è almeno il **20% sotto** l'apertura di 24 ore prima; (b) la chiusura è almeno il
  **2% sotto** l'apertura di 14 minuti prima; (c) il volume in dollari medio dei 15 minuti fino a t è almeno **2 volte** la mediana
  dei minuti delle 24 ore prima.
* **Entrata**: long all'apertura del minuto t + 1. **Uscite**: obiettivo **+3%** a limite; protezione **−15%** (uscita al livello
  meno l'1%); al massimo **24 ore**. Se nello stesso minuto si toccano obiettivo e protezione, conta la protezione.
* Una posizione per moneta; rientro solo con un segnale nuovo almeno 15 minuti dopo l'uscita.
* Costi e funding come la prova 75 (il long paga il funding se positivo).
* Una prova a eventi: nel conto diventano **144**, le prove a eventi **20**.

## 4. L'esame

* Come la prova 75: media per operazione sopra zero con **p ≤ 0,01**, positiva nelle due metà e senza le 5 migliori; per dirla
  valida contando le 20 prove a eventi: **p ≤ 0,0005**. Portafoglio con il 5% a operazione (al massimo 20 aperte), Sharpe corretto
  con l'aggiunta (vale la decisione del proprietario del 24 ottobre per le candidate da 0,90 in su).
* Per capire, senza decidere niente: il caso (entrate a minuti a caso negli stessi giorni-moneta), la versione senza protezione (al
  massimo 7 giorni), per anno e per mese, e il periodo del trader (27 giugno – 22 ottobre 2026) come confronto.
