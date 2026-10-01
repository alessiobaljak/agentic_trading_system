# Backlog — cose emerse e rimandate

Elenco delle cose **trovate e NON fatte**, con il motivo per cui sono state
rimandate e cosa servirebbe per deciderle. Non è un piano: è una memoria, perché
finora questi punti vivevano solo dentro le conversazioni e sparivano.

**Regola d'ingresso:** ci si mette una voce quando si scopre qualcosa che vale la
pena valutare ma NON si fa subito. Con: cosa, perché rimandata, e il numero
misurato che l'ha fatta emergere. Senza il numero, una voce è un'opinione.

**Regola d'uscita:** si toglie quando è fatta (e finisce in `andremo_live.md` con
la misura) oppure quando si decide di non farla — scrivendo perché. Una voce che
sparisce senza verdetto è peggio di una voce mai scritta.

**Due vincoli che valgono per quasi tutto qui sotto:**

1. **Niente cambia le uscite prima dei 40 trade chiusi.** Al 23 set sono 40, ma la
   misura pulita è ripartita la sera del 21 (freno, cooldown, tetto per coin). Cambiare
   stop, obiettivi o size a metà misurazione rende i primi trade non confrontabili
   coi successivi, e il verdetto che aspettiamo da tre settimane sparisce.
2. **Tutto passa dal GATE, mai solo dal paper.** Una modifica applicata al paper e
   non al gate fa sì che il PF promesso descriva un sistema diverso da quello che
   opera. È la classe di problema che ha prodotto BIRBUSDT (1,51 promesso, 0,16
   vissuto).

---

**INDICE AL 1 OTT (dopo la pulizia: 44 voci; J1, J3, J4, J5 chiuse col verdetto nel diario).** Il dettaglio di ogni voce è più sotto.

| Stato | Voci | Cosa serve |
|---|---|---|
| **Aperte (15; K2, D6 e K8 compaiono anche in un'altra riga)** | K2 (spazio del registro), D6 (leve della spesa AI), D7 (modello del runner GitHub), E4 (strategie gemelle), K7 (dati sbagliati all'AI), K8 (conti in R, costi), G3 (voto minimo nel gate), G6 (recenza nell'approvazione), B8 (varianti giudicate senza il paper), C4 (annunci USA), I4bis, I5, J15, D1, D5 | vedi ogni voce: chi decide e quando |
| **In misura (21)** — si leggono da sole | 1 ott: J14 (letture Firebase), D6 (primo giorno intero di spesa) · 3 ott: A4 (declassate contro attive) · 7 ott: H5, K1 (selezione o esecuzione) · ~10 ott: J7, J9, I4ter · ~14-15 ott: H5 (rilettura), K3 (gruppo di controllo) · ~18 ott: J11, J13, C1 · ~26 ott: J6 · metà nov: K2 (regola H1) · senza data: F1bis (100 trade esplorativi), F1ter (selettore), I1 (panchina), I3, I4 (trailing), J8, J10, E1 | niente: leggere il numero alla data |
| **Scoperte da ricordare (4)** | K4 (il paper ha la firma del caso), K5 (il quarto di size non agisce), K6 (uscita del freno irraggiungibile), K8 (costi e scivolamento: prima di soldi veri) | prima di un passaggio a soldi veri |
| **Parcheggiate dal proprietario (6)** | B5, B6, B7 (dati esterni), H3 (stop giornaliero), H4 (freno di serie), J2 | solo se il proprietario le riprende |

**Stato al 30 set (rilettura completa delle 70 voci, verificata contro i risultati ops).**
Conteggio dopo la pulizia del 30 set (62 voci; F2 e J12 chiuse la sera del 30 set, verdetto nel
diario), H5 fatta il 30 set e in misura fino al 7 ott, 18 in
misura, 11 fatte in parte, 14 aperte, 6 parcheggiate, 12 fatte (restano come memoria finché non si
decide di spostarle nel diario). Stati che il testo delle voci non dice ancora:
* **H5 riaperta, ma il numero del `portafoglio` non la decide:** il 25 set «è il mercato» (ops 0232),
  il 28-29 set «è esecuzione» (+7.190 e +9.596 simulati contro −69 e −67 del paper, ops 0328, 0339).
  Sugli STESSI giorni 16-24 set il simulato fa −1.357 con le 160 coppie del 25 set e +8.465 con le
  202 di oggi (somme dal controllo del 30 set): cambia solo l'insieme di coppie, scelte anche su
  quei giorni. Quel confronto misura la selezione, non l'esecuzione. (Corretto il 30 set: la prima
  stesura diceva «troppo grande per essere solo quello», senza base.) Serve il confronto FUORI
  CAMPIONE: proposta del 30 set nel diario.
* **I5 in calo, non peggiorata:** 137 su 212 il 27 set (ops 0300) → 131 → 125 → 124 su 202 il 30 set
  (ops 0358). La correzione (`scripts/optimize.py:610`) è del 26 set sera, non del 25, e funziona per
  le nuove promosse; restano le vecchie validate, per lo più declassate, che non ripassano.
  (Corretto il 30 set: la prima stesura confrontava con 72 su 131 del 25 set.)
* **B4 sbloccata:** la lettura AI dei referti aspettava 100 trade: sono 174 (ops 0340).
* **F1 / F1ter:** 96 trade col voto del selettore (ops 0340), sopra i 40 richiesti; il voto non
  distingue (0,653 vinti contro 0,644 persi) e il selettore non batte «apri tutto» (ops 0348).
* **H1:** il numero che si aspettava c'è (26 validate su 42 con t ≥ 2, mediana 2,23, ops 0363),
  ma la misura esiste solo per 42 validate su 202: `last_t` non è nel nucleo del registro
  (`scripts/optimize.py:572-628`; scritto solo a `discover_strategies.py:2615-2616`) e si perde
  prima della promozione. Finché non ci entra, H1 non si può decidere.
* **C1:** a 1 ora passa lo 0,32% il 27, 0,69% il 28, 1,15% il 29 set, contro 0,22% a 15 minuti;
  la passata copre 19-21 monete, non 30.
* **Tolte il 30 set** (sì del proprietario: «aggiorna il backlog rimuovendo le scartate»; il
  verdetto di ognuna è nel diario, sezione «Voci tolte dal backlog il 30 set»): A5, C2, C3, D4,
  I7, I8.
* **Numeri vecchi:** D1 (registro 399 KiB su 879, 278 byte a coppia, ops 0343), I2 (PF atteso
  2,04, non 1,89), J10 (primo giro completo ridotto ~1h45, sopra l'1h30 voluto; stima dal log).

---

## K. Revisione delle voci in sospeso (30 set) — scoperte nuove e verdetti

Revisione completa in `docs/revisione_sospese_30set.md` (7 analisti con verifica su codice,
conti e simulazioni; un critico statistico e uno da trader; sintesi). Richiesta del proprietario:
«fai una revisione di quelle proposte per capire cosa davvero serve per migliorare il nostro
modello». Nessuna voce è stata fatta: aspettano il sì.

### K1. Regole delle letture del 3, 7 e 14 ott, scritte prima (proposta: serve adesso)
**30 set: FATTO (sì del proprietario), regole scritte nel diario prima delle letture.** In `portafoglio` (FUORI CAMPIONE) e in `trades` (DECLASSATE). Dettaglio nel diario del 30 set.
**30 set sera, revisione avversaria di A (e correzioni fedeli alla regola, soglie invariate):** la
selezione dice «non si decide» se il diario delle vite non si legge (prima usciva un verdetto senza
le coppie rimosse); «oltre il margine» = strettamente maggiore anche per l'esecuzione; abbinamenti
paper/motore nello stesso verso; inizio della coppia rimossa ricavato dalla «rimossa» se la
«promossa» è caduta dal diario (tetto 500 eventi). Restano: (a) un trade dello stesso verso alla
barra dopo può «rubare» l'abbinamento a quello giusto (raro, non corretto); (b) **contare gli eventi
del diario delle vite prima del 7 ott** (se vicini a 500, alzare `GATE_LIFECYCLE_MAX`); (c) la regola
del 3 ott non ha un minimo di trade per lato: aggiungerlo ora, dopo aver visto 28 contro 22, vorrebbe
dire cambiarla — decide il proprietario.
Il verdetto «è il bot che esegue male» del 7 ott oggi si decide sulla media di tutti i trade (margine
±0,25R); sugli stessi segnali il margine è ±0,16R e la differenza +0,04R (ops 0371). Pacchetto:
riga «stessi segnali» per il verdetto sul bot con almeno 30 trade accoppiati, conteggio unico dei
segnali (le gemelle contano doppio nel motore), margine per giornata, segnali non presi confrontati
col portafoglio del motore (anche lui apre 995 segnali su 2.203), due righe per le coppie uscite
(sopravvivenza: dall'8 ott circa le prime rimozioni rendono il motore più ottimista), regola del
3 ott («uguale» solo se il margine esclude ±0,15R). ~1 giorno, nessun riavvio.

### K2. H1-misura: salvare la t di ogni validata e dividere il fuori campione per t (serve adesso)
**30 set sera: REGOLA H1 DECISA dal proprietario, prima della prima lettura divisa per t** («H1:
ultimo esame, soglia 1,5, minimo 80: sì»): decide solo la t dell'ultimo esame (holdout di 45
giorni), soglia 1,5; con almeno 80 segnali per gruppo: t alta sopra t bassa oltre il margine →
H1-soglia sull'holdout è la prossima proposta; differenza + margine sotto 0,25R → H1 chiusa;
altrimenti non si sa ancora (si rilegge a metà novembre). Nel report: `REGOLA_H1_DECISA`,
`lettura_h1`. Passata del voto t fatta il 30 set (ops 0383): 213 coppie in 647 s; t del gate ≥ 2 in
47 su 213 (mediana 1,27); t dell'ultimo esame ≥ 2 in 18 su 183 con almeno 5 trade.
**30 set: FATTO (sì del proprietario), revisione avversaria + correzioni + riverifica.** La t
(walk-forward e holdout, coi trade) entra nel nucleo del registro (nomi brevi t, n, h, o) e si FISSA
alla promozione (`val_t`, `val_trades`, `val_t_holdout`, `val_trades_holdout`, `val_uscita`: un
ripasso non li cambia). La passata una tantum `scripts/t_validate.py` (voci ops `voto-t-completo`
in sfondo e `voto-t-esito`, da aggiungere a mano sulla VPS) calcola la t di tutte le validate sui
dati TAGLIATI al giorno della loro validazione, non scrive Firebase (file locale
`data/voto_t/validate.json`), ha un lucchetto del kernel, salva dopo ogni coin, non parte se il gate
gira o parte entro 40 minuti e ricontrolla prima di ogni coin, gira a priorità bassa. Il portafoglio
divide il FUORI CAMPIONE per t (un segnale conta in un solo gruppo). Verificato: 252 valutazioni del
gate identiche prima e dopo; merge identici salvo i campi t; registro nuovo leggibile dal codice
vecchio. Durata non misurata sulla VPS (~33 s per coin per giorno di validazione diverso, su dati
sintetici). **Da decidere prima del 7 ott (proprietario): la regola H1** — quale t decide
(walk-forward o holdout), soglia (2 o 1,5), minimo di segnali per gruppo (proposta 80), esiti
(proposta / chiusa se differenza + margine < 0,25R / non si sa ancora). Attesa realistica: la
differenza stimata è piccola (+0,03/+0,09R): al 14 ott l'esito più probabile è «non si vede», da non
leggere come «H1 smentita». **Avvertenza sul registro:** coi campi t la capienza scende da ~3.180 a
~2.700 coppie (a ~50 coppie in più al giorno, fra ~3 settimane); oltre, scatta l'alleggerimento
d'emergenza a ogni giro e le validate perdono `regime_pf` (il veto di regime lascerebbe passare
tutto). Rimedio pronto da decidere prima: campi t nel nucleo solo per le coppie a 2+ conferme
(capienza ~2.880) oppure tetto a ~2.600 coppie. Da controllare la riga «ci stanno ancora ~N coppie»
di `gate`.
La t c'è solo per le 42 validate NON declassate (202 − 160, ops 0363): si scrive solo quando una
coppia ripassa. Serve il campo nel nucleo del registro e una passata una tantum sulle 202 (15-17
minuti di VPS: voce ops in sfondo, riga nuova nella lista bianca da aggiungere a mano). In
simulazione una t minima all'ultimo esame separa davvero le buone dalle fortunate (rapporto da 3,0 a
5,4 con t ≥ 1,5), ma costa ~70% delle nuove validate: prima si guarda se sui dati veri la t prevede.

### K3. Gruppo di controllo del fuori campione, da raccogliere da subito (serve adesso)
**30 set: RACCOLTA ACCESA (sì del proprietario).** `scripts/gruppo_controllo.py`, chiamato dalla
discovery a ogni giro (15 minuti e passata a 1 ora): ~50 bocciate a caso con almeno 30 trade e la
spec intera (generatore casuale separato, seme salvato: verdetti e ordine del giro identici) in
`data/gruppo_controllo/AAAA-MM-GG_bocciate.jsonl`, e al primo giro di ogni giorno italiano la foto
delle conferme di tutto il registro in `..._conferme.jsonl`. File locali sulla VPS (~1,1-1,5 MB al
giorno, rotazione 120 giorni, tetto 300 MB), zero letture Firebase. Resta da fare dopo il 7 ott: il
rigioco (voce ops in sfondo) con le regole da scrivere prima: configurazione d'uscita con cui
rigiocare, gruppo fissato alla prima foto, solo trade dopo `data_end`, margine per giornata.
**30 set sera, revisione avversaria di C e correzioni:** la raccolta non cambia il giro (discovery
vera lanciata con e senza: identica) e i record si rigiocano esattamente (106 su 106, poi 37 su 37
col solo record «giro»). Aggiunti: una riga «giro» con commit, impostazioni del motore e le 15 soglie
GATE_* (formato 2: le righe del formato 1, raccolte il 30 set pomeriggio, si ricostruiscono solo in
modo approssimato); l'elenco compresso delle idonee a ogni giro (~125 KiB, 21 giorni) per rifare
l'estrazione col seme; il file delle spec del giorno (le spec possono sparire da Firebase); `params`
per le coppie base; timeframe None se la spec manca; foto con creazione esclusiva e giorno di inizio
giro; numeri del .env letti senza far fallire l'import. **Regole dell'analisi (scritte prima dei
numeri, in testa a `scripts/gruppo_controllo.py` e in `docs/revisione_sospese_30set.md`):** separare
sempre 15 minuti e 1 ora (la quota di 50 a giro rende una bocciata a 1 ora ~9 volte più probabile);
gruppo fissato alla prima foto; solo trade dopo `data_end`; margine per giornata. **Trovati, non
fatti:** `rebuild_clean.sh` azzera le spec su Firebase senza copia; la lettura dei numeri dal .env
con int()/float() all'import può far fallire l'avvio in tutto il repo (corretto solo in
`gruppo_controllo`).
H5 dice se le validate guadagnano DOPO essere state scelte, non PERCHÉ scelte. Raccolta: ~50
candidate bocciate a giro (a caso, con almeno 30 trade) e una foto giornaliera delle conferme;
dopo 14 giorni il motore le rigioca per gruppo (validate, 2 conferme, 1 conferma, bocciate).
Risponde anche a «servono 3 conferme?» (F2) in ~15 giorni.

