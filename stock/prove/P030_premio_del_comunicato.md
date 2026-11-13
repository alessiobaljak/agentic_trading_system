# Prova 30 — le azioni dell'S&P 500 nella settimana in cui pubblicano i risultati, coperte con lo SPY

Regole scritte il 13 novembre 2026 **prima di qualsiasi calcolo** (idea I32 di `REGISTRO.md`). Si conoscevano le prove 1-29; nessun
rendimento e nessun conteggio delle settimane con le date previste è stato guardato prima di scrivere questo file. Contano come
**2 prove** (la strategia da sola, e la miscela con lei): 77 nel conto.

## Perché dovrebbe funzionare

Le azioni rendono di più nei giorni in cui l'azienda pubblica i risultati che negli altri giorni, e la data si può prevedere da quella
dell'anno prima. È uno degli effetti più vecchi e più confermati: Beaver, *Journal of Accounting Research* 6 (1968); Chari,
Jagannathan, Ofer, «Seasonalities in security returns: the case of earnings announcements», *Journal of Financial Economics* 21 (1988);
Frazzini e Lamont, «The earnings announcement premium and trading volume», NBER 13090 (2007), con la data prevista dall'anno prima;
Barber, De George, Lehavy, Trueman, «The earnings announcement premium around the globe», *Journal of Financial Economics* 108 (2013),
in molti paesi e soprattutto nei giorni vicini al comunicato; Savor e Wilson, «Earnings announcements and systematic risk», *Journal of
Finance* 71 (2016). Le spiegazioni: chi tiene il titolo nei giorni del comunicato si prende un rischio che non si diversifica e va
pagato; e prima del comunicato l'attenzione e gli acquisti aumentano.

Perché proprio adesso: è un effetto **di calendario**, come il più forte trovato finora sull'indice (prima della banca centrale,
prova 7: per evento +0,23%, t 2,9, poi non confermato nel periodo chiuso dalle prove 9 e 14), ma sulle singole azioni; ed è coperto con lo SPY, quindi dovrebbe muoversi poco con
la miscela (prove 26 e 27: le parti che seguono il mercato non entrano). Le date dei comunicati della SEC sono già scaricate (prova 20).

**Sospetti scritti prima:**

* è noto da decenni e pubblicato molte volte: può essersi ridotto, soprattutto nelle 500 grandi, che sono le più seguite;
* parte del guadagno può essere solo **mercato**: nei giorni del comunicato le azioni si muovono di più con l'indice (Savor e Wilson);
  coprire un dollaro con un dollaro di SPY non toglie tutto. Si stampa il beta della strategia rispetto allo SPY;
* **i costi**: si cambia quasi tutto ogni settimana. Con 100'000 dollari e fino a 50 titoli da circa 1'000 dollari, la commissione
  minima di Interactive Brokers (1 dollaro a ordine) pesa circa lo 0,1% a ogni passaggio: può mangiare tutto il vantaggio;
* la data prevista è approssimata: l'azienda può pubblicare una settimana prima o dopo dell'anno prima, e nella prova 20 la data
  del deposito è a volte il giorno dopo il comunicato. Si stampa quante delle scelte hanno davvero depositato un comunicato nella
  settimana (controllo, non regola);
* la famiglia «bilanci» (prove 10, 20, 21) non ha mai trovato niente nelle grandi; ma quelle prove guardavano la reazione dopo il
  comunicato, non i giorni intorno.

## I dati

* **Le date dei comunicati:** i moduli 8-K con la voce 2.02 della SEC per ogni azienda che è stata nell'S&P 500 fra il 2016 e il 2024
  (lo stesso elenco della prova 20, `stock/dati/eventi_minuti.py`, un comunicato per trimestre), messe nel repository in
  `stock/prove/dati/P030_comunicati.csv.gz` (sono dati pubblici della SEC: simbolo di allora e data del deposito, nient'altro).
* **I prezzi:** al giorno di Alpaca, non rettificati, con dividendi e frazionamenti, con il **simbolo di allora** (`asof` «-»), come la
  prova 28; un titolo in mano che resta 5 giorni di borsa senza prezzi si chiude all'ultima chiusura e si conta.
* **La composizione dell'S&P 500:** `stock/prove/dati/P028_membri.csv.gz` (fine di ogni mese, simboli di allora); per una decisione a
  metà mese vale l'ultimo fine mese prima.

## La regola

* **La data prevista:** per ogni comunicato depositato il giorno D, la data prevista dell'anno dopo è **D + 364 giorni** (lo stesso
  giorno della settimana, 52 settimane dopo), come fanno gli studi con la data dell'anno prima.
* **Ogni settimana**, all'ultima chiusura della settimana: fra i membri dell'S&P 500 con la barra di quel giorno, quelli con una data
  prevista **dopo il primo giorno di borsa della settimana dopo e fino al venerdì** di quella settimana. Il primo giorno è escluso per
  logica, non per i dati: un comunicato del lunedì mattina arriva prima del nostro ordine all'apertura e il suo salto non si prende.
* Se sono più di **50**, i primi 50 in ordine alfabetico (un ordine che non ha a che fare con i rendimenti); se sono meno di **10**,
  quella settimana si resta fuori (tutto chiuso).
* **Posizioni:** i titoli scelti a pesi uguali per il **50%** del conto; venduto allo scoperto lo **SPY** per il **50%**; ordini a
  mercato all'apertura del primo giorno di borsa della settimana dopo; si tiene fino all'apertura del primo giorno di borsa della
  settimana seguente, quando si passa alla scelta nuova.
* **Periodo:** le date previste partono dai comunicati del 2016, quindi le decisioni partono dall'ultima settimana del 2016; rendimenti
  dal gennaio 2017 al 31 dicembre 2024. Il periodo chiuso (2025-01 → 2026-09) non si guarda.

## I costi (fissati prima, come le prove 11, 24 e 28 sulle azioni dell'S&P 500)

Metà dello scarto misurato dove c'è (`dati/ESITO_CONTROLLI_UNIVERSO.md`), altrimenti 5 punti base più 2 di slittamento; lo SPY con lo
scarto misurato e 0,5 punti base di slittamento; prestito dello SPY venduto allo scoperto **0,5% l'anno**; commissioni Interactive
Brokers «fisso» (0,005 dollari ad azione, minimo 1 dollaro a ordine). Versione con tutti i costi raddoppiati.

## L'esame (uguale alla prova 28)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione dei rendimenti
giornalieri con la miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe
più alto della miscela e del tenere lo SPY.

Da leggere accanto (non sono prove): quanti titoli con la data prevista ogni settimana e quante settimane fuori; il rendimento medio
della settimana di **tutti** i titoli con la data prevista (senza il limite di 50) meno lo SPY, dall'apertura all'apertura, senza
costi, con il suo t; quante delle scelte hanno depositato davvero un comunicato nella settimana; il beta rispetto allo SPY; il
risultato anno per anno. **Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (la famiglia «bilanci» non l'ha mai
usato), poi la misura in avanti sul demo.
