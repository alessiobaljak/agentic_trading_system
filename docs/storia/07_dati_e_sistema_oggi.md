# 07 — I dati raccolti e la mappa del sistema di oggi

> Capitolo della storia del progetto: il riepilogo è in [`README.md`](README.md). Scritto il 18 ottobre 2026 da un lettore in sola lettura sul repository, poi ricontrollato da un secondo lettore che ha aperto le fonti e corretto nel testo gli errori trovati (circa 110 affermazioni, 93 giuste, 17 corrette). Dove il testo dice «bozza» o «questo pezzo», intende questo capitolo.

> **Cosa è cambiato dopo la fotografia di questo capitolo (commit `672663b8`), lo stesso 18 ottobre:**
> * `573d084d`: il test della ricerca rosso dal 17 ottobre è corretto; la suite della ricerca passa (3.151 test).
> * `896d5196`: copiati sul principale i testi della campagna PANIERE (consegna, ipotesi, log, lezioni, codice) e tutti i
>   file della campagna BTC51 compresi i risultati delle 40 varianti. Restano solo sui branch soprattutto gli elenchi dei
>   trade e dell'avanzamento del paniere (`trade/` 44,3 MiB e `avanzamento/` 89,1 MiB), i risultati delle varianti di LINK6
>   (`risultati/`, 1,2 MiB) e una trentina di file vecchi degli archivi (circa 2 MiB).
> * `896d5196`: nuovo `scripts/esporta_storia.py` (copia di Firestore, RTDB e `data/` in `ops/results/archivio_AAAAMMGG/`,
>   con i segreti oscurati e un tetto di letture) e la voce `esporta-storia` in `ops/allowlist.example` (ora 61 voci). Sulla
>   macchina la voce non c'è finché il proprietario non la aggiunge alla lista bianca vera: fino ad allora vale ancora che
>   nessuna voce esporta i dati (sezioni 3.5 e 5).
> * Le etichette git sulle punte dei branch (proposta 4 della sezione 5) non si sono potute fare: il proxy git della
>   sessione rifiuta il push delle etichette (errore 403).

_Bozza scritta il 18 ottobre 2026 in sola lettura. Fotografia del repository al commit `672663b8` (18 ott 2026,
09:02 UTC), branch `claude/brave-albattani-1b12fv`. Gli orari sono in UTC; l'ora italiana oggi è UTC+2._

Come leggere i numeri: accanto a ognuno c'è da dove viene, cioè il file, il commit, la risposta della macchina
(«ops NNNN» = file `ops/results/NNNN-*.md`) o il comando lanciato. Le stime sono segnate come «stima». Le dimensioni
«su disco» vengono da `du -sh`, quelle «tracciate» dalla somma delle dimensioni dei file in `git ls-tree -r -l HEAD`.

Cose che questa bozza NON ha potuto vedere: la macchina Hetzner (nessun accesso diretto), Firebase (nessuna chiave in
questa sessione), Vercel. Per quelle si riporta cosa dice il codice e l'ultima risposta della macchina, con la data.

---

## 0. In breve

* Il repository tiene **3.158 file** (`git ls-files | wc -l`), **65,3 MiB** tracciati, **3.956 commit** dal
  10 giugno 2026 07:15 UTC (`76e6723f`) al 18 ottobre 09:02 UTC (`672663b8`): 1.879 dell'agente della macchina
  (`ops-agent`), 1.175 di Claude, 902 delle azioni di GitHub (`git log --format=%an | sort | uniq -c`).
* I dati che **non** sono nel repository e potrebbero andare persi sono tre gruppi: (1) tutto ciò che vive solo in
  **Firebase** (i 704 trade chiusi del paper, il registro delle strategie del gate, i documenti del learning);
  (2) le cartelle di misura che vivono solo **sulla macchina** (`data/…`, i backup dei reset, la cache delle candele,
  i log di sistema); (3) i risultati di ricerca che stanno **solo su un branch** (PANIERE, BTC51, LINK6 e i tre
  archivi): circa 156 MiB, quasi tutti di PANIERE. I 114 MiB di GRUPPO non sono sulla punta del principale ma sono
  nella sua storia (il branch è unito, `git merge-base --is-ancestor`; il commit `a6adee6e` li ha tolti solo dalla
  punta), quindi non si perdono cancellando il branch.
* Le candele usate dalla ricerca (`research/data/`, 470 MB in questo contenitore) non sono nel repo per scelta, ma si
  possono riscaricare dall'archivio pubblico di Binance e verificare con le impronte che invece sono nel repo.

---

## 1. Inventario dei dati

### 1.0 Tabella riassuntiva

| Insieme di dati | Dove sta | Periodo | Quanto è grande | Come si recupera o si rifà | Rischio di perderlo |
|---|---|---|---|---|---|
| Candele, mark price e funding della ricerca | cartella ignorata `research/data/` (in ogni contenitore di sessione cloud che li ha scaricati) | 2020-01 → 2023-12 (costruzione e validazione); 2024-01 → 2026-09 (vault) | 470 MB, 23.498 file in questo contenitore | si riscaricano da data.binance.vision; impronte SHA-256 nel repo | basso finché Binance tiene l'archivio (non verificato per le monete tolte dal listino) |
| Candele del bot e del gate | `.cache/candles/` sulla macchina | quattro anni a 15 minuti per centinaia di monete (`docs/hetzner_setup.md`) | mai misurata (la voce `cache` non è mai stata chiesta) | si riscaricano da Binance (lento) | basso, solo tempo |
| Risultati delle campagne (sul principale) | `research/campagne/` e cartelle vicine, tracciate | 7 → 18 ott 2026 | 1.258 file, 29 MB su disco | sono in git | basso |
| Risultati delle campagne (solo sui branch) | branch `research/campagna/PANIERE`, `…/GRUPPO`, `…/BTC51`, `…/LINK6`, `research/archivio/campagna/*` | 7 → 18 ott 2026 | ~271 MiB (somma della sezione 2), di cui ~156 MiB assenti anche dalla storia del principale | solo da quei branch; GRUPPO anche dalla storia del principale (commit `a6adee6e^`) | **medio**: basta cancellare il branch (non per GRUPPO) |
| Log delle ricerche | `research/campagne/*/log.jsonl` (23 sul principale) | 7 → 18 ott 2026 | il più grande 3,7 MiB (GRUPPO) | in git | basso (quello di PANIERE solo sul branch) |
| Log del gate | log di sistema della macchina; `data/gate_storia/`; Firestore `gate_history`, `gate_autopsy` | giri da prima di agosto (inizio non misurato), risposte ops dal 14 ago; storia completa solo 1-13 ott | non misurato | non si rifà | **alto** |
| Trade e stato del paper | Firestore `trades`; Realtime Database (`/positions`, `/account`, …) | paper attuale dal 16 set 2026 | 704 trade chiusi al 18 ott 04:34 UTC | non si rifà | **alto**: solo in Firebase, e il reset li cancella |
| Registro delle strategie del gate | Firestore `strategy_registry/validated`, `discovered_strategies/specs`, `strategy_params/current` | registro fermo al giro del 13 ott 18:40 UTC | 2.435 coppie, 249 validate | non si rifà (le spec generate non sono nel repo) | **alto** |
| Dati di misura della macchina | `data/selettore/`, `data/gruppo_controllo/`, `data/voto_t/`, `data/replay_gate/`, `data/ingressi_*`, backup JSON | 24 set → 13 ott 2026 (i file del selettore più vecchi di 14 giorni li cancella il gate stesso, sezione 1.7) | non misurato | in parte si rifanno ricalcolando | **alto**: solo sulla macchina |
| Risultati ops | `ops/requests/`, `ops/results/`, tracciati | 14 ago → 16 ott 2026 | 621 richieste, 620 risposte | in git | basso |
| Battito della macchina | `ops/heartbeat.md` (git), `/ops/battito` (RTDB), `/bot_status/heartbeat` (RTDB) | dal 15 ago 2026 | 1.518 versioni in git | in git | basso |
| Diario e documenti | `docs/`, `research/*.md`, `CLAUDE.md`; conversazioni su claude.ai | 10 giu → 18 ott 2026 | `docs/` 32 file, 0,8 MiB | in git; le conversazioni no | medio per le conversazioni |
| Foto dello stato ogni 2 ore | `docs/state.md` e la sua storia in git | 13 giu → 18 ott 2026 | 891 versioni | `git log -p -- docs/state.md` | basso |
| Dashboard | codice in `dashboard/`, pubblicata su Vercel, dati in Firebase | dal 10 giu 2026 | 49 file tracciati | codice in git; impostazioni Vercel no | basso per il codice |

Le sottosezioni che seguono danno i dettagli e le fonti di ogni riga.