### K4. I numeri del paper hanno la firma del caso
Prezzo casuale con le nostre uscite contro il paper: stop 46% contro 44%, stop d'ingresso/uscita
48,5/51,5% contro 47/52%, massimo toccato mediano 0,81R contro 0,87R, vinti 54% contro 56%, R medio
−0,067 contro −0,084 ±0,09 (simulazione del 30 set su ops 0360, 0366). Le classi «ingresso/uscita»
e «88% senza primo target» sono la forma delle regole d'uscita, non una diagnosi: le proposte
basate solo su quelle classi vanno fermate.

### K5. Il «quarto di size» di declassate ed esplorative quasi non agisce
Il fattore riduce il rischio richiesto PRIMA del tetto per posizione (`bot/main.py:1555`,
`risk_manager.py:139-148`); con gli stop tipici il tetto del 10% taglia comunque, e declassata e
attiva finiscono quasi uguali (es. stop 1,3%: 0,125% contro 0,130% di rischio). Il controllo scrive
«size ridotta»: non è vero. Non tocca ciò che si impara (tutto in R), ma chi volesse ridurre il
danno delle coppie deboli deve sapere che oggi questa manopola non lo fa.

### K6. Il freno globale ha un'uscita irraggiungibile (I2-bis)
Per uscire serve anche un massimo toccato mediano sopra 1,05R: il paper è a 0,87R (ops 0366), il
motore che guadagna a 1,03R (ops 0371), un prezzo casuale a 0,81R. La condizione scatta con e
senza vantaggio: non dice niente. Da sistemare prima di qualunque discorso di denaro vero.

### K7. L'AI riceve numeri sbagliati
Oltre allo «scarto 0,000» (H2): a ogni giro legge «su 1320 valutazioni ne passano 0», fermo al 21
set (oggi 24.503 valutazioni, 48 passate, ops 0363); il giro a 15 minuti legge l'autopsia della
passata a 1 ora credendola sua (ops 0345, 0372).

### K8. Righe in USDT che portano fuori strada, costi e scivolamento
«Regime neutro −58,30», long/short e i conti per strategia mescolano size diverse e il periodo del
difetto della sessione (fino al 26 set −77,93, dal 27 set +10,19, ops 0371): vanno rifatti in R col
taglio al 27 set. I costi pesano 29,66 sui −68,65; motore e paper chiudono lo stop al suo prezzo
esatto, senza scivolamento (`executor.py:549-563`): da verificare prima del denaro vero.

### K9. I pesi riportano la leva a 2x dopo una sola vincita (trovato il 1 ott)
Verifica del 1 ott (richiesta del proprietario: «il sistema può solo fare modifiche per guadagnare di
più?»). `adaptation.py:210-228`, `risk_manager.py:65, 93, 149`, `metrics.py:485` (shrinkage k=5,
prior 0,65): con peso > 0,80 la strategia torna a leva piena; ci si arriva con 1 vinta su 1, o 1
vinta e 1 persa. Il rischio raddoppia quando morde il tetto del 10% (equity × leva × 10%). Il 1 ott
MITO e TST erano a leva 2,0x (docs/state.md). È fortuna amplificata e non passa dal gate. **Da
decidere dopo le letture del 7-14 ott** (tocca la size): per esempio un minimo di trade prima che il
peso alzi la leva. Correzione allo stesso giro: la pausa dopo 3 stop di fila è SPENTA in parità
(`bot/main.py:1338`), non attiva come scritto in I1.

### K10. Il supervisore ha allentato una soglia del gate e non l'ha mai rimessa (trovato il 1 ott)
`GATE_WIN_RATE_FLOOR` è scesa da 0,45 a 0,3966 (tra il 19 ago e l'8 set) per decisione del
supervisore automatico (`bot/learning/supervisor.py`, scritta in `tuning.env`, caricato con override:
`bot/config.py:35`, usata in `backtesting/engine.py:408`); dal 16 set il supervisore è fermo («ready»,
`supervisor.py:264-269`) ma la soglia allentata resta. Più strategie passano, non necessariamente
migliori. **Da fare (sola lettura, nessun rischio):** contare quante validate oggi esistono SOLO
grazie alla soglia a 0,397 (win rate fra 0,397 e 0,45) e come rendono fuori campione. Rimetterla a
0,45 è una modifica del gate: dopo il 7-14 ott, col numero. Nota: `backlog.md` diceva che il
supervisore regola `DECISION_THRESHOLD`: sbagliato, regola le soglie `GATE_*`.
Precisazione a K5: con stop larghi il quarto di size agisce davvero (PHA del 1 ott, stop ~4,3%: rischio
da ~0,40% a ~0,14%, stima); «quasi non agisce» vale con stop stretti a leva 1x.

### Verdetti della revisione sulle voci esistenti — APPLICATI il 1 ott (voci tolte, verdetto nel diario)
Non servono: F2 (70-77% delle coppie a 1-2 conferme non ripassa; il quarto di size non limita il
danno, K5; la domanda la risolve K3), FR-leva (il −0,23R viene dal periodo del difetto), H1 con
t ≥ 3 sulle finestre, H2 seconda metà, I9, A3, E4-adx (ADX ultima su 18 variabili, ops 0368), B4,
B1 (a 1 ora lo stesso vocabolario passa 0,94% contro 0,20%: il limite sono i costi), I2 (spegnere
il freno non cambia nessun R), I6 (il tetto toglierebbe trade in ordine d'arrivo, non i peggiori),
D6-L2. Scelte del proprietario: filtro monete AI (spegnere, dare i dati, lasciare), ombra AI.
J12: l'obiettivo «80% dei trade del paper con un ingresso del motore vicino» è all'81% (62 su 77,
ops 0371): da chiudere se il proprietario è d'accordo. Dopo il 7 ott: H1-soglia sull'holdout,
conti in R, riga «caso» nel controllo, pulizia dei dati all'AI, D6-IPOTESI (contare le coppie per
origine), I6-misura, E4-gemelle.

## A. Uscite — dopo il verdetto dei 40 trade

### A4. Quanto vive una strategia validata — la prova non si distrugge più
**Stato:** **misura avviata il 21 set** · risposta fra qualche settimana

**26 set (passo 2 del piano del 26 set 15:xx): le DECLASSATE.** Il numero: al primo giro completo vero (26 set, ops 0282-0284) 167 validate su 182 non hanno passato il gate sui dati aggiornati, e fino alla chiusura della finestra (7 giorni) più due finestre di purga il bot le operava a size piena. Il proprietario non vuole tetti sul numero di trade, quindi non «sospese» ma **declassate**: nel merge del giro COMPLETO (`scripts/discover_strategies.py::aggiorna_declassate`) una validata passata oggi torna a `bocciata_notti = 0`, `declassata = false`; bocciata oggi `bocciata_notti += 1`, e alla seconda notte di fila (`DECLASSATA_NOTTI` = 2, dichiarato in `bot/config.py`) `declassata = true` con `declassata_at`. Mai pass_count, finestre o purga: la storia decide come prima. Il bot (`adaptation.is_declassata`, letto a ogni ricarica del registro) le opera a `DECLASSATA_SIZE_MULT` = 0,25 della size, applicato una volta sola in `_try_open` (col fattore esplorativa vale il minimo, mai il prodotto), riga `[declassata]` nel log, marca sul trade chiuso e sulla posizione (sopravvive al riavvio). Insieme: ogni validata è ora giudicata sulla PROPRIA configurazione d'uscita (scala/BE/keep di `last_params`, `config_iniziale` in `evaluate_spec`), non su quella globale; una configurazione globale la sostituisce solo se la batte di ≥ 10% (`DISCOVERY_CONFIG_MARGINE`); `giro.passate_solo_con_propria_config` conta chi passa solo grazie alla sua. Visibile in `gate` (riga DECLASSATE), `trades` (sezione DECLASSATE contro ATTIVE), controllo `paper.declassate`, doc del gate `registro.declassate`. I tre campi sono nel nucleo `REGISTRY_CORE_FIELDS` (sopravvivono anche all'alleggerimento d'emergenza). **Metro:** PF vissuto e R medio delle declassate contro le attive nei 7 giorni dopo la prima declassata (`trades`): se le declassate fanno peggio, il gate aveva ragione e si può proporre la sospensione vera; se fanno uguale, il gate sui dati recenti non discrimina e la soglia delle 2 notti va ripensata — con un numero, non prima. Non verificato dal vivo: il primo `[cervello] declassate` nel log del prossimo giro completo, il costo del passo 4 di `evaluate_spec` (≤ 1 backtest per validata che passa con config ≠ globale).

Domanda del proprietario: *«la strategia è costruita per passare quei 4 anni circa
più quelle settimane che aggiungiamo, ma ora il mercato è diverso e lo sarà sempre.
Non credo che questa strategia possa valere per i prossimi 3 anni.»*

Ha ragione, e il sistema in parte lo sa già: una coppia validata **non è
permanente**. Ogni 7 giorni di dati nuovi prende una conferma o un fallimento
(`judge_window`), e dopo **due finestre fallite di fila** viene rimossa
(`OPTIMIZER_PURGE_FAILS=2`, `scripts/optimize.py:878`). L'holdout di 45 giorni
scorre in avanti col tempo, quindi una strategia deve continuare a funzionare su
dati recenti che non ha mai visto. Non cerchiamo una strategia che duri tre anni:
teniamo viva una **popolazione**, e i singoli muoiono.

**Il buco:** non abbiamo MAI misurato quanto dura un individuo, e non possiamo,
perché la prova viene cancellata nel momento in cui nasce. Il purge stampa

```
[registry] AUTO-PURGE: rimosse N coppie (fallite 2+ finestre di fila)
```

nel journal e poi elimina il record. Il journal scorre via in poche ore (ci è già
costato tre diagnosi), e il registro contiene solo i **sopravvissuti** — lo stesso
bias di sopravvivenza che `scripts/survivorship_report.py` misura sulle coin,
rientrato dalla porta di servizio sulle strategie.

Quindi oggi a *«quanto vive una strategia validata?»* si può solo rispondere «non
lo so», che è esattamente la risposta che la sua domanda non può accettare.

**FATTO il 21 set** (`registra_vite` in `scripts/optimize.py`, documento
`gate_history/lifecycle`). A ogni promozione e a ogni rimozione si scrive una riga
durevole: chiave, `pass_count`, `fail_count`, PF, giorni vissuti, e se la coppia
era in deriva dal paper. La riga si scrive **prima** della cancellazione — dopo, il
record non esiste più.

Non tocca l'esperimento: non promuove, non rimuove, non cambia una size. È un
diario, `best-effort`, tagliato a 500 righe come la timeline.

**Una cosa che NON fa, di proposito:** dare una data di nascita alle coppie già
validate. Al momento del rilascio ce n'erano 56: scrivergli `validated_at = adesso`
avrebbe fabbricato 56 età false, tutte corte, e la vita mediana sarebbe risultata
più breve del vero proprio nel primo mese di misura. Escono con
`vissuta_giorni = None`, che è «non lo so». **Quindi la risposta arriva dalle
coppie promosse da qui in avanti, non da domani.**

**Poi, solo dopo:** chiedersi se il gate premi strategie legate a un regime. Oggi
valida su 4,6 anni **come un blocco unico** (con walk-forward a 3 blocchi OOS, che
mitiga ma non elimina): una strategia che funziona solo in mercato toro può passare
se i periodi toro pesano abbastanza. Nessuno ha mai chiesto *«sarebbe passata nel
2022? nel 2023? nel 2024?»* separatamente. `scripts/edge_stability.py` (allowlist
`edge`) confronta vecchio vs recente ed è il mattone più vicino, ma non è la stessa
domanda.

---

## B. Ricerca — dove il sistema smette di cercare

### B5. Notizie e dati macro
**Stato:** rimandata alla **sessione dedicata ai dati esterni** (decisione del 23 set) · aperto · ricerca fatta il 20 set (30 agenti, 23 candidati, 8 confermati)

Non esistono nel sistema: le strategie vedono solo prezzo e volume. **Il problema
non è leggerle, è validarle** — serve l'archivio STORICO allineato al minuto,
altrimenti il gate non può testarle.

**Cosa è stato verificato (e cosa no).** La ricerca ha girato da una rete che
blocca quasi tutti i domini dei fornitori: LunarCrush, CoinGecko, FRED, Dune,
ForexFactory, DefiLlama, Alpha Vantage. Letti DIRETTAMENTE solo: il README del
server MCP LunarCrush su GitHub, la pagina prezzi di BigQuery, i file S3 di
Binance Vision. Il resto è marcato come non verificato ed è da ricontrollare da
una rete non filtrata prima di costruirci sopra.

**Piani gratuiti che NON esistono più** (tutti verificati, tutti chiusi nel 2026):

| fonte | stato |
|---|---|
| CryptoPanic | piano Developer gratuito dismesso a inizio 2026 |
| CryptoCompare / CoinDesk Data | gratuito chiuso il 21 maggio 2026 |
| Dune Analytics | dal **10 settembre 2026** il free è in sola lettura: non esegue query |
| CoinGecko | storico gratuito fermo a 365 giorni; per il 2022 serve il piano da **129 $/mese** |
| Santiment free | 1 anno di storico **con gli ultimi 30 giorni tagliati**: backtestabile ma non operabile |

**LunarCrush: no.** Il server MCP ufficiale esiste ma usa la **stessa chiave**
della REST (`Authorization: Bearer <LUNARCRUSH_API_KEY>`, README letto) e la nostra
risponde **402** da tre misure indipendenti. Il prezzo attuale non è verificabile
da qui: si sa che la chiave che abbiamo non funziona e che l'MCP ne richiede una.

**GDELT** resta l'unica vera fonte di notizie con storico gratuito (tono e volume
ogni 15 minuti dal 2015, file bulk ri-scaricabili, nessuna chiave). Riserve:
domini bloccati quindi non provato di persona; è rumore macro mondiale, non
notizie crypto; e **BigQuery non basta gratis** — il tetto è 1 TiB/mese
(verificato) ma una passata 2022→oggi ne consuma ~1,68 TiB.

