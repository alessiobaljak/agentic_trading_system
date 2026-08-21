# `ops/` — il ponte fra il repo e la VPS

Serve a togliere il copia-incolla: una richiesta viene committata qui, la macchina
la esegue e ricommitta la risposta. Nessuna porta aperta, nessuna chiave su GitHub,
nessun runner esterno con accesso alla shell.

## Come funziona

1. **Richiesta** — un file in `ops/requests/`, ad esempio `20260814-autopsy.req`:
   ```
   autopsy
   ```
   La prima riga utile è la **chiave**; le righe successive, se ci sono, sono
   argomenti (uno per riga).

2. **Esecuzione** — `scripts/ops_agent.py` gira ogni minuto da un timer systemd,
   fa `git pull`, trova le richieste senza risposta, esegue e scrive in
   `ops/results/` un file con lo stesso nome (`.md`).

3. **Risposta** — l'agente committa e pusha. Chi ha chiesto la legge da git.

Il file di risposta **è** lo stato: se esiste, la richiesta è stata evasa. Niente
database da tenere allineato, e un riavvio non perde nulla.

## Perché è sicuro (e dove sta il controllo)

Questa macchina tiene le chiavi Binance e gestisce posizioni: un canale di comando
mal fatto sarebbe peggio del problema che risolve. Tre proprietà:

- **La lista bianca non sta nel repo.** Vive in `ops/allowlist`, sulla macchina, ed
  è ignorata da git. È la differenza fra *"esegue solo ciò che il proprietario ha
  approvato"* e *"esegue ciò che chiede chi scrive la richiesta"*. Se fosse
  versionata, chiunque possa committare potrebbe ampliarla e il controllo sarebbe
  finto.
- **Niente shell.** Il comando viene da `shlex.split` ed è eseguito senza shell:
  `;`, pipe e backtick non hanno alcun potere. Una richiesta può solo *nominare*
  una voce, mai comporre un comando.
- **Argomenti ristretti.** Ammessi solo dove la voce dichiara `+args`, e solo
  caratteri innocui. Un argomento sospetto ferma l'intera richiesta invece di
  essere ripulito in silenzio.

In più: timeout su ogni esecuzione, output troncato (testa e coda, così si vede sia
cosa è partito sia perché è finito), e una passata di oscuramento su tutto ciò che
somiglia a una chiave — un segreto finito in un repo è compromesso per sempre,
anche se il commit viene poi rimosso.

## Installazione

```bash
cp ops/allowlist.example ops/allowlist    # e adattala: è tua, non del repo
bash scripts/install_ops_agent.sh
```

## Aggiungere un comando

PRIMA DI AGGIUNGERE UNA VOCE, un vincolo che non e' ovvio: una richiesta **nomina**
una voce, non compone un comando. Quindi il comando scritto qui e' esattamente e per
sempre quello che verra' eseguito, e **un comando che pretende argomenti non potra'
mai riceverli** — la voce nasce morta. E' successo con `gate-vs-paper`, aggiunta dopo
un controllo statico troppo debole: usciva con l'usage di argparse e nessuno lo
sapeva finche' non e' stata lanciata.

Ora c'e' un test che le lancia davvero: `tests/test_allowlist_runnable.py` prende
ogni voce Python di `ops/allowlist.example` e pretende che non muoia sugli
argomenti. Se aggiungi una voce all'esempio e lo script non ha un comportamento di
default sensato, la suite te lo dice prima che la voce finisca sulla macchina.

Modifica `ops/allowlist` sulla VPS. La regola pratica: aggiungi una voce solo se
sei disposto a vederla eseguita automaticamente, di notte, senza che tu la stia
guardando. Le voci distruttive (`fast_gate`, `reset_paper`) sono lasciate
commentate di proposito.

## Fermarlo

```bash
sudo systemctl disable --now trading-ops.timer
```
