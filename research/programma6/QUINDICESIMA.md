# Programma 6 — quindicesima prova: F3 e M1 insieme, a rischio uguale

Scritto il 20 ottobre 2026, mattina, **prima del calcolo**. Vale `TERZA.md` (esame settimanale) dove qui non si dice altro.

## 1. Perché

* F3 (prova 8, il funding fra monete) e M1 (prova 14, il modello che unisce gli indicatori) sono **le due candidate più
  forti con le regole scritte prima**: Sharpe 1,28 e 1,35, tutte e due sopra il caso (`F3_caso.md`, `caso_M1.json`).
* Si somigliano poco: correlazione delle settimane **0,17** (`RISULTATI_QUATTORDICESIMA.md`). Due fonti di guadagno quasi
  indipendenti insieme oscillano meno di ciascuna: è il modo più vecchio e più solido di migliorare un portafoglio, e non
  richiede di scegliere niente sui dati.
* Onestà sul metodo: le due sono state scelte come le migliori su questi anni. La combinazione conta come **una prova in
  più** (nel conto del programma 6 diventano **37**) e lo Sharpe corretto ne tiene conto con tutte le altre; la prova
  pulita resta il paper. K1 (prova 12) non entra nell'esame perché sul passato è costruzione: si riporta solo come
  informazione la combinazione a tre.

## 2. La regola

* Ogni lunedì il capitale si divide fra F3 e M1 in parti **inversamente proporzionali alla volatilità delle 26 settimane
  prima** di ciascuna (solo il passato; almeno 13 settimane, altrimenti metà e metà); dentro ciascuna, le posizioni della sua
  regola. Il rendimento della settimana è la somma pesata dei due rendimenti netti (costi e funding già dentro).
* Dal 3 gennaio 2022 (M1 parte lì).

## 3. L'esame

Le condizioni della terza prova (`TERZA.md`, sezione 4) dal 3 gennaio 2022, con lo Sharpe corretto sulle **37** prove, gli
anni 2022-2026 (almeno 4 su 5), i trimestri pieni dal 2022 al 2025, i costi doppi (la somma pesata dei due a costi doppi). Si
riportano anche la discesa massima e la combinazione F3 + M1 + K1 (solo informazione).
