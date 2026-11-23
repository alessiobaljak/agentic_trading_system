# Revisione indipendente: la prova 45 sul conto demo di Alpaca (commit df4abcd)

Revisore indipendente, 23 novembre 2026. Nessun file del repository è stato modificato.

**Verdetto: REQUEST CHANGES.** Nessun problema Bloccante. Un problema Alto da chiudere prima di creare `stock/avanti/gamma_accesa`
(il percorso d'uscita all'asta). La divisione del conto (punto 2) è corretta in tutti i punti che leggono posizioni e ordini, e la
contabilità a tre è giusta nel percorso normale; i problemi stanno nei percorsi d'errore.

## Cosa ho eseguito davvero, e cosa no

Eseguito:
* `python -m pytest stock/tests -q`: **195 passati** (HEAD b6dae19, che sopra df4abcd cambia solo `stock/STATO.md`).
* Uno script mio nella cartella temporanea (`prova_conto.py`, accanto a questo file) che chiama le funzioni di `conto.py` e
  `gamma.py` su una copia di `valori.csv` e con `conto.adesso` sostituito da valori finti: nessuna chiamata ad Alpaca, nessun file
  del repository scritto.
* Una prova di `git add` in un repository vuoto nella cartella temporanea (punto B1).
* `git ls-remote --symref origin HEAD`: il ramo di default è `claude/brave-albattani-1b12fv`, quindi gli orari programmati del lavoro
  di GitHub partono (GitHub li fa girare solo dal ramo di default).

Letto per intero: `gamma.py`, `conto.py`, `miscela.py`, `avanti.py`, `plancia.py` (le parti che pubblicano), `GAMMA.md`,
`.github/workflows/azioni_gamma.yml`, `azioni_avanti.yml`, `azioni_miscela.yml`, `stock/avanti/vps/gira.sh` e `installa.sh`,
`stock/tests/test_gamma.py`, le deviazioni di `MISCELA.md` e `REGOLE.md`.

