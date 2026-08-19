# Istruzioni per Claude su questo repo

Chi legge questo file sta rispondendo a una domanda arrivata dalla tab **Claude**
della dashboard (o direttamente da una issue). Chi scrive e' il proprietario, spesso
da un telefono e spesso senza poter lanciare comandi: la risposta dev'essere
autosufficiente.

## Cos'e' questo sistema

Bot di trading crypto autonomo, in **paper trading**. Gira su una VPS Hetzner, tiene
lo stato su Firebase, e la dashboard Next.js (Vercel) lo mostra. La ricerca delle
strategie e' un job separato (`scripts/optimize.py`, `scripts/discover_strategies.py`)
che gira ogni 3 ore e alimenta il registro `strategy_registry/validated`.

Il documento da leggere per primo e' **`docs/state.md`**: e' lo stato aggiornato, con
cosa e' fatto e cosa e' aperto. Poi `docs/architecture.md` per la mappa, e
`docs/audit_backtesting.md` per l'ultima revisione del motore di backtest.

## Regole che non si negoziano

* **`DRY_RUN` resta `true`.** Il sistema non ha mai toccato denaro vero e non deve
  iniziare senza una richiesta esplicita, ripetuta e consapevole del proprietario.
  Non e' un parametro di ricerca.
* **Non si lavora su altri branch.** Lo sviluppo va sul branch di default di questo
  repo. Non aprire pull request se non e' stato chiesto.
* **Mai un segreto in un commit.** Niente chiavi, token, `.env`, output di
  `git remote -v` o `git config --list` (il token puo' essere dentro l'URL del
  remoto). Un segreto finito in un repo pubblico e' compromesso per sempre, anche se
  il commit viene poi rimosso. **Questo repo e' pubblico.**
* **Il trailer dei commit** e' quello che trovi negli ultimi commit: copialo da li'
  invece di inventarlo.
* **Non dichiarare fatto cio' che non e' verificato.** Se i test non girano, dillo.
  Se una cosa e' stata saltata, dillo. Questa e' la regola che il proprietario ha
  chiesto piu' volte.

## Non hai accesso alla VPS — ma hai un canale

Non puoi entrare sulla macchina ne' leggere Firebase. Puoi pero' **chiedere alla VPS
di eseguire un comando** dal repo: si scrive un file in `ops/requests/`, l'agente
sulla macchina lo esegue contro una lista bianca locale e ricommitta la risposta in
`ops/results/` col nome corrispondente. Leggi `ops/README.md` prima di usarlo.

Regola pratica: se la domanda richiede di sapere cosa sta succedendo **adesso** sulla
macchina, metti in coda una richiesta, dillo nella risposta, e spiega che l'esito
arriva entro qualche minuto in `ops/results/`. Non inventare numeri.

Il battito della macchina e' in `ops/heartbeat.md`: se e' fermo da ore, la VPS o
l'agente sono giu', ed e' un'informazione che vale la pena dare subito.

## Come rispondere

* **In italiano**, e semplice. Il proprietario lo ha chiesto esplicitamente: niente
  gergo se una frase normale basta.
* **Prima la risposta, poi il perche'.** Se la risposta e' "no", che sia la prima
  parola.
* **Un numero va con la sua fonte.** "224 coppie a 1 pass" va bene se viene da un
  file o da un risultato ops; se viene da una stima, dillo.
* Se la domanda e' una richiesta di modifica al codice, falla davvero: leggi, cambia,
  lancia `python -m pytest tests/ -q`, committa. Poi riassumi cosa e' cambiato.
