# Programma 7 — diciottesima prova: vendere le fiammate delle monete piccole, in giornata (G16)

Scritto il 24 ottobre 2026, alle 11:45 UTC, **prima di scaricare le candele a 1 minuto e prima di qualunque calcolo**. Idea nata dal
trader da copiare n. 2 (`research/trader_copiati/trader_2.md`: 178 posizioni dal 27 giugno al 23 ottobre 2026, controllate sui
prezzi veri). In coda come idea 42 di `research/REGISTRO.md`.

## 1. Perché

Quando una moneta piccola esplode (+50% in un giorno, e ancora +4% in un quarto d'ora con il volume che si moltiplica), chi compra
in quel momento paga un prezzo gonfiato dalla fretta, e chi gli vende fa da controparte: il prezzo rientra in pochi minuti
(l'inversione di breve periodo è più forte proprio dove la liquidità è poca: Nagel 2012; fra le cripto Zaremba e altri 2021). Il
trader n. 2 vende proprio lì ed esce al primo −5%: 103 short, mediana 3 minuti. **Il dubbio scritto prima**: la sua quota di vinte
(95%) viene dal tenere le perdenti per ore o giorni (BR +361% contro); una regola con la protezione perde le volte in cui la
fiammata continua, e può bastare a mangiare tutto. Le prove vicine fatte prima perdevano: lo short il giorno dopo una salita del
30% (prova 62) e le salite estreme al minuto sul 2020-2022 (programma 5).

## 2. I dati e il periodo (fissati qui)

* **Periodo: dal 1° gennaio 2025 al 26 giugno 2026**, il giorno prima della prima posizione del trader che abbiamo visto. I suoi
  trade dopo il 27 giugno non si usano.
* **Universo**: tutti i perpetui USDT-M del pannello (`seconda.pannello`, senza `esclusi.ESCLUSI`), **tolte le 30 con più volume
  medio** nel periodo, il Bitcoin compreso.
* **Candele a 1 minuto** dall'archivio pubblico di Binance (`data.binance.vision`, future USDT-M, file giornalieri) solo per i
  giorni candidati: il massimo del giorno almeno 1,5 volte l'apertura del giorno prima, con il giorno prima e il giorno dopo.

## 3. La regola

* **Il segnale al minuto t** (chiusura del minuto): (a) la chiusura è almeno **1,5 volte** l'apertura di 24 ore prima; (b) la
  chiusura è almeno **1,04 volte** l'apertura di 14 minuti prima (i 15 minuti fino a t); (c) il volume in dollari medio dei 15
  minuti fino a t è almeno **5 volte** la mediana dei minuti delle 24 ore prima (escluso il quarto d'ora).
* **Entrata**: short all'apertura del minuto t + 1.
* **Uscite**: obiettivo a **−5%** dall'entrata con un ordine limite (eseguito se il minimo del minuto lo tocca); protezione a
  **+30%** dall'entrata (se il massimo la tocca; uscita al livello più l'1%); al massimo **24 ore**, poi all'apertura del minuto.
  Se nello stesso minuto si toccano obiettivo e protezione, conta la protezione.
* Una posizione per moneta; dopo un'uscita la moneta può rientrare solo con un segnale nuovo, almeno 15 minuti dopo.
* **Costi**: entrata a mercato (`seconda.costi_moneta`: commissione più lo scarto della moneta); obiettivo a limite (0,02%);
  protezione e uscita a tempo a mercato (come l'entrata). Funding: quello del giorno diviso per le ore tenute (lo short incassa se
  positivo).
* Una prova a eventi: nel conto diventano **141**, le prove a eventi **18**.

## 4. L'esame

* Come le altre prove a eventi (`trentesima.esame`): media per operazione sopra zero con **p ≤ 0,01** (bootstrap sulle settimane),
  positiva nelle due metà e senza le 5 migliori; **per dirla valida contando tutte le 18 prove a eventi: p ≤ 0,00056**.
* Il portafoglio: il 5% a operazione, al massimo 20 aperte (`quarantunesima.portafoglio`), Sharpe e Sharpe corretto con l'aggiunta.
* Si riportano, per capire e senza decidere niente: quante operazioni al giorno, la durata, la quota di obiettivi, protezioni e
  uscite a tempo; per anno e per mese; **la versione senza protezione** (lo stile del trader: solo l'obiettivo, al massimo 7 giorni);
  le stesse regole con il segnale preso a caso negli stessi giorni-moneta (per vedere se il momento conta).
