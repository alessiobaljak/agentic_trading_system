# Revisione del 27 novembre 2026: lo «stato» della macchina e l'oscuramento dei segreti dell'agente

Revisore: live-path-reviewer. Base `117d2b9` sul ramo `claude/brave-albattani-1b12fv`, modifiche non committate.

## Riepilogo e verdetto

**REQUEST CHANGES**, ma solo per `scripts/state_snapshot.py`.

- **L'agente della macchina (`scripts/ops_agent.py` e `tests/test_ops_agent.py`) va bene così com'è.** Ora toglie davvero tutto il
  blocco di una chiave privata, i valori di `private_key` e `private_key_id` e le sequenze lunghe che sembrano una chiave. Non ho
  trovato problemi. Si può committare da solo, subito.
- **Lo «stato» risolve il taglio dei 20.000 caratteri**, ma sposta il battito del bot e la riga del `DRY_RUN` in fondo, sotto un
  titolo che dice «Vecchio sistema (fermo dal 13 ottobre)». Sono invece il battito e il `DRY_RUN` dell'unico processo del bot,
  quello che fa girare il demo, i paper e il conto vero (problema 203, Medio). È una correzione piccola. Dopo, serve un riesame breve.
- Ci sono quattro problemi Bassi (204-207). Nessun problema Bloccante o Alto. Gli ordini e i limiti fissi non cambiano. Non serve
  nessun riavvio del bot.

I numeri partono dal 203, non dal 187: dal 188 al 202 sono già usati dalle revisioni del trader AI (`reviews/INDEX.md:15`). Il 187
resta libero.

## Oggetto

- File e impronte md5 al momento della revisione:
  - `scripts/ops_agent.py`: c8d9f508
  - `tests/test_ops_agent.py`: 3d3c4a62
  - `scripts/state_snapshot.py`: d4e48408
  - `tests/test_stato_audit.py` (nuovo): 847695ea
  - `tests/test_pesi_g1_oggi.py`: 2771ad7a
- Cosa correggono: i problemi dell'audit del 26 novembre (`.../scratchpad/audit/tutti.md`):
  - salute-5, l'oscuramento (righe 1087-1111);
  - salute-1, il taglio dello stato (righe 977-1004);
  - salute-8 e salute-9 (righe 1159-1202);
  - per la parte dello stato, ordini-2, ordini-4 e ordini-5 (righe 411-478).
  - Rapporti dei correttori: `.../scratchpad/correzioni/segreti.md` e `.../scratchpad/correzioni/stato.md`.
- Come entrano in funzione: i due script si rileggono da soli. L'agente cambia al primo giro del timer dopo il `git pull`. Lo
  stato cambia alla prima richiesta «stato» e al primo giro di GitHub (`.github/workflows/snapshot.yml:12`). Il bot non va riavviato.
  Il bot importa lo stato solo per `_EXIT_LABEL` (`bot/learning/controllo.py:426`). A livello di modulo sono state aggiunte solo
  `import calendar` e alcune costanti.
- Invarianti coinvolti:
  - Il pulsante a file del demo (`ops/demo_binance_chiudi_tutto`) arriva con il `git pull` dell'agente. Se l'agente si rompe, quel
    pulsante non arriva più, e non arriva più nemmeno una correzione.
  - Nessun segreto nelle risposte committate (il repository è pubblico).
  - Lo stato legge e basta (sola lettura).
  - Si vede in modo chiaro in quale ambiente gira il bot (`DRY_RUN`).

## Checklist A–F

### A. Limiti fissi e interruttori

- **Valori fissi di `bot/risk/hard_limits.py`: OK.** Non sono toccati. `git diff --stat -- bot/risk/ bot/config.py firebase/` è
  vuoto.
- **Nessun limite spostato in configurazione: OK.** Le costanti nuove sono soglie del testo dello stato, non limiti di rischio:
  `LIMITE_DELLA_RISPOSTA` 19.500 (`state_snapshot.py:89`), `GIORNI_TABELLE` 14 (`:90`), `MONETE_DA_PREZZARE_MASSIME` 12
  (`:943`). Non c'è nessuna variabile d'ambiente nuova.
