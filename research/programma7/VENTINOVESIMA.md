# Programma 7 — ventinovesima prova: la seconda tranche delle monete nuove, dal 37° al 67° giorno (N3B2)

Scritto il 25 ottobre 2026, alle 06:50 UTC, **prima di scaricare le candele e prima di qualunque calcolo**. Idea 59 della coda di
`research/REGISTRO.md`. Vale `programma6/TRENTESIMA.md` e `TRENTADUESIMA.md` (N3 sul passato di Binance) dove qui non si dice altro.

## 1. Perché, e il dubbio

La regola delle monete nuove vende dal 7° giorno di vita per 30 giorni (+4,29% a operazione su 613, prova 32). Nei mesi dopo arrivano
gli sblocchi delle prime allocazioni (squadra, investitori: prova 74, le date pubbliche) e i market maker della quotazione riducono il
sostegno: la discesa potrebbe continuare. **Il dubbio scritto prima**: senza uscita di protezione lo short a 7-60 giorni perdeva (N1,
prova 18: −18,5% l'anno) per le poche monete che esplodono; con l'uscita a +30% di N3 la coda è tagliata, ma la pressione dei
venditori della novità (chi ha comprato il primo giorno) si esaurisce nel primo mese. Probabilità bassa-media.

## 2. La regola (valori fissati qui)

* **Le stesse monete della prova 32** (le 613 monete nuove di Binance dal 2021), con le stesse condizioni (volume il giorno prima).
* **Entrata all'apertura del 37° giorno** di vita (il giorno dopo la fine della prima tranche), short la moneta e long il Bitcoin per
  lo stesso valore; **uscita a +30%** dall'entrata (candele a 1 ora, 1% di scarto) o **dopo 30 giorni**; costi e funding come N3.
* Le candele orarie dal 37° al 69° giorno dall'archivio di Binance (file mensili, come la prova 32).
* Una prova a eventi: nel conto diventano **160**, le prove a eventi **25**.

## 3. L'esame

Come N3 (`trentesima.esame`): media sopra zero con **p ≤ 0,01**, positiva nelle due metà e senza i 5 migliori; contando le 25 prove a
eventi **p ≤ 0,0004**. Si riportano la quota di uscite a +30%, per anno, la versione senza uscita, e il confronto con N3 (prima
tranche) sulle stesse monete; il portafoglio con il 5% a operazione (al massimo 20) e lo Sharpe corretto.
