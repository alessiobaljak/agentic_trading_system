# Prova 36 — gli acquisti dei dirigenti comprati subito: due minuti dopo la pubblicazione alla SEC, venduti all'apertura dopo

Regole scritte il 16 novembre 2026 **prima di qualsiasi calcolo sui prezzi** e prima di scaricare i prezzi al minuto (idea I22 di
`REGISTRO.md`). Si conoscevano le prove 1-35, in particolare la 18 (da cui nasce l'idea), la 19 e la 27, e la lezione della 35 (in
giornata sui titoli singoli serve un vantaggio di più di circa 0,25% a operazione prima dei costi, oppure titoli con lo scarto di pochi
punti base). Contano come **2 prove** (la strategia da sola, e la miscela con lei): 89 nel conto.

## Perché dovrebbe funzionare

La prova 18 (`P018_risultati.md`, correzione del 25 ottobre) ha misurato su 2'656 acquisti di dirigenti nell'S&P 500 che il titolo
sale dello **0,42% più dello SPY nella notte dopo il deposito** (t 15,7), e che dall'apertura dopo in poi non resta niente (−0,04% in
20 sedute). Il mercato reagisce, ma solo nelle ore dopo la pubblicazione: chi compra all'apertura del giorno dopo arriva tardi. Il
modulo 4 **è** l'annuncio (non c'è un comunicato prima, a differenza dei risultati trimestrali: `stock/dati/bilanci.py`), quindi l'ora
in cui la SEC lo accetta è l'ora in cui il pubblico lo sa. Lo 0,42% è più grande dei costi di un titolo dell'S&P 500 (lo scarto delle
grandi è di 0,8-5,8 punti base in seduta: `stock/dati/ESITO_CONTROLLI.md`). La domanda della prova: **quanto ne resta a chi arriva due
minuti dopo la pubblicazione, anche fuori dalla seduta, pagando i costi veri?**

**Fatti noti prima (solo conteggi, nessun prezzo visto):** `stock/prove/dati/P036_depositi.csv.gz` (da `python -m
stock.dati.depositi_dirigenti`, dati pubblici della SEC): 5'559 moduli 4 con acquisti sul mercato di dirigenti o consiglieri, di
aziende nell'S&P 500 al giorno del deposito, dal 2016 al 2024, con l'ora di accettazione; 25 senza ora (azienda senza elenco). Dei
2'978 da almeno 100'000 dollari: **1'936 accettati fra le 16:00 e le 20:00** di New York, 672 in seduta, 182 fra le 4:00 e le 9:30,
176 fra le 20:00 e le 24:00, 12 fra mezzanotte e le 4:00.

**Sospetti scritti prima (forti):**

* **l'idea nasce dal risultato della prova 18 sugli stessi anni**: il 2016-2024 non conferma che l'effetto esista (lì è già stato
  visto); misura quanto ne prende chi arriva con l'ora vera e i costi veri. Il periodo chiuso della famiglia «dirigenti» è già stato
  aperto dalla prova 19: **la conferma indipendente è solo in avanti**;
* **chi riceve i depositi della SEC a pagamento arriva prima** (secondi): due minuti possono bastare perché il prezzo si sia già mosso,
  soprattutto in seduta;
* **fuori dalla seduta** (due depositi su tre) lo scarto è largo e le operazioni rade: l'apertura di una barra può essere lontana dalle
  quotazioni, e il risultato dipenderà quasi tutto da lì;
* **pochi eventi**: circa 1,3 al giorno di borsa; il capitale resta fermo quasi sempre, lo Sharpe del conto può essere basso anche con
  un vantaggio vero a operazione.

## La regola

* **Gli eventi:** i moduli del file qui sopra; si scarta un modulo con il prezzo medio dell'operazione oltre il 50% dalla chiusura del
  giorno dell'operazione (o del giorno di borsa prima), come nella prova 18.
* **La soglia:** si entra con il modulo che porta **ad almeno 100'000 dollari** la somma dei moduli della stessa azienda nella stessa
  «notte di borsa» (dalle 16:00 di una seduta alle 16:00 della seduta dopo). Al massimo un ingresso per azienda per notte di borsa; un
  modulo che arriva mentre la posizione è aperta non cambia niente.
* **Quando si sa:** l'ora di accettazione della SEC **più 2 minuti** (leggere la SEC e mandare l'ordine).
* **L'ingresso:** all'apertura della prima barra al minuto (tutte le borse, Alpaca, simbolo di allora) che inizia almeno 2 minuti dopo
  l'accettazione, **fra le 4:00 e le 19:59 di New York** in un giorno di borsa (gli orari estesi, in cui Alpaca accetta ordini limite).
  Un deposito accettato fra le 20:00 e le 4:00, o nei giorni senza borsa, entra dalle 4:00 del primo giorno di borsa dopo. Se in un
  giorno non c'è nessuna barra nella finestra, si continua dalle 4:00 del giorno di borsa dopo.
* **L'uscita:** all'**apertura ufficiale** (la barra al giorno, prezzo «open», l'asta d'apertura) della prima seduta che apre dopo
  l'ingresso: un ingresso fra le 4:00 e le 9:29 esce all'apertura di quel giorno; uno dalle 9:30 in poi all'apertura del giorno dopo.
* **Quanto:** il **10%** del valore del conto all'inizio del giorno dell'ingresso; al massimo **10 posizioni** insieme (oltre, si salta,
  in ordine d'arrivo); azioni intere; niente leva. Il guadagno di un'operazione si conta nel giorno dell'uscita.
* **Periodo:** i depositi dal 4 gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima)

**Metà dello scarto misurato**: le quotazioni migliori di Alpaca (tutte le borse) per un campione di **500 ingressi** estratti a caso
(seme 36), l'ultima quotazione valida prima della fine del minuto dell'ingresso (`stock/dati/scarto.py`); la mediana **separata per
fascia**, «in seduta» (9:30-15:59) e «fuori seduta» (4:00-9:29 e 16:00-19:59), applicata a tutti gli ingressi della fascia.
**Slittamento 2 punti base** all'ingresso e 2 all'uscita; all'asta d'apertura nessuno scarto. Commissioni Interactive Brokers «fisso»
(0,005 dollari ad azione, minimo 1 dollaro, massimo l'1% del valore). Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-35)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti
a blocchi di 20 giorni.

Da leggere accanto (non sono prove e non cambiano l'esito): operazioni, quota in guadagno, guadagno medio a operazione prima e dopo i
costi rispetto allo SPY negli stessi minuti; per fascia (in seduta, dopo la chiusura, prima dell'apertura); lo scarto misurato per
fascia (mediana, media, 90° percentile); i ritardi di 1, 5, 15 e 60 minuti al posto di 2; la versione coperta (la stessa cifra venduta
sullo SPY negli stessi minuti, chiusa all'apertura dello SPY); il movimento dalla chiusura prima del deposito all'ingresso (quanto si
perde arrivando dopo); il risultato anno per anno.

**Se passa uno dei due esami:** revisore separato, poi la misura **in avanti** sul demo (nessun periodo chiuso: già usato dalla
famiglia). Per farla servono la lettura della SEC ogni minuto dalle 4:00 alle 20:00 (sulla VPS) e ordini limite negli orari estesi:
si scrive dopo il revisore.
