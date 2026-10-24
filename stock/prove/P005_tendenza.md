# Prova 5 — seguire la tendenza dell'indice (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I5 di `REGISTRO.md`, sezione 2), committate
prima di lanciare il programma. Si conoscevano le prove 1, 2 e 4 (bocciate) e il periodo chiuso della prova 2. Famiglia diversa (si
decide una volta al mese, si tiene per settimane o mesi): il periodo chiuso si può riusare.

## Perché dovrebbe funzionare

Su molti mercati il rendimento degli ultimi 12 mesi indica il segno del mese dopo: Moskowitz, Ooi, Pedersen, «Time series momentum»,
*Journal of Financial Economics* 104 (2012). Una spiegazione è che gli investitori reagiscono in ritardo alle notizie e poi
esagerano. **Sospetto scritto prima:** sugli indici azionari di solito riduce le perdite più che aumentare il guadagno; con una
decisione al mese esce tardi nei crolli veloci (marzo 2020); le operazioni sono poche, quindi i numeri hanno poca forza statistica. E
fuori dal mercato i contanti qui rendono zero, mentre nella realtà renderebbero il tasso dei titoli di stato (prudenza: sfavorisce
la regola).

## La regola (un solo numero, quello del lavoro: 12 mesi)

* **Titoli:** SPY e QQQ, ognuno da solo. **2 prove**.
* **Periodo:** prezzi al giorno di Alpaca dal 4 gennaio 2016 al 31 dicembre 2024 (non rettificati; dividendi, frazionamenti applicati
  dal simulatore a più titoli). Le prime decisioni arrivano quando ci sono 252 sedute di storia (fine dicembre 2016).
* **Segnale:** alla chiusura dell'ultimo giorno di borsa di ogni mese, il rendimento delle ultime 252 sedute con i dividendi (chiusura
  rettificata di oggi / chiusura rettificata di 252 sedute prima − 1).
* **Posizione:** se il rendimento è sopra zero, comprati con il 98% del conto; altrimenti tutto in contanti. Ordini a mercato
  all'apertura del giorno di borsa dopo. Niente vendite allo scoperto, niente leva.

## I costi e l'esame

Costi come le prove precedenti (metà della mediana dello scarto misurato, 0,5 punti base di slittamento, commissioni Interactive
Brokers «fisso», costi raddoppiati, capitale 100'000 dollari). La serie dei rendimenti parte dal primo giorno in cui la regola può
decidere; lo stesso per il comprare e tenere.

Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del comprare e tenere lo
stesso titolo, sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi;
(4) almeno il 60% dei 32 trimestri di prova in guadagno (nei trimestri passati in contanti il guadagno è zero e **non** conta come
guadagno). Se passa: revisore separato, poi il periodo chiuso con l'esame della prova 2.
