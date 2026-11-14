# Revisione: i pesi di oggi di G1 nello «stato» (paper e demo, sola lettura)

Data: 14 novembre 2026. Revisore: live-path-reviewer. Primo giro.

### Riepilogo e verdetto

**REQUEST CHANGES** (0 Bloccanti, 0 Alti, 1 Medio, 4 Bassi). La sezione è davvero di sola lettura: nessun ordine e nessuna scrittura
sono possibili, né su Binance né su Firebase; non stampa chiavi né firme; la finestra 23:50-01:45 UTC è rispettata; un errore non
fa fallire lo stato; il segno e il conto ridotto sono giusti nel caso che il test descrive. Il problema Medio è lo stesso tipo del 79 e
dell'80 della revisione del 12 novembre: la sezione nuova ha un cliente e un lettore suoi, quindi **dopo un 429 o un 418 preso dalla
sezione delle esecuzioni nello stesso «stato» manda comunque una richiesta al demo** (provato con un Binance finto). È la regola
«ci si ferma al primo 429 o 418» che vale per una sezione e non per tutto lo stato. La correzione è piccola. I Bassi riguardano la
qualità del numero (equity vecchia o assurda, segno preso da `notional`, pesi del paper al prezzo del ribilancio contro quelli del demo
al prezzo di adesso) e i test.

### Oggetto

- Branch `claude/brave-albattani-1b12fv`, base `6740920`; modifica **non committata**: `scripts/state_snapshot.py` (+76 −1, impronta
  git `161fa83`), test nuovo non tracciato `tests/test_pesi_g1_oggi.py` (impronta `3ae01c1`). Copia dei due file rivisti nella cartella
  di lavoro, `giro14nov/copia/`.
- Righe toccate: chiamata in fondo a `build()` (`state_snapshot.py:223-224`); `PESO_LETTURE` con `"/fapi/v2/positionRisk": 5`
  (`:809-810`), quindi `SoloLettura.AMMESSI` (`:841`); `sezione_pesi_g1_oggi` (`:1163-1173`), `MONETE_PER_RIGA` (`:1176`),
  `_pesi_g1_oggi` (`:1179-1232`).
- Chi lo esegue: la macchina con la richiesta «stato» (`ops/allowlist.example:25`, `--no-write`), ogni volta che si chiede, senza
  riavvio del bot; e GitHub ogni 2 ore e a ogni spinta del file (`.github/workflows/snapshot.yml:8`, `:12`), senza le chiavi del demo
  (`:32-34`, `:42-44`): lì la sezione scrive solo il paper e «manca la chiave».
- Invarianti coinvolti: nessuno dei limiti fissi; la separazione fra demo e conto vero (indirizzo fisso del demo); la regola della
  sezione vicina «stop al primo 429 o 418, finestra vietata, soglia del peso usato» (revisione del 12 novembre, problemi 79-81).

### Checklist A–F

**A. Limiti fissi e interruttori**
- Valori di `bot/risk/hard_limits.py`: **OK**, invariati (`git diff --stat HEAD`: solo `scripts/state_snapshot.py`).
- Nessun limite spostato in configurazione: **OK** (nessun limite toccato).
- Parametri della dashboard: **NON APPLICABILE** (non toccati).
- Limiti propri di G1 sul demo: **OK**, invariati (`demo_binance.py` non toccato).
- Pulsante che chiude tutto: **OK** per questa modifica: non lo tocca; l'unico legame è indiretto (problema 84: un blocco dell'indirizzo
  ferma anche le protezioni del demo, che passano dallo stesso indirizzo).

**B. Ordini**: **NON APPLICABILE** per tutti i punti (quantità, identificativi, «solo riduzione», prezzo degli stop, leva e margine,
stop per posizione): la sezione non manda ordini. Verificato: il cliente è `ClienteDemo` con `SoloLettura` (`state_snapshot.py:987-992`),
che rifiuta ogni metodo diverso da GET e ogni percorso fuori da `AMMESSI` prima di partire (`:852-853`, confronto esatto del percorso:
`/fapi/v2/positionRisk/../order` non passa); `AMMESSI` adesso è userTrades, commissionRate, income, positionRisk e time, tutte letture;
l'indirizzo è solo `demo-fapi.binance.com` (`demo_binance.py:116-120`). Mutazione «anche GET non ammessi»: presa dal test nuovo.

