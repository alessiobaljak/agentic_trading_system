# Prova 33 — il momento dei settori: comprati i 3 settori saliti di più in un anno, venduti i 3 saliti di meno, ogni mese

Regole scritte il 14 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare i prezzi dei fondi di settore (idea I35 di
`REGISTRO.md`). Si conoscevano le prove 1-32, in particolare la 13 (il momento a 12 mesi fra le singole azioni, bocciata) e la 26 (la
tendenza sui fondi di altre classi, bocciata per la correlazione). Contano come **2 prove** (la strategia da sola, e la miscela con
lei): 83 nel conto.

## Perché dovrebbe funzionare

Il momento delle azioni viene in gran parte dai **settori**: i settori saliti di più nei 12 mesi prima continuano a fare meglio nei mesi
dopo (Moskowitz e Grinblatt, «Do industries explain momentum?», *Journal of Finance* 54, 1999); è uno degli effetti più confermati su
mercati e periodi diversi (Asness, Moskowitz, Pedersen, «Value and momentum everywhere», *Journal of Finance* 68, 2013). La spiegazione:
le notizie che riguardano un intero settore entrano nei prezzi lentamente.

Perché ora: i fondi di settore costano pochissimo da comprare e vendere (la lezione delle prove 29-32: i costi e le aziende piccole);
comprato e venduto insieme, dovrebbe muoversi poco con la miscela; i prezzi di Yahoo sono gratuiti e il calcolo si fa qui.

**Sospetti scritti prima:**

* **pochi pezzi**: 9-11 settori, 3 comprati e 3 venduti; poche scommesse indipendenti, molto rumore;
* **2016-2024 è il decennio della tecnologia**: il settore tecnologico in cima per anni può fare tutto il risultato; si stampa la
  correlazione con QQQ meno SPY;
* il momento ha **crolli** improvvisi quando il mercato gira (novembre 2020, 2022 con l'energia): i venduti salgono di colpo;
* è pubblicato dal 1999 e molto usato; i fondi di settore sono più grossolani delle industrie degli studi;
* il momento fra le singole azioni dell'S&P 500 è stato bocciato (prova 13).

## I dati

* **I fondi:** i fondi di settore dell'S&P 500 (SPDR): XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY (dal 1998), XLRE (dall'ottobre 2015),
  XLC (dal giugno 2018); un fondo entra quando ha 12 mesi di prezzi prima della decisione.
* **I prezzi:** Yahoo, barre al giorno come scambiate, con i dividendi; la chiusura rettificata per il segnale (`stock/dati/yahoo.py`,
  come la prova 26). Restano fuori dal repository.

## La regola

* **Il segnale:** il rendimento dalla chiusura di 252 sedute prima alla chiusura di 21 sedute prima della decisione (12 mesi meno
  l'ultimo, la misura standard degli studi: l'ultimo mese si toglie perché nel breve i prezzi tornano indietro).
* **Ogni fine mese** (ultima chiusura del mese): comprati a pesi uguali i **3 settori con il segnale più alto** per il **50%** del conto;
  venduti allo scoperto a pesi uguali i **3 con il segnale più basso** per il **50%**; ordini a mercato all'apertura del giorno di
  borsa dopo; si tiene un mese.
* **Il limite del conto:** come nelle prove 29 e 31, al cambio del mese le vendite allo scoperto nuove passerebbero prima delle
  ricoperture vecchie; il calcolo usa il limite di un conto con margine (2 volte il valore); l'esposizione voluta non cambia.
* **Periodo:** decisioni dalla fine di dicembre 2015 alla fine di novembre 2024; rendimenti dal gennaio 2016 al 31 dicembre 2024. Il
  periodo chiuso (2025-01 → 2026-09) non si guarda: i prezzi si scaricano solo fino al 31 dicembre 2024.

## I costi (fissati prima, come la prova 26 sui fondi)

Metà scarto 2,5 punti base e slittamento 1; commissioni Interactive Brokers «fisso»; prestito dei fondi venduti allo scoperto **0,5%
l'anno**. Versione con tutti i costi raddoppiati.

## L'esame

**Da sola** (come le prove 28 e 30-32): (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe
corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata il 14 novembre, come la prova 32): Sharpe con i costi sopra zero, anche con i costi
doppi; correlazione con la miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo
Sharpe più alto della miscela e del tenere lo SPY; il t dello Sharpe della parte con i costi almeno 1,3; la miscela nuova più alta in
almeno l'80% di 2000 campionamenti a blocchi di 20 giorni.

Da leggere accanto (non sono prove): quante volte ogni settore è stato comprato e venduto; i comprati meno i venduti, mese dopo, senza
costi, con il t; la correlazione con lo SPY e con QQQ meno SPY; il risultato anno per anno. **Se passa uno dei due esami:** revisore
separato, poi il periodo chiuso (la famiglia «momento e tendenza», prove 5, 13 e 26, non l'ha mai aperto), poi la misura in
avanti sul demo.