**Il passo a costo zero che viene PRIMA di tutto.** Esiste su Hugging Face un
dataset gratuito con ~5 anni di notizie crypto con orario (ott 2019 → feb 2025,
verificato leggendo il CSV). Non alimenta la produzione, ma permette di misurare
**se le notizie hanno un qualche edge sulle nostre coppie**. Se la risposta è no,
ogni abbonamento è risparmiato. Licenza CC-BY-NC, qualità bassa (contiene
comunicati sponsorizzati).

### B6. Lo storico di open interest e long/short: già gratis, mai usato
**Stato:** rimandata alla **sessione dedicata ai dati esterni** (decisione del 23 set) · aperto · **la raccomandazione numero uno** · verificato con le mani 20 set

Binance pubblica in file scaricabili le STESSE grandezze che oggi leggiamo solo
dal vivo: open interest, long/short ratio dei top trader, taker buy/sell ratio.

Misurato davvero, non stimato:

```
download anonimo, senza chiave: 25 file in parallelo → 25× HTTP 200 in 1,1s
granularità 5 minuti · 288 righe al giorno · checksum SHA256 corretti
BTCUSDT dal 2020-09-01 · ETH/BNB/XRP/DOGE dal 2021-12-01 · fino a ieri
s3-ap-northeast-1.amazonaws.com/data.binance.vision  prefix=data/futures/um/daily/metrics/
```

**Perché è il candidato migliore:** è la *stessa fonte* che il bot usa già in
produzione, quindi ricerca e live non possono disallinearsi. L'endpoint REST tiene
solo 30 giorni ed è per questo che quei dati non sono mai entrati nel gate: questo
dataset toglie esattamente quel muro.

Trappole verificate, da scrivere nel codice:
* esistono solo file **giornalieri** (i mensili non ci sono): su tutte le coppie
  sarebbero ~850.000 file → farlo solo sulle 25 coppie validate;
* i file recenti **non sono ordinati** per orario: riordinare dopo il parsing;
* i file del 2020/inizio 2021 hanno ogni riga **duplicata**;
* usare l'origine S3, non l'hostname `data.binance.vision` (già fatto così in
  `scripts/survivorship_report.py:40`);
* è un dataset **non documentato** nel README di Binance: può cambiare senza
  preavviso.

**Primo passo FATTO il 20 set** — `scripts/binance_metrics_probe.py` (lettore in
`backtesting/metrics_loader.py`, allowlist `storico-oi`). Misurato sulle 25
coppie validate, finestra 2022-01-01 → 2026-09-19:

```
coppie con dati dal 2022-01-01:   3 su 25   (DOT, EGLD, VET)
coppie con dati (anche recenti): 25 su 25
peso compresso, tutta la finestra: 221 MiB · 20.926 file da ~11 KiB
scompattato, proiezione dal campione: ~676 MiB (×3,1)
giorni mancanti nello storico: 1 solo (STXUSDT 2023-12-08) su 20.926
```

Le tre trappole del contenuto sono nel lettore e nei test
(`tests/test_storico_metrics.py`): righe non ordinate, righe doppie nel 2020/21,
checksum SHA256 verificato a ogni download.

**Cosa dice il numero, e perché la feature resta ferma.** Solo 3 coppie su 25
hanno storico dal 2022: le altre 22 sono coin quotate fra il 2023 e il 2025. Una
feature costruita su questi dati **non potrebbe essere validata sulla stessa
finestra del gate** — 22 coppie avrebbero l'indicatore vuoto per la maggior
parte dei 4,6 anni, e il walk-forward a 4 blocchi non avrebbe dati nei primi
blocchi. Non è un difetto della fonte: è che la fonte esiste da prima delle coin,
non delle coin da prima della fonte.

Restano due strade, nessuna delle due da aprire adesso:
* usare la finestra **corta** (dal listing di ogni coin) e accettare meno blocchi
  OOS — cioè meno severità, proprio dove il GATE 1 è tutta la difesa;
* tenerli come **tilt di size dal vivo**, come già fanno trend e sentiment, senza
  passare dal gate. Costa poco e non tocca la validazione.

221 MiB compressi sono un peso accettabile per la VPS; il problema non è lo
spazio, è la copertura. **Decisione rimandata a dopo i 40 trade del paper.**

### B7. Registrare noi lo storico da oggi — non è "una riga di codice"
**Stato:** rimandata alla **sessione dedicata ai dati esterni** (decisione del 23 set) · aperto · emerso 20 set

Sembra la soluzione ovvia e non lo è. Oggi non registriamo nulla
(`bot/execution/executor.py:184` salva il sentiment solo dentro il singolo trade),
il gratuito di CoinGecko non regge un polling continuo (lo dice il repo stesso in
`bot/agents/market_scanner.py:166`), **23 delle 25 coppie validate non hanno
nemmeno un id CoinGecko**, e soprattutto il backtest consuma **solo candele**
(`bot/core/indicators.py:119`): non esiste un canale per una serie esterna.

**Serve:** prima costruire il canale nel backtest, poi cominciare a registrare.

---

### B8. Una strategia generata non può essere RITARATA: può solo morire
**Stato:** **prima metà FATTA il 23 set pomeriggio** — le VARIANTI DAI REFERTI: quando i referti del paper scattano su una regola dichiarata (short tutte perse → «solo long»; perdite controtrend o mai andate a favore → «con conferma a 1 ora»; stop larghi → «stop più stretto»), la discovery genera la variante della STESSA spec (`bot/strategies/generator.py::varianti_da_referto`, `scripts/discover_strategies.py::varianti_dai_referti`) e la mette nel gate al posto di altrettante candidate casuali: stesse 3 conferme, stesso holdout, il giro non si allunga. Il paper propone, la storia decide. La variante porta `genitore` e `origine=referto`, così si vede da dove viene. **Dal 24 set sera (audit):** la variante DOVREBBE valutarsi solo su dati precedenti al primo trade del paper che ha fatto nascere l'ipotesi (`ipotesi_da`: pre-registrazione) — **ma dal 24 set alle 20:18 questa valutazione «troncata» è SPENTA** (`DISCOVERY_VARIANTI_TRONCATE=false`): raddoppiava la memoria dei worker e ha ucciso quattro giri; si riaccende quando si misura che il picco per worker (2,3 GB con 6 worker, ops 0225) lascia margine. Finché è spenta le figlie si giudicano sui dati interi, che contengono le perdite del paper che le hanno generate: limite noto. La variante non nasce se il gate ha già misurato che il lato da spegnere rende (PF ≥ 1 su ≥ 20 trade OOS, `direzione_pf`), e quando è validata sostituisce la madre (`sostituita_da`), altrimenti validarla non cambiava un trade. **Dal 24 set le tre conferme si raccolgono nello stesso giro** (`conferme_retroattive`: dati fino a oggi, a 8 e a 16 giorni fa; passa tutte e tre più l'holdout → validata subito, altrimenti muore subito): il tempo di calendario non era l'ingrediente, lo sono i dati che finiscono in momenti diversi, come in `scripts/backfill_passes.sh`. **Seconda metà FATTA il 24 set (punto 1 del disegno):** l'intorno — ogni notte nel giro completo fino a 10 coppie validate (prima quelle in `watch`/`drift`) vengono riprovate con ogni soglia spostata di un gradino, solo sulla loro coin (`figlie_intorno`, `coppie_per_intorno`); una figlia sostituisce la madre solo con le conferme retroattive e un margine del 10% sul ritorno OOS; la madre resta nel registro (`sostituita_da`) ma non si opera (`coppie_validate`, regola unica per optimize e discovery). Una coppia ogni 7 giorni, una figlia riposa **30** giorni (audit del 24 set; il disegno diceva 14). Tetto 10 finché il giro completo non stava sotto 1h30; **dal 25 set tetto 40** (`DISCOVERY_INTORNO_CAP`): giro completo a 1h09 (ops 0235), sì del proprietario. Metro: giro sotto 1h30, se sfora le 2h si torna a 10.

_Emerso il 21 set; testo originale qui sotto._

Osservazione del proprietario: *«magari la strategia è corretta ma le regole di
ingresso no, e vanno riadattate per quella strategia»*. È esatta, e oggi il sistema
non ha nessun modo di farlo.

Quando la discovery promuove una spec, nel registro scrive:

```python
entries[key] = {"symbol": sym, "strategy": spec["id"], "params": {}, ...}
```

`params` **vuoto** (`scripts/discover_strategies.py:367`). E la docstring di
`evaluate_spec` lo dice: *«le spec generate non hanno train»*. Le soglie d'ingresso
— quale RSI, quale ADX minimo, quale moltiplicatore di volume — sono **congelate
alla nascita**. L'unico parametro tarato per coppia è la scala dei TP, aggiunta
dopo, e infatti il commento di `ladder_multiples` racconta proprio quella
migrazione.

Quindi il gate sa rispondere solo **sì / no** sulla spec così com'è scritta. Non sa
dire *«l'idea è buona, la soglia è sbagliata: spostala da RSI<30 a RSI<25»*. Una
spec che sbaglia di poco viene bocciata, purgata, e sostituita da un'altra estratta
a caso: si butta via l'ipotesi insieme alla taratura.

**Quello che oggi si adatta, e quello che no:**

| cosa | si adatta? | da cosa |
|---|---|---|
| scala dei TP per coppia | sì | gate: 4 candidate fisse + 1 dal vissuto del paper |
| peso strategia × regime | sì | learning → modula la **size** |
| calibrazione confidenza | sì | → modula **size** e leva |
| freno da deriva | sì | → modula **size** |
| soglie globali (`DECISION_THRESHOLD`…) | sì | supervisore, dentro un budget di falsi positivi |
| **soglie d'ingresso di una spec** | **no** | **mai** |
| feature di una spec | no | congelate alla nascita |

Tutto ciò che impara modula **size o uscite**. L'ingresso, no.

**Attenzione a non "risolverlo" nel modo sbagliato.** Tarare i parametri sui
risultati del paper è vietato per un motivo scritto in `bot/config.py:383`: *«Il
paper FALSIFICA, non ottimizza: tararci i parametri lo consumerebbe come training
set»*. È la stessa trappola che ha prodotto BIRBUSDT (PF 1,51 promesso, 0,16
vissuto). Il paper è l'unica prova fuori campione che esiste: se la si usa per
tarare, smette di essere una prova.

**La strada giusta è nel GATE, su dati storici**, esattamente come già avviene per
le strategie scritte a mano (`effective_param_grid`): una **ricerca nell'intorno**
di una spec validata — stesse feature, soglie numeriche spostate di poco — valutata
con lo stesso walk-forward e lo stesso holdout. Non consuma il paper, perché non lo
guarda.

**Il costo, misurato:** una passata del gate dura già **2h22 dentro una finestra di
3 ore**, con 8 processi al 99% su 8 core (`ops/results/0118`). Provare 5 varianti
per spec moltiplicherebbe il lavoro. Mitigazione ovvia: fare l'intorno **solo sulle
coppie in `watch` o `drift`**, cioè spendere calcolo solo dove l'evidenza dice già
che la taratura attuale è sbagliata.

**Perché non è stato fatto adesso:** cambierebbe quali coppie entrano nel registro,
quindi cosa il paper opera, quindi la misura in corso. È la modifica più invasiva
di tutto il backlog. Va decisa, non fatta di slancio.

---

## C. Timeframe e universo

