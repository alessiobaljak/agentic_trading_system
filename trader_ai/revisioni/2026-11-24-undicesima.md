# Undicesima revisione del trader AI — correzione del problema 167

Revisore: live-path-reviewer, 24 novembre 2026. Controllo limitato al diff della correzione del 167 (decima revisione,
`trader_ai/revisioni/2026-11-24-decima.md`), come chiesto dalla condizione 1 della decima.

### Riepilogo e verdetto

**REQUEST CHANGES** (nessun problema Bloccante né Alto; un Medio, il **170**, e due Bassi, 171 e 172).

Il **167 è chiuso** per il caso che descriveva: lo stop spostato o rimesso a metà minuto ora protegge la posizione in quel minuto
(prove D1, D3, D4 rifatte: tutte e tre danno il risultato giusto, D1 esce a 89.700 meno lo scarto, D4 a 89.100 meno lo scarto).
Resta però lo stesso difetto quando il cambio dello stop avviene nei primi secondi di un minuto e il minuto appena chiuso non è
ancora stato contato (170): lo stop vecchio, attivo per tutto quel minuto, non conta, e lo stop nuovo conta anche prima di nascere.
Inoltre la parte della correzione che conta di più (la lista degli stop tolti, che vale quando lo stop si **allarga**) non è
protetta da nessun test del repository (171): togliendola, tutti i test passano.

Correzione piccola, tutta in `conto_simulato.py`; poi un controllo limitato al diff.

### Oggetto

* Branch `claude/brave-albattani-1b12fv`, commit `19c3b91` (padre `a23d73b`).
* File toccati: `trader_ai/conto_simulato.py` (`_candela` righe 204-212, `annulla_condizionato` righe 366-372),
  `trader_ai/tests/test_simulato.py` (test rinominato riga 292, tre test nuovi righe 321, 340, 354), `trader_ai/REGOLE.md:17-20`.
* Invarianti coinvolti: «ogni posizione ha uno stop» nel conto simulato (la simulazione deve contare lo stop come lo conterebbe
  Binance, sempre dal lato peggiore per noi). Nessun invariante del bot, nessun limite fisso.

### Checklist A–F

**A. Limiti fissi e interruttori**
* `bot/risk/hard_limits.py` e limiti del trader (`trader_ai/limiti.py`): non toccati dal diff (`git show 19c3b91 --stat`). OK.
* Parametri da dashboard, regole di Firebase, limiti di G1 sul demo, pulsante che chiude tutto: NON APPLICABILE (diff solo nel
  conto simulato del trader).

**B. Ordini**
* Passi, identificativi, «solo riduzione», leva e margine: NON APPLICABILE (nessun ordine verso Binance nel diff; il conto simulato
  non manda ordini).
* Tipo di prezzo degli stop: invariato, prezzo mark (`conto_simulato.py:215`, `:224`). OK.
* Stop per ogni posizione (simulato): **PROBLEMA 170** (sotto). Il caso a metà minuto è corretto: `conto_simulato.py:208-210`
  prende tutti gli stop in `algo` e quelli tolti nel minuto stesso, e fra questi il più vicino al prezzo; `:368-372` registra
  l'ora in cui lo stop è tolto. Prove D1, D3, D4 e U3 corrette.
* Obiettivo: invariato rispetto alla nona e decima (dal minuto dopo, `:211-212`; escluso nel minuto del limite, `:213-214`). OK.

**C. Stato e resilienza**
* Lo stato `tolti` è salvato nello stesso file sotto blocco (`:366-372` dentro `_stato()`); un file vecchio senza la chiave
  funziona (`self.s.get("tolti", [])`, `:209`, `:371`). OK.
* La lista si svuota solo a un annullamento successivo, con una finestra di 2 minuti di orologio (`:371`), non quando il minuto
  è stato contato né quando la posizione si chiude: **Basso 172**.
* Ora di nascita e di annullamento dall'orologio della macchina (`:363`, `:370`): stessa radice del 168 (aperto). Nessun peggioramento.

**D. Separazione fra paper, demo e conto vero**
* NON APPLICABILE al diff (nessun cambio di client, chiavi o indirizzi).

**E. Segreti e sicurezza**
* Nessuna chiave, nessun log nuovo nel diff. OK.

