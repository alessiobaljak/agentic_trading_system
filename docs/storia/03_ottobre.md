# 03 — Ottobre 2026 (1-18): bot, gate, paper e decisioni del proprietario

> Capitolo della storia del progetto: il riepilogo è in [`README.md`](README.md). Scritto il 18 ottobre 2026 da un lettore in sola lettura sul repository, poi ricontrollato da un secondo lettore che ha aperto le fonti e corretto nel testo gli errori trovati (circa 160 affermazioni, circa 134 giuste, 26 correzioni). Dove il testo dice «bozza» o «questo pezzo», intende questo capitolo.

Bozza per la storia del progetto. Copre il lato bot, gate e paper; le ricerche dei protocolli sono solo in sequenza
(sezione 5), il dettaglio lo racconta un'altra parte.

**Come leggere le fonti.** «ops NNNN» = file `ops/results/NNNN-*.md` (risposta della macchina a una richiesta). «diario»
= `docs/andremo_live.md` (le righe del mese vanno dalla 2321 alla fine, 4101). «capito» = `docs/capito.md`, sezione del
giorno. Un hash di 8 caratteri è un commit del branch principale `claude/brave-albattani-1b12fv`. Le ore sono UTC salvo
dove è scritto «ora italiana» (in ottobre l'ora italiana è UTC+2). «Calcolo mio» = conto fatto da me sui numeri citati,
non stampato da nessuno strumento. «Stima» = numero non misurato.

**Glossario minimo delle sigle che tornano spesso** (codici del backlog `docs/backlog.md` e dell'archivio
`docs/backlog_archivio.md`):
* **gate** = il filtro automatico (`scripts/optimize.py` + `scripts/discover_strategies.py`, timer ogni 3 ore) che
  genera strategie a caso o per mutazione, le prova sulla storia e scrive nel registro (`strategy_registry/validated`)
  le coppie moneta|strategia che il bot può operare. **Validata** = coppia con almeno 3 passaggi.
* **paper** = il bot che opera in `DRY_RUN` (denaro finto, 1000 USDT di partenza dal 16 settembre).
* **motore** = il backtest del gate (`backtesting/engine.py`), usato anche per rigiocare gli stessi segnali del paper.
* **R** = risultato del trade in multipli del rischio iniziale (−1 R = stop pieno).
* **fuori campione (H5)** = i trade del motore e del paper nati DOPO la data di validazione di ogni coppia: dice se la
  scelta del gate regge sui giorni che non ha visto. Regola di lettura scritta il 30 settembre: «selezione» (motore ≤ 0
  con almeno 80 segnali → la prossima modifica va nel gate) ed «esecuzione» (stessi segnali, paper sotto il motore oltre
  il margine → la prossima modifica va su ingressi e uscite del bot). Letture ufficiali il 7 e il 14 ottobre.
* **declassate** = validate bocciate per due giri completi di fila, operate a un quarto della size.
* **esplorative** = quasi-passaggi del gate operati a un quarto della size per vedere se rendono come le validate.
* **R1** = il gate rigiocato nel passato; **R2** = taratura di R1; **G7** = il gate sui prezzi mescolati; **T2** = la
  curva del vantaggio del segnale; **C5** = costi veri di Binance; **D8** = i dati che non si raccoglievano; **J2** = il
  backlog in dashboard; **K10** = la soglia del win rate abbassata dal supervisore; **H1** = il voto t delle coppie;
  **H3/H4** = stop giornaliero e freno di serie; **I6** = affollamento nello stesso verso; **G8** = porta per direzione e
  mercato nel gate. Il loro testo è nel backlog e nell'archivio.

---

## 1. Cronologia giorno per giorno

### Giovedì 1 ottobre — pulizia, misure nuove, report giornaliero

**Il punto di partenza.** Controllo delle 08:15 ora italiana: 204 trade (196 delle validate + 8 esplorativi), 57% vinti,
−70,82 USDT, equity 929,18, `DRY_RUN` True; BTC dal primo giorno +11,2% contro −7,1% nostro (ops 0386; ops 0389 scrive +11,37% e il diario +11,4%: le due cifre
non coincidono). Il giro completo del gate è durato 2 h 58, a 2 minuti dalle 3 ore del timer
(41.419 valutazioni, 356 passate, 0,86%; ops 0391). Spazio del registro per circa 1.380 coppie (ops 0391). In R dal 27
settembre (cioè dopo la correzione del difetto della sessione oraria, 27 set 19:40 UTC): +0,042 R netti a trade su 61,
+0,118 lordi, costi 0,076 (ops 0388). Fuori campione in anteprima: motore +0,06 R su 89 segnali ±0,18 (ops 0387).

**Decisioni e lavori del giorno** (tutti con il sì del proprietario, parole nel diario):
* «pulisci il registro»: il backlog perde 12 voci fatte, 10 «non servono» e 4 chiuse senza lavoro (diario, «1
  ottobre: pulizia del backlog»). Nel primo pomeriggio il backlog viene rifatto con solo le voci aperte (6 gruppi, 21
  voci); il vecchio file diventa `docs/backlog_archivio.md` (diario, «1 ottobre, primo pomeriggio»).
* «correggi il report»: il report dei rifiutati confronta rifiutati e aperti nello stesso periodo (J6, d7b57c8a).
* «fai tutte quelle 15 aperte»: lato gate di tre voci, solo descrittivo (346f1a97): nessun verdetto del gate cambia.
* «procedi k10-k11 e la scritta fuorviante»: conteggio della soglia del win rate, storia delle esplorative, scritta della
  panchina (537a0b91). «fai i4bis»: data in cui scatta l'ipotesi «scala stretta» (8d241733).
* Il proprietario riempie il segreto `ANTHROPIC_MODEL` su GitHub: voce D7 chiusa (diario, «primo pomeriggio»).
* «vai con R1»: regola del gate rigiocato nel passato scritta PRIMA dei numeri (6882c972) e strumento
  `scripts/replay_gate.py` (faa46632). Domanda: il gate sceglie strategie con un vantaggio vero o soprattutto fortuna?
* Domanda del proprietario su stop giornaliero e freno di serie: rigiocati, restano parcheggiati (f131fa08; sezione 3).
* Richiesta in 5 punti: la **stella polare** entra in `CLAUDE.md` (d416ad97: «ogni giorno un passo più vicino, anche in
  ciò che abbiamo CAPITO»; «una funzione senza misura del contributo non è utile»); il backlog in dashboard senza copie
  a mano (J2, 0f504532); «le funzioni servono?» (0527e830, e6002bb1); il **report giornaliero** a nove sezioni fisse,
  prima scheda della dashboard, pubblicato dopo ogni giro del gate (6576524a); i **dati che non raccoglievamo** (D8, 12
  campi nuovi, solo raccolta; 5e7522bc).
* **Riavvio del bot** alle 15:24 UTC (ops 0414): codice ebe4d0d, equity riconciliata 921,96 (ops 0416).
* Sera: il primo lancio di R1 (13:49 ora italiana, ops 0407) ha aspettato 4 ore senza trovare una pausa, perché ogni giro del gate dura circa 3
  ore e il timer scatta ogni 3 ore; insieme non stanno in memoria (10 GB occupati su 15 col gate in corso; ops
  0410-0413). Il proprietario: «procedi con R1 al posto di un giro del gate al giorno» (fecbf758): il giro delle 12:00 UTC
  esce subito finché esiste `data/replay_gate/attivo`.

### Venerdì 2 ottobre — nessun vantaggio all'ingresso; AI e varianti dai referti spente

* Mattina, il proprietario: «fai la misura del punto 1… la mia idea alla fine è operare più come un quant». **T2, la
  curva del vantaggio del segnale**, regola scritta prima (b5087a3a), primo esito alle ~06:20 UTC: **nessun vantaggio
  misurabile** a 1, 4, 12 e 24 ore (ops 0437; eee06fc5). Per la regola, il lavoro sui take profit si ferma (T1
  congelata).
* **I costi contro Binance** (richiesta del proprietario): il modello conta 0,08% di commissioni andata e ritorno
  contro lo 0,10% di Binance da taker; il funding è trattato come «ogni 8 ore» anche dove scade ogni 4 o ogni ora; lo stop
  è senza scivolamento (diario, «2 ottobre, mattina: i costi per trade»; backlog C5). Il proprietario: «sì C5, e limita R1
  alle 71 monete» — C5 approvata ma **da fare dopo le letture del 14 ottobre** (5d66c097). C5 a oggi non è stata fatta
  (sezione 2.3).
* Controllo del mattino: un giro del gate di 3 h 04 (anomalia GATE_SFORA); 224 trade, −77,22 USDT, equity 922,78 (ops
  0421); in R dal 27 set −0,065 su 81 (ops 0420). Fuori campione in anteprima: motore −0,03 R su 106 segnali ±0,21, la
  lettura stampata dice già «la prossima modifica va nel gate» (ops 0429). Le strategie nate da idee AI hanno 0 validate
  su 103 nel registro (ops 0423).
* 14:45 ora italiana: prima finestra di R1, il gate salta il giro delle 12 UTC (ops 0440); R1: 0 passate su 14.150
  candidate giudicate (ops 0439). Punto di verifica fissato prima dei numeri: dopo 5 date complete, se le promosse sono
  meno di 10 il piano cambia (diario, «2 ottobre, 14:45»).
* 20:47 ora italiana: **10 long aperti in 20 secondi** (ops 0442-0443). Non è un guasto: in parità il bot apre tutti i
  segnali validi, il tetto di 5 posizioni è spento e il tetto per direzione (3% di rischio) con le puntate ridotte ne
  ammetteva molte (diario, «2 ottobre, sera»). Fatto: la sezione «AFFOLLAMENTO» nel report `trades`, solo misura.
* Sera, il proprietario («se pensi che non diano valore»): **spente le idee dell'AI con l'autopsia**
  (`AI_HYPOTHESES_ENABLED=false`: 0 validate su 103 spec AI, ops 0423) e **le varianti dai referti**
  (`DISCOVERY_VARIANTI_REFERTI=false`: 0 promosse da quando esistono, ops 0391/0423) (57382099).
* Un secondo riavvio del bot avviene il 2 ottobre senza richiesta ops: il pid cambia da 1975598 a 2005927 (ops 0424,
  0443; «riavvii 1» in ops 0460). Ora e causa non sono nei file (il diario del 3 ott stima ~08:20 ora italiana).

### Sabato 3 ottobre — prima lettura a data fissa: declassate, non si decide

* **Lettura ufficiale del 3 ottobre (declassate contro attive): NON SI DECIDE** — −0,131 R su 70 contro +0,127 R su 33,
  differenza −0,258, margine ±0,458 (ops 0445; e3df041d).
* 246 trade, −73,68 USDT, equity 929,04 (ops 0446); il 2 ottobre +3,48 USDT (ops 0460). Stop: 51 su 107 «sbagliati
  dall'inizio» (mai a favore di 0,25 R; ops 0451).
* R1: 2 date su 26, 0 passate su 16.000 candidate (ops 0458). Sospetto, non dimostrato: il gate vero passa lo 0,19% di un
  misto di strategie (44 su 22.632, ops 0448/0450). Sì del proprietario a **R2** (le stesse candidate giudicate dal gate
  di produzione, regola scritta prima: ff45bcf0).
* Trovato un difetto di etichetta: le «ondate» erano in ora UTC con scritto «italiana» (`trade_stats.py`, corretto in
  e3df041d).

### Domenica 4 ottobre — R2 dice che lo zero è vero; R1 fermato; prima settimana in utile

* Mattina: 264 trade, 57% vinti, −62,59 USDT (lordo −24,56, costi 38,03), equity 937,41 (ops 0466). Il 3 ottobre è stata
  la giornata migliore del paper: 16 trade delle validate, 15 vinti, +0,869 R a trade, +18,85 USDT sul conto (ops 0479).
  Fuori campione: +0,006 R su 156 segnali ±0,17 (ops 0474): per un giorno buono la regola del 7 non sarebbe scattata.
* Il proprietario: «sì G7, procedi» — **G7, il gate sui prezzi mescolati**, regola scritta prima (cf208a7a).
* **Referto settimanale** (ops 0481-0482): settimana 28 set-4 ott **+14,09 USDT, la prima in utile** (ops 0474; il 4 ott contato solo fino alle 08:20 ora
  italiana).
* 10:40 ora italiana, sì del proprietario: **USELESS e SUI trade per trade** (ops 0483): 14 trade, tutti short, tutti fra
  il 21 e il 27 settembre, che il motore non riproduce. È la firma del difetto della sessione oraria corretto il 27
  settembre (la feature `session` leggeva l'ora del processo). Su 18 coppie rigirate i trade non riprodotti sono 20,
  tutti di prima della correzione, e fanno −33,57 USDT, circa metà della perdita del paper di allora (−62,59).
* 13:55 ora italiana: **R2: 0 passate su 3.600** (ops 0485): lo zero di R1 è vero. **G7 non fa nessuna prova** per un
  difetto (sezione 6); corretto (0dc9e382).
* 15:50 ora italiana, il proprietario sceglie l'opzione (c): «fermala dopo la prova di domani» — **R1 fermato** dopo la
  prova sul prezzo casuale (69f686dc). Lo stesso giorno chiede di **non usare sigle** nelle risposte (b0e634b1).
* Pomeriggio: «da +18 a −10». Il 4 ottobre a metà pomeriggio −10,14 USDT su 17 trade (ops 0486-0488): 7 stop, di cui 5
  «a favore ma sotto il primo gradino». Lettura del diario: le vincite sono piccole (massimo a favore mediano 0,84 R
  contro un primo incasso a 1,5-2 R), gli stop interi; senza vantaggio all'ingresso il segno del giorno lo decide il
  mercato.
* 16:30 ora italiana, domanda del proprietario «abbassare il primo incasso a 0,8R?»: no prima delle letture del 7-14
  ottobre; aggiunta solo una colonna di misura 0,8/1,6/2,4 nel report `mfe` (6edf239f).

### Lunedì 5 ottobre — il gate sui prezzi mescolati

* Mattina: 291 trade, −76,08 USDT (lordo −33,61, costi 42,47), equity 923,92 (ops 0490). Giro completo della notte 3 h
  22 (ops 0501). R1 fermo a 8 date su 26: 6 promosse, 45 trade a −0,22 R contro −0,14 R delle bocciate, non decide (ops
  0502).
* **G7 fatta** (13:13-13:48 ora italiana, ops 0505-0506): sulle candele vere 8 passate su 7.200 (0,11%), sulle stesse candele
  mescolate 16 su 7.200 (0,22%). Per la regola: NON SI SA (meno di 10 passate sul vero). Il file «attivo» di R1 è tolto,
  il gate torna a 8 giri al giorno (ops 0507).
* Proposta del giorno: **P0, il protocollo di ricerca per moneta** (versione 4.2, consegnata al proprietario quella
  mattina; diario, «Controllo del 5 ottobre»).

### Martedì 6 ottobre — parte il protocollo di ricerca

* Mattina: 309 trade, −77,42 USDT, equity 922,58 (ops 0509); giro completo 3 h 28 (ops 0520); il registro cresce a 257
  validate su 82 monete, spinto dall'«intorno» dei quasi-passaggi (204 figlie in una notte; ops 0511; capito 6 ott).
* Sera, il proprietario: «sì alla 4.3, sì ai branch, vai col Passo 0». Fatto il Passo 0 del protocollo (613d552d,
  4fa1ea58). Dal lato del bot il Passo 0 scrive tre fatti che contano per la storia del gate: lo stop del paper scatta sul
  percorso del prezzo medio bid/ask allargato al mark, mentre il gate usa le ombre delle candele; una strategia del
  protocollo non ha una porta d'ingresso nel bot senza passare il gate; il modello dei costi del bot è più leggero del
  reale (capito, «6 ottobre, sera», con i riferimenti al codice).

### Mercoledì 7 ottobre — prima lettura ufficiale: «la prossima modifica va nel gate»

* **Lettura ufficiale del fuori campione** (ops 0532): SELEZIONE → «la prossima modifica va nel gate» (motore dopo la
  validazione −0,05 R su 230 segnali, ±0,14 per giornata); ESECUZIONE → non si decide (stessi 200 segnali: paper −0,09,
  motore −0,04, differenza +0,05 ±0,07). Seconda lettura il 14.
* 345 trade, −88,03 USDT, equity 912,77; **13 posizioni aperte** con il 2,05% a rischio (ops 0524, 0535). Spazio del
  registro sceso a ~603 coppie (ops 0526).
* Ricerca: lista delle 20 monete confermata («confermo la lista, apri tu in autonomia la sessione BTC…»), tre campagne
  della prova di processo, rapporto (sezione 5). Il proprietario chiede di **non parlare più di costi in dollari**
  (d4b83707).
* Incidente: i test di GitHub rossi dalle 07:38 ora italiana (sezione 6).

### Giovedì 8 ottobre — più long che short in un mercato che scende

* Mattina: 377 trade, −98,04 USDT, equity 902,30, massimo 15 posizioni insieme (ops 0539). Il giro della notte ha fatto
  81.788 valutazioni in 4 h 47, quasi il doppio del giro prima (ops 0541). Spazio del registro ~496 (ops 0541).
* Il proprietario chiede: «con un mercato in discesa apriamo più long che short?». Sì: il 7 ottobre 31 long e 9 short
  (ops 0551); la casella «long mentre BTC scende» è la peggiore (79 trade dal 27 set, −0,229 R; ops 0538). Nasce la voce
  **G8** (porta nel gate per direzione e mercato), da fare dopo la lettura del 14 se il proprietario dice sì (backlog G8).
* Ricerca: versione 4.4 approvata (05:08 UTC), tre campagne rifatte, primo candidato (BTC); regola Opus 5.5 con ultracode
  per ogni sessione (6cc8b288; sezione 5).

### Venerdì 9 ottobre — la ricerca per moneta va su tutte e 20 le monete

* Mattina: 417 trade nel periodo del paper, −111,27 USDT (ops 0562), equity 890,11 (ops 0554). Il registro si libera a
  ondate (spazio da ~496 a ~537; capito 9 ott). Letture di Firebase in crescita: 14.521 in 24 ore, 10.793 dai segnali
  rifiutati (ops 0557).
* Ricerca: prova con strategie finte («l'esame regge»), versione 4.5 approvata alle 12:06 UTC, 17 campagne in un giorno,
  3 candidati per il vault; regola «candidato solo con R medio dopo i costi positivo» per tutti (sezione 5).
* Incidente: test di GitHub rossi a ogni push dall'8 ottobre, corretti (89f1d376; sezione 6).

### Sabato 10 ottobre — campagna di gruppo; «domani niente report»

* Mattina: 440 trade, −109,41 USDT (ops 0577), equity 890,58; il 9 ottobre +1,28 USDT, +0,171 R a trade (ops 0581).
  Fuori campione −0,05 R su 351 ±0,11 (ops 0577).
* 07:40 ora italiana: «sì alla campagna di gruppo, no a rifare Bitcoin». 08:35: «devo uscire, il testo è approvato appena
  hai finito, parti con l'esecuzione».
* 21:12 ora italiana: «fammi sapere appena finisce e domani mattina non eseguire il report giornaliero». Spento solo il
  controllo giornaliero (diario, «10 ottobre, 21:12»): errore, si vede il giorno dopo.

### Domenica 11 ottobre — report del mattino fermi; vault aperto, 0 su 3

* 05:45 ora italiana parte lo stesso il **referto settimanale** (ops 0583-0595): settimana 5-11 ottobre **−41,33 USDT**
  (ops 0590; l'11 contato solo fino alle 06:00 ora italiana); totale 458 trade, −109,19 USDT, equity 891,26 (ops 0584); spazio del registro ~325 coppie, sotto
  l'allarme dei 400 (ops 0586); giro del gate 4 h 18 (ops 0586, 0593).
* 07:35 ora italiana, il proprietario: **«ferma del tutto i report della mattina fino a nuovo ordine, anche ieri ti avevo
  scritto di non farlo oggi ma lo hai eseguito lo stesso»**. Spente le due routine del mattino; regola scritta in
  `CLAUDE.md` (18b3f39a). Da quel giorno nessun controllo giornaliero automatico.
* Ricerca: la campagna di gruppo consegna «nessuna strategia valida»; sessioni di gruppo archiviate; alle 17:29 UTC il
  proprietario scrive «APRI IL VAULT»; il vault boccia tutti e tre i candidati (sezione 5).

### Lunedì 12 ottobre — chiusura della ricerca 4.5; analisi dei trade; letture esterne

* 18:05 ora italiana: «Sì, salta e passa alla conclusione» (salta il trasferimento sulle altre monete). Dalla sessione di
  quel giorno il modello è Fable 5.1, scelta del proprietario (diario, «12 ottobre, 18:05»; i commit portano il trailer
  Fable 5.1 dal 6a0806ba del 12 ott 16:04 UTC al c3d0e6f3 del 14 ott 14:18 UTC, poi di nuovo Opus 5.5 dal f6f79c1a del
  16 ott 05:29 UTC).
* 21:00 ora italiana: Passo 7, la ricerca 4.5 è chiusa con zero strategie su 630 varianti (sezione 5).
* 22:00 ora italiana: **analisi dei trade del paper dal 16 settembre** (`docs/analisi_trade_16set_12ott.md`, chiesta
  dal proprietario; sezione 3.10) e **letture di tre progetti esterni** (`docs/letture_esterne/`; sezione 3.11).

### Martedì 13 ottobre — gate fermo, ingressi a limite nel paper

* 09:13 ora italiana: «Procedi» alle regole della **prova degli ordini limite sulla storia** (motore della ricerca, nove
  strategie delle campagne). Esito alle 10:45: **«conviene poco»** (sezione 3.12).
* 19:20 ora italiana il proprietario chiede cosa fare del gate. Risposta: fermare la ricerca automatica, cambiare terreno
  (giorni invece di ore, il paniere invece della moneta, poche idee con fonte), tenere il vault, usare il paper come esame
  finale. 19:50: **«ok procedi con tutto»** (diario, «13 ottobre, 20:10»). In ordine:
  1. **Ricerca automatica del gate FERMA** (4c315e80, pushato alle 17:54 UTC, prima del giro delle 18:00 UTC). Il giro
     già partito alle 15:34 UTC (ops 0614) è andato avanti fino in fondo: alle 17:59 UTC ha ancora validato
     XPINUSDT|gen_c5e06de1 (ops 0613) ed è finito alle 18:40 UTC (34.048 valutazioni, 113 passate, 0,33%; `docs/state.md`,
     autopsia). È l'ultimo giro del gate.
  2. **Ingressi a ordine limite nel paper** (6d50adfa, 18:09 UTC) e **riavvio del bot** alle 18:10 UTC (ops 0615): nuovo
     codice d5939a7 (che contiene 6d50adfa), 8 posizioni ricaricate, equity riconciliata **864,94** (realizzato −135,06;
     ops 0617).
  3. Bozza della seconda edizione del protocollo (7262d0df), approvata alle 21:34 ora italiana: «Approvo la seconda
     edizione, 3 idee e anche più varianti, dal 16 gennaio 2023 va bene».
* Il 13 ottobre è la **giornata peggiore del paper**: 51 trade (ops 0622), −25,25 USDT (ops 0619), con due ondate di long
  nella notte (02:17 ora italiana, 8 aperture, −12,39; 03:03, 9 aperture, +9,98; ops 0620).

### Mercoledì 14 ottobre — campagna del paniere

* 07:00 ora italiana: «procedi» allo STOP del Passo 0 della seconda edizione. 11:05: scelta (a) sugli strumenti. La
  campagna del paniere consegna alle 16:12: nessuna strategia valida (sezione 5).
* Paper: −13,76 USDT nella giornata (ops 0619). Nessun controllo del paper in quel giorno (report del mattino fermi).

### Giovedì 15 ottobre — giornata senza lavoro scritto

* Nessuna voce del diario e nessun commit di lavoro (solo quelli automatici del battito ops e dello stato) fra il 14 ottobre 14:18 UTC (c3d0e6f3) e il 16 ottobre 05:29 UTC (f6f79c1a)
  (`git log`). Il paper intanto fa −23,95 USDT, secondo giorno peggiore (ops 0619).

### Venerdì 16 ottobre — seconda lettura ufficiale; il proprietario propone il protocollo su BTC

* 07:45 ora italiana, il proprietario: «oggi è il 14, che era l'altra data del controllo». **Seconda lettura ufficiale**
  fatta a mano coi dati fino alle 05:40 UTC (ops 0619-0621; 3d2d775a): selezione **confermata**, esecuzione **per la
  prima volta oltre il margine** (sezione 3.13). Il semaforo rosso «gate in ritardo» (ultimo giro 2 g 11 h prima) è
  atteso: il gate è fermo (ops 0621).
* Mattina: archiviate su richiesta le 22 sessioni di campagna finite. Il proprietario carica il «Protocollo di ricerca
  strategie su BTC, versione 5.1» e chiarisce l'obiettivo: **rifare il gate per avere prima di tutto un METODO efficace,
  valido e senza buchi di processo, provato su BTC, e poi replicarlo sulle altre monete** (diario, «16 ottobre,
  mattina»).
* 19:26 UTC: «ok approvato, procedi con il Passo 0» (protocollo 3). Il Passo 0 scrive un fatto importante per il bot:
  **il bot oggi non sa eseguire nessuna variante del catalogo del protocollo** (`research/config/bot_3.md`, punto 3;
  backlog P7).

### Sabato 17 ottobre — BTC51: un candidato, bocciato dal vault; protocollo 4 approvato

* Giornata di sola ricerca (sezione 5), con molte decisioni del proprietario: «ok sì a tutto, procedi con le correzioni»
  (08:11 ora italiana); **«Sì apri la sessione.. lascia il paper acceso per ora»** (09:15); «ok correggi» (09:38); «sì
  procedi con la validazione» (15:39); «procedi con la consegna»; «APRI IL VAULT 3»; «ok sì, fai la prova sulle altre
  monete»; «ok sì, chiudi la campagna e scrivi le lezioni»; «ok sì, scrivi la bozza del prossimo protocollo»; «sì,
  approvato» (protocollo 4, 20:12 UTC); delega: «procedi in autonimia con gli altri passi» (CLAUDE.md la data alle 21:10
  UTC).
* Paper: nessuna lettura ops quel giorno. Dalla lettura del 18 (ops 0622): 27 trade il 17 ottobre.

### Domenica 18 ottobre — LINK6 chiusa; «dobbiamo continuare»

* Mattina: la ricerca su LINK si ferma a 33 varianti su 40 senza candidati e consegna alle 10:14 ora italiana (sezione 5).
* **~08:40 UTC, decisione del proprietario** (672663b8, `docs/backlog.md` P11, `CLAUDE.md`): «la domanda non è se vuoi
  continuare e dobbiamo continuare fino a quando non trovi delle strategie valide... se serve riscriviamo totalmente il
  gate non mi interessa (prima però voglio che tu storicizzi tutti i dati raccolti, quello che abbiamo imparato, cosa
  abbiamo cambiato, insomma tutto dall'inizio di questo progetto ad oggi)». Primo passo: la storia in `docs/storia/`.
* Ultima lettura del paper, chiesta per questa storia: ops 0622 e 0623 delle 09:03 UTC (sezione 4).

---

## 2. Le modifiche al bot, al gate e al paper

### 2.1 Tabella delle modifiche (codice in `bot/`, `scripts/`, `dashboard/`, `backtesting/`)

Elenco completo dei 32 commit del mese che toccano queste cartelle (`git log --full-history --no-merges`, filtrato dal 1
ottobre; attenzione: `git log --since=2026-10-01` senza l'ora ne perde tre, 346f1a97, d7b57c8a, edc3aaab, perché parte
dall'ora del momento in cui si lancia; senza `--full-history` si perde anche 27461905). Il codice
del bot vale solo dal riavvio successivo (1 ott 15:24 UTC, ops 0414; 13 ott 18:10 UTC, ops 0615); il codice del gate e
dei report vale dal giro o dal lancio successivo.

| Quando (UTC) | Commit | Cosa | Perché | Effetto misurato |
|---|---|---|---|---|
| 1 ott 05:56 | edc3aaab | Report `trades`: conti in R tagliati al 27 set, riga «paper contro il caso» (K8, K4); reset completo del paper (D5) | leggere i trade in R e accanto a un prezzo casuale con le stesse uscite | il paper sta sul caso: stop 46% contro 46%, vinti 54% contro 54% (ops 0401) |
| 1 ott 06:59 | d7b57c8a | Rifiutati confrontati con gli aperti dello stesso periodo (J6) | il verdetto «RITARARE» sui rifiutati per «posizione aperta» confrontava periodi diversi | 4 ott: rifiutati +0,01 R contro aperti −0,03 su 73, solo informazione (ops 0476) |
| 1 ott 08:56 | 346f1a97 | Gate: voto t nel nucleo del registro solo dalle 2 conferme (K2); scarto vero sull'holdout e autopsia per timeframe (K7); riga ORIGINI (D6-IPOTESI) | spazio del registro; dati giusti all'AI; sapere se le idee AI servono | su un registro finto −34 KB (−8%) nel nucleo (diario, «lato gate»); nessun verdetto del gate cambia |
| 1 ott 09:51 | 537a0b91 | Conteggio K10, storia delle esplorative senza perdere le validate (K11), scritta della panchina in parità | sapere quante validate esistono solo per la soglia abbassata | primo conteggio: 7 «allentate» +0,244 R su 11, 72 a ≥ 0,45 −0,054 su 50, 129 non classificabili (ops 0403) |
| 1 ott 10:02 | 8d241733 | I4bis: data in cui scatta l'ipotesi «scala stretta» per la corsia urgente | le strategie in paper da più di 7 giorni non entravano nella corsia urgente | non misurato |
| 1 ott 11:09 | f131fa08 | Stop giornaliero e freno di serie rigiocati (solo misura) | domanda del proprietario | sezione 3.2: restano parcheggiati |
| 1 ott 11:09 | 6cfa336b | Controllo: il rimando al backlog punta al gruppo 1 dell'indice nuovo (una riga di `bot/learning/controllo.py`) | il backlog con l'indice nuovo (8d241733) | — |
| 1 ott 11:28 | faa46632 | R1, `scripts/replay_gate.py` | il gate sceglie vantaggio o fortuna? | sezione 3.5 |
| 1 ott 13:55 | 0f504532 | J2: backlog in dashboard letto da `docs/backlog.md` | niente copie a mano | non misurato; dal 13 ott non si aggiorna più, dedotto dal codice (sezione 6, punto 24) |
| 1 ott 14:06-14:07 | 0527e830, e6002bb1 | «Le funzioni servono?» (`bot/learning/contributi.py`), regola dei verdetti scritta prima | la stella polare: una funzione senza misura va misurata o tolta | sezione 3.3: nessuna funzione oltre il margine fino al 18 ott, salvo il paper esplorativo il 4 ott su 10 trade (ops 0465), rientrato il 5 |
| 1 ott 14:14 | 6576524a | Report giornaliero a nove sezioni, prima scheda della dashboard | richiesta del proprietario | pubblicato (ops 0435); fermo dal 13 ott, dedotto dal codice (sezione 6, punto 24) |
| 1 ott 14:36 | 5e7522bc | D8: 12 dati nuovi sui trade (versione, promessa del gate, dopo l'uscita, motore sullo stesso segnale, percorso dello stop, qualità d'ingresso…), solo raccolta | i dati per capire perché si perde non c'erano | prova di parità `tests/test_dati_parita.py`; primo dato: ingresso +0,038 R peggio della chiusura del segnale, 155 s di ritardo (ops 0479) |
| 1 ott 15:25-16:13 | 5510577e, a8165a42, 7d9e4178 | Correzioni del report e della dashboard (Firestore non accetta liste annidate) | errori del primo giorno | — |
| 1 ott 17:54 | fecbf758 | R1 al posto del giro del gate delle 12 UTC (`bot/core/finestra_r1.py`) | gate e R1 non stavano insieme in memoria (ops 0412-0413) | il gate salta il giro (ops 0440) |
| 2 ott 05:12 | eafa9816 | Report `mfe`: i take profit delle posizioni aperte sono raggiungibili? | verifica T1 | difetto di lettura della cache trovato e corretto (sezione 6) |
| 2 ott 06:13 | fc4ec225 | T2, curva del vantaggio nel report `mfe` | la domanda «quant» del proprietario | sezione 3.4 |
| 2 ott 06:48 | 3a2d31f0 | Report: taglio del testo a fine parola | il fuori campione era troncato a 400 caratteri | — |
| 2 ott 07:33 | 5d66c097 | R1 sulle sole monete operate | R1 troppo lento (45,8 ore stimate, ops 0433) | piano da 5.200 a 1.872 unità (ops 0478) |
| 2 ott 19:13 | 57382099 | Sezione AFFOLLAMENTO; **spente idee AI con autopsia e varianti dai referti** | 0 validate su 103 spec AI (ops 0423), 0 promosse dalle varianti | chiamate AI del bot da 31 e 29 al giorno (1 e 2 ott, ops 0422, 0447) a nessuna (ops 0467, 0510, 0525); prova indiretta: «nuove AI 0, varianti 0» nella riga ORIGINI (ops 0492, 0511…) |
| 3 ott 06:42 | e3df041d | Ondate in ora italiana vera | etichetta sbagliata | — |
| 3 ott 07:03 | ff45bcf0 | R2 | lo zero di R1 era sospetto | sezione 3.5 |
| 4 ott 07:13 | cf208a7a | G7, `scripts/gate_sul_caso.py` | il gate distingue il rumore? | sezione 3.6 |
| 4 ott 11:57 | 0dc9e382 | Correzione di G7 (stato del modulo `__main__`) | G7 aveva fatto 0 prove | corretto, verificato il 5 ott (ops 0505-0506) |
| 4 ott 16:04 | 69f686dc | `R1_FERMATA` | decisione del proprietario | il gate torna a 8 giri dal 5 ott (ops 0507) |
| 4 ott 16:16 | 6edf239f | Colonna 0,8/1,6/2,4 solo misura (`SCALE_SOLO_MISURA`) | domanda del proprietario sul primo incasso | sezione 3.7 |
| 9 ott 12:12-12:16 | 89f1d376, 27461905 | Lettore del backlog: data con l'apostrofo (oltre al guardiano della ricerca) | il report perdeva la data | test di GitHub di nuovo verdi (run 863) |
| 13 ott 17:54 | **4c315e80** | **Interruttore della ricerca del gate** (`ops/gate_fermo`, `bot/core/gate_fermo.py`): optimize e discovery escono subito | 27.000 prove a giro, 0,29% passate (ops 0601); dopo la validazione il motore fa −0,06 R a trade su 396 segnali (ops 0600; il messaggio del commit e `ops/gate_fermo` scrivono «in paper» e citano ops 0601, 0604, che non hanno quel numero) | ultimo giro finito il 13 ott 18:40 UTC (`docs/state.md`); nessuna validazione dopo; anomalia rossa GATE_IN_RITARDO attesa (ops 0621) |
| 13 ott 18:09 | **6d50adfa** | **Ingressi a ordine limite virtuale nel paper** (`bot/execution/executor.py`, `bot/main.py`, `bot/config.py`) | la prova sulla storia diceva «conviene poco» ma il proprietario ha detto «procedi con tutto»; misurare nel paper per 3-4 settimane | **misura prevista non ancora fatta** (sezione 3.14) |

Fuori da queste cartelle, ma utili per la storia: 45e664d7 (7 ott, `pyyaml` fra le dipendenze e test della ricerca nella
CI), de2618ae ed e761cc05 (10 ott, avvio delle sessioni di ricerca compatibile con Python 3.13), 6b290f2e (11 ott, test di
GitHub solo sul branch principale), 18b3f39a (11 ott, report del mattino fermi in `CLAUDE.md`).

### 2.2 Come funzionano le due modifiche grandi del mese

**Il gate fermo (4c315e80).** Se esiste il file `ops/gate_fermo`, `scripts/optimize.py` e `scripts/discover_strategies.py`
escono prima di caricare qualunque dato (`bot/core/gate_fermo.py`). Per riaccendere: togliere il file con un commit, o
`GATE_FERMO_IGNORA=1` nell'ambiente del servizio. L'interruttore agisce all'**inizio** di un giro: il giro in corso al
momento del commit è finito normalmente (ops 0613, `docs/state.md`). Conseguenze: il registro resta com'era al 13 ottobre
18:40 UTC (249 coppie validate su 80 monete, `docs/state.md` e ops 0623); niente più declassamenti, promozioni, purghe,
esplorative nuove. Il bot continua a operare quelle 249 coppie perché legge la lista `validated` scritta dal gate
(`bot/learning/adaptation.py:284-288`).

**Gli ingressi a limite (6d50adfa).** In `DRY_RUN` la decisione mette un ordine limite virtuale al prezzo di chiusura della
candela di segnale, valido una candela; si riempie al suo prezzo se il prezzo lo attraversa (long sotto, short sopra),
altrimenti scade e il segnale conta come saltato. Lato d'ingresso: commissione maker 0,02% e scarto zero; uscite a mercato
come prima. Ordini in attesa in RTDB `/ordini_limite`, contatori e segnali saltati in `/paper/ordini_limite`, campi
`ingresso_tipo`, `limite_prezzo`, `attesa_ingresso_s` sul trade chiuso; `PAPER_INGRESSO_LIMITE=0` rimette l'ingresso a
mercato (messaggio del commit 6d50adfa). 13 test nuovi, suite del bot 2.305 passati (diario, «13 ottobre, 20:10»). La
dashboard non mostra gli ordini in attesa.

### 2.3 Cosa è acceso e cosa è spento oggi (18 ottobre)

**Acceso:**
* Il bot in paper, `DRY_RUN` True, online, 80 monete valutate, 3 posizioni aperte con lo 0,44% a rischio (ops 0623, 09:03
  UTC).
* Le 249 coppie validate dal vecchio gate, ferme al 13 ottobre (ops 0623).
* Gli ingressi a ordine limite (dal 13 ott 18:10 UTC; 6d50adfa, ops 0615). Che stiano funzionando come previsto non è
  stato letto da nessuna risposta ops (sezione 3.14).
* Il **freno globale da deriva**: size ×0,5 e leva ×0,71 su ogni trade finché il PF a 30 giorni resta sotto 0,6 volte il
  promesso (PF vissuto 0,709 contro 2,02; ops 0623). Per la voce K6 non si spegne di fatto più (uscita irraggiungibile).
* Declassate a un quarto della size, panchina dei pesi (17 strategie in panchina il 16 ott, ops 0621), keep del trailing per
  coppia, inclinazione per trend e sentimento, tetto per direzione 3%, paper esplorativo (25 coppie attive, ops 0622),
  selettore **solo in ombra** (non decide, ops 0617), leva fino a 2× per i pesi alti (XPINUSDT a 2,0×, ops 0623).
* Il supervisore (timer orario: ultimo giro 18 ott 09:01 UTC, «coppie validate 278», soglia del win rate a 0,3966; ops
  0623). Il canale ops (battito 18 ott 09:22 UTC in `ops/heartbeat.md`, commit 9f5a6c4d; risposte alle 09:03, commit 3c7fbdb8).
* Il controllo orario del bot (anomalie, semafori: ops 0621).

**Spento:**
* La **ricerca automatica del gate**, dal 13 ott 17:54 UTC (`ops/gate_fermo`).
* Le **idee AI con autopsia** e le **varianti dai referti**, dal 2 ott sera (57382099).
* L'**ombra AI** e il **filtro delle monete AI**, dal 30 settembre (decisione del proprietario del 30 set, riavvio ops 0384;
  conferma nel controllo del 1 ott, ops 0390, 0392).
* Il **freno di serie** (`STREAK_BRAKE_ENABLED=false`, dal 24 set: ops 0620 lo stampa ancora spento; gen_fa304106 è a 11
  perdite di fila in ops 0620 e 0622, a 10 nello `stato`, ops 0623).
* **R1** (fermato il 4-5 ott: 69f686dc, ops 0507).
* I **report del mattino** (controllo giornaliero con proposta dal backlog e referto settimanale), dall'11 ottobre «fino a
  nuovo ordine»; anche il controllo orario della campagna di gruppo (11 ott) e quello del paniere (14 ott) (`CLAUDE.md`;
  diario 11 e 14 ott).
* Il **report giornaliero in dashboard** e il **backlog in dashboard**: si pubblicano alla fine di un giro della discovery
  (`scripts/discover_strategies.py:4416-4424`), che col gate fermo esce prima (riga 3778). Quindi sono fermi dal 13 ottobre.
  **Dedotto dal codice, non verificato sulla macchina.**
* **C5** (costi veri di Binance): approvata il 2 ottobre per dopo il 14, mai fatta: il modello del bot conta ancora 0,08%
  andata e ritorno da taker (tranne il lato d'ingresso a limite, ora maker 0,02%) (backlog C5).

---

## 3. Le letture e le misure del mese

### 3.1 La soglia del win rate abbassata dal supervisore (K10)
* **Domanda:** le validate che esistono solo perché il supervisore ha abbassato la soglia da 0,45 a 0,3966 rendono peggio?
* **Numeri:** 1 ott, 7 «allentate» +0,244 R su 11 trade, 72 a ≥ 0,45 −0,054 R su 50, 129 senza win rate salvato −0,137 su
  57 (ops 0403). 16 ott: 207 coppie a ≥ 0,45 (−0,082 R su 230), 0 allentate, 42 senza win rate (ops 0620).
* **Conclusione:** nessun segno contro la soglia bassa, campione minimo. Mai decisa (backlog K10). Il 18 ottobre la
  sezione stampa 0 coppie in ogni gruppo e tutti i 629 trade fra le «non più validate» (ops 0622): non è un cambio del
  sistema ma un effetto del gate fermo (sezione 6, punto 25).

### 3.2 Stop giornaliero e freno di serie rigiocati (H3, H4)
* **Domanda (del proprietario):** avrebbero avuto senso?
* **Numeri del 1 ott:** sul paper ogni regola aiuta un poco (stop 2% +5,09 USDT, freno di serie del bot a 3 perdite
  +15,62, ops 0404); sul portafoglio del motore tolgono guadagni (stop 2% −17.456 su un PnL simulato, drawdown da 11,74% a
  17,02%; ops 0405). Il win rate dopo 4 perdite di fila non cambia (62,5% su 8 contro 68,2%, ops 0387).
* **Rilettura del 18 ott** (ops 0622): sul paper la regola che aiuta di più è ancora il freno a 3 perdite del bot, +11,55
  USDT su −173,00.
* **Conclusione:** sul paper aiutano solo perché meno esposizione a un sistema in perdita; sul gate tolgono i rimbalzi.
  Restano parcheggiate (backlog gruppo 6).

### 3.3 «Le funzioni servono?»
* **Domanda:** ogni funzione che modifica size, leva o scelta dei trade migliora l'esito? Regola scritta prima: meno di 10
  trade per gruppo «campione piccolo»; oltre 2 errori standard «contribuisce» o «va contro»; altrimenti «non si vede
  ancora» (`bot/learning/contributi.py`).
* **Prima lettura** (ops 0409, 1 ott): nessuna oltre il margine. **4 ott:** primo «contribuisce», il paper esplorativo (10
  trade, +0,385 R contro −0,065; ops 0465); il 5 ott torna «non si vede ancora» (11 trade, ops 0489).
* **Ultima lettura** (ops 0622, 18 ott), tutte «non si vede ancora»: freno globale −0,108 R toccati contro −0,173 altri
  (ma +47,38 USDT risparmiati a size piena); declassate −0,088 contro −0,136 (+64,49 USDT risparmiati; rischio effettivo
  0,11% contro 0,22%); pesi alti −0,167 contro −0,005; leva sopra 1× −0,151 contro −0,100; inclinazione −0,169 contro −0,063;
  ombra AI (spenta) −0,100 sui trade che avrebbe vetato contro +0,226 su quelli approvati (diff −0,326 ±0,360); esplorative
  −0,068 su 39 contro −0,113. Origine: idee AI 18 trade −0,173 R, casuali 592 −0,105, «intorno» 19 −0,314.
* **Conclusione:** nessuna funzione ha un contributo dimostrato; quelle che «imparano» dal paper (pesi alti, leva,
  inclinazione) hanno tutte il segno sbagliato (anche nell'analisi del 12 ott, sezione 2.5). Le uniche che risparmiano
  denaro sono quelle che riducono la size (freno, declassate): meno esposizione, non un vantaggio.

### 3.4 La curva del vantaggio del segnale (T2)
* **Domanda:** i segnali delle strategie hanno un vantaggio sul caso, e per quanto dura? Regola scritta prima (diario, «2
  ottobre, mattina»): movimento del prezzo dopo 1, 4, 12, 24 ore dall'ingresso, contro 20 ingressi a caso nelle 12 ore
  DOPO il segnale, intervallo al 95% con ricampionamento per giornate.
* **Primo esito** (ops 0437, 201 trade, 15 giornate): −0,080 · −0,001 · +0,026 · −0,068 mosse tipiche di 24 ore, tutte
  dentro il margine → **nessun vantaggio misurabile**; T1 (take profit adattivi) congelata.
* **Riletture:** 240 trade misurati (ops 0471), 256 (ops 0495), 293 (ops 0529), 337 (ops 0559): sempre nessun vantaggio. Il 12 ott,
  448 trade su 25 giornate: +0,008 · +0,066 · +0,119 · +0,028, tutte dentro il margine (ops 0597; analisi, sezione 2.1).
* **Conclusione:** gli ingressi non portano informazione sulla direzione; le stime a 4 e 12 ore sono positive ma piccole
  (un indizio, non un fatto). Limite dichiarato: su prezzi a caso la regola dice «nessun vantaggio» circa 3 volte su 4.

### 3.5 Il gate rigiocato nel passato (R1) e la sua taratura (R2)
* **Domanda:** il gate, rifatto con i soli dati fino a una data, sceglie candidate che rendono dopo? Regola scritta prima
  (6882c972): 26 date ogni 14 giorni, passate contro bocciate, almeno 80 trade delle passate.
* **Numeri:** prova piccola 0 passate su 14.150 (ops 0439); R2, le stesse 50 candidate del 17 set nel gate di produzione:
  **0 passate su 3.600** (ops 0485); fermato a 8 date su 26: 6 promosse su 25.631 giudizi, 45 trade a −0,22 R contro −0,14 R
  delle bocciate, differenza −0,08 ±0,31 (ops 0502; capito 5 ott).
* **Conclusione:** per la regola «non si sa» (meno di 80 trade). Ma lo zero di R2 dice che una candidata nuova a caso non
  passa quasi mai: **le validate nascono dalla ricerca ripetuta giro dopo giro** (mutazioni dei quasi-passaggi,
  rivalutazioni), dove il numero delle prove cresce senza essere contato (capito 4 ott).

### 3.6 Il gate sui prezzi mescolati (G7)
* **Domanda:** quante strategie passa il gate per puro caso, a 1 ora? Regola scritta prima: quota sul caso ≥ metà di quella
  vera → il gate passa soprattutto rumore; ≤ un quinto → filtra; meno di 10 passate sul vero → non si sa.
* **Numeri** (ops 0506): 100 candidate nuove su 72 monete; candele vere **8 su 7.200 (0,11%)**, stesse candele mescolate
  **16 su 7.200 (0,22%)**.
* **Conclusione:** per la regola NON SI SA. Osservato: sui prezzi senza nessun vantaggio possibile il gate ha promosso il
  doppio. Il 2,2% di passaggio della passata a 1 ora era composizione (spec già note), non bravura (capito 4 e 5 ott).

### 3.7 Il primo incasso più vicino (colonna 0,8/1,6/2,4)
* **Domanda (del proprietario, 4 ott):** abbassare il primo incasso a 0,8 R?
* **Numeri** (modello semplificato del report `mfe`, che conta i gradini raggiunti come incassati): 0,8/1,6/2,4 −0,20 R
  (ops 0495), −0,24 (ops 0529), −0,27 (ops 0559), contro 2/4/6 −0,85/−0,86.
* **Conclusione:** è la scala che perde meno, ma resta sotto zero; su un prezzo senza informazione nessuna scala crea un
  vantaggio (analisi del 12 ott, sezione 2.3). Nessun cambio.

### 3.8 Declassate contro attive
* **Regola** (del 3 ott, scritta il 30 set): «diverso» solo oltre il margine.
* **Numeri:** 3 ott −0,131 R su 70 contro +0,127 su 33, ±0,458 (ops 0445); 16 ott −0,098 su 283 contro −0,119 su 194, ±0,174
  (ops 0620); 18 ott −0,088 su 299 contro −0,124 su 234, +0,036 ±0,163 (ops 0622).
* **Conclusione:** NON SI DECIDE a ogni lettura; le coppie che il gate stesso boccia rendono quanto quelle che tiene.

### 3.9 Affollamento, trailing, stop e ingressi (referti settimanali del 4 e dell'11 ottobre)
* **Affollamento (I6):** il 3 ott la fascia «6 o più posizioni nello stesso verso» era l'unica positiva (+0,026 R su 11; ops
  0445); con più dati si gira: −0,162 R (12 ott, ops 0596), −0,193 su 70 (ops 0620), **−0,160 su 84** contro −0,092 della
  fascia 1-2 (ops 0622). Quattro ondate di 8-12 aperture in 5 minuti (ops 0622).
* **Trailing:** nella settimana al 4 ott 38 prematuri contro 36 protetti, nella settimana all'11 ott 41 contro 38 (ops
  0477, 0593); la regola del referto chiedeva di proporre un keep più largo: **proposto e sconsigliato**, 3 su 79 è dentro il
  caso. Totale al 16 ott: 120 prematuri contro 124 protetti su 244 (ops 0621).
* **Stop:** al 18 ott 309 stop su 707 uscite (44%), −588,72 USDT (ops 0623). Al 12 ott dei 221 stop 101 «mai andati a favore»
  e 119 «a favore ma sotto il primo gradino» (ops 0597).
* **Il paper entra dove entra il gate?** 33 su 51 (65%) al 4 ott (ops 0481), 58 su 72 (81%) all'11 ott (ops 0594), 102 su 133
  con scarto 0 minuti al 12 ott (ops 0608).

### 3.10 L'analisi dei trade dal 16 settembre al 12 ottobre (`docs/analisi_trade_16set_12ott.md`)
* **Domanda (del proprietario):** perché i trade falliscono, e questi dati possono creare strategie o migliorare il gate?
  Fonti: 17 letture ops del 12 ott (0596-0612), quattro in timeout a 900 s.
* **Numeri:** 508 trade chiusi su 91 monete e 159 strategie (3 per strategia); R prima dei costi −0,015 (dal 27 set +0,003),
  costi 0,095 R, dopo i costi −0,110 R (ops 0596); lordo −58,62 USDT, costi 67,59, netto −126,21 (ops 0607); il paper ha la
  firma del caso (stop 44% contro 46%, massimo toccato 0,80 R contro 0,81, vinti 55% contro 54%; ops 0596); sugli stessi
  segnali il bot fa come il motore (+0,03 ±0,05, ops 0600); il motore dopo la validazione −0,06 R su 396 segnali (ops 0600);
  il gate a 26.986 valutazioni passa lo 0,29%, con t massimo 1,92 contro i 3,96 che servirebbero per lasciarne passare una
  sola per caso (ops 0601); il selettore addestrato su 150.015 trade non batte «apri tutto» in 0 finestre su 3 (ops 0604).
* **Conclusione:** i trade falliscono perché gli ingressi non sanno la direzione e i costi fanno il resto; non è
  l'esecuzione; è la scelta del gate. I dati del paper **non servono a creare strategie** (regola: il paper non è un
  insieme di addestramento; e aritmetica: 3 trade a strategia), servono come diagnosi e danno tre ipotesi da provare sulla
  storia: costo per trade con ordini limite, tetto di esposizione per verso, orizzonte 4-12 ore. Per il gate chiedono
  cambiamenti strutturali: confronto con entrate casuali, correzione per i tentativi, fuori campione vero, costi per moneta,
  un solo regime, niente figlie dai quasi-passaggi (sezione 4 del file).

### 3.11 Le letture di tre progetti esterni (12 ottobre, `docs/letture_esterne/`)
* **Domanda (del proprietario):** c'è là fuori un approccio che risolve il nostro problema?
* **Esito:** freqtrade (GPLv3, 55.307 stelle), Vibe-Trading (MIT, Università di Hong Kong) e NOFX (AGPL) **non portano
  nessuna prova di rendimento**; due lo dicono da soli (freqtrade: le strategie di esempio «non saranno redditizie»; il loro
  esempio di report ha p-value 0,48) (`docs/letture_esterne/README.md`).
* **Da prendere:** la regola di riempimento degli ordini limite con contabilità maker/taker e tempo massimo, lo slippage
  stimato sul libro, il test «taglia i dati e rifai» contro il lookahead, la checklist delle assunzioni del backtest, tre
  protezioni semplici (freqtrade); scadenza dell'evidenza e commissione di pareggio (Vibe-Trading); tre ipotesi d'uscita da
  provare nel gate (NOFX). **Da non prendere:** hyperopt e LLM come fonte di vantaggio.

### 3.12 La prova degli ordini limite sulla storia (13 ottobre, `research/esperimenti/ordini_limite/risultati.md`)
* **Domanda:** entrare con un ordine limite alla chiusura della candela di segnale abbassa abbastanza i costi? Regole
  scritte prima e approvate («Procedi», 09:13 ora italiana); soglia E2: risparmio ≥ 0,04 R a trade.
* **Numeri** (nove strategie delle campagne, 2020-2023, mediane; sezioni 2.1 e 7 del file): l'ordine si esegue nel 98% dei
  segnali; costo da **0,062 a 0,039 R** (−0,0225 R, un terzo); lordo −0,007 R; i trade saltati sono il 2,4% (67 su 2.747) ma
  sono i migliori (+0,68 R contro +0,06); anche le entrate casuali a limite risparmiano +0,016 R; uscite a limite: costo
  0,022 R ma lordo da 0,086 a 0,048 R.
* **Conclusione:** **«conviene poco»**: i costi scendono, un vantaggio non nasce. Il file proponeva, se si voleva provarla,
  una misura nel paper per qualche settimana prima di toccare il gate. È ciò che è stato fatto la sera stessa (6d50adfa).
  L'analisi del 12 ottobre aveva stimato un risparmio fino a circa la metà (da 0,095 a 0,04-0,05 R, stima): la prova ha
  detto un terzo.

### 3.13 La seconda lettura ufficiale (quella del 14 ottobre, fatta il 16; ops 0619-0621)
* **Selezione: «la prossima modifica va nel gate», CONFERMATA.** Motore dopo la validazione −0,03 R su 566 segnali, ±0,09 per
  giornata (il 7 ott −0,05 su 230). Le coppie ancora validate fanno +0,001 R su 329 segnali, quelle uscite dal registro
  trascinano giù (ops 0619).
* **Esecuzione: «è esecuzione», per la prima volta.** Stessi segnali, 451 trade: motore −0,06 R, paper −0,12 R, differenza
  +0,06 R, margine ±0,05 per giornata (ops 0619). Avvertenze del diario: supera il margine di poco, nessuna lettura
  successiva lo conferma, e circa 80 dei 481 trade del paper sono entrati con l'ordine limite, che il motore non simula
  (stima del diario, non contata). In più (ops 0619): i 113 segnali del motore non presi dal paper fanno +0,07 R contro −0,06
  dei presi; 11 trade del paper hanno girato con scala, break-even o keep diversi da quelli con cui il motore li rigira oggi
  (senza di loro il paper fa −0,11).
* **H1 (il voto t separa le coppie buone?): chiusa.** t dell'ultimo esame ≥ 1,5: −0,11 R su 142; sotto: −0,01 su 346;
  differenza −0,09 ±0,21 (ops 0619): anche nel caso migliore non separa oltre 0,25 R.
* **Conclusione del diario:** il paper perde −0,12 R a trade, circa metà per la selezione (il motore stesso fa −0,06 sugli
  stessi segnali) e metà per l'esecuzione (−0,06 in più). Si sbloccavano G8 e C5, ma il gate è fermo e nessuna delle due è
  stata fatta (backlog G8, C5).

### 3.14 La misura degli ordini limite nel paper (dal 13 ottobre) — NON ANCORA FATTA
* **Cosa era previsto:** «fra 3-4 settimane si misurano tasso di esecuzione, costo per trade e R dei segnali saltati»
  (diario, «13 ottobre, 20:10»), leggendo `/paper/ordini_limite` e i trade con `ingresso_tipo`.
* **Stato:** nessuno script di report legge quei campi (`grep` in `scripts/`: solo `bot/main.py`, `bot/config.py`,
  `bot/core/models.py`, `bot/execution/executor.py` li nominano) e nessuna risposta ops li riporta. Le righe di log `[limite]`
  esistono nel codice (`bot/main.py:1398-1420`) ma i log letti dopo il riavvio arrivano solo alle 18:24 UTC del 13 ottobre
  (ops 0618) e non ne contengono.
* **Un indizio, non la misura** (calcolo mio, campione piccolo): fra la lettura del 16 ott 05:40 (ops 0620) e quella del 18
  ott 09:03 (ops 0622) sono entrati nel conto in R 56 trade nuovi, con R netto −4,56 in tutto (−0,081 a trade), lordo −0,67
  (−0,012 a trade) e costi stimati 3,89 R (0,069 R a trade, contro 0,087-0,089 della media di tutto il paper). Costo più basso,
  coerente con l'ingresso maker, ma su 56 trade e coi costi del modello, non dei riempimenti.

---

## 4. I numeri del paper

### 4.1 L'andamento nel mese

Il paper è partito il 16 settembre con 1000 USDT. Il PnL è realizzato (trade chiusi), esplorativi compresi; l'equity del
bot è base + realizzato (ops 0617, 0623).

| Quando | Trade | Vinti | PnL realizzato (USDT) | Lordo / costi | Equity | R netto a trade (dal 27 set salvo dove detto) | Fonte |
|---|---|---|---|---|---|---|---|
| 1 ott, 08:15 ora it. | 204 (196 + 8 esplorativi) | 57% | −70,82 | −39,75 / — | 929,18 | +0,042 su 61 | ops 0386-0389 |
| 2 ott | 224 | 55% | −77,22 | — | 922,78 | −0,065 su 81 | ops 0420-0421 |
| 3 ott | 246 | 56% | −73,68 | −37,93 / 35,76 | 929,04 | −0,048 su 103 | ops 0445-0446 |
| 4 ott | 264 | 57% | −62,59 | −24,56 / 38,03 | 937,41 | +0,015 su 119 | ops 0465-0466 |
| 5 ott | 291 | 57% | −76,08 | −33,61 / 42,47 | 923,92 | −0,039 su 145 | ops 0489-0490 |
| 6 ott | 309 | 57% | −77,42 | −33,02 / 44,40 | 922,58 | −0,057 su 162 | ops 0508-0509 |
| 7 ott | 345 | 56% | −88,03 | −38,62 / 49,41 | 912,77 | −0,091 su 197 | ops 0523-0524 |
| 8 ott | 377 | 55% | −98,04 | −45,16 / — | 902,30 | −0,101 su 227 | ops 0538-0539 |
| 9 ott | 417 (nel periodo, `portafoglio`) | — | −111,27 | — | 890,11 | −0,109 su 264 | ops 0553-0554, 0562 |
| 10 ott | 440 (nel periodo) | — | −109,41 | — | 890,58 | −0,080 su 283 | ops 0568, 0577, 0581 |
| 11 ott, 06:00 | 458 | 56% | −109,19 | −47,45 / 61,74 | 891,26 | — | ops 0584 |
| 12 ott, sera | 508 | 56% | −126,21 | −58,62 / 67,59 | — | −0,110 su 442 (tutto il periodo) | ops 0596, 0607 |
| 13 ott, 18:10 UTC (riavvio) | — | — | −135,06 | — | 864,94 | — | ops 0617 |
| 16 ott, 05:40 UTC | 647 (612 + 35 esplorativi) | 55% | −164,47 | — | — | −0,116 su 573 (tutto); −0,107 su 477 dal 27 set | ops 0620-0621 |
| 18 ott, 04:34 UTC | 704 | 56% | −172,92 | −87,25 / 85,66 | 827,08 | — | `docs/state.md` |
| **18 ott, 09:03 UTC** | **707 (668 + 39 esplorativi)** | **393 (56%)** | **−174,41** | **−88,62 / 85,78** | **825,59** | **−0,113 su 629 (tutto); −0,104 su 533 dal 27 set** | **ops 0622-0623** |

Due fonti che non coincidono del tutto: il 16 ottobre il `controllo` dà 647 trade e −164,47 USDT (ops 0621), il
`portafoglio` 646 trade e −164,98 (ops 0619, trade «usciti nel periodo» per giornata italiana). I conti tornano fra
`trades` e `stato`: 612 + 35 esplorativi = 647, e −162,17 + (−2,30) = −164,47 (ops 0620); 668 + 39 = 707, e −173,01 + (−1,40)
= −174,41 (ops 0622-0623; calcolo mio).

**Nel mese** (dal 1 ott mattina al 18 ott 09:03 UTC): +503 trade, −103,59 USDT realizzati (calcolo mio, da −70,82 a −174,41).
**Dagli ingressi a limite** (13 ott 18:10 UTC → 18 ott 09:03 UTC): −39,35 USDT (da 864,94 a 825,59; calcolo mio).

### 4.2 Le giornate di ottobre (colonna «paper» del `portafoglio`, ops 0619, giornate in ora italiana)

| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 (fino alle 07:40) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| −9,57 | +3,48 | +18,85 | −9,65 | −6,38 | −7,80 | −12,95 | −12,51 | +1,58 | −1,16 | −16,09 | +9,56 | −25,25 | −13,76 | −23,95 | +11,58 |

Dal 1 al 15 ottobre: 4 giornate in utile e 11 in perdita, somma −105,60 USDT (calcolo mio). Nello stesso periodo il
portafoglio simulato del motore sulle stesse coppie fa giornate da −16.531,65 a +10.231,27 su un conto simulato unico da 10.000 (ops 0619; `scripts/portafoglio_backtest.py`):
ma quel numero è ottimista per costruzione, perché le coppie sono state scelte anche su quei giorni. Settimane: 28 set-4 ott
+14,09 USDT (ops 0474), 5-11 ott −41,33 (ops 0590), ma con l'ultimo giorno contato solo al mattino; a giornate intere
+8,82 e −55,31 (colonna paper di ops 0619, calcolo mio).

### 4.3 La fotografia dell'ultima lettura (18 ottobre, 09:03 UTC)

* **Conto:** 707 trade, 56% vinti, −174,41 USDT, −17,44% contro BTC +7,94% nello stesso periodo; equity 825,59; drawdown di
  portafoglio 177,44 USDT; massimo 15 posizioni insieme (ops 0623; 14 nel `trades`, che conta solo le 668 validate,
  ops 0622).
* **Costi stimati dal modello** (non misurati sui riempimenti): 85,78 USDT = commissioni 48,07 + spread 37,40 + funding +0,31;
  0,12 USDT a trade; pareggio al 10,39% dell'equity (ops 0623).
* **Come escono:** trailing 313 (+232,33), stop prima di qualsiasi incasso 309 (−588,72), incasso parziale 63 (+111,76),
  tempo scaduto 16 (+37,10), take profit pieno 6 (+33,12); nessun gradino raggiunto nell'89% dei trade; massimo a favore
  mediano 0,78 R, almeno 1 R nel 34%, almeno 1,5 R nel 13% (ops 0623).
* **In R** (668 trade delle validate, 629 con R; ops 0622): netto −0,113, lordo −0,026, costi 0,087. Long −0,153 su 376, short
  −0,055 su 253. Regime all'apertura: rialzo −0,187 su 127, ribasso −0,086 su 235, laterale −0,157 su 174, incertezza alta
  +0,000 su 93. Controtrend −0,165 su 250, in trend −0,025 su 112.
* **Contro il caso** (ops 0622): stop 44% contro 46%; massimo toccato 0,77 R contro 0,81; primo target 12% contro 17%; vinti 55%
  contro 54%; R −0,113 contro −0,067.
* **Deriva:** PF vissuto 0,709 contro 2,02 promesso dal gate su 663 trade (ops 0623).
* **Ritmo:** 20,2 trade al giorno in media, massimo 51 (13 ott); 99 monete e 200 strategie diverse (ops 0622).

---

## 5. Le ricerche del mese, in sequenza

1. **Protocollo per moneta, versioni 4.2 → 4.5 (5-12 ottobre).** 4.2 proposto il 5 ott; 4.3 approvato il 6 sera («sì alla
   4.3, sì ai branch, vai col Passo 0»); Passo 0 (motore, dati, statistica, guardiano; 36 difetti trovati dai revisori) e
   Passo 1 (7 ott: 100 monete idonee su 895 contratti, 20 di campagna). **Prova di processo** su BTC, ETH, SOL (7 ott): 0
   candidati su 56 varianti; diagnosi: la ricerca per moneta singola non ha abbastanza trade. **4.4** approvata l'8 ott alle
   05:08 UTC («ok alla 4.4, archivia e riapri le tre campagne»): BTC dà il primo candidato (p 0,048). Prova a placebo del 9
   ott: l'esame regge (0,41% «nette» per caso, soglia 3%). **4.5** approvata il 9 ott alle 12:06 UTC: 17 campagne in un
   giorno, 20 monete su 20, 600 varianti, 3 candidati (BTCUSDT-V10, BNBUSDT-045, ADAUSDT-037) (diario 5-9 ott).
2. **Campagna di gruppo sulle 80 monete (10-11 ottobre).** Decisa il 10 («sì alla campagna di gruppo, no a rifare
   Bitcoin»), regole in vigore alle 17:11 UTC; tre sessioni per farla partire (sezione 6); consegna l'11 alle 07:49 UTC:
   nessuna strategia valida (la più vicina t 2,06 contro 2,16). Placebo di gruppo: regge.
3. **Vault della 4.5 (11 ottobre).** «APRI IL VAULT» alle 17:29 UTC; tutti e tre bocciati sul 2024-2026: BTCUSDT-V10 profit
   factor 1,067 contro 1,10 (325 trade, +0,031 R), BNB 0,55, ADA 0,79 (`research/vault/risultati.md`). **Passo 7 (12 ott):**
   630 varianti → 45 candidate → 7 in validazione → 3 al vault → 0 (`research/confronto/risultati.md`).
4. **Seconda edizione, campagna del paniere (13-14 ottobre).** Barre giornaliere, 80 monete, tre idee con fonte; bozza e
   approvazione il 13, Passo 0 nella notte, campagna il 14 (06:58 UTC): nessuna strategia valida (due candidate dell'idea
   «ritardo dopo un giorno forte di Bitcoin» cadute nelle verifiche).
5. **Protocollo 3, campagna BTC51 (16-17 ottobre).** Il protocollo «versione 5.1 su BTC» scritto dal proprietario, approvato
   il 16 alle 19:26 UTC; collaudo del metodo bocciato al primo giro e passato al secondo dopo tre correzioni; un solo
   candidato, V-020 (long a 1 ora nei giorni feriali con funding sotto zero), passa la validazione (+0,167 R su 80) e cade nel
   vault (−0,007 R su 180, p 0,337) e sulle altre 9 monete (regge solo su LTC) (`research/vault/BTC51_risultati.md`,
   `research/altre_monete_3/risultati.md`).
6. **Protocollo 4, campagna LINK6 (17-18 ottobre).** Approvato il 17 alle 20:12 UTC: LINK con 9 monete di controllo;
   collaudo superato al primo giro; 33 varianti su 40, nessun candidato; vault 4 mai aperto (`research/campagne/LINK6/
   lezioni.md`).

**Bilancio del mese:** su circa 730 varianti con un esame tarato (630 + 30 del paniere + 40 di BTC51 + 33 di LINK6 = 733; somma
mia), 4 candidati al vault, 0 superati. Il metodo trova i vantaggi inseriti di proposito (88 su 88 da 0,35 R,
`research/collaudo_4/esiti.md`): «nessuna strategia» è un'informazione sul terreno cercato (regole tecniche classiche, grandi
monete, 15 minuti-4 ore, e barre giornaliere sul paniere), non un difetto dell'esame.

---

## 6. Errori, bug, incidenti e ipotesi sbagliate del mese

**Bug e difetti del codice del bot, del gate e dei report**
1. **Lettura della cache dei take profit** (2 ott): la tabella del report `mfe` prendeva i file corti scritti per un'altra
   sezione invece della storia del gate (HEMI 601 ingressi invece di 8.640). Corretto in fc4ec225 prima della lettura vera.
2. **Testo del fuori campione troncato** a 400 caratteri nel report giornaliero (2 ott): taglio a fine parola (3a2d31f0).
3. **Ondate con l'ora UTC etichettata «italiana»** (3 ott, `trade_stats.py`): corretto (e3df041d).
4. **G7 senza nessuna prova** (4 ott, ops 0485; 5 ott 144 unità in errore «'cfg'», ops 0502): sulla macchina R1 gira come
   `python -m scripts.replay_gate`, cioè come modulo `__main__`, e l'unità di G7 importava una seconda copia del modulo con
   lo stato vuoto. Nei test non si vedeva (modulo unico). Corretto in 0dc9e382, verificato il 5 ott (ops 0505-0506).
5. **Due test di R1 legati alla data** (serie finta ferma al 1 ott): sistemati il 4 ott (diario, «G7 scritta»).
6. **Un test del voto t instabile** (`test_un_errore_su_una_coin_non_butta_le_coin_gia_votate`, coi processi) è caduto una
   volta e ripassato da solo il 1 ott: «da tenere d'occhio» (diario, «1 ottobre, mezzogiorno»). Non risulta ricontrollato.
7. **Errore della dashboard** il 1 ott: Firestore non accetta liste annidate, il report andava in errore (7d9e4178).

**Incidenti di funzionamento**
8. **Gate e R1 non stanno insieme** (1-3 ott): i giri del gate durano quanto il timer (2 h 58-3 h 28; ops 0391, 0501, 0520) e
   sono «attaccati» uno all'altro; R1 non trovava pause (ops 0410-0413, 0463). Rimedio: R1 al posto di un giro al giorno, poi
   R1 fermato.
9. **Giri del gate sempre più lunghi**: 3 h 09 (4 ott), 3 h 21 (7 ott), 4 h 47 con 81.788 valutazioni (8 ott), 4 h 18 (11 ott)
   (ops 0470, 0535, 0541, 0586). Causa: le valutazioni, non un rallentamento (~16.000 l'ora; capito 9 ott). Il motivo delle
   notti al +35% non è stato trovato.
10. **Durata del giro non coerente** fra due fonti (3 ott: 1 h 56 nel `gate`, 2 h 57 nel log; ops 0448, 0450): non spiegato.
11. **Un riavvio del bot non spiegato** il 2 ottobre (pid 1975598 → 2005927; ops 0424, 0443, 0460): nessuna richiesta ops,
    ora e causa non nei file.
12. **Spazio del registro**: da ~1.380 coppie (1 ott, ops 0391) a ~325 (11 ott, ops 0586), sotto l'allarme dei 400; proposta
    D1 mai fatta. Il problema è sparito con il gate fermo, non è stato risolto.
13. **Letture di Firebase in crescita** dai segnali rifiutati: 8.674 (7 ott) → 12.109 → 14.521 → 16.811 (10 ott) in 24 ore
    (ops 0527, 0542, 0557, 0572); 12.218 il 13 ott (ops 0616). «Va capito perché i rifiutati letti crescono più dei trade»
    (capito 9 ott): non risulta capito.
14. **Test di GitHub rossi** tre volte: 7 ott dal commit 5ca2c8e (`yaml` non fra le dipendenze; 12 esecuzioni rosse; corretto
    45e664d); dall'8 al 9 ott a ogni push (run 833-862: un buco del guardiano visibile solo col git di GitHub e il lettore del
    backlog; corretto 89f1d376); dal 10 all'11 ott (script senza `PYTHONPATH`; corretto, run 38165200292). Il proprietario
    riceveva un'e-mail per ogni esecuzione fallita. Lezione del diario: un test rosso a ogni push nasconde i problemi veri.
15. **Il report della mattina eseguito contro la volontà del proprietario** (11 ott): «non eseguire il report giornaliero»
    letto alla lettera, spento solo il controllo giornaliero, e alle 05:45 è partito il referto settimanale. Correzione: tutte
    le routine del mattino spente, regola in `CLAUDE.md` («un "non farlo domattina" vale per TUTTI i report del mattino»).
16. **Quattro letture ops in timeout** a 900 s il 12 ott (`edge`, `confidenza`, `costi`, `timeframe`; ops 0602, 0603, 0606,
    0610): mai rilanciate. In particolare il ricontrollo dei costi sui riempimenti non c'è.
17. **Incidenti delle sessioni di ricerca** (dettaglio nella parte sulla ricerca): una sessione nata senza il repository fra
    le sorgenti (7 ott, push 403); sessioni giudicate ferme troppo presto e riaperte (8 ott); ultracode che non si eredita in
    modo affidabile (8, 10, 14, 17 ott); domande delle sessioni rimaste ore senza risposta (SOL 4 h 20 l'8 ott; FIL 55 minuti
    il 9); sessioni di gruppo ferme per pytest e scipy mancanti e poi per Python 3.13 (10 ott); il guardiano che negava alla
    campagna del paniere le regole del gruppo e lo strumento delle notifiche (14 ott); un comando d'attesa che non finiva mai
    ha ritardato di due ore un candidato nel vault (11 ott).
18. **Il caricatore del funding** (trovato dalla campagna BTC l'8 ott: il funding arriva fino a 47 ms dopo l'ora piena,
    2.233 settlement su 4.383): corretto (2fedf41, adfb831); effetto su ETH al massimo 0,0075 R a trade.

**Ipotesi o previsioni sbagliate, e la loro correzione**
19. **«Sotto 400 domani»** (8 ott, spazio del registro): sbagliata, il registro si libera a ondate; proiettare in linea retta
    non funziona (capito 9 ott).
20. **«Diciotto volte»** (4 ott: passata a 1 ora 2,2% contro 0,12% a 15 minuti): era composizione (spec già note), non una
    differenza di timeframe; corretto alle 09:30 (capito 4 ott).
21. **L'affollamento «non è dove si perde»** (3 ott, 11 trade a +0,026 R): con più dati la fascia 6+ è la peggiore (−0,160 R
    su 84, ops 0622).
22. **Il paper esplorativo «contribuisce»** (4 ott, 10 trade): il giorno dopo «non si vede ancora» (ops 0489). Era il limite
    del campione minimo.
23. **«Il problema è il gate, non il bot»** (lettura del 7 ott, e analisi del 12 ott: «non è l'esecuzione»): il 16 ott la
    differenza d'esecuzione supera per la prima volta il margine (−0,06 R in più del motore, ops 0619). Le due letture non si
    contraddicono del tutto (prima dentro il margine, poi appena fuori, con i trade a limite mescolati), ma la frase «non è
    l'esecuzione» oggi va scritta con riserva.
24. **Il report giornaliero e il backlog in dashboard «si aggiornano da soli»**: vero solo finché gira il gate. Dal 13 ottobre,
    con la discovery che esce subito (`scripts/discover_strategies.py:3778`), la pubblicazione (riga 4424) non avviene più.
    Dedotto dal codice, non verificato sulla macchina; nessuno l'ha scritto.
25. **I report che ricalcolano le validate vedono 0 coppie dopo 3 giorni di gate fermo.** `coppie_validate`
    (`bot/core/registry.py:67-85`) tiene solo le coppie viste dal gate da meno di `FRESH_DAYS` giorni (3 di default,
    `OPTIMIZER_FRESH_DAYS`). Col gate fermo dal 13 ott 18:40 UTC, dal 16 ott sera circa questa funzione restituisce zero
    coppie: lo mostra la sezione K10 di ops 0622 (0 coppie in ogni gruppo, tutti i 629 trade «non più validate»), mentre il
    16 ott alle 05:40 ne vedeva ancora 207 + 42 (ops 0620). Il bot invece continua a operare le 249 coppie perché legge la lista
    scritta dal gate (`bot/learning/adaptation.py:284-288`). La usano anche `scripts/portafoglio_backtest.py` (il fuori
    campione) e `scripts/gate_progress.py`: una lettura del fuori campione fatta oggi rischia di essere vuota o falsata.
    **Trovato da me leggendo il codice; il valore di `OPTIMIZER_FRESH_DAYS` sulla macchina non è verificato.**
26. **Il testo di `ops/gate_fermo` è superato:** dice che la ricerca «riparte con la seconda edizione del protocollo
    (research/PROTOCOLLO_2.md), quando il proprietario la approva»; la seconda edizione è stata approvata e chiusa il 13-14
    ottobre, e dopo sono venuti il protocollo 3 e il 4. Non cambia il funzionamento (conta solo che il file esista).
27. **La stima del risparmio degli ordini limite** (12 ott: costo da 0,095 a 0,04-0,05 R, stima) contro la misura (13 ott: −0,0225
    R, un terzo): la stima era ottimista perché le uscite restano a mercato.
28. **La probabilità che il candidato BTC fosse vero** (8 ott): «31-63%» era il massimo possibile, corretta la sera stessa in
    22-52% (diario, «8 ott, sera tardi»); il vault l'ha bocciato.

---

## 7. Cosa abbiamo capito, ed errori da non ripetere

**Cosa abbiamo capito sul paper e sul gate (con il numero che lo dice)**
1. **Gli ingressi del gate non sanno la direzione.** Lordo vicino a zero (−0,026 R su 629, ops 0622), curva del vantaggio
   piatta a 1-24 ore (ops 0437, 0597), ogni misura d'uscita uguale a quella di un prezzo casuale con le stesse uscite (ops
   0622). Il paper perde quasi esattamente i suoi costi (0,087 R a trade).
2. **La scelta del gate non regge dopo la scelta.** Motore dopo la validazione −0,05 R su 230 (7 ott) e −0,03 R su 566 (16
   ott) (ops 0532, 0619); PF vissuto 0,71 contro 2,02 promesso (ops 0623); R2 0 su 3.600 (ops 0485); G7 il doppio di passate
   sui prezzi mescolati (ops 0506). Il gate «trova» strategie perché prova 27.000 candidate a giro e ne riprova di simili a
   ogni giro senza contare i tentativi (analisi del 12 ott, sezione 2.6): è il motivo per cui il proprietario ha detto che
   si può riscriverlo da zero.
3. **L'esecuzione aggiunge una perdita propria, piccola:** −0,06 R in più del motore sugli stessi segnali al 16 ottobre (ops
   0619), oltre il margine per la prima volta, con riserva.
4. **Nessuna delle funzioni «intelligenti» del bot ha un contributo misurato** (ops 0622); quelle che imparano dal paper
   vanno nel verso sbagliato. Spegnere l'AI (idee, autopsia, ombra, filtro) non ha cambiato nessun numero visibile e ha
   portato le chiamate AI del bot a zero (ops 0467, 0510, 0525).
5. **Uscite, trailing, scala dei target, size e freni non sono la leva**: su un prezzo senza informazione nessuna regola
   d'uscita crea un vantaggio (analisi del 12 ott, sezione 2.3; trailing 120 prematuri contro 124 protetti, ops 0621).
6. **L'affollamento pesa:** con 6 o più posizioni nello stesso verso −0,160 R contro −0,092 (ops 0622): il bot scommette tutto
   insieme sulla stessa cosa nelle ondate. Non crea vantaggio limitarlo, riduce le giornate peggiori (ipotesi, non provata).
7. **Gli ordini limite abbassano i costi di un terzo, non creano vantaggio** (prova sulla storia del 13 ott). Nel paper la misura
   vera non è ancora stata letta.
8. **I long hanno perso più degli short** (−0,153 contro −0,055 R, ops 0622), soprattutto contro BTC che scendeva: è un effetto
   del periodo, non una regola (analisi del 12 ott, sezione 2.4).

**Errori da non ripetere (per chi riscrive il gate)**
1. **Contare i tentativi.** Un filtro che prova decine di migliaia di candidate a giro, e ripesca i quasi-passaggi, fa passare
   rumore per costruzione. Serve un confronto con entrate casuali per ogni candidata e una correzione per il numero di prove
   (analisi del 12 ott, sezione 4; protocollo).
2. **Mai usare il paper come insieme di addestramento.** Tre trade a strategia non insegnano niente; i «referti» e le
   ipotesi nate dai trade del paper erano rumore (13 ipotesi nella lettura del 12 ott; provate dal gate: 3 nate, 1 variante, 0 passate; analisi, sezione 2.5).
3. **Scrivere la regola prima dei numeri** e rispettarla: ha funzionato per T2, R1, R2, G7 e le due letture ufficiali, e ha
   evitato di leggere un giorno buono (il 3 ott, +0,869 R) come una svolta.
4. **Non decidere su campioni minimi**: «contribuisce» su 10 trade (4 ott) e l'affollamento positivo su 11 (3 ott) si sono
   girati con più dati.
5. **Un interruttore che ferma una parte del sistema va seguito in tutto ciò che ne dipende**: col gate fermo si sono fermati
   anche il report giornaliero, il backlog in dashboard e, dopo 3 giorni, il conteggio delle validate nei report (sezione 6,
   punti 24-25), senza che nessuno lo scrivesse.
6. **Le istruzioni del proprietario sui report vanno lette nel senso, non alla lettera** (11 ott).
7. **Una misura promessa va messa in calendario con lo strumento che la legge**: la misura degli ordini limite nel paper non
   ha ancora un report, e le quattro letture in timeout del 12 ottobre non sono mai state rilanciate.
8. **Una modifica approvata «per dopo» va riguardata quando arriva il dopo**: C5 (costi veri) e G8 (porta per direzione)
   erano sbloccate dalla lettura del 16 ottobre e sono rimaste ferme col gate fermo, senza una decisione scritta.
9. **I test rossi vanno sistemati subito**: tre volte in un mese hanno nascosto un difetto vero (un buco del guardiano) e
   riempito di e-mail il proprietario.

---

## Note per chi unisce le parti: cose incerte o non verificate

* La misura degli ordini limite nel paper (tasso di esecuzione, costo, R dei saltati) **non esiste ancora**; il «circa 80
  trade a limite» del 16 ottobre è una stima del diario; il costo a trade più basso nei 56 trade fra il 16 e il 18 ottobre è un
  mio calcolo su un campione piccolo.
* Che il report giornaliero e il backlog in dashboard siano fermi dal 13 ottobre è dedotto dal codice, non verificato.
* L'effetto di `FRESH_DAYS` sui report (0 validate dopo 3 giorni) è dedotto dal codice e dalla sola riga K10 di ops 0622; il
  valore di `OPTIMIZER_FRESH_DAYS` sulla macchina non è noto.
* Il supervisore dice «coppie validate 278» mentre lo stato e il bot dicono 249 (ops 0623): non ho capito da dove venga la
  differenza.
* Il secondo riavvio del bot del 2 ottobre: ora e causa sconosciute.
* BTC dal primo giorno al 1 ottobre: +11,2% in ops 0386, +11,37% in ops 0389, +11,4% nel diario.
* Il 16 ottobre: 647 trade e −164,47 USDT (ops 0621) contro 646 e −164,98 (ops 0619).
* Le risposte ops 0622 e 0623 sono arrivate col commit 3c7fbdb8 (18 ott 09:03 UTC): prima lette da GitHub in sola lettura,
  poi ricontrollate sulla copia locale.
* Il diario non dice quando il modello della sessione di coordinamento è tornato da Fable 5.1 a Opus 5.5: lo deduco dai
  trailer dei commit (ultimo Fable 14 ott 14:18 UTC, primo Opus di nuovo 16 ott 05:29 UTC).
