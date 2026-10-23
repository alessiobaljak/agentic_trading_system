# Programma 7 — dodicesima prova: il «buco» del CME sul Bitcoin (G10)

Scritto il 23 ottobre 2026, **prima del calcolo**. Un'idea nuova, molto diffusa fra i trader: «i buchi del CME si chiudono
sempre».

## 1. Perché

I future sul Bitcoin del CME (la borsa di Chicago) chiudono il venerdì pomeriggio e riaprono la domenica sera; il Bitcoin intanto si
scambia anche nel fine settimana. Se alla riapertura il prezzo è lontano dalla chiusura del venerdì, sul grafico del CME resta un
«buco», e si dice che il prezzo torni quasi sempre a chiuderlo nei giorni dopo (chi opera sul CME, fondi e istituzioni, rientra ai
prezzi del venerdì). Non l'abbiamo mai provato. Un prezzo che vaga torna spesso a un livello vicino, quindi la quota di buchi
«chiusi» da sola non dice niente: conta se l'operazione guadagna dopo i costi, con uno stop.

## 2. La regola (valori fissati qui)

* **Gli orari del CME** (ora di Chicago, con l'ora legale): chiusura il venerdì alle 16:00, riapertura la domenica alle 17:00
  (in UTC: 21:00 o 22:00 il venerdì, 22:00 o 23:00 la domenica).
* **Il buco**: l'apertura dell'ora della riapertura (Bitcoin perpetuo di Binance, candele da 1 ora) rispetto all'apertura dell'ora
  della chiusura del venerdì. Si opera se il buco è di almeno l'**1%**.
* **L'operazione**: alla riapertura, nel verso che chiude il buco (buco in su: short; buco in giù: long), a mercato. **Obiettivo**:
  il prezzo della chiusura del venerdì, a ordine limite. **Stop**: alla stessa distanza dall'altra parte (rischio uguale al premio).
  Stop e obiettivo nella stessa ora: vale lo stop. **Uscita a tempo** all'apertura della chiusura del venerdì dopo.
* Costi: a mercato 0,05% più lo scarto dello 0,01%; a limite 0,02%; funding vero del Bitcoin (un terzo del funding del giorno per
  ogni regolamento attraversato). Dal 1 gennaio 2021 al 4 ottobre 2026. Una prova: nel conto diventano **133**.

## 3. L'esame

Per operazione in multipli del rischio: media netta sopra zero con **p ≤ 0,01** (bootstrap sulle operazioni), positiva nelle due
metà e senza le 5 migliori. Si riportano la quota di buchi chiusi entro la settimana, le uscite per motivo e per anno.
