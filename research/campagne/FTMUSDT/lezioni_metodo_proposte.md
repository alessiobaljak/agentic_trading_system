# FTMUSDT — lezioni di metodo proposte (solo metodo e trappole dei dati)

* **I mesi illiquidi all'inizio accorciano la costruzione più di quanto dicano le
  date.** Con il primo dato a fine settembre 2020 e quattro mesi sotto la liquidità
  minima, una costruzione di 851 giorni ha trade solo in due anni: la verifica di
  stabilità per anno conterebbe su due anni soli. Conviene guardarlo in Fase 0, prima di
  scegliere i timeframe.
* **Le idee giornaliere con tenute di giorni arrivano raramente a 70 trade su due anni
  utili**: otto scarti su 15 idee. Scriverli prima di vedere i risultati dell'idea
  permette l'allentamento della regola 6; dopo aver visto la variante gemella non più
  (caso I-04): conviene contare tutte le varianti di un'idea prima di testarne una.
* **Il guardiano legge come percorsi i testi dentro i comandi**: note, messaggi di commit
  e espressioni di sed vanno in file; niente awk, niente asterischi (la shell li risolve
  nella cartella di lavoro, che può essere la radice del repository), niente `cd` nella
  cartella madre `research/`; le stampe dei comandi in background vanno scritte dagli
  script in `data/insample/<SIMBOLO>/`, perché il file di uscita del comando sta in una
  cartella non ammessa. Un comando in background parte dalla cartella della sessione, non
  da quella dell'ultimo `cd`: mettere il `cd` nello stesso comando.
* **Stop in ATR giornalieri su un'altcoin**: distanze del 30% e oltre, quindi stop che
  il bot non esegue e violazioni del margine dalla liquidazione (con la leva calcolata
  sul nozionale). Chi disegna idee a 1d lo sappia prima.
* **Indicatori calcolati una volta su tutta la serie** (causali) e letti per indice
  rendono le 200 simulazioni della (b) veloci anche a 30 minuti; il controllo positivo
  con lo sguardo al futuro ha confermato che il quadro non guarda avanti.