**F. Test**
* Comando: `TRADER_AI_BLOCCO=/tmp/x.lock python -m pytest trader_ai/tests -q` → **87 passed in 9,49 s** (84 della decima + 3 nuovi).
* Test nuovi: `test_simulato.py:321` (stop spostato a metà minuto, più stretto), `:340` (stop rimesso a metà minuto), `:354`
  (stop spostato nel minuto del limite eseguito). Il test di riga 292 rinominato «obiettivo messo a metà minuto»: **169 chiuso**.
* Prove a mutazione (copie fuori dal repository):
  * togliendo il limite inferiore della nascita dello stop, cioè rimettendo «dal minuto dopo», falliscono i tre test nuovi: la parte
    «lo stop conta nel minuto in cui nasce» è protetta;
  * togliendo del tutto la lista `tolti` (`:209` sostituita da `[]`) **passano tutti i 24 test** di `test_simulato.py`: la parte «lo
    stop tolto vale fino alla fine del suo minuto» non è protetta (171). Nei tre test nuovi lo stop nuovo è sempre più stretto del
    vecchio, quindi il vecchio non serve mai.
* Prove del revisore: `/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/undicesima/test_prove_undicesima.py`,
  lanciate con `TRADER_AI_BLOCCO=/tmp/x.lock PYTHONPATH=<radice> python -m pytest <file> -q -s`: 6 passati.
  * D1 (stop spostato a metà minuto da 89.500 a 89.700, minimo 89.400): chiusa allo stop a 89.691,03 (89.700 meno lo scarto). Corretto.
  * D3 (stop nel minuto del limite eseguito): chiusa allo stop. Corretto.
  * D4 (stop spostato nel minuto del limite eseguito, da 89.000 a 89.100, minimo 88.800): chiusa a 89.091,09. Corretto.
  * U3 (stop **allargato** a metà minuto da 89.500 a 89.000, minimo 89.400): chiusa a 89.500 meno lo scarto. Corretto sul codice;
    sulla copia senza `tolti` fallisce. È il test che manca nel repository (171).
  * U1 e U2 affermano il problema 170 (sotto).

### Problemi

#### 170 Medio — al confine del minuto lo stop vecchio non conta e quello nuovo conta prima di nascere
* Dove: `conto_simulato.py:208` (gli stop in `algo` contano per **ogni** minuto non ancora contato, anche precedente alla loro
  nascita), `:209` (uno stop tolto conta solo nel minuto in cui è tolto), `:352-364` e `:366-372` (`condizionato` e
  `annulla_condizionato` non contano prima i minuti già chiusi, a differenza di `apri`, `:336`, e `chiudi`, `:382`),
  `:158-164` (`aggiorna()` non riconta se l'ultima volta è di meno di 5 secondi prima), `avvio.py:319` e `:427-446` (in
  `_esegui` si legge la posizione, poi filtri e prezzo, poi `_sostituisci`).
* Scenario concreto: `_esegui` legge la posizione al secondo 59,5 del minuto M (i minuti fino a M esclusa sono contati), poi
  legge filtri e prezzo e sposta lo stop al secondo 0,5 del minuto dopo. Il minuto M non è ancora stato contato quando lo stop
  cambia. Al conteggio successivo:
  * se lo stop si **allarga** (da 89.500 a 89.000) e nel minuto M il prezzo mark è sceso a 89.400, sul conto vero lo stop a 89.500
    era attivo per tutto M e sarebbe scattato; nel simulato M si conta solo con lo stop nuovo a 89.000 e la posizione resta (prova
    U1). Numeri migliori del vero: il difetto del 167, spostato al confine del minuto;
  * se lo stop si **stringe** (da 89.500 a 89.800) e il minimo di M è 89.700, il simulato chiude a 89.800 meno lo scarto per uno
    stop che in M non esisteva (prova U2). Lato prudente, ma numeri sbagliati.
  Frequenza stimata (non misurata): serve un confine di minuto fra la lettura della posizione e il cambio dello stop, qualche decimo
  di secondo su 60, circa 1 cambio su 100; nel caso dell'allargamento conta solo se il prezzo ha toccato lo stop vecchio.
