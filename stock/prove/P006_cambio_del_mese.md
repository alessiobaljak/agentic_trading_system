# Prova 6 — il cambio del mese (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I7 di `REGISTRO.md`, sezione 2, la parte
«inizio del mese»), committate prima di lanciare il programma. Si conoscevano le prove 1-5 (bocciate) e il periodo chiuso della prova 2.
Famiglia diversa (calendario, pochi giorni al mese): il periodo chiuso si può riusare.

## Perché dovrebbe funzionare

Il guadagno delle azioni americane si concentra nei giorni a cavallo della fine del mese: Lakonishok, Smidt, «Are seasonal anomalies
real? A ninety-year perspective», *Review of Financial Studies* 1 (1988); McConnell, Xu, «Equity returns at the turn of the month»,
*Financial Analysts Journal* 64 (2008), che lo trovano dall'ultimo giorno di borsa del mese ai primi tre del mese dopo. Una
spiegazione sono i flussi di denaro che arrivano a date fisse (stipendi, fondi pensione). **Sospetto scritto prima:** è pubblicato da
decenni; sulle crypto il «giorno migliore del mese» non reggeva; e la regola sta investita circa 6 giorni su 21.

## La regola (la finestra del lavoro del 2008, adattata a ordini eseguiti all'apertura)

* **Titoli:** SPY e QQQ, ognuno da solo. **2 prove**.
* **Periodo:** prezzi al giorno di Alpaca dal 4 gennaio 2016 al 31 dicembre 2024, con dividendi e frazionamenti (simulatore a più
  titoli).
* **Ingresso:** alla chiusura del terz'ultimo giorno di borsa del mese si decide; si compra con il 98% del conto all'apertura del
  penultimo giorno di borsa. Così la posizione copre per intero l'ultimo giorno del mese (la finestra del lavoro parte dalla chiusura
  del penultimo giorno; noi entriamo qualche ora prima, all'apertura del penultimo).
* **Uscita:** alla chiusura del terzo giorno di borsa del mese dopo si decide; si vende all'apertura del quarto.
* Niente vendite allo scoperto, niente leva, contanti a rendimento zero fuori dalla finestra.

## I costi e l'esame

Come la prova 5 (costi delle prove precedenti; la serie dei rendimenti e il comprare e tenere partono dal primo ingresso). Passa la
ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del comprare e tenere lo stesso
titolo; (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32
trimestri di prova in guadagno. Se passa: revisore separato, poi il periodo chiuso con l'esame della prova 2.
