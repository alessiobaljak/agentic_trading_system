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

### A5. I take profit non guardano il grafico: sono multipli dello stop
**Stato:** **misurato il 24 set sera (ops 0210), ipotesi nella forma «massimo/minimo delle 24 ore» SMENTITA** — su 45 trade il livello strutturale sta in mediana a 3,96R, molto più lontano del primo gradino (1,5R): raggiunto nel 2% dei trade contro l'11% di TP1. Il problema non è dove stanno i bersagli, è che il prezzo non va lontano (escursione mediana 0,84R). La strada che resta è un primo gradino più basso, e la scala dal vissuto (0,75 / 1,5 / 2,25) è già fra le candidate che il gate confronta per coppia. Emersa il 24 set (domanda del proprietario su DOT: TP3 a 1,26 da un ingresso a 1,10).

Oggi ogni gradino è `multiplo × R`, con R = distanza dello stop (ATR): la scala si
adatta alla volatilità del trade, ma **non alla struttura** (massimi recenti,
bande, VWAP, livelli dove il prezzo si è già fermato). I multipli sono scelti dal
gate per coppia fra 4-5 scale fisse; TP3 a 5R è la coda, presa di rado per
costruzione. I numeri di oggi dicono che il problema è il primo gradino: 19 stop su
28 andati a favore ma sotto TP1, escursione mediana 0,84R contro un primo gradino a
1,5R.

**Cosa fare, in ordine, senza toccare nulla a mano:**
1. **Misurare** (in `mfe`): all'ingresso di ogni trade la distanza in R dalla
   resistenza/supporto più vicino (massimo/minimo delle ultime 96 barre, banda di
   Bollinger) e quante volte l'escursione l'ha raggiunta. Se il livello
   strutturale viene toccato più spesso di TP1, vale la pena.
2. **Candidata strutturale nel gate**: gradino = min(multiplo × R, livello
   strutturale), valutata per coppia accanto alle scale fisse e a quella dal
   vissuto; vince chi rende di più su OOS e holdout, come oggi.
3. **Nel bot** via `exit_logic` (parità: stessa funzione del motore).

Non si abbassa TP1 a mano sul paper: sarebbe tarare sul vissuto.

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
**Stato:** **parte meccanica FATTA il 23 set** — `bot/risk/setup_check.py`: alla chiusura ogni trade riceve un referto (`post_mortem`: classe della morte, stop largo, lock mai armato, controtrend, verdetto) scritto nel documento del trade e stampato da `trades`; la stessa aritmetica blocca PRIMA i setup con stop oltre `MAX_STOP_PCT` (6%) nel gate e nel bot. **Aggregazione FATTA il 23 set pomeriggio** — `bot/learning/referti.py`: il bot somma i referti per strategia, coin e direzione e scrive `learning/referti` a ogni refresh dei pesi, con le IPOTESI che scattano da regole dichiarate prima (vedi F1). Resta la lettura narrativa dall'AI, a 100+ trade.

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
**Stato:** **FATTA il 22 set sera su BTC, allargata il 23 a ETH, SOL, ADA, BCH** (`DISCOVERY_EXTRA`); prima candidata ADAUSDT@1h con 1 conferma il 24 set. Il resto della voce è la storia. — la spec porta il suo timeframe (id incluso), il motore etichetta la riga base col suo intervallo, `optimize` lancia a ogni giro una passata di discovery a 1h su BTCUSDT (`DISCOVERY_EXTRA=1h:BTCUSDT`, max 40 min, senza toccare il timer), il bot fa decidere ogni strategia sul suo orologio e i trade portano il timeframe della strategia. Le prime coppie BTC@1h servono 3 conferme (3 settimane). Allargare ad altre coin = cambiare `DISCOVERY_EXTRA`.

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

---

## F. Apprendimento — l'obiettivo finale

### F1. Il bot non sceglie quale trade aprire: apre tutti i segnali validi
**Stato:** aperto · **è l'obiettivo finale del proprietario** · scritto il 23 set · **primo pezzo FATTO il 23 set pomeriggio** (vedi «Cosa è stato fatto» in fondo alla voce)

