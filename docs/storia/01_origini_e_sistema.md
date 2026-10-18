# 01 — Origini e sistema: giugno-agosto 2026, la storia del gate e del bot

> Capitolo della storia del progetto: il riepilogo è in [`README.md`](README.md). Scritto il 18 ottobre 2026 da un lettore in sola lettura sul repository, poi ricontrollato da un secondo lettore che ha aperto le fonti e corretto nel testo gli errori trovati (circa 160 affermazioni, circa 150 giuste, 10 corrette). Dove il testo dice «bozza» o «questo pezzo», intende questo capitolo.

_Bozza scritta il 18 ottobre 2026. Copre dal primo commit (10 giugno 2026, 07:15 UTC) al 31 agosto 2026 in
dettaglio; per il gate e per lo stato attuale delle parti del bot arriva fino a oggi, ma settembre e
ottobre sono solo riassunti (li racconta un'altra parte della storia)._

## Come leggere questa bozza

* **Fonti.** Ogni numero porta la sua fonte fra parentesi:
  * un **hash di commit** (8 caratteri, es. `81be83a1`): si legge con `git show <hash>`; quasi tutti i
    commit di questo periodo hanno nel messaggio il perché e i numeri;
  * uno **stato** (es. «stato `49d4f886`»): è la fotografia di `docs/state.md` committata in quel
    momento da GitHub Actions; si legge con `git show 49d4f886:docs/state.md`. Ne esistono 677 fra il
    13 giugno e il 31 agosto, in media una ogni ~3 ore;
  * un **risultato ops** (es. `ops/results/0021-gate-27ago.md`): la risposta della macchina a una
    richiesta del canale ops (esiste dal 14 agosto);
  * un **file del repo** con la sezione (es. `docs/audit_fase0.md` §5.1).
* **«stima»** vuol dire che il numero l'ho ricavato io (somme, differenze, letture di serie), non che
  sta scritto in una fonte.
* **Quanti commit.** Fra il 1 giugno e il 31 agosto ci sono **1.391 commit**: 302 scritti da Claude
  (il lavoro vero), 677 fotografie automatiche dello stato (`github-actions`) e 412 risposte del canale
  ops (`ops-agent`, dal 14 agosto) (conteggio con `git log --format=%an`).

### Piccolo dizionario (le parole che tornano sempre)

| Parola | Cosa vuol dire |
|---|---|
| **GATE 1**, «il gate» | il filtro che decide quali strategie il bot può usare: le prova sulla storia (backtest) e scrive le promosse nel **registro**. |
| **GATE 2**, «il paper» | il bot che opera con soldi finti (`DRY_RUN=true`) sui prezzi veri di Binance. È l'esame dopo il gate. |
| **coppia** | una moneta più una strategia, es. `BIRBUSDT|gen_472f85b8`. Il gate giudica coppie, non strategie. |
| **registro** | il documento Firestore `strategy_registry/validated`: tutte le coppie seguite, coi loro passaggi. Il bot opera solo quelle «validate». |
| **pass / conferma** | una volta in cui la coppia supera il gate. Dal 10 agosto conta solo se è passata una settimana di dati nuovi dall'ultima (dal 14 agosto: una per «finestra» di 7 giorni). |
| **validata** | coppia con almeno 3 conferme (`OPTIMIZER_MIN_PASSES=3`). |
| **ready** | il gate dichiara «superato»: abbastanza coppie validate (prima una percentuale di monete coperte, poi anche un numero minimo di coppie) perché il bot possa operare. |
| **walk-forward / OOS** | si sceglie la strategia su un tratto di storia e la si giudica sul tratto **dopo**, mai visto («fuori campione», in inglese out-of-sample, OOS). |
| **holdout** | gli ultimi 45 giorni di storia, tenuti fuori da ogni scelta e usati solo come esame finale (dal 31 luglio). |
| **PF** (profit factor) | somma dei guadagni diviso somma delle perdite. 1 = pareggio. |
| **R** | il rischio del trade: la distanza fra ingresso e stop. Perdere 1R = stop pieno. |
| **mfe_r** | quanto lontano è andato il prezzo a favore, misurato in R (dal 30 luglio su ogni trade). |
| **scale-out / scala di TP** | uscita a gradini: es. 30% a 1,5R, 30% a 3R, 40% a 5R. |
| **profit-lock / trailing** | lo stop che sale quando il trade va a favore, per non restituire tutto. |
| **BE** (break-even) | stop spostato al prezzo d'ingresso dopo il primo gradino. |
| **generata** (`gen_xxxxxxxx`) | strategia inventata dal sistema combinando «mattoncini» (feature) di indicatori; le **base** sono le 8–9 scritte a mano. |
| **parità** (`BACKTEST_PARITY`) | modalità in cui il paper fa esattamente quello che il gate ha simulato (stessi costi, uscite, timeframe), spegnendo i freni che il gate non modella. |
| **deriva** (drift) | il confronto paper-contro-promessa del gate (dal 4 agosto). |
| **autopsia** | il conteggio di quale criterio del gate ha bocciato ogni candidata (dal 13 agosto). |
| **supervisore** | il processo orario che ritocca da solo le soglie del gate dentro un «budget di falsi positivi» (dal 13 agosto). |
| **ops** | il canale per chiedere comandi alla VPS via git: richiesta in `ops/requests/`, risposta in `ops/results/` (dal 14 agosto). |
| **VPS** | il server Hetzner dove girano bot e gate. |
| **RTDB / Firestore** | le due basi dati Firebase: la prima per lo stato veloce (posizioni, battito), la seconda per lo storico (trade, registro). |

---

## 1. Cos'era il sistema al primo commit e cosa voleva fare

### Il primo giorno: tutto in otto ore

Il 10 giugno 2026 ci sono **17 commit** (conteggio per giorno da `git log`). In ordine:

| Ora UTC | Commit | Cosa |
|---|---|---|
| 07:15 | `76e6723f` | Fondamenta: 36 file, 2.598 righe. Configurazione, modelli dati, indicatori, **8 strategie**, rischio con limiti fissi (leva max 5x, rischio max 3% a trade), interruttori di emergenza, controllo delle correlazioni, agenti dati (prezzo, sentiment, on-chain, macro), **14 test**. |
| 07:18 | `c7da8429` | «Orchestratore + motore di apprendimento (il cuore)»: Claude decide il trade col resoconto del learning nel prompt; pesi per strategia×regime ricalcolati di notte; 20% del capitale sempre senza adattamento come riferimento. |
| 07:21 | `b11e8666` | Esecuzione (stesso codice in paper e in live), ordini limite, trailing a +1 ATR, uscita parziale del 50%, ciclo 24/7 (scan ogni 4h, regime ogni ora, decisione ogni 15 minuti), Telegram. |
| 07:30 | `a0e0860e` | **GATE 1**: motore di backtest con conteggio delle liquidazioni a 2x/3x/5x/10x/20x. Il verdetto: «superato se almeno una strategia è profittevole» (`backtesting/engine.py`, funzione `verdict`, in quel commit). |
| 08:02 | `ebb1e7f4` | GitHub Actions (learning notturno alle 02:00, monitoraggio ogni 15 minuti, test, backtest), documentazione. |
| 08:03 | `5f97003b` | Dashboard Next.js 14 per Vercel: stato, posizioni, curva dell'equity, mappa strategia×regime, pesi, pannello del rischio, interruttore di emergenza. |
| 14:57 | `67e3ba5f` | Regole di sicurezza Firebase e login Google sulla dashboard. |
| 15:29 | `f861e18f` | Il GATE 1 passa a dati veri: Binance → Bybit → OKX, con ripiego su dati **sintetici** (questo ripiego sarà la causa di un incidente il 24 giugno). |
| 20:10 | `282fd22e` | Backtest su un paniere di monete (BTC, ETH, SOL, BNB, XRP). |

### Cosa voleva essere

Dal `README.md` del primo commit (`git show 76e6723f:README.md`):

* «Sistema di trading algoritmico **agentico** e **auto-apprendente** per crypto futures su Binance»;
* «il cuore del progetto non è un insieme di regole fisse: è un motore di apprendimento» che adatta i
  pesi delle strategie «senza intervento manuale»;
* un **orchestratore LLM** (Claude) chiamato a ogni candela da 15 minuti, che riceve indicatori,
  sentiment, Fear & Greed, funding, eventi macro, il resoconto del learning e gli ultimi 20 trade, e
  sceglie **un** trade (o nessuno);
* uno scanner che ogni 4 ore guarda tutto l'universo dei futures Binance e sceglie 3–5 monete;
* limiti di rischio scritti nel codice e mai esposti all'LLM;
* tutto nel cloud: codice su GitHub, bot 24/7 su una VPS Hetzner, stato su Firebase, dashboard su
  Vercel, job notturni su GitHub Actions;
* ordine di marcia: **GATE 1** (backtest) → **GATE 2** (paper) → soldi veri, e `DRY_RUN=true` di
  default.

### Cosa è rimasto, cosa no (anticipazione)

* L'**LLM che decide i trade non ha mai deciso un trade.** Dal 30 giugno il bot in parità apre ogni
  segnale valido con una funzione deterministica (`decide_all`), e il ramo LLM «non viene MAI
  raggiunto» (`docs/audit_fase0.md` §1.8, `61e8fba5`). Dal 12 agosto l'LLM è stato provato solo
  «in ombra» (registra cosa avrebbe fatto, `4079ffb6`).
* Il **motore di apprendimento** è rimasto, ma col tempo ha perso il ruolo di «cuore»: i pesi
  modulano la size, non scelgono le strategie. Le strategie le sceglie il gate.
* Lo **scanner che sceglie 3–5 monete** è diventato «le monete che hanno almeno una coppia validata»
  (`86893393`, 7 luglio).
* Il **GATE 1** è passato da «almeno una strategia in utile su un paniere» a un filtro con dieci
  criteri, holdout, tre conferme settimanali e un supervisore (sezione 3). È fermo dal 13 ottobre
  (`ops/gate_fermo`).
* Le **strategie scritte a mano** non sono mai arrivate alla validazione dopo che il gate è diventato
  onesto. Qualche coppia base ha preso una conferma (es. `MUSDT|mean_reversion` in
  `ops/results/0016-finestre-aperte.md`, `MUBARAKUSDT|mean_reversion` in
  `ops/results/0027-registro-dopo-due-run.md`), ma al 27 agosto il giro faceva «0 passaggi su 1.136
  valutazioni» (`docs/andremo_live.md`, «Cosa dice l'evidenza contro»); dal 21 settembre sono escluse
  dal giro (`1670bc71`).

---

## 2. Cronologia per settimana (10 giugno – 31 agosto)

Per ogni settimana: quanti commit, cosa è stato costruito, tolto o cambiato e perché, e com'era lo stato
alla fine della settimana. I conteggi «Claude/totale» vengono da `git log --author` per settimana.

### Settimana 1 — 10–14 giugno (37 commit di Claude su 55): costruire tutto, e il primo «gate continuo»

* **10 giugno**: vedi sezione 1.
* **11 giugno**: guida e script d'installazione della VPS Hetzner (`281e8729`, `ae0e02b1`). Le fonti a
  pagamento (LunarCrush, Coinglass) sostituite con fonti gratuite: CoinGecko per il sentiment, Binance
  pubblico per open interest e funding (`2f34883f`). **Primo ottimizzatore walk-forward** (`fdb4473d`):
  le strategie diventano parametriche; per ogni moneta si cercano i parametri sul tratto di train e si
  giudicano sul tratto dopo; una coppia «passa» con PF fuori campione ≥ 1,10, guadagno > 0 e almeno 10
  trade (`backtesting/optimizer.py` in quel commit). Gira ogni giorno alle 03:00.
* **12 giugno**: ogni trade del backtest paga **0,08% di commissioni+slippage** andata e ritorno
  (`55c09a27`): «passato» vuol dire netto, non lordo. L'ottimizzatore lavora sulle prime N monete per
  volume, non su 3 fisse (`d3b071ea`).
* **13 giugno**: nasce `docs/state.md`, la fotografia dello stato letta da Firebase e committata da una
  Action (`b40400a1`) — sarà per mesi l'unico modo di vedere la VPS da fuori. Nasce il **gate
  continuo** (`1661bc2e`): una coppia è «validata» solo dopo aver passato in **3 giri** (`MIN_PASSES=3`),
  e il gate è «superato» quando le validate coprono abbastanza monete (prima 5, poi 15 in `03904791`,
  poi il **60% dell'universo scansionato** in `6b9acb9a`). L'ottimizzazione gira su GitHub ogni 6 ore
  «senza bisogno della VPS» (`03904791`).
* **14 giugno**: il backtest paga anche il **funding** (`530f2c20`). Filtro di storia minima (~10.000
  candele, ~14 mesi) e scadenza delle validate dopo 3 giorni senza essere riviste (`d7d4000c`): il
  motivo scritto è che il primo gate passava quasi solo memecoin nuove. Lo stesso giorno la storia
  minima viene **abbassata** a ~2.500 candele (~3–4 mesi) e l'universo OKX ordinato per volume in
  dollari (`ce1c3fdc`); si aggiunge l'opzione per azzerare il registro «per ripartire puliti»
  (`b265fd50`), usata il 15 giugno con un giro una tantum (`1158d4a8`).
* **Stato a fine settimana** (stato `e0c60acc`, 14 giugno 23:38): gate «✅ SUPERATO», 48 coppie
  validate, 22 monete coperte su 34 (65%); ultimo giro 204 coppie valutate, 31 passate. Bot non ancora
  acceso sulla VPS.

### Settimana 2 — 15–21 giugno (39 su 85): il bot parte, e i primi difetti gravi

* **15 giugno**: universo solo Binance (OKX dava anche azioni e metalli tokenizzati che il bot non può
  comprare) (`1158d4a8`). Il bot gira sulla VPS: prima fotografia con lo stato «running» alle 18:47
  (stato `aa67b5e8`). Ripristino delle posizioni dopo un riavvio (`44561c40`): prima ogni riavvio
  «orfanizzava» le posizioni.
* **16 giugno**: si scopre che **nessun trade chiuso veniva registrato**: Firebase RTDB rifiuta
  `set(None)`, l'eccezione interrompeva la chiusura prima di scrivere il trade, e restavano posizioni
  «fantasma» (`cd6edb42`). Nasce `scripts/reset_paper` per ripartire puliti (`7ab31785`). L'equity del
  paper non veniva mai aggiornata — restava ferma a 10.000 — e viene corretta (`744a7ff9`, `426a3be6`).
  Il PnL del paper diventa netto di commissioni e funding come nel backtest (`2cdc8a07`).
* **17 giugno**: **scoperta automatica di strategie** (`515fcec0`): il sistema inventa strategie come
  combinazioni di mattoncini su indicatori (`bot/strategies/generated.py`, `generator.py`) e le passa
  allo stesso gate. Lo stesso giorno: l'interruttore della perdita giornaliera contava la perdita **sul
  margine** (amplificata dalla leva) invece che sul capitale, e fermava il bot dopo 2–3 stop normali
  «pur essendo +65 complessivo» (`700591c1`). **Il VWAP era cumulativo su tutta la serie**: produceva
  PF da 99 a 262 e guadagni fuori campione del 57.000–71.000% su `vwap_reversion` (`7ef6aa74`); registro
  azzerato (`cda28b50`).
* **18 giugno**: orizzonte del gate esteso a **4 anni, dal 1 gennaio 2022** (include il crollo del 2022)
  (`71d62680`); il backtest si divide in 3 pezzi paralleli su GitHub (`e930ace0`).
* **19 giugno**: con 883 coppie il documento del registro supera il limite di Firestore (40.000 voci
  d'indice) e il registro smette di aggiornarsi; le coppie diventano una stringa JSON e il registro
  ha un tetto di **3.000 coppie** (`436d1958`) — quel tetto sarà il cuore dell'incidente del 31 agosto.
* **20 giugno**: **prima correzione di parità**: il backtest usciva a stop o target pieno, mentre il
  bot usava uscita parziale del 50% + trailing, cioè «i vincenti venivano tagliati corti mentre i
  perdenti prendevano lo stop pieno» (`f56d641e`). Il bot si allinea al backtest.
* **21 giugno**: il bot cerca segnali su 100 monete e non più su 30 (`12faeeca`); pausa di 4 ore su una
  moneta dopo uno stop (`5f1b2127`); «panchina» di 8 ore per una strategia dopo 3 stop di fila invece di
  fermare tutto il bot (`bc16b710`); questi stati sopravvivono ai riavvii (`970c907d`).
* **Stato a fine settimana** (stato `82140326`, 21 giugno 23:45): bot online, equity **$9.580,02**
  (partita da $10.000 il 16 giugno, stato `34beca98`); gate «superato», 56 validate, 48 monete su 80
  (60%).

### Settimana 3 — 22–28 giugno (26 su 73): il gate si fa severo, e scopriamo che validava su dati finti

* **22 giugno**: le coppie validate crollano **da 432 a 56** perché le generate non venivano
  rivalutate e scadevano dopo 3 giorni (`ff607d55`). Il bot, se il registro non era leggibile,
  **operava tutto senza validazione**: da qui `REQUIRE_VALIDATED_PAIRS` (resta flat) e un filtro di
  liquidità a 25 milioni di dollari al giorno (`a92cb0a7`).
* **23 giugno**: **gate più severo** (`80e3e731`): PF ≥ 1,25, vinti ≥ 45%, almeno 20 trade, ritorno
  fuori campione ≥ 15%, e in utile **in ogni finestra** fuori campione. Arriva il **profit-lock**
  (oltre metà strada verso il target lo stop blocca metà del miglior guadagno) con la stessa logica nel backtest e nel bot
  (`bot/execution/exit_logic.py`). Registro e paper azzerati (stato `07655b9c`: equity $10.000, 2
  validate).
* **24 giugno**: per accelerare, `MIN_PASSES` passa a **1** nella ricostruzione (`8af08741`): «la
  robustezza ora la danno il gate severo […] non il ripetere lo stesso run su dati identici». Poche ore
  dopo il **difetto più grave del mese** (`073ab5f8`): dai server di GitHub Binance rispondeva 451
  (blocco geografico), Bybit 403, OKX 429, e il caricatore ripiegava su **dati sintetici** — una
  passeggiata casuale con lo stesso seme (7) per **ogni** moneta. Risultato: coppie validate finte,
  «robusta su 18 monete», +500% inventati. «Il registro attuale è da buttare.» Le pianificazioni su
  GitHub vengono spente (`b6e72a34`) e il gate si sposta sulla VPS con un timer notturno alle 03:00,
  top 80 monete, 4 anni, niente dati sintetici (`e464b505`).
* **25 giugno**: il servizio del gate veniva ucciso da systemd dopo 90 secondi (`ffd40694`; causa dubbia: il 15
  agosto `44621f57` scrive che a un servizio oneshot systemd non applica un timeout di avvio di default); un crash nel
  riepilogo finale impediva alla scoperta di partire (`a9dfb500`); `MIN_PASSES` torna a **3**
  (`f72ebb92`): «filtra le strategie generate fortunate su un singolo giro».
* **27 giugno**: timer **ogni 8 ore** (00, 08, 16 UTC) (`c1834fae`). Tre correzioni da un controllo del
  gate (`47f5d37e`): una strategia senza perdite aveva PF = guadagni e veniva bocciata; una finestra
  senza abbastanza trade nel train applicava parametri non validati; una finestra senza segnali contava
  come perdita. Il bot opera una strategia solo se è validata su **almeno 3 monete** (`c6a3eae9`).
  Storia minima a **2 anni** (17.520 candele orarie) per escludere le monete appena quotate e gonfiate
  (`8dfc370b`).
* **Stato a fine settimana** (stato `23962ac2`): bot spento per manutenzione, equity $10.000, 74
  validate, 30 monete su 38 (79%).

### Settimana 4 — 29 giugno–5 luglio (13 su 64): la parità col backtest

* **29 giugno**: universo del gate da 80 a **400 monete** (`7617e562`), su richiesta: «più crypto, senza
  ripartire da zero».
* **30 giugno**: nasce **`BACKTEST_PARITY`** (`f1805b45`): il bot spegne i freni che il backtest non ha
  (perdita giornaliera, pausa sulla moneta, panchina) così che paper e gate siano confrontabili. Più
  strategie aperte insieme, ognuna con al massimo il **10% dell'equity** di margine (`a42f0954`,
  richiesta del proprietario: «non ridurre il numero di trade, al massimo la size»). In parità il bot
  apre **ogni** segnale valido del ciclo (`decide_all`), «niente LLM» (`f7a12b13`).
* **1 luglio**: in parità il regime si calcola per ogni moneta, come nel gate (`5484c611`).
* **2 luglio**: il trend diventa un «inclinatore» della size, solo dal vivo (`74e7a5cb`). **Seconda
  correzione di parità**: il bot ricalcolava stop e target coi valori fissi del gestore del rischio
  (1,5 ATR / rapporto 2,0) invece di quelli validati della strategia (`3b43f17d`): «il paper perdeva
  mentre il backtest era positivo».
* **3 luglio**: chiusura manuale delle posizioni da dashboard (`bacef957`).
* **Stato a fine settimana** (stato `1e68796e`): equity **$9.911,34**; gate con **738 coppie validate**,
  copertura **167 su 167 monete (100%)**. Questi numeri vanno letti col senno di poi: le finestre fuori
  campione erano sempre le stesse a ogni giro e tre giri al giorno davano tre «conferme» sugli stessi
  dati (diagnosi del 31 luglio, `81be83a1`).

### Settimana 5 — 6–12 luglio (17 su 74): la «causa radice» del timeframe

* **5–8 luglio**: strumenti di diagnosi in sola lettura: strategie in perdita (`ce3afea4`), statistiche
  dei trade (`79bc84f5`), analisi della confidenza (`f754aabb`). Ogni trade registra il suo TP e il suo
  stop; la dashboard mostra un verdetto «controfattuale» sul trailing (avrebbe vinto restando?)
  (`8cf135aa`, `a966c2af`). Dashboard a schede (`e1cfc011`). L'universo del bot diventa esattamente
  quello delle monete validate (`86893393`).
* **9 luglio**: **«CAUSA RADICE del paper ≠ gate»** (`90d4c783`): il gate validava su candele da **1
  ora**, ma il bot faceva girare le stesse strategie su candele da **15 minuti** («tutte cablavano
  `ind("15m")`»). Segnali, ATR, stop e target completamente diversi da quelli validati. Nasce
  `ORCHESTRATOR_TIMEFRAME`, unico per gate e bot (allora 1h).
* **10 luglio**: il caricatore dei dati si fermava al 1 gennaio 2026 fisso (`3536dfe5`). Nuova strategia
  base **Momentum** (`32b071b3`): le strategie base diventano 9.
* **11 luglio**: niente filtro di liquidità in paper (tagliava ~168 monete validate a ~30) (`5cfcaed4`);
  al suo posto un **costo che dipende dalla liquidità** dentro il gate (`fe794aa0`): lo spread stimato
  si allarga sulle monete sottili, e chi non lo batte è bocciato.
* **Stato a fine settimana** (stato `4911db1a`): equity **$10.571,77**; 431 validate (il giorno prima
  erano 872, stato `a939fed1`: il calo coincide con la rivalidazione coi costi nuovi, `7829c8a5` —
  collegamento mio, non scritto in un commit).

### Settimana 6 — 13–19 luglio (18 su 83): costi misurati, passaggio ai 15 minuti, registro vuoto

* **13 luglio**: lo spread vero misurato su Binance è molto più stretto delle stime: **0,010% / 0,021% /
  0,039% / 0,068%** andata e ritorno per fascia di volume, contro 0,02/0,05/0,10/0,20% stimati, «2–3
  volte troppo alte» (`8b45914b`). Pesi del learning con «restringimento» graduale invece del salto a 5
  trade (`a2f49878`). Verdetto del trailing salvato nel registro (`5ed82a6b`): nel complesso il
  profit-lock taglia più vincitori di quanti ne protegga, **48% prematuri contro 36% protetti**
  (`0898ce2c`). **Auto-pulizia** del registro: fuori dopo 2 bocciature di fila (`bcd56431`).
* **15 luglio**: pesi ricalcolati ogni ora dal bot (`f4610600`); riserva di margine come Binance e
  funding visibile sulle posizioni aperte (`97f85fae`); **funding al tasso reale e col segno** (chi è
  long paga se il tasso è positivo) (`44341f0b`). **Passaggio al timeframe da 15 minuti** per gate e
  bot (`c8337045`): stop più stretti, posizioni più brevi. Lo stesso giorno un controllo da capo a fondo
  trova **15 difetti** (`67e71c98`), fra cui: nel backtest la «candela da 1 ora» era un alias della riga
  da 15 minuti (regime e doppia conferma ridotti a tautologia); il bot teneva le posizioni 96 **ore**
  invece di 96 **barre**; la storia minima in candele era 4 volte più debole a 15 minuti; la cache
  accettava serie troncate; l'interruttore d'emergenza chiudeva a prezzi vecchi; gli indicatori dal vivo
  usavano la candela ancora in formazione. Pesi in «prova» invece di sparire (`81d4ef0b`).
* **16 luglio**: la ricostruzione del registro a 15 minuti non finiva in 19 ore; memorizzando le
  fotografie per barra il motore va **~70 volte più veloce** (`be22f98d`).
* **Stato a fine settimana** (stato `9efbe928`): equity **$10.875,74** (ferma dal 15 luglio: nessun
  trade), gate «in corso», **0 coppie** nel registro.

### Settimana 7 — 20–26 luglio (32 su 78): il registro rinasce a 15 minuti, la scala di TP

* **21 luglio**: «CAUSA VERA del registro sempre vuoto» (`886c5a3f`): l'ottimizzatore finiva il calcolo
  (1h31 di CPU) e poi crashava all'ultima scrittura su Firestore, per lo stesso limite di indici del 19
  giugno, su un altro documento. Poi, con 59 coppie passate, il bot ne operava 0 perché non decodificava
  il nuovo formato (`e2378080`). Le generate vengono esentate dalla regola «almeno 3 monete» (sono
  «specifiche di una moneta per costruzione»). **Scelta del proprietario: niente trading su strategie
  non validate** (`b0c31c0e`). Script per fare 3 passate di fila (`4129be24`).
* **22 luglio**: il bot non controllava mai il «gate superato» e apriva trade con la copertura all'1%
  (`359493ad`); ora resta flat sotto soglia. Il tetto di rivalutazione delle generate passa da 80 a 500
  (`a5038973`).
* **25 luglio**: **allocazione guidata dai dati** (`83fb29bd`): rischio e leva = scelta dell'utente ×
  convinzione del segnale × peso appreso, dentro i limiti; il profit-lock di ogni strategia impara dai
  verdetti del paper (voce interna B2). Le chiusure manuali escono dal learning (`f3e601a3`). Leva
  arrotondata all'intero (`a479e3bc`). Restyling totale della dashboard (`5c203dbb`…`54be8c53`).
* **26 luglio**: **scale-out su multipli di R** dietro un interruttore (`91084bc5`); prova A/B sugli
  stessi dati: la scala **1,5R / 3R / 5R con quote 30/30/40** batte il TP unico «su 4/4 metriche» su 2
  semi e fino a 377 coppie (`2dddd4b1`); promossa a standard con ricostruzione del registro
  (`0043602d`). Learning ricalcolato a ogni trade chiuso (`d6108e5b`). «Inclinatore» del sentiment, solo
  dal vivo (`8fcad1fe`).
* **Stato a fine settimana** (stato `77159b80`): equity **$10.051,45**; registro a 0 dopo la promozione
  dello scale-out. In tre giorni (23–26 luglio) le validate erano salite da 44 a 718 (stati `4f76812b`,
  `777d47d3`): tre passate di fila sugli stessi dati bastavano a «validare».

### Settimana 8 — 27 luglio–2 agosto (27 su 88): fedeltà del paper e riforma del gate

* **28 luglio**: l'equity di partenza del paper passa da **$10.000 a $1.000** «più realistica»
  (`7614bc5b`).
* **29 luglio**: registro ricaricato ogni ora (era ogni 6) (`6e9088d5`); tolto un avviso Telegram «−3%»
  che non corrispondeva a nessuna azione (`cbce2b79`); ogni gradino del TP incassa e libera margine
  come su Binance (`d14a299b`).
* **30 luglio**: giornata della **fedeltà del paper** (14 commit): gli ordini TP/SL scattano sulle
  **ombre** delle candele come nel gate e su Binance (`fe6651d8`); in live, un ordine di protezione per
  ogni gradino (`fe46de5f`); **flusso WebSocket dei prezzi** e **riproduzione del percorso** punto per
  punto, perché «stesso range, esito opposto» se il prezzo tocca prima il TP o prima lo stop
  (`fdf480a4`, `c23a39fe`). Dalla VPS gli stream dei trade di Binance futures restavano muti (accettati
  e poi silenziosi), il libro prezzi no: si usa il **prezzo medio fra miglior bid e ask**
  (`441a2c63`). Un filtro «anti-rumore» dello 0,02% cancellava i tuffi sotto il break-even e faceva
  incassare TP mai raggiunti: paper **ottimista**, filtro tolto (`96f8d893`). **Scala di TP per coppia**
  scelta dal gate e congelata all'ingresso; nasce `mfe_r` (`f3f253a4`).
* **31 luglio**: **riforma del GATE 1** (`81be83a1`). Il paper aveva fatto **−99 su 74 trade contro +80
  attesi** dalla promessa (scarto ~2,4 sigma). Diagnosi: le finestre fuori campione erano identiche a
  ogni giro e migliaia di candidate venivano scelte su di esse, quindi «l'OOS era diventato un training
  set» e il conteggio dei passaggi contava rivalutazioni degli stessi dati; «i numeri implausibili del
  registro (PnL OOS 700%+, PF 4+) sono l'impronta di questa lotteria». Correzioni: **holdout di 45
  giorni mai usato per scegliere**; un passaggio conta solo con **24 ore di dati nuovi**; veto del
  regime in cui il gate ha visto la coppia perdere; **minimo 30 trade** (era 20). Poi: il gate premia il
  **profitto continuo**, ritorno/caduta massima ≥ 2 (`28029e80`). Lo script di ricostruzione lasciava il
  bot aprire posizioni col registro vecchio per un'ora (`107d1961`).
* **1 agosto**: il passaggio «onesto» non era chiuso in caso di dubbio: senza data dei dati, contava
  comunque (`15d0a03c`); e un mio ordine sbagliato di due righe cancellava la scala per coppia delle
  generate.
* **Stato a fine settimana** (stato `bab841e7`): equity $1.000, nessun trade chiuso, 63 validate, 46
  monete su 179 (26%), gate «in corso».

### Settimana 9 — 3–9 agosto (12 su 76): audit, deriva, e il paper riparte (e perde)

* **4 agosto**: **rilevatore di deriva** (`860d5853`): il paper «falsifica, non ottimizza»; frena size e
  leva quando la coppia non mantiene la promessa e le impedisce di accumulare conferme. **Recenza**
  nella scelta dei parametri (emivita 180 giorni) (`912b9b92`). **Audit completo** di 102 file
  (`c274fe2a`, `docs/audit.md`): il **controllo delle correlazioni aveva zero import** — documentato,
  mai collegato («il bot può aprire 5 posizioni perfettamente correlate») — e l'**agente macro** era un
  segnaposto che restituiva sempre una lista vuota. Blocchi A–D (`ef73ba0b`, `a8593736`, `278c8cfa`):
  correlazioni collegate, tetto del 3% al rischio nella stessa direzione, agente macro rimosso, conferma
  dei riempimenti in live, break-even scelto per coppia dal gate, PF minimo 0,8 in ogni regime,
  mattoncini di «condizione» (volatilità, forza del trend, volume, fascia oraria).
* **6 agosto**: calibrazione della confidenza e confronto con BTC (`45168a31`); **bias di
  sopravvivenza misurato al 3,4%** (28 monete delistate su 829 attive nella finestra) e giudicato
  marginale (`88de99d3`).
* **6–7 agosto**: la soglia del «gate superato» passa dal **60% al 35%** delle monete: lo si vede nelle
  fotografie (stato `55f1a0a6` del 2 agosto dice «obiettivo ≥ 60%», stato `633d5a4a` del 7 agosto 04:33
  dice «≥ 35%»). Non ho trovato il commit né la decisione scritta: probabilmente è stata cambiata nel
  `.env` della VPS. Con il 39% di copertura il gate risulta superato e il bot riapre trade il 7 agosto
  (stato `f397bcff`).
* **8 agosto**: `gate_vs_paper` mostra **da dove viene il profitto**: con PF 1,514 e 50% di vinti «il
  vincitore medio deve valere 1,65R» mentre chi si ferma al primo gradino incassa ~0,36R: «il risultato
  del gate lo fa la coda, non la mediana» (`3c160e85`).
* **Stato a fine settimana** (stato `49d4f886`, 9 agosto 22:49): equity **$895,20**; **78 trade chiusi,
  22 vinti (28%), −116,72**; 211 validate, 82 monete su 186 (44%). Uscite: 56 stop prima di ogni TP
  (72%, −247,73), 15 scale-out (+63,82), 6 a scadenza (+45,63), 1 TP pieno (+21,57). Deriva globale:
  PF vissuto **0,529 contro 1,649** promesso.

### Settimana 10 — 10–16 agosto (50 su 172): la settimana più densa — upgrade «v3», supervisore, ops

* **10 agosto**: il freno della deriva globale **non frenava** (era solo un'etichetta) mentre 96 trade
  facevano PF 0,525 contro 1,648 promesso (`1ccea23d`). **Quattro criteri contro le strategie
  fortunate** (`7aa1ca06`) dall'analisi di `BIRBUSDT|gen_472f85b8`: (1) il PF deve restare ≥ 1 anche
  togliendo il 5% dei trade migliori («robustezza», `pf_ex_top`); (2) storia minima da 180 a **365
  giorni**; (3) passaggio onesto da 24 a **168 ore** di dati nuovi; (4) il PF scritto nel registro
  ricalcolato con la scala davvero eseguita («per 95 coppie su 184 il registro pubblicizzava un PF che
  nessuno eseguiva»). Registro ricostruito (stato `9e4cfb4f`: 1 validata). **Livello AI** (`61e8fba5`):
  ipotesi con un meccanismo dichiarato, filtro delle monete, analista — «mai decisioni di trade». Si
  scopre che **i test leggevano il `.env` di produzione e si collegavano al Firebase vero**: un test
  aveva trovato una posizione BEATUSDT reale aperta (`271cb485`).
* **11 agosto**: il paper viene **azzerato** fra le 07:37 e le 09:13 UTC (stati `1b73dbcb` e
  `75d76506`) dopo **144 trade**. Audit «Fase 0» (`d57fb377`, `docs/audit_fase0.md`) in risposta al
  «prompt di upgrade v3» del proprietario: 52 moduli, mappa delle dipendenze, inventari, 15 lacune.
  Conclusione: la disparità gate↔paper **non** viene da costi, uscite o indicatori (moduli condivisi),
  ma da «selezione su una statistica fragile». Script per accumulare le conferme rigiocando la storia
  con date di fine diverse (`3e8d299b`).
* **12 agosto**: Fasi 1–5 dell'upgrade in un giorno (17 commit): confronto trade-per-trade dal backup
  (`65eec4d2`) — **30 coppie su 31 non rigiocabili** perché le specifiche delle generate erano state
  cancellate con le coppie (`7124ba40`); il tetto del 10% per posizione **mordeva su ogni trade** e il
  rischio vero era ~0,4% invece dell'1%; la leva 3x era irraggiungibile per l'arrotondamento «alla pari»
  di Python (`e353e4ce`); **caduta di portafoglio** (il gate la misurava coppia per coppia) (`fbc6d6f2`);
  learning con 4 difese (filtro anomalie, minimo 50 trade, smussamento, blocco se i pesi cambiano più del
  40%) (`f222b7bf`); regime con confidenza (`0bd0bf17`); punteggio delle monete a 6 fattori (`052355f0`);
  interruttore d'emergenza a 3 livelli e costi scomposti (`bb2921be`); riconciliazione con l'exchange
  (`803674d5`); errori Binance per gravità (`71f128df`); **LLM in ombra** e veto disarmato (`4079ffb6`,
  `5e2a2346`); metriche di qualità del backtest e guardia automatica contro il «guardare il futuro»
  (`22ef3ebd`); due confronti di mercato (`cf6ede64`); prove di guasto: **Firebase muto spegneva il bot
  con le posizioni aperte** (`40673fa3`, `docs/fase5_report.md`). Test da 293 a **512**.
* **13 agosto**: calendario delle conferme (`efe16078`); `fast_gate`, le tre conferme in poche ore con
  date di fine distanziate (`9ad4379a`); **autopsia**: il gate dice perché boccia, e i quasi-passaggi
  diventano i semi delle mutazioni (`54a9347b`); cache delle candele estendibile — «il costo più grosso
  del GATE 1 era rete, non CPU» (`1c9f1b57`); **supervisore** (`88e3262c`, richiesta esplicita del
  proprietario: il sistema deve tarare da solo); timer del gate **da 8 a 3 ore**.
* **14 agosto**: il registro dei parametri sfora 1 MiB **dopo 4 ore di calcolo** e butta via tutto
  (`775e4d5c`); soglia del voto t da 2 a ~3,9 (`1c89201d`); **canale ops** (`5849d258`) e sei correzioni
  al canale lo stesso giorno (HOME mancante, HEAD staccato, rebase bloccato, identità git, credenziali,
  token oscurati) (`eec84360`…`2b7e0596`). **Un verdetto per finestra** (`583fbaec`): la regola «fuori
  dopo 2 bocciature di fila» contava a ogni giro (ogni 3 ore) mentre una conferma richiedeva una
  settimana, cioè **56 giri**: «il registro non poteva accumulare tre conferme per costruzione».
* **15 agosto**: il proprietario parte per alcuni giorni; audit prima dell'assenza (`44621f57`): git
  senza tempo massimo poteva spegnere il canale per sempre; **`fast_gate` disarmato di default** (sarebbe
  partito da solo il 18 agosto e avrebbe azzerato il registro); token negli URL non oscurati.
* **Stato a fine settimana** (stato `2c95943b`, 16 agosto): equity $1.000, nessun trade; 0 validate;
  autopsia delle generate: **32.760 valutazioni, 79 passate (0,24%)**; supervisore ha abbassato la
  soglia dei vinti da 0,45 a **0,3985** e dice «budget di falsi positivi SFORATO».

### Settimana 11 — 17–23 agosto (23 su 286): il backtest rivisto da capo, la 1h di bitcoin

* **17 agosto**: il supervisore non annullava la propria mossa pur dicendo che il budget era sforato
  (`629f7910`).
* **19 agosto**: il budget del supervisore era sbagliato di **56 volte** (contava le passate, non le
  finestre): 1,07 coppie fortunate attese al giorno col modello vecchio, **0,019** con quello giusto
  (`200c690b`). Il calendario annunciava una data leggendo il campo sbagliato (`bfe70b1e`), e lo stesso
  controllo trova una porta nella migrazione che dava una conferma senza dati nuovi. **Revisione intera
  del backtest** (`973525f5`, `docs/audit_backtesting.md`): la cache della candela oraria non aveva il
  simbolo nella chiave, così **la 1h di bitcoin veniva servita a quasi tutte le monete** — regime e
  doppia conferma calcolati sul grafico sbagliato «in ogni finestra e in ogni holdout», da quando si è
  passati ai 15 minuti (15 luglio). Altri sei difetti: «in utile in ogni finestra» poteva poggiare su una
  finestra sola (nuovo criterio `oos_windows` ≥ 2); la deriva purgava in 6 ore; la unit della VPS
  imponeva 180 giorni di storia mentre il codice ne voleva 365; le monete delistate venivano validate;
  confine dell'holdout; passo della cache. La scoperta delle generate aveva **una terza copia a mano**
  della regola delle conferme (`457ca821`). Nasce la scheda **Claude** della dashboard (scrivere al
  sistema da Vercel tramite la issue #1) e la scheda **Ricerca** (`457ca821`, `8d595498`). La suite era
  rossa solo sulla VPS per le variabili d'ambiente di produzione (`99edc740`).
* **20–21 agosto**: analisi degli **spike** (`bf073694`, `b672bdae`, `ops/results/0017-spike.md`): due
  mie conclusioni erano sbagliate; vedi sezione 6. Le coppie di monete uscite dall'universo restavano
  «congelate» nel registro e falsavano il calendario (`c025b3e5`); un campo, `last_seen_at`, aveva due
  significati diversi a seconda di chi lo scriveva (`1f2a3ccb`); un test che lancia davvero ogni voce
  della lista bianca (`cae0eb80`).
* **21–27 agosto: nessun commit di Claude.** Il sistema gira da solo: la cronologia (`git log
  --author=Claude`) salta dal 21 agosto 06:28 al 27 agosto 01:20; il commit `ed6d1b56` parla di «sei
  giorni di lavoro autonomo».
* **Stato a fine settimana** (stato `27e2f49d`, 23 agosto): equity $1.000, 0 validate; generate:
  **39.634 valutazioni, 37 passate (0,09%)**; supervisore fermo: le candidate più vicine «sono fermate
  da `GATE_MIN_PF_EX_TOP`, che è già al pavimento».

### Settimana 12 — 24–31 agosto (8 su 257): «andremo mai live?» e l'incidente del registro

* **27 agosto**: il calendario «mentiva per la terza volta» (`ed6d1b56`): metteva in cima coppie che non
  stavano più maturando. Il proprietario chiede **«Il sistema è buono? Andremo mai live?»** e nasce
  `docs/andremo_live.md` (`13959d06`) con criteri scritti **prima** di vedere il risultato (sezione 3.5).
* **31 agosto**: le coppie a una conferma crollano **da 137 a 2** (`4ee6c1aa`). Trovato
  (`fee6cb12`): il registro conteneva **3.041 coppie base e 0 generate**, oltre il tetto di 3.000; il
  tetto calcolava lo spazio per le generate come 3.000 − 3.041 = zero e le cancellava **a ogni giro**.
  Racconto completo in `docs/incidente_31ago.md` e in sezione 5.
* **Stato a fine settimana** (stato `c3b7fa32`, 31 agosto 23:51): dopo la correzione 1.889 base e 105
  generate, tutte con almeno una conferma; generate **48.334 valutazioni, 84 passate (0,17%)**; base
  1.136 valutazioni, 0 passate; 0 validate. Test: **717** (`b42ded60`).

---

## 3. Il gate: cos'è, come funziona, come è cambiato, cosa ha prodotto

### 3.1 Cos'è

Il GATE 1 è il **filtro che decide quali coppie (moneta, strategia) il bot può operare**. Prende delle
candidate, le simula sulla storia con lo stesso motore di costi e di uscite del bot, e scrive nel
registro (`strategy_registry/validated`, Firestore) quelle che superano i criteri. Il bot rilegge il
registro ogni ora (`ADAPT_RELOAD_SECONDS`, `6e9088d5`) e opera solo le coppie validate
(`REQUIRE_VALIDATED_PAIRS`, `a92cb0a7`), e solo quando il gate è «superato» (`REQUIRE_GATE1_READY`,
`359493ad`). Senza registro resta fermo (`b0c31c0e`).

Il codice vive in: `backtesting/engine.py` (simulazione e criteri, funzione `gate_verdict`),
`backtesting/optimizer.py` (walk-forward e holdout), `scripts/optimize.py` (strategie base),
`scripts/discover_strategies.py` (strategie generate), `scripts/supervisor.py` (taratura),
`scripts/gate_progress.py` e `scripts/gate_autopsy.py` (letture).

### 3.2 Come funzionava nella sua ultima forma (fino al fermo del 13 ottobre)

**Frequenza.** Un giro ogni 3 ore (`OnCalendar=*-*-* 00/3:00:00` in
`scripts/install_optimizer_timer.sh`, dal 13 agosto `88e3262c`), più il supervisore ogni ora. Due
passi per giro: `scripts.optimize` (base) e `scripts.discover_strategies` (generate).

**Universo.** Le prime 200 monete perpetue USDT di Binance per volume (`--top 200`), con almeno 365
giorni di storia (`OPTIMIZER_MIN_HISTORY_DAYS=365` nella unit, dal 19 agosto `973525f5`), escluse le
delistate (`973525f5`), più le monete che hanno coppie a metà validazione (dal 14 settembre,
`f0bcbbec`). Con 365 giorni l'universo è sceso da ~200 a 143 monete (`c025b3e5`).

**Dati.** Candele da 15 minuti (`ORCHESTRATOR_TIMEFRAME=15m`, dal 15 luglio) dal 1 gennaio 2022 a oggi;
Binance, poi Bybit, poi OKX; **mai dati sintetici** (`BACKTEST_ALLOW_SYNTHETIC=false`, dal 24 giugno);
cache su disco estendibile (`1c9f1b57`).

**Candidate.**
* strategie base: ognuna con la sua griglia di parametri, al massimo 12 combinazioni a caso per giro
  (`--max-combos 12`). Escluse dal giro dal 21 settembre (`OPTIMIZER_SKIP_BASE=true`, `1670bc71`);
* strategie generate: **100 nuove a caso per giro** (`--generate 100`), più le mutazioni dei
  quasi-passaggi del giro prima (`54a9347b`), più fino a **500** specifiche già note da rivalutare
  (`--reeval-cap 500`, `a5038973`); le ipotesi dell'AI sono spente di default
  (`AI_HYPOTHESES_ENABLED=false`, `bot/config.py` riga 100).

**Prova.** Walk-forward a 3 finestre (`--windows 3`) e un holdout finale di 45 giorni
(`GATE_HOLDOUT_DAYS=45`) mai usato per scegliere. Costi: commissioni, spread per fascia di liquidità
misurato (`bot/core/costs.py`), funding reale col segno. Uscite: le stesse funzioni del bot
(`bot/execution/exit_logic.py`): scala di TP scelta per coppia, break-even sì/no scelto per coppia,
profit-lock, chiusura d'ufficio dopo 96 barre (24 ore).

**Criteri** (tutti valutati, non a corto circuito; `gate_verdict` in `backtesting/engine.py` riga 377;
soglie in `bot/config.py`):

| Criterio | Soglia | Da quando |
|---|---|---|
| numero di trade fuori campione | ≥ 30 | 20 dal 23 giu (`80e3e731`), 30 dal 31 lug (`81be83a1`) |
| profit factor | ≥ 1,25 | 1,10 dall'11 giu (`fdb4473d`), 1,25 dal 23 giu |
| percentuale di vinti | ≥ 0,45 (il supervisore l'ha portata a **0,3966**, stato di oggi) | 23 giu |
| ritorno totale fuori campione | ≥ 15% | 23 giu |
| in utile in ogni finestra con trade | 100% | 23 giu |
| finestre con trade | ≥ 2 su 3 | 19 ago (`973525f5`) |
| ritorno / caduta massima | ≥ 2,0 | 31 lug (`28029e80`) |
| PF senza il 5% dei trade migliori | ≥ 1,0 | 10 ago (`7aa1ca06`) |
| PF in ogni regime con almeno 10 trade | ≥ 0,8 | 4 ago (`278c8cfa`) |
| holdout: trade, PF, guadagno, PF senza i migliori | ≥ 5, ≥ 1,05, > 0, ≥ 1,0 | 31 lug, 10 ago |

**Conferme.** Una coppia guadagna al massimo **una conferma per finestra di 7 giorni**
(`judge_window`, `583fbaec`, 14 agosto; i 168h sono in `OPTIMIZER_NEW_DATA_MIN_HOURS` nel `.env` di
produzione — il default nel codice è 24, `bot/config.py` riga 417). Una finestra intera senza passare è
un fallimento; **due finestre fallite** e la coppia esce. Tre conferme = validata. Una coppia che il paper
smentisce (deriva) non può chiudere la finestra con una conferma.

**«Gate superato».** Copertura delle monete ≥ soglia (60% fino al 7 agosto 00:15 UTC, 35% dalle 04:33: stati `ec3589ca`
e `633d5a4a`) **oppure** almeno 10 coppie validate su almeno 5 monete diverse
(`OPTIMIZER_READY_MIN_PAIRS`, `4079ffb6`: spenta di default, impostata a 10 sulla macchina solo il 16
settembre, `c20013f6`, `cb125967` e `docs/andremo_live.md` «16 settembre, 16:00»; le 5 monete sono il minimo
assoluto che vale per tutte e due le vie).

**Supervisore** (dal 13 agosto, `88e3262c`, `docs/fase5_report.md` appendice): può allentare una soglia
alla volta solo se le «coppie fortunate attese al giorno» restano sotto 1; non può toccare holdout,
robustezza, dati sintetici, parità, `DRY_RUN`; non può abbassare le conferme. Oggi ha modificato solo
la soglia dei vinti (0,396614, stato di oggi `docs/state.md`).

### 3.3 Come è cambiato nel tempo

| Data | Cambiamento | Perché | Commit |
|---|---|---|---|
| 10 giu | Gate = «almeno una strategia in utile» su un paniere | prima versione | `a0e0860e` |
| 11 giu | Walk-forward per moneta: PF OOS ≥ 1,10, guadagno > 0, ≥ 10 trade | non giudicare sui dati usati per scegliere | `fdb4473d` |
| 12 giu | 0,08% di costi per trade | passato = netto | `55c09a27` |
| 13 giu | Registro cumulativo, 3 passaggi, «superato» al 60% delle monete | consolidare prima del paper | `1661bc2e`, `6b9acb9a` |
| 13 giu | Giri su GitHub ogni 6 ore | niente VPS necessaria | `03904791` |
| 14 giu | Funding nei costi; storia minima; scadenza dopo 3 giorni | memecoin nuove promosse | `530f2c20`, `d7d4000c` |
| 17 giu | Strategie generate | più idee | `515fcec0` |
| 18 giu | 4 anni di storia dal 2022 | includere il crollo del 2022 | `71d62680` |
| 19 giu | Tetto di 3.000 coppie | limite di Firestore | `436d1958` |
| 23 giu | PF ≥ 1,25, vinti ≥ 45%, ≥ 20 trade, ritorno ≥ 15%, ogni finestra in utile | «profittevole, e di tanto» | `80e3e731` |
| 24 giu | Passaggi 1 per accelerare; poi niente dati sintetici; gate sulla VPS ogni notte | validava su dati finti | `8af08741`, `073ab5f8`, `e464b505` |
| 25 giu | Passaggi di nuovo 3 | filtrare le fortunate | `f72ebb92` |
| 27 giu | Ogni 8 ore; 2 anni di storia | ritmo, niente monete appena quotate | `c1834fae`, `8dfc370b` |
| 29 giu | 400 monete | richiesta del proprietario | `7617e562` |
| 11–13 lug | Costo per liquidità; spread misurati; fuori dopo 2 bocciature | monete sottili; auto-pulizia | `fe794aa0`, `8b45914b`, `bcd56431` |
| 15 lug | Timeframe 15 minuti; storia in giorni (180) | stop più stretti | `c8337045`, `67e71c98` |
| 26 lug | Scale-out 1,5/3/5 come standard | A/B 4 metriche su 4 | `2dddd4b1`, `0043602d` |
| 30 lug | Scala di TP per coppia | ogni coppia «tende» in modo diverso | `f3f253a4` |
| **31 lug** | **Holdout 45 giorni; passaggio con 24h di dati nuovi; minimo 30 trade; ritorno/caduta ≥ 2** | l'OOS riusato era diventato training | `81be83a1`, `28029e80` |
| 4 ago | PF per regime ≥ 0,8; break-even per coppia; recenza; deriva dal paper | coppie che vivono di un solo regime | `278c8cfa`, `912b9b92`, `860d5853` |
| 6–7 ago | «Superato» dal 60% al 35% (fuori dal repo) | non documentato | stati `55f1a0a6`, `633d5a4a` |
| **10 ago** | **Robustezza senza il 5% migliore; storia 365 giorni; 168h di dati nuovi; PF con la scala vera** | BIRBUSDT: PF 1,51 nel gate, 0,16 nel paper | `7aa1ca06` |
| 12 ago | «Superato» anche con un numero minimo di coppie (via spenta di default, accesa a 10 il 16 set) | con il gate severo il 35% era irraggiungibile | `4079ffb6`, `c20013f6`, `cb125967` |
| 13 ago | Autopsia, semi dalle quasi-passate, supervisore, ogni 3 ore | ciclo senza memoria diagnostica | `54a9347b`, `88e3262c` |
| 14 ago | Un verdetto per finestra | due orologi incompatibili | `583fbaec` |
| 19 ago | Almeno 2 finestre con trade; 365 giorni anche nella unit; delistate escluse; una sola contabilità delle conferme | revisione intera | `973525f5`, `457ca821` |
| 31 ago | Le base morte escono; il tetto non cancella più chi ha conferme | incidente del registro | `fee6cb12` |
| 13–14 set | Il taglio della rivalutazione non scarta chi ha conferme; le monete con coppie avviate restano nell'universo | coorte ORCAUSDT | `a01b05cb`, `f0bcbbec` |
| 21 set | Strategie base fuori dal giro | non passavano mai | `1670bc71` |
| 26 set – 1 ott | Varie (giudizio delle validate sulla loro configurazione, voto t, gruppo di controllo) | — | `579109fa`, `50ed6462`, `af120806` |
| **13 ott** | **Ricerca automatica del gate FERMA** | «rumore, non informazione» | `4c315e80`, `ops/gate_fermo` |

### 3.4 Cosa ha prodotto: i numeri

**Giugno–luglio, gate «non onesto».** Coppie validate e copertura dalle fotografie:

| Data | Validate | Copertura | Fonte |
|---|---|---|---|
| 14 giu | 48 | 22/34 (65%) | stato `e0c60acc` |
| 21 giu mattina | 432 | 49/50 (98%) | stato `cb48b5dc` |
| 22 giu | 56 | 48/80 (60%) | stato `38509e38` |
| 5 lug | 738 | 167/167 (100%) | stato `1e68796e` |
| 11 lug | 872 | 176/176 (100%) | stato `a939fed1` |
| 30 lug | 753 | 168/181 (93%) | stato `9d196e58` |

Questi numeri non valgono come prova: fino al 24 giugno parte del registro poteva venire da dati
sintetici (`073ab5f8`); fino al 31 luglio le finestre fuori campione erano le stesse a ogni giro e tre
giri bastavano a «validare» (`81be83a1`); dal 15 luglio al 19 agosto a 15 minuti il regime di quasi
tutte le monete era calcolato sulla 1h di bitcoin (`973525f5`).

**Agosto, gate dopo la riforma.**

| Data | Coppie nel registro | Con 1 conferma | Validate | Fonte |
|---|---|---|---|---|
| 2 ago | — | — | 63 (26% copertura) | stato `bab841e7` |
| 9 ago | — | — | 211 (44%) | stato `49d4f886` |
| 14 ago | 1.504 | 8 | 0 | `ops/results/0001-gate.md` |
| 17 ago | 2.315 | 132 | 0 | `ops/results/0005-gate-conferme.md` |
| 19 ago | 2.615 | 224 | 0 | `ops/results/0007-gate-19ago.md` |
| 21 ago | 2.807 (2.246 vive) | 200 (46 con la finestra aperta) | 0 | `ops/results/0016-finestre-aperte.md` |
| 27 ago | 2.992 (1.720 vive) | 137 (42 con la finestra aperta) | 0 | `ops/results/0021-gate-27ago.md`, `0022-gate-vere.md` |
| 31 ago | 3.041, tutte base | 2 | 0 | `fee6cb12`, `4ee6c1aa` |
| 1 set | 1.974 | 111 | 0 | `ops/results/0027-registro-dopo-due-run.md` |

Le 63 e 211 validate del 2 e 9 agosto avevano ancora il passaggio onesto a 24 ore (tre conferme in tre
giorni); dal 10 agosto, con 168 ore, «zero coppie validate, mai, da quando il registro esiste nella
forma attuale» fino al 13 settembre (`docs/andremo_live.md`).

**Quanto passava per giro** (autopsia nelle fotografie):

| Data | Generate: valutate → passate | Base: valutate → passate | Fonte |
|---|---|---|---|
| 13 ago (prima autopsia) | 21.948 → 8 (0,036%), totale | — | `docs/fase5_report.md` appendice |
| 16 ago | 32.760 → 79 (0,24%) | 1.456 → 0 | stato `2c95943b` |
| 23 ago | 39.634 → 37 (0,09%) | 1.192 → 0 | stato `27e2f49d` |
| 27 ago | 41.038 combinazioni in tutto → 52 (0,127%) | 1.136 → 0 | `docs/andremo_live.md` |
| 31 ago | 48.334 → 84 (0,17%) | 1.136 → 0 | stato `c3b7fa32` |
| 13 ott (ultimo) | 34.048 → 113 (0,33%) | 1.320 → 0 (21 set) | `docs/state.md` di oggi |

Il motivo di bocciatura più frequente è sempre stato il **ritorno troppo basso**: 73,2% il 16 agosto,
71,1% il 31 agosto, 78,0% il 13 ottobre (stesse fonti). «Sono profittevoli, ma di troppo poco»
(`docs/andremo_live.md`). Ma la prima autopsia diceva anche che quasi tutte le candidate fallivano quasi
tutti i criteri insieme (PF senza i migliori 98%, PF 96%, vinti 94%, ritorno/caduta 88%, ogni finestra
88%) (`docs/fase5_report.md`, «Correzione dopo la prima autopsia reale»).

**Quante passerebbero per caso.** Con 41.038 prove per giro e 52 passate, le coppie fortunate attese
sarebbero 7,4 al giorno con 1 conferma, 0,26 con 2, **0,0094 con 3** («una ogni 106 giorni»)
(`docs/andremo_live.md`). Il voto t necessario con ~21.000 prove è **3,92**; il migliore osservato era
**2,65** (`1c89201d`).

**Settembre–ottobre (riassunto; dettaglio in un'altra parte).**
* 13 settembre: ancora 0 validate (243 coppie a 1 conferma, 90 a 2) (`ops/results/0035-verdetto-13set.md`,
  tabella in `docs/andremo_live.md`).
* 14 settembre: le **prime 7 validate, tutte su ORCAUSDT** (`ops/results/0054-fine-giro-0626.md`,
  `422e0a50`); il 15 settembre 11 su 4 monete (`eee22962`); il 16 settembre 31 su 16 monete
  (`c20013f6`) e il paper riparte con 35 validate (stato `531155ca`).
* Oggi: 2.435 coppie generate nel registro, 2.100 con almeno una conferma, **249 validate** su 80
  monete (registro aggiornato al 13 ottobre); il supervisore ne conta 278 (`docs/state.md` del 18
  ottobre).

**Come sono andate poi, nel paper e nel motore.**
* Paper dal 16 settembre a oggi: **704 trade chiusi, 391 vinti (56%), −172,92 USDT**, equity **$827,08**;
  deriva globale **PF vissuto 0,705 contro 2,02 promesso** su 661 trade; mediana di `mfe_r` 0,79R
  (`docs/state.md` del 18 ottobre).
* Lettura ufficiale del 7 ottobre: dopo la validazione il motore fa **−0,05R a trade su 230 segnali**
  (`ops` 0532, citato in `docs/capito.md`); lettura del 14 ottobre: **−0,03R su 566 segnali**, margine
  ±0,09R (`docs/capito.md`, 16 ottobre; `3d2d775a`).
* Il gate rigiocato nel passato: 6 promosse su 25.631 giudizi, i loro 45 trade fanno −0,22R contro
  −0,14R delle bocciate (`ops` 0502, `docs/capito.md`). Sul **prezzo rimescolato** (dove nessun vantaggio
  è possibile) il gate a 1 ora ha promosso **16 strategie su 7.200, contro 8 su 7.200 sui prezzi veri**
  (`ops` 0506, voce G7 in `docs/backlog.md`).
* 13 ottobre, motivo del fermo: «il giro ogni 3 ore faceva 27.000 prove, ne passava lo 0,29% e le
  passate facevano −0,06 R a trade in paper (ops 0601 e 0604): rumore, non informazione»
  (`ops/gate_fermo`).

### 3.5 I punti di decisione scritti prima dei numeri

* **27 agosto** (`docs/andremo_live.md`, `13959d06`): «entro il 5 settembre almeno qualche coppia a 2
  conferme → il meccanismo funziona; zero → […] la mossa non è allentare il gate, è cambiare cosa si
  cerca». Esito (stessa fonte, tabella del 13 settembre): 8 coppie a 2 conferme il 6 settembre, quindi
  «funziona» per quel criterio.
* **6 settembre**: «Segnale 1 — il 13 settembre, se nessuna arriva a tre conferme». Esito del 13: zero
  (la coorte ORCA non ripassa), poi il 14 le prime 7 (dopo una correzione all'universo).
* «Segnale 2 — se validano ma il paper perde: il problema non è cosa cerchiamo ma come misuriamo»
  (`docs/andremo_live.md`). Con i numeri di oggi (PF 0,705 contro 2,02) il segnale 2 è quello che si è
  verificato.

---

## 4. Le altre parti del bot: cosa fanno oggi e come ci si è arrivati

### 4.1 Strategie

* **Oggi**: il bot opera solo strategie **generate** validate (tutte le righe della tabella delle
  validate in `docs/state.md` sono `gen_…`). Sono combinazioni di al massimo 3 mattoncini presi da una
  libreria (`bot/strategies/generated.py`, `FEATURE_LIBRARY`), con soglie fissate alla nascita.
* **Come ci si è arrivati**: 8 strategie base il 10 giugno (`76e6723f`: trend following, mean reversion,
  breakout, funding arbitrage, VWAP reversion, momentum cross-asset, liquidity grab, grid); parametri
  ottimizzabili l'11 giugno (`fdb4473d`); generate dal 17 giugno (`515fcec0`) con più mattoncini lo
  stesso giorno (`71b1efaf`); Momentum il 10 luglio (`32b071b3`); mattoncini di «condizione» il 4 agosto
  (`278c8cfa`); ipotesi con meccanismo dichiarato proposte dall'AI il 10 agosto (`61e8fba5`).
* **Cosa si è capito**: il generatore «combina feature col dado. Nessuna candidata ha una ragione per
  funzionare» (`docs/audit_fase0.md` §1.3 e §4, «CRITICO 1»). Le base: 0 passaggi su 1.136 al 27 agosto
  (`docs/andremo_live.md`), ma il 13 agosto si era calcolato che «zero su 1.488 non è un segnale, è il
  campione piccolo» e che le base producevano quasi-passaggi 2,5 volte più delle generate (`e86ecb69`).
  Il 21 agosto, sui parametri di default, `vwap_reversion` perdeva su BTC, ETH e SOL (−192%, −439%,
  −821%) mentre momentum e trend following guadagnavano (`b672bdae`, `ops/results/0017-spike.md`).
  Quasi ogni generata funziona su **una moneta sola** (`docs/andremo_live.md`, 6 settembre: 78 spec
  distinte su 95 coppie, una sola su 5 monete).

### 4.2 Orchestratore (chi decide il trade)

* **Oggi**: in parità il bot apre **ogni** segnale valido di ogni coppia validata, uno per moneta, con una
  funzione deterministica (`decide_all` in `bot/orchestrator/orchestrator.py`). L'LLM non decide
  niente; l'ombra (`AI_SHADOW_ENABLED`) e il veto (`AI_VETO_ENABLED`) sono spenti di default
  (`bot/config.py` righe 123 e 130).
* **Come ci si è arrivati**: Claude a ogni candela da 15 minuti con un ripiego deterministico senza
  chiave (`c7da8429`) → in parità «niente LLM/selezione globale» (`f7a12b13`, 30 giugno) → «il bot non
  consumava token perché l'LLM non era mai raggiunto» (`61e8fba5`) → ombra e veto disarmato il 12 agosto
  (`4079ffb6`, `5e2a2346`). Il motivo è scritto: una scelta dell'LLM «non è riproducibile, quindi non
  sarebbe mai backtestabile» e romperebbe la parità (`docs/fase5_report.md`, Parte 3 punto 5).
* La confidenza delle generate è sempre 60 (`docs/state.md` di oggi: «tutte le strategie generate escono
  a confidenza 60»), quindi qualunque modulazione per confidenza non può misurare niente. Il 9 agosto la
  calibrazione era «flat», correlazione 0,0 su 78 trade (stato `49d4f886`); il documento Fase 0 dell'11
  agosto riporta invece «ok, correlazione 0.125 su 133 trade» (`docs/audit_fase0.md` §1.6): due letture
  in momenti diversi, la seconda probabilmente su trade con confidenze non tutte uguali.

### 4.3 Rischio e dimensione delle posizioni

* **Limiti fissi** (dal primo giorno, `bot/risk/hard_limits.py`): leva massima 5x, rischio massimo 3% a
  trade; default dell'utente leva 2x e rischio 1% (`246c515e`).
* **Interruttori**: perdita giornaliera −5% sul **capitale** (era sul margine fino al 17 giugno,
  `700591c1`); pausa globale dopo 6 stop (era 3, `bc16b710`); panchina della strategia dopo 3 stop;
  pausa sulla moneta dopo uno stop. **In parità questi freni sono spenti** (`f1805b45`).
* **Size**: margine massimo per posizione 10% dell'equity in parità (`a42f0954`); allocazione guidata
  da convinzione e pesi (`83fb29bd`); il 12 agosto si scopre che il tetto del 10% «morde sempre»: col
  conto da 1.000 e leva 2 il nozionale era ~200 e il rischio vero ~0,4% invece dell'1% (`e353e4ce`); la
  leva 3x era irraggiungibile per l'arrotondamento (stessa fonte).
* **Portafoglio**: controllo delle correlazioni (0,85, massimo 3 posizioni) **scollegato fino al 4
  agosto** (`ef73ba0b`); tetto del 3% al rischio nella stessa direzione dal 4 agosto; caduta di
  portafoglio misurata dal 12 agosto (`fbc6d6f2`). Oggi la caduta di portafoglio è 177,44 USDT con fino a
  15 posizioni insieme (`docs/state.md`).
* **Freno della deriva**: oggi «size x0,5 e leva x0,71 su ogni trade» (`docs/state.md`): le due
  posizioni aperte oggi hanno leva 1,0x e rischio 0,09% e 0,23%.
* **Interruttore d'emergenza** a 3 livelli dal 12 agosto (`bb2921be`); dopo 5 minuti di Firebase muto
  niente nuove aperture (`40673fa3`).
* **Macro**: nessuna protezione sugli eventi macro (FOMC, CPI): l'agente era un segnaposto ed è stato
  tolto (`ef73ba0b`, `docs/data_sources.md`).

### 4.4 Uscite e trailing

* **Oggi**: scala di TP a 3 gradini scelta per coppia dal gate (nella tabella delle validate di
  `docs/state.md` si vedono scale da 0,75/1,25/1,75 a 2/4/6), break-even dopo il primo gradino,
  profit-lock con una quota da tenere per coppia (0,35–0,75), chiusura d'ufficio dopo 96 barre.
  Dal 21 settembre il profit-lock si arma rispetto al **primo** gradino (`432e7f48`).
* **Come ci si è arrivati**: trailing a +1 ATR e uscita del 50% (`b11e8666`) → tolti per parità (20
  giugno, `f56d641e`) → profit-lock condiviso (23 giugno, `80e3e731`) → verdetto controfattuale sul
  trailing (5 e 13 luglio) → scale-out su R come standard (26 luglio) → ombre, flusso dei prezzi e
  percorso riprodotto (30 luglio) → scala per coppia (30 luglio) → break-even per coppia (4 agosto).
  Il codice che adatta il profit-lock dai verdetti del paper (voce interna B2, `83fb29bd`) è ancora in
  `bot/main.py` righe 2394–2401; se e quanto incida oggi non l'ho verificato.
* **Cosa dicono i numeri**: oggi su 704 trade il 44% esce allo stop prima di ogni TP (−586,72) e l'89%
  non raggiunge nemmeno il primo gradino; mediana `mfe_r` 0,79R (`docs/state.md`). Il 9 agosto la
  mediana era 0,64R e il 74% non arrivava al primo gradino (stato `49d4f886`). Il 31 luglio: «61% delle
  uscite è stop_loss, mfe mediana 1,10R con TP1 a 1,5R raggiunto solo dal 25%» (`81be83a1`).

### 4.5 Learning e AI

* **Pesi strategia×regime**: dal win rate (≤ 35% → peso 0, ≥ 60% → 1) (`docs/learning.md`); di notte
  su GitHub (`c7da8429`) → restringimento graduale (13 luglio) → ogni ora nel bot (15 luglio) → a ogni
  trade chiuso (26 luglio) → filtro anomalie, minimo 50 trade, smussamento 0,3, blocco oltre il 40% di
  variazione (12 agosto, `f222b7bf`). Le chiusure manuali e d'emergenza escluse (`f3e601a3`, `89a79499`).
* **Deriva** (4 agosto) e **calibrazione** (6 agosto): il paper giudica, non addestra. Principio scritto:
  «tararci sopra i parametri lo consumerebbe come training set» (`860d5853`).
* **AI** (`bot/ai/`, 10–12 agosto): ipotesi, filtro delle monete, analista, ombra. Tutto «fail-open»: senza
  chiave il comportamento è identico. Oggi ipotesi, filtro e ombra sono spenti di default (`bot/config.py`
  righe 100, 113, 123); filtro e ombra sono stati spenti di default il 30 settembre (`3d8f20a2`), per le
  ipotesi non ho verificato la data.
* **Dopo agosto** (solo per completezza): un «selettore» (meta-labeling) disegnato il 24 settembre
  (`docs/disegno_cervello.md`), in ombra dal 25 settembre; su 96 trade il suo voto «non distingue (0,653
  vinti contro 0,644 persi) e non batte "apri tutto"» (`docs/backlog_archivio.md`, voce F1ter, ops 0340 e
  0348).

### 4.6 Esecuzione

* **Oggi**: `DRY_RUN=true` (`docs/state.md`). In paper l'ingresso è a **ordine limite virtuale** dal 13
  ottobre (`6d50adfa`, `PAPER_INGRESSO_LIMITE`, `bot/config.py` riga 260). Le uscite si valutano sul
  percorso dei prezzi (flusso del libro, prezzo medio bid/ask) con ripiego sulle candele da 1 minuto.
* **Come ci si è arrivati**: stesso codice paper/live dal primo giorno (`b11e8666`) → ripristino dopo i
  riavvii (15 giugno) → log dei trade che funziona (16 giugno) → registro di scrittura anticipata dei
  trade chiusi (15 luglio) → ombre e percorso (30 luglio) → per il live: conferma del riempimento (4
  agosto), ordini di protezione per gradino (30 luglio), riconciliazione (12 agosto), errori per gravità
  (12 agosto).
* **Ancora aperto per i soldi veri** al 4 agosto: i riempimenti delle **uscite** in live sono «dedotti
  dal prezzo, non letti» (`docs/audit.md` §7), e i costi non si possono calibrare dal vissuto in paper.

### 4.7 Dashboard

* Next.js su Vercel, login Google (10 giugno), regole Firebase ristrette all'UID del proprietario (24
  giugno, `f89db16e`); schede (5 luglio); restyling (25–26 luglio); 7 pannelli nuovi (12 agosto);
  schede **Claude** e **Ricerca** (19 agosto). La scheda Claude è stata tolta il 21 settembre perché il
  proprietario non la usava (`CLAUDE.md`). Oggi la prima scheda è il «Controllo» orario
  (`docs/architecture.md`, tabella dei moduli; commit `425d8086` del 25 settembre).

### 4.8 VPS e job

* **VPS Hetzner**: la guida consiglia una CX22 (2 vCPU, 4 GB) per il bot (`docs/hetzner_setup.md` riga
  14); a metà agosto la macchina aveva 16 GB (commit `304c307f`: «Con 8 worker su 16 GB»); il modello
  esatto della macchina di oggi non è scritto nei file che ho letto. Installazione in
  `/root/agentic_trading_system` (`cd57c4f0`).
* **Servizi**: il bot (`trading-bot.service`), il gate (`trading-optimizer.timer`: ogni notte dal 24
  giugno, ogni 8 ore dal 27 giugno, ogni 3 ore dal 13 agosto), il supervisore (ogni ora dal 13 agosto),
  l'agente ops (dal 14 agosto).
* **GitHub Actions**: monitoraggio ogni 15 minuti, ma «misurato che il cron */15 produce ~10 esecuzioni al
  giorno invece di 96» (`docs/audit_fase0.md` §3.3); fotografia dello stato; learning notturno; test. I
  giri del gate su GitHub sono stati spenti il 24 giugno (geo-blocco) e i workflow rimossi il 21
  settembre (`docs/optimization.md`).

### 4.9 Ops

* Nato il 14 agosto (`5849d258`) perché Claude non può entrare sulla VPS: si committa una richiesta, la
  macchina la esegue contro una **lista bianca che vive solo sulla macchina** e ricommitta la risposta.
  Niente shell, argomenti ristretti, oscuramento dei segreti. Il primo giorno ha avuto sei difetti che lo
  rendevano muto (sezione 5). Battito orario in `ops/heartbeat.md` dal 15 agosto (`3beb3539`).
* Le azioni distruttive (`fast_gate`, `reset_paper`) non sono mai state in lista bianca «perché non si
  annullano da lontano» (`a94323bb`). Al 31 agosto i risultati erano 26 (`ops/results/0026-…`), oggi 622
  (`ls ops/results | wc -l`, dopo `3c7fbdb8` del 18 ottobre).

---

## 5. Incidenti, bug e difetti (giugno–agosto)

In ordine di data. «Effetto» è quello misurato o scritto nella fonte.

| Data | Difetto | Effetto | Correzione |
|---|---|---|---|
| 10 giu | Variabile `ANTHROPIC_MODEL` vuota invece che assente | chiamate Anthropic in errore 400 | `7e59747c` |
| 15 giu | Al riavvio le posizioni non venivano ricaricate | posizioni riaperte e mai chiuse né registrate | `44561c40` |
| 16 giu | `set(None)` su Firebase RTDB solleva | **nessun trade chiuso registrato**, posizioni fantasma | `cd6edb42` |
| 16 giu | Equity del paper mai aggiornata | restava 10.000; size che non componeva | `744a7ff9`, `426a3be6` |
| 16 giu | PnL del paper lordo | paper ottimista rispetto al gate | `2cdc8a07` |
| 17 giu | Perdita giornaliera calcolata sul margine | bot fermo dopo 2–3 stop pur essendo +65 | `700591c1` |
| 17 giu | Scanner sui primi 60 simboli in ordine d'API; decisione su 5 monete | monete liquide saltate | `dc2ec91a`, `2ae9e542` |
| 17 giu | VWAP cumulativo | PF 99–262, +57.000% fuori campione su `vwap_reversion` | `7ef6aa74` |
| 17 giu | Generate mai rivalutate; documento oltre 1 MiB | ferme a 1 passaggio; scrittura fallita | `cc90bc2f`, `fd0553b9` |
| 19 giu | Registro oltre il limite d'indice di Firestore (883 coppie) | registro non aggiornato | `436d1958` |
| 20 giu | Bot con trailing e uscita al 50%, backtest a stop/target pieni | vincenti tagliati, perdenti pieni | `f56d641e` |
| 22 giu | Generate validate scadute dopo 3 giorni | validate da 432 a 56 | `ff607d55` |
| 22 giu | Senza registro il bot operava tutto | trading non validato | `a92cb0a7` |
| **24 giu** | **Dati sintetici sui server di GitHub** (stesso seme per ogni moneta) | registro di validate finte, «+500% finti» | `073ab5f8`, `b6e72a34` |
| 25 giu | Servizio ucciso dopo 90 s (causa dubbia, `44621f57`); crash del riepilogo | gate non finiva; scoperta mai partita | `ffd40694`, `a9dfb500` |
| 27 giu | PF senza perdite, finestre senza trade, parametri non validati | strategie buone bocciate, altre promosse a torto | `47f5d37e` |
| 2 lug | Stop/target del bot coi valori fissi | rapporto rischio/rendimento diverso dal validato | `3b43f17d` |
| **9 lug** | **Gate a 1 ora, bot a 15 minuti** | «il paper non poteva replicare il GATE 1» | `90d4c783` |
| 10 lug | Dati fermi al 1 gennaio 2026 | mesi recenti esclusi | `3536dfe5` |
| 13 lug | Spread stimati 2–3 volte troppo alti | coppie bocciate a torto | `8b45914b` |
| 15 lug | 15 difetti (1h come alias, 96 ore invece di 96 barre, candele in formazione, prezzi vecchi nell'emergenza…) | vedi settimana 6 | `67e71c98` |
| 15 lug | Ordini SL/TP orfani dopo una chiusura in live | potenziale chiusura di una posizione futura | `81d4ef0b` |
| 21 lug | Crash all'ultima scrittura su Firestore; lettura non decodificata | registro sempre vuoto dal 15 luglio; 0 coppie operate | `886c5a3f`, `e2378080` |
| 22 lug | Il bot ignorava il «gate superato» | trade con copertura all'1% | `359493ad` |
| 23 lug | Fotografia dello stato in errore ogni 2 ore | `docs/state.md` fermo da 24 ore | `06df15a4` |
| 30 lug | Filtro di rumore dello 0,02% sul percorso | TP mai raggiunti incassati: paper ottimista | `96f8d893` |
| **31 lug** | **Finestre fuori campione identiche a ogni giro** | «l'OOS era diventato un training set»; −99 su 74 trade contro +80 attesi | `81be83a1` |
| 31 lug | Ricostruzione del registro col bot acceso | posizioni aperte col registro vecchio | `107d1961` |
| 1 ago | Passaggio onesto non chiuso nel dubbio; campi persi; scala sovrascritta | «validata su 3 giorni» in un giorno | `15d0a03c` |
| **4 ago** | **Controllo delle correlazioni mai collegato; agente macro finto** | protezioni credute attive e inesistenti | `ef73ba0b` |
| 4 ago | In live l'ingresso a limite era dato per eseguito | posizioni inesistenti gestite | `a8593736` |
| 10 ago | Freno della deriva globale mai applicato | 96 trade a size piena con PF 0,525 contro 1,648 | `1ccea23d` |
| 10 ago | PF del registro calcolato con la scala sbagliata | 95 coppie su 184 con un PF non eseguito | `7aa1ca06` |
| **10 ago** | **Test che leggevano il `.env` di produzione** | collegati al Firebase vero (trovata una posizione reale aperta) | `271cb485` |
| 12 ago | Specifiche delle generate cancellate con le coppie | 30 coppie su 31 e 138 trade su 144 non rigiocabili | `7124ba40`, `docs/fase5_report.md` |
| 12 ago | Tetto del 10% sempre attivo; leva 3x irraggiungibile | rischio ~0,4% invece dell'1% | `e353e4ce` |
| 12 ago | Firebase muto ⇒ eccezione nel blocco finale del ciclo | bot spento con le posizioni aperte | `40673fa3` |
| 12 ago | Scan senza tempo massimo | ore senza sorvegliare le posizioni con Binance lenta | `40673fa3` |
| 13 ago | Il supervisore sceglieva la soglia sbagliata | allentamento che non avrebbe convertito nessuna candidata | `3b73ee45` |
| 13 ago | `git pull` bloccato da `docs/state.md` modificato sulla VPS | timer installati da uno script vecchio | `90ca74b5` |
| 14 ago | Documento dei parametri oltre 1 MiB | **4 ore di calcolo buttate**, autopsia persa | `775e4d5c` |
| 14 ago | Canale ops muto (HOME, HEAD staccato, rebase, identità git, credenziali, token) | nessuna risposta dalla VPS | `eec84360`, `cd38c935`, `83ae17b8`, `b6069277`, `986c48b0`, `2b7e0596` |
| **14 ago** | **Due orologi: fuori dopo 2 giri falliti, conferma dopo 7 giorni** | registro incapace di arrivare a 3 conferme | `583fbaec` |
| 15 ago | `fast_gate` armato in automatico | avrebbe azzerato il registro il 18 agosto | `44621f57` |
| 17 ago | Il supervisore non annullava la propria mossa | soglia allentata lasciata in vigore | `629f7910` |
| 19 ago | Budget del supervisore sbagliato di 56 volte | «allarme fabbricato» per giorni | `200c690b` |
| **19 ago** | **1h di bitcoin servita a quasi tutte le monete** | regime e doppia conferma sbagliati in ogni finestra e holdout dal 15 luglio (la chiave senza simbolo c'è già in `backtesting/engine.py` riga 237 al commit `67e71c98`) | `973525f5` |
| 19 ago | Tre copie della regola delle conferme | generate e base contate con criteri diversi | `457ca821` |
| 21 ago | Coppie congelate di monete uscite; campo con due significati | calendario su coppie morte | `c025b3e5`, `1f2a3ccb` |
| 21 ago | Script degli spike con soglia che copriva il 100% delle barre | «tautologia con l'aria di un risultato» | `1be71c42` |
| **31 ago** | **Registro pieno di coppie base morte** | generate cancellate a ogni giro; 137 prime conferme perse | `fee6cb12`, `docs/incidente_31ago.md` |

Sull'incidente del 31 agosto il documento corregge un'esagerazione: il danno è di «2-3 giorni, non di due
settimane» più la perdita delle 137 prime conferme, «circa dieci giorni di accumulo»
(`docs/incidente_31ago.md`; `b42ded60`).

---

## 6. I numeri del paper e dei backtest nel periodo

### 6.1 Il paper: cinque tentativi, tutti azzerati

Ricostruiti dalle fotografie dello stato. Le date di inizio e fine sono mie letture della serie (stima,
±qualche ora).

| Periodo | Condizioni | Equity | Trade | Fonte |
|---|---|---|---|---|
| 16–23 giu | 1h; registro in parte da dati GitHub (forse sintetici); bot con trailing fino al 20 giu | $10.000 → **$9.501,59** (−5,0%) | non registrato nello stato | stati `34beca98`, `406efebb` |
| 29 giu – 15 lug | 1h nel gate, **15 minuti nel bot fino al 9 luglio**; stop/target sbagliati fino al 2 luglio; registro con OOS riusato | $10.000 → **$10.875,74** (+8,8%) | non registrato nello stato | stati `23962ac2`, `4b69eb6e` |
| 23–26 lug | 15 minuti; registro «validato» in 3 giorni con tre passate sugli stessi dati; 1h di BTC per tutte | $10.874,12 → **$10.051,45** (−7,6%) | non registrato | stati `4f76812b`, `bcd0d258` |
| 28–31 lug | conto da $1.000; scale-out | $1.000 → **$911,02** (−8,9%) | **70 trade, 27 vinti (39%), −95,11**; il commit della riforma dice −99 su 74 | stato `6c206437`, `81be83a1` |
| 7–11 ago | gate dopo la riforma ma passaggio a 24h; «superato» al 35% | $1.000 → **$788,41** (−21,2%) | **144 trade, 48 vinti (33%), −225,59** | stato `1b73dbcb` |

Due fonti non concordano sull'ultimo tentativo: `docs/andremo_live.md` scrive «equity da $1.000 a $831
in cinque giorni», il commit `fbc6d6f2` «un −17% in cinque giorni», mentre l'ultima fotografia prima
dell'azzeramento dice $788,41 con 144 trade (e $785,51 con 142 trade la notte prima, stato `86e8f3fb`).
Le riporto tutte; non so a quale momento si riferisca $831. Anche la data dell'azzeramento: il documento
Fase 0 (scritto l'11 agosto) dice che i 144 trade sono stati cancellati «ieri», ma le fotografie mostrano
i trade ancora presenti l'11 agosto alle 07:37 UTC e l'equity a $1.000 alle 09:13 UTC.

**In tutto**, fra il 16 giugno e il 31 agosto il paper ha operato circa 33 giorni su 77 (stima dalle
fotografie); gli altri giorni era flat perché il registro era vuoto o in ricostruzione. Dall'11 agosto
al 16 settembre non ha operato affatto (stati `c3b7fa32`, `531155ca`).

**L'unico tentativo in utile (29 giugno–15 luglio) non è interpretabile**: in quei giorni il bot girava
su un timeframe diverso da quello validato e il registro veniva dalla «lotteria» poi smontata il 31
luglio. Lo segnalo perché è un numero positivo che potrebbe essere letto come prova, e non lo è.

**Il confronto con la promessa**, quando è stato misurato:
* 31 luglio: −99 su 74 trade contro +80 attesi, «gap ~2,4 sigma» (`81be83a1`);
* 9 agosto: PF 0,529 contro 1,649 su 78 trade (stato `49d4f886`);
* 10 agosto: PF 0,525 contro 1,648 su 96 trade (`1ccea23d`);
* 11 agosto: PF 0,46 contro ~1,5 su 142 trade; trade a ≥ 3R il 7% contro il 16% atteso, a ≥ 5R l'1% contro
  il 7% (`docs/audit_fase0.md` §4 e §5.1);
* `BIRBUSDT|gen_472f85b8`: PF 1,51 nel gate, 0,16 nel paper; sull'holdout 94 trade, +29,5%, ma 7 trade
  facevano tutto il profitto e gli altri 87 perdevano il 22,6% (PF 1,51/0,16: `docs/audit_backtesting.md` §4; holdout: `docs/audit_fase0.md` §5.1, `7aa1ca06`).

### 6.2 Misure fatte sui backtest (diagnosi, non validazioni)

| Data | Misura | Risultato | Fonte |
|---|---|---|---|
| 13 lug | Profit-lock: prematuro contro protetto | 48% contro 36%: taglia più vincitori di quanti ne salvi | `0898ce2c` |
| 13 lug | Spread reali per fascia | 0,010 / 0,021 / 0,039 / 0,068% | `8b45914b` |
| 26 lug | TP unico contro scala 1,5/3/5 | la scala vince 4 metriche su 4, 2 semi, fino a 377 coppie | `2dddd4b1` |
| 30 lug | Costo del percorso senza filtro | ~1,8 µs a punto, ~40 ms a tick con 12 posizioni (0,13% del tick) | `96f8d893` |
| 30 lug | Combinazioni ripetute nella griglia | 67–75% di cloni quando `rr` non ha effetto | `f3f253a4` |
| 6 ago | Bias di sopravvivenza | 28 delistate su 829 = 3,4% | `88de99d3` |
| 12 ago | Semaforo di qualità (run di prova da riga di comando) | 1.047 trade, Sharpe −1,13, caduta 53%: ROSSO | `22ef3ebd` |
| 12 ago | BTC contro paniere delle monete tradate (run di prova) | BTC −34,9%, paniere +14,5% | `cf6ede64` |
| 12 ago | Backfill dopo il reset | 9 coppie a 1 passaggio su 1.200 (0,75%); anche tutte validate sarebbero 6,7% di copertura contro il 35% | `4079ffb6`, `docs/fase5_report.md` |
| 13 ago | Supervisore sui numeri veri | 22.264 valutazioni, 8 passate: ~0,02 fortunate attese, margine 7x | `88e3262c` |
| 14 ago | Voto t | soglia 3,92 per ~21.000 prove; migliore osservato 2,65 | `1c89201d` |
| 14 ago | Tasso di passaggio con conferme settimanali | 0,027%: servivano ~28 passaggi in 7 giorni per sopravvivere | `583fbaec` |
| 17 ago | Supervisore dopo l'allentamento | soglia vinti 0,3985, tasso 0,244%, 1,64 attese al giorno | `629f7910` |
| 21 ago | Spike ≥ 10% in 24h dal 2022 | eventi: BTC 49, ETH 110; trade negli spike = 3% del profitto su BTC (5% delle barre), 4% su ETH (12%), 18% su SOL (27%); `vwap_reversion` −192% / −439% / −821% | `b672bdae`, `ops/results/0017-spike.md` |
| 21 ago | Regime del gate contro regime del bot negli spike | discordano 0% su BTC, 23% su ETH, 46% su SOL | `b672bdae` |

---

## 7. Cosa abbiamo imparato in questo periodo, ed errori da non ripetere

### 7.1 Cosa abbiamo capito

1. **La differenza fra gate e paper è venuta prima da errori nostri, poi dalla selezione.** Fino al 19
   agosto quasi ogni divergenza aveva una causa meccanica: uscite diverse (20 giugno), stop/target diversi
   (2 luglio), timeframe diverso (9 luglio), «1h» finta (15 luglio), filtro del percorso (30 luglio), 1h di
   bitcoin per tutti (19 agosto). Dopo averle chiuse, la causa rimasta è statistica: «selezione su una
   statistica fragile» (`docs/audit_fase0.md` §0 punto b, dettaglio in §5.1).
2. **Scegliere fra migliaia di candidate trova la fortuna.** Con ~1.464 candidate per giro e una soglia a
   t=2,8, «~4 strategie prive di edge superano […] per puro caso a ogni passata» (`docs/audit_fase0.md`
   §4); con 21.000 prove la soglia giusta è 3,92 e il meglio osservato era 2,65 (`1c89201d`).
3. **Il profitto promesso viene dalla coda.** Con scale-out a 5R, il PF del gate esiste «solo perché ~15%
   dei trade arriva a 5R» (`docs/fase5_report.md` Parte 4 punto 2); nel paper a 5R arriva l'1% (`docs/audit_fase0.md`).
4. **Il prezzo non arriva al primo gradino.** Mediana `mfe_r` 1,10R (31 luglio), 0,64R (9 agosto), 0,79R
   (oggi) contro primi gradini per lo più da 1,5–2R (oggi da 0,75 a 2R, `docs/state.md`): è il dato più stabile di tutto il periodo.
5. **Le strategie generate vivono su una moneta sola**, e una moneta che esce dall'universo per volume
   ricorda il caso BIRBUSDT (`docs/andremo_live.md`, 6 e 14 settembre).
6. **Il gate onesto passa pochissimo e quasi tutto muore sul ritorno troppo basso** (71–78% delle
   bocciature, sezione 3.4).
7. **I numeri giusti erano tutti veri e insieme ingannavano**: «80 candidate passate», «3.041 coppie nel
   registro» erano veri mentre il registro cancellava tutto (`docs/incidente_31ago.md`).

### 7.2 Errori da non ripetere

1. **Mai un ripiego silenzioso su dati finti.** I dati sintetici hanno prodotto un registro intero di
   validate false (24 giugno). Se mancano i dati veri, la moneta si salta e lo si dice.
2. **Il fuori campione si usa una volta.** Finestre uguali a ogni giro e migliaia di candidate hanno
   trasformato l'OOS in training (31 luglio). Lo stesso vale per il paper: non va usato per tarare.
3. **Una conferma deve vedere dati nuovi.** «3 passaggi» ha significato tre cose diverse: tre giri sugli
   stessi dati (giugno–luglio), tre giorni (31 luglio), tre settimane (10 agosto). Scrivere sempre
   *cosa* conta come evidenza, non solo *quanta* ne serve.
4. **Le regole devono usare lo stesso orologio.** Purga per giro contro conferma per settimana (14
   agosto), budget per passata contro conferma per finestra (19 agosto): due volte lo stesso difetto.
5. **I tetti messi per tempo e spazio non devono poter cancellare l'evidenza.** Il tetto del registro (31
   agosto), il taglio della rivalutazione (13 settembre), la scadenza delle generate (22 giugno): tre
   volte un limite tecnico ha buttato via (il 13 settembre: poteva buttare via, ma non aveva ancora tolto
   niente, `docs/andremo_live.md` «Il 13 settembre») proprio ciò che il sistema produceva. Un'evidenza accumulata
   non si cancella per far spazio.
6. **Un totale non dice di cosa è fatto.** Confrontare sempre ciò che la ricerca produce con ciò che il
   registro conserva, e guardarne la composizione (31 agosto).
7. **Codice morto documentato come protezione è peggio di nessuna protezione** (controllo delle
   correlazioni, agente macro, 4 agosto; quarta difesa del 31 agosto).
8. **Una sola implementazione di ogni regola.** Le tre copie della contabilità delle conferme (19 agosto)
   e i «due significati» di un campo (21 agosto) hanno prodotto numeri sbagliati per settimane.
9. **Prima di azzerare, esportare tutto.** Il reset dell'11 agosto ha reso non rigiocabili 30 coppie su 31
   (`7124ba40`). Ogni reset ha anche ricominciato il paper da zero: in tre mesi nessun campione del paper
   ha superato i 144 trade.
10. **Non cambiare le regole mentre si misura.** Il gate è stato riformato o il registro azzerato almeno
    il 17 giugno, 23 giugno, 24 giugno, 15 luglio, 26 luglio, 31 luglio e 10 agosto (commit citati
    sopra); ogni volta il confronto gate↔paper ripartiva.
11. **Non annunciare date e conclusioni da stime.** Il calendario delle conferme ha mentito tre volte
    (19, 21, 27 agosto); due conclusioni sugli spike erano sbagliate (21 agosto); la gravità
    dell'incidente del 31 agosto è stata prima esagerata. Le correzioni pubbliche nel diario sono la
    regola, non l'eccezione.
12. **I test verdi non bastano.** 716 test verdi non provavano il registro pieno (31 agosto); i test
    leggevano la produzione (10 agosto); la suite era rossa solo sulla VPS (19 agosto). Servono test sui
    casi limite reali e sull'ambiente reale.
13. **Un processo automatico non deve poter finire in uno stato da cui non esce** (agente ops, 14–15
    agosto), né fare da solo azioni irreversibili quando nessuno guarda (`fast_gate`, 15 agosto).
14. **GitHub Actions non è un posto per i calcoli del gate né un orologio affidabile** (geo-blocco di
    Binance; ~10 esecuzioni al giorno invece di 96).
15. **Prima si misura, poi si collega**: confidenza, regime, punteggio delle monete, LLM sono stati
    registrati prima di poter toccare la size (`docs/fase5_report.md` Parte 2). Le volte in cui si è
    fatto il contrario (allocazione «guidata dai dati» del 25 luglio su una confidenza sempre uguale a 60)
    il numero si è rivelato senza significato.

---

## Cose incerte o non verificate in questa bozza

* **Chi e quando ha portato la soglia del «gate superato» dal 60% al 35%** (fra il 6 e il 7 agosto): lo
  vedo nelle fotografie ma non in un commit o in un documento; probabilmente nel `.env` della VPS.
* **L'equity finale del paper di agosto**: $831 (`docs/andremo_live.md`), −17% (`fbc6d6f2`) o $788,41
  (stato `1b73dbcb`).
* **La data del reset dell'11 agosto**: «ieri» nel documento Fase 0 contro le fotografie del mattino
  dell'11.
* **Quanti trade ha fatto il paper fino al 30 luglio**: la sezione «trade chiusi» dello stato esiste solo
  dal 30 luglio (`148d3d55`), quindi per i primi tre tentativi conosco solo l'equity.
* **Il calo da 872 a 431 validate dell'11–12 luglio**: lo collego alla rivalidazione coi costi nuovi, ma è
  una mia deduzione.
* **Il valore di `OPTIMIZER_NEW_DATA_MIN_HOURS` in produzione** (168) lo deduco dai messaggi del gate
  («un pass ogni 168h di dati nuovi» in `ops/results/0001-gate.md`); il `.env` non è nel repo.
* **Se il profit-lock adattato dal paper (B2) incida ancora oggi** sulle coppie validate: il codice c'è, la
  verifica no.
* **La dimensione attuale della VPS**: so solo dei 16 GB di metà agosto.
* I numeri di settembre–ottobre (sezione 3.4 e alcuni in 4) li ho presi dai riassunti in `docs/capito.md`,
  `docs/state.md` e `ops/gate_fermo`, senza aprire i singoli risultati ops 0485–0619.