**C. Stato e resilienza**
- Ricostruzione dello stato da Binance: **NON APPLICABILE** (il bot non è toccato).
- Flussi in tempo reale, candele chiuse: **NON APPLICABILE**.
- Errori delle interfacce: **PROBLEMA** (84, Medio). Dentro la sezione: un 429 o 418 diventa `LimiteInLettura` già in `SoloLettura`
  (`:855-858`), il cliente non riprova, il lettore si ferma (`:910-912`), riga «non letto» (provato). Fra sezioni: dopo un 429 o 418
  della sezione delle esecuzioni la sezione nuova chiede lo stesso (provato: 1 richiesta dopo il 429, 1 dopo il 418), e il controllo
  del peso già usato dall'indirizzo (`:896`) non vale per la sua prima richiesta, perché il cliente è nuovo e non sa niente
  (`peso_usato` è `None`). Errore d'orario -1021: una rilettura dell'ora e un solo nuovo tentativo (`demo_binance.py:479-482`), dentro
  `AMMESSI`. Tempo: una richiesta, `timeout=15` (`demo_binance.py:469`), tetto del lettore 180 s.
- Scrittura su Firebase: **OK**: la sezione fa solo `get_rtdb` (`:1183-1188`); provato con un Firebase finto che registra le scritture:
  zero.
- Un errore non fa fallire lo stato: **OK** con una riserva sui test (88): cornice esterna (`:1170-1173`) più `try` interni per Firebase
  (`:1184-1187`), per la chiave (`:1198-1204`) e per Binance (`:1207-1215`). Provato: un errore dentro la sezione diventa «non letto:
  ZeroDivisionError». La mutazione che toglie la cornice esterna non è presa da nessun test.
- Finestra vietata 23:50-01:45 UTC: **OK**: controllata con l'ora della sezione, all'inizio (`:1180-1181`), quindi anche se lo
  «stato» parte alle 23:49 e arriva in fondo dopo le 23:50 la sezione non chiede niente. Bordi provati: 23:49:59 libero, 23:50:00
  vietato, 01:44:59 vietato, 01:45:00 libero. Dentro la finestra la sezione non scrive nemmeno il paper (solo cosmetico).
- Orologio: **NON APPLICABILE** (invariato).

**D. Separazione fra paper, demo e conto vero**: **OK**. Solo `ClienteDemo` (indirizzo fisso del demo), chiavi `BINANCE_DEMO_*`
(`state_snapshot.py:991`), nessun uso di `BINANCE_API_KEY`; su GitHub nessuna chiave del demo (`snapshot.yml:32-34`), quindi nessuna
richiesta. Nessun legame con `DRY_RUN`, giusto per una lettura.

