# Diciassettesima revisione del trader AI — versione 8, le correzioni del riesame della sedicesima

Revisore: live-path-reviewer, 27 novembre 2026, mattina (06:20-06:50 UTC). Oggetto: le modifiche non committate su `11ad4c2` (branch
`claude/brave-albattani-1b12fv`), cioè le correzioni della sessione ai problemi del riesame della sedicesima
(`revisioni/2026-11-26-sedicesima.md`, sezione «### Riesame»). La differenza l'ho rifatta io dalla copia del riesame
(`scratchpad/mut_v8/copia/trader_ai`, impronte uguali a quelle approvate nel riesame: `avvio.py` 5ae0701f, `limiti.py` a3e811bb,
`messaggio.py` b6923e17) ai file di adesso: è uguale a quella data dalla sessione (`scratchpad/dal_riesame16.diff`).

Prove mie nella cartella `/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/rev17/revisore_lp/`
(sotto: «la cartella»). Nessuna richiesta a Binance: il mercato è quello finto dei test. I dati veri di `trader_ai/avanti/` solo letti:
il trader è fermo a mano dalle 07:11 UTC del 26, senza niente di aperto, e il 3% non è mai stato raggiunto (nessun evento «obiettivo
del giorno raggiunto» nel diario).

### Riepilogo e verdetto

**APPROVE con condizioni.** Nessun Bloccante, nessun Alto, nessun Medio. Del riesame: 207, 209, 210 e 211 sono chiusi; il 208 è
chiuso per la parte lunga (la chiamata al modello), ma resta una finestra corta (213). Quattro problemi nuovi, tutti Bassi (213-216);
il 216 c'era già.

1. **207 chiuso.** Con un ordine limite in attesa il ramo dell'obiettivo usa `_annulla_limite`: se il limite si esegue proprio in
   quel momento, la posizione si chiude subito e si registra (`avvio.py:301-308`). Ho provato anche gli errori: esito non letto,
   chiusura rifiutata, annullamento che non riesce. In tutti e tre il passo si interrompe e il passo dopo rimette le cose a posto
   (prove P1, P2, P4).
2. **Il richiamo salvato subito** (`_ricorda`, `avvio.py:144-151`, usato a `:258`, `:294`, `:336`, `:344`): non si ripete due volte
   e non resta dopo una chiamata, anche con tetto finito, conto esaurito, errore del modello o mezzanotte (P9-P12). Resta una
   finestra di una lettura del saldo fra la chiusura del programma e il salvataggio (213).
3. **Il fermo che si toglie** (`avvio.py:279-294`): solo senza niente di aperto, una volta sola, e senza giri fermo/sfermo. L'ho
   provato con un funding vero pagato in ritardo sul conto simulato (P6). Il resoconto non lo racconta bene (214).
4. **Un centesimo solo per tutti** (`limiti.py:56-59`), usato anche da `giro.decidi` (P14). «Mancano» nel messaggio è «0.00»
   se e solo se l'obiettivo è raggiunto: provato su 8.414 casi (P13).
5. **I test prendono gli errori, con dei buchi.** Le 52 mutazioni della sessione, rifatte su una copia mia: 52 prese. Delle mie 9,
   2 sono prese dai test del repository. Delle 7 vive, 6 le prendono le mie prove: una di queste porta a un fermo che si toglie e si
   rimette a ogni passo (215). La settima è equivalente al codice.
6. **Nessuna regressione.** 178 test del trader passano. I 20 test nuovi, sul codice del riesame: 13 falliscono, 7 passano (come
   detto dalla sessione). Suite della radice come prima: 2825 passati, 1 fallito (lo stesso della ricerca), 1 saltato.

**Problemi nuovi**
- **213, Basso.** Dopo una chiusura per l'obiettivo, lo stato si salva solo dopo una nuova lettura del saldo. Se proprio quella
  lettura fallisce, al passo dopo l'operazione si registra di nuovo: con il modo sbagliato, due volte nel diario, e sotto il 3% senza
  il perché. È la stessa cosa del 208, ma la finestra è molto più corta.
- **214, Basso.** Il resoconto non dice che il fermo è stato tolto. Lo stesso fatto dà due testi diversi se lo si vede 30 secondi
  prima o dopo la mezzanotte. Il 3% è scritto a mano.
- **215, Basso.** Mancano i test per sei mutazioni vive. Una toglie e rimette il fermo a ogni passo.
- **216, Basso, c'era già.** «Chiudi» a mano dopo una chiusura sul conto non ancora vista dal programma perde l'operazione dalla
  memoria.

**Condizioni**
1. Il riavvio lo approva Alessio, con «riparti» (il trader è fermo a mano). Con lo stesso ok conferma le due scelte prese dalla
   sessione dalla sua frase (vedi «Decisioni per Alessio»).
2. Al commit il codice deve avere le impronte qui sotto. Se cambiano solo i test (215, consigliato prima del commit), basta che le
   impronte del codice restino queste. Se cambia il codice (213, 214, 216), serve un riesame.
3. Prima di qualunque conto demo per il trader: 213 corretto, 212 misurato, 198 e 199 della quindicesima corretti, e una revisione
   nuova.

### Oggetto

* Branch `claude/brave-albattani-1b12fv`, base `11ad4c2`, niente di committato. Fuori da `trader_ai/` non cambia niente:
  `git diff HEAD --stat -- bot/ firebase/ ops/ .claude/ tests/` è vuoto, e `bot/risk/hard_limits.py` ha l'impronta 841f04e6.
* File cambiati dal riesame:
  - `avvio.py`:
    - commento in testa (`:9-11`);
    - `_ricorda` (`:144-151`), usato dopo la chiusura trovata (`:255-258`), quando il fermo si toglie (`:279-294`) e nel ramo
      «sotto il 3%» (`:333-344`);
    - limite in attesa con `_annulla_limite` (`:298-308`);
    - verifica dopo la chiusura con `obiettivo_raggiunto(dopo)` (`:318-327`);
    - motivo con il modo vero (`:331-344`);
    - resoconto «poi il conto è sceso» (`:1074-1076`);
  - `limiti.py`: `obiettivo_raggiunto` al centesimo (`:56-59`);
  - `messaggio.py`: «mancano» al centesimo (`:333`);
  - `REGOLE.md`, `README.md`: le regole nuove e gli aperti 209 e 212;
  - test nuovo: `tests/test_obiettivo_riesame.py` (20 casi).
* Uguali al riesame: `giro.py`, `ripara.py`, `istruzioni.md`, `conto_simulato.py`, `operazioni.py`, `costi.py`, `conto_demo.py`,
  `sveglia.py`, `config.json` e tutti gli altri file di test (impronte qui sotto). Nessun test tolto: 158 + 20 = 178.
* Invarianti coinvolti: l'obiettivo del giorno e il fermo fino a mezzanotte (sezione 15 della mappa); lo stop per ogni posizione
  (il 207).

### Stato dei problemi del riesame

| Problema | Esito | Dove | Prova |
|---|---|---|---|
| 207 revisore (= 211 secondo cercatore): limite in attesa annullato con `chiudi(None)` | **chiuso** | `avvio.py:301-308`, `:925-958` | Test B1 (due casi) e B2 del repository; mie: P1 (esito non letto: il passo si interrompe, l'ordine è già tolto dal conto; il passo dopo lo vede sparito, fermo, niente aperto); P2 (limite eseguito e chiusura rifiutata: la posizione resta senza stop fino al passo dopo, 30 secondi, poi lo stop si rimette e si chiude per l'obiettivo, registrata una volta, fermo; è lo stesso di quando annulla il modello); P3 (limite eseguito e chiuso dallo stop nello stesso minuto: registrata una volta, con il modo dello stop); P4 (annullamento che non riesce, come sul demo: niente fermo e niente chiamate finché non riesce; il codice del riesame andava in fermo con l'ordine ancora sul libro). |
| 208 revisore (= 207 secondo cercatore) e 200 | **chiuso in parte** | `avvio.py:255-258`, `:333-344` | Chiusa la finestra lunga, cioè candele, interesse aperto e chiamata fino a 5 minuti (test C1 e `test_chiusura_trovata_nel_passo_e_passo_interrotto`; mia P12 a mezzanotte). Resta la lettura del saldo fra la chiusura e il salvataggio, in tutti e due i rami: **213**. |
| 209 revisore: motivo e commento | **chiuso** | `avvio.py:9-11`, `:331-344` | D1, A5, `test_niente_da_chiudere_e_conto_che_scende`; mia P3; mutazioni N9, N10, N11, R13 prese. |
| 210 revisore (= 208 secondo cercatore): il centesimo | **chiuso** | `limiti.py:56-59`, `giro.py:33`, `messaggio.py:333`, `avvio.py:281`, `:321` | E1, E2, `test_obiettivo_raggiunto_al_centesimo`, `test_mancano_...`; mie P13 (8.414 casi, nessuna differenza fra «mancano 0.00» e `obiettivo_raggiunto`) e P14 (`giro.decidi`). Mancano due test: R1 e R4 (215). |
| 211 revisore: casi senza test | **chiuso** | `tests/test_obiettivo_riesame.py:108-213` | A1-A5 nel repository; le mutazioni vive del riesame (R5, R6, R7, R8, R15, R17 di allora) corrispondono a N2, N4, N6, N10, A3 e A2, tutte prese. |
| 209 secondo cercatore: conto e prezzo da due letture | **rinviato, il rinvio regge** | `README.md:65-70` | Sul simulato il saldo e il prezzo arrivano a frazioni di secondo uno dall'altro. Le spese di chiusura cambiano di pochi centesimi per un dollaro di BTC. Dal 204 un controllo scattato un attimo prima non ferma più il programma. Una lettura sola non toglie la terza lettura, quella della chiusura. Costo: un'uscita anticipata e, se il modello vuole continuare, una nuova entrata. Da rivedere prima di un conto vero. |
| 210 secondo cercatore: funding pagato dopo il fermo | **chiuso, con una scelta da confermare** | `avvio.py:279-294`, `:1074-1076` | Test `test_funding_dopo_il_fermo_...`, `test_fermo_non_si_toglie_...`, `test_resoconto_dice_...`; mie P6 (funding vero in ritardo sul simulato: fermo tolto una volta, applicato una volta, nessuna chiamata in più nei tre passi dopo), P7 (passo interrotto: il motivo resta e l'evento non si ripete), P8 (funding ricevuto: il fermo resta), P15 (+29,998: il fermo resta). La scelta regge con la frase del proprietario e con il 204, ma è una scelta: la conferma Alessio. |
| 212 secondo cercatore: saldo forse vecchio sul demo | **rinviato, il rinvio regge** | `config.json` («simulato»), `README.md:69-70` | Il demo è spento e la verifica avversaria non l'ha riprodotto. Resta una condizione prima di un demo, con il 213. |

### Checklist A–F

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py` invariato (841f04e6; `git diff HEAD` vuoto su `bot/`, `firebase/`, `ops/`, `.claude/`, `tests/`). **OK**
* Limiti nel codice, non in configurazione: il 3% a `limiti.py:15`, la leva fino a 10 a `limiti.py:16`, il tetto di 5 dollari in
  `costi.py` (2b1e9f30, invariato); `config.json` invariato (6ad5da2d). **OK**
* Parametri dalla dashboard: **NON APPLICABILE** (il trader non legge Firebase).
* Limiti di G1 sul demo: **NON APPLICABILE**.
* Pulsante che chiude tutto:
  - il file del fermo si legge per primo (`avvio.py:186-187`) e vale anche sul fermo che si toglie;
  - il comando «chiudi» (`:1006-1040`) e i controlli prima di ogni ordine (`:777-778`, `:841`, `:856`) non sono toccati, e vanno
    senza Firebase;
  - chiude tutto; ma se l'operazione si era già chiusa sul conto senza che un passo la vedesse, la perde dalla memoria: **PROBLEMA
    216** (c'era già).

**B. Ordini**
* Passi, minimi, leva e margine non toccati (`avvio.py:807-825`, `:840`). **NON APPLICABILE**
* Identificativo dell'ordine: la chiusura del limite eseguito usa `_cid(ora, "x")` (`avvio.py:734`), unico nel passo; l'operazione
  nuova dello stesso passo ha nomi suoi (F1). **OK**
* Solo riduzione: conto simulato (`conto_simulato.py:433-444`); il demo è spento. **NON APPLICABILE**
* Prezzo che attiva gli stop: il mark, invariato. **OK**
* Stop per ogni posizione: il limite eseguito durante l'annullamento si chiude subito (B1, B2). Se la chiusura fallisce, resta senza
  stop fino al passo dopo (30 secondi) e lì la protezione lo rimette (P2), come quando annulla il modello. **OK**

**C. Stato e resilienza**
* Posizioni, ordini e saldo letti dal conto a ogni passo; nel ramo dell'obiettivo `_annulla_limite` rilegge posizione, ordini ed esito
  (`avvio.py:925-958`). **OK**
* Flussi in tempo reale: **NON APPLICABILE**.
* Candele chiuse: non toccate. **OK**
* Errori:
  - un errore di `_annulla_limite` interrompe il passo e il passo dopo riprova bene (P1, P2, P4);
  - il richiamo salvato non si ripete (P9-P12);
  - resta la finestra di una lettura del saldo dopo la chiusura: **PROBLEMA 213**.
  - *c'era già*: un passo interrotto dopo la mezzanotte rifà la mezzanotte al passo dopo (P12: tre eventi «giorno nuovo» al posto di
    due, resoconto riscritto). Oggi il resoconto riscritto è uguale.
* Firebase e orologio: **NON APPLICABILE**.

**D. Separazione fra simulato, demo e conto vero**
* Il trader gira sul conto simulato (`config.json`, `avvio.py:1145-1149`), con sole letture pubbliche e il controllo dell'indirizzo
  (`conto_simulato.py:62-67`). Il fermo che si toglie non fa letture nuove; nel ramo dell'obiettivo le letture in più sono dello stesso
  tipo di prima (posizione, ordini, esito). **OK**

**E. Segreti**
* Differenza letta tutta: nessuna chiave, nessun percorso di file segreti; gli eventi nuovi scrivono solo conto e guadagno. **OK**
* Chiavi e permessi del demo: **NON APPLICABILE** (demo spento).

**F. Test** (comandi ed esiti; tutto nella cartella)
* `TRADER_AI_BLOCCO=<cartella>/x.lock python -m pytest trader_ai/tests -q -p no:cacheprovider`: **178 passed** in 11,1 s. `git status`
  uguale a prima.
* Mutazioni (`mutazioni17.py`, esiti in `esito_mut17.txt` ed `esito_mut17_vive.txt`). Copia mia, cartella temporanea di pytest mia,
  base 177 passati più 1 tolto (quello che chiede git, come la sessione):
  - **sessione: 52 prese su 52** (la lista è letta da `mut_v8/mutazioni_v8b.py`);
  - **mie: 2 prese su 9 dai test del repository** (R9, R13). Delle 7 vive, 6 le prendono le mie prove (R1 da P13, R2 da P7, R3 da
    P17, R4 da P15, R5 da P16, R6 da P1, P2 e P4). La R16 («mancano» senza arrotondare il guadagno) è equivalente al codice: cambia
    solo sul mezzo centesimo esatto.
* Mie prove (`prove/test_prove17.py`, 23 casi; il primo stampa quale `avvio.py` importa):
  - sul codice di adesso (8ace7619): **21 passate, 2 fallite**. Le due fallite sono le P5, cioè il problema 213 (`prove_adesso.txt`);
  - sulla copia del riesame (5ae0701f), prima delle prove P15-P17 e della prova del 216: 13 fallite (le prove del comportamento
    nuovo, più le P5) e 6 passate (`prove_riesame.txt`).
* Test nuovi del repository sul codice del riesame (`prima17_esito.txt`): **13 falliti, 7 passati**, come detto dalla sessione.
* `python3 -m pytest tests/ -q -p no:cacheprovider` (cartella temporanea mia): **2825 passed, 1 failed, 1 skipped** in 214 s
  (`suite_radice.txt`). Il fallito è lo stesso della sedicesima
  (`tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore`, ricerca). I test dei limiti fissi passano.
* **Attenzione**, giro buttato: alle 06:30-06:33 UTC il mio primo giro di mutazioni e un'altra suite della radice giravano in
  `rev17/copia_mut`. Nello stesso momento lo usava un altro processo (`rev17/mutazioni_rifatte.py`), e tutti usavano le cartelle
  temporanee comuni di pytest. Quegli esiti li ho buttati e rifatti tutti nella cartella, con le cartelle temporanee separate (vedi
  «Domande aperte»).

### Problemi

**213 — Basso — `trader_ai/avvio.py:310-321` (e `:305-308` per il limite eseguito durante l'annullamento).** Resto del 208.
* **Che cosa succede.**
  - Nel ramo dell'obiettivo il programma chiude e registra l'operazione nella memoria del processo (`:310-314`). Poi rilegge il saldo
    (`:318`), e solo dopo salva: con il fermo (`:326`) o con il motivo (`:336`, `:344`).
  - Se proprio quella lettura fallisce, lo stato salvato crede l'operazione ancora aperta. Al passo dopo la registra di nuovo dal
    conto.
  - Effetti: il modo diventa «chiusa sul conto (stop, obiettivo o liquidazione)» (sul simulato «chiusa a mercato») invece di
    «obiettivo del giorno (chiusa dal programma)»; il diario ha due «operazione chiusa».
  - Sotto il 3%, il modello si chiama senza sapere che l'ha chiusa il programma e che il 3% non è arrivato. Sopra il 3% il fermo
    arriva lo stesso al passo dopo.
* **Quando.** Sul simulato è raro: la lettura del saldo va in rete solo se sono passati più di 5 secondi dall'ultimo aggiornamento
  del conto (`conto_simulato.py:167-173`), e solo per i pagamenti di funding (`:250-270`); poi la richiesta deve fallire (una pausa per
  troppe richieste, la rete giù). Sul demo ogni lettura del saldo è una richiesta firmata: per questo è una condizione prima di un
  demo. Il codice del riesame aveva la stessa finestra (P5 fallisce anche lì).
* **Prova** (eseguita, `test_P5_lettura_del_saldo_dopo_la_chiusura_che_fallisce`, due casi). Conto finto, operazione lunga, conto a
  1.031. Dopo la chiusura del programma il conto va a 1.029 (sotto) oppure resta a 1.031 (sopra), e la seconda lettura del saldo dà
  «429: pausa».
  - In tutti e due i casi, al passo dopo: modo «chiusa sul conto (stop, obiettivo o liquidazione)» e due «operazione chiusa» nel
    diario.
  - Sotto il 3%, il motivo della chiamata è «operazione chiusa (chiusa sul conto (stop, obiettivo o liquidazione))», senza il perché.
* **Correzione** (sessione principale). Salvare subito dopo la chiusura o l'annullamento, prima di rileggere il saldo. Per esempio
  `_ricorda` con un motivo provvisorio: «operazione chiusa (<modo>; il guadagno dopo la chiusura non si è potuto leggere)», oppure
  «ordine limite annullato dal programma per l'obiettivo del giorno (nessuna operazione)». Poi tutto come adesso: il fermo salva senza
  richiamo, il ramo sotto il 3% riscrive il motivo intero. Test: le due P5.

**214 — Basso — `trader_ai/avvio.py:1071-1076` con `:289`.**
* **Che cosa succede.**
  - Quando il fermo si toglie di giorno, `obiettivo_ora` diventa vuoto. A mezzanotte il resoconto dice solo «non raggiunto»: non dice
    che il 3% era arrivato, a che ora il fermo si è tolto, né perché.
  - Se lo stesso funding si vede nel primo passo dopo mezzanotte, il resoconto dice «raggiunto alle 23:59 UTC, poi il conto è sceso
    sotto il 3% (+29.06)». Lo stesso fatto ha due testi.
  - Il confronto nuovo usa `conto_inizio * 0.03` scritto a mano (`:1072`, c'era già), non `OBIETTIVO_GIORNO_QUOTA`.
  - Senza queste righe, Alessio non vede quanto costa la scelta del fermo che si toglie (vedi «Decisioni»). Oggi il dato c'è solo nel
    diario.
* **Prova** (eseguita, `test_R_resoconto_stesso_fatto_due_testi`). Fermo alle 23:59:10 con +31; il conto scende a +29,06.
  - Visto alle 23:59:40: «* Obiettivo del 3% (30.00 USDT): non raggiunto».
  - Visto alle 00:00:10: «... raggiunto alle 23:59 UTC, poi il conto è sceso sotto il 3% (+29.06)».
* **Correzione.**
  - Tenere nello stato l'ora del primo 3% e l'ora del fermo tolto, e scriverle nel resoconto, per esempio: «raggiunto alle 14:02 UTC,
    fermo tolto alle 16:00 UTC (funding dopo la chiusura, guadagno +29,40), poi non raggiunto».
  - Usare `OBIETTIVO_GIORNO_QUOTA`.
  - Test: le due varianti qui sopra.

**215 — Basso — `trader_ai/tests/` (codice coinvolto: `limiti.py:59`, `avvio.py:281`, `:294`, `:305-308`, `:344`).**
* **Che cosa manca.** Sei mutazioni passano tutti i 177 test del repository (`esito_mut17.txt`):
  - R4, il fermo che si toglie senza il centesimo. Con questa mutazione e il conto a +29,998 durante il fermo, il fermo si toglie e
    si rimette a ogni passo: in 4 passi, 4 «fermo tolto» e 5 «obiettivo raggiunto», per tutto il resto del giorno (prova eseguita su
    una copia mutata, `copia_r4`);
  - R1, il centesimo solo sul guadagno: cambia l'esito quando il 3% del conto della mezzanotte non è un numero tondo di centesimi;
  - R2 e R3, il motivo non salvato quando il fermo si toglie o quando il limite si annulla sotto il 3%;
  - R5, il limite «eseguito» riconosciuto dalle operazioni vecchie invece che dal contatore: con un'operazione già in memoria, il
    motivo direbbe «operazione chiusa (chiusa da te; ...)» per un limite mai eseguito;
  - R6, l'errore di `_annulla_limite` ingoiato.
* **Prova** (eseguita): `esito_mut17_vive.txt`. Le mie prove prendono tutte e sei: R1 da P13, R2 da P7, R3 da P17, R4 da P15, R5 da
  P16, R6 da P1, P2 e P4.
* **Correzione.** Portare nei test del repository P1, P2, P4, P7, P13, P15, P16 e P17 (da `prove/test_prove17.py`; gli aiuti `sim`,
  `finto`, `vai` sono gli stessi del test nuovo).

**216 — Basso, c'era già — `trader_ai/avvio.py:1027-1030`.**
* **Che cosa succede.** L'operazione si chiude da sola sul conto (stop o obiettivo) e il proprietario lancia «chiudi» prima che un
  passo la veda. Il comando registra la chiusura solo se ha chiuso lui una posizione (`if st.get("aperta") and pos is not None`).
  Altrimenti mette `aperta` a vuoto e l'operazione sparisce dalla memoria. Il suo risultato resta nel conto, ma non nella memoria del
  modello, non nel bilancio di oggi e non nel resoconto.
* **Prova** (eseguita, `test_R_chiudi_a_mano_dopo_una_chiusura_sul_conto_non_ancora_vista`). Su tutti e due i codici: 0 operazioni in
  memoria dopo «chiudi» e dopo «riparti». Se invece un passo ha già visto la chiusura e si è interrotto, adesso la memoria la tiene
  (grazie a `_ricorda`, `test_R_richiamo_vecchio_dopo_fermo_a_mano`). Il codice del riesame la perdeva anche in quel caso.
* **Correzione.** Nel comando, con `aperta` piena e nessuna posizione: per un'operazione eseguita, `_registra_chiusura` con l'esito
  del conto; per un limite in attesa, il controllo di `_limite_sparito`. Non serve prima del riavvio.

### Invarianti modificati

* **Il fermo fino a mezzanotte non è più certo, una volta scattato.**
  - Prima: messo il fermo, niente chiamate fino a mezzanotte.
  - Adesso: se durante il fermo non c'è niente di aperto e il guadagno sul conto scende sotto il 3% al centesimo, il fermo si toglie.
    Evento «dopo il fermo il guadagno del giorno è sceso sotto il 3%: fermo tolto, si continua», e il modello si chiama con il perché
    (`avvio.py:279-294`).
  - Il fermo a mano (il file) vale sempre per primo (`:186-187`).
* **Il centesimo vale anche prima della chiusura.** La chiusura per l'obiettivo scatta quando il guadagno dopo le spese di chiusura,
  arrotondato al centesimo, arriva al 3% arrotondato (`limiti.py:56-59`). Prima della chiusura il centesimo non c'era. Così si chiude
  già da circa 29,995 su 30 (per un conto di 1.000 a mezzanotte).
* **Ordine limite in attesa quando l'obiettivo è raggiunto**: si annulla con `_annulla_limite`; se si esegue in quel momento, la
  posizione si chiude subito (`avvio.py:301-308`).
* **Invariati:** il tetto di 5 dollari, la leva fino a 10, il 3%, lo stop obbligatorio, il conto simulato, `bot/risk/hard_limits.py`.

### Decisioni per Alessio

* Il riavvio con la versione 8 sul conto simulato, e il «riparti», sono suoi. Al primo passo la memoria si ricostruisce una volta
  dal conto simulato (lo stato della copia non ha la versione della memoria): è il passaggio della versione 7, già rivisto.
* Due scelte le ha prese la sessione dalla sua frase del 26 novembre («non si deve fermare finché non ha raggiunto il 3% di profitto,
  è obbligatorio»). Con l'ok al riavvio le conferma, o ne sceglie altre:
  - sotto il 3% dopo la chiusura del programma si continua (il 204);
  - il fermo si toglie se il conto scende sotto il 3% durante il fermo (un funding pagato dopo la chiusura).
  - Quanto costa: per pochi centesimi il modello deve aprire un'altra operazione e pagare di nuovo entrata e uscita (con 0,11 BTC
    circa 12 USDT; con l'ordine minimo da 100 USDT circa 0,12). E nessuna perdita massima del giorno lo limita.
  - Quando succede: un funding delle 00, 08 o 16 UTC pagato dopo una chiusura di quei minuti, o il prezzo che si muove nell'attimo
    della chiusura.
  - Altre strade: tenere il fermo se mancano meno di pochi centesimi, chiudere solo con un piccolo margine sopra il 3%, o accettare un
    poco meno del 3%.
* Prima di un conto demo per il trader: 213 corretto, 212 misurato, 198 e 199 corretti, revisione nuova.

### Domande aperte

* La memoria del revisore (`reviews/`) da quest'area non si scrive. Le righe sono qui sotto, per la sessione delle crypto. Chi le
  applica? Restano da applicare anche quelle della sedicesima, del suo riesame e di `trader_ai/revisioni/righe_per_reviews.patch`.
* Nella cartella `rev17/` lavora nello stesso momento un altro processo: `mutazioni_rifatte.py`, `test_rev17.py`, `prima17/`,
  uscita `esito_mutazioni.txt`. Usa la stessa copia `rev17/copia_mut` e lo stesso blocco `rev17/x.lock` del mio primo giro.
  - Fra le 06:30 e le 06:34 UTC circa le due liste di mutazioni hanno scritto sugli stessi file, e i test hanno usato le stesse
    cartelle temporanee di pytest. Le righe di `rev17/esito_mutazioni.txt` scritte in quei minuti (fino a M28 circa) vanno rifatte.
  - I miei esiti validi sono solo in `rev17/revisore_lp/`.
  - Se anche quel processo numera i problemi da 213, chi riallinea i numeri?
* `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore` fallisce ancora, come alla sedicesima. È fuori dal
  percorso degli ordini: lo guarda la sessione della ricerca?

### Impronte md5 (primi 8 caratteri) dei file approvati

* Codice cambiato dal riesame: `trader_ai/avvio.py` 8ace7619, `trader_ai/limiti.py` 06ad62e4, `trader_ai/messaggio.py` f5201c43,
  `trader_ai/REGOLE.md` ec75e77f, `trader_ai/README.md` 358f4fb5.
* Uguali al riesame: `giro.py` 32156f63, `ripara.py` 392908eb, `istruzioni.md` cc36e981, `conto_simulato.py` c7f7e815, `operazioni.py`
  3120d09a, `costi.py` 2b1e9f30, `conto_demo.py` 453e0288, `sveglia.py` 6fd9d573, `config.json` 6ad5da2d.
* Test: `tests/test_obiettivo_riesame.py` cc2b1f5d (nuovo), `tests/test_obiettivo_netto.py` 24f039ce, `tests/test_controllo_26.py`
  5808b10c, `tests/test_trader_ai.py` 73aa19e2, `tests/test_avvio.py` 37c0be12, `tests/test_simulato.py` 5d0acfe5,
  `tests/test_corse_188.py` f759675a, `tests/test_secondo_riesame.py` b372138c.
* `bot/risk/hard_limits.py` 841f04e6, invariato.
* Impronte rilette alla fine della revisione (06:49 UTC): uguali.

### Righe per `reviews/` (da applicare dalla sessione delle crypto)

* `reviews/REVIEW_LOG.md`, riga nuova in fondo (poi le voci chiuse più vecchie delle ultime 10 vanno in `ARCHIVE.md`):
  `| 2026-11-27 | claude/brave-albattani-1b12fv | non committato su 11ad4c2 (md5 avvio.py 8ace7619, limiti.py 06ad62e4, messaggio.py f5201c43) | trader AI versione 8, correzioni del riesame della sedicesima: limite in attesa annullato con rilettura, stato e motivo salvati prima della chiamata, centesimo sempre, fermo tolto se il conto scende sotto il 3% | APPROVE con condizioni (207, 209-211 chiusi, 208 in parte; Bassi 213-216, il 216 c'era già) | aperta: riavvio con l'ok di Alessio, che conferma le scelte 204 e fermo tolto; 213 e 212 prima di un demo | trader_ai/revisioni/2026-11-27-diciassettesima.md |`
* `reviews/INDEX.md`:
  - riga «Numeri dei problemi»: «trader AI fino al 216 (`trader_ai/revisioni/2026-11-27-diciassettesima.md`): i nuovi partono da
    217»;
  - nella riga «Trader AI» aggiungere: «diciassettesima (correzioni del riesame): APPROVE con condizioni (213-216 Bassi; 213 finestra
    di una lettura del saldo dopo la chiusura, da correggere prima di un demo)».
* `reviews/LIVE_PATH_MAP.md`:
  - sezione 15, riga dell'obiettivo: «obiettivo del 3% del conto della mezzanotte UTC, al centesimo, contato dopo le spese di chiusura
    (`limiti.py:15`, `:51-63`; `avvio.py:295-346`); fermo fino alla mezzanotte UTC solo se il guadagno dopo la chiusura arriva al 3%
    (`avvio.py:318-327`), tolto se durante il fermo il conto scende sotto il 3% senza niente di aperto (`avvio.py:279-294`); ordine
    limite in attesa annullato con rilettura (`avvio.py:301-308`, `:925-958`)»;
  - in «Storia degli invarianti»: «27 nov, trader AI versione 8, correzioni del riesame (non committato, APPROVE con condizioni):
    **invariante cambiato**, il fermo dell'obiettivo si toglie se durante il fermo il conto scende sotto il 3%; il centesimo vale anche
    prima della chiusura. Tetto, leva, stop e limiti fissi invariati».
