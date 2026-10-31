# Programma 7 — settantanovesima prova: il funding che diventa negativo dopo una settimana positiva (FS)

Scritto il 31 ottobre 2026 alle 04:22 UTC (ora dell'orologio), **prima di qualunque calcolo**. È un'idea nuova, la 118 della coda, scritta
con la coda vuota, nella famiglia che regge: chi paga la leva perde.

## 1. Perché

* **Il funding di quasi tutte le monete è positivo per giorni** (i long pagano la base). Quando, dopo una settimana positiva, il funding di
  un giorno diventa **negativo**, vuol dire che sono arrivati in fretta molti short, che adesso pagano loro.
* **Gli short appena arrivati sono quelli che perdono**: G1 guadagna proprio dal lato long, le monete con il funding più basso (prova 57:
  il lato long di F5 fa +42,8% l'anno), ed E3 (long dopo il funding al tetto in negativo, prova 26) aveva una media alta ma molto rumorosa.
  Il giorno in cui il funding cambia segno è il primo momento in cui l'affollamento degli short si vede.
* **È trading di ogni giorno**: si guarda ogni mattina e si entra il giorno stesso.
* **I dubbi scritti prima**:
  * può essere solo G1 visto da un altro lato: il confronto con il controllo dice se il cambio di segno aggiunge qualcosa;
  * a volte gli short arrivano perché sanno qualcosa (un furto, uno sblocco, una notizia cattiva);
  * E3 aveva solo il 38% di operazioni vinte.

## 2. La regola (fissata qui)

* **L'evento**: una moneta dell'universo di G1 del giorno d (le 100 più scambiate del lunedì), con la somma del funding del giorno d − 1
  **sotto zero** e quella di **ognuno** dei 7 giorni prima (da d − 8 a d − 2) **sopra zero** (`seconda.pannello`, funding per giorno di
  tenuta); al massimo un evento ogni 14 giorni per moneta; tutte le monete tranne il Bitcoin; dal 4 gennaio 2021 al 20 settembre 2026.
* **L'operazione**: long il perpetuo della moneta e short il Bitcoin per lo stesso valore dall'apertura del giorno d (00:00 UTC), uscita
  dopo 7 giorni o quando il minimo orario della moneta scende del 30% sotto l'entrata (con lo scarto dell'1%); costi a mercato della moneta
  e del Bitcoin (`ventunesima.COSTO_MONETA` e `COSTO_BTC`), funding dei giorni tenuti (il long incassa il funding negativo).
* **Una prova a eventi**: nel conto delle prove diventano **239**, le prove a eventi **44**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): media per evento sopra zero con **p ≤ 0,01**, positiva
  nelle due metà e senza i 5 eventi migliori, **e sopra il controllo** (differenza con p ≤ 0,05). Contando le 44 prove a eventi la soglia
  è **0,00023**.
* **Il controllo**: la stessa operazione sulle stesse monete in giorni con il funding del giorno prima sotto zero ma **senza** la settimana
  positiva prima (gli short c'erano già), presi a caso (seme 2026, 20 per evento, fra 30 e 365 giorni prima o dopo). Se il controllo rende
  uguale, il cambio di segno non aggiunge niente a «funding negativo».
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: le tenute di 3 e 14 giorni; senza la copertura del Bitcoin; per anno; quanto è negativo il funding
  del giorno dell'evento.
