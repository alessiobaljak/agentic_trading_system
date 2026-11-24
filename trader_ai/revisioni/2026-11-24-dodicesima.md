# Dodicesima revisione del trader AI — correzione dei problemi 170, 171 e 172

Revisore: live-path-reviewer, 24 novembre 2026. Controllo limitato al diff della correzione dei problemi 170, 171 e 172
dell'undicesima revisione (`trader_ai/revisioni/2026-11-24-undicesima.md`), come chiesto dalla sua condizione 1.

### Riepilogo e verdetto

**APPROVE con condizioni** (nessun problema Bloccante, Alto o Medio; tre Bassi nuovi: 173, 174, 175).

* **170 chiuso.** Al confine del minuto lo stop vecchio conta per tutto il minuto chiuso e lo stop nuovo non conta prima di nascere:
  prove U1 e U2 rifatte, ora danno il risultato giusto (U1 esce a 89.491,05, cioè 89.500 meno lo scarto; in U2 la posizione resta).
* **171 chiuso.** Togliendo la lista degli stop tolti fallisce il test nuovo `test_stop_allargato_a_meta_minuto_il_vecchio_vale_fino_alla_fine`.
* **172 chiuso.** La lista si svuota quando il minuto dell'annullamento è stato contato e alla chiusura della posizione.
* La correzione fa due cose che si coprono a vicenda: (1) ogni stop vale dal minuto in cui nasce al minuto in cui è tolto;
  (2) `condizionato` e `annulla_condizionato` contano prima i minuti chiusi. Le prove a mutazione mostrano che **la (1) da sola basta**
  a dare U1, U2 e U3 giusti. La (2) non aggiunge correttezza ma aggiunge due effetti: un ordine «orfano» possibile (173) e nuove
  richieste di dati che possono fallire dentro le operazioni sullo stop (174). Nessuno dei due è pericoloso oggi (conto simulato,
  casi rari, il programma resta coperto); il consiglio è togliere la (2) al prossimo tocco del file.
* Uno dei tre test nuovi non prova niente (175).

### Oggetto

* Branch `claude/brave-albattani-1b12fv`, commit `69d5ee9` (padre `19c3b91`).
* File toccati: `trader_ai/conto_simulato.py` (`_aggiorna` riga 184, `_candela` righe 209-214, `_chiudi_posizione` riga 277,
  `condizionato` riga 365, `annulla_condizionato` righe 374-378), `trader_ai/tests/test_simulato.py` (righe 370-420: un aiuto e tre test),
  e il rapporto dell'undicesima.
* Invarianti coinvolti: «ogni posizione ha uno stop» nel conto simulato (la simulazione deve contare lo stop come lo conterebbe
  Binance, sempre dal lato peggiore per noi). Nessun invariante del bot, nessun limite fisso.

