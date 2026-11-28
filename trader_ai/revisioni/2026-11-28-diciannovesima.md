# Diciannovesima revisione del trader AI — versione 9: la sveglia decisa dal modello e la ripartenza da 1.000 USDT

Revisore: live-path-reviewer, 28 novembre 2026, mattina. Oggetto: le modifiche non committate sul commit `8f06ed2` (branch
`claude/brave-albattani-1b12fv`; in testa adesso `c63f247`, che fuori da `trader_ai/avanti/` non tocca il trader). La differenza data
dalla sessione (`scratchpad/versione9.diff`, 478 righe) è uguale a `git diff HEAD` (confronto senza differenze). Le impronte dei file
sono quelle dette dalla sessione.

Prove mie nella cartella `/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/rev19/`
(sotto: «la cartella»), con blocchi e cartelle temporanee miei. Nessuna richiesta a Binance né al modello: conto finto, conto simulato con
mercato finto, modello finto. I dati veri di `trader_ai/avanti/` solo letti.

Il trader che gira adesso sulla macchina ha il codice approvato alla diciottesima: l'ultimo «acceso» del diario (28 nov, 06:33 UTC) è al
commit `5b7dde6e`, uguale a `bcf284d` in tutti i file `.py`, `config.json` e `istruzioni.md` (cambia solo `vps/installa.sh`, il
salvataggio ogni 10 minuti). Alle 07:30 UTC aveva un corto aperto (limite eseguito alle 07:12), conto 928,95, mezzanotte 942,50.

### Riepilogo e verdetto

**APPROVE con condizioni.** Nessun Bloccante, nessun Alto, nessun Medio. Sette problemi nuovi, tutti Bassi (268-274).

1. **Il modello viene sempre richiamato.** Ho provato ogni strada che la sessione chiedeva di guardare:
   - riavvio con una sveglia vecchia nello stato, cioè con l'«entro» nel passato: chiamata al primo passo (Q1);
   - tetto finito: niente sveglia, poi le candele, e a mezzanotte di nuovo chiamato (Q3);
   - fermo per l'obiettivo: nessuna chiamata durante il fermo, chiamata a mezzanotte (Q4);
   - fermo a mano: dopo «riparti» chiamato (Q5);
   - risposta non letta («errore», «rifiuto», «troncata», «fuori schema»): si torna alle candele (Q9 e il test della sessione).
   L'«entro» è sempre fra 1 e 240 minuti dopo la chiamata (`sveglia.py:40`, `:51`), e scatta anche con il prezzo fermo (`:72-73`).
2. **Niente chiamate a raffica.**
   - Prezzo che resta oltre il livello: una chiamata sola, perché il livello già superato non si rimette (Q2, `sveglia.py:43-48`).
   - Livelli attaccati al prezzo che oscilla: al massimo una chiamata al minuto (Q2b).
   - Limite eseguito: una chiamata, poi niente (Q6).
   - Mezzanotte: una volta (Q11).
   - Richiami e chiusure: come prima, subito e una volta.
   Il freno vero, oltre al minuto, resta il tetto di 5 dollari (`costi.py:22`, invariato). Con il costo vero di una chiamata (mediana
   0,054 dollari su 261 chiamate del diario) basta per circa 90 chiamate: a una al minuto, circa un'ora e mezza. È una scelta di
   Alessio (sotto, «Decisioni»).
3. **La sveglia con un'operazione aperta e con un limite in attesa.**
   - Stop, obiettivo, protezione e 3% girano a ogni passo come prima, con o senza chiamata.
   - Un limite eseguito chiama subito (test della sessione, Q6).
   - Restano due casi in cui il limite si esegue senza chiamata (271).
4. **La ripartenza da 1.000 USDT.**
   - Si fa solo sul conto simulato (`avvio.py:1106`), con il fermo a mano (`:1108`) e niente di aperto. Il niente di aperto si controlla
     due volte: nel trader sotto il blocco (`:1111`) e nel conto simulato sotto il suo blocco (`conto_simulato.py:438-439`).
   - Non manda richieste nuove e non tocca ordini.
   - Restano quattro buchi piccoli: 268 (un'operazione si può perdere), 269 (il resoconto del giorno mescola prima e dopo), 270 (ordine
     delle scritture e secondo «azzera»), 273 (un funding pagato dopo).
5. **Test** (comandi più sotto):
   - trader: 235 passati;
   - radice: 3097 passati, 1 fallito (lo stesso della ricerca, come alla diciottesima), 1 saltato;
   - mutazioni della sessione rifatte su una copia mia: 20 prese su 21, la A4 è davvero equivalente;
   - mutazioni mie: 4 prese su 12 dai test del repository; delle 8 vive, la R1 è la raffica che questa revisione doveva escludere e
     nessun test del repository la vede (274).

