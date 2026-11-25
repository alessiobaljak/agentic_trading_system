# Revisione del 25 novembre 2026: il conto vero esegue F5 al posto di G1

### Riepilogo e verdetto

**REQUEST CHANGES** per il commit così com'è. Nessun problema Bloccante, nessun Alto. Il conto vero resta spento: questa modifica da
sola non può mandare ordini (interruttore, `DRY_RUN` e versione approvata su Firebase invariati; la versione approvata, se c'era, non
vale più perché `conto_vero.py` cambia).

La meccanica è giusta: lo stato del paper di F5 ha le stesse due chiavi che il conto vero legge (`ultimo_lunedi`, `pesi`), il giorno
della decisione è sempre un lunedì, e la prima accensione, il «riparti», il fermo e la fine di un blocco aspettano correttamente la
decisione del lunedì dopo. L'ho dimostrato con 9 prove a mano, tutte superate, compresa una che va dal vero `PaperF5` al conto vero
(`giro25nov/test_prove_25nov.py` nella cartella di lavoro).

Cosa manca per l'APPROVE:
* **178 (Medio)**: i test del repository non coprono la modifica: il file letto davvero non è fissato da nessun test (la prova di
  mutazione passa tutta la suite) e non c'è nessun test del ciclo settimanale.
* **179 (Medio)**: il conto vero non dice da nessuna parte che esegue F5: log d'avvio, Firebase, allarmi e dashboard dicono «G1» e «la
  mezzanotte». Il proprietario approverebbe dalla scheda «G1 sul conto vero» una versione che esegue F5.

Prima dell'accensione servono due decisioni di Alessio. **180 (Medio)**: i limiti dei pesi (200% e 60%) si controllano solo al lunedì,
mentre le posizioni di F5 restano ferme 7 giorni. **181 (Medio)**: un blocco sopra il lunedì salta tutta la settimana. Restano aperti
anche, dalle revisioni di prima, il 54 (ii) Alto, il 70 Medio e il 78 Basso.

Test: `python3 -m pytest tests/ -q` (senza il test della firma) → **2818 passed, 1 deselected** in 218 s. Il test della firma, con la
libreria di cifratura della cartella di lavoro, passa insieme ai test di guardia dei limiti: `tests/test_demo_binance.py::test_firma_dei_tre_tipi_di_chiave tests/test_risk.py
tests/test_sizing.py tests/test_conto_vero.py` → **119 passed**. Prove del revisore: **9 passed**.

### Oggetto

* Branch `claude/brave-albattani-1b12fv`, modifica **non committata** su `932c048`. Mentre rivedevo, la sessione principale ha
  committato come `932c048` le parti di documentazione (`CLAUDE.md`, `allocazione/REGOLE.md`, `docs/decisioni_del_proprietario.md`).
  Restano fuori dal commit: `bot/portafoglio/conto_vero.py` (md5 `f3d97671d6c150964b36cd03e0bcb794`) e `tests/test_conto_vero.py`
  (md5 `d0c657c7da7e4ff088cebc0171bcf06e`). Se al commit le impronte sono diverse, va rivisto il cambio.
* La modifica:
  * nuove costanti `STRATEGIA = "F5"` e `FILE_STRATEGIA = RADICE / "data" / "paper_f5.json"`, a `conto_vero.py:127-130`;
  * `ETA_MASSIMA_DECISIONE_S`: da 26 ore a 8 giorni e 2 ore (194 ore), a `conto_vero.py:131`, copiata nella classe a `:334`;
  * il file predefinito `file_g1` di `ContoVeroG1.__init__` diventa `FILE_STRATEGIA`, a `conto_vero.py:341`;
  * la guardia del test: `tests/test_conto_vero.py:171-172`.
* La decisione: il proprietario il 25 novembre, «metti F5 come candidata per il conto piccolo»
  (`docs/decisioni_del_proprietario.md:197-205`). Il valore di 8 giorni e 2 ore lo ha scritto la sessione principale, non il
  proprietario.
* Invarianti coinvolti:
  * la fonte della decisione del conto vero;
  * l'età massima della decisione;
  * l'attesa alla prima accensione, dopo un «riparti», alla fine di un blocco e con un capitale nuovo: ora fino al lunedì dopo;
  * il significato dei limiti dei pesi su posizioni tenute 7 giorni.

Il demo non cambia: legge ancora `data/paper_g1.json` (`demo_binance.py:68`, `:513`) con l'età di 26 ore (`:86`).

