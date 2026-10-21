# Programma 6 — quarantesima prova: le coppie di monete che si allontanano (C-COPPIE)

Scritto il 21 ottobre 2026, mezzogiorno, **prima di qualunque calcolo**. Idea 5 della coda di `research/REGISTRO.md`, mai
provata.

## 1. Perché

Monete che si muovono quasi sempre insieme (stessa famiglia, stessi compratori) a volte si allontanano per flussi propri di
una sola (una vendita grossa, una notizia minore) e poi si riavvicinano. Comprando quella rimasta indietro e vendendo quella
andata avanti per lo stesso valore, il guadagno non dipende da dove va il mercato. L'indicatore è la distanza del rapporto
fra le due dalla sua media, in deviazioni (z). Con le candele giornaliere i movimenti sono di qualche punto percentuale, più
grandi dei costi delle quattro operazioni (due monete, entrata e uscita).

## 2. La regola (valori fissati qui)

* **Monete**: l'universo della settimana (le 100 più scambiate, terza prova, dati corretti).
* **Coppie**, rifatte il primo lunedì di ogni mese con i soli 180 giorni prima: per ogni moneta dell'universo la moneta con la
  correlazione dei rendimenti giornalieri più alta; si tengono le coppie con correlazione almeno **0,80**, le **20** più
  correlate, senza monete ripetute. Rapporto: `log(prezzo A) − b · log(prezzo B)` con `b` dalla regressione dei 180 giorni.
* **z** di ogni giorno: (rapporto − media dei 60 giorni prima) / deviazione dei 60 giorni prima.
* **Entrata** (alla chiusura del giorno, si opera all'apertura del giorno dopo): |z| sopra **2** → short la moneta cara e
  long quella a buon mercato, il **5%** del capitale per gamba (la gamba B per `b` volte il valore della A, al massimo
  il doppio); al massimo **20** coppie aperte.
* **Uscita**: |z| sotto **0,5**, oppure |z| sopra **4** (la coppia si è rotta), oppure dopo **20** giorni. Una coppia aperta
  resta aperta anche se il mese dopo non è più fra le scelte, fino alla sua uscita.
* **Costi**: per ogni gamba commissione 0,05% più lo scarto (0,01% BTC, ETH, SOL; 0,02% le altre) all'entrata e all'uscita;
  funding di ogni giorno, con il segno, per le due gambe.
* Dal **4 gennaio 2021** al **10 ottobre 2026**. Una prova: nel conto del programma 6 diventano **63**.

## 3. L'esame

Per operazione (media netta sopra zero con **p ≤ 0,01**, bootstrap sulle settimane d'entrata, due metà, senza le 5 migliori)
**e** come portafoglio (rendimento della settimana = somma delle operazioni chiuse; `terza.esame`, Sharpe corretto sulle **63**
prove). Si riportano anche: quante coppie per mese, la tenuta media, quante uscite per obiettivo, per rottura e per tempo.
