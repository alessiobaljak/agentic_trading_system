# Guida pratica per la sessione di ricerca del protocollo 4 (LINK6)

Scritta dal coordinamento il 17 ottobre 2026. Non aggiunge regole al protocollo (`research/PROTOCOLLO_4.md`
vale sempre per primo): spiega come usare gli strumenti e come lavorare con il guardiano senza farsi
rifiutare comandi innocui. Raccoglie le esperienze pratiche delle sessioni precedenti, senza i loro risultati.

## 1. Il guardiano

Il guardiano (`research/src/guardiano.py`) si accende quando esiste il marcatore `research/.sessione`. Con il
marcatore `{"tipo": "campagna", "simbolo": "LINK6"}` la sessione vede solo: `research/PROTOCOLLO_4.md`, gli
strumenti in `research/src/` (in sola lettura), `research/config/parametri_4.yaml`, `bot_4.md`, questa guida e
`percorsi_vietati.txt` (in sola lettura), la propria cartella `research/campagne/LINK6/` (le cartelle
`risposte/` e il via libera alla validazione in sola lettura), i dati in `research/data/insample/LINKUSDT/`,
`CLAUDE.md` e `.gitignore` (in sola lettura). Tutto il resto e' vietato, compresi i dati delle monete di
controllo: il caricatore li rifiuta (regola 10).

Il guardiano legge la **forma** dei comandi, non le intenzioni. Forme che vengono rifiutate e come evitarle:

- **File e testi si scrivono con lo strumento di scrittura dei file**, mai con heredoc, `echo ... >`,
  `python3 -c`, `sed -i` o `awk`.
- **Niente variabili della shell, `$?`, `$(...)`, `2>&1`, cicli `for`/`until`, asterischi.** I comandi restano
  semplici; quello che serve si fa con uno script Python nella cartella `research/campagne/LINK6/codice/`,
  lanciato con `python3 research/campagne/LINK6/codice/<nome>.py`.
- **Percorsi assoluti dalla radice del repository**, senza `cd` nella cartella della campagna, senza `..`,
  senza `git -C`, senza `find .`. Non nominare file fuori dai percorsi ammessi, nemmeno per elencarli.
- **Git:** `fetch`, `pull` e `push` solo con il nome del proprio branch (`research/campagna/LINK6`); la storia
  dei commit solo per la propria cartella (`git log -- research/campagne/LINK6/`, senza `-p`); `git diff`
  solo contro HEAD e con un percorso; niente merge, rebase, cherry-pick, revert, show, checkout di altri branch.
- **Il messaggio di commit si scrive in un file** dentro `research/data/insample/LINKUSDT/` (ammesso e fuori da
  git), subito prima del commit, e si passa con `git commit -F <file>`. Mai `-m` con un indirizzo web dentro.
- **L'uscita dei comandi lanciati in background non si puo' leggere** (sta in una cartella temporanea fuori
  dai percorsi ammessi). Ogni script lungo scrive da solo l'avanzamento e l'esito in un file della propria
  cartella o in `research/data/insample/LINKUSDT/`, e la sessione legge quel file. Per aspettare la fine si usa
  un piccolo script che aspetta una parola nel file, oppure si lancia in primo piano con un tempo massimo lungo.
- **Le pagine web** si aprono solo dai siti di pubblicazioni scientifiche elencati nel guardiano (non
  Wikipedia: le sue pagine sono aggiornate a oggi). Le ricerche sul web non possono nominare questo
  repository, GitHub o i branch del protocollo.
- Un rifiuto del guardiano **non si aggira**: si registra nel log e, se blocca il lavoro, si chiede all'utente.

## 2. Il primo avvio

1. Apri il branch `research/campagna/LINK6` (il coordinamento l'ha gia' creato e pushato):
   `git fetch origin research/campagna/LINK6` e `git checkout -b research/campagna/LINK6 origin/research/campagna/LINK6`.
