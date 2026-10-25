# Programma 7 — ventitreesima prova: l'inversione fra le monete 101-200 con meno giro (G21)

Scritto il 25 ottobre 2026, alle 04:30 UTC, **prima di qualunque calcolo**. Idea 34 della coda di `research/REGISTRO.md` (in giornata,
ogni giorno). Vale `UNDICESIMA.md` (G9, prova 67) dove qui non si dice altro.

## 1. Perché

La prova 67 ha mostrato che l'inversione di un giorno fra le monete 101-200 **esiste** (+29,1% l'anno prima dei costi) ma il giro
di 17,5 volte il capitale a settimana la uccide (spese 61,2%). Due cambiamenti con un perché, non per cercare il parametro:
* **solo gli estremi**: l'inversione è più forte nei decili estremi (Zaremba e altri 2021, Nagel 2012: chi deve vendere in fretta
  spinge il prezzo di più dove la liquidità è poca); il 10% invece del 20% per lato dimezza le monete e il giro;
* **tenuta di tre giorni**: la compensazione per chi fornisce liquidità si realizza in pochi giorni, non in uno solo (Nagel 2012: una
  parte il giorno dopo, il resto nei 2-4 giorni seguenti); tenere tre giorni divide il giro per tre.
Insieme il giro scende a circa 3 volte a settimana (stima: 17,5 / 2 / 3), le spese a circa un sesto. **Il dubbio scritto prima**: il
lordo per unità di capitale cala (la parte dell'inversione dopo il primo giorno è più piccola), e le spese erano il doppio del
lordo: probabilità bassa.

## 2. La regola (valori fissati qui)

* Monete 101-200 per volume di ogni settimana, come la prova 67.
* **Ogni giorno alle 00:00 UTC**: il rendimento di ieri (apertura → apertura); **long il 10% sceso di più, short il 10% salito di
  più**; pesi secondo l'inverso della volatilità dei 30 giorni, ogni lato al 100% dentro la fetta.
* **Tre fette da un terzo del capitale**: ogni giorno si apre una fetta nuova con il segnale del giorno, che resta ferma per **tre
  giorni** e poi si chiude; il peso di una moneta è la somma delle fette che la contengono. Le variazioni di peso da un giorno
  all'altro si eseguono come la prova 67 (ordine limite all'apertura per un'ora, poi a mercato con il movimento contro; costo a
  mercato 0,05% più lo scarto dello 0,10%); funding vero.
* Dal 4 gennaio 2021 al 4 ottobre 2026. Una prova: nel conto diventano **151**.

## 3. L'esame

Come la prova 67: `terza.esame` e `terza.esito` sulle settimane, Sharpe corretto con l'aggiunta e il t; la regola del proprietario
del 24 ottobre (da 0,90, ogni anno positiva, t sopra 3). Si riportano il giro a settimana, le spese, il lordo prima dei costi, la
quota di ordini a limite, e il confronto con la prova 67 (lordo +29,1%, spese 61,2%, netto −38,4%).
