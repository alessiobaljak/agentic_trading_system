# Le regole del trader AI (versione 3, 23 novembre 2026, prima di ogni chiamata al modello)

Le scelte del proprietario del 23 novembre 2026 (risposte alle domande della sessione «trading AI»):
* «La moneta la scelgo io, esempio BTC, time frame anche questo fisso 5, 15, 30 [...] lui deve live guardare i dati, indicatori etc
  e decidere quando entrare, TP, SL, leva; l'obiettivo [...] partendo da 1000 fare XX profitto al giorno, dopo quello si ferma.»
* Obiettivo: **50** (USDT al giorno). Perdita massima del giorno: «non ci sono limiti nella demo pur di raggiungere l'obiettivo di
  profitto». Ritmo: «ogni 15 minuti se il trade è ancora aperto, altrimenti appena il trade si chiude deve essere invocato». Leva:
  «anche 10».
* «Questa AI deve adattarsi in maniera velocissima: deve provare quello che crede sia il momento migliore per entrare e vendere, ma
  deve anche capire se quello che sta provando non va bene e cambiare approccio.»
* «Non deve guardare e sapere nulla delle altre strategie create dall'altra sessione: si lavora su due approcci totalmente diversi.»
Decisione del 23 novembre (`docs/decisioni_del_proprietario.md`): conto demo di Binance suo (1.000 USDT, separato da G1), Claude Opus
5.5, tetto di spesa di 5 euro al giorno nel codice, sulla macchina.

## 1. Cosa fa
Su **una moneta scelta dal proprietario** (all'inizio **BTCUSDT**, si cambia in `trader_ai/config.json`), il modello guarda le candele da
**5, 15 e 30 minuti** con gli indicatori e decide da solo: entrare lungo o corto, quanto, con quale leva, dove mettere lo stop (SL) e
l'obiettivo (TP), quando chiudere. Quando il conto ha guadagnato **50 USDT dalla mezzanotte UTC**, il codice chiude tutto e il trader
**si ferma fino alla mezzanotte UTC** (l'una di notte in Svizzera d'inverno).

## 2. Quando viene chiamato
* **A ogni candela da 15 minuti chiusa** (:00, :15, :30, :45 UTC), con o senza un'operazione aperta;
* **subito quando un'operazione si chiude** (stop, obiettivo o liquidazione sul conto), per decidere cosa fare dopo.
* Non viene chiamato: dopo l'obiettivo del giorno raggiunto; quando il tetto di spesa è finito (sezione 3).

## 3. Il modello e il tetto di spesa
* `claude-opus-5-5`, SDK Python ufficiale `anthropic`, pensiero adattivo (sempre acceso), sforzo `medium`, risposta al massimo 12.000
  token. Data di addestramento: giugno 2026 (https://platform.claude.com/docs/en/about-claude/models/overview, letta il 21 novembre
  2026). Nessuno strumento (niente web, niente codice). Nessun ripiego automatico su un altro modello.
* **Tetto: 5 dollari al giorno UTC** (sotto i 5 euro finché l'euro vale più del dollaro), contati sui token dichiarati da ogni risposta
  (4 dollari al milione in entrata, 20 in uscita, cache 0,20 in lettura e 5,00 in scrittura). **Prima di ogni chiamata** il codice
  calcola il costo più alto possibile (messaggio a 2 caratteri per token al prezzo più caro, più 12.000 token di risposta); se non sta nel
  rimasto, non chiama fino alla mezzanotte UTC. Le operazioni aperte restano con lo stop e l'obiettivo già piazzati sul conto.
* **Stima, non misura**: con una sola moneta una chiamata costa circa 5-7 centesimi; 96 chiamate al giorno più quelle alle chiusure
  fanno circa 5-7 dollari, cioè **il tetto può finire prima di sera**. La misura vera dei primi giorni si scrive qui.

## 4. Cosa riceve
1. **Istruzioni fisse** (`trader_ai/istruzioni.md`): l'obiettivo del giorno, i limiti della sezione 6, le spese, il formato della risposta.
2. **I dati della moneta**: candele chiuse da 5 minuti (ultime 4 ore), da 15 minuti (ultime 12 ore), da 30 minuti (ultime 24 ore), con
   per ogni intervallo gli indicatori calcolati dal codice sull'ultima candela chiusa (medie esponenziali a 9, 21 e 50, RSI a 14,
   MACD 12-26-9, bande di Bollinger 20-2, ATR a 14, VWAP del giorno, volume rispetto alla media di 20); il prezzo attuale, il funding
   attuale e il prossimo, l'interesse aperto e la sua variazione nell'ultima ora. Solo candele chiuse prima dell'ora della chiamata.
3. **Il conto**: saldo, guadagno del giorno rispetto alla mezzanotte e quanto manca ai 50, l'operazione aperta (lato, entrata, leva,
   margine, stop, obiettivo, risultato, prezzo di liquidazione), gli ordini aperti.
4. **La sua memoria** (per adattarsi in fretta): le ultime 30 operazioni chiuse con entrata, uscita, come si sono chiuse, risultato e
   l'approccio che stava usando; il suo approccio attuale e le sue ultime 10 note di diario.
