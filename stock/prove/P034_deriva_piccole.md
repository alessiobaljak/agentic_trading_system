# Prova 34 — le aziende piccole che salgono di più nei giorni dei risultati continuano a salire: comprate un mese, coperte con l'IWM

Regole scritte il 15 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare le date dei comunicati delle aziende piccole
(idea I29, la parte «deriva dopo i bilanci nelle aziende piccole»; idea I36 di `REGISTRO.md`). Si conoscevano le prove 1-33, in
particolare la 10 (la deriva nelle 10 più grandi, bocciata), la 20 e la 21 (la prima candela nel giorno del comunicato), la 27, la 28 e
la 32 (il lato comprato delle piccole coperto con l'IWM, sempre in perdita). Contano come **2 prove**: 85 nel conto.

## Perché dovrebbe funzionare

Dopo un comunicato sui risultati il prezzo continua per settimane nella direzione della prima reazione: Bernard e Thomas, *Journal of
Accounting Research* 27 (1989); Chan, Jegadeesh, Lakonishok, «Momentum strategies», *Journal of Finance* 51 (1996); Brandt, Kishore,
Santa-Clara, Venkatachalam, «Earnings announcements are full of surprises» (2008): la reazione dei 3 giorni intorno al comunicato
prevede i rendimenti dei mesi dopo, più della sorpresa sugli utili. L'effetto è più forte nelle aziende piccole, poco seguite dagli
analisti: lì l'informazione entra lentamente.

Perché ora: è l'ultima parte aperta dell'idea in cima alla coda (le aziende piccole); la prova 10 l'ha guardata solo nelle 10 più
grandi, dove gli studi dicono che non c'è più; i prezzi delle piccole con il simbolo di allora sono già nella memoria del lavoro di
GitHub (prova 32).

**Sospetti scritti prima:**

* **la deriva si è molto ridotta dopo il 2006** e per le grandi è sparita (Martineau, «Rest in peace post-earnings announcement drift»,
  *Critical Finance Review* 11, 2022); nelle piccole può essere troppo piccola per pagare i costi;
* **il lato comprato delle piccole, coperto con l'IWM, ha perso in tre prove su tre** (27, 28, 32);
* la data è quella del deposito del modulo, che può essere il giorno dopo il comunicato (prova 20): la finestra di 3 giorni intorno
  al deposito copre i due casi;
* il simbolo viene dai moduli dei dirigenti: un'azienda senza moduli dei dirigenti resta fuori;
* nella prova 32 i titoli scelti erano probabilmente società vuote in attesa di una fusione (non verificato): qui si escludono con il
  codice di settore della SEC (6770, «blank checks»), che si conosce senza guardare i rendimenti.

## I dati

* **I comunicati sui risultati:** i moduli 8-K con la voce 2.02 di ogni azienda che compare nei moduli dei dirigenti della SEC dal 2016
  (`stock/dati/dirigenti.py`) con un simbolo di 1-4 lettere presente nell'archivio di FINRA (quindi scambiato); un comunicato per
  trimestre (`bilanci.un_evento_per_trimestre`); il settore (SIC) della SEC. Dati pubblici: nel repository vanno simbolo, codice,
  data e settore (`stock/prove/dati/P034_comunicati.csv.gz`).
* **Il simbolo di allora:** quello scritto più spesso dall'azienda nei moduli dei dirigenti depositati **nei 365 giorni prima** del
  comunicato (mai dopo); se non ce n'è, il comunicato resta fuori.
* **I prezzi:** Alpaca, simbolo di allora (`asof` «-»), con dividendi e frazionamenti; un titolo che resta 5 giorni di borsa senza
  prezzi si chiude all'ultima chiusura e si conta.

## La regola

* **La reazione al comunicato** depositato il giorno d: il rendimento dalla chiusura del giorno di borsa prima di d alla chiusura del
  giorno di borsa dopo d (3 giorni), meno quello dell'IWM negli stessi giorni.
* **Chi può entrare:** il giorno prima di d il titolo non è nell'S&P 500, chiude ad almeno **5 dollari** e ha la mediana dei dollari
  scambiati nelle 20 sedute prima di almeno **2 milioni** (i filtri delle prove 27-32); il settore non è 6770; il nome non è di un fondo
  (lo stesso elenco della prova 28).
* **Ogni fine mese** (ultima chiusura del mese): fra i comunicati la cui finestra di 3 giorni è finita nel mese (dopo la fine del mese
  prima e fino a questo giorno), il **20% con la reazione più alta**, al massimo 50 (i più alti; a pari valore in ordine alfabetico);
  se i comunicati ammessi sono meno di 25, quel mese si resta fuori. Un titolo con due comunicati nel mese conta con l'ultimo.
* **Posizioni:** comprati a pesi uguali per il **50%** del conto; venduto allo scoperto l'**IWM** per il **50%**; ordini a mercato
  all'apertura del primo giorno di borsa del mese dopo; si tiene un mese.
* **Periodo:** decisioni dalla fine di gennaio 2016 alla fine di novembre 2024; rendimenti dal febbraio 2016 al 31 dicembre 2024. Il
  periodo chiuso (2025-01 → 2026-09) non si guarda: il programma non usa comunicati dopo il 31 dicembre 2024.

## I costi (come le prove 27-32 sulle piccole)

Metà scarto 15 punti base e slittamento 5; commissioni Interactive Brokers «fisso»; prestito dell'IWM venduto allo scoperto **1%
l'anno**. Versione con tutti i costi raddoppiati.

## L'esame (uguale alla prova 32)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte con i costi almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000
campionamenti a blocchi di 20 giorni.

Da leggere accanto (non sono prove): quanti comunicati ammessi ogni mese; il quinto con la reazione più alta meno il quinto più basso, e
il quinto alto meno l'IWM, mese dopo, senza costi, con il t; la correlazione con lo SPY; i titoli chiusi perché spariti dal listino; il
risultato anno per anno. **Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (la famiglia «bilanci» non l'ha mai
usato), poi la misura in avanti sul demo.
