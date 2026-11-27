# Sedicesima revisione del trader AI — versione 8 (le tre decisioni del proprietario)

Revisore: live-path-reviewer, 26 novembre 2026. Modifiche non committate su `11ad4c2` (branch `claude/brave-albattani-1b12fv`; ultimo
commit dell'area `624d867`, ultimo del codice `82baadc`). Le prove sono nella cartella di lavoro
`/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/revisione_obiettivo/` (sotto: «la
cartella»). Nessuna richiesta a Binance: il mercato è quello finto dei test. I dati veri di `trader_ai/avanti/` solo letti.

### Riepilogo e verdetto

**APPROVE con condizioni.** Nessun Bloccante, nessun Alto. Un Medio (203, test) e tre Bassi (204, 205, 206).

1. **Le tre decisioni sono nel codice come le ha dette il proprietario.**
   - Tetto: resta 5 dollari, nessun cambio (`costi.py:22`, impronta invariata).
   - Istruzioni: stesse frasi, senza maiuscole (`istruzioni.md:4-10`). L'unica aggiunta è «contato dopo le spese di chiusura», cioè la
     decisione 3. Nessun consiglio di strategia.
   - Il 3% dopo le spese di chiusura. Provato con il conto simulato vero e il programma vero, lungo e corto, 0,11 BTC a leva 10:
     - sopra il 3% prima delle spese ma sotto dopo, il programma **non** chiude. Il codice di prima lì chiudeva e realizzava 27,02
       invece di 30;
     - mezzo dollaro di BTC sopra la soglia vera, chiude: guadagno **realizzato** 30,055.
   - Le spese contate alla soglia sono 5,96 USDT su circa 9.940 di valore (commissione 0,05% e scarto 0,01%). Al centesimo, sono quelle
     che il conto simulato toglie davvero quando chiude.
2. **Un solo numero dappertutto.** `avvio.passo` e `giro.decidi` usano la stessa funzione sullo stesso conto con le spese (una spia su
   `decidi` vede le spese 5,96). Il messaggio dice gli stessi numeri del programma: «da mezzanotte UTC +32.98, +27.02 se chiudi adesso
   (spese di chiusura tolte) ... mancano 2.98» e «uscita a mercato circa 5.96».
3. **Senza posizione, o con un ordine limite in attesa, niente cambia.** 16 scenari danno lo stesso esito sul codice committato e sul
   nuovo: decisioni, chiamate, «mancano», eventi, ordini.
4. **Fermo e resoconto sono giusti nel caso normale.**
   - Fermo fino alle 00:00 UTC, e per 14 ore nessuna chiamata.
   - A mezzanotte il resoconto dice «Conto: da 1000.00 a 1030.05 USDT, +30.05 (+3.01%)» e «Obiettivo del 3% (30.00 USDT): raggiunto
     alle 10:16 UTC».
   - Poi il fermo si toglie e le chiamate riprendono.
5. **Nessun test indebolito.**
   - Passano 150 test: prima erano 148, 2 sono nuovi, nessuno è stato tolto. L'unica asserzione cambiata è più severa.
   - I 3 test nuovi o cambiati falliscono sul codice committato.
   - Nei dati veri l'obiettivo non è mai stato raggiunto (al massimo +8,40 il 25 e +2,49 il 26): nessun giorno passato cambia.

**Problemi**
- **203, Medio.** I test non coprono tutta la modifica: 7 mutazioni su 19 sopravvivono. Fra queste:
  - lo scarto tolto dalle spese;
  - `giro.decidi` che guarda il conto prima delle spese (con questo errore il modello resterebbe senza chiamate e la posizione aperta);
  - le spese contate anche con un limite in attesa;
  - la frase del proprietario cambiata.
- **204, Basso, c'era già prima.** Dopo la chiusura il guadagno vero può restare sotto il 3%. Il programma si ferma lo stesso fino a
  mezzanotte e il resoconto dice «raggiunto». Due prove:
  - 10 dollari di BTC contro nel secondo della chiusura: realizzato 28,96;
  - uno stop scattato nel minuto che si chiude durante la chiusura: realizzato 21,10 (+2,11%).
- **205, Basso.** Il test delle istruzioni non vede un cambio della frase del proprietario.
- **206, Basso.** Il diario e le lezioni tengono solo il guadagno prima delle spese di chiusura, e una lezione lo chiama «netto».

**Condizioni**
1. **Prima del commit**, i test del 203. C'è una base pronta: `test_prove_obiettivo.py` nella cartella, che prende le tre mutazioni vive
   del codice. Se cambiano solo test e testi, il codice da committare deve avere le impronte in fondo. Altrimenti serve una revisione
   nuova.
2. Il riavvio si fa solo con l'ok di Alessio, perché cambia il momento in cui il programma chiude tutto.
3. Il 204 lo decide Alessio. Se il codice cambia, serve una revisione nuova.

### Oggetto

* `git diff HEAD -- trader_ai/`: 7 file, +77 −20.
  - `limiti.py`: campo `Conto.spese_chiusura` (`:46-48`), funzione `guadagno_netto` (`:51-53`), `obiettivo_raggiunto` sul netto
    (`:56-57`).
  - `avvio.py`:
    - `_conto` con il prezzo e le spese di chiusura (`:435-448`);
    - il prezzo passato in `passo` (`:266`) e in `_esegui` (`:746`);
    - campo `guadagno_netto` nell'evento dell'obiettivo (`:278-280`);
    - importazioni (`:47-48`).
  - `messaggio.py`: `blocco_conto` (`:325-333`).
  - `istruzioni.md` (`:4-10`).
  - `REGOLE.md`: versione 8 (`:1-6`, `:55`, `:125-126`, `:168`).
  - Test: `tests/test_controllo_26.py` con due test nuovi (`:655-682`); `tests/test_trader_ai.py`, asserzione delle istruzioni
    (`:282-287`).
* Riletti e invariati:
  - `giro.py`, controllo a `:33` e diario a `:63`;
  - `conto_simulato.py`: saldo `:346-357`, chiusura `:433-444`, `_chiudi_posizione` `:283-298`;
  - `operazioni.py:26-28`;
  - `costi.py:22`;
  - il resoconto (`avvio.py:981-1067`).
* Invariante coinvolto: l'obiettivo del giorno e il fermo fino a mezzanotte (`LIVE_PATH_MAP.md`, sezione 15).

### Checklist A–F

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py` è invariato: `git diff HEAD --stat -- bot/ firebase/ ops/` è vuoto. **OK**
* I limiti stanno nel codice, non in configurazione. **OK**
  - Il 3% è a `limiti.py:15`, la leva fino a 10 a `:16`, il tetto a `costi.py:22`.
  - Le spese vengono dalle costanti del conto simulato (`conto_simulato.py:43`, `:50-51`), lette da `operazioni.py:16` e `:26-28` e da
    `avvio.py:47-48`: nessun numero scritto a mano.
  - `config.json` non cambia.
* Parametri dalla dashboard: **NON APPLICABILE**, il trader non legge Firebase.
* Limiti di G1 sul demo: **NON APPLICABILE**.
* Pulsante che chiude tutto. **OK**
  - Il comando «chiudi» (`avvio.py:942-975`) e il file del fermo (`:146-147`, letto a `:174` e `:713`) non sono toccati.
  - Vanno senza Firebase.

**B. Ordini**
* Passi, minimi, leva e margine non sono toccati (`avvio.py:743-761`). **NON APPLICABILE**
* Identificativo dell'ordine. **OK**
  - La chiusura dell'obiettivo usa ancora `_cid(ora, "x")` (`avvio.py:268`, `:149-150`).
* Solo riduzione: il conto simulato chiude la sua posizione (`conto_simulato.py:433-444`), il demo è spento. **NON APPLICABILE**
* Prezzo che attiva gli stop: il mark. **OK**
  - Anche le spese di chiusura si contano sul mark (`avvio.py:442-445`).
  - È lo stesso prezzo su cui chiude il conto simulato (`conto_simulato.py:435-441`).
* Stop per operazione: non toccato (`limiti.py:117`, `avvio.py:674-692`). **OK**

**C. Stato e resilienza**
* Conto, posizione e prezzo si leggono dal conto a ogni passo (`avvio.py:180-210`). **OK**
  - Le spese di chiusura sono un calcolo: nessuna richiesta in più.
* Flussi in tempo reale: **NON APPLICABILE**.
* Candele chiuse: non toccate. **OK**
* Errori. **OK**
  - Un errore di `mercato()` o `chiudi()` fa fallire il passo; il servizio lo scrive e riprova (`avvio.py:1111-1117`), come prima.
* Firebase e orologio: **NON APPLICABILE**.
* Corsa fra il controllo e la chiusura: **PROBLEMA 204**.
  - È Basso e c'era già.
  - Conto e prezzo vengono da due letture (`:207`, `:208`); la chiusura rilegge il prezzo.

**D. Separazione fra simulato, demo e conto vero**
* Il trader gira sul conto simulato (`config.json`, `avvio.py:1080-1082`). **OK**
  - Nessun ordine a Binance, solo letture pubbliche (`conto_simulato.py:42`, `:62-67`).
  - La modifica non aggiunge richieste.

**E. Segreti**
* La differenza, letta tutta, non contiene chiavi né percorsi di file segreti. **OK**
* Chiavi e permessi del demo: **NON APPLICABILE**, il demo è spento.

**F. Test** (comandi ed esiti; le prove sono nella cartella)
* `TRADER_AI_BLOCCO=/tmp/x.lock python -m pytest trader_ai/tests -q -p no:cacheprovider`: **150 passed** in 10,1 s.
* Codice committato con i suoi test (copia `vecchio/`): 147 passed e 1 failed. Il fallito è `test_il_fermo_non_entra_mai_in_git`, che
  chiede git, e la copia non sta dentro git. In tutto fanno 148.
* Test nuovi sul codice committato (`vecchio_test_nuovi/`): falliscono i tre nuovi o cambiati, più quello di git. Quindi coprono la
  modifica.
* Mutazioni sulla copia (`mutazioni.py`): **12 prese su 19**.
  - Restano vive M2, M9, M12, M16, M17, M18 e M19 (problemi 203 e 205).
  - M18 è equivalente: `controlla` non usa le spese.
* Le prove della revisione (`test_prove_obiettivo.py`): 5 passano sul codice nuovo.
  - Sul codice committato lo stesso caso chiude sotto il 3% (27,02).
  - Le prove prendono M2, M9 e M12 (`mutazioni_vive_contro_prove.py`).
* Codice committato contro codice nuovo (`differenziale.py`): 16 scenari, 0 differenze.
  - Gli scenari sono senza posizione e con un limite in attesa.
  - Il conto è a 1029,98, 1029,99, 1029,999, 1030, 1030,01, 1031, 1100 e 900.
  - «mancano 0.00» con 1029,999 senza chiusura succedeva già prima: è l'arrotondamento del testo.
* `python3 -m pytest tests/ -q`: **2825 passed, 1 failed, 1 skipped** in 207 s.
  - Il fallito è `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore`, della ricerca.
  - Fallisce anche da solo, e nessun test della radice importa `trader_ai`: non è legato a questa modifica.
  - I test dei limiti fissi (`tests/test_risk.py`, `tests/test_sizing.py`, demo, conto vero) passano.

### Problemi

**203 — Medio — `trader_ai/tests/test_controllo_26.py:657-682` e `trader_ai/tests/test_trader_ai.py:282-287` (codice coinvolto:
`avvio.py:442-447`, `giro.py:33`).**
* **Che cosa manca.**
  - Il test nuovo controlla la decisione di `passo` da lontano: sotto la soglia di metà delle spese, sopra di 0,01 USDT.
  - Per il lungo usa la formula della chiusura del corto (`1.0001` invece di `0.9999`; la differenza è 0,0001 USDT).
  - Usa il conto finto, che alla chiusura non toglie niente. Così non prova che il guadagno realizzato arrivi al 3%.
  - Non c'è un test di `giro.decidi` con le spese, né uno del limite in attesa.
* **Prova** (eseguita, `mutazioni.py`). Sopravvivono queste mutazioni:
  - **M2**: spese senza lo scarto d'uscita. Il programma chiuderebbe fino a circa 1 USDT prima del 3% vero (lo 0,01% di 9.940).
  - **M9**: `giro.decidi` che guarda il conto prima delle spese. Nella fascia fra le due soglie il modello non viene più chiamato e il
    programma non chiude. Provato: alla candela delle 10:15 nessuna chiamata (`assert 1 == (1 + 1)`). La posizione resta aperta con il
    solo stop finché il prezzo non esce dalla fascia.
  - **M12**: spese contate anche con un ordine limite in attesa.
  - **M19**: nell'evento, il campo `guadagno_netto` scritto senza togliere le spese.
* **Correzione** (sessione principale). Portare nei test del repository le prove di `test_prove_obiettivo.py`, che prendono M2, M9 e M12:
  - la soglia calcolata con le costanti del conto simulato;
  - il controllo a mezzo dollaro di prezzo sotto e sopra la soglia, lungo e corto;
  - il guadagno realizzato almeno 30 sul conto simulato vero;
  - alla candela dentro la fascia, la chiamata al modello e il conto passato a `decidi` con le spese;
  - spese zero con il limite in attesa e senza posizione;
  - `guadagno_netto` dell'evento uguale al realizzato.

  Correggere anche `1.0001` in `0.9999` per il lungo.

**204 — Basso, c'era già nel codice committato — `trader_ai/avvio.py:207-208`, `:266-282`, `:1007-1010`; `trader_ai/conto_simulato.py:433-444`.**
* **Che cosa succede.**
  - Il 3% si controlla con il conto letto all'inizio del passo.
  - La chiusura a mercato rilegge il prezzo e prima conta i minuti chiusi nel frattempo.
  - Dopo, il programma scrive «obiettivo raggiunto» e si ferma fino a mezzanotte senza rileggere quanto ha guadagnato davvero.
* **Prova** (eseguita, `test_prove_obiettivo.py`).
  - Il prezzo scende di 10 dollari fra il controllo e la chiusura, con 0,11 BTC. Il realizzato è 28,96, l'evento dice `guadagno_netto`
    30,05, e il programma si ferma fino a mezzanotte.
  - Il modello sposta lo stop a 90.300. Il controllo delle 10:16:59,5 vede 30,55 dopo le spese. La chiusura arriva alle 10:17:00,3: il
    conto simulato conta prima il minuto 10:16 (minimo 90.290) e lo stop scatta. Risultato:
    - realizzato 21,10;
    - operazione «stop spostato da te»;
    - fermo fino a mezzanotte;
    - nel resoconto «Conto: da 1000.00 a 1021.10 USDT, +21.10 (+2.11%)» insieme a «Obiettivo del 3% (30.00 USDT): raggiunto alle
      10:16 UTC».
  - Sul codice committato lo stesso caso finisce uguale (21,10 e fermo): non è una regressione. Quel codice, nella fascia, chiudeva
    sempre sotto il 3% (27,02).
* **Quanto conta.** È raro: serve un passo a cavallo della fine di un minuto, o un salto di prezzo nel secondo della chiusura. Il passo
  gira ogni 30 secondi più la sua durata (`avvio.py:65`, `:1111-1117`). Con la modifica il caso normale è giusto; prima era sempre
  sotto.
* **Correzione** (sessione principale, dopo la scelta di Alessio).
  - Dopo la chiusura, rileggere il conto e scrivere nell'evento il guadagno realizzato.
  - Mettere il fermo solo se il realizzato arriva al 3%. Altrimenti scrivere un evento «chiuso sotto il 3%» e continuare, oppure
    fermarsi lo stesso, se Alessio preferisce.
  - Nel resoconto, «raggiunto» solo con il realizzato al 3%.
  - Prendere conto e prezzo da una lettura sola (oggi sono due: `saldo` a `:207`, `mercato` a `:208`).

  Se il codice cambia, serve una revisione nuova.

**205 — Basso — `trader_ai/tests/test_trader_ai.py:282-287`.**
* Il test delle istruzioni guarda tre pezzi («Obiettivo obbligatorio», «Non è un tetto», «Impara dai tuoi risultati») e che il maiuscolo
  non ci sia più.
* **Prova** (eseguita, `mutazioni.py`). Il test passa anche con due cambi della frase del proprietario:
  - M16 aggiunge «anche alzando la leva dopo una perdita», cioè un consiglio di strategia;
  - M17 toglie «Finché non l'hai raggiunto devi continuare a cercare operazioni per arrivarci».
* **Correzione.** Confrontare per intero i due paragrafi (`istruzioni.md:4-10`) con il testo atteso. Così un cambio della frase del
  proprietario passa solo da un cambio voluto del test.

**206 — Basso — `trader_ai/giro.py:63`, `trader_ai/avvio.py:366`, `trader_ai/messaggio.py:138`, `trader_ai/README.md:32`.**
* Restano senza le spese di chiusura tre cose:
  - la riga del diario di ogni chiamata, che ha solo `guadagno_giorno` prima delle spese. Provato: 32,98, mentre il modello leggeva
    +27,02 e «mancano 2.98». Per misurare la decisione 3 nei primi giorni il numero dopo le spese manca;
  - le lezioni: salvano `giorno_netto`, che però è il guadagno prima delle spese, e il modello lo legge come «giorno a +X»;
  - il README, che dice «obiettivo del 3% al giorno» senza «dopo le spese di chiusura».
* **Correzione.**
  - Aggiungere `guadagno_netto` alla riga del diario.
  - Nelle lezioni, chiamare il campo `giorno_lordo` oppure salvarci il netto.
  - Aggiungere una frase al README.

### Invarianti modificati

* **L'obiettivo del giorno del trader AI cambia.**
  - Prima: conto ≥ conto della mezzanotte × 1,03.
  - Adesso: conto meno le spese di chiusura dell'operazione aperta ≥ conto della mezzanotte × 1,03 (`limiti.py:46-57`,
    `avvio.py:435-448`, controllo a `avvio.py:266-267` e `giro.py:33`).
  - Le spese sono quantità × (scarto + 0,05% del prezzo d'uscita). L'uscita, su BTC, è il mark meno lo 0,01% per un lungo e più lo
    0,01% per un corto.
  - Senza posizione o con un limite in attesa le spese sono zero, come prima.
  - Con un'operazione aperta a mezzanotte, la base resta il conto della mezzanotte con il risultato aperto. Quindi le spese di chiusura
    di quell'operazione contano nel giorno dopo, come nel resoconto.
* **Messaggio.** La riga del conto aggiunge «+X se chiudi adesso (spese di chiusura tolte)», e «mancano» si conta dopo le spese
  (`messaggio.py:325-333`).
* **Istruzioni.** Stesse frasi senza maiuscole, più «contato dopo le spese di chiusura» (`istruzioni.md:4-10`).
* **Evento dell'obiettivo.** Ha un campo nuovo, `guadagno_netto` (`avvio.py:278-280`).
* **Invariati:**
  - il tetto dei 5 dollari (`costi.py:22`);
  - la leva fino a 10 (`limiti.py:16`);
  - il fermo fino a mezzanotte (`avvio.py:276`);
  - il conto simulato;
  - `bot/risk/hard_limits.py`.

### Decisioni per Alessio

* Il riavvio con la versione 8 sul conto simulato è suo: cambia il momento in cui il programma chiude tutto.
* Problema 204: se dopo la chiusura il guadagno vero resta sotto il 3%, il programma deve fermarsi lo stesso fino a mezzanotte (come
  oggi) o continuare finché non arriva al 3% (come «non si deve fermare finché non ha raggiunto il 3%»)?
* Decisione 1, il tetto: si misura dal primo giorno. Il resoconto conta le chiamate, il costo medio e l'ora in cui finisce il tetto
  (`avvio.py:1044-1051`).

### Domande aperte

* La memoria del revisore (`reviews/`) da quest'area non si scrive: anche oggi il blocco delle aree ha rifiutato la scrittura. Le righe
  sono qui sotto, per la sessione delle crypto: chi le applica? Restano da applicare anche quelle del riesame e del secondo riesame della
  quindicesima (`trader_ai/revisioni/righe_per_reviews.patch`).
* `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore` fallisce anche da solo (nel contenitore c'è pandas 3.0.5).
  È fuori dal percorso degli ordini e non dipende da questa modifica: lo guarda la sessione della ricerca?

### Impronte md5 (primi 8 caratteri) dei file approvati

* Codice:
  - `trader_ai/limiti.py` a3e811bb;
  - `trader_ai/avvio.py` 62129355;
  - `trader_ai/messaggio.py` b6923e17;
  - `trader_ai/istruzioni.md` cc36e981;
  - `trader_ai/REGOLE.md` 74379c1f.
* Riletti e invariati:
  - `giro.py` 0b813210;
  - `conto_simulato.py` c7f7e815;
  - `operazioni.py` 3120d09a;
  - `costi.py` 2b1e9f30.
* Test di oggi, che cambieranno per il 203:
  - `tests/test_controllo_26.py` f21dcf67;
  - `tests/test_trader_ai.py` 5e4b6337.
* Impronte rilette alla fine della revisione: uguali.

### Righe per `reviews/` (da applicare dalla sessione delle crypto)

* `reviews/REVIEW_LOG.md`, riga nuova in fondo:
  `| 2026-11-26 | claude/brave-albattani-1b12fv | non committato su 11ad4c2 (md5 avvio.py 62129355, limiti.py a3e811bb, messaggio.py b6923e17, istruzioni.md cc36e981) | trader AI versione 8: tetto di 5 dollari confermato; istruzioni senza maiuscole; il 3% contato dopo le spese di chiusura | APPROVE con condizioni (Medio 203; Bassi 204-206) | aperta: 203 prima del commit; riavvio con l'ok di Alessio; 204 da decidere | trader_ai/revisioni/2026-11-26-sedicesima.md |`
* `reviews/INDEX.md`, la riga «Numeri dei problemi» diventa: «trader AI fino al 206 (`trader_ai/revisioni/2026-11-26-sedicesima.md`): i
  nuovi partono da 207». Nella riga «Trader AI» aggiungere: «sedicesima (versione 8, il 3% dopo le spese di chiusura): APPROVE con
  condizioni (203 Medio, 204-206 Bassi)».
* `reviews/LIVE_PATH_MAP.md`.
  - Sezione 15: la riga dell'obiettivo diventa «obiettivo del 3% del conto della mezzanotte UTC, contato dopo le spese di chiusura
    dell'operazione aperta (dal 26 nov, versione 8: `limiti.py:15`, `:51-57`; `avvio.py:266-282`, `:435-448`), poi fermo fino alla
    mezzanotte UTC».
  - In «Storia degli invarianti»: «26 nov, trader AI versione 8 (non committata, APPROVE con condizioni): **invariante cambiato**,
    l'obiettivo del giorno si conta dopo le spese di chiusura dell'operazione aperta; tetto, leva e fermo invariati; limiti fissi
    invariati».

### Riesame

Revisore: live-path-reviewer, 26 novembre 2026, sera. Oggetto: le stesse modifiche non committate su `11ad4c2` (branch
`claude/brave-albattani-1b12fv`), dopo le correzioni della sessione per 203-206 e la sua scelta sul 204. La differenza l'ho rifatta io,
dalla copia approvata qui sopra (`revisione_obiettivo/copia`, impronte uguali a quelle della sedicesima) ai file di adesso: le righe
cambiate sono le stesse della differenza data dalla sessione (`mut_v8/dalla_sedicesima.diff`). Prove mie nella cartella
`/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/riesame16/` (sotto: «la cartella»):
i file in cima alla cartella elencati sotto, e la mia sottocartella `revisore_live_path/` con le prove finali e una copia pulita del
codice della sedicesima (`vecchio16/`). Nessuna richiesta a Binance: il mercato è quello finto dei test. I dati veri di
`trader_ai/avanti/` solo letti: il trader è fermo a mano dalle 07:11 UTC del 26, senza operazioni aperte, e il 3% non è mai stato
raggiunto (nessun evento «obiettivo del giorno raggiunto» nel diario).

#### Riepilogo e verdetto del riesame

**APPROVE con condizioni.** Nessun Bloccante, nessun Alto, nessun Medio. 203, 204, 205 e 206 sono chiusi. Cinque problemi nuovi, tutti
Bassi (207-211); il 207 c'era già nel codice della sedicesima.

1. **Il fermo solo con il 3% incassato.** Dopo la chiusura per l'obiettivo il programma rilegge il conto. Il fermo fino a mezzanotte e
   l'ora dell'obiettivo si scrivono solo se il guadagno arriva al 3% al centesimo (`avvio.py:283-291`). Il resoconto dice «raggiunto»
   solo con quell'ora (`avvio.py:1025`).
2. **Sotto il 3% si continua.** Evento, niente fermo, conto ricalcolato senza posizione, modello chiamato subito con il perché nel
   motivo, e la sua decisione eseguita nello stesso passo (`avvio.py:292-313`). Provato con il conto simulato vero:
   - tetto finito: nessuna chiamata, niente aperto, a mezzanotte «non raggiunto» e «Tetto di spesa finito alle 10:05 UTC»;
   - conto esaurito: fermo per conto esaurito, nessuna chiamata;
   - richiamo in sospeso: vale il motivo della chiusura;
   - ordine limite annullato: fermo se il conto resta al 3%, se no chiamata;
   - l'operazione nuova aperta nello stesso passo ha il suo stop sul conto e un nome d'ordine nuovo.
3. **I test prendono gli errori.** Le 31 mutazioni della sessione, rifatte sulla mia copia: 31 prese. Delle mie 20, 13 prese dai test
   del repository; le 7 vive sono su rami rari e le prendono tutte le mie prove (210, 211).
4. **Nessuna regressione.** 158 test del trader passano; 16 scenari senza posizione e con un limite in attesa danno gli stessi
   risultati del codice della sedicesima; la suite della radice è come alla sedicesima.

**Problemi nuovi**
- **207, Basso, c'era già.** Un ordine limite che si esegue mentre il programma lo annulla per l'obiettivo resta una posizione senza
  stop, e il trader si ferma senza toccarla. Caso molto raro.
- **208, Basso.** Nel ramo «sotto il 3%» lo stato si salva solo dopo la chiamata al modello. Un errore nel mezzo fa perdere come si è
  chiusa l'operazione e il perché.
- **209, Basso.** In due casi rari il motivo della chiamata dice una cosa non vera; il commento in testa ad `avvio.py` è rimasto vecchio.
- **210, Basso.** Il centesimo vale solo dopo una chiusura del programma, e nessun test prova la fascia fra 29,995 e 30.
- **211, Basso.** Mancano i test del limite annullato per l'obiettivo, del conto esaurito e del tetto finito dopo una chiusura sotto il
  3%.

**Condizioni**
1. Il riavvio si fa solo con l'ok di Alessio. Con lo stesso ok conferma la scelta del 204 fatta dalla sessione (vedi «Decisioni»). Il
   trader è fermo a mano: serve anche «riparti».
2. Al commit il codice deve avere le impronte qui sotto. Se cambiano solo i test (211 e la parte di test del 210, consigliati prima del
   commit), basta che le impronte del codice restino queste. Se cambia il codice (207, 208, 209, la regola del 210), serve un riesame.
3. Prima di qualunque conto demo per il trader: 207 e 208 corretti (sul demo la stessa radice del 207 è il 198).

#### Oggetto del riesame

* File cambiati dalla sedicesima:
  - `avvio.py`: importazione di `guadagno_netto` (`:44-45`); ramo dell'obiettivo (`:268-298`); lezioni con il guadagno dopo le spese
    (`:383`);
  - `giro.py`: campo `guadagno_netto` nella riga del diario (`:64`);
  - `ripara.py`: lezioni ricostruite con `guadagno_netto` quando la riga lo ha (`:175`);
  - `README.md` (`:32-33`, `:44-47`) e `REGOLE.md` (`:6-9`, `:128-130`, `:172`);
  - test: `tests/test_obiettivo_netto.py` nuovo (6 funzioni, 8 casi), `tests/test_controllo_26.py:663` (0,9999 per il lungo),
    `tests/test_trader_ai.py:282-300` (paragrafi interi).
* Uguali alla sedicesima (impronte): `limiti.py`, `messaggio.py`, `istruzioni.md`, `conto_simulato.py`, `operazioni.py`, `costi.py`,
  `conto_demo.py`, `sveglia.py`, `config.json`. Nessun file fuori da `trader_ai/`: `git diff HEAD --stat -- bot/ firebase/ ops/ .claude/`
  è vuoto.
* Nessun test tolto: i nomi raccolti sono i 150 della sedicesima più gli 8 casi nuovi (`revisore_live_path/raccolti_*.txt`).
* Invariante coinvolto: l'obiettivo del giorno e il fermo fino a mezzanotte (sezione 15 della mappa).
* File miei in cima alla cartella: `diff_codice.diff`, `diff_test.diff`, `mutazioni_riesame.py`, `mutazioni_1.txt`, `mutazioni_2.txt`,
  `copia/`, `suite_radice.txt`, e le prime versioni di `test_prove_riesame.py`, `vive_contro_prove.py`, `differenziale.py`,
  `diff_*.json` e `raccolti_*.txt` (rifatte in `revisore_live_path/`). Le altre cartelle (`mut/`, `prove/`,
  `verifica_casi-limite_207/`) e `blocco.lock` sono di un altro processo che lavora qui nello stesso momento. **Attenzione**: alle
  21:53 UTC ho copiato il codice della sedicesima in `vecchio/`, che quel processo aveva creato alle 21:44:59. I file con lo stesso
  nome sono stati sovrascritti con quelli della sedicesima (`avvio.py` 62129355, test della sedicesima); è rimasto il suo
  `tests/test_obiettivo_netto.py`. Chi usa `vecchio/` ricontrolli le impronte. Le mie prove finali usano solo la mia copia pulita
  (`revisore_live_path/vecchio16/`).

#### Stato di 203-206

| Problema | Esito | Dove | Prova |
|---|---|---|---|
| 203 Medio | **chiuso** | `tests/test_obiettivo_netto.py:92-282`, `tests/test_controllo_26.py:663` | Le mutazioni vive della sedicesima (M2, M9, M12, M16, M17; M19 adesso sul campo `guadagno_previsto`) sono prese. I test nuovi usano il conto simulato vero e controllano: il guadagno incassato almeno 30; la chiamata nella fascia, con il conto che arriva a `giro.decidi` (spia); le spese a zero con il limite in attesa. |
| 204 Basso | **chiuso** | `avvio.py:283-313`, `:1025` | Test della sessione: prezzo che scende di 10 dollari durante la chiusura (0,11 BTC), incassati 28,96 contro 30,05 previsti, niente fermo, chiamata, apertura nuova eseguita, poi fermo al 3% vero; stop scattato nel minuto della chiusura, «non raggiunto». Mie A1-A5 e F1. Il quarto punto della correzione suggerita (conto e prezzo da una lettura sola) non è fatto: con la verifica dopo la chiusura non decide più il fermo, sposta solo di poco il momento della chiusura. |
| 205 Basso | **chiuso** | `tests/test_trader_ai.py:282-300` | I due paragrafi confrontati per intero; M14, M15, M16, M17 prese. |
| 206 Basso | **chiuso** | `giro.py:64`, `avvio.py:383`, `ripara.py:175`, `README.md:32-33` | M24, M25, M26 prese, e le mie R16 (spese tolte due volte) e R19 (campo tolto). |

#### Checklist A–F (riesame)

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py` invariato (841f04e6; `git diff HEAD` vuoto su `bot/`, `firebase/`, `ops/`, `.claude/`). **OK**
* Limiti nel codice, non in configurazione: il 3% a `limiti.py:15`, la leva fino a 10 a `limiti.py:16`, il tetto di 5 dollari a
  `costi.py:22`, con le impronte della sedicesima; `config.json` invariato. **OK**
* Parametri dalla dashboard: **NON APPLICABILE** (il trader non legge Firebase).
* Limiti di G1 sul demo: **NON APPLICABILE**.
* Pulsante che chiude tutto: il comando «chiudi» (`avvio.py:958-991`) e il file del fermo (letto a `:175`, `:729`, `:793`, `:808`) non
  sono toccati e vanno senza Firebase. **OK**

**B. Ordini**
* Passi, minimi, leva e margine non toccati (`avvio.py:759-797`). **NON APPLICABILE**
* Identificativo dell'ordine: la chiusura usa `_cid(ora, "x")` (`avvio.py:270`); l'operazione che il modello apre nello stesso passo usa
  «o» per l'apertura e «s» per lo stop, nomi diversi da quello della chiusura (prova F1). **OK**
* Solo riduzione: il conto simulato chiude la sua posizione (`conto_simulato.py:433-444`); il demo è spento. **NON APPLICABILE**
* Prezzo che attiva gli stop: il mark, invariato. **OK**
* Stop per ogni posizione: l'operazione nuova aperta subito dopo la chiusura sotto il 3% ha il suo stop sul conto (F1). **OK**; ma il
  limite eseguito durante la chiusura per l'obiettivo resta senza stop: **PROBLEMA 207** (c'era già).

**C. Stato e resilienza**
* Conto, posizioni e ordini letti dal conto a ogni passo (`avvio.py:181-211`). Dopo la chiusura per l'obiettivo si rilegge il conto
  (`:283`), non la posizione (207). **OK, con il 207**
* Flussi in tempo reale: **NON APPLICABILE**.
* Candele chiuse: non toccate. **OK**
* Errori: lo stato del ramo sotto il 3% si salva solo dopo la chiamata, **PROBLEMA 208**. Un errore del passo resta scritto e riprovato
  dal servizio (`avvio.py:1127-1133`), come prima.
* Firebase e orologio: **NON APPLICABILE**.

**D. Separazione fra simulato, demo e conto vero**
* Il trader gira sul conto simulato (`config.json`, `avvio.py:1096-1098`), con sole letture pubbliche e il controllo dell'indirizzo
  (`conto_simulato.py:62-78`). La modifica aggiunge una lettura del saldo dopo la chiusura, nessun tipo di richiesta nuovo. **OK**

**E. Segreti**
* Differenza letta tutta: nessuna chiave, nessun percorso di file segreti, nessun log nuovo con dati riservati. **OK**
* Chiavi e permessi del demo: **NON APPLICABILE** (demo spento).

**F. Test** (comandi ed esiti; tutto nella cartella)
* `TRADER_AI_BLOCCO=<cartella>/x.lock python -m pytest trader_ai/tests -q -p no:cacheprovider`: **158 passed** in 10,3 s; `git status`
  uguale a prima.
* `mutazioni_riesame.py` (esiti in `mutazioni_1.txt` e `mutazioni_2.txt`): base 157 passed più 1 tolto (quello che chiede git).
  - **Sessione: 31 prese su 31.** La lista è identica a `mut_v8/mutazioni_v8.py` (controllato).
  - **Mie: 13 prese su 20.** Vive: R1 (verifica senza arrotondare), R5 (posizione non azzerata), R6 (lo stato tiene il limite annullato),
    R7 (il modo del limite perso), R8 (fermo sempre con il limite), R15 (il richiamo vince sulla chiusura), R17 (conto esaurito non
    controllato dopo la chiusura).
* `revisore_live_path/prove/test_prove_riesame.py` (14 prove; il file controlla quale `avvio.py` importa):
  - sul codice di adesso (5ae0701f): **14 passate**;
  - sulla copia pulita della sedicesima (62129355): 8 falliscono, cioè quelle che descrivono il comportamento nuovo, e 6 passano, fra
    cui B2: il buco del 207 c'era già.
* `revisore_live_path/vive_contro_prove.py`: le 7 mutazioni vive, contro le mie prove: **7 prese**.
* `revisore_live_path/prove/differenziale.py` (quello della sedicesima): 16 scenari, **0 differenze** fra il codice della sedicesima e
  quello di adesso.
* `python3 -m pytest tests/ -q -p no:cacheprovider`: **2825 passed, 1 failed, 1 skipped** in 165,5 s (`suite_radice.txt`). Il fallito è lo
  stesso della sedicesima (`tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore`, ricerca). I test dei limiti fissi
  passano.

#### Problemi nuovi

**207 — Basso, c'era già — `trader_ai/avvio.py:268-275` con `trader_ai/conto_simulato.py:433-444`.** Nel 198 della quindicesima era
indicato come «letto e non provato»: adesso è provato sul conto simulato.
* **Che cosa succede.**
  - Con un ordine limite in attesa, il ramo dell'obiettivo chiama `chiudi(None)`. Il conto simulato conta prima i minuti chiusi: se nel
    minuto appena chiuso il prezzo è passato oltre il limite, il limite si esegue.
  - Poi `chiudi` toglie tutti gli ordini, stop compreso, e non chiude la posizione, perché il programma gli ha detto «nessuna posizione».
    Lo stato del trader scrive «limite annullato».
  - Dal passo dopo il trader vede una posizione che non conosce e si ferma senza toccarla. La posizione resta aperta senza stop finché
    qualcuno non interviene.
* **Quando.** Molto raro. Serve un limite in attesa con il conto già sopra il 3%: senza posizione il conto si muove solo con un funding
  arrivato in ritardo per un'operazione già chiusa. In più il minuto deve chiudersi nei pochi secondi fra le letture del passo e la
  chiusura. Quando annulla il modello, questa corsa è già gestita: `_annulla_limite` (`avvio.py:877-910`) rilegge e chiude a mercato.
* **Prova** (eseguita, `test_B1...` e `test_B2...`).
  - Limite lungo a 89.500 con stop a 88.500. Portafoglio portato a 1.030,50, al posto del funding in ritardo. Minuto 10:20 con minimo
    89.400.
  - Dopo il passo delle 10:21:00,5: posizione aperta sul conto, nessun ordine condizionato, `aperta` vuota nello stato.
  - Se il minuto chiude a 89.990: fermo fino a mezzanotte. Se chiude a 89.400: adesso il modello si chiama e crede di non avere niente.
  - Al passo dopo: «FERMO: il conto non è solo del trader, non tocco niente», con «una posizione che il trader non ha aperto», e ancora
    nessuno stop.
  - B2 passa uguale sulla copia della sedicesima.
* **Correzione** (sessione principale). Nel ramo dell'obiettivo, per il limite in attesa, usare `_annulla_limite`; oppure, dopo `chiudi`,
  rileggere la posizione e, se c'è, chiuderla con `_chiudi_ora`. Poi rileggere il conto come adesso. Test: B1.

**208 — Basso — `trader_ai/avvio.py:292-313` con `:315-366`.** Stessa radice del 200 (quindicesima, secondo riesame), su una strada
nuova.
* **Che cosa succede.**
  - Nel ramo «sotto il 3%» la chiusura è registrata solo nella memoria del processo e nel diario. Lo stato si salva alla fine di
    `_decidi_ed_esegui` (`:366`). In mezzo ci sono letture di rete (candele, interesse aperto) e la chiamata al modello, fino a 5 minuti.
  - Se il passo si interrompe lì (una pausa di Binance per troppe richieste, la rete giù, un riavvio del servizio), lo stato salvato crede
    l'operazione ancora aperta.
  - Al passo dopo la registra di nuovo dal conto, come «chiusa a mercato» invece di «obiettivo del giorno (chiusa dal programma)». Il
    modello si chiama con «operazione chiusa (chiusa a mercato)», senza sapere che l'ha chiusa il programma e che il 3% non è arrivato.
    Nel diario la stessa operazione risulta chiusa due volte.
  - Prima della versione 8 il ramo dell'obiettivo salvava subito, senza altre letture prima.
* **Prova** (eseguita, `test_C1...`). Candele in errore («429: pausa») dopo la chiusura sotto il 3%:
  - sul disco `aperta` resta piena, mentre il conto non ha più la posizione;
  - 30 secondi dopo: un'operazione sola in memoria, con il modo «chiusa a mercato»; motivo «operazione chiusa (chiusa a mercato)»; due
    «operazione chiusa» nel diario.
* **Correzione.** Salvare lo stato subito dopo la registrazione della chiusura nel ramo dell'obiettivo, prima di rileggere il saldo. Tenere
  il motivo «sotto il 3%» nello stato finché il modello non è stato chiamato (per esempio come richiamo, tolto dopo la chiamata). È
  anche la correzione del 200. Test: C1 girato.

**209 — Basso — `trader_ai/avvio.py:295-296` e `:9`.**
* **Che cosa succede.**
  - L'operazione si è già chiusa da sola sul conto nello stesso passo (il suo obiettivo, o lo stop spostato in guadagno). Poi il conto
    scende sotto il 3% mentre il programma «chiude tutto», e non c'è niente da chiudere. Il motivo dice «chiusa dal programma», e il
    modo vero già trovato dal passo (per esempio «obiettivo») si perde.
  - Con il limite annullato, il motivo comincia con «operazione chiusa (ordine limite annullato ...)», ma nessuna operazione c'è stata.
  - Il commento in testa ad `avvio.py` (riga 9) dice ancora «a +3% [...] chiude tutto e si ferma fino alla mezzanotte dopo».
* **Prova** (eseguita).
  - `test_D1...`: operazione chiusa dal suo obiettivo a +30,50, conto a +29,95 dopo la «chiusura». La scheda dice «obiettivo», il motivo
    «operazione chiusa (chiusa dal programma; dopo la chiusura il guadagno ...)».
  - `test_A5...`: motivo «operazione chiusa (ordine limite annullato dal programma per l'obiettivo del giorno; ...)», nessuna operazione
    in memoria.
* **Correzione.** Nel motivo usare il modo già trovato (`come or chiusa or "chiusa dal programma"`). Per il limite, un motivo che non
  cominci con «operazione chiusa», come il richiamo «ordine limite annullato da te (nessuna operazione)» (`avvio.py:845`). Aggiornare il
  commento della riga 9.

**210 — Basso — `trader_ai/avvio.py:285` con `trader_ai/limiti.py:56-57`; test `tests/test_obiettivo_netto.py:207-227`.**
* **Che cosa succede.** Il «3% al centesimo» vale solo dopo una chiusura del programma. Il controllo di prima, `obiettivo_raggiunto`,
  confronta senza arrotondare. Così lo stesso guadagno, per esempio +29,998, dà due esiti:
  - se l'operazione l'ha chiusa il programma, fermo;
  - se si è chiusa da sola sul conto, nessun fermo: il modello legge «mancano 0.00» e deve continuare.
  In più nessun test del repository prova un guadagno fra 29,995 e 30: senza l'arrotondamento i 158 test passano tutti.
* **Prova** (eseguita).
  - `test_E1...`: chiusura del programma con incassati circa 29,998: fermo.
  - `test_E2...`: gli stessi 29,998 dopo la chiusura sul conto: nessun fermo, chiamata con «mancano 0.00».
  - Mutazione R1 (`incassato >= obiettivo_usdt(conto)`, senza arrotondare): viva con i test del repository, presa da E1.
* **Correzione.** Una regola sola in `limiti.py`, usata prima e dopo la chiusura: la sessione ha scelto il centesimo, quindi al centesimo
  anche in `obiettivo_raggiunto`. Aggiungere E1 ed E2 ai test.

**211 — Basso — `trader_ai/tests/` (codice coinvolto: `avvio.py:272-275`, `:297-304`).**
* **Che cosa manca.** Nessun test del repository passa da:
  - il ramo dell'obiettivo con un limite in attesa, né con il fermo né sotto il 3% (vive R6, R7, R8);
  - il conto esaurito dopo una chiusura sotto il 3% (vive R5, R17);
  - il tetto finito dopo una chiusura sotto il 3% (nessuna mutazione, ma nessun test);
  - un richiamo in sospeso insieme alla chiusura (viva R15; oggi le due cose non capitano insieme).
* **Prova** (eseguita). `mutazioni_2.txt` e `revisore_live_path/vive_contro_prove.txt`: le 6 mutazioni vive qui sopra sono prese dalle
  prove A2, A3, A4 e A5 (la R1 è del 210).
* **Correzione.** Portare nei test del repository A1, A2, A4 e A5 (A3 se si vuole), da `revisore_live_path/prove/test_prove_riesame.py`.

#### Invarianti modificati (dalla sedicesima)

* **Il fermo dell'obiettivo cambia.**
  - Prima: dopo la chiusura per l'obiettivo, sempre fermo fino a mezzanotte, e «raggiunto» nel resoconto.
  - Adesso: fermo e «raggiunto» solo se il guadagno letto sul conto dopo la chiusura arriva al 3% del conto della mezzanotte, al
    centesimo (`avvio.py:283-291`).
  - Se no: evento «chiuso per l'obiettivo del giorno, ma dopo la chiusura il guadagno è sotto il 3%: si continua», niente fermo, e il
    modello si chiama subito con il perché (`avvio.py:292-313`), salvo tetto finito o conto esaurito.
  - Il momento della chiusura non cambia: quando il guadagno dopo le spese di chiusura arriva al 3% (sedicesima).
* **Evento dell'obiettivo.** `conto` e `guadagno` adesso sono quelli dopo la chiusura; `guadagno_previsto` è la stima di prima della
  chiusura; il campo `guadagno_netto` della sedicesima non c'è più. Nessun altro file del repository lo legge (ricerca).
* **Diario e lezioni.** La riga di ogni chiamata ha `guadagno_netto` (dopo le spese di chiusura); `giorno_netto` delle lezioni adesso è
  dopo le spese.
* **Invariati:** il tetto di 5 dollari, la leva fino a 10, il 3%, le istruzioni, il messaggio, il conto simulato,
  `bot/risk/hard_limits.py`.

#### Decisioni per Alessio

* Il riavvio con la versione 8 sul conto simulato, e il «riparti»: sono suoi.
* La scelta del 204 l'ha fatta la sessione, dalla sua frase del 26 novembre («non si deve fermare finché non ha raggiunto il 3% di
  profitto, è obbligatorio»). Con l'ok al riavvio la conferma, o ne sceglie un'altra.
  - Quando capita, il programma ha già chiuso l'operazione: per gli ultimi centesimi il modello deve aprirne un'altra e pagare di nuovo
    entrata e uscita (con 0,11 BTC circa 12 USDT fra andata e ritorno; con l'ordine minimo da 100 USDT circa 0,12).
  - Sul simulato capita solo se il prezzo si muove nell'attimo fra il controllo e la chiusura (con 0,11 BTC, 1 dollaro di BTC vale circa
    0,11 USDT), o se uno stop scatta in quel minuto.
  - Altre strade possibili, se le vuole: chiudere solo con un piccolo margine sopra il 3%, oppure accettare un poco meno del 3%.
* Prima di un conto demo per il trader: misurare quante volte il guadagno incassato resta sotto la stima. Su un conto vero l'uscita non
  avviene al prezzo mark, e il caso potrebbe essere frequente.

#### Domande aperte

* La memoria del revisore (`reviews/`) da quest'area non si scrive: le righe sono qui sotto, per la sessione delle crypto. Chi le
  applica? Restano da applicare anche quelle della sedicesima (sopra) e quelle di `trader_ai/revisioni/righe_per_reviews.patch`.
* Nella cartella `riesame16/` lavora nello stesso momento un altro processo, con una cartella `verifica_casi-limite_207/`. Se anche lui
  numera i problemi da 207, chi riallinea i numeri? E chi usa `riesame16/vecchio/` sa che alle 21:53 UTC i suoi file con lo stesso nome
  sono stati sovrascritti dalla mia copia della sedicesima (vedi «Oggetto»)?
* `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore` fallisce ancora, come alla sedicesima. È fuori dal percorso
  degli ordini: lo guarda la sessione della ricerca?

#### Impronte md5 (primi 8 caratteri) dei file approvati

* Codice cambiato dalla sedicesima: `trader_ai/avvio.py` 5ae0701f, `trader_ai/giro.py` 32156f63, `trader_ai/ripara.py` 392908eb,
  `trader_ai/README.md` 69e3bfe7, `trader_ai/REGOLE.md` 02d3992c.
* Uguali alla sedicesima: `limiti.py` a3e811bb, `messaggio.py` b6923e17, `istruzioni.md` cc36e981, `conto_simulato.py` c7f7e815,
  `operazioni.py` 3120d09a, `costi.py` 2b1e9f30, `conto_demo.py` 453e0288, `sveglia.py` 6fd9d573, `config.json` 6ad5da2d.
* Test: `tests/test_obiettivo_netto.py` 24f039ce, `tests/test_controllo_26.py` 5808b10c, `tests/test_trader_ai.py` 73aa19e2.
* `bot/risk/hard_limits.py` 841f04e6, invariato.
* Impronte rilette alla fine del riesame: uguali.

#### Righe per `reviews/` (da applicare dalla sessione delle crypto)

* `reviews/REVIEW_LOG.md`, riga nuova in fondo:
  `| 2026-11-26 | claude/brave-albattani-1b12fv | non committato su 11ad4c2 (md5 avvio.py 5ae0701f, giro.py 32156f63, ripara.py 392908eb, limiti.py a3e811bb) | trader AI versione 8, riesame della sedicesima: fermo solo se dopo la chiusura il guadagno incassato arriva al 3% al centesimo, se no si continua | APPROVE con condizioni (203-206 chiusi; Bassi 207-211) | aperta: riavvio con l'ok di Alessio; 207 e 208 prima di un demo | trader_ai/revisioni/2026-11-26-sedicesima.md (### Riesame) |`
* `reviews/INDEX.md`:
  - riga «Numeri dei problemi»: «trader AI fino al 211 (`trader_ai/revisioni/2026-11-26-sedicesima.md`, riesame): i nuovi partono da
    212»;
  - nella riga «Trader AI» aggiungere: «riesame della sedicesima (fermo solo con il 3% incassato): APPROVE con condizioni (207-211
    Bassi; 207 posizione senza stop in un caso molto raro, c'era già)».
* `reviews/LIVE_PATH_MAP.md`:
  - sezione 15, riga dell'obiettivo: «obiettivo del 3% del conto della mezzanotte UTC, contato dopo le spese di chiusura
    dell'operazione aperta (`limiti.py:15`, `:51-57`; `avvio.py:267-279`, `:451-464`); fermo fino alla mezzanotte UTC solo se il guadagno
    letto sul conto dopo la chiusura arriva al 3% al centesimo (`avvio.py:283-291`), se no evento e il modello si chiama subito
    (`:292-313`)»;
  - in «Storia degli invarianti»: «26 nov, trader AI versione 8, riesame (non committato, APPROVE con condizioni): **invariante
    cambiato**, fermo e "raggiunto" solo con il 3% incassato dopo la chiusura, al centesimo; se no si continua. Tetto, leva e limiti
    fissi invariati».
