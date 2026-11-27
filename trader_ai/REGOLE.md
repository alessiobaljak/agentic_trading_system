# Le regole del trader AI (versione 8, 26 novembre 2026: le tre decisioni del proprietario; versione 7, 26 novembre 2026: dati e istruzioni corretti dopo il controllo del 26 novembre; versione 5, 25 novembre 2026: obiettivo del giorno al 3%; versione 4, 24 novembre 2026, prima di ogni chiamata al modello)

**Versione 8, le tre decisioni del proprietario** (26 novembre 2026, «sì alle tre decisioni, procedi», sulle proposte 5.1-5.3 del
controllo): (1) il tetto resta 5 dollari il primo giorno; si misura quanto costa una chiamata a sforzo alto e fino a che ora bastano,
poi decide il proprietario; (2) l'obiettivo e il «impara» delle istruzioni senza maiuscole, stessa frase; (3) il 3% si conta dopo le
spese di chiusura dell'operazione aperta (commissione e scarto d'uscita), così è guadagno vero. Il fermo fino a mezzanotte scatta solo
se il guadagno letto sul conto **dopo** la chiusura arriva al 3%, al centesimo: se fra il controllo e la chiusura il prezzo si è mosso,
o uno stop è scattato prima, il guadagno resta sotto, l'obiettivo non è raggiunto e il modello si chiama subito per la chiusura
(revisione del 26 novembre 2026, problema 204; il proprietario: «non si deve fermare finché non ha raggiunto il 3%»). Dal riesame
della sedicesima (27 novembre 2026): il centesimo vale sempre, prima e dopo la chiusura; un ordine limite in attesa si annulla come
quando lo annulla il modello (se si esegue proprio in quel momento, si chiude subito); se durante il fermo il conto scende sotto il 3%
(un funding pagato dopo la chiusura) il fermo si toglie e il modello si chiama (il resoconto lo dice); dopo una chiusura lo stato e il
motivo della chiamata si salvano subito, prima di ogni altra lettura del conto; annullando un ordine limite si toglie prima il solo
limite, e stop e obiettivo restano finché non si sa se il limite si è eseguito.

**Versione 7, il controllo del 26 novembre 2026** (`trader_ai/revisioni/2026-11-26-controllo-istruzioni-e-dati.md`; il proprietario: «sei
sicuro di avere creato le istruzioni corrette [...] che abbia tutti gli elementi a disposizione per prendere le decisioni?»). Il primo
giorno (25-26 novembre) il modello riceveva dati sbagliati: un ordine limite non eseguito come «operazione aperta» con un guadagno finto
(19 chiamate su 104), le uscite sbagliate in memoria, un'operazione eseguita e chiusa fra due controlli mai registrata, le lezioni
sparite dopo due ore e mezza, il budget in dollari scambiato per un motivo per aspettare. Corretto tutto: sezioni 2-5 e 7 qui sotto. Le
scelte del proprietario non cambiano (moneta, intervalli, obiettivo, nessuna perdita massima, leva, tetto, nessun consiglio di strategia).

**Versione 4, il conto simulato** (il proprietario, 24 novembre 2026: «non posso creare un account nuovo [...] posso solo creare altre
chiavi API», poi «conto simulato sul programma va bene»). La prova sul demo del 24 novembre si è fermata al primo punto, senza toccare
niente: le chiavi nuove aprivano il conto demo di G1 (53 monete aperte). Da qui il trader **non usa nessun conto di Binance**: legge i
prezzi veri dalle pagine pubbliche dei future (nessuna chiave) e simula ordini, spese, funding, stop, obiettivo e liquidazione nel
programma (`trader_ai/conto_simulato.py`), minuto per minuto sulle candele vere da 1 minuto, partendo da 1.000 USDT finti. Tutto il resto
delle regole qui sotto vale uguale («il conto demo» va letto come «il conto simulato»); il collegamento al demo (`conto_demo.py`) resta
pronto se un giorno ci sarà un conto demo suo (`config.json`, `"conto": "demo"`).

