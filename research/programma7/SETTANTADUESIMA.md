# Programma 7 — settantaduesima prova: la pompa del pronti con i long intrappolati (PM)

Scritto il 30 ottobre 2026 alle 04:23 UTC (ora dell'orologio), **prima di qualunque calcolo dei rendimenti**. È l'idea 109 della coda
(dalla ricerca nelle pubblicazioni del 29 ottobre). Fino a qui si sono solo contati i giorni di picco (2.321, vedi la sezione 2), senza
guardare nessun prezzo dopo.

## 1. Perché

* **Come funziona la manipolazione, secondo la fonte**: chi manipola compra il pronti di una moneta poco scambiata (il pronti fa da
  indice al perpetuo) mentre è già venduto sul perpetuo; i piccoli vedono il prezzo salire ed entrano long a leva sul perpetuo; poi il
  pronti viene lasciato cadere, e i long rimasti chiudono vendendo nei giorni dopo.
* **La fonte**: Wang e Zhang, «Spot-Futures Manipulations in Cryptocurrency Markets» (SSRN 5125326; letto solo da un riassunto di terzi,
  che segnala conti non riconciliati): più di 300 altcoin di Binance, 2020-2024; i giorni di picco con le tracce della manipolazione
  (nelle ore prima del picco il premio del perpetuo scende, le posizioni aperte salgono, i conti grandi riducono i long) fanno −1,64%
  nelle 24 ore dopo rispetto agli altri picchi (t 3,04).
* **I dubbi scritti prima**:
  * la famiglia delle fiammate (prove 62, 75, 76, 104) è sempre andata male;
  * il numero della fonte è un confronto fra picchi, non un guadagno: anche gli altri picchi possono salire;
  * la fonte non l'abbiamo letta per intero.

## 2. La regola (fissata qui)

* **Il giorno di picco**: il massimo del giorno è almeno 1,2 volte il più alto fra l'apertura e la chiusura del giorno (`seconda.pannello`),
  su un perpetuo con almeno 30 giorni di vita e almeno 2 milioni di dollari scambiati al giorno in media nei 30 giorni prima; tutte le
  monete tranne il Bitcoin; dal 6 dicembre 2021 (i dati delle posizioni a 5 minuti esistono da lì) al 30 settembre 2026. Il conto fatto:
  2.321 giorni di picco (2022: 112, 2023: 86, 2024: 133, 2025: 959, 2026: 1.026).
* **L'ora del picco**: l'ora con il massimo più alto del giorno (candele orarie).
* **La bandiera della manipolazione**, tutte e tre insieme, fra 6 ore prima dell'ora del picco e l'ora del picco:
  * l'indice del premio del perpetuo (candele orarie dell'archivio pubblico) chiude più basso nell'ora prima del picco che 6 ore prima;
  * l'interesse aperto in dollari (i dati a 5 minuti dell'archivio pubblico) è più alto all'inizio dell'ora del picco che 6 ore prima;
  * il rapporto fra long e short dei conti grandi («sum_toptrader_long_short_ratio») è più basso all'inizio dell'ora del picco che 6 ore
    prima.
* **L'operazione**, come la prova 105 (`quarantatreesima.operazione`, con un giorno di tenuta): short il perpetuo e long il Bitcoin per lo
  stesso valore dall'apertura del giorno dopo il picco, uscita dopo 24 ore o quando il massimo orario sale del 30% sopra l'entrata; costi
  a mercato e funding.
* **Una prova a eventi**: nel conto delle prove diventano **231**, le prove a eventi **41**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): sui picchi con la bandiera, media per evento sopra zero
  con **p ≤ 0,01**, positiva nelle due metà e senza i 5 eventi migliori, **e sopra il controllo** (differenza con p ≤ 0,05). Contando le
  41 prove a eventi la soglia è **0,00025**.
* **Il controllo**: la stessa operazione sui picchi senza la bandiera (il confronto della fonte).
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: quanti picchi hanno la bandiera e quanti non hanno i dati; ognuna delle tre condizioni da sola;
  per anno; il Bitcoin tenuto contro; le tenute di 3 giorni.
