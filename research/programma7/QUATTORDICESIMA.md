# Programma 7 — quattordicesima prova: il funding al tetto con l'entrata subito (G12)

Scritto il 23 ottobre 2026, **prima del calcolo**. Ultima parte dell'idea 4 di `METODO.md` («il funding al tetto con l'entrata
scelta dentro la giornata»).

## 1. Perché

E4 (prova 26) vende per 7 giorni (contro il Bitcoin) le monete a cui Binance accorcia l'intervallo del funding con il funding
positivo: +11,67% a evento su 62. Entra però all'**apertura del giorno dopo** l'evento, e dall'apertura del giorno dell'evento a
quella del giorno dopo lo short ha già guadagnato in media il 3,92% (la «prima reazione», `RISULTATI_VENTISEIESIMA.md`). L'evento è
pubblico nel momento in cui succede (il primo regolamento all'intervallo più corto): entrare **all'ora dopo** prende una parte di
quel movimento. **Riserva:** la prima reazione è stata vista; la regola d'uscita (7 giorni) resta quella di E4.

## 2. La regola (valori fissati qui; il resto come E4)

* **Gli eventi**: quelli di E4 (`ventiseiesima.eventi`: il primo regolamento con l'intervallo più corto, funding positivo, volume
  il giorno dell'evento), sui perpetui del pannello.
* **L'entrata**: all'apertura dell'ora dopo il regolamento dell'evento, short la moneta e long il Bitcoin per lo stesso valore
  (candele da 1 ora). **L'uscita**: all'apertura di 7 giorni (168 ore) dopo l'entrata.
* Costi come E4 (la moneta 0,05% + 0,10% di scarto all'entrata e all'uscita, il Bitcoin 0,05% + 0,01%); funding vero dei giorni di
  tenuta per le due gambe. Una prova a eventi: nel conto diventano **135**.

## 3. L'esame e la decisione (fissati qui)

Come E4 (`ventunesima.esame`: media sopra zero con p ≤ 0,005 a una coda, bootstrap sulle settimane, positiva nelle due metà e senza i
5 migliori); accanto, evento per evento, E4 com'è. **Per il bot**: se G12 passa l'esame e sugli stessi eventi rende almeno **1 punto**
in più di E4, il bot entra in E4 all'ora dopo l'evento invece che alle 00:05 del giorno dopo; altrimenti resta com'è.