* Correzione suggerita (tutta in `_candela` e `annulla_condizionato`, senza nuove chiamate a Binance che possano fallire durante
  `_sostituisci`): dare a ogni stop il suo intervallo di vita, contato a minuti interi:
  1. uno stop in `algo` conta per i minuti `t >= minuto di messo_ms` (non prima);
  2. uno stop tolto conta per i minuti `minuto di messo_ms <= t <= minuto di tolto_ms` (non solo il minuto dell'annullamento);
  3. la lista `tolti` si svuota quando il minuto del suo annullamento è stato contato (`ultimo_minuto_ms > tolto_ms`) o quando la
     posizione si chiude, non con i 2 minuti di orologio (vedi 172);
  4. due test: U1 (allargato al confine: deve uscire a 89.500) e U2 (stretto al confine: non deve uscire nel minuto M).
  In alternativa, `condizionato` e `annulla_condizionato` possono contare prima i minuti chiusi come fa `apri` (`:336`); ma se le
  candele mancano `_aggiorna` solleva un errore e `_sostituisci` lo prenderebbe per un rifiuto dello stop (fino a chiudere a mercato,
  `avvio.py:447-451` e seguenti): per questo suggerisco la prima strada.

#### 171 Basso — la lista degli stop tolti non ha un test
* `test_simulato.py:321-354`: in tutti e tre i test lo stop nuovo è più stretto del vecchio; la lista `tolti` (`conto_simulato.py:209`,
  `:368-372`) non cambia l'esito di nessun test (mutazione: 24 passati senza). Suggerito: aggiungere U3 (stop allargato a metà
  minuto, il minimo tocca solo il vecchio, uscita al vecchio).

#### 172 Basso — la lista `tolti` non dipende dalla posizione né dal minuto contato
* `conto_simulato.py:209`, `:371`: gli stop tolti non si confrontano con il lato della posizione e non si svuotano alla chiusura
  (`_chiudi_posizione` `:261-273`, `chiudi` `:378-389`, `annulla_tutto` `:374-376`); si tolgono solo dopo 2 minuti di orologio, e solo
  a un annullamento successivo. Oggi non ha effetti: una posizione nuova nello stesso minuto si valuta solo se nasce da un limite, e
  un limite messo nello stesso minuto conta dal minuto dopo; il programma tiene una sola operazione per volta. Con la correzione del
  170 (punto 3) si chiude da solo.

#### Aperti dalle revisioni precedenti
* 168 (orologio della macchina), 164, 166, 159, 160, 161 e 162 in parte; Medi 100, 117; Bassi 113, 114, 121, 122, 123, 125, 129, 130,
  137, 138, 139, 141, 142, 144, 145, 146, 147, 148, 150, 151. **167 chiuso, 169 chiuso.**

### Invarianti modificati

Nessun invariante del bot né limite fisso. Del trader: «stop per ogni posizione» nel simulato **ripristinato** per lo spostamento a
metà minuto (167 chiuso); resta scoperto il caso del confine del minuto (170). `REGOLE.md:17-20` dice «quando lo stop si sposta la
posizione non resta mai scoperta»: vero solo dopo la correzione del 170.

### Decisioni per Alessio

1. Nessuna nuova sui limiti. La regola «sempre il caso peggiore per noi» nella simulazione resta una scelta tecnica già approvata
   nella nona e nella decima; il 170 la completa.
2. Restano quelle della nona: cancellare dal sito di Binance le chiavi del 24 novembre se non servono; l'ok all'avvio è suo.

**Condizioni definitive prima del primo avvio** (sostituiscono quelle della decima):
1. 170 corretto come sopra con i test U1 e U2, più il test U3 (171), e un controllo del revisore limitato a quel diff.
2. Sulla macchina `bash trader_ai/vps/installa.sh` dalla copia aggiornata, con `config.json` in simulato: lo script non deve fermarsi
   per chiavi di Binance; controllo `grep -c TRADER_AI_DEMO /etc/trader-ai.env` uguale a 0 (senza stampare il file).
3. La riga finale di `controlla`: «conto pulito per il primo avvio: sì», conto 1000.00.
4. Ok esplicito di Alessio all'avvio.
5. Dopo l'avvio: nel diario l'evento «acceso» con `conto: simulato` e il commit installato.

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
   scrivere fuori da `trader_ai/`; undici revisioni del trader mancano dalla memoria del revisore (in `reviews/REVIEW_LOG.md` ci sono
   solo quelle del 23 novembre). (dalla prima revisione)
