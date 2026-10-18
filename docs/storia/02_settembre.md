# 02 — Settembre 2026: il mese del paper, del gate e delle misure

> Capitolo della storia del progetto: il riepilogo è in [`README.md`](README.md). Scritto il 18 ottobre 2026 da un lettore in sola lettura sul repository, poi ricontrollato da un secondo lettore che ha aperto le fonti e corretto nel testo gli errori trovati (105 affermazioni, 93 giuste, 12 corrette). Dove il testo dice «bozza» o «questo pezzo», intende questo capitolo.

Bozza scritta il 18 ottobre 2026 in sola lettura sul repo (branch `claude/brave-albattani-1b12fv`).
Copre dal 1 al 30 settembre 2026, con il dettaglio dal 14 settembre in poi; in fondo al capitolo 1
c'è un paragrafo sulla mattina del 1 ottobre, perché lì sta il riassunto di cosa si sapeva a fine mese.

## Come leggere questa bozza

* **Fonti.** «diario r. N» = `docs/andremo_live.md`, riga N. «ops NNNN» = il file
  `ops/results/NNNN-*.md` (la risposta della macchina a una richiesta). Un codice di 8 caratteri
  (per esempio `432e7f48`) è un commit. «revisione 30 set» = `docs/revisione_sospese_30set.md`.
  «controllo unico» = `docs/controllo_unico_14set.md`. «disegno» = `docs/disegno_cervello.md`.
* **Ore.** In UTC, salvo dove è scritto «ora italiana» (a settembre l'ora italiana è UTC+2). Il diario
  mescola le due cose senza dirlo sempre: dove l'ho notato lo segnalo.
* **«stima»** = un numero mio, ricavato da altri numeri (per esempio una somma). Tutto il resto viene
  da un file o da un commit.
* **Le sigle del backlog** (A1, J11, K3...) compaiono perché stanno nei file; ognuna ha accanto cosa fa.

### Le parole usate (in breve)

* **Gate**: il filtro che decide quali strategie il bot può operare. Prova ogni strategia su una
  moneta (una «coppia», per esempio `ORCAUSDT|gen_6d06dca0`) sulla storia dal 2022, con un test fuori
  campione a blocchi (walk-forward) e un esame finale sugli ultimi 45 giorni (holdout).
* **Conferma / finestra**: una coppia che passa il gate prende una conferma; la conferma successiva
  vale solo su almeno 7 giorni di dati nuovi (una «finestra»). **Validata** = 3 conferme in 3 finestre.
* **Registro**: il documento Firestore `strategy_registry/validated` con tutte le coppie seguite.
* **Discovery / optimize**: i due programmi del gate. La discovery genera e prova le strategie
  automatiche (`gen_*`); optimize prova le 8 strategie scritte a mano e calcola `ready`.
* **Giro completo / giro urgenti**: un giro del gate che rivaluta tutte le strategie note, oppure solo
  quelle che possono cambiare stato a breve (introdotto il 23 set, commit `7b77b23b`).
* **Paper**: il bot che opera con soldi finti (`DRY_RUN=true`) partendo da 1.000 USDT.
* **R**: il risultato di un trade in multipli del rischio iniziale (−1R = stop pieno). **mfe** = il
  massimo guadagno toccato durante il trade, in R.
* **Scala dei TP / scale-out**: i tre incassi parziali (per esempio 2/4/6 R). **Lock / keep**: la
  protezione del profitto (quando si arma e quanta parte del massimo guadagno blocca).
* **Freno globale (deriva)**: se il PF vissuto dal paper è molto sotto quello promesso dal gate, size e
  leva vengono dimezzate.
* **Declassata**: una validata che non ripassa il gate in due giri completi di fila; opera a un quarto
  della size (dal 26 set). **Esplorativa**: una coppia quasi passata, operata in paper a un quarto della
  size (dal 25 set).
* **Intorno**: le soglie di una validata spostate di un gradino, per cercare una «figlia» migliore.
  **Varianti dai referti**: varianti di una strategia nate dalle perdite del paper.
* **Selettore**: un modello che dovrebbe dire «prendi / non prendere» un segnale (mai acceso).

### Da dove partiva settembre (in tre righe)

A fine agosto il registro non aveva **nessuna** coppia validata (diario r. 38). Il 19 agosto una
revisione del motore di backtest aveva trovato che quasi tutte le monete erano giudicate col grafico
orario di bitcoin, e che quindi le misure precedenti erano «contaminate» (`docs/audit_backtesting.md`,
punto 1; diario r. 42-45). La regola in vigore era «tre conferme distanziate di una settimana»: con una
sola conferma, stimava il diario, entrerebbero 52 coppie fortunate a settimana; con tre, una ogni 106
giorni (diario r. 15-19). Il paper, prima del reset di agosto, aveva perso (equity da 1.000 a 831 in
cinque giorni, diario r. 36-37); da allora il bot restava fermo finché il registro non dichiarava
`ready` (`REQUIRE_GATE1_READY=true`, diario r. 400-401). Il caso da non ripetere, citato tutto il mese, era BIRBUSDT:
profit factor (PF) 1,51 promesso dal gate, 0,16 realizzato dal paper (diario r. 89).

---

## 1. Cronologia

### 1-13 settembre: l'attesa della terza conferma

* Il gate gira ogni 3 ore. Le coppie a 2 conferme crescono: 8 il 6 set (ops 0030), 58 l'8 set
  (ops 0031), 81 su 32 monete l'11 set (ops 0032, 0033), 84 su 35 il 12 set (ops 0034), 90 su 37 il 13 set
  (ops 0035). Validate: 0 in tutti questi giorni (stesse fonti).
* **6 settembre.** Domanda del proprietario: quando cercare cose diverse? Il diario fissa tre segnali
  (diario r. 94-146): (1) se il 13 set nessuna coppia arriva a tre conferme; (2) se le validate perdono
  nel paper («il fallimento più informativo»: vorrebbe dire che il gate misura male); (3) se la ricerca
  converge su poche idee. Misurato il terzo: 78 strategie diverse su 95 coppie, su 48 monete, ma quasi
  ogni strategia funziona su una moneta sola (solo `gen_9a383fff` su cinque) (diario r. 119-126).
  Raccomandazione: aspettare il 13.
* **11 settembre.** Il report del gate impara a contare le **monete** e non solo le coppie (commit
  `5ccd46dd`): otto strategie su ORCAUSDT sono otto coppie ma una sola moneta. Il diario ricorda che
  quel giorno era stata dedotta per errore una concentrazione da un elenco troncato (diario r. 223-224).
* **13 settembre.** Zero validate. Le otto coppie ORCAUSDT a 2/3 sono state riprovate con la finestra
  scaduta e non hanno ripassato (ops 0035, 0040; diario r. 150-182). Trovato un difetto: il taglio della
  rivalutazione (al massimo 500 strategie note per giro) teneva le **più vecchie**, non quelle con
  conferme. Non aveva ancora tolto niente (329 strategie note contro un tetto di 500, ops 0040). Corretto:
  prima le conferme, e chi ha un passaggio non si taglia mai (commit `a01b05cb`, 6 test in
  `tests/test_reeval_priority.py`).

### 14 settembre: le monete che escono dall'universo, la potatura che cancellava, le prime 7 validate

* Mattina presto, 0 validate (ops 0041, 0042): 277 coppie a 1 conferma su 89 monete, 104 a 2 su 40.
  Cinque coppie con la finestra scaduta (AXS, EGLD, tre su STX) riprovate: nessuna ripassa (diario r.
  245-253).
* **Trovato:** ORCAUSDT era uscita dall'universo (le 200 monete più scambiate, che ruota: circa un
  quarto cambia in sei giorni; dell'universo dell'8 set restava dentro il 74%, diario r. 260-270). Una
  coppia la cui moneta esce non viene più valutata: non prende né conferma né bocciatura, resta ferma.
  **Correzione** (commit `f0bcbbec`): le monete con una coppia avviata rientrano nell'universo, fino a 40,
  in ordine di vicinanza al traguardo (7 test in `tests/test_universe_rotation.py`, suite 730 verdi).
* **Il «controllo unico»** (commit `e29232d0`, `docs/controllo_unico_14set.md`), nato da una frase del
  proprietario («ogni volta trovi un problema diverso e la mia pazienza ha un limite»). Conclusione: non
  erano problemi diversi ma lo stesso, cinque volte: «da qualche parte un limite scarta in silenzio
  proprio quello che stiamo aspettando». Il più grave: **la potatura cancellava le coppie a 1-2 conferme
  non viste da sei giorni** — perdita attiva, quante ne fossero già sparite «non è ricostruibile»; quel
  giorno 23 erano nella finestra di rischio. Le otto di ORCA sarebbero sparite il 19 set. Scritta una
  regola fissa («una coppia con almeno una conferma recente non viene cancellata da nessuna potatura...»)
  e un test che la verifica su ogni percorso (`tests/test_confirmations_are_never_lost.py`). Suite 739
  verdi (commit `e29232d0`).
* **08:08 UTC: prime 7 validate, tutte ORCAUSDT** (ops 0054: «3 pass: 7 su 1 coin»). Erano proprio le
  coppie salvate dalla correzione della mattina (diario r. 317-332). Il diario avverte: sette strategie
  sulla stessa moneta, lo stesso giorno, sugli stessi dati, sono «un evento solo»; e la moneta era uscita
  dalle 200 più scambiate, come BIRBUSDT (diario r. 336-343).
* La ricerca guidata (le mutazioni) dà la precedenza alle monete non ancora coperte (commit `81a87f3d`,
  suite 745).

### 15 settembre: 11 validate su 4 monete, e la sonda sui timeframe

* 11 validate su 4 monete: ORCA 8, STX 1, HEI 1, EGLD 1 (ops 0055; diario r. 362-376). Il diario scrive
  «manca una moneta sola» perché il paper parta (diario r. 389-392): **era sbagliato** (vedi 16 set).
* **Sonda sui timeframe** (domanda del proprietario: certe monete si coprono a 1 ora o a 5 minuti?).
  20 candidate su 3 scale, 6 monete scoperte e 3 di controllo (ops 0060; diario r. 412-482). PF mediano:
  1 ora 0,910 (scoperte) / 0,949 (controllo); 15 minuti 0,826 / 0,876; 5 minuti 0,694 / 0,779. Sopra il
  pareggio: 29-37% a 1 ora, 8% a 15 minuti, 2-3% a 5 minuti. Lettura: il timeframe per moneta non serve;
  ma **più lunga la scala, meglio vanno le strategie, su tutte le monete**, e la spiegazione più semplice
  sono i costi. Decisione: non toccare niente (cambiare timeframe invaliderebbe il registro; la sonda
  misura il PF, non il gate; 9 monete e 20 candidate).

### 16 settembre: la soglia sbagliata, la scelta del proprietario, il paper parte

* Mattina: 31 validate su 16 monete, `ready: False` (ops 0061). Correzione del diario (r. 496-519): la
  regola vera non era «10 coppie su 5 monete» (quella via, `READY_MIN_PAIRS`, era spenta di default) ma
  **il 35% dell'universo coperto** (circa 76 monete su 217; ne avevamo 16, il 7,4%). Raccomandazione
  scritta: **aspettare**, perché abbassare l'asticella proprio quando diventa raggiungibile «è la
  definizione di spostare il traguardo» (diario r. 535-539).
* **Il proprietario aggiunge `OPTIMIZER_READY_MIN_PAIRS=10` al `.env` della macchina** (scritto nella
  richiesta `ops/requests/0063-ricalcola-ready.req`, commit `588c2181` delle 07:02). Il diario non lo dice
  in modo esplicito: parla di «via a conteggio impostata a 10» (r. 566).