### 1.1 Candele, mark price e funding della ricerca (`research/data/`)

* **Dove.** La cartella `research/data/` è esclusa da git (`.gitignore`, riga «research/data/», sezione «Protocollo di
  ricerca (6 ott 2026): dati di mercato e marcatore di sessione, mai in git»). I file li scarica ogni sessione di
  ricerca nel proprio contenitore cloud; non stanno sulla macchina Hetzner.
* **Cosa c'è in questo contenitore** (`du -sh research/data/*`, `find … -name '*.zip' | wc -l`):
  * `insample/`: 352 MB, 19.458 file zip mensili, 223 simboli. Dieci simboli hanno tutto (candele «last» e
    «mark» su 9 timeframe da 15 minuti a 1 giorno, più il funding: 741-912 file ciascuno): LINKUSDT e le nove monete di
    controllo del protocollo 4 (BTC, ETH, SOL, XRP, DOGE, BNB, LTC, MATIC, BCH; elenco in
    `research/passo0_4/fatti_monete.json`). Degli altri, 128 hanno quasi solo le candele giornaliere del 2023, scaricate
    per la scelta delle monete (`research/src/passo1.py`, docstring); 80 (le monete del paniere e del gruppo,
    `research/campagne/PANIERE/monete.csv`) hanno candele giornaliere last e mark e funding dal 2020 al 2023 (75-160
    file); 5 (ADA, AVAX, DYDX, ETC, FIL) hanno anche serie a 15 minuti, 30 minuti o 1 ora. Anni dei file: 2.859 del
    2020, 4.928 del 2021, 5.356 del 2022, 6.315 del 2023 (conteggio sui nomi dei file). Più 12 file di cache `.pkl`
    (83 MB).
  * `vault/`: 19 MB, 966 file, dieci monete a 1 ora (candele last, mark e funding) dal 2024-01 al 2026-09: BTCUSDT e le
    nove «altre monete» del protocollo 3 (APT, BCH, BNB, DOGE, ETH, LTC, MATIC, SOL, XRP).
  * `placebo/`: 99 MB, 3.061 file, 80 monete a 1 ora, per la prova a placebo del 9 ott.
  * `altre_monete/`: vuota.
