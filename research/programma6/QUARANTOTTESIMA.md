# Programma 6 — quarantottesima prova: il regista (R1)

Scritto il 22 ottobre 2026, mattina presto, **prima del calcolo**. Idea 6 della coda di `research/REGISTRO.md`, aggiornata alle
strategie di oggi (F5, M7, K2 al posto di F3, K1, M1, che erano sui dati non corretti).

## 1. Perché

Le strategie hanno periodi buoni e periodi cattivi, e i periodi tendono a durare: per i fattori di borsa è pubblicato che un
fattore che ha guadagnato nel mese prima tende a guadagnare anche nel mese dopo («factor momentum», Gupta e Kelly 2019,
«Factor Momentum Everywhere»). Il regista tiene, ogni mese, solo le strategie che nel mese prima hanno guadagnato.

## 2. La regola (valori fissati qui)

* Le serie settimanali nette di **F5**, **M7** e **K2** (`risultati_ventiquattresima`, `risultati_venticinquesima`,
  `risultati_ventottesima`), già con i loro costi.
* Il **primo lunedì di ogni mese**: una strategia è accesa se la somma dei suoi rendimenti netti delle **4 settimane prima**
  è sopra zero. Le accese si pesano a rischio uguale (l'inverso della deviazione delle 26 settimane prima, almeno 13, come
  `quindicesima.combina`); se nessuna è accesa, il mese si sta fuori.
* Costo del cambio: |variazione del peso di una strategia| × 2 (i due lati, ciascuno al 100%) × 0,07%.
* Dal 4 aprile 2022 (servono 13 settimane dal 3 gennaio 2022, inizio di M7 e K2) al 5 ottobre 2026. Una prova: nel conto del
  programma 6 diventano **107**.

## 3. L'esame

`terza.esame` e `terza.esito` sugli anni pieni 2023-2025 per i trimestri (Sharpe corretto sulle **107** prove almeno 0,95);
si riportano anche F5 + M7 + K2 a rischio uguale sempre accese (la prova 28) sulle stesse settimane e quante volte ogni
strategia è stata spenta.
