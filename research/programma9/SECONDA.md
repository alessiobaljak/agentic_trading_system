# Programma 9 — seconda prova: le fiammate da vendere solo quando i long sono affollati (P9C)

Scritto il 24 ottobre 2026, alle 16:40 UTC, **prima di scaricare i dati del periodo e prima di qualunque calcolo**. Idea di
combinazione del programma 9 (`METODO.md`): la regola delle fiammate (prova 75, trader n. 2) unita al funding (F5) e alla meccanica
delle liquidazioni.

## 1. Perché

Nelle prove 75 e 76 vendere le fiammate perde per le poche volte in cui la salita continua (COAI fino a +1.500%). Una salita che
continua è spesso uno **schiacciamento degli short**: chi è short viene liquidato e deve ricomprare, e questo succede quando gli
short sono affollati (funding negativo: sono loro a pagare). Quando invece sono affollati i long (funding positivo e alto), la
fiammata è comprata a leva da chi arriva tardi, e il rientro è più probabile. **L'idea non viene dal guardare i risultati delle prove
75-78 per funding**: non li ho mai divisi così. Il dubbio scritto prima: il funding si aggiorna ogni 8 ore (o 4, o 1), e durante una
fiammata di pochi minuti quello dell'ultimo regolamento può essere vecchio.

## 2. Periodo e dati

* **Periodo: dal 27 giugno al 21 ottobre 2026**, mai usato dalla regola delle fiammate (le prove 75-76 si fermano al 26 giugno; i
  trade del trader n. 2 li abbiamo visti, ma non la regola su questi mesi). Universo, giorni candidati, candele a 1 minuto e segnale
  **identici alla prova 75** (`diciottesima`).
* Il funding: quello dell'ultimo regolamento prima del segnale, dall'archivio pubblico di Binance (`fundingRate` mensile della moneta);
  l'intervallo della moneta lo dà la distanza fra due regolamenti.

## 3. La regola

* Il segnale della prova 75 (+50% in 24 ore, +4% nel quarto d'ora, volume 5 volte), **e in più**: il funding dell'ultimo regolamento
  è **almeno +0,01% per 8 ore** (riportato a 8 ore se l'intervallo è più corto): i long pagano almeno il tasso di base.
* Uscite della prova 75: obiettivo −5% a limite, protezione +30%, al massimo 24 ore. Costi come la prova 75.
* Si riportano anche, per capire: le fiammate con il funding sotto la soglia (dove dovrebbero stare le perdite grosse) e tutte
  insieme (la prova 75 su questi mesi).
* Una prova a eventi: nel conto diventano **147**, le prove a eventi **21**.

## 4. L'esame

* Media per operazione sopra zero con **p ≤ 0,01**, positiva nelle due metà e senza le 5 migliori; contando le 21 prove a eventi
  **p ≤ 0,00048**. Con quattro mesi, se le operazioni sono poche (meno di 100) la prova dice poco e si scrive così.
* Il punto da controllare comunque: le perdite oltre −30% stanno davvero dalla parte del funding negativo?
