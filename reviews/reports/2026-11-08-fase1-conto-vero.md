# Revisione della fase 1 del conto vero (modifiche non committate, 8 nov 2026)

Revisore: `live-path-reviewer`. Oggetto: `git diff HEAD -- bot/portafoglio/demo_binance.py scripts/state_snapshot.py
tests/test_demo_binance.py dashboard/app/components/PaperBot.tsx` sul branch `claude/brave-albattani-1b12fv`, HEAD `4f866a1`.
Le modifiche in `research/` (processo in sottofondo) sono fuori dalla revisione.

### Riepilogo e verdetto

**REQUEST CHANGES.** Un problema Alto nuovo, introdotto da queste modifiche (40): con Binance che limita le richieste proprio mentre
lo stop sul conto chiude le posizioni, il demo non resta fermo. Chiude metà del portafoglio, si interrompe senza salvare il fermo e, se
il conto risale sopra la soglia nei 2 minuti di attesa, riprende come se niente fosse con un solo lato aperto; l'allarme si cancella
al giro dopo. Sul codice di prima lo stesso caso lasciava il demo fermo e chiudeva il resto nei minuti seguenti (prova p1). La
correzione è breve: segnare e salvare il fermo prima delle chiusure.

Gli 11 problemi dichiarati:

| Problema | Esito | Evidenza |
|---|---|---|
| 36 (niente «vuoto» senza lettura riuscita) | **chiuso** | `demo_binance.py:811-832`, test `:830` (fallisce sul codice di prima) |
| 37 (guasto di rete sulla lettura degli ordini da fermo) | **chiuso** | `:813`, `:859`, test `:858` («rete» fallisce sul codice di prima) |
| 38 (allarme degli ordini bloccati che non si spegne) | **chiuso**, con un resto Basso (46) | `:908-922`, `:1122-1124`, `:1164`, test `:887`, `:900` |
| 10 (pesi senza controllo) | **chiuso in parte** (42) | `:125-146`, `:701-705`, test `:919`, `:933` |
| 12 (età della decisione di G1) | **chiuso** (un resto Basso: 45) | `:743-757`, test `:943`; prova p8 |
| 13 (429 e 418) | **chiuso per 429 e 418, ma con la regressione Alta 40**; resto Basso 44 | `:380-413`, `:681-683`, `:721-741`, test `:964-1020` |
| 15 (massimo dello stop solo in locale) | **chiuso** | `:589-617`, `:783`, test `:1022` (vero: prova a parte sul codice di prima) |
| 16 (capitale senza tetto, filtri fissi) | **chiuso in parte** (41, Medio) | `:447-468`, `:1023-1028`, test `:1067`, `:1090`; prova p10 |
| 21 (indirizzo firmato nei messaggi) | **chiuso** | `:118-122`, `:391-401`, test `:1110` |
| 22 (minimo scritto a mano, filtri a mercato, leva, log d'avvio) | **chiuso in buona parte** (43) | `:165-199`, `:935-941`, `:971-991`, `:759-768`, test `:1162-1207` |
| 23 («riparti» senza pavimento) | **chiuso come chiesto**; il limite vero di perdita è circa −58% (decisione) | `:800`, `:838-850`, test `:1209`; prova p5 |

Test: suite intera `2597 passed, 1 skipped, 1 deselected` in 180 s (il deselezionato è il test delle firme, lanciato a parte con la
libreria indicata: `1 passed`). Dei 34 test nuovi o cambiati in `tests/test_demo_binance.py`, 29 falliscono sul codice di prima: sono veri.
Non c'è un test per il caso del problema 40.

Limiti fissi: `bot/risk/hard_limits.py` invariato; nessun file in `bot/risk`, `bot/config.py`, `bot/main.py`, `bot/execution`, `firebase/`,
`ops/` toccato.

### Oggetto (branch, commit, file toccati, invarianti coinvolti)

- Branch `claude/brave-albattani-1b12fv`, base `4f866a1` (il codice del demo a HEAD è uguale al `013f9426` già rivisto: `git diff
  013f9426 HEAD -- bot/ firebase/` vuoto). Modifiche non committate.
- File: `bot/portafoglio/demo_binance.py` (+389 −56 circa), `tests/test_demo_binance.py` (+458), `scripts/state_snapshot.py` (+6),
  `dashboard/app/components/PaperBot.tsx` (+13).
- Invarianti coinvolti: stop sul conto (riferimento del massimo, blocco del fermo), pulsante che chiude tutto, «riparti», dimensioni e
  filtri degli ordini, leva e modo delle posizioni, capitale del conto ridotto, pesi di G1, comportamento con i limiti di Binance.

### Checklist A–F

**A. Limiti fissi e interruttori**
- Valori di `hard_limits.py` invariati: **OK** (`git diff HEAD --stat` elenca solo i 4 file e due di `research/`).
- Nessun limite critico spostato fuori dal codice: **OK**. Le costanti nuove sono nel codice (`demo_binance.py:84-94`). Il massimo dello
  stop ora vive anche su Firebase (`/demo_binance/massimo`, `:589-617`), ma Firebase può solo alzarlo, mai abbassarlo (`:615`): più
  prudente. Chi può scrivere su Firebase può già premere il pulsante, quindi nessun potere nuovo.
- Parametri della dashboard (`user_risk_settings`, vecchio bot): **NON APPLICABILE** a questa modifica (Problema 17 aperto, invariato).
- Limiti di G1 come costanti: **OK, ma fuori da `hard_limits.py`** (`:73`, `:80`, `:84-94`); nessun test di guardia li fissa tutti (la
  leva 5 e il tetto 10.000 sono controllati solo dal test del log d'avvio, `tests/test_demo_binance.py:1200`). Decisione per Alessio.
- Pulsante che chiude tutto senza Firebase: **OK** (comando a file). Con un 418 o un 429 che dura il comando si riprova dopo l'attesa
  perché il testo del file non è salvato come eseguito (prova p2: fermo dopo 2 minuti, conto vuoto). **PROBLEMA** per lo stop sul conto:
  non resta fermo (40).

**B. Ordini**
- Passi, minimi, massimi dalle informazioni del simbolo: **OK con resti**. Il valore minimo non è più scritto a mano (`:172`); gli ordini
  a mercato dei resti usano `MARKET_LOT_SIZE` e la quantità massima (`:1115`, `:1134-1140`); i limite la quantità massima di `LOT_SIZE`
  (`:1029`, `:1047-1048`). Le chiusure di `_chiudi_posizioni` (`:868-874`), `parti_da_zero` (`:530-536`) e `controlla_margine`
  (`:962-963`) mandano ancora la quantità piena senza guardare il massimo (43).
- Identificativo riusato nei tentativi: **OK**. Nei ritentativi dopo un 429 si rimanda lo stesso `newClientOrderId` (prova p4:
  `g1d-20750-400-BUSDT` tre volte); una nuova firma e un nuovo orario a ogni tentativo (`:385-390`).
- «Solo riduzione»: **OK**, invariato.
- Prezzo che attiva gli stop: **NON APPLICABILE** (nessuno stop per posizione; lo stop sul conto usa `totalMarginBalance`).
- Leva e margine espliciti: **OK**. Ora la leva delle monete con posizione e il modo a due lati si rileggono ogni ora (`:971-991`, test
  `:1185`); il modo a due lati fa solo ricontrollare il modo al ribilancio dopo.
- Protezione di G1 (stop sul conto e pulsante): esistono; **PROBLEMA** 40 sullo stop. Stop per posizione assenti: decisione per Alessio
  (invariata).

**C. Stato e resilienza**
- Stato di Binance per primo: **OK**, invariato; il massimo dello stop non si perde più con il file (`:599-617`; prova a parte: sul
  codice di prima con il file perso lo stop a −35,2% non scatta, sul nuovo sì). Passaggio dal file di oggi (massimo senza `massimo_dal`):
  il massimo resta e si scrive su Firebase (prova p6).
- Flussi in tempo reale: **NON APPLICABILE** (il demo non ne usa).
- Candele chiuse: **NON APPLICABILE** a questo modulo (decide il paper di G1 sui giorni chiusi).
- Errori delle interfacce: **PROBLEMA**. 429 e 418: ritentativi 1-2-4 secondi o l'attesa chiesta da Binance fino a 10 secondi, poi
  `LimiteBinance`, nessuna richiesta per almeno un minuto (o quanto chiede Binance), allarme (`:380-413`, `:730-741`). Nessun tentativo
  infinito. Però: regressione sullo stop (40); nessun tetto all'attesa chiesta (prova: un `Retry-After` di 86.400 secondi ferma le
  protezioni 24 ore) e gli errori d'orario (-1021) non sono gestiti (44).
- Firebase che non risponde non blocca le chiusure: **OK** (`_unisci_massimo` prende ogni errore, `:606-610`; le scritture non sollevano).
- Orologio: **NON APPLICABILE** (nessun cambiamento).

**D. Separazione fra paper, demo e conto vero**
- **OK**, invariata: `_url` (`:111-115`) rifiuta ogni indirizzo diverso dal demo; il log d'avvio ora dice indirizzo, leva, stop,
  capitale e limiti, nel log e in `/demo_binance/avvio` (`:759-768`).

**E. Segreti e sicurezza**
- **OK.** Nessuna chiave nel codice o nei test (la «firma» `deadbeef…` del test è finta). Gli errori di rete escono senza la parte firmata
  dell'indirizzo (`:391-401`), anche su Firebase e nel log (test `:1110`); gli errori di Binance non contenevano già l'indirizzo
  (`:412`). La chiave sta nell'intestazione, mai nei messaggi.
- Chiavi senza prelievo e limitate all'indirizzo: **da confermare con Alessio** (invariato: quelle vere non sono limitate all'indirizzo).
- Regole di Firebase: **da confermare con Alessio** (mai pubblicate, utente segnaposto). Il ramo nuovo `/demo_binance/allarmi` si legge
  con la regola di lettura di tutto il database (`firebase/database.rules.json:3`).