### Checklist A–F

**A. Limiti fissi e interruttori**
* A1, valori di `bot/risk/hard_limits.py` invariati. **OK**: la modifica tocca solo `conto_vero.py` e il suo test. L'ultimo cambio a
  `hard_limits.py`, `circuit_breakers.py` e `kill_switch.py` è `e3a5254` del 30 ottobre.
* A2, nessun limite critico in configurazione, variabili d'ambiente o Firebase. **OK**: strategia, file ed età sono costanti nel codice
  (`conto_vero.py:129-131`), fissate dal test di guardia (`tests/test_conto_vero.py:171-172`, `:182-185`).
* A3, parametri della dashboard (`user_risk_settings`). **NON APPLICABILE**: riguardano il vecchio bot, che la modifica non tocca. I
  problemi del 7 novembre restano aperti (mappa, sezione 6).
* A4, limiti propri come costanti. **OK, con un invariante cambiato.** L'età massima del conto vero passa da 26 a 194 ore (sezione
  «Invarianti modificati»). Il docstring della guardia chiede che ogni cambio sia «spiegato al proprietario e fatto approvare»
  (`tests/test_conto_vero.py:162-163`): l'approvazione della versione nuova su Firebase sarà quel sì. I limiti dei pesi restano quelli
  pensati per G1 (`conto_vero.py:125-126`): vedi 180. Come prima, i limiti del conto vero stanno fuori da `hard_limits.py` (scelta dell'8
  novembre).
* A5, pulsante che chiude tutto senza Firebase. **OK, invariato.** Il file `ops/conto_vero_chiudi_tutto` (`conto_vero.py:87`, `:331`) e
  lo stop sul conto non dipendono dalla strategia. La prova P3 lo conferma col ciclo di F5: pulsante di mercoledì, conto chiuso,
  «riparti».

**B. Ordini** (codice ereditato da `demo_binance.py`, invariato)
* B1, passi e valore minimo da `exchangeInfo`. **OK**: `ribilancia` `demo_binance.py:1301-1302`, con i filtri veri a ogni ribilancio
  (`conto_vero.py:894-903`).
* B2, identificativo. **OK**: `id_ordine(giorno, s, int(now))` (`demo_binance.py:1333`), con `giorno` che ora è il lunedì. Il resto a
  mercato usa l'identificativo fisso, controllato prima dell'invio (mappa, sezione 7).
* B3, «solo riduzione» e una posizione per moneta. **OK**: `demo_binance.py:1124-1125`, `:1334-1335`, `:1305-1309`.
* B4, prezzo degli stop. **OK**: lo stop sul conto usa il valore del margine, cioè il prezzo mark. Gli ordini limite stanno al prezzo
  mark per un'ora, come la simulazione del paper di F5 (`f5.py:11-15`).
* B5, leva e margine espliciti. **OK**: `demo_binance.py:1337-1342`, leva 5 della classe.
* B6, strategia a portafoglio. **OK**: stop sul conto e pulsante ci sono e funzionano (prove P3 e
  `tests/test_conto_vero.py:296-322`). Non c'è uno stop per posizione: è una decisione di Alessio, e con F5 le posizioni restano 7
  giorni invece di 1 (decisione 4).

**C. Stato e resilienza**
* C1, ricostruzione da Binance. **OK, invariato**: posizioni rilette a ogni ribilancio (`demo_binance.py:1316`), confronto ogni ora
  (`:1261-1282`).
* C2, flussi in tempo reale. **NON APPLICABILE**: solo richieste una per volta.
* C3, decisioni su candele chiuse. **OK**: F5 decide il lunedì alle 00:05 con i dati fino alla domenica, e aspetta il regolamento delle
  00:00 se manca per oltre il 10% delle monete (`f5.py:6-7`, `:528-534`, `:314-334`).
* Lettura dello stato di F5. **OK**:
  * il paper scrive in modo atomico (`f5.py:297-301`) le due chiavi insieme (`f5.py:457-459`);
  * il giorno è sempre il lunedì (`f5.py:306-312`);
  * ogni lato somma 1 (`f5.py:159-164`), quindi 200% in tutto;
  * il conto vero legge le stesse chiavi del demo (`demo_binance.py:870-874`), le controlla (`:875-878`), controlla età e data nel
    futuro (`:917-934`) e prende il giorno con `_giorno_g1` (`:1127-1133`);
  * il paper di F5 gira nello stesso giro, prima del conto vero (`bot/main.py:2636`, `:2655-2659`): la decisione del lunedì è letta
    nello stesso giro in cui nasce (prova P8).