**E. Segreti e sicurezza**
- Chiavi e firme: **OK**. L'errore della chiave stampa solo il tipo (`:1200-1201`); gli errori di Binance passano da `_motivo` con
  `senza_firma` (`:870-873`, `demo_binance.py:123-127`); gli errori di rete del cliente escono già senza la parte firmata
  (`demo_binance.py:470-478`). Provato sul percorso della macchina (chiavi finte nell'ambiente, rete finta): nel testo non ci sono la
  chiave, il segreto, né `signature`. L'oscuramento dell'agente (`ops_agent.py:53-75`) resta l'ultima rete; i nomi delle monete non
  lo fanno scattare (servirebbero «:» o «=» dopo).
- Permessi delle chiavi e regole pubblicate: **da confermare con Alessio**, come sempre (non dal codice).
- Pubblicità: le risposte della macchina vanno nel repository pubblico; ora anche le posizioni del demo moneta per moneta. Per il
  demo va bene (soldi finti); per il conto vero sarebbe una decisione (sotto).

**F. Test**
- Test nuovi: 7, tutti superati (`python3 -m pytest tests/test_pesi_g1_oggi.py tests/test_demo_esecuzioni.py -q`: 25 passed).
- Suite intera: `python3 -m pytest tests/ -q` → **1 failed, 2804 passed in 190.68 s**; il fallito è
  `tests/test_demo_binance.py::test_firma_dei_tre_tipi_di_chiave` (libreria `cryptography` del contenitore rotta, già noto); con
  `PYTHONPATH=<cartella di lavoro>/cripto` la firma e i test dei limiti fissi (`tests/test_risk.py`, `tests/test_sizing.py`,
  `tests/test_demo_binance.py`, `tests/test_conto_vero.py`) passano: 210 passed.
- Mutazioni (`giro14nov/mutazioni.py`, con una copia mutata caricata davvero; controllo senza mutazione: 7 passed): prese «finestra
  tolta», «valore senza segno», «try della lettura tolto», «sezione in cima», «anche GET non ammessi», «senza il lettore»; **non presa**
  «cornice esterna tolta». Mancano anche i casi del Medio 84 e dei Bassi (88).

### Problemi

**84 — Medio — dopo un 429 o un 418 della sezione delle esecuzioni, la sezione nuova chiede ancora a Binance**
- Dove: `state_snapshot.py:1197-1206` (cliente nuovo da `cliente_di_sola_lettura()`, `_Lettore` nuovo), contro `:119` (la sezione delle
  esecuzioni, con il suo lettore) e `:826-828`, `:855-858` («ci si ferma al primo segnale»).
- Scenario: lo «stato» parte poco dopo l'ora piena, quando il bot del demo fa la valutazione, il margine e il confronto (stesso
  indirizzo, stesso `demo-fapi`); la sezione delle esecuzioni prende un 429 e si ferma come deve; 10-40 secondi dopo (lo stato dura
  circa 51 s, `ops/results/0741-14nov-stato-per-il-proprietario.md:7`) la sezione nuova manda `positionRisk` con un cliente che non
  sa del 429 e senza il controllo del peso già usato. Binance scrive che chi non si ferma dopo un 429 viene bloccato (418, da 2 minuti a
  3 giorni, più lunghi per chi ripete); con un 418 già in corso il codice del demo stesso assume che riprovare allunghi il blocco
  (`demo_binance.py:91`, `:486`). Con l'indirizzo bloccato il bot del demo non legge il conto: stop sul conto e pulsante che chiude
  tutto aspettano la fine del blocco (mappa, sezione 8). Probabilità bassa, una richiesta sola, ma è proprio la regola chiusa con l'80.
- Provato: `giro14nov/test_prove_14nov.py::test_dopo_un_429_della_sezione_vicina_la_sezione_nuova_chiede_ancora` e `::test_dopo_un_418`
  (prima sezione 1 richiesta e fermata; seconda sezione 1 richiesta).
- Correzione suggerita alla sessione principale: uno stop comune a tutto il processo dello «stato». Per esempio: `SoloLettura`
  ricorda in un attributo della classe (o del modulo) il primo 429 o 418 visto e il peso usato più recente; `_Lettore.chiedi` (o
  `SoloLettura.__call__`) rifiuta ogni richiesta dopo un 429 o 418 visto nello stesso processo, e applica `PESO_USATO_MASSIMO` anche
  alla prima richiesta con il peso ricordato. In alternativa un solo cliente creato in `build()` e passato alle due sezioni. Scrivere
  nella sezione nuova, come nella vicina (problema 81), le richieste fatte e il peso usato, o il motivo per cui non ha chiesto. Test:
  le due sezioni di fila con chiavi finte e rete finta, 429 e 418 nella prima → zero richieste nella seconda; peso usato 700 nella prima
  → zero richieste nella seconda.

**85 — Basso — equity del demo presa senza guardare quando è stata scritta né se è un numero sensato**
- Dove: `state_snapshot.py:1191-1195`. `/demo_binance/stato` lo scrive `valuta` ogni ora (`demo_binance.py:1453`, con `aggiornato`) o
  lo stop con lo stato «fermo» (`:790`).
- Scenario: con il bot fermo da un giorno la sezione divide le posizioni di adesso per un'equity vecchia senza dirlo. Provato con
  valori estremi: `"nan"` → «+nan», `"inf"` → demo «+0.00» (cioè «il demo non ha la moneta», falso), `1e-9` → «+2000000000000.00».
  Firebase non tiene `nan` né `inf`, quindi il caso reale è l'equity vecchia o molto piccola. Nessun effetto sugli ordini.
- Correzione: accettare solo un numero finito sopra una soglia (per esempio 1 USDT), scrivere accanto l'ora di `aggiornato` e lo
  `stato` («acceso» o «fermo: …»), e avvisare se è più vecchia di 2 ore.

