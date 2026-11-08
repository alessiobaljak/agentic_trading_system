# Revisione: fase 2 del conto vero, secondo giro (correzioni dei problemi 53-63) — 8 novembre 2026

## Riepilogo e verdetto

**REQUEST CHANGES.** Nessun Bloccante. Dei problemi del primo giro: 53, 55, 57, 59, 61, 62, 63 chiusi; 56 chiuso come scelto dalla
sessione (decisione 5); 58 chiuso nel disegno, ma la lettura dei redditi introduce due Medi nuovi (64, 65); 54 chiuso per la parte
nel codice, **aperta la parte (ii)**: con l'agente che ora porta il tag forzato ogni minuto, chi può spingere il tag su GitHub
approva il codice dei soldi veri (Alto, condizione obbligatoria prima dell'accensione, decisione 2); 60 chiuso per il «riparti»
(solo da file), restano pulsante, stato e regole in dashboard per la fase 4. Nuovi Bassi 66-69.

Verificato che quello che girerebbe oggi non cambia comportamento in modo pericoloso: il demo ha un solo cambio voluto (lo stato
salvato dopo `parti_da_zero`, problema 62, con test); `scripts/ops_agent.py` aggiunge un `git fetch` del solo tag che non può
sollevare eccezioni; il conto vero spento e mai acceso non fa richieste e non legge chiavi; all'avvio tre-quattro comandi `git`.
**Attenzione**: `ops_agent.py` si rilegge a ogni giro del timer, quindi il suo cambio entra in funzione sulla macchina al primo
`git pull` dopo il commit, senza riavvio.

## Oggetto

- Branch `claude/brave-albattani-1b12fv`, modifiche non committate su HEAD `7d77c9a` (codice del percorso = `1a8522f`; `git diff
  1a8522f HEAD -- bot/ firebase/ scripts/ops_agent.py tests/` vuoto). Copia dei file rivisti in `fase2/giro2/` (cartella di lavoro).
- File: `bot/portafoglio/conto_vero.py` (nuovo, 564 righe), `demo_binance.py`, `bot/config.py` (`:791-813`), `bot/main.py`
  (`:43`, `:503-506`, `:1447`, `:1493`, `:1553`, `:1981`, `:2522`, `:2653-2656`), `scripts/ops_agent.py` (`:448-466`, `:499`),
  `scripts/state_snapshot.py`, `tests/test_conto_vero.py` (790 righe), `tests/test_demo_binance.py`, `tests/test_sicurezza_avvio.py`.
  Righe del working tree.

## Checklist A–F

### A. Limiti fissi e interruttori
- `hard_limits.py` invariato: **OK** (`git diff HEAD -- bot/risk` vuoto; `tests/test_risk.py`, `tests/test_sizing.py` passati).
- Limiti del conto vero come costanti con test: **OK** (`conto_vero.py:82-89`, `tests/test_conto_vero.py:89-110`).
- Parametri della dashboard: **NON APPLICABILE** al conto vero.
- Pulsante senza Firebase: **OK** anche con il conto spento, finché non è vuoto (prove p1, q2; test `:585-621`, 6 casi: interruttore
  o `DRY_RUN`, stop o file o Firebase). Nessun pulsante in dashboard: resto del 60.

### B. Ordini
- Filtri veri, identificativi, «solo riduzione», leva e margine: **OK**, invariati dal primo giro.
- Freno del cliente: **OK** (`conto_vero.py:189-193`); da spento si richiude a ogni giro (`:281-282`, `:488`).
- Stop per posizione: **NON APPLICABILE** (stop sul conto e pulsante, ora attivi anche da spento).

### C. Stato e resilienza
- Stato di Binance che prevale: **OK con riserve**. Il fermo sopravvive al file perso (57 chiuso, p3, p3b, p3c, test `:646-681`), ma
  il segno «acceso» su Firebase si legge una volta e un Firebase muto in quel momento vale «mai acceso» (66).
- **Valore del conto**: capitale + redditi + non realizzato (`:417-424`): un versamento non conta (p4, p4b), un prelievo non fa
  scattare lo stop e ferma gli ordini nuovi (q6). **PROBLEMA**: righe dei redditi perse (64, prova q4) e righe della fase vecchia
  contate nella nuova (65, prova q5).
- 429/418, orologio, Firebase che fallisce: **OK** (invariati; i limiti di Binance nei redditi risalgono, `:414`).

### D. Separazione fra paper, demo e conto vero
- Mai acceso: nessuna richiesta e nessuna chiave letta anche con l'interruttore e `DRY_RUN` vero (q3; test `:131-170`). **OK.**
- **Invariante cambiato**: con `DRY_RUN` vero, se il conto vero è stato acceso almeno una volta e Binance non dice il conto vuoto, il
  bot legge le chiavi vere e manda ordini «solo riduzione» e annulli al conto vero (`:274-306`, `:509-520`). È la scelta della
  sessione sul 53; serve il sì di Alessio (decisione 1).
- Avvio: con `DRY_RUN` falso il bot parte sempre, salvo la parità accesa (`config.py:801-813`; test `test_sicurezza_avvio.py`). **OK.**
- Vecchio sistema con `DRY_RUN` falso: niente «🔴 LIVE» (`main.py:1447`…), riconciliatore non avviato (`:2522`). **OK** (63).

### E. Segreti e sicurezza
- Nessuna chiave in codice, log, Firebase: **OK**.
- Chiave senza prelievo e limitata all'indirizzo; regole di Firebase: **da confermare con Alessio** (invariato).
- **Chi approva il codice: PROBLEMA aperto** (54 ii): `porta_il_tag` (`ops_agent.py:452-466`) porta sulla macchina, forzato, il tag di
  GitHub; nessuna firma verificata, nessuna regola nel repo.

### F. Test
- `python3 -m pytest tests/ -q`: **2681 passed, 1 failed** in 192 s; il fallito è la firma (libreria di cifratura del contenitore),
  che con `PYTHONPATH=/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/cripto` passa
  (con `tests/test_risk.py` e `tests/test_sizing.py`: 21 passed). Coincide con quanto dichiarato.
- Quattro mutazioni a mano su `conto_vero.py` (tolto il segno di Firebase nel 57, tolto il controllo del saldo, protezioni da spento
  sempre spente, tolto il controllo del conto non vuoto): ognuna fa fallire un test. Non ho rifatto le 27 dell'implementatore.
- Controllo del codice in un clone con il tag (`fase2/giro2/clone`): `import bot.main` carica 53 file del repository, fra cui
  `research/programma6/esclusi.py`; con il clone uguale al tag il controllo dà «approvato» all'avvio e dopo; `esclusi.py` cambiato →
  «diversi dal tag»; un modulo caricato toccato dopo l'avvio → «file cambiati dopo l'avvio del processo».
- Prove p1-p9 rifatte sul codice nuovo (`fase2/prove_fase2*.py`) e nuove q1-q8 (`fase2/giro2/prove_giro2*.py`). Con il valore nuovo un
  calo del saldo senza righe di reddito è un prelievo: p1b e p3 del primo giro non provano più lo stop, rifatte come q1 con la perdita
  non realizzata.

## Stato dei problemi del primo giro

| N. | Esito | Evidenza |
|---|---|---|
| 53 | **chiuso** | Spento con posizioni: stop (q1), pulsante a file (p1) e su Firebase (q2) chiudono, solo «solo riduzione»; a conto vuoto nessuna richiesta (q1: 0 richieste dopo). Avvio con `DRY_RUN` falso senza interruttore: il bot parte. Invariante D cambiato (sopra). |
| 54 | **chiuso (i), aperto (ii)** | Tutti i file caricati nel processo contro il tag (`:100-116`, `:129-172`, `:219-225`; prova nel clone). Tag: decisione 2. |
| 55 | **chiuso** | `porta_il_tag` scarica, sposta e toglie il tag (test `:532-583` con git vero). Resta il 67. |
| 56 | **chiuso come scelto** | Con un blocco gli ordini limite vivono la loro ora, poi annullati senza resto (`:495-496`, `:522-533`; test `:240`); un blocco tolto entro l'ora completa il ribilancio (p2: conto neutro). Oltre l'ora il conto resta a metà: decisione 5. |
| 57 | **chiuso** | Stato perso o illeggibile dopo un'accensione → fermo, chiusure, «riparti» nuovo dal file (p3c, p7; test `:646`). Resta il 66. |
| 58 | **chiuso nel disegno** | Versamento non conta (p4b: nessun ordine in più), prelievo ferma gli ordini senza stop (q6). Nuovi 64, 65. |
| 59 | **chiuso** | Prima accensione con posizioni o ordini non del bot: niente ordini, allarme (p5; test `:683`). Nota 69. |
| 60 | **chiuso in parte** | «Riparti» solo dal file (`:69`; test `:708`). Pulsante, stato e testata in dashboard e regole di Firebase: fase 4. |
| 61 | **chiuso** | All'avvio anche i file cambiati dopo l'ora d'avvio del processo (`:119-126`, `:164-169`; prova nel clone). |
| 62 | **chiuso** | Stato salvato dopo `parti_da_zero` (`demo_binance.py:677`, `conto_vero.py:435`); p9: niente richiusura. |
| 63 | **chiuso** | Testi propri, avviso di `DRY_RUN` una volta (`:252-258`), etichette e riconciliatore legati all'esecutore. |

## Problemi

### 54 (parte ii) — Alto, aperto — Il tag che approva il codice dei soldi veri lo sposta chiunque possa spingere su GitHub
- Dove: `scripts/ops_agent.py:452-466` (fetch forzato del tag ogni minuto), `conto_vero.py:142-145` (basta che il tag esista e sia
  uguale ai file); nessuna verifica di firma, nessuna protezione del tag nel repository o in `.claude/settings.json`.
- Scenario: con il conto vero acceso, una sessione modifica `bot/portafoglio/` e, per sbloccare gli ordini, sposta da sola il tag
  (`git tag -f`, `git push -f`); un minuto dopo la macchina lo scarica e il conto vero torna a mandare ordini; al primo riavvio (anche
  un crash, `Restart=always`) gira con soldi veri codice che nessuno ha rivisto.
- Correzione: tag firmato con una chiave che ha solo Alessio e `git verify-tag` nel bot (con la sua chiave pubblica sulla macchina),
  oppure una regola di GitHub che permetta solo a lui di spostarlo (domanda 1). Non blocca il commit del codice spento; blocca
  l'accensione.

### 60 (resto) — Medio, aperto per la fase 4 — Nessun pulsante né stato del conto vero in dashboard; regole senza il comando
- Invariato dal primo giro per questa parte: dal telefono Alessio non ha un pulsante per i soldi veri e la testata dice «DRY_RUN ·
  paper» (`DashboardShell.tsx:416-419`). Da fare prima dell'accensione (decisione 8).

### 64 — Medio, nuovo — I redditi del conto si leggono in modo fragile: una riga persa ferma gli ordini con «un prelievo?»
- Dove: `conto_vero.py:393-408` (si legge da `fino_ms + 1`, l'ora più alta vista, fino ad adesso), `:462-464` (saldo vero sotto il
  valore del bot di oltre 0,01 USDT → niente ordini nuovi), `:414-415` (un errore di lettura: solo una riga nel log).
- Prova q4: due righe di funding con la stessa ora (le 08:00), la seconda visibile un minuto dopo: la seconda non si conta mai; saldo
  vero 279,10 contro 279,50 del bot → «niente ordini nuovi: … un prelievo? serve un capitale nuovo». Prova q7: con la lettura dei
  redditi sempre in errore nessun allarme.
- Scenario: il funding delle 08:00 per 38 monete ha la stessa ora; se Binance lo scrive in qualche secondo e il bot legge in mezzo, le
  righe arrivate dopo si perdono. Basta un funding pagato perso: ordini nuovi fermi con un messaggio sbagliato; per ripartire serve un
  capitale nuovo, cioè chiudere tutto e riaprire alla mezzanotte. Una riga incassata persa abbassa il valore e anticipa lo stop.
- Correzione: leggere fino a qualche minuto prima di adesso e con una finestra che si sovrappone, togliendo i doppioni con
  l'identificativo della riga (`tranId` con il tipo); tolleranza del controllo del saldo più larga (per esempio 1 USDT o lo 0,5%) e
  ripetuta per qualche minuto prima di fermare; allarme dopo qualche lettura fallita. Test con righe della stessa ora in due letture.

### 65 — Medio, nuovo — Con un capitale nuovo le righe delle chiusure della fase vecchia entrano nella fase nuova
- Dove: `conto_vero.py:428-433`: `fino_ms = now + (durata di parti_da_zero)`, dove `now` è l'ora d'inizio del giro, non l'ora vera
  della fine delle chiusure.
- Prova q5: fase da 280 con +30 non realizzati, capitale nuovo 290; il giro parte alle t, le chiusure a t + 5 s: la fase nuova conta
  +30 di utile e −0,2 di commissioni → valore del bot 319,80 (sopra la costante di 300) e saldo 309,80 → «un prelievo?», niente ordini.
- Scenario: in produzione basta che fra l'inizio del giro e `parti_da_zero` passino più secondi di quanti ne dura `parti_da_zero`
  (circa 3, con l'attesa di 2 s dopo le chiusure): il giro prima legge Firebase, il conto, i redditi e git. Allora la fase nuova parte
  con l'utile o la perdita della vecchia: posizioni su più capitale di quello scelto (anche oltre 300), oppure ordini fermi.
- Correzione: segnare l'inizio dei redditi con l'ora vera dopo le chiusure (`time.time()`), o meglio con l'ora più alta delle righe
  lette subito dopo le chiusure; test con le righe delle chiusure dopo l'inizio del giro.

### 66 — Basso, nuovo — Un Firebase muto alla prima lettura vale «mai acceso» per tutto il processo
- Dove: `conto_vero.py:321-332` (letto una volta; `get_rtdb` non solleva e con il database muto dà lo specchio, vuoto dopo un riavvio,
  `firebase_client.py:681-702`): `{}` resta in memoria.
- Scenario (tre coincidenze): file di stato perso, riavvio con Firebase che non risponde, conto vero spento → nessuna protezione per le
  posizioni aperte; acceso e conto vuoto dopo un fermo → si riarma e compra alla mezzanotte senza «riparti».
- Correzione: non tenere in memoria una risposta vuota finché Firebase non ha risposto davvero (rileggere ogni minuto, o chiedere a
  `degraded_for` che il database sia vivo).

### 67 — Basso, nuovo — Il tag tolto si riconosce dal testo inglese di git
- Dove: `ops_agent.py:458` (`"couldn't find remote ref"`). Con git in un'altra lingua sulla macchina un tag tolto da Alessio resta
  sulla macchina (la revoca non arriva) e il log scrive ogni minuto «tag non scaricato». Correzione: `git ls-remote --exit-code origin
  refs/tags/conto-vero-approvato` (codice 2 = non c'è), che non dipende dalla lingua (provato: codice 2).

### 68 — Basso, nuovo — L'allarme `stato_perso` non si spegne mai
- Dove: `conto_vero.py:372`: scritto, mai tolto; dopo il «riparti» resta in dashboard e nella fotografia. Correzione: toglierlo al
  «riparti» riuscito.

### 69 — Basso, nuovo (risposta alla domanda dell'implementatore) — Alla prima accensione con posizioni non del bot lo stop le chiude
- Prova q8: posizione di CUSDT del proprietario, perdita del 41% del conto intero → lo stop del bot la chiude a mercato. «Nessuna
  chiusura» vale per il ribilancio, non per stop e pulsante, che lavorano sul conto intero. È una protezione, ma va detto ad Alessio.

Restano i Bassi 51 e 52 del demo.

## Invarianti modificati

- **Paper e conto vero** (cambiato): con `DRY_RUN` vero il conto vero, se è stato acceso una volta e non è vuoto, legge le chiavi
  vere e manda ordini «solo riduzione» e annulli (`conto_vero.py:274-306`, `:509-520`).
- **Avvio** (cambiato): con `DRY_RUN` falso il bot parte sempre, salvo la parità accesa (`config.py:801-813`).
- **Codice approvato** (cambiato): i 5 percorsi più tutti i file del repository caricati nel processo, e all'avvio nessun file
  cambiato dopo l'ora d'avvio (`conto_vero.py:100-172`, `:219-225`); il tag arriva sulla macchina forzato ogni minuto
  (`ops_agent.py:452-466`, `:499`).
- **Valore del conto vero** (nuovo): capitale + redditi di `REDDITI_DEL_CONTO` + non realizzato; saldo sotto il valore → niente ordini
  nuovi (`:77-78`, `:377-424`, `:462-464`).
- **«Riparti» del conto vero** (cambiato): solo dal file `ops/conto_vero_riparti` (`:69`).
- **Demo** (cambiato, voluto): lo stato si salva dopo `parti_da_zero` (`demo_binance.py:677`). Limiti fissi invariati.

## Decisioni per Alessio

1. Le sole protezioni da spento (53): con `DRY_RUN` vero il bot manda ordini «solo riduzione» al conto vero se questo è stato acceso e
   non è vuoto. Va bene questa eccezione alla regola «in paper nessun ordine al conto vero»?
2. **Chi approva il codice** (obbligatoria prima dell'accensione): tag firmato da lui e verificato dal bot (raccomandato) o regola di
   GitHub sul tag. Oggi chi spinge il tag approva.
3. I limiti del conto vero (300, 600, 200%, 60%, leva 5, stop −35% e pavimento 65%, 26 ore); G1 neutra non ci sta (fino al 300%).
4. I prelievi: ognuno ferma gli ordini nuovi finché non scrive un capitale nuovo (che chiude tutto e riapre alla mezzanotte). Va bene
   per i «prelievi regolari» del piano?
5. I blocchi del codice: ogni commit che tocca un file caricato dal bot (tutto `bot/` e `research/programma6/esclusi.py`) ferma gli
   ordini nuovi finché il tag non si sposta, poi si aspetta la mezzanotte; un ribilancio in corso, oltre l'ora, resta a metà. Accettarlo
   o tenere il codice dei soldi veri separato dalle varianti del paper?
6. Lo stato perso dopo un'accensione chiude tutte le posizioni a mercato e aspetta il suo «riparti» (p7): va bene il costo?
7. «Riparti» solo da file: lo può scrivere chiunque spinga sul branch, sessioni comprese. Due passi?
8. Pulsante, stato e testata del conto vero in dashboard prima dell'accensione.
9. Fuori dal codice, da confermare: chiave senza prelievo e limitata all'indirizzo; regole di Firebase pubblicate; conto con una
   posizione per moneta, margine in solo USDT (niente «multi-assets»), niente «portfolio margin», niente BNB per le commissioni.
10. Il commit: `ops_agent.py` entra in funzione sulla macchina al primo `git pull` (nessun riavvio); il resto al riavvio, con il suo ok.
11. Restano: stop per posizione assente per scelta, avvisi sul telefono, lo Sharpe corretto 0,86, «almeno 10 monete per lato».

## Domande aperte

1. Con quale identità la sessione spinge su GitHub? Serve per scegliere fra firma e regola di GitHub (54 ii).
2. Sulla macchina: bot e agente `ops` con lo stesso utente, `git` eseguibile dal bot nella cartella; git in inglese o tradotto (67)?
3. Il conto dei future: modalità, attivi, BNB per le commissioni, nessun'altra posizione (decisione 9)?
4. `/fapi/v1/income` sul conto vero: le righe arrivano dalla più vecchia, c'è un tetto all'intervallo fra `startTime` e `endTime`, il
   funding delle 08:00 ha la stessa ora per tutte le monete? Va visto con una lettura vera prima dell'accensione (64).
5. Risposte all'implementatore: l'elenco `REDDITI_DEL_CONTO` va bene per un conto in solo USDT (i rimborsi di commissione esclusi sono
   prudenti: alzano il saldo, non fermano niente; i nomi vanno confermati con una lettura vera, domanda 4); il punto debole è la
   lettura, non l'elenco (64, 65). Posizioni senza tracce di accensione → 59 e non 57: va bene, con la nota del 69 e del 66.
6. Lunedì G1 o G1 neutra? Con G1 neutra servono file della decisione e somma dei pesi diversi.
7. Dal 7 novembre: la proposta della leva a 10 si chiude come «non applicata»?
