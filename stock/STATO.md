# Lo stato delle azioni

Da leggere per primo, dopo `README.md`. Aggiornato il 24 ottobre 2026.

## Cosa ha deciso il proprietario

* Mercato: **America** (24 ottobre).
* Obiettivo: il profitto; prima le prove sul passato, poi il paper su un conto demo, poi (solo su sua richiesta esplicita) i soldi
  veri. Nessuna strategia imposta: in giornata o su più giorni, ingressi, uscite e indicatori li sceglie la sessione (24 ottobre).
* Titoli: per ora le **10 azioni più grandi**, poi si vedrà se allargare (24 ottobre).
* Le richieste delle crypto (per esempio il trading in giornata) non valgono qui: le azioni partono da zero (24 ottobre).
* Prezzi storici: conto demo gratuito di **Alpaca** (Trading API), chiavi messe dal proprietario nell'ambiente con i nomi
  `ALPACA_API_KEY_ID` e `ALPACA_API_SECRET_KEY` (24 ottobre). Mai scriverle, stamparle o committarle.

* **Sì alle proposte di `METODO.md`** (24 ottobre): nelle prove sul passato le 10 azioni più scambiate *di allora* più SPY e QQQ;
  l'indice come asticella; il periodo chiuso da gennaio 2025 a settembre 2026; le condizioni per il demo e per i soldi veri.
* **Piattaforma del demo: Interactive Brokers** (24 ottobre).
* **Il periodo chiuso si riusa per idee di famiglie diverse** (24 ottobre: «sì, riusa il periodo chiuso per idee diverse»): non per
  altre regole in giornata che seguono il movimento dell'indice (la famiglia della prova 2); ogni apertura conta come una prova in più
  nel registro e nell'asticella.
* **Universo allargato a tutte le azioni dell'S&P 500** (24 ottobre: «sì, allarga a tutte le azioni dell'S&P 500»): le prove nuove
  usano i titoli che erano nell'indice in quel momento (circa 500, 717 in tutto dal 2016 al 2024), non più solo le 10 più scambiate.
* **Ricerca più ampia, anche sulle 10 grandi** (24 ottobre: «ti consiglio di ampliare notevolmente la ricerca ma soprattutto di non
  seguire le regole standard su internet [...] è la tua capacità di leggere informazioni diverse e metterle insieme [...] non è che se le
  10 più scambiate sono fallite che non riprovi più strategie su queste»): idee proprie e combinazioni di informazioni diverse, su tutti
  gli universi (10 grandi compresi), sempre con regole scritte prima e il conto delle prove. Provare la leva nei giorni prima della banca
  centrale, senza chiedere.
* **Autonomia** (24 ottobre: «procedi in autonomia su diverse idee non chiedermi il permesso ma fammi sapere quando vogliamo fare la demo
  su Interactive Brokers»): la sessione prova le idee da sola, con il metodo, e scrive al proprietario quando una strategia è pronta
  per il demo.

## Cosa aspetta il proprietario