**F. Test**
- `python3 -m pytest tests/ -q -p no:cacheprovider --deselect tests/test_demo_binance.py::test_firma_dei_tre_tipi_di_chiave`:
  `2597 passed, 1 skipped, 1 deselected in 180.54s`. Test delle firme con `PYTHONPATH=…/scratchpad/cr`: `1 passed`. Test dei limiti
  fissi e dell'avvio (`tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_sicurezza_avvio.py`) insieme al demo: `95 passed`.
- Test veri: i test nuovi copiati sull'albero di HEAD (`git archive HEAD`) danno **29 fallimenti su 63**. Falliscono per il
  comportamento (non solo per i rami nuovi di Firebase): 10 (ordini partiti), 12 (ordini partiti a 27 ore), 13 (429 diventato rifiuto),
  15 (stop non scattato dopo il file perso: provato a parte), 16 con «50000» e «inf» (capitale accettato), 21 (firma su Firebase), 22
  (BUSDT trattato con 5 USDT, quantità oltre il massimo, leva non rimessa), 23 (ripartito sotto il pavimento), 36, 37 «rete», 38 (h5).
  Con «abc» e «-280» il capitale era già rifiutato prima: lì il test controlla solo l'allarme nuovo.
- I cinque test vecchi passati da 429 a 400 (-1021): cambio legittimo. Ho lanciato i test di HEAD (con il 429) sul codice nuovo: 6
  falliscono perché il loro 429 vale una volta sola e ora si riprova con successo (più quello del «riparti», per il pavimento).
