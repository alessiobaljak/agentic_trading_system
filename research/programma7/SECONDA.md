# Programma 7 — seconda prova: lo short in giornata delle monete con la leva più cara (G2)

Scritto il 23 ottobre 2026, mattina, **prima del calcolo**. Idea 2 di `METODO.md`.

## 1. Perché

Il vantaggio che regge (F5) sta soprattutto dal lato short: le monete con il funding più alto, dove la leva dei long è più cara,
rendono meno delle altre (lato short di F5 +42% l'anno contro +15% del lato long, prova 24). Nelle prove a 4 ore con il filtro del
funding il lato short era positivo e il long negativo (T6 short +0,36%, T8 short +0,53% a operazione, prove 37 e 39): **riserva**,
l'idea di guardare solo gli short nasce anche da quei numeri già visti. Qui il trading è **in giornata**: ogni operazione si apre e
si chiude nello stesso giorno, con un'entrata decisa dal prezzo, uno stop e un obiettivo.

## 2. La regola (valori fissati qui)

* **Le monete del giorno** (alle 00:00 UTC): fra le 100 della settimana, il 20% con il funding dei 7 giorni più alto (la soglia
  d'entrata di F5; `sesta.funding_7` con le parità corrette), con la volatilità dei 30 giorni disponibile.
* **L'entrata**: dalle 01:00 alle 20:00 UTC, la prima candela da 1 ora che **chiude sotto l'apertura del giorno** (le 00:00): il
  prezzo cede, la leva comincia a uscire. Short a mercato all'apertura dell'ora dopo. Una sola operazione per moneta al giorno.
* **Lo stop**: il massimo del giorno fino all'entrata (dalle 00:00 all'ultima candela prima dell'entrata); a mercato quando il
  massimo di un'ora lo supera, al livello (o all'apertura se il prezzo ci salta oltre). Se lo stop è a meno dello 0,2%
  dall'entrata, si mette allo 0,2%.
* **L'obiettivo**: due volte la distanza dello stop sotto l'entrata, a **ordine limite**, eseguito se il minimo di un'ora va sotto.
  Se nella stessa ora si toccano stop e obiettivo, vale lo stop.
* **L'uscita a tempo**: alle 00:00 del giorno dopo, a mercato, se né stop né obiettivo.
* **Costi**: a mercato 0,05% più lo scarto (0,01% BTC, ETH, SOL; 0,02% le altre); a limite 0,02%. **Funding**: lo short incassa
  (o paga) un terzo del funding del giorno per ogni regolamento delle 08:00 e delle 16:00 che attraversa.
* **La dimensione**: ogni operazione rischia lo **0,5%** del capitale fra entrata e stop, con un tetto del 20% del capitale per
  operazione.
* Candele da 1 ora (`programma6/esecuzione.ore_di`); senza candele la moneta quel giorno non si opera. Dal 4 gennaio 2021 al 4
  ottobre 2026. Una prova: nel conto diventano **121**.

## 3. L'esame

* **Per operazione**: media netta in R sopra zero con **p ≤ 0,01** (bootstrap sui giorni), positiva nelle due metà del periodo e
  senza i 5 giorni migliori.
* **Come portafoglio** (la somma giornaliera dei risultati, sommata per settimana): `terza.esame` e `terza.esito`, Sharpe corretto
  con l'aggiunta del 23 ottobre, soglia 0,95.
* Si riportano: operazioni al giorno, quota vinte, vincita e perdita medie in R, uscite per motivo (stop, obiettivo, tempo), costi
  e funding in R, per anno.
