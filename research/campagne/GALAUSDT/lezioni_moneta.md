# Lezioni sulla moneta GALAUSDT (costruzione 2021-09-18 → 2023-04-19)

Idee provate e risultati: sono nella tabella di `consegna.md`. Qui le cose da ricordare.

* **I costi decidono quasi tutto a 1 ora.** Con commissione e slippage di 0,05% per lato, un giro
  costa 0,2% del prezzo, cioè 0,03-0,10 R con gli stop usati. Le entrate casuali (b) a 1 ora con
  uscite brevi stanno fra -0,05 e -0,08 R: qualunque regola di breve parte da lì.
* **Unico vantaggio netto in costruzione: short quando il last è sopra il mark più del solito
  (032)**, circa 0,06 R sopra il caso, ma l'R medio dopo i costi è +0,013 e a costi doppi -0,043.
  Lo specchio long (031) è più debole (t 1,25). Il segnale regge a ritardo, robustezza e timeframe
  vicini: lo scarto c'è, ma vale meno di un giro di costi.
* **Gruppo di varianti long di breve a 1 ora vicine alla soglia** (ritardo rispetto a BTC 011,
  volume alto 015, rottura di Williams 017; t contro il caso 1,3-1,9): dopo un'ora forte il prezzo
  di GALAUSDT tende a continuare per qualche ora. Anche il controllo positivo col ritardo di una
  barra (entrare dopo un'ora già in salita) batte il caso (t 3,7). Due ritocchi di 011 (filtro di
  volatilità, stop più largo) non l'hanno portata oltre la soglia. Non è un risultato: è un
  indizio da non contare due volte.
* **Le regole di tendenza su 2-4 ore** (I-01, I-02 long) hanno R medi grandi solo per 2-3 trade del
  rialzo di fine 2021: senza i 3 migliori l'R è negativo.
* **Pompa e scarico (024) è peggio del caso** (t -2,75): dopo un'ora con salto di prezzo e volume
  enorme, lo short perde; coerente con la continuazione delle ore forti, opposto alla ricaduta.
* **Ritorno verso la media** (RSI(2) short, valore relativo rispetto a BTC, numeri tondi) perde.
* **Calendario** (lunedì, periodicità oraria, momentum dentro la giornata): come il caso.
* **Dati**: il mark manca per tre giorni interi (2022-07-31, 2022-10-02, 2023-02-24); il last parte
  il 2021-09-18, il mark il giorno prima. Nessun mese sotto la liquidità minima; volume medio da
  828 milioni al giorno (2021) a 198 milioni (2023).
* **Stop al tetto del 6%**: con 2 ATR su 4 ore lo stop tocca il tetto del bot in più di metà dei
  trade (001: 69 su 109); anche a 1 ora succede spesso nel 2021-2022 (032: 78 su 325).