* Per due ore il registro mostra 31 validate, via a conteggio a 10 e `ready: False`. Causa: `ready` lo
  calcola optimize, e la discovery riscrive i contatori dopo senza ricalcolarlo. Ora `ready` registra su
  quali numeri è stato deciso (commit `bb9a88a8`, `96196d43`; suite 757).
* **15:44 UTC: `ready: True` «via numero coppie», su 35 validate / 19 monete / universo 156** (ops
  0071). Il bot valuta 16 monete invece di 100; prima posizione SPXUSDT long, rischio 0,39%, leva 2x
  (diario r. 548-561; commit `cb125967`).
* **Regola di lettura fissata prima dei numeri:** nessuna conclusione sul gate prima di **40 trade
  chiusi** (diario r. 584-588).

### 17-18 settembre: i primi trade, e due domande del proprietario

* **17 set**: 3 trade chiusi, 1 vinto, −2,34 USDT, equity 997,66; lordo −1,38, costi 0,97 stimati dal
  modello del gate; BTC +1,17% nello stesso periodo (ops 0073, 0074; diario r. 598-640). Ritmo misurato
  1,5 trade al giorno, quindi 40 trade in circa quattro settimane (diario r. 617).
* **17 set, sera — due richieste esplicite del proprietario** (commit `78813a2f`, `4f7ede65`): (1) «le
  coppie che iniziano il processo di validazione lo devono portare al termine, non importa se il volume
  scende»: il tetto sulla riaggiunta delle monete è spento; (2) «se superano il terzo passaggio, anche se
  il volume non è nei nostri standard, il paper li deve operare»: le validate non vengono più scartate per
  volume o spread nel bot.
* **18 set** (diario r. 649-740). Domanda 1: «l'ho visto in positivo per quasi 10 ore e alla fine siamo
  andati in stop loss». Il trade VETUSDT `gen_6d06dca0` short, −3,24. Causa: la protezione del profitto si
  armava a metà strada dall'**ultimo** gradino della scala (3R su 2/4/6). Sui primi 7 trade: mfe mediana
  0,52R, nessuno oltre 3R, 6 stop pieni su 7 (−17,47); PF vissuto 0,221 contro 1,884 atteso
  (`docs/state.md` del 18 set, citato al diario r. 674-686). Il gate faceva la stessa cosa
  (`backtesting/engine.py:712`, `bot/execution/executor.py:435`), quindi non era una divergenza.
  Domanda 2: «in una giornata di rialzo 4 posizioni su 5 short». Tre cause volute: il regime si calcola
  sulla moneta e non su BTC; le strategie generate sono attive in tutti i regimi; il trend modula la size
  ma non vieta. E metà dei mattoncini sono di ritorno alla media, che per costruzione «vendono la forza».
  Cambiata solo la strumentazione (blocco DIREZIONE in `scripts/trade_stats.py`, commit `b081298e`,
  774 test). Non cambiata l'uscita: «se ne riparla col verdetto dei 40 trade» (diario r. 732-740).

### 19 settembre: il registro vicino al muro, la sonda sbagliata, l'AI spenta da sei giorni

* **Registro**: un solo documento Firestore, limite 1 MiB; 759 KiB su 879 (86%), +37 KiB al giorno,
  circa tre giorni al muro (diario r. 742-752). La difesa che c'era (`slim_registry`) scattava solo oltre
  la soglia e non era mai stata eseguita; la discovery riscriveva il registro grezzo dopo optimize.
  Corretto (commit `ecb99ab5`): formato compatto, alleggerimento sempre, rete sulla scrittura. Misurato
  dopo: 272 KiB (31%), 108 byte a coppia, **47 validate prima e dopo** (diario r. 798-807). 787 test.
  Non fatto: dividere il registro su più documenti.
* **«Come è possibile +12.821 $ nel backtest e −4 nel paper?»** (`gen_4465723e`, diario r. 829-851). Il
  backtest punta tutto il capitale su ogni trade (`backtesting/engine.py:788`), il paper 200 $ su 1.000:
  gli stessi 215 trade nel paper darebbero circa +25%. Con 12 trade e 2 vinti, la probabilità di un
  risultato così brutto se il sistema funzionasse era 3,6%.
* **La sonda `frequenza` misurava su candele da 1 ora** mentre il bot gira a 15 minuti: «22 attesi in 7
  giorni» e «tutto torna» erano falsi (commit `86d5625b`). Rifatta: 71 segnali grezzi, 49 apribili in 7
  giorni (circa 7 al giorno) contro 3-4,5 aperti (diario r. 870-874). Sera: giorno per giorno, dal 16 al
  18 set, attesi 10,3 e aperti 9 (87%), il 18 set 6 aperti contro 3 attesi: **nessun divario** (diario r.
  898-922; commit `b19cc196`).
* **Il livello AI non girava**: chiave API rifiutata (401) dal 13 set alle 06:12; l'ombra AI aveva zero
  decisioni (diario r. 935-951). Rimessa la chiave, nuovo errore (400: serve l'intestazione del
  workspace), corretto con `ANTHROPIC_WORKSPACE_ID` (commit `965a87ed`). Primo giro con l'AI: 19 proposte
  su 20 scartate (commit `893e7267`).
* **«Il paper propone, il gate dispone»** (commit `ed042b11`, richiesta del proprietario): l'AI riceve un
  riassunto dei fatti misurati dal paper; dal mfe del paper nasce una scala di TP che **si aggiunge** alle
  quattro fisse, e la sceglie il gate.

### 20 settembre: nasce il backlog

* `docs/backlog.md` nasce con 20 voci, ognuna col numero che l'ha fatta emergere e il motivo del rinvio
  (commit `f0ac205f`).
* Le proposte AI morivano su un parametro (`rr` sotto 1,5: 14 su 19), che il prompt non dichiarava e che
  sotto scale-out non ha nessun effetto (commit `46d5b124`, `32c50254`).
* Misurato lo storico dell'open interest: arriva al 2022 solo per 3 coppie su 25 (commit `6d7f125c`).

### 21 settembre: il giorno in cui abbiamo letto cosa fanno le strategie

* Il proprietario manda i grafici di MUBARAKUSDT (+37% in 30 ore, RSI 88) e USELESSUSDT in salita
  verticale: «siamo entrati short lì? siamo stupidi?». Numeri del giorno: short 13 trade, 2 vinti,
  −30,11; long 11 trade, 3 vinti, −15,59; USELESSUSDT `gen_2031005e` mfe mediana 0,20R contro un primo
  gradino a 2,00R (diario r. 988-1000; commit `ba32eaa8`).
* **Quattro cause, tutte nel codice da luglio** (commit `1d96dc3d`): (1) il rilevatore di regime chiamava
  «incertezza» ogni moneta con volatilità sopra il 2,5% prima di guardare la direzione, quindi il freno
  sul controtrend non frenava proprio sulle monete che correvano; (2) la quarantena di un'ora dopo uno
  stop c'era nel bot ma non nel gate (il gate rientrava alla candela dopo); (3) le «gemelle»: strategie
  identiche che differivano solo per un parametro inerte erano contate come diverse (USELESS 3 validate
  con PF 1,541 / 1,541 / 1,54); (4) il vocabolario non sapeva dire «questa non è un'oscillazione»:
  aggiunti `not_stretched` e `adx_below`.
* **La discovery non caricava nemmeno BTC**: per le strategie generate il mercato «non era nella stanza».
  Aggiunti tre mattoncini di mercato (`market_trend`, `market_fade`, `relative_strength`), non un divieto
  (commit `c7033755`).
* **Strumenti che sbagliavano** (stesso giorno): «0/21 ingressi combaciano» era un difetto del confronto
  (le date ISO valevano zero, commit `2ee8de44`); la sonda dello storico misurava 263 monete invece di 25
  (commit `cc080d1c`); la voce del backlog sul rischio era scritta al contrario: il rischio per trade
  **cresce** con la larghezza dello stop fino all'1% (commit `fad02496`).
* **Le «vite» delle strategie**: prima della rimozione di una coppia si scrive una riga durevole
  (`gate_history/lifecycle`), così non resta solo chi sopravvive (commit `9d3b69ae`).
* **Sera: gli stop divisi per come sono morti** (diario r. 1038-1054): su 27 trade chiusi, 21 stop; 7
  (33%) mai andati a favore, 13 (62%) andati a favore ma sotto il primo gradino (mfe mediana 0,69R), 1
  oltre il primo gradino. Nessuna scala da sola gira in positivo (la più corta, 1/1,5/2,5, −0,30R).
  **Decisione del proprietario, coi numeri sopra: la protezione si arma al primo gradino** (A1, commit
  `432e7f48`), nel gate e nel bot con la stessa funzione `lock_anchor`. Registro non azzerato. Il
  proprietario sceglie anche che la misura dei 40 trade «da qui in poi non è più confrontabile con i
  primi 24» («non buttiamo via nulla, andiamo avanti», diario r. 1033-1036).
* **Copertura ferma** a 26 monete su 165 (15,8% contro 35%; commit `1670bc71`): le 8 strategie scritte a
  mano (0 validate su 1.312 valutazioni) escono dal giro; i semi delle mutazioni da 10 a 30.
