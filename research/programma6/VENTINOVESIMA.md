# Programma 6 — ventinovesima prova: il modello con un obiettivo diverso (M8)

Scritto il 21 ottobre 2026, notte, **prima di qualunque calcolo**. Idea 3 della coda di `research/REGISTRO.md`. Vale
`VENTICINQUESIMA.md` (M7: cinque semi, media dei ranghi, banda) dove qui non si dice altro.

## 1. Perché

* M1, M6 e M7 imparano a prevedere il **rango** del rendimento della settimana dopo: sanno chi sale più degli altri, ma non
  di quanto. Il rango toglie peso alle settimane in cui le differenze fra monete sono grandi (quelle che contano di più per il
  portafoglio) e lo dà a quelle in cui sono piccole (rumore).
* **M8**: lo stesso modello ma con l'obiettivo **di quanto la moneta fa meglio della media delle monete della settimana**
  (rendimento meno la media), tagliato all'1% e al 99% di ogni settimana perché poche esplosioni non dominino l'allenamento.

## 2. La regola

* Come M7 (dati corretti, cinque modelli con i semi 1-5, media dei ranghi delle cinque previsioni, banda: entrata nel 20%,
  uscita sotto il 40%, pesi secondo l'inverso della volatilità dei 30 giorni, costi come M1), cambia solo l'obiettivo
  dell'allenamento: il rendimento della settimana meno la media delle monete dell'universo, tagliato ai percentili 1 e 99
  della settimana.
* Una prova: nel conto del programma 6 diventano **53**.

## 3. L'esame

Dal **3 gennaio 2022**, `terza.esame` e `terza.esito` con lo Sharpe corretto sulle **53** prove; si riporta M7 sugli stessi
dati per confronto e la correlazione fra i due.

## 4. Nel paper

Se passa l'esame entra nel paper come candidata dalla settimana dopo; se no, ma fa meglio di M7, come informazione.