- **Non coperti**: stop o chiudi tutto con un limite di Binance che dura durante le chiusure (40); da fermo con un limite che dura (40);
  capitale oltre il saldo (41); pesi vuoti (42); attesa senza tetto (44); data nel futuro (45).
- Dashboard: compilazione non verificata (la lettura di `dashboard/node_modules` è vietata); il codice usa `quando` e `nome` già
  definiti (`PaperBot.tsx:42`, `:51`).

Prove a mano (`/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/fase1/prove_fase1.py`,
`prova_15.py`, `prova_bordi.py`; copia di HEAD in `fase1/vecchio/`):

| Prova | Caso | Codice nuovo | Codice di prima |
|---|---|---|---|
| p1 | Stop a −36%, 429 che dura sulla chiusura di BUSDT, poi il conto risale a −34% | non fermo; AUSDT chiuso, BUSDT −99,986 aperto anche 10 minuti dopo; allarme dei limiti già tolto | fermo subito, BUSDT chiuso nei minuti dopo |
| p1 bis | Come p1, senza risalita | fermo dopo l'attesa, tutto chiuso | fermo subito, tutto chiuso |
| p2 | Chiudi tutto da file, 418 sulla lettura degli ordini | fermo dopo 2 minuti, tutto chiuso | fermo subito |
| p3 | Da fermo, 429 che dura sulla chiusura di BUSDT, 10 minuti | tentativi fermi a 1, nessun allarme del fermo (solo quello dei limiti) | 11 tentativi, allarme del fermo |
| p4 | Due 429 sull'ordine di BUSDT | stesso identificativo nei 3 invii | — |
| p5 | Stop a 6.500, «riparti», secondo stop a 4.225 | «riparti» accettato a 6.500, rifiutato a 4.225: perdita possibile 57,8% | — |
| p6 | File di oggi senza `massimo_dal`, Firebase vuoto, conto a 6.800 su 10.500 | stop a −35,2%, massimo scritto su Firebase | — |
| p7 | 429 che dura su CUSDT a metà ribilancio | stato non salvato; 30 minuti dopo il ribilancio riparte, AUSDT non raddoppia, CUSDT aperto | CUSDT rifiutato e mai aperto quel giorno |
| p8 | Decisione di ieri, alle 01:59 e alle 02:01 | allarme solo alle 02:01 | — |
| p9 | File di G1 con pesi vuoti | tutto chiuso, nessun allarme | uguale |
| p10 | Conto demo 5.000, capitale nel file 9.999 | accettato: ordini per il 197% del saldo vero | uguale |
| bordi | Decisione con data 99999, poi quella vera | ordini eseguiti col giorno 99999, poi mai più, nessun allarme | uguale |
| bordi | 429 con `Retry-After: 86400` | protezioni ferme 24 ore | — |

