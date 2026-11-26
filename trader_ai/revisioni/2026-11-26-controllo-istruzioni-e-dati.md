# Trader AI: istruzioni e dati del modello prima del riavvio

## 1. Risposta alla domanda del proprietario

**No, non ancora.** Le istruzioni hanno la forma che ha chiesto: sono corte e non danno consigli di strategia. Però i dati che il modello riceve a ogni chiamata lo ingannano. Un ordine limite non ancora eseguito gli arriva come «operazione aperta» con un guadagno che non esiste: è successo in 19 chiamate su 104, e il modello ci ha creduto tutte le volte. Le uscite delle sue operazioni in memoria sono sbagliate, e un'operazione persa manca del tutto.

Gli mancano anche i fatti per imparare da ogni operazione: dov'era lo stop all'inizio e quante volte l'ha spostato, quanto è costata, quanto è durata. Le sue lezioni spariscono dalla memoria dopo circa due ore e mezza. Il budget scritto in dollari gli fa credere che aspettare faccia risparmiare. E noi non vediamo il suo ragionamento.

Con le correzioni qui sotto, da fare prima del riavvio, la risposta diventa sì. Restano da misurare due cose: quanto ragiona a sforzo alto e se 5 dollari bastano per un giorno intero.

## 2. Da correggere prima del riavvio

Le voci 2.1, 2.2, 2.4, 2.5 e 2.10 toccano il percorso degli ordini del trader (`avvio.py`, `limiti.py`, `conto_simulato.py`). Servono quindi la revisione, come per le altre modifiche (`REGOLE.md` §8, `trader_ai/revisioni/`), e l'ok del proprietario per il riavvio. I test vanno in `trader_ai/tests/`.

### 2.1 [Alto] Un ordine limite in attesa arriva come «operazione aperta» con un guadagno finto, e la «modifica» accetta stop dalla parte sbagliata del limite

**Problema.**
- `Trader._conto` (avvio.py:251-252) trasforma l'ordine in attesa in una `Posizione` con l'entrata uguale al prezzo limite.
- `messaggio.blocco_conto` (messaggio.py:47-50) la scrive come «operazione aperta … risultato ±X USDT».
- Finché è in attesa, il limite sta dalla parte buona del prezzo; altrimenti si esegue subito (conto_simulato.py:344-345). Quel risultato è quindi quasi sempre positivo.
- Quando il limite si esegue (avvio.py:177-178 e 326-327) non restano né un evento né l'ora.
- `limiti.controlla` controlla lo stop di una «modifica» contro il prezzo di adesso (limiti.py:98-99). All'apertura invece lo controlla contro il limite (limiti.py:86-89).
- Le istruzioni non dicono come si esegue un limite (istruzioni.md:15-21).

**Prova.** Fonti: diario.jsonl, con le esecuzioni prese da `conto_simulato.json`. Script: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_prompt/v1_limiti.py e /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_apprendimento/attesa.py.
- 13 aperture su 15 sono a limite.
- In 19 chiamate su 104 un limite non eseguito appare come aperto. Una di queste, alle 22:00:06, cade nel minuto stesso dell'esecuzione. In tutte e 19 il diario lo tratta come una posizione viva.
- 13 delle 22 «modifica» riguardano ordini non eseguiti.
- 14:45: «Il corto da 58450 è a +43», con il conto fermo.
- 19:15: «Chiudo a mercato e incasso», su un lungo a 59.050 mai eseguito (risultato mostrato +12,83). In realtà era un annullamento.
- 19:30: «non era mai stato eseguito … Lo verifico sempre dal conto». Con questa nota ancora in memoria, alle 21:15 scrive «il limite a 60120 è stato eseguito»; l'esecuzione è arrivata alle 22:00.
- 5 operazioni hanno avuto lo stop avvicinato prima dell'esecuzione (11:48, 15:01, 15:34, 22:00 e 00:41 del 26).
  - All'esecuzione lo stop stava a 0,08-0,43 volte l'ATR da 15 minuti (ATR15), contro 0,63-1,12 delle altre operazioni.
  - Si sono chiuse in 0-11 minuti (mediana 3).
  - Il loro netto è −22,75 su −59,86 totali. È il loro risultato, non un danno calcolato.
- 6 «modifica» sono state accettate con lo stop dalla parte sbagliata del limite:
  - alle 14:45, corto a 58.450 con stop 57.720;
  - dalle 17:45 alle 19:00, lungo a 59.050 con stop da 59.200 a 59.590.
- Nel simulatore uno stop così scatta nel minuto dell'esecuzione, al prezzo d'apertura del minuto (conto_simulato.py:202 e 229-231). Ne esce un risultato impossibile.

