# Prova 49 — le vendite allo scoperto fuori borsa (il DIX di SqueezeMetrics): più investiti nello SPY quando sono alte

Regole scritte il 24 novembre 2026 **prima di qualsiasi calcolo sui prezzi** (idea I57 di `REGISTRO.md`). Del dato nuovo si sono visti
solo i conteggi: la colonna `dix` di `squeezemetrics.com/monitor/static/DIX.csv` va dal 2 maggio 2011 al 23 novembre 2026, nessun giorno
vuoto, 2'264 giorni dal 2016 al 2024. Si conoscevano le prove 1-48, in particolare la 16 (metà fuori quando la salita la fanno in poche:
la stessa forma di regola, 98% o 49%), la 15 (più investiti con il mercato calmo, decisione settimanale) e le 45 e 47 (la colonna `gex`
dello stesso file). Contano come **2 prove** (la strategia da sola, e la miscela con lei): 113 e 114 nel conto. La prova 42, ancora da
calcolare, passa a 115 e 116.

## Perché dovrebbe funzionare (e perché il perché è debole)

**Un dato mai usato.** SqueezeMetrics calcola ogni giorno il DIX: la quota delle vendite allo scoperto sul volume scambiato fuori borsa
(i circuiti riservati segnalati a FINRA) per le azioni dell'S&P 500, pesata per il valore. La loro tesi (documento «Short is Long»,
citato da fonti secondarie; il documento non è stato letto): fuori borsa chi vende allo scoperto è quasi sempre l'intermediario che
serve un compratore. Quindi molte vendite allo scoperto fuori borsa vogliono dire **molti acquisti dei clienti**, e un DIX alto
annuncerebbe rendimenti più alti nei mesi dopo.

**Sospetti scritti prima:**

* **nessuno studio serio**: la tesi è della società che vende il dato, non è stata controllata da altri; le fonti secondarie la leggono
  anche al contrario (DIX alto = discesa vicina);
* **il dato può essere stato rifatto**: per la colonna `gex` dello stesso file le copie pubbliche si possono confrontare solo dal novembre
  2021 (revisione della prova 45); prima il file può essere stato ricalcolato con quello che si sapeva dopo;
* **può essere solo «comprare dopo le cadute»**: chi compra di più fuori borsa potrebbe essere chi compra quando il mercato è sceso; allora
  il DIX ripeterebbe il rimbalzo e la paura, cose che la miscela ha già (la regola della calma);
* **un segnale lento su pochi anni**: 9 anni di decisioni settimanali, con un effetto che lo stesso venditore descrive su 1-3 mesi.

## I dati

* **Il DIX:** la colonna `dix` di SqueezeMetrics, scaricata dal programma, mai nel repository. Il valore con la data di un giorno di borsa
  si conosce prima dell'apertura del giorno dopo (FINRA pubblica le vendite allo scoperto del giorno la sera stessa).
* **Lo SPY:** chiusure giornaliere rettificate per i dividendi (Yahoo, in locale, mai nel repository), come le prove 15, 16 e 48.

## La regola

* **La decisione, una volta a settimana** (come la prova 15): con i valori di tutti i giorni di borsa della settimana appena finita, la
  media del DIX della settimana si confronta con la media del DIX delle **52 settimane prima** (i giorni delle 52 settimane prima di
  quella appena finita). Se la media della settimana è **più alta**: lo SPY al **98%** del conto; se è più bassa o uguale: al **49%**
  (la forma della prova 16).
* **Quando si esegue:** alla **chiusura del primo giorno di borsa della settimana dopo** (asta di chiusura), perché il DIX dell'ultimo
  giorno si conosce solo dopo la chiusura di quel giorno. La quota vale da quella chiusura fino all'esecuzione della decisione dopo.
* **La partenza:** la prima decisione usa la prima settimana con 52 settimane prima nel file (il file parte nel 2011: dal 2016 sempre).
* **Il resto del conto** non rende niente (come le prove 15 e 16).
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (come la prova 48)

A ogni cambio di quota: slittamento di 0,5 punti base sulla parte comprata o venduta (all'asta di chiusura, nessuno scarto) e la
commissione di Interactive Brokers «fisso» sulle azioni comprate o vendute. Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-48)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie
del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata, dalla prova 47 anche senza marzo 2020; la parte è la regola intera, come nelle
prove 30-48): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la miscela della prova 25 sotto 0,3; la miscela
nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; il t dello Sharpe della
parte almeno 1,3, anche senza marzo 2020; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a blocchi di 20 giorni. (La
regola sta sempre almeno per metà nello SPY: la correlazione con la miscela sarà probabilmente alta, ed è giusto che l'esame lo conti.)

Da leggere accanto (non cambiano l'esito): **lo SPY tenuto sempre alla quota media della regola** (se rende come la regola, il DIX non
aggiunge niente); la regola al contrario (98% con il DIX basso), per vedere da che parte sta il dato; il
rendimento medio dello SPY nelle 4 settimane dopo le settimane con il DIX alto e con quello basso, con il t; la correlazione fra la
decisione e il rendimento dello SPY delle 4 settimane prima (se è forte, il DIX ripete il «comprare dopo le cadute»); quante volte cambia
la quota per anno; l'anno per anno.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «vendite fuori borsa» non l'ha mai usato.