Obiettivo dichiarato: *«che la scelta delle strategie e delle monete sia talmente
avanzata da scegliere praticamente sempre quella corretta che ci porti in
profitto»*. Cosa impara oggi il sistema, misurato sul codice:

| dove impara | da cosa | su cosa agisce |
|---|---|---|
| pesi strategia × regime (`compute_weights`) | win rate dei trade chiusi | **size**, panchina a peso 0 |
| freno da deriva | PF vissuto vs promesso (8 trade) | **size**, fallimento al gate |
| scala dei TP dal vissuto (`ladder_from_mfe`) | quantili di mfe | **uscite**, passando dal gate |
| keep del lock (dal 25 set: `evaluate_spec` nel gate, `keep_dal_paper`) | la storia della coppia decide fra 0,35 / 0,5 / 0,65; i verdetti prematuro/protetto del paper (tutte le coppie insieme, ≥ 8) propongono un quarto candidato: 0,25 se ≥ 60% prematuri, 0,75 se ≥ 60% protetti | **uscite**: il vincitore va in `last_params.profit_lock_keep` e motore e bot leggono lo stesso numero · `compute_trailing_keep` resta solo come ripiego per le coppie non ancora rigiudicate |
| calibrazione della confidenza | esito vs confidenza | **size** — inerte: le generate escono tutte a 60 |
| autopsia dei quasi-passaggi (B3) | 40 quasi-passaggi a giro | **proposte** dell'AI |

**Il buco:** in parità col gate il bot apre *tutti* i segnali validi del ciclo, uno
per coin. Nessun meccanismo dice «questo sì, quest'altro no»: la scelta è solo a
monte (il gate) e, lentamente, la panchina a peso zero. Tutto ciò che impara modula
size o uscite; **né gli ingressi (B8) né la selezione fra segnali**.

**Perché non si fa «a mano»:** una scelta tarata sul vissuto del paper trasforma il
paper da prova in training set — è BIRBUSDT. Le tre strade oneste, in ordine:

1. **B8** — spostare l'apprendimento nel gate: ritarare le soglie di ingresso delle
   spec in `watch`/`drift`. Alza la qualità del «sì» alla fonte.
2. **Un selettore validato**: il criterio di scelta fra segnali (peso, PF per
   regime, confidenza calibrata, mfe attesa) si simula nel backtest come una
   strategia — «apri solo i segnali che il selettore avrebbe scelto» contro «apri
   tutti» — e si misura se rende di più. Solo così la scelta è una prova, non
   un'opinione.
3. **Far parlare i referti** (B4) e l'**ombra** dell'AI (31 decisioni, 0 d'accordo
   col bot): le due fonti ricche oggi mute. Servono 100+ trade.

**A 37 trade, col paper in perdita e le short che non reggono, il profitto oggi
viene da segnali migliori (gate), non dallo scegliere fra segnali.** Il selettore ha
senso quando c'è qualcosa di buono fra cui scegliere.

**Cosa è stato fatto il 23 set pomeriggio** (richiesta: «il sistema deve imparare
da tutto quello che fa … e adattarsi tutti i giorni»; 40 trade, 6 giornate su 8 in
perdita, −50,88 realizzato):

| pezzo | dove | cosa fa | cosa NON fa |
|---|---|---|---|
| referti aggregati | `bot/learning/referti.py` → `learning/referti` | somma i referti per strategia, coin, direzione; fa scattare IPOTESI da regole scritte prima (3 short tutte perse → solo long; 3 perdite controtrend → conferma a 1 ora; 2 stop larghi → stop stretto) | non cambia nessun parametro |
| varianti nel gate (B8) | `generator.py::varianti_da_referto`, `discover_strategies.py::varianti_dai_referti` | ogni ipotesi diventa una variante della stessa spec messa nel gate (3 conferme + holdout) al posto di candidate casuali | non entra in paper senza passare il gate; non allunga il giro |
| freno di serie | `drift.py::serie_perdite`, `STREAK_BRAKE_*` | 4 perdite di fila su una strategia → size a metà, leva ×0,7, fino al primo guadagno. **SPENTO dal 24 set sera** (audit: scatta per caso al 30-44% delle strategie ogni mese; si riaccende solo se `portafoglio` misura un win rate dopo 4 perdite davvero più basso) | non spegne, non tara: frena e basta |

