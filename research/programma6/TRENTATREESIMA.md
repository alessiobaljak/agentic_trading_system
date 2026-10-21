# Programma 6 — trentatreesima prova: le due strategie di Binance in un portafoglio (N3 a portafoglio, F5 + N3)

Scritto il 21 ottobre 2026, mattina, **prima del calcolo**, dopo la richiesta del proprietario di vedere strategie
utilizzabili su Binance subito. Vale `TRENTADUESIMA.md` (N3 su Binance) e `VENTIQUATTRESIMA.md` (F5).

## 1. Perché

N3 è misurata per operazione (+4,29% a evento su Binance); F5 per settimana (Sharpe 1,93). Per usarle insieme serve sapere
come va il **capitale giorno per giorno**: quanto rende, quanto oscilla, quanto può scendere.

## 2. Le regole

* **N3 a portafoglio**: ogni operazione di N3 (gli eventi di `risultati_trentaduesima/eventi_N3B.csv`, stesse entrate e
  uscite) usa il **5%** del capitale per gamba (short la moneta 5%, long il Bitcoin 5%), al massimo **20** operazioni
  aperte insieme (le altre si saltano, in ordine di data). Ogni giorno il valore segue le chiusure giornaliere della moneta e
  del Bitcoin; il giorno dell'uscita vale il prezzo d'uscita della regola (+30% più l'1% se scatta l'uscita, se no l'apertura
  del giorno 30); costi all'entrata e all'uscita come N3; funding di ogni giorno di tenuta.
* **F5 + N3**: il capitale diviso fra F5 (settimane, `risultati_ventiquattresima/settimane_F5.csv.gz`) e N3 a portafoglio
  (sommato per settimana dal lunedì) a rischio uguale con la volatilità delle 26 settimane prima (`quindicesima.combina`).
* Due prove: nel conto del programma 6 diventano **56**.

## 3. L'esame

Dal **4 gennaio 2021**, `terza.esame` e `terza.esito` sulle settimane, con lo Sharpe corretto sulle **56** prove. Si
riportano anche: quante operazioni saltate per il tetto di 20, il numero medio di operazioni aperte, la correlazione
fra F5 e N3.