### Problemi

**Problema 40 — Alto (introdotto da questa modifica) — `demo_binance.py:640-654` con `:852-875`, `:675-683`, `:730-741`: con Binance
che limita le richieste durante le chiusure, lo stop sul conto non resta fermo.**
- Prima, un 429 sulla chiusura di una moneta era un `RuntimeError`: preso moneta per moneta, il fermo si segnava, il resto si richiudeva
  ogni minuto. Ora un 429 che dura (4 risposte in 7 secondi) o un 418 diventa `LimiteBinance`, che non è un `RuntimeError`: esce da
  `_chiudi_posizioni` e da `chiudi_tutto` **prima** che `st["fermo"]` sia scritto (`:647`), e `tick` non salva lo stato (`:681-683`,
  `_limite_di_binance` lo dice apposta).
- Scenario (prova p1): il conto scende a −36%. Lo stop chiude AUSDT; la chiusura di BUSDT riceve 429 di fila. Nessuna richiesta per 2
  minuti, nessun fermo salvato. Nei 2 minuti il conto risale a −34%: al giro dopo lo stop non scatta. Il demo resta acceso con il solo
  short di BUSDT (G1 è un portafoglio con i due lati: ora ne ha uno solo), l'allarme dei limiti si toglie al primo giro buono (`:679`),
  e non resta traccia che lo stop è scattato. Alla decisione di G1 dopo il demo riapre tutto senza il «riparti» del proprietario.
