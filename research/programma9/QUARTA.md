# Programma 9 — quarta prova: le monete nuove al 7° giorno, divise per funding (P9D)

Scritto il 24 ottobre 2026, alle 20:25 UTC, **prima di dividere per funding le operazioni della regola delle monete nuove** (mai
fatto: la prova 32 le ha guardate tutte insieme).

## Perché

La vendita delle monete nuove al 7° giorno (N3) è una delle poche strategie che reggono (sul passato di Binance +4,29% a operazione
su 613, p 0,0017), ma perde quando la moneta nuova esplode (la coda verso l'alto). Lo stesso meccanismo della prova 81: una salita
che continua è spesso uno schiacciamento degli short, più probabile quando a essere affollati sono gli short (funding negativo).
Sulle fiammate delle monete piccole il funding non ha separato niente (prova 82); qui la base è diversa (una regolarità che esiste) e
le monete nuove hanno spesso il funding molto negativo nei primi giorni (molti le vendono). **Il dubbio scritto prima**: la prova 82
dice che il funding dell'ultimo regolamento può non contare.

## La regola

* **Le 613 operazioni della prova 32**, identiche (`programma6/risultati_trentaduesima/eventi_N3B.csv`: short all'apertura del 7°
  giorno contro il Bitcoin, uscita a +30% o dopo 30 giorni).
* Il funding dell'ultimo regolamento **prima** dell'entrata (prima delle 00:00 del 7° giorno), riportato a 8 ore, dai file mensili
  dell'archivio di Binance.
* **P9D = solo le operazioni con il funding almeno +0,01% per 8 ore** (i long pagano almeno il tasso di base).
* Una prova a eventi: nel conto **149**, prove a eventi **23**.

## L'esame

* La media di P9D sopra zero con **p ≤ 0,01**, positiva nelle due metà e senza le 5 migliori; **e migliore delle operazioni con il
  funding sotto la soglia**, con la differenza sopra zero con p ≤ 0,05 (bootstrap sulle settimane). Se P9D non è migliore, la regola
  delle monete nuove resta com'è.
* Si riportano per anno le due parti, la quota di uscite a +30% nelle due parti e quante operazioni non hanno il funding.
