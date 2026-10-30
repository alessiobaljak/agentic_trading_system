# Programma 7 — settantaquattresima prova: il Bitcoin e l'Ether che passano un numero tondo (NT)

Scritto il 30 ottobre 2026 alle 08:18 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 112 della coda (dalla ricerca
nelle pubblicazioni del 29 ottobre). Nessun prezzo di questa prova è ancora stato guardato.

## 1. Perché

* **Gli ordini si ammassano sui numeri tondi**: chi è short mette lo stop appena sopra 100.000 dollari, chi è long appena sotto 90.000. Quando
  il prezzo passa il numero tondo, gli stop scattano insieme e spingono il prezzo ancora oltre. Sui cambi lo ha misurato Osler («Stop-loss
  orders and price cascades in currency markets», *Journal of International Money and Finance*, 2005; non letto per intero). Sulle crypto
  non abbiamo trovato studi seri, solo affermazioni di trader.
* **È un'operazione in giornata**: si entra al passaggio e si esce dopo un'ora.
* **I dubbi scritti prima**:
  * lo scalping con gli indicatori a 1-5 minuti (prove 108 e 111) non aveva nessun vantaggio prima dei costi;
  * il passaggio di un numero tondo lo vedono tutti, quindi il movimento può essere già finito al primo minuto;
  * i costi a mercato (0,12% andata e ritorno sul Bitcoin) chiedono un movimento grande in un'ora.

## 2. La regola (fissata qui)

* **Dati**: le candele a 1 minuto dei perpetui BTCUSDT (già in casa, `research/data/minuti_btc/`) ed ETHUSDT (dall'archivio pubblico di
  Binance, salvate in `research/data/minuti_eth/` fuori da git), dal 1° gennaio 2021 al 30 settembre 2026.
* **I numeri tondi**: i multipli di 1.000 dollari per il Bitcoin e di 100 dollari per l'Ether.
* **L'evento**: un minuto che chiude oltre un numero tondo (sopra, se il minuto prima chiudeva sotto; sotto, se chiudeva sopra), quando nelle
  24 ore prima nessun minuto aveva chiuso dall'altra parte di quel numero (cioè il primo passaggio del giorno). Al massimo un evento ogni
  60 minuti per moneta.
* **L'operazione**: nel verso del passaggio (long se il prezzo è salito oltre, short se è sceso), dall'apertura del minuto dopo per 60
  minuti. Costi a mercato del Bitcoin delle prove a eventi (`ventunesima.COSTO_BTC`, 0,12%) per tutte e due le monete; il funding non
  conta in un'ora.
* **Una prova a eventi**: nel conto delle prove diventano **233**, le prove a eventi **42**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): media per operazione sopra zero con **p ≤ 0,01**, positiva
  nelle due metà e senza le 5 migliori, **e sopra il controllo** (differenza con p ≤ 0,05). Contando le 42 prove a eventi la soglia è
  **0,00024**.
* **Il controllo**: la stessa regola con i livelli spostati a metà fra due numeri tondi (500 dollari più i multipli di 1.000 per il
  Bitcoin, 50 più i multipli di 100 per l'Ether). Se i livelli spostati rendono uguale, il numero tondo non conta.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: il lordo; le tenute di 5, 15 e 240 minuti; per moneta; per anno; i passaggi verso l'alto contro
  quelli verso il basso.