1. **Aprire il conto Interactive Brokers** (tipo «Pro», non «Lite»: l'interfaccia per i programmi vale solo per i conti Pro [IB1]),
   farlo approvare e depositare (è la condizione per avere il demo, `piattaforme.md`). Poi, nel portale clienti, Impostazioni →
   conto di paper trading: lì c'è il **nome utente del demo**, diverso da quello del conto vero, e conviene dargli una password sua
   («Reset Paper Trading Password») [IB2]. Le credenziali non vanno mai scritte in chat né nel repository.
2. **Dove gira il collegamento**, da decidere più avanti. Interactive Brokers non dà una chiave come Alpaca: per un conto privato il
   programma parla con un piccolo programma di Interactive Brokers (il «Gateway»), che deve restare acceso su una macchina e fare il
   login col nome utente del demo [IB3]. Questa sessione vive in un contenitore che si spegne: non può ospitarlo. Serve una macchina
   sempre accesa (la VPS delle crypto, toccando la loro cartella `ops/` d'accordo con la loro sessione, o una macchina a parte).
   Esiste anche un accesso senza Gateway (OAuth 1.0a); se valga per i conti privati è **da verificare** con Interactive Brokers.
   Non serve adesso: il demo si usa solo quando una strategia avrà passato le prove sul passato (`METODO.md`, sezione 7).

Fonti: [IB1] https://ibkrcampus.com/campus/ibkr-api-page/cpapi-v1/ ; [IB2] https://www.interactivebrokers.com/docs/web-api/authentication/paper ;
[IB3] https://www.interactivebrokers.com/docs/web-api/web-api-v-1-0-documentation/authentication (lette tramite i risultati della ricerca, 24 ottobre).

## Cosa è fatto (24 ottobre, sessione nuova con le chiavi)

* **Le chiavi di Alpaca funzionano**: risposta 200 per barre al giorno e al minuto dal 2016, quotazioni, frazionamenti e dividendi,
  calendario della borsa e conto demo. Gli ultimi 15 minuti non si possono chiedere col piano gratuito (403): il programma lo evita.
* **Il programma dei prezzi** (`stock/dati/`): `alpaca.py` scarica, `archivio.py` salva in `~/stock_dati` (o `STOCK_DATI_DIR`) e
  rifiuta una cartella dentro il repository, `controlli.py` controlla, `scarto.py` misura lo scarto, `scarica.py` fa tutto e scrive
  l'esito (solo conteggi e date, mai prezzi). Si lancia con `python -m stock.dati.scarica SPY QQQ ... --scarto --esito <file>`.
* **I controlli**: barre incoerenti o doppie; giorni di borsa senza barra e barre in giorni chiusi (col calendario vero, chiusure
  anticipate comprese); salti di prezzo senza frazionamento; frazionamenti dichiarati e non visti nei prezzi; la rettifica di Alpaca
  confrontata con una calcolata da noi dai frazionamenti e dai dividendi; i dividendi che mancano nella cadenza; per le barre al
  minuto, i minuti mancanti nella seduta e quelli fuori seduta.
* **L'esito sui 12 titoli di prova** (SPY, QQQ e 10 grandi di oggi, 2016-2024; `stock/dati/ESITO_CONTROLLI.md`): 2264 giorni per
  tutti, nessun buco, nessuna barra incoerente, tutti gli 8 frazionamenti visti nei prezzi e rettificati bene. Tre cose trovate:
  1. **Allo SPY mancano 3 dividendi su 36** (18 marzo 2016, 15 giugno 2018, 20 dicembre 2024): i primi due mancano anche nei prezzi
     rettificati di Alpaca. Il comprare e tenere lo SPY, cioè l'asticella, risulterebbe più basso del vero. Va corretto con una
     seconda fonte prima di qualsiasi confronto (`METODO.md`, sezione 3). Il controllo della cadenza trova quello del 2018; quelli in
     testa e in coda al periodo li trova solo il confronto delle due rettifiche (il 2024) o nessuno (il 2016): limite noto.
  2. **NVDA, 25 maggio 2023**: apertura il 26% sopra la chiusura del giorno prima senza frazionamento. Credo sia un evento vero (il
     bilancio del giorno prima), non un errore: lo dico a memoria, **da verificare** su una seconda fonte.
  3. **QQQ ha 5 dividendi nel 2023** (uno in più il 27 dicembre): coerente con la rettifica di Alpaca; il motivo è **da verificare**.
* **Le barre al minuto di SPY e QQQ** (2016-2024; `stock/dati/ESITO_MINUTI.md`): circa 880'000 minuti di seduta ciascuno, più
  800-900'000 fuori seduta (4:00-9:30 e 16:00-20:00). Mancano minuti in un solo giorno per titolo: **SPY il 12 agosto 2019, l'ultima
  mezz'ora intera** (15:29-15:59, 30 minuti), QQQ il 22 febbraio 2016 (10:26-11:17, 50 minuti). L'ultima mezz'ora è proprio quella
  dell'idea I1: quel giorno va tolto dalla prova, non riempito.
* **Lo scarto misurato** (primo giorno di ogni trimestre 2016-2024, tre finestre di 5 minuti al giorno, circa 530 fotografie al
  minuto per titolo): mediana da 0,37 punti base (SPY) a 5,75 (AVGO); un punto base è lo 0,01%. Il costo di un ingresso a mercato è
  circa metà dello scarto. Sono numeri di seduta normale: l'apertura e la chiusura non sono misurate a parte.
* **Il simulatore** (`stock/simulatore/`): la strategia decide alla chiusura di una barra e si esegue nella barra dopo; ordini a
  mercato, limite (solo se il prezzo passa oltre il livello) e stop (al tocco, e un'apertura oltre lo stop si paga tutta); stop
  prima dell'obiettivo se si toccano tutti e due; commissioni con minimo e massimo, metà dello scarto, slittamento, costo del prestito
  per lo scoperto, dividendi e frazionamenti; ogni prova anche con i costi raddoppiati; le finestre che avanzano (12 mesi di scelta, 3
  di prova) che rifiutano il periodo chiuso. Nessuna commissione predefinita: il broker non è scelto.
* **I test**: 41 (al 24 ottobre sera), tutti su casi costruiti a mano (`python -m pytest stock/tests -q`), verdi. Ho controllato che un errore voluto (il
  limite eseguito al semplice tocco) faccia fallire il test giusto.

* **I dividendi dello SPY sistemati** (24 ottobre): confronto con Yahoo su 12 titoli (`stock/dati/ESITO_DIVIDENDI.md`). Yahoo
  conferma 33 dei 33 dividendi dello SPY che ha Alpaca e ha i 3 che mancano, ora aggiunti a mano con la fonte
  (`stock/dati/integrazioni.py`). Yahoo non è perfetto (gli manca un dividendo di QQQ del 2020, due importi di AVGO del 2018 sono
  il doppio del vero): per questo si aggiunge solo ciò che manca ad Alpaca, non si sostituisce una fonte con l'altra.
* **L'universo «di allora»** (`stock/universo/`, esito in `ESITO_UNIVERSO.md`, elenco in `dieci_di_allora.csv`): 104 mesi, da maggio
  2016 (servono 63 giorni di borsa prima, e i dati partono il 4 gennaio 2016) a dicembre 2024; 717 simboli passati per l'indice, 34
  entrati almeno una volta fra i 10. Alpaca ha anche i titoli tolti dal listino e i simboli vecchi (FB fino al giugno 2022, poi META):
  i «titoli sopravvissuti» sono evitati. Ne mancano 5 (CMCSK, HCBK, HSP, SIAL, SNDK), tutti usciti dall'indice entro maggio 2016 e
  troppo piccoli per stare fra i 10.
* **La prova 1** (`stock/prove/P001_ultima_mezzora.md`, regole committate prima; risultati in `P001_risultati.md`): l'ultima mezz'ora
  segue la giornata, SPY e QQQ, 2016-2024. **Bocciata su tutti e due.** Sharpe annuo con i costi −0,60 (SPY) e −0,30 (QQQ), contro 0,87
  del comprare e tenere lo SPY; trimestri in guadagno 28% e 38%.

* **Il simulatore a più titoli** (`stock/simulatore/portafoglio.py`): un solo conto con più azioni, barre al giorno; vendite prima
  degli acquisti, ordini per titoli senza barra non eseguiti e contati, titoli spariti dal listino segnalati; 6 test in più.
* **La prova 2** (`stock/prove/P002_zona_di_rumore.md`, regole committate prima; risultati in `P002_risultati.md`): uscita dalla «zona
  di rumore» dell'apertura. **SPY bocciata** (Sharpe con i costi 0,41, costi doppi sotto zero). **QQQ passa la ricerca**: Sharpe annuo con
  i costi 1,05 contro 0,92 del tenere QQQ e 0,87 del tenere lo SPY; Sharpe corretto 1,00 (soglia 0,95); costi doppi 0,48; 25 trimestri
  su 32 in guadagno; perdita massima −9,6%; opera in circa 6 giorni su 10 (1320 su 2230). **Revisione separata fatta** (`stock/prove/REVISIONE_P002.md`):
  nessun errore bloccante; margini stretti (passa con costi fino a circa 1,2 volte quelli usati); lo scarto vero negli istanti degli ordini
  è uguale a quello usato (0,57 contro 0,56 punti base, `P002_scarto_vero.md`). **Periodo chiuso aperto** (sì del proprietario, 24
  ottobre; `P002_chiuso.md`): **bocciata**. Dal 2 gennaio 2025 al 30 settembre 2026 guadagna il 10,1% con i costi (Sharpe 0,64, 6
  trimestri su 7 in guadagno, costi doppi 0,24), ma tenere QQQ fa Sharpe 1,09 e tenere lo SPY 1,04. Il periodo chiuso del metodo è
  ora consumato: non si può più usare per nessuna prova.

* **Le prove 3-8** (24 ottobre, in autonomia; regole committate prima di ogni calcolo; registro in `stock/REGISTRO.md`): **tutte
  bocciate.**

  | Prova | Idea | Sharpe con i costi | Da battere |
  |---|---|---|---|
  | 3 | Il rimbalzo: i 3 peggiori della settimana fra le 10 di allora | 0,91 | 0,94 (tenere le 10) |
  | 4 | Tenere solo di notte, SPY / QQQ | 0,54 / 0,60 | 0,87 / 0,92 |
  | 5 | Seguire la tendenza a 12 mesi, SPY / QQQ | 0,70 / 0,92 | 0,85 / 0,94 |
  | 6 | Il cambio del mese, SPY / QQQ | 0,57 / 0,54 | 0,91 / 0,96 |
  | 7 | Le 24 ore prima della banca centrale, SPY / QQQ | 0,84 / 0,89 | 0,87 / 0,92 |
  | 8 | I titoli appena tolti dall'S&P 500 | −0,27 | 0,87 |

* **Le prove 9 e 10** (24 ottobre, richieste dal proprietario): **bocciate.** I giorni speciali insieme (cambio del mese + prima della
  banca centrale), giudicati solo sul periodo chiuso, nel 2025-2026 fanno +1,5% (SPY) e +1,2% (QQQ) in 21 mesi, Sharpe 0,15 e 0,12 contro
  1,04-1,09 del tenere (`stock/prove/P009_risultati.md`). La deriva dopo i bilanci sulle 10 di allora: −0,50% a evento rispetto allo SPY,
  Sharpe 0,82 contro 0,94 (`P010_risultati.md`). Le date dei bilanci vengono dalla SEC (`stock/dati/bilanci.py`): si usa solo la data del
  deposito, perché l'ora del modulo può arrivare ore dopo il comunicato.
* **Le prove 11-13 su tutte le azioni dell'S&P 500** (24 ottobre, dopo il sì del proprietario ad allargare): **bocciate.** Il rimbalzo
  della settimana (i 20 peggiori) fa Sharpe 0,51 con i costi e 0,80 anche senza costi, contro 0,91 dello SPY; le 50 meno nervose 0,64 e
  le 50 salite di più in un anno 0,59, contro 0,84 dello SPY e 0,73 dell'indice a pesi uguali. Strumenti nuovi: 18 cambi di simbolo
  trovati in automatico (`stock/universo/cambi_di_nome.csv`), azioni societarie dei 717 titoli. Restano piccoli difetti noti dei dati
  (fusioni con un simbolo nuovo e una storia diversa, per esempio Discovery → Warner Bros. Discovery: il titolo resta valutato all'ultima
  chiusura) che non cambiano gli esiti, bocciati con margini larghi.
* **Le prove 14 e 15** (24 ottobre): la leva prima della banca centrale, giudicata solo sul periodo chiuso, è **bocciata** (nel 2025-2026
  le 14 finestre con la leva hanno perso: +30,1% contro +32,7% del tenere lo SPY). **La prova 15 (più investiti quando il mercato è calmo)
  è la prima che batte il tenere sullo Sharpe** (QQQ 1,08 contro 0,99; SPY 0,95 contro 0,93; perdite massime −23/24% contro circa −33%),
  ma **non passa l'asticella corretta per i tentativi** (0,79 e 0,67 contro 0,95, con 27 prove nel conto): bocciata, come vuole il metodo.
  **Periodo chiuso aperto per decisione del proprietario, dopo la revisione separata (`stock/prove/REVISIONE_P015.md`): bocciata anche
  lì** (`P015_chiuso.md`): nel 2025-2026 SPY Sharpe 0,76 contro 1,04 del tenere, QQQ 1,05 contro 1,09; su QQQ perdita massima più
  piccola (−17% contro −23%) ma guadagno più basso (+32,9% contro +45,9%). Perché (controllato sugli ordini dello SPY): è entrata nel
  calo di febbraio-marzo 2025 con la leva quasi al massimo (1,44 volte il conto il 18 febbraio), ha ridotto solo dopo la caduta (0,30 il
  14 aprile) ed è tornata al 100% solo il 27 maggio, dopo il rimbalzo: il difetto previsto nel sospetto delle regole (i crolli che
  arrivano quando la calma recente spinge a investire di più).
* **Le prove 16-18** (24-25 ottobre): **bocciate.** L'ampiezza del mercato (16) batte di poco il tenere sullo Sharpe ma con 7 uscite in
  8 anni non passa l'asticella. La prima candela dopo l'apertura (17, idea del proprietario, 5 e 15 minuti su SPY e QQQ): Sharpe con i
  costi da −0,48 a 0,38; il caso migliore (QQQ, 5 minuti) fa +106% senza costi e +33% con i costi; l'80% dei giorni esce allo stop. Gli
  acquisti dei dirigenti (18, dati della SEC sbloccati con l'indirizzo del proprietario): nelle aziende dell'S&P 500 il titolo, nel mese
  dopo, **non fa meglio** dello SPY. *Correzione del 25 ottobre:* il «−0,59% a evento, t −3,0» scritto prima era sbagliato (prezzi
  senza dividendi e con i costi); corretto è −0,24% (t −1,2). Il mercato reagisce già nella notte dopo il deposito (+0,42%, t 15,7); da
  lì in poi non resta niente (−0,04%). La prova 19 (vendere allo scoperto quei titoli, idea nata dal numero sbagliato) è bocciata nel
  periodo chiuso (+19,0% contro +32,7% del tenere lo SPY).
* **La prova 20, le azioni con una notizia** (25 ottobre, idea del proprietario: la prima candela da 5 minuti nel giorno del bilancio,
  quando all'apertura il titolo salta di almeno il 2%): **bocciata**, ma con la lezione più chiara di tutte. Il vantaggio prima dei costi
  c'è ed è il più forte trovato finora (Sharpe 1,29, +0,128% a operazione su 6562), ma in quei momenti lo scarto vero è di 23 punti base
  (mediana, misurata alle 9:35 su 379 casi): ogni operazione costa più di quanto rende. Chi descrive queste regole come profittevoli
  probabilmente non conta lo scarto dell'apertura.
* **La prova 21** (le stesse azioni con notizie, entrando con un ordine limite): **bocciata.** L'ordine limite risparmia lo scarto
  all'ingresso, ma l'uscita (allo stop o alla chiusura) lo paga comunque, e i pochi casi in cui il limite non si esegue sono i migliori
  (+1,71% a operazione contro +0,10%). Con i costi veri: −0,088% a operazione, Sharpe −0,89.
* **La prova 22** (l'inversione dopo l'apertura a 5 passi di Riley Coleman, scritta a regole fisse su SPY e QQQ): **bocciata.**
  Perde **anche senza costi** (−4,6% e −2,6% in nove anni); solo il 31-34% delle operazioni guadagna e l'obiettivo più largo dello stop
  non basta a compensare. Togliere il livello o allargare l'orario non cambia niente: la testa e spalle dopo l'apertura, così scritta,
  non porta informazione. Che dopo l'apertura il prezzo cambi spesso direzione (prova 17) non vuol dire che il punto del cambio si veda
  in tempo.
* **La prova 23** (le regole in giornata rifatte sulle 10 azioni di allora, richiesta del proprietario): **bocciate tutte e cinque.**
  Le regole che seguono il movimento hanno un vantaggio **prima dei costi** anche sulle azioni (zona di rumore Sharpe 1,31, prima candela
  0,95-0,96, più del tenere le 10 a 0,94), soprattutto sui titoli più nervosi (AMD, TSLA, NVDA); ma operano ogni giorno su 10 titoli
  (circa 40'000 ordini in 9 anni) e i costi, anche con lo scarto di metà giornata che è più stretto di quello vero dell'apertura, le
  portano sotto zero. Stima (non calcolata): anche dimezzando i costi lo Sharpe resterebbe sotto quello del tenere. L'inversione perde
  anche senza costi, come sugli indici. Da qui: il vantaggio in giornata esiste ma è più piccolo di quanto costa prenderlo.
* **La prova 24** (le azioni più vendute allo scoperto, idea delle crypto): **bocciata.** Nell'S&P 500 2018-2024 le azioni con più
  giorni per ricomprarle sono salite **più** dell'indice: vendute allo scoperto hanno perso il 3,35% l'anno. L'effetto degli studi vive
  nelle aziende piccole e care da prendere a prestito, non nelle 500 grandi.
* **La prova 25** (la miscela delle prove 7, 15 e 16): Sharpe 1,08 contro 0,89 dello SPY, perdita massima −14,6% contro −33,8%, ma lo
  Sharpe corretto per le prove è 0,05: non si distingue dal caso. Proposta al proprietario per il demo come misura in avanti.
* **La prova 26** (la tendenza su obbligazioni, oro, materie prime e azioni estere come parte nuova della miscela): **bocciata**, non
  entra. Da sola fa Sharpe 0,34; è legata alla miscela più del previsto (correlazione 0,41) e la miscela con lei fa 1,05 contro 1,08.
* **La prova 27** (gli acquisti dei dirigenti nelle aziende fuori dall'S&P 500, 1'795 operazioni in 9 anni): **bocciata**. Per evento
  fa −0,16% rispetto al fondo delle aziende piccole (t −0,58): il vantaggio degli studi non c'è più neanche qui. Da sola Sharpe 0,42
  contro 0,56 del fondo; nella miscela peggiora (0,84 contro 1,08). Capito: Alpaca ha i prezzi del 92% delle aziende piccole, anche
  di quelle sparite, quindi le prossime prove sulle piccole si possono fare (lavoro `azioni-ricerca` su GitHub). Nel conto: 69.
* **Difetto dei prezzi trovato il 12 novembre 2026 (aperto).** Alpaca, senza l'opzione `asof`, dà a ogni simbolo la storia
  dell'azienda che lo porta oggi: nell'archivio locale il simbolo PARA del 2022-2024 non è Paramount, e 16 membri dell'S&P 500 di
  allora mancano in tutto o in parte (SunTrust, Twitter, Citrix, Andeavor...). Tocca le prove sull'intero S&P 500 (11, 12, 13, 16,
  18, 24: tutte bocciate, e 17 simboli su 708 non bastano a cambiarne l'esito, ma non è stato ricalcolato) e la prova 27 (lì ogni
  acquisto è controllato contro la chiusura del giorno, entro il 50%: i prezzi di un'altra azienda quasi sempre si scartano; non
  ricalcolata). Dalla prova 28 i prezzi si scaricano con il simbolo di allora (`asof` «-») e i titoli spariti dal listino si chiudono
  all'ultimo prezzo (`simula_conto`, `liquida_dopo`). **Prova 27 rifatta il 12 novembre con i prezzi giusti**
  (`prove/P027b_risultati.md`): l'esito non cambia. Con i prezzi giusti entrano 2'089 operazioni invece di 1'795; per evento +0,00%
  rispetto al fondo delle piccole (prima −0,16%), Sharpe 0,45 (prima 0,42) contro 0,56 del fondo; nella miscela 0,82 contro 1,08.
  **Restano da ricalcolare** le prove sull'intero S&P 500 (11, 12, 13, 16, 18, 24), tutte bocciate: non urgente.
* **La prova 28** (il tono delle notizie, idea del proprietario del 30 ottobre): **bocciate tutte e due le varianti**. Nelle 500
  grandi il tono non dice niente (quinto alto meno basso −0,16% al mese, t −0,67). Nelle aziende piccole **sì**: +0,94% al mese fra il
  quinto con le notizie migliori e quello con le peggiori (t 3,04), ma tutto dal lato delle notizie cattive: comprare le buone e vendere
  l'IWM fa Sharpe 0,00 prima dei costi, −0,97 dopo. Capito: le notizie cattive delle aziende piccole entrano nel prezzo lentamente, le
  buone no. Da qui l'idea I31 (vendere allo scoperto le piccole con le notizie peggiori), vista dopo il calcolo: si giudica solo sul
  periodo chiuso, con il costo del prestito. Nel conto: 73.
* **La prova 29** (vendere allo scoperto le piccole con le notizie peggiori, coperte comprando l'IWM; idea I31): **bocciata nel
  periodo chiuso** (2025-01 → 2026-09), aperto una volta sola: −20,1% con i costi contro +32,7% dello SPY, Sharpe −0,13 (senza costi
  −0,00) contro 1,04, perdita massima −37,2% (`prove/P029_risultati.md`). Capito: il vantaggio visto nel 2016-2024 (Sharpe 0,84 senza
  costi) già lì spariva con scarto e prestito (0,01), e nel 2025-2026 non c'è nemmeno prima dei costi (probabile, non
  misurato: i salti al rialzo dei titoli venduti allo scoperto, perdita massima −37%). Il periodo chiuso della famiglia «notizie» ora è usato:
  un'altra prova sulle notizie si potrà giudicare solo in avanti. Nel conto: 75.
* **La prova 30** (il premio del comunicato: le azioni dell'S&P 500 nella settimana in cui pubblicano i risultati, coperte con lo
  SPY; idea I32): **bocciata.** Nelle 500 grandi, dal 2017 al 2024, il premio degli studi non c'è: tutti i titoli con la data
  prevista meno lo SPY −0,13% a settimana (t −1,19). Senza costi +7,0% in 8 anni, con i costi −26,2%: cambiare quasi tutto ogni
  settimana con 100'000 dollari costa circa 3'600 dollari l'anno fra commissioni e scarto (`prove/P030_risultati.md`). Capito: un
  effetto di calendario sulle singole azioni con un ricambio settimanale deve valere più di circa lo 0,24% a settimana sulla parte
  investita solo per pagare i costi (28'541 dollari in 242 settimane dentro, su 50'000 investiti); la data prevista dall'anno prima è
  giusta nel 68% dei casi. Nel conto: 77.
* **La prova 31** (la redditività lorda, dai conti della SEC: comprate le aziende dell'S&P 500 più redditizie sui beni, vendute le
  meno, una volta l'anno; idea I33): **bocciata.** Da sola +3,0% con i costi in 8 anni e mezzo (Sharpe 0,09 contro 0,87 dello SPY);
  il passaggio al pelo per la miscela (1,09 contro 1,08) **non ha retto al revisore separato** (`prove/REVISIONE_P031.md`, FAIL).
  Capito, sui dati: (1) le «cornici» della SEC danno i bilanci **rifatti dopo**, non quelli di allora: per i conti serve la versione
  depositata prima della decisione (i `companyfacts` con la data di deposito); (2) `stock/universo/codici_sec.csv` dà un solo codice
  per simbolo su tutti gli anni: un simbolo passato a un'altra azienda prende i conti sbagliati; (3) le voci di ripiego accoppiate
  alla lettera danno valori assurdi (C.H. Robinson 3,2-4,0); (4) il programma prendeva l'ultimo esercizio con un valore anche se
  vecchio di anni (AT&T con il 2014 fino al 2024). Capito, sul metodo: il criterio per entrare nella miscela lasciava passare il caso;
  dalla prova 32 chiede anche il t della parte da 1,3 e la miscela nuova più alta nell'80% dei campionamenti (idea I30). Periodo
  chiuso della famiglia «conti delle aziende» non aperto. Nel conto: 79.
* **La prova 32** (comprare le aziende piccole meno vendute allo scoperto, coperte con l'IWM; idea I34): **bocciata, e male**:
  −66,7% con i costi dal 2018 al 2024 (senza costi −58,5%), in perdita ogni anno, correlazione con lo SPY −0,49
  (`prove/P032_risultati.md`). Il quinto con meno vendite allo scoperto fa peggio dell'IWM (−0,42% al mese, t −1,71): il contrario
  di Boehmer, Huszar e Jordan. Spiegazione probabile, non verificata: fra le piccole i titoli che nessuno vende allo scoperto sono
  soprattutto società vuote in attesa di una fusione (SPAC), ferme intorno ai 10 dollari. Capito: il lato comprato delle piccole,
  coperto con l'IWM, ha perso in tutte e tre le prove (27, 28, 32); prima di un'altra prova sulle piccole serve un filtro scritto
  prima che tolga le società vuote. Nel conto: 81.
* **La prova 33** (il momento dei settori: comprati i 3 fondi di settore saliti di più in un anno, venduti i 3 saliti di meno; idea
  I35): **bocciata.** Dal 2016 al 2024 i comprati fanno meglio dei venduti di +0,03% al mese (t 0,07): l'effetto degli studi sui
  settori qui non c'è; con i costi −7,2% in 9 anni (`prove/P033_risultati.md`). Capito: in tre giorni (12-14 novembre) sono cadute sei idee pubblicate
  (prove 28-33) su notizie, comunicati, conti, vendite allo scoperto e settori; nelle azioni americane dal 2016 gli effetti noti, dopo
  i costi, non ci sono più o sono troppo piccoli per vedersi. Nel conto: 83.
* **La prova 34** (la deriva dopo i risultati nelle aziende piccole, comprate dopo la reazione più alta e coperte con l'IWM; idea
  I36, l'ultima parte della I29): **bocciata.** Il quinto con la reazione più alta fa peggio dell'IWM nel mese dopo (−0,27% al mese,
  t −1,20); con i costi −39,3% dal 2016 al 2024 (`prove/P034_risultati.md`). L'idea I29 (le aziende piccole) è provata in tutte e tre
  le parti. Capito: il lato comprato delle piccole coperto con l'IWM ha perso in **quattro prove su quattro** (27, 28, 32, 34), con
  regole diverse; sospetto (da misurare, non misurato): un paniere a pesi uguali di piccole scambiate fa peggio dell'IWM di per sé
  negli anni 2016-2024, e la copertura non è neutra. Prima di un'altra prova sulle piccole: misurare quel paniere di base contro
  l'IWM. Nel conto: 85.
* **Il controllo del 15 novembre** (`prove/P034b_risultati.md`, non è una prova): il paniere di **tutte** le piccole ammesse, a pesi
  uguali, fa quasi come l'IWM (−0,13% al mese, t −1,24, dal 2018; −0,02% dal 2016 per chi ha un comunicato): **la copertura è quasi
  neutra**, il sospetto non regge. Ma il titolo **mediano** fa −0,44/−0,53% al mese peggio dell'IWM (t −3,1/−3,9): il paniere medio
  tiene grazie a pochi titoli che salgono moltissimo; un gruppo di 50 ne prende pochi, e il suo risultato tipico scivola verso la
  mediana. Le società vuote nella prova 32 non si vedono (0-2% dei nomi, un minimo): la spiegazione di allora non è confermata.
* **La prova 35** (le azioni «in gioco»: ogni mattina, fra tutte le azioni liquide, le 20 con il volume dei primi 5 minuti più alto
  del solito, la rottura della prima candela da 5 minuti; idea I37, nata dalla domanda del proprietario «perché solo le 10 più
  scambiate»): **bocciata.** Il vantaggio dello studio c'è: 36'520 operazioni dal 2016 al 2024, +0,140% a operazione prima dei costi
  (t 11,0); con le sole commissioni Sharpe 2,55, vicino al 2,81 dichiarato. Ma lo scarto su quei titoli in quei minuti è di 16,2
  punti base all'ingresso e 13,0 all'uscita (mediane, 500 operazioni a caso) contro uno stop a 34,5: ogni operazione costa 0,242%,
  e con la leva il conto va a zero (`prove/P035_risultati.md`). Capito: (1) la risposta alla domanda del proprietario, con un numero:
  le 10 più scambiate si usano perché il loro scarto è di 0,8-5,8 punti base (mediane, `dati/ESITO_CONTROLLI.md`), le azioni «in gioco» lo hanno da 3 a 20 volte
  più largo; (2) è la quinta volta che la rottura della prima candela muore sui costi (prove 17, 20, 21, 23, 35); (3) regola per le
  idee in giornata su titoli singoli: prima dei costi servono più di circa 0,25% a operazione, oppure titoli con lo scarto di pochi
  punti base. Nel conto: 87.
* **La prova 36** (gli acquisti dei dirigenti nell'S&P 500 comprati due minuti dopo la pubblicazione alla SEC, anche negli orari
  estesi, venduti all'apertura dopo; idea I22): **bocciata.** Il vantaggio c'è anche arrivando dopo: 2'615 operazioni dal 2016 al 2024,
  +0,223% a operazione prima dei costi (t 5,4), +0,18% anche con un'ora di ritardo. Ma due depositi su tre arrivano dopo la chiusura, e
  lì lo scarto misurato ha mediana 103,6 punti base contro 7,6 in seduta: con i costi −44,3% in 9 anni (`prove/P036_risultati.md`). In
  seduta (802 operazioni) resta +0,05% a operazione prima delle commissioni: troppo poco. Capito: (1) il modulo 4 è l'annuncio stesso,
  e l'ora d'accettazione della SEC è utilizzabile (copertura 99,5%: `dati/depositi_dirigenti.py`); (2) il vantaggio vive proprio
  dove comprare costa di più, fra la pubblicazione e l'apertura dopo (dall'apertura in poi non resta niente: prova 18); (3) dubbio
  aperto sul costo fuori seduta (forse contato due volte, idea I38): si può solo misurare, non usare per promuovere. Nel conto: 89.
* **Il controllo del 16 novembre sul costo fuori seduta** (`prove/P036b_risultati.md`, non è una prova; chiesto dal proprietario):
  600 ingressi della prova 36 con le quotazioni e le operazioni di mercato del minuto. (1) **Nessun doppio conteggio**: fuori seduta la
  barra apre in mediana al prezzo di mezzo (−0,03), solo il 30% al prezzo di chi vende. (2) **Le quotazioni esagerano**: fuori seduta
  metà dello scarto quotato vale 41,6 punti base, ma chi ha scambiato ha pagato 21,4 (dopo la chiusura 19,1); la prova 36 ne contava
  51,8. (3) Con il costo effettivo, dopo la chiusura resta circa +0,07% a operazione (stima: +0,317% prima dei costi della prova 36,
  meno 19 + 4 punti base e le commissioni), non distinguibile da zero; prima dell'apertura si perde comunque (−0,45%, t −5,3). (4) Un
  ingresso fuori seduta su tre non ha nemmeno una quotazione valida nei 5 minuti prima. Capito: la porta degli acquisti dei dirigenti
  fuori seduta è chiusa; per le idee future su eventi fuori seduta il costo da usare è lo scarto effettivo (circa 20 punti base per
  lato dopo la chiusura, sull'S&P 500), non quello quotato.
* **La prova 37** (anticipare il ribilanciamento dei fondi 60/40: SPY contro IEF, regole dell'articolo NBER w33554, idea I39 dalla
  ricerca su GitHub): **bocciata da sola** (Sharpe con i costi 0,56 contro 0,87 dello SPY), **passa il criterio per la miscela**
  (correlazione −0,00, miscela 1,18 contro 1,08, t 1,67, 85% dei campionamenti; `prove/P037_risultati.md`). Due allarmi scritti nel
  risultato: senza marzo 2020 lo Sharpe è 0,02 (il 2020 fa +32,3%, gli altri anni fra −4% e +5%), e con un giorno di ritardo è
  −0,54. **FAIL del revisore separato** (`prove/REVISIONE_P037.md`): il calcolo è giusto e fedele all'articolo, ma il passaggio
  dipende da un solo mese (marzo 2020 fa il 101% del guadagno in logaritmi, controllato dalla sessione); senza, t della parte 0,07 e
  42% dei campionamenti; dopo la fine del campione dell'articolo t 0,70; il margine sui costi è sottile (cade con costi più alti del
  30%). Periodo chiuso **non aperto**. Capito: il criterio per la miscela con t 1,3 si supera per caso circa una volta su dieci senza
  vantaggio vero (prove 31 e 37, tutte e due cadute alla revisione): il revisore separato è indispensabile. Nel conto: 91.
* **La prova 38** (la stagionalità dello stesso mese nell'S&P 500, comprate le 50 salite di più nello stesso mese dell'anno prima e
  vendute le 50 scese di più; idea I45): **bocciata.** Già prima dei costi comprati meno venduti fanno −0,11% al mese (t −0,28) dal
  2017 al 2024: l'effetto di Heston e Sadka (t 7,6 nello studio) nelle grandi americane dopo la pubblicazione non c'è; con i costi
  −33,9% (`prove/P038_risultati.md`). Capito: con un conto da 100'000 dollari diviso in 100 posizioni che cambiano quasi tutte ogni
  mese, le sole commissioni minime pesano circa il 2% l'anno: una strategia mensile a molti titoli deve rendere più di questo prima di
  tutto il resto. Nel conto: 93.
* **La prova 39** (l'emissione netta di azioni nell'S&P 500: comprate le 50 aziende che hanno ridotto di più le azioni in un anno,
  vendute le 50 che le hanno aumentate; idea I42): **bocciata.** Fatta con i dati della SEC giusti questa volta (la data di deposito
  di ogni numero e il codice SEC del simbolo di allora: i due difetti della prova 31; `dati/P039_*.csv.gz`, 95% dei membri coperti).
  Prima dei costi comprati meno venduti +0,14% al mese (t 0,53): la direzione dello studio, ma non distinguibile dal caso; con i costi
  −4,9% in 8 anni (`prove/P039_risultati.md`). Capito: anche l'effetto che Fama e French trovavano fra le grandi, dopo il 2017 nell'S&P
  500 è al massimo di 1-2% l'anno prima dei costi. Strumento nuovo: le azioni in circolazione con la data di deposito servono anche
  per la misura vera dei giorni dei dividendi (idea I46). Nel conto: 95.
* **La prova 40** (i giorni con molti dividendi pagati: lo SPY solo quando i dollari pagati dall'S&P 500 sono sopra la mediana
  dell'anno prima, regola dello studio di Hartzmark e Solomon; idea I46): **bocciata** (Sharpe 0,58 contro 0,85;
  `prove/P040_risultati.md`). Un difetto dei dati visto nel risultato (2017-2019 a zero) e controllato con un metodo scritto prima di
  guardare (`prove/P040b_risultati.md`): **Alpaca non ha le date di pagamento dei dividendi prima del 2020**. Sugli anni completi
  (2021-2024) l'effetto non c'è: +5,7 contro +5,6 punti base al giorno (t 0,01). Capito: (1) la pressione dei dividendi reinvestiti,
  forte nello studio fino al 2018, sull'S&P 500 del 2021-2024 non si vede; (2) **le date di pagamento di Alpaca partono dal 2020**:
  ogni idea che le usa ha solo 4-5 anni. Nel conto: 97.
* **La prova 41** («lazy prices»: comprate le aziende dell'S&P 500 che non cambiano il testo dei bilanci, vendute quelle che lo
  cambiano di più; idea I40, studio di Cohen, Malloy e Nguyen): **bocciata** (Sharpe con i costi −0,19 contro 0,84 dello SPY; nella
  miscela 17% dei campionamenti; `prove/P041_risultati.md`). Comprati meno venduti +0,17% al mese (t 0,79); prima del 2020 +0,44%
  (t 1,24), dal 2020 +0,02% (t 0,06). Capito: (1) **sull'S&P 500 dopo la pubblicazione dello studio l'effetto non si vede**; (2) i
  bilanci annuali somigliano all'anno prima più dei trimestrali (0,997 contro 0,991): una classifica unica avrebbe comprato chi ha
  appena depositato il bilancio annuale, non chi non cambia il testo. Trovato nel controllo dei dati e corretto nelle regole prima del
  calcolo (classifica dentro il tipo). Strumento nuovo: `dati/testi_bilanci.py` (le somiglianze di 22'490 bilanci 2015-2024 di
  733 aziende, `prove/dati/P041_somiglianze.csv.gz`; i testi non si salvano). Nel conto: 99.
* **La prova 42, in corso dal 19 novembre** (gli attivisti: comprare in seduta, o all'asta d'apertura, dopo la pubblicazione di un
  modulo 13D alla SEC, coperti con l'IWM, per 20 sedute; idea I43): regole committate prima di scaricare i depositi
  (`prove/P042_attivisti.md`), caricatore `dati/attivisti.py`, primo passo `prove/p042a.py` (l'elenco dei 13D con l'ora, su GitHub);
  dal 20 novembre pronto anche il calcolo sui prezzi (`prove/p042.py`, con i test), che parte solo dopo il controllo dell'ora. **Ferma
  in attesa del proprietario**: il blocco della privacy non lascia più mettere l'indirizzo di contatto nei comandi della sessione, e la
  SEC lo chiede in ogni richiesta; serve il segreto `SEC_CONTATTO` nel repository (il lavoro di GitHub lo legge già). Chiuse senza prova
  le idee I13 (la deriva dopo i risultati nell'S&P 500: mancata sulle 10 grandi e sulle piccole), I29 (completata), I41 (= prova 40).
* **La prova 43** (il carry delle valute: comprate le 2 valute con il tasso più alto fra sei fondi delle valute, vendute le 2 con
  il più basso; idea I47): **bocciata** (Sharpe con i costi −0,07; `prove/P043_risultati.md`). Comprati meno venduti +0,02% al mese
  (t 0,13). Capito: (1) nel 2016-2024 il carry fra le valute dei paesi ricchi è stato **comprare le valute del rischio (dollaro
  canadese, australiano, sterlina) e vendere i rifugi (franco, euro)**: si muove con le azioni (correlazione 0,42 con lo SPY) e non
  rende; (2) il grande guadagno sullo yen del 2021-2024 qui non c'è, perché il franco e l'euro avevano tassi più bassi dello yen fino
  al 2022. Chiusa senza prova l'idea delle aste del Tesoro (I48): lo studio della Fed di New York del 2026 dice che dopo il 2014
  l'effetto si è indebolito molto. Nel conto: 101.
* **La prova 44** (la volatilità rovesciata: VIXY tenuto solo quando il VIX chiude sopra il VIX a tre mesi; idea I50): **bocciata**
  (Sharpe con i costi 0,14, perdita massima −66,8%; `prove/P044_risultati.md`). Capito: (1) la parte si muove davvero al contrario
  della miscela (correlazione −0,37), ma **guadagna solo nelle crisi lunghe**: marzo 2020 +129,5%, senza il 2020 −51,7%; nei crolli
  di un giorno (agosto 2024, febbraio 2018) si compra in cima; (2) con un solo episodio buono in 9 anni non si può dire che ci sia un
  vantaggio. Chiusa senza prova l'idea della fine del divieto di vendita dopo le quotazioni (I49): su Alpaca non si potrebbero vendere
  allo scoperto quei titoli, e il prestito costa più del guadagno. Nel conto: 103.
* **La prova 45** (l'ultima mezz'ora segue la giornata solo nei giorni con la copertura delle opzioni sotto zero, uscita all'asta;
  idea I52): passava l'esame per entrare nella miscela (1,12 contro 1,08, t 1,53, 94% dei campionamenti), ma **FAIL del revisore**
  (`prove/REVISIONE_P045.md`): i numeri si rifanno uguali con codice e calendario indipendenti, ma metà del guadagno lordo viene dalle
  18 operazioni di marzo 2020; senza quel mese il t della parte è 0,86. Il periodo chiuso non si apre. Capito: (1) **il dato della
  copertura separa davvero i giorni** (+7,58 punti base a operazione sotto zero, +0,05 negli altri 2'004; la direzione giusta nel 57%
  anche senza marzo 2020), e non è solo «giornata agitata» (i giorni agitati con la copertura positiva non rendono); (2) ma il guadagno
  sta nelle crisi, come nelle prove 37 e 44: idea nuova I53, un esame scritto prima per le parti «da crisi»; (3) il dato di
  SqueezeMetrics si può controllare solo dal novembre 2021 (11 copie pubbliche identiche), prima può essere stato rifatto; (4) le
  chiusure giornaliere di Alpaca non sono quelle ufficiali in 13 giorni (10 in marzo 2020), errore ancora nella miscela della prova 25.
  Chiuse senza prova le idee dei fondi a leva su una sola azione (I51) e dell'uscita all'asta (I8, con il numero della 45). Nel conto: 105.
* **Sul demo dal 12 novembre 2026:** la **miscela** nello stesso conto della prima candela (capitale virtuale di 100'000 dollari
  ciascuna, titoli separati: `stock/avanti/conto.py`, `MISCELA.md`), accesa da `stock/avanti/miscela_accesa`. Ogni avvio lancia il
  comando `auto`, che decide dall'orologio (chi avvia non deve essere puntuale). Pronta l'installazione sulla VPS
  (`stock/avanti/vps/installa.sh`, da lanciare una volta dal proprietario). Routine della sessione: quattro avvii al giorno, la sera
  della miscela, e la ricerca continua due volte al giorno.
* **La misura in avanti sul conto demo di Alpaca** (richiesta del proprietario del 7 nov 2026: «non in back testing [...] real time,
  forward testing»): la prima candela da 15 minuti sulle 10 azioni più scambiate del mese, regole in `stock/avanti/REGOLE.md`, due
  routine nei giorni di borsa (9:46 e 15:55 di New York) dentro la sessione «trading stock», diario in `stock/avanti/diario.csv`,
  riepilogo ogni lunedì. Dall'11 novembre 2026 gira su **GitHub** con le chiavi nei segreti del repository (`.github/workflows/azioni_avanti.yml`, acceso da `stock/avanti/acceso_su_github`); le routine della sessione sono spente; pubblica sulla Plancia sotto `/azioni`.
* **Strumenti nuovi della giornata:** le scissioni (GE, DHR, PFE: valutate come incasso al prezzo d'apertura del titolo nuovo; per PFE
  è Alpaca a non contare quella di Viatris), la frazione di azione pagata in contanti nei raggruppamenti, i cambi di nome (FB → META),
  le date dei comunicati della banca centrale con la fonte (`stock/dati/fomc.py`), le misure dello scarto e i controlli dei 34 titoli
  dell'universo (`stock/dati/ESITO_CONTROLLI_UNIVERSO.md`).

## Cosa abbiamo capito il 24 ottobre

* **La regola dei costi:** nei momenti in cui c'è movimento (l'apertura, le notizie) lo scarto è largo; il vantaggio di quei momenti
  si paga tutto in scarto (prova 20: 23 punti base alle 9:35 nei giorni con notizie).
* **Sul 2016-2024 solo un'idea su 15 batte il comprare e tenere sullo Sharpe** (la prova 15, più investiti quando il mercato è calmo), e non abbastanza per l'asticella (27 nel conto, comprese 3 aperture del periodo chiuso). La direzione del mercato non si indovina; la sua agitazione sì. Gli effetti
  studiati spesso ci sono ancora (prima della banca centrale +0,23% a evento, t 2,9; il cambio del mese; la notte) ma sono troppo
  rari o troppo costosi per battere un mercato salito molto. Le grandi aziende americane del 2016-2024 sono state un avversario
  durissimo: tenere le 10 più scambiate a pesi uguali ha fatto Sharpe 0,94, più dello SPY (0,87).
* **I titoli tolti dall'indice non recuperano più**: in media −1,56% nel mese dopo (il lavoro del 2004 diceva il contrario).

* **Nel periodo chiuso la zona di rumore su QQQ guadagna ma non batte il tenere QQQ** (Sharpe 0,64 contro 1,09): sul 2016-2024, che gli
  autori della regola conoscevano, lo batteva (1,05 contro 0,92). È la stessa lezione delle crypto: un risultato pubblicato sul periodo
  che lo ha prodotto vale meno di quanto sembra. La strategia è bocciata come l'ha voluta il metodo, senza ritocchi.
* **Su QQQ la regola della zona di rumore regge dopo i costi, sullo SPY no** (sul 2016-2024). Prima dei costi lo Sharpe è 1,62 su QQQ e 1,01 sullo SPY:
  il movimento di QQQ in giornata è più ampio, mentre il costo di un'operazione è quasi lo stesso. Sospetto da tenere: QQQ, nel
  2016-2024, è stato un periodo eccezionale per i titoli tecnologici (anche se la regola compra e vende allo scoperto in giornata).

* **L'effetto dell'ultima mezz'ora c'è, ma è più piccolo dei costi.** Senza costi la prova guadagna (Sharpe annuo 0,31 sullo SPY, 0,67
  su QQQ): circa 0,5 punti base al giorno sullo SPY (12,4% in 2259 giorni). Ogni giornata costa circa 1,7 punti base fra commissioni
  (0,3), scarto (0,37) e lo slittamento messo per prudenza (1,0). Anche senza lo slittamento i costi (circa 0,7) superano il guadagno.
  Lezione per tutte le idee in giornata: un'operazione al giorno deve rendere **più di circa 0,7 punti base** solo per pareggiare sullo
  SPY, e di più sulle azioni singole (scarto da 0,8 a 5,8 punti base).
* **I dati di Alpaca vanno sempre confrontati con una seconda fonte**: senza, l'asticella sarebbe stata più bassa del vero.

## Cosa non è fatto, e perché

* **I prezzi del periodo chiuso** (dal 2025) non sono stati scaricati: nessuno li ha visti.
* Il simulatore gira su un titolo alla volta: la prova 1 (2 titoli × 3 varianti di costo, 880'000 minuti ciascuno) ha impiegato 4
  minuti. Il simulatore a più titoli adesso c'è.
* Le commissioni di Interactive Brokers (0,005 dollari per azione, minimo 1) sono **da verificare** sul listino ufficiale.
* **Le chiusure giornaliere di SPY di Alpaca** (trovato dal revisore della prova 37, controllato dalla sessione il 16 nov 2026):
  contro Yahoo, in marzo 2020 14 giorni su 22 differiscono di più di 5 punti base (fino a 287), nel 2019 15 su 252. Le usano lo SPY di
  riferimento di tutte le prove e le parti delle prove 15 e 16, quindi la miscela della prova 25 sul demo. Da rifare: le prove 15, 16 e
  25 con le chiusure ufficiali (Yahoo) e vedere se cambia qualcosa; non urgente per gli esiti già bocciati, importante per la miscela.
  **Fatto il 17 nov 2026** (`prove/P025c_risultati.md`, controllo, non è una prova): SPY differisce oltre 5 punti base in 81 chiusure
  su 2'264 (fino a 287) e 26 aperture, QQQ in 1 chiusura; con le chiusure ufficiali le parti delle prove 15 e 16 cambiano di 0-0,02
  di Sharpe e **la miscela resta 1,08** (correlazione 0,9996 con la serie di prima) contro 0,87 del tenere lo SPY (0,89 con Alpaca):
  resta sul demo come è. Lo SPY di riferimento delle prove passate era un poco più alto del vero (0,89 contro 0,87): le bocciature
  contro lo SPY restano tali.
* **Il conto dello Sharpe corretto** (`carica_serie`) comprende anche le 9 serie `*_chiuso` (trovato dal revisore della prova 37):
  conta di più le prove (più prudente), ma usa serie con date del periodo chiuso; da decidere se escluderle.

## Il prossimo passo

* Il periodo chiuso si riusa per famiglie diverse (deciso il 24 ottobre, sopra).
* La coda delle idee (`REGISTRO.md`, sezione 2): restano le varianti a costi più bassi (I8, I9) e la leva nei giorni speciali (I11,
  da proporre al proprietario). Le idee della bozza del metodo sono finite: per andare avanti servono idee nuove (vedi il messaggio al
  proprietario del 24 ottobre).
* Verificare il salto di NVDA del 25 maggio 2023 e il dividendo in più di QQQ del 27 dicembre 2023.
* Misurare lo scarto nei primi e negli ultimi minuti della seduta (le idee in giornata entrano ed escono proprio lì).