**Problemi nuovi** (tutti Bassi)
- **268.** «Azzera» dopo un «chiudi» che non ha preso il blocco cancella dalla memoria un'operazione chiusa e non ancora registrata.
- **269.** Il giorno della ripartenza il resoconto, la riga «oggi» del modello e la plancia mescolano il prima e il dopo, senza dirlo.
- **270.** «Azzera» rimette il conto a 1.000 prima di leggere e salvare lo stato; un secondo «azzera» perde il «prima» vero.
- **271.** Con la sveglia, due casi in cui un limite si esegue senza la chiamata promessa.
- **272.** Tempo e prezzo della sveglia contati dall'inizio del passo, non dalla risposta.
- **273.** Un funding pubblicato dopo la ripartenza, per una posizione chiusa prima, entra nel conto nuovo.
- **274.** Mutazioni vive: la raffica con un'operazione aperta (R1) e la ripartenza (R4-R6) senza test che le vedano.

**Condizioni**
1. Caricare il codice nuovo, «azzera» e «riparti» li approva Alessio (il trader manda ordini sul conto simulato). Procedura sulla macchina:
   - «chiudi» con il codice di adesso;
   - **se «chiudi» stampa «il blocco era occupato», rilanciare «chiudi»** prima di andare avanti (268: rilanciato, registra
     l'operazione, prova Z1c);
   - codice nuovo e servizio riavviato (resta fermo a mano);
   - «azzera»: deve stampare «conto da X a 1000 USDT», e nel diario deve comparire «ripartito da 1000 USDT»;
   - «riparti».
2. Dopo «riparti», la prima chiamata deve avere stato «ok», con una `sveglia` nella risposta. Lo schema nuovo ha un oggetto annidato
   (`$defs` e `$ref`, `anthropic.transform_schema`, 11 campi facoltativi): qui non si può provare senza una chiamata vera. Se la prima
   chiamata è «errore» con un rifiuto dello schema: «chiudi» e tornare alla versione 8.
3. Al commit il codice deve avere le impronte qui sotto.
   - Se cambiano solo i test (per esempio quelli del 274), basta questo.
   - Se cambia il codice (268-273), serve un riesame breve.
   - Consigliato prima di «azzera»: il 268, una riga di rifiuto più un test, e il 274 R1 (la prova `test_prove19c.py` è pronta da copiare).
4. Il 269 va corretto prima di «azzera», oppure Alessio sa che il resoconto di quel giorno mescola il prima e il dopo.
5. Prima di qualunque conto demo per il trader valgono le condizioni della diciottesima (198, 199, 212, 234, 242, la prova di
   `allOpenOrders`) e serve una revisione nuova.

### Oggetto

* Branch `claude/brave-albattani-1b12fv`, base `8f06ed2`, niente di committato. Fuori da `trader_ai/` e dalla plancia non cambia niente:
  `git diff HEAD --stat -- bot/ firebase/ ops/ .claude/ tests/ research/` è vuoto, `bot/risk/hard_limits.py` 841f04e6.
* File cambiati:
  - `sveglia.py`: `nuova()` (`:33-50`), `motivo()` con sveglia e prezzo (`:53-74`), `MINUTI_MIN, MINUTI_MAX = 1, 240` (`:21`);
  - `schema.py`: `Sveglia` (`:17-21`) e il campo `sveglia` di `Risposta` (`:42-43`);
  - `avvio.py`:
    - `limite_prima` e `giorno_nuovo` (`:236-237`, `:271`);
    - la scelta del motivo (`:379-393`);
    - la sveglia salvata dopo la risposta (`:438-443`);
    - `_chiamate` (`:496-514`);
    - `azzera` (`:1101-1125`) e il comando (`:1256-1259`);
  - `conto_simulato.py`: `azzera` (`:433-444`);
  - `messaggio.py`: la ripartenza nella memoria stabile (`:214-231`);
  - `istruzioni.md` (il paragrafo delle chiamate e la riga dei campi), `REGOLE.md` (versione 9), `README.md` (punto 7);
  - `vps/installa.sh`: il comando `azzera` (`:91-94`);
  - test nuovo `tests/test_sveglia.py` (16 casi);
  - plancia: `Adesso.tsx` e `dati.ts`, solo testi (fuori dal percorso degli ordini).
* Uguali alla diciottesima: `conto_demo.py` (8b34c79b), `limiti.py` (06ad62e4), `giro.py` (32156f63), `ripara.py` (392908eb),
  `operazioni.py` (3120d09a), `costi.py` (2b1e9f30), `modello.py` (46038db6), `config.json` (6ad5da2d, «simulato») e gli altri test. Nessun
  test tolto: 219 + 16 = 235.
* Invarianti coinvolti (sezione 15 della mappa): il ritmo delle chiamate (cambiato); il tetto di 5 dollari (ora l'unico freno al ritmo,
  invariato); il conto simulato (nuovo comando che lo rimette a 1.000); stop, leva, una sola operazione, 3% e fermo, «chiudi»: invariati.

### Checklist A–F

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py` invariato (841f04e6); `git diff HEAD` vuoto su `bot/`, `firebase/`, `ops/`, `.claude/`, `tests/`. **OK**
* Limiti nel codice, non in configurazione:
  - `limiti.py`, `costi.py` e `config.json` invariati;
  - i limiti nuovi della sveglia sono costanti nel codice (`sveglia.py:21-22`), non parametri;
  - il capitale della ripartenza è la costante `CAPITALE_PROVA` (`avvio.py:75`), non un argomento del comando (`:1257`). **OK**
* Parametri dalla dashboard: **NON APPLICABILE** (il trader non legge Firebase; la plancia cambia solo testi).
* Limiti di G1 sul demo: **NON APPLICABILE**.
* Pulsante che chiude tutto: «chiudi» invariato (`avvio.py:1052-1095`), fermo a file letto per primo (`:191`) e prima di ogni ordine
  (`:820`, `:884`, `:899`), senza Firebase. **OK**
  - «Azzera» richiede il fermo a mano e non lo toglie (`:1108`): il trader resta fermo fino a «riparti». **OK**
  - Dopo un «chiudi» che non ha preso il blocco, «azzera» perde l'operazione: **PROBLEMA 268**.

**B. Ordini**
* Passi, minimi, leva, margine, solo riduzione, prezzo mark degli stop: non toccati. **NON APPLICABILE**
* Identificativi: non toccati. **NON APPLICABILE**
* Stop per ogni posizione:
  - la protezione gira a ogni passo prima della scelta del motivo (`avvio.py:254-262`), con o senza chiamata (Q4, Q6, Q12);
  - la sveglia non decide niente sugli ordini;
  - con un limite che incrocia il prezzo, lo stop si mette subito come prima (`:914-924`). **OK**

**C. Stato e resilienza**
* Posizioni e ordini riletti dal conto a ogni passo, come prima. «Azzera» rilegge il conto sotto il blocco (`:1111`) e il conto simulato
  ricontrolla sotto il suo (`conto_simulato.py:436-439`). **OK**
* Stato vecchio senza `sveglia`: vale la regola delle candele (`sveglia.py:62-65`). Riavvio con una sveglia scaduta: chiamata subito (Q1).
  **OK**
* Ordine delle scritture di «azzera» e secondo «azzera»: **PROBLEMA 270**. Funding pagato dopo la ripartenza: **PROBLEMA 273**.
* Candele chiuse:
  - senza sveglia, la regola di prima;
  - con la sveglia, il modello si chiama anche a metà candela. È la scelta del proprietario; il messaggio porta la candela in corso
    come prima;
  - tempo e prezzo della sveglia contati dall'inizio del passo: **PROBLEMA 272**.
* Limiti di frequenza: nessuna richiesta nuova a Binance. Il prezzo della sveglia è quello già letto a ogni passo
  (`conto_simulato.py:92-97`, `markPrice`). **OK**
* Tentativi: un passo che si interrompe dopo la scelta del motivo si ripete al passo dopo, come prima con le candele; nessun tentativo
  infinito nuovo. **OK**
* Firebase e orologio: **NON APPLICABILE**.

**D. Separazione fra simulato, demo e conto vero**
* «Azzera» esiste solo sul conto simulato: `ContoDemo` non ha `azzera`, e `Trader.azzera` lo rifiuta (`avvio.py:1106-1107`;
  `test_azzera_solo_sul_conto_simulato`). **OK**
* `conto_simulato.azzera` cambia solo il file del conto, senza richieste nuove (`_aggiorna` legge le candele pubbliche come gli altri
  comandi). **OK**

**E. Segreti**
* Differenza letta tutta: nessuna chiave, nessun percorso di file segreti, nessun indirizzo nuovo. `installa.sh azzera` carica lo stesso
  file d'ambiente di «chiudi» (`:93`), senza stamparlo. **OK**

**F. Test** (comandi ed esiti; file nella cartella)
* Trader: `TRADER_AI_BLOCCO=<cartella>/blocco.lock python -m pytest trader_ai/tests -q -p no:cacheprovider --basetemp=<cartella>/pytmp`:
  **235 passed** in 12,0 s.
* Radice: `python3 -m pytest tests/ -q -p no:cacheprovider --basetemp=<cartella>/pytmp_radice` (`suite_radice2.txt`): **3097 passed,
  1 failed, 1 skipped** in 189 s. Il fallito è `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore` (ricerca),
  lo stesso della diciottesima. I test dei limiti fissi passano.
* Mutazioni (`mutazioni_rev19.py`, `esito_mutazioni.txt`; copia, blocco e cartella temporanea miei):
  - **sessione: 20 prese su 21**. La A4 è equivalente: `(ris.esito and None)` dà None in tutti e due i casi;
  - **mie: 4 prese su 12** (R2, R3, R10, R11). Le 8 vive:
    - R1 (raffica con un'operazione aperta) e R4 (ripartenza con l'operazione nello stato): le prendono le mie prove
      `test_prove19c.py` e Z1 (**274**);
    - R5 e R6 (controllo del conto simulato, blocco di «azzera»): nessuna prova (**274**);
    - R7, R8, R9, R12: effetti piccoli o nessuno (**274**).
* Mie prove (sul codice di adesso, 5d857221; tutte passano: dove una prova mostra un problema, l'asserzione descrive il problema):
  - `test_prove19.py`, 21 casi: Q1-Q11 come detto sopra; Z1-Z6 mostrano 268, 269, 270 e 273;
  - `test_prove19b.py`, 2 casi: Q12 e Q13 mostrano il 271;
  - `test_prove19c.py`, 1 caso: con un'operazione a mercato aperta e la sveglia, 20 passi senza eventi non chiamano. Sotto la
    mutazione R1 fallisce con 61 chiamate in mezz'ora;
  - `test_prove19d.py`, 1 caso (Z1c): «chiudi» rilanciato con il blocco libero registra l'operazione prima di «azzera».
* `git status` uguale prima e dopo: le mie prove non toccano il repository.

### Problemi

**268 — Basso. «Azzera» dopo un «chiudi» che non ha preso il blocco cancella un'operazione chiusa.**
* Dove: `avvio.py:1119-1120` (`aperta=None`), insieme a `:1089-1090` e `:191`.
* Scenario:
  - «chiudi» chiude la posizione sul conto e poi aspetta il blocco al massimo 30 secondi. Se il passo del servizio è lungo, finisce con
    «lo stato si aggiornerà al passo dopo (il blocco era occupato)», con `aperta` ancora nello stato;
  - col fermo a mano il passo esce subito (`:191`), quindi l'operazione aspetta «riparti» per essere registrata (Z1b: dopo «riparti»
    c'è);
  - «azzera» mette `aperta=None`. L'operazione sparisce da memoria, lezione e resoconto, e il suo risultato resta solo dentro il «prima»
    (Z1: 0 operazioni).
* Correzione per la sessione: in `azzera`, sotto il blocco, rifiutare se `st.get("aperta")` non è vuoto, con un messaggio tipo
  «c'è un'operazione da registrare: rilancia «chiudi»». Rilanciato, «chiudi» la registra (Z1c). Con un test.
* Fino alla correzione: la procedura della condizione 1.

**269 — Basso. Il giorno della ripartenza mescola il prima e il dopo, senza dirlo.**
* Dove:
  - `avvio.py:1119` (`conto_mezzanotte=capitale`);
  - il resoconto (`:1132-1220`);
  - la riga «oggi» della memoria (`messaggio.py:226`);
  - la plancia (`Adesso.tsx:212`, «da … (fine di ieri)»);
  - `REGOLE.md:12`.
* Prova Z2. Il resoconto del giorno dice:
  - «Conto: da 1000.00 a 1000.00 USDT, +0.00»;
  - «Operazioni chiuse: 1 (vinte 0, perse 1), netto -29.90»;
  - «Dall'inizio della prova (2026-11-24, 1000 USDT): +0.00».
  Non dice da nessuna parte che il conto è stato rimesso a 1.000.
* Nel caso vero: se «azzera» si fa oggi, il resoconto del 28 novembre avrà le operazioni della mattina (mezzanotte vera 942,50)
  accanto a un conto che parte da 1.000. Il modello legge «oggi: −X» nel bilancio e un guadagno del giorno da 1.000. La plancia
  chiama «fine di ieri» un 1.000 che non lo è.
* `REGOLE.md:12` dice «il 3% … sulla fine del giorno prima (non sui 1.000 di partenza)», ma il giorno della ripartenza la base è 1.000.
* Correzione per la sessione:
  - `azzera` salva `st["ripartenza"]` (ora, conto di prima, mezzanotte di prima);
  - il resoconto scrive una riga «ripartito da 1.000 alle HH:MM UTC; prima, da mezzanotte, da M a P» e separa le operazioni di prima;
  - la memoria dice «oggi, dopo la ripartenza»;
  - la plancia dice «a mezzanotte o alla ripartenza»;
  - in `REGOLE.md` una frase sul giorno della ripartenza.

**270 — Basso. Ordine delle scritture di «azzera» e secondo «azzera».**
* Dove: `avvio.py:1114-1124`.
* Scenario:
  - il conto simulato va a 1.000 (`:1114`) prima che lo stato si legga (`:1115`) e si salvi (`:1124`);
  - se lo stato non si legge (file rovinato: Z5) o il salvataggio fallisce (Z6), il conto è a 1.000 e lo stato ha la mezzanotte vecchia;
  - al «riparti» il guadagno del giorno sembra +40. Il trader scrive «obiettivo del giorno raggiunto: chiuso tutto, fermo fino a
    mezzanotte UTC» e si ferma per il giorno (Z6);
  - un secondo «azzera» lo stesso giorno scrive come «prima» il 1.000 appena messo (Z3: `prima.fine` 1000, giorno quello nuovo): il
    conto vero di prima si perde dallo stato (resta solo nel movimento «azzeramento» del conto simulato).
* Correzione per la sessione:
  - leggere e preparare lo stato prima di `self.c.azzera`;
  - rifiutare un secondo «azzera» se il conto è già al capitale e non c'è stata nessuna operazione dopo, oppure tenere una lista
    delle ripartenze.

**271 — Basso. Con la sveglia, due casi in cui un limite si esegue senza la chiamata promessa.**
* Dove: `avvio.py:887-898` (limite che incrocia il prezzo, eseguito subito a mercato dentro `_esegui`) e `:831-833` (limite eseguito
  mentre il modello pensa, risposta «modifica»).
* Perché manca la chiamata: al passo dopo `in_attesa` è già falso, `limite_prima` è falso (`:236`) e la chiamata «il tuo ordine limite
  si è eseguito» (`:387`) non arriva.
* Prove:
  - Q12: un'ora senza chiamate, con un lungo aperto da un limite che incrocia e la sveglia a 240 minuti;
  - Q13: lo stesso dopo una «modifica».
* `REGOLE.md` promette «con la sveglia anche quando un suo ordine limite si esegue». La posizione ha sempre il suo stop.
* Nel diario vero: 0 limiti eseguiti subito su 16.
* Correzione per la sessione: nei due rami mettere `st["richiama"]` («il tuo ordine limite si è eseguito subito a …» e «… mentre
  decidevi»), con test.

**272 — Basso. Tempo e prezzo della sveglia contati dall'inizio del passo.**
* Dove: `avvio.py:441` usa `ora` (inizio del passo) e `prezzo` (letto prima della chiamata).
* Effetto: l'«entro» e il minuto minimo contano dall'inizio della chiamata, non dalla risposta. Q10: con una risposta dopo 3 minuti,
  «entro 5 minuti» diventa 2 minuti dopo la risposta.
* Con le durate vere (261 chiamate nel diario: mediana 9,9 s, massimo 25,6 s) la differenza resta sotto il mezzo minuto.
* Correzione per la sessione: usare `self.ora()` alla risposta, oppure scrivere in `istruzioni.md` e `REGOLE.md` «dall'inizio della
  chiamata». Priorità bassa.

**273 — Basso. Un funding pagato dopo la ripartenza entra nel conto nuovo.**
* Dove: `conto_simulato.py:250-268` (`_funding` vale anche per le posizioni chiuse) e `:433-444` (`azzera` lascia `chiuse`).
* Scenario: un pagamento pubblicato dopo la ripartenza, per una posizione aperta all'ora del funding e chiusa prima della ripartenza,
  entra nel conto nuovo. Z4: 997,57 con un tasso dello 0,1%; con lo 0,01% normale circa 0,24 USDT.
* Finestra: una ripartenza pochi minuti dopo le 00:00, 08:00 o 16:00 UTC, con una posizione aperta a quell'ora.
* Correzione per la sessione: scrivere nella procedura «azzera almeno 10 minuti dopo un'ora di funding». Oppure: `azzera` salva l'ora
  e `_funding` non somma (ma scrive un movimento) i pagamenti di posizioni chiuse prima.

**274 — Basso. Mutazioni vive per i test del repository.**
* R1 (`avvio.py:236`, `limite_prima = bool(a)`):
  - con un'operazione a mercato aperta e la sveglia, una chiamata a ogni passo: 61 in mezz'ora;
  - è la raffica che questa revisione doveva escludere: oggi il codice è giusto, ma nessun test vedrebbe il ritorno indietro;
  - la prende `test_prove19c.py`.
* R4 (`azzera` lascia l'operazione nello stato): la prende solo la mia Z1 (vedi 268).
* R5 (controllo del niente di aperto in `conto_simulato.azzera` tolto) e R6 (`azzera` senza blocco): nessuna prova. Il controllo del
  trader copre il primo. Il blocco evita che il salvataggio nel repository prenda a metà stato e conto.
* R7, R8, R9 ed R12:
  - R7: un prezzo uguale al livello verrebbe messo e scatterebbe dopo un minuto;
  - R8: il testo della mezzanotte anche senza sveglia;
  - R9: equivalente;
  - R12: «azzera» senza togliere il fermo dell'obiettivo; dopo «riparti» si avrebbe un falso «fermo tolto».
* Correzione per la sessione: almeno R1 (la prova è pronta da copiare) e il test del 268.

### Invarianti modificati

* **Il ritmo delle chiamate.** Fino alla versione 8, una chiamata a ogni candela da 15 minuti e subito alle chiusure. Dalla 9 lo
  decide il modello:
  - prezzo mark sopra o sotto, tempo da 1 a 240 minuti, almeno un minuto fra due chiamate della sveglia;
  - in più, subito quando un suo limite si esegue (con il buco del 271) e a mezzanotte UTC;
  - senza sveglia, la regola di prima.
  Non è un invariante di sicurezza: lo stop sul conto, la protezione a ogni passo e il 3% non dipendono dalle chiamate. Il tetto di
  5 dollari (`costi.py:22`) resta l'unico freno al ritmo.
* **Nuovo: il conto simulato si rimette a 1.000 USDT** con «azzera»:
  - solo sul simulato, solo con il fermo a mano, solo senza niente di aperto (controllato due volte), sotto il blocco;
  - la prova riparte da quel giorno (inizio, mezzanotte, discesa, niente fermo né sveglia);
  - la memoria del modello resta.
* Invariati: leva intera 1-10, una sola operazione o un solo limite, stop obbligatorio e protezione, 3% dopo le spese e fermo, «chiudi»,
  tetto di 5 dollari, limiti fissi del bot, conto demo spento.

### Decisioni per Alessio

1. **Il ritmo.** Minimo un minuto, massimo quattro ore. Con il costo di oggi (mediana 0,054 dollari a chiamata, diario) il tetto basta
   per circa 90 chiamate: se il modello si fa chiamare ogni minuto, finisce in circa un'ora e mezza. Poi niente chiamate fino a
   mezzanotte UTC, e l'operazione aperta resta solo con stop e obiettivo. Lui ha detto «non voglio limitare il modello». Va
   confermato che l'unico freno è il tetto di 5 dollari, oppure va scelto un minimo più alto.
2. **Il 3% il giorno della ripartenza.** Quel giorno si conta su 1.000, non sul conto vero della mezzanotte (942,50 oggi alle 07:30
   UTC). Da confermare.
3. **La memoria resta** (23 operazioni, 25 lezioni): il modello riparte da 1.000 ma ricorda. Lui ha chiesto «riparti da 1000 USD», non
   «dimentica». Da confermare.
4. **Quando ripartire.** Oggi stesso, con il resoconto del 28 novembre mescolato (269), oppure dopo la correzione del 269 (e del 268).
5. **Riavvio.** Codice nuovo, «azzera» e «riparti» solo con il suo ok, con la procedura della condizione 1.

### Domande aperte

1. Alessio vuole la ripartenza oggi stesso, accettando che il resoconto del 28 novembre mescoli il prima e il dopo (269), o dopo la
   correzione?
2. La sessione corregge il 268 prima di «azzera», o si segue la procedura (rilanciare «chiudi» se il blocco era occupato)?
3. L'interfaccia del modello accetta lo schema nuovo con la `sveglia` annidata? Qui non si può provare: lo dice la prima chiamata dopo
   il riavvio, che deve avere stato «ok».
4. Per il funding dopo la ripartenza (273): basta scriverlo nella procedura, o si corregge il conto simulato?

### Impronte md5 (primi 8 caratteri) dei file approvati

| File | Impronta |
|---|---|
| `trader_ai/avvio.py` | 5d857221 |
| `trader_ai/sveglia.py` | 6d281f39 |
| `trader_ai/schema.py` | 948769ce |
| `trader_ai/conto_simulato.py` | f6c2f6ca |
| `trader_ai/messaggio.py` | 99141ece |
| `trader_ai/istruzioni.md` | b90ccb2d |
| `trader_ai/REGOLE.md` | af211811 |
| `trader_ai/README.md` | 07b693fe |
| `trader_ai/vps/installa.sh` | b627e1f2 |
| `trader_ai/tests/test_sveglia.py` | 7bca6741 |
| `dashboard/app/components/trader_ai/Adesso.tsx` (solo testi) | 69826108 |
| `dashboard/app/components/trader_ai/dati.ts` (solo testi) | 9a5eb878 |
| invariati: `conto_demo.py` 8b34c79b, `limiti.py` 06ad62e4, `giro.py` 32156f63, `ripara.py` 392908eb, `operazioni.py` 3120d09a, `costi.py` 2b1e9f30, `modello.py` 46038db6, `config.json` 6ad5da2d | |

Il `README.md` deve aggiungere 268-274 fra gli aperti (oggi non li ha).

### Righe per `reviews/` (da applicare dalla sessione delle crypto)

**`reviews/REVIEW_LOG.md`**: la riga della diciottesima passa a «superata dalla diciannovesima (riavvio della versione 8 fatto: acceso
al `5b7dde6e`, codice uguale a `bcf284d`)». Riga nuova:

| 2026-11-28 | claude/brave-albattani-1b12fv | non committato su `8f06ed2` (md5 `avvio.py` 5d857221, `sveglia.py` 6d281f39, `schema.py` 948769ce, `conto_simulato.py` f6c2f6ca, `messaggio.py` 99141ece, `test_sveglia.py` 7bca6741) | trader AI versione 9: sveglia decisa dal modello (prezzo mark sopra o sotto, 1-240 minuti, almeno un minuto; più limite eseguito e mezzanotte), comando «azzera» del conto simulato a 1.000 USDT | APPROVE con condizioni (Bassi 268-274) | aperta: caricare, «azzera» e «riparti» con l'ok di Alessio (procedura: «chiudi» rilanciato se il blocco era occupato); prima chiamata «ok»; prima di un demo le condizioni della diciottesima | `trader_ai/revisioni/2026-11-28-diciannovesima.md` |

**`reviews/INDEX.md`**, sezione «Stato»:
- **Ultima revisione**: trader AI, diciannovesima (28 nov, `trader_ai/revisioni/2026-11-28-diciannovesima.md`): APPROVE con condizioni
  per la versione 9 (sveglia decisa dal modello, «azzera» a 1.000), Bassi 268-274; md5 `avvio.py` 5d857221, `sveglia.py` 6d281f39.
- **Numeri dei problemi**: fino al 274; i nuovi partono da 275, per tutte le aree.
- Trader AI: diciannove revisioni; la versione 8 gira dal 28 nov 06:33 UTC (`5b7dde6e`, codice uguale a `bcf284d`).

**`reviews/LIVE_PATH_MAP.md`**, sezione 15 (titolo: «versione 9 non committata su `8f06ed2`, approvata alla diciannovesima»), dopo la
riga del tetto:

* quando chiamare (versione 9): sveglia del modello in ogni risposta (`schema.py:17-21`, `:42-43`), salvata dopo la risposta letta,
  anche se scartata, e tolta senza risposta (`avvio.py:438-443`); prezzo mark del passo sopra o sotto, tempo da 1 a 240 minuti, almeno un
  minuto (`sveglia.py:21-22`, `:53-74`); in più limite eseguito e mezzanotte (`avvio.py:383-390`; buco 271); senza sveglia ogni candela
  da 15 minuti; chiusure e richiami subito; unico freno il tetto;
* «azzera» (`avvio.py:1101-1125`, `conto_simulato.py:433-444`, `installa.sh:91-94`): solo simulato, fermo a mano, niente di aperto
  (due controlli), sotto il blocco; inizio, mezzanotte e discesa nuovi, memoria tenuta (268, 269, 270, 273).

In «Storia degli invarianti»:
- 28 nov, trader AI versione 9 (non committata, diciannovesima, APPROVE con condizioni): **invariante cambiato**, il ritmo delle
  chiamate lo decide il modello (1-240 minuti, almeno uno; limite eseguito e mezzanotte), freno solo il tetto di 5 dollari; **nuovo**
  il conto simulato rimesso a 1.000 USDT con il fermo a mano. Stop, leva, 3%, «chiudi» e limiti fissi invariati.

### Riesame

Revisore: live-path-reviewer, 28 novembre 2026, poco dopo. Oggetto: le correzioni di 268, 269 e i test del 274, non committate su
`8f06ed2`. La differenza data (`scratchpad/versione9_b.diff`, 229 righe) è uguale a `git diff 8f06ed2` di `avvio.py` e `messaggio.py`.
Rispetto alla copia rivista sopra (`rev19/copia`: `avvio.py` 5d857221, `messaggio.py` 99141ece) cambiano solo:
* `azzera` (`avvio.py:1113-1117`, `:1121`): legge lo stato prima del conto, rifiuta con «aperta» e salva l'ora;
* il resoconto (`:1139-1143`, `:1155-1158`);
* `_ripartenza_di_oggi`, la riga «oggi» e la riga del conto (`messaggio.py:211-214`, `:232-234`, `:348-353`);
* la plancia, solo testi.

**Verdetto: APPROVE con condizioni.** Nessun Bloccante, nessun Alto, nessun Medio.

| Problema | Esito | Prova |
|---|---|---|
| 268 | **chiuso** | «Azzera» rifiuta: «nello stato c'è ancora un'operazione da registrare: rilancia «chiudi», poi «azzera»». La mia Z1 ora finisce con questo rifiuto, senza toccare il conto. Il rifiuto non blocca la strada, perché «chiudi» rilanciato registra e vuota «aperta» (Z1c passa). Test del repository `test_azzera_rifiuta_con_un_operazione_non_registrata`; mutazione N1 presa. |
| 269 | **chiuso** | Mia prova E1 (`test_prove19e.py`), con un'operazione prima e una dopo la ripartenza. Il resoconto dice «Ripartito da 1000 USDT alle 10:05 UTC (prima il conto era a 970.10)», «Conto: da 1000.00 a 966.23, -33.77» e «Operazioni chiuse: 1 … netto -33.77»: conto e operazioni ora tornano. Il messaggio dice «oggi (24/11, dalla ripartenza)» e «dalla ripartenza delle 10:05 UTC -33.77», con il 3% «del conto alla ripartenza». Il giorno dopo torna «da mezzanotte». Il confronto delle ore come testo regge: sul conto simulato un'operazione aperta dopo la ripartenza chiude in un minuto che comincia dopo. Mutazioni N3-N7 prese. Resta un dettaglio: **275**. |
| 270 | **in parte** | Uno stato illeggibile ora ferma «azzera» prima di toccare il conto: la mia Z5 vede il conto rimasto a 943. Restano il salvataggio che fallisce dopo il conto (Z6 passa ancora) e il secondo «azzera» (Z3). Basso, aperto. |
| 271, 272, 273 | aperti, come detto | Il 273 va nella procedura («non lanciare «azzera» nei minuti subito dopo le 00:00, 08:00 e 16:00 UTC»). Oggi non è scritto in nessun file: `REGOLE.md` e `README.md` hanno le stesse impronte. |
| 274 | **chiuso in parte** | La R1 (raffica con un'operazione aperta) ora la prende `test_operazione_aperta_con_la_sveglia_niente_raffica`, e la R4 il test del 268. Mutazioni del riesame (`mutazioni_riesame.py`, `esito_mutazioni_riesame.txt`): 8 prese su 10. Le due vive sono il «solo il giorno della ripartenza» del messaggio (N8, la prende la mia E1) e quello del resoconto (R2: nei giorni dopo il resoconto ripeterebbe la riga «Ripartito»). Restano vive anche R5 e R6 della prima parte. |

**Nuovo, Basso**
- **275.** Il giorno della ripartenza la riga del resoconto «BTCUSDT negli stessi orari» parte ancora da mezzanotte
  (`prezzo_inizio_giorno`, non toccato da `azzera`). Conto e operazioni invece partono dalla ripartenza (E1: «da 90000 a 87900» con la
  ripartenza alle 10:05).
  - Correzione per la sessione: in `azzera` `prezzo_inizio_giorno` = il prezzo di adesso, oppure la riga dice «da mezzanotte».

**Test**
* Trader: `TRADER_AI_BLOCCO=<cartella>/blocco5.lock python -m pytest trader_ai/tests -q -p no:cacheprovider`: **237 passed** in 11,9 s.
* Mie prove sul codice nuovo: 23 passate, 3 fallite, tutte e tre attese (`test_prove19*.py`):
  - Z1 fallisce perché ora c'è il rifiuto (268 chiuso);
  - Z2 fallisce perché il resoconto ora separa (269 chiuso);
  - Z5 fallisce perché lo stato illeggibile ora ferma prima del conto (270 in parte).
* Mia E1 (`test_prove19e.py`): passa.
* Suite della radice: non rilanciata. Nessun file fuori da `trader_ai/` e dalla plancia è cambiato, e nessun test di `tests/` usa
  `trader_ai`; l'ultimo giro, sopra, dava 3097 passati e 1 fallito della ricerca.

**Condizioni** (al posto di quelle sopra)
1. Codice nuovo, «azzera» e «riparti» solo con l'ok di Alessio. Procedura sulla macchina:
   - «chiudi»;
   - codice nuovo e servizio riavviato (resta fermo a mano);
   - «azzera»: se rifiuta per «un'operazione da registrare», rilanciare «chiudi» e poi «azzera»; deve stampare «conto da X a 1000
     USDT»;
   - non lanciarlo nei 10 minuti dopo le 00:00, le 08:00 e le 16:00 UTC (273);
   - «riparti».
2. Dopo «riparti», la prima chiamata deve avere stato «ok» e una `sveglia` nella risposta. Se lo schema viene rifiutato: «chiudi» e
   tornare alla versione 8.
3. Al commit, le impronte qui sotto.
   - Se cambiano solo i test o i testi (per esempio la riga del 273 nella procedura), basta così.
   - Se cambia il codice, serve un riesame.
4. Prima di un demo valgono le condizioni della diciottesima, e serve una revisione nuova.

**Impronte md5 approvate al riesame (primi 8 caratteri)**

| File | Impronta |
|---|---|
| `trader_ai/avvio.py` | 3e7b1218 |
| `trader_ai/messaggio.py` | 4970115b |
| `trader_ai/tests/test_sveglia.py` | 3d043e73 |
| `trader_ai/sveglia.py` | 6d281f39 |
| `trader_ai/schema.py` | 948769ce |
| `trader_ai/conto_simulato.py` | f6c2f6ca |
| `trader_ai/istruzioni.md` | b90ccb2d |
| `trader_ai/REGOLE.md` | af211811 |
| `trader_ai/README.md` | 07b693fe |
| `trader_ai/vps/installa.sh` | b627e1f2 |
| `dashboard/app/components/trader_ai/Adesso.tsx` (solo testi) | 7e210d3a |
| `dashboard/app/components/trader_ai/dati.ts` (solo testi) | 5224af9b |
| invariati: `conto_demo.py` 8b34c79b, `limiti.py` 06ad62e4, `giro.py` 32156f63, `ripara.py` 392908eb, `operazioni.py` 3120d09a, `costi.py` 2b1e9f30, `modello.py` 46038db6, `config.json` 6ad5da2d | |

Il `README.md` deve aggiungere fra gli aperti 270 (in parte), 271, 272, 273 (con la procedura), 274 (in parte) e 275.

**Righe per `reviews/`**: nella riga nuova di `REVIEW_LOG.md` (sopra) le impronte diventano `avvio.py` 3e7b1218, `messaggio.py`
4970115b, `test_sveglia.py` 3d043e73 (le altre uguali). Oggetto: «più il riesame: 268 e 269 chiusi, 274 in parte». Verdetto:
«APPROVE con condizioni (riesame: aperti 270 in parte, 271-273, 274 in parte, 275 Basso nuovo)». In `INDEX.md`: problemi fino al 275,
i nuovi partono da 276.
