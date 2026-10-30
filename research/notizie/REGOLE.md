# La raccolta delle notizie crypto e la prova in avanti del «volume senza notizie»

Scritto il 30 ottobre 2026 alle 12:39 UTC (ora dell'orologio), **prima che arrivi qualunque articolo raccolto**. Il proprietario (30
ottobre): «ok parti con la raccolta gratuita da oggi». Nasce dalla prova 138 (`research/programma7/RISULTATI_SETTANTASEIESIMA.md`): il
verso opposto di GA2 (comprare le monete con tanti articoli per dollaro scambiato, vendere quelle molto scambiate senza notizie) faceva
Sharpe 0,93 sul 2021 – gennaio 2025, ma è nato guardando quei dati (idea 116 del registro). L'archivio di CoinDesk finisce a febbraio 2025 e
il servizio gratuito che lo alimentava non esiste più dal 21 maggio 2026: gli articoli nuovi si raccolgono da qui in avanti, dalle pagine
pubbliche degli ultimi articoli dei siti.

## 1. Cosa si raccoglie

* **Le fonti** (21, le pagine pubbliche con gli ultimi articoli, controllate il 30 ottobre): Cointelegraph, CoinDesk, Decrypt, The Block,
  CryptoSlate, NewsBTC, Bitcoin Magazine, U.Today, AMBCrypto, CoinGape, CryptoPotato, BeInCrypto, Cryptonews, The Daily Hodl, Crypto
  Briefing, CoinJournal, crypto.news, Bitcoinist, ZyCrypto, CoinCodex, The Defiant. L'elenco esatto è in `raccolta.py` (`FONTI`); una fonte
  che smette di rispondere resta nell'elenco e si conta come vuota.
* **Ogni articolo**: la fonte, il titolo, il sommario (senza HTML, al massimo 500 caratteri), il collegamento, l'ora di pubblicazione
  (UTC) e l'ora in cui l'abbiamo visto. Un articolo si riconosce dal collegamento: chi l'ha già visto non lo salva una seconda volta.
* **Dove**: `research/notizie/archivio/AAAA-MM-GG.jsonl.gz`, uno per giorno di raccolta, dentro il repo (sono dati pubblici: titoli e
  collegamenti). Ogni giro scrive anche una riga in `research/notizie/archivio/giri.csv`: quanti articoli ha dato ogni fonte e quanti erano
  nuovi; se tutti gli articoli di una fonte erano nuovi, forse ne abbiamo persi (la pagina ne mostra pochi): si scrive «piena».
* **Quando**: a ogni giro della ricerca continua (ogni 4 ore) e a ogni aggiornamento del mattino. Un giro saltato si scrive, non si
  ricostruisce.

## 2. Di quale moneta parla un articolo (fissato qui, uguale per tutto il periodo)

* **L'elenco dei nomi**: le prime 1.000 monete di CoinGecko per valore (sigla e nome), abbinate ai perpetui di Binance con
  `annunci.perpetuo`; se due monete hanno la stessa sigla vale quella con il valore più alto. L'elenco si rifà il primo giorno di ogni mese
  con i dati di quel giorno (`nomi_AAAA-MM.json`), così le monete nuove entrano senza guardare avanti.
* **Un articolo cita una moneta** se nel titolo o nel sommario c'è:
  * la **sigla in maiuscolo come parola intera**, solo se ha almeno 3 lettere e non è nell'elenco delle sigle che sono anche parole comuni
    (`PAROLE` in `raccolta.py`, per esempio ONE, ALL, GAS, SUN, NOT, WIN, HOT, KEY, BAND, FLOW, MOVE, PEOPLE), oppure preceduta da «$» (anche
    se corta);
  * oppure il **nome** con la maiuscola come parola intera, solo se il nome ha almeno 5 lettere e non è una parola comune (stesso elenco).
* Il Bitcoin e l'Ether si contano come le altre.
* **Differenza scritta prima**: nell'archivio di CoinDesk le monete erano assegnate dalla fonte (il campo `categories`), qui le assegniamo
  noi con questa regola. La prova in avanti verifica l'idea, non la stessa identica misura.

## 3. La prova in avanti (scritta prima)

* **La regola, GA2 al contrario** (la regola GA2 di `programma7/SETTANTASEIESIMA.md` con il verso opposto): ogni lunedì l, per ogni moneta
  dell'universo di G1 della settimana, il numero degli articoli raccolti che la citano nei 28 giorni fino al giorno l − 2 (più uno), diviso
  il volume in dollari del perpetuo negli stessi giorni, in logaritmo; **long il quinto con il valore più alto, short il quinto con il più
  basso**, banda 20/40, pesi secondo l'inverso della volatilità, almeno 20 monete con almeno 3 articoli nei giorni raccolti fino a l − 2 (al
  massimo 112), costi e funding come F5.
* **Da quando**: dal primo lunedì con 28 giorni di raccolta prima di l − 2, cioè dal **30 novembre 2026**.
* **Il verdetto**, come il conto a tavolino del programma 6: un'occhiata a 26 settimane (giugno 2027) e il **verdetto a 52 settimane**
  (novembre 2027): la regola regge se lo Sharpe delle 52 settimane è sopra 0,5 e sopra quello di G1 sulle stesse settimane. Prima i numeri
  sono informazione. Il calcolo settimanale si aggiunge al conto a tavolino quando ci sono i primi 28 giorni (voce P31 del backlog).