* Notte (commit `340fda18`, `f5645622`): il break-even dopo il primo gradino lo sceglie il gate per coppia
  (A2); `rr` non più controllato (B2bis); modello AI configurabile (D3); **tetto di perdita per moneta
  al giorno** (1,5% dell'equity, `bot/risk/daily_cap.py`); referto settimanale la domenica; i quasi
  passaggi vanno all'AI (B3); dati sintetici spenti per default (D2); via quattro workflow GitHub senza
  dati (E3). Dashboard: tema chiaro, tolta la tab Claude, corretto il grafico che mostrava sempre BTC
  (commit `74a10e8e`).

### 22 settembre: il giro sfora le 3 ore, la conferma a 1 ora, le strategie native a 1 ora

* La discovery gira oltre 2h53 contro circa 2 ore del giorno prima: causa più probabile (lo dice il
  commit), il contesto di mercato veniva calcolato a ogni candela anche per le circa 550 strategie che non lo usano. Corretto (commit
  `dead71b4`). Il tempo del giro ora si misura da solo (commit `8d0b6474`).
* Col salto delle strategie a mano, la copertura risultava «26/26 (100%)»: il denominatore era
  collassato (commit `a083fdf8`).
* **`htf_confirm`**, idea del proprietario: guardare la moneta a 15 minuti per operare e a 1 ora per
  confermare, come mattoncino che il gate misura (diario r. 1114-1122). Sui 35 trade del 22 set avrebbe
  tolto 11 trade, il cui netto era +5,87. Il giorno stesso il proprietario chiede anche l'opposto
  (`htf_fade`, lo short sul calo dentro un trend orario in salita, commit `4ab04729`).
* **Strategie native a 1 ora, solo su BTC** (C1, commit `e9989e7f`), allargate il 23 set a ETH, SOL, ADA,
  BCH (commit `ddf62dea`).

### 23 settembre: il controllo prima di aprire, il referto dopo, il «cervello»

* **Rivalutazione completa una volta al giorno** (commit `7b77b23b`): ogni giro durava 2h29 e il 77%
  del tempo rivalutava circa 430 strategie note, otto volte al giorno sugli stessi dati. Negli altri giri
  si rivalutano solo le coppie vicine alla chiusura della finestra (il giro «urgenti»). Il commit dice:
  le coppie al limite «avranno un tentativo al giorno invece di otto — meno biglietti, stesso esame».
* **MUBARAK long** dopo il +37%: stop a −15,3%, primo incasso a +31%; ore in positivo al 3-6% (0,3R),
  poi stop pieno −9,8 (diario r. 1139-1141). Da oggi (`bot/risk/setup_check.py`, commit `cf94be7d`):
  prima di aprire, uno stop più largo del 6% del prezzo rende il setup non operabile, nel gate e nel bot;
  dopo, ogni trade chiuso riceve un referto (classe della morte, lock mai armato, controtrend).
* **«Il sistema deve imparare da tutto quello che fa e adattarsi tutti i giorni»** (il proprietario,
  davanti a 40 trade chiusi, 6 giornate su 8 in perdita e −50,88, dalla dashboard; diario r. 1154-1156).
  Tre pezzi (commit `e26682a5`, suite 1058): referti aggregati con ipotesi da regole scritte prima (per
  esempio tre short tutte perse → «solo long»); ogni ipotesi diventa una variante della strategia nel gate;
  **freno di serie** (quattro perdite di fila su una strategia → size e leva a metà).
* L'obiettivo finale del proprietario entra in `CLAUDE.md` (commit `3368b238`).

### 24 settembre: il cervello prende forma, l'audit, quattro giri uccisi per memoria

* Le varianti dai referti si provano nello stesso giro con i dati fino a oggi, a 8 e a 16 giorni fa
  (commit `daf083bd`). Disegno del «cervello» (`docs/disegno_cervello.md`, commit `80c83ffc`): il
  selettore (passo 0 dataset, passo 1 confronto) e l'intorno (fino a 10 validate a notte). Commit
  `91da019e`, `b79ac764`.
* Tetto di rischio per direzione al 3%, statistica t nel registro, 40 candidate casuali per giro invece
  di 100, backtest di portafoglio (commit `033a1ee4`, `cbb89e57`).
* **Controllo delle 08:20 ora italiana** (ops 0175-0183; diario r. 1241-1270): il modello AI sulla
  macchina era `claude-opus-4.8`, un nome inesistente, dalle 23:12 del giorno prima (proposte, autopsia
  e filtro saltati in silenzio). 44 trade in 9 giorni, −49,15; PF vissuto 0,60 contro 1,89. 59 validate
  su 27 monete. Prima coppia a 1 ora passata: ADAUSDT.
* **Portafoglio** (ops 0184, 0188): le 59 validate insieme sugli ultimi 60 giorni, coi limiti del bot,
  fanno +10.386 su 10.000, ma «il PnL NON è una previsione»: le coppie sono state scelte su quel periodo.
  Il paper apre 4,9 trade al giorno contro 8,6 simulati (diario r. 1273-1290).
* **Audit del cervello** (domanda del proprietario: «hai fatto un check di tutto il codice appena
  creato?»; diario r. 1293-1319; commit `eb0b992d`). Quattro revisori su 4.400 righe di due giorni. Due
  errori ammessi: il tetto per direzione **esisteva già** (ne era stata scritta una seconda copia); il
  freno di serie scatta per caso al 30-44% delle strategie ogni mese e, sommato al freno globale, portava
  la size a un quarto: **spento**. Trovata anche la causa del giro «urgenti» da 1h54: le bocciature non
  chiudevano la finestra, e 223 strategie restavano «urgenti» per sempre.
* **Quattro giri del gate uccisi per memoria** (09, 12, 15 e 18 UTC; `scripts/discover_strategies.py`
  r. 1313-1318 e commit `29754c75`). Il diario ne racconta due e poi un terzo (r. 1334-1352). Cause: le
  righe del dataset del selettore tenute in memoria, poi le varianti valutate su dati troncati, che
  facevano ricostruire la cache del motore. Soluzione finale: **varianti troncate spente**
  (`DISCOVERY_VARIANTI_TRONCATE=false`), 6 worker invece di 8. Il diario: «colpa mia» (r. 1334).
* **Due misure** (diario r. 1355-1361): il livello del grafico come take profit (A5) sta in mediana a
  3,96R ed è raggiunto nel 2% dei trade, contro l'11% del primo gradino (ops 0210): ipotesi smentita. I
  segnali del gate aperti dal paper (15) hanno PF 0,50; quelli non aperti (9) PF 1,23 (ops 0211): indizio.
* Giro lanciato a mano alle 21:11 ora italiana (19:11 UTC) con 6 worker: 2h07, 70.560 valutazioni, 135 coppie passate; le coppie
  a 2 conferme salgono da 213 a 380 (diario r. 1365-1371).

### 25 settembre: le validate da 59 a 160, il controllo orario, il paper esplorativo

* **Validate da 59 a 160 su 52 monete** (ops 0224; diario r. 1380-1387). Causa: la correzione
  dell'audit. Una coppia che passa dentro la sua finestra ora prende la conferma alla chiusura della
  finestra; prima la prendeva solo se ripassava dopo la scadenza. Otto revisori su otto lo giudicano
  legittimo (diario r. 1405-1406). Effetto: il bot opera 160 coppie; attesi 19-24 segnali apribili al
  giorno (ops 0229).
* **Portafoglio sulle 160** (ops 0232): dal 16 set anche il simulato perde (−1.516 su 10.000) contro
  −46,65 del paper; il diario conclude «è il mercato di queste due settimane, non l'esecuzione» (r. 1423-
  1425; commit `f48e9e37` «H5 risolta (è il mercato)»). **Conclusione sbagliata**, corretta il 30 set
  (vedi capitolo 5).
* **Il keep del lock lo sceglie il gate per coppia** fra 0,35 / 0,5 / 0,65 (più un quarto valore
  proposto dal paper), e la scelta pesa di più i dati recenti (commit `dde6f9e7`; diario r. 1430-1456).
  Motivo, del proprietario: «ogni dato raccolto deve arrivare al cervello, altrimenti raccogliamo dati a
  fare».
* **Proposta del giorno: intorno da 10 a 40 coppie a notte**, perché «il giro completo di stanotte ha
  fatto 1h09» (ops 0235; diario r. 1487-1498). Sì del proprietario alle 08:40 ora italiana secondo il diario (commit `ea64eb3a`, 06:32 UTC). Il
  giorno dopo si scopre che quell'1h09 era un giro urgenti (vedi 26 set).
* **Controllo orario e dashboard nuova** (commit `425d8086`, `159ff292`; `docs/controllo_schema.md`):
  il bot calcola ogni ora un documento con due semafori («è rotto?», «perde?»), 27 anomalie con soglia,
  una frase per sezione scritta da regole; la discovery scrive il documento del gate. La dashboard passa
  da 6+1 a 4+1 tab, tolti 16 pannelli (diario r. 1511-1545). Il controllo si ferma dopo il primo giro:
  il ramo orario usava l'orologio dei pesi, azzerato a ogni chiusura (commit `8e632b4b`). Trovato anche
  che il rischio effettivo delle posizioni si perdeva al riavvio del bot (commit `04147c7b`, ops 0245).
* **Imparare di più da ogni chiusura** (commit `ae309d1c`): scala dei TP proposta per strategia dal
  vissuto; quinta ipotesi «scala stretta»; **selettore in ombra** (scrive la sua probabilità, non decide).
* **Paper esplorativo acceso** (F1bis, sì del proprietario; commit `3b191851`): fino a 20 quasi
  passaggi, uno per moneta, operati a un quarto della size, al massimo 3 aperti.
* Ogni trade chiuso conserva lo stop originale, la scala, i prezzi dei gradini e le 10 variabili
  d'ingresso (commit `ad236718`).

### 26 settembre: il giro completo che non girava, e la cosa scomoda

* **Il giro completo non girava da giorni** (diario r. 1612-1621; commit `3d3c3278`): partiva solo se la
  discovery cominciava prima delle 03:00 UTC, ma il timer a catena la faceva partire alle 03:30-03:48.
  Quindi l'intorno aveva lavorato su 0 madri e 167 validate su 182 non erano mai state rivalutate (ops
  0261). Corretto con «completo se l'ultimo completo è di più di 20 ore fa», poi limitato alla notte
  (commit `6848923c`).
* Primo giro completo vero: **3h48**, 134.994 valutazioni, 358 coppie passate; intorno a 40: 40 madri,
  5 figlie passate, **0 promosse** (ops 0282-0284; diario r. 1714-1723).
* **La cosa scomoda** (diario r. 1725-1736): **167 validate su 182 non passano più il gate** sui dati
  aggiornati. «È il gate che dice, sui suoi numeri, quello che il paper dice col PF 0,61».
* Dati che mancavano al learning (commit `0fa6c6d2`): l'ombra dei segnali rifiutati (cosa sarebbe
  successo), il controfattuale dopo uno stop, il contesto BTC, la storia delle ipotesi. Corrette tre
  rotture di parità che avrebbero colpito la prima validata a 1 ora (orizzonte 24 ore nel bot contro 96
  nel gate, quarantena in barre, finestra del verdetto del trailing) (diario r. 1682-1689).
* Verifica «attesi contro aperti» sui giorni confrontabili (24-25 set): 46 attesi, 41 aperti, 89%
  (ops 0265, 0258; diario r. 1691-1700).
* **Piano 1-5, sì del proprietario a tutto** (commit `e8e52bc7`, `579109fa`; diario r. 1738-1771, suite
  1701): autopsia delle validate; il gate giudica le validate con la configurazione che operano e
  **declassa a un quarto della size** quelle bocciate in due giri completi di fila; giro completo ridotto;
  freno per gruppo (allarmi statistici per famiglia e regime); 1 ora su 30 monete.

### 27 settembre: l'autopsia, la conferma a maggioranza, il bug della sessione

* **Autopsia delle validate** (ops 0290; diario r. 1777-1788): 194 esaminate su 212. Col gate di oggi
  ne passano 17; giudicate con la configurazione che operano, 23. Le 171 bocciate in entrambi i modi
  cadono su criteri diversi (recupero 37, consistenza 33, rendimento totale 32, holdout 30, regime 28).
  Lettura: **«la porta d'ingresso è larga»**: `judge_window` contava una finestra come conferma se la
  coppia passava **almeno una volta** nei 7 giorni, su molte valutazioni; «valutata una volta sola, oggi
  ne passa una su otto».
* **Replay del freno per gruppo** (ops 0288): suona dopo il freno globale in 6 gruppi su 7. Bocciato con
  la regola scritta prima.
* **Tre sì del mattino** (commit `aa6b89e5`; diario r. 1837-1849): **conferma a maggioranza** (J11: una
  finestra vale solo se la coppia passa più della metà delle valutazioni della settimana); freno per
  gruppo spento (I2); report dei rifiutati corretto (J6: «−6,80R» era uno stop letto come percentuale
  invece che come frazione; il valore giusto era −0,17R).
* **Referto settimanale** (diario r. 1851-1897): settimana 21-27 set 91 trade, −55,75 (ops 0302); il
  paper entra dove entra il gate solo nel 54% dei casi (20 su 37, ops 0304), contro il 59% del 21 set;
  il paper ha fatto 8 perdite di fila, il gate sulle stesse 8 coppie e 2.256 trade dal 2023 mai più di 7
  (ops 0304). Proposta: aprire il problema degli ingressi trade per trade.
