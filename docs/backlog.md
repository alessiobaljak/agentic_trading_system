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

1. **Niente cambia le uscite prima dei 40 trade chiusi.** Siamo a 15. Cambiare
   stop, obiettivi o size a metà misurazione rende i primi trade non confrontabili
   coi successivi, e il verdetto che aspettiamo da tre settimane sparisce.
2. **Tutto passa dal GATE, mai solo dal paper.** Una modifica applicata al paper e
   non al gate fa sì che il PF promesso descriva un sistema diverso da quello che
   opera. È la classe di problema che ha prodotto BIRBUSDT (1,51 promesso, 0,16
   vissuto).

---

## A. Uscite — dopo il verdetto dei 40 trade

### A1. La protezione del profitto si accende troppo tardi
**Stato:** **FATTO il 21 set sera** (`lock_anchor` in `exit_logic`, usata da motore ed executor: ancora al PRIMO gradino). Il numero che l'ha deciso: 13 stop su 21 erano trade andati a favore (mfe mediana 0,69R) senza toccare il primo gradino, e uscivano a −1R pieno. Le coppie validate tengono i passaggi e vengono rigiudicate con la regola nuova (registro misto).

Il profit-lock si arma a metà della distanza dall'**ultimo** gradino. Con la scala
2/4/6 significa **3R**, mentre il primo incasso è a 2R: fra 2R e 3R il 70% della
posizione è protetto solo al pareggio.

```
mfe mediana (15 trade) ..... 0,85R
trade oltre 3R ............. 7%
```

I "runner" che un floor più basso taglierebbe sono **rari**; le inversioni nella
zona scoperta sono il caso comune. Proposta del proprietario: stop al primo
gradino una volta superato. Resa validabile: **ancorare il lock al PRIMO gradino
invece che all'ultimo** (su 2/4/6 si armerebbe a 1R).

**Serve:** farlo nel gate, rivalidare, poi il paper. **Non** prima dei 40 trade.

### A2. Il break-even non è validato per le strategie generate
**Stato:** **FATTO il 21 set sera** — `evaluate_spec` prova, sulla scala scelta, anche l'alternativa al default di `sl_to_breakeven` (una passata in più, non il doppio) e scrive la scelta in `last_params`; il bot la legge già (`breakeven_after_tp1`). Le coppie esistenti restano sul default finché non vengono rigiudicate.

`breakeven_after_tp1` dice che «lo decide il gate per ogni coppia». Per le generate
— cioè **tutte e 52 le validate** — non lo decide mai: non hanno griglia di ricerca,
e il passaggio che sceglie la scala dei TP non sceglie anche questo flag. Girano
tutte sul default globale `true`.

È lo stesso buco già chiuso per la scala (*«le generate non hanno grid → senza
questo passo restavano per sempre sulla scala globale»*), lasciato indietro su un
parametro.

**Serve:** estendere il ciclo che sceglie la scala perché provi anche
`sl_to_breakeven`. Non è ovvio che convenga: protegge, ma con mfe mediana 0,85R il
prezzo ritocca l'entrata di continuo e ogni volta chiude il 70% a zero.

### A3. La manopola del rischio non fa quello che dice — e non come credevamo
**Stato:** aperto · emerso 18 set · **corretto il 21 set: la regola era scritta al contrario**

Con il cap per-posizione attivo, il rischio effettivo **non è fisso e non cala con
stop larghi**. Dalla formula in `bot/risk/risk_manager.py:147`:

```
rischio effettivo = min( leva × cap_posizione × ampiezza_stop ,  rischio_impostato )
                  = min( 2 × 0,10 × ampiezza_stop , 1% )
```

cioè **cresce con l'ampiezza dello stop** finché non tocca l'1% impostato:

```
stop 1,0%  →  0,20%       stop 4,4%  →  0,88%
stop 2,0%  →  0,40%       stop 5,0%  →  1,00%  (il cap smette di mordere)
stop 3,0%  →  0,60%       stop 8,0%  →  1,00%
```

La voce diceva *«più lo stop è largo meno si rischia»*: **è l'opposto**. Il ~0,35%
osservato il 18 settembre non è il comportamento del sistema, è il comportamento
del sistema **su coppie con stop stretti**.

**Il numero misurato che lo ha fatto emergere** (21 set, USELESSUSDT, due short
consecutivi di `gen_2031005e`): −8,25 e −8,65 su un'equity di ~970$, cioè **0,85% e
0,89%** — praticamente l'intero 1% impostato, non un terzo. Lo stop era largo ~4,3%,
normale per l'ATR di una micro-cap sul timeframe da 15 minuti.

**Conseguenza pratica, che cambia la lettura di tutto il paper:** sulle coin
volatili il sistema rischia il massimo consentito, su quelle tranquille un quinto.
Il rischio per trade non è una costante ma una funzione della volatilità della
coin — e nessuno lo stava leggendo così.

