# Programma 7 — sessantaduesima prova: G1 con un minimo di monete per lato (G1M)

Scritto il 29 ottobre 2026 alle 06:19 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 97 della coda, nata dalla
revisione separata di G1N (`research/programma7/REVISIONE_G1N.md`, sezione 5). Non cerca uno Sharpe più alto: toglie un rischio che le
medie non vedono, in vista dei soldi veri.

## 1. Perché

* **Nei giorni di funding uguale per molte monete G1 resta con poche monete su un lato.** Quando tante monete sono al funding di base, le
  parità prendono il rango medio e un lato si svuota.
  * Il 5 febbraio 2024 lo short aveva 5 monete, e BLZ, una moneta piccola, pesava il 47,8% del capitale.
  * I giorni con meno di 10 monete short sono 67, quelli con 5 o meno sono 8 (revisione di G1N).
* **Con i soldi veri** un rialzo improvviso di una sola moneta short così pesante può costare molto in un giorno. I conti medi del
  passato non lo pesano.
* **La regola**: quando un lato ha meno monete del necessario, si riduce l'esposizione di tutto il portafoglio invece di concentrarla.

## 2. La regola (fissata qui)

* **Tutto come G1** (`programma7/prima.py`): il funding dei 7 giorni, la banda 20/40, i pesi secondo l'inverso della volatilità, la
  decisione ogni giorno, gli ordini limite, i costi e il funding.
* **In più**: ogni giorno si contano le monete del lato long (n_L) e del lato short (n_S) di G1. Se il più piccolo dei due è sotto 10,
  tutti i pesi del giorno si moltiplicano per min(n_L, n_S) / 10. Con 5 monete short, per esempio, l'esposizione si dimezza su tutti e
  due i lati.
* **Periodo**: come G1, dal 4 gennaio 2021 al 5 ottobre 2026 (`prima.FINE`), sugli stessi dati.
* **Una variante di G1**: nel conto delle prove diventano **219**.

## 3. L'esame (scritto prima, sui rischi)

* **G1M passa se**:
  * la **discesa massima** è più bassa di quella di G1;
  * il **giorno peggiore** (il netto giornaliero più basso) è meno grave di quello di G1;
  * lo **Sharpe** non scende di più di 0,10 sotto quello di G1.

  Si calcolano tutti e due con lo stesso codice e gli stessi dati, così le differenze sono solo della regola.
* **Se passa**, la regola è una protezione da proporre per i soldi veri insieme a G1 (backlog P26), dopo un revisore separato.
* **Per capire, senza decidere niente**: quanti giorni l'esposizione scende, e di quanto in media; la settimana peggiore; per anno; il
  ricampionamento a blocchi di 8 settimane della differenza di discesa (quante volte G1M scende meno di G1).
