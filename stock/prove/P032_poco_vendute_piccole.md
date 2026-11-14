# Prova 32 — comprare le aziende piccole meno vendute allo scoperto, coperte con il fondo delle piccole, un mese

Regole scritte il 14 novembre 2026 **prima di qualsiasi calcolo** (idea I29, la parte «vendite allo scoperto nelle aziende piccole»; idea
I34 di `REGISTRO.md`). Si conoscevano le prove 1-31, compresa la prova 24 (le vendite allo scoperto nell'S&P 500) e il solo conteggio
dei titoli per data nell'archivio di FINRA (circa 19'500 a ogni data, dal 12 gennaio 2018: nessun rendimento guardato). Contano come
**2 prove** (la strategia da sola, e la miscela con lei): 81 nel conto.

## Perché dovrebbe funzionare

Chi vende allo scoperto è di solito informato: i titoli **poco** venduti allo scoperto sono quelli su cui nessun informato scommette
contro, e rendono più del mercato. Boehmer, Huszar e Jordan, «The good news in short interest», *Journal of Financial Economics* 96
(2010): il vantaggio dei titoli poco venduti è significativo e sta dal lato che si compra; Hong, Li, Ni, Scheinkman e Yan, «Days to
cover and stock returns», NBER 21166 (2015): i giorni per ricomprare (vendute diviso volume medio) misurano meglio quanto è caro
scommettere contro. Si **compra** e basta: niente prestito caro sui titoli (la lezione della prova 29); la copertura è il fondo delle
piccole (IWM), facile da prendere a prestito.

Perché ora: è in cima alla coda (le aziende piccole, idea I29); il dato di FINRA è già scaricato e non è mai stato usato sulle piccole;
si tiene un mese (meno costi delle prove 29 e 30).

**Sospetti scritti prima:**

* nella prova 24, nell'S&P 500, è successo il contrario degli studi (i titoli più venduti sono saliti più dell'indice): può succedere
  anche qui;
* le prove 27 e 28 (variante B) dicono che **comprare un gruppo di piccole e coprirlo con l'IWM non ha mai battuto l'IWM**: il lato
  comprato delle piccole è rumoroso;
* gli studi arrivano fino al 2012-2015: dopo la pubblicazione gli effetti calano;
* i titoli con pochissimi giorni per ricomprare sono spesso quelli con un volume altissimo per una notizia: possono essere una scelta di
  «titoli del momento», non di titoli sani;
* lo scarto fra acquisto e vendita delle piccole (15 punti base, più 5 di slittamento) si paga ogni mese su quasi tutto il lato comprato.

## I dati

* **Le vendite allo scoperto:** FINRA, «consolidated short interest», due volte al mese, pubblico e senza chiave (`stock/dati/finra.py`);
  si usa il campo dei giorni per ricomprare (`daysToCoverQuantity`), le righe con volume medio sopra zero. FINRA pubblica circa 7 giorni
  di borsa dopo la data di regolamento: alla decisione del giorno D vale **l'ultima data di regolamento almeno 14 giorni prima di D**.
  Nel repository non entra niente di FINRA: il lavoro di GitHub lo scarica e tiene solo i risultati.
* **I titoli:** i simboli di FINRA di **1-4 lettere** (più le classi «.A», «.B»), come si scrivono le azioni ordinarie sulle borse
  americane (la quinta lettera segna diritti, unità, warrant, titoli esteri fuori borsa); fuori dall'S&P 500 quel giorno
  (`dati/P028_membri.csv.gz`); esclusi i fondi (lo stesso elenco di parole della prova 28, dai nomi di Alpaca).
* **I prezzi:** Alpaca, con il simbolo di allora (`asof` «-»), con dividendi e frazionamenti; un titolo in mano che resta 5 giorni di
  borsa senza prezzi si chiude all'ultima chiusura e si conta.

## La regola

* **Ogni fine mese** (ultima chiusura del mese): fra i titoli con chiusura di almeno **5 dollari**, mediana dei dollari scambiati nelle
  20 sedute prima di almeno **2 milioni** (i filtri delle prove 27-29) e i giorni per ricomprare della data valida: il **20% con meno
  giorni per ricomprare**, al massimo 50 (i più bassi; a pari valore in ordine alfabetico). Se i titoli ammessi sono meno di 25, quel mese
  si resta fuori.
* **Posizioni:** comprati a pesi uguali per il **50%** del conto; venduto allo scoperto l'**IWM** per il **50%**; ordini a mercato
  all'apertura del primo giorno di borsa del mese dopo; si tiene un mese.
* **Periodo:** decisioni dalla fine di gennaio 2018 (la prima data di FINRA è il 12 gennaio 2018) alla fine di novembre 2024; rendimenti
  dal febbraio 2018 al 31 dicembre 2024. Il periodo chiuso (2025-01 → 2026-09) non si guarda; il programma non legge le date di FINRA
  dopo il 31 dicembre 2024.

## I costi (fissati prima, come le prove 27-29 sulle piccole)

Metà scarto 15 punti base e slittamento 5; commissioni Interactive Brokers «fisso»; prestito dell'IWM venduto allo scoperto **1%
l'anno**. Versione con tutti i costi raddoppiati.

## L'esame

**Da sola** (come le prove 28, 30 e 31): (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe
corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30, **rafforzata il 14 novembre** dopo la prova 31): Sharpe con i costi sopra zero, anche con i
costi doppi; correlazione dei rendimenti giornalieri con la miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela,
un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; **in più** il t dello Sharpe della parte con i costi
(media diviso deviazione dei rendimenti giornalieri per la radice del numero dei giorni) **almeno 1,3**, e la miscela nuova con lo
Sharpe più alto della miscela in **almeno l'80%** di 2000 campionamenti a blocchi di 20 giorni (gli stessi giorni per le due serie).

Da leggere accanto (non sono prove): quanti titoli ammessi ogni mese; il quinto con meno giorni per ricomprare meno il quinto con più
giorni, e il quinto basso meno l'IWM, mese dopo, senza costi, con il loro t; la correlazione con lo SPY; i titoli chiusi perché spariti
dal listino; il risultato anno per anno. **Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (la famiglia «vendite
allo scoperto» non l'ha mai usato), poi la misura in avanti sul demo.

## Aggiunta sui dati del 14 novembre 2026, prima di qualsiasi calcolo (nessun rendimento visto)

Guardando solo la distribuzione del dato di FINRA (2018-2024, simboli di 1-4 lettere): il campo `daysToCoverQuantity` **non scende mai
sotto 1** (quando le azioni vendute allo scoperto sono meno del volume medio di un giorno FINRA scrive 1: succede sempre, sul 100% di
quei casi); già il 20% più basso sarebbe tutto a pari valore e la scelta diventerebbe alfabetica. Sopra 1 il campo coincide con il
rapporto (differenza entro 0,01 nel 99,8% dei casi). Quindi i giorni per ricomprare si calcolano come **azioni vendute allo scoperto
(`currentShortPositionQuantity`) diviso volume medio giornaliero (`averageDailyVolumeQuantity`)**, la stessa definizione senza il
pavimento a 1 (mediana 1,59; il 20% più basso sotto 0,19). Nient'altro cambia.