* C4, errori delle interfacce. **OK, invariato** (`ClienteDemo.chiedi`, mappa, sezione 7).
* C5, scrittura su Firebase che fallisce. **OK, invariato.**
* C6, orologio della macchina. **OK, invariato**: `systemd-timesyncd` (mappa, sezione 11).

**D. Separazione fra paper, demo e conto vero**
* Indirizzo, chiavi e `DRY_RUN`. **OK, invariato**: indirizzo solo `fapi.binance.com` (`conto_vero.py:141-146`, `:316-317`),
  `ClienteVero` soltanto (`:345-346`), `DRY_RUN` letto con `_get_bool_sicuro` (`:402-415`).
* Log d'avvio chiaro sull'ambiente. **PROBLEMA (179)**: il log e `/conto_vero/avvio` non dicono quale strategia il conto vero esegue
  (prova P6). Demo e conto vero ora eseguono strategie diverse.

**E. Segreti e sicurezza**
* Segreti nel cambio. **OK**: il cambio non contiene chiavi né indirizzi con chiavi.
* Chiavi senza prelievo e limitate all'indirizzo della macchina. **Da confermare con Alessio**, come prima: il 7 novembre lui ha detto
  che non sono limitate all'indirizzo.
* Regole di Firebase. **Da confermare con Alessio**: quelle pubblicate non hanno i blocchi del conto vero (foto del 12 novembre).

**F. Test**
* Suite e test di guardia. **OK**: suite intera 2818 superati; test di guardia dei limiti (`tests/test_risk.py`,
  `tests/test_sizing.py`, `tests/test_conto_vero.py`) superati.
* Test che coprono la modifica. **PROBLEMA (178)**: il test nuovo fissa le costanti, non il comportamento, e nemmeno il file che la
  classe legge davvero.

### Le prove del revisore

File: `giro25nov/test_prove_25nov.py` nella cartella di lavoro. Lancio:
`PYTHONPATH=<radice> python3 -m pytest <file> -q -s -p no:cacheprovider`. Esito: **9 passed**. Le date sono vere: lunedì 23 novembre
(giorno 20780), poi 30 novembre, 7 e 14 dicembre.

| Prova | Cosa | Esito |
|---|---|---|
| P1 | Acceso mercoledì 25 a mezzogiorno con la decisione del 23 nel file: nessuna richiesta che scrive da giovedì a domenica né lunedì alle 00:03, nessun allarme; alla decisione del 30 due ordini limite. `compra_alla_decisione_di_g1_dopo_il` = 2026-11-23 | come atteso |
| P2 | Età: martedì alle 02:01 nessun allarme (con le 26 ore di G1 ci sarebbe); a 194 ore meno un minuto nessun allarme; a 194 ore e due minuti allarme `decisione_g1`; la decisione nuova arrivata dopo si esegue e l'allarme si toglie | come atteso; testo dell'allarme sotto (179) |
| P2b | Lunedì, F5 in ritardo di 3 ore (regolamento non pubblicato): nessun allarme, poi si esegue | come atteso |
| P3 | Pulsante e «riparti» mercoledì 2 dicembre: conto vuoto fino al 7 dicembre, poi ordini | come atteso (fino a 5 giorni vuoto) |
| P4 | Blocco martedì, tolto mercoledì: niente fino al lunedì dopo | come atteso |
| P5 | Blocco da domenica 6 a lunedì 7 alle 09:00: la decisione del 7 dicembre non si esegue mai; ordini solo il 14 | come scritto nel codice; vedi 181 |
| P6 | File predefinito del conto vero = `paper_f5.json` = `f5.FILE_STATO`; demo su `paper_g1.json`; `/conto_vero/avvio` senza «F5» | file giusti; strategia non dichiarata (179) |
| P7 | Mutazione: file predefinito riportato a `paper_g1.json` → `test_i_limiti_del_conto_vero_sono_fissati` passa lo stesso | il test non vede il cambio (178) |
| P8 | Il vero `PaperF5`, con il Binance finto dei suoi test (`tests/test_paper_f5.py:75`), decide lunedì 23 e 30; il conto vero acceso mercoledì esegue la decisione del 30: 12 ordini limite, lato per lato uguali ai pesi di F5 (somma 2,0000, massimo 0,408) | come atteso |

