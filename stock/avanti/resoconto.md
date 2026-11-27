# Il resoconto del lunedì — le tre strategie sul demo

Aggiornato il 2026-11-27 02:46 UTC da `python -m stock.avanti.resoconto` (solo lettura dei diari; lo SPY da Yahoo, mai nel repository). Misure chieste dalle regole e mancanti in `riepilogo.md` (audit `stock/AUDIT_2026-11-27.md`).

## La prima candela (`REGOLE.md`)

* Giorni nel giudizio: 12 (fuori regola, nel diario ma non nel giudizio: 2026-11-11); operazioni chiuse: 120; ordini «già oltre lo stop» (saltati, si contano a parte): 0.
* Totale: -1'913,53 dollari prima delle commissioni, -2'153,53 dopo la commissione stimata di Interactive Brokers.
* **Il t sui giorni** (le operazioni dello stesso giorno sono legate: un giorno è un'osservazione): guadagno medio a operazione -0,17%, t -0,48; con la commissione -0,19%, t -0,53. Contando le operazioni come indipendenti il t sarebbe -0,87. Giorni che servirebbero per arrivare a t 3 con la media netta di oggi: nessun numero (media netta non positiva).
* **Il costo vero dell'ingresso** (prezzo eseguito contro la chiusura della candela, punti base, positivo = peggio): nei giorni puntuali media +3,9, mediana +5,0, +406,24 dollari su 110 ingressi; su tutti i giorni media +10,0. Sul passato la prova 23 supponeva circa 1-2,5 punti base per lato.
* Giorni con l'ingresso dopo le 9:50 (si segnalano, `REGOLE.md`): 2026-11-09 (dalle 09:57).
* Uscite allo stop: 54; scarto contro il prezzo dello stop: media +0,5 punti base (negativo = eseguito meglio dello stop: il demo è più comodo del vero).
* **Lo SPY negli stessi giorni** (12): dall'apertura alla chiusura -5,27%, da una chiusura all'altra -3,80%; la prima candela -1,91% del capitale prima delle commissioni, -2,15% dopo.
* Il valore della prima candela nel conto (`valori.csv`, la Plancia) al 2026-11-25: -2,01% dal capitale di partenza. È diverso dal totale qui sopra perché comprende l'11 novembre (fuori regola) e le tasse americane sulle vendite che il conto addebita.

| Settimana (dal sabato) | Giorni | Operazioni | Guadagno (dollari) | Commissioni IB stimate | Netto |
|---|---|---|---|---|---|
| 2026-11-07 | 4 | 40 | +1'138,05 | 80,00 | +1'058,05 |
| 2026-11-14 | 5 | 50 | -665,75 | 100,00 | -765,75 |
| 2026-11-21 | 3 | 30 | -2'385,83 | 60,00 | -2'445,83 |

## La miscela (`MISCELA.md`)

* Dalla sera del 2026-11-12 al 2026-11-25: -3,27%; lo SPY da una chiusura all'altra negli stessi giorni -5,34%.
* I valori di fine giornata si scrivono all'ora del primo lavoro dopo la chiusura, a volte con i prezzi del dopo borsa (audit): qualche decimo di differenza in un giorno, che si annulla nei giorni dopo.

## La prova 45 (`GAMMA.md`)

* Giorni: 2; con la copertura sotto zero: 0; operazioni: 0; guadagno +0,00 dollari; giorni saltati: 0.
