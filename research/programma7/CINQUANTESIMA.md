# Programma 7 — cinquantesima prova: comprare dopo le cascate di vendite forzate, in giornata (LQ)

Scritto il 27 ottobre 2026, alle 08:35 UTC (commit `c291fc1e` delle 08:36; la prima versione diceva per errore 08:55). Le regole sono fissate **prima di scaricare i dati sulle posizioni a 5 minuti dei giorni
candidati e prima di qualunque calcolo di rendimento**. Fino a qui si è guardata solo la copertura delle candele orarie: il 5,2% delle
ore mancava, su 142 monete, e i mesi mancanti si stanno scaricando. È l'idea 78 della coda di `research/REGISTRO.md`, scritta il 27
ottobre perché la coda era vuota con i dati gratuiti. Fa parte del trading di ogni giorno: si entra e si esce nella stessa giornata,
in 4 ore.

## 1. Perché

* **Chi è costretto a vendere paga.** Quando i long a leva vengono liquidati, o toccano lo stop, vendono a qualunque prezzo.
  Quelle vendite spingono il prezzo sotto il giusto, e chi compra da loro guadagna quando il prezzo risale. È il premio di chi fornisce
  liquidità a chi deve uscire (Nagel 2012) e la spirale delle vendite forzate (Brunnermeier e Pedersen 2009). È la stessa famiglia che
  per noi regge, «chi paga la leva perde», vista come evento dentro la giornata.
* **Cosa c'è di nuovo rispetto alla prova 78.** La prova 78 (G19) comprava le monete piccole crollate e faceva −0,25% a operazione.
  Un crollo da solo mescola due cose diverse:
  * le **vendite forzate**: le posizioni si chiudono, quindi l'interesse aperto scende;
  * le **vendite informate**: si aprono short nuovi, quindi l'interesse aperto resta uguale o sale (notizie, furti, sblocchi).

  I dati sulle posizioni a 5 minuti dell'archivio di Binance separano i due casi, e non li abbiamo mai usati dentro la giornata.
  **La previsione scritta prima**: dopo un crollo con l'interesse aperto in calo il prezzo rimbalza di più che dopo un crollo con
  l'interesse aperto in salita.
* **I dubbi scritti prima.**
  * Nella prova 78 i crolli spesso continuavano.
  * La prova 4 (il rimbalzo dopo i crolli) andava bene solo quando crollava tutto il mercato.
  * Le cascate di tutto il mercato sono pochi giorni indipendenti: in un giorno come il 10 ottobre 2025 scattano decine di monete
    insieme. Per questo l'esame tiene insieme gli eventi della stessa settimana.

## 2. Dati e periodo (fissati qui)

* **Periodo**: dal 1° dicembre 2021 al 24 ottobre 2026. Il 1° dicembre 2021 è l'inizio dei dati a 5 minuti sulle posizioni per la
  maggior parte delle monete; il 24 ottobre 2026 è l'ultimo giorno dei dati.
* **Universo**: ogni settimana le 100 monete più scambiate del programma 6 (l'universo U di `terza.pannello_settimane`, deciso con i
  dati delle settimane prima). Comprende anche le monete tolte dopo dal listino, quindi non si guarda solo chi è sopravvissuto: 450
  monete in 255 settimane.
* **Dati**:
  * le candele da 1 ora (`programma6/esecuzione.ore_di`, completate con i mesi mancanti dell'archivio);
  * i dati sulle posizioni a 5 minuti (`metrics` dell'archivio pubblico di Binance, un file al giorno controllato con il CHECKSUM),
    solo per i giorni-moneta con almeno un'ora che passa la condizione sul prezzo (a);
  * le candele da 1 minuto (archivio di Binance) del giorno dell'evento e di quello dopo.

  I giorni-moneta senza i dati sulle posizioni si saltano, e si dice quanti sono.

## 3. La regola

L'ora `t` è la candela che apre al minuto 60·t (UTC).

* **Il segnale alla fine dell'ora t**, per una moneta dell'universo della settimana:
  * (a) **il prezzo**: la chiusura dell'ora t è almeno il **5% sotto** la chiusura dell'ora t − 1;
  * (b) **le posizioni**: l'interesse aperto **in monete** (`sum_open_interest`, non in dollari, così il calo del prezzo non lo
    muove da solo) nell'ultima rilevazione dell'ora t (minuto 60·t + 55) è almeno il **5% sotto** quello dell'ultima rilevazione
    dell'ora t − 1 (minuto 60·t − 5). Vuol dire che nella stessa ora si è chiuso almeno un ventesimo delle posizioni.
* **Entrata**: long all'apertura del minuto 60·(t + 1) + 5. I 5 minuti servono alla pubblicazione del dato sulle posizioni e alla
  lettura del bot. L'ordine è a mercato, con il costo di ogni moneta del programma 6 (`sc.costi_moneta`).
* **Uscita**:
  * dopo **4 ore**, all'apertura del minuto entrata + 240, a mercato;
  * **protezione a −15%** dall'entrata, con l'uscita a quel livello meno l'1%;
  * nessun obiettivo;
  * se i dati finiscono, all'ultima chiusura.
* **Funding**: il long paga il funding quando è positivo, in proporzione al tempo (come le prove 75 e 78), con il funding giornaliero
  del pannello.
* **Una posizione per moneta**: il segnale seguente della stessa moneta conta solo dopo l'uscita.
* **Una prova a eventi**: nel conto delle prove diventano **207**, le prove a eventi **33**.

## 4. L'esame

* **Come le prove 75 e 78.** La media per operazione dopo i costi deve essere sopra zero con **p ≤ 0,01** (`trentesima.esame`, con il
  ricampionamento a blocchi), positiva nelle due metà del periodo e positiva anche senza le 5 operazioni migliori. Per dirla valida
  contando le 33 prove a eventi serve **p ≤ 0,0003**.
* **In più, scritto qui**: deve restare positiva con i costi doppi.
* **Portafoglio**: il 5% del conto a operazione, al massimo 20 aperte (`quarantunesima.portafoglio` del programma 6). Si calcola lo
  Sharpe corretto con l'aggiunta, e per le candidate da 0,90 in su vale la decisione del proprietario del 24 ottobre.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**:
  * **C1**, il crollo con le posizioni in salita: (a) e l'interesse aperto alla fine dell'ora non sotto quello dell'inizio (short nuovi);
  * **C2**, il crollo senza condizione sulle posizioni: solo (a), cioè l'analogo della prova 78 sulle 100 grandi;
  * **il caso**: entrate a ore prese a caso negli stessi giorni-moneta, con la stessa uscita;
  * le uscite dopo 1 ora e dopo 24 ore;
  * la versione coperta con il Bitcoin;
  * le cascate di tutto il mercato (il Bitcoin giù almeno del 3% nella stessa ora) contro quelle della moneta da sola;
  * per anno, e la parte del guadagno che viene dai 5 giorni migliori.
