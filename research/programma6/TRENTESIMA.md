# Programma 6 — trentesima prova: le monete appena quotate, short con l'uscita di protezione, su Gate.io (N3)

Scritto il 21 ottobre 2026, notte, **prima di scaricare le candele a 1 ora e di qualunque calcolo sui prezzi** delle monete
nuove di Gate.io. Idea 7 della coda di `research/REGISTRO.md`. Contati solo i contratti dalle candele giornaliere già
scaricate (prova 27): 1.123 contratti nuovi fra febbraio 2023 e luglio 2026, circa 747 senza un perpetuo di Binance della
stessa moneta quando arrivano su Gate.io.

## 1. Perché

* Prova 18 (Binance): la moneta appena quotata tipica scende (mediana −3,6% a settimana), ma poche esplodono verso l'alto e
  lo short perde (−18,5% l'anno). Senza le code la media era −1,6% a settimana: l'idea dell'uscita di protezione viene da
  lì, quindi su Binance sarebbe una costruzione.
* Qui la si prova **su dati mai guardati**: le monete nuove di Gate.io che su Binance non c'erano (altre monete, o le stesse
  ma prima che Binance le quotasse).

## 2. La regola

* **Monete**: i contratti USDT perpetui di Gate.io con la prima candela giornaliera fra il **1 febbraio 2023** e il **31
  luglio 2026** (quelli che compaiono a gennaio 2023, il primo mese dell'archivio, possono essere più vecchi), esclusi i
  contratti che non sono una moneta (`seconda.ESCLUSI` con lo stesso nome) e quelli della stessa moneta già quotata come
  perpetuo su Binance il giorno dell'ingresso.
* **Ingresso**: short all'apertura del giorno **7** dalla prima candela (età 7 giorni, come N1), long il Bitcoin di Gate.io
  per lo stesso valore; serve volume non zero il giorno prima.
* **Uscita di protezione**: se nelle candele a 1 ora il massimo della moneta arriva a **+30%** dal prezzo d'ingresso, si esce
  a +30% più l'**1%** di scarto (nelle esplosioni il prezzo salta); il Bitcoin si chiude alla chiusura di quell'ora.
* Altrimenti si esce all'apertura del giorno **30 dopo l'ingresso**.
* **Costi**: la moneta 0,05% + 0,10% di scarto all'entrata e all'uscita, il Bitcoin 0,05% + 0,01%; il funding di Gate.io dei
  giorni di tenuta per le due gambe, con il segno.

## 3. L'esame

Per evento, come le prove 21 e 26 (`ventunesima.esame`): media sopra zero con **p ≤ 0,01** a una coda (una regola sola su
dati nuovi), con il bootstrap che rimescola le settimane d'ingresso; positiva nelle due metà degli eventi e senza i 5 eventi
migliori. Si riportano anche: quante volte scatta l'uscita di protezione, lo stesso senza l'uscita (solo per capire), e per
anno. Una prova a eventi, nel registro.
