# Programma 7 — sessantatreesima prova: l'indice di paura e avidità sul Bitcoin (FG)

Scritto il 29 ottobre 2026 alle 06:48 UTC (ora dell'orologio), **prima di qualunque calcolo**. Fino a qui si è guardato solo quanti giorni
ci sono (3.189 dal 1° febbraio 2018). È un'idea del proprietario («mi viene in mente anche fear and greed»), la 100 della coda, ed è nuova:
la prova 47 misurava la paura con le opzioni, non con questo indice.

## 1. Perché

* **L'indice** (alternative.me, gratis) dà ogni giorno un numero da 0 (paura estrema) a 100 (avidità estrema). Lo calcola dalla
  volatilità, dal momento e dal volume, dai social, dal peso del Bitcoin e dalle ricerche su Google.
* **La lettura classica**: «compra quando gli altri hanno paura». Nella paura estrema vende chi è costretto o chi si spaventa, e il prezzo
  scende sotto il giusto. Nell'avidità estrema compra chi insegue, e il prezzo sale troppo. È la nostra famiglia («chi paga l'entusiasmo
  perde»), letta con un indice di tutto il mercato.
* **I dubbi scritti prima**:
  * è un indice famoso e gratis, quindi tutti lo guardano;
  * le prove sul solo Bitcoin non hanno mai battuto il Bitcoin tenuto (prove 13, 47, 72, 99);
  * nelle discese lunghe (2022) la paura estrema dura mesi e il prezzo continua a scendere.

## 2. Le regole (fissate qui, due varianti)

* **Dati**: l'indice giornaliero (`api.alternative.me/fng`), salvato in `research/data/paura_avidita.json` fuori da git. Il valore del
  giorno d si usa solo per la decisione del giorno d + 2: un giorno di ritardo in più, perché non si sa a che ora esatta del giorno viene
  pubblicato.
* **Mercato**: il perpetuo del Bitcoin, dal 1° gennaio 2020 al 25 ottobre 2026; costo a mercato del Bitcoin a ogni entrata e uscita;
  funding del giorno.
* **PA, la paura**: si compra il Bitcoin quando l'indice è a **20 o sotto**; si esce quando torna a **50 o sopra**.
* **AV, l'avidità**: si vende il Bitcoin quando l'indice è a **80 o sopra**; si esce quando scende a **50 o sotto**.
* **Due varianti**: nel conto delle prove diventano **221**.

## 3. L'esame

* **Per ognuna, come le prove a portafoglio** (`terza.esame`, `terza.esito`, con il Bitcoin come riferimento): lo Sharpe corretto con
  l'aggiunta sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **Se una regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**:
  * quanti giorni si è dentro, quante operazioni, per anno;
  * il Bitcoin tenuto negli stessi anni;
  * la media del Bitcoin nei 30 giorni dopo, per fasce dell'indice (0-20, 20-40, 40-60, 60-80, 80-100);
  * le due varianti insieme.
