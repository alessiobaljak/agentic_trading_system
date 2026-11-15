# Prova 35 — le azioni «in gioco»: ogni mattina le 20 con il volume dei primi 5 minuti più alto del solito, la rottura della prima candela

Regole scritte il 15 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare i prezzi al minuto (idea I37 di `REGISTRO.md`,
nata dalla domanda del proprietario: «perché solo le 10 più scambiate, perché non controllare tutte le azioni nei primi 15 minuti»).
Si conoscevano le prove 1-34, in particolare la 17, la 20, la 21 e la 23 (la prima candela, sempre bocciata dopo i costi) e la sola
sintesi pubblica dello studio (sotto). Contano come **2 prove** (la strategia da sola, e la miscela con lei): 87 nel conto.

## Perché dovrebbe funzionare

Zarattini, Barbon, Aziz, «A profitable day trading strategy for the U.S. equity market», SSRN 4729284 e Swiss Finance Institute 24-98
(2024): la rottura dei primi 5 minuti funziona solo sulle azioni **in gioco** quel giorno, cioè con un volume dei primi minuti molto più
alto del solito (una notizia, un fatto nuovo): lì il movimento della mattina continua. Dichiarano, dal 2016 al 2023, il 41,6% l'anno e
Sharpe 2,81 al netto delle sole commissioni (sintesi di CXO Advisory, «Intraday trading of overactive stocks via opening range
breakout»). Le regole qui sotto sono le loro, come riportate in quella sintesi.

**Sospetti scritti prima (forti):**

* **lo scarto**: lo studio conta solo le commissioni. Nella prova 20 (le azioni dell'S&P 500 con un comunicato, la stessa idea nei
  giorni dei bilanci) lo scarto vero alle 9:35 era di **23 punti base** di mediana, e ha mangiato tutto il vantaggio (+0,128% a
  operazione prima dei costi). Qui lo stop è a un decimo del movimento medio di un giorno: spesso lo scarto è grande quanto lo stop;
* **gli stop eseguiti al prezzo dello stop** in un mercato veloce sono ottimisti: con le barre al minuto si esegue al peggiore fra lo
  stop e l'apertura del minuto, più 5 punti base di slittamento;
* **il periodo 2016-2023 è quello su cui lo studio ha scelto le regole**: su quegli anni la prova ripete il loro calcolo con i nostri
  costi, non è una conferma indipendente; la conferma indipendente è solo **in avanti** (il periodo chiuso della famiglia «in giornata»
  è già stato aperto dalla prova 2 su QQQ);
* **la leva**: lo studio arriva fino a 4 volte il capitale; la leva è una decisione del proprietario (regola della prova 2): qui si
  calcola come lo studio e si stampa accanto la versione senza leva.

## I dati

* **Le azioni:** le azioni americane (simboli di 1-4 lettere più le classi «.A», «.B», come la prova 32: i simboli di FINRA e i membri
  dell'S&P 500), esclusi i fondi (lo stesso elenco di parole della prova 28); prezzi al giorno di Alpaca con il simbolo di allora.
* **I primi 5 minuti:** le barre al minuto dalle 9:30 alle 9:34 di New York, di tutte le borse (Alpaca, simbolo di allora), per ogni
  titolo che passa i filtri del giorno o dei 14 giorni prima; poi le barre al minuto dalle 9:30 alle 16:00 dei soli 20 scelti.
* **Lo scarto:** le quotazioni migliori di Alpaca (tutte le borse) per un campione di **500 operazioni** estratte a caso (seme 35),
  nel minuto dell'ingresso e nel minuto dell'uscita; l'ultima quotazione valida prima della fine del minuto (`stock/dati/scarto.py`).
  Nel repository vanno solo i risultati.

## La regola (dallo studio)

* **Chi può entrare, ogni giorno:** apertura sopra **5 dollari**; volume medio giornaliero delle 14 sedute prima di almeno **1 milione
  di azioni**; escursione media (ATR) delle 14 sedute prima sopra **0,50 dollari**.
* **Il volume relativo:** il volume dei primi 5 minuti di oggi diviso la media del volume dei primi 5 minuti delle 14 sedute prima;
  almeno **1** (100%). Si scelgono i **20** con il volume relativo più alto (a pari valore, in ordine alfabetico).
* **La direzione:** se la candela dei primi 5 minuti chiude sopra l'apertura, un ordine stop di **acquisto** al massimo dei 5 minuti;
  se chiude sotto, un ordine stop di **vendita allo scoperto** al minimo; se chiude uguale, niente. L'ordine vale dalle 9:35 alla
  chiusura: se il prezzo non lo raggiunge, niente.
* **Lo stop:** a un decimo dell'ATR dal prezzo eseguito. **L'uscita:** allo stop, oppure alla chiusura delle 15:59.
* **Quanto:** ogni operazione rischia l'**1%** del capitale all'inizio del giorno (perdita allo stop); il conto non supera **4 volte**
  il capitale (interpretazione scritta prima: ogni operazione al massimo un ventesimo di 4 volte il capitale); azioni intere.
* **Le esecuzioni con le barre al minuto:** l'ingresso al peggiore fra il prezzo dello stop d'ingresso e l'apertura del primo minuto che
  lo raggiunge; lo stop al peggiore fra il suo prezzo e l'apertura del minuto che lo tocca; se il minuto dell'ingresso tocca anche lo
  stop, si esce allo stop in quel minuto (il caso peggiore, perché l'ordine dentro il minuto non si conosce).
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024 (i primi 14 giorni servono solo per le medie). Il periodo chiuso non si usa.

## I costi (fissati prima)

Metà dello **scarto misurato** sul campione (la mediana all'ingresso e la mediana all'uscita, applicate a tutte le operazioni);
**slittamento 5 punti base** su ogni esecuzione stop (ingresso e stop), 2 all'uscita della chiusura; commissioni Interactive Brokers
«fisso» (0,005 dollari ad azione, minimo 1 dollaro); prestito delle vendite allo scoperto in giornata: nessuno. Versione con tutti i
costi raddoppiati, e versione con le sole commissioni (per confrontarsi con lo studio).

## L'esame (uguale alle prove 28 e 30-34)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti
a blocchi di 20 giorni.

Da leggere accanto (non sono prove): operazioni, quota in guadagno, guadagno medio a operazione prima e dopo i costi; lo scarto
misurato (mediana, media, 90° percentile) confrontato con lo stop medio in punti base; la versione senza leva; il risultato anno per
anno. **Se passa uno dei due esami:** revisore separato, poi la misura **in avanti** sul demo (nessun periodo chiuso: già usato dalla
famiglia «in giornata»), con la leva solo se il proprietario la approva.