Testo dell'allarme della prova P2, come lo vedrebbe la dashboard: «la decisione di G1 è del 2026-11-23, 194 ore fa (oltre 194): niente
ordini nuovi finché il paper di G1 non decide di nuovo».

### Problemi

**178 — Medio — i test del repository non coprono la modifica**
* Dove: `tests/test_conto_vero.py:171-172`. La guardia fissa `cv.STRATEGIA` e `cv.FILE_STRATEGIA`, ma `STRATEGIA` non è usata da nessun
  codice (grep: solo il test) e nessun test controlla che `ContoVeroG1` legga davvero `FILE_STRATEGIA`. Tutti i test del conto vero
  passano un `file_g1` loro (`tests/test_conto_vero.py:122-123`) con decisioni giornaliere (`:27-29`, `:106-107`).
* Guasto concreto: una fusione o un riordino riporta il valore predefinito a `demo.FILE_G1`, oppure cambia il calcolo dell'età. La
  suite resta tutta verde (prova P7) e il conto vero, una volta acceso, eseguirebbe G1 mentre il proprietario crede F5. Chi approva la
  versione si fida della revisione e dei test.
* Correzione suggerita, in `tests/test_conto_vero.py`:
  * (a) un controllo che fissi il file letto davvero: `cv.ContoVeroG1(_Fb(), verifica_codice=lambda: None).file_g1 == cv.FILE_STRATEGIA
    == f5.FILE_STATO`, e che il demo resti su `paper_g1.json`;
  * (b) un test del ciclo settimanale con date di lunedì: accensione a metà settimana con niente fino al lunedì dopo, nessun allarme in
    settimana, allarme oltre le 194 ore;
  * (c) se si vuole, il passaggio dal vero `PaperF5` al conto vero.

  Le prove P1, P2, P6 e P8 si possono copiare così come sono.

**179 — Medio — la strategia eseguita non è dichiarata e i testi dicono G1 e la mezzanotte**
* Dove:
  * `_ambiente` (`demo_binance.py:936-942`, `conto_vero.py:905-915`): log d'avvio e `/conto_vero/avvio` senza la strategia né il file
    della decisione (prova P6);
  * l'allarme dell'età (`demo_binance.py:927-929`): «decisione di G1», «finché il paper di G1 non decide di nuovo» (prova P2);
  * la prima accensione (`conto_vero.py:847-854`): chiave `compra_alla_decisione_di_g1_dopo_il` e «(la mezzanotte UTC)»;
  * il capitale nuovo (`demo_binance.py:618`): «parte alla prossima decisione di G1»;
  * la dashboard: la scheda si chiama «G1 sul conto vero» (`dashboard/app/lib/strategie.ts:61`), e i due passi del «riparti» dicono
    «riapre alla prossima decisione di G1» e «alla prossima decisione di G1 (dopo la mezzanotte UTC)»
    (`dashboard/app/components/strategie/ComandiContoVero.tsx:182`, `:192-193`);
  * il piano: «decisione di G1 non più vecchia di 26 ore» (`docs/conto_vero.md:44`);
  * la fotografia dello stato: «Le righe di G1 sul conto vero» (`scripts/state_snapshot.py:686-687`).
* Guasti concreti:
  * (1) il proprietario approva dalla scheda «G1 sul conto vero» una versione che esegue F5: il suo sì, sui soldi veri, non è informato
    da quello che vede;
  * (2) dopo un «riparti» si aspetta le posizioni dopo la mezzanotte, invece il conto resta vuoto fino al lunedì (prova P3);
  * (3) con il paper di F5 fermo, l'allarme manda a controllare il paper di G1, che gira bene, e la causa vera resta nascosta.
* Correzione suggerita:
  * `STRATEGIA` e il nome del file in `_ambiente` del conto vero e in `/conto_vero/versione`, così la scheda dell'approvazione li mostra;
  * i testi degli allarmi e del log presi dalla classe (`self.STRATEGIA`, «al prossimo lunedì» per il conto vero). La chiave di
    Firebase `compra_alla_decisione_di_g1_dopo_il` è letta anche da `_stato_perso` (`conto_vero.py:600`): se si rinomina, vanno
    cambiate insieme, oppure si lascia il nome e si cambia solo il testo;
  * nome della scheda e testi del «riparti» in dashboard, `docs/conto_vero.md`, la fotografia.

  Per il commit bastano log, Firebase e allarmi del bot. Dashboard e documenti vanno corretti prima dell'approvazione della versione.