- Se il conto non risale, lo stop riscatta dopo l'attesa e chiude tutto (p1 bis): la perdita non supera il −35% di molto, ma la regola
  «stop → fermo fino al riparti» non vale più, e il conto può restare con un lato solo fino al giorno dopo.
- Lo stesso schema da fermo (prova p3): i tentativi non crescono (restano a 1 per 10 minuti), quindi l'allarme «fermo ma il conto non è
  vuoto» non arriva mai; si vede solo l'allarme dei limiti. Meno grave: `controlla_margine` (`:958-968`) con un limite fra la chiusura
  e il cambio di margine lascia la moneta chiusa fino alla decisione dopo.
- Perché Alto: tocca l'unica protezione di G1, nel momento in cui serve (un crollo è anche il momento dei limiti di Binance), ed è una
  regressione introdotta qui.
- Correzione suggerita alla sessione principale:
  - in `chiudi_tutto`, scrivere `st["fermo"]` (con `tentativi: 0`, `chiuse: 0`), pulire il «riparti», scrivere `/demo_binance/fermo` e
    **salvare lo stato prima** di `_chiudi_posizioni`; poi aggiornare chiuse ed errori e salvare di nuovo;
  - prendere `LimiteBinance` intorno a `_chiudi_posizioni` in `chiudi_tutto` e in `_da_fermo`: segnare l'errore e il tentativo in
    `fermo`, salvare, poi rilanciare (così l'attesa resta e `_da_fermo` riprende dopo);
  - test: p1 con la risalita (il demo resta fermo e BUSDT si chiude dopo l'attesa) e p3 (i tentativi crescono e l'allarme del fermo
    arriva al terzo).

**Problema 41 — Medio (resto del 16, non introdotto qui) — `demo_binance.py:447-468`, `:498-515`, `:543-550`: il capitale del file non
si confronta con il saldo.**
- Il tetto di 10.000 USDT c'è; il confronto con il saldo vero, chiesto dal 16, no.
- Scenario (prova p10): conto demo da 5.000, nel file 9.999. Il capitale si accetta, lo scarto diventa negativo e il demo apre posizioni
  come per 9.999. Risultato: ordini per il 197% del saldo vero invece del 100%; lo stop a −35% di 9.999 vale −70% del saldo vero.
- Sul conto vero, con 250 euro, un file a 10.000 vorrebbe dire 40 volte il saldo. Binance rifiuterebbe una parte degli ordini per
  margine insufficiente, lasciando un portafoglio a metà e con una leva molto alta.
- Oggi sul demo non succede (capitale 1.000, conto demo più grande). Non è una condizione per questa modifica, ma va fatto prima del
  conto vero.
- Correzione: in `parti_da_zero`, rifiutare il capitale (allarme `capitale`, fase in corso tenuta) se è sopra `valore vero` del conto
  appena letto; scegliere con Alessio il tetto per il conto vero.

**Problema 42 — Basso (resto del 10) — `demo_binance.py:125-146`, `:84`: il controllo dei pesi non guarda le monete per lato, e il 250%
vale anche con gli eventi spenti.**
- Pesi vuoti passano: il demo chiude tutto senza allarme (prova p9). Succede se il paper scrive `pesi: {}`, per esempio con meno di 20
  monete valide (`f5.py:132-133`).
- Un lato con una moneta sola sopra il 60% fa rifiutare tutta la decisione: è voluto, ma va detto ad Alessio.
- Con gli eventi spenti (oggi) G1 vale 200%: un errore che porta i pesi al 240% passa.
- Con più di 5 operazioni a eventi aperte si supera il 250% e si rifiuta anche G1.
- Correzione: limite di somma 2,0 più 0,10 per ogni operazione a eventi aperta; numero minimo di monete per lato (idea 97 della coda);
  pesi vuoti → allarme.

**Problema 43 — Basso (resto del 22) — `demo_binance.py:868-874`, `:530-536`, `:962-963`, `:165-176`.**
- Le chiusure (pulsante, stop, cambio di capitale, margine separato) mandano la quantità piena senza la quantità massima di
  `MARKET_LOT_SIZE`. Sopra quel massimo Binance rifiuta e la chiusura fallisce ogni minuto. Con 1.000 USDT oggi non succede.
- Una moneta senza il filtro del valore minimo esce da `f`. Se ha una posizione aperta, il ribilancio non la riduce più
  (`ordini_del_giorno` la salta, `:224`). La chiude solo il pulsante.
- Correzione: chiusure divise in pezzi dentro il massimo; per le monete con posizione e senza filtri, un allarme.

**Problema 44 — Basso (resto del 13) — `demo_binance.py:363-370`, `:404-410`, `:734-735`.**
- L'attesa chiesta da Binance non ha un tetto: un `Retry-After: 86400` su un 429 ferma pulsante e stop per 24 ore (prova). Per un 418
  è giusto (l'indirizzo è bloccato comunque); per un 429 no.
- Gli errori d'orario (-1021) restano un rifiuto qualunque; l'ora di Binance non si legge mai.
- Correzione: tetto all'attesa dei 429 (per esempio 5 minuti, poi si riprovano le protezioni); con -1021 leggere `/fapi/v1/time` e
  correggere lo scarto.

**Problema 45 — Basso — `demo_binance.py:747-754`, `:706`: una decisione di G1 con una data nel futuro blocca il demo per sempre, senza
allarme.**
- Il controllo dell'età guarda solo il passato. Con `ultimo_lunedi` = 99999 il demo esegue i pesi, segna quel giorno e poi non esegue
  più nessuna decisione vera, senza allarme (prova).
- C'era già prima.
- Correzione: una data oltre l'ora di adesso più un'ora → allarme `decisione_g1` e niente ordini.

**Problema 46 — Basso — allarmi che restano accesi o comandi persi.**
- L'allarme `ordini` resta se il pulsante toglie gli ordini mentre il blocco è in corso (`:646`): si spegne solo alla fine di un
  ribilancio completo dopo il «riparti».
- Con il file dello stato perso, gli allarmi già scritti su Firebase non si spengono più (`st["allarmi"]` perso; `_accesi` all'avvio ha
  solo `limiti_binance`, `:431`).
- Il «riparti» della dashboard si consuma prima del controllo del pavimento (`:800`, `_riparti` `:894-906`): se quel controllo va in
  errore (per esempio un limite di Binance su `_conto`), il comando è perso e il proprietario deve ripremerlo.
- Il blocco degli ordini conta come «di fila» se fra due blocchi passano esattamente 3.600 secondi (`:915`, maggiore stretto): un caso
  di confine.
- Correzione: spegnere `ordini` anche quando `chiudi_tutto` toglie gli ordini; all'avvio leggere `/demo_binance/allarmi` e mettere le
  chiavi in `_accesi`.

Stato dei problemi precedenti non dichiarati:
- 33 resta come prima: blocco senza uscita automatica, ma ora con un allarme visibile che si spegne.
- 39 è **chiuso**: dashboard e fotografia leggono sia `/demo_binance/allarme` (dal `755bde2`) sia `/demo_binance/allarmi`
  (`PaperBot.tsx:131-134`, `:157-162`; `scripts/state_snapshot.py:641-650`).
- 11 resta aperto per la parte degli avvisi sul telefono.
- 14, 34, 35 non toccati.

### Invarianti modificati

Nessun valore di `hard_limits.py` cambiato. Cambiano, nel demo:
- **limiti nuovi nel codice** (`demo_binance.py:84-94`): somma dei pesi al massimo 250%, una moneta al massimo 60%, decisione di G1 al
  massimo 26 ore, capitale del file al massimo 10.000 USDT, filtri del conto vero al massimo 30 giorni (data scritta nel codice,
  2026-11-06), pavimento del «riparti» al 65% del capitale di partenza della fase, 429 e 418 con 3 ritentativi (1-2-4 secondi o
  l'attesa di Binance fino a 10 secondi) e poi nessuna richiesta per almeno 60 secondi (120 senza attesa indicata);
- **stop sul conto**: il massimo si tiene anche in `/demo_binance/massimo` e, se il file non lo ha o è della stessa serie, vale il più
  alto; la regola «resta fermo fino al riparti» si rompe con i limiti di Binance (40);
- **«riparti»**: rifiutato sotto il 65% del capitale di partenza, salvo un capitale nuovo in attesa;
- **ordini**: niente ordini nuovi (anche degli eventi) con una decisione vecchia o pesi fuori dai limiti; monete senza valore minimo non
  trattate; resti a mercato con i filtri a mercato; quantità entro il massimo;
- **ogni ora**: leva rimessa a 5 sulle monete con posizione, modo a due lati ricontrollato;
- **allarmi**: uno per tipo in `/demo_binance/allarmi/<tipo>` (decisione_g1, pesi, limiti_binance, capitale, filtri_veri, riparti,
  ordini); quello del fermo resta in `/demo_binance/allarme`.

### Decisioni per Alessio

1. **Riavvio**: non con questo codice finché non è corretto il 40. Dopo la correzione e la revisione, il riavvio resta tuo.
2. **Pavimento del «riparti»**: al 65% del capitale di partenza la perdita possibile prima del rifiuto è circa il 58%, non il 35%. Infatti
   dopo l'ultimo «riparti» accettato (a 6.500 su 10.000) c'è ancora uno stop intero (fino a 4.225), prova p5. Va bene, o il pavimento
   deve stare più in alto (per esempio all'80%, così la perdita resta vicina al 48%)?
3. **«Riparti» con un capitale nuovo**: riaccende subito e riapre a metà giornata con la decisione di oggi (`ultimo_giorno` a 0,
   `:802`), non alla mezzanotte. Il 7 novembre hai deciso che il conto vero comprerà alla mezzanotte. Per il conto vero vuoi l'attesa
   della mezzanotte anche dopo un «riparti»?
4. **Valori dei limiti nuovi**: 250% (con gli eventi spenti G1 vale 200%), 60% per moneta, 26 ore, 10.000 USDT di tetto (il conto vero
   partirà da circa 280), 30 giorni per i filtri. Vanno in `hard_limits.py` o in un file fisso del conto vero, con un test di guardia
   ciascuno?
5. **Una moneta sopra il 60%** fa saltare tutta la decisione del giorno: il demo tiene le posizioni di ieri. Va bene così, o preferisci
   tagliare quella moneta al 60%?
6. In sospeso, invariate: stop per posizione su Binance; avvisi sul telefono; `DRY_RUN` falso che ferma anche il demo; chiavi vere non
   limitate all'indirizzo e permesso di prelievo da confermare; regole di Firebase mai pubblicate.

### Domande aperte

1. Il problema 16 chiedeva anche «capitale non oltre il saldo»: la sessione principale ha scelto solo il tetto di 10.000. È voluto per il
   demo? Per il conto vero il confronto con il saldo serve (41).
2. Il 10 chiedeva anche un numero minimo di monete per lato: è rimandato all'idea 97 della coda, o è stato lasciato fuori per scelta?
3. Durante un 418 le protezioni si fermano per tutta l'attesa chiesta da Binance, ed è giusto. Per il conto vero vuol dire che con
   l'indirizzo bloccato non c'è nessuna protezione, se non la liquidazione di Binance. È accettato, o serve uno stop per posizione su
   Binance (decisione 1 del primo avvio)?
