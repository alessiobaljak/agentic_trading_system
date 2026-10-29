# Programma 7 — sessantunesima prova: l'inclinazione delle opzioni sul Bitcoin, verso della letteratura, misura larga (RRB)

Scritto il 29 ottobre 2026 alle 00:55 UTC (commit `0cfd8dbc`), **prima di calcolare l'inclinazione larga sul Bitcoin**. È trading di ogni
giorno, sul solo Bitcoin.

## 1. Da dove viene (da dichiarare)

* **Il verso è quello scritto prima di qualunque dato**: quello della letteratura (Neo 2026) e della prova 121. Quando le opzioni da salita
  sono più care del solito, il prezzo tende a salire: si compra.
* **Cosa si è già visto sullo stesso segnale**:
  * **prova 121**: Bitcoin, misura stretta (2 ore, scadenze 20-45 giorni, almeno 5 operazioni per parte), solo 773 giorni validi. Questo
    verso perdeva (Sharpe −0,34; correlazione con il giorno dopo −0,117);
  * **prova 122**: Ether, misura larga (8 ore, scadenze 7-60 giorni, almeno 10 per parte), 1.959 giorni validi. Il verso opposto perdeva
    molto, quindi questo verso andava bene sull'Ether.
* **Perché questa prova**: la misura larga sul Bitcoin non è mai stata calcolata. Se il segnale è vero, deve reggere anche lì. Se sul
  Bitcoin con la misura larga non regge, il risultato dell'Ether è con buona probabilità un caso.
* **Riserva**: la prova nasce dopo aver visto l'Ether, e le due monete si muovono insieme. Nel conto.

## 2. La regola (la misura della prova 122, sul Bitcoin)

* **Le operazioni**: quelle sulle opzioni del Bitcoin di Deribit fra le **16:00 e le 24:00 UTC**, dal 1° aprile 2021 al 25 ottobre 2026.
  Si salva solo l'inclinazione di ogni giorno (`research/data/deribit_rr_btc_larga/`).
* **La misura**:
  * scadenze fra **7 e 60 giorni**;
  * opzioni d'acquisto con il delta fra 0,15 e 0,35, opzioni di vendita fra −0,35 e −0,15;
  * almeno **10** operazioni per parte;
  * l'inclinazione è la mediana della volatilità implicita delle prime meno quella delle seconde.
* **Il segnale per il giorno d + 1**: l'inclinazione del giorno d meno la mediana dei 90 giorni prima (almeno 45 giorni validi).
  * Sopra zero: **long** il perpetuo del Bitcoin.
  * Sotto zero: **short**.
  * Se il segnale manca, resta la posizione del giorno prima.
* **Costi e funding**: come la prova 121.
* **Una prova a portafoglio**: nel conto delle prove diventano **218**.

## 3. L'esame

* **Come la prova 121**: lo Sharpe corretto con l'aggiunta sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **Se regge**, passa da un revisore separato insieme al risultato dell'Ether (la prova 122 letta al contrario), e si misura in avanti
  prima di qualunque paper.
* **Per capire, senza decidere niente**: la correlazione fra il segnale e il Bitcoin del giorno dopo; per anno; la versione solo long.