2. Solo quando `git branch --show-current` stampa `research/campagna/LINK6`, scrivi il marcatore
   `research/.sessione` (non e' in git) con lo strumento di scrittura dei file.
3. Se mancano, installa le librerie: `python3 -m pip install numpy scipy pyyaml pytest`.
4. Controlla le versioni (regola 11): `python3 --version` e `python3 -c "import numpy; print(numpy.__version__)"` devono
   dare esattamente quelle di `parametri_4.yaml` (`versioni`). Se no, STOP.
5. Lancia i test: `python3 -m pytest research/src/tests/test_guardiano_link6.py research/src/tests/test_dati_link6.py research/src/tests/test_statistica4.py -q -p no:cacheprovider`.
6. Fai il primo commit e `git push -u origin research/campagna/LINK6` nei primi minuti: la macchina della
   sessione e' temporanea. Se il push fallisce, STOP e avvisa l'utente.

## 3. Gli strumenti (in sola lettura)

- `research/src/dati.py`: `scarica_periodo(simbolo, tipo, intervallo, inizio, fine, verifica_checksum=True)`
  scarica i file mensili (tipi `klines`, `markPriceKlines`, `fundingRate`); `serie_4("LINKUSDT", timeframe,
  inizio, fine)` carica una serie pronta per il motore (tutte le candele last, il mark dove c'e', il funding
  vero e quello riportato a 8 ore per i segnali, la serie che finisce all'ultima candela con scambi);
  `serie_4_con_conteggi` da' anche i conteggi; `fatti_passo1_3("LINKUSDT")` da' i conteggi del Passo 1 che
  riguardano anche la validazione, senza prezzi; `calcola_impronte` e `registra_impronte` per le impronte. Il
  caricatore rifiuta da solo le date dal 2022-10-01 senza il via libera alla validazione (regola 2), dal
  2024-01-01 senza l'apertura del vault (regola 1) e ogni moneta diversa da LINKUSDT.
- `research/src/catalogo3.py`: una variante e' un dizionario con gli elementi della sezione 7.1 (esempio
  nella docstring del modulo); `normalizza(variante)` controlla che usi solo il catalogo; `compila(variante,
  serie)` calcola segnali e livelli.
- `research/src/motore3.py`: `stima_trade(compilata, regole, inizio, fine)` e' la stima della 8.4 (solo
  conteggi); `esegui` e `metriche` il backtest della sezione 9; `test_troncamento` la 9.8.
- `research/src/statistica4.py` (protocollo 4): `REGOLE_LINK`, `COSTI_LINK` e `COSTI_DOPPI_LINK` sono le regole
  e i costi di LINKUSDT (margine 1%, slippage 0,02%): si usano sempre al posto di quelli predefiniti del
  motore, che sono di BTC. `fase2_4(variante, serie, inizio, fine)` e' la Fase 2 completa; `fase4_4(variante,
  serie, inizio, fine, serie_di, serie_giornaliera)` le verifiche della Fase 4 tranne la 12 (con 1, 3, 3bis e
  4 nella forma del protocollo 4).
- `research/src/statistica3.py`: `supera_validazione`, `supera_vault`, `asticella_vault` e il resto delle
  regole statistiche della sezione 10, che non cambiano. Le sue `fase2` e `fase4` hanno i costi di BTC: per
  LINKUSDT non si usano.
- `research/src/controllo4.py` e' lo strumento del coordinamento per le monete di controllo: la sessione di
  ricerca non lo usa (non ha i dati).
- Gli indici `inizio` e `fine` sono posizioni nella serie: si trovano con `numpy.searchsorted(serie.ts, ...)`
  sui millisecondi UTC delle date del periodo.
- Gli strumenti non si modificano. Se uno sembra sbagliato, o un test di `research/src/tests/` fallisce,
  STOP: lo si scrive nel log e all'utente, e lo corregge il coordinamento (che poi rifa' il collaudo,
  sezione 13bis.5).

## 3bis. Le richieste al coordinamento (monete di controllo)

Per la verifica 12, per il controllo di una variante nata dalla Fase 3 e per la validazione sulle monete di
controllo (regola 10, sezione 12):

1. registra la verifica nel log (`tipo_test` `verifica`, con `verifica_di`, e `monete_di_controllo: true`);
2. scrivi `research/campagne/LINK6/richieste/<ID>.json` con `{"id": "<ID>", "variante": "<id della variante>",
   "tipo": "verifica_12" | "fase3" | "validazione"}` (per `fase3` anche `"confronto_con": "<id>"`);
3. committa, fai il push e scrivi all'utente in una riga che aspetti il coordinamento;
4. il coordinamento risponde in `research/campagne/LINK6/risposte/<ID>.json` sul tuo branch (`git pull`), con
   `{"supera": true}` o `{"supera": false}` (per la validazione anche i numeri); registra il risultato nel log.

Mentre aspetti puoi lavorare ad altre varianti, ma non costruire su quella in attesa.

## 4. Il log e i lotti

- Le varianti si scrivono come file JSON in `research/campagne/LINK6/codice/` e si provano con uno script che,
  per ogni variante, registra nel log, poi stima o testa, poi scrive il risultato: in serie, cosi' nessun
  calcolo resta fuori dal log e gli id restano progressivi.
- Prima di contare o testare, una prova del codice che stampa solo «ok» o l'errore.
- L'orario di ogni voce del log lo prende lo script dall'orologio della macchina, mai a memoria.
- Gli id delle voci si controllano prima di scrivere (uno script rilanciato non deve ripetere un id).
- Una sessione puo' finire: quando ti fermi, lascia tutto committato e pushato e scrivi nel log una voce
  `nota` con il punto da cui riprendere, poi aggiorna `STATO.md`.