**Non verificato** (non ho accesso al conto né a GitHub): come il conto demo di Alpaca tratta gli ordini «cls» (esecuzione, ritardo
della comunicazione, cancellabilità dopo le 15:50, limite delle 12:50 nei giorni corti); se Alpaca accetta un secondo ordine
d'uscita mentre un «cls» è ancora aperto; se i passi `if: always()` girano quando un lavoro supera `timeout-minutes`; se la VPS delle
azioni è installata; come la routine delle 13:30 della sessione «trading stock» avvia il lavoro (non è nel repository); l'esito del
comando `controlla` (STATO.md dice «passato», non l'ho visto).

---

## 1. Il codice e GAMMA.md

| Regola | Esito | Dove |
|---|---|---|
| 1. Copertura del giorno di borsa prima, scaricata alla decisione; se manca, giorno saltato e scritto; il valore mai nel repository | **Conforme.** `copertura(scarica_copertura(), ieri)`, con `ieri = prima[-1]` dal calendario di Alpaca; nel file del giorno e nel diario solo «sotto zero / sopra zero / mancante»; nei log (pubblici: il repository è pubblico) il valore non si stampa. | gamma.py:240-251 |
| 2. r sulla barra delle 15:29 (IEX) contro l'ultima barra di ieri (tutte le borse); barra di oggi entro un minuto, se no salto scritto | **Conforme.** Barra con inizio `ingresso − 1 min`, attesa fino a `ingresso + 60 s`; ieri: ultima barra `< chiusura` di ieri con `feed="sip"`. | gamma.py:151-175, 252-259 |
| 3. VOO | Conforme (`SIMBOLI_GAMMA = ("VOO",)`). Lo scoperto di VOO lo dice STATO.md, non l'ho visto. | conto.py:24 |
| 4. Ingresso a mercato appena chiusa la barra; oltre 5 minuti il giorno si salta; **mai un ingresso più tardi** | **In parte.** L'ora si ricontrolla dopo i dati, ma **prima** di `posizione()`, `ultimo_prezzo()` e del POST: vedi M4. | gamma.py:260-267 |
| 5. Uscita all'asta subito dopo l'ingresso; se rifiutata, mercato alle 15:55; se ancora aperta dopo la chiusura, fuori orario; nessuna posizione di notte | **In parte.** Il rifiuto è gestito solo se arriva come errore alla consegna dell'ordine: vedi **A1** e M1. | gamma.py:294-332 |
| 6. 98% del capitale virtuale (100'000 + diario) / ultimo prezzo di VOO, azioni intere | Conforme. | gamma.py:68-70, 187-190, 264-265 |
| 7. Chiusure anticipate: mezz'ora prima della chiusura del calendario | Conforme (ingresso, limite dell'asta e 15:55 sono tutti relativi a `chiusura`); provato da `test_chiusura_anticipata_ingresso_mezzora_prima`. | gamma.py:78, 314, 318 |
| Giorni saltati scritti | Conforme per ogni salto dentro `entra` e per l'avvio tardivo (`tardi`, che scrive anche dopo la chiusura, fino al giorno stesso). Un giorno senza **nessun** avvio dopo le 15:35 non si scrive mai (basso). | gamma.py:224-228, 377-387 |
| Diario: solo nostri ordini e prezzi eseguiti | Conforme: prezzi eseguiti, r (ammesso da GAMMA.md), scarto in punti base; l'ultimo prezzo scaricato non si scrive. | gamma.py:100-126 |

## 2. La divisione per titolo: ogni punto di `stock/avanti/` che legge `/v2/positions` o `/v2/orders`

Tutti controllati, **tutti corretti** dopo il commit:

* `avanti.py:188` `_posizioni_candela` → `separa()[0]` → `della_candela` (esclude SPY, QQQ, VOO). Usata da `chiudi`, `chiudi_fuori_orario`,
  `_auto` (conteggio delle posizioni e «posizioni di un altro giorno»), `conto.registra`, `plancia.raccogli`.
* `avanti.py:193` `_ordini_aperti_candela` → `della_candela`; `avanti.py:200` cancella solo quelli.
* `avanti.py:253` POST solo sui 10 titoli dell'elenco (da `sp500_membri.csv`, che non contiene VOO, SPY, QQQ né IVV: controllato con grep;
  l'elenco di novembre è MU, NVDA, SNDK, AAPL, META, TSLA, MSFT, AMD, INTC, AMZN).
* `avanti.py:285` ricostruzione: filtro sul nome `candela15-{oggi}-`; `avanti.py:344` chiude solo le posizioni della candela;
  `avanti.py:440` fuori orario solo sulle sue; `scrivi_diario` usa solo le esecuzioni dei suoi titoli (`operazioni_del_giorno`).
* `miscela.py:157` `separa()[1]` (solo SPY e QQQ); `miscela.py:161/173` solo ordini SPY e QQQ; `miscela.py:205` POST solo SPY e QQQ;
  `miscela.py:348` sola lettura filtrata.
* `gamma.py:184` solo VOO; `gamma.py:213` POST solo VOO; `273/280` il suo ordine per id; `323` e `415` `DELETE /v2/positions/VOO`;
  `339-344` cancella solo ordini VOO; `350` POST VOO; `398` ricostruzione dal nome `gamma-{giorno}-in`; `468` sola lettura filtrata.
* `conto.py:106` legge tutte le posizioni e le divide.
* Nessun `DELETE /v2/positions` o `DELETE /v2/orders` senza simbolo in tutto `stock/` (grep). Fuori da `stock/avanti/` nessun altro
  codice di `stock/` manda ordini.
* Nomi unici distinti: `candela15-…`, `miscela-…`, `gamma-{giorno}-in`, `gamma-{giorno}-asta`.

Eccezione condizionata: vedi M5 (copia vecchia del codice sulla VPS).

## 3. La contabilità a tre

**Percorso normale: corretta.** Prima della riga del giorno: `valore_gamma` = flusso delle esecuzioni VOO di oggi + valore di mercato
delle posizioni VOO; dopo: somma del diario + non realizzato. Con la posizione chiusa le due strade danno lo stesso numero (la riga usa
`(p_out − p_in) × q_in`, uguale al flusso quando le uscite pareggiano l'ingresso). La candela non conta più le esecuzioni di VOO
(`_flusso(…, della_candela)`, prima era `not della_miscela`). La miscela toglie `gamma − 100'000`. Il test
`test_conto_a_tre_il_guadagno_della_prova_45_non_va_alla_miscela` prova entrambi i casi e passa.

**`valori.csv` con le righe vecchie: corretto** (eseguito sulla copia): l'intestazione diventa `giorno,conto,prima_candela,miscela,gamma`,
le righe vecchie restano con la colonna vuota, `giorni("gamma")` le salta, `giorni("miscela")` non cambia.

**Percorsi d'errore: il guadagno di VOO finisce nella miscela** (M2, M6).

## 4. Ordini doppi o persi

* Avvii ripetuti: un lavoro alla volta (gruppo `azioni-gamma`, `cancel-in-progress: false`; GitHub tiene al massimo un lavoro in
  attesa e cancella i precedenti in attesa: innocuo, `auto` è ripetibile). Nomi unici per ingresso e asta: un secondo invio è
  rifiutato e `manda` riprende l'ordine vivo con lo stesso nome. **Corretto.**
* Giro che muore dopo l'ingresso: il file del giorno si scrive subito dopo il POST (riga 271) ma arriva nel repository solo al passo
  «Salva». Se la posizione è ancora aperta, il giro dopo ricostruisce dal nome (righe 397-401). **Se la posizione è già chiusa
  (asta eseguita) il file non si ricostruisce**: il giro dopo le 15:35 trova «non deciso» e scrive «saltato: avvio in ritardo» al posto
  di un'operazione vera (M2).
* Giro che parte con la posizione aperta: «segui» → cerca l'asta per nome, non la rimanda. **Corretto.**
* Gli ordini d'emergenza (fuori orario, mercato) non hanno nome unico: senza giri in parallelo non è un problema; vedi M1 per il caso
  dell'asta eseguita in ritardo.

## 5. Orari

* Ora legale e solare: gli orari UTC danno d'inverno 8:40, 10:40, 12:40, 13:40, 14:40, 16:10, 17:10 di New York; d'estate 9:40 (troppo
  presto, esce), 11:40, 13:40, 14:40, 15:40 (dopo l'ingresso: in attesa dietro al lavoro che gira, poi «niente», o «tardi»), 17:10,
  18:10. In entrambe le stagioni ci sono avvii utili per l'ingresso e avvii dopo la chiusura prima delle 20:00. Tutti nello stesso
  giorno UTC, quindi `1-5` è giusto. **Corretto.**
* Chiusure anticipate: tutto relativo alla chiusura del calendario (vedi tabella). Il limite di Alpaca per i «cls» nei giorni corti
  (12:50) l'ho supposto, non verificato.
* Limite di Alpaca per gli ordini alla chiusura (15:50): `LIMITE_ASTA = 10 min`, conforme a quanto scritto in GAMMA.md.
* Limite di 6 ore: **M3**.

## 6. Posizioni aperte di notte senza che nessuno lo sappia

* Percorso normale: se dopo la chiusura fuori orario resta qualcosa, errore (lavoro rosso) e allarme sulla Plancia; gli avvii delle
  16:10/17:10 (d'estate 17:10/18:10) riprovano; la mattina dopo «chiudi_subito» o fuori orario prima dell'apertura. Buono.
* Restano scoperti: M5 (nessuno controlla VOO se il lavoro della prova 45 non parte) e i ritorni «niente» che chiudono il lavoro in
  verde con una posizione aperta (gamma.py:76, 86, 94), innocui finché nessun avvio cade dopo le 20:00 o prima delle 4:00.

---

## Problemi

### Bloccanti
Nessuno.

### Alti

**A1. L'uscita all'asta: lo stato dell'ordine «cls» si legge una volta sola, e un'asta accettata e poi rifiutata o scaduta non porta
alla chiusura a mercato delle 15:55 (GAMMA.md, regola 5).** `segui` (gamma.py:310-316) guarda l'asta all'inizio; se l'ordine è vivo
(«new», «accepted», «pending_new») non lo rilegge più e dorme fino alle 16:02 (riga 327-329). Il ripiego a mercato (righe 317-326)
scatta solo se il POST torna con un errore. Su Alpaca un ordine può essere accettato e poi diventare «rejected», «canceled» o
«expired» senza esecuzione, e **su questo stesso conto demo è già successo con gli ordini d'asta d'apertura**: gli «opg» della miscela
del 12 novembre sono «scaduti alle 9:31 senza esecuzione» (`stock/avanti/MISCELA.md:44-47`, `miscela.py:186-187`). Se i «cls» si
comportano allo stesso modo, ogni operazione arriva alle 16:02 con la posizione aperta e si chiude fuori orario con un ordine limite
peggiorato dello 0,5% (gamma.py:347-352): la regola 5 («mercato 5 minuti prima») non viene mai applicata, la posizione supera ogni
volta la chiusura, il diario segna «fuori orario» e la domanda della prova («l'uscita all'asta costa quanto si è supposto?») non ha
risposta. Il comando `controlla` non prova i «cls» (guarda solo le proprietà del titolo). Percorso concreto: 15:30:05 ingresso; 15:30:10
asta accettata («accepted»); 15:50-16:00 Alpaca la cancella o la fa scadere; 16:02 `posizione() != 0` → `fuori_orario`. Da fare prima
di `gamma_accesa`: rileggere l'asta per nome subito prima del limite (per esempio alle 15:51) e alle 15:54:30, e se non è viva né
eseguita chiudere a mercato alle 15:55 come dice la regola; e sapere, con un ordine di prova o con l'esito degli «opg», se il conto
demo esegue davvero i «cls».

### Medi

**M1. Dopo la chiusura, l'ordine fuori orario parte senza aspettare che l'asta sia finita.** Alle 16:02 (`DOPO_LA_CHIUSURA = 2 min`)
`fuori_orario` prova a cancellare gli ordini VOO aperti, compreso il «cls» (gamma.py:339-344, errori ignorati), aspetta 5 secondi,
rilegge la posizione e manda un limite fuori orario (346-352). Se Alpaca comunica l'esecuzione dell'asta dopo quella lettura e la
cancellazione del «cls» non è possibile dopo le 15:50, l'uscita può essere doppia: per una vendita allo scoperto ricoperta, il limite
di acquisto può portare a una posizione lunga; per una lunga, Alpaca probabilmente rifiuta la seconda vendita (azioni già impegnate) e
il lavoro si ferma con un errore. Non verificato su Alpaca. Correzione semplice: prima dell'ordine fuori orario aspettare che l'ordine
d'asta sia in uno stato finale e rileggere la posizione.

**M2. Nei percorsi d'errore il guadagno di VOO finisce nella miscela, e per qualche ora la miscela si crede con il doppio (o quasi
zero) di capitale.** (a) Posizione rimasta di notte: la riga di ieri resta «aperta» con guadagno vuoto; oggi `auto` la chiude come
«altro giorno» (gamma.py:419, `fuori_orario("altro giorno")` non riscrive la riga di ieri, riga 359). Finché oggi non c'è la riga del
giorno (scritta alle 15:30 o da `tardi`), `valore_gamma` conta il flusso della ricopertura senza il costo di ieri. Eseguito sulla
copia: ricoperta stamattina una vendita di 160 VOO a 600 → prova 45 **4'000**, miscela **196'000** (conto.py:59-70, 97-98). La miscela
usa `conto.adesso()["miscela"]` per le quantità (`miscela.py:248` la sera, `miscela.py:277` la banca centrale alle 13:59/14:00):
ordini sbagliati di circa il doppio in un'altra strategia. Dopo la riga di oggi resta comunque una perdita: il guadagno della notte
non entra mai nella prova 45 e resta alla miscela. (b) File del giorno perso con l'asta già eseguita: la ricostruzione c'è solo con la
posizione aperta (gamma.py:397), quindi il giro dopo scrive «saltato: avvio in ritardo» (`tardi`) per un giorno con un'operazione vera,
e il suo guadagno va alla miscela. Correzioni: ricostruire dal nome `gamma-{giorno}-in` anche senza posizione; quando si chiude una
posizione di un altro giorno, riscrivere la riga di quel giorno; contare nel flusso di oggi solo le esecuzioni degli ordini di oggi.

**M3. L'attesa massima della prima candela (5 ore e 20) è troppo lunga per la prova 45.** `cosa_fare` usa `av.ATTESA_MASSIMA`
(gamma.py:88, avanti.py:358), pensata per un giro che finisce pochi minuti dopo l'ora attesa; qui dopo l'ingresso il giro resta acceso
fino alle 16:02 e oltre. Eseguito: un avvio alle 10:10 di New York risponde «entra» e dura almeno 352 minuti, contro `timeout-minutes:
350` (azioni_gamma.yml:31), più installazione e download (fino a circa 3 minuti di tentativi su SqueezeMetrics). Un orario di GitHub
delle 8:40 in ritardo di 90 minuti (ritardi di ore già visti l'11 novembre) fa uccidere il lavoro verso le 16:00, durante l'asta,
prima del controllo e del diario; ci pensa il lavoro in attesa, se c'è. Correzione: un'attesa sua di circa 4 ore e 45.

**M4. Il limite dei 5 minuti non è controllato al momento dell'ordine.** Dopo il controllo dell'ora (gamma.py:260) vengono
`posizione()` (fino a 3 tentativi da 30 secondi), `ultimo_prezzo()` (`alpaca._get`: fino a 10 tentativi con attese che crescono fino
a 60 secondi, alcuni minuti in tutto) e il POST (fino a 3 tentativi). Con Alpaca lento l'ingresso può partire dopo le 15:35, contro
«mai un ingresso più tardi». Correzione: ricontrollare l'ora subito prima del POST.

**M5. VOO non ha più una seconda rete di sicurezza.** Prima del commit la prima candela considerava suo ogni titolo non della miscela
e avrebbe chiuso o segnalato una posizione VOO rimasta; ora la esclude (corretto per la divisione), ma nessun altro controlla «nel
conto c'è solo ciò che le tre strategie si aspettano». Se il lavoro della prova 45 non parte (GitHub non fa partire gli orari, cosa
già successa; `gamma_accesa` tolto con una posizione aperta; un errore all'importazione) una posizione VOO può passare la notte senza
allarme: l'allarme della Plancia lo scrive solo `gamma.py`. In più: se la VPS delle azioni è installata (non verificato; STATO.md dice
che manca solo il timer della prova 45), `gira.sh:20-21` usa «quello che c'è» quando il `git pull` fallisce: una copia vecchia di
`conto.py` tratta VOO come titolo della prima candela, quindi alle 15:55 lo chiude a mercato e cancella l'ordine d'asta, o alle 15:31
lo chiude subito come «posizione di un altro giorno» se quel giorno la candela non ha ordini. Correzioni: un controllo dei titoli
sconosciuti nel giro della candela (VOO aperto dopo le 16:05 → allarme), e sulla VPS non girare con codice vecchio.

**M6. Letture non simultanee nei valori di fine giornata.** `conto.adesso()` legge conto, posizioni ed esecuzioni con tre chiamate
(conto.py:105-115). Se l'esecuzione dell'asta di VOO cade fra la lettura delle posizioni e quella delle esecuzioni, la prova 45 conta
due volte il valore della posizione. Eseguito: valore **196'320** invece di 100'160; la miscela perde la stessa somma. `registra` scrive
una volta sola al giorno e non riscrive (conto.py:145-146), quindi l'errore resterebbe in `valori.csv`. La finestra è stretta e
riguarda soprattutto i timer della VPS delle 16:00 e 16:03 (GitHub arriva alle 16:15); correzione: in `registra` aspettare che VOO non
abbia posizioni né ordini aperti, o rileggere le posizioni dopo le esecuzioni e scartare se cambiano.

**M7. Nessun test sui percorsi degli ordini.** `test_gamma.py` prova le funzioni pure; non ci sono prove (con Alpaca finto) di `segui`
con l'asta rifiutata, della ricostruzione, di `fuori_orario`, del ritardo oltre i 5 minuti dentro `entra`.

### Bassi

* **B1.** `git add stock/avanti/gamma_diario.csv stock/avanti/gamma_giorni` (azioni_gamma.yml:68): se uno dei due non esiste, git non
  aggiunge niente (provato: «pathspec did not match», uscita 128, niente in coda). Succede solo il primo giorno con un'operazione se il
  giro si interrompe prima del diario: il file del giorno non si salva.
* **B2.** L'allarme `allarmi/posizioni_aperte_gamma` si scrive solo quando c'è (gamma.py:445-446) e non si cancella mai quando il
  problema è risolto (la prima candela invece lo azzera a ogni pubblicazione, plancia.py:164).
* **B3.** Da oggi `registra` scrive `gamma = 100000.0` ogni giorno anche a prova spenta: lo storico della Plancia della prova 45 parte
  dal giorno del commit, non dal primo giorno di misura. Il messaggio di `registra` non nomina la colonna nuova.
* **B4.** `_ordine_per_nome` restituisce None anche per un errore di rete: se il file del giorno manca e la ricerca fallisce, una
  posizione di oggi viene trattata come «di un altro giorno» e chiusa a mercato (gamma.py:397-401, 414-417).
* **B5.** Il lavoro che aspetta l'ingresso tiene occupato il gruppo per ore: un `controlla`, `ordini` o `plancia` lanciato a mano
  aspetta fino alla fine.
* **B6.** La riga del diario usa `q_in` anche quando le uscite non pareggiano l'ingresso (gamma.py:115): il guadagno è approssimato
  e la nota lo dice.
* **B7.** `${{ inputs.comando }}` dentro lo script (azioni_gamma.yml:40-41): lo può lanciare solo chi ha accesso in scrittura al
  repository; stesso schema degli altri lavori.
* **B8.** La routine delle 13:30 della sessione non è nel repository: se lanciasse `python -m stock.avanti.gamma auto` fuori da GitHub
  (invece di avviare il lavoro), girerebbe in parallelo al lavoro che aspetta; i nomi unici evitano ingressi doppi, non le uscite
  d'emergenza doppie. Da confermare che avvii il lavoro di GitHub.

## Cosa serve prima di accendere (creare `stock/avanti/gamma_accesa`)

1. A1: ricontrollo dell'asta prima delle 15:55 e ripiego a mercato; sapere se il conto demo esegue i «cls».
2. M1: aspettare lo stato finale dell'asta prima dell'ordine fuori orario.
3. M3 e M4: attesa massima sua e controllo dell'ora subito prima del POST.
4. Consigliati: M2 (ricostruzione anche senza posizione, riga di ieri riscritta), M5 (allarme su VOO nel giro della candela; codice
   vecchio sulla VPS), M6, M7.

---

# Aggiunta: ricontrollo del commit 847040c (23 novembre 2026)

**Verdetto: APPROVE**, a una condizione che non ho potuto verificare: prima di creare `gamma_accesa`, il comando `controlla` deve
stampare `None` per il nome d'ordine inesistente. Se Alpaca rispondesse a un nome inesistente con un codice diverso da 404, **ogni**
avvio di un giorno di borsa si fermerebbe con un errore: la prova non opererebbe mai, ma lo segnalerebbe. Nessun problema Bloccante
né Alto. Due problemi Medi nuovi (N1, N2), consigliati prima della prima operazione.

## Cosa ho eseguito

* `python -m pytest stock/tests -q`: **198 passati** (HEAD 847040c).
* Due script miei nella cartella temporanea (`prova_correzioni.py`, `prova_ritardo_posizione.py`, accanto a questo file): conto finto,
  orologio finto, `GIORNI` e `DIARIO` dirottati nella cartella temporanea. Nessun file del repository scritto (`git status` pulito).
* Non verificato: il comportamento vero di Alpaca (codice per un nome inesistente, «cls» sul demo, cancellabilità dopo le 15:50,
  ritardi fra ordini, posizioni ed esecuzioni).

## (1) I problemi della prima revisione

* **A1, chiuso.** `segui` (gamma.py:365-377) rilegge posizione e stato dell'asta ogni 30 secondi fino alle 15:58. Se l'asta non è viva
  né eseguita: prima delle 15:50 la rimanda con un nome nuovo (`gamma-{giorno}-asta-{n}`, al massimo 3 invii); dopo, aspetta le 15:58 ed
  esce a mercato. Alla riga 376 lo stato si rilegge ancora una volta. Percorsi eseguiti:
  * asta scaduta, giro partito alle 15:51: **una** uscita a mercato, alle **15:58:00**, nessun nuovo ordine d'asta;
  * asta cancellata alle 15:40: rimandata come `asta-2`, nessuna uscita a mercato.

  Un'asta che muore dopo le 15:59:15 porta alla chiusura fuori orario: corretto, perché a quell'ora un ordine a mercato non è più
  sicuro.
* **M1, chiuso.** `dopo_la_chiusura` (382-391) aspetta fino alle 16:07 finché l'asta è viva. Poi `_cancella_ordini_gamma` (394-410)
  ferma il giro **prima** di mandare un ordine nuovo, se un ordine VOO resta aperto. Lo prova il test 3.
  * Resto, basso: se il demo tiene un «cls» aperto senza eseguirlo né cancellarlo oltre le 20:00, la posizione passa la notte. Il
    lavoro però si ferma con un errore e l'allarme resta: non è silenzioso.
  * Resto, basso: gli stati «pending_cancel», «stopped» e «suspended» non sono fra i vivi, quindi provocano un nuovo invio con l'ordine
    vecchio forse ancora valido. Rarissimo.
* **M3, chiuso.** `ATTESA_MASSIMA` della prova 45 è ora 4 ore e 30, quindi l'ingresso parte dalle 11:00. Il giro più lungo:
  * 10:59 → circa 16:11 (asta fino alle 16:07, fuori orario con 30 secondi di cancellazioni e 60 di attesa), cioè circa 312 minuti
    contro 350;
  * nei giorni corti 8:00 → circa 13:11.

  L'orario d'inverno delle 10:40 ora esce subito («troppo presto»): restano 12:40, 13:40 e 14:40 più le routine. Il commento nel file
  del lavoro dice ancora «5 ore e 20» (basso, solo testo).
* **M4, chiuso.** L'ora si ricontrolla subito prima del POST (gamma.py:270). Resta solo il caso dei ritentativi di rete dentro
  `_richiesta`: fino a circa 1 minuto e mezzo in più, e solo con la rete in errore.

## (2) Le correzioni: problemi nuovi

**N1 (Medio, nuovo): uscita a mercato alle 15:30 se la prima lettura della posizione torna vuota.**
* Nel ciclo di `segui`, `if q == 0: break` (riga 367-368) esce dal ciclo. Poi la riga 376 rilegge la posizione e, se ora c'è e l'asta
  non c'è (stato None), esce subito a mercato. La condizione è soltanto «prima delle 15:59:15», non «dalle 15:58 in poi».
* Eseguito: ingresso eseguito, prima lettura della posizione vuota (un ritardo di Alpaca fra ordine e posizione), seconda con 160
  azioni. Risultato: `DELETE /v2/positions/VOO` alle **15:30:40**, nessun ordine d'asta, nota «uscita a mercato 2 minuti prima della
  fine», che è falsa.
* Il ritardo è raro, ma il giorno misurato diventa un'andata e ritorno di pochi secondi con una nota sbagliata.
* Correzione: alla riga 376 aggiungere `av.ny_adesso() >= a_mercato - 5 s`; con `q == 0` subito dopo l'ingresso, rileggere invece di
  uscire.

**N2 (Medio-basso, nuovo): `chiudi_rimasta` perde le esecuzioni di un giro precedente e non controlla di quale giorno è la posizione.**
* (a) La riga del giorno d'ingresso si ricalcola con le esecuzioni di oggi del **solo** ordine di questo giro
  (`e["order_id"] == o.get("id")`, riga 456).
  * Eseguito: la posizione rimasta di 160 è chiusa in due giri fuori orario (100 a 601, poi 60 a 602). La riga dice «uscite 60 su 160»
    e guadagno **−320** invece di **−220**; il valore della prova 45 è 99'680 invece di 99'780. La differenza resta alla miscela.
  * Correzione: prendere le esecuzioni di oggi di tutti gli ordini già segnati in `orig["uscite"]`.
* (b) `orig` è l'ultimo giorno precedente con un ingresso (450-451), senza controllare lato e quantità. Se il file di quel giorno
  mancasse, o se la posizione venisse da un'uscita doppia, si riscriverebbe la riga di un'operazione già chiusa.
* La nota «chiusa il …» si ripete a ogni giro (solo testo).

**`_ordine_per_nome` che ferma il giro: accettabile, anzi più sicuro.**
* Eseguito: con un 404 restituisce None; con un 500 o con la rete in errore ferma il giro dopo 3 tentativi.
* Dove viene chiamato:
  * all'inizio di ogni avvio di un giorno di borsa senza file del giorno (`ricostruisci`, riga 529, **prima** dell'attesa): un errore
    ferma quell'avvio senza ordini, e gli avvii dopo riprovano;
  * dentro `manda` dopo un POST fallito: fermarsi è meglio che supporre «non mandato», che con l'asta porterebbe a due ordini
    «cls» vivi e a un'uscita doppia.
* Prezzo da sapere: con Alpaca in errore proprio durante `segui`, il ripiego a mercato delle 15:58 non parte da quel giro. Lo fa il
  lavoro in coda o, dopo la chiusura, l'avvio delle 16:10 (d'estate 17:10). Rumoroso, non silenzioso.
* Condizione: `controlla` deve dare None per il nome inesistente (vedi verdetto).

**`ricostruisci`: corretto.** Eseguito: file del giorno perso, operazione già chiusa all'asta, avvio delle 16:10. Ricostruisce il file
(con `asta-1` e `tentativi_asta`) e fa «diario», non più «tardi».

**`diario_scritto`: corretto**, con un effetto innocuo. Quando l'ingresso non è stato eseguito, il file del giorno ha `id_ingresso`
ma la riga non ha quantità. Allora ogni avvio dopo le 16:02 rifà «diario» e riscrive la stessa riga, poi ripubblica (basso).

**`conto.registra`: corretto, e chiude M6.** Il controllo degli ordini aperti viene prima, poi `adesso()` legge le posizioni **prima**
delle esecuzioni. Un'esecuzione di VOO cade quindi o prima della lettura delle posizioni (e allora le esecuzioni la contengono) o
dopo (e allora c'è la posizione, e la riga non si scrive).
* Resto, basso: se l'elenco delle esecuzioni di Alpaca fosse in ritardo rispetto alle posizioni, la prova 45 risulterebbe a circa
  2'000 e la riga sbagliata resterebbe. Controllo semplice: le azioni VOO eseguite oggi, con il loro segno, devono sommare alla
  posizione (zero).
* Effetto nuovo, basso: con un ordine VOO bloccato fino a mezzanotte, la riga di quel giorno non si scrive mai.
* B3: la colonna resta vuota finché `gamma_diario.csv` non esiste. Giusto.

**B1, B2, B4: chiusi.**
* B1: il salvataggio aggiunge solo i percorsi che esistono.
* B2: ogni pubblicazione scrive l'allarme, e None lo azzera. Basso: anche un `plancia` lanciato a mano lo azzera con VOO ancora aperta.
* B4: un errore non è più preso per «ordine inesistente».

## (3) Le prove nuove

* `test_cosa_fare_a_ogni_ora`: 10:40 «troppo presto», 11:05 «entra». Prova la nuova attesa (il confine esatto delle 11:00 non è provato).
* `test_asta_scaduta_dopo_le_15_50_si_esce_a_mercato_2_minuti_prima`: prova una sola uscita a mercato, nessun nuovo invio d'asta e la
  nota. **Non controlla l'ora**, che il nome promette («2 minuti prima»): l'ho controllata io (15:58:00). Basta aggiungere l'ora alla
  chiamata registrata.
* `test_asta_cancellata_prima_delle_15_50_si_rimanda_e_si_esce_all_asta`: prova davvero il nuovo invio come `asta-2` e l'assenza
  dell'uscita a mercato. Il conto finto dà lo stesso stato a tutti gli ordini d'asta: va bene per questo caso.
* `test_fuori_orario_non_manda_un_secondo_ordine_se_l_asta_resta_aperta`: prova davvero «niente ordine nuovo se uno resta aperto»
  (errore e nessun POST).
* Non provati: `ricostruisci`, `diario_scritto`, `chiudi_rimasta`, i controlli nuovi di `registra`, `_ordine_per_nome` (404 contro
  errore), il ricontrollo dell'ora prima del POST, e il caso N1.

## Rimasti aperti per scelta (presi atto)

* M5: la VPS, secondo la sessione, non è installata; non l'ho verificato.
* Se il demo esegue i «cls» lo dirà la prima operazione. Con A1 e M1 corretti, un'asta morta porta all'uscita a mercato alle 15:58 e
  un'asta mai eseguita alla chiusura fuori orario dopo le 16:07. Un'asta che resta aperta oltre le 20:00 lascia la posizione per la
  notte, ma con errore e allarme.

## Dopo la seconda revisione (sessione principale, 23 novembre 2026)

* N1 corretto: in `segui` una posizione non ancora visibile non fa più uscire dal ciclo; l'uscita a mercato solo da 5 secondi prima
  delle 15:58 (prova `test_posizione_vista_in_ritardo_non_fa_uscire_a_mercato_alle_15_30`).
* N2 corretto: `chiudi_rimasta` sceglie il giorno con lo stesso lato della posizione e usa tutte le uscite segnate per quell'ingresso.
* Bassi: il commento del lavoro di GitHub dice 4 ore e 30; «stopped» conta come asta viva.
* La condizione del verdetto è verificata: `controlla` su GitHub (23 novembre, 21:52 UTC) stampa `None` per il nome d'ordine che non
  esiste.
* Restano aperti per scelta: M5 (nessuna rete della prima candela su VOO; prima di installare la VPS lo script va aggiornato con la
  prova 45, e una copia vecchia del codice sulla VPS chiuderebbe VOO) e se il demo esegue gli ordini alla chiusura (lo dirà la prima
  operazione).
