# Programma 7 — cinquantottesima prova: il Bitcoin dopo gli acquisti annunciati da Strategy (ST)

Scritto il 28 ottobre 2026 alle 12:25 UTC (ora dell'orologio), **prima di leggere i testi delle comunicazioni e prima di qualunque
calcolo sul prezzo**. Fino a qui si è contato solo quante comunicazioni ci sono e a che ora: 172 comunicazioni di eventi generali
(«8.01») dal settembre 2021, quasi tutte il lunedì fra le 12 e le 13 UTC. È l'idea 92 della coda, dalla ricerca nella letteratura del 28
ottobre. È una prova a eventi sul Bitcoin, con entrata e uscita in un giorno.

## 1. Perché

* **Il grande compratore ha finito, e si vende sulla notizia.** Strategy (prima MicroStrategy) compra Bitcoin durante la settimana e lo
  dice il lunedì mattina con una comunicazione ufficiale alla SEC americana. Quando la notizia esce, gli acquisti sono già fatti: la
  spinta è finita. Chi ha comprato prima per anticiparla vende.
* **Cosa dice la ricerca**: K33 Research (Lunde, 28 marzo 2023, rapporto di settore, non un articolo accademico) trova il Bitcoin a
  −2,2% in media nel giorno dell'annuncio.
* **La direzione scritta prima**: short il Bitcoin dopo l'annuncio.
* **I dubbi scritti prima**:
  * il calo potrebbe venire prima della comunicazione (i giornali di settore vedono gli acquisti), e dopo restare solo il rumore;
  * dal 2024 gli annunci sono quasi ogni lunedì, quindi l'effetto si confonde con quello del lunedì;
  * gli annunci dicono anche che Strategy continuerà a comprare.

## 2. Gli eventi (fissati qui)

* **Le comunicazioni**: tutti i moduli 8-K di Strategy (CIK 1050446) dall'agosto 2020 al 26 ottobre 2026, presi dall'archivio pubblico
  EDGAR della SEC (`data.sec.gov/submissions`, anche il file più vecchio).
* **Un evento** è una comunicazione il cui documento principale contiene la frase degli acquisti, «acquired approximately [numero]
  bitcoin» (anche al plurale), senza guardare le date o i prezzi.
* **L'ora dell'evento** è quella di accettazione della SEC (UTC), cioè il momento in cui la comunicazione diventa pubblica.

## 3. La regola

* **Entrata**: short il perpetuo del Bitcoin all'apertura della candela a 1 minuto che comincia 5 minuti dopo l'ora dell'evento.
* **Uscita**: dopo 24 ore, all'apertura della candela; nessuna uscita di protezione.
* **Costi e funding**: il costo a mercato del Bitcoin del programma 6, all'entrata e all'uscita; il funding del giorno, che lo short
  riceve quando è positivo.
* **Una prova a eventi**: nel conto delle prove diventano **216**, le prove a eventi **36**.

## 4. L'esame

* **Come le prove a eventi** (`trentesima.esame`): media sopra zero con **p ≤ 0,01**, positiva nelle due metà e senza i 5 eventi
  migliori. Per dirla valida contando le 36 prove a eventi serve **p ≤ 0,00028**.
* **Il controllo**: la stessa operazione alla stessa ora del giorno, nello stesso giorno della settimana, nelle settimane fra 4 e 52
  prima dell'evento senza annunci in quel giorno (fino a 5 per evento). Dove non ce ne sono si prende un giorno qualunque senza
  annunci, alla stessa ora. Il guadagno dell'evento va confrontato con quello del controllo.
* **Se regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**: il Bitcoin dalle 24 ore prima fino all'annuncio, per vedere se il calo viene prima; le
  tenute di 1 e 4 ore; per anno.

## 5. Sospesa il 28 ottobre alle 14:35 UTC, prima di qualunque risultato

* **I testi delle comunicazioni non si possono scaricare.** L'archivio dei documenti della SEC (`www.sec.gov/Archives`) risponde 403 a
  tutte le richieste di questa macchina. La SEC chiede un indirizzo email di contatto nelle richieste automatiche, e qui non se ne usa
  nessuno senza il permesso del proprietario. L'elenco dei moduli (`data.sec.gov`) invece risponde.
* Il calcolo partito alle 12:27 ha salvato solo file vuoti, quindi non ha riconosciuto nessun evento e non ha calcolato nessun
  rendimento. È stato fermato.
* **La frase della regola era troppo stretta.** Lo dice la ricerca nel testo della SEC (`efts.sec.gov`, che risponde), contando solo i
  moduli trovati, senza prezzi:
  * «acquired approximately» trova 32 moduli;
  * «bitcoins for approximately» ne trova 38;
  * gli annunci settimanali di Strategy dal novembre 2024 usano «acquired [numero] bitcoins for approximately».

  La regola, quando ripartirà, dovrà riconoscere anche questa forma: «acquired» seguito, entro poche parole, da un numero e da
  «bitcoin».
* **Non conta nel conto delle prove**, perché non è stata calcolata. Riparte con un indirizzo di contatto per la SEC, se il
  proprietario lo vuole, oppure con un'altra fonte pubblica delle date degli acquisti.
