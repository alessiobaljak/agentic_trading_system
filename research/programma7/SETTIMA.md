# Programma 7 — settima prova: K2 decisa ogni giorno (G6) e G1 + G6 a rischio uguale

Scritto il 23 ottobre 2026, **prima del calcolo**. Un'idea nuova della coda del programma 7.

## 1. Perché

G1 (F5 decisa ogni giorno, prova 57) ha mostrato che decidere ogni giorno non toglie il vantaggio fra monete, anzi: Sharpe 1,96
contro 1,88 della versione del lunedì. K2 (prova 28; dopo la correzione delle parità Sharpe 1,745) usa tre misure invece di una: il
funding, la quota degli acquisti a mercato dei 7 giorni e la crescita dell'interesse aperto dei 7 giorni; legame con F5 solo
moderato. La stessa idea di G1 applicata a K2 dà un secondo sistema che opera ogni giorno, e messo insieme a G1 dovrebbe
oscillare meno.

## 2. La regola (valori fissati qui, tutti uguali a K2 e a G1 tranne il giorno)

* **G6**: ogni giorno alle 00:00 UTC, fra le 100 monete della settimana, il segnale di K1 (media dei ranghi di −funding dei 7
  giorni, quota degli acquisti a mercato dei 7 giorni prima, crescita dell'interesse aperto dei 7 giorni; almeno 2 su 3,
  `dodicesima.segnale_k1` calcolato sui giorni); banda 20%/40%, pesi secondo l'inverso della volatilità dei 30 giorni, ogni lato al
  100%; esecuzione con gli ordini limite come G1. Dal 3 gennaio 2022 (i dati sull'interesse aperto) al 4 ottobre 2026.
* **G1 + G6**: le due a rischio uguale (`quindicesima.combina`: pesi dall'inverso della volatilità delle 26 settimane prima).
* Due prove: nel conto diventano **128**.

## 3. L'esame

`terza.esame` e `terza.esito` sulle settimane, Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95; si riportano le entrate e
uscite al giorno, la durata media, le spese, K2 settimanale sulle stesse settimane e la correlazione con G1.