### Checklist A–F

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py` e `trader_ai/limiti.py`: non toccati (`git show 69d5ee9 --stat`). OK.
* Parametri da dashboard, regole di Firebase, limiti di G1 sul demo, pulsante che chiude tutto: NON APPLICABILE (diff solo nel conto
  simulato del trader).

**B. Ordini**
* Passi, identificativi, «solo riduzione», leva e margine: NON APPLICABILE (il conto simulato non manda ordini a Binance).
* Tipo di prezzo degli stop: invariato, prezzo mark (`conto_simulato.py:220-221`). OK.
* Stop per ogni posizione (simulato): OK per 170 (`conto_simulato.py:210-214`: `vivo` conta lo stop dal minuto di `messo_ms` al minuto
  di `tolto_ms`, compresi; fra gli stop vivi vale il più vicino al prezzo). `vivo` non guarda il lato dello stop: **Basso 173**.
* Obiettivo: invariato (dal minuto dopo, `:216-217`; escluso nel minuto del limite, `:218-219`). OK.

**C. Stato e resilienza**
* `tolti` si svuota quando il suo minuto è contato (`:184`: resta solo se `tolto_ms >= ultimo_minuto_ms`, cioè se il minuto
  dell'annullamento non è ancora contato) e alla chiusura (`:277`). Un file vecchio senza la chiave funziona (`.get("tolti", [])`). OK.
* Un errore dentro `_aggiorna` (`:178` candele mancanti, o una richiesta di dati che fallisce) in `condizionato` o
  `annulla_condizionato` esce dal blocco senza scrivere il file (`_stato`, `:133-150`): lo stato resta quello di prima, lo stop vecchio
  resta al suo posto (prova N1). OK. Effetti sul programma: **Basso 174** (sotto, con l'analisi di `_esegui`, `_sostituisci` e
  `_protezione`).
* Orologio della macchina: ora che il minuto si conta anche nel momento esatto del cambio dello stop (spesso nei primi secondi del
  minuto), una macchina in anticipo su Binance può contare un minuto non ancora finito; è il 168, aperto, nessun peggioramento sostanziale.

**D. Separazione fra paper, demo e conto vero**
* NON APPLICABILE (nessun cambio di client, chiavi o indirizzi).

**E. Segreti e sicurezza**
* Nessuna chiave, nessun log nuovo nel diff. OK.

**F. Test**
* Comando: `TRADER_AI_BLOCCO=/tmp/x.lock python -m pytest trader_ai/tests -q` → **90 passed in 9,41 s** (87 dell'undicesima + 3 nuovi).
* Prove del revisore (fuori dal repository):
  `/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/dodicesima/test_prove_dodicesima.py`,
  lanciate con `TRADER_AI_BLOCCO=/tmp/x.lock PYTHONPATH=<radice> python -m pytest <file> -q -s`: **5 passati**.
  * U1 (stop allargato da 89.500 a 89.000 un secondo dopo l'inizio del minuto, minimo del minuto chiuso 89.400): chiusa allo stop a
    89.491,05 (89.500 meno lo scarto). Corretto.
  * U2 (stop stretto da 89.500 a 89.800 un secondo dopo l'inizio del minuto, minimo del minuto chiuso 89.700): la posizione resta. Corretto.
  * U3 (stop allargato a metà minuto, minimo 89.400): chiusa a 89.491,05. Corretto.
  * N1 (candele mancanti): `condizionato` e `annulla_condizionato` alzano l'errore e il file dello stato non cambia. Corretto.
  * N2 (il minuto contato dentro `condizionato` fa scattare lo stop vecchio): la posizione si chiude e lo stop nuovo resta nella lista
    senza posizione; una posizione corta aperta dopo viene chiusa subito «allo stop» da quello stop di una posizione lunga (173).
* Prove a mutazione (`.../scratchpad/dodicesima/muta.py`, copie fuori dal repository; test di `test_simulato.py` più le prove):
  | mutazione | test del repository | prove del revisore |
  |---|---|---|
  | senza la lista `tolti` | **fallisce** il test dello stop allargato a metà minuto | fallisce U3 |
  | senza il conteggio prima in entrambe le funzioni | tutti passano | U1, U2, U3 passano; falliscono solo N1 e N2 |
  | senza il conteggio prima solo in `condizionato` | tutti passano | come sopra |
  | senza il conteggio prima solo in `annulla_condizionato` | tutti passano | fallisce solo N1 |
  | senza `tolti` e senza il conteggio in `annulla_condizionato` | fallisce lo stesso test | fallisce U3 |
  | senza il limite «dal minuto in cui nasce» | tutti passano | tutti passano (lo copre il conteggio prima) |
  | senza il limite «dal minuto in cui nasce» e senza il conteggio in `condizionato` | **tutti passano** | fallisce U2 |
  | senza svuotare la lista | tutti passano | tutti passano |
  Lettura: la lista `tolti` è protetta (171 chiuso). Il conteggio prima di cambiare lo stop non è protetto da nessun test del repository,
  ma non serve a dare il risultato giusto: lo danno gli intervalli di vita. Il limite «lo stop conta dal minuto in cui nasce» non ha un
  test del repository che lo protegga (175). Lo svuotamento della lista non ha un test, ma senza di esso il risultato non cambia
  (gli intervalli limitano comunque ogni stop tolto al suo minuto): accettabile.

### Problemi

#### 173 Basso — uno stop «orfano» può valere per la posizione dopo, anche dal lato opposto
* Dove: `conto_simulato.py:365-369` (`condizionato` conta i minuti chiusi, che possono chiudere la posizione, e poi aggiunge lo stop
  nuovo comunque), `:210-214` (`vivo` non confronta il lato dello stop con quello della posizione), `avvio.py:171-174` (con l'ordine
  limite «in attesa» non più sul libro il programma azzera l'operazione **senza** `annulla_tutto`, a differenza di `_registra_chiusura`,
  `avvio.py:275`).
* Scenario concreto: ordine limite lungo in attesa con stop a 89.500; nei primi secondi di un minuto il modello sposta lo stop. Dentro
  `condizionato` si conta il minuto appena chiuso: il limite si esegue e lo stop vecchio scatta, la posizione si chiude; poi lo stop
  nuovo si aggiunge senza posizione. Al passo dopo il programma vede il limite sparito e la posizione assente e azzera l'operazione
  senza annullare niente: lo stop resta. Se il modello apre poi una posizione corta, al primo minuto contato quello stop di una posizione
  lunga (sotto il prezzo) la chiude subito «allo stop» (prova N2). Su Binance uno stop di vendita «chiudi tutto» non può chiudere una
  posizione corta. Prima di questo commit il caso non poteva succedere: la posizione si chiudeva solo in `_aggiorna`, che svuota gli
  stop dopo averli contati.
  Effetto: un'uscita finta, dal lato prudente (perdita di commissioni e scarto). Frequenza: molto rara (servono ordine limite in attesa,
  modifica nei primi secondi del minuto, esecuzione e stop nello stesso minuto appena chiuso).
* Correzione suggerita: togliere le due chiamate a `_aggiorna` in `condizionato` e `annulla_condizionato` (righe 365 e 374: gli intervalli
  di vita già danno U1, U2 e U3 giusti, vedi mutazioni); in più, per difesa, in `vivo` e nella scelta dell'obiettivo contare solo gli
  ordini con `a["lato"] == p["lato"]`. Test: N2 (aperto lungo, poi corto, lo stop del lungo non conta).

#### 174 Basso — nuove richieste di dati dentro le operazioni sullo stop
* Dove: `conto_simulato.py:365` e `:374`; `_aggiorna` (`:166-185`) chiede sempre il funding (`_funding`, `:238`, appena c'è una
  posizione o una chiusa fra le ultime 20) e, se un minuto si è chiuso, le candele dei prezzi e del mark.
* Prima: `condizionato` faceva 2 richieste di dati (prezzo mark e interesse aperto) e `annulla_condizionato` nessuna, quindi non poteva
  fallire. Ora `condizionato` ne fa da 3 a 5 e `annulla_condizionato` da 1 a 3, e possono alzare anche «candele da 1 minuto mancanti».
* Cosa succede nel programma (letto in `avvio.py`):
  * `_esegui`, apertura a mercato (`avvio.py:367-374`): `apri` riesce, poi lo stop «rifiutato» per un errore dei dati porta a
    `_chiudi_ora`, che chiama `chiudi` e quindi di nuovo `_aggiorna`. Se l'errore dura, `chiudi` alza a sua volta: l'errore esce
    dall'`except`, il passo scrive «errore di esecuzione» e la posizione simulata resta **senza stop** finché i dati non tornano; al
    ritorno i minuti persi si contano senza stop (può arrivare la liquidazione simulata, o al contrario la posizione sopravvive a un
    calo che lo stop vero avrebbe chiuso). Se l'errore è passeggero, l'operazione si chiude a mercato per un problema dei dati.
    Questo stesso percorso esisteva già con le 2 richieste di prima (e con la pausa dopo un 429 falliscono tutte allo stesso modo):
    il commit lo rende un po' più probabile, non lo crea. Sul conto vero lo stesso percorso si avrebbe con un guasto di rete.
  * `_sostituisci` (`avvio.py:427-471`): se lo stop nuovo fallisce e anche l'annullamento del vecchio fallisce (riga 446, fuori da un
    `try`), l'errore esce e **lo stop vecchio resta**: sicuro (prima l'annullamento non poteva fallire, quindi questo ramo è anzi più
    prudente). Se lo stop nuovo riesce e l'annullamento del vecchio fallisce (righe 440-443), restano due stop fino alla chiusura e il
    programma non riprova ad annullare: con uno stop allargato vale ancora il vecchio, più stretto (prudente).
  * `_protezione` (`avvio.py:284-305`): stop «rifiutato» per i dati → `_chiudi_ora` → `chiudi` può alzare → l'errore esce da
    `_protezione`, il passo scrive «protezione non riuscita» e continua; si riprova al passo dopo. Nessun blocco, nessuna scrittura a metà.
  * `_obiettivo_sul_conto` (`avvio.py:307-314`): un errore dei dati azzera l'obiettivo dell'operazione per sempre (non si riprova).
    Nessun rischio, ma numeri diversi dal conto vero.
* Correzione suggerita: la stessa del 173 (togliere i due `_aggiorna`); torna il comportamento di prima su questi errori, con la
  correttezza data dagli intervalli.

#### 175 Basso — il test dello stop stretto al confine non prova niente
* Dove: `trader_ai/tests/test_simulato.py:395-406` (`test_stop_stretto_nei_primi_secondi_non_conta_nel_minuto_prima`). Il commento
  dice «89.400: sotto lo stop nuovo», ma lo stop nuovo è 89.300: per una posizione lunga 89.400 non tocca né il vecchio (89.000) né il
  nuovo, quindi il test passa anche se lo stop nuovo contasse prima di nascere (mutazione «senza il limite dal minuto in cui nasce e senza
  il conteggio in `condizionato`»: tutti i test del repository passano).
* Correzione suggerita: minimo del minuto a 89.200 (sotto il nuovo 89.300, sopra il vecchio 89.000), oppure stop nuovo a 89.500;
  la posizione deve restare aperta.

#### Aperti dalle revisioni precedenti
* 168 (orologio della macchina), 164, 166, 159, 160, 161 e 162 in parte; Medi 100, 117; Bassi 113, 114, 121, 122, 123, 125, 129, 130,
  137, 138, 139, 141, 142, 144, 145, 146, 147, 148, 150, 151. **170, 171, 172 chiusi.**

### Invarianti modificati

Nessun invariante del bot né limite fisso. Del trader: «stop per ogni posizione» nel simulato **ripristinato** anche al confine del
minuto (170 chiuso). `REGOLE.md:17-20` («quando lo stop si sposta la posizione non resta mai scoperta») ora è vero.

### Decisioni per Alessio

1. Nessuna nuova sui limiti. Restano quelle della nona: cancellare dal sito di Binance le chiavi del 24 novembre se non servono; l'ok
   all'avvio è suo.

**Condizioni definitive prima del primo avvio** (sostituiscono quelle dell'undicesima; la condizione 1 dell'undicesima è soddisfatta):
1. Sulla macchina `bash trader_ai/vps/installa.sh` dalla copia aggiornata (con il commit `69d5ee9` o successivo), con `config.json` in
   simulato: lo script non deve fermarsi per chiavi di Binance; controllo `grep -c TRADER_AI_DEMO /etc/trader-ai.env` uguale a 0 (senza
   stampare il file).
2. La riga finale di `controlla`: «conto pulito per il primo avvio: sì», conto 1000.00.
3. Ok esplicito di Alessio all'avvio.
4. Dopo l'avvio: nel diario l'evento «acceso» con `conto: simulato` e il commit installato.

173, 174 e 175 non bloccano l'avvio (conto simulato, casi rari, il programma resta sempre coperto o si ferma con un errore scritto); si
correggono al prossimo tocco di `conto_simulato.py`, con un controllo del revisore limitato a quel diff.

**Prima di qualunque uso con soldi veri:** invariato (146, 147 e una revisione nuova); il conto simulato non prova il percorso degli
ordini su Binance.

### Domande aperte

1. Il file `/etc/trader-ai.env` sulla macchina contiene oggi le chiavi `TRADER_AI_DEMO_*` inserite il 24 novembre? (157; ora lo script
   lo riscrive, ma la risposta dice se le chiavi vanno cancellate sul sito) (dalla nona)
2. Da quale copia si lancia `installa.sh` sulla macchina, visto che la copia del bot legge il branch di default? Conta perché lo script
   decide «simulato» leggendo `config.json` di quella copia, non di `/opt/trader-ai` (159). (dalla seconda revisione)
3. Chi lancia i comandi sulla macchina (`installa.sh`, avvio), visto che il proprietario lavora dal telefono e il canale `ops/` non ha
   comandi per il trader? (dalla settima, domanda 4)
4. Chi copia questo rapporto e aggiorna registro, indice e mappa in `reviews/`? Il blocco delle aree impedisce a questa sessione di
   scrivere fuori da `trader_ai/`; dodici revisioni del trader mancano dalla memoria del revisore (in `reviews/REVIEW_LOG.md` ci sono
   solo quelle del 23 novembre). (dalla prima revisione)