**Come simula** (`conto_simulato.py`; scelte tecniche della sessione, approvate dalla nona revisione del 24 novembre):
* spese 0,05% a mercato e 0,02% con ordine limite eseguito; scarto di prezzo 0,01% su BTC, ETH e SOL, 0,02% sulle altre, contro di noi;
* stop, obiettivo e liquidazione scattano sul **prezzo mark** del minuto (come farebbero sul conto, `workingType=MARK_PRICE`); si esce al
  livello meno lo scarto, o all'apertura del minuto se apre già oltre; stop e obiettivo nello stesso minuto: vale lo stop;
* un ordine limite si esegue solo se il prezzo **va oltre** il limite (toccarlo non basta); un limite che incrocia subito il prezzo si
  esegue a mercato;
* stop e obiettivo valgono solo per una posizione del loro lato (dal 26 novembre: uno stop rimasto da un lungo chiudeva il corto aperto
  dopo); ogni posizione tiene i suoi conti (nome dell'ordine, spese, funding, uscita, modo), che il programma legge con `esito_ordine`;
  prima di annullare gli ordini si contano i minuti già chiusi (un limite eseguito in un minuto appena chiuso non sparisce);
* sempre il caso peggiore per noi: un ordine limite e un obiettivo contano **dal minuto dopo** quello in cui sono nati; uno stop
  conta **già nel minuto in cui nasce**, e uno stop tolto resta valido fino alla fine del suo minuto (quando lo stop si sposta la
  posizione non resta mai scoperta; fra più stop vale il più vicino al prezzo); nel minuto in cui un limite si esegue l'obiettivo non
  conta e lo stop sì;
* liquidazione: si perde tutto il margine della posizione (margine separato), prezzo approssimato a 1/leva meno lo 0,5%;
* funding: i pagamenti veri pubblicati da Binance, anche in ritardo, una volta sola, alla posizione aperta in quel momento;
* dopo un fermo si recuperano tutti i minuti persi; se Binance non li ha, nessuna decisione finché non arrivano.

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
l'obiettivo (TP), quando chiudere. Quando il conto ha guadagnato **il 3% del conto della mezzanotte UTC** (30 USDT su 1.000; fino al 24 novembre 50 USDT), contato dopo le spese di chiusura dell'operazione aperta (dal 26 novembre), il codice chiude tutto e il trader
**si ferma fino alla mezzanotte UTC** (l'una di notte in Svizzera d'inverno).

## 2. Quando viene chiamato
* **A ogni candela da 15 minuti chiusa** (:00, :15, :30, :45 UTC), con o senza un'operazione aperta;
* **subito quando un'operazione si chiude** (stop, obiettivo o liquidazione sul conto), per decidere cosa fare dopo; dal 26 novembre
  anche quando la chiude il modello stesso o quando annulla un ordine limite (al passo dopo, entro 30 secondi), e quando un limite si
  esegue e si chiude fra due controlli.
* Non viene chiamato: dopo l'obiettivo del giorno raggiunto; quando il tetto di spesa è finito (sezione 3).

## 3. Il modello e il tetto di spesa
* `claude-opus-5-5`, SDK Python ufficiale `anthropic`, pensiero adattivo (sempre acceso) con il **riassunto del ragionamento**
  (`display: "summarized"`, dal 26 novembre: si paga uguale, ma si vede come ragiona; nel diario i primi 1.500 caratteri, intero nei file
  dei messaggi sulla macchina), sforzo `high` (dal 26 novembre; prima `medium`), risposta al massimo 16.000 token. Istruzioni e memoria
  stabile nella **cache da un'ora** (dal 26 novembre: con una chiamata ogni 15 minuti quella da 5 minuti scadeva sempre). Data di addestramento: giugno 2026 (https://platform.claude.com/docs/en/about-claude/models/overview, letta il 21 novembre
  2026). Nessuno strumento (niente web, niente codice). Nessun ripiego automatico su un altro modello.
