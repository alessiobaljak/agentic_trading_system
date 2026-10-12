# XRPUSDT — Lezioni sulla moneta (idee provate e risultati)

Tutto su costruzione (2020-01-06 → 2022-10-18), salvo dove è scritto validazione. Dettagli in
`consegna.md` e nel log.

* **Nessuna delle 15 idee con fonte batte il caso così com'è scritta.** Il `t` più alto contro
  l'entrata casuale con la stessa uscita è 1,77 (premio negativo del perpetuo, long a 1h).
* **Momentum** (una settimana, forza relativa contro BTC, sovrareazione giornaliera, rottura del
  canale a 4h, rottura dell'intervallo d'apertura UTC): nessun vantaggio sopra il caso. La rottura
  del canale long a 4h ha l'R medio più alto (+0,42) ma è fatto da pochi trend enormi del 2020-21
  (senza i 3 migliori −0,01).
* **Rientro dopo movimenti estremi** (1h con volume alto, RSI(2) a 4h): nessun vantaggio; il rientro
  dopo un'ora estrema è sotto il caso in tutte e due le direzioni.
* **Funding estremo** (8h): lo short dopo funding alto perde (−0,13 R); il long dopo funding negativo
  ha +0,15 R ma `t` 0,92 e quasi tutto dal 2021.
* **Calendario**: il lunedì long ha +0,10 R, `t` 1,11, negativo nel 2022; la prima mezz'ora UTC non
  prevede l'ultima.
* **BTC che guida**: XRP rimasto indietro non recupera abbastanza da pagare i costi.
* **Numeri tondi** e **squilibrio degli ordini aggressivi**: nessun effetto oltre il caso.
* **Compressione delle bande a 1h**: troppo rara (sotto i 70 trade anche allargando).
* **Premio del perpetuo sul mark**: l'unica idea vicina. Il long dopo un last molto sotto il mark
  rende +0,02 R; togliendo i crolli oltre il 10% e alzando la soglia a −0,20% diventa candidato
  (+0,17 R, `t` 2,33), ma 84 trade su 97 sono del 2020 a volume basso e in validazione la condizione
  scatta 5 volte in 14 mesi (R −0,57). Lezione: è un effetto (se c'è) dei periodi di liquidità
  scarsa, che su XRP dal 2021 non si sono più visti; da riprovare solo su monete o periodi a volume
  basso, con regole scritte prima.
* **Lo short di breve dopo un premio positivo** (perpetuo caro sul mark) non rende: −0,075 R.
