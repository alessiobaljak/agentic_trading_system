# Programma 7 — sessantesima prova: l'inclinazione delle opzioni al contrario, sull'Ether (RRE)

Scritto il 29 ottobre 2026 alle 00:23 UTC (ora dell'orologio), **prima di scaricare le operazioni sulle opzioni dell'Ether e prima di
qualunque calcolo sull'Ether**. Fino a qui si è contato solo quante operazioni ci sono in un giorno (più di 10.000 il 4 marzo 2024). È
l'idea 94 della coda, nata dalla prova 121. È trading di ogni giorno, sul solo Ether.

## 1. Perché, e cosa si è già visto

* **La prova 121 sul Bitcoin** ha mostrato che l'inclinazione va al contrario di quanto previsto: quando le opzioni da salita sono più
  care del solito, il giorno dopo il Bitcoin tende a scendere (correlazione −0,117).
* **La lettura**: chi compra le opzioni da salita care è l'entusiasmo dei piccoli, che paga troppo, come chi paga il funding alto (la
  famiglia di G1).
* **La direzione scritta prima, presa dal Bitcoin**: short l'Ether quando le sue opzioni da salita sono più care del solito, long quando
  lo sono meno.
* **Riserve scritte prima**:
  * il verso viene da dati già visti, ma quelli del Bitcoin; l'Ether ha le sue opzioni e il suo prezzo;
  * l'Ether e il Bitcoin si muovono insieme (le loro inclinazioni anche), quindi non è una conferma del tutto indipendente;
  * la misura è più larga di quella della prova 121, perché quella lasciava fuori il 62% dei giorni.

## 2. La misura (fissata qui)

* **Le operazioni**: quelle sulle opzioni dell'Ether di Deribit (`history.deribit.com`) fra le **16:00 e le 24:00 UTC** di ogni giorno,
  dal 1° aprile 2021 al 25 ottobre 2026. Non si salvano: per ogni giorno si salva solo l'inclinazione già calcolata
  (`research/data/deribit_rr_eth/`, fuori da git), perché le operazioni di un giorno occupano qualche megabyte.
* **Si tengono**:
  * le scadenze fra **7 e 60 giorni**;
  * le opzioni d'acquisto con il delta fra 0,15 e 0,35 e quelle di vendita fra −0,35 e −0,15 (Black e Scholes con la volatilità
    implicita dell'operazione, il prezzo dell'indice e il tasso zero).
* **L'inclinazione del giorno d**: la mediana della volatilità implicita delle opzioni d'acquisto meno quella delle opzioni di vendita,
  con almeno **10** operazioni per parte; altrimenti il giorno manca.

## 3. La regola

* **Il segnale per il giorno d + 1**: l'inclinazione del giorno d meno la mediana di quelle dei 90 giorni prima (almeno 45 validi).
  * Sopra zero: **short** il perpetuo dell'Ether.
  * Sotto zero: **long**.
  * Se il segnale manca, resta la posizione del giorno prima.
* **Costi e funding**: come la prova 121, con l'Ether. Il costo a mercato a ogni cambio di verso; il funding del giorno.
* **Una prova a portafoglio**: nel conto delle prove diventano **217**.

## 4. L'esame

* **Come la prova 121** (`terza.esame`, `terza.esito`): lo Sharpe corretto con l'aggiunta sopra 0,95, il t contro 3 e la regola del
  proprietario del 24 ottobre.
* **Se regge**, passa da un revisore separato, e prima di qualunque paper si misura in avanti: il verso è nato su dati visti.
* **Per capire, senza decidere niente**: quanti giorni mancano; la correlazione fra il segnale e l'Ether del giorno dopo; per anno; la
  versione solo short (fuori quando il segnale è sotto zero).
