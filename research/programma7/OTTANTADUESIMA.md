# Programma 7 — ottantaduesima prova: il momento delle salite continue (FP, «la rana nella pentola»)

Scritto il 31 ottobre 2026 alle 16:21 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 123 della coda, scritta oggi
con la coda vuota, dopo una ricerca nelle pubblicazioni del 2026. Trading di ogni giorno: si decide ogni giorno alle 00:00 come G1.

## 1. Perché

* **Nelle azioni il momento regge quando arriva a piccoli passi** (Da, Gurun e Warachka 2014, «Frog in the pan»): una moneta che sale
  un po' quasi ogni giorno attira poca attenzione, la gente reagisce in ritardo e la salita continua; una salita fatta di uno o due
  salti si vede subito, è già nel prezzo, e non continua. Lo stesso, al contrario, per le discese.
* **Nelle monete**: Kim, «Price Path Continuity and the Cross-Section of Cryptocurrency Returns» (SSRN 6871159, giugno 2026; **letto
  solo il breve riassunto che compare nei risultati di una ricerca, non il testo**: il sito rifiuta gli strumenti automatici) trova che una misura di continuità del
  percorso sui 14 giorni, legata all'attenzione e alla «rana nella pentola», prevede i rendimenti fra le monete e regge con altri
  orizzonti e altre misure. Il verso esatto della sua misura non l'ho letto: la regola qui sotto prende quello di Da e altri.
* **È una famiglia diversa** da quella che regge (chi paga la leva o la novità perde), ma con lo stesso perché di fondo: l'attenzione.
  Le monete «saltate» sono quelle che la folla vede; quelle che salgono piano no.
* **I dubbi scritti prima**:
  * il momento semplice fra le monete non ha retto (prova 49, Sharpe 0,05) e nei perpetui è debole (Luo 2025);
  * decidendo ogni giorno, i costi possono mangiare il segnale come nella prova 118 (il momento dei vicini);
  * metà delle monete resta fuori ogni giorno, quindi i lati sono più piccoli di quelli di G1.

## 2. La regola (fissata qui)

* **L'universo**: quello di G1 di ogni giorno (`prima.universo_del_giorno`), dal 4 gennaio 2021 (`sesta.INIZIO`) al 5 ottobre 2026
  (`prima.FINE`).
* **I numeri di ogni moneta**, il giorno g alle 00:00, con le chiusure dei giorni da g − 15 a g − 1 (solo prezzi già noti):
  * R14, il rendimento dalla chiusura del giorno g − 15 a quella del giorno g − 1;
  * la **discontinuità** ID = segno di R14 × (quota dei 14 giorni in discesa − quota dei 14 giorni in salita) (Da e altri 2014):
    più è bassa, più il movimento è fatto di tanti piccoli passi nello stesso verso.
* **Il segnale**: fra le monete dell'universo del giorno con R14 e ID noti, le monete con ID **fino alla mediana del giorno** (la metà
  più continua) hanno come segnale R14; le altre restano fuori quel giorno.
* **Il portafoglio**: come G1 (`prima.py`): banda 20/40 sul segnale (`ventiquattresima.pesi_banda`: long chi è salito di più a passi
  continui, short chi è sceso di più a passi continui), pesi secondo l'inverso della volatilità dei 30 giorni, ordini limite, costi e
  funding (`cinquantaduesima.conto`); il conto a settimana con `prima.per_settimana`.
* **Una prova**: nel conto delle prove diventano **242**.

## 3. L'esame (scritto prima)

* Lo stesso delle prove a portafoglio (`terza.esame`, `terza.esito`), con lo Sharpe corretto rivisto per tutte le prove
  (`asticella.corretto_rivisto`) e la regola del proprietario del 24 ottobre (Sharpe corretto da 0,90 in su, ogni anno positivo, t
  sopra 3).
* **In più**, perché l'idea è la continuità e non il momento: FP passa solo se il suo Sharpe sta sopra quello della stessa regola con il
  momento semplice (R14 su tutte le monete, senza il filtro), calcolato con lo stesso codice.
* **Per capire, senza decidere niente**: il momento della metà «a salti» (ID sopra la mediana); quante monete per lato; quante entrate
  e uscite al giorno; le spese; la correlazione con G1 (settimane della prova 142).
