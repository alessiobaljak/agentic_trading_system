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

## Cosa deve fare il proprietario (la sessione non può: niente accesso a Binance, Firebase e alla macchina)

1. **Le chiavi del conto vero di Binance** (Binance, Gestione API, la chiave già usata):
   * togliere il permesso di prelievo (deve restare solo «lettura» e «future»);
   * limitarla all'indirizzo della macchina («Limita l'accesso agli IP affidabili»): l'indirizzo IPv4 della macchina sta nella console
     di Hetzner (il server, «Networking», «Public IP»);
   * controllare che il conto abbia i future USDⓈ-M attivi.
2. **Le regole di Firebase**: mandare alla sessione l'identificativo utente (Firebase, «Authentication», «Users», la colonna «User
   UID») oppure una foto delle due pagine «Regole» (Firestore e Realtime Database); la sessione prepara le regole da incollare e
   pubblicare. L'identificativo non va nel repo.
3. **Le decisioni sui soldi veri** (sì o no; la sessione nel frattempo prepara la scelta più prudente):
   * niente stop per singola moneta (proteggono lo stop sul conto e il pulsante);
   * un pavimento: sotto i 650 USDT su 1.000 (il 65% del capitale di partenza) il conto non riparte più da solo;
   * i limiti di G1 come costanti protette con test (leva 5, tetto del capitale, stop sul conto);
   * «riparti» in due passi (una richiesta e una conferma).
   * lo Sharpe corretto di G1 è 0,86, sotto lo 0,90 della regola del 24 ottobre (revisione del 29 ottobre): va accettato da lui.
4. **Le decisioni nate dalla revisione della fase 2** (`reviews/reports/2026-11-08-fase2-conto-vero-2.md`, «Decisioni per
   Alessio»):
   * **chi approva il codice per i soldi veri** (obbligatoria prima dell'accensione): un tag firmato da lui e verificato dal bot,
     oppure una regola di GitHub che solo lui possa spostare il tag `conto-vero-approvato`; oggi lo può spostare chiunque spinga sul
     repository, sessioni comprese;
   * l'eccezione: con il conto vero già acceso e posizioni aperte, ordini di sola chiusura anche con `DRY_RUN` vero (per non
     lasciarle scoperte quando lo si spegne);
   * i limiti: 300 USDT di capitale, 600 di valore massimo, posizioni al massimo il doppio del conto, 60% per moneta, leva 5, stop a
     −35% con il pavimento al 65%;
   * un prelievo ferma gli ordini nuovi finché non si mette un capitale nuovo (che chiude tutto e riapre alla mezzanotte);
   * ogni commit che tocca un file caricato dal bot ferma gli ordini nuovi finché il tag non si sposta;
   * se lo stato si perde dopo un'accensione, il bot chiude tutto e aspetta un «riparti»;
   * il conto dei future solo del bot: una posizione per moneta, margine solo in USDT, niente «portfolio margin», niente BNB per le
     commissioni.
5. **Alla fine, l'accensione**: la richiesta esplicita, i 280 USDT nel portafoglio dei future, l'ok al riavvio.

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
