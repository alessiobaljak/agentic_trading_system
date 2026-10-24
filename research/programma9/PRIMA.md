# Programma 9 — prima conferma: le due combinazioni scelte dall'esplorazione (P9A, P9B)

Scritto il 24 ottobre 2026, alle 16:20 UTC, **dopo l'esplorazione sul 2022-2023 (`ESPLORAZIONE.md`) e prima di leggere il periodo di
conferma** (`research/data/p9/conferma.pkl`, mai aperto finora). Fra le ~10.000 caselle dell'esplorazione si scelgono le due con un
meccanismo chiaro, un orizzonte di più giorni (i costi) e un'aggiunta rispetto agli ingredienti da soli; le caselle a 1 giorno e
quelle «di mezzo» senza un perché restano fuori.

## P9A — «la folla compra sui massimi»

* **Casella**: monete nel terzo più alto per vicinanza al massimo dei 30 giorni (`dist_hi30`) **e** nel terzo più basso per
  differenza fra il rapporto long/short dei conti grandi e quello di tutti i conti (`ls_diff`): vicino ai massimi i conti piccoli
  sono più long dei grandi.
* **Perché**: sui massimi chi ha posizioni grandi vende a chi arriva tardi; quando la folla è più long dei grandi, il massimo è una
  distribuzione e il prezzo scende. Nell'esplorazione: −1,27% in 7 giorni contro la media dell'universo (t −3,5), −0,15% a 1 giorno
  (t −2,7); gli ingredienti da soli −0,17% e −0,24%.
* **Strategia**: ogni giorno, short le monete della casella per **7 giorni** contro la media dell'universo.

## P9B — «la leva già pulita quando il mercato scende»

* **Casella**: monete nel terzo più basso per variazione dell'interesse aperto in 30 giorni (`oi30`: chi ha già perso più leva)
  **quando** il Bitcoin è sceso più del **6,07%** nei 30 giorni prima (il terzo più basso del 2022-2023, soglia fissata qui).
* **Perché**: quando il mercato scende, le vendite forzate vengono dalle posizioni a leva; le monete che hanno già perso la loro leva
  hanno meno vendite forzate davanti. Nell'esplorazione: +0,40% in 3 giorni (t 3,5), +0,12% a 1 giorno, +0,64% a 7; con il mercato
  che non scende la casella non dice niente.
* **Strategia**: ogni giorno con il mercato in calo, long le monete della casella per **3 giorni** contro la media dell'universo.

## Il conto (uguale per le due)

* Ogni giorno t è una «coorte»: il rendimento della casella nei giorni dopo meno la media dell'universo (`y7` o `y3`), meno i costi
  (entrata e uscita di ogni moneta: `seconda.costi_moneta`, due volte; la copertura con l'universo: 0,05% due volte), più il funding
  (lo short incassa, la copertura paga la media). Il capitale è diviso fra le coorti aperte: ogni coorte pesa 1/h.
* La serie settimanale somma le coorti che si chiudono nella settimana, divise per h. Periodo: **dal 1° gennaio 2024 al 26 giugno 2026**.
* Esame come il programma 7: Sharpe settimanale, ogni anno, Sharpe corretto con l'aggiunta, t; vale la decisione del proprietario
  del 24 ottobre (da 0,90 in su, ogni anno positiva, t sopra 3). Si riporta anche ciascun ingrediente da solo con lo stesso conto.
* **Due prove nel conto: diventano 146** (prima la prova 78 in calcolo).
