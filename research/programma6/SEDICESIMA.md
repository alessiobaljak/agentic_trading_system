# Programma 6 — sedicesima prova: il modello che unisce gli indicatori, ogni giorno (M3)

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo**. Vale `QUATTORDICESIMA.md` (ingredienti, modello ad
alberi, costi) dove qui non si dice altro. Idea 2 della coda di `research/REGISTRO.md`.

## 1. Perché

* M1 (prova 14) decide una volta a settimana; fra gli ingredienti che contano di più ci sono segnali di **un giorno**
  (crescita dell'interesse aperto di 1 giorno, rendimento peggiore del mese, ampiezza della giornata). Decidere ogni giorno
  usa quell'informazione mentre è fresca e dà 7 volte più decisioni, quindi più prove indipendenti.
* Il rischio è il costo: cambiare posizioni ogni giorno costa. Per questo una regola che cambia poco: si entra fra le
  migliori (o peggiori) del 20% e si esce solo quando si scende sotto il 40%.

## 2. La regola

* **Universo**: ogni giorno, le monete dell'universo della settimana (le 100 più scambiate, come la terza prova).
* **Ingredienti**: quelli di M1 (`quattordicesima.py`), calcolati alla chiusura di **ogni giorno** con i soli dati fino a
  quel giorno, portati al rango fra le monete dell'universo; più lo stato del mercato dello stesso giorno.
* **Obiettivo**: il rango del rendimento del **giorno dopo** (dall'apertura del giorno dopo all'apertura di quello dopo
  ancora).
* **Modello**: lo stesso di M1 (alberi, 300 iterazioni, passo 0,05, 15 foglie, almeno 200 esempi per foglia, L2 1, seme
  2026), riallenato **ogni 28 giorni** sugli ultimi **730 giorni** già conclusi (almeno 365).
* **Portafoglio**: long le monete che entrano nel 20% con la previsione più alta e restano finché sono nel 40% più alto;
  short lo stesso dal basso; dentro ogni lato pesi secondo la volatilità dei 30 giorni; lato long +1 e short −1; si opera
  all'apertura del giorno dopo; costi (commissione a mercato e scarto) su ogni variazione di peso e funding.
* Una prova: nel conto del programma 6 diventano **38**.

## 3. L'esame

Dal **3 gennaio 2022** all'ultimo giorno: l'esame giornaliero della seconda prova (`SECONDA.md`, sezione 7: intervallo della
media giornaliera sopra zero, bootstrap a blocchi di 20 giorni; Sharpe corretto ≥ 0,95 con le **38** prove; almeno 4 anni su 5
positivi e l'ultimo anno; costi doppi), senza la condizione sull'articolo e con quella sul Bitcoin. Si riportano il giro
giornaliero, i costi l'anno e la correlazione settimanale con F3 e M1.