**180 — Medio — i limiti dei pesi valgono solo al lunedì; con F5 le posizioni restano ferme 7 giorni**
* Dove: `pesi_fuori_dai_limiti` controlla solo i pesi della decisione nel file (`demo_binance.py:874-878`). Il confronto di ogni ora
  (`:1261-1282`) misura le quantità contro gli obiettivi, non il peso di una moneta né la somma rispetto al valore del conto di adesso.
  Il 60% per moneta è giustificato dal massimo di G1 sul passato, il 47,8% di BLZ (`conto_vero.py:126`, `docs/backlog.md:210-211`). Il
  massimo di F5 sul passato non ha una fonte nel repository: l'ho cercato e non l'ho trovato.
* Guasto concreto: un lato venduto a 5 monete (il caso di BLZ) con una moneta al 45%, che sale del 30% in quattro giorni. Arriva al
  58,5% del capitale di partenza con il conto a −13,5%, cioè circa il 68% del valore di adesso. L'esposizione totale supera il 200% del
  valore del conto. Con G1 il ribilancio del giorno dopo la riportava all'obiettivo; con F5 resta così fino al lunedì. La protezione vera
  resta lo stop sul conto a −35%, che chiude tutto: la perdita non va oltre lo stop, salvo i salti di prezzo e il bot fermo. Ma i due
  limiti «200%» e «60%» descrivono il conto solo il lunedì.
* Correzione suggerita, da decidere (non per il commit):
  * (a) misurare sul passato il peso massimo per moneta di F5 e l'esposizione totale con la deriva della settimana: è lavoro di
    strategy-researcher e backtest-auditor, non mio;
  * (b) Alessio decide se aggiungere al giro di ogni ora un controllo sull'esposizione vera (allarme, o riduzione oltre una soglia), o
    se basta lo stop sul conto.

**181 — Medio — un blocco sopra il lunedì salta la settimana; «riparti» e capitale nuovo aspettano fino a 7 giorni**
* Dove:
  * alla fine di un blocco si prende come già eseguita la decisione nel file (`conto_vero.py:846-851`);
  * il «riparti» fa lo stesso (`demo_binance.py:996-997`);
  * il capitale nuovo parte al ribilancio dopo (`demo_binance.py:614-618`, `:880-881`).

  Con G1 l'attesa era al massimo un giorno, ora è una settimana (prove P3, P4, P5).
* Frequenza misurata: dal 26 ottobre al 25 novembre, 17 commit in 9 giorni diversi hanno toccato i percorsi degli ordini (`git log` su
  `bot/portafoglio`, `bot/execution`, `bot/risk`, `bot/config.py`, `bot/main.py`). Ognuno chiede una versione approvata nuova, e un
  riavvio, altrimenti il conto vero è bloccato (`conto_vero.py:445-470`, `:768-813`). Contano anche gli altri file del repository
  caricati nel processo (`file_caricati`).
* Guasto concreto (prova P5): un commit la domenica, approvato il lunedì alle 09:00. La decisione di F5 di quel lunedì non si esegue
  mai e il conto tiene le posizioni della settimana prima fino al lunedì dopo: 14 giorni sulla stessa decisione, mentre il paper ha già
  ribilanciato. È lo stesso tipo di guasto del 74 (un buco salta il ribilancio), che fu valutato Medio. Non toglie protezioni: stop e
  pulsante restano.
