# Programma 6 — F3 contro il caso (prova a placebo)

Scritto il 19 ottobre 2026, sera, **prima del calcolo**. Il metodo (`METODO.md`, e il programma 5) chiede di confrontare
una strategia con il caso. Per F3 (`OTTAVA.md`) il caso è: **lo stesso portafoglio** (le stesse monete dell'universo ogni
lunedì, gli stessi quinti, gli stessi pesi secondo la volatilità, gli stessi costi e funding), ma con il segnale del
funding **mescolato a caso fra le monete** ogni settimana. Così si vede quanto della resa viene dal funding e quanto dal
solo modo di costruire il portafoglio (per esempio dallo stare short sulle monete più agitate).

* 200 ripetizioni (seme 2026), dal 4 gennaio 2021 come la sesta e l'ottava prova.
* **Attesa scritta prima**: lo Sharpe di F3 (1,28) sopra il **99° percentile** degli Sharpe delle 200 ripetizioni, e la
  media delle ripetizioni vicina a zero o negativa. Se non è così, il risultato di F3 non viene dal funding.

## Risultato (`risultati_ottava/caso.json`, calcolato dopo il commit qui sopra)

* F3: Sharpe **1,30**, +51,3% l'anno (con la tabella aggiornata al 18 ottobre e i contratti non-moneta tolti: 1,28 nella
  prova originale).
* Le 200 ripetizioni col segnale mescolato: Sharpe medio **−0,37** (−11,3% l'anno), 99° percentile **0,56**, massimo
  **0,64**; **nessuna** arriva a F3.
* **Attesa rispettata**: il risultato di F3 viene dal funding, non dalla costruzione del portafoglio (che da sola perde).
