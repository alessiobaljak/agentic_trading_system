# Revisione della fase 1 del conto vero, secondo giro (modifiche non committate, 8 nov 2026)

Revisore: `live-path-reviewer`. Oggetto: lo stesso `git diff HEAD -- bot/portafoglio/demo_binance.py scripts/state_snapshot.py
tests/test_demo_binance.py dashboard/app/components/PaperBot.tsx` del primo giro (`reviews/reports/2026-11-08-fase1-conto-vero.md`), con
le correzioni dei problemi 40-46 e le decisioni 2, 3, 4 e 5 prese dalla sessione principale. Base `4f866a1`. Ignorati `research/` e `reviews/`.
Per vedere solo il secondo giro ho confrontato il file con la copia del primo giro (`scratchpad/fase1/nuovo_test_vecchi/bot/`): circa
550 righe di differenza in `demo_binance.py`. Fotografia e dashboard sono uguali al primo giro.

### Riepilogo e verdetto

**REQUEST CHANGES, per un solo punto breve.**
- **Il problema Alto 40 è chiuso.** Con un 429 che dura durante lo stop il demo resta fermo e chiude il resto dopo l'attesa (prova p1),
  da fermo i tentativi crescono e l'allarme arriva (p3), il pulsante della dashboard si consuma solo dopo (p17).
- Chiusi anche 41, 43, 44, 45, 46 e il 42 come scelto. Non ci sono problemi Bloccanti né Alti.
- **Resta un problema Medio, introdotto in questo giro (47).** Con un capitale nuovo in attesa e le posizioni aperte, lo stop perde il
  pavimento del 65% del capitale di partenza. La decisione 2 («perdita della fase entro il 35%») allora non vale fino alla mezzanotte:
  nella prova p11 lo stop scende da 6.500 a 4.615 e il conto a 6.000 non si ferma.
- La correzione è di una riga, più un test. Non è peggio del codice committato (che il pavimento non lo ha proprio), ma è un buco in
  una protezione appena decisa, quindi la chiedo prima del commit.