### C1. A 1 ora le strategie vanno molto meglio
**Stato:** **FATTA il 22 set sera su BTC, allargata il 23 a ETH, SOL, ADA, BCH** (`DISCOVERY_EXTRA`); prima candidata ADAUSDT@1h con 1 conferma il 24 set. **26 set (passo 5 del piano del 26 set 15:xx): allargata a ~30 coin.** Il numero: su 5 coin la passata a 1 ora ha fatto 460 valutazioni e 1 passata (ADAUSDT, sempre lei) il 26 set (ops 0282-0284), cioè lo **0,22%**; a 1 ora le candidate battono il pareggio nel 29-37% dei casi contro l'8% dei 15 minuti (tabella sotto), quindi il collo è il numero di coin, non il timeframe. `DISCOVERY_EXTRA` vale ora `1h:auto30` (`scripts/optimize.py::coin_1h_auto`): le 5 fisse + le coin con una coppia a 1 ora già nel registro (perché non si fermi a metà strada, come ORCAUSDT a 15 minuti) + le coin con coppie validate a 15 minuti (più coppie prima) + il top per volume, fino a 30; se la unit sulla VPS porta ancora la vecchia lista di 5 coin, si legge come auto30. Costo: 2 minuti per 5 coin misurati il 26 set → ~12 minuti stimati, il tetto resta 40 minuti (`DISCOVERY_EXTRA_MAX_S`); il log stampa coin e stima, `gate` la riga PASSATA A 1 ORA (N coin). **Metro:** tasso di passaggio a 1 ora in 3 notti contro lo 0,22% (`discovered_last_run_1h`: n_passed/n_eval); la **prima validata a 1 ora non prima dell'8 ottobre** (ADAUSDT: seconda conferma dal 1° ottobre, terza dall'8: tre finestre di 7 giorni, non si accelera); **60 coin solo se la passata a 30 dura meno di 15 minuti** (riga PASSATA A 1 ORA). Non verificato dal vivo: la durata vera su 30 coin si legge alla prossima passata. Il resto della voce è la storia. — la spec porta il suo timeframe (id incluso), il motore etichetta la riga base col suo intervallo, `optimize` lancia a ogni giro una passata di discovery a 1h su BTCUSDT (`DISCOVERY_EXTRA=1h:BTCUSDT`, max 40 min, senza toccare il timer), il bot fa decidere ogni strategia sul suo orologio e i trade portano il timeframe della strategia. Le prime coppie BTC@1h servono 3 conferme (3 settimane). Allargare ad altre coin = cambiare `DISCOVERY_EXTRA`.

```
candidate che battono il pareggio:
   5 minuti ..... 2-3%
  15 minuti ..... 8%      ← dove giriamo
   1 ora ........ 29-37%
```

L'ordine è monotono. La spiegazione più semplice sono i **costi**: più corto
l'orizzonte, più trade per lo stesso movimento, più fee e funding. Coerente col
paper, dove i costi sono 4,61 su un lordo di −13,39.

**Serve:** il verdetto dei 40 trade. Cambiare timeframe azzera il confronto.

### C4. Il bot non si mette flat su FOMC/CPI/NFP
**Stato:** aperto · rischio documentato dal 4 agosto, mai chiuso

`macro_agent.py` esisteva, non era importato da nessuno e il suo
`upcoming_high_impact_events()` ritornava `[]`. È stato rimosso perché «codice
morto documentato come protezione è peggio di una protezione assente». La
conseguenza scritta nei documenti: **il bot tiene le posizioni aperte durante i
dati macro**, e nessuno lo sta guardando.

Ricerca del 20 settembre: **nessuna fonte gratuita e verificata copre il caso.**

* **FRED** sembrava la risposta ed è stato scartato dalla verifica: i termini
  d'uso vietano *«storing, caching, or archiving»* e l'uso per addestrare
  software — cioè precisamente ciò che il gate fa — e le date sono **al giorno,
  senza orario**. Da rileggere da una rete non filtrata prima di escluderlo del
  tutto.
* **ForexFactory / CryptoCraft**: gratis e col campo "impatto", ma ~2 mesi
  indietro → solo live, mai gate. Il pacchetto `market-calendar-tool` che
  prometteva lo storico non è installabile (vuole Python 3.12, siamo su 3.11),
  è fermo da 23 mesi, e se ForexFactory cambia una scritta **cancella le righe in
  silenzio**: il backtest riceverebbe un calendario vuoto senza errore.
* **La lista scritta a mano.** Dal 2022 a oggi sono ~8 FOMC l'anno + 12 CPI + 12
  NFP: **circa 140 righe**. Un CSV nel repo, nessuna API, nessuna licenza, nessuno
  scraper che si rompe durante un giro. Gli orari sono costanti (CPI e NFP 14:30
  ora italiana, FOMC 20:00). *È un ragionamento, non una fonte letta.*

---

---

## F. Apprendimento — l'obiettivo finale

### F1bis. Il «paper esplorativo» — proposto il 25 set, **FATTO il 25 set** (il proprietario ha detto sì)
Il proprietario ha chiesto di imparare il più possibile da ogni chiusura e ha detto che in paper si può rischiare di più per validare ipotesi. Proposta: le coppie che passano per un pelo (quasi-passaggi, ~36 a giro) si operano in paper a un quarto della size, marcate `esplorativa`, escluse da pesi e freno; il gate le giudica anche col loro vissuto. Rischio: l'equity del paper si sporca di trade più deboli (per questo size ridotta e contatore separato). Simile a F2 ma senza le due settimane e senza rifare il ciclo.

**Fatto il 25 set:** a fine giro il gate sceglie fino a 20 quasi-passaggi (mancato più piccolo, una coppia per coin, non validate, spec generata, coin nell'universo) e li scrive in `strategy_registry/esplorative` (`pairs`, `specs`, `storia`; ciclo di vita: resta finché quasi-passaggio o vista entro 2 giri, validata → storia «validata», sparita da > 2 giri → «scartata»; `scripts/discover_strategies.py::pubblica_esplorative`, fail-open). Il bot le carica ogni ora con le spec (`adaptation.esplorative_for`), le opera SOLO in DRY_RUN, a un quarto della size (`ESPLORATIVA_SIZE_MULT=0.25`), al massimo 3 aperte insieme (`ESPLORATIVE_MAX_APERTE`, rifiuto «esplorative al tetto» contato), e una validata sulla stessa coin vince sempre. Il trade porta `esplorativa: true` (posizione persistita, `ClosedTrade`, badge «espl.» in dashboard). Fuori: pesi, keep del trailing, deriva (globale e per coppia), calibrazione, i numeri di `paper` nel controllo orario e in `trades`. Dentro: referti (con il conteggio `esplorative`), scala e keep letti dal gate (più dati è il punto). **Metro:** dopo 100 trade esplorativi, quante coppie esplorative sono poi passate il gate contro quante scartate — si legge in `gate` («ESPLORATIVE: N attive · validate poi X · scartate Y»), in `trades` («PAPER ESPLORATIVO») e in `dashboard/gate.giro.esplorative`. Numeri di partenza: 0 trade esplorativi, 0 coppie (il primo giro col codice nuovo le sceglie). Se a 100 trade le «validate poi» sono zero, il paper esplorativo si spegne (`ESPLORATIVE_ENABLED=false`).

### F1ter. Selettore in ombra: attivo dal 25 set (passo 2 del disegno)
Il modello (che ancora NON BATTE «apri tutto», ops 0231) dà a ogni trade aperto dal bot la sua `p` e la scrive sul trade (`selector_p`, `selector_soglia`) e nel log `[selettore]`; `trades` stampa «SELETTORE IN OMBRA» (p media vinti vs persi, PnL sopra soglia vs tutti, correlazione da 10 trade). Si accende solo se batte su 2 finestre su 3 E la calibrazione sul paper non è piatta con ≥ 40 trade con p. Divergenze dichiarate fra bot e gate: stop del risk gate invece di quello grezzo, ora della decisione, contesto BTC fino a 60 minuti vecchio. Da mostrare in dashboard (colonna p nei trade chiusi) quando ci saranno i primi trade con p.

## G. Portafoglio e gate — quello che i sistemi seri fanno (24 set)

### G3. La statistica t è misurata ma non decide
**Stato:** **misura FATTA il 24 set** — `last_t` nel registro per ogni validata (scritto dalla discovery, cioè per tutte le generate), `gate` stampa quante reggerebbero t ≥ 2 e la mediana. L'audit propone t ≥ 3 come criterio (con centinaia di candidate per coin, 2 è il livello del rumore): **si decide dopo aver visto il numero** (H).

### G6. La pesatura di recenza nel gate esiste ma nessuno la chiama
**Stato:** **fatta a metà il 25 set, la metà che non cambia chi entra.** Nella discovery la SCELTA fra scale di TP, break-even e keep del lock (`_metrica_scelta` in `discover_strategies.py`) pesa i trade con l'emivita di 180 giorni (`GATE_RECENCY_HALFLIFE_DAYS`, 0 = uniforme): prima sette giorni nuovi su 4,6 anni valevano lo 0,42% dell'evidenza e la scelta non si spostava mai. I criteri di validazione (PF, win rate, ritorno, consistenza, holdout) restano NON pesati, per costruzione: il tasso di passaggio non cambia. Resta aperta l'altra metà — pesare anche la validazione — che cambia quali coppie entrano: va decisa con il tasso di passaggio prima/dopo come metro, e per ora non si fa.

## H. Audit del 24 set — cose da decidere (proporre, non fare)

Quattro revisori indipendenti sul codice dei due giorni (integrazione, correttezza,
regole, disegno). Corretto subito: bocciature che chiudono la finestra (il giro
«solo urgenti» non si svuotava mai: causa dell'1h54), varianti senza conferme
retroattive scartate davvero, una sola figlia per madre, confronto figlia/madre
nello stesso giro su ritorno − drawdown e per finestra, riposo 30 giorni, tetto per
direzione duplicato rimosso, `portfolio/backtest` che non si pubblicava, dataset del
selettore anche con i quasi-passaggi (`passed`), verdetto del selettore per
permutazione (prima «batte» valeva una moneta), interazioni direzione × mercato e
regime nel selettore, dedup delle gemelle, freno di serie spento, madre sostituita
visibile in dashboard e in `gate`.

### H3. Stop giornaliero di portafoglio e netto in R
**Stato: PARCHEGGIATA il 25 set** — il proprietario: «non voglio limitare la quantità, voglio trade migliori». Uno stop giornaliero riduce le perdite, non migliora gli ingressi: resta qui solo come memoria.
**Sulle 160 coppie (ops 0232, 60 giorni):** senza limiti 974 trade, 16 al giorno, drawdown 14,8%, 34/27 giorni; + tetto direzione 3%: 854 trade, dd 16,0%; + stop giornaliero 3%: 765 trade, 13 giorni fermati, PnL −21%, dd 16,8% (peggiore, non migliore: dopo il blocco il rimbalzo si perde); + netto 2R: 713 trade, dd 13,6%, 35/25 giorni. Il giorno peggiore (30 ago, −1.609) passa a −563 solo con lo stop giornaliero. Non c'è una regola che vinca su tutto: si decide sul rischio che si vuole, non sui numeri.
I 5 giorni peggiori del portafoglio simulato perdono il 6-8% in un giorno con 1% per
trade e 5 posizioni: non stop simultanei, trade riaperti in una giornata che scende.
Nessuna regola oggi. `portafoglio` simula i due what-if (3% al giorno; |long − short|
≤ 2R): si decide sui suoi numeri.

### H4. Il freno di serie
Spento. **Misurato sulle 160 (ops 0232):** dopo 4 perdite di fila win rate 56% su 16 casi contro 63% incondizionato, t −0,58: nessuna evidenza, resta spento.

Spento. Si riaccende solo se `portafoglio` misura un win rate dopo 4 perdite più
basso di quello incondizionato con t ≥ 2 su ≥ 200 osservazioni.

### H5. La misura che separa mercato da esecuzione
**30 set: FATTA la misura FUORI CAMPIONE (sì del proprietario), in misura fino al 7 ott.**
Il confronto del «PERIODO DEL PAPER» misurava la selezione, non l'esecuzione: sugli stessi giorni
16-24 set il simulato fa −1.357 con le coppie del 25 set (ops 0232) e +8.465 con quelle del 30
(ops 0359). Ora `portafoglio` (voce ops già esistente) stampa la sezione «FUORI CAMPIONE»: per ogni
validata solo i trade del motore nati DOPO la sua validazione (`validated_at`; per le coppie senza
data il 25 set 12:00 UTC, quando il campo è arrivato sulla macchina per tutte le promozioni — non il
21, verificato col revisore), accanto ai trade del paper sulle stesse coppie e negli stessi istanti,
con R medio, vinti, max R, primo target, differenza e margine (2 errori standard), più tre righe di
scomposizione: «stessi segnali» (paper e motore entrano insieme), «non aperti» (segnali del motore
che il paper non ha preso), trade del paper senza un segnale del motore. La vecchia «Lettura» del
periodo non conclude più né «mercato» né «esecuzione». **Regola decisa prima di vedere i numeri,
il 7 ott:** con almeno 80 trade del motore: motore ≤ 0 → la promessa non regge dopo la validazione
(selezione del gate o mercato cambiato: la misura da sola non li separa) e la prossima modifica va
nel gate; motore > 0 e motore − paper oltre il margine → esecuzione, la prossima modifica va su
ingressi e uscite del bot; altrimenti si rilegge il 14 ott. **Limiti dichiarati:** (a) sopravvivenza:
le validate rimosse non si rigiocano (il report le conta e dà l'R del paper su di esse); (b) scala,
break-even e keep di oggi, non del giorno della validazione (il report conta i trade del paper con
config diversa e l'R senza di loro); (c) il paper salta segnali, il motore no (riga «non aperti»);
il margine tratta i trade come indipendenti (con un effetto di giornata comune copre ~81% invece
del 95%, simulazione del correttore). **Da decidere col proprietario prima del 7 ott:** se la regola
debba poggiare sulla riga accoppiata «stessi segnali» invece che sulla media di tutti i trade, e un
minimo di trade per il paper. Per separare gate e mercato servirebbe il motore sulle coppie NON
scelte negli stessi giorni (backtest in più: non fatto).

**Risposta del 25 set (ops 0232, portafoglio sulle 160 coppie dal 16 set):** anche il portafoglio simulato perde nel periodo del paper, −1.516 su 10.000 (−15%) con 8 giorni su 10 in perdita, contro −46,65 del paper (−5%): **è il mercato, non l'esecuzione**; il paper ha perso meno perché ha size dimezzata e freni. Chiuso il dubbio sull'esecuzione; resta il fatto che il gate ha promesso su un mercato diverso da quello di queste due settimane (deriva globale).

**Misurato il 24 set sera (ops 0211, 8 coppie rigirate):** dal 16 set i segnali del gate aperti dal paper sono 15 (PF 0,50, win rate 53%) e quelli non aperti 9 (PF 1,23, win rate 56%; 6 short su 9). Indizio che il percorso live scarta segnali migliori di quelli che apre, ma 9 trade non decidono niente. Prossimo passo: contare i motivi dei rifiuti nel log del bot (cooldown, tetto per coin, stop troppo largo, soglia) nel periodo del paper.

Il paper apre 4,9 trade al giorno contro 8,6 simulati. PF dei segnali «apribili ma
non aperti» (da `frequenza` + `confronto`) e `portafoglio --dal 2026-09-16`: se
anche il portafoglio simulato perde dal 16 set, è il mercato più la selezione; se
vince, è esecuzione/parità. È la domanda che vale tutte le altre.

## I. Check end-to-end del learning (25 set, otto revisori)

Cosa è ATTIVO e cambia davvero le decisioni oggi: il freno globale da deriva (size ×0,5 e leva ×0,71 su ogni trade da quando i trade hanno superato 40: PF 0,64 contro 1,89, ops 0227); i pesi strategia×regime (attivi dal 24 set alle 14:32, 32 coppie da 54 trade, ops 0228) che con confidenza fissa 60 mettono in panchina una strategia a peso < 0,5; il trend tilt; i tetti per coin e per direzione; il controllo del setup (stop > 6%); le regole del gate (finestra, intorno, varianti, scala dal vissuto). Cosa è misurato ma NON cambia niente: verdetti del trailing (keep mai adattato: servono 8 verdetti per strategia, 14 uscite trailing su 21 strategie → I3, fatto il 25 set: il keep lo sceglie il gate per coppia), deriva per coppia/strategia (soglie 8 e 20 mai raggiunte: max 5 trade per coppia), calibrazione (confidenza costante), referti «lock mai armato» e «sotto TP1» (contati, nessuna ipotesi), selettore (NON BATTE, ops 0231), ombra AI (contatore rotto, corretto il 25), filtro universo AI (mai escluso nulla).

### I1. I pesi mettono in panchina dopo due perdite
Con confidenza fissa 60 e soglia 30, «peso < 0,5» spegne la strategia in quel regime: bastano 2 perdite su 2 (`orchestrator.py`, `metrics.compute_weights`). Il commento parla di 4-5. Da decidere se è troppo aggressivo: misurare quante coppie sono a peso 0 nel doc `strategy_weights` (i pesi non sono leggibili da nessun comando ops: aggiunto al passo 1 di visibilità).

**26 set (passo 4 del piano del 26 set 15:xx): la panchina non rifiuta più, riduce.** Il numero: nel log del 26 set i rifiuti erano 18 «posizione già aperta», 17 cooldown, 3 «confidenza sotto soglia», 0 per peso (ops 0268), quindi non era un problema oggi, ma il proprietario non vuole tetti sul numero di trade («riduci la size, non rifiutare»). Ora un peso che porta la confidenza sotto soglia passa con `peso_size = max(PANCHINA_PAVIMENTO, peso)` (0,25, dichiarato in `bot/config.py`) e main lo applica alla size (in più del `learn_mult` dell'allocazione: peso 0,3 → ×0,725 poi ×0,3, è ciò che chiede la specifica); nel log una riga `[panchina] SYM strat: peso 0.30 -> size x0.30` (non contata fra i rifiuti). Il peso 0 («strategia spenta dal learning») rifiuta ancora; con `PANCHINA_PAVIMENTO ≤ 0` torna il rifiuto di prima. Sul trade chiuso `size_factors_at_entry.peso_size`. **Metro:** R medio dei trade con `peso_size < 1` contro quelli a peso pieno su ≥ 30 casi (`trades`); se la panchina fa peggio, il pavimento scende; se fa uguale, i pesi non discriminano e I1 si chiude così.

### I3. Il keep del trailing non scatterà mai con questi volumi
**Stato:** **FATTO il 25 set** (richiesta del proprietario: «ogni dato raccolto deve arrivare al cervello e produrre una decisione»). Il numero che l'ha deciso: 8 verdetti per strategia contro 14 uscite trailing in 10 giorni su 21 strategie, quindi l'adattamento del bot non sarebbe mai scattato; e se fosse scattato, il gate avrebbe continuato a simulare keep 0,5 (paper e gate divergenti). Ora il keep è un parametro PER COPPIA scelto dal gate come la scala dei TP e il break-even: `evaluate_spec` prova 0,35 / 0,5 / 0,65 sulla scala e sul break-even già scelti (3 backtest in più per ogni spec che passa, non per le bocciate), il vincitore va in `last_params.profit_lock_keep`, motore e bot lo leggono con la stessa funzione (`lock_keep`). Il paper entra come in `scala_dal_paper`: `keep_dal_paper` somma i verdetti di TUTTE le coppie e, con almeno 8, propone un quarto candidato (0,25 se ≥ 60% prematuri, 0,75 se ≥ 60% protetti) che il gate mette a confronto con gli altri: il paper propone, la storia decide. Le coppie non ancora rigiudicate col nuovo parametro continuano col keep con cui sono state validate (chiave assente → comportamento di prima), quindi il registro misto non rompe la parità. Visibile in `gate` (riga «keep del lock scelto dal gate») e nel log del giro (`[paper] N verdetti trailing…`, `[cervello] keep…`). Da misurare nelle prossime settimane: quante coppie finiscono su 0,35 e quante su 0,65, e se sul paper i prematuri calano.

**27 set: proposta per strategia** (sì del proprietario). La proposta del 25 set somma i verdetti di TUTTE le strategie: ma «il lock taglia i vincitori» può essere vero per una e falso per un'altra, e i verdetti portano già il perché (`trailing_knockout_atr` < 1 ATR = rumore, altrimenti inversione vera). Ora la discovery calcola anche un keep per OGNI strategia con ≥ 5 verdetti trailing sul timeframe del bot (`keep_per_strategia`, come `scale_per_strategia` per la scala), con la regola dichiarata in `bot/learning/metrics.py::proposta_keep_strategia`: 0,25 se i prematuri sono ≥ 60% **e almeno metà da rumore** (se sono da inversioni vere, allargare non aiuterebbe: nessuna proposta), 0,75 se i protetti sono ≥ 60%. È un candidato in più per il gate della sola spec a cui appartiene, dopo i tre fissi e la proposta globale (`candidate_keeps(keep_paper, keep_strategia)`), mai al posto loro: il gate lo giudica sulla storia come gli altri. Le conferme retroattive vedono gli stessi candidati. Misurato e solo stampato: il tragitto verso il TP lasciato sul tavolo (`metrics.soldi_sul_tavolo`, media di `trailing_miss_to_tp` — una FRAZIONE del tragitto entry→TP, non un multiplo di R: per convertirla servirebbe la distanza del TP in R di ogni trade, che il trade chiuso non porta). Visibile: log del giro (`[paper] keep per strategia dal vissuto: N strategie…`, `[cervello] keep… dal paper per strategia xN`), doc del gate (`giro.paper_propone.keep_strategie`, `cervello.keep_giro.dal_paper_strategia_n`), `trades` (blocco «KEEP PER STRATEGIA»). Costanti dichiarate prima di ogni misura (5 verdetti, 60%, metà da rumore, 1 ATR), mai tarate sul paper. **Metrica, fra 2 settimane:** la quota di «prematuri» sui trade delle coppie il cui keep è venuto dalla proposta per strategia (`dal_paper_strategia_n` nei doc del gate, `last_params.profit_lock_keep` = 0,25/0,75 sul registro) contro quella delle altre coppie; se non cala, la regola del rumore non discrimina e la proposta per strategia va tolta. Non verificato dal vivo: quante strategie superano i 5 verdetti si vede dal primo giro (`[paper] keep per strategia…`).

### I4. I referti sulle uscite non producono ipotesi
**Stato:** **FATTO il 25 set** (sì del proprietario) — quinta ipotesi `scala_stretta` in `bot/learning/referti.py` (≥ 3 perdite di classe «uscita» sulla stessa strategia, con la mediana degli mfe nel testo); la discovery calcola una scala per OGNI strategia con ≥ 5 trade con mfe (`scale_per_strategia`, un candidato in più dopo quella globale, mai al posto dei fissi) e rigiudica nel giro le strategie con l'ipotesi fresca (`strategie_scala_stretta`, ≤ 10 per giro; `giro.ipotesi_uscita` nel doc del gate). Limite dichiarato: «fresca» = `da_ts` (primo trade del paper della strategia) negli ultimi 7 giorni, perché il referto non porta la data in cui l'ipotesi è scattata; una strategia in paper da più di 7 giorni non entra da questa porta (entra nel giro completo di mezzanotte). Da misurare: quante volte il gate sceglie la scala per strategia (`scala_validate` nel doc del gate).

«Andato a favore ma sotto TP1» 19 su 31 stop, «lock mai armato» 6 su 6: contati, nessuna variante. Quinta ipotesi «uscita» (≥ 3 perdite sotto TP1 sulla stessa strategia → variante con la scala dal vissuto, nel gate con le conferme retroattive): **serve il sì** (cambia quali candidate entrano).

### I4bis. La freschezza dell'ipotesi «uscita» usa la data del primo trade
`da_ts` del referto è il primo trade del paper della strategia, non il giorno in cui l'ipotesi è scattata: una strategia in paper da più di 7 giorni con 3 perdite sotto TP1 non entra come urgente da questa porta (entra nel giro completo, con la sua scala fra i candidati comunque). Serve un timestamp per ipotesi scritto dal bot: piccolo, da fare se i numeri mostrano che l'urgenza serve.

### I4ter. Ipotesi sulle condizioni d'ingresso — **FATTO il 26 set** (sì del proprietario)
La sesta ipotesi dei referti: le perdite «mai andate a favore» (classe ingresso, mfe < 0,25 R) di una strategia sono nate in una condizione riconoscibile, e i suoi vinti no. Regola dichiarata in `bot/learning/referti.py` (`MIN_INGRESSO`, `QUOTA_INGRESSO`, soglie): per ogni variabile fra ADX, volume/media, ATR% e RSI, scatta `ingresso_<variabile>` quando la strategia ha **≥ 4 perdite d'ingresso** con la variabile nota, **≥ 3 su 4** dallo stesso lato della soglia (ADX < 20; vol_ratio < 1; ATR% sopra il 75° percentile dei vinti o sopra il 3%; RSI 40-60) e la mediana dei vinti (≥ 2) dall'altro lato. Le variabili vengono da `feats_at_entry` (ogni trade dal 25 set) o, per i più vecchi, da `indicators_at_entry` con le stesse formule del gate (`variabili_ingresso_del_trade`). La figlia (`varianti_da_referto`) stringe di UN gradino del generatore il filtro corrispondente: `min_adx` → 25, `volume_mult` → 1,5 poi 2,0, banda RSI di `rsi_extreme` un gradino più larga; il gate la giudica come le altre varianti (conferme retroattive, holdout). Il paper propone, non tara: la soglia della figlia è del generatore, non il numero misurato.

**Limite dichiarato:** `ingresso_atr_pct` nasce solo per spec `solo: long`. L'unico mattoncino sulla volatilità è `volatility_regime`, che dice «long se calmo, short se agitato» — non è un tetto a due lati. Aggiungere un tetto `max_atr_pct` a livello di spec cambierebbe il formato (fuori dall'hash come `solo`) e va deciso a parte, quando i referti mostreranno che l'ipotesi scatta e resta senza figlia.

**Metrica:** varianti create/passate da questi tipi, visibili nella riga `[cervello] varianti dai referti` del log del giro e nel `gate` (chiavi `cervello.varianti`; la figlia porta `ipotesi = "ingresso_<variabile>"`); i numeri per strategia in `trades` (blocco «CONDIZIONI D'INGRESSO»). Da misurare fra due settimane: quante ipotesi d'ingresso scattano, quante figlie passano il gate, e se sul paper le perdite di classe ingresso calano per le figlie promosse.

### I5. Validate senza promessa nel registro
72 su 131 visibili senza `last_pf` (alleggerite quando non erano validate, promosse poi dalla chiusura della finestra): deriva e veto di regime in fail-open per loro. Corretto il 25 set: `last_pf` fra i campi che l'alleggerimento conserva; si riempie al prossimo passaggio di ognuna.

## J. Controllo orario e dashboard (25 set)

Fatto il 25 set su richiesta del proprietario («check di tutto in automatico, le evidenze in dashboard ogni ora, la dashboard come un sistema serio»): il bot scrive ogni ora `dashboard/controllo` (`bot/learning/controllo.py`, schema in `docs/controllo_schema.md`), la discovery scrive `dashboard/gate` a ogni giro, la dashboard passa da 6+1 tab a 4+1 con il Controllo in prima pagina e 16 pannelli tolti. Rimandato, con il motivo:

### J2. «Cosa aspetta il sì» non è persistito
Le voci in attesa del sì vivono qui nel backlog: il controllo le lascia `null` e lo dice. Persisterle (un doc scritto dal controllo del mattino) è possibile ma è un altro posto da tenere allineato a mano; si fa solo se il proprietario vuole vederle in dashboard.

### J7. Direzione × contesto BTC nei referti — **FATTO il 26 set** (misura, nessuna decisione)
Dall'audit del flusso di learning: E1 dice «short 54 trade, −44,95», ma non dice se è «short» o «short con BTC su». Il dato c'è dal 25 set su ogni trade (`feats_at_entry.market_up`, la stessa variabile del gate e del selettore); i trade più vecchi restano «ignoto» (il contesto NON si ricava dagli indicatori della coin, che non sono BTC). Fatto in `bot/learning/referti.py`: `per_contesto` (globale e per strategia: long_con / long_contro / short_con / short_contro / ignoto, ognuna con trade, vinti, PnL) nel documento `learning/referti`, la tabella «DIREZIONE x CONTESTO BTC» in `trades`, e la settima ipotesi `controtrend_btc` (regola dichiarata: ≥ 3 perdite CONTRO il contesto — long con BTC giù, short con BTC su — e 0 vinti contro, per strategia), che la discovery prova come figlia `conferma_trend` (la conferma a 1 ora è il mattoncino che c'è) con l'etichetta `ipotesi = "controtrend_btc"`.

**Metrica:** la riga `tutte` della tabella in `trades` (vinti/trade e PnL per casella); quante ipotesi `controtrend_btc` nascono e quante figlie passano (`gate_progress`, riga «IPOTESI PER TIPO», J9). Si legge fra due settimane, quando i trade con contesto noto saranno abbastanza: oggi i 54 short di E1 sono quasi tutti «ignoto». Se «short_contro» perde e «short_con» no, il passo dopo è una porta nel gate per direzione × contesto — da decidere, non da fare qui.

### J8. Calibrazione del regime e del Fear & Greed — **FATTO il 26 set** (misura, `trust` invariato)
`regime_confidence_at_entry` e `fear_greed_at_entry` sono registrati su ogni trade «per poter misurare se predicono l'esito» (`bot/core/models.py`) e nessuno li aveva mai letti. Fatto in `bot/learning/calibration.py`: `calibrate(trades)` porta anche `regime_confidence` (terzili, con n / win rate / pnl medio e un `verdetto_regime`: «cresce» se il pnl medio della fascia alta supera la bassa, «piatta» altrimenti, «campione insufficiente» sotto 10 trade per fascia) e `fear_greed` (tre fasce fisse ≤ 25 / 26-74 / ≥ 75, i confini del sito che lo pubblica). Stessa popolazione della calibrazione (fuori esiti esterni ed esplorativi), ognuna con i suoi trade noti. `confidence_trust` non le guarda: nessuna size cambia. `trades` le stampa nel blocco «CALIBRAZIONE (regime, F&G)» da `calibration/current`.

**Metrica:** `verdetto_regime` e le tre righe del F&G in `trades`. Da leggere quando ogni fascia ha ≥ 10 trade (oggi ~55 trade delle validate in tutto: le fasce del F&G estreme saranno vuote a lungo). Solo se «cresce» regge per settimane ha senso proporre di legare la confidenza del regime alla size — con il gate, non qui.

### J9. Storia delle ipotesi e delle varianti per tipo — **FATTO il 26 set**
Le ipotesi dei referti vanno e vengono con i trade (una strategia che vince uno short spegne `solo_long`): senza memoria non si può dire se una REGOLA dei referti (un tipo) produce varianti che passano il gate o solo rumore. Fatto: documento Firestore `learning/ipotesi_storia` = `voci` («strategia|tipo» → nata_at, tipo, strategia, variante_id, esito aperta / variante_creata / passata / validata / bocciata / scartata, at, e il primo istante di ogni traguardo) e `per_tipo` (nate, varianti, passate, validate, bocciate). Chi scrive: `aggiorna_storia` (pura, in `bot/learning/referti.py`) alla prima comparsa di un'ipotesi — la chiama la discovery all'inizio di ogni giro (`aggiorna_ipotesi_storia`), e va chiamata dal bot dopo `learning/referti` (una riga in `_publish_referti`, da collegare); `varianti_dai_referti` lascia «variante_creata» (con l'id della figlia) o «scartata» (figlia impossibile, o il gate aveva già la risposta); dopo il merge `esiti_varianti_dal_merge` segna «validata» (promossa con le conferme retroattive), «bocciata» (scartata dal merge, o creata in questo giro e mai passata su nessuna coin), «passata». Il diario delle vite (`gate_history/lifecycle`) porta `ipotesi` e `genitore` sulle righe delle varianti. `gate_progress` stampa «IPOTESI PER TIPO: solo_long 9 nate / 9 varianti / 1 passate / 1 validate / 6 bocciate · …» con il tasso delle figlie accanto a quello delle candidate dell'ultimo giro (`gate_autopsy/discover`), dichiarando che sono unità diverse (una figlia è una spec su molte coin; l'autopsia conta coppie coin × spec).

**Limiti dichiarati:** negli shard (`--num-shards > 1`) gli esiti del merge non si scrivono (il merge degli shard non passa da qui); una variante bocciata e rinata al giro dopo torna «variante_creata» ma conserva `bocciata_at` (per questo `per_tipo` conta dai traguardi, non dall'ultimo esito). **Metrica:** la riga di `gate_progress`; da leggere a due settimane: un tipo con molte varianti e zero passate è una regola da rivedere (o da spegnere), uno con passate sopra il tasso delle casuali è una regola che funziona.

### J6. Ombra dei segnali rifiutati — **FATTO il 26 set (misura)**
**Il numero che l'ha fatta emergere:** ops 0211 (24 set, 8 coppie rigirate): 9 segnali del gate NON aperti dal paper con PF 1,23 contro 15 aperti con PF 0,50 — e il rifiuto più frequente (ops 0268, «posizione già aperta su questa coin») finiva in `altro`. Un rifiuto lasciava una riga di log e un contatore in RAM: nessuno sapeva se avrebbe vinto, e i freni (cooldown, tetto per coin, soglia di peso, tetto esplorative, veto di regime, margine, rischio direzionale, stop largo) si potevano tarare solo a intuito.

**Fatto:** ogni rifiuto con un segnale dietro viene scritto in Firestore `segnali_rifiutati/{YYYYMMDDHHMM}_{coin}_{strategia}` (una chiave per candela: idempotente) con entry, stop, target, scala, motivo e classe (`bot/learning/rifiutati.py::registra`; dall'orchestratore via `_rifiuto(..., dettaglio=...)`, da `_try_open` via `registra_decisione`). Ogni giro il bot valuta i pendenti sulle candele vere di Binance (`valuta_pendenti`, max 20 chiamate a giro) con le stesse uscite del motore (`simula_segnale`: stop, scala di TP, protezione del profitto, orizzonte 96 barre) e scrive `esito` (tp/stop/trailing/orizzonte), `pnl_r`, `mfe_r`, `mae_r`, `barre`; chi non ha candele entro orizzonte + 8 barre diventa `scaduto`. La voce ops `rifiutati` (`scripts/rifiutati_report.py`) stampa per motivo segnali, valutati, R medio, % vincenti, mfe mediana, e il confronto con gli APERTI dello stesso periodo in R netto. `motivo_rifiuto` ha la classe nuova `posizione aperta`.

**La regola, scritta prima dei numeri:** un freno si ritara SOLO se per un motivo i rifiutati hanno R medio > aperti con ≥ 30 casi valutati — e anche allora è una proposta per il gate, non una modifica al paper. Avvertenza fissa: i rifiutati sono prezzo puro (niente costi), gli aperti netti: ~0,1-0,2 R di vantaggio apparente ai rifiutati.

**Metro:** `ops rifiutati` dopo 30 giorni: quanti motivi hanno ≥ 30 valutati, e per quali il R medio dei rifiutati supera gli aperti. Numeri di partenza (26 set): 0 documenti, 0 valutati. **Non verificato dal vivo:** il cablaggio in `bot/main.py` (tre righe: `orchestrator.fb`, `registra_decisione` in `_rifiuto` di `_try_open`, `valuta_pendenti` nel giro) e la lettura di Firestore vera; da guardare al primo `ops rifiutati` dopo il riavvio. Non fatto: feats e p del selettore sui rifiuti di `_try_open` prima del risk gate (non esistono ancora a quel punto: restano `null`); il confronto per coppia (solo per motivo).

**27 set:** corretto il confronto con gli aperti in `scripts/rifiutati_report.py`: `post_mortem.stop_pct` è una frazione e veniva divisa ancora per 100 (R medio degli aperti −6,80 invece di −0,17, ops 0289). Senza la correzione la regola «rifiutati meglio degli aperti» avrebbe dato un falso via libera ad allentare i freni.

### J10. Il giro completo ridotto: spec note solo dove hanno una coppia viva + una fetta rotante — **FATTO il 26 set** (passo 3 del piano del 26 set 15:xx)
**Il numero che l'ha fatta nascere:** il primo giro completo con tutte le spec (26 set, 09:06-12:55 UTC, ops 0282-0284) ha fatto 134.994 valutazioni in **3h48** (0,61 s l'una con 6 worker): ~120.000 erano le ~502 spec note rivalutate su TUTTE le ~240 coin, e quasi nessuna di quelle coppie (spec, coin) ha mai passato il gate. Il timer è a 3 ore: un completo di quasi 4 ore rimanda i giri urgenti del giorno, e l'intorno a 40 aveva come condizione «completo sotto 1h30».

**Fatto** (`scripts/discover_strategies.py::riduci_spec_note`, `RIDUZIONE_ENABLED`, `RIDUZIONE_FETTE=7`): nel giro COMPLETO le spec già note si valutano solo (a) sulle coin dove hanno una coppia viva nel registro (pass_count ≥ 1: è lì che maturano le conferme e si giudicano validate e declassate) e (b) su una fetta rotante di 1/7 dell'universo (giorno UTC dall'epoca modulo 7, su ordine alfabetico delle coin: ogni coin è rivista da ogni spec nota entro una settimana). Le candidate NUOVE (ipotesi AI, varianti dai referti, figlie dell'intorno, casuali, semi) restano su tutte le coin: la scoperta non rallenta. Meccanismo: le note viaggiano nel canale per coin delle figlie dell'intorno (`specs_per_symbol`), i worker non cambiano. I giri «solo urgenti», le passate mirate (`--symbols`, quindi anche quella a 1 ora) e gli shard non cambiano. Atteso: 35-50 mila valutazioni (stima: 90 nuove × 240 coin + ~34 coin di fetta × 500 note + le coppie vive). In apertura il log dice `[discover] completa: N spec note su M coin (proprie + rotazione g/7) + K candidate nuove su tutte · ~S valutazioni stimate`; nel doc del gate `giro.riduzione = {spec_note, coin_proprie, fetta, valutazioni_stimate}` (null se non ridotto). `DISCOVERY_RIDUZIONE=false` rimette tutto su tutto.

**Metro:** (1) durata del giro completo **≤ 1h30** (`gate`, riga TEMPO DELL'ULTIMO GIRO; `giro.valutazioni` contro `giro.riduzione.valutazioni_stimate`: se il vero supera la stima di molto, le coin saltate non sono il motivo); (2) coppie nuove a 1 pass a settimana **prima e dopo** (`registro.distribuzione_pass` a pass 1 e le promosse nel diario `gate_history/lifecycle`, settimana 19-26 set contro 26 set-3 ott): se dopo scendono di più del rumore, la fetta a 1/7 è troppo stretta e si passa a 1/4 (`DISCOVERY_RIDUZIONE_FETTE`). Se il completo resta sopra le 2 ore anche ridotto, il tempo non è nelle spec note e va misurato dove sta.

**Limiti dichiarati:** una coin appena entrata nell'universo aspetta al massimo 7 notti per essere vista dalle spec note (le nuove la vedono subito); una notte senza giro completo salta la sua fetta per quella settimana; le coppie «congelate» (coin fuori dall'universo da 3 giorni) si valutano comunque quando la coin rientra, perché il merge le segna viste e le giudica — escluderle darebbe un fallimento senza valutazione.

**Insieme, lo stesso giorno: il bot ricarica il registro appena il gate lo scrive.** Prima ricaricava ogni ora (`ADAPT_RELOAD_SECONDS`): una coppia validata, declassata o sostituita dalle 03:30 restava «alla vecchia» fino a 59 minuti. Ora `bot/main.py::_ricarica_registro_se_cambiato` (nel loop, ogni 30 s) chiede al massimo ogni 60 s (`REGISTRO_CHECK_S`, dichiarato) ad `adaptation.registro_cambiato()` se `strategy_registry/validated.updated_at` è diverso da quello dell'ultima lettura, e ricarica pesi, registro, spec e selettore; un minuto dopo rilegge le spec una volta ancora (la discovery le scrive subito dopo il merge). Sul Firestore vero legge SOLO il campo (`field_paths`, proiezione lato server: il documento da ~1 MB resta a casa) passando dal client interno `_fs` di `FirebaseClient`, che oggi non ha un metodo per farlo — **da fare:** un `get_doc_field` nel client, così `adaptation` smette di guardare dentro. Fail-open: qualunque errore → si resta sulla ricarica oraria. Il gate non scrive uno specchio RTDB del registro, quindi non c'era un segnale più economico da leggere. Da verificare dal vivo: la riga `[main] registro riscritto dal gate: ricarico` entro un minuto dalla fine del prossimo giro.

### J11. Conferma a maggioranza della finestra — **FATTO il 27 set** (sì del proprietario)
Il numero che l'ha decisa: l'autopsia delle validate (ops 0290) ha trovato che, valutate una volta sola, passavano 23 validate su 194 (una su otto); l'artefatto della scala globale ne spiegava solo 6. La regola «almeno un pass nella finestra di 7 giorni = una conferma» (`scripts/optimize.py::judge_window`) lasciava entrare le coppie al limite: valutate più volte a settimana, prima o poi passano per caso. Ora ogni valutazione della finestra si conta (`window_evals`, `window_passes`) e la finestra è una conferma solo se la coppia ha passato più della metà delle sue valutazioni (`CONFERMA_QUOTA_MIN = 0,5`, strettamente sopra). Resta un verdetto per finestra; le finestre aperte prima del 27 set chiudono con la regola vecchia, una sola volta. Contatori nel nucleo del registro e nel codec corto. Metro: quota di validate che passano una valutazione singola (`autopsia-validate`), 12% il 27 set, obiettivo sopra il 50% in tre settimane; PF vissuto delle validate nate con la regola nuova contro le vecchie su almeno 30 trade ciascuna. Effetto atteso: meno validate nuove, e più lente.

### J13. La sessione oraria leggeva l'orologio, non la candela — **corretto il 27 set**; la sera la feature e' diventata un FILTRO e le coppie che la usano sono state azzerate (opzione c)
**Il numero che l'ha trovata:** i 5 trade «IGNOTO» dell'indagine sugli ingressi (ops 0310 `ingressi-orca`, 3 trade; ops 0311 `ingressi-vet`, 3 trade; 5 nella prima lettura di ops 0308), tutti di `gen_6d06dca0` = «rsi_extreme low=20 high=75 AND session hour_from=8 hour_to=16»: stessi indicatori del motore (entro 5%), regola che non scatta nemmeno sui valori scritti dal paper, e nel dettaglio la feature che frena è sempre `session` con `ora_utc=13` su candele delle 03:30 UTC — cioè l'ora in cui lo strumento GIRAVA (13:13 UTC), non l'ora della candela.

**La causa:** `bot/strategies/generated.py::_feat_session` leggeva `datetime.now(timezone.utc).hour` (e `_valori_feature` lo stampava come `ora_utc`): l'orologio del processo, non la candela valutata. Era l'unico punto del codice delle strategie che leggeva l'orologio (due righe, entrambe in quel file). Due conseguenze:
1. **Nel backtest** ogni barra della storia era giudicata con l'ora in cui girava il gate: un giro alle 03:30 UTC vedeva una spec «8-16» *fuori sessione* su tutta la storia (solo short ammesso), un giro alle 13:00 la vedeva *dentro* ovunque (solo long). Le validazioni di ogni spec con `session` non avevano senso e cambiavano da un giro all'altro — i passaggi si accumulavano su una feature valutata a caso.
2. **Nel bot** l'ora era quella della decisione: alle 03:30 UTC `gen_6d06dca0` apriva short (fuori sessione → short ammesso), e il motore rigirato alle 13:xx diceva «solo long, nessun segnale». Non un bug del bot: il bot faceva la cosa «giusta» per la sua ora, era il motore a non poterla riprodurre.

**Fatto il 27 set (parità: motore e bot usano la STESSA ora, l'apertura della candela su cui la regola decide, in UTC):**
* `AssetSnapshot.ts` (`bot/core/models.py`): epoch dell'apertura dell'ultima candela CHIUSA del timeframe primario, la stessa di `close_chiusa`. Il motore lo mette da `row["open_time"]` (`engine._snapshot_from_frame`, via `epoch_utc`, che legge un datetime senza fuso come UTC); il bot dall'`open_time` di `closed[-1]` (`price_agent.build_snapshot`); lo strumento degli ingressi da `candles[k]` e dalla candela del paper (`ingressi_report`).
* `generated.py`: `ora_candela(asset)` legge l'ora da `ts`; `_verdetto` la passa a `_valuta_feature`/`_valori_feature` solo se la spec usa `session` (`usa_sessione`); `spiega` riporta `ora_utc` della candela. Semantica invariata e ora documentata: dentro la fascia → solo long ammesso, fuori → solo short (la feature sceglie il LATO, non filtra). Senza `ts` si torna all'orologio con un avviso stampato una volta (`[session] ora dal calendario: snapshot senza ts`): non deve comparire nei log del bot né del gate.
* Visibilità: `gate_progress` stampa «FEATURE session: N validate su M usano la sessione oraria (…passaggi da rifare)»; la discovery stampa a inizio giro «[cervello] sessione oraria: N spec note su M usano `session`». **Nessun contatore del registro è stato toccato.**
* Test: `tests/test_sessione_ora_candela.py` (13): candela 03:30 vs 13:00 con orologio inchiodato all'ora opposta; `ts` del motore = apertura della barra; `ts` del bot = ultima candela chiusa; backtest di una spec con `session` identico con l'orologio alle 3 e alle 13, e long solo dentro 8-16; `spiega` stampa l'ora della candela; avviso una volta sola; le due righe di visibilità. Suite: 1761 passati (1748 prima).

**DECISIONE PRESA dal proprietario il 27 set sera — opzione (c), azzerare, piu' un cambio di significato della feature.** Le opzioni erano: (a) non fare niente e lasciare che il gate le rigiudichi; (b) declassarle subito a un quarto; (c) azzerare i loro `pass_count`. Scelta la (c), perche' e' l'unica in cui «validata» torna a voler dire quello che dice — e perche' guardando la regola e' venuto fuori che non aveva senso nemmeno con l'ora giusta: «dentro la fascia solo long, fuori solo short» non ha nessuna ragione economica (perche' comprare solo fra le 8 e le 16 UTC e vendere solo di notte?). Una sessione dice QUANDO il mercato e' liquido e leggibile, non in che verso va.

**Fatto il 27 set sera:**
* `generated._feat_session` ritorna `(dentro, dentro)`: dentro la fascia entrambi i lati ammessi (la direzione la danno le altre feature), fuori nessuno. In `_verdetto` e' l'AND sui due lati: `(False, False)` e' il veto su entrambi, `(True, True)` non tocca niente. `spiega` stampa anche `dentro`. Il generatore tiene `session` fra le condizioni (`_CONDITIONAL`), mai da sola.
* **Migrazione una tantum** `discover_strategies.azzera_sessione`, chiamata da `main` subito dopo la lettura del registro, protetta dal marcatore `strategy_params/migrazioni.sessione_lato_at` (scritto DOPO il registro; se registro o spec sono vuoti non si fa e non si segna niente, si riprova al giro dopo). Per ogni coppia con `pass_count >= 1` la cui spec usa `session`: `pass_count = 0`, `fail_count = 0`, `passed_in_window = False`, finestra cancellata (`window_start/evals/passes/contata`), `declassata = False`, `bocciata_notti = 0`, `sessione_azzerata_at = now`. Il record e i `last_params` restano. Scrive il registro una volta con lo stesso scrittore del merge (la coda del merge e' diventata `finalizza_registro`, usata da entrambi). Stampa `[cervello] sessione: N coppie azzerate (M validate) perche' la feature ha cambiato significato: ripartono da zero passaggi`.
* Con `pass_count = 0` le azzerate escono da `validated` → il bot smette di aprirle alla prima ricarica (`updated_at` cambia, `registro_cambiato` entro un minuto); le posizioni aperte le chiude l'esecutore come sempre (`adaptation` decide solo i segnali nuovi, verificato nel test col motore di adattamento). Restano NOTE: coin propria nel giro completo ridotto (`coin_proprie_delle_spec`), rigiudicate sopra il cap (`specs_da_rivalutare`, mezza conferma di priorita'), protette dalla potatura per MIN_PASSES finestre dall'azzeramento (`conferme_da_proteggere`, poi via come ogni candidata mai passata) e intoccabili per il tetto. `sessione_azzerata_at` e' nel nucleo (`REGISTRY_CORE_FIELDS`) e fra i tempi del codec compatto.
* Visibilita': la riga `FEATURE session` di `gate_progress` aggiunge «· N azzerate il 27 set, ripassano da zero (K gia' ripassate)». Dashboard: niente.
* Test: `tests/test_sessione_filtro.py` (12): i due lati / nessuno, giro di mezzanotte; con `rsi_extreme` dentro decide l'rsi in entrambi i versi e fuori niente; due sessioni in AND; il generatore non mette mai la sessione da sola; migrazione su registro finto (con e senza sessione, validate e no, spec sconosciuta; campi azzerati; `last_params` tenuti; una volta sola; senza registro o spec non si segna); coin proprie, protezione, rivalutazione sopra il cap, non urgenti; il merge non le pota; codec e nucleo; il bot le toglie alla ricarica; riga di `gate_progress`. Aggiornati i tre test di `test_sessione_ora_candela.py` che pretendevano la semantica vecchia (commentati) e `test_registro_spazio` (guarda `finalizza_registro`). Suite: 1773 passati (1761 prima).

**Non verificato dal vivo (sera):** la migrazione gira al primo `main` della discovery dopo `aggiorna` (anche la passata a 1 ora la fa: e' la prima che parte). Il numero vero (47 su 212 al 27 set, ops 0314) lo dice la riga `[cervello] sessione:` nel log del giro e la coda della riga `FEATURE session` di `ops gate`. Il bot vede il cambio di semantica solo al riavvio (`aggiorna` + `riavvia-bot`). **Metrica:** quante delle 47 azzerate ripassano il gate ENTRO 3 SETTIMANE (MIN_PASSES finestre da `sessione_azzerata_at`, la durata della protezione) con il filtro a due lati — il numero «K gia' ripassate» della riga `FEATURE session`. Lettura: se sono poche (sotto un quarto) la sessione era una feature che vinceva per il difetto, non per il mercato; se sono molte, la fascia oraria vale davvero e la si puo' spingere nel generatore. Le azzerate che non ripassano in 3 settimane escono dal registro da sole.

**Non verificato dal vivo (mattina, la correzione dell'ora):** la correzione entra nel bot solo al riavvio (`aggiorna` + `riavvia-bot`) e nel gate al primo giro della discovery; le due righe di visibilità non sono state viste su Firebase vero. Da rilanciare `ingressi-orca` / `ingressi-vet` dopo `aggiorna`: i 5 IGNOTO devono diventare ABBINATI o una classe spiegata (il motore, rigirato con l'ora della candela, dovrebbe ora trovare gli short delle 03:30-04:00). **Metrica:** 0 trade IGNOTO su `gen_6d06dca0` al prossimo `ingressi`; quota di abbinati (J12) in salita.

### J14. Letture Firestore: la quota gratuita si è esaurita — **FATTO il 28 set** (cache dei trade, finestra dei rifiutati, contatore), da misurare sulla console

**Il numero che l'ha fatta emergere (misurato sulla console Firebase, non stimato):** 8.000 letture al giorno il 20 set → 39.000 il 26 set → **quota di 50.000 esaurita il 28 set alle 06:18 UTC** (ops 0331 e 0332: `mfe` e `frequenza` falliti con `429 RESOURCE_EXHAUSTED`; alle 05:34 tutto funzionava). Finché la quota è esaurita il bot non rilegge registro, pesi e trade e lavora con quello che ha in memoria; le scritture hanno una quota a parte. Le cause, dal codice (stima per chiamante, prima della correzione): verdetti trailing a ogni candela su `recent(100)` (~9.600/giorno), pesi su tutti i trade di 30 giorni dopo ogni chiusura e ogni ora (~8.200), controllo orario con tutti i trade + 200 documenti dell'ombra AI + ~16 documenti (~8.900), ombra dei rifiutati a ogni candela su una finestra di ~17 giorni che cresce di ~30 documenti al giorno (~5.300, ~24.000 una settimana dopo), registro ogni minuto (1.440), stop recenti, referti, report ops e dashboard.

**Fatto il 28 set (quattro pezzi):**
1. **Contatore delle letture** in `bot/core/firebase_client.py` (`ContatoreLetture`, `fb.letture()`): ogni `get_doc` vale 1, ogni `query_collection` i documenti tornati (almeno 1), il Realtime DB non conta; ogni lettura porta l'etichetta del chiamante (`chi=`, o il nome della funzione). Il bot stampa ogni ora `[firebase] letture ultime 24 h: N (registro X · trade Y · controllo Z · rifiutati W …)` e il controllo pubblica `salute.letture_firestore_24h` e `letture_per_chiamante`; anomalia `LETTURE_FIRESTORE` gialla sopra 25.000, rossa sopra 40.000. Nuovi nel client: `get_doc_field` (proiezione: `registro_cambiato` non passa più dal client interno `_fs`, era il «da fare» di J10), `count_collection` (aggregazione del server, 1 lettura), `max_value` nelle query.
2. **Cache dei trade chiusi** in `bot/learning/trade_logger.py`: `recent` e `all_since` rispondono dalla memoria; carico intero al primo uso, poi `log`/`aggiorna` (i verdetti scritti sul posto da `evaluate_pending_trailing`) aggiornano la cache e, al massimo ogni 5 minuti, una query `exit_ts >= ultimo visto` (1 lettura quando non c'è niente di nuovo) è la rete contro uno scrittore esterno; una volta al giorno conteggio con l'aggregazione + ricarica intera (`manutenzione`); se il conteggio non torna: `[trades] cache disallineata: X vs Y, ricaricata` e anomalia `CACHE_TRADE_DISALLINEATA` (info) nel controllo. `_publish_controllo` passa i trade della cache e `carica_dati` non li rilegge; l'ombra AI del controllo legge 50 documenti invece di 200.
3. **Finestra dell'ombra dei rifiutati** (`bot/learning/rifiutati.py`): (orizzonte + margine + 2) barre del timeframe più lungo davvero in uso (15m: 106 barre ≈ 26 h; 1h: ≈ 106 h; i timeframe vengono dalle spec in RAM e da quelli visti fra i pendenti), tetto di 200 documenti per giro; passata giornaliera `chiudi_scaduti` che segna «scaduto» chi è in attesa da più di 5 giorni leggendo solo la fetta dal 5° all'8° giorno (~90 letture al giorno).
4. **Le giornate in ora italiana, e i due conti** (`bot/core/tempo.py::giorno_locale`, `GIORNO_TZ = "Europe/Rome"`, ripiego UTC+2 dichiarato se manca tzdata): il controllo orario (`oggi`, `giornate`), il portafoglio simulato (`bot/risk/portafoglio.py`), `pnl_paper_per_giorno`, `trade_stats` e `signal_frequency` contano lo stesso giorno. Il documento porta `giornate.tutti` (tutti i trade chiusi: esplorativi e uscite esterne, il conto del report `portafoglio`) e `giornate.validate` (le validate decise dalla strategia), ogni riga `pnl_tutti`/`pnl_validate`, `oggi.pnl_tutti`; la dashboard mostra «conto» e «validate» per giorno, etichetta «giornate in ora italiana». È la spiegazione del 27 set (+3,25 sul conto, +1,26 sulle validate): non un errore, due conti, ora dichiarati nello stesso posto. Candele e timestamp dei trade restano in UTC.

**Atteso dopo la correzione (stima per chiamante, dal codice):** registro ogni minuto ~1.440 · registro/pesi/spec ogni ora ~200 · trade ~600 (carico iniziale + incrementale ≤ 288 + ricarica giornaliera) · controllo orario ~1.600 (66 documenti × 24) · rifiutati ~3.300 (finestra di 26 h ≈ 30-35 documenti × 96 candele + la passata giornaliera) · resto del bot ~200 (rischio, selettore, deriva, referti) ≈ **7.300 al giorno dal bot**, più snapshot GitHub, comandi ops e dashboard (~2.000). La voce più grossa che resta è l'ombra dei rifiutati a ogni candela: se serve, il passo dopo è tenerla in memoria come i trade.

**Metrica:** la console Firebase (Usage → Reads) **sotto 15.000 letture al giorno per due giorni di fila** (30 set e 1 ott), e la riga oraria `[firebase] letture ultime 24 h` nel log del bot che dica lo stesso numero ± le letture fuori dal bot. Se resta sopra: piano a consumo (Blaze, ~0,06 $ ogni 100.000 letture) invece di rincorrere il codice. **Non verificato dal vivo:** l'aggregazione `count()` e la proiezione `field_paths` sul Firestore vero (in memoria sono simulate; `google-cloud-firestore` 2.30 le ha); il numero sulla console, che si legge fra due giorni; la dashboard nel browser (tipi e parità campo per campo verificati, resa no).

### J15. «Cambiamenti del learning» confronta con un'ora prima, non con ieri
`controllo.cambiamenti_24h` legge l'impronta precedente da RTDB `/controllo/learning/attivo/impronta`,
riscritta ogni ora: dice quasi sempre «nessuno» (ops 0338: 06:05 contro 05:06) anche quando in 24 ore
il keep di decine di coppie è cambiato (ops 0324 contro 0343). **29 set:** il «cosa è cambiato ieri»
ora c'è davvero, dalle foto giornaliere (`/learning_giorni`, sezioni STORIA DEL LEARNING / COME
IMPARA IL TRAILING / COSA IMPARANO LE STRATEGIE di `controllo`). Resta da rinominare o togliere la
riga oraria, che col nome «24h» inganna.

## D. Infrastruttura

### D1. Il registro su più documenti
**Stato:** aperto · rimandato 19 set, non più urgente

È l'unica correzione che **scala** davvero. Rimandata perché tocca ogni lettore —
bot, learning, quattro script, due componenti della dashboard — e farla di fretta
su un documento che contiene settimane di attesa, mentre il paper gira, trasforma
un problema di spazio in una perdita di dati.

Il formato compatto ha spostato il vincolo da 3 giorni a mesi (272 KiB su 879, 108
byte a coppia): c'è tempo per farla bene.

### D5. `reset_paper.py` non azzera l'inizio del paper (né il prezzo BTC di partenza)
**Stato:** aperto · trovato il 28 set leggendo `scripts/reset_paper.py` mentre si aggiungeva il benchmark BTC dal primo giorno

Il reset riscrive `/account/equity` e `/account/starting_equity` ma lascia
`/account/paper_started_at`: dopo un reset `giorni_paper` e il benchmark «BTC
tenuto dal primo giorno» partirebbero dal paper VECCHIO. Il benchmark ha già una
difesa (`/account/btc_inizio` vale solo se la sua candela apre entro un'ora
dall'inizio del paper, altrimenti il bot la riscrive e il controllo la ignora), ma
l'inizio stesso resta sbagliato. **Serve:** nel reset, `paper_started_at` e
`btc_inizio` a `None` (il bot li riscrive da soli al riavvio). Non fatto il 28 set:
nessun reset in vista e il proprietario non l'ha chiesto; il numero che lo ha fatto
emergere è la sola lettura del codice, non un reset andato male.

### D6. Spesa dell'AI: ~2,75 $ al giorno, più di metà sono le ipotesi del gate
**Stato:** aperto · trovato il 29 set, quando il proprietario ha visto circa 10 $ spesi in 4 giorni · **il contatore misurato c'è dal 29 set** (richiesta del proprietario: «aggiungi al report la spesa giornaliera di AI e per quali ragioni»): ogni chiamata somma i token dell'API in Firestore `ai_spesa/{giorno}` (`bot/ai/spesa.py`), e `ai-stato` stampa la sezione SPESA AI (ieri per ragione, oggi, media dei giorni interi, risposte troncate, avviso se risponde un modello diverso da quello del prezzo). Le leve qui sotto restano da decidere, ora con un numero misurato.

**Il numero (stima dai log, non dalla fattura):** token per chiamata letti nelle righe
`[ai-*] ok in … · IN+OUT token` dei risultati ops (0219, 0236, 0263, 0283, 0296, 0307 e i log
del bot), prezzo di `claude-opus-4-8` 5 $ per milione in ingresso e 25 $ in uscita:

| chiamata | token (ingresso+uscita) | costo | volte al giorno | al giorno |
|---|---|---|---|---|
| ipotesi (`ai-hypotheses`) | ~2.000 + ~3.400 | ~0,095 $ | 16 (8 giri × passata 15m + passata 1h) | ~1,52 $ |
| ombra (`ai-shadow`) | ~830 + ~600 | ~0,019 $ | ~42 (184−100 decisioni in 2 giorni, ops 0260→0330) | ~0,80 $ |
| autopsia (`ai-autopsia`) | ~1.000 + ~750 | ~0,024 $ | 16 | ~0,38 $ |
| universo (`ai-universe`) | ~480 + 10-110 | ~0,003 $ | ≤16 | ~0,05 $ |

Totale ~2,75 $/giorno, ~11 $ in 4 giorni: torna con quanto visto dal proprietario. Più
dell'80% è testo SCRITTO dal modello (l'uscita costa 5 volte l'ingresso). La sola
previsione scritta nel repo era quella dell'ombra («qualche euro al mese», `bot/ai/shadow.py`);
la passata a 1 ora (`DISCOVERY_EXTRA`, dal 25-26 set) ha raddoppiato ipotesi e autopsia,
perché è un secondo `discover_strategies` con la stessa chiamata. `claude.yml` (le issue
con «@claude») non è mai partito: 0 esecuzioni. `learning.yml` chiama il modello solo la
domenica, con 400 token al massimo.

**Leve, in ordine di risparmio, nessuna fatta:** (1) ipotesi e autopsia una volta per
giro invece di due (la passata 1h riusa quelle della 15m, o non le chiede): ~-0,95 $/giorno;
(2) ipotesi solo al giro completo (1 al giorno) invece che ogni 3 ore: ~-1,3 $/giorno, ma
meno idee nuove per il gate (29 delle 605 che hanno passato vengono dall'AI, ops 0330);
(3) ombra con risposta corta (motivo in una riga, `max_tokens` più basso: già oggi il motivo
viene tagliato a 600 caratteri): ~-0,4 $/giorno; (4) modello più economico: è una scelta del
proprietario (D3). **Manca:** un contatore dei token spesi al giorno nel controllo (come le
letture Firestore), così il numero ha una fonte misurata e non una stima.

### D7. Chiamate AI pagate e buttate — trovate il 29 set leggendo il codice per il contatore
* **`ai-universe` del giro principale fallisce a ogni giro** con «risposta senza JSON valido» (11 volte
  nei log: ops 0104, 0190, 0198, 0201, 0212, 0219, 0263, 0283, 0296, 0307, 0345); riesce solo nella
  passata a 1 ora. Causa probabile, non verificata: 277 coin in ingresso e risposta tagliata a 2000
  token. Da ora il log stampa i token e «troncata» anche in quel ramo, e `ai-stato` conta le troncate:
  **metro** = la riga «risposte tagliate a metà» dei prossimi giorni. Se sono troncate: più spazio o
  meno coin nella domanda; se no, leggere la risposta.
  **Confermato il 29 set alle 09:10 UTC** (ops 0356): «2119+2000 token · troncata: finito lo spazio
  max_tokens». Ogni volta ~0,06 $ pagati e buttati, fino a 8 al giorno (~0,48 $): la risposta non ci
  sta nei 2000 token. **Fatto il 29 set (sì del proprietario: «dai più spazio al filtro monete»):**
  `MAX_TOKENS` 5000 in `bot/ai/universe_filter.py` e motivi in poche parole nella domanda (5000 token
  ≈ 70 s, sotto il timeout di 120 s). **Metro:** nella sezione SPESA AI di `ai-stato` la riga
  «tagliate a metà» di ai-universe deve sparire, e nel log del giro «[ai-universe] escluse N» o
  nessuna esclusione al posto di «senza JSON». Il costo per chiamata sale (fino a ~0,14 $ se usa tutto
  lo spazio): il contatore dirà quanto.
  **30 set:** col filtro finalmente non troncato, la passata a 1 ora (che usa `--symbols`) ha perso
  10 coin su 30 giudicate dal solo nome (ops 0365), e con `--symbols` la riaggiunta delle coin in
  maturazione non gira. Corretto col sì del proprietario: con `--symbols` il filtro non si applica
  (`discover_strategies.filtra_universo`). Resta aperto: il filtro riceve solo i simboli, senza
  storia né volume (era pensato con `history_days`, `volume_24h`, `atr_pct`), quindi giudica a
  memoria anche nel giro principale (dove però tocca solo coin senza coppie in corso).
* **La narrativa della domenica** (`learning_loop`, runner GitHub) falliva sempre con «'ThinkingBlock'
  object has no attribute 'text'»: il secret GitHub `ANTHROPIC_MODEL` è vuoto, quindi gira il modello
  di default, che ragiona prima di rispondere, e il codice leggeva solo il primo blocco. **Corretto il
  29 set** (`bot/ai/client.py::testo_di`, anche in `orchestrator._decide_llm`). Resta: con 400 token
  di spazio il ragionamento può mangiarsi la risposta (il log ora lo dice), e il secret vuoto fa
  scattare ogni lunedì l'avviso «modello diverso» in `ai-stato`: la scelta (riempire il secret o
  lasciarlo) è del proprietario.

### E1. Le short perdono sistematicamente
**Stato:** **NON risolta · in osservazione** — 23 set: short 23 trade, 8 vinti, **−35,84**; long 14 trade, 6 vinti, +4,75. Dal 21 sera il freno sul controtrend agisce davvero (VET short a 0,47% di rischio il 23) e la conferma a 1 ora è nel vocabolario: se le short perdono anche frenate, il passo successivo è validarle con un criterio a parte (PF per direzione nel gate).

```
long    7 trade · 3 vinti · +0,53 · mfe 1,23R
short   8 trade · 1 vinto  · −18,52 · mfe 0,72R
```

Il 19 settembre erano 7 short e 0 vinte (probabilità 1,3% se il sistema fosse sano);
poi una ha vinto e si è risaliti al 5,7%. **Il divario non si è chiuso, ha smesso di
allargarsi.**

Se regge ai 40 trade, il trend smette di essere un suggerimento sulla size
(`size_mult ≥ 0,5`) e diventa un **veto**. Oggi sarebbe una reazione al rumore.

### E4. Vendiamo le salite verticali, e con più strategie quasi gemelle
**Stato:** **FATTO il 21 set sera** (vedi il blocco «FATTO» in fondo alla voce) · **resta aperto** `min_adx` sulle spec esistenti e le gemelle già validate, che si stampano a ogni giro e vanno decise.

MUBARAKUSDT, 21 settembre: da 0,0320 a 0,04407 in ~30 ore (**+37%**), con un tratto
quasi verticale da 0,034 a 0,044 fra le 11:00 e le 12:42 e RSI a **88**. Ci siamo
entrati **short**.

Non è un guasto: è quello che le nostre strategie sono. `rsi_extreme` restituisce
*«RSI sopra soglia → vendi»*, `bb_touch` *«prezzo sopra la banda → vendi»*. Su un
RSI di 88 qualunque soglia ammessa (55–95) spara short.

**Due cose rendono il difetto strutturale, non sfortuna:**

1. **`min_adx` seleziona proprio i casi peggiori.** È un filtro che lascia passare
   il segnale SOLO quando l'ADX è alto, cioè **solo quando un trend c'è**. Combinato
   con feature di ritorno alla media significa: *opera solo quando c'è un trend, e
   vendilo*. Il vocabolario non ha nessun modo di dire *«non vendere una salita
   verticale»* — non esiste un tetto sulla distanza dalla media, né un `max_adx`.

2. **Più strategie quasi gemelle sulla stessa coin.** Al 21 settembre:

```
ORCAUSDT     8 coppie validate
SKYAIUSDT    4        MUBARAKUSDT  4
USELESSUSDT  3   → PF 1,541 · 1,541 · 1,54   (PnL OOS 77% · 77% · 72%)
```

Tre PF identici alla terza cifra non sono tre ipotesi diverse: è la stessa
scommessa contata tre volte. Non esiste **nessun controllo di somiglianza** fra
spec, né nel generatore né nella discovery: `spec_id` è un hash, quindi due spec
che differiscono per una soglia (RSI 70 vs 72) sono "diverse" per il sistema.

Il bot tiene una posizione per coin, quindi le gemelle non si sommano: **si mettono
in fila**. Chiuso uno stop, la successiva riapre. Su USELESSUSDT il 21 settembre
sono stati **tre trade short consecutivi** sulla stessa coin mentre saliva.

**Il numero:** short 13 trade, 2 vinti, **−30,11**; long 11 trade, 3 vinti, −15,59.
`USELESSUSDT|gen_2031005e` ha mfe mediana **0,20R** contro un primo gradino a 2,00R.

**FATTO il 21 set sera**, su richiesta esplicita del proprietario («fai 1, 2 e
anche 3, ma non buttiamo via nulla»), senza azzerare il registro:
* **il freno non frenava**: il rilevatore di regime chiamava «incertezza» ogni
  coin con ATR/prezzo > 2,5% — quindi più correva, meno era «in trend», e il freno
  leggeva zero. Ora la direzione si legge prima; la volatilità decide solo quando
  una direzione non c'è. Le generate operano in tutti i regimi, quindi i loro
  backtest non cambiano: cambia l'etichetta, cioè ciò che freno e learning leggono.
  Il pavimento del freno è una manopola (`TREND_TILT_FLOOR`, default 0,5).
* **tritacarne**: l'attesa dopo uno stop in perdita (`COOLDOWN_HOURS`, 1h a 15m)
  ora sta nel motore di backtest E nel bot, con una sola conversione ore→barre.
  Nel bot è per coin (blocca anche le gemelle in fila), nel motore per strategia:
  dal vivo è più stretta, divergenza nella direzione sicura. Le coppie validate
  tengono i passaggi e vengono rigiudicate con la regola nuova alla prossima
  finestra: è la migrazione a registro misto già usata per la scala dei TP.
* **gemelle**: `firma_spec` (feature + soglie arrotondate, `rr` escluso perché
  inerte) e `scarta_gemelle` nella discovery: nessuna copia nuova entra. Quelle
  già validate **non vengono rimosse** — vengono stampate a ogni giro
  (`gemelle_validate`) perché la decisione sia del proprietario, non del codice.
* **le parole che mancavano**: `not_stretched` (prezzo entro N ATR dalla media)
  e `adx_below` (l'opposto di `min_adx`) nel vocabolario, nel generatore, nel
  prompt AI e nel validatore. Additivo: le spec esistenti non le usano, il gate
  misura se servono.

**Resta aperto:** `min_adx` sulle spec esistenti non è stato toccato — cambiarlo
cambierebbe strategie già validate. Le nuove hanno `adx_below` come alternativa.
E le gemelle già validate sono ancora lì: vanno decise, non nascoste.
