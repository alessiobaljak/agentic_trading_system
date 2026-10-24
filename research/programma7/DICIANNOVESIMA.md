# Programma 7 — diciannovesima prova: le fiammate delle monete piccole senza protezione, con posizioni piccole (G17)

Scritto il 24 ottobre 2026, alle 13:20 UTC, **prima di scaricare le candele del 2023-2024 e prima di qualunque calcolo**. Ipotesi
nata dalla parte descrittiva della prova 75 (`RISULTATI_DICIOTTESIMA.md`), quindi si prova **solo su anni non usati**.

## 1. Perché

Nella prova 75 (gennaio 2025 – giugno 2026) la regola del trader n. 2 **con** la protezione a +30% perde (−0,88% a operazione); la
versione **senza** protezione, solo descrittiva, fa +1,65% a operazione con il 97% di vinte, ma 23 operazioni su 3.494 perdono più
del 100% del valore (fino a −1.511%, COAI nell'ottobre 2025). Con il 5% del conto a operazione una settimana perde più del conto;
**con l'1%** la somma delle operazioni arriva a 1,57 volte il conto, con la discesa peggiore del 34%. L'ipotesi: vendere le fiammate
e aspettare che rientrino rende, se ogni posizione è abbastanza piccola da sopravvivere alla moneta che sale di 10-15 volte (come chi
vende assicurazioni: tante polizze piccole). Il dubbio scritto prima: il +1,65% non era sicuro (p 0,074), e il 2023-2024 ha avuto
meno fiammate.

## 2. Dati, periodo e universo

* **Periodo: 1° gennaio 2023 – 31 dicembre 2024**, mai usato per questa idea (né dalla prova 75, né dai trade del trader).
* Universo, giorni candidati, candele a 1 minuto e segnale **identici alla prova 75** (`diciottesima.candidati` e
  `diciottesima.segnali`, con le 30 monete più grandi tolte sul nuovo periodo): 630 giorni-moneta candidati su 213 monete.

## 3. La regola

* Entrata come la prova 75 (short all'apertura del minuto dopo il segnale).
* Uscite: **obiettivo −5% a limite; nessuna protezione; al massimo 7 giorni**, poi all'apertura del minuto.
* Una posizione per moneta, rientro solo con un segnale nuovo almeno 15 minuti dopo l'uscita.
* **Dimensione: l'1% del conto a operazione** (valore della posizione), al massimo 50 aperte.
* Costi e funding come la prova 75.
* Una prova a eventi: nel conto diventano **142**, le prove a eventi **19**.

## 4. L'esame

* Operazioni: media sopra zero con **p ≤ 0,01** (bootstrap sulle settimane), positiva nelle due metà e senza le 5 migliori; per
  dirla valida contando tutte le 19 prove a eventi: **p ≤ 0,00053**.
* **Il conto con l'1% a operazione**: Sharpe settimanale, Sharpe corretto con l'aggiunta (soglia 0,95), e **la discesa peggiore
  deve stare sotto il 30%** del conto; se una sola operazione costa più del 10% del conto, si dice.
* Si riportano anche: con il 2% a operazione; quante operazioni oltre −100%; per anno e per mese.