Il ciclo è: referto → ipotesi (regola dichiarata) → variante nel gate → se passa,
opera.

**24 set:** il disegno del selettore (punto 2) e della ritaratura periodica (punto 1)
è in `docs/disegno_cervello.md`. **Fatti il 24 set sera:** passo 0 del selettore (ogni trade simulato porta le variabili all'ingresso, `feats_ingresso`; la discovery scrive `data/selettore/<data>_<tf>.jsonl` e `selector/dataset`), passo 1 (addestramento e confronto offline «apri tutto» vs «selettore», comando ops `selettore`, chiave da aggiungere alla lista bianca), punto 1 (l'intorno, vedi B8). Aperti: passi 2 e 3 del selettore (ombra, poi accensione) dopo il verdetto del passo 1. Il paper non tara nulla da solo. **Il selettore validato (punto 2) e la
lettura AI dei referti (B4) restano aperti**: servono 100+ trade.

### F1bis. Il «paper esplorativo» — proposto il 25 set, **FATTO il 25 set** (il proprietario ha detto sì)
Il proprietario ha chiesto di imparare il più possibile da ogni chiusura e ha detto che in paper si può rischiare di più per validare ipotesi. Proposta: le coppie che passano per un pelo (quasi-passaggi, ~36 a giro) si operano in paper a un quarto della size, marcate `esplorativa`, escluse da pesi e freno; il gate le giudica anche col loro vissuto. Rischio: l'equity del paper si sporca di trade più deboli (per questo size ridotta e contatore separato). Simile a F2 ma senza le due settimane e senza rifare il ciclo.