5. L'ora, il motivo della chiamata, il budget di chiamate rimasto oggi.

**Niente altro**: nessun dato, file, risultato o nome delle strategie dell'altra sessione (G1, la ricerca, le notizie e i conti di
Hyperliquid raccolti dalla ricerca). Il codice di `trader_ai/` non importa niente da `research/` né da `bot/` (test).

## 5. Cosa risponde (uscita strutturata validata)
* `azione`: `aspetta`, `apri_lungo`, `apri_corto`, `chiudi`, `modifica` (sposta stop o obiettivo dell'operazione aperta).
* Per aprire: `margine_usdt` (quanto del conto mette), `leva` (da 1 a 10), `stop_prezzo` (obbligatorio), `obiettivo_prezzo`
  (facoltativo), `tipo_ordine` (`mercato` o `limite` con `prezzo_limite`).
* Per modificare: `stop_prezzo` e/o `obiettivo_prezzo` nuovi.
* `approccio`: in una frase, il metodo che sta usando adesso (per esempio «rottura del massimo delle 4 ore sui 15 minuti»).
* `cambio_approccio`: vero se ha deciso di cambiare metodo, con `perche`.
* `diario`: cosa vede e perché decide così (al massimo 600 caratteri).
* Rifiuto, risposta fuori schema, tagliata o errore del servizio: nessuna operazione nuova; si riprova alla candela dopo.

## 6. I limiti nel codice (pochi, per scelta del proprietario: «non ci sono limiti nella demo»)
* Solo la moneta scelta dal proprietario, solo **il conto demo suo**: il programma rifiuta di partire se le chiavi sono uguali a
  quelle del demo di G1 (`BINANCE_DEMO_API_KEY`, `BINANCE_DEMO_API_SECRET`, `BINANCE_DEMO_PRIVATE_KEY_PATH`).
* **Leva al massimo 10**; margine al massimo il saldo disponibile; una sola operazione aperta alla volta.
* **Stop obbligatorio** per ogni operazione, piazzato sul conto come ordine vero (scatta anche se il programma è fermo), dalla parte
  giusta del prezzo e prima del prezzo di liquidazione. Lo stop e l'obiettivo li sceglie il modello; li può spostare quando vuole.
* **Obiettivo del giorno**: conto ≥ conto a mezzanotte UTC + 50 USDT → si chiude tutto e niente chiamate fino a mezzanotte.
* **Nessuna perdita massima del giorno né totale** (scelta del proprietario). Se il conto non basta per l'ordine minimo di Binance, il
  trader si ferma da solo e lo scrive.
* Una decisione fuori da questi limiti si scarta e si scrive nel diario, e il modello alla chiamata dopo vede che è stata scartata e perché.

## 7. Spese e misura
* Le spese sono quelle vere del conto demo (commissioni, funding, prezzo eseguito). Il costo delle chiamate si sottrae dal risultato
  come se 1 dollaro valesse 1 USDT.
* Ogni lunedì al proprietario: quanti giorni ha raggiunto i 50, quanto ha guadagnato o perso al netto di tutto, quante operazioni e con
  che risultato, quante volte ha cambiato approccio e con che effetto, quanto sono costate le chiamate, la discesa massima del conto.
  **In più, la prova di una previsione della sessione** (23 novembre, il proprietario: «chi ha detto che il modello deve alzare il
  rischio per recuperare?»): la leva e il margine medi delle aperture fatte quando il guadagno del giorno era sotto zero, contro quelle
  fatte quando era sopra. Le istruzioni gli dicono di non alzarli per recuperare; se salgono lo stesso, la previsione era giusta e si
  corregge; se non salgono, era sbagliata.
  Confronto con il solo BTC tenuto negli stessi giorni. Non si confronta con le strategie dell'altra sessione dentro il trader (il
  modello non le vede mai); il confronto, se il proprietario lo vuole, lo fa la sessione nei resoconti.
* Soldi veri: mai senza la richiesta esplicita del proprietario.

## 8. Prima dell'avvio
Codice e test con un modello finto → `conto_demo.py`, lo script d'installazione e il servizio sulla macchina (tutto in `trader_ai/`, sul
modello di `stock/avanti/vps/`; risposta della sessione crypto in `docs/risposte_trading_ai.md`) → live-path-reviewer → conto demo e
chiavi del proprietario → ok del proprietario al primo avvio.

## 9. Versioni
| Versione | Data | Cosa cambia |
|---|---|---|
| 1 | 21 novembre 2026 | ogni 4 ore, 12 monete fisse, solo simulato. Mai usata |
| 2 | 23 novembre 2026 | il modello sceglie monete e momenti, demo suo. Mai usata |
| 3 | 23 novembre 2026 | moneta e intervalli scelti dal proprietario (BTC; 5, 15, 30 minuti), chiamata ogni 15 minuti e a ogni chiusura, obiettivo di 50 USDT al giorno poi stop, leva fino a 10, nessuna perdita massima, memoria per cambiare approccio, nessun dato dell'altra sessione |
