# Prova 1 — l'ultima mezz'ora segue il resto della giornata (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I1 di `REGISTRO.md`, sezione 2), committate
prima di lanciare il programma. Nessuno ha guardato i rendimenti dell'ultima mezz'ora di SPY o QQQ prima di scriverle.

## Perché dovrebbe funzionare

Chi vende opzioni e i fondi a leva devono ricoprirsi nella direzione del movimento della giornata, e lo fanno soprattutto verso la
chiusura: Gao, Han, Li, Zhou, «Market intraday momentum», *Journal of Financial Economics* 129 (2018); Baltussen, Da, Lammers,
Martens, «Hedging demand and market intraday momentum», *Journal of Financial Economics* 142 (2021). Si usa la versione di Baltussen
e altri: il rendimento dalla chiusura di ieri fino a mezz'ora dalla chiusura di oggi indica la direzione dell'ultima mezz'ora.
**Sospetto scritto prima:** l'effetto spiega poco (circa il 2% dei movimenti nel lavoro del 2018), gli studi non contano i costi, ed è
pubblicato da anni (potrebbe essere stato consumato).

## La regola (nessun parametro libero)

* **Titoli:** SPY e QQQ, ognuno da solo. Contano come **2 prove** nel registro.
* **Periodo:** tutta la ricerca, dal 4 gennaio 2016 (primo giorno di Alpaca) al 31 dicembre 2024. Il periodo chiuso (dal 2025) non si
  tocca.
* **Barre:** al minuto, prezzi non rettificati di Alpaca (tutte le borse), solo dentro la seduta (dall'apertura alla chiusura del
  calendario di borsa; nei giorni di chiusura anticipata la chiusura è quella vera, per esempio le 13:00).
* **Segnale**, alla chiusura del minuto che finisce mezz'ora prima della chiusura (di solito la barra delle 15:29, che finisce alle
  15:30): r = prezzo di chiusura di quella barra / chiusura dell'ultima barra della seduta di ieri − 1.
* **Ingresso:** se r > 0 si compra, se r < 0 si vende allo scoperto, se r = 0 niente. Ordine a mercato, eseguito all'apertura della
  barra dopo (le 15:30).
* **Uscita:** ordine a mercato deciso alla chiusura della penultima barra della seduta, eseguito all'apertura dell'ultima (le 15:59).
  Nessuna posizione resta aperta di notte.
* **Quanto:** tutto il valore del conto diviso per il prezzo della decisione, azioni intere, senza leva (il simulatore rifiuta
  l'ordine se, al prezzo eseguito, servirebbe leva: in quel caso la giornata salta e viene contata).
* **Giorni esclusi:** il primo giorno (non c'è ieri), e i giorni segnalati dal controllo dei minuti (`stock/dati/ESITO_MINUTI.md`:
  SPY 12 agosto 2019, QQQ 22 febbraio 2016), o un giorno in cui manca la barra del segnale, dell'ingresso o dell'uscita.

## I costi

* **Scarto:** metà della mediana misurata (`stock/dati/ESITO_CONTROLLI.md`): SPY 0,37 punti base → 0,185; QQQ 0,56 → 0,28.
* **Slittamento:** 0,5 punti base in più per ogni ordine a mercato (scelto qui, senza misura: è un margine).
* **Commissioni:** Interactive Brokers, piano «fisso»: 0,005 dollari per azione, minimo 1 dollaro, massimo l'1% del valore
  **(da verificare sul listino ufficiale, che non si lascia leggere dai programmi)**. Le piccole tasse americane sulle vendite non
  sono contate a parte: le copre la versione con i costi raddoppiati.
* Capitale di partenza 100'000 dollari.

## L'esame (fissato qui)

La prova passa la ricerca se, sul periodo intero e per quel titolo, **tutte** queste condizioni sono vere:

1. **Lo Sharpe annuo dopo i costi è più alto di quello del comprare e tenere lo SPY** sullo stesso periodo (prezzi rettificati da noi
   con dividendi e frazionamenti, i 3 dividendi mancanti aggiunti: `stock/dati/integrazioni.py`). Si confronta lo Sharpe e non il
   guadagno totale perché la strategia è investita mezz'ora al giorno: battere l'indice nel guadagno vorrebbe dire usare la leva, che
   è una decisione del proprietario e viene dopo.
2. **Lo Sharpe corretto per i tentativi ≥ 0,95** (Bailey e López de Prado 2014, come `research/programma6/ASTICELLA.md`): N = numero
   di gruppi di prove nel conto delle azioni (prove con correlazione dei rendimenti giornalieri ≥ 0,5 nello stesso gruppo); V =
   varianza degli Sharpe dei gruppi, ma finché i gruppi sono meno di 5 si usa V = 1/T (la varianza dello Sharpe stimato su T giorni
   quando il vantaggio vero è zero), perché con meno di 5 valori la varianza non si stima. Con N = 1 la soglia è Sharpe vero
   sopra zero (la formula con un solo tentativo non ha massimo «per caso»). Accanto, il t dello Sharpe contro 3
   (Harvey, Liu e Zhu 2016), solo da leggere.
3. **Con i costi raddoppiati lo Sharpe resta sopra zero.**
4. **Almeno il 60% dei trimestri** (le finestre di prova da 3 mesi, `stock/simulatore/finestre.py`) chiude in guadagno dopo i costi.

Se passa: revisore separato, poi il periodo chiuso, una volta sola. Se non passa: bocciata, con il risultato nel registro. In ogni caso
si scrivono anche i numeri senza costi, per capire quanto mangiano i costi.