- **Parametri della dashboard: NON APPLICABILE.** `bot/main.py` non fa parte di questa revisione.
- **Limiti di G1 sul demo: NON APPLICABILE.** `bot/portafoglio/demo_binance.py` non fa parte di questa revisione. È cambiato
  anche lui nella copia di lavoro, ma per un'altra revisione.
- **Pulsante che chiude tutto senza Firebase: OK.** Le prove:
  - `main()` fa `fetch` e avanti veloce come primo passo (`ops_agent.py:543-547`), prima di ogni richiesta. L'oscuramento gira solo
    dentro `render` (`:250`, chiamato a `:586`).
  - Il modulo si compila con Python 3.11, 3.12 (la versione della macchina: «python3.12» nelle risposte di `ops/results`) e 3.13.
  - I tempi crescono in modo lineare con la lunghezza del testo. Con le mie prove, Python 3.12:
    - testo normale di 4,86 milioni di caratteri: 0,93 s;
    - 15 testi ostili: fino a 0,17 s (intestazioni senza fine, finte righe di fine, virgolette aperte, un milione di caratteri
      casuali);
    - sullo stesso testo normale il codice di prima era più lento: 1,28 s contro 0,83 s; 1,69 s contro 1,10 s.
  - Anche un blocco resterebbe limitato: `TimeoutStartSec=1200` (`scripts/install_ops_agent.sh:57`).
  - Prove: `.../scratchpad/revisione_27nov/tempi_redact.py` e `vecchio_contro_nuovo.py`.

### B. Ordini

**NON APPLICABILE**: nessun codice degli ordini cambia.

- Lo stato non scrive niente su Firebase (`tests/test_stato_audit.py:283`).
- Lo stato chiede al demo solo letture, su quattro indirizzi (`:284`). La funzione di sola lettura è invariata
  (`state_snapshot.py:1094-1124`).
- La lettura nuova è una richiesta pubblica senza firma e senza intestazioni (`:958-959`). Non può toccare nessun conto.
- Protezione di G1 (stop sul conto e pulsanti): non toccata.

### C. Stato e resilienza

- **Ricostruzione da Binance, flussi in tempo reale, candele chiuse: NON APPLICABILE.** Lo stato è un resoconto. Per oggi la colonna
  nuova usa l'ultimo prezzo, e lo dice.
- **Errori delle interfacce: PROBLEMA (204, Basso).** Le letture pubbliche nuove non si fermano al primo 429 o 418. Le letture del
  demo restano come prima:
  - stop al primo 429 o 418 (`:1112-1119`);
  - finestra vietata dalle 23:50 alle 01:45 (`:1080`), rispettata anche dalle letture nuove (`:987`);
  - limite di peso (`:1071-1072`).
- **Una scrittura su Firebase che fallisce: OK.** Lo stato non scrive. Ogni parte nuova è chiusa in un `try` e, se fallisce,
  scrive «non letto (Tipo)» invece di fermarsi (`:305-308`, `:843-846`, `:980-1000`). Test `test_un_dato_rotto_non_ferma_lo_stato`.
- **Orologio della macchina: OK.** È un passo avanti: lo stato ora mostra se l'orologio è sincronizzato (`timedatectl`, `:293-312`;
  comandi senza shell, tempo massimo 5 s, `:250-256`). Sulla macchina non è stato provato, perché qui manca systemd: è nelle
  condizioni.

### D. Separazione fra paper, demo e conto vero

- **PROBLEMA (203, Medio).** Il `DRY_RUN` e il battito dell'unico processo del bot sono finiti sotto «Vecchio sistema (fermo dal 13
  ottobre)», al carattere 14.901 di 19.133 (`state_snapshot.py:153-159`).
