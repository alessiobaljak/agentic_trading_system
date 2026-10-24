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
* **Strumenti nuovi della giornata:** le scissioni (GE, DHR, PFE: valutate come incasso al prezzo d'apertura del titolo nuovo; per PFE
  è Alpaca a non contare quella di Viatris), la frazione di azione pagata in contanti nei raggruppamenti, i cambi di nome (FB → META),
  le date dei comunicati della banca centrale con la fonte (`stock/dati/fomc.py`), le misure dello scarto e i controlli dei 34 titoli
  dell'universo (`stock/dati/ESITO_CONTROLLI_UNIVERSO.md`).

## Cosa abbiamo capito il 24 ottobre

* **Sul 2016-2024 nessuna delle 10 idee batte il comprare e tenere** (19 nel conto, comprese 2 aperture del periodo chiuso). Gli effetti
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

## Il prossimo passo

* Il periodo chiuso si riusa per famiglie diverse (deciso il 24 ottobre, sopra).
* La coda delle idee (`REGISTRO.md`, sezione 2): restano le varianti a costi più bassi (I8, I9) e la leva nei giorni speciali (I11,
  da proporre al proprietario). Le idee della bozza del metodo sono finite: per andare avanti servono idee nuove (vedi il messaggio al
  proprietario del 24 ottobre).
* Verificare il salto di NVDA del 25 maggio 2023 e il dividendo in più di QQQ del 27 dicembre 2023.
* Misurare lo scarto nei primi e negli ultimi minuti della seduta (le idee in giornata entrano ed escono proprio lì).
