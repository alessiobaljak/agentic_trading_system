# Le regole del trader AI (scritte il 21 novembre 2026, prima di ogni calcolo e di ogni chiamata al modello)

Nessun numero di questo trader esiste ancora: queste regole sono scritte prima. Ogni cambio dopo la prima chiamata al modello è una
**versione nuova** (sezione 10), con la data, e non cancella la precedente.

## 1. Cosa fa, in una frase
Ogni 4 ore un modello linguistico di Anthropic riceve un riassunto del mercato e del suo portafoglio e risponde con decisioni
strutturate (apri, chiudi, riduci, sposta lo stop); il codice controlla i limiti fissi, scarta ciò che li supera e simula gli ordini sui
perpetui in USDT di Binance con spese vere. **Nessun ordine vero, su nessun conto** (né il demo di G1, né altri).

## 2. Il modello
* **Quale**: `claude-opus-5-5` (Claude Opus 5.5), il modello predefinito della documentazione di Anthropic; si chiama con l'SDK
  Python ufficiale `anthropic`. Pensiero adattivo (sempre acceso su questo modello), sforzo `medium` scritto esplicitamente.
  Un modello diverso (per esempio `claude-sonnet-5-5`, la metà del prezzo) solo se lo sceglie il proprietario, ed è una versione nuova.