**Correzione.**
- `limiti.Posizione`: due campi nuovi, `in_attesa` (falso di base) e `messo` (ora dell'ordine), riempiti in `_conto`.
- `messaggio.blocco_conto` con `in_attesa`: niente «operazione aperta» e niente «risultato». Per esempio: «ordine limite IN ATTESA, non eseguito, nessuna posizione: corto 0,04 BTC a 58450 (valore 2.338, margine 468 bloccato), messo alle 14:09 (36 min fa); prezzo ora 57368; stop 58520 e obiettivo 57700 lavorano solo dall'esecuzione; «chiudi» lo annulla».
- `passo` (righe 177-178) e `_esegui` (righe 326-327):
  - evento «ordine limite eseguito»;
  - `st['aperta']['eseguita']` con l'ora vera (simulatore: `aperta_ms`; demo: `updateTime`);
  - la riga della posizione dice «eseguita alle HH:MM».
- `limiti.controlla`, ramo «modifica» con `in_attesa`:
  - lo stop va dalla parte giusta del prezzo limite ed entro 0,9/leva da esso;
  - l'obiettivo va dall'altra parte del limite;
  - restano anche i controlli sul prezzo di adesso.
- Se il modello prova ad aprire con un limite già in attesa, lo scarto deve dire «c'è un ordine limite in attesa: annullalo con chiudi». Oggi dice «c'è già un'operazione aperta» (limiti.py:75-76).
- Test in `test_avvio.py`:
  - con un limite in attesa il messaggio non contiene né «operazione aperta» né «risultato»;
  - la modifica delle 14:45 viene scartata.

### 2.2 [Alto] Un limite eseguito e chiuso fra due controlli sparisce, e può lasciare uno stop orfano che chiude l'operazione dopo

**Problema.**
- avvio.py:170-174 mette `aperta` a None e scrive solo «ordine limite non più aperto». Non chiama `_registra_chiusura` e non imposta `chiusa`, quindi il modello non viene chiamato subito (sveglia.py:18-19). Non chiama nemmeno `annulla_tutto`.
- Se intanto il modello ha risposto «modifica», `_esegui` (avvio.py:391-404) mette sul conto uno stop senza posizione.
- `ContoSimulato._candela` poi sceglie lo stop più vicino senza guardare il lato (conto_simulato.py:214-215).

**Prova.**
- `conto_simulato.json` ha 14 posizioni chiuse, `stato.json` solo 13 operazioni.
- Manca il corto a 58.450 eseguito e fermato nel minuto delle 15:01. Movimenti delle 15:02:06: −0,4676, −3,0341 (a 58.525,85) e −1,1705; in tutto −4,67.
- Il resoconto del 25 dice 10 operazioni e −48,93. Il conto invece è passato da 1.000 a 946,39 (−53,61): le operazioni erano 11, di cui 10 perse.
- La chiamata successiva è arrivata solo alle 15:15, come «candela chiusa».
- Il difetto era già noto come problema 123, aperto e classificato «Basso» (`trader_ai/revisioni/2026-11-23-terza.md:54`). Ora è successo davvero.
- Ho rilanciato la prova con il codice vero e un mercato finto (/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/avv_incentivi/prova_stop_rimasto.py). Lo stop di un lungo a 89.200, rimasto sul conto, chiude «allo stop» a 90.009 il corto aperto dopo, che aveva il suo stop a 90.500. Succede in un minuto tranquillo.

**Correzione.**
- Un metodo nuovo, uguale nei due conti perché l'interfaccia è comune (conto_simulato.py:24). Per esempio `esito_ordine(cid)`, che restituisce entrata, quantità, ora di esecuzione, ora e prezzo d'uscita, modo e spese, oppure None se l'ordine non si è mai eseguito.
  - Simulatore: salvare `cid`, `uscita` e `come` nella posizione (`_apri_posizione` e `_chiudi_posizione`, conto_simulato.py:258-277).
  - Demo: `GET /fapi/v1/order` con `origClientOrderId`, più gli scambi di chiusura.
- avvio.py:171-174:
  - se l'ordine si è eseguito, chiamare `_registra_chiusura` con i dati del conto («eseguito e chiuso fra due controlli») e impostare `chiusa`;
  - in ogni caso chiamare `annulla_tutto`.
- Lo stesso controllo va fatto in `_esegui` prima di una «modifica», e nel ramo «chiudi» senza posizione (avvio.py:385-386). Oggi quel ramo scriverebbe «annullato dal modello».
- conto_simulato.py:214: contare solo gli stop con `lato` uguale a quello della posizione (il campo c'è già, riga 368).
- Test: un limite eseguito e fermato nello stesso minuto deve comparire in memoria, nel bilancio e nel resoconto, e nessuno stop deve restare sul conto.

### 2.3 [Alto, spesa] La cache da 5 minuti si riscrive a ogni chiamata (fatto già noto, qui con i numeri)

**Problema.** modello.py:43 usa la cache da 5 minuti, ma le chiamate arrivano ogni 15.

**Prova.**
- Su 104 chiamate ci sono state 100 scritture e 4 letture, da 1.849 token l'una.
- La cache è costata 0,92 $, più che senza cache (0,77 $).
- La skill claude-api (`shared/prompt-caching.md:144-153`) dice:
  - la scrittura da 1 ora costa il doppio dell'entrata (8 $/M su Opus 5.5);
  - la lettura costa 0,20 $/M e ogni lettura rinnova il timer;
  - con 5-60 minuti fra le chiamate la cache giusta è quella da 1 ora.

**Correzione.**
- modello.py:43: `"cache_control": {"type": "ephemeral", "ttl": "1h"}`.
- `costi.costo_dollari`: scritture da 5 minuti a 5,00 e da 1 ora a 8,00, lette da `usage["cache_creation"]` (`ephemeral_5m_input_tokens` ed `ephemeral_1h_input_tokens`). `cache_creation_input_tokens` è la loro somma e non va contato due volte.
- `costo_massimo`: la parte fissa a 8,00.
- Il commento di costi.py:23-24 va corretto: si misurano circa 1,8 caratteri per token, non 2,5-3.
- Un test con un usage finto.
- Dopo il riavvio, controllare che `cache_read_input_tokens` sia circa 2.000 a ogni chiamata dopo la prima.
- Anche l'eventuale secondo blocco in cache (sezione 6) va a 1 ora: le voci da 1 ora devono venire prima di quelle da 5 minuti (`shared/prompt-caching.md:172`).

### 2.4 [Medio] Le uscite in memoria e nel resoconto sono sbagliate (fatto già noto, qui con i numeri)

**Problema.**
- `_registra_chiusura` (avvio.py:265-273) scrive come uscita il prezzo mark del momento in cui il programma se ne accorge.
- Il «come» lo indovina con una tolleranza dello 0,3%.
- La stessa uscita finisce nel resoconto (avvio.py:525-526).

**Prova.** Script: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_dati/script/uscite_mie.py.
- Errore medio 48 USDT per BTC, massimo 168.
- Nel conto le 12 uscite allo stop sono tutte allo stop ±0,01%. In memoria, invece, 5 su 11 sono mostrate dalla parte impossibile dello stop. Esempio: corto delle 15:45 con stop a 58.950, uscita mostrata 58.804,65.
- Il modello ne ricava lezioni false:
  - 08:30: «uscita a 59124 contro lo stop a 59010» (vera 59.015,90);
  - 02:53 del 26: «scattato a 60760 con slittamento» (vera 60.788,92).

**Correzione.**
- `_registra_chiusura` prende uscita, «come», ore e spese da `esito_ordine` (punto 2.2).
- Correggere le 13 righe di `stato.json` e aggiungere l'operazione delle 15:01. Va fatto sulla copia della macchina (`TRADER_AI_DATI`, avvio.py:41-42), a servizio fermo. Non sulla copia del repository, perché `salva.sh` fa il rebase.

### 2.5 [Medio] Decisioni non eseguite di cui il modello non sa niente

**Problema.**
- (a) `schema.Risposta` mette `max_length` (schema.py:20, 22 e 23), ma l'API non lo applica: l'SDK lo sposta nella descrizione. `messages.parse` lo controlla solo dopo, con pydantic. Così un diario di 601 caratteri diventa «fuori_schema» (modello.py:48-49), senza token:
  - la decisione si butta;
  - dal tetto resta scalato il costo massimo, circa 0,37 $ (giro.py:41).
- (b) Con un esito diverso da «ok» (fuori schema, tagliata, rifiuto, errore), `ultimo_scarto` resta vuoto (avvio.py:228). Alla chiamata dopo il modello crede che la sua decisione sia stata eseguita.
- (c) avvio.py:240 scrive «Binance ha rifiutato» anche per gli scarti decisi dal programma (avvio.py:333 e 341).

**Prova.**
- Provato in locale con anthropic 2.12.0, la versione di `requirements.txt`: 600 caratteri accettati, 601 ValidationError (/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_prompt/v5_sdk_lunghezza.py).
- Finora 0 casi: i diari vanno da 385 a 566 caratteri. Ma erano tutte chiamate a sforzo medium.
- A sforzo alto con 16.000 token cresce anche il rischio di risposte «troncata».

**Correzione.**
- schema.py: togliere `max_length`. Lasciare «circa 600, 300 e 200 caratteri» nelle descrizioni e tagliare nel codice quando si salva la nota (avvio.py:234).
- avvio.py, dopo `decidi`: con un esito diverso da «ok», `ultimo_scarto = "la tua risposta delle HH:MM non è stata letta (<motivo>): nessuna azione eseguita"`.
- avvio.py:240: «rifiutata dal programma: …» quando il motivo non viene da Binance.

### 2.6 [Medio] Il resoconto del giorno ha il risultato sbagliato e non ha le misure promesse

**Problema.**
- `Trader.resoconto` (avvio.py:513-530) somma le operazioni registrate.
- Come «Conto a mezzanotte» scrive il conto di inizio giorno, perché viene chiamato prima di aggiornarlo (avvio.py:156-158).
- `REGOLE.md:98-105` promette misure che il resoconto non ha: l'ora dell'obiettivo, il motivo del modello, la discesa massima, il risultato meno il costo delle chiamate, il confronto con il solo BTC tenuto, leva e margine con il giorno in perdita e in guadagno.

**Prova.**
- `resoconti/2026-11-25.md` dice −48,93.
- Il conto è sceso da 1.000 a 946,39 (−53,61; −5,75% togliendo i 3,87 $ di chiamate).
- Negli stessi orari BTC (prezzo del diario) è salito da 58.634,7 (07:37) a 60.429,4 (00:00:30), cioè +3,06%.

**Correzione.** In `resoconto` aggiungere:
- conto a fine giorno e risultato presi dal conto;
- discesa massima;
- risultato meno il costo delle chiamate;
- BTC negli stessi orari;
- ora dell'obiettivo (da salvare insieme a `fermo_fino`);
- esiti per tipo e durata mediana (problema 184 della quattordicesima revisione);
- per ogni apertura: rischio allo stop in % del conto, leva, valore, quanto mancava al 3% e quante ore alla mezzanotte. È la misura del punto 5.2.

Servono solo al proprietario: al modello non va niente.

### 2.7 [Medio] Non si vede come ragiona, né quanto dura una chiamata

**Problema.**
- modello.py:40-47 non passa `thinking`. Su Opus 5.5 il ragionamento c'è sempre, ma di base torna vuoto («omitted»).
- giro.py:56-64 salva risposta e token, ma non la durata né il messaggio.
- Durata ed esiti nel resoconto li chiedeva già il problema 184 (`trader_ai/revisioni/2026-11-26-quattordicesima.md:47-52`).

**Prova.** Skill claude-api, sezione «Thinking & Effort»: `display: "summarized"` restituisce un riassunto leggibile, e il ragionamento si paga uguale con qualunque `display`.

**Correzione.**
- modello.py: `thinking={"type": "adaptive", "display": "summarized"}`.
- `giro.scrivi_diario`: aggiungere il riassunto del ragionamento e `durata_s`.
- Il messaggio intero va in un file al giorno sulla macchina (circa 1-2 MB al giorno, troppi per il diario che va nel repository ogni ora). Nel diario resta solo la sua impronta.

Senza questo, dopo il riavvio non si può dire se a sforzo alto «pensa davvero».

### 2.8 [Basso] Il VWAP del giorno ha tre valori diversi, e sul 5 minuti è sbagliato dopo le 16:40 UTC

**Problema.** indicatori.py:52-55 calcola il VWAP solo sulle candele ricevute: sono 199 chiuse, che sul 5 minuti coprono 16 ore e 35 minuti. In più ci mette la candela di ieri che chiude alle 00:00.

**Prova.**
- Nello stesso messaggio ci sono tre valori: 60.804,2, 60.805,6 e 60.798,2 (`messaggio_vero.txt:116,167,218`).
- Sul 5 minuti il VWAP mostrato arriva a 80 USDT sotto quello vero (alle 20:30 del 25), e lo scarto supera i 20 USDT in 35 chiamate.
- Il 26 alle 00:00 tutti e tre i valori erano di ieri.
- Il VWAP è citato in 69 risposte su 104, ma il prezzo è finito dalla parte sbagliata del VWAP solo in 2.

**Correzione.**
- Un solo «vwap del giorno UTC» nel blocco della moneta, calcolato sulle candele da 5 minuti aperte dopo la mezzanotte. Si può fare con `n=300` per il 5 minuti in avvio.py:218, oppure con `startTime` = mezzanotte in tutti e due i `candele`.
- «-» prima della prima candela del giorno.
- Toglierlo da `riassunto`.
- Test alle 00:00:30 e alle 20:00.

### 2.9 [Basso] Il «prezzo da mezzanotte» manca il giorno del riavvio, ed è falso dopo un riavvio

**Problema.** avvio.py:155-158 scrive il prezzo solo al cambio di giorno, e usa il prezzo del primo controllo dopo. Se il programma era spento, quel controllo può arrivare ore dopo la mezzanotte. Eppure istruzioni.md:8-9 promette questa riga a ogni chiamata.

**Prova.**
- `stato.json` non ha la chiave, e il messaggio ricostruito non ha la riga.
- La quattordicesima revisione lo ha accettato (punto 2), con il test mancante (problema 186).

**Correzione.**
- In `passo`, usare l'apertura della prima candela da 5 minuti del giorno UTC, che è già fra le candele scaricate; se manca, il comportamento di oggi.
- Test con uno stato senza la chiave.

### 2.10 [Basso] Dopo un suo «chiudi» il modello non viene richiamato

**Problema.**
- avvio.py:383-390 butta il valore di `_registra_chiusura`.
- `sveglia.motivo` (avvio.py:213) vede solo le chiusure delle righe 176 e 185.
- Invece istruzioni.md:12 dice «subito quando un'operazione si chiude», e la regola del proprietario è «appena il trade si chiude deve essere invocato» (`REGOLE.md:28-29`).

**Prova.** Il 25 il modello ha chiuso alle 13:00:13, alle 19:15:21 (un annullamento) e alle 20:00:01. Le chiamate successive sono arrivate alle 13:15:03, 19:30:11 e 20:15:25.

**Correzione.** In `_esegui`, dopo «chiudi» e dopo un annullamento, salvare nello stato il motivo «operazione chiusa (chiusa dal modello)» e passarlo a `sveglia.motivo` al passo dopo. Costa una chiamata in più per ogni chiusura del modello (3 in un giorno e mezzo).

## 3. Dati da aggiungere al messaggio

Regole comuni a tutte le voci:
- il codice li calcola da dati già scaricati o già nel conto;
- gli intervalli restano 5, 15 e 30 minuti;
- niente dati dell'altra sessione e nessun consiglio di strategia.

I caratteri in più sono stime. Fuori cache, 1.000 caratteri sono circa 550 token: circa 0,0022 $ a chiamata e 0,24 $ al giorno.

Unità usate negli esempi:
- «R» è la perdita prevista allo stop iniziale;
- «ATR15» è l'atr14 del 15 minuti, già presente nel messaggio.

### 3.1 [Alto] La scheda di ogni operazione chiusa

**Perché.**
- Oggi ogni operazione chiusa è una riga sola (messaggio.py:75-78): ora della decisione in formato ISO con i microsecondi, lato, leva, entrata, uscita sbagliata (2.4), «come» indovinato, risultato e approccio.
- Lo stop iniziale si perde alla prima modifica (avvio.py:404) e non entra nell'operazione (avvio.py:271-273).
- Le 14 posizioni eseguite si sono chiuse così:
  - 0 all'obiettivo;
  - 2 allo stop iniziale;
  - 10 a uno stop avvicinato dal modello, 5 delle quali sul guadagno finto del punto 2.1;
  - 2 chiuse dal modello.
- Il rapporto previsto fra obiettivo e stop era in media 2,14.
- Il corto delle 07:46 era arrivato a +1,12 R prima di chiudersi a −9,61.
- Con lo stop e l'obiettivo iniziali, il 25 sarebbe andato meglio di circa 27 USDT e il 26 peggio di 10-16 (stima su candele spot, /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_prompt/v4_controfattuale.py).
- Spostare lo stop ha quindi aiutato un giorno e danneggiato l'altro: al modello vanno mostrati i fatti, non giudizi.

**Forma.**
- In testa: «ultime 14: 0 all'obiettivo, 2 allo stop iniziale, 10 a uno stop spostato da te, 2 chiuse da te; durata mediana 24 min; spese 19,26 USDT».
- Le ultime 5 per intero, per esempio: «#1 25/11 07:46→08:29 (43') corto x10 val 3.475 | entrata 58890 | stop iniziale 59110 (0,37%, 0,85 ATR15) → 59010 (1 spostamento, più vicino) | obiettivo <prezzo> | uscita 59015,9 allo stop spostato | −9,61 netti (−0,74 R; spese 2,44; funding +0,25) | a favore +1,12 R, contro −0,74 R | motivo all'apertura: <i primi 200 caratteri del tuo diario> | approccio: <…>».
- Le altre senza motivo e approccio.

**Dove.**
- All'apertura (avvio.py:344-346) salvare:
  - stop e obiettivo iniziali;
  - l'ATR15, passato da `passo`, che ha le candele;
  - il motivo.
- A ogni «modifica» (avvio.py:404): aggiungere lo spostamento con la sua ora.
- Alla chiusura: uscita, ore, spese e funding da `esito_ordine` (punto 2.2).
- Massimo a favore e contro: dalle candele da 5 minuti già scaricate, chiuse dopo l'esecuzione. Per un limite si esclude il lato favorevole della candela dell'esecuzione.

**Caratteri.** Misurato su `stato.json` (/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/sintesi/righe.py):
- riga corta circa 260 caratteri, contro i 217 di oggi;
- scheda intera circa 640;
- in totale circa +2.500 caratteri con 13 operazioni e circa +3.200 con 30.

Conviene metterle nel blocco in cache (sezione 6).

### 3.2 [Alto] Spese, pareggio e netto in USDT

**Perché.**
- istruzioni.md:20 dà solo le percentuali, e messaggio.py:50 il risultato lordo.
- Nei movimenti del conto: commissioni −19,26, funding +0,32, prezzo −40,92. Le commissioni sono il 32% della perdita.
- Per andare in pari servivano 41-59 USD di prezzo a operazione.
- Le stime del modello erano sbagliate:
  - 14:00 «utile di circa 4 netti» → +2,53 (i 4,17 erano lordi);
  - 08:00 «taglio il rischio a ~7 USDT» → −9,61;
  - 26/11 alle 04:45 «circa 1 USDT» → −2,28, di cui 1,24 di spese.
- Il modello sa che le spese ci sono (09:45: «spese escluse»), ma le sottostima.

**Forma.** Nella posizione, e come valori «previsti» nell'ordine in attesa: «spese pagate 0,47; uscita a mercato stimata 1,17; pareggio netto 58.403; allo stop −7,10 netti; all'obiettivo +12,40 netti; se chiudi adesso +2,15 netti» (numeri d'esempio). Si calcolano dalle costanti di conto_simulato.py:40-48, senza scriverle a mano.

**Caratteri.** Circa +150.

### 3.3 [Medio] La posizione aperta con tempo, rischio e percorso

**Perché.**
- Oggi la riga della posizione (messaggio.py:47-50) non ha:
  - l'ora di esecuzione (avvio.py:344 salva l'ora dell'ordine, non quella dell'esecuzione);
  - valore e margine, che `REGOLE.md:67-68` promette;
  - lo stop iniziale e le distanze.
- In 18 chiamate su 23 con una posizione aperta, il modello rifà i conti a mano.

**Forma.** «posizione: corto 0,059 BTC, valore 3.475, margine 347, leva 10, eseguita alle 07:46 (14 min fa) | stop 59010 (iniziale 59110), dal prezzo 0,20% = 0,45 ATR15 | 1 R = 12,98 USDT | obiettivo … | liquidazione … | risultato +3,10 lordi, +0,95 netti | dall'esecuzione a favore +1,12 R, contro −0,30 R» (numeri d'esempio). Va sempre detto se una distanza si misura dal prezzo o dall'entrata.

**Caratteri.** Circa +200.

### 3.4 [Medio] Le lezioni che restano

**Perché.**
- avvio.py:229-234 salva l'approccio e solo le ultime 10 note, con l'ora ma senza la data.
- Il «perche» (schema.py:22) non torna mai al modello: il modello ne ha scritti 11, e nessuno è in `stato.json`.
- La nota più vecchia ancora in memoria ha in mediana 135 minuti.
- Esempi:
  - alle 17:05 il modello scrive come «perche»: «il range 57250-58970 con ATR 15m ~490 rende gli stop stretti inefficaci e quelli larghi troppo costosi». Non gli è mai tornato davanti, e la nota della stessa chiamata è uscita dalla memoria alle 19:45;
  - la nota delle 04:57, «Ho fatto troppe operazioni piccole in perdita, quindi riduco la frequenza», uscirà dopo 10 chiamate.
- L'effetto atteso è modesto, per due motivi:
  - l'errore ripetuto delle 21:15 è venuto dal messaggio (punto 2.1), non da una nota scaduta;
  - una lezione tratta da poche operazioni può essere sbagliata: il 26 stringere gli stop ha limitato le perdite.

**Forma.**
- Un blocco «le tue lezioni (scritte da te)» sopra le note, per esempio: «#4 25/11 17:05, giorno −47,9, dopo le operazioni 7-9: <testo>».
- Le ultime 10, al massimo 300 caratteri l'una, conservate anche nei giorni dopo; dentro anche i «perche».
- Note con la data e senza l'ora doppia: 60 diari su 104 cominciano già con l'ora.

**Caratteri.** Fino a +3.000.

### 3.5 [Medio] Le chiamate rimaste invece dei dollari

**Perché.**
- messaggio.py:92-93 dice solo «budget di chiamate rimasto oggi X dollari».
- 37 risposte su 104 citano il budget, per lo più come motivo per aspettare o per non toccare gli ordini:
  - 10:45: «Per risparmiare budget, preservo il capitale»;
  - 22:00: «Non tocco gli ordini per risparmiare budget»;
  - 22:12: «quasi finito … quindi aspetto», quando restavano 1,53 $ e solo 7 chiamate a mezzanotte;
  - 19:15: «Il budget delle chiamate è limitato. Chiudo a mercato e incasso».
- Il 25 sono avanzati 1,13 $.
- Le chiamate delle candele arrivano comunque (sveglia.py:15-24). Fra un «aspetta» (0,052 $) e un'apertura (0,058-0,062 $) c'è circa mezzo centesimo.

**Forma.**
- «chiamate rimaste oggi: circa 41, l'ultima verso le 18:20 UTC; poi niente fino a mezzanotte, e l'operazione aperta resta con il suo stop e il suo obiettivo» (esempio), oppure «bastano fino a mezzanotte».
- Calcolo:
  - N = (rimasto − costo massimo della prossima chiamata) / costo medio delle chiamate di oggi + 1;
  - alla prima chiamata del giorno si usa il costo medio di ieri;
  - ora dell'ultima = adesso + N × 15 minuti, scritta come «circa» perché le chiusure aggiungono chiamate.
- Alla prima chiamata dopo un tetto finito: «ieri non sei stato chiamato dalle HH:MM a mezzanotte».

**Caratteri.** Circa +60.

### 3.6 [Medio] Un bilancio con i fatti certi: oggi, ieri e dall'inizio

**Perché.**
- `bilancio_di_oggi` (messaggio.py:54-66) conta solo vinte e perse per lato e, solo per oggi, il prezzo da mezzanotte.
- Senza l'operazione sparita (punto 2.2), alle 17:05 avrebbe detto −43,26 mentre il conto diceva −47,94.
- Il capitale di partenza non compare da nessuna parte.
- Il 25 il modello ha cambiato lato dopo 9 corti, 8 dei quali persi (ne vedeva 7).
- La striscia di perdite più lunga è stata di 7 operazioni: dalle 15:01 alle 00:41 del 26, con 4 corti e 3 lunghi.

**Forma.**
- Per oggi, ieri e dall'inizio: «N operazioni, netto X (prezzo A, spese B, funding C); obiettivi N; uscite: stop iniziale N, stop spostato da te N, chiuse da te N, obiettivo N; perse di fila adesso N (lato), netto Y; prezzo dalla prima della striscia ±Z%».
- In più: «dall'inizio della prova (25/11, 1.000 USDT): −59,86 (−6,0%)».
- Niente etichette come «direzione sbagliata»: richiedono il senno di poi e un orizzonte fisso. Se serviranno, andranno definite prima in REGOLE.md.
- Le parti che dipendono dal prezzo di adesso restano fuori dal blocco in cache (sezione 6).

**Caratteri.** Circa +600.

### 3.7 [Medio] Il rumore del prezzo accanto agli stop

**Perché.**
- L'ATR compare solo in dollari (messaggio.py:34), lo stop solo come prezzo.
- Nelle 15 aperture lo stop iniziale stava in mediana allo 0,41%, cioè 0,77 ATR15 (1,43 ATR del 5 minuti, 0,60 del 30 minuti).
- Nelle 22 modifiche lo stop stava a 0,73 ATR15.
- 12 operazioni su 14 si sono chiuse allo stop, 6 entro 15 minuti.
- Dal 20 al 25/11 l'escursione giornaliera è andata dal 3,95% al 9,95% (5,46% il 25).
- Il modello sa fare il conto: alle 02:45 e alle 04:30 lo fa giusto in ATR del 5 minuti, alle 17:05 in ATR15. Ma non ha il dato davanti a ogni chiamata.

**Forma.**
- In ogni blocco degli indicatori: «atr14 221 (0,37%), ampiezza mediana delle ultime 20 candele X (Y%)».
- Una riga «escursione: ieri 5,46% (57300-60568), oggi finora 2,06%», calcolata dalle 200 candele da 30 minuti.
- Nella posizione e nell'ordine in attesa: la distanza di stop e obiettivo in % e in ATR dei tre intervalli.

**Caratteri.** Circa +300.

### 3.8 [Medio] La candela in corso

**Perché.**
- Le candele non ancora chiuse si buttano (conto_simulato.py:283-286, conto_demo.py:125-132, messaggio.py:17-19).
- 7 delle 11 chiamate arrivate dopo uno stop sono cadute 2-4 minuti dentro la candela da 5 minuti.
- Il 25, alle 14:09, 15:37 e 16:22, c'erano rispettivamente 4, 2 e 2 minuti già chiusi che il modello non vedeva, con escursioni di 319, 469 e 455 USDT. Alle 16:21 il massimo di 58.971,5 ha preso lo stop a 58.950.
- Fonti: candele da 1 minuto dei future da data.binance.vision (/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/critico/scarichi/k/BTCUSDT-1m-2026-11-25.csv); calcolo in /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/sintesi/verifica.py.
- Nelle chiamate dei :15 e dei :45 la candela da 30 minuti è a metà. Il modello lo scrive alle 17:15 e alle 19:45: «la 30m non ha ancora chiuso».

**Forma.**
- Per ogni intervallo: «in corso (aperta alle 16:20, da 2 min): apertura, massimo, minimo, ultimo, volume finora».
- Gli indicatori restano calcolati sulle candele chiuse.
- La candela in corso arriva già nella risposta di Binance: nessuna richiesta in più.
- Aggiornare REGOLE.md:66 e messaggio.py:2: «solo candele chiuse» è una regola della sessione, non del proprietario.

**Caratteri.** Circa +200.

### 3.9 [Medio] I livelli dei giorni prima e l'andamento degli indicatori

**Perché.**
- Si scaricano 200 candele (avvio.py:218, conto_simulato.py:280), ma se ne mostrano 48 (messaggio.py:14): sul 30 minuti sono solo 24 ore.
- Alle 07:28 del 26 restavano fuori i massimi del 24/11 (61.682) e del 23/11 (64.603). La parola «ieri» compare in 3 risposte su 104.
- Ogni indicatore è un valore solo (messaggio.py:34). Su 19 frasi del modello sul MACD, 5 sono contrarie ai numeri. Esempio, 14:15: «istogramma in calo su tutti i timeframe», mentre sul 5 minuti saliva da −48 a −30 (/tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_avversario/pendenze.py).

**Forma.**
- «## livelli (dalle candele da 30 minuti): oggi min–max; ieri min–max; ultime 100 ore min–max; prezzo a −X% dal massimo di oggi».
- In ogni blocco degli indicatori gli ultimi 4 valori di rsi14, istogramma MACD e volume/media, arrotondati.

**Caratteri.** Circa +500.

### 3.10 [Basso] Funding, interesse aperto, premio e prezzo mark, leggibili

**Perché.**
- messaggio.py:94 stampa coppie chiave-valore a 6 cifre: il funding esce come «7.217e-05».
- `mercato()` butta `indexPrice`, che pure arriva nella stessa risposta di premiumIndex (conto_simulato.py:89-93, conto_demo.py:137-141).
- L'interesse aperto è citato in 0 risposte, il funding in 5.
- Alle 07:45 e alle 09:15 il funding positivo è fra i motivi di due corti, poi persi. Ma il funding stava sotto il livello base dello 0,01%, e il premio del perpetuo sull'indice era −5,3 e −4,8 punti base (mediana del 25: −4,3; premi a 5 minuti in /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/critico/scarichi/p/BTCUSDT-5m-2026-11-25.csv).

**Forma.**
- «prezzo (mark) 60518,8: stop, obiettivo e liquidazione scattano su questo; le candele sono del prezzo degli scambi | funding +0,0072% (positivo: i lunghi pagano i corti; livello base 0,0100%), prossimo fra 200 min, sulla tua posizione +0,25 | premio sull'indice −4,3 punti base | interesse aperto 96.517 BTC, variazione in 1 h e in 4 h».
- La storia dell'interesse aperto va presa da `/futures/data/openInterestHist` (pubblico, stesso host), invece di allungare `st['oi']` (avvio.py:188), che salva un punto ogni 30 secondi.

**Caratteri.** Circa +150.

### 3.11 [Basso] L'ora del giorno e il calendario

**Perché.**
- Il messaggio dà solo l'ora UTC (messaggio.py:92), e nessuna delle 104 risposte parla di sessioni di borsa o di calendario.
- Dal 20 al 25/11 l'ampiezza mediana di una candela da 30 minuti è stata dell'1,04% fra le 13 e le 17 UTC, e dello 0,58% fra le 0 e le 13.
- Le 5 vendite del 25 aperte fra le 13:45 e le 16:45 fanno −23,54, il 44% della perdita del giorno. È un fatto, non la prova che la causa sia l'ora: era anche un giorno in salita.
- Il 26/11 è il Ringraziamento.

**Forma.**
- «fascia 13-17 UTC (Europa e USA): ampiezza mediana di una 30m nelle ultime 100 ore 1,0%, nel resto 0,6%; oggi festivo USA; orari fissi: 13:30 dati USA (non tutti i giorni), 14:30 apertura di Wall Street, funding alle 00, 08 e 16».
- Festivi e cambio dell'ora in una tabella dentro `trader_ai/`, da aggiornare ogni anno. Nessuna notizia.

**Caratteri.** Circa +200.

### 3.12 [Basso] Acquisti e vendite aggressive

**Perché.**
- Il campo 9 delle candele di Binance (gli acquisti aggressivi) si butta (conto_simulato.py:287-288, conto_demo.py:133-134).
- Il volume è citato in 91 risposte su 104.
- Non c'è prova che questo dato avrebbe cambiato una decisione: va fatto per ultimo.

**Forma.** Una colonna «acq%» nelle candele e, per ogni intervallo, il saldo dalla mezzanotte.

**Caratteri.** Circa +600.

## 4. Istruzioni da cambiare

Si aggiungono solo meccanica del programma, spese, memoria e formato, cioè i contenuti che REGOLE.md:60-62 ammette. Nessun consiglio di strategia. Il testo del proprietario sull'obiettivo (istruzioni.md:4-6) resta com'è (vedi 5.2). In tutto il system si allunga di circa 1.500 caratteri. Va segnata la versione 7 in REGOLE.md §9.

**4.1 Chiamate e tetto.** Sostituisce la prima frase di istruzioni.md:12 e la seconda di istruzioni.md:20-21:
> Vieni chiamato a ogni candela da 15 minuti chiusa, qualunque cosa decidi, e subito quando un'operazione si chiude, anche quando la chiudi tu: aspettare, tenere, modificare o chiudere non fa risparmiare chiamate. Il tetto di 5 dollari al giorno lo conta il programma: il messaggio ti dice quante chiamate restano e a che ora arriverà l'ultima; dopo non vieni chiamato fino a mezzanotte UTC e l'operazione aperta resta solo con il suo stop e il suo obiettivo.

Prova: punti 3.5 e 2.10. «anche quando la chiudi tu» vale solo con la correzione 2.10. Senza quella correzione si scrive: «dopo un tuo chiudi la chiamata arriva alla candela dopo».

**4.2 Come vengono eseguiti gli ordini.** Va dopo istruzioni.md:18 e sostituisce il minimo di istruzioni.md:16:
> - il «prezzo» del messaggio è il prezzo mark: stop, obiettivo e liquidazione scattano su quello; le candele sono del prezzo degli scambi;
> - un ordine limite si esegue solo quando il prezzo degli scambi va oltre il limite (toccarlo non basta), dal minuto dopo l'invio, e non scade; un limite già oltre il prezzo si esegue subito a mercato. Finché è in attesa non hai una posizione né un risultato: stop e obiettivo lavorano dall'esecuzione, «chiudi» lo annulla, e il suo prezzo non si può spostare (lo annulli e lo rimetti alla chiamata dopo);
> - «modifica» cambia solo stop e obiettivo; stop, obiettivo e «chiudi» escono sempre a mercato;
> - la leva è un numero intero; la quantità si arrotonda per difetto a 0,001 BTC: servono almeno 0,002 BTC (circa 120 USDT di valore a 60.000).

Prova:
- punto 2.1;
- conto_simulato.py:193-195 e 344-346;
- avvio.py:336 (`int(r.leva)`), 339-341 e 391-405;
- il valore eseguito è stato fra −0,1% e −6,6% di quello deciso (alle 17:30, 885 → 827 USDT).

«Toccarlo non basta» vale per il simulatore: se si passa al conto demo, la riga va riscritta.

**4.3 Spese.** Sostituisce la prima frase di istruzioni.md:20:
> Spese: 0,05% del valore a ogni esecuzione a mercato, 0,02% con ordine limite, più uno scarto di prezzo dello 0,01% a ogni esecuzione a mercato, più il funding. Andata e ritorno costa circa lo 0,12% del valore a mercato e lo 0,08% con entrata a limite. Il messaggio ti dà in USDT le spese, il pareggio e il netto allo stop e all'obiettivo.

Prova: punto 3.2; conto_simulato.py:230, 235, 273, 346 e 391.

**4.4 Imparare.** Va dopo istruzioni.md:10. Il bilancio descritto in istruzioni.md:8-9 va aggiornato al punto 3.6.
> La tua memoria: le operazioni chiuse con i loro fatti (stop iniziale e spostamenti, spese, durata, quanto il prezzo è andato a favore e contro); le tue lezioni (le ultime 10, con data e operazioni, restano anche nei giorni dopo); le tue note (solo le ultime 10 chiamate). Quando sei chiamato per un'operazione chiusa, scrivi nel campo `lezione` che cosa avevi previsto, che cosa è successo e che cosa cambi; se i fatti smentiscono una lezione di prima, scrivilo.

Nel codice:
- schema.py: `lezione: Optional[str] = Field(None, description="cosa hai capito; da scrivere quando il motivo è un'operazione chiusa; circa 300 caratteri")`.
- avvio.py la salva in `st['lezioni']` con data, ora, operazione e risultato del giorno, insieme al `perche`.

Prova: punto 3.4.

**4.5 Formato della risposta** (istruzioni.md:23-24 e schema.py).
- `approccio`: «il tuo metodo in una frase, senza i livelli di oggi (quelli vanno nel diario)».
  - Oggi 87 approcci su 104 contengono prezzi.
  - Il testo cambia in 58 passaggi su 103, ma `cambio_approccio` è vero solo 11 volte. Per questo il conteggio dei cambi (avvio.py:231-232, nel resoconto) non misura niente.
- `tipo_ordine` e `prezzo_limite` oggi sono senza descrizione (schema.py:18-19). Aggiungere: «prezzo_limite: solo con tipo_ordine "limite"».
- `limiti.controlla` deve scartare, scrivendo il motivo:
  - «prezzo_limite senza tipo_ordine limite»: oggi l'ordine parte a mercato (limiti.py:86);
  - «leva non intera»: oggi viene troncata (avvio.py:336).
  - Nessuno dei due è mai successo nelle 104 risposte: è un rischio, non un danno visto.
- `diario`, `perche`, `approccio`: «circa 600, 300 e 200 caratteri», senza `max_length` (punto 2.5).

## 5. Decisioni del proprietario

**5.1 I 5 dollari al giorno non bastano per tutta la giornata.**
- Già con il ragionamento corto di prima, le chiamate sarebbero finite verso le 18:30 UTC (le 19:30 in Svizzera): nella sola notte del 26 ha speso 1,76 dollari in 7 ore.
- Con il ragionamento più lungo che ha chiesto finiranno prima. Quanto prima, lo dirà solo il primo giorno.
- Dopo, niente chiamate fino a mezzanotte. Questo va contro «non si deve fermare prima del 3%».
- Le correzioni gratuite della sezione 6 recuperano circa un quinto del tetto.

Le scelte possibili:
- (a) tenere 5 dollari e decidere con il numero del primo giorno. È quella consigliata.
- (b) alzare il tetto.
- (c) chiamarlo meno spesso quando non ha niente aperto, per esempio ogni 30 minuti, o quando il prezzo tocca livelli scelti da lui. Oggi 63 chiamate su 104 avvengono senza niente aperto, e il 44% della spesa va in risposte «aspetto». Questa scelta cambia il ritmo che ha deciso lui.

**5.2 «OBIETTIVO OBBLIGATORIO» scritto in maiuscolo, senza una perdita massima.**
- Il rischio: per arrivare al 3% a ogni costo, il modello può forzare operazioni o ingrandirle dopo le perdite.
- Finora non è successo. Con il testo vecchio, dopo le perdite ha ridotto il rischio solo a fine giornata: circa l'1% del conto per operazione fino alle 15:45, circa lo 0,5-0,6% dalle 16:45. Con il testo nuovo non ci sono ancora dati.
- La guida di Anthropic dice che, sui modelli di oggi, il testo troppo enfatico fa applicare una regola più del dovuto (skill claude-api, `shared/prompt-audit.md:60-62`).

La proposta:
- stessa sostanza, senza maiuscole («Obiettivo obbligatorio di ogni giorno: guadagnare il 3% del conto della mezzanotte UTC. Non è un tetto: finché non l'hai raggiunto continui a cercare operazioni per arrivarci…»), e lo stesso per «IMPARA DAI TUOI RISULTATI». Solo con il suo sì.
- Intanto si misura ogni giorno (punto 2.6).
- La frase «non alzare leva o margine per recuperare» l'ha fatta togliere lui il 23/11 (commit b271c28): si rimette solo se la chiede.

**5.3 Il 3% si conta prima delle spese di chiusura** (limiti.py:42-43 sul conto lordo; conto_simulato.py:300-311).
- La differenza è piccola: sulle operazioni viste va da 0,5 a 2,1 USDT, cioè dal 2 al 7% dell'obiettivo. Con tutto il conto a leva 10 arriverebbe a circa il 20%.
- Domanda: il 3% lo vuole al netto delle spese? La risposta cambia il momento in cui il programma chiude tutto.
- Intanto il modello vede la riga «se chiudi adesso: +X netti» (punto 3.2).

**5.4 Il riavvio.**
- Le correzioni della sezione 2 toccano il percorso degli ordini del trader: prima le rilegge chi controlla gli ordini, poi serve il suo ok per riaccendere.
- Nello stesso fermo si correggono sulla macchina le 13 uscite sbagliate e si aggiunge l'operazione mancante delle 15:01 (punto 2.4).

## 6. Effetto sui costi

**Base misurata** (sforzo medium, messaggio vecchio; /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/sintesi/verifica.py):
- 104 chiamate, 5,63 $ in 23,4 ore, cioè 0,0541 $ a chiamata (entrata 0,0339, cache 0,0089, uscita 0,0113).
- 25/11: 72 chiamate, 3,87 $ (dalle 07:37 alle 23:45).
- 26/11 dalle 00:00 alle 07:00: 32 chiamate, 1,76 $ (0,25 $ all'ora).
- Un giorno intero fa circa 107 chiamate (96 candele più circa 11 chiusure), cioè circa 5,8 $.
- Si possono spendere circa 4,63 $, perché il programma chiama solo se resta il costo massimo di una chiamata, 0,367 $ (costi.py:38-42 e 68-70). Allo stesso ritmo le chiamate finirebbero verso le 18:30 UTC.

**Prezzi di Opus 5.5** (skill claude-api; costi.py:16-17): entrata 4 $/M, uscita 20 $/M, scrittura in cache 5 $/M (5 minuti) o 8 $/M (1 ora), lettura 0,20 $/M. Il messaggio ha circa 1,8 caratteri per token: alle 07:00 del 26, 9.287 token per circa 16.600 caratteri.

| Voce | Effetto al giorno (circa 107 chiamate) |
|---|---|
| Cache da 1 ora sul system (2.3) | −0,87 $ sulle 104 chiamate misurate (circa −1,0 $ con il system attuale, più lungo) |
| Candele compatte: ora senza data salvo al cambio di giorno, prezzi interi (errore massimo 0,5 USDT), volume a 3 cifre, indicatori arrotondati; da 8.014 a 5.988 caratteri (−25%) | circa −0,54 $ (stima, da misurare con `count_tokens`, che è gratuito) |
| Memoria stabile (operazioni chiuse, lezioni, bilancio dei chiusi) in un secondo blocco in cache da 1 ora, in testa al messaggio: cambia solo alle chiusure | oggi la lista costa circa 0,67 $ fuori cache. Con 3.1, 3.4 e 3.6 (circa +6.100 caratteri) costerebbe circa 2,1 $ fuori cache e circa 0,7 $ in cache (circa 15 riscritture al giorno): circa +0,03 $. Con 30 operazioni: 1,55 $ la lista di oggi fuori cache, circa 1,05 $ il blocco nuovo in cache |
| Altri dati nuovi fuori cache (3.2, 3.3, 3.5 e da 3.7 a 3.10: circa +1.500 caratteri) | circa +0,36 $ (3.11 e 3.12 aggiungerebbero circa +0,19 $) |
| Istruzioni più lunghe (circa +1.500 caratteri nel system, in cache) | circa +0,03 $ |
| Chiamata dopo un «chiudi» del modello (2.10) | circa +0,1 $ |
| Riassunto del ragionamento (2.7) | 0: il ragionamento si paga uguale |
| **Totale, a parità di ragionamento** | **circa −0,9 $: da 0,054 a circa 0,046 $ a chiamata (stima)** |

Senza il secondo blocco in cache, le aggiunte costano circa +1,8 $ al giorno e il totale sale a circa +0,5 $ rispetto a oggi (0,059 $ a chiamata).

**Lo sforzo alto non è ancora misurato.** Tutte le 104 chiamate sono a medium, con circa 200 token di ragionamento in media. Ogni 1.000 token di ragionamento in più a chiamata costano 0,02 $, cioè circa 2,1 $ al giorno.

Fino a che ora durerebbero le chiamate (stima, 4,5 chiamate all'ora):

| Ragionamento medio a chiamata | Con le correzioni | Senza le correzioni |
|---|---|---|
| 200 token | fino alle 23 circa | — |
| 1.000 token | fino alle 17 circa | verso le 15 |
| 2.000 token | fino alle 13 circa | verso le 11:30 |
| 3.000 token | fino alle 10 circa | — |

Il numero vero va misurato nelle prime 20 chiamate dopo il riavvio: `usage.output_tokens_details`, costo, durata ed esiti «troncata». Va scritto in REGOLE.md §3, come chiede REGOLE.md:56-57, e portato al proprietario per la scelta 5.1. Le correzioni della sezione 2 non cambiano la spesa, salvo la 2.10.

**Fonti dei numeri.** Non ho modificato nessun file del repository. I numeri vengono da questi file:
- costi per giorno, ritardo delle chiamate dopo uno stop, chiusure del modello (rifatti da me): /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/sintesi/verifica.py
- lunghezza delle righe proposte (rifatta da me): /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/sintesi/righe.py
- stop orfano (rilanciato da me): /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/avv_incentivi/prova_stop_rimasto.py
- ordini in attesa: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_prompt/v1_limiti.py e /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_apprendimento/attesa.py
- uscite e operazione sparita: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_dati/script/uscite_mie.py
- R, spese e uscite per tipo: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_apprendimento/operazioni.py
- cache e costi: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_prompt/v2_costi.py
- candele compatte: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/avv_costi/sezioni.py
- proiezioni del tetto: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/lente_costi/proiezione.py
- conteggi sui testi del diario: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_prompt/v6_testi.py
- ATR e livelli su candele spot: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_avversario/candele_analisi.py
- VWAP: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/verifica_prompt/v3_vwap.py
- messaggio ricostruito: /tmp/claude-0/-home-user-agentic-trading-system/3e86fc2d-e676-5e8c-aab8-125249da6bfe/scratchpad/messaggio_vero.txt