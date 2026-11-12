# Revisione: la versione del conto vero approvata dalla dashboard, il «riparti» in due passi, i problemi 66, 72, 73 — 12 novembre 2026

## Riepilogo e verdetto

**APPROVE per il commit del codice spento** e per il riavvio che lo carica (il riavvio con l'ok di Alessio). **REQUEST CHANGES per
l'accensione.**

Perché il commit va bene: il conto vero resta spento e non può accendersi con questo cambio. Servono ancora l'interruttore
`ops/conto_vero_acceso` (assente), `DRY_RUN` falso, il capitale e le chiavi vere; l'approvazione su Firebase è una condizione in
più, non un interruttore. Prova con il bot vero costruito con i moduli del working tree: «spento: manca l'interruttore», nessun
cliente creato, 0 richieste di rete, tre giri in 0,00 s. Demo e paper: nessuna riga cambiata (`demo_binance.py`, `f5.py`,
`eventi.py` fuori dal cambio; `main.py` e `config.py` cambiano solo un commento e un testo). Nessun segreto. Suite intera: 2758
superati, 1 fallito (la firma, libreria del contenitore; passa con la libreria buona). Undici mutazioni a mano: tutte fanno
fallire un test.

Perché l'accensione no:
- **54 (parte ii), Alto, non chiuso** (il cambio lo dichiara chiuso): su Firebase scrive anche la chiave di amministratore, che
  ignora le regole; ce l'hanno il bot, l'agente della macchina (riletto dal branch ogni minuto) e quattro flussi di GitHub (uno
  parte a ogni push). Chi può spingere sul branch può far scrivere l'approvazione a uno di loro.
- **74, Medio, nuovo**: con un buco di Firebase di 20 secondi nel minuto sbagliato il conto vero salta il ribilancio del giorno, o
  lo lascia a metà senza il resto a mercato. Buchi così ci sono stati (5 novembre, quattro in quattro minuti).
- **70, Medio, aperto dall'8 novembre** e non toccato.
- Bassi nuovi 75, 76, 77; regole da pubblicare e provare (il resto del 60).

Chiusi: 66 (resto), 72, 73; il 60 nel codice (pulsanti e regole nel repository).

## Oggetto

- Branch `claude/brave-albattani-1b12fv`, modifiche non committate su HEAD `d0cf6bf` (codice del percorso = `ff89531`, la fase 2
  committata). Verificato oggi: in `ff89531` `conto_vero.py`, `main.py` e `ops_agent.py` sono identici alle copie riviste al terzo
  giro con il delta del 71; `demo_binance.py` e `config.py` identici alla copia del secondo giro (il terzo giro non li toccava).
- File toccati (esclusi `research/` e `audits/`): `bot/portafoglio/conto_vero.py` (656 → 913 righe), `bot/core/firebase_client.py`
  (+19: `leggi_rtdb_davvero`), `bot/config.py` (un testo), `bot/main.py` (un commento), `scripts/ops_agent.py` (tolto il tag),
  `scripts/state_snapshot.py` (allarmi anche senza stato), `firebase/database.rules.json` (+30), `tests/test_conto_vero.py` (91 test),
  dashboard: `ComandiContoVero.tsx` (nuovo), `SchedaStrategia.tsx`, `Strategie.tsx`, `RigaStato.tsx`, `lib/strategie.ts`,
  `globals.css`, `prova/dati.ts`.
- Invarianti coinvolti: la condizione (c) degli ordini del conto vero (il codice approvato); il «riparti» del conto vero; i
  comandi della dashboard e le regole di Firebase. Limiti fissi e limiti del conto vero invariati.

## Checklist A–F

### A. Limiti fissi e interruttori
- `bot/risk/hard_limits.py`, `circuit_breakers.py`, `kill_switch.py`: nessuna riga cambiata. **OK.**
- Nessun limite numerico spostato: leva, capitale, valore, stop, pavimento, pesi restano costanti con il test di guardia
  (`tests/test_conto_vero.py:161-194`, superato). La condizione del codice approvato passa da un tag di git a Firebase per scelta di
  Alessio («ok pulsante in dashboard»); è chiusa in sicurezza: senza risposta di Firebase non è mai approvato
  (`conto_vero.py:182-208`, `firebase_client.py:704-721`). **OK**, con il limite di 54 (ii) su chi può scriverla.
- Parametri della dashboard (`user_risk_settings`): non toccati. **NON APPLICABILE** (aperti dal primo avvio 11, 14, 17-20, 24).
- Limiti del demo e del conto vero come costanti nel codice: invariati. **OK.**
- Pulsante senza Firebase: il file `ops/conto_vero_chiudi_tutto` resta l'unico file di comando (`conto_vero.py:316`) e lo stop sul
  conto gira senza Firebase. **OK.** Il «riparti» ora c'è solo da Firebase (scelta: fermo resta fermo; ma vedi 76).

### B. Ordini
- Ribilancio, filtri, passi, «solo riduzione», identificativi, margine e leva: righe non toccate (mappa, sezione 7). **OK** come prima.
- Stop per posizione assente per G1: decisione già registrata per Alessio. **NON APPLICABILE** a questo cambio.

### C. Stato e resilienza
- Binance prevale su Firebase e sui file: invariato. **OK.**
- Lettura dell'approvazione: una seconda lettura subito, poi «non approvato» (`conto_vero.py:427-436`); allarme dopo 3 controlli
  (`:735-738`). Sicura, ma un «non approvato» passeggero vale come un blocco vero: **PROBLEMA 74**.
- Scritture su Firebase: `/conto_vero/versione` riscritta finché non arriva (`:457-474`, **OK**); allarme di creazione riscritto
  finché non arriva (`:891-913`, **OK**, 73); `/conto_vero/fermo` no: **PROBLEMA 76**.
- Chiamate senza tempo massimo: git 15 s (`:94`, `:163-165`; il primo che non risponde chiude il controllo); Firebase senza
  `httpTimeout` (120 s e un ritentativo di serie in `firebase_admin` 6.5.0). Il conto vero spento ora chiama Firebase ogni minuto:
  **PROBLEMA 75** (Basso).
- Il controllo del codice prima del primo giro vale «approvato»: **PROBLEMA 77** (Basso, latente).
- Orologio: invariato. **NON APPLICABILE.**

### D. Separazione fra paper, demo e conto vero
- Con `DRY_RUN` vero o senza interruttore il conto vero mai acceso non legge chiavi e non chiama Binance (prova del bot vero; test
  `test_la_versione_si_pubblica_anche_da_spento_senza_richieste_a_binance`, `:1410`). Indirizzo solo `fapi.binance.com` (`:126-131`).
  Avvio con `DRY_RUN` falso: invariato da `ff89531` (`config.py:791-813`). **OK.**

### E. Segreti e sicurezza
- Nessuna chiave, token o identificativo nel cambio: regole con i soli segnaposto (`REPLACE_WITH_YOUR_FIREBASE_UID`,
  `REPLACE_WITH_STOCK_FIREBASE_UID`), test di guardia `:1522-1568`; i commit della prova della dashboard sono inventati. **OK.**
- Regole nel repository (`firebase/database.rules.json:26-58`): radice in sola lettura per il proprietario, scrittura chiusa; i
  quattro comandi del conto vero solo al proprietario e validati (booleani; conferma solo cifre, al massimo 12, e solo con la
  richiesta già vera; versione `{commit: 40 caratteri esadecimali minuscoli, ora: numero}` e nient'altro); `/azioni` solo all'utente
  delle azioni. **OK.** Note minime: `ora` non è legata all'ora del server (`newData.val() === now` la legherebbe; il bot non la usa);
  `close_position_meta` senza validazione (di prima).
- Chi può scrivere davvero l'approvazione: **PROBLEMA 54 (ii)**.
- Regole pubblicate (foto di Alessio, `docs/conto_vero.md:85-90`): chiuse e con il suo identificativo, ma **senza** i blocchi del
  demo e del conto vero: oggi i pulsanti del conto vero (e del demo) verrebbero rifiutati. **Da confermare con Alessio** dopo la
  pubblicazione, provando ogni pulsante fino in fondo.
- Chiavi vere: prelievo e limite all'indirizzo della macchina **da confermare con Alessio** (come sempre).

### F. Test
- `python3 -m pytest tests/ -q`: **2758 passed, 1 failed in 214,69 s**; il fallito è `test_firma_dei_tre_tipi_di_chiave`
  (libreria `cryptography` del contenitore rotta), che passa con `PYTHONPATH=<cartella di lavoro>/cripto` (1 passed).
- Test dei limiti e della sicurezza: `tests/test_conto_vero.py`, `test_risk.py`, `test_sizing.py`, `test_sicurezza_avvio.py`,
  `test_strategie_restano_accese.py`, `test_kill_switch_levels.py`: **140 passed**.
- Mutazioni a mano (`giro12nov/mutazioni.py`), **11 su 11 fanno fallire un test**: ritardo dei redditi tolto (72), lo specchio di
  Firebase preso per risposta, senza il commit in memoria, conferma del «riparti» ignorata, file del «riparti» di nuovo letto,
  Firebase muto preso per «mai acceso» (66), allarme di creazione tolto (73), seconda lettura tolta, avvio non pulito ignorato,
  conferma non tolta all'entrata nel fermo, conferma non tolta dopo il «riparti».
- Dashboard: `tsc --noEmit` senza errori; nessuna costruzione né prova nel browser fatta qui.
- Prove del revisore (`giro12nov/test_prove_12nov.py`, `prova_bot.py`, `prova_firebase_muto.py`): S1, S2 (74), S3 (76), il bot
  vero spento, il conto delle chiamate a Firebase (75).

## Stato dei problemi delle revisioni precedenti

| N. | Esito | Evidenza |
|---|---|---|
| 54 (ii) | **aperto, Alto** (ridotto, non chiuso) | Sotto. |
| 60 (resto) | **chiuso nel codice** | Pulsanti, stato e versione del conto vero in dashboard (`ComandiContoVero.tsx`); regole nel repository. Resta la pubblicazione (fuori dal codice). |
| 66 (resto) | **chiuso** | Stato locale muto e Firebase muto: niente prima accensione (`conto_vero.py:525-530`, `:739-741`); test `:1151`; mutazione uccisa. |
| 70 | **aperto, Medio** | Non toccato: la traccia `acceso_dal` si scrive una volta senza conferma (`:813`), senza la traccia lo stop vale 0 (`:637-642`). |
| 72 | **chiuso** | Test `:1491`; tolto il ritardo il test fallisce. |
| 73 | **chiuso** | `/conto_vero/allarmi/creazione` riscritto finché non arriva, tolto alla creazione riuscita (`:878-913`); fotografia (`state_snapshot.py:679-690`); la dashboard lo mostra fra gli allarmi del conto vero; test `:1235`. |
| 51, 52 | aperti, Bassi (demo) | Non toccati. |

## Problemi

### 54 (parte ii) — Alto, aperto (blocca l'accensione, non il commit; decisione di Alessio)
- Dove: `conto_vero.py:19-27` e `:83-85` («su quel percorso di Firebase scrive solo lui»), `ComandiContoVero.tsx:10-12`,
  `lib/strategie.ts:194`. Le regole valgono solo per chi entra con un utente; la chiave di amministratore di Firebase le ignora. Ce
  l'hanno: il bot; `scripts/ops_agent.py:349-353` (usa il client del bot per il battito), riletto dal branch a ogni minuto senza
  riavvio; i flussi di GitHub `connectivity.yml:24`, `monitoring.yml:24`, `learning.yml:25`, `snapshot.yml:33` e `:43`
  (`snapshot.yml` parte anche a ogni push, `:10`).
- Scenario: una sessione spinge un commit che, in uno di quei programmi (per esempio `scripts/state_snapshot.py`, che gira a ogni
  push su GitHub), scrive `{commit: <quello in esecuzione>, ora}` in `/commands/conto_vero_versione_approvata`. Il bot lo legge
  entro un minuto e, con le altre condizioni, manda ordini veri con codice che Alessio non ha approvato. Allo stesso modo si
  possono scrivere la richiesta e la conferma del «riparti» (l'ora del fermo si legge da `/conto_vero/fermo`). Rispetto al tag è
  meglio: serve un cambio di codice visibile nel diff, non un `git push` di un nome. Ma non è «solo lui».
- Lo stesso vale oltre Firebase: l'agente della macchina che si rilegge dal branch può cambiare qualunque file della macchina,
  compreso l'ambiente del bot. Finché la macchina con le chiavi vere esegue da sola il codice spinto sul branch, chi spinge comanda il
  conto vero.
- Correzione (da scegliere con Alessio): per i soldi veri, una macchina (o almeno un'installazione) che non esegue da sola il codice
  del branch: il bot del conto vero e l'agente partono da una copia che aggiorna solo Alessio; la chiave di amministratore fuori
  dai flussi di GitHub (o un progetto Firebase separato per il conto vero, senza chiave su GitHub). Subito, a costo zero: correggere
  i commenti (dire «solo lui dalla dashboard; la chiave di amministratore no») e aggiungere un test che nessun file Python né flusso
  del repository scriva i quattro comandi del conto vero.

### 74 — Medio, nuovo — Un buco di Firebase di pochi secondi fa saltare il ribilancio del giorno o lo lascia a metà
- Dove: `conto_vero.py:427-436` (due letture perse = «non approvato» per tutto il minuto), `:799-805` (un motivo segna `blocco` e,
  scaduta l'ora, annulla gli ordini limite senza resto a mercato), `:806-814` (alla fine del blocco si aspetta la decisione di G1
  dopo: `ultimo_giorno` = quella di oggi).
- Prova S1: conto acceso e approvato, Firebase muto per un solo controllo nel minuto della decisione di G1, poi di nuovo vivo:
  **0 ordini quel giorno** (`ultimo_giorno` = 20752, il giorno della decisione); senza il buco, 4 ordini lo stesso giorno; si
  ricompra solo il giorno dopo. Prova S2: Firebase muto nel minuto in cui scade l'ora degli ordini limite: «ordini limite scaduti
  annullati, niente resto a mercato (2 monete)».
- Perché capita: il 5 novembre il bot ha scritto quattro buchi di Firebase in quattro minuti (16-22 s ciascuno, «Internal server
  error»), `ops/results/0700-5nov-log-bot-dopo-riavvio-entrate.md:49-55`. Con il tag (un riferimento locale) un blocco veniva solo
  da un cambio vero; ora viene anche da un errore passeggero della rete.
- Danno: giorni di G1 saltati (il conto vero si allontana dalla ricerca e dal paper) o un ribilancio a metà, con un lato eseguito e
  l'altro no fino al giorno dopo (esposizione in una direzione, con leva 5).
- Correzione: «Firebase non risponde» è un motivo passeggero: niente ordini in quel giro, ma senza segnare `blocco` (quindi senza
  saltare al giorno dopo) e senza annullare gli ordini limite allo scadere dell'ora (il resto a mercato aspetta qualche minuto, con
  un massimo, poi vale il blocco). In alternativa, decisione di Alessio: un'approvazione letta davvero negli ultimi 10 minuti vale,
  se il confronto con git dà ancora «uguale». Test: S1 e S2 come test.

### 75 — Basso, nuovo — Il conto vero spento chiama Firebase ogni minuto, nello stesso filo del demo
- Dove: `conto_vero.py:405` (il controllo anche da spento), `:427-430` (seconda lettura subito), `:467-474` (riscrittura finché non
  arriva). Prova `prova_firebase_muto.py`: con Firebase muto, conto vero spento e mai acceso, 5-6 chiamate al minuto (3 nuove: due
  letture della versione e una scrittura; le altre 2 per giro sono quelle del 66, di prima). Con Firebase che risponde: 1 lettura
  al minuto.
- Scenario: Firebase che non risponde affatto (rete che perde i pacchetti): ogni chiamata dura fino a 120 s più un ritentativo
  (`firebase_admin` 6.5.0, `_http_client.py:33-37`); il giro del bot si allunga di minuti e lo stop sul conto del demo si controlla
  più di rado. Il demo ha già le sue chiamate che si allungano allo stesso modo; il conto vero spento ne aggiunge.
- Correzione: da spento e mai acceso, controllo ogni 10 minuti; niente seconda lettura se la prima è durata più di qualche secondo;
  niente riscrittura di `/conto_vero/versione` mentre Firebase è muto. A parte (cambio da rivedere): un tempo massimo per Firebase
  all'avvio del client.

### 76 — Basso, nuovo — Se il fermo non arriva su Firebase, il «riparti» dalla dashboard non si può fare
- Dove: il fermo si scrive su Firebase all'entrata e al primo conto vuoto, senza guardare se arriva (`demo_binance.py:776`, `:789`,
  `:1039`); la dashboard calcola la conferma dall'ora di `/conto_vero/fermo` (`ComandiContoVero.tsx:69`); il file del «riparti» non
  c'è più.
- Prova S3: scritture perse durante il fermo, poi Firebase di nuovo vivo: fermo e vuoto nel file, `/conto_vero/fermo` assente su
  Firebase. La dashboard non mostra il fermo né il «Riparti»; un «Chiudi tutto» da fermo non crea un fermo nuovo
  (`demo_binance.py:956-958`). Il conto resta fermo finché qualcuno non cambia il codice o lo stato a mano. Lato sicuro, ma senza
  uscita.
- Correzione: nel conto vero riscrivere `/conto_vero/fermo` finché la scrittura non arriva (come `/conto_vero/versione`).

### 77 — Basso, nuovo, latente — Prima del primo controllo il codice vale «approvato»
- Dove: `conto_vero.py:355` (`_codice_ora` parte da `_codice_all_avvio`, che ora vuol dire «avvio pulito», non «approvato»).
  Oggi non succede niente: `tick` fa il controllo prima di tutto (`:405`, `_codice_controllato` = 0). Ma chi un domani chiamasse
  `motivo_niente_ordini` prima di `tick` avrebbe «nessun motivo».
- Correzione: far partire `_codice_ora` da «versione approvata non ancora letta».

## Le due domande di chi ha scritto il cambio

1. **Approvare un commit sblocca gli ordini senza riavvio: va bene?** Sì. Il controllo lega l'approvazione al codice in memoria:
   all'avvio i file caricati devono essere quelli di HEAD e non cambiati dopo l'avvio (`:346-351`), poi ogni minuto il commit
   approvato deve essere uguale a quello in memoria e ai file di adesso (`:435-436`, `:249-266`; test `:1355`, mutazione uccisa). Il
   primo acquisto aspetta comunque la decisione di G1 dopo (test `:1344-1351`). Il riavvio non aggiungerebbe sicurezza. Due avvertenze:
   il pulsante approva «quello che gira», senza dire se il revisore lo ha approvato (vedi le decisioni); e un buco di Firebase vale
   come un blocco (74).
2. **Git ogni minuto anche da spento (15 s al massimo): accettabile?** Sì per git: gira solo se un'approvazione c'è (senza, il
   controllo si ferma alla lettura di Firebase: tre giri in 0,00 s nella prova del bot vero); sono quattro-cinque comandi locali e
   al primo che non risponde il controllo finisce, quindi al massimo 15 s al minuto. Il peso vero è Firebase, non git: 75.

## Invarianti modificati

- **Condizione (c) degli ordini del conto vero**: da «codice uguale al tag `conto-vero-approvato`» a «codice in memoria = HEAD
  all'avvio, pulito, e uguale al commit scritto in `/commands/conto_vero_versione_approvata`, letto davvero da Firebase ogni minuto».
  Firebase muto = non approvato. L'approvazione vale dal minuto dopo, senza riavvio.
- **«Riparti» del conto vero**: da «solo il file `ops/conto_vero_riparti`» a «solo dalla dashboard, in due passi» (richiesta e
  conferma uguale all'ora del fermo in secondi interi). Nessun file.
- **Agente della macchina**: non porta più il tag (vale sulla macchina dal primo `git pull`).
- **Regole di Firebase nel repository**: quattro comandi del conto vero e `/azioni`.
- Limiti fissi, limiti del demo e del conto vero: invariati.

## Decisioni per Alessio

1. **Chi può approvare i soldi veri (54 ii)**: la dashboard lega l'approvazione a te, ma la chiave di amministratore di Firebase (il
   bot, l'agente della macchina che si aggiorna da solo, quattro flussi di GitHub) la può scrivere lo stesso, e chi spinge sul branch
   può far girare quel codice. Scegli: (a) accettarlo: l'approvazione protegge dagli errori, non da una sessione che volesse
   aggirarla; (b) per i soldi veri, un'installazione che non esegue da sola il codice del branch (la aggiorni solo tu) e la chiave di
   amministratore fuori da GitHub. Raccomando (b) prima della prima accensione.
2. **Il buco di Firebase (74)**: (a) un errore passeggero ferma gli ordini solo per qualche minuto, senza saltare il giorno
   (raccomandato); oppure (b) vale un'approvazione letta negli ultimi 10 minuti.
3. **Il pulsante «Approva»**: oggi mostra solo il commit, la data e il titolo. Raccomando che mostri anche i file cambiati rispetto
   all'ultima versione approvata e se il revisore ha dato APPROVE a quel commit, e un pulsante «Revoca».
4. **Le regole**: pubblicare quelle del repository con il tuo identificativo (e quello dell'utente delle azioni), compresi i due
   blocchi del demo che mancano dal 7 novembre, poi provare ogni pulsante fino in fondo.
5. **70, ancora aperto**: prima della prima accensione, con posizioni nel conto, lo stop deve chiuderle? Raccomando di sì.
6. **Il riavvio che carica questo codice**: con il tuo ok. Aggiunge una lettura di Firebase al minuto e qualche comando git
   all'avvio; nessuna richiesta a Binance da spento.

## Domande aperte

- Le regole con i blocchi nuovi sono pubblicate? Con quale utente? (da confermare con Alessio; oggi, dalla foto, no.)
- Sulla macchina git gira con lo stesso utente che possiede la cartella? Se no, il commit in esecuzione non si legge e il conto vero
  resta bloccato per sempre (lato sicuro). Dopo il riavvio basta guardare `/conto_vero/versione`: deve avere il commit e
  `pulito: true`.
- Le chiavi vere sono sulla macchina? Prelievo spento? Limitate all'indirizzo della macchina? (da confermare con Alessio)
- Restano quelle di prima: con quale identità si spinge su GitHub; utente e lingua di git sulla macchina; modo del conto dei future;
  come risponde `/fapi/v1/income` sul conto vero; G1 o G1 neutra; la proposta della leva a 10 da chiudere come «non applicata».
