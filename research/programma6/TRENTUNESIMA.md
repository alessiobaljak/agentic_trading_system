# Programma 6 — trentunesima prova: i due modelli insieme (M7 + M8)

Scritto il 21 ottobre 2026, mattina, **prima del calcolo**. Idea 13 della coda di `research/REGISTRO.md`. **Costruzione**:
l'idea viene dal risultato della prova 29 (M8 rende quasi come M7, ma con correlazione 0,47), quindi sul passato è solo
informazione.

## 1. Perché

Due modelli quasi ugualmente buoni (M7 Sharpe 1,25, M8 1,21 dal 2022) ma poco legati fra loro (0,47): insieme, a rischio
uguale, dovrebbero oscillare meno di ognuno.

## 2. La regola

* **M7 + M8**: il capitale diviso fra M7 (`risultati_venticinquesima/settimane_M7.csv.gz`) e M8
  (`risultati_ventinovesima/settimane_M8.csv.gz`) a rischio uguale con la volatilità delle 26 settimane prima
  (`quindicesima.combina`), dal 3 gennaio 2022.
* Una prova: nel conto del programma 6 diventano **54**.

## 3. L'esame e il paper

`terza.esame` e `terza.esito` con lo Sharpe corretto sulle **54** prove. È una costruzione: se fa meglio di M7 da solo, nel
paper si aggiunge come informazione (serve allora calcolare M8 nel paper).
