# Revisione del backtesting — 19 agosto

Le correzioni precedenti erano mirate: si trovava un difetto, si chiudeva quello.
Funziona finche' i difetti sono indipendenti, e questi non lo erano — due volte di
fila e' saltato fuori lo stesso schema (due contatori su orologi diversi, un campo
letto al posto di un altro) da una porta diversa. Questa volta il controllo e' stato
fatto per intero, modulo per modulo, e sono elencati anche i punti risultati **puliti**:
un elenco di soli difetti non dice quanto e' stato guardato.

Suite: **681 test verdi**, sia con ambiente pulito sia con quello di
produzione (vedi il punto 9 in fondo: non era cosi').

---

## Trovati e corretti

### 1. La 1h di bitcoin usata per quasi tutto l'universo — GRAVE

`Backtester._htf_for` memorizzava la candela oraria ricostruita con chiave
`(prima_candela, ultima_candela, quante)`. Tutte le coin condividono la stessa
griglia temporale: chiesta la stessa storia con lo stesso timeframe, quelle tre cose
sono **identiche** per BTCUSDT e per qualunque altra coin quotata da prima di
`--start`. Il simbolo non c'era.

Conseguenza: dentro ogni worker, la prima serie inserita in cache veniva servita a
tutte le altre. E la prima era sempre **BTC**, perche' il contesto cross-asset si
costruisce all'avvio del worker (`_opt_init`). Quindi il rilevatore di regime e la
conferma dual-timeframe di quasi tutto l'universo leggevano il grafico orario di
bitcoin — nelle finestre di train, in quelle OOS e nell'holdout.

Nessuna eccezione, nessun log, nessun crash: solo numeri sbagliati. E' il difetto
piu' silenzioso possibile, ed e' una spiegazione concreta della divergenza
gate↔paper che inseguiamo da settimane: il paper opera con la 1h **vera** della sua
coin, il gate la validava con quella di BTC.

Attivo solo con timeframe base sotto l'ora — cioe' a 15m, che e' il default
(`ORCHESTRATOR_TIMEFRAME=15m`). A 1h il ramo non si attiva.

Correzione: il simbolo entra nella chiave. Il riuso dentro una coin resta intatto
(lo verifica un test apposta: senza, la grid search costerebbe piu' del dovuto).

### 2. "Profittevole in ogni finestra OOS" misurato su una finestra sola

La consistenza si valuta solo sulle finestre che hanno prodotto trade — ed e'
giusto, una finestra senza segnali non e' una perdita. Ma nessuno controllava
**quante** ne fossero rimaste: una candidata che concentra tutti i suoi trade in una
sola delle tre finestre superava il criterio con una osservazione, e il gate
dichiarava "profittevole in ogni finestra" avendone vista una.

E' la differenza fra un walk-forward e un backtest normale con un nome altisonante.

Correzione: nuovo criterio `oos_windows`, soglia `GATE_MIN_OOS_WINDOWS=2` (su 3).
Non e' fra i parametri tarabili dal supervisore: non e' una soglia di severita', e'
la definizione stessa di walk-forward, e un supervisore che potesse abbassarla si
comprerebbe passaggi cancellando la prova che il gate esiste per raccogliere.

**Effetto atteso: il tasso di passaggio scende.** E' voluto — le candidate che
sparisce sono quelle che non avevano la prova che dichiaravano di avere.

### 3. La deriva purgava in sei ore, e la redenzione promessa non esisteva

Il ramo "coppia smentita dal paper" in `update_registry` **saltava** `judge_window` e
incrementava `fail_count` a ogni run. Col timer ogni tre ore, due run sono sei ore:
una coppia in deriva spariva dal registro in mezza giornata. E non poteva redimersi,
perche' il contatore si azzera solo alla chiusura di una finestra e quella coppia non
ne vedeva mai una — la docstring prometteva esplicitamente il contrario.

E' lo **stesso difetto dei due orologi** che `judge_window` aveva chiuso sul percorso
principale, rimasto vivo sulla scorciatoia. Esattamente il motivo per cui questa
revisione andava fatta a tappeto invece che a colpi mirati.

Correzione: la deriva ora impedisce alla finestra di chiudersi con una conferma
(`passed_in_window = False`) e passa da `judge_window` come tutti. Un fallimento per
finestra, redenzione raggiungibile. La sicurezza non ne risente: la deriva frena
gia' size e leva **in tempo reale** dentro `bot/learning/adaptation.py`, il registro
non e' il freno d'emergenza.

### 4. La lezione di BIRBUSDT scritta nel codice e disattivata dall'ambiente

`_min_history` documenta perche' servono **365** giorni di storia e non 180: con 180,
tolti i 45 di holdout, restano 135 divisi in 4 blocchi, cioe' tre fette contigue
dello stesso trimestre — spesso i primi mesi di una listing nuova, una fase di
mercato sola. E' il caso misurato su BIRBUSDT: 191 giorni di storia, PF 1.51 nel gate
e 0.16 nel paper.

La unit systemd installata scriveva `OPTIMIZER_MIN_HISTORY_DAYS=180`, e l'ambiente
batte il default. La lezione era scritta e non applicata.

Correzione: 365 nella unit, con il perche' accanto.
**Richiede di rilanciare `sudo bash scripts/install_optimizer_timer.sh` sul VPS.**

### 5. Le coin delistate validate su un mercato che non esiste piu'

`quality.looks_delisted` esiste da tempo, ma era cablato solo in
`backtesting/run.py` — il report che si lancia a mano. I due job che **riempiono il
registro** (`scripts/optimize.py`, `scripts/discover_strategies.py`) non lo
chiamavano: una coin con due anni di storia ferma a sei mesi fa passava il controllo
di storia minima e veniva validata normalmente, con l'ultima posizione chiusa a un
prezzo che nella realta' si sarebbe eseguito in un book in liquidazione.

Correzione: il controllo e' nei due job, con una riga di log quando scatta.

### 6. Il confine dell'holdout senza rete di sicurezza

L'holdout include il warmup degli indicatori prima del taglio — corretto, gli
indicatori devono essere caldi. Ma se la storia e' piu' corta del warmup l'indice di
partenza veniva bloccato a zero e i primi trade cadevano **prima** del taglio:
l'holdout avrebbe verificato in parte su dati che la selezione aveva gia' visto.

Non raggiungibile con i parametri attuali (il taglio cade a ~13.000 candele, il
warmup e' 200), ma e' una trappola che aspetta un run piu' corto. Correzione: i trade
vengono filtrati per timestamp sul confine, sempre.

### 7. Il passo della cache dedotto dalla prima coppia di candele

`_merge_candles` deduceva il passo temporale dalla prima coppia. Se proprio li' c'era
un buco (manutenzione dell'exchange), ogni coppia successiva sembrava incoerente e
l'intera serie veniva scartata: quattro anni di candele riscaricati per niente.

Non produceva numeri sbagliati — solo ore di rete buttate, che e' il difetto piu'
difficile da notare perche' somiglia alla lentezza normale. Correzione: il passo e'
il **minimo** dei salti, non il primo. Il controllo resta capace di rifiutare due
serie con timeframe diversi (test apposta).

---

## Controllato e risultato pulito

* **Causalita' degli indicatori.** Tutto `bot/core/indicators.py` usa `rolling`,
  `ewm` e `shift(1)`: nessuna finestra centrata, nessun accesso al futuro. Gli
  indicatori sono calcolati sull'intera serie e poi affettati — corretto, e anzi
  necessario: cosi' l'inizio di ogni finestra ha gli indicatori gia' caldi.
* **Ordine intrabarra.** Nel percorso classico e in quello scale-out lo **stop viene
  controllato prima del take-profit**: se in una barra il prezzo tocca entrambi si
  assume il caso peggiore. E' la scelta conservativa giusta.
* **Profit-lock senza look-ahead.** `best_fav` viene aggiornato **dopo** i controlli
  di uscita, quindi lo stop effettivo della barra `j` usa solo l'escursione fino a
  `j-1`.
* **Timing d'ingresso.** Con `BACKTEST_ENTRY_NEXT_OPEN` l'ingresso e' all'apertura
  della barra successiva al segnale, e stop e target **traslano** con l'ingresso
  invece di restare assoluti: la distanza R resta ancorata al prezzo eseguito, come
  in live.
* **Separazione holdout/selezione.** `split_holdout` taglia prima di calcolare le
  finestre; la selezione non tocca mai l'holdout; la verifica finale usa i parametri
  che verrebbero davvero spediti (`history[-1]`).
* **`cut_to`** usa il confronto stretto (`<`): una sola candela oltre il confine
  sarebbe look-ahead.
* **Cache su disco.** La fonte viaggia con la serie, quindi un'estensione
  incrementale non puo' allungare candele Binance con candele Bybit; l'ultima candela
  in formazione viene rimpiazzata, non congelata; le serie troncate non vengono mai
  scritte in cache.
* **Dati sintetici.** `BACKTEST_ALLOW_SYNTHETIC=false` e' in tutti gli script di
  validazione e in entrambe le unit systemd, ed e' nella lista `NEVER` del
  supervisore.
* **`_prep_cache`** (snapshot e regimi per barra) aveva gia' il simbolo nella chiave:
  il difetto n.1 riguardava solo la cache 1h.
* **Contabilita' del registro** (`judge_window`, purge, `ready`): rivista dopo la
  correzione del 19 agosto, coerente. Il ramo deriva era l'unica scorciatoia
  rimasta, ed e' il punto 3.
* **Budget di falsi positivi** del supervisore: l'unita' di occasione e' la finestra,
  coerente con `judge_window`.

---

## Da fare sul VPS

```bash
cd ~/agentic_trading_system
git pull
sudo bash scripts/install_optimizer_timer.sh     # applica MIN_HISTORY_DAYS=365
```

Il resto entra da solo al prossimo run dell'optimizer (ogni 3 ore).

## Cosa aspettarsi

Il tasso di passaggio **scendera'**: due criteri in piu' (finestre OOS, coin
delistate) e uno storico minimo piu' lungo. Non e' un peggioramento — e' il numero
che avremmo dovuto vedere fin dall'inizio. In compenso il difetto n.1 significa che
**tutte le valutazioni fatte finora a 15m vanno considerate sospette**: il regime era
quello di bitcoin. Le 224 coppie a 1 pass nel registro sono state prodotte cosi'.

---

## Aggiunta del 19 agosto sera — trovati usando il canale ops

Le due correzioni qui sotto non vengono dalla lettura del codice ma dall'aver
**lanciato** le verifiche sulla macchina. Sono il tipo di difetto che una revisione
statica non trova, perche' esistono solo nell'ambiente reale.

### 8. Una terza contabilita' del registro, in `discover_strategies`

`merge_into_registry` teneva una **copia a mano** della vecchia regola del "pass
onesto" (differenza fra due `data_end`) e non chiamava mai `judge_window`. Quindi le
coppie **generate** — che sono la maggioranza del registro — accumulavano conferme con
un criterio, e le base con un altro. Il suo ramo deriva incrementava `fail_count` a
ogni run, come quello di `optimize.py` prima della correzione n.3.

E' ancora una volta lo stesso schema: finche' esistono due copie della stessa regola,
prima o poi divergono. Ora `judge_window` e' l'unica contabilita' del registro.

Effetto collaterale visibile: `gate_progress` stampava «finestra chiusa il 08 Jan» per
le coppie generate. Era il 1970 — la settimana sommata a un `window_start` mai
impostato. Una data falsa in mezzo a date vere, che sembra un dato e non lo e'. Ora
dice «finestra non ancora aperta», e le finestre si aprono davvero alla prima passata
della discovery dopo l'unificazione.

### 9. La suite era rossa **solo sulla macchina**: 11 test

Lanciata via canale ops, `pytest` restituiva 11 fallimenti su 679 — e qui era verde.
Non una regressione: le unit systemd hanno `EnvironmentFile=.env`, quindi la
configurazione di produzione (scale-out attivo, cap di rischio diversi) arriva
dall'**ambiente del processo**. Il `conftest` disattivava la lettura del `.env` —
difesa giusta ma insufficiente, perche' le variabili erano gia' dentro.

Perche' conta piu' di quanto sembri: una suite rossa per default sulla macchina non e'
una rete di sicurezza, e' rumore. Chi la lancia smette di distinguere una regressione
vera da uno scarto di configurazione — ed e' esattamente cio' che serve saper
distinguere quando si e' lontani e si puo' solo leggere un output. Il canale ops, che
esiste per questo, ereditava lo stesso ambiente e restituiva lo stesso rosso.

Correzione: il `conftest` ora **toglie** dall'ambiente tutte le variabili di
configurazione, e la lista si ricava dai sorgenti invece di essere scritta a mano —
un'impostazione aggiunta domani viene neutralizzata senza che nessuno se ne debba
ricordare. Verificato: la suite passa identica con l'ambiente pulito e con quello di
produzione.

**681 test verdi**, in entrambi gli ambienti.