**Serve:** decidere se il cap per posizione deve restare al 10%. Non è un difetto
da riparare di nascosto — è una scelta. Toccarlo cambia la size a metà esperimento.

### A4. Quanto vive una strategia validata — la prova non si distrugge più
**Stato:** **misura avviata il 21 set** · risposta fra qualche settimana

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

### B1. Il vocabolario è chiuso: 18 mattoncini
**Stato:** aperto · la più importante di questa sezione · emerso 19 set · **primo passo il 21-22 set**: sei parole nuove (market_trend, market_fade, relative_strength, not_stretched, adx_below, htf_confirm), tutte additive. Il salto vero — l'AI che propone una feature come formula — resta da fare.

L'AI può solo **combinare** 18 feature (RSI, Bollinger, MACD, VWAP, volume,
sessione, volatilità). Non può inventarne una nuova. Tutto lo spazio di ricerca è
chiuso lì dentro, per sempre.

È probabilmente la causa di un'osservazione archiviata il 6 settembre: **quasi ogni
strategia funziona su UNA sola moneta**. Se il vocabolario è troppo povero per
descrivere una regolarità vera, l'unica cosa che resta da adattare è la storia
della singola moneta.

**Serve:** un percorso perché l'AI proponga una feature NUOVA come formula
dichiarativa, validata dal gate come tutto il resto.

### B2. Le strategie scritte a mano non hanno mai validato niente
**Stato:** **FATTO il 21 set sera** — `OPTIMIZER_SKIP_BASE=true` (default nel codice): la valutazione delle base è saltata, resta la manutenzione del registro; le coppie base senza conferme escono con la regola delle stantie. Il calcolo liberato va ai semi della discovery (`DISCOVERY_SEEDS` 10→30, precedenza alle coin non coperte). Obiettivo: copertura, 26 coin su 165.

```
strategie base: 1312 valutazioni, 0 passate (0,00%)
registro: 2024 coppie base · 574 generate
```

Le 8 strategie a mano non producono una singola coppia validata da quando il
registro esiste, e occupano il 78% del registro.

**Serve:** decidere se continuare a valutarle. Toglierle libererebbe tempo di
calcolo e spazio; tenerle costa poco ma il conto è zero da settimane.

### B2bis. `rr` non serve a niente, ma scarta il 74% delle proposte AI
**Stato:** **FATTO il 21 set sera** — `rr` non è più richiesto né controllato dal validatore, e non compare più nel prompt; resta nella spec col default 2.0 perché fa parte dell'id.

Sotto scale-out il take-profit non è più `rr × R`: è la **scala di gradini**. Il
ramo scale-out ignora `target`, quindi **`rr` non ha nessun effetto sulle uscite** —
lo dice la docstring di `effective_param_grid`, che per le strategie classiche lo
sostituisce apposta nella griglia.

Per le generate invece `rr` resta un campo obbligatorio e validato. Risultato
misurato il 20 settembre: **14 proposte AI su 19 scartate** perché `rr` era sotto
1,5, cioè per un parametro che non cambia un solo trade.

**Serve:** decidere se per le generate `rr` vada ignorato del tutto (accettando
qualsiasi valore, o togliendolo dalla spec) quando lo scale-out è attivo. Non
toccato ora: cambiare cosa si valida a metà misurazione invalida il confronto fra
le coppie validate prima e dopo.

### B3. Nessuno chiede PERCHÉ le candidate muoiono
**Stato:** **FATTO il 21 set notte** — `bot/ai/autopsia.py`: a ogni giro i 40 quasi-passaggi (feature, coin, criterio, scarto) vanno al modello, che risponde con schema, ipotesi e consigli; i consigli entrano nel contesto delle proposte dello stesso giro. Esito in `ai_hypotheses/autopsia`, visibile in `ai-stato`. L'AI legge e suggerisce, il gate decide.

Il 68% muore su `total_return`, giro dopo giro. Contiamo i morti, non facciamo
l'autopsia. Ci sono ~40 quasi-passaggi a ogni giro che nessuno legge.

**Serve:** dare all'AI i quasi-passaggi e chiederle uno schema. È ipotesi sulla
RICERCA, non su una strategia.

### B4. Un referto su ogni trade chiuso
**Stato:** aperto · emerso 19 set

Ogni trade registra indicatori all'entrata, regime, confidenza, dove è arrivato il
prezzo, perché è uscito. **Nessuno li legge.** Con 15 trade è aneddoto; con 200
diventa il dato più ricco che abbiamo — e l'AI è l'unica cosa capace di leggere 200
referti e trovare il filo comune.

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
**Stato:** aperto · **la più importante di tutto il backlog** · emerso 21 set

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
**Stato:** **FATTA il 22 set sera, solo su BTC** — la spec porta il suo timeframe (id incluso), il motore etichetta la riga base col suo intervallo, `optimize` lancia a ogni giro una passata di discovery a 1h su BTCUSDT (`DISCOVERY_EXTRA=1h:BTCUSDT`, max 40 min, senza toccare il timer), il bot fa decidere ogni strategia sul suo orologio e i trade portano il timeframe della strategia. Le prime coppie BTC@1h servono 3 conferme (3 settimane). Allargare ad altre coin = cambiare `DISCOVERY_EXTRA`.

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

