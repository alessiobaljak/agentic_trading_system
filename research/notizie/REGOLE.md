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

## Aggiunta del 31 ottobre 2026 (16:23 UTC): le monete di tendenza di CoinGecko

* **Cosa**: a ogni giro della raccolta si legge anche la lista pubblica delle monete più cercate su CoinGecko (`search/trending`, 15
  monete) e la si salva in `archivio/tendenze.csv` (ora, posizione, id, sigla, nome, posizione per capitalizzazione). È l'idea 126 del
  registro: la famiglia dell'attenzione, chi compra quello che tutti guardano paga troppo.
* **Perché da oggi**: lo storico gratuito di questa lista non esiste; l'unico modo di averlo è raccoglierlo.
* **Quando si prova**: in avanti, quando ci sono almeno 6 mesi di dati (non prima del 30 aprile 2027), con regole scritte prima di
  guardare i dati raccolti. Fino ad allora la lista non si usa per nessuna decisione.

## Aggiunta del 1° novembre 2026: niente attese fisse

Il proprietario, 1° novembre 2026: «perché il 30 novembre? devo per forza aspettare un mese? [...] verdetto dopo 52 settimane? questo
è inaccettabile, cosa usiamo a fare il backtesting e demo se devo aspettare 52 settimane». Ha ragione: lo aveva già detto il 21 ottobre
(«si giudica sul passato di Binance, il paper è una conferma, non una condizione») e il 24 ottobre («usiamo i dati passati e simuliamo con
paper / live demo per qualche giorno, settimana, ma poi se funziona andiamo live»). Quindi, **da oggi e per tutte le misure in avanti di
questo file** (comprese quelle scritte prima con le 52 e le 104 settimane):
* **niente attese fisse**: le 26, 52 e 104 settimane non sono più condizioni; restano solo come date in cui si rifà il conto per informazione;
* **i numeri vanno al proprietario ogni settimana**, con il confronto con il passato e con G1 negli stessi giorni, detti chiari anche
  quando sono pochi («4 settimane non bastano a dire che funziona» si scrive, ma non blocca niente);
* **cosa decide**: quello che passa la regola del proprietario sul passato (sezione 1 del registro: Sharpe corretto da 0,90 in su, ogni
  anno positivo, t sopra 3) va subito in paper e sul demo; dopo qualche giorno o settimana di demo che esegue come il paper, **i soldi
  veri li decide il proprietario quando li chiede in modo esplicito** (regola di `CLAUDE.md`: `DRY_RUN` resta vero fino ad allora);
* le idee nate dai dati, che sul passato non si possono giudicare in modo pulito, vanno in paper (soldi finti) appena si può, e il
  proprietario decide quando ha visto abbastanza.

Per le notizie: la regola si è già provata sui titoli del 2026 (prova 147, `programma7/RISULTATI_OTTANTACINQUESIMA.md`); il primo calcolo
con la nostra raccolta resta il 30 novembre solo perché la regola conta gli articoli dei 28 giorni prima.

## Aggiunta del 4 novembre 2026: la seconda pagina di Crypto Briefing

Il 2 e il 3 novembre la pagina di Crypto Briefing (30 articoli) è stata tre volte tutta nuova fra un giro e l'altro: qualche articolo
sfuggiva. Da oggi si legge anche la seconda pagina (`cryptobriefing2` in `raccolta.py`); gli articoli già visti si riconoscono dal link,
quindi non si contano due volte. Le fonti lette diventano 22 (la stessa testata con due pagine). La regola della prova in avanti non
cambia: conta gli articoli, non le fonti.

## Aggiunta del 6 novembre 2026: la seconda pagina di BeInCrypto

La pagina di BeInCrypto ha 12 articoli, circa 5 ore; il 6 novembre è stata tutta nuova due volte (alle 04:20 e alle 16:20,
`archivio/giri.csv`). Da oggi si legge anche la seconda pagina (`beincrypto2` in `raccolta.py`), come per Crypto Briefing: gli articoli
già visti si riconoscono dal link. Le fonti lette diventano 23. La regola della prova in avanti non cambia.

## Aggiunta del 10 novembre 2026: la terza pagina di Crypto Briefing

Il 10 novembre alle 16:18 erano piene sia la prima sia la seconda pagina di Crypto Briefing (164 articoli nuovi nel giro, il giorno di
più notizie da quando si raccoglie): qualche articolo può essere sfuggito. Da oggi si legge anche la terza pagina (`cryptobriefing3` in
`raccolta.py`); gli articoli già visti si riconoscono dal link, quindi non si contano due volte. Le fonti lette diventano 24. La regola
della prova in avanti non cambia: conta gli articoli, non le fonti.

## Aggiunta del 27 novembre 2026 (audit del 26 novembre)

