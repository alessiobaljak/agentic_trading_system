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
**Stato:** aperto · emerso 19 set, confermato dal proprietario il 20 set

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
**Stato:** aperto · emerso 20 set

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

### A3. La manopola del rischio non fa quello che dice
**Stato:** aperto · emerso 18 set

L'utente imposta 1% e il sistema rischia ~0,35-0,39%, variabile col trade: il cap
del 10% per posizione morde quasi sempre, e più lo stop è largo meno si rischia.

**Serve:** decidere se il cap per posizione deve restare al 10%. Non è un difetto
da riparare di nascosto — è una scelta. Toccarlo cambia la size a metà esperimento.

### A4. Non sappiamo quanto vive una strategia validata — e distruggiamo la prova
**Stato:** aperto · **la più importante di questa sezione** · emerso 21 set

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

**Serve (piccolo, e non tocca l'esperimento):** scrivere una riga durevole a ogni
purge e a ogni promozione — chiave, `pass_count` raggiunto, quando è entrata,
quando è uscita, con che PF. Fra qualche settimana quella collezione risponde da
sola: vita mediana di una coppia validata, quante muoiono entro la prima finestra,
se le generate durano più o meno delle base. Senza, fra un mese saremo allo stesso
punto di oggi.

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
**Stato:** aperto · **la più importante di questa sezione** · emerso 19 set

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
**Stato:** aperto · misurato ogni giorno

```
strategie base: 1312 valutazioni, 0 passate (0,00%)
registro: 2024 coppie base · 574 generate
```

Le 8 strategie a mano non producono una singola coppia validata da quando il
registro esiste, e occupano il 78% del registro.

**Serve:** decidere se continuare a valutarle. Toglierle libererebbe tempo di
calcolo e spazio; tenerle costa poco ma il conto è zero da settimane.

### B2bis. `rr` non serve a niente, ma scarta il 74% delle proposte AI
**Stato:** aperto · emerso 20 set

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
**Stato:** aperto · emerso 19 set

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
**Stato:** aperto · ricerca fatta il 20 set (30 agenti, 23 candidati, 8 confermati)

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
**Stato:** aperto · **la raccomandazione numero uno** · verificato con le mani 20 set

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
**Stato:** aperto · emerso 20 set

Sembra la soluzione ovvia e non lo è. Oggi non registriamo nulla
(`bot/execution/executor.py:184` salva il sentiment solo dentro il singolo trade),
il gratuito di CoinGecko non regge un polling continuo (lo dice il repo stesso in
`bot/agents/market_scanner.py:166`), **23 delle 25 coppie validate non hanno
nemmeno un id CoinGecko**, e soprattutto il backtest consuma **solo candele**
(`bot/core/indicators.py:119`): non esiste un canale per una serie esterna.

**Serve:** prima costruire il canale nel backtest, poi cominciare a registrare.

---

## C. Timeframe e universo

### C1. A 1 ora le strategie vanno molto meglio
**Stato:** aperto · misurato 15 set (sonda `timeframe_probe`)

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
**Stato:** aperto · rimandato per scelta

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
**Stato:** da decidere

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
**Stato:** parzialmente chiuso · 19 set

`BACKTEST_ALLOW_SYNTHETIC` vale `true` di default. È spento esplicitamente ovunque
si validi (unit systemd, script, workflow) e nelle analisi in lista bianca, ma
qualunque percorso nuovo che carichi candele **ricade su dati inventati in
silenzio** se Binance non risponde.

**Serve:** invertire il default e accenderlo solo nei test. Richiede di verificare
ogni chiamante.

### D3. Il modello dell'AI è la versione precedente
**Stato:** aperto · banale

`ANTHROPIC_MODEL=claude-opus-4-8`. Rimandato il 19 set per non cambiare due cose
insieme mentre si verificava la chiave.

### D4. LunarCrush: abbonamento scaduto
**Stato:** da decidere · emerso 19 set

HTTP 402. È una fonte di sentiment **opzionale** e il sistema ricade su CoinGecko
(funzionante), quindi non è rotto niente. Da rinnovare o da togliere: una chiave
scaduta in configurazione è rumore che a ogni controllo sembra un guasto.

---

## E. Da tenere d'occhio (non ancora azioni)

### E1. Le short perdono sistematicamente
**Stato:** in osservazione · aggiornato 20 set

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
**Stato:** corretto 20 set · in attesa di conferma al prossimo giro

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

### E3. Binance risponde 451 dai runner GitHub
**Stato:** noto e gestito · nessuna azione

Blocco geografico. La ricerca e la validazione girano sulla VPS dove Binance
risponde, e i due workflow che avrebbero bisogno di dati veri hanno lo schedule
disabilitato apposta. Registrato perché a ogni controllo sembra un guasto nuovo.
