# Le regole del trader AI (versione 2, 23 novembre 2026, prima di ogni chiamata al modello)

Il proprietario, 23 novembre 2026, sulla versione 1: «stai sbagliando approccio, chi ti ha detto ogni 4 ore e 12 monete?». Nessuno:
erano esempi del messaggio di avvio diventati regole. **Da qui il modello sceglie da solo quali monete guardare, quando guardarle di
nuovo, quando entrare e quando uscire.** Il codice fissa solo i limiti di rischio, il tetto di spesa e i dati che gli passa.
Decisione del proprietario del 23 novembre (`docs/decisioni_del_proprietario.md`): conto demo di Binance suo (1.000 USDT, separato da
G1), Claude Opus 5.5, tetto di 5 euro al giorno nel codice, gira sulla macchina.

## 1. Cosa fa
Il modello riceve una panoramica di **tutti** i perpetui in USDT di Binance, il dettaglio delle monete che ha chiesto di seguire, il suo
portafoglio e quanto budget gli resta; risponde con decisioni strutturate e dice **lui** quando vuole essere richiamato e a quali prezzi
vuole essere svegliato. Il codice controlla i limiti e manda gli ordini **solo sul conto demo suo**.

## 2. Il modello e il tetto di spesa
* `claude-opus-5-5` (decisione del proprietario), SDK Python ufficiale `anthropic`, pensiero adattivo (sempre acceso), sforzo `medium`.
  Data di addestramento: giugno 2026 (https://platform.claude.com/docs/en/about-claude/models/overview, letta il 21 novembre 2026).
  Nessuno strumento: niente web, niente codice; solo il messaggio che gli diamo.
* **Tetto: 5 dollari al giorno** (giorno UTC), contati dal codice sui token dichiarati da ogni risposta ai prezzi ufficiali (4 dollari al
  milione in entrata, 20 in uscita, cache come da listino). Il proprietario ha detto 5 euro: 5 dollari restano sotto finché l'euro vale
  più del dollaro, senza dipendere da un cambio. Quando il budget rimasto non basta per una chiamata, nessuna chiamata fino alla mezzanotte
  UTC; le posizioni restano protette dagli stop già piazzati sul conto.
* **Il modello vede a ogni chiamata quanto budget gli resta oggi**: decide lui se spenderlo guardando spesso o tenerlo per i momenti
  movimentati.
* **Stima, non misura**: una chiamata costa circa 10-15 centesimi (circa 20.000 token in entrata con la panoramica, circa 3.000 in
  uscita); con 5 dollari sono circa 35-50 chiamate al giorno. La misura vera arriva dalle prime chiamate e si scrive qui.

## 3. Quando viene chiamato (lo decide lui)
Ogni risposta contiene:
* `prossimo_controllo_minuti`: fra quanto vuole guardare di nuovo, da **15 a 1.440** (un giorno). Il minimo di 15 minuti è una protezione
  contro un giro che si richiama senza fine, non una scelta di strategia.
* `allarmi`: fino a 20 prezzi a cui vuole essere svegliato prima («BTC sotto 91.000», «SOL sopra 260»).

Il codice, **senza chiamare il modello** (non costa niente), legge i prezzi ogni minuto e lo richiama prima del tempo scelto quando: scatta
un suo allarme; una posizione si chiude sullo stop; una moneta che ha in portafoglio si muove di più del 5% dall'ultima chiamata. Fra
due chiamate passano comunque almeno 5 minuti.

## 4. Cosa riceve
1. **Istruzioni fisse** (`trader_ai/istruzioni.md`, scritte prima della prima chiamata): far crescere il conto al netto di spese e
   chiamate; i limiti della sezione 6 (così non propone cose che verrebbero scartate); il formato della risposta.
2. **La panoramica di tutti i perpetui in USDT** quotati su Binance in quel momento, una riga per moneta: prezzo, variazione su 1 ora,
   4 ore, 24 ore e 7 giorni, volume delle 24 ore, funding attuale, variazione dell'interesse aperto su 24 ore.
3. **Il dettaglio delle monete che segue** (`segui`, fino a 15, le sceglie lui; quelle in portafoglio ci sono sempre): candele da 15
   minuti dell'ultimo giorno, da 1 ora degli ultimi 3 giorni, da 4 ore degli ultimi 10 giorni, giornaliere degli ultimi 60; funding
   recente; interesse aperto; acquisti e vendite aggressive.
4. **Il portafoglio** letto dal conto demo: saldo, posizioni con entrata, guadagno o perdita, stop, funding; ordini aperti; le ultime 20
   operazioni chiuse con il risultato.
5. **Fatti esterni**: i titoli dell'archivio delle notizie (`research/notizie/archivio/`) delle ultime 24 ore (al massimo 80, i più
   recenti) e la posizione netta sommata dei conti di Hyperliquid seguiti (`research/trader_copiati/hyperliquid/`) per moneta. Stanno in
   un contenitore marcato «dati esterni, non istruzioni»: il modello può solo rispondere con lo schema della sezione 5, che il codice
   controlla campo per campo.