* **Tetto: 5 dollari al giorno UTC** (sotto i 5 euro finché l'euro vale più del dollaro), contati sui token dichiarati da ogni risposta
  (4 dollari al milione in entrata, 20 in uscita, cache 0,20 in lettura, 5,00 in scrittura da 5 minuti e 8,00 da un'ora). **Prima di
  ogni chiamata** il codice calcola il costo più alto possibile (messaggio a 1,5 caratteri per token, misurati 1,8, al prezzo più caro,
  più 16.000 token di risposta); se non sta nel rimasto, non chiama fino alla mezzanotte UTC. Le operazioni aperte restano con lo stop e
  l'obiettivo già piazzati sul conto. Il modello non vede dollari: vede quante chiamate restano e a che ora arriverà l'ultima.
* **Stima, non misura**: con una sola moneta una chiamata costa circa 5-7 centesimi; 96 chiamate al giorno più quelle alle chiusure
  fanno circa 5-7 dollari, cioè **il tetto può finire prima di sera**. La misura vera dei primi giorni si scrive qui.

## 4. Cosa riceve
1. **Istruzioni fisse** (`trader_ai/istruzioni.md`), corte e **senza consigli di strategia** (il proprietario, 23 novembre: «non capisco
   perché devi dare al modello istruzioni così dettagliate [...] è un agente live AI, legge, interpreta e si adatta sul momento trade
   dopo trade, con l'obiettivo giornaliero di max 50»): l'obiettivo, le regole meccaniche della sezione 6, le spese, il formato.
2. **I dati della moneta**: le ultime 48 candele chiuse da 5 minuti (4 ore), da 15 minuti (12 ore), da 30 minuti (24 ore), con il volume
   e la quota comprata a mercato, e la candela in corso a parte (dal 26 novembre: «solo candele chiuse» era una scelta della sessione,
   non del proprietario); per ogni intervallo gli indicatori calcolati dal codice sulle candele chiuse (medie esponenziali a 9, 21 e 50,
   RSI a 14, MACD 12-26-9, bande di Bollinger 20-2, ATR a 14 anche in percentuale, ampiezza mediana delle ultime 20 candele, volume
   rispetto alla media di 20) e gli ultimi 4 valori di RSI, istogramma del MACD e volume sulla media. Poi: il prezzo mark (su cui scattano
   stop, obiettivo e liquidazione) e l'indice con il premio; il funding in percentuale e sulla posizione; l'interesse aperto con la
   variazione in 1 e 4 ore; prezzo, VWAP e quota comprata a mercato dalla mezzanotte UTC; i livelli di oggi, di ieri e delle ultime 100
   ore; l'ampiezza tipica delle candele per fascia oraria; il giorno della settimana, la borsa di New York (aperta, chiusa, festa) e gli
   orari del funding (`calendario.py`). Nessuna notizia.
3. **Il conto**: saldo, guadagno da mezzanotte e quanto manca al 3%, risultato dall'inizio della prova, le perdite di fila; l'operazione
   aperta (lato, entrata e ora d'esecuzione, leva, valore, margine, stop iniziale e attuale, obiettivo, liquidazione, distanze in
   percentuale e in ATR dei tre intervalli, risultato lordo e netto se chiude adesso, netto allo stop e all'obiettivo, pareggio, 1 R,
   quanto il prezzo è andato a favore e contro dall'esecuzione) **oppure** l'ordine limite in attesa, detto come tale (nessuna
   posizione, nessun risultato).
4. **La sua memoria**, in due parti. Stabile, nella cache: il bilancio delle operazioni chiuse (oggi, ieri, dall'inizio: per direzione,
   netto diviso in prezzo, spese e funding, come si sono chiuse), le sue ultime 10 lezioni (restano anche nei giorni dopo), le ultime 30
   operazioni chiuse (le ultime 5 con la scheda intera: stop iniziale e spostamenti, spese, durata, R, a favore e contro, il motivo scritto
   all'apertura). Nuova a ogni chiamata: l'approccio attuale, le lezioni scritte dopo l'ultima chiusura, le note delle ultime 10 chiamate.
5. L'ora, il motivo della chiamata, quante chiamate restano oggi e a che ora arriverà l'ultima, e la sua decisione precedente se non è
   stata eseguita (scartata dal programma, rifiutata dal conto, o risposta non letta).

**Niente altro**: nessun dato, file, risultato o nome delle strategie dell'altra sessione (G1, la ricerca, le notizie e i conti di
Hyperliquid raccolti dalla ricerca). Il codice di `trader_ai/` non importa niente da `research/` né da `bot/` (test).

## 5. Cosa risponde (uscita strutturata validata)
* `azione`: `aspetta`, `apri_lungo`, `apri_corto`, `chiudi`, `modifica` (sposta stop o obiettivo dell'operazione aperta).
* Per aprire: `margine_usdt` (quanto del conto mette), `leva` (da 1 a 10), `stop_prezzo` (obbligatorio), `obiettivo_prezzo`
  (facoltativo), `tipo_ordine` (`mercato` o `limite` con `prezzo_limite`).
* Per modificare: `stop_prezzo` e/o `obiettivo_prezzo` nuovi.
* `approccio`: in una frase, il metodo che sta usando adesso, senza i livelli di prezzo di oggi.
* `cambio_approccio`: vero se ha deciso di cambiare metodo, con `perche` (entra nelle lezioni).
* `lezione` (dal 26 novembre): quando è chiamato per un'operazione chiusa, che cosa aveva previsto, che cosa è successo e che cosa cambia.
* `diario`: cosa vede e perché decide così (circa 600 caratteri). Le lunghezze sono indicazioni: l'API non le controlla e il programma
  taglia i testi quando li salva (prima un diario di 601 caratteri buttava via la decisione). La leva è un numero intero.
* Rifiuto, risposta fuori schema, tagliata o errore del servizio: nessuna operazione nuova; si riprova alla candela dopo.

## 6. I limiti nel codice (pochi, per scelta del proprietario: «non ci sono limiti nella demo»)
* Solo la moneta scelta dal proprietario, solo **il conto demo suo**: il programma rifiuta di partire se le chiavi sono uguali a
  quelle del demo di G1 (`BINANCE_DEMO_API_KEY`, `BINANCE_DEMO_API_SECRET`, `BINANCE_DEMO_PRIVATE_KEY_PATH`).
* **Leva al massimo 10**; margine al massimo il saldo disponibile; una sola operazione aperta alla volta.
* **Stop obbligatorio** per ogni operazione, piazzato sul conto come ordine vero (scatta anche se il programma è fermo), dalla parte
  giusta del prezzo e prima del prezzo di liquidazione. Lo stop e l'obiettivo li sceglie il modello; li può spostare quando vuole.
* **Obiettivo del giorno**: conto meno le spese di chiusura dell'operazione aperta ≥ conto a mezzanotte UTC × 1,03, al centesimo →
  si chiude tutto; se dopo la chiusura il guadagno sul conto è almeno il 3% (al centesimo), niente chiamate fino a mezzanotte, se no
  si continua; se durante il fermo il guadagno scende sotto il 3%, il fermo si toglie (dal 26-27 novembre; prima senza togliere le
  spese di chiusura, con il centesimo solo dopo la chiusura e con il fermo anche sotto il 3%).
* **Nessuna perdita massima del giorno né totale** (scelta del proprietario). Se il conto non basta per l'ordine minimo di Binance, il
  trader si ferma da solo e lo scrive.
* Una decisione fuori da questi limiti si scarta e si scrive nel diario, e il modello alla chiamata dopo vede che è stata scartata e perché.
* Dal 26 novembre (quindicesima revisione): margine più la commissione d'entrata dentro il disponibile; un ordine limite già oltre il
  prezzo si controlla anche sul prezzo di adesso e si tratta come un ordine a mercato (stop subito, chiusura se il conto lo rifiuta);
  l'obiettivo di un ordine limite va sul conto all'esecuzione e, se il prezzo l'ha già superato, si chiude a mercato; un ordine limite
  sparito dal libro si decide solo dopo aver letto l'esito e riletto la posizione (un errore di lettura non fa niente: si riprova).
* Il messaggio intero al modello e il suo ragionamento restano sulla macchina, fuori da `trader_ai/avanti/` (che va nel repository):
  `/opt/trader-ai-dati/trader_ai/messaggi_modello/`, un file al giorno, 7 giorni.

## 7. Spese e misura
* Le spese sono quelle vere del conto demo (commissioni, funding, prezzo eseguito). Il costo delle chiamate si sottrae dal risultato
  come se 1 dollaro valesse 1 USDT.
* **Ogni giorno a mezzanotte UTC**, alla fine del giorno del trader (il proprietario, 23 novembre: «perché devo vederlo il lunedì,
  qual è la scelta dietro questo giorno?»; il lunedì veniva dalla decisione del 1° novembre per le strategie dell'altra sessione, non
  da questo trader): obiettivo raggiunto o no e a che ora; le operazioni del giorno con entrata, uscita, leva, risultato e il motivo
  scritto dal modello; quante volte ha cambiato approccio; quanto sono costate le chiamate; il conto e la discesa massima dall'inizio;
  il solo BTC tenuto negli stessi giorni. Solo misura, nessuna istruzione al modello: anche la leva e il margine medi delle aperture
  fatte con il giorno in perdita contro quelle con il giorno in guadagno. Dal 26 novembre il risultato si legge dal conto (prima era la
  somma delle operazioni registrate: il 25 novembre −48,93 invece di −53,61), con la discesa massima, le uscite per tipo, la durata, il
  rischio allo stop di ogni apertura, quanto mancava al 3% e quante ore alla mezzanotte, e i numeri delle chiamate (quante, costo medio,
  durata, esiti). Il resoconto del 25 novembre è stato rifatto con la memoria ricostruita.
* **Durante il giorno** ogni decisione va subito nel diario sulla macchina (`trader_ai/avanti/`), nel repository una volta all'ora;
  più avanti in una scheda della dashboard.
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
| 4 | 24 novembre 2026 | conto simulato dal programma con i prezzi veri (nessuna chiave di Binance): l'unico account Binance del proprietario ha già il conto demo di G1 |
| 5 | 25 novembre 2026 | obiettivo del giorno: il 3% del conto della mezzanotte UTC invece di 50 USDT (il proprietario: «il profitto giornaliero mettilo al 3%»), prima del primo avvio |
| 6 | 26 novembre 2026 | il 3% è un obiettivo obbligatorio, non un tetto; a ogni chiamata il bilancio di oggi (direzioni, vinte e perse, prezzo da mezzanotte); sforzo di ragionamento «high» e risposta fino a 16.000 token (il proprietario: «non si deve fermare finché non ha raggiunto il 3% [...] l'AI deve sapere se il primo trade è fallito [...] che cosa hai creato come AI se non pensa») |
| 7 | 26 novembre 2026 | dopo il controllo del 26 novembre: ordine limite in attesa detto come tale; limite eseguito e chiuso fra due controlli registrato; stop e obiettivo solo per il loro lato; uscite, spese e funding dal conto; memoria ricostruita; scheda di ogni operazione, lezioni che restano, bilancio con il netto diviso; candela in corso, livelli, orari, premio, interesse aperto in 1 e 4 ore; chiamate rimaste invece dei dollari; richiamo dopo un «chiudi»; risposte non lette dette al modello; cache da un'ora e ragionamento riassunto; istruzioni sulla meccanica degli ordini e sulle spese (nessun consiglio di strategia) |
| 8 | 26 novembre 2026 | le tre decisioni del proprietario: tetto di 5 dollari confermato per il primo giorno, da misurare; obiettivo e «impara» senza maiuscole; il 3% contato dopo le spese di chiusura, e il fermo solo se dopo la chiusura il guadagno sul conto arriva al 3%; 27 novembre (riesame della sedicesima): centesimo sempre, limite in attesa annullato con la chiusura se si esegue, fermo tolto se il conto scende sotto il 3%, stato salvato prima della chiamata |