* **Come si rifà.** Fonte unica: i file mensili pubblici di Binance USDS-M futures su data.binance.vision
  (`research/src/dati.py`, docstring). Il repository tiene le **impronte SHA-256** dei file scaricati: 58 file con
  «impront» nel nome (`git ls-files | grep -i impront`, per esempio `research/campagne/BTCUSDT/impronte.json`, che
  associa a ogni zip la sua impronta), più `research/passo0_4/scarico.json` (lo scarico del protocollo 4: 9.120 file
  previsti, 8.664 presenti, con l'elenco degli assenti) e i `fase0_dati.md` di ogni campagna. Quindi si possono
  riscaricare e controllare byte per byte.
* **Rischio.** Il contenitore di questa sessione è temporaneo: alla sua chiusura la cartella sparisce. Il danno è solo
  di tempo, a una condizione non verificata: che Binance continui a pubblicare i file delle monete tolte dal listino
  (FTM, MATIC e altre). Se un giorno li togliesse, quei dati non si potrebbero più rifare.

### 1.2 Candele del bot e del gate (`.cache/` sulla macchina)

* **Dove.** `.cache/candles/` nella cartella del programma sulla macchina (`backtesting/data_loader.py:226`, variabile
  `BACKTEST_CACHE_DIR`); anche `data_cache/` è esclusa da git.
* **Cosa e quanto.** Candele scaricate da Binance per il gate: «quattro anni a 15m per centinaia di coin»
  (`ops/allowlist.example`, commento della voce `cache`), circa 140.000 candele per moneta (`docs/hetzner_setup.md`,
  «Cos'era rete e non CPU»). La dimensione non è mai stata misurata: nessuna risposta ops con la chiave `cache` o
  `disco` (conteggio sulle 621 richieste, sezione 1.8).
* **Come si rifà.** Si riscarica da Binance. È lenta (era il collo di bottiglia del gate ad agosto, stesso documento).
* **Rischio.** Basso: costa solo tempo.

### 1.3 Risultati delle campagne di ricerca

**Sul branch principale** (tutto tracciato):

* `research/campagne/`: 24 cartelle, 1.258 file tracciati (`git ls-files -s research/campagne | wc -l`), 29 MB su
  disco. Per tipo di file: 405 in `codice/`, 292 in `lavoro/`, 160 in `schede/`, 89 in `esiti/`, 66 in `risultati/`,
  31 impronte, 26 in `candidati/`, 23 log, 22 `ipotesi`, 22 `fase0_dati`, 22 `consegna`, 21 `lezioni_moneta`, 21
  `lezioni_metodo_proposte`, 20 `scheda_moneta` (conteggio sul primo livello dei percorsi).
  * 20 campagne per moneta della prima edizione (7-9 ott; da 20 file, LTCUSDT, a 119, MATICUSDT; la più pesante
    su disco è DYDXUSDT con 2,1 MB);
  * GRUPPO, la campagna di gruppo su 80 monete (10-12 ott; 429 file, 14 MB; `monete.csv`, 80 righe più
    l'intestazione);
  * PANIERE (13-14 ott): sul principale solo `regole.md`, `monete.csv`, `impronte_1d.json` e 80 schede; il resto è sul
    branch (sezione 2);
  * BTC51 (16-17 ott): sul principale solo `STATO.md`, `lezioni.md`, `log.jsonl`; consegna, ipotesi, validazione,
    codice e risultati sono sul branch;
  * LINK6 (17-18 ott): 40 file sul principale (consegna, ipotesi, fase 5, validazione, log, codice); i 32 file di
    `risultati/` sono solo sul branch.
* Esiti scritti nelle consegne (`grep` su `research/campagne/*/consegna.md`): nessuna strategia valida in tutte, con
  tre candidati della prima edizione mandati al vault (BTCUSDT-V10, BNBUSDT-045, ADAUSDT-037) e nessuno dei tre lo
  supera (`research/vault/risultati.md`, vault aperto l'11 ott alle 19:26 UTC). Il candidato di BTC51 (V-020) non
  supera il vault 3 (`research/vault/BTC51_risultati.md`). LINK6: «Nessuna strategia valida trovata»
  (`research/campagne/LINK6/consegna.md`, sezione Esito).
* Cartelle accanto alle campagne, tutte tracciate (`git ls-files research | awk …`): `research/vault/` (16 file: le
  aperture `APERTURA.md` e `APERTURA_3.md`, gli esiti dei candidati in JSON, uno a uno), `research/vault_strumenti/` (3
  lanciatori), `research/taratura/` (49 file: le prove a placebo della prima edizione, del gruppo e del paniere, e il
  controllo positivo del gruppo), `research/collaudo_3/` (43) e `research/collaudo_4/` (10) (il collaudo del metodo
  dei protocolli 3 e 4), `research/esperimenti/ordini_limite/` (13: la prova degli ordini limite del 13 ott, nove
  strategie, esiti JSON fino a 2,9 MiB l'uno), `research/altre_monete_3/` (5), `research/monete_di_controllo_4/` (1),
  `research/passo0_2/` (8), `research/passo0_4/` (8), `research/passo4/` (1), `research/universo/` (7: la scelta delle
  monete), `research/confronto/` (2), `research/prova_processo/` (1), `research/apertura/` (5 messaggi di apertura
  delle sessioni), `research/lezioni/metodo.md`, i quattro protocolli e il registro delle correzioni
  `research/CHANGELOG.md`.
* Fuori da git, solo in questo contenitore: i log testuali delle prove del collaudo 3 e degli ordini limite (`*.log`,
  `*.out`, 26 file da 8-28 KB; `git status --ignored`). Sono copie dell'uscita a video; gli esiti veri sono nei JSON
  tracciati.

**Solo sui branch**: dettaglio nella sezione 2. In breve: PANIERE 258 file (141,8 MiB, fra cui `log.jsonl` di 7,4
MiB, `trade/` e `avanzamento/`), GRUPPO 68 file (114,4 MiB: `trade/` e `avanzamento/`, tolti dal principale il 12 ott,
`research/CHANGELOG.md` riga del 2026-10-12, ma ancora nella storia del principale: commit `a6adee6e`), BTC51 84 file
(1,8 MiB), LINK6 32 file (1,2 MiB), più i tre archivi della prova di processo.

### 1.4 Log delle ricerche e del gate

* **Ricerca a protocollo.** Ogni campagna ha un `log.jsonl` (una riga per ipotesi, variante, prova): 23 sul
  principale (`git ls-files research/campagne | grep -c log.jsonl`); il più grande è quello di GRUPPO, 3,7 MiB.
  Quello di PANIERE (7,4 MiB) è solo sul branch. In git, quindi al sicuro.
* **Gate automatico (la ricerca «vecchia», `scripts/optimize.py` e `scripts/discover_strategies.py`).** Il racconto
  di ogni giro sta in quattro posti, nessuno completo:
  * il log di sistema della macchina (`journalctl -u trading-optimizer.service`, voce ops `log-gate`): quanto indietro
    arrivi non è noto (dipende dalla configurazione di journald, non verificata). 60 risposte `log-gate` ne
    conservano dei pezzi in `ops/results/` (sezione 1.8);
  * `data/gate_storia/AAAA-MM.jsonl` sulla macchina, una riga per giro e per coppia, **dal 1 ott 2026**
    (`scripts/gate_storia.py`, docstring); il gate è fermo dal 13 ott, quindi copre 1-13 ott;
  * Firestore `gate_history/timeline` (ultimi 240 punti, `scripts/optimize.py:1059`) e `gate_history/lifecycle`
    (ultimi 500 eventi, `GATE_LIFECYCLE_MAX`, `scripts/optimize.py:1120`): si sovrascrivono da soli;
  * Firestore `gate_autopsy/current` e `gate_autopsy/discover` (dove muoiono le candidate dell'ultimo giro) e
    `strategy_params/discovered_last_run` e `…_1h` (l'ultimo giro): solo l'ultimo.
* **Rischio.** Alto per la storia del gate prima del 1 ott: esiste solo come riassunto nelle risposte ops e nelle
  891 versioni di `docs/state.md` (sezione 1.10).

### 1.5 Trade e stato del paper (Firebase)

**Firestore** (il «magazzino» interrogabile; schema in `docs/firebase_schema.md`, che però è indietro: elenca 7 voci
contro le 26 che il codice usa, conteggio con `grep` su `set_doc/get_doc/query_collection` in `bot/` e `scripts/`):

* `trades/{id}`: un documento per trade chiuso, scritto dal bot (`bot/learning/trade_logger.py`), con prezzi, uscita,
  regime, indicatori, sentiment, funding e confidenza all'ingresso (`docs/firebase_schema.md`). **704 trade chiusi**,
  391 vinti (56%), risultato realizzato −172,92 USDT al 18 ott 04:34 UTC (`docs/state.md`, sezione «Trade chiusi»).
  Il paper attuale è partito il **16 settembre 2026** (primo giorno nei conteggi di ops 0620; commit `cb125967` del
  16 set «il paper opera — prima posizione aperta»). Equity 827,08 USDT con 2 posizioni aperte (`docs/state.md`);
  partenza di 1.000 USDT (`scripts/reset_paper.py`, `START_EQUITY = 1000.0`; −16,4% su −164,47 USDT in ops 0621 è
  coerente).
* I trade dei paper precedenti non ci sono più: il 10 ago 2026 ne sono stati cancellati 144 con
  `scripts/reset_paper.py`, con un'esportazione `trades_backup_20260811.json` lasciata sulla macchina
  (`docs/audit_fase0.md`, sezione 0). Non risultano altre esportazioni nel repo (nessun file di trade del paper fra i
  495 JSON/CSV tracciati, `git ls-files | grep -E '\.(json|csv|jsonl)$'`).
* Gli altri documenti, con chi li scrive (ricerca con `grep -rl "set_doc(…"`):

| Collezione / documento | Scritto da | Cosa contiene | Si conserva? |
|---|---|---|---|
| `strategy_registry/validated`, `strategy_registry/esplorative` | gate (`scripts/optimize.py`, `scripts/discover_strategies.py`) | il registro delle coppie moneta × strategia (sezione 1.6) | riscritto a ogni giro |
| `discovered_strategies/specs` | `scripts/discover_strategies.py` | le regole delle strategie generate | riscritto |
| `strategy_params/current`, `discovered_last_run`, `discovered_last_run_1h` | gate | parametri e ultimo giro | riscritti |
| `gate_autopsy/current`, `discover`; `gate_history/timeline`, `lifecycle` | gate | autopsia e storia breve | 240 punti / 500 eventi |
| `optimize_shards/{i}`, `discover_shards/{i}` | gate | pezzi del giro diviso in parti | riscritti |
| `memory/30`, `60`, `90`; `insights/{settimana}` | learning notturno (`bot/learning/learning_loop.py`, azione GitHub delle 02:00 UTC) | rapporto di memoria e racconto settimanale | `insights` uno per settimana |
| `strategy_weights/current` e `v000`…`v089` | `bot/learning/adaptation.py` | pesi strategia × regime | ultime 90 versioni (`LEARNING_HISTORY_VERSIONS`, `bot/config.py:292`) |
| `drift/current`, `calibration/current`, `asset_scores/current`, `learning/referti`, `learning/ipotesi_storia` | bot (`bot/main.py`) | deriva paper/gate, calibrazione della confidenza, referti dei trade | riscritti |
| `selector/current`, `selector/dataset`, `selector/report` | `scripts/selettore_report.py`, `scripts/discover_strategies.py` | il selettore (riassunto; il dataset vero è sulla macchina) | riscritti |
| `supervisor/state` | `scripts/supervisor.py` | decisioni del supervisore | riscritto |
| `portfolio/backtest` | `scripts/portafoglio_backtest.py` | backtest delle validate insieme | riscritto |
| `ai_hypotheses/last`, `autopsia`; `ai_reports/latest`; `ai_shadow/{istante}`; `ai_spesa/{giorno}` | livello AI | idee, analisi, decisioni in ombra (240 fino al 30 set, ops 0585), consumo | `ai_shadow` e `ai_spesa` crescono |
| `dashboard/controllo`, `dashboard/gate`, `dashboard/backlog`, `dashboard/report_giornaliero`; `report_giornaliero/{giorno}` | bot ogni ora; gate a ogni giro; `scripts/report_giornaliero.py` | i documenti letti dalla dashboard (`docs/controllo_schema.md`) | il report si tiene un giorno per documento |
| `user_risk_settings/current` | dashboard | leva e rischio scelti dal proprietario | uno |
| `_healthcheck/ping`, `github_ci` | prove di collegamento | — | — |

**Realtime Database** (lo stato «dal vivo», percorsi trovati nel codice di `bot/` e `scripts/`):
`/bot_status` (stato, regime, `dry_run`, battito), `/positions/{simbolo}`, `/account/equity`, `starting_equity`,
`paper_started_at`, `btc_inizio`, `/risk_state` (interruttori di sicurezza), `/decision_status`, `/adapt_state`
(panchina), `/ordini_limite/{simbolo}` e `/paper/ordini_limite/contatori`, `…/saltati/{…}` (gli ingressi a limite
dal 13 ott), `/unlogged_trades/{id}` (trade non riusciti a scrivere su Firestore), `/regime_history`,
`/trailing_keep`, `/reconciliation`, `/bot_active`, `/commands/kill_switch`, `close_position`, `bot_state`,
`maintenance` (comandi), `/btc_history` (anello di 200 punti orari, `bot/main.py:965`), `/avvii` (ultimi 20 avvii),
`/learning_giorni/{giorno}` e `/learning_indice` (foto giornaliera del learning, tenute **35 giorni**,
`bot/learning/apprendimento.py:63`), `/controllo`, `/gate`, `/backlog`, `/report_giornaliero` (specchi per la
dashboard), `/ops/battito`, `/giorni_fatti`, `/_healthcheck`.

**Rischio: alto.** I trade e lo stato vivono solo in Firebase. `scripts/reset_paper.py` cancella `trades`,
`/positions`, `/risk_state`, `/account/equity`, `/adapt_state` e l'inizio del paper **senza scrivere un backup**
(docstring del file, righe 1-25; l'esportazione del 10 ago era stata fatta a parte). Nel repo restano solo i riassunti:
le risposte ops `trades` (44), `stato` (35), `controllo` (21), `portafoglio` (25), `mfe` (25), e
`docs/analisi_trade_16set_12ott.md` (508 trade del 16 set-12 ott, 17 letture ops 0596-0612).

### 1.6 Il registro delle strategie del gate

* **Dove.** Un solo documento Firestore, `strategy_registry/validated`, con un limite di 1 MiB
  (`bot/core/firebase_client.py:46`) e un tetto di 3.000 coppie (`OPTIMIZER_MAX_PAIRS`, `bot/core/registry.py:39`).
  Le regole delle strategie generate stanno in un secondo documento, `discovered_strategies/specs`.
* **Quanto.** Al giro del 13 ott 18:40 UTC: 2.435 coppie generate (0 di base), 2.100 con almeno una conferma, **249
  validate** con almeno 3 passaggi fuori campione su 80 monete coperte su 200 (`docs/state.md`, «GATE 1» e «Salute del
  registro»). Il supervisore, che conta in un altro modo, ne dice 278 (`docs/state.md`, «Supervisore», 18 ott
  04:03 UTC). L'11 ott il documento occupava 771 KiB su 879 utili (88%) e le spec 331 KiB, 1.437 spec note (ops 0586).
* **Periodo.** È fermo dal 13 ott: con il file `ops/gate_fermo` nessun giro lo riscrive (`bot/core/gate_fermo.py`).
* **Storia.** Il registro si riscrive a ogni giro, quindi non ha storia propria. Ne restano: `data/gate_storia/` sulla
  macchina (dal 1 ott); la tabella delle validate dentro 523 delle 891 versioni di `docs/state.md` (nelle altre le
  validate erano 0, tranne le prime 2 del 13 giu, con una tabella più vecchia; moneta, strategia, passaggi, profit
  factor, rendimento, parametri d'uscita, ma non le regole);
  i file `gate_backup_*.json`
  che `scripts/fast_gate.sh` scrive sulla macchina prima di azzerare (`scripts/fast_gate.sh:106`).
* **Rischio: alto.** Senza le spec le coppie non si possono più rigiocare: è già successo, «30 coppie su 31 non
  replayabili dopo un reset» (`.gitignore`, commento su `gate_backup_*.json`).

### 1.7 I dati di misura che vivono solo sulla macchina

Tutte cartelle escluse da git di proposito (`.gitignore`, con il motivo scritto accanto). Nessuna dimensione è stata
misurata (nessuna risposta ops `disco` o `cache`).

| Cartella / file sulla macchina | Cosa contiene | Da quando | Fonte |
|---|---|---|---|
| `data/selettore/` | un JSONL per giro del gate con le condizioni all'ingresso di ogni trade simulato (il dataset del selettore) | ~24 set → 13 ott (nomi `2026-09-24_1h…` nelle risposte ops); ma ogni giro cancella i file più vecchi di 14 giorni (`SELETTORE_RITENZIONE_GIORNI`, `scripts/discover_strategies.py:1417`), quindi dopo l'ultimo giro del 13 ott dovrebbero restare solo quelli dal ~29 set (non verificato sulla macchina) | `.gitignore`; `scripts/discover_strategies.py:1381` |
| `data/gruppo_controllo/` | bocciate a caso e foto giornaliera delle conferme (il gruppo di controllo del fuori campione) | 30 set | `.gitignore`; `scripts/gruppo_controllo.py` |
| `data/voto_t/validate.json` | il voto t di tutte le validate, una tantum | 30 set | `.gitignore`; `scripts/t_validate.py` |
| `data/replay_gate/` (con `g7/`) | il gate rigiocato nel passato e la prova sul prezzo casuale | 1-5 ott (fermato dal proprietario il 4 ott: `docs/letture.md:11`) | `.gitignore`; `scripts/replay_gate.py:108` |
| `data/ingressi_*` | l'analisi «il paper entra dove entra il gate?» | 27 set | `.gitignore`; `scripts/ingressi_report.py:142` |
| `data/gate_storia/` | storia del gate, un file al mese | 1 ott → 13 ott | `scripts/gate_storia.py` |
| `trades_backup_20260811.json` | i 144 trade del paper cancellati il 10 ago | 11 ago | `docs/audit_fase0.md` |
| `gate_backup_*.json` | registro e spec prima di un azzeramento | non noto | `scripts/fast_gate.sh:106` |
| `tuning.env` | i parametri scelti dal supervisore | — | `scripts/supervisor.py:29` |
| log di sistema (journald) | bot, gate, supervisore, agente ops | non noto | voci `log-bot`, `log-gate`, `log-super`, `log-ops` |

**Rischio: alto.** Se la macchina si rompe o viene ricreata, queste misure spariscono. I loro risultati principali
sono riassunti nelle risposte ops (per esempio `replay-gate-esito`, 11 risposte; `voto-t-esito`, 2; `ingressi-esito`,
3) e nei documenti (`docs/capito.md`).

### 1.8 Le risposte della macchina (`ops/`)

* **Quante.** 621 richieste in `ops/requests/` (2,5 MB su disco) e 620 risposte in `ops/results/` (6,3 MB). Due
  richieste del 18 ott erano ancora senza risposta alla fotografia (`0622-18ott-storia-trades`, `0623-18ott-storia-stato`,
  create alle 09:02 UTC, dopo l'ultimo battito delle 08:22); le risposte sono arrivate alle 09:03 UTC (commit
  `3c7fbdb8`, dopo la fotografia); una risposta non ha più la sua richiesta (`0123-serie-perdite`,
  rifiutata perché la voce non esisteva). 9 risposte sono rifiuti della lista bianca, 5 sono andate in «TIMEOUT dopo
  900s», 24 non finiscono con codice 0 (`grep` su `ops/results/*.md`).
* **Periodo** (data del commit che ha creato la risposta, `git log --diff-filter=A`): 26 ad agosto (dal 14 ago), 358
  a settembre, 236 a ottobre; l'ultima è la 0621 del 16 ott.
* **Per tipo** (chiave della prima riga della richiesta):

| Gruppo | Totale | ago | set | ott | Voci più usate |
|---|---|---|---|---|---|
| Gate e ricerca automatica | 179 | 18 | 112 | 49 | `gate` 75, `log-gate` 60, `replay-gate-esito` 11, `lancia-gate` 7, `replay-gate` 6 |
| Paper e misure | 278 | 4 | 126 | 148 | `trades` 44, `stato` 35, `frequenza` 26, `portafoglio` 25, `mfe` 25, `controllo` 21, `selettore` 20, `report-giornaliero` 20, `rifiuti` 18, `rifiutati` 17 |
| Macchina e canale | 161 | 4 | 118 | 39 | `log-bot` 44, `riavvia-bot` 31, `ai-stato` 29, `servizi` 14, `memoria` 13 |
| Senza chiave | 1 | — | 1 | — | `0046-chi-valida-oggi` |

  Le ultime letture: il 12 ott (0596-0612) diciassette misure per l'analisi dei trade; il 13 ott (0613-0618) lo stop
  del gate e il riavvio del bot con gli ingressi a limite; il 16 ott (0619-0621) portafoglio, trade e controllo.
* **Limite da sapere.** L'uscita di ogni comando viene tagliata a 20.000 caratteri (`OPS_MAX_OUTPUT`,
  `scripts/ops_agent.py:47`) e ogni comando ha 900 secondi (`OPS_TIMEOUT_S`, riga 48): il canale non può riportare in
  git un'esportazione intera dei trade o del registro.

### 1.9 Il battito della macchina

* `ops/heartbeat.md`: riscritto dall'agente ops una volta l'ora; **1.518 versioni** in git dal 15 ago 2026
  (`git log -- ops/heartbeat.md`); l'ultima: «ultimo giro: 2026-10-18 08:22 UTC», ramo
  `claude/brave-albattani-1b12fv`, 0 richieste in attesa (commit `7eea6e9f`).
* `/ops/battito` su RTDB: lo stesso battito, dal 28 set (`scripts/ops_agent.py:343`).
* `/bot_status/heartbeat` su RTDB: il battito del bot, a ogni giro del ciclo (ogni 30 secondi, `bot/main.py:2497` e
  2606). L'azione GitHub `bot-monitoring` lo legge ogni 15 minuti sulla carta (nei fatti GitHub l'ha lanciata 7 volte
  nelle 24 ore fino al 18 ott 09:00 UTC, `gh run list`) e manda un avviso Telegram se è più vecchio di 180
  secondi (`scripts/monitor.py:15`).

### 1.10 Diario, documenti e conversazioni

* `docs/`: 32 file tracciati, 0,8 MiB. I principali (`wc`, `git log`):
  * `docs/andremo_live.md`, il diario: 320.825 byte, 4.101 righe, dal 27 ago al 18 ott, 212 commit;
  * `docs/capito.md` (cosa abbiamo capito, dal 1 ott, 37 commit), `docs/backlog.md` (dal 20 set, 143 commit),
    `docs/backlog_archivio.md` (1 commit del 1 ott), `docs/letture.md`;
  * documenti di revisione e analisi: `audit.md`, `audit_fase0.md`, `audit_backtesting.md`, `fase5_report.md`,
    `revisione_sospese_30set.md`, `analisi_trade_16set_12ott.md`, `incidente_31ago.md`, `disegno_cervello.md`,
    `controllo_schema.md`, `letture_esterne/` (tre letture di altri progetti, 12 ott);
  * documenti di impianto: `architecture.md`, `firebase_schema.md`, `deployment.md`, `hetzner_setup.md`,
    `data_sources.md`, `security_rules.md`, `risk.md`, `learning.md`, `orchestrator.md`, `optimization.md`,
    `paper_trading.md`.
* `docs/state.md`: la foto dello stato, generata da Firebase dall'azione GitHub `state-snapshot` ogni 2 ore
  (`.github/workflows/snapshot.yml`, `cron "15 */2 * * *"`; nei fatti meno spesso: 5 versioni nelle 24 ore fino al
  18 ott 09:00 UTC). **891 versioni** in git dal 13 giu al 18 ott, tutte di
  `github-actions` (`git log -- docs/state.md`). È una serie storica di fatto: equity, posizioni, tabella delle
  validate, autopsia, supervisore, trade chiusi, deriva. Si legge con `git log -p -- docs/state.md`.
* Protocolli di ricerca: `research/PROTOCOLLO.md` (prima edizione, versione 4.5), `PROTOCOLLO_2.md`, `PROTOCOLLO_3.md`,
  `PROTOCOLLO_4.md`, `protocollo_4_note.md`, `CHANGELOG.md`.
* `CLAUDE.md` e `README.md` (il README è del 10 giu e non è più stato toccato: 1 commit).
* **Conversazioni.** Il lavoro è passato da sessioni di Claude Code su claude.ai che **non sono nel repo**: una
  sessione di coordinamento aperta il 10 giu («Agentic crypto trading system») e 37 sessioni di ricerca o di prova dal
  7 al 17 ott (elenco delle sessioni dell'account, titoli e date). Le decisioni del proprietario sono in gran parte
  ricopiate nel diario e nei protocolli, ma non c'è un modo di verificare che lo siano tutte.

### 1.11 La dashboard

* **Codice:** `dashboard/`, Next.js 14 (`dashboard/package.json`), 49 file tracciati, 41 file TypeScript (30
  componenti, 9 librerie, `layout.tsx`, `page.tsx`), 9.107 righe. Sei schede: Report, Controllo, Operatività, Gate,
  Learning, Impostazioni (`dashboard/app/components/DashboardShell.tsx:120-151`). La scheda Claude è stata tolta il
  21 set (`CLAUDE.md`).
* **Dati:** nessuno di suo; legge Firebase dal browser dopo il login Google (`docs/security_rules.md`), per esempio
  `bot_status`, `positions`, `account/equity`, `decision_status`, `commands/*`, `strategy_registry/validated`,
  `gate_history/timeline`, `gate_autopsy/*`, `supervisor/state`, `user_risk_settings/current` (`grep` di `ref(db…)` e
  `doc(db…)` nei componenti). Scrive `user_risk_settings/current`, `commands/kill_switch` e
  `commands/close_position`, più `commands/kill_switch_meta`, `commands/close_position_meta` e `/reconciliation`
  (`KillSwitch.tsx:38`, `Positions.tsx:76`, `ReconcilerStatus.tsx:80`); le regole in `firebase/firestore.rules` e
  `firebase/database.rules.json` ammettono le prime tre e `close_position_meta`, non le altre due; lì l'UID
  del proprietario è ancora il segnaposto `REPLACE_WITH_YOUR_FIREBASE_UID`: non si sa se le regole pubblicate siano
  queste.
* **Fuori dal repo:** il progetto Vercel e le sue variabili `NEXT_PUBLIC_FIREBASE_*` (`docs/deployment.md`).
  `dashboard/node_modules/` (616 MB in questo contenitore) è escluso da git e si rifà con `npm ci`.

### 1.12 Configurazione e segreti (dove stanno, senza contenuto)

* Sulla macchina: `.env` (chiavi Binance, Anthropic, Firebase, Telegram; elenco dei nomi in
  `docs/hetzner_setup.md`, passo 7), `tuning.env` (supervisore), `ops/allowlist` (la lista bianca vera; una sua copia
  del 2 ott, che contiene solo chiavi e comandi, è in ops 0436).
* Su GitHub, nei segreti del repository (solo i nomi, da `.github/workflows/*.yml`): `ANTHROPIC_API_KEY`,
  `ANTHROPIC_MODEL`, `ANTHROPIC_WORKSPACE_ID`, `FIREBASE_SERVICE_ACCOUNT`, `FIREBASE_RTDB_URL`, `TELEGRAM_BOT_TOKEN`,
  `TELEGRAM_CHAT_ID`, `COINGLASS_API_KEY`, `LUNARCRUSH_API_KEY`, `NEWSAPI_KEY`.
* Su Vercel: la configurazione web di Firebase.
* Nel repo c'è solo il modello `.env.example` (non letto in questa bozza: le regole della sessione ne vietano la
  lettura).

---

## 2. I branch

Ci sono **29 branch remoti** (`git branch -r | wc -l`). Il bot, la macchina e la dashboard leggono solo il
principale (`CLAUDE.md`). Il 12 ott i 21 branch di campagna della prima edizione e quello di coordinamento sono stati
uniti nel principale (22 commit di unione, `research/CHANGELOG.md`, riga del 2026-10-12). Colonne: «avanti» = commit
del branch che il principale non ha; «solo qui» = file presenti nella punta del branch e assenti dal principale
(confronto per percorso, `git ls-tree`), con la loro dimensione.

| Branch | Ultimo commit | Cosa contiene | Avanti | Solo qui | Chiuso? |
|---|---|---|---|---|---|
| `claude/brave-albattani-1b12fv` (principale) | `672663b8`, 18 ott 09:02 | tutto il sistema | — | — | in uso |
| `research/campagna/LINK6` | `bb8b444d`, 18 ott | campagna del protocollo 4 su LINKUSDT. **Storia separata**: non ha antenati in comune col principale (`git merge-base` vuoto), 19 commit del 17-18 ott, 507 file | 19 | 32 file, 1,16 MiB (`risultati/`) | sì: consegna «nessuna strategia valida», vault 4 mai aperto (`CLAUDE.md`) |
| `research/campagna/BTC51` | `739a1853`, 17 ott | campagna del protocollo 3 su BTCUSDT; nel branch sono stati tolti 2.596 file che la sessione non doveva leggere (commit `fc24e7e9`) | 25 | 84 file, 1,78 MiB (consegna, ipotesi, validazione, via libera, `codice/` 29, `risultati/` 49) | sì: chiusa il 17 ott, V-020 non supera il vault |
| `research/campagna/PANIERE` | `70d17c85`, 14 ott | seconda edizione, idee sul paniere di 80 monete a barre giornaliere | 28 | 258 file, 141,76 MiB (`log.jsonl`, `trade/` 64, `avanzamento/` 64, `lavoro/` 92, `codice/` 30, consegna, ipotesi, lezioni) | sì: «Fase 5 e consegna scritte, campagna chiusa» |
| `research/campagna/GRUPPO` | `121eb4ab`, 11 ott | campagna di gruppo (Passo 4bis) su 80 monete; unita al principale | 0 | 68 file, 114,44 MiB (`trade/` 34, `avanzamento/` 34, tolti dal principale il 12 ott ma ancora nella sua storia, commit `a6adee6e`) | sì |
| `research/coordinamento` | `6a0806ba`, 12 ott | lavoro del coordinamento della prima edizione (placebo, Passo 4, vault); unito | 0 | 0 | sì |
| 20 branch `research/campagna/<MONETA>` della prima edizione: 1000SHIB, ADA, AVAX, BCH, BNB, BTC, DOGE, DYDX, ETC, ETH, FIL, FTM, GALA, LINK, LTC, MASK, MATIC, SOL, TRB, XRP (USDT) | 8-9 ott | una campagna per moneta (BTC, ETH e SOL rifatte con la versione 4.4 l'8 ott, le altre 17 con la 4.5 il 9 ott) | 0 | 0 | sì, tutte consegnate e unite |
| `research/archivio/campagna/BTCUSDT` | `b60dd847`, 7 ott | la prova di processo del 7 ott, poi rifatta | 6 | 43 file, 0,13 MiB; 67 file con lo stesso nome ma contenuto diverso dal principale | sì, archivio |
| `research/archivio/campagna/ETHUSDT` | `a60898c2`, 7 ott | idem | 25 | 49 file, 11,31 MiB; 65 diversi | sì, archivio |
| `research/archivio/campagna/SOLUSDT` | `d1955b4d`, 7 ott | idem | 18 | 9 file, 0,07 MiB; 67 diversi | sì, archivio |

Somma di quello che esiste solo sui branch: 32 + 84 + 258 + 68 + 43 + 49 + 9 = 543 file, circa 271 MiB (somma delle
colonne; più i file degli archivi con lo stesso nome e contenuto diverso). Tolti i 68 file di GRUPPO, che sono nella
storia del principale, e i pochi file uguali a versioni della storia, quello che non esiste in nessun commit del
principale sono 437 file, circa 156 MiB (confronto degli oggetti con `git rev-list --objects 672663b8`). I file
«diversi» degli archivi sono quasi tutti versioni vecchie che stanno nella storia del principale: mancano da tutta la
storia solo 29 versioni (9, 7 e 9 negli archivi, 3 in BTC51, 1 in LINK6; ~2 MiB).

---

## 3. La mappa del sistema di oggi

### 3.1 Il codice in numeri

| Parte | Moduli | Righe | Fonte |
|---|---|---|---|
| `bot/` (il bot che gira 24 ore su 24) | 67 moduli Python | 23.880 | `git ls-files bot` + `wc -l` |
| `scripts/` (gate, misure, manutenzione) | 47 moduli Python + 10 script shell | 24.333 (solo Python) | idem |
| `backtesting/` (il motore del gate) | 8 | 2.854 | idem |
| `research/src/` (strumenti della ricerca) | 14 | 16.139 | idem |
| `dashboard/app/` | 41 file TypeScript | 9.107 | idem |
| `tests/` | 160 moduli di test + `conftest.py` | 36.937 | idem |
| `research/src/tests/` | 40 moduli di test (44 file) | — | `git ls-files` |

Test: **2.305** in `tests/` e **3.153** in `research/src/tests/` (`python -m pytest --collect-only -q`). Su GitHub
la suite gira insieme (`.github/workflows/tests.yml`): l'ultima esecuzione (n. 39113796642, 18 ott 09:12 UTC) dice
**5.452 passati, 1 fallito, 5 saltati**. Il fallito è
`research/src/tests/test_guardiano_gruppo.py::test_A_elenco_del_repo_non_tocca_le_monete_di_campagna`
(`assert (21 == 20)`, riga 195); i test su GitHub sono rossi a ogni push dal 17 ott 20:50 UTC (`gh run list`). La causa
non è stata indagata in questa bozza. Dopo la fotografia il commit `573d084d` (18 ott 09:38 UTC) ha corretto il test
(la cartella LINK6 non conta fra le monete della campagna per moneta) e l'esecuzione 39116131334 è verde.

### 3.2 I moduli del bot e cosa fanno

Il giro del bot (`bot/main.py`, docstring): ogni 4 ore scansione del mercato e scelta delle monete; ogni ora regime
del mercato; a ogni candela di 15 minuti chiusa la decisione; a ogni giro del ciclo (30 secondi) aggiornamento delle
posizioni, kill switch e interruttori. Oggi gira «in parità col backtest» (riga «spenta in parita'» nel log di
avvio, ops 0617): apre ogni segnale valido delle coppie validate, uno per moneta, senza chiedere a un modello
(`bot/orchestrator/orchestrator.py:445`, `decide_all`; `bot/main.py:1608`).

| Cartella | Moduli principali | Cosa fanno |
|---|---|---|
| `bot/core` | `models.py`, `config.py` (in `bot/`), `firebase_client.py`, `indicators.py`, `costs.py`, `registry.py`, `gate_fermo.py`, `tempo.py`, `finestra_r1.py` | i contratti dei dati, le impostazioni, il collegamento a Firebase (con ripiego in memoria), gli indicatori, il modello dei costi uguale per gate e paper, la lettura unica del registro, l'interruttore del gate |
| `bot/agents` | `price_agent.py`, `price_stream.py`, `market_scanner.py`, `regime_detector.py`, `sentiment_agent.py`, `onchain_agent.py` | prezzi e funding da Binance, flusso dei prezzi in tempo reale per il paper, scelta delle monete, regime del mercato su BTC, sentiment (CoinGecko), open interest |
| `bot/strategies` | `base.py`, `generated.py`, `generator.py` e 9 strategie scritte a mano (`bot/strategies/__init__.py`, che nel commento dice ancora 8) | le strategie: quelle generate sono combinazioni dichiarative di «mattoncini»; le 9 di base sono a 0 nel registro (`docs/state.md`) |
| `bot/orchestrator` | `orchestrator.py`, `prompt.py` | dai segnali alla decisione |
| `bot/risk` | `hard_limits.py`, `risk_manager.py`, `circuit_breakers.py`, `kill_switch.py`, `correlation_guard.py`, `daily_cap.py`, `portafoglio.py`, `setup_check.py` | limiti fissi nel codice, ultimo controllo prima di ogni ordine, interruttori, tetto per moneta al giorno |
| `bot/execution` | `executor.py` (1.548 righe), `exit_logic.py`, `reconciler.py`, `error_handler.py`, `notifier.py` | ordini (in paper simulati, dal 13 ott con ingresso a ordine limite), uscite condivise col gate, confronto con l'exchange, avvisi Telegram |
| `bot/learning` | `trade_logger.py`, `learning_loop.py`, `adaptation.py`, `metrics.py`, `drift.py`, `calibration.py`, `controllo.py`, `apprendimento.py`, `report.py`, `referti.py`, `rifiutati.py`, `selettore.py`, `supervisor.py`, `cattura.py`, `contributi.py`, `curva_vantaggio.py`, `backlog_doc.py` | scrittura dei trade, pesi notturni, freno da deriva, controllo orario, foto giornaliera, report, misure sui segnali rifiutati, selettore, supervisore |
| `bot/ai` | `client.py`, `hypotheses.py`, `autopsia.py`, `shadow.py`, `analyst.py`, `universe_filter.py`, `spesa.py` | il livello AI: idee di strategie, lettura dei quasi-passaggi, decisioni in ombra, filtro delle monete, conteggio dei consumi |

`scripts/` ha tre famiglie: il **gate** (`optimize.py`, 1.599 righe; `discover_strategies.py`, 4.440; `supervisor.py`;
`gate_progress.py`; `gate_autopsy.py`; `gate_storia.py`; `fast_gate.sh` e gli altri script shell di ricostruzione); le
**misure** in sola lettura chiamate dal canale ops (`trade_stats.py`, `portafoglio_backtest.py`, `mfe_report.py`,
`confronto_gate_paper.py`, `replay_gate.py`, `t_validate.py`, `ingressi_report.py`, `selettore_report.py`,
`rifiutati_report.py`, `controllo.py`, `gate_sul_caso.py` e altre venti); la **manutenzione** (`ops_agent.py`,
`state_snapshot.py`, `monitor.py`, `reset_paper.py`, `verify_keys.py`, `connectivity_check.py`, gli installatori dei
servizi).

### 3.3 Servizi, timer e lavori pianificati

| Cosa | Dove | Quando | Comando | Fonte |
|---|---|---|---|---|
| `trading-bot.service` | macchina | sempre, si riavvia da solo | `python -m bot.main` | `docs/hetzner_setup.md`, passo 10 |
| `trading-ops.timer` → `trading-ops.service` | macchina | ogni 60 secondi | `python -m scripts.ops_agent` | `scripts/install_ops_agent.sh:63-69` |
| `trading-optimizer.timer` → `trading-optimizer.service` | macchina | ogni 3 ore (`OnCalendar=*-*-* 00/3:00:00`) | `scripts.optimize` poi `scripts.discover_strategies` (200 monete, 3 finestre, dal 2022-01-01) | `scripts/install_optimizer_timer.sh:48-64` |
| `trading-supervisor.timer` → `trading-supervisor.service` | macchina | ogni ora | `python -m scripts.supervisor` | `scripts/install_optimizer_timer.sh:84-92` |
| `bot-monitoring` | GitHub Actions | ogni 15 minuti sulla carta; nei fatti 7 volte nelle 24 ore fino al 18 ott 09:00 UTC (`gh run list`) | `scripts.monitor` (avviso Telegram se il bot tace) | `.github/workflows/monitoring.yml` |
| `state-snapshot` | GitHub Actions | ogni 2 ore sulla carta (nei fatti 5 volte nelle stesse 24 ore) e ai push sul principale che toccano `scripts/state_snapshot.py` o il workflow | `scripts.state_snapshot --publish-controllo`, commit di `docs/state.md` | `.github/workflows/snapshot.yml` |
| `nightly-learning-loop` | GitHub Actions | 02:00 UTC (nei fatti fra le 06:19 e le 06:43 UTC negli ultimi quattro giorni) | `bot.learning.learning_loop` | `.github/workflows/learning.yml` |
| `tests` | GitHub Actions | a ogni push sul principale e sulle pull request | `pytest tests/ research/src/tests` | `.github/workflows/tests.yml` |
| `connectivity-check` | GitHub Actions | ai push sul principale che toccano il workflow, `scripts/connectivity_check.py` o `bot/config.py` | `scripts.connectivity_check` | `.github/workflows/connectivity.yml` |
| `claude` | GitHub Actions | a ogni commento con «@claude» del proprietario in una issue | sessione di Claude Code | `.github/workflows/claude.yml` |
| quattro Routine di Claude | claude.ai | — | controllo giornaliero del paper, referto settimanale, controlli orari delle campagne di gruppo e PANIERE | elenco delle Routine dell'account: tutte con `enabled: false` |

L'ultima volta che la macchina ha elencato i timer (ops 0614, 13 ott 18:10 UTC) c'erano `trading-supervisor.timer`,
`trading-ops.timer` e `trading-optimizer.timer` (ultimo avvio 13 ott 15:34 UTC, nessun prossimo avvio indicato).

### 3.4 Cosa è acceso e cosa è spento

| Pezzo | Stato | Fonte |
|---|---|---|
| Bot in paper, `DRY_RUN` | **acceso, `DRY_RUN: True`**, battito 18 ott 04:34 UTC, regime «sideways», equity 827,08, 2 posizioni (PARTIUSDT long, TRUMPUSDT short), rischio aperto 0,32% | `docs/state.md` |
| Ingressi a ordine limite nel paper | acceso dal 13 ott (validità 1 barra, commissione maker 0,02%) | `CLAUDE.md`; ops 0615-0618; `bot/config.py:260-262` (valori predefiniti) |
| Ricerca automatica del gate | **ferma dal 13 ott**: con il file `ops/gate_fermo` i due script del giro escono subito; si riaccende togliendo il file con un commit | `ops/gate_fermo`; `bot/core/gate_fermo.py`; ops 0613 |
| Registro delle validate | congelato al giro del 13 ott 18:40 UTC; il bot continua a operarlo | `docs/state.md` |
| Supervisore | gira ogni ora (ultimo 18 ott 04:03 UTC) ma non cambia nulla: «GATE 1 superato: il paper opera, la taratura si ferma» | `docs/state.md` |
| Freno globale da deriva | attivo: size ×0,5 e leva ×0,71 su ogni trade (profit factor vissuto 0,705 contro 2,02 atteso) | `docs/state.md`, «Deriva paper vs gate» |
| Freno sulle serie di perdite | spento dal 24 set, solo misura | `docs/state.md` |
| Freno per gruppo | spento (valore predefinito) | `bot/config.py:543` |
| Idee AI e autopsia AI; varianti dai referti | spente dal 2 ott | `docs/backlog.md:315` e `:333` |
| Filtro monete AI e ombra AI | spenti dal 30 set (ultima decisione in ombra 30 set 15:47 UTC) | `docs/backlog.md:334`; ops 0585 |
| Gate rigiocato nel passato | fermato dal proprietario il 4 ott | `docs/letture.md:11` |
| Report della mattina e referto settimanale | fermi dall'11 ott fino a nuovo ordine | `CLAUDE.md`; Routine con `enabled: false` |
| Controlli orari delle campagne | spenti (gruppo dall'11 ott, PANIERE dal 14 ott) | Routine con `enabled: false` |
| Agente ops | acceso, battito 18 ott 08:22 UTC | `ops/heartbeat.md` |
| Azioni GitHub | monitoraggio, foto dello stato e learning notturno girano (ultimi: 18 ott 09:05, 04:33, 06:43 UTC); i test sono rossi da 17 ott 20:50 UTC (di nuovo verdi dopo la fotografia, commit `573d084d` delle 09:38) | `gh run list` |
| Vault della ricerca | chiuso: vault 1 aperto l'11 ott, vault 3 il 17 ott (`APERTURA.md`, `APERTURA_3.md`), vault 2 e 4 mai aperti | `research/vault/`; `CLAUDE.md` |
| Guardiano della ricerca | inattivo: il marcatore `research/.sessione` non esiste in questo contenitore | `ls research/.sessione` |

I valori veri delle impostazioni stanno nel `.env` della macchina, che non si legge da qui: dove la tabella cita
`bot/config.py` parla del valore predefinito del codice.

### 3.5 Il canale ops e i comandi ammessi

Come funziona (`ops/README.md`): si committa un file in `ops/requests/` con il nome di una voce; ogni minuto
`scripts/ops_agent.py` sulla macchina fa `git pull`, esegue la voce **solo se è nella lista bianca locale**
`ops/allowlist` (esclusa da git), senza shell, con 900 secondi di tempo e l'uscita tagliata e ripulita da ciò che
somiglia a una chiave, e ricommitta la risposta in `ops/results/`.

La lista di esempio `ops/allowlist.example` ha **60 voci** in cinque gruppi (conteggio per sezione); la copia della
lista vera del 2 ott (ops 0436) ha le stesse voci, con `ingressi-completo` ripetuta:

| Gruppo | N. | Voci |
|---|---|---|
| Diagnosi in sola lettura | 9 | `autopsy`, `gate`, `supervisor` (prova a secco), `stato`, `shadow`, `trades`, `connettivita`, `test`, `gate-top` |
| Analisi che rispondono a una domanda | 28 | `spike`, `gate-vs-paper`, `edge`, `frequenza`, `sopravvivenza`, `timeframe`, `confidenza`, `ai-stato`, `storico-oi`, `confronto`, `portafoglio`, `mfe`, `selettore`, `rifiutati`, `replay`, `controllo`, `costi` (a secco), `autopsia-validate`, `ingressi`, `ingressi-completo`, `ingressi-esito`, `ingressi-orca`, `ingressi-vet`, `voto-t-completo`, `voto-t-esito`, `replay-gate`, `replay-gate-esito`, `report-giornaliero` (quest'ultimo pubblica in dashboard) |
| Diagnosi del canale | 5 | `lista`, `log-ops`, `ops-unit`, `git-stato`, `git-storia` |
| Stato della macchina | 12 | `attivi`, `servizi`, `log-bot`, `rifiuti`, `log-gate`, `log-super`, `memoria`, `disco`, `carico`, `processi`, `tmux`, `cache` |
| Azioni operative | 6 | `aggiorna` (git pull), `riavvia-bot`, `lancia-gate`, `lancia-super`, `riavvia-gate`, `riavvia-super-timer` |

Restano commentate di proposito le due voci che distruggono: `fast-gate` (azzera il registro) e `reset-paper`
(cancella i trade). Nessuna voce esporta i dati in un file del repository.

---

## 4. Gli strumenti della ricerca (`research/src/`)

`research/src/` ha 14 moduli (16.139 righe) e 40 moduli di test (3.153 test). Sono **indipendenti dal bot**: non
importano nulla da `bot/`, `backtesting/` o `scripts/` (docstring di `motore.py`, `dati.py`, `statistica.py`).
Impronte di oggi calcolate con `sha256sum research/src/*.py`.

| Modulo | Righe | Cosa fa | Usato da | Impronta di oggi (inizio) |
|---|---|---|---|---|
| `dati.py` | 2.117 | caricatore dei file Binance, blocco del vault (rifiuta date dopo il 2023-12-31 finché non esiste il marcatore di apertura), controllo delle impronte, allineamento last/mark | tutti i protocolli | `4a6d0ded…` |
| `motore.py` | 2.096 | motore di backtest della prima edizione: tre serie di candele, stop sul mark, funding, liquidazioni | prima e seconda edizione | `2adb94e1…` |
| `statistica.py` | 2.013 | bootstrap a blocchi, confronto con le entrate casuali, p-value, asticelle | prima e seconda edizione; fra gli strumenti congelati anche nei protocolli 3 e 4 | `e42edc00…` |
| `gruppo.py` | 3.073 | l'esecutore unico dell'esame di gruppo (stima dei trade, baseline, blocco, p-value, validazione) | GRUPPO e PANIERE | `f3c19625…` |
| `paniere.py` | 250 | classifica giornaliera delle monete del paniere, causale | PANIERE | `3a58e432…` |
| `selezione.py` | 576 | regole pure della scelta delle monete «come al 31 dic 2023» | coordinamento, Passo 1 | `f0f69423…` |
| `passo1.py` | 164 | il Passo 1 eseguito: liste dei contratti e candele giornaliere del 2023 | coordinamento | `9e7dd3b3…` |
| `fatti.py` | 148 | controlla i riferimenti «file:riga» al codice del bot citati nei documenti | Passo 0 | `46abc25e…` |
| `catalogo3.py` | 1.218 | il catalogo delle strategie del protocollo 3 come dati: indicatori, segnali, riscaldamento | protocolli 3 e 4 | `5c72340f…` |
| `motore3.py` | 583 | motore del protocollo 3, un trade alla volta dal segnale all'uscita, ordini limite | protocolli 3 e 4 | `84d3700c…` |
| `statistica3.py` | 581 | entrate casuali (1.000), p-value, Fase 2, le undici verifiche, vault con Benjamini-Hochberg | protocolli 3 e 4 | `1e5bbd75…` |
| `statistica4.py` | 388 | verifiche della Fase 4 cambiate nel protocollo 4 | protocollo 4 | `bb29a814…` |
| `controllo4.py` | 197 | verifiche sulle 9 monete di controllo (le usa solo il coordinamento) | protocollo 4 | `0e47e91e…` |
| `guardiano.py` | 2.735 | il blocco meccanico: controllo eseguito prima di ogni azione del modello (in `.claude/settings.json`), attivo solo con `research/.sessione` | tutte le campagne | `fa7d4a34…` |

**Quali sono congelati e con quali impronte.**

* **Protocollo 4 (LINK6), le impronte che valgono oggi** («valgono per tutta la ricerca, 13bis.5»,
  `research/collaudo_4/esiti.md`, sezione «Impronte», da `esiti/giro1/impronte.json`): `catalogo3.py` `5c72340f…`,
  `motore3.py` `84d3700c…`, `statistica3.py` `1e5bbd75…`, `statistica4.py` `bb29a814…`, `controllo4.py` `0e47e91e…`,
  `statistica.py` `e42edc00…`, `dati.py` `4a6d0ded…`, `guardiano.py` `fa7d4a34…`, più `research/config/parametri_4.yaml`
  `8f46a666…`, `research/config/bot_4.md` `88dc419c…`, `research/collaudo_4/collaudo.py` `701edfe4…` e
  `research/collaudo_4/regole.md` `4d9dcc6d…`. **Tutte e dodici coincidono** con i file di oggi (`sha256sum`).
  Congelamento: 17 ott, con la delega del proprietario delle 21:10 UTC (stesso file, «Approvazione»;
  `parametri_4.yaml`, campo `stato`).
* **Protocollo 3 (BTC51)**, quarto giro del collaudo del 17 ott, strumenti al commit `7b189254`
  (`research/collaudo_3/esiti.md`, «Quarto giro»): `catalogo3.py` `a9c7e996…`, `dati.py` `440e6ef0…`, `guardiano.py`
  `b8382509…` (questi tre sono cambiati dopo, per il protocollo 4); `motore3.py`, `statistica3.py`, `statistica.py` e
  `parametri_3.yaml` (`85b0e7bb…`) sono uguali a oggi.
* **Seconda edizione (PANIERE)**, prova a placebo del paniere (`research/taratura/placebo_paniere/regole.md`, righe
  60-64): `parametri.yaml` `7f530082…`, `gruppo.py` `f3c19625…`, `motore.py` `2adb94e1…`, `statistica.py` `e42edc00…`
  uguali a oggi; `dati.py` `1a5c36e4…`, poi cambiato.
* **Prima edizione, campagna di gruppo**, prova a placebo di gruppo (`research/taratura/placebo_gruppo/regole.md`,
  righe 114-118): `gruppo.py` `1f3fe8c8…`, `statistica.py` `ca027d26…`, `motore.py` `5a3998c5…`, `dati.py` `4b9ed237…`,
  tutti cambiati dopo; `parametri.yaml` `7f530082…` uguale.
* I file di parametri congelati sono quattro: `research/config/parametri.yaml` (prima edizione), `parametri_2.yaml`,
  `parametri_3.yaml`, `parametri_4.yaml` (`grep stato research/config/*.yaml`): i primi due con `stato: congelato`,
  `parametri_4.yaml` con «congelato il 2026-10-17 dopo il collaudo…»; `parametri_3.yaml` ha ancora nel campo `stato`
  «bozza del Passo 0; … si congela all'approvazione degli esiti», anche se è il file congelato del collaudo
  (impronta `85b0e7bb…`) e gli esiti sono stati approvati il 17 ott (commit `91d2851b`).

Conseguenza pratica: per rifare esattamente un numero di una campagna vecchia non basta il codice di oggi; serve il
codice al commit indicato nelle sue regole (le impronte permettono di verificarlo con `git show <commit>:<file> |
sha256sum`).

---

## 5. Cosa manca per non perdere niente (proposte, non azioni)

In ordine di rischio. Nessuna di queste cose era stata fatta alla fotografia (la 9 è stata fatta dopo).

1. **Esportare i trade del paper.** I 704 trade chiusi esistono solo in Firestore `trades` (sezione 1.5) e un reset li
   cancella senza copia. Proposta: uno script che scriva tutti i trade e lo stato RTDB in un file JSONL con data, da
   lanciare prima di ogni reset e una volta adesso. Il canale ops non basta per riportarlo in git (uscita tagliata a
   20.000 caratteri): o lo script committa il file da sé, o lo si mette in un deposito privato. Va deciso se dati del
   paper, che non contengono segreti, possano stare in un repository pubblico.
2. **Fotografare il registro del gate prima di riscriverlo.** Prima di riscrivere il gate da zero, salvare
   `strategy_registry/validated`, `strategy_registry/esplorative`, `discovered_strategies/specs` e
   `strategy_params/current` in un file (la stessa cosa che fa `fast_gate.sh` con `gate_backup_*.json`). Senza le spec
   le 2.435 coppie non si possono più rigiocare (sezione 1.6). Il registro oggi è fermo, quindi la foto di adesso è
   quella definitiva del vecchio gate.
3. **Copiare i dati che stanno solo sulla macchina**: `data/gate_storia/`, `data/selettore/`,
   `data/gruppo_controllo/`, `data/voto_t/`, `data/replay_gate/`, `data/ingressi_*`, `trades_backup_20260811.json`,
   i `gate_backup_*.json` e `tuning.env` (dopo aver controllato che non contenga segreti). Prima serve sapere quanto
   pesano: una richiesta `disco` e `cache` (voci già ammesse) lo direbbe. Si potrebbe aggiungere alla lista bianca
   una voce che li comprime in un unico archivio sul disco della macchina, da scaricare a mano.
4. **Mettere al sicuro i risultati che stanno solo sui branch** (sezione 2: 543 file, ~271 MiB; ~156 MiB senza
   GRUPPO, che è già nella storia del principale). Proposte:
   un'etichetta git (tag) sulla punta di ognuno dei sette branch, più difficile da cancellare per sbaglio; e una copia
   fuori da GitHub con `git bundle`. Unirli al principale non conviene per `trade/` e `avanzamento/` (~248 MiB: quelli
   di GRUPPO tolti apposta il 12 ott, quelli di PANIERE, 133 MiB, mai entrati), ma conviene per le consegne di BTC51 e
   i risultati di LINK6, che sono piccoli.
5. **Tenere una copia delle candele della ricerca.** I 470 MB di `research/data/` di questo contenitore spariscono
   con lui. Si riscaricano, ma solo finché Binance pubblica le monete tolte dal listino. Una copia compressa in uno
   spazio privato, verificabile con le impronte già nel repo, chiude il rischio.
6. **Salvare la storia che Firebase cancella da solo**: `gate_history/timeline` (240 punti), `lifecycle` (500 eventi),
   `/learning_giorni` (35 giorni), `/btc_history` (200 punti), `/avvii` (20), le 90 versioni dei pesi. Una foto di
   tutto il database adesso conserva l'ultima finestra.
7. **Le conversazioni.** Prima di archiviare la sessione di coordinamento (aperta il 10 giu) e le 37 sessioni di
   ricerca, controllare che ogni decisione del proprietario sia nel diario o nei protocolli. Le conversazioni non
   sono nel repository.
8. **Aggiornare `docs/firebase_schema.md`**, che elenca 7 voci di Firestore su 26 e pochi percorsi RTDB (sezione 1.5):
   chi riscrive il gate deve sapere cosa legge e scrive il bot.
9. **Fuori dal tema dei dati, ma trovato qui:** i test su GitHub sono rossi da ieri sera per un test del guardiano
   (sezione 3.1); andrebbe sistemato prima di cambiare il gate, se no un errore nuovo non si vede. (Sistemato dopo la
   fotografia: commit `573d084d`, 18 ott 09:38 UTC.)

---

## Note sulle fonti di questa bozza

* Comandi usati: `git ls-files`, `git ls-tree -r -l`, `git log`, `git branch -r`, `git merge-base`,
  `git rev-list --left-right --count`, `git for-each-ref`, `du -sh`, `find`, `wc`, `sha256sum`, `grep`,
  `python -m pytest --collect-only -q -p no:cacheprovider`, `gh run list`, `gh run view --log-failed`, l'elenco delle
  Routine e delle sessioni dell'account (sola lettura).
* Nessun file del repository è stato modificato, nessuna richiesta ops è stata creata, nessun segreto è stato letto o
  copiato (il file `.env.example` non è stato aperto).