Scritta prima del primo calcolo della prova in avanti: nessun numero della regola è stato guardato. **La regola della sezione 3 non
cambia.**

* **Le parole comuni (sezione 2), da oggi**: in `PAROLE` entrano anche **ARK, HIVE, GENIUS, SATS e APR** (`PAROLE_27_NOVEMBRE` in
  `raccolta.py`). Nel conto automatico davano abbinamenti falsi: ARK Invest (ARKUSDT, 23 articoli di novembre), la società di mining HIVE
  (9), la legge GENIUS sulle monete stabili (8), le azioni SATS di Strive (1000SATSUSDT, 6), «APR» il tasso annuo (APRUSDT, 4); numeri
  dell'audit del 26 novembre, `raccolta.citate` sugli 11.697 articoli di novembre. Con il «$» davanti si contano ancora. **ANT non
  entra**: dal 17 novembre ANTUSDT di Binance è il perpetuo sulle azioni di Anthropic (il verificatore dell'audit, da exchangeInfo), quindi
  gli articoli su Anthropic parlano proprio di quel contratto; è l'elenco del mese che dice ancora «Autonomi». La prova in avanti riporta
  ogni settimana il conto con le parole di oggi (la misura) e senza le cinque sigle nuove (`PAROLE_FINO_AL_26_NOVEMBRE`), per vedere quanto
  pesano gli abbinamenti falsi.
* **«Piena» (sezione 1), da oggi**: si calcola per sito, non per pagina. Un sito letto con più pagine (Crypto Briefing con quattro,
  BeInCrypto con due) è «pieno» solo se gli articoli nuovi riempiono tutto quello che le sue pagine hanno dato, e la nota va sulla riga
  della sua ultima pagina. Prima bastava una pagina tutta nuova: il 26 novembre alle 16:18 la prima pagina di Crypto Briefing era tutta
  nuova ma la seconda aveva 16 articoli nuovi su 30 (gli altri già visti), e il diario ha segnalato una perdita che non c'era.
* **Gli articoli già visti (sezione 1), da oggi**: la raccolta riconosce un collegamento già visto in tutto l'archivio, non più solo negli
  ultimi 10 giorni. Prima un articolo rimasto in pagina più di 10 giorni si salvava di nuovo (al 27 novembre alle 02:14: 12.866 righe per
  12.849 articoli diversi; fra i doppi la pagina fissa di Cointelegraph «Here's what happened in crypto today»). Le righe doppie già
  salvate restano nell'archivio; la prova in avanti conta ogni articolo una volta sola, la prima volta che l'abbiamo visto.
* **Le ore (sezione 1)**: nell'archivio sono in UTC e si scrivono senza il fuso. `raccolta.ora_utc` le legge sempre in UTC, qualunque sia
  il fuso della macchina (`fromisoformat` seguito da `astimezone` le prendeva come ora locale: con l'ora svizzera la finestra si
  spostava di 1 ora, 2 d'estate). La usa la prova in avanti.
* **Come `prova_avanti.py` legge la sezione 3** (nessun cambio della regola, solo le scelte che il testo lascia aperte, fissate prima):
  * «gli articoli raccolti nei 28 giorni fino al giorno l − 2»: gli articoli che la raccolta ha visto (ora `visto`, in UTC) dal giorno
    l − 29 al giorno l − 2 compresi, come la prova 147 contava il giorno di raccolta dei titoli; più uno, diviso il volume in dollari del
    perpetuo (`quote_volume` del pannello del programma 6) negli stessi giorni, in logaritmo;
  * le monete citate secondo `raccolta.citate`, con l'elenco dei nomi del mese in cui l'articolo è stato visto (sezione 2);
  * «almeno 3 articoli nei giorni raccolti fino a l − 2 (al massimo 112)»: dal 30 ottobre 2026, primo giorno della raccolta (o dai 112
    giorni prima, quando saranno dopo), al giorno l − 2;
  * universo di G1 della settimana, volatilità, banda, almeno 20 monete, costi e funding: le stesse funzioni del conto a tavolino e delle
    prove 138 e 147 (`terza.pannello_settimane`, `ottava.sigma_30`, `ventiquattresima.pesi_banda`, `terza.conto`); la banda parte vuota il
    30 novembre;
  * una settimana si conta quando è finita, cioè dal lunedì dopo: il primo numero (la settimana dal 30 novembre al 6 dicembre) arriva il
    7 dicembre; il 30 novembre lo script dice solo che non ci sono ancora settimane finite;
  * accanto, G1 a tavolino sulle stesse settimane (le regole di `programma7/prima.py`, banda dal 4 gennaio 2021), con le spese a limite
    (a mercato dove mancano le candele a 1 ora) e tutto a mercato.