| Problema | Esito | Evidenza |
|---|---|---|
| 40 (Alto: stop che non resta fermo) | **chiuso** | `demo_binance.py:725-756` (fermo salvato a `:739` prima delle chiusure), `:956-968`, `:1015-1018`; test `tests/test_demo_binance.py:1263`, `:1287`; prove p1, p3, p17 |
| 41 (capitale oltre il saldo) | **chiuso** | `:574-576`, `:603-611`, `:1108`; test `:1306`; prova p10 (ordini al 100% del saldo vero, prima 197%) |
| 42 (pesi vuoti) | **chiuso come scelto**: niente ordini, allarme, posizioni di ieri tenute | `:136-137`; test `:1406`; prova p9 |
| 43 (chiusure oltre la quantità massima, monete senza filtri) | **chiuso** (resto minimo nel 49) | `:204-214`, `:1021-1035`, allarme `monete_senza_filtri` in `ribilancia`; test `:1541`, `:1552` |
| 44 (attesa senza tetto, errori d'orario) | **chiuso** | 429 con tetto di 10 minuti, 418 per intero o 10 minuti (`:843-865`); -1021 con l'ora di Binance e un solo nuovo tentativo (`:431-440`, `:441-...`); test `:1326`, `:1343`, `:1365` |
| 45 (data nel futuro) | **chiuso** | `:805-807`, `_decisione_da_non_eseguire` `:867-...`; test `:1386` |
| 46 (allarmi che restano, «riparti» perso, confine dell'ora) | **chiuso** | `:733` e tick per `ordini`, `:772-776`, `:929`, `:1076-...` (soglia 45 minuti); test `:1424-1475` |

Decisioni della sessione principale:
- **2** (stop al più alto fra il 65% del massimo e il 65% del capitale della fase): fatta (`:217-235`, `:917`, `:1350`). Il limite di
  perdita ora è il 35% del capitale della fase (prova p5b: dopo un «riparti» a 6.700 lo stop scatta a 6.499). Il buco è il 47.
- **3** (dopo un «riparti» il conto resta vuoto fino alla decisione dopo): fatta (`:929-939`, `:821-823`, `_giorno_g1` `:1037-...`;
  test `:1499`). Il caso del conto non vuoto è nel 48.
- **4** (limiti fissi nel codice, con un test di guardia): fatta (test `:1520`).
- **5** (moneta sopra il 60%): invariata, fa saltare la decisione.

Test: suite intera `2616 passed, 1 deselected in 166.03s`; firme (con `PYTHONPATH=…/scratchpad/cr`) e test di guardia dei limiti
fissi e dell'avvio `33 passed`. I 20 test nuovi o cambiati del secondo giro, lanciati sul codice del primo giro, **falliscono tutti e 20**:
sono veri. I cambi ai test vecchi sono legittimi:
- `_rifiutata` passa da -1021 a -1000, perché il -1021 ora si riprova;
- il test del pulsante e quello del 26 seguono la decisione 3; il secondo ribilancio dello stesso giorno ora passa dal margine separato.

`bot/risk/hard_limits.py`, `bot/config.py`, `bot/main.py`, `bot/execution`, `firebase/`, `ops/`: invariati.

Sulla nota dell'implementatore: anche nel primo giro le prove giravano con `PYTEST_CURRENT_TEST=x` (comando nel primo rapporto e in
`reviews/INDEX.md`). Quindi leggevano il capitale scelto dalla prova, non `ops/demo_binance_capitale`. Gli esiti di allora (p1, p3, p9,
p10) erano quelli del codice del primo giro: sono cambiati ora grazie alle correzioni.

### Oggetto (branch, commit, file toccati, invarianti coinvolti)

- Branch `claude/brave-albattani-1b12fv`, base `4f866a1`, modifiche non committate.
- File: `bot/portafoglio/demo_binance.py` (+639 −102 su HEAD), `tests/test_demo_binance.py` (+788), `scripts/state_snapshot.py` (+6),
  `dashboard/app/components/PaperBot.tsx` (+13).
- Invarianti coinvolti:
  - stop sul conto: soglia nuova al pavimento, fermo salvato prima delle chiusure;
  - «riparti»: pavimento, attesa della decisione dopo;
  - capitale contro il saldo;
  - limiti di Binance: tetto, blocco dell'indirizzo, ora;
  - chiusure in pezzi;
  - pesi vuoti e date nel futuro.

### Checklist A–F

**A. Limiti fissi e interruttori**
- `hard_limits.py` invariato: **OK**.
- Nessun limite spostato fuori dal codice: **OK**. Costanti nuove `:91`, `:97-99`, fissate dal test `:1520` insieme alle altre del
  demo. Restano fuori da `hard_limits.py`, per scelta (decisione 4).
- Parametri della dashboard: **NON APPLICABILE** (vecchio bot, problema 17 invariato).
- Pulsante senza Firebase: **OK**. Il comando a file si riprova dopo un 418 (p2b: chiuso dopo i 10 minuti di blocco). Il comando
  della dashboard resta vero finché il fermo non è salvato (p17).
- Stop sul conto: **PROBLEMA** 47 (pavimento perso con un capitale in attesa) e 48 (casi di confine del «riparti»).

**B. Ordini**
- Passi, minimi e massimi letti da Binance: **OK**. Chiusure in pezzi dentro `MARKET_LOT_SIZE` (`:1028-1035`), anche in
  `parti_da_zero` e nel margine separato. Oltre 20 pezzi il ventunesimo ordine porta tutto il resto ed è rifiutato (49).
- Identificativo riusato: **OK**. Un -1021 riprova con gli stessi parametri: l'ordine non era stato eseguito, e i limite e i resti
  hanno l'identificativo fisso.
- «Solo riduzione»: **OK** su ogni pezzo.
- Prezzo che attiva gli stop: **NON APPLICABILE**.
- Leva e margine: **OK**, come nel primo giro.
- Protezione di G1: stop sul conto e pulsante **OK**, salvo il 47. Stop per posizione assenti: decisione per Alessio, invariata.

**C. Stato e resilienza**
- Stato di Binance per primo: **OK**. Il fermo è sul file prima di ogni chiusura (`:739`). Il capitale si confronta con il valore vero
  letto da Binance (`:1108`).
- Flussi in tempo reale e candele chiuse: **NON APPLICABILE**.
- Errori delle interfacce: **OK**.
  - 429: ritentativi, poi al massimo 10 minuti senza richieste, con allarme.
  - 418: tutta l'attesa chiesta, 10 minuti se manca, e l'allarme dice fino a quando il bot non protegge il conto.
  - -1021: l'ora di Binance si rilegge e si riprova una volta.
  - Nessun ciclo infinito (`:441-...`: al massimo un nuovo tentativo per l'ora e 3 per i limiti).
  - Resto Basso: da fermo, con tutte le richieste limitate, i tentativi non crescono, perché si ferma prima la lettura del conto (p13,
    uguale al codice committato). Si vede l'allarme dei limiti.
- Firebase che non risponde: **OK**. La lettura degli allarmi all'avvio è protetta (`:772-776`).
- Orologio: **OK in parte**. L'orologio della macchina è sempre quello di `systemd-timesyncd`, ma ora uno scarto si corregge da solo.

**D. Separazione fra paper, demo e conto vero**
- **OK**. Anche `/fapi/v1/time` passa da `_url` (`:434`).

**E. Segreti e sicurezza**
- **OK**. Nessuna chiave nei file. La lettura dell'ora è senza firma; i messaggi passano da `senza_firma`.
- Chiavi senza prelievo e limitate all'indirizzo, regole di Firebase pubblicate: **da confermare con Alessio** (invariato).

**F. Test**
- Comandi:
  - `python3 -m pytest tests/ -q -p no:cacheprovider --deselect tests/test_demo_binance.py::test_firma_dei_tre_tipi_di_chiave` →
    `2616 passed, 1 deselected in 166.03s`;
  - firme e guardia (`test_risk.py`, `test_sizing.py`, `test_sicurezza_avvio.py`) → `33 passed`.
- Test veri: sul codice del primo giro falliscono tutti i 20 test nuovi o cambiati.
- Non coperti: capitale in attesa con posizioni aperte dopo un «riparti» (47); «riparti» con il conto non vuoto, e al pavimento
  esatto (48); limiti su tutte le richieste da fermo (p13).
- Dashboard: compilazione non verificata (lettura di `dashboard/node_modules` vietata).

Prove a mano (`scratchpad/fase1/prove_fase1.py`, `prove_giro2.py`, `prova_bordi.py`, `prova_15.py`, tutte con `PYTEST_CURRENT_TEST=x`):

| Prova | Caso | Esito ora |
|---|---|---|
| p1 | Stop a −36%, 429 che dura su BUSDT, poi −34% | fermo subito (1 chiusa), BUSDT chiuso dopo l'attesa |
| p2b | Chiudi tutto da file, 418 senza attesa | fermo subito, tutto chiuso dopo i 10 minuti |
| p3 | Da fermo, 429 che dura sulla chiusura di BUSDT | 6 tentativi in 10 minuti, allarme del fermo |
| p5b | 10.000 → stop a 6.450 → «riparti» a 6.700 → 6.499 | stop «−35,0% dal capitale di partenza della fase» |
| p6, p7, p8, p4 | massimo dal file vecchio, ribilancio interrotto, età, identificativo | come nel primo giro, corretti |
| p9 | Pesi vuoti | niente ordini, posizioni tenute, allarme |
| p10 | Conto 5.000, capitale 9.999 | rifiutato, ordini al 100% del saldo vero |
| p11 | Stop e «riparti» nella stessa fase, riapertura, poi capitale 2.000 nel file | stop da 6.500 a 4.615; a 6.000 nessuno stop (47) |
| p12 | «Riparti» con il conto a 6.500 su 10.000 | accettato, al minuto dopo di nuovo fermo (48) |
| p13 | Da fermo, 429 su ogni richiesta per 30 minuti | tentativi fermi a 1, solo l'allarme dei limiti |
| p16 | «Riparti» con BUSDT −20 rimasto aperto | ripartito, BUSDT −20 tenuto 9 ore, nessun allarme (48) |
| p17 | Pulsante della dashboard con 429 su BUSDT | fermo salvato, comando consumato dopo, tutto chiuso |
| bordi | Data 99999 nel file; `Retry-After: 86400` su un 429 | nessun ordine e allarme, poi la decisione vera; attesa di 10 minuti |

### Problemi

**Problema 47 — Medio (introdotto in questo giro) — `demo_binance.py:217-221` (`_pavimento`) usato da `livello_di_stop` `:223-228`:
con un capitale nuovo in attesa lo stop perde il pavimento anche con le posizioni aperte.**
- `_pavimento` vale 0 quando c'è `capitale_in_attesa`. Serve al «riparti» e al conto vuoto che aspetta la fase nuova: senza, lo stop
  riscatterebbe subito sul conto vuoto e la fase nuova non partirebbe mai. Ma vale anche per lo stop mentre la fase vecchia ha ancora
  le posizioni aperte.
- Scenario (prova p11):
  - conto da 10.000, massimo 11.000, stop a 7.100;
  - «riparti» a 7.100, riapertura alla decisione dopo; lo stop è al pavimento, 6.500;
  - durante il giorno il proprietario scrive un capitale nuovo (2.000) nel file: resta in attesa fino alla mezzanotte e lo stop scende
    a 4.615 (−35% da 7.100);
  - il conto va a 6.000 e non si ferma.
- Fino alla mezzanotte la fase può perdere fino a circa il 54% del capitale di partenza invece del 35% deciso.
- Servono tre cose insieme (stop e «riparti» nella stessa fase, un capitale nuovo scritto di giorno, un altro calo forte prima della
  mezzanotte): per questo Medio e non Alto. Non è peggio del codice committato, ma la decisione 2 non vale in uno stato raggiungibile.
- Correzione suggerita: in `livello_di_stop` togliere il pavimento solo quando il conto aspetta la fase nuova, per esempio
  `0.0 if st.get("capitale_in_attesa") and st.get("riparti_attende_g1") else …`. In `_sopra_il_pavimento` la deroga resta com'è.
- Test: p11 (con le posizioni aperte e il capitale in attesa lo stop resta a 6.500). Per il caso del «riparti» con un capitale nuovo
  e il conto vuoto c'è già `tests/test_demo_binance.py:1209`: deve restare verde.

**Problema 48 — Basso — `demo_binance.py:925-939`, `:917` con `:984`: due casi di confine del «riparti».**
- **Conto non vuoto** (p16): il «riparti» si accetta anche se una chiusura è fallita e una posizione è rimasta, perché il controllo
  viene prima della richiusura del minuto. Con la decisione 3 il demo smette di richiudere e tiene quella posizione da sola fino alla
  decisione dopo (9 ore nella prova), senza allarme. Prima il ribilancio immediato la riportava nei pesi.
  - Correzione: accettare il «riparti» solo con `fermo["vuoto"]` segnato. Altrimenti allarme «riparti rimandato: il conto non è
    vuoto», il fermo resta e le chiusure continuano.
- **Pavimento esatto** (p12): il «riparti» vale con il conto uguale al pavimento (`>=`, `:984`). Lo stop scatta con il conto uguale
  o sotto (`<=`, `:917`), quindi al minuto dopo il demo è di nuovo fermo. Sul conto vuoto non costa niente, ma confonde.
  - Correzione: lo stop al pavimento con `<`, oppure il «riparti» con `>`.

**Problema 49 — Basso — testi e resti minori.**
- La dashboard (`PaperBot.tsx:165`) e la fotografia (`scripts/state_snapshot.py:639`) scrivono «Stop sul conto a −35% dal massimo»
  anche quando `stop_a` è il pavimento del capitale (decisione 2). Correzione: «si chiude tutto sotto $X (il più alto fra −35% dal
  massimo e il 65% del capitale di partenza)».
- `PEZZI_MASSIMI` (`:99`) dice «al massimo 20 ordini», ma `pezzi_di_chiusura` (`:204-214`) ne manda un ventunesimo con tutto il
  resto, che Binance rifiuta se è oltre il massimo. Correzione: fermarsi a 20 pezzi; il resto si richiude al minuto dopo, dalla
  posizione vera.
- Da fermo, con tutte le richieste limitate, i tentativi non crescono (p13, come sul codice committato): l'allarme del fermo arriva
  solo quando una lettura riesce. Si vede quello dei limiti. Va bene così; da sapere.
- Scelta dell'implementatore, non fatta: la chiusura per margine separato interrotta da un limite lascia la moneta chiusa fino alla
  decisione dopo (`controlla_margine` `:1122-...`). Chiude, non apre: accettabile; il portafoglio resta senza quella moneta per al
  massimo un giorno.

Stato dei problemi del primo giro: 40, 41, 43, 44, 45, 46 chiusi; 42 chiuso come scelto (decisione per Alessio). Restano aperti dai
rapporti del 7 nov: 11 (avvisi sul telefono), 14, 17-20, 24, 33 (senza uscita automatica), 34, 35.

### Invarianti modificati

Nessun valore di `hard_limits.py` cambiato. Rispetto al primo giro:
- **stop sul conto**: si chiude tutto sotto il più alto fra −35% dal massimo e il 65% del capitale di partenza della fase, tranne con
  un capitale nuovo in attesa (47). Il fermo si salva prima di ogni chiusura;
- **«riparti»**: il comando della dashboard si consuma dopo il controllo del pavimento. Dopo un «riparti» il conto resta vuoto fino
  alla decisione di G1 dopo;
- **capitale**: non oltre il valore vero del conto, controllato anche alla mezzanotte prima di chiudere niente;
- **pesi vuoti o data nel futuro**: niente ordini, allarme;
- **limiti di Binance**: 429 con al massimo 10 minuti di attesa; 418 per tutta l'attesa (10 minuti se manca); -1021 con l'ora di Binance;
- **chiusure**: in pezzi entro la quantità massima a mercato (fino a 20 più il resto);
- **costanti nuove**: `ATTESA_418_SENZA_RETRY_S = 600`, `ATTESA_LIMITE_TETTO_S = 600`, `PEZZI_MASSIMI = 20`, tutte fissate da un
  test di guardia (`tests/test_demo_binance.py:1520`).

### Decisioni per Alessio

1. **Riavvio**: dopo la correzione del 47 per me si può, e la decisione resta tua. Il 48 è consigliato, ma non è una condizione.
2. **Le scelte della sessione principale da confermare**:
   - lo stop al più alto fra −35% dal massimo e il 65% del capitale della fase: la perdita di una fase resta entro circa il 35%;
   - dopo un «riparti» si aspetta la decisione di G1 della mezzanotte;
   - i limiti restano nel codice del demo, con un test di guardia;
   - una moneta sopra il 60% fa saltare la decisione.
3. **Quando G1 non decide bene** (decisione vecchia di oltre 26 ore, pesi vuoti, pesi fuori dai limiti) il demo **tiene le posizioni
   di ieri** e scrive un allarme. Il paper invece resta vuoto con i pesi vuoti: per quei giorni il confronto settimanale fra demo e
   paper non torna. Vuoi tenere (oggi) o chiudere tutto come il paper?
4. In sospeso, invariate:
   - stop per posizione su Binance (oggi, con l'indirizzo bloccato, resta solo la liquidazione: ora lo dice l'allarme);
   - avvisi sul telefono;
   - `DRY_RUN` falso che ferma anche il demo;
   - chiavi vere non limitate all'indirizzo, prelievo da confermare;
   - regole di Firebase mai pubblicate;
   - tetto del capitale a 10.000 (il conto vero partirà da circa 280).

### Domande aperte

1. La deroga di `_pavimento` con un capitale in attesa serve solo al «riparti» con il conto vuoto, o c'è un altro caso che vi ha
   portato a metterla anche nello stop? Se non c'è, va limitata come nel 47.
2. Il «riparti» con il conto non ancora vuoto deve essere accettato? Con la decisione 3 la posizione rimasta resta da sola fino alla
   mezzanotte (48).
