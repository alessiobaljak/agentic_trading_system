# Fase 5 — Stress test e rapporto finale

_Chiusura dell'upgrade v3. Le fasi 0–4 hanno cambiato il sistema; questa fase
verifica come si comporta quando qualcosa si rompe, e mette per iscritto cosa
resta aperto._

---

## Parte 1 — Gli stress test

Tre guasti che sulla VPS capiteranno, non "se" ma "quando". Il resto della suite
verifica che il sistema faccia la cosa giusta quando tutto funziona; questi test
verificano che faccia la cosa **meno peggio** quando non funziona.

Il criterio è uno solo, uguale per tutti e tre:

> **Una posizione aperta non resta mai senza sorveglianza.**

Un guasto può costare uno scan incompleto, una dashboard vecchia, un'occasione
persa. Non può costare uno stop che non scatta: è l'unico errore che si paga in
denaro e non si recupera. Da qui la regola che ricorre nei tre scenari — in
degrado si **continua a gestire** ciò che è aperto e si **smette di aprire**.
Gestire non ha bisogno del componente rotto (i prezzi arrivano da Binance, lo
stato vive in memoria); aprire aggiunge rischio proprio mentre un controllo è
cieco.

I test sono in `tests/test_stress.py` (23 test).

### Scenario 1 — WebSocket giù con una posizione aperta