**Fatto il 25 set:** a fine giro il gate sceglie fino a 20 quasi-passaggi (mancato più piccolo, una coppia per coin, non validate, spec generata, coin nell'universo) e li scrive in `strategy_registry/esplorative` (`pairs`, `specs`, `storia`; ciclo di vita: resta finché quasi-passaggio o vista entro 2 giri, validata → storia «validata», sparita da > 2 giri → «scartata»; `scripts/discover_strategies.py::pubblica_esplorative`, fail-open). Il bot le carica ogni ora con le spec (`adaptation.esplorative_for`), le opera SOLO in DRY_RUN, a un quarto della size (`ESPLORATIVA_SIZE_MULT=0.25`), al massimo 3 aperte insieme (`ESPLORATIVE_MAX_APERTE`, rifiuto «esplorative al tetto» contato), e una validata sulla stessa coin vince sempre. Il trade porta `esplorativa: true` (posizione persistita, `ClosedTrade`, badge «espl.» in dashboard). Fuori: pesi, keep del trailing, deriva (globale e per coppia), calibrazione, i numeri di `paper` nel controllo orario e in `trades`. Dentro: referti (con il conteggio `esplorative`), scala e keep letti dal gate (più dati è il punto). **Metro:** dopo 100 trade esplorativi, quante coppie esplorative sono poi passate il gate contro quante scartate — si legge in `gate` («ESPLORATIVE: N attive · validate poi X · scartate Y»), in `trades` («PAPER ESPLORATIVO») e in `dashboard/gate.giro.esplorative`. Numeri di partenza: 0 trade esplorativi, 0 coppie (il primo giro col codice nuovo le sceglie). Se a 100 trade le «validate poi» sono zero, il paper esplorativo si spegne (`ESPLORATIVE_ENABLED=false`).

### F1ter. Selettore in ombra: attivo dal 25 set (passo 2 del disegno)
Il modello (che ancora NON BATTE «apri tutto», ops 0231) dà a ogni trade aperto dal bot la sua `p` e la scrive sul trade (`selector_p`, `selector_soglia`) e nel log `[selettore]`; `trades` stampa «SELETTORE IN OMBRA» (p media vinti vs persi, PnL sopra soglia vs tutti, correlazione da 10 trade). Si accende solo se batte su 2 finestre su 3 E la calibrazione sul paper non è piatta con ≥ 40 trade con p. Divergenze dichiarate fra bot e gate: stop del risk gate invece di quello grezzo, ora della decisione, contesto BTC fino a 60 minuti vecchio. Da mostrare in dashboard (colonna p nei trade chiusi) quando ci saranno i primi trade con p.

### F2. Il gate a due livelli: «candidata» in paper a size ridotta, «validata» a size piena
**Stato:** proposta del 23 set pomeriggio · **aspetta il sì del proprietario** · non si tocca il gate senza

Domanda del proprietario: *«se una strategia in backtest funziona, poi sarà il paper
a validarla nelle settimane successive: possiamo rivedere le tre settimane del gate?»*

Quello che le 3 conferme fanno davvero: **non servono al paper, servono contro i
falsi positivi**. Passa lo 0,3% delle candidate; con una sola finestra passerebbero
molte strategie fortunate. E non sono tre settimane fisse: 3 pass con almeno 7 giorni
di dati nuovi fra uno e l'altro (`NEW_DATA_MIN_HOURS=168`) = minimo 14 giorni.

Perché «conferma il paper» da solo non basta: a 4-5 trade al giorno su 59 coppie,
una coppia arriva a 8 trade in settimane — più lento del gate, non più veloce. E se
il criterio si decide dopo aver visto i risultati, è BIRBUSDT al contrario.

**Proposta:** due livelli, senza accorciare nulla.
* **candidata** (1 pass + holdout): entra in paper subito, a un quarto della size, e
  continua a raccogliere conferme nel gate;
* **validata** (3 pass): size piena, come oggi;
* regole d'uscita scritte PRIMA: deriva confermata o bocciatura nel gate = fuori;
  statistiche del paper separate per livello.

Si guadagna: più coin in paper e prima (oggi 27 su 165), più dati per il cervello,
falsi positivi limitati dalla size. Costa: più coppie da rivalutare nel giro (il
cronometro decide), paper più rumoroso se i due livelli non restano separati.

## G. Portafoglio e gate — quello che i sistemi seri fanno (24 set)

### G1. Rischio per direzione
**Stato:** **esisteva già dall'8 set** (`MAX_DIRECTIONAL_RISK_PCT=0.03`, `bot/main.py::_directional_risk_blocks`): l'audit del 24 set ha trovato che il 24 mattina ne avevo scritta una seconda copia, tolta la sera stessa. Nel bot la regola è una. Il backtest di portafoglio (G2, ops 0188 con la semantica del bot) dice che al 3% è quasi neutra (64 trade su 526 fermati, PnL −7%, drawdown invariato); con la size dimezzata dal freno globale ammette ~8 posizioni nello stesso verso: le regole di portafoglio che mancano davvero sono lo stop giornaliero e il netto in R (vedi H).

### G2. Il gate valida coppie una alla volta, mai il portafoglio
**Stato:** **script FATTO il 24 set** (`portafoglio`, da aggiungere alla lista bianca: `portafoglio: .venv/bin/python -m scripts.portafoglio_backtest`) — tutte le validate insieme sugli ultimi 60 giorni con i limiti veri del conto: trade al giorno, posizioni contemporanee, quante nella stessa direzione, giornate in utile/perdita, drawdown, e il confronto con/senza tetto per direzione. Dal 24 set sera simula anche lo stop giornaliero di portafoglio e il netto in R come what-if, misura il win rate dopo k perdite di fila (per decidere il freno di serie) e il diversification ratio. Aperto: leggerlo ogni settimana e decidere le regole di portafoglio sui suoi numeri (H).

### G3. La statistica t è misurata ma non decide
**Stato:** **misura FATTA il 24 set** — `last_t` nel registro per ogni validata (scritto dalla discovery, cioè per tutte le generate), `gate` stampa quante reggerebbero t ≥ 2 e la mediana. L'audit propone t ≥ 3 come criterio (con centinaia di candidate per coin, 2 è il livello del rumore): **si decide dopo aver visto il numero** (H).

### G4. Meno candidate a caso
**Stato:** **FATTO il 24 set** — `DISCOVERY_RANDOM_MAX=40` (erano 100 a giro). Metro: tasso di passaggio in `gate_autopsy` prima e dopo (0,3% il 23 set).

### G6. La pesatura di recenza nel gate esiste ma nessuno la chiama
**Stato:** **fatta a metà il 25 set, la metà che non cambia chi entra.** Nella discovery la SCELTA fra scale di TP, break-even e keep del lock (`_metrica_scelta` in `discover_strategies.py`) pesa i trade con l'emivita di 180 giorni (`GATE_RECENCY_HALFLIFE_DAYS`, 0 = uniforme): prima sette giorni nuovi su 4,6 anni valevano lo 0,42% dell'evidenza e la scelta non si spostava mai. I criteri di validazione (PF, win rate, ritorno, consistenza, holdout) restano NON pesati, per costruzione: il tasso di passaggio non cambia. Resta aperta l'altra metà — pesare anche la validazione — che cambia quali coppie entrano: va decisa con il tasso di passaggio prima/dopo come metro, e per ora non si fa.

### G5. Sopravvivenza dell'universo
**Stato:** aperto · noto — si valida sulle coin oggi nel top 200 per volume e si saltano le delistate: le strategie sono provate solo su chi è sopravvissuto. Da tenere a mente nel giudizio dei numeri; nessuna correzione semplice.

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

### H1. La statistica t come criterio del gate (t ≥ 3)
Passa lo 0,3% delle candidate; il 70-77% delle coppie a 1-2 conferme non ripassa:
firma del massimo di un rumore selezionato. `gate` stampa quante validate reggono
t ≥ 2 e la mediana: **si decide dopo quel numero**. Metro: tasso di passaggio in
`gate_autopsy` prima e dopo.

### H2. Holdout non condiviso fra candidate
Migliaia di candidate per giro puntano lo STESSO holdout di 45 giorni (PF ≥ 1,05 su
5 trade: sotto il caso lo passa circa metà). Proposta: `GATE_HOLDOUT_MIN_TRADES` a
10 e finestra di holdout per candidata (hash dell'id → mese fra gli ultimi 12).

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

### I2. Il freno globale non ha una data di uscita
Dimezza tutto finché il PF a 30 giorni non supera 0,6 × 1,89 ≈ 1,13. È il freno più forte del sistema e non compariva in nessun log: ora `stato` lo scrive. Il paper a size dimezzata impara più lentamente (meno euro per trade, stessi trade).

### I3. Il keep del trailing non scatterà mai con questi volumi
**Stato:** **FATTO il 25 set** (richiesta del proprietario: «ogni dato raccolto deve arrivare al cervello e produrre una decisione»). Il numero che l'ha deciso: 8 verdetti per strategia contro 14 uscite trailing in 10 giorni su 21 strategie, quindi l'adattamento del bot non sarebbe mai scattato; e se fosse scattato, il gate avrebbe continuato a simulare keep 0,5 (paper e gate divergenti). Ora il keep è un parametro PER COPPIA scelto dal gate come la scala dei TP e il break-even: `evaluate_spec` prova 0,35 / 0,5 / 0,65 sulla scala e sul break-even già scelti (3 backtest in più per ogni spec che passa, non per le bocciate), il vincitore va in `last_params.profit_lock_keep`, motore e bot lo leggono con la stessa funzione (`lock_keep`). Il paper entra come in `scala_dal_paper`: `keep_dal_paper` somma i verdetti di TUTTE le coppie e, con almeno 8, propone un quarto candidato (0,25 se ≥ 60% prematuri, 0,75 se ≥ 60% protetti) che il gate mette a confronto con gli altri: il paper propone, la storia decide. Le coppie non ancora rigiudicate col nuovo parametro continuano col keep con cui sono state validate (chiave assente → comportamento di prima), quindi il registro misto non rompe la parità. Visibile in `gate` (riga «keep del lock scelto dal gate») e nel log del giro (`[paper] N verdetti trailing…`, `[cervello] keep…`). Da misurare nelle prossime settimane: quante coppie finiscono su 0,35 e quante su 0,65, e se sul paper i prematuri calano.

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

### I6. Il cap di 5 posizioni è spento in parità
`MAX_OPEN_POSITIONS` vale solo fuori dalla parità col gate; in parità il limite è il margine (10% dell'equity per posizione ≈ 10 posizioni); il paper ha già toccato 7 contemporanee. Con 160 coppie e il freno che dimezza la size, il tetto per direzione (3%) ammette ~8 posizioni nello stesso verso. Da decidere con `portafoglio` sulle 160 (in coda): cap in parità, o tetto direzionale più stretto finché il globale è in deriva, o stop giornaliero (H3).

## J. Controllo orario e dashboard (25 set)

Fatto il 25 set su richiesta del proprietario («check di tutto in automatico, le evidenze in dashboard ogni ora, la dashboard come un sistema serio»): il bot scrive ogni ora `dashboard/controllo` (`bot/learning/controllo.py`, schema in `docs/controllo_schema.md`), la discovery scrive `dashboard/gate` a ogni giro, la dashboard passa da 6+1 tab a 4+1 con il Controllo in prima pagina e 16 pannelli tolti. Rimandato, con il motivo:

### J1. Totali «da sempre» del paper ricalcolati a ogni ora
Il controllo rilegge tutti i trade chiusi ogni ora (oggi 55: costa niente). Oltre ~5.000 trade servono somme incrementali aggiornate a ogni chiusura. Metro: `meta.durata_ms` nel controllo (anomalia `CONTROLLO_LENTO` oltre 2 s).

### J2. «Cosa aspetta il sì» non è persistito
Le voci in attesa del sì vivono qui nel backlog: il controllo le lascia `null` e lo dice. Persisterle (un doc scritto dal controllo del mattino) è possibile ma è un altro posto da tenere allineato a mano; si fa solo se il proprietario vuole vederle in dashboard.

### J3. Il ripiego GitHub del controllo è lento quanto GitHub
Se il bot è fermo, il controllo lo scrive lo snapshot di GitHub (ogni 2 ore sulla carta, 3-7 ore misurate). La dashboard lo segnala con «scritto dal ripiego» e il rosso oltre 2 ore: è voluto, un controllo vecchio È l'evidenza che qualcosa è fermo. Un timer sulla VPS (`ops controllo --publish`) sarebbe più regolare ma non aggiunge informazione: se il bot è giù lo dice il battito.

### J4. Non verificato dal vivo
La dashboard nuova è verificata con tipi, build e un test di parità campo per campo fra chi scrive (Python) e chi legge (TypeScript), non in un browser né con dati veri (nessun accesso a Firebase da qui): il ripiego RTDB→Firestore, la resa su telefono e le liste RTDB rese come oggetti vanno guardate dal proprietario al primo giro. Da segnalare qui ciò che non torna.

### J5. Contatori che vivono in RAM
`rifiuti_24h`, `errori_ciclo_1h` e `riavvii_24h` si azzerano al riavvio del bot (lo dicono `rifiuti_24h_dal` e l'anello `/avvii`). Persisterli su RTDB costa una scrittura per rifiuto: non ora.

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
**Stato:** **FATTO il 21 set sera** — `ANTHROPIC_MODEL` default `claude-opus-5`. Dal 24 set il proprietario ha scelto sulla VPS `claude-opus-4-8` (più economico): l'env vince sul default, `ai-stato` dice quale gira.

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
