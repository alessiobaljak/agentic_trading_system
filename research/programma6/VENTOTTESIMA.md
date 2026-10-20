# Programma 6 — ventottesima prova: K1 con la banda (K2) e le tre insieme (F5 + M7 + K2)

Scritto il 20 ottobre 2026, sera, **prima di qualunque calcolo**. Idea 11 della coda di `research/REGISTRO.md`. Vale
`DODICESIMA.md` (K1), `VENTIQUATTRESIMA.md` (la banda) e `VENTICINQUESIMA.md` (F5 + M7) dove qui non si dice altro.

## 1. Perché

* La banda (entrata nel 20%, uscita sotto il 40%) ha migliorato F3 (da 1,28 a 1,93) e il modello (da 1,08 a 1,25): stesso
  segnale, meno giro e meno spese, più monete per lato. K1 (funding, acquisti a mercato, interesse aperto) cambia posizioni
  ogni settimana come loro.
* K1 è poco legato a M1 (0,03) e mediamente a F3 (0,39): come terza gamba può abbassare ancora le oscillazioni.
* **K1 è una costruzione** (i versi di due ingredienti li avevo visti prima di scriverla, `DODICESIMA.md`): K2 e la
  combinazione con K2 lo restano. Sul passato sono informazione; la prova vera è il paper.

## 2. Le regole

* **K2**: il segnale di K1 (`dodicesima.segnale_k1`) con la banda di F5 (`ventiquattresima.pesi_banda`), pesi secondo
  l'inverso della volatilità dei 30 giorni, costi come K1. Dal 3 gennaio 2022 (come K1).
* **F5 + M7 + K2**: il capitale diviso fra le tre a rischio uguale, con la volatilità delle 26 settimane prima
  (`quindicesima.combina`).
* Due prove: nel conto del programma 6 diventano **52**.

## 3. L'esame

Dal **3 gennaio 2022**, `terza.esame` e `terza.esito` con lo Sharpe corretto sulle **52** prove. Si riportano anche K1 e
F5 + M7 sugli stessi anni, per confronto.

## 4. Nel paper

Sono costruzioni: se fanno meglio della loro versione senza banda (K2 di K1) o senza la terza gamba (F5 + M7 + K2 di F5 +
M7), nel paper si aggiungono **come informazione**; non diventano candidate con il loro verdetto.
