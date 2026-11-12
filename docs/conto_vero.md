# Il conto vero di Binance: il piano e la lista di chi fa cosa

Il proprietario, 8 novembre 2026: «procedi anche con il setup del trade live e nel caso dimmi cosa devo fare io su firebase o altri
spazi che non puoi fare tu, se puoi fare tu procedi». Il piano viene da `docs/backlog.md`, voce P26 e le sue aggiunte. **Preparare
non è accendere**: il codice del conto vero nasce spento e si accende solo con la richiesta esplicita, ripetuta e consapevole del
proprietario (la regola di `DRY_RUN` in `CLAUDE.md`). Strategia: G1, con 250 euro (280 USDT, prova 148), partenza da conto vuoto alla
mezzanotte UTC, eventi spenti.

## Le fasi

| Fase | Cosa | Chi | Stato |
|---|---|---|---|
| 1 | Chiudere i problemi rimasti del demo che il conto vero erediterà (36-38 della revisione del 7 novembre; Medi 10, 12, 13, 15, 16; Bassi 21-23), con test | sessione principale, poi live-path-reviewer | **fatta l'8 novembre**: approvata al quarto giro (`reviews/reports/2026-11-08-fase1-conto-vero-4.md`); il riavvio del demo aspetta l'ok del proprietario |
| 2 | Il codice del conto vero, spento: modulo suo accanto al demo, solo l'indirizzo vero di Binance, chiavi sue, interruttore suo, tetto del capitale scritto nel codice, partenza da vuoto alla mezzanotte, stop sul conto, limiti di G1 come costanti protette con test, rifiuto dell'avvio se i file del percorso degli ordini non sono quelli della versione approvata (un tag che si sposta solo con l'ok del proprietario) | sessione principale, poi live-path-reviewer | **codice spento committato l'8 novembre** (approvato al terzo giro, `reviews/reports/2026-11-08-fase2-conto-vero-3.md`); restano da chiudere prima dell'accensione i punti nel diario |
| 3 | I controlli finali: backtest-auditor su G1 nella configurazione finale; gate2-reconciler su paper e demo; portfolio-allocator con le regole approvate | agenti | da fare (primo giro lunedì 9 novembre) |
| 4 | L'accensione: la richiesta esplicita del proprietario, i 280 USDT nel portafoglio dei future, un riavvio approvato; il primo ingresso alla mezzanotte dopo | proprietario | dopo le fasi 1-3 |

## Cosa deve fare il proprietario (riletta il 12 novembre 2026 sui tre rapporti della fase 2, sezione «Decisioni per Alessio»)

La sessione non può: niente accesso a Binance, a Firebase e alla macchina.

1. **Firebase, per primo.** Mandare una foto delle due pagine «Regole» (Firestore e Realtime Database) oppure l'identificativo utente
   (Firebase, «Authentication», «Users», colonna «User UID»); la sessione prepara le regole da incollare e pubblicare
   (l'identificativo non va nel repo). Perché per primo: nel repo le regole hanno ancora il segnaposto e nessuno sa quali sono
   pubblicate; il pulsante «chiudi tutto» del demo passa da Firebase; servono alle azioni (`stock/avanti/FIREBASE.md`) e al canale di
   approvazione del punto 2.
2. **Chi approva la versione del codice per i soldi veri** (obbligatoria prima dell'accensione). **Una regola di GitHub con il
   proprietario fra le eccezioni non basta**: il 12 novembre gli strumenti GitHub di questa sessione rispondono come l'utente del
   proprietario (`get_me`: il suo login), quindi una regola che lui può scavalcare la scavalcano anche le sessioni. Due strade, nessuna
   ancora costruita: (a) tag firmato con una sua chiave e verificato dal bot (raccomandata dal revisore; a ogni approvazione serve un
   computer con git); (b) approvazione dalla dashboard con il suo accesso a Firebase, come i comandi del demo (comoda dal telefono;
   richiede le regole del punto 1). Tutte e due passano da live-path-reviewer.
3. **Binance.** Sulla chiave del conto vero: togliere il permesso di prelievo (restano lettura e future) e limitarla all'indirizzo
   della macchina (console di Hetzner, il server, «Networking», «Public IP»). Nel conto dei future: future USDⓈ-M attivi, una
   posizione per moneta (modalità unidirezionale), margine solo in USDT (niente «multi-assets»), niente «portfolio margin», niente BNB
   per le commissioni, nessuna posizione aperta: il conto dei future serve solo al bot.
4. **Le decisioni sì o no** (tutte quelle chieste dal revisore; fra parentesi cosa fa oggi il codice):
   a. spento con posizioni aperte, il bot manda solo ordini di chiusura anche con `DRY_RUN` vero (sì nel codice; è un'eccezione alla
      regola «in paper nessun ordine al conto vero» e serve il suo sì);
   b. i limiti: capitale 300 USDT, valore massimo 600 prima di fermare gli ordini nuovi, posizioni al massimo il 200% del conto, 60%
      per moneta, leva 5, stop a −35% dal massimo con il pavimento al 65% del capitale, decisione di G1 non più vecchia di 26 ore;
   c. un prelievo ferma gli ordini nuovi finché non si scrive un capitale nuovo (che chiude tutto e riapre alla mezzanotte);
   d. ogni commit che tocca un file caricato dal bot ferma gli ordini nuovi finché la versione non è riapprovata, e un ribilancio in
      corso resta a metà; l'alternativa è tenere il codice dei soldi veri separato dalle varianti del paper (non fatto);
   e. se lo stato si perde dopo un'accensione, il bot chiude tutto a mercato e aspetta un «riparti» (costa le spese di chiusura);
   f. quando G1 non decide (decisione vecchia, pesi vuoti o fuori dai limiti, codice bloccato) il conto tiene le posizioni di ieri
      senza limite di tempo, protette solo dallo stop: va bene, o dopo un certo numero di giorni si chiude? Il conto vero dipende
      anche dal paper di G1 acceso;
   g. prima della prima accensione, lo stop chiude le posizioni che trova nel conto (oggi no; il revisore raccomanda sì, problema 70);
   h. «riparti» dopo uno stop: oggi solo da un file del repo, che può scrivere qualunque sessione; i «due passi» non sono ancora
      progettati: la conferma deve passare da un canale che solo il proprietario può scrivere (la dashboard, punto 1);
   i. niente stop per singola moneta su Binance: proteggono lo stop sul conto e il pulsante; se Binance blocca l'indirizzo della
      macchina, per tutto il blocco il bot non protegge e resta solo la liquidazione;
   j. «almeno 10 monete per lato» (revisione con le skill) e gli avvisi sul telefono: non applicati al conto vero;
   k. le scelte della fase 1 già in funzione sul demo e mai confermate una per una: stop anche al 65% del capitale, «riparti» solo a
      conto vuoto con la riapertura alla mezzanotte, una moneta oltre il 60% fa saltare la decisione del giorno, il blocco di Binance
      rispettato per intero.
   Chiusa: lo Sharpe corretto 0,86 di G1 (il proprietario ha approvato la soglia di 0,80 il 9 novembre, contata per famiglie l'11).
5. **Il riavvio che carica la fase 2** sulla macchina (il bot gira ancora il codice della fase 1; il conto vero resta spento): con il
   suo ok, in un'ora tranquilla. Finché non c'è, un riavvio per un guasto caricherebbe comunque l'ultimo codice del branch.
6. **Alla fine, l'accensione**: la richiesta esplicita, i 280 USDT nel portafoglio dei future, l'ok al riavvio.

## Diario
* 8 novembre 2026: piano scritto; fase 1 iniziata.
* 8 novembre 2026: fase 1 approvata da live-path-reviewer al quarto giro (rapporti `reviews/reports/2026-11-08-fase1-conto-vero*.md`):
  chiusi i problemi 36-38, 10, 12, 13, 15, 16, 21-23 e quelli nati nelle correzioni (40-50; restano due Bassi, 51 e 52). Scelte
  della sessione da confermare dal proprietario: stop anche al 65% del capitale della fase (la perdita resta entro il 35%), «riparti»
  solo a conto vuoto e con la riapertura alla decisione di G1 dopo (la mezzanotte), limiti nuovi come costanti con un test di
  guardia, una moneta oltre il 60% fa saltare la decisione del giorno, quando G1 non decide il demo tiene le posizioni di ieri, con
  Binance che blocca l'indirizzo si rispetta tutto il blocco (in quel tempo il bot non protegge il conto). 2.624 test passano.
* 8 novembre 2026, 19:02 UTC: riavvio del bot con la fase 1, ok del proprietario; nessun errore all'avvio (`ops/results/0723-*`).
  Il proprietario: la strategia per i soldi veri (G1 o G1 neutra) la decide portfolio-allocator lunedì 9 novembre, con le regole che
  approva lui. Prossimo: fase 2 (il codice del conto vero, spento).
* 8 novembre 2026, sera: fase 2, il codice del conto vero (`bot/portafoglio/conto_vero.py`) committato **spento**, approvato da
  live-path-reviewer al terzo giro (più il controllo del problema 71). Senza `ops/conto_vero_acceso` e con `DRY_RUN` vero non fa
  richieste e non legge le chiavi. `scripts/ops_agent.py` porta sulla macchina il tag `conto-vero-approvato` (entra in funzione al
  primo `git pull`, senza riavvio). Il bot lo carica al prossimo riavvio, che si fa con l'ok del proprietario. **Da chiudere prima
  dell'accensione**: la protezione del tag (54, decisione del proprietario: firma o regola di GitHub); il 70 (stato e traccia su
  Firebase persi: le posizioni restano senza stop) con la decisione se lo stop chiude le posizioni trovate prima della prima
  accensione; pulsante, stato e regole di Firebase del conto vero in dashboard (60); 66, 72, 73 (bassi); le decisioni del proprietario
  qui sopra; la verifica con una lettura vera dei redditi di Binance; poi una revisione nuova prima dell'accensione.
* 12 novembre 2026: lista del proprietario riletta sui rapporti del revisore: la regola di GitHub non basta (la sessione agisce su
  GitHub come il proprietario), mancavano quattro decisioni (stato perso, G1 che non decide, codice separato, monete per lato) e il
  riavvio che carica la fase 2; Firebase passa al primo posto. Lanciata la revisione di G1 con backtest-auditor (fase 3).
* 12 novembre 2026, le regole di Firebase pubblicate (foto del proprietario): Firestore e Realtime Database sono **chiusi e con il suo
  identificativo** (lettura solo sua; scrittura solo dei comandi `kill_switch` e `close_position` e, per l'utente dedicato delle azioni,
  di `/azioni`). **Mancano** i blocchi `commands/demo_binance_chiudi_tutto` e `commands/demo_binance_riparti`, che il file del repo ha dal
  7 novembre: i pulsanti «Chiudi tutto» e «Riparti» del demo in dashboard oggi sono rifiutati da Firebase (lo stop automatico sul conto e
  i comandi da file funzionano). Il testo dei due blocchi da aggiungere è stato dato al proprietario in conversazione (l'identificativo
  non va nel repo). Punto 2: il proprietario ha scelto «pulsante in dashboard»; lavoro avviato (implementatore, poi live-path-reviewer).
* 12 novembre 2026, **la revisione di G1 con backtest-auditor** (fase 3; `audits/reports/2026-11-12-G1_CONTO_VERO.md`): **PASS
  tecnico** (Sharpe 1,98, a 280 USDT con i minimi 1,90, ogni anno positivo, nessun dato del futuro, il bot calcola gli stessi pesi
  della ricerca in 60 giorni su 60), **con 4 problemi Alti da chiudere prima dell'accensione**: (1) l'esame a 0,80 passa solo se gli
  ordini limite pagano davvero la commissione bassa (0,81; tutto a mercato 0,77): va misurata sul demo, e l'ordine al prezzo mark può
  eseguirsi subito come ordine a mercato; (2) la soglia scritta prima era 0,95, scesa a 0,90 e poi a 0,80 per decisione del
  proprietario: l'esame non è più quello scritto prima; (3) concentrazione: una moneta venduta è arrivata al 43,7% del capitale (un
  rialzo del 100% costerebbe il 44% del conto prima dello stop), 67 giorni con meno di 10 monete vendute, e i limiti fissi del vecchio
  bot (perdita giornaliera 5%, 3% a posizione) non valgono per G1; (4) il funding del demo è circa il 40% sotto quello del paper il 10
  e l'11 novembre. In corso: gate2-reconciler su (1) e (4), le regole della prova 152 su (3).