- **La richiesta nuova a `fapi.binance.com` (l'indirizzo del mercato vero): OK.** È pubblica e senza chiave: non può mandare
  ordini né leggere un conto.

### E. Segreti e sicurezza

- **Nessuna chiave nelle risposte: OK.** È il cuore della modifica. Cosa fa adesso l'oscuramento:
  - toglie tutto il blocco della chiave privata (`ops_agent.py:80-94`), anche con le cifre nel nome (ED25519), con gli a capo
    scritti come `\n`, con data e processo del giornale di sistema davanti, e anche senza la riga di fine;
  - toglie le coppie fra virgolette `"NOME": "valore"` (`:95-102`) e lascia il testo leggibile come prima;
  - aggiunge `private[_-]?key` ai nomi (`:56`);
  - toglie le sequenze lunghe casuali (`:104-134`): restano gli hash dei commit, i percorsi e i numeri.
- **La regola dei nomi è equivalente a quella di prima.** Ho controllato il ragionamento: una corrispondenza dentro una parola
  implica sempre quella dall'inizio della parola. Il correttore ha misurato 0 differenze su 4.944 file.
- **Le risposte vere non cambiano.** La risposta 0778 è identica dopo l'oscuramento nuovo (mia prova), e anche le 777 risposte
  misurate dal correttore.
- **Limiti che restano e accetto:**
  - una chiave tagliata in testa lascia l'ultima riga corta (EC e RSA; per Ed25519 non resta niente);
  - `Authorization: Bearer` non è fra i nomi;
  - il token di Telegram negli errori di rete non è riconosciuto. Lo affronta `bot/execution/notifier.py`, cambiato nella copia di
    lavoro e non rivisto qui (domanda aperta 2).
- **Lo stato non stampa segreti.** Stampa `df`, `free` e `timedatectl` già letti, e gli errori del conto vero accorciati a 80
  caratteri, che passano comunque dall'oscuramento.
- **Chiavi di Binance senza prelievo e limitate all'indirizzo: da confermare con Alessio.** Non cambia niente. Le chiavi vere non
  sono limitate all'indirizzo (7 novembre).
- **Regole di Firebase pubblicate: da confermare con Alessio.** Non cambia niente.

### F. Test

- **Suite intera: OK.** Ho lanciato:
  `python3 -m pytest tests/ -q -p no:cacheprovider -x --deselect tests/test_demo_binance.py::test_firma_dei_tre_tipi_di_chiave`.
  Esito: **3054 passed, 6 skipped, 1 deselected in 197,87 s**.
  - La suite gira su tutta la copia di lavoro, quindi anche sulle modifiche degli altri correttori.
  - Il test escluso richiede la libreria delle chiavi `cryptography`, che in questo contenitore con Python 3.11 è rotta.
  - I 6 saltati sono le chiavi vere di `tests/test_ops_agent.py`. Li ho lanciati con Python 3.12 e con 3.13: 104 passed ogni volta.
- **Test dei limiti fissi:** sono dentro la suite (`tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_demo_binance.py`,
  `tests/test_conto_vero.py`) e passano.
- **Le mie prove sullo stato** (`.../scratchpad/revisione_27nov/test_prove_revisore.py`, 4 passed), con i dati finti del test:
  - lunghezza 19.133 caratteri: 367 di margine al ripiego e circa 830 al taglio dell'agente;
  - con il conto vero acceso, il ripiego scatta e lo stato fa 16.827 caratteri;
  - su GitHub, senza la chiave del demo, 14.755 caratteri;
  - l'oscuramento non cambia nessuna riga dello stato finto.
- **Mancano:**
  - un test sulla posizione del `DRY_RUN` e del battito (203);
  - un test sul 429 o 418 delle letture pubbliche (204);
  - un test del ripiego su GitHub (205).

## Problemi

### 203 — Medio — il battito del bot e il `DRY_RUN` finiscono sotto «Vecchio sistema (fermo dal 13 ottobre)»

- **File:** `scripts/state_snapshot.py:135-166` (riga del `DRY_RUN` `:157`, battito `:159`, titolo `:154`). Prima erano sotto
  «## Bot», in cima.
- **Cosa non va:**
  - `/bot_status/heartbeat` lo scrive a ogni giro l'unico processo del bot (`bot/main.py:2715`). È lo stesso processo che fa girare
    il demo con il suo stop sul conto e i suoi pulsanti, i paper e il conto vero.
  - `/bot_status/dry_run` è `settings.DRY_RUN` del processo intero (`bot/main.py:983`). Per il conto vero è una delle condizioni
    per mandare ordini.
  - Ora tutti e due stanno al carattere 14.901 di 19.133, sotto un titolo che dice «fermo». Il test lo vuole proprio lì:
    `tests/test_stato_audit.py:295`.
- **Scenario di guasto:**
  1. Il processo del bot si blocca. Lo stato scrive «stato: running (🔴 offline)» e un battito vecchio, ma sotto «Vecchio
     sistema (fermo dal 13 ottobre)».
  2. Chi legge (la sessione principale, il confronto del lunedì, il proprietario dal telefono) lo prende per normale: il vecchio
     sistema è fermo.
  3. Intanto il demo G1 da 1.000 USDT con leva 5 è senza stop sul conto e senza pulsanti, perché girano dentro quel processo.
  4. Allo stesso modo, un riavvio con `DRY_RUN` falso comparirebbe come un dato del sistema fermo.
- **Correzione suggerita alla sessione principale:**
  - In cima, subito dopo la riga della macchina, un blocco corto «## Il bot (un solo processo: paper, demo e conto vero)» con
    stato e online/offline, ultimo battito e `DRY_RUN` (circa 150 caratteri).
  - Nel vecchio sistema restano regime, equity, prezzi e GATE 1.
  - Un test: le tre righe vengono prima di «## Paper F5» e non stanno sotto «## Vecchio sistema». Il test della risposta tipica
    deve restare sotto i 19.500 caratteri.

### 204 — Basso — le letture pubbliche dei prezzi mark non si fermano al primo 429 o 418

- **File:** `scripts/state_snapshot.py:946-965` (`rendimenti_mark_giornalieri`). Un 429 diventa «non letta» (`:960-964`) e il giro
  passa alla moneta dopo, con 0,2 s di pausa, fino a 12 richieste.
- **Scenario di guasto:**
  1. Fuori dalla finestra vietata, l'indirizzo della macchina è al limite su `fapi.binance.com`, per esempio per uno scarico dei
     paper ripetuto dopo un errore.
  2. La prima richiesta riceve un 429, e lo stato ne manda altre 11 in circa 2 s.
  3. Per Binance chi non si ferma dopo un 429 rischia il blocco dell'indirizzo (418) su quell'indirizzo. Da lì i paper F5 e G1
     prendono i dati pubblici, e dai paper prendono la decisione il demo (G1) e il conto vero (F5).
  - La probabilità è bassa: 12 richieste da peso 1. È però l'unica lettura dello stato che non segue la regola «stop al primo
    429 o 418» (revisioni del 12 e del 14 novembre, problemi 80 e 84).
- **Correzione suggerita:**
  - al primo 418 o 429 si ferma il giro;
  - le monete rimaste si segnano non lette con «Binance 429: letture fermate (Retry-After ...)»;
  - un test con il finto `http`.

### 205 — Basso — il ripiego scatta anche su GitHub, dove nessuno taglia, e rimanda al file che sta scrivendo

- **File:** `scripts/state_snapshot.py:121-132`. Il ripiego vale anche per `python -m scripts.state_snapshot --publish-controllo`
  su GitHub (`.github/workflows/snapshot.yml:38`), che scrive `docs/state.md` intero.
- **Scenario di guasto:**
  1. Su GitHub lo stato supera i 19.500 caratteri, per esempio con il conto vero acceso e molti allarmi.
  2. `docs/state.md` perde le sezioni del vecchio sistema e scrive che «sono intere in docs/state.md», cioè in sé stesso.
  3. Quelle sezioni non si trovano più da nessuna parte.
  - Oggi su GitHub fa 14.755 caratteri (mia prova con i dati finti): non succede.
- **Correzione suggerita:** il ripiego solo dove c'è l'agente, cioè con `GITHUB_ACTIONS` diverso da «true» (o solo con
  `--no-write`). Più un test.

### 206 — Basso — l'«ultimo ribilancio» del conto vero può essere la chiave `in_corso`; i resti rifiutati non si vedono

- **File:**
  - `scripts/state_snapshot.py:777-779`: `max(chiavi)` su tutte le chiavi, senza il filtro dei giorni che usa
    `monete_mancanti_per_giorno` (`:909`, lunghezza 10).
  - `bot/portafoglio/conto_vero.py:879` (nel `HEAD`; `:890` nella copia di lavoro) scrive
    `ribilanciamenti/in_corso/scaduti_senza_mercato` quando gli ordini non hanno la chiave.
- **Scenario di guasto:**
  - «in_corso» viene dopo ogni data nell'ordine alfabetico. Nella mia prova la riga diventa «ultimo ribilancio in_corso: 0 ordini;
    rifiutati 0; ordini limite scaduti ...» e nasconde il ribilancio vero del lunedì. Oggi la chiave c'è sempre
    (`demo_binance.py:1645`), quindi è un caso raro.
  - In più, la copia di lavoro di `demo_binance.py` scrive ora i resti a mercato rifiutati in
    `ribilanciamenti/{chiave}/resti_rifiutati` (`:1843-1844`). Il correttore dello stato scrive che il bot non li scrive: è vero
    per il `HEAD`, non per la copia di lavoro. Lo stato del conto vero non li mostra.
- **Correzione suggerita:**
  - scegliere il massimo fra le chiavi con la forma di un giorno e mostrare `in_corso` a parte;
  - aggiungere `resti_rifiutati` alla riga quando si committa la modifica di `demo_binance.py`.

### 207 — Basso — il titolo del conto vero legge la strategia dal file, non dal processo che gira

- **File:** `scripts/state_snapshot.py:761-768` importa `STRATEGIA` dal file sul disco.
- **Scenario di guasto:** dopo un commit che cambia la strategia, e prima del riavvio, il titolo dice la strategia nuova mentre il
  bot esegue ancora quella vecchia.
- **Il dato giusto c'è già:** all'avvio il bot scrive `strategia` in `/<ramo>/avvio` (`demo_binance.py:1184`; nel `HEAD` `:944`).
- **Correzione suggerita:**
  - preferire `/conto_vero/avvio/strategia`, se c'è, e usare il file solo come ripiego;
  - se i due sono diversi, scriverlo: «nel codice F5, nel processo G1: manca il riavvio».

### Note, che non sono problemi

- **183 (Basso, 25 novembre: il titolo «G1 sul conto vero»):** si chiude al commit di questa modifica.
- **La colonna «senza le monete che il demo non ha» è una stima.** Usa i pesi di oggi anche per i giorni passati, e la riga lo
  dice. Il confronto del lunedì non deve usarla come prova finché il paper non pubblica i pesi di ogni giorno: è la voce di
  backlog proposta dal correttore. Decidere se vale come prova spetta a gate2-reconciler e a backtest-auditor, non a me.
- **Gli ordini di lettura sul demo sono cambiati.** Le tre sezioni che leggono il demo (esecuzioni, pesi, funding) ora girano una
  dopo l'altra, senza le letture del vecchio sistema in mezzo. Con il limite «peso già usato oltre 600» (`:1072`) potrebbe capitare
  più spesso un «non letto» nelle ultime due: va guardato nella prima risposta (condizione 3).

## Invarianti modificati

- **Percorso degli ordini: nessuno.** Restano invariati i limiti fissi, gli ordini, i pulsanti, lo stop sul conto, la sola lettura
  del demo nello stato, la finestra vietata e il blocco al 429 o 418 delle letture del demo.
- **Chi parla con Binance (sezione 1 della mappa):** in più c'è una lettura pubblica senza chiave dallo stato. È
  `GET fapi.binance.com/fapi/v1/markPriceKlines`: al massimo 12 per stato, solo fuori dalle 23:50-01:45 e solo se ci sono monete
  che il demo non ha (`state_snapshot.py:943-965`, `:984-991`).
- **L'oscuramento dell'agente (sezione 11 della mappa) è più forte.** Toglie il blocco intero delle chiavi, le coppie fra
  virgolette e le sequenze lunghe casuali (`ops_agent.py:50-146`). Le righe citate nella mappa per `ops_agent.py` si spostano di 70
  (`:349-353` diventa `:419-423`, `:473-477` diventa `:543-547`, `:271-303` diventa `:341-373`).
- **Come si mostra l'ambiente attivo:** il `DRY_RUN` è uscito dalla testa dello stato. Si sistema con il 203.

## Decisioni per Alessio

1. Nessuna decisione sui limiti.
2. **Da confermare fuori dal codice.** Su GitHub, nelle impostazioni del repository pubblico, accendere «secret scanning» e «push
   protection» (gratis per i repository pubblici). Sono una seconda rete dietro l'oscuramento dell'agente: dal codice non posso
   vedere se sono accese, e nemmeno l'audit l'ha verificato.
3. Restano da confermare come prima:
   - chiavi di Binance senza permesso di prelievo e, per le vere, limitate all'indirizzo della macchina (oggi non lo sono);
   - regole di Firebase pubblicate con i blocchi del demo e del conto vero.
4. Per il commit di questi due script non serve il suo ok: non c'è riavvio e non si toccano gli ordini. Va però saputo che
   l'agente della macchina cambia al primo giro dopo il commit.

## Domande aperte

1. **Numeri dei problemi.** Il compito chiedeva di partire dal 187. Ho usato 203-207 perché dal 188 al 202 sono già usati dal
   trader AI (`reviews/INDEX.md:15`); il 187 resta libero. Va bene così, o la sessione principale vuole rinumerare?
2. **`bot/execution/notifier.py` è cambiato nella copia di lavoro** (il token di Telegram fuori dal registro, punto 5 del
   rapporto del correttore dei segreti). È nel percorso degli ordini e chiede una revisione sua e un riavvio con l'ok di Alessio.
   Lo copre un'altra revisione di questo giro? La riga del 27 novembre nella mappa, scritta da un'altra revisione, parla di
   «telefono».
3. **La dimensione vera dello stato sulla macchina non la conosce nessuno** fino alla prima risposta «stato» dopo il commit: il
   correttore non l'ha potuto lanciare. Chi la chiede e chi controlla le righe della condizione 3?

## Condizioni

1. `scripts/ops_agent.py` e `tests/test_ops_agent.py` si possono committare da soli, con le md5 di questo rapporto (c8d9f508,
   3d3c4a62).
2. `scripts/state_snapshot.py`, `tests/test_stato_audit.py` e `tests/test_pesi_g1_oggi.py`: prima si corregge il 203, con il suo
   test, poi un riesame breve. I problemi 204-207 si possono correggere insieme oppure restano aperti come Bassi.
3. Dopo il commit dello stato si chiede una risposta «stato». Bisogna controllare che:
   - non ci sia la scritta «caratteri omessi»;
   - ci siano le righe «Le 10 monete con il funding più grande», «monete del paper G1 che il demo non ha avuto» e la tabella del
     funding per regolamento;
   - le tre sezioni che leggono il demo non siano «non letto»;
   - la riga della macchina abbia letto disco, memoria e orologio, e l'orologio risulti sincronizzato;
   - la lunghezza sia sotto i 19.500 caratteri.
4. Dopo il commit dell'agente, il battito `ops/heartbeat.md` deve continuare ad andare avanti, e la risposta seguente deve arrivare
   come sempre.
