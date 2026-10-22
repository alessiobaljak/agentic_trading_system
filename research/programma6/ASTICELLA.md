# Programma 6 — l'asticella rivista: lo Sharpe corretto come lo prescrivono i suoi autori

Scritto il 22 ottobre 2026, mattina, **prima di ricalcolare**, su richiesta del proprietario: «riguarda questa asticella
[...] non sto dicendo di non avere un'asticella ma di essere sicuri che la stiamo usando nella maniera corretta».

## 1. Cosa abbiamo fatto finora

Lo «Sharpe corretto» è il Deflated Sharpe Ratio (Bailey e López de Prado, *Journal of Portfolio Management* 2014): la
probabilità che lo Sharpe vero della strategia sia sopra il massimo che N prove senza vantaggio darebbero per caso. Il
massimo per caso dipende da due numeri: **N**, quante prove indipendenti, e **V**, quanto variano gli Sharpe delle prove.
Noi abbiamo messo **N = tutte le prove contate una per una** (107) e **V = la varianza degli Sharpe di tutte le 107**.

## 2. Cosa prescrivono gli autori (e dove sbagliamo)

1. **N è il numero di prove indipendenti, non di prove.** Varianti molto simili (le 34 strategie di TradingView, le versioni
   di F, le combinazioni che contengono F5) sono quasi la stessa prova. López de Prado (2019, «A Data Science Solution to the
   Multiple-Testing Crisis in Financial Research», *Journal of Financial Data Science*; 2020, *Machine Learning for Asset
   Managers*, cap. 8) prescrive di **raggruppare le prove per somiglianza dei rendimenti** e usare come N il numero di gruppi.
2. **V è la varianza degli Sharpe dei gruppi**, non delle prove una per una: ogni gruppo diventa una strategia (la media dei
   suoi membri) e si misura il suo Sharpe. Contando le prove una per una, le famiglie con tante varianti pesano di più e le
   strategie che perdono per costruzione (per esempio le regole di TradingView a 4 ore con il 40-58% l'anno di spese) allargano
   V e alzano l'asticella anche per strategie che con loro non hanno niente a che fare.

Il livello del 95% resta: è il livello standard. La revisione non tocca le altre condizioni dell'esame (intervallo sopra zero,
anni, ultimo anno, costi doppi, trimestri, più del Bitcoin).

## 3. La procedura corretta (fissata qui, prima del calcolo)

* **Le serie**: i rendimenti netti settimanali di ogni prova a portafoglio salvati nei `risultati_*` (quelli giornalieri
  sommati per settimana); per le prove a operazioni senza serie salvata (34, 35, 37, 39, 40, 41, 43, 45-I2) la serie si
  ricostruisce dalle operazioni salvate con il loro portafoglio; le prove senza nessuna serie (le famiglie della prova 1 e
  della 2B, i rimbalzi 4-5) contano **ognuna come un gruppo a sé** con il suo Sharpe pubblicato (scelta prudente: N più alto).
* **La somiglianza**: la correlazione dei rendimenti settimanali sulle settimane comuni (almeno 52).
* **I gruppi**: raggruppamento gerarchico a legame medio con la distanza √((1 − ρ)/2), tagliato a **ρ = 0,5** (stanno nello
  stesso gruppo le prove con correlazione media almeno 0,5). Si riportano anche i tagli a 0,3 e 0,7, solo per capire.
* **Gli Sharpe dei gruppi**: lo Sharpe della media a pesi uguali dei membri sulle loro settimane.
* **N** = numero di gruppi; **V** = varianza degli Sharpe dei gruppi; lo Sharpe corretto di ogni candidata con il suo Sharpe,
  le sue settimane, la sua asimmetria e curtosi (come `terza.sharpe_corretto`), soglia **0,95**.
* Per confronto, una seconda asticella pubblicata e diversa: il **t dello Sharpe** (Sharpe × √anni) contro **3,0**, la soglia
  che Harvey, Liu e Zhu (*Review of Financial Studies* 2016) chiedono ai fattori nuovi perché se ne provano tanti.
* **Si accetta quello che viene**: se una candidata passa, è validata sul passato con questa asticella; se no, no. Nel registro
  restano scritti tutti e due i valori, quello di prima e quello rivisto, con questo file.

## 4. Riserva

La revisione arriva dopo aver visto F5 a 0,52 con il calcolo di prima. Per questo la procedura è quella pubblicata dagli autori,
con un solo valore scelto qui (il taglio a 0,5) e i tagli 0,3 e 0,7 riportati accanto: se il verdetto cambiasse solo a uno dei
tagli, lo si dice.