**86 — Basso — il segno viene da `notional`, non da `positionAmt`**
- Dove: `state_snapshot.py:1211-1213`. Il bot del demo usa `positionAmt` per le sue posizioni (`demo_binance.py:1197`); la
  documentazione di Binance dà il segno a `positionAmt` nella modalità a una posizione per moneta, mentre per `notional` non lo scrive
  in chiaro. Per quel che so `notional` è negativo per le posizioni corte, ma non è verificato in questo repository (nessuna risposta
  vera salvata; il test usa un `notional` finto già con il segno).
- Scenario: se il demo restituisse `notional` senza segno, ogni corta del demo comparirebbe come lunga: provato, paper «−2.00», demo
  «+2.00», differenza 4% invece di 0. Nessun effetto sugli ordini; numero sbagliato per spiegare lo scarto.
- Correzione: peso = `positionAmt` × `markPrice` / equity (sono nella stessa risposta), oppure il valore assoluto di `notional` con il
  segno di `positionAmt`; un test con una corta che ha `notional` positivo. Al primo «stato» vero, controllare che le corte del demo
  escano con «−».

**87 — Basso — paper al prezzo del ribilancio, demo al prezzo di adesso: la «somma delle differenze» mescola esecuzione e prezzi**
- Dove: `state_snapshot.py:1190` e `:1229-1231`. `/paper_g1/posizioni` sono i pesi voluti al ribilancio (`f5.py:449`: quantità = peso ×
  equity / prezzo del ribilancio; `f5.py:478`: si pubblicano i pesi); il demo è valore di adesso (`notional` al prezzo mark) su
  un'equity fino a un'ora fa. Il confronto del bot (`demo_binance.py:1261-1280`) invece confronta le quantità allo stesso prezzo.
- Scenario: con circa 50 monete e qualche punto percentuale di movimento dalla mezzanotte, il solo movimento dei prezzi aggiunge alcuni
  punti alla «somma delle differenze» (stima, non misurata), dello stesso ordine dello scarto vero (11,5% del conto alle 12:03 UTC,
  `ops/results/0741-14nov-stato-per-il-proprietario.md:66`). Chi legge può prendere il movimento dei prezzi per un difetto del demo.
- Correzione: dirlo nella riga d'intestazione («paper ai prezzi del ribilancio, demo ai prezzi di adesso»), oppure portare anche il
  paper ai prezzi di adesso (servono i prezzi del ribilancio del paper, oggi solo nel suo file locale).

