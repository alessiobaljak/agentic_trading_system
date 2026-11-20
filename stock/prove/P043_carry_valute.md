# Prova 43 — il «carry» delle valute: comprate le due valute con il tasso più alto, vendute le due con il più basso

Regole scritte il 20 novembre 2026 **prima di qualsiasi calcolo sui prezzi** (idea I47 di `REGISTRO.md`). Visti prima solo la presenza
dei dati (i tassi dei sei paesi senza mesi vuoti dal settembre 2015 al dicembre 2024; i sei fondi con 2'286 giorni ciascuno dal dicembre
2015 al dicembre 2024), nessun rendimento. Si conoscevano le prove 1-41, in particolare la 26 (la tendenza su sei fondi di altre classi:
**non entra nella miscela per la correlazione 0,41** con le azioni americane) e la 33 (il momento dei settori). Contano come **2 prove**
(la strategia da sola, e la miscela con lei).

## Perché dovrebbe funzionare

Chi tiene una valuta con il tasso d'interesse alto contro una con il tasso basso guadagna, in media, più di quanto la valuta alta perda
di valore: la parità dei tassi «scoperta» non vale nei dati. Lustig, Roussanov e Verdelhan, «Common Risk Factors in Currency Markets»,
Review of Financial Studies 24 (2011); Koijen, Moskowitz, Pedersen e Vrugt, «Carry», Journal of Financial Economics 127 (2018): il
carry delle valute dei paesi ricchi ha uno Sharpe di circa 0,6-0,8 dal 1983. È un **premio per un rischio** (le valute alte crollano
nelle crisi), non un errore del mercato che si chiude quando viene pubblicato: per questo dura da decenni. Ed è un dato **mai usato** qui
(i tassi d'interesse dei paesi) su una **classe mai provata** (le valute).

**Sospetti scritti prima:**

* **le crisi**: il carry perde quando le azioni crollano (marzo 2020; agosto 2024, la fine del carry sullo yen): la correlazione con la
  miscela può superare 0,3, come per la prova 26;
* **i tassi quasi a zero** nel 2016-2021 per l'euro, il franco e lo yen: le differenze fra le valute basse sono piccole e la scelta dei
  venduti cambia per poco;
* **solo sei valute**: due comprate e due vendute; poca diversificazione, un paese pesa molto;
* **i fondi delle valute non sono la valuta**: pagano l'interesse del deposito meno le spese (0,40% l'anno) e, con i tassi negativi,
  l'hanno pagato loro; la differenza dei tassi arriva solo in parte;
* **gli studi finiscono prima del 2016**, e il carry delle valute dei paesi ricchi è andato male negli anni 2010.

## I dati

* **I fondi** (Invesco CurrencyShares): FXA (dollaro australiano), FXB (sterlina), FXC (dollaro canadese), FXE (euro), FXF (franco
  svizzero), FXY (yen). Prezzi al giorno di Yahoo con le distribuzioni (scaricati da qui, tenuti fuori dal repository, come la prova 26).
* **I tassi:** il tasso interbancario a tre mesi, media del mese, dell'OECD (banca dati FRED della Fed di St. Louis, serie
  `IR3TIB01AUM156N`, `IR3TIB01GBM156N`, `IR3TIB01CAM156N`, `IR3TIB01EZM156N`, `IR3TIB01CHM156N`, `IR3TIB01JPM156N`), salvati nel
  repository (`dati/P043_tassi.csv`, dati pubblici).
* **Quando si sa:** il tasso di un mese esce alcune settimane dopo: alla decisione di fine mese *m* si usa il tasso del mese **m − 2**
  (sempre già pubblicato).

## La regola

* **Quando:** alla chiusura dell'ultimo giorno di borsa di ogni mese, da dicembre 2015 a novembre 2024; si tiene da gennaio 2016 a
  dicembre 2024.
* **La scelta:** le sei valute in fila per il tasso del mese m − 2; si **comprano le 2 con il tasso più alto** e si **vendono allo
  scoperto le 2 con il più basso** (a pari tasso, in ordine alfabetico del fondo).
* **Quanto:** metà del conto nei comprati e metà nei venduti, a pesi uguali (un quarto ciascuno); si ribilancia ogni fine mese, come
  le prove 31, 38, 39 e 41 (stessa esecuzione: `p031.strategia`).
* **Periodo:** fino al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima)

Gli scarti di questi fondi non sono misurati (`dati/ESITO_CONTROLLI_UNIVERSO.md` non li ha): si fissa **metà dello scarto a 5 punti base**
per lato (il doppio di quello della prova 26 per TLT, GLD e gli altri, perché i fondi delle valute sono meno scambiati), slittamento 1
punto base, commissioni Interactive Brokers «fisso», prestito dei venduti allo scoperto 0,5% l'anno. Versione con tutti i costi
raddoppiati.

## L'esame (uguale alle prove 28 e 30-42)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a
blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): comprati meno venduti mese per mese prima dei costi (media, t, mesi positivi); la differenza
media dei tassi fra comprati e venduti; quante volte ogni valuta è comprata o venduta; la correlazione con lo SPY; l'anno per anno; i
mesi di marzo 2020 e agosto 2024.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «valute» non l'ha mai usato.
