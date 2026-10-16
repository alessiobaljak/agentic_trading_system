# Guida pratica per la sessione di ricerca del protocollo 3 (BTC51)

Scritta dal coordinamento il 16 ottobre 2026. Non aggiunge regole al protocollo (`research/PROTOCOLLO_3.md`
vale sempre per primo): spiega come usare gli strumenti e come lavorare con il guardiano senza farsi
rifiutare comandi innocui. Raccoglie le esperienze pratiche delle sessioni precedenti, senza i loro risultati.

## 1. Il guardiano

Il guardiano (`research/src/guardiano.py`) si accende quando esiste il marcatore `research/.sessione`. Con il
marcatore `{"tipo": "campagna", "simbolo": "BTC51"}` la sessione vede solo: `research/PROTOCOLLO_3.md`, gli
strumenti in `research/src/` (in sola lettura), `research/config/parametri_3.yaml`, `bot_3.md`, questa guida e
`percorsi_vietati.txt` (in sola lettura), la propria cartella `research/campagne/BTC51/`, i dati in
`research/data/insample/BTCUSDT/`, `CLAUDE.md` e `.gitignore` (in sola lettura). Tutto il resto e' vietato.

Il guardiano legge la **forma** dei comandi, non le intenzioni. Forme che vengono rifiutate e come evitarle:

- **File e testi si scrivono con lo strumento di scrittura dei file**, mai con heredoc, `echo ... >`,
  `python3 -c`, `sed -i` o `awk`.
- **Niente variabili della shell, `$?`, `$(...)`, `2>&1`, cicli `for`/`until`, asterischi.** I comandi restano
  semplici; quello che serve si fa con uno script Python nella cartella `research/campagne/BTC51/codice/`,
  lanciato con `python3 research/campagne/BTC51/codice/<nome>.py`.
- **Percorsi assoluti dalla radice del repository**, senza `cd` nella cartella della campagna, senza `..`,
  senza `git -C`, senza `find .`. Non nominare file fuori dai percorsi ammessi, nemmeno per elencarli.
- **Git:** `fetch`, `pull` e `push` solo con il nome del proprio branch (`research/campagna/BTC51`); la storia
  dei commit solo per la propria cartella (`git log -- research/campagne/BTC51/`, senza `-p`); `git diff`
  solo contro HEAD e con un percorso; niente merge, rebase, cherry-pick, revert, show, checkout di altri branch.
- **Il messaggio di commit si scrive in un file** dentro `research/data/insample/BTCUSDT/` (ammesso e fuori da
  git), subito prima del commit, e si passa con `git commit -F <file>`. Mai `-m` con un indirizzo web dentro.
- **L'uscita dei comandi lanciati in background non si puo' leggere** (sta in una cartella temporanea fuori
  dai percorsi ammessi). Ogni script lungo scrive da solo l'avanzamento e l'esito in un file della propria
  cartella o in `research/data/insample/BTCUSDT/`, e la sessione legge quel file. Per aspettare la fine si usa
  un piccolo script che aspetta una parola nel file, oppure si lancia in primo piano con un tempo massimo lungo.
- **Le pagine web** si aprono solo dai siti di pubblicazioni scientifiche elencati nel guardiano (non
  Wikipedia: le sue pagine sono aggiornate a oggi). Le ricerche sul web non possono nominare questo
  repository, GitHub o i branch del protocollo.
- Un rifiuto del guardiano **non si aggira**: si registra nel log e, se blocca il lavoro, si chiede all'utente.

## 2. Il primo avvio

1. Apri il branch `research/campagna/BTC51` (il coordinamento l'ha gia' creato e pushato):
   `git fetch origin research/campagna/BTC51` e `git checkout -b research/campagna/BTC51 origin/research/campagna/BTC51`.
2. Solo quando `git branch --show-current` stampa `research/campagna/BTC51`, scrivi il marcatore
   `research/.sessione` (non e' in git) con lo strumento di scrittura dei file.
3. Se mancano, installa le librerie: `python3 -m pip install numpy scipy pyyaml pytest`.
4. Lancia i test: `python3 -m pytest research/src/tests/test_guardiano_btc51.py research/src/tests/test_dati_btc51.py -q -p no:cacheprovider`.
5. Fai il primo commit e `git push -u origin research/campagna/BTC51` nei primi minuti: la macchina della
   sessione e' temporanea. Se il push fallisce, STOP e avvisa l'utente.

## 3. Gli strumenti del protocollo 3 (in sola lettura)

- `research/src/dati.py`: `scarica_periodo(simbolo, tipo, intervallo, inizio, fine, verifica_checksum=True)`
  scarica i file mensili (tipi `klines`, `markPriceKlines`, `fundingRate`); `serie_3("BTCUSDT", timeframe,
  inizio, fine)` carica una serie pronta per il motore (last e mark allineati, funding); `fatti_passo1_3()` da'
  i conteggi del Passo 1 che riguardano anche la validazione, senza prezzi; `calcola_impronte` e
  `registra_impronte` per le impronte dei file. Il caricatore rifiuta da solo le date dal 2022-10-01 senza il
  via libera alla validazione (regola 2) e dal 2024-01-01 senza l'apertura del vault (regola 1).
- `research/src/catalogo3.py`: una variante e' un dizionario con gli elementi della sezione 7.1 (esempio
  nella docstring del modulo); `normalizza(variante)` controlla che usi solo il catalogo; `compila(variante,
  serie)` calcola segnali e livelli.
- `research/src/motore3.py`: `stima_trade(compilata, Regole(), inizio, fine)` e' la stima della 8.4 (solo
  conteggi); `esegui` e `metriche` il backtest della sezione 9; `test_troncamento` la 9.8.
- `research/src/statistica3.py`: `fase2(variante, serie, inizio, fine)` e' la Fase 2 completa (metriche,
  1.000 entrate casuali, p-value, soglie); `fase4(...)` le undici verifiche; `supera_validazione`,
  `supera_vault`, `asticella_vault` le soglie della sezione 10.3 e 10.4.
- Gli indici `inizio` e `fine` sono posizioni nella serie: si trovano con `numpy.searchsorted(serie.ts, ...)`
  sui millisecondi UTC delle date del periodo.
- Gli strumenti non si modificano. Se uno sembra sbagliato, o un test di `research/src/tests/` fallisce,
  STOP: lo si scrive nel log e all'utente, e lo corregge il coordinamento (che poi rifa' il collaudo,
  sezione 13bis.5).

## 4. Il log e i lotti

- Le varianti si scrivono come file JSON in `research/campagne/BTC51/codice/` e si provano con uno script che,
  per ogni variante, registra nel log, poi stima o testa, poi scrive il risultato: in serie, cosi' nessun
  calcolo resta fuori dal log e gli id restano progressivi.
- Prima di contare o testare, una prova del codice che stampa solo «ok» o l'errore.
- L'orario di ogni voce del log lo prende lo script dall'orologio della macchina, mai a memoria.
- Gli id delle voci si controllano prima di scrivere (uno script rilanciato non deve ripetere un id).
- Una sessione puo' finire: quando ti fermi, lascia tutto committato e pushato e scrivi nel log una voce
  `nota` con il punto da cui riprendere, poi aggiorna `STATO.md`.
