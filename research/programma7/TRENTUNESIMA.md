# Programma 7 — trentunesima prova: l'interruttore sulle perdite del conto per G1 (G1S)

Scritto il 25 ottobre 2026, alle 07:26 UTC, **prima di qualunque calcolo**. Idea 61 della coda di `research/REGISTRO.md`, nata dalla
skill di terze parti «drawdown-circuit-breaker» (tradermonty/claude-trading-skills): la skill ferma le entrate nuove dopo una perdita
del 2% in un giorno, del 5% in una settimana o dell'8% in un mese, fino al giorno, al lunedì o al mese dopo, senza alcuna validazione
dichiarata; sono soglie per chi fa trading discrezionale in giornata. Qui si prova la forma scritta nella coda, con una soglia e una
pausa sole. Vale `programma7/PRIMA.md` (G1) dove qui non si dice altro.

## 1. Perché, e il dubbio

La discesa massima di G1 (−28,8%; −23,1% nella versione neutra al beta, prova 88) è il numero che fa più paura quando ci saranno soldi
veri (backlog P26), e non abbiamo mai misurato se una pausa dopo le perdite la riduce senza mangiare il rendimento. **Il dubbio scritto
prima**: il funding fra monete tende a tornare (le settimane dopo le peggiori sono spesso di recupero: `programma6/PERDITE_F5.md`;
la prova 83 sulle uscite prudenti ha perso), quindi la pausa potrebbe saltare proprio il recupero, e paga due giri di spese (chiudere e
riaprire tutto). Probabilità bassa.

## 2. La regola (valori fissati qui)

* **G1** come nella prova 88 (`programma7/ventiseiesima.py`: pesi giornalieri, dal 4 gennaio 2021 al 5 ottobre 2026, ordini limite).
* **L'interruttore**: si tiene il conto giornaliero di G1-S (netto a mercato: lordo, spese sul giro, funding) e il suo massimo. Il giorno
  d, se il conto alla fine del giorno d−1 è sceso di **almeno il 15%** dal massimo, si chiudono tutte le posizioni e si resta fermi per
  **7 giorni** (d … d+6); dal giorno d+7 si riparte con i pesi pieni e **il massimo di riferimento si azzera al valore del conto in quel
  momento** (altrimenti un conto fermo sotto la soglia non riparte mai). Una soglia, una pausa: nessun'altra variante.
* Le spese del giro (chiusura e riapertura) si pagano come in G1: a mercato per decidere la pausa, con gli ordini limite nel conto
  finale (`cinquantaseiesima.spese_a_limite` sui pesi finali), come nella prova 88.
* **Controllo**: lo stesso numero di pause di 7 giorni messe a caso nel periodo (20 estrazioni, seme 2026): media di Sharpe e discesa.
* Una prova nel conto (G1-S): **163**.

## 3. L'esame e cosa si riporta

Come le prove 86-89: `terza.esame` dal 4 gennaio 2021, Sharpe corretto rivisto per gruppi, t, la regola del proprietario. G1-S «aggiunge
qualcosa» solo se la discesa massima è minore di quella di G1 **senza** che lo Sharpe scenda sotto quello di G1, e meglio delle pause a
caso. Si riportano: quante pause e quanti giorni fermi; quanto avrebbe fatto G1 nei giorni di pausa (se positivo, la pausa ha saltato
il recupero); le 15 settimane peggiori di G1 rifatte con l'interruttore; la discesa massima e per anno.