### C2. L'universo è fermo a `--top 200`
**Stato:** aperto · **da rivalutare dopo il 28 set**, quando le 74 coin a 2/3 avranno avuto la finestra: se la copertura resta sotto 40 coin, allargare a 250-300 col calcolo liberato da B2

Allargarlo aumenterebbe le monete coperte (15% contro l'obiettivo del 35%), ma un
giro dura già ~2h contro un timer di 3h.

**Serve:** prima misurare quanto dura davvero un giro, poi decidere.

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

### C3. La copertura non raggiungerà mai il 35%
**Stato:** **SUPERATA il 21 set** dalle azioni sulla copertura (B2 chiusa, semi 10→30). Si riapre solo se al 28 set la copertura è sotto 40 coin: allora si decide se il 35% ha ancora senso.

Il gate è "pronto" per numero di coppie, non per copertura: 25 monete su 164 = 15%,
contro un obiettivo del 35% che con questo tasso di passaggio non arriverà.

**Serve:** decidere se l'obiettivo del 35% ha ancora senso o va sostituito.

---

## D. Infrastruttura

### D1. Il registro su più documenti
**Stato:** aperto · rimandato 19 set, non più urgente

È l'unica correzione che **scala** davvero. Rimandata perché tocca ogni lettore —
bot, learning, quattro script, due componenti della dashboard — e farla di fretta
su un documento che contiene settimane di attesa, mentre il paper gira, trasforma
un problema di spazio in una perdita di dati.

Il formato compatto ha spostato il vincolo da 3 giorni a mesi (272 KiB su 879, 108
byte a coppia): c'è tempo per farla bene.

### D2. I dati sintetici sono attivi per default
**Stato:** **FATTO il 21 set notte** — default spento; i test lo accendono in `tests/conftest.py`, unico posto.

`BACKTEST_ALLOW_SYNTHETIC` vale `true` di default. È spento esplicitamente ovunque
si validi (unit systemd, script, workflow) e nelle analisi in lista bianca, ma
qualunque percorso nuovo che carichi candele **ricade su dati inventati in
silenzio** se Binance non risponde.

**Serve:** invertire il default e accenderlo solo nei test. Richiede di verificare
ogni chiamante.

### D3. Il modello dell'AI è la versione precedente
**Stato:** **FATTO il 21 set sera** — `ANTHROPIC_MODEL` default `claude-opus-5` (era `claude-opus-4-8`). L'env sulla VPS, se impostato, vince: `ai-stato` dice quale gira.

`ANTHROPIC_MODEL=claude-opus-4-8`. Rimandato il 19 set per non cambiare due cose
insieme mentre si verificava la chiave.

### D4. LunarCrush — RIMOSSA dal backlog il 23 set
**Stato:** **tolta su decisione del proprietario**: i dati esterni (sentiment, notizie, macro, open interest) si affrontano tutti insieme in una **sessione dedicata**, più avanti. Fino ad allora il sentiment resta un tilt di size come oggi.

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

### E2. L'AI si vede scartare quasi tutte le proposte
**Stato:** **CHIUSA il 21 set** — dal 20 set 20/20 proposte accettate a ogni giro e 2 spec di origine AI hanno passato il gate (`ai-stato`, 21 set 05:45 UTC). La correzione ha funzionato.

Diagnosi misurata (`ai_hypotheses/last`, giro delle 08:41 ora italiana):

```
1 proposta accettata su 20
rr=1.3 ×4 · rr=1.2 ×4 · rr=1 ×3 · rr=0.9 ×3   →  14 su 19
rsi_momentum: manca il parametro mid ×1
nessuna feature direzionale ×1
```

**Non** era il parametro mancante, come mi aspettavo: era `rr` sotto il minimo di
1.5. E il prompt non nominava **nessuna** fascia numerica, quindi il modello non
poteva saperlo. Corretto generando le fasce dalle stesse costanti che validano.

Resta da vedere al prossimo giro se il tasso di accettazione sale.

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

### E3. Binance risponde 451 dai runner GitHub
**Stato:** **CHIUSA il 21 set notte** — rimossi i quattro workflow che non potevano avere dati veri dai runner (optimize, discover, reset-optimizer, backtest). Tutto gira sulla VPS; niente più falsi guasti.

Blocco geografico. La ricerca e la validazione girano sulla VPS dove Binance
risponde, e i due workflow che avrebbero bisogno di dati veri hanno lo schedule
disabilitato apposta. Registrato perché a ogni controllo sembra un guasto nuovo.