* Correzione suggerita, da decidere: Alessio sceglie fra
  * tenere la regola «si compra solo alla decisione», più prudente, con un allarme «settimana saltata» quando un lunedì passa sotto
    blocco;
  * permettere di eseguire la decisione della settimana se il blocco finisce entro poche ore dalle 00:05 del lunedì (per esempio
    nell'ora degli ordini limite). Il proprietario il 6-7 novembre ha detto «comprerà alla mezzanotte, senza copiare a metà giornata il
    paper».

**182 — Basso — il controllo del margine riapre a metà settimana**
* Dove: `controlla_margine` azzera `ultimo_giorno` quando trova una moneta a margine separato con una posizione
  (`demo_binance.py:1234-1235`). Il giro dopo riesegue la decisione nel file: con G1 erano «i pesi di oggi», con F5 sono i pesi del
  lunedì, vecchi fino a 7 giorni. Con un capitale in attesa parte anche `parti_da_zero` a metà settimana (`:880-881`), contro la regola
  della mezzanotte.
* Succede solo se qualcuno mette a mano il margine separato: il bot imposta sempre il margine unico. Comportamento che c'era già con
  G1, a metà giornata.
* Correzione suggerita: con F5 riaprire solo le monete sistemate, non tutto il conto, e niente `parti_da_zero` fuori dalla decisione.
  Oppure lasciarlo e scriverlo.

Restano aperti dalle revisioni di prima, per l'accensione: 54 (ii) Alto (la chiave di amministratore di Firebase può scrivere
l'approvazione), 70 Medio (stato e traccia persi = stop spento), 78 Basso (`reports/2026-11-12-conto-vero-versione-firebase-2.md`).

### Invarianti modificati

* **La fonte della decisione del conto vero**: da `data/paper_g1.json` (G1, ogni giorno) a `data/paper_f5.json` (F5, ogni lunedì alle
  00:05), in `conto_vero.py:130`, `:341`. Il demo resta su G1.
* **L'età massima della decisione del conto vero**: da 26 ore a 194 ore, cioè 8 giorni e 2 ore (`conto_vero.py:131`). Con il paper di
  F5 fermo l'allarme arriva fino a 8 giorni dopo l'ultima decisione, non più dopo 26 ore. Il demo resta a 26 ore
  (`demo_binance.py:86`).
* **L'attesa prima degli ordini** alla prima accensione, dopo un «riparti», alla fine di un blocco e con un capitale nuovo: da «fino
  alla mezzanotte» a «fino al lunedì», cioè fino a 7 giorni (181).
* **Le posizioni fra due ribilanci**: da 1 giorno a 7. I limiti dei pesi del 200% e del 60% valgono al lunedì (180).
* I limiti fissi di `hard_limits.py` non cambiano. Leva, capitale, valore massimo, stop, pavimento, somma e peso per moneta del conto
  vero non cambiano.

### Decisioni per Alessio

1. **L'età di 8 giorni e 2 ore** (il valore l'ha scelto la sessione principale): va bene che, con il paper di F5 fermo, l'allarme
   arrivi fino a 8 giorni dopo invece che dopo 26 ore? Secondo la guardia dei limiti, il suo sì è l'approvazione della versione nuova.
2. **Le attese fino a 7 giorni** (181): prima accensione, «riparti», capitale nuovo e fine di un blocco aspettano il lunedì; un blocco
   sopra il lunedì salta la settimana. Tenere così (più prudente), con un allarme «settimana saltata», o eseguire la decisione della
   settimana se il blocco finisce entro poche ore?
3. **I pesi fra un lunedì e l'altro** (180): basta lo stop sul conto, o serve un controllo di ogni ora sull'esposizione vera? Prima
   serve la misura del peso massimo di F5 sul passato, con la deriva della settimana: si può chiedere alla ricerca.
4. **Nessuno stop per posizione** (come per G1, scelta già fatta): con F5 le posizioni restano 7 giorni. Confermare che bastano lo stop
   sul conto e il pulsante.
5. **F5 non è mai passata dal demo**: gli ordini veri sono stati provati solo con le decisioni giornaliere di G1. Il percorso è lo
   stesso, ma cambiano il ritmo e la grandezza dei ribilanci. Decidere se serve una prova di F5 su un conto demo prima dei soldi veri,
   senza spegnere G1 sul demo (regola dell'8 novembre).
6. Per l'accensione restano: la decisione sul 54 (ii), il 70, il 78, le regole di Firebase pubblicate con i blocchi del conto vero, le
   chiavi senza prelievo e limitate all'indirizzo, e una revisione nuova sul commit da approvare.

### Domande aperte

1. Il peso massimo per moneta di F5 sul passato (e con la deriva della settimana) è stato misurato da qualche parte? Nel repository ho
   trovato solo quello di G1 (47,8%, `docs/backlog.md:210-211`).
2. «Il conto piccolo» della decisione del 25 novembre è il conto vero con il tetto di 300 USDT (`conto_vero.py:121`)? Il codice
   presuppone di sì.
3. La sessione principale aggiorna la scheda della dashboard («G1 sul conto vero») e i testi del «riparti» prima di chiedere al
   proprietario l'approvazione della versione nuova?