**88 — Basso — test che mancano**
- Non presa la mutazione «cornice esterna tolta» (`:1170-1173`): nessun test fa esplodere la sezione dall'interno.
- Il percorso della macchina (`cliente=None`, chiavi nell'ambiente, `requests.request` finto, `SoloLettura` vera dentro la sezione) non
  è provato per questa sezione; c'è solo la prova del cliente da solo (`tests/test_pesi_g1_oggi.py`, ultima prova del cliente).
- Mancano: 429 e 418 dentro la sezione e dopo la sezione vicina (84); `notional` senza segno (86); equity vecchia o assurda (85); la
  lunghezza con 100 monete sotto i 10.000 caratteri della coda (provato a mano: 3.338 caratteri, 21 righe).
- Le prove del revisore sono in `giro14nov/test_prove_14nov.py` (si possono copiare).

### Invarianti modificati

Nessuno dei limiti fissi né del percorso degli ordini. Cambiato: la lista delle letture permesse alla funzione di sola lettura dello
stato (`AMMESSI`) ora comprende `GET /fapi/v2/positionRisk` del conto demo (peso 5, come nella documentazione di Binance). Lo «stato»
fa al massimo 1.005 di peso sul demo invece di 1.000 (più 1 per l'ora dopo un errore d'orario).

### Decisioni per Alessio

1. Nessuna decisione sui limiti per questa modifica. Il commit non tocca il bot e non richiede riavvio: entra in funzione alla prima
   richiesta «stato» dopo la spinta. Con il verdetto attuale, prima del commit va corretto l'84.
2. Le risposte della macchina sono pubbliche: con questa sezione si pubblicano ogni volta le posizioni del demo moneta per moneta. Per
   il demo va bene; per il conto vero una sezione uguale pubblicherebbe le posizioni vere e la grandezza del conto. Da decidere prima
   di farla anche per il conto vero.

### Domande aperte

1. Al primo «stato» vero dopo il commit: le posizioni corte del demo escono con «−»? Se escono con «+», `notional` non ha il segno e i
   numeri della sezione sono sbagliati (86).
2. La sezione deve misurare lo scarto di esecuzione (come il confronto del bot, allo stesso prezzo) o la differenza di pesi così come
   si vede adesso? Dalla risposta dipende se basta una frase nell'intestazione o se serve portare il paper ai prezzi di adesso (87).

### Rilettura (secondo giro, 14 novembre 2026)

**Verdetto: APPROVE** per il commit (nessun riavvio: lo «stato» la usa alla prima richiesta dopo la spinta). 0 Bloccanti, 0 Alti,
0 Medi; un Basso nuovo, 89, solo un commento. Riletto solo il cambio: `scripts/state_snapshot.py` impronta md5 `3c07b74e…`, test
`05a50a46…` (copia in `giro14nov/copia2/`), ancora non committati.

- **84 chiuso.** `build()` crea un solo cliente (`state_snapshot.py:120-126`) e lo passa alle due sezioni (`:126`, `:231`);
  `SoloLettura` ricorda il primo 429 o 418 in `bloccato` (`:866-868`) e da lì rifiuta ogni richiesta prima della rete (`:861-862`),
  anche la rilettura dell'ora del cliente; il peso usato è dello stesso oggetto, quindi vale anche per la prima richiesta della
  seconda sezione. Provato sullo **stato intero** (`build()` con Firebase finto, chiavi finte, rete finta,
  `giro14nov/test_prove_14nov_b.py`): con un 429 o un 418 in tutto lo stato parte **una sola** richiesta; con il peso usato a 700
  nella prima sezione `positionRisk` non parte; normale: solo GET, solo `demo-fapi.binance.com`, nessuna scrittura su Firebase, nessuna
  chiave o firma nel testo; senza chiave nessuna richiesta. Resta un caso trascurabile: se la chiave non si legge in `build()` e si legge
  subito dopo dentro una sezione, ognuna ha il suo cliente (come prima della correzione).
- **85 chiuso.** Equity solo finita, sopra zero e sotto 1e9 (`:1205`), avviso oltre 2 ore da `aggiornato` (`:1206`, `:1237-1238`);
  pesi del paper non finiti scartati.
- **86 chiuso.** Segno da `positionAmt`, valore assoluto di `notional` (`:1225-1228`). Provato: corta con `notional` positivo e lunga
  con `notional` negativo escono giuste.
- **87 chiuso come scelto**: l'intestazione lo dice (`:1232-1235`).
- **88 chiuso.** Mutazioni (`giro14nov/mutazioni2.py`, copia mutata caricata davvero; controllo senza mutazione: 13 passed): prese
  tutte e 9 (blocco non controllato, blocco non ricordato, segno da `notional`, equity senza limiti, avviso tolto, protezione esterna
  tolta, clienti separati nello stato, finestra tolta, GET non ammessi). «Clienti separati» la prende solo il controllo sul testo di
  `build()`; il comportamento l'ho provato io sullo stato intero.
- **89 Basso nuovo, solo testo**: il commento di `EQUITY_VECCHIA_S` (`:1188`) dice «il demo riscrive l'equity ogni pochi minuti»; la
  riscrive ogni ora (`demo_binance.py:75` `OGNI_VALUTAZIONE_S = 3600`, `:841-842`; `/demo_binance/stato` scritto solo a `:790` e `:1453`).
  La soglia di 2 ore resta giusta (una valutazione saltata). Correggere il commento quando capita.
- Test: `test_pesi_g1_oggi.py` e `test_demo_esecuzioni.py` 31 passed; suite intera `python3 -m pytest tests/ -q` → **1 failed, 2810
  passed in 189.55 s** (il fallito è la firma, libreria del contenitore, già noto); firma, limiti fissi, conto vero e le due sezioni con
  la libreria buona: 150 passed. Nessun file di `bot/` o `firebase/` toccato; limiti fissi invariati.
- Domanda aperta 1 resta per il primo «stato» vero: le corte del demo escono con «−»? (Con la correzione 86 devono uscire con «−»
  comunque; se non è così, `positionAmt` stesso è sbagliato e va detto subito.) Domanda 2 chiusa dalla scelta della sessione (87).