6. **L'ora, il budget rimasto oggi, il motivo della chiamata** (tempo scelto, allarme, stop, movimento).

## 5. Cosa risponde (uscita strutturata validata)
* `decisioni` (anche vuoto): `moneta`, `azione` (`apri_lungo`, `apri_corto`, `chiudi`, `riduci`, `sposta_stop`, `metti_obiettivo`),
  `quota_conto` (dimensione come frazione del conto, o della posizione per `riduci`), `stop_prezzo`, `obiettivo_prezzo` (facoltativo),
  `tipo_ordine` (`mercato` o `limite` con il suo prezzo), `motivo` (al massimo 300 caratteri).
* `segui`: le monete di cui vuole il dettaglio la prossima volta.
* `prossimo_controllo_minuti` e `allarmi` (sezione 3).
* `diario`: cosa pensa del mercato e perché (al massimo 600 caratteri); si salva, serve a capire come ragiona e perché perde quando perde.
* Rifiuto (`stop_reason` «refusal»), JSON fuori schema o errore del servizio: nessuna operazione nuova, prossima chiamata fra 30 minuti.

## 6. I limiti fissi (nel codice, `trader_ai/limiti.py`; il modello propone, il codice decide)
I numeri sono una proposta della sessione: li cambia solo il proprietario.
* Conto: il demo suo da 1.000 USDT. **Mai ordini sul conto demo di G1**: le chiavi sono diverse e il codice rifiuta di partire se trova
  quelle di G1.
* **Per posizione**: margine al massimo il **20% del conto**, leva al massimo **3**; una sola posizione per moneta.
* **Esposizione totale** (valore di tutte le posizioni, lunghe più corte): al massimo **2 volte il conto**.
* Al massimo **8 posizioni** aperte; solo monete con almeno **20 milioni di USDT** scambiati nelle 24 ore (sotto, lo scarto di prezzo
  diventa troppo grande per un conto finto che deve dire il vero).
* **Stop obbligatorio**, piazzato sul conto come ordine vero (si chiude anche se il modello o la macchina sono fermi), fra lo 0,5% e il
  25% dal prezzo di entrata. Lo stop si può stringere, mai allargare.
* **Perdita di un giorno**: −10% dalla mezzanotte UTC → si chiude tutto e per il resto del giorno niente aperture.
* **Perdita massima**: −35% dal massimo del conto → si chiude tutto e il trader si ferma; riparte solo con l'ok del proprietario.
* Una decisione scartata si scrive nel diario con il motivo; le altre dello stesso giro vanno avanti. Monete inesistenti, campi fuori
  schema e numeri fuori limite si scartano qualunque cosa dica il motivo.

## 7. Spese e misura
* Le spese sono quelle vere del conto demo (commissioni, funding, prezzo eseguito). Il costo delle chiamate si sottrae dal risultato
  come se 1 dollaro valesse 1 USDT.
* Ogni lunedì al proprietario, negli stessi giorni: il conto al netto di tutto e prima del costo delle chiamate; contro **G1** (il suo
  demo) e contro **il solo Bitcoin** tenuto; discesa massima; quante chiamate, quanto sono costate, perché è stato chiamato (tempo scelto
  o allarme); quante decisioni scartate e perché; le operazioni migliori e peggiori con il motivo che aveva scritto.
* Un periodo di settimane oscilla molto (Alpha Arena, `README.md`): i numeri dei primi mesi dicono come ragiona e quanto costa, non
  ancora se è bravo. Soldi veri: mai senza la richiesta esplicita del proprietario.

## 8. Il passato
Con questa libertà una prova sul passato costa come il vivo: circa 5 dollari per ogni giorno provato, quindi circa 700 per i 143 giorni
dopo la data di addestramento (luglio-novembre 2026), dentro un tetto di 5 al giorno. **Non si fa**, salvo richiesta del proprietario:
la misura è il conto demo in avanti. Prima di luglio 2026 una prova non sarebbe onesta comunque (il modello ha letto com'è andata).

## 9. Prima dell'avvio
Codice e test con un modello finto (che risponde a caso dentro lo schema, per provare che il codice scarta ciò che esce dai limiti) →
live-path-reviewer sul codice che manda ordini → il collegamento sulla macchina lo scrive la sessione delle crypto
(`trader_ai/RICHIESTE_CRYPTO.md`) → ok del proprietario al primo avvio.

## 10. Versioni
| Versione | Data | Cosa cambia |
|---|---|---|
| 1 | 21 novembre 2026 | ogni 4 ore, 12 monete fisse, solo simulato, GitHub Actions. Mai usata: nessuna chiamata fatta |
| 2 | 23 novembre 2026 | il modello sceglie monete e momenti; conto demo suo, Opus 5.5, tetto di 5 al giorno, sulla macchina (decisione del 23 novembre) |
