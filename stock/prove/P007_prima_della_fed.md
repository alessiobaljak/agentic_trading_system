# Prova 7 — le 24 ore prima del comunicato della banca centrale (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I7 di `REGISTRO.md`, la parte «giorni prima delle
riunioni della banca centrale»), committate prima di lanciare il programma. Si conoscevano le prove 1-6 (bocciate) e il periodo chiuso
della prova 2. Famiglia diversa (eventi a data fissa): il periodo chiuso si può riusare.

## Perché dovrebbe funzionare

Nelle 24 ore prima del comunicato delle riunioni programmate della banca centrale americana l'indice sale in media molto più che negli
altri giorni: Lucca, Moench, «The pre-FOMC announcement drift», *Journal of Finance* 70 (2015). **Sospetto scritto prima:** Kurov,
Wolfe, Gilbert, «The disappearing pre-FOMC announcement drift», *Finance Research Letters* 40 (2021), trovano che dopo la
pubblicazione l'effetto è sparito; e gli eventi sono solo 71 in nove anni, quindi la forza statistica è poca.

## La regola (la finestra del lavoro del 2015)

* **Titoli:** SPY e QQQ, ognuno da solo. **2 prove**.
* **Date:** i 71 comunicati delle riunioni programmate dal 2016 al 2024 (`stock/dati/fomc.py`, fonte: il sito della Federal Reserve).
  Il comunicato esce alle 14:00 di New York.
* **Barre:** al minuto, come la prova 1.
* **Ingresso:** il giorno di borsa prima del comunicato, decisione alla chiusura della barra delle 13:59, acquisto a mercato all'apertura
  della barra delle 14:00, con il 98% del conto.
* **Uscita:** il giorno del comunicato, decisione alla chiusura della barra delle 13:58, vendita a mercato all'apertura della barra delle
  13:59, prima del comunicato.
* Se manca una di queste barre, l'evento salta (e si conta). Niente vendite allo scoperto, niente leva, contanti a zero negli altri
  giorni.

## I costi e l'esame

Come le prove precedenti. Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e
del comprare e tenere lo stesso titolo; (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi
doppi; (4) almeno il 60% dei 32 trimestri di prova in guadagno. Accanto, da leggere: il guadagno medio per evento e il suo t.