* **Ingressi, prima lettura** (ops 0308; diario r. 1899-1932; commit `169945f7`): su 70 trade del paper,
  36 abbinati a un ingresso del motore (51%). Fra i non abbinati: 15 «senza motore» (la cache delle
  candele finiva il 26 alle 15:45: un limite dello strumento), 5 «prezzo vivo» (il bot decideva sul
  prezzo dell'ultimo tick, il motore sulla chiusura della candela), 5 «ignoto» tutti di `gen_6d06dca0`.
  Corretto il prezzo: il bot decide sulla chiusura della candela (commit `33caaf24`,
  `DECISIONE_SU_CHIUSURA`).
* **Il bug della sessione oraria** (J13; diario r. 1934-1947; commit `6a846de4`): il mattoncino
  `session` leggeva l'ora **dall'orologio del computer**, non dalla candela. Nel gate tutta la storia era
  giudicata con l'ora del giro (di notte «fuori sessione» = solo short, di giorno solo long). Spiegava i
  5 «ignoto». **47 validate su 212 usavano la sessione** (ops 0314).
* **Sera, sì del proprietario** (commit `a7aa299a`): la sessione diventa un filtro per entrambi i lati;
  le coppie che la usano ripartono da zero passaggi. Il giorno dopo il report dirà **347 coppie
  azzerate**, comprese le 47 validate (ops 0324).
* Il keep del lock proposto per strategia dai verdetti del trailing (I3, commit `4829c82a`).
* **Analisi completa degli ingressi** (ops 0318-0320; diario r. 1979-1996): 62 abbinati su 135 (46%),
  ma per l'effetto atteso delle correzioni del giorno: le coppie con la sessione cambiano comportamento
  nel motore (SUI `gen_490a90e5` da 782 a 292 trade sulla storia). La parità vera si misura solo sui
  trade aperti dopo le correzioni del 27.

### 28 settembre: il primo giorno in utile, le declassate, la quota di Firestore

* Il 27 set è il primo giorno chiuso in utile (+3,25 sul conto; +1,26 sulle sole validate in dashboard:
  due conti diversi, diario r. 2018-2025). Totale 142 trade delle validate più 2 esplorativi, 52% vinti,
  −69,31 (ops 0322; −69,10 sulle sole 142 validate, ops 0321, cifra che il diario r. 1998-2016 dà come totale).
* **121 validate su 192 declassate a un quarto della size** (ops 0324): «la maggior parte del paper oggi
  rischia un quarto». (Il 30 set la revisione scoprirà che il quarto di size quasi non agisce: vedi cap. 5.)
* **Quota di letture Firestore esaurita** alle 06:18 UTC (piano gratuito: 50.000 letture al giorno; ops
  0331, 0332; la console mostrava il passaggio da 8.000 a 39.000 letture al giorno, commit `76ffb8d0`).
  Corretto (sì del proprietario): contatore delle letture, cache dei trade nel bot, finestra dei
  rifiutati ridotta; stima circa 7.300 letture al giorno dal bot (J14). Le giornate passano all'ora
  italiana, con due totali («conto» = tutti i trade, «validate» = solo quelle decise dalla strategia).

### 29 settembre: la proposta dell'holdout a 10 trade, ritirata

* Controllo (ops 0338-0350; diario r. 2075-2107): 174 trade, 55% vinti, −67,34; PF vissuto 0,70 contro
  2,04 promesso; 199 validate su 69 monete; letture Firestore circa 9.400 al giorno.
* **Proposta H2: l'esame finale chiede almeno 10 trade invece di 5** (diario r. 2109-2119). Ritirata
  dopo la misura (diario r. 2123-2131; commit `fd58002c`): una strategia senza vantaggio passa il 31%
  delle volte con 5 trade e il 37% con 10 (simulazione, non codice del repo); toglierebbe soprattutto le
  coppie con pochi trade (il 70% delle validate fa meno di 10 trade in 45 giorni, ops 0290). Trovato
  anche che lo «scarto 0,000» che l'AI leggeva come misura era un segnaposto del codice.
* Il report del mattino racconta il learning (storia, come impara il trailing, cosa imparano le
  strategie) e la spesa delle chiamate AI del bot (commit `6ae4c6a7`). Il filtro monete dell'AI riceve
  5.000 token invece di 2.000 perché le sue risposte venivano tagliate a ogni giro (commit `c8117991`).

### 30 settembre: la revisione delle voci sospese, la misura fuori campione, le regole di ottobre

* **Il filtro monete dell'AI, appena smesso di essere tagliato, toglie 10 monete su 30 alla passata a 1
  ora**, giudicandole dal nome («listing recente, storia troppo corta», ops 0365), compresa QUSDT con
  393 giorni di storia (diario r. 2309). Corretto: con un elenco scelto apposta il filtro non si applica
  (commit `a2a2aeaf`); in serata il filtro è spento del tutto.
* **Copertura 35,0%: `ready` ora vale anche per la via originale** (ops 0363: «ready ... True (via
  copertura) · 202 validate / 70 coin coperte / universo 200»).
* **Revisione delle voci in sospeso** (`docs/revisione_sospese_30set.md`, commit `cadaa136`). In tre
  righe: nessuna voce in sospeso rende i trade migliori da sola; dal 27 set il paper è in pari (+10,19,
  ops 0371); **i numeri del paper sono quelli che darebbe un prezzo casuale con le nostre uscite**; la
  domanda vera è se il gate sceglie coppie con un vantaggio o solo fortunate.
* Voci tolte dal backlog col verdetto (commit `1e17508b`; diario r. 2217-2237): take profit dal grafico
  (smentita: 3,35R in mediana, raggiunto dal 7% contro l'11% del primo gradino, ops 0366); allargare
  l'universo (non serve: 70 monete coperte); «la copertura non arriverà al 35%» (smentita); e altre tre.
* **Prima lettura fuori campione** (H5; commit `a2a2aeaf`; ops 0371; diario r. 2252-2260): il motore,
  sui soli trade nati dopo la validazione di ogni coppia, fa 117 trade a +0,12R; il paper sulle stesse
  coppie 77 trade a +0,001R; differenza dentro il margine (±0,25R). Sugli stessi segnali motore +0,05R e
  paper +0,01R. **La cosa nuova:** il paper sulle 25 coppie non più validate fa 45 trade a −0,23R: la
  perdita del paper sta soprattutto su coppie che il gate aveva già tolto o ridotto.
* **Regole delle letture di ottobre scritte prima dei numeri** (K1, commit `795b6821`; diario r.
  2262-2281): il 7 e il 14 ottobre, «selezione» se il motore fuori campione ha R medio ≤ 0 su almeno 80
  segnali unici; «esecuzione» solo sui trade dove paper e motore entrano sullo stesso segnale, con almeno
  30 trade accoppiati e la differenza oltre 2 errori standard per giornata.
* **Gruppo di controllo acceso** (K3, commit `af120806`): a ogni giro circa 50 bocciate a caso e la foto
  delle conferme, per sapere se le validate battono le scartate.
* **Voto t di ogni validata** (K2, commit `50ed6462`): 30 revisori, 22 difetti confermati,
  19 corretti; la passata una tantum dà t ≥ 2 sul walk-forward per 47 su 213 coppie (mediana 1,27) e
  sull'ultimo esame per 18 su 183 (ops 0383).
* **Sera, decisioni del proprietario** (commit `3d8f20a2`; diario r. 2299-2319): regola H1 (la t
  dell'ultimo esame di 45 giorni, soglia 1,5, almeno 80 segnali per gruppo, lettura a metà novembre);
  **filtro monete AI spento**; **ombra AI spenta** (229 decisioni, veto sull'85% dei trade, nessuno la
  usava); F2 chiusa («strategie in paper dopo 1 conferma»: non si fa); J12 chiusa (81% dei trade del
  paper con un ingresso del motore vicino, contro l'80% richiesto, ops 0373). Suite 2023 test verdi.

### 1 ottobre, mattina: cosa si sapeva alla fine del mese

Dalla prima sezione di `docs/capito.md` (2026-10-01) e dal controllo del 1 ottobre (diario r. 2358-2382):

* Il bot esegue quasi come il motore: sugli stessi 79 segnali la differenza è +0,05R con margine ±0,16R
  (ops 0387). «Un difetto grosso di esecuzione è quasi escluso; il problema sembra prima del bot.»
* Dopo la scelta del gate le validate rendono poco anche nel motore: +0,06R a trade su 89 segnali (ops
  0387), contro +0,18 promesse.
* Il paper non si distingue da un prezzo casuale con le stesse uscite: 54% di vinti contro 54%, 46% di
  stop contro 46% (ops 0401).
* Stop giornaliero e freno di serie, rigiocati sul gate, avrebbero tolto soprattutto i rimbalzi (ops
  0405). Nessuna funzione ha ancora un contributo dimostrato oltre il margine (ops 0409).
* Per completezza (fuori dal mese): la lettura ufficiale del 7 ottobre dice «selezione → la prossima
  modifica va nel gate» (motore dopo la validazione −0,05R su 230 segnali, ops 0532), confermata il 16
  ottobre (−0,03R su 566, ops 0619) (`docs/letture.md`). Dal 13 ottobre la ricerca automatica del gate è
  ferma (`ops/gate_fermo`).

---

## 2. Le modifiche del mese (bot, gate, paper)

Per ognuna: **cosa**, **quando** (commit), **perché**, **effetto misurato**, **destino** dopo
settembre. «Destino» l'ho controllato sui valori predefiniti del codice di oggi (`bot/config.py`,
`scripts/optimize.py`, `scripts/discover_strategies.py`); dove scrivo «non verificato» non l'ho
controllato. Ricordo che dal 13 ottobre il gate non gira più (`ops/gate_fermo`), quindi tutto ciò che
vive nel gate oggi è fermo comunque.

### 2.1 Il gate e la contabilità delle conferme

| cosa | quando | perché | effetto misurato | destino |
|---|---|---|---|---|
| Il taglio della rivalutazione tiene prima le coppie con conferme | 13 set, `a01b05cb` | teneva le più vecchie | non aveva ancora tolto niente (329 note contro 500, ops 0040) | non verificato |
| Le monete con una coppia avviata rientrano nell'universo | 14 set, `f0bcbbec`; senza tetto dal 17 set, `78813a2f` e `4f7ede65` | ORCAUSDT uscita dall'universo, le sue coppie congelate | le prime 7 validate (ops 0054) erano proprio quelle | non verificato |
| Nessuna potatura cancella una coppia con conferme recenti (regola fissa + test) | 14 set, `e29232d0` | la potatura cancellava coppie a 1-2 conferme non viste da 6 giorni | 23 coppie nella finestra di rischio quel giorno (controllo unico) | test ancora nel repo (`tests/test_confirmations_are_never_lost.py`) |
| Semi delle mutazioni prima sulle monete non coperte | 14 set, `81a87f3d` | aumentare le monete operabili | non misurato a parte | non verificato |
| `ready` registra i numeri su cui è deciso | 16 set, `96196d43` | contraddizione fra registro e decisione | si legge «deciso il ... su ...» (ops 0071) | rimasto (ops 0363 lo stampa) |
| Via a conteggio accesa (`OPTIMIZER_READY_MIN_PAIRS=10`) | 16 set, `.env` della macchina (`ops/requests/0063`) | scelta del proprietario, contro la raccomandazione di aspettare | paper partito alle 15:44 con 35 validate su 19 monete (ops 0071) | al 30 set `ready` vale anche via copertura (ops 0363) |
| Registro compatto, alleggerito sempre, rete sulla scrittura | 19 set, `ecb99ab5` | 86% del limite di 1 MiB, 3 giorni al muro | da 759 a 272 KiB, 47 validate prima e dopo (diario r. 802-806) | rimasto (476 KiB su 879 il 1 ott, diario r. 2364) |
| Quarantena dopo uno stop anche nel gate | 21 set, `1d96dc3d` | parità bot/gate | non misurato a parte | `COOLDOWN_HOURS` ancora in `bot/config.py` |
| Scarto delle «gemelle» (stessa firma) fra le candidate | 21 set, `1d96dc3d` | strategie identiche contate come diverse | le validate gemelle restano: 8 gruppi il 27 set (diario r. 1873) | `firma_spec` ancora nel codice |
| Strategie scritte a mano fuori dal giro; semi da 10 a 30 | 21 set, `1670bc71` | 0 validate su 1.312 valutazioni; copertura 15,8% | copertura al 35,0% il 30 set (ops 0363) | rimasto (`OPTIMIZER_SKIP_BASE=true`, `DISCOVERY_SEEDS=30`) |
| Contesto di mercato solo alle strategie che lo usano | 22 set, `dead71b4` | il giro sforava le 3 ore | non misurato nel diario | non verificato |
| Rivalutazione completa una volta al giorno, «urgenti» negli altri giri | 23 set, `7b77b23b` | 2h29 a giro, 77% speso a ripetere lo stesso verdetto | ha prodotto due difetti: le urgenti che non si svuotavano (fino al 24 set) e il completo che non partiva (fino al 26 set) | modificato il 26 set (regola delle 20 ore, solo di notte, `3d3c3278`, `6848923c`) |
| Le bocciature chiudono la finestra; la conferma si registra alla chiusura della finestra | 24 set, `eb0b992d` | 223 strategie «urgenti» per sempre; conferme guadagnate e mai registrate | urgenti da 223 a 8; validate da 59 a 160 (ops 0224, diario r. 1376-1387) | non verificato |
| 40 candidate casuali per giro invece di 100 | 24 set, `033a1ee4` | quattro fonti ragionate | tasso di passaggio 0,21-0,26% contro 0,3% prima (diario r. 2333) | non verificato |
| Statistica t salvata nel registro (misurata, non regola) | 24 set, `033a1ee4`; voto fissato alla promozione 30 set, `50ed6462` | capire se le validate sono fortunate | 47 su 213 con t ≥ 2 (ops 0383) | regola H1 da leggere a metà novembre |
| Il keep del lock scelto dal gate per coppia (0,35/0,5/0,65 + proposta del paper) | 25 set, `dde6f9e7`; per strategia 27 set, `4829c82a` | parità: se l'avesse cambiato solo il bot, gate e paper avrebbero diviso | scelto per 43 validate su 202 il 30 set; i trade con keep 0,75 sono 5 a −0,14R (ops 0358) | non verificato |
| Intorno: tetto da 10 a 40 coppie a notte | 25 set, `ea64eb3a` | il giro «completo» durava 1h09 (in realtà era un giro urgenti) | primo vero: 40 madri, 5 figlie passate, 0 promosse (ops 0282-0284) | default ancora 40 |
| Giro completo se l'ultimo è di oltre 20 ore fa, solo di notte | 26 set, `3d3c3278`, `6848923c` | il completo non partiva da giorni | primo completo 3h48 (ops 0282-0284); il 1 ott 2h58 (diario r. 2360) | non verificato |
| Le validate giudicate con la configurazione che operano; **declassate** a un quarto dopo due bocciature notturne | 26 set, `579109fa` | 167 validate su 182 non passavano più | declassate 0 → 121 → 142 → 160 (ops 0294, 0324, diario r. 2096, ops 0363); il quarto di size quasi non agisce (revisione 30 set, punto 4) | `DECLASSATA_NOTTI=2` ancora nel codice |
| Giro completo ridotto (le note solo sulle loro monete più 1/7 dell'universo) | 26 set, `579109fa` | 134.994 valutazioni, 3h48 | completo della notte circa 1h45 (dedotto dal log del bot, diario r. 1814) | non verificato |
| 1 ora su 30 monete (`DISCOVERY_EXTRA=1h:auto30`) | 26 set, `579109fa` | allargare dopo BTC | passaggio a 1 ora 0,32-1,15% contro 0,20-0,26% a 15 minuti (diario r. 1816, 2011, 2097, 2174); nessuna validata a 1 ora a settembre | default ancora `1h:auto30` |
| **Conferma a maggioranza** (J11) | 27 set, `aa6b89e5` | «la porta è larga»: una finestra valeva con un solo passaggio su molti | lettura prevista il 18 ott (`docs/letture.md`) | `GATE_CONFERMA_QUOTA=0.5` ancora nel codice |
| Sessione oraria letta dalla candela, poi filtro per entrambi i lati; 347 coppie azzerate | 27 set, `6a846de4`, `a7aa299a` | il mattoncino leggeva l'orologio del computer | 0 validate con la sessione il 28-29 set (ops 0324, diario r. 2098) | non verificato |
| Filtro monete AI saltato con un elenco scelto; poi spento | 30 set, `a2a2aeaf`, `3d8f20a2` | escludeva monete dal nome | — | spento (`AI_UNIVERSE_FILTER=false`) |
| Gruppo di controllo (bocciate a caso) | 30 set, `af120806` | sapere se il gate seleziona davvero | lettura prevista il 15 ott | gate fermo dal 13 ott |

### 2.2 Il bot e il paper: ingressi, uscite, rischio

| cosa | quando | perché | effetto misurato | destino |
|---|---|---|---|---|
| Le validate si operano anche se il volume scende | 17 set, `4f7ede65` | richiesta del proprietario | — | non verificato |
| Protezione del profitto ancorata al **primo** gradino (A1) | 21 set, `432e7f48` | 13 stop su 21 erano andati a favore sotto il primo gradino | protezione: 1 stop su 58 nella classe «protezione» il 27 set (ops 0297); non c'è una misura prima/dopo | `lock_anchor` ancora nel codice |
| Regime: prima la direzione, poi la volatilità | 21 set, `1d96dc3d` | il freno sul controtrend non frenava | non misurato | non verificato |
| Break-even dopo il primo gradino scelto dal gate (A2) | 21 set, `340fda18` | — | non misurato a parte | non verificato |
| Tetto di perdita per moneta al giorno, 1,5% | 21 set, `340fda18` | — | zero blocchi nelle 24 ore del 27 set (diario r. 1889-1890) | default ancora 1,5% |
| Conferma a 1 ora e `htf_fade` come mattoncini | 22 set, `7d0e5261`, `4ab04729` | idea del proprietario | sui 35 trade del 22 set avrebbe tolto 11 trade (+5,87) | nel vocabolario |
| Strategie native a 1 ora | 22-23 set, `e9989e7f`, `ddf62dea` | richiesta del proprietario | 0 validate e 0 operate a settembre (diario r. 1682) | vedi 1 ora su 30 |
| Stop più largo del 6% = setup non operabile (gate e bot) | 23 set, `cf94be7d` | MUBARAK con stop a −15,3% | 1 rifiuto «stop largo» nelle 24 ore del 27 set (diario r. 1827) | default ancora 6% |
| Referto di ogni trade chiuso | 23 set, `cf94be7d` | richiesta del proprietario | le classi del referto risultano uguali a quelle di un prezzo casuale (revisione 30 set) | non verificato |
| **Freno di serie** (4 perdite → size a metà) | acceso 23 set, `e26682a5`; spento 24 set, `eb0b992d` | — / scattava per caso | dopo 4 perdite il win rate non cala oltre il caso (sempre un po' sotto l'incondizionato, t fra −1,55 e −0,15): 33% su 6, 56% su 16, 61% su 18, 63,6% su 22 casi (ops 0188, 0232, 0267, 0302) | spento (`STREAK_BRAKE_ENABLED=false`) |
| Tetto di rischio per direzione 3% | 24 set, `033a1ee4`; la copia tolta il 24 set (`eb0b992d`) | — | portafoglio simulato: ops 0184 PnL da +10.386 a +11.983; ops 0188 da +10.386 a +9.664 (due risultati diversi) | resta la regola già esistente (`MAX_DIRECTIONAL_RISK_PCT`) |
| Il rischio effettivo sopravvive al riavvio | 25 set, `04147c7b` | perso al riavvio (ops 0245) | — | non verificato |
| Paper esplorativo (quasi passaggi a un quarto della size) | 25 set, `3b191851` | più chiusure da cui imparare | 7 chiuse, 6 vinte, +2,67 al 30 set (diario r. 2175) | `ESPLORATIVE_MAX=20` ancora nel codice; stato attuale non verificato |
| Freno per gruppo; panchina con pavimento 0,25 | 26 set, `579109fa`; freno spento 27 set, `aa6b89e5` | — / suona dopo il freno globale | replay ops 0288 | spento (`POOL_BRAKE_ENABLED=false`) |
| Il bot decide sulla chiusura della candela | 27 set, `33caaf24` | parità col motore («prezzo vivo») | paper entra dove entra il motore: 54% il 27 set → 81% il 30 set (ops 0304, 0373) | default ancora `DECISIONE_SU_CHIUSURA=true` |
| Ricarica del registro entro un minuto dalla scrittura | 26 set, `579109fa` | — | — | non verificato |

### 2.3 Il «cervello» (learning)

| cosa | quando | effetto misurato | destino |
|---|---|---|---|
| Scala dei TP dal mfe del paper che si aggiunge alle quattro fisse | 19 set, `ed042b11` | scala dal vissuto 0,75/1,25/2 proposta (ops 0261) | non verificato |
| Referti aggregati e ipotesi da regole scritte prima | 23 set, `e26682a5`; sesta ipotesi «condizioni d'ingresso» 26 set, `3b851fe7`; settima «controtrend BTC» 26 set, `0fa6c6d2` | — | ipotesi ancora scritte nella storia (diario r. 2735) |
| Varianti dai referti nel gate, con conferme retroattive | 23-24 set, `e26682a5`, `daf083bd` | 2 create e 2 bocciate il 26 set (ops 0282-0284); 0 promosse in tutto (diario r. 2733-2734) | il taglio sui dati prima dell'ipotesi è spento dal 24 set; varianti spente dal 2 ott (`DISCOVERY_VARIANTI_REFERTI=false`) |
| Intorno delle validate | 24 set, `91da019e` | 0 promosse il 26 set (ops 0282-0284) | tetto 40 nel codice; gate fermo |
| Dataset del selettore, addestramento, verdetto per permutazione | 24 set, `91da019e`, `b79ac764`, `f6e16b04` | **NON BATTE** «apri tutto» a ogni lettura del mese, fino a 0 finestre su 3 su 92.257 trade (ops 0368) | mai acceso (nel codice di oggi non c'è un interruttore di attivazione) |
| Selettore in ombra nel bot | 25 set, `ae309d1c` | probabilità media dei vinti 0,65 contro 0,63 dei persi su 70 trade (diario r. 2015) | solo osservato |
| Ombra dei segnali rifiutati | 26 set, `0fa6c6d2` | «posizione aperta» −0,15R contro −0,21R degli aperti, sotto la soglia (ops 0370) | report corretto il 1 ott per confrontare lo stesso periodo |
| Memoria completa di ogni trade | 25 set, `ad236718`; 26 set, `0fa6c6d2` | — | non verificato |

### 2.4 AI, strumenti, infrastruttura, dashboard

* **AI** (vedi anche cap. 5): chiave con intestazione del workspace (19 set, `965a87ed`); stesse
  intestazioni ovunque (`99953432`); motivi degli scarti (`893e7267`); fasce nel prompt (20 set,
  `46d5b124`); `rr` tolto (21 set, `340fda18`); idee AI: 38 delle 637 coppie passate al 29 set venivano
  dall'AI (diario r. 2102); spente il 2 ottobre (0 validate su 103 strategie AI, diario r. 2732).
* **Strumenti di misura**: `trade_stats` per direzione (18 set), `frequenza` giorno per giorno (19 set),
  `confronto` gate/paper con gradini e serie (21 set, `3e1e23fb`, `ededca9e`), `mfe` con gli stop per
  classe (21 set, `b6c50e74`), `portafoglio` (24 set), `autopsia-validate` (26 set), `ingressi` (27 set),
  `replay` del freno (26 set), sezione FUORI CAMPIONE del `portafoglio` (30 set).
* **Controllo orario e dashboard 4+1** (25 set, `425d8086`), con schema in `docs/controllo_schema.md`;
  ora italiana e due totali (28 set, `76ffb8d0`); benchmark BTC dal primo giorno e battito dell'agente ops
  (28 set, `b2e9e9d4`).
* **Quanto è cresciuto il codice a settembre** (stima mia con `git diff --shortstat` fra l'ultimo
  commit di agosto e l'ultimo di settembre): +55.496 / −4.789 righe in `bot`, `scripts`, `backtesting`,
  `tests`, `dashboard` (bot +11.083, scripts +14.490, tests +23.648); file di test da 56 a 135; la suite
  da 730 test verdi del 14 set (commit `f0bcbbec`) a 2.023 del 30 set (commit `3d8f20a2`).

---

## 3. Le misure e le letture del mese

Ogni voce: **domanda** → **numero** (fonte) → **conclusione**.

### 3.1 Il gate produce qualcosa? (le conferme)

* **Una coppia che passa il gate ripassa una settimana dopo, e una terza?** → 13 set: 0 validate, le 8 di
  ORCA a 2/3 non ripassano (ops 0035, 0040); 14 set: 7 validate su 1 moneta (ops 0054); 15 set: 11 su 4
  (ops 0055); 16 set: 31 su 16 e poi 35 su 19 (ops 0061, 0071); 19 set: 47 su 24 (diario r. 804); 21 set:
  56 su 26 (commit `1670bc71`); 24 set: 59 su 27 (diario r. 1252); 25 set: 160 su 52 (ops 0224); 26 set:
  182 su 62 (ops 0261); 27 set: 212 su 68 (ops 0294); 28 set: 192 su 66 dopo l'azzeramento della sessione
  (ops 0324); 29 set: 199 su 69 (diario r. 2095); 30 set: 202 su 70 (ops 0363). → Il segnale del 6 set è
  risolto in positivo: quello che il gate trova si ripete anche la terza volta. Ma vedi 3.2.
* **Copertura dell'universo** → 7,4% il 16 set (diario r. 516), 12,2% alla partenza del paper (ops 0071),
  15,8% il 21 set (commit `1670bc71`), 26% il 25 set, 31% il 26 set, 34% il 27 set, 35,0% il 30 set (ops
  0224, 0261, 0294, 0363). → Obiettivo del 35% raggiunto due settimane dopo la partenza del paper.
* **Tasso di passaggio** → a 15 minuti 0,20-0,26% delle valutazioni (diario r. 1816, 2011, 2097, 2174);
  a 1 ora 0,32-1,77% (stesse righe e r. 2377). → Coerente con la sonda del 15 set: a 1 ora va meglio.

### 3.2 Il gate sceglie bene? (la «porta larga»)

* **Le validate ripassano il gate sui dati aggiornati?** → **167 su 182 no** (primo giro completo, 26
  set; diario r. 1725-1731).
* **Perché?** (autopsia, ops 0290) → col gate del 27 set ne passano 17 su 194; con la loro
  configurazione 23; la scala globale spiega solo 6 bocciature su 177. → «La porta d'ingresso è larga»:
  bastava un passaggio su molte valutazioni della settimana. Risposta: conferma a maggioranza (27 set).
* **Holdout a 10 trade toglierebbe i fortunati?** → no: senza vantaggio si passa il 31% delle volte con 5
  trade e il 37% con 10 (simulazione, diario r. 2127-2128); l'holdout lo passa il 46% di chi supera le
  finestre (ops 0322). → Proposta ritirata.
* **La t separa le buone dalle fortunate?** → per una simulazione della revisione, con t ≥ 1,5 all'ultimo
  esame le fortunate che passano scendono dal 13,6% al 2,6%, ma le buone (PF 2) dal 40,5% al 14,3%
  (stima, revisione 30 set §2). Sui dati veri: t ≥ 2 sull'ultimo esame per 18 su 183 (ops 0383). → Regola
  H1 scritta prima, lettura a metà novembre.
* **Il gate promette su un regime che c'è ancora?** → sulle 8 coppie rigirate, nel periodo del paper i
  segnali del gate aperti dal paper hanno PF 0,45, quelli non aperti 0,66 (ops 0304). → «Il gate ha
  promesso su un regime che non c'è più» (ops 0304, lettura dello strumento).

### 3.3 Il paper esegue quello che il gate ha validato?

* **Frequenza: il paper apre i segnali che deve?** → 19 set: 87% sui giorni corretti per le ore (diario
  r. 913-914); 26 set: 89% sui giorni confrontabili (ops 0265, 0258); 27 set: 51 attesi, 51 aperti il
  25-26 set (diario r. 1827); 29 set: 24 apribili contro 23 chiusi (diario r. 2177). → Nessun divario
  sistematico. (Il 25 set il diario scriveva «24 apribili al giorno contro 5,5 aperti, il collo è il bot»,
  ops 0229, 0234: la sonda usava le validate di quel giorno su tutta la settimana.)
* **Il paper entra dove entra il motore (entro 2 candele)?** → 21 set 10 su 17 (59%); 27 set 20 su 37
  (54%) (ops 0304); 27 set con lo strumento `ingressi` 36 su 70 (51%), 65% togliendo i trade senza cache
  (ops 0308); 46% sui 135 dell'analisi completa, ma per effetto delle correzioni (ops 0320); 30 set 81%
  (64 su 79, ops 0373; la revisione scrive 62 su 77, ops 0371). → Problema chiuso dopo la correzione della
  chiusura della candela e della sessione.
* **Esecuzione o selezione?** → 24 set: segnali del gate aperti 15 (PF 0,50) e non aperti 9 (PF 1,23)
  (ops 0211); 25 set: simulato −1.516 contro paper −46,65 dal 16 set, letto come «è il mercato» (ops
  0232); 30 set: sugli stessi giorni 16-24 set il simulato fa −1.357 con le coppie del 25 set e +8.465 con
  quelle del 30 set (ops 0232, 0359): **il numero misurava la selezione**. Prima misura pulita fuori
  campione: motore +0,12R su 117, paper +0,001R su 77, stessi segnali +0,05R contro +0,01R (ops 0371).
  → Non si decide a settembre; regole scritte per il 7 e il 14 ottobre.

### 3.4 Come perde il paper (ingresso, uscita, stop, trailing)

* **Come muoiono gli stop** (classi: «ingresso» = mai andato a favore; «uscita» = andato a favore ma
  sotto il primo gradino; «protezione» = oltre il primo gradino) → 21 set 7/13/1 su 21 (diario r. 1043-
  1045); 24 set 8/19/1 su 28 (diario r. 1264); 26 set 18/26/1 (ops 0264); 27 set 23/34/1 su 58 (ops 0297);
  29 set 34/43/1 (ops 0346); 30 set 39/43/1 (ops 0366). → Per sei settimane si è letto «la leva è
  l'uscita». Il 30 set la revisione mostra che un prezzo casuale con le nostre uscite dà 48,5% / 51,5%
  (paper 47% / 52%): **le classi sono la forma delle regole d'uscita, non una diagnosi** (revisione 30
  set §4 punto 1).
* **Dove arriva il prezzo** → mfe mediana 0,52R sui primi 7 trade (diario r. 677); 0,87-0,88R a fine mese
  (diario r. 2093, 2171); l'88% dei trade non tocca il primo TP (stesse righe); prezzo casuale 0,81R
  (revisione 30 set §4).
* **Take profit dal grafico (A5)** → 3,96R in mediana, raggiunto dal 2% (ops 0210); 4,04R, 2% (ops 0237);
  3,35R, 7% (ops 0366); primo gradino 11%. → Smentita.
* **Il lock taglia i vincitori?** → 27 set: 30 verdetti del trailing, 11 prematuri e 19 protetti (ops
  0290, diario r. 1859-1861); 30 set: 70 verdetti, 29 prematuri e 41 protetti (58,6%) (ops 0358). → No.
* **Le serie di perdite sono anomale?** → il paper ha fatto 8 perdite di fila; il gate sulle stesse 8
  coppie mai più di 7 su 2.256 trade (ops 0304). Dopo 4 perdite il win rate del gate non scende oltre il caso (ops
  0188, 0232, 0267, 0302). → Il freno di serie resta spento.
* **Gli short in un mercato che sale** → in USDT entrambe le direzioni perdono tutto il mese (vedi
  cap. 4); in R, dal 27 set, short +0,21R su 27 e long −0,09R su 34 (ops 0388); col contesto BTC noto dal
  25 set, short +5,39 su 52 e long −12,98 su 46 (ops 0360). → Indizio, non verdetto (la revisione chiede
  di rifare i conti in R e dal 27 set, §4 punto 9).
* **I rifiutati sarebbero andati meglio?** → 27 set: «cooldown» 11 casi a −1,00R, «posizione già aperta»
  16 a −0,68R (ops 0289); 28-30 set «posizione aperta» −0,20 / −0,10 / −0,15R contro −0,26 / −0,21 /
  −0,21R degli aperti (diario r. 2012-2014, ops 0350, 0370). → Sotto la soglia, nessuna ritaratura.

### 3.5 Sonde e portafoglio

* **Timeframe** (ops 0060) → vedi 15 set: 1 ora meglio di 15 minuti meglio di 5 minuti, su tutte le
  monete.
* **Portafoglio simulato delle validate** → 24 set +10.386 su 10.000 in 60 giorni, drawdown 16,25% (ops
  0184, 0188); 25 set +12.296, drawdown 14,8% (ops 0232); 27 set +25.444, drawdown 19,6%; long 463 trade
  +24.997, short 686 trade +447 (ops 0302). → Il livello è gonfiato dalla selezione; vale la forma.
  Diversification ratio 0,17 → 0,11 → 0,10 (ops 0188, 0232, 0302): le coppie si compensano molto.
* **Stop giornaliero di portafoglio al 3%** (simulato) → da +9.664 a +7.638, drawdown da 17,0% a 14,9%
  (ops 0188). Rigiocato il 1 ott sul gate: −11.615 e drawdown da 11,7% a 20,3% (ops 0405, `docs/capito.md`
  1 ott). → Parcheggiato.
* **Spazio del registro** → 759 KiB (86%) il 19 set; 272 KiB dopo la correzione (diario r. 750-806); 2.859
  coppie su 3.000 il 26 set (diario r. 1630); 476 KiB il 1 ott (diario r. 2364).
* **Durata dei giri** → 21 set 2h22 (commit `1670bc71`); 22 set oltre 2h53 (commit `dead71b4`); 23 set
  2h29 (commit `7b77b23b`); 24 set urgenti 1h54, a mano 2h07; 25 set «1h09» (era urgenti); 26 set completo
  3h48; 27 set completo ridotto circa 1h45 (dedotto) e urgenti 1h13; 28-30 set urgenti 1h48, 2h03, 2h01;
  1 ott completo 2h58 (diario r. 1254, 1365, 1471, 1716, 1812-1815, 2015, 2097, 2164, 2360).

---

## 4. I numeri del paper a settembre

Il paper è partito il 16 settembre alle 15:44 UTC (ops 0071) con 1.000 USDT finti; `DRY_RUN` è rimasto
`true` per tutto il mese (ogni report lo stampa). I numeri qui sotto sono cumulativi dalla partenza.

### 4.1 Le fotografie del mese

| data (fonte; dal 24 set le ore sono in ora italiana) | trade chiusi | vinti | PnL realizzato (USDT) | equity | costi stimati | PF vissuto / promesso |
|---|---|---|---|---|---|---|
| 17 set 20:07 (ops 0073, 0074) | 3 | 1 (33%) | −2,34 | 997,66 | 0,97 (lordo −1,38) | — |
| 18 set 12:58 (`docs/state.md`, diario r. 674-686) | 7 | — | 6 stop pieni su 7, −17,47 | — | — | 0,221 / 1,884 |
| 19 set (diario r. 849) | 12 | 2 | — | — | — | — |
| 21 set (diario r. 997) | 24 | 5 (stima: 2 short + 3 long) | −45,70 (stima: −30,11 −15,59) | — | — | — |
| 23 set (dashboard, diario r. 1154) | 40 | — | −50,88 | — | — | — |
| 24 set 08:20 (ops 0175-0183, diario r. 1249) | 44 | 16 (stima: 6 long + 10 short) | −49,15 | 950,85 | 11,30 (lordo −37,85) | 0,60 / 1,89 |
| 25 set 07:10 (ops 0227; alle 08:10 i trade sono 55, ops 0234) | 54 | 23 (stima: 9 + 14) | −46,65 | 953,35 | 12,64 su 54 (lordo −34,01) | 0,64 / 1,89 |
| 26 set 08:20 (ops 0258, 0259) | 84 | 46% | −63,73 | 936,27 | — | 0,61 / 2,09 |
| 27 set 08:00 (ops 0291, 0292) | 110 + 1 esplorativo | 48% | −73,79 | 927,56 | 20,58 (lordo −53,21) | 0,62 / 2,10 |
| 28 set 07:40 (ops 0321-0330) | 142 + 2 | 52% | −69,31 (−69,10 sulle sole validate, ops 0321) | 930,69 | — | 0,67 / 2,10 |
| 29 set 08:20 (ops 0340, 0341, 0338) | 174 (168 + 6) | 96 (55%) | −67,34 | 932,66 | 28,16 (lordo −39,18) | 0,70 / 2,04 |
| 30 set 08:20 (ops 0360, 0361) | 189 (182 + 7) | 106 (56%) | −68,65 | 931,35 | 29,66 (lordo −38,99) | — |
| **1 ott 08:15 ora italiana** (ops 0387-0389) | **204 (196 + 8)** | **116 (57%)** | **−70,82** | **929,18** | circa 31,07 (stima: lordo −39,75 meno netto −70,82) | — |

Confronto col mercato: −0,23% contro BTC +1,17% il 17 set (ops 0073); −6,9% contro +9,9% il 30 set
(ops 0358); **−7,08% contro BTC +11,37% al 1 ott** (ops 0389).

### 4.2 Giorno per giorno (ora italiana, ops 0387)

| giorno | PnL | giorno | PnL | giorno | PnL |
|---|---|---|---|---|---|
| 16 set | −4,19 | 21 set | −10,60 | 26 set | −14,49 |
| 17 set | +1,85 | 22 set | −2,44 | 27 set | +1,26 |
| 18 set | −4,20 | 23 set | −17,66 | 28 set | +8,06 |
| 19 set | −13,51 | 24 set | +1,17 | 29 set | −0,17 |
| 20 set | +2,01 | 25 set | −15,87 | 30 set | −2,18 |

* Somma 16-30 set: **−70,96** (stima mia: somma della tabella; il 1 ott vale +0,15 e il totale stampato
  è −70,81). Dal 16 al 26 set −77,93, dal 27 set +10,19 (revisione 30 set, ops 0371). Giorni in utile: 5
  su 15, in perdita 10 (diario r. 2369-2370).
* I trade delle validate per giorno (ora italiana, ops 0388): 1, 2, 6, 4, 6, 16, 2, 5, 11, 29, 21, 32, 21,
  23, 14 dal 16 al 30 set (somma 193, stima mia). Il salto dal 25 set viene dalle validate passate da 59 a
  160.
* Le giornate cambiano a seconda del conto: il 25 set vale −13,90 nel giorno UTC (ops 0267), −15,87 in
  ora italiana (ops 0387), +0,92 alla lettura delle 08:10 (ops 0232); il 27 set +3,25 sul conto e +1,26
  sulle sole validate (diario r. 2018-2025).

### 4.3 In R e contro il caso

* Su 157 trade con R calcolabile (dal 16 set al 1 ott): **−0,084R netti a trade**, −0,003R lordi, costi
  0,081R (ops 0388). Dal 27 set 19:40 UTC: **+0,042R netti su 61**, +0,118R lordi, costi 0,076R (ops 0388).
* Paper contro un prezzo casuale con le nostre uscite (revisione 30 set §4, simulazione ricalcolata dal
  revisore; ops 0360, 0366): stop 44% contro 46%; mfe mediana 0,87R contro 0,81R; primo target 11% contro
  17%; vinti 56% contro 54%; R medio −0,084 (±0,09) contro −0,067.
* Uscite al 30 set (diario r. 2170): 83 stop −236,68; 84 trailing +89,30; 19 scale-out +44,48. Il 25 set
  erano 31 stop −128,57 e 14 trailing +29,97 (ops 0227).
* Direzione al 1 ott (ops 0388): long 85 trade, 45 vinti, −33,97; short 111, 64 vinti, −39,82.
* Declassate contro attive (ops 0388): declassate 37 trade, R +0,041; attive 159 trade, R −0,123 (su
  120 con R). Esplorative: 8 chiuse, 7 vinte, +2,97 (ops 0388).

---

## 5. Errori, bug, incidenti e ipotesi sbagliate del mese

In ordine di data. Per ognuno: cosa, come si è visto, correzione, fonte.

1. **Il taglio della rivalutazione per anzianità** (13 set). Avrebbe congelato coppie a 2/3 quando le
   strategie note avessero superato 500. Corretto prima che mordesse (commit `a01b05cb`; diario r. 184-
   211).
2. **La potatura cancellava coppie con conferme** e **il flag `generated` si perdeva nell'alleggerimento**
   (14 set). Perdita attiva, non ricostruibile (controllo unico, punti 1-3). Nella stessa correzione un
   errore nuovo: un tempo dei dati confrontato con l'orologio del computer, trovato subito dai test
   (controllo unico, punto 5).
3. **L'universo che ruota congelava le coppie** (14 set; commit `f0bcbbec`).
4. **La soglia del paper letta male** (15 set): «manca una moneta», in realtà il 35% dell'universo.
   Corretto il 16 set (diario r. 496-519).
5. **`ready` deciso su numeri diversi da quelli che si leggevano** (16 set; commit `96196d43`).
6. **La raccomandazione di non abbassare l'asticella non è stata seguita** (16 set): il paper è partito
   con la via a conteggio, scelta del proprietario (`ops/requests/0063-ricalcola-ready.req`). Non è un
   bug; è il motivo per cui il paper ha operato dal 16 set coppie che la regola originale avrebbe
   ammesso solo dal 30 set (ops 0363).
7. **La protezione del profitto non si armava mai** (18 set): ancorata all'ultimo gradino, 0 trade oltre
   3R (diario r. 677-683). Cambiata il 21 set (A1).
8. **Registro a tre giorni dal limite di Firestore**; la difesa non era mai stata eseguita; la discovery
   disfaceva l'alleggerimento di optimize (19 set; commit `ecb99ab5`).
9. **La sonda dei segnali contava su candele da 1 ora** (19 set): «tutto torna» era falso; poi il
   divario «7 attesi contro 3» era un artefatto della media su giorni in cui il paper non girava (diario r.
   853-922).
10. **L'AI spenta per sei giorni senza che nessuno se ne accorgesse** (13-19 set): chiave rifiutata, il
    sistema proseguiva «senza AI» (fail-open) (diario r. 940-951). Si ripete il 23-24 set con un nome
    di modello inesistente (diario r. 1245-1248).
11. **Strumenti che inventavano scoperte** (21 set): «0/21 ingressi combaciano» (le date ISO valevano
    zero, commit `2ee8de44`); la sonda dello storico su 263 monete invece di 25 (commit `cc080d1c`);
    la regola sul rischio scritta al contrario nel backlog (commit `fad02496`).
12. **Il freno sul controtrend non frenava, la quarantena non c'era nel gate, le gemelle, il vocabolario
    che non sapeva dire «non vendere una salita verticale»** (21 set; commit `1d96dc3d`). «Tutte nel
    codice da luglio, nessuna letta.»
13. **La discovery non caricava BTC**: le strategie generate non vedevano il mercato (21 set; commit
    `c7033755`).
14. **Il giro sfora le 3 ore**, probabilmente per il contesto di mercato calcolato a ogni candela (22 set; commit
    `dead71b4`). **La copertura risultava 100%** per un denominatore collassato (22 set; commit
    `a083fdf8`).
15. **Lo stop a −15,3% su MUBARAK** perché l'ATR era gonfiato dal pump (23 set; commit `cf94be7d`).
16. **Il tetto per direzione scritto due volte** (24 set; audit, commit `eb0b992d`). Il diario e il commit
    dicono che la regola esisteva «dall'8 settembre»; nel git la variabile `MAX_DIRECTIONAL_RISK_PCT`
    nasce il 4 agosto (commit `ef73ba0b`) e nessun commit la tocca fra il 5 e il 10 settembre.
17. **Il freno di serie scattava per caso** e portava la size a un quarto insieme al freno globale (24
    set; spento, commit `eb0b992d`).
18. **Quattro giri del gate uccisi per memoria** dalle modifiche del giorno (24 set, 09-12-15-18 UTC;
    commit `f5620973`, `e9ce7a0d`, `29754c75`). La correzione «in locale bastava, sulla VPS no». Per
    rimettere in piedi il giro sono state **spente le varianti troncate**: da allora le varianti dai
    referti si giudicavano anche sulle perdite del paper che le avevano fatte nascere — contro la regola
    «il paper non si usa come training set» — finché non sono state spente il 2 ottobre (backlog B8,
    `docs/backlog.md` r. 315-319).
19. **Le bocciature non chiudevano la finestra** (fino al 24 set): 223 strategie «urgenti» per sempre e
    conferme già guadagnate mai registrate; correggerle ha fatto salire le validate da 59 a 160 in una
    notte (diario r. 1380-1387).
20. **«Il giro completo dura 1h09»** (25 set): era un giro urgenti; il completo non partiva da giorni
    per uno slittamento del timer (diario r. 1612-1618). La decisione di alzare l'intorno a 40 (diario r.
    1487-1506, `docs/disegno_cervello.md` r. 186) era presa su quel numero sbagliato.
21. **«Dal 16 settembre anche il simulato perde: è il mercato, non l'esecuzione»** (25 set, ops 0232;
    commit `f48e9e37` «H5 risolta»). Sbagliato: il simulato dipende da quali coppie sono validate quel
    giorno. Sugli stessi giorni −1.357 con le coppie del 25 set, +8.465 con quelle del 30 set (diario r.
    2199-2202). H5 riaperta il 30 set (commit `66be0761`).
22. **Il controllo orario si fermava dopo il primo giro** (25 set; commit `8e632b4b`), **il rischio
    effettivo si perdeva al riavvio** (25 set; commit `04147c7b`), **il contatore dell'ombra AI leggeva
    la chiave sbagliata** («0/60», commit `a1a67e81`).
23. **Tre rotture di parità a 1 ora** trovate prima che colpissero (26 set; diario r. 1682-1687).
24. **Il report dei rifiutati leggeva una frazione come percentuale** (−6,80R invece di −0,17R; 27 set;
    commit `aa6b89e5`).
25. **Il bot decideva sul prezzo vivo, il motore sulla chiusura** (27 set; commit `33caaf24`).
26. **Il mattoncino della sessione leggeva l'orologio del computer** (27 set; commit `6a846de4`). 47
    validate su 212 avevano guadagnato i passaggi con una regola valutata male (ops 0314); 347 coppie
    azzerate (ops 0324). Nota: il diario cita «commit 803a99f» (r. 1942), che è il commit delle richieste
    ops; la correzione del codice è `6a846de4`.
27. **L'analisi in sfondo moriva col servizio ops** (27 set; commit `a7aa299a`).
28. **Quota di letture Firestore esaurita** (28 set, 06:18 UTC; ops 0331, 0332; commit `76ffb8d0`).
29. **Due conti diversi della stessa giornata** (+3,25 contro +1,26 il 27 set; 28 set; commit
    `eb4a5ac0`).
30. **L'AI leggeva un segnaposto come misura** («scarto 0,000», 29 set; commit `fd58002c`); **e leggeva
    numeri fermi al 21 set** («su 1320 valutazioni ne passano 0», revisione 30 set §4 punto 7).
31. **Il filtro monete AI giudicava dal nome** (30 set; ops 0365): spento.
32. **La mediana della t delle validate saliva (1,47 → 2,23) solo perché la t si misurava sulle coppie
    che ripassavano**: le 42 misurate erano esattamente le 42 non declassate (revisione 30 set §2 punto
    2; ops 0363).
33. **Il «quarto di size» delle declassate quasi non agisce**: il fattore si applica prima del tetto per
    posizione; con uno stop dell'1,3% una declassata rischia lo 0,125% e un'attiva lo 0,130% (revisione
    30 set §4 punto 4, `risk_manager.py:139-148`, `main.py:1554-1566`).
34. **Il freno globale ha un'uscita che non si raggiunge** (per uscire la mfe mediana deve superare
    1,05R; paper 0,87R, motore 1,03R; revisione 30 set §2).
35. **La regola dei 40 trade non è mai stata applicata come scritta**: il 21 set, con 27 trade chiusi,
    l'uscita è cambiata (A1, decisione del proprietario) e i primi 24 trade sono stati dichiarati non
    confrontabili (diario r. 1033-1036); il 23 set, a 40 trade, si è aggiunto il «cervello» invece di
    leggere il verdetto (diario r. 1152-1185).

---

## 6. Cosa abbiamo capito, ed errori da non ripetere

### 6.1 Cosa abbiamo capito a settembre

1. **Il gate trova cose che si ripetono, ma molte sono biglietti vincenti di una lotteria.** La terza
   conferma arriva (0 → 202 validate in 16 giorni, ops 0054, 0363), però 167 validate su 182 non
   ripassano il gate pochi giorni dopo (diario r. 1725-1727) e una su otto passa una valutazione singola
   (ops 0290). La causa principale trovata: una finestra valeva come conferma con un solo passaggio su
   molte valutazioni (otto giri al giorno sugli stessi dati quasi identici).
2. **Il paper non ha mai mantenuto la promessa del gate.** PF vissuto fra 0,22 e 0,70 contro 1,88-2,10
   promesso per tutto il mese (diario r. 686, 1251, 1467, 1631, 1784, 2003, 2082). È esattamente il
   «segnale 2» scritto il 6 set (diario r. 106-111): validano ma il paper perde.
3. **Il bot esegue quasi come il motore.** Frequenza giusta (87-89%, diario r. 913-914, 1698), ingressi
   allineati all'81% dopo le correzioni (ops 0373), stessi segnali +0,05R contro +0,01R (ops 0371). Il
   problema sta prima del bot, nella scelta delle coppie (la selezione è confermata a ottobre; ma la
   lettura del 16 ott dice per la prima volta anche «è esecuzione», al limite e non confermata,
   `docs/letture.md`).
4. **Il paper ha la forma di un prezzo casuale con le nostre uscite** (revisione 30 set §4 punto 1).
   Quindi «sei stop su dieci erano andati a favore» e «88% senza primo target» descrivono le regole di
   uscita, non dicono dove intervenire. Nessuna regola d'uscita crea profitto su un prezzo senza
   vantaggio.
5. **Scale più lunghe vanno meglio**: 1 ora meglio di 15 minuti meglio di 5 minuti, su tutte le monete
   (ops 0060); passaggio a 1 ora da 2 a 5 volte quello a 15 minuti (stima: rapporti dei tassi del diario r. 2011, 2097, 2174, 2377). I costi
   pesano: 29,66 sui −68,65 al 30 set (diario r. 2166); 0,081R a trade (ops 0388).
6. **Le funzioni aggiunte non hanno mostrato un contributo**: selettore NON BATTE (ops 0368), freno di
   serie e per gruppo bocciati dai numeri (ops 0188, 0288), intorno e varianti 0 promosse (ops 0282-
   0284, diario r. 2733-2734), idee AI 0 validate su 103 (diario r. 2732), ombra AI non usata (diario r. 2310).
7. **I take profit non sono messi male: è il prezzo che non va lontano** (ops 0210, 0366).
8. **«Un totale non dice mai su cosa è stato calcolato»** (diario r. 576-577) e **«un numero giusto per
   un'altra domanda»** (diario r. 861): le due frasi del mese che riassumono metà degli errori.

### 6.2 Errori da non ripetere (soprattutto se si riscrive il gate)

1. **Un passaggio su molte valutazioni non è una conferma.** Il gate deve contare le prove
   indipendenti, non i tentativi: con otto giri al giorno sugli stessi dati, «almeno una volta in sette
   giorni» è una lotteria (ops 0290; commit `7b77b23b`, `aa6b89e5`).
2. **Ogni tetto, filtro o potatura deve dire quanto morde e non deve poter scartare in silenzio
   quello che si aspetta** (controllo unico). A settembre è successo con il taglio della rivalutazione,
   la potatura, la rotazione dell'universo, il registro vicino al limite, il giro completo che non
   partiva.
3. **Una sola copia di ogni regola, nel gate e nel bot.** Le divergenze del mese: quarantena (21 set),
   prezzo vivo contro chiusura (27 set), sessione con l'orologio del computer (27 set), tre rotture a 1
   ora (26 set), tetto per direzione scritto due volte (24 set), `_ts` copiato (21 set).
4. **Due orologi diversi sono un difetto.** Tempo dei dati contro orologio del computer (controllo unico
   punto 5; sessione J13); timer «a catena» contro una regola a orario fisso (26 set).
5. **Non cambiare la cosa misurata a metà misura**, e non abbassare l'asticella quando diventa
   raggiungibile (diario r. 535-539, 732-738). A settembre è successo comunque (punti 6 e 35 del cap. 5).
6. **Il paper non è un training set.** Anche indirettamente: le varianti giudicate sulle perdite che le
   hanno generate (cap. 5 punto 18).
7. **Verificare cosa misura lo strumento prima di leggere il numero**: scala (sonda a 1 ora), unità
   (frazione contro percentuale), date (ISO), denominatore (copertura al 100%), periodo (rifiutati e
   aperti su periodi diversi, diario r. 2384-2391), insieme di coppie (il simulato «è il mercato»).
8. **Il fail-open nasconde i guasti**: l'AI ha girato a vuoto per sei giorni (13-19 set) e poi per ore
   (23-24 set). Un pezzo che si spegne da solo deve suonare un allarme.
9. **Misurare in R, non in USDT**, e tagliare i periodi dei difetti (dal 27 set): le righe in USDT
   mescolano size piena, mezza e ridotta (revisione 30 set §4 punto 9).
10. **Le modifiche vanno provate sulla macchina vera prima di metterle nel giro**: quattro giri persi
    per memoria in un giorno (24 set).
11. **Troppe cose nuove in pochi giorni generano difetti nuovi**: in settembre +55.000 righe e la suite
    da 730 a 2.023 test (cap. 2.4); l'audit del 24 set su 4.400 righe di due giorni ha trovato una
    funzione duplicata e un freno che scattava per caso.
12. **Scrivere la regola di lettura prima dei numeri, e poi applicarla.** A fine mese lo si fa (K1, H1,
    regola del 3 ott: diario r. 2262-2316); a metà mese no (regola dei 40 trade).

### 6.3 Il gate a fine settembre, in poche righe (per chi lo riscrive)

Ricavato dalle fonti sopra; i numeri sono quelli del 30 set salvo dove indicato.

* Tre conferme in tre finestre di 7 giorni di dati; dal 27 set ogni finestra vale solo se la coppia
  passa più della metà delle valutazioni (commit `aa6b89e5`).
* Esame finale sugli ultimi 45 giorni con PF ≥ 1,05 su almeno 5 trade (diario r. 2111-2113); almeno 2
  finestre fuori campione su 3 e 365 giorni di storia (dall'agosto, `docs/audit_backtesting.md` punti 2
  e 4); stop più largo del 6% scartato (23 set).
* Una coppia viene tolta dopo due finestre fallite di fila (commit `57ff082c`; `PURGE_FAILS=2`,
  revisione 30 set §4 punto 2); declassata a un quarto dopo due bocciature in giri completi (26 set).
* `ready` per il paper: 35% dell'universo coperto oppure 10 coppie validate (ops 0363).
* Registro: un documento Firestore da al massimo 1 MiB, tetto 3.000 coppie (diario r. 815-816).
* Passaggio: circa 0,2% delle valutazioni a 15 minuti; validate 202 su 70 monete; 562 coppie a 2/3
  (ops 0363). Fuori campione, dopo la validazione, il motore fa circa zero (+0,12R su 117 il 30 set, ops
  0371; −0,05R su 230 il 7 ott, ops 0532).

---

## Appendice: cose incerte, fonti in disaccordo, cose non verificate

* **Tetto per direzione «dall'8 settembre»** (diario r. 1302, commit `eb0b992d`) contro il git, dove
  `MAX_DIRECTIONAL_RISK_PCT` nasce il 4 agosto (commit `ef73ba0b`). Non ho trovato commit che lo tocchino
  fra il 5 e il 10 settembre.
* **Commit della correzione della sessione**: il diario dice `803a99f` (r. 1942), che contiene solo due
  richieste ops; la correzione del codice è `6a846de4`.
* **Tetto per direzione nel portafoglio simulato**: ops 0184 dice PnL da +10.386 a +11.983 e drawdown
  invariato; il diario (r. 1284-1285) scrive «PnL e drawdown invariati». Ops 0188, dopo l'audit, dà
  +9.664 e drawdown 17,0%. Il diario per 0188 riporta i trade «saltati» (64, 44, 80), mentre la
  differenza netta dei trade aperti è minore (36, 33, 38: «Lettura» di ops 0188).
* **Giri uccisi per memoria il 24 set**: il diario ne racconta tre (r. 1336-1352, con orari che sembrano
  in ora italiana: «11:00 e 14:06»), il commit `29754c75` e il commento in
  `scripts/discover_strategies.py` (r. 1313-1318) ne contano quattro (09, 12, 15, 18 UTC).
* **J12**: 64 su 79 (ops 0373, diario r. 2318) contro 62 su 77 (ops 0371, revisione 30 set §2). Tutti e
  due danno circa l'81%.
* **Livello del grafico (A5)**: 3,96R e 2% (ops 0210), 4,04R e 2% (ops 0237), 3,35R e 7% (ops 0366): tre
  campioni diversi.
* **Giornate del paper**: 25 set −13,90 (UTC, ops 0267), −15,87 (ora italiana, ops 0387). Curiosamente i
  valori dal 16 al 24 set sono identici nelle due tabelle; non ho verificato perché.
* **Il 23 set (40 trade, −50,88)** viene da uno screenshot della dashboard citato nel diario, non da un
  risultato ops.
* **Quanti trade a fine settembre**: non c'è una fotografia al 30 set alle 24:00. Uso quella del 1 ott
  08:15 ora italiana (204 trade, −70,82, ops 0387-0389), che contiene già 3 trade del 1 ott; la somma dei
  giorni 16-30 set (−70,96) è una mia stima.
* **Win rate al 21, 24 e 25 set**: ricavati da me sommando long e short del diario (stima).
* **Chi ha deciso la via a conteggio**: lo dice la richiesta `ops/requests/0063-ricalcola-ready.req` («Il
  proprietario ha aggiunto OPTIMIZER_READY_MIN_PAIRS=10 al .env»); il diario non lo dice in chiaro.
* **Il «destino» delle modifiche** l'ho controllato solo sui valori predefiniti del codice di oggi, non
  sul `.env` della macchina (che non posso leggere). Dove ho scritto «non verificato» non ho cercato.
* **Il periodo 1-13 settembre** l'ho trattato in breve (diario r. 94-230 e ops 0030-0040): potrebbe
  sovrapporsi al capitolo precedente.
* La simulazione «senza vantaggio passa il 31% con 5 trade e il 37% con 10» (diario r. 2127) e quelle
  della revisione del 30 set non sono nel codice del repo: restano stime degli analisti.