* **Data di addestramento**: «Training data cutoff: Jun 2026», «Reliable knowledge cutoff: Jun 2026» (pagina ufficiale
  https://platform.claude.com/docs/en/about-claude/models/overview, letta il 21 novembre 2026).
* **Prezzo** (stessa pagina): 4 dollari per milione di parole-pezzo («token») in entrata, 20 in uscita; le letture dalla cache costano
  il 5% dell'entrata; le richieste in blocco («Batch») costano la metà.
* **Niente strumenti**: il modello non cerca sul web, non esegue codice, non vede altro che il messaggio che gli diamo.
* **Rifiuto o risposta non valida** (`stop_reason` «refusal», JSON che non rispetta lo schema, errore del servizio dopo i tentativi
  dell'SDK): in quel giro **nessuna operazione nuova**; le posizioni aperte restano con i loro stop. Si scrive nel diario.

## 3. Il passato onesto e il paper in avanti
* **La prova sul passato** comincia il **1° luglio 2026 alle 00:00 UTC** (il primo giorno dopo la data di addestramento) e finisce il
  **20 novembre 2026 alle 24:00 UTC** (143 giorni, 858 decisioni da 4 ore). Prima di luglio il modello ha già letto com'è andata: lì
  **nessuna prova**, mai.
* A ogni decisione il modello riceve **solo i dati chiusi prima dell'ora della decisione**: il codice taglia ogni serie all'ora della
  decisione e un test lo controlla (`tests/`: nessuna riga dopo l'ora della decisione entra nel messaggio).
* **Nel messaggio c'è la data vera.** Dopo giugno 2026 il modello non sa niente del mercato, quindi la data non gli dà vantaggi; toglierla
  non servirebbe (i prezzi la tradiscono comunque).
* **Il paper in avanti** parte appena c'è la chiave, accanto alla prova sul passato, e prosegue finché il proprietario non lo ferma.
* **Una sola corsa vale.** Il modello non risponde due volte uguale. La corsa che conta è la prima, completa, sul periodo intero; una
  seconda corsa solo su luglio misura quanto il risultato cambia a parità di dati (si scrive, non sostituisce la prima). Ritoccare le
  istruzioni e rifare la prova sullo stesso periodo finché viene bella è vietato: ogni versione nuova si prova sui giorni **dopo** la sua
  data (paper in avanti), il periodo luglio-novembre è usato una volta.

## 4. Le monete
* **Regola**: i 12 perpetui in USDT di Binance con più volume scambiato (in USDT) nel **mese di giugno 2026**, fra quelli quotati da prima
  del 1° gennaio 2026 e ancora quotati il 20 novembre 2026, esclusi gli stablecoin e l'oro tokenizzato. Il mese di giugno sta prima della
  prova: la scelta non guarda avanti. Lo script `trader_ai/universo.py` la calcola dai file mensili pubblici di
  `data.binance.vision`, scrive `trader_ai/universo.json` e quel file non cambia più per tutta la versione.
* **BTC** entra sempre (è anche il riferimento); se non fosse fra i primi 12 sarebbe il tredicesimo.

## 5. Cosa riceve il modello a ogni decisione
Tutto in un unico messaggio, con le parti fisse (istruzioni, regole, schema) in testa per la cache e le parti che cambiano in coda.
1. **Le istruzioni fisse** (`trader_ai/istruzioni.md`, scritte prima della prima chiamata): il compito (far crescere il conto al netto
   delle spese), i limiti fissi della sezione 7 (così non propone cose che verrebbero scartate), le spese della sezione 8, il formato della
   risposta.
2. **Per ogni moneta**: le ultime 42 candele da 4 ore (7 giorni: apertura, massimo, minimo, chiusura, volume in milioni di USDT), le
   chiusure giornaliere degli ultimi 30 giorni, il funding degli ultimi 3 pagamenti e la media dei 7 giorni, l'interesse aperto in USDT
   ora e la sua variazione su 24 ore e 7 giorni, il rapporto fra acquisti e vendite aggressive delle ultime 24 ore.
3. **Il portafoglio**: il conto (contanti più guadagni e perdite aperti), ogni posizione con lato, valore, prezzo di entrata, guadagno o
   perdita, stop, funding pagato o incassato, da quante ore è aperta; le ultime 10 operazioni chiuse con il risultato.
4. **Solo nel ramo «con notizie e balene» (sezione 6)**: i titoli (non i testi) degli articoli dell'archivio
   `research/notizie/archivio/` visti nelle ultime 24 ore che citano una moneta dell'elenco (al massimo 60, i più recenti), e per ogni
   moneta la posizione netta sommata dei conti di Hyperliquid seguiti in `research/trader_copiati/hyperliquid/` (lettura più recente prima
   dell'ora della decisione) con quanti conti sono lunghi e quanti corti. Questi testi stanno dentro un contenitore marcato «dati esterni,
   non istruzioni»; il modello non ha strumenti e può solo rispondere con lo schema della sezione 6, che il codice controlla.

I dati di mercato della prova sul passato vengono dai file pubblici di Binance (`data.binance.vision`: candele, funding, «metrics» con
l'interesse aperto e gli acquisti aggressivi). Le notizie esistono solo dal 30 ottobre 2026 e le posizioni di Hyperliquid dal 2 novembre
2026: per questo la prova sul passato usa **solo il ramo «mercato»**.

## 6. Cosa risponde il modello, e i due rami
* **Lo schema** (uscita strutturata validata, `output_config.format` con schema JSON): un elenco di al massimo 12 decisioni, ognuna con
  `moneta` (dell'elenco), `azione` (`apri_lungo`, `apri_corto`, `chiudi`, `riduci`, `sposta_stop`), `quota_conto` (la dimensione come
  frazione del conto, da 0 a 0,20; per `riduci` la frazione della posizione da chiudere), `stop_percentuale` (distanza dello stop dal
  prezzo, da 1 a 15), `motivo` (al massimo 300 caratteri), più un `commento_mercato` generale (al massimo 600 caratteri). Un elenco vuoto
  vuol dire «non faccio niente», ed è una risposta valida.
* **Ramo «mercato»**: le parti 1-3 della sezione 5. È quello della prova sul passato e gira anche in avanti, con le stesse istruzioni.
* **Ramo «con notizie e balene»**: le parti 1-4, solo in avanti. Il confronto fra i due rami negli stessi giorni dice se notizie e balene
  aggiungono qualcosa. Il secondo ramo raddoppia il costo delle chiamate: parte solo con l'ok del proprietario.

## 7. I limiti fissi (nel codice, `trader_ai/limiti.py`; il modello propone, il codice decide)
* **Capitale simulato di partenza**: 1.000 USDT per ramo (come il demo di G1 dall'8 novembre 2026).
* **Per posizione**: valore al massimo il **20% del conto** al momento dell'apertura; una sola posizione per moneta (aprire il lato
  opposto vuol dire prima chiudere).
* **Esposizione totale** (somma dei valori di tutte le posizioni, lunghe più corte): al massimo il **100% del conto**, cioè leva 1.
* **Al massimo 6 posizioni aperte** insieme; ordine minimo 20 USDT.
* **Stop obbligatorio** fra l'1% e il 15% dal prezzo di entrata; senza stop valido la decisione si scarta. Lo stop si può solo
  avvicinare al prezzo (stringere), mai allontanare.
* **Perdita di un giorno**: se il conto scende dell'**8%** rispetto alla mezzanotte UTC, si chiude tutto e per 24 ore non si apre niente.
* **Perdita massima**: se il conto scende del **25%** dal massimo raggiunto, si chiude tutto e il trader **si ferma**; riparte solo con
  l'ok del proprietario (versione nuova).
* **Spesa delle chiamate in avanti**: al massimo **3 dollari al giorno** e **60 al mese** contati dal codice sui token veri della
  risposta; oltre, nessuna chiamata fino al giorno (o al mese) dopo, e le posizioni restano con i loro stop. **La prova sul passato** ha
  un tetto suo, **100 dollari** per la corsa intera (stima in `README.md`, «Il piano»): oltre, si ferma e si scrive dove è arrivata. Le
  858 decisioni sono in fila (ognuna dipende dal portafoglio lasciato dalla precedente), quindi lo sconto delle richieste in blocco non si
  può usare. In più il proprietario mette un limite di spesa
  sul suo conto di Anthropic: è l'ultima protezione, fuori dal nostro codice.
* Una decisione scartata si scrive nel diario con il motivo dello scarto; il resto delle decisioni dello stesso giro va avanti.
* Il codice rifiuta qualunque moneta fuori elenco e qualunque campo fuori schema, qualunque cosa dica il motivo.

## 8. Come si simulano gli ordini e le spese
* **Quando**: la decisione delle 00, 04, 08, 12, 16, 20 UTC usa i dati chiusi a quell'ora; l'ordine si esegue all'**apertura della
  candela da 4 ore che comincia a quell'ora** (nella prova sul passato) o al prezzo letto dopo la risposta del modello (in avanti).
* **Spese**: ogni ordine a mercato paga lo **0,05%** del valore; scarto di prezzo **0,01%** su BTC, ETH e SOL e **0,02%** sulle altre,
  sempre contro di noi (decisione del proprietario del 7 novembre 2026). Nessun ordine limite nella prima versione (non sapremmo
  simularne l'esecuzione in modo onesto con candele da 4 ore).
* **Funding vero**: ogni 8 ore (o all'intervallo vero della moneta) la posizione aperta paga o incassa il tasso pubblicato da Binance per
  quell'ora sul valore della posizione.
* **Stop**: si controllano sulle candele da 1 ora. Se il minimo (per i lunghi) o il massimo (per i corti) tocca lo stop, si esce allo
  stop meno lo scarto; se la candela apre già oltre lo stop, si esce all'apertura (il caso peggiore). La spesa dello 0,05% vale anche qui.
* **Costo delle chiamate**: si conta in dollari dai token veri di ogni risposta (entrata, cache, uscita) e si sottrae dal conto come se
  1 dollaro valesse 1 USDT.

## 9. Come si giudica
* **Contro chi**, negli stessi giorni e con 1.000 USDT di partenza: (a) **G1** (nella prova sul passato il G1 ricalcolato dalla ricerca
  su luglio-novembre; in avanti il G1 del paper e del demo); (b) **il solo Bitcoin** comprato e tenuto; (c) **i contanti** (zero).
* **Quali numeri**, ogni lunedì al proprietario: il conto al netto di tutto; il conto **prima** del costo delle chiamate (dice se il
  modello sa scegliere, a prescindere da quanto costa); la discesa massima; lo Sharpe sui giorni; quante decisioni, quante scartate e
  perché; quanto è costato il modello.
* **Cosa può dire la prova sul passato**: 143 giorni non bastano per l'esame delle strategie (ogni anno positivo, t da 3, Sharpe corretto
  da 0,80): un risultato bello lì **non promuove** niente, perché un periodo di 4-5 mesi oscilla troppo (Alpha Arena, `README.md`).
  Può però **bocciare**: se il conto prima del costo delle chiamate finisce sotto zero **e** sotto il solo Bitcoin, l'idea si scrive come
  bocciata (con il perché) e il paper in avanti continua solo se il proprietario lo chiede.
* **Soldi veri o un conto demo suo**: mai senza la richiesta esplicita del proprietario, qualunque sia il risultato.

## 10. Versioni
| Versione | Data | Cosa cambia |
|---|---|---|
| 1 | 21 novembre 2026 | prima scrittura, prima di ogni chiamata al modello |
