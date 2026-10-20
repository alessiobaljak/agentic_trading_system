# Programma 6 — ventiquattresima prova: F3 che cambia meno (F5, entrata al 20% e uscita al 40%)

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo**. Vale `OTTAVA.md` (F3) dove qui non si dice altro.

## 1. Perché

* F3 è il vantaggio che regge a tutti i controlli (prove 8 e 19, controllo dei dati del 20 ottobre). Ma ogni settimana
  rigira quasi tutto il portafoglio: giro medio **2,12** volte il capitale a settimana (con 1 long e 1 short), spese del
  **7,7%** l'anno (`risultati_ottava/esame.json`). Il funding di una moneta cambia lentamente: una moneta che esce appena dal
  quinto più caro di solito resta cara, e venderla per ricomprarla dopo costa.
* Con una banda (si entra fra le prime o le ultime del 20%, si esce solo quando si scende sotto il 40%) le posizioni
  restano finché il segnale è ancora forte: meno giro, meno spese, quasi lo stesso segnale. È la regola usata nella
  sedicesima prova per il modello di ogni giorno.

## 2. La regola

* Universo, segnale (−funding dei 7 giorni prima del lunedì), pesi (inverso della volatilità dei 30 giorni) come F3, dati
  corretti del 20 ottobre.
* **Long**: le monete che entrano nel 20% con il funding più basso, e restano finché sono nel 40% con il funding più basso;
  **short** lo stesso dall'alto. Una moneta che esce dall'universo esce dal portafoglio.
* Dentro ogni lato pesi secondo l'inverso della volatilità; lato long +1, lato short −1; costi e funding come F3.
* Una prova: nel conto del programma 6 diventano **48**.

## 3. L'esame

Come F3: dal **4 gennaio 2021**, `terza.esame` e `terza.esito` con lo Sharpe corretto sulle **48** prove. Si riportano anche
il giro medio, le spese l'anno, il numero medio di monete per lato e F3 sugli stessi dati (con le stesse correzioni).

## 4. Se regge

Se passa l'esame, entra nel paper accanto a F3 dalla settimana dopo. Se non passa ma fa meglio di F3 sugli stessi dati con
meno spese, nel paper si aggiunge come informazione (è lo stesso segnale eseguito meglio).