**Cosa fa il sistema.** Lo stream serve a vedere l'*ordine* dei prezzi dentro il
minuto. Se cade si perde quella precisione, non la sorveglianza: si ricade sulle
candele 1m via REST (vedono gli estremi, non l'ordine). Se cade anche il REST si
resta col solo mark price. Ogni gradino è più povero del precedente, nessuno è
cieco.

**Esito: nessun difetto trovato.** La degradazione era già corretta ed è ora
coperta dai test, incluso il caso che conta davvero — *stop che scatta comunque
mentre lo stream è morto* — e il doppio guasto stream + REST.

Una cosa da sapere: alla riconnessione il bot **non riapre subito**. Aspetta due
candele complete (`_stream_recovery_guard`), perché gli indicatori poggiano
ancora su una serie con un pezzo mancante. Le posizioni aperte, invece,
continuano a essere gestite per tutto il tempo.

### Scenario 2 — Binance lenta (oltre 5 secondi a risposta)

Il pericolo qui non è l'errore: è l'**attesa**. Un sistema che aspetta
all'infinito non dà segnali di guasto — sembra vivo e non fa niente.

**Difetto trovato e corretto: lo scan non aveva un tetto di tempo.** Ogni simbolo
può costare fino a ~20s (timeout 10s + un retry). Su un universo di oltre cento
coin uno scan con Binance lenta diventa di **ore**, e per tutto quel tempo il
loop non torna a gestire le posizioni aperte: la lentezza della rete si
trasformava in stop e take-profit non sorvegliati.

Correzione: `SCAN_MAX_SECONDS` (default **300s**). Scaduto il budget lo scan si
ferma, tiene ciò che ha raccolto e **dichiara quante coin ha saltato** — una
troncatura silenziosa si leggerebbe come "ho guardato tutto il mercato".

Verificato inoltre: ogni chiamata REST porta un timeout; un 504 viene ritentato
un numero finito di volte con attese crescenti; un `Retry-After` dell'exchange
vince sul backoff; e un errore mentre si piazza la protezione dopo l'entry resta
**critico qualunque sia il codice** (posizione aperta e forse senza stop).

### Scenario 3 — Firebase irraggiungibile

**Difetto trovato e corretto, il più grave dei tre.** Vanno distinti due guasti:

* *Firebase non configurato* (test, primo avvio locale) — stato noto in partenza,
  si parte sullo store in memoria, tutto funziona.
* *Firebase configurato ma muto* (rete giù, quota finita, credenziali revocate) —
  il client è vivo e **ogni chiamata solleva**.

Il secondo caso non era gestito. Il Realtime DB sta sul percorso caldo del loop
(stato, equity, comandi, heartbeat), quindi un'eccezione lì fermava il ciclo; e
l'heartbeat sta in un blocco `finally`, dove un'eccezione **non è intercettata da
nessuno e termina il processo**. In pratica: un buco di rete su Firebase
spegneva il bot lasciando aperte le posizioni.

Correzioni:

1. **Il Realtime DB non solleva mai.** Le scritture vanno comunque nello specchio
   in memoria, le letture ricadono sull'ultimo valore noto, una lettura riuscita
   aggiorna lo specchio (così il valore più fresco è già lì quando il database
   smetterà di rispondere). Il guasto viene *contato*, non propagato.
2. **`set_rtdb` ora ritorna un booleano**: `True` se la scrittura è finita davvero
   su Firebase. Serve al WAL dei trade chiusi — senza, "scritto" e "perso al
   prossimo riavvio" sarebbero indistinguibili. Un WAL non durevole viene ora
   dichiarato nei log.
3. **Firestore continua a sollevare, ed è voluto**: lì ci sono i trade chiusi. Se
   una scrittura fallita passasse per riuscita, il WAL verrebbe cancellato subito
   dopo e quel trade sparirebbe per sempre (equity mai più riconciliabile). Meglio
   un ciclo interrotto che un trade perso.
4. **Blocco delle nuove aperture dopo un'interruzione prolungata**
   (`FIREBASE_DEGRADED_BLOCK_SECONDS`, default **300s**). Col RTDB muto non si
   legge più `/commands`, e lì dentro c'è il kill switch: aprire mentre il freno
   dell'utente è scollegato aggiunge rischio che nessuno può più fermare. Le
   posizioni aperte continuano a essere gestite. È la stessa regola del
   reconciler: nell'incertezza si gestisce ciò che c'è, non si aggiunge altro.

Il singolo errore non conta, conta la **durata**: una richiesta persa è rete,
cinque minuti di silenzio sono un guasto.

---

## Parte 2 — Rapporto finale dell'upgrade

### Cosa è stato preservato

Nessuna delle modifiche ha toccato il cuore del sistema:

* **Il GATE 1 e la sua soglia.** Criteri, walk-forward, holdout, purge/embargo:
  invariati. Le aggiunte (robustezza `pf_ex_top`, drawdown di portafoglio) sono
  criteri *in più*, non sostituzioni.
* **La parità gate ↔ paper.** Le primitive di uscita restano condivise
  (`bot/execution/exit_logic.py`): un solo posto decide dove sta uno stop, dove
  stanno i take-profit e quando si va a break-even. Ogni nuovo filtro di
  comportamento segue la convenzione `BACKTEST_PARITY` — inerte quando la parità
  è attiva, perché filtrare in live ciò che il gate ha validato ricrea proprio la
  divergenza che stiamo combattendo.
* **DRY_RUN.** Il sistema non ha mai toccato denaro vero e non lo tocca ora.
* **La disciplina "prima si misura, poi si collega".** Confidenza del regime,
  punteggio degli asset e decisioni dell'LLM sono *calcolati e registrati*, ma
  nessuno di essi tocca size o leva finché non ha dimostrato di predire l'esito.

### Cosa è stato modificato

| Area | Prima | Ora |
|---|---|---|
| Leva | troncata a int → sempre 2x | arrotondata e limitata: la leva dinamica si vede davvero |
| Rischio | `risk_per_trade` inerte (il cap sul notional legava sempre) | `risk_effective_pct` e `capped_by_position_limit` rendono visibile quale vincolo lega |
| Freno sulla deriva | leggeva solo `pairs`/`strategies` → non scattava mai | legge anche il verdetto `global` |
| Kill switch | booleano acceso/spento | tre livelli (PAUSED / STOPPING / EMERGENCY), il più severo vince |
| Errori Binance | un unico `except Exception` | tassonomia per gravità (retry / stop / critico), sconosciuto → stop |
| Pesi del learning | ricalcolati su qualunque campione | soglia di campione, smoothing, controllo di sicurezza 40%, storico versioni |
| Drawdown | per trade | anche di **portafoglio**, ordinato nel tempo |
| Scan | senza tetto di tempo | budget `SCAN_MAX_SECONDS`, troncatura dichiarata |
| Firebase | eccezioni sul percorso caldo | RTDB che degrada, Firestore che solleva |

### Cosa è stato aggiunto

* **Riconciliazione** stato interno ↔ exchange (`bot/execution/reconciler.py`): un
  thread rileva, il loop applica. Inerte in DRY_RUN.
* **Strato AI** (`bot/ai/`): analista, ipotesi, filtro d'universo, **modalità
  ombra**. Tutto fail-open: senza chiave il comportamento è identico.
* **Qualità del backtest** (`backtesting/quality.py`): Sharpe, Sortino, drawdown
  datato, semaforo di validazione, **due rilevatori di look-ahead**, due benchmark
  (BTC e paniere equipesato delle coin tradate), curva di equity, rilevamento
  delisting.
* **`mfe_r`** su ogni trade simulato e chiuso: un solo numero che dice quali
  gradini *qualunque* scala di take-profit avrebbe raggiunto.
* **Sette pannelli** nella dashboard (regime, rischio di portafoglio, evoluzione
  del learning, punteggio asset, reconciler, costi, ombra dell'orchestratore).
* **Strumenti**: `scripts/gate_vs_paper.py --entry-timing` e `--trades-file`,
  `scripts/shadow_report.py`, `scripts/ai_analyst.py`, `scripts/backfill_passes.sh`.
* **219 test nuovi** (da 293 a 512).

---

## Parte 3 — Problemi aperti

Questi non sono dettagli: sono le cose da sapere **prima** di pensare ai soldi
veri.

### 1. Il bot oggi è fermo, e non riparte da solo

Dopo il reset del registro, il backfill ha prodotto **9 coppie con 1 passaggio su
1200 valutate (0,75%)**. Servono 3 passaggi per validare, e la copertura richiesta
è 35% dell'universo. Anche se tutte e 9 arrivassero a 3 passaggi, sarebbero
9/135 ≈ **6,7%**: sotto soglia, quindi il bot resterebbe flat per sempre.

È stata aggiunta una via d'uscita — `OPTIMIZER_READY_MIN_PAIRS` (default 0,
disattivata) — che sblocca il trading su un numero minimo di coppie validate
invece che su una percentuale di universo. **Raccomandazione: 10.** Va deciso
dall'utente e messo nel `.env`, perché è un cambio di politica, non un bug fix.

### 2. Il tasso di passaggio dice qualcosa sulle strategie, non solo sul gate

0,75% di passaggi non è solo un problema di soglia. Con 1464 coppie valutate per
run e t=2.80, ci si aspettano **~3,7 strategie di puro rumore** che raggiungono
quella soglia a ogni run: servirebbe t≥3.20 per tenere i falsi positivi sotto 1.
Detto altrimenti: una parte di ciò che *passa* potrebbe essere fortuna, e ciò che
non passa è la maggioranza schiacciante. Il sistema oggi cerca un ago in un
pagliaio e trova soprattutto paglia.

### 3. La disparità gate ↔ paper non è ancora misurata sul nuovo registro

La **strada A** (replay dei vecchi trade) è chiusa: 30 coppie su 31 non erano
rigiocabili perché le specifiche generate vengono eliminate quando le coppie sono
purgate — 138 trade su 144 persi. *Lezione operativa: esportare
`discovered_strategies/specs` prima di qualunque reset futuro.*

La **strada B** (misura sui nuovi trade) richiede che il paper accumuli trade sul
registro nuovo, e il paper è fermo per il punto 1. La sequenza corretta è:
sbloccare il gate → accumulare trade → misurare.

### 4. Il timing d'ingresso non è stato quantificato

Tutte le altre ipotesi (indicatori, costi, funding, uscite) sono cadute: sono
moduli **condivisi**, non due implementazioni diverse. Resta il fatto che il gate
entra alla chiusura della barra e il bot al primo prezzo davvero eseguibile.
Lo strumento esiste (`BACKTEST_ENTRY_NEXT_OPEN` + `scripts.gate_vs_paper
--entry-timing`), il default è `false` finché l'effetto non è misurato. **Non è
ancora stato eseguito.**

### 5. L'ombra dell'LLM non ha ancora dati

`scripts/shadow_report.py` risponde alla sola domanda falsificabile ("i trade che
avrebbe vietato sono andati peggio?"), ma serve un campione. Il veto
(`AI_VETO_ENABLED`) resta **disarmato** finché quel numero non esiste. È corretto
che sia così, ed è anche il motivo per cui il passo 3 (selezione) non va
considerato in programma: una scelta dell'LLM non è riproducibile, quindi non
sarebbe mai backtestabile.

---

## Parte 4 — Limiti strutturali (non risolvibili con altro codice)

1. **Il paper non è il reale.** Nessuna simulazione modella il proprio impatto sul
   book. Il modello di costo è onesto (spread più largo sulle coin sottili), ma
   uno slippage vero su una coin sottile può essere peggiore di qualunque stima.
2. **Il profitto del gate viene dalla coda.** Con un vincitore che si ferma al
   primo gradino a +0,36R e un perdente a −1,09R, il pareggio richiede il 76% di
   operazioni vinte. Il PF 1.514 al 50% di vittorie esiste **solo** perché ~15%
   dei trade arriva a 5R. Se la coda non si ripresenta nel futuro, il sistema
   perde — e nessun test può garantire che si ripresenti.
3. **Il campione di validazione è piccolo su alcune coin.** L'analisi di
   `gen_472f85b8` su BIRB ha mostrato un holdout che poggiava su **7 trade**: un
   numero su cui non si può fondare niente.
4. **La leva amplifica anche gli errori di modello.** Ogni imprecisione della
   simulazione va moltiplicata per la leva quando arriva sul conto vero.
5. **Il sistema non conosce il mondo.** Non legge notizie, non sa di un hack, di
   un delisting annunciato o di un blocco normativo. Il rilevamento delisting
   guarda i prezzi *dopo* che è successo qualcosa, non prima.
6. **BTC è una coin su ~135.** Batterlo (o perderci contro) non dice quasi niente
   sul portafoglio: nel confronto del quarto trimestre BTC ha fatto −34,9% e il
   paniere equipesato delle coin tradate +14,5%. Il benchmark che conta è il
   paniere; il confronto con BTC resta perché è quello che tutti guardano.

---

## Cosa fare, in ordine

1. Decidere `OPTIMIZER_READY_MIN_PAIRS` (raccomandato: 10) e far girare
   l'optimizer, altrimenti il resto non parte.
2. Far accumulare trade al paper sul registro nuovo.
3. Eseguire `scripts.gate_vs_paper --entry-timing` e chiudere il punto 4.
4. Quando ci sono trade: strada B (disparità gate ↔ paper) e
   `scripts/shadow_report.py`.
5. Solo dopo, e solo se i numeri reggono, parlare di soldi veri.

---

## Appendice — Il supervisore (automazione della taratura)

Aggiunto dopo la Fase 5, su richiesta esplicita: il sistema deve tarare i propri
parametri **da solo**, senza attendere un comando.

### Il vincolo che rende la cosa difendibile

Automatizzare "abbassa le soglie finché qualcosa passa" sarebbe il modo più rapido
di validare rumore. Il supervisore lo evita con un vincolo misurabile invece che
con la prudenza:

```
coppie fortunate attese al giorno  ≈  valutazioni × tasso_passaggio ^ conferme_efficaci
```

Il tasso di passaggio non è una stima: lo **misura l'autopsia** a ogni run. Le
conferme non contano come test indipendenti (finestre vicine vedono quasi gli
stessi dati): ognuna oltre la prima vale mezza
(`SUPERVISOR_CONFIRM_INDEPENDENCE`, dichiarato e modificabile).

Finché quel numero resta sotto il budget (default: **1 coppia fortunata al
giorno**), allentare è legittimo e si sa *di quanto*. Coi numeri attuali —
22.264 valutazioni, 8 passate, 3 conferme — le coppie fortunate attese sono ~0,02:
il gate è molto più severo di quanto il budget richieda, e c'è circa 7× di margine.
Quando il margine finisce, non si allenta più nulla nemmeno se non passa niente per
mesi: a quel punto il problema non è la soglia, ed è onesto dirlo.

### Cosa non può fare, mai

- scendere sotto i **pavimenti** (ognuno con scritto il motivo per cui esiste);
- toccare l'**holdout**, la robustezza `pf_ex_top`, i dati sintetici, la parità col
  backtest, `DRY_RUN`, i limiti di rischio hard;
- **abbassare** il numero di conferme: può solo alzarlo;
- allentare quando le candidate muoiono sull'**holdout** — lì il dato dice
  "funzionano dove le abbiamo scelte e non fuori", e allentare promuoverebbe
  proprio le sovradattate. La reazione è opposta: ridurre le estrazioni;
- toccare qualcosa mentre il **paper opera**: cambiare le regole a partita in corso
  renderebbe non interpretabile il confronto gate ↔ paper.

Muove **un parametro alla volta**, altrimenti al run successivo non si saprebbe
quale dei due ha prodotto l'effetto.

### L'anello si chiude in ore, non in settimane

Dopo un cambiamento il supervisore lancia `fast_gate` (rigioca la storia su tre
finestre) se sono passati abbastanza giorni senza validazioni e il cooldown è
scaduto. Così il parametro modificato viene **giudicato dai dati in poche ore**
invece che dopo tre settimane. Senza questo, ogni modifica sarebbe una scommessa.

### Dove si legge cosa ha deciso

`tuning.env` (scritto solo dal supervisore, mai il `.env` con le chiavi),
`supervisor/state` su Firebase, e la sezione "Supervisore" in `docs/state.md`, che
è committata: il *perché* di ogni soglia resta leggibile a mesi di distanza senza
entrare sulla VPS. Per tornare ai default: cancellare `tuning.env` e riavviare.
