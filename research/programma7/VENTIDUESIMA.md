# Programma 7 — ventiduesima prova: il modello ad alberi deciso ogni giorno con gli ordini limite (G20)

Scritto il 25 ottobre 2026, alle 00:35 UTC, **prima di qualunque calcolo**. Idea 33 della coda di `research/REGISTRO.md`.

## 1. Perché

Il modello che unisce gli indicatori deciso ogni giorno (M3, prova 16) faceva Sharpe 0,95 ma con spese del 23,8% l'anno a
mercato, con un solo seme e con le monete tolte dal listino ancora dentro i dati. Da allora: (a) la media di cinque semi ha reso il
modello settimanale più stabile (M6, prova 23); (b) gli ordini limite tagliano il costo di ogni variazione a circa un terzo (prove
51 e 56: 90-95% delle variazioni eseguite a limite; G1, prova 57: spese 6,7% invece di 9,5%); (c) i dati sono corretti. Se le spese
scendono da 24% a circa 8-10% e il modello resta com'era, il netto sale di 14 punti l'anno. **Il dubbio scritto prima**: K2 deciso
ogni giorno (G6, prova 63) ha fatto peggio del settimanale (1,21 contro 1,75: «decidere ogni giorno raddoppia le spese e aggiunge
rumore»), e il modello ad alberi è fragile (M1 1,35 → 0,79 con 41 settimane-moneta tolte).

## 2. La regola

* **Il modello**: quello di M3 (`programma6/sedicesima.py`: gli ingredienti di M1 alla chiusura di ogni giorno portati al rango
  fra le monete dell'universo, più lo stato del mercato; obiettivo il rango del rendimento del giorno dopo; alberi con 300
  iterazioni, passo 0,05, 15 foglie, almeno 200 esempi per foglia; riallenato ogni 28 giorni sugli ultimi 730 giorni conclusi, almeno
  365), **con cinque semi (1-5) e la media dei ranghi delle previsioni** come M6.
* **Il portafoglio**: la banda di M3 e G1 (entrata nel 20% più alto o più basso, uscita sotto il 40%), pesi secondo l'inverso della
  volatilità dei 30 giorni, lato long +1 e short −1; la decisione alla chiusura del giorno t vale per il giorno t + 1.
* **Le variazioni di peso con gli ordini limite** come G1 (`cinquantaseiesima.spese_a_limite`: ordine limite all'apertura del giorno
  per un'ora, eseguito se il prezzo passa oltre, altrimenti a mercato con il movimento contro). Funding vero.
* **Periodo**: dal 3 gennaio 2022 (il modello parte lì) al 5 ottobre 2026 (la fine del programma 7).
* Una prova: nel conto diventano **150**.

## 3. L'esame

* Come G1: le settimane dal conto giornaliero, `terza.esame` dal 3 gennaio 2022 (anni pieni 2022-2025), Sharpe corretto con
  l'aggiunta e il t; vale la decisione del proprietario del 24 ottobre (Sharpe corretto da 0,90, ogni anno positiva, t sopra 3: sul
  demo e nel paper).
* Si riportano: spese l'anno a limite e a mercato, quota di variazioni eseguite a limite, operazioni e durata media, correlazione
  settimanale con G1 e con M7, e il confronto con M3 (Sharpe 0,95, spese 23,8%) e con M7 settimanale (1,25 dal 2022).
