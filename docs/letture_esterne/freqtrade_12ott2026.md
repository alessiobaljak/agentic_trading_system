# Freqtrade — riassunto in sola lettura (12 ott 2026)

Letto da: `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/repos/freqtrade`
(clone superficiale, 1 solo commit nella storia locale). Nessuno script eseguito, nessuna installazione.
I percorsi qui sotto sono relativi a quella cartella. I numeri «da GitHub» vengono dall'API pubblica
del repository (lettura metadati, 12 ott 2026); l'elenco delle issue non era leggibile da questa
sessione (accesso negato), quindi i «problemi frequenti» vengono solo da FAQ e modelli di issue.

---

## 1. Cos'è, da quanto esiste, quanto è mantenuto, chi lo usa

**Cos'è.** Un bot di trading crypto open source in Python (spot e futures perpetui), con backtest,
ottimizzazione dei parametri («hyperopt»), un modulo di apprendimento automatico (FreqAI), dry-run,
Telegram, API REST e interfaccia web. Si appoggia a `ccxt` per parlare con gli exchange.
Fonte: `README.md`, `docs/index.md`, `pyproject.toml`.

**Da quando.** Repository creato il **17 maggio 2017** (da GitHub). Le FAQ citano ancora la release
0.15.1 (`docs/faq.md`, sezione hyperopt) e `docs/deprecated.md` parla di opzioni deprecate nel 2018.

**Quanto è mantenuto.**
* Ultimo commit locale: **12 ott 2026 06:56 (+0200)**, «Merge pull request #13665 … renovate/python-minor-patch»
  (da `git log` sul clone). Ultimo push visto da GitHub: 12 ott 2026 17:37 UTC.
* Versione: **`2026.10-dev`** (`freqtrade/__init__.py`). Il numero è anno.mese: release mensili;
  il supporto copre solo l'ultima release e il ramo di sviluppo (`docs/faq.md`, «Support policy»).
* Licenza: **GPLv3** (`LICENSE`, `pyproject.toml`). Attenzione: è copyleft. Copiare *codice* dentro
  un repository pubblico come quello del proprietario obbliga a rispettare la GPL; copiare *idee* no.
* Dimensione: 64 MB senza `.git`; 487 file `.py`; ~65.700 righe nel pacchetto `freqtrade/`,
  ~79.800 righe in `tests/` (104 file di test). Richiede Python ≥ 3.12.
* CI: 10 workflow in `.github/workflows/` (ci, docker, docs, aggiornamento tier di leva Binance, ecc.).
* Da GitHub: **55.307 stelle, 11.428 fork, 33 issue aperte** (poche per la dimensione: triage attivo).

**Chi lo usa.** Comunità ampia (Discord ufficiale, repository separato `freqtrade-strategies`), progetti
terzi elencati in `docs/includes/showcase.md` (strat.ninja per i backtest, frequenthippo per statistiche
di dry/live, remotepairlist, FTUI). FreqAI è pubblicato sul Journal of Open Source Software (2022,
`docs/freqai.md`). La policy dei contributi è dura con l'IA: niente issue scritte da modelli, e
«strategia generata da un'IA che non funziona» è elencata come caso tipico da chiudere
(`CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/*.md`).

Exchange: spot 12 (Binance, Bybit, OKX, Kraken, Gate, Bitget, HTX, Hyperliquid, …), futures 7
(Binance, Bitget, Bybit, Gate, Hyperliquid, Kraken, OKX). `README.md`.

---

## 2. Architettura e come si definisce una strategia

**Componenti principali** (cartella `freqtrade/`):

| Componente | Dove | Note |
|---|---|---|
| Exchange | `exchange/exchange.py` (4.380 righe) + un file per exchange | sopra `ccxt`; contiene anche la simulazione ordini del dry-run |
| Ciclo del bot | `freqtradebot.py` (2.837 righe), `worker.py` | gira ogni ~5 s (`process_throttle_secs`); gli indicatori si ricalcolano una volta per candela (`docs/bot-basics.md`) |
| Strategia | `strategy/interface.py` (classe `IStrategy`, 1.908 righe) | vedi sotto |
| Backtest | `optimize/backtesting.py` (1.977 righe) | un ciclo per candela e per coppia |
| Hyperopt | `optimize/hyperopt/`, `optimize/hyperopt_loss/` (13 funzioni di perdita) | usa `optuna` (campionatore NSGA-III) (`docs/hyperopt.md`) |
| Analisi anti-bias | `optimize/analysis/lookahead.py`, `recursive.py` | comandi `lookahead-analysis`, `recursive-analysis` |
| FreqAI | `freqai/` (data_kitchen, data_drawer, 15 modelli in `prediction_models/`) | LightGBM, XGBoost, CatBoost, RandomForest, PyTorch MLP/Transformer, reinforcement learning |
| Protezioni | `plugins/protections/` (4 classi) | blocchi temporanei del trading |
| Liste coppie | `plugins/pairlist/` | statiche o dinamiche (volume, spread, …) |
| Persistenza | `persistence/` | SQLite via SQLAlchemy |
| Controllo | `rpc/` (Telegram, API REST FastAPI, webhook); freqUI è un progetto separato | |

**Come si scrive una strategia** (`docs/strategy-101.md`, `docs/strategy-customization.md`,
`freqtrade/templates/sample_strategy.py`):
* Una classe Python che eredita da `IStrategy` con tre metodi su un DataFrame pandas:
  `populate_indicators` (aggiunge colonne-indicatori), `populate_entry_trend` (mette 1 in `enter_long`
  / `enter_short`), `populate_exit_trend` (`exit_long` / `exit_short`). Il bot non usa mai la candela in
  corso: solo candele chiuse (`docs/faq.md`, «I want to use incomplete candles»).
* Attributi di classe: `timeframe`, `stoploss` (es. `-0.10`), `minimal_roi` (tabella minuti → profitto
  minimo per uscire, es. `{"0": 0.04, "30": 0.02, "60": 0.01}`), `trailing_stop`,
  `trailing_stop_positive`, `trailing_stop_positive_offset`, `trailing_only_offset_is_reached`,
  `order_types` (entry/exit/stoploss/emergency_exit: `limit` o `market`, più `stoploss_on_exchange`),
  `order_time_in_force`, `can_short`, `startup_candle_count`, `use_exit_signal`, `exit_profit_only`,
  `position_adjustment_enable`, `unfilledtimeout`.
* Callback opzionali (tutti in `strategy/interface.py`): `custom_stoploss` (stop dinamico, mai più largo
  dello `stoploss` fisso), `custom_roi`, `custom_exit`, `custom_entry_price` / `custom_exit_price`,
  `adjust_order_price` (cancella e ripiazza un ordine limite non eseguito), `check_entry_timeout` /
  `check_exit_timeout`, `confirm_trade_entry` / `confirm_trade_exit`, `custom_stake_amount`,
  `adjust_trade_position` (DCA, uscite parziali), `leverage`, `order_filled`, `bot_loop_start`,
  `informative_pairs` e il decoratore `@informative` per timeframe superiori senza lookahead.
* Stop: statico, trailing, trailing con offset positivo, trailing solo dopo un offset, custom; stop
  sull'exchange (stop-market o stop-limit con `stoploss_on_exchange_limit_ratio` 0.99, aggiornato ogni
  60 s, `emergency_exit` a mercato se non si riesce a piazzarlo); su futures `stoploss_price_type`
  last/mark/index (`docs/stoploss.md`). Con leva, lo stop è «rischio sul capitale proprio»: stop 10% a
  10x scatta su un movimento dell'1% (`docs/stoploss.md`, «Stoploss and Leverage»).
* Parametri ottimizzabili dichiarati come `IntParameter`, `DecimalParameter`, `CategoricalParameter`
  con uno spazio (`buy`, `sell`, `protection`, …) (`docs/hyperopt.md`).

---

## 3. Backtest e validazione

**Modello dei costi.**
* Commissioni: se non passi `--fee`, usa **il caso peggiore** fra taker e maker della prima coppia,
  al livello più basso dell'exchange, e la applica due volte (entrata e uscita)
  (`optimize/backtesting.py`, `set_fee`, righe 268-281; `docs/backtesting.md`).
* **Slippage: nessuno nel backtest.** Testuale: «All orders are filled at the requested price (no
  slippage) as long as the price is within the candle's high/low range» (`docs/backtesting.md`,
  «Assumptions made by backtesting»). L'unica traccia è nelle funzioni di perdita Sharpe/Sortino
  giornaliere, che sottraggono 0,05% a trade (`optimize/hyperopt_loss/hyperopt_loss_sharpe_daily.py`,
  riga 38). Lo schema di configurazione suggerisce di gonfiare `fee` «per simulare lo slippage»
  (`config_schema/config_schema.py`, riga 186).
* Funding dei perpetui: calcolato nel backtest se ci sono i dati dei tassi
  (`backtesting.py`, `_run_funding_fees`); se mancano, `futures_funding_rate: 0` con avviso esplicito
  «This will mean your backtests are inaccurate» (`docs/leverage.md`).
* Limiti di quantità/precisione: quelli attuali dell'exchange, non quelli storici (`docs/backtesting.md`).

**Fill degli ordini limite** (`backtesting.py`):
* Regola unica: l'ordine è eseguito se `low ≤ prezzo ≤ high` della candela (`_get_order_filled`,
  riga 787). Nessun fill parziale, nessun volume, nessuna coda nel book.
* Entrata di default all'`open` della candela successiva al segnale; con `custom_entry_price` il
  prezzo viene forzato dentro la candela (`min(prezzo, high)` per i long) (`get_valid_entry_price_and_stake`).
* Un ordine limite non eseguito resta aperto nelle candele seguenti fino al timeout
  (`unfilledtimeout`, `check_entry_timeout`) o alla sostituzione (`adjust_order_price`); il report conta
  «Entry/Exit Timeouts», ordini cancellati e sostituiti (`check_order_cancel`, `check_order_replace`).
* Stop: esce **esattamente al prezzo di stop**, non al low (ma la perdita include 2 commissioni); se la
  candela apre già oltre lo stop, esce all'open. Sul trailing scattato nella candela di entrata si
  assume il caso peggiore (prezzo sale fino all'offset e crolla). Ordine di valutazione nella stessa
  candela: segnale di uscita → stop → ROI → trailing; «il low avviene prima dell'high» per lo stop.
  Fonti: `_get_close_rate_for_stoploss`, `_get_close_rate_for_roi`; `docs/backtesting.md`.
* `--timeframe-detail 5m` (o 1m): valuta le candele con trade aperto su un timeframe più fine per
  simulare il movimento intra-candela; la doc dice che le strategie che reggono anche così «hanno buone
  probabilità» in dry-run, ma che «solo il forward testing può confermare».

**Controlli di lookahead** (il pezzo più interessante per il proprietario):
* `lookahead-analysis` (`optimize/analysis/lookahead.py`, righe 66-200): fa un backtest completo come
  base; poi, per ognuno dei primi N trade (default 20), **rifà il backtest con i dati tagliati alla
  candela di entrata (+1) e alla candela di uscita (+1), su quella sola coppia**, e verifica (a) che il
  segnale esista ancora nella stessa data e (b) che le colonne-indicatori siano identiche
  (`DataFrame.compare`). Forza ordini a mercato, protezioni spente, portafoglio «infinito» per evitare
  falsi positivi. Limiti dichiarati: segnali mai scattati non vengono verificati (falsi negativi);
  logiche che dipendono dalla lista coppie danno falsi positivi (`docs/lookahead-analysis.md`).
* `recursive-analysis` (`optimize/analysis/recursive.py`): ricalcola gli indicatori con diversi
  `startup_candle_count` (es. 20, 40, 80, 100, 150, 300, 999) e stampa la varianza % dell'ultima riga.
  Serve a scoprire perché live e backtest divergono: in live il bot vede meno candele
  (`docs/recursive-analysis.md`).
* La doc elenca gli errori classici: `shift(-1)`, `.iloc[-1]` nei `populate_*`, medie su tutta la
  colonna invece di `rolling()`, `resample` senza `label='right'`, `merge` fra timeframe
  (`docs/strategy-customization.md`, «Common mistakes»). E avverte: un esito negativo «non garantisce»
  l'assenza di bias.

**Walk-forward e fuori campione: non ci sono.** Zero occorrenze di «walk forward» / «out of sample» in
`docs/` e in `freqtrade/` (grep). Hyperopt ottimizza *dentro* il periodo scelto; l'unico consiglio è
usare `--timerange` per un «test-set più piccolo» (`docs/hyperopt.md`). L'unica cosa simile a un
walk-forward è il backtest di FreqAI (finestra scorrevole addestra 30 giorni / prova 7, vedi §4).

**Hyperopt e funzioni di perdita** (`docs/hyperopt.md`, `optimize/hyperopt_loss/`): spazi `buy`,
`sell`, `roi`, `stoploss`, `trailing`, `protection`, `trades`; 13 funzioni di perdita: ShortTradeDur
(legacy), OnlyProfit, Sharpe, SharpeDaily, Sortino, SortinoDaily, MaxDrawDown, MaxDrawDownRelative,
MaxDrawDownPerPair (ottimizza la coppia peggiore, per non farsi gonfiare da una sola), Calmar,
ProfitDrawDown, MultiMetric (profitto × fattore di profitto × expectancy × win-rate, con penalità sotto
50 trade: `hyperopt_loss_multi_metric.py`). `--early-stop`. Le FAQ consigliano fino a 10.000 epoche e
ammettono che lo spazio di ricerca è dell'ordine di «80 miliardi» di combinazioni (`docs/faq.md`).

**Cosa dice la doc sull'overfitting.** Poco e in modo indiretto:
* «ogni valore più preciso di 3 decimali di solito produce risultati overfittati» (`docs/hyperopt.md`,
  righe 664/706/744);
* «usare solo le coppie vincenti porta a una strategia overfittata» (`docs/utils.md`, riga 336);
* la nota sul **p-value del profitto medio** nel report di backtest: test t sulla media per trade, ma
  «il test assume trade indipendenti … è un limite inferiore ottimistico» e «poiché backtest e hyperopt
  valutano molte strategie, alcune avranno un p-value basso per puro caso» (`docs/backtesting.md`,
  «Reading the mean profit p-value»). È l'unica frase sul problema dei confronti multipli;
* «il backtest non sostituirà mai il dry-run»; «i risultati passati non garantiscono il futuro»
  (`docs/backtesting.md`, riga ~589); «è molto facile distorcere i risultati perché una strategia sembri
  più redditizia di quanto sia» (`docs/strategy-101.md`, riga 140).

**Report di backtest** (`docs/backtesting.md`): tabella per coppia, per `enter_tag`, per motivo di
uscita (roi / exit_signal / stop_loss / trailing / force_exit), metriche Sharpe/Sortino/Calmar (su trade
chiusi e su saldo giornaliero), SQN, p-value, profit factor, expectancy, drawdown assoluto e relativo,
«Rejected Entry signals», timeouts, `--breakdown month year`. `backtesting-analysis` stampa i valori
degli indicatori sulla candela di entrata e di uscita di ogni trade (`docs/advanced-backtesting.md`):
utile per la domanda «perché perdiamo».

---

## 4. FreqAI

**Cosa fa** (`docs/freqai.md`, `docs/freqai-running.md`, `docs/freqai-feature-engineering.md`):
* Apprendimento supervisionato (regressione o classificazione) sulle feature che scrivi tu nella
  strategia (`feature_engineering_expand_all/basic/standard`), con espansione automatica su più
  periodi, timeframe e coppie «informative» (anche 10.000+ feature). Il target lo definisci in
  `set_freqai_targets`; l'esempio è «media del close dei prossimi N candele / close attuale»
  (`templates/FreqaiExampleStrategy.py`, righe 192-197).
* Finestra scorrevole: `train_period_days` (es. 30) / `backtest_period_days` (es. 7); in live
  riaddestra di continuo in un thread separato (`live_retrain_hours`, `expiration_hours`).
* Modelli (`freqai/prediction_models/`): LightGBM, XGBoost (anche RF), CatBoost (via config),
  RandomForest sklearn, PyTorch MLP e Transformer, reinforcement learning (stable_baselines3).
* Pipeline dati: normalizzazione, rimozione outlier con Dissimilarity Index (distanza dal set di
  addestramento, usato anche come «incertezza» della previsione), SVM, DBSCAN; PCA; rumore gaussiano
  opzionale «per prevenire l'overfitting» (`docs/freqai-parameter-table.md`).

**Come valuta i modelli.** Split train/test con `test_size` (default 0,1; 0,25 nell'esempio;
`freqai/data_kitchen.py`, riga 145; `base_models/BaseRegressionModel.py`); l'insieme di test va in
`eval_set` per l'early stopping delle librerie (`prediction_models/LightGBMRegressor.py`, riga 33).
Non c'è un report di accuratezza proprio: si usa la metrica della libreria, Tensorboard, e in strategia
la deviazione standard del target (`&-*_std/mean`) per filtrare le previsioni «rare» (z-score 1,25
nell'esempio, `docs/freqai-configuration.md`). Il backtest FreqAI addestra un modello per finestra: è
la cosa più vicina a un walk-forward in freqtrade, ma la doc avverte che le feature sono calcolate
una volta su tutto il periodo («you should be sure that features do not look-ahead»), mentre i target
sì per finestra (`docs/freqai-running.md`). Non si può fare hyperopt sulle feature: le previsioni sono
salvate e riusate, si ottimizzano solo le soglie di entrata/uscita.

**Cosa dichiarano sui rischi.**
* La strategia di esempio «non è progettata per andare in produzione» (`docs/freqai.md`, «Not for production»).
* `continual_learning`: «approccio ingenuo … alta probabilità di overfitting o di restare in un minimo
  locale mentre il mercato si allontana dal modello» (`docs/freqai-running.md`).
* Reinforcement learning: «agenti mal addestrati possono trovare "trucchi" per massimizzare la
  ricompensa senza vincere davvero nessun trade»; l'ambiente di addestramento «NON è» il backtest
  reale (`docs/freqai-reinforcement-learning.md`).
* «Il modo migliore per provare davvero un modello è farlo girare in dry-run» (`docs/freqai-running.md`).
* Avviso di sicurezza sul caricare modelli pickle non propri.
* Nessuna affermazione, da nessuna parte, che FreqAI renda.

---

## 5. Esecuzione

**Ordini limite vs mercato** (`docs/includes/pricing.md`, `docs/exchanges.md`, `exchange/exchange.py`):
* Prezzo preso dal ticker o dal book (`use_order_book`, `order_book_top`), lato `same` (non attraversa
  lo spread, commissione maker probabile) o `other` (attraversa: si comporta quasi come un market con
  prezzo massimo, commissione taker). Su **Binance futures il book è obbligatorio** perché non c'è
  ticker (`docs/exchanges.md`, «Binance Futures»), e Binance ha «regole quantitative» che puniscono
  troppi ordini piccoli.
* In **dry-run** la simulazione è concreta (`exchange.py`, righe 1206-1445): un ordine limite si
  considera eseguito quando il miglior ask (per un buy) scende sotto il limite, controllato a ogni ciclo
  sul book L2 (`_dry_is_price_crossed`); un limite che attraversa lo spread di più dell'1% viene
  convertito in market; un market viene riempito **camminando il book a 20 livelli** e il prezzo medio
  è limitato a uno slippage massimo del 5% (`get_dry_market_fill_price`, `slippage = 0.05` riga 1261);
  commissione maker per i limiti eseguiti dopo, taker per gli immediati (`add_dry_order_fee`).
* Timeout: `unfilledtimeout.entry/exit` (minuti o secondi); `exit_timeout_count` → uscita d'emergenza a
  mercato (`docs/configuration.md`, righe 193-196). `adjust_order_price` per ripiazzare invece di cancellare.
* Differenze dry-run/backtest elencate nella doc: ritardo di qualche secondo dopo l'apertura della
  candela, fill non garantiti sui limiti, callback chiamati ogni 5 s in live e una volta per candela in
  backtest (`docs/strategy-101.md`, `docs/bot-basics.md`).

**Protezioni** (`plugins/protections/`, `docs/includes/protections.md`): quattro classi, tutte con
`lookback_period(_candles)`, `stop_duration(_candles)`, `trade_limit`; il blocco finisce arrotondato alla
candela successiva; backtestabili con `--enable-protections` e ottimizzabili con lo spazio `protection`.
* `CooldownPeriod`: blocca la coppia per N candele dopo un'uscita (`cooldown_period.py`).
* `StoplossGuard`: se ≥ `trade_limit` trade chiusi in stop (stop, trailing, stop su exchange,
  liquidazione) con profitto < `required_profit` nella finestra, blocca tutto o solo la coppia
  (`only_per_pair`) o solo un lato long/short (`only_per_side`, pensato per i futures) (`stoploss_guard.py`).
* `MaxDrawdown`: drawdown nella finestra oltre `max_allowed_drawdown` → blocco globale; due modi,
  `ratios` (legacy) o `equity` (vero picco-valle sul saldo) (`max_drawdown_protection.py`).
* `LowProfitPairs`: blocca le coppie con profitto cumulato sotto soglia.

**Dimensione posizione** (`docs/configuration.md`, righe 355-447): `stake_amount` fisso oppure
`"unlimited"` = saldo / `max_open_trades`; `tradable_balance_ratio` 0,99; `custom_stake_amount`;
una sola posizione per coppia; `adjust_trade_position` per DCA e uscite parziali
(`max_entry_position_adjustment`), con avviso «Loose logic» (in live viene chiamato ogni 5 s e può
ricomprare all'infinito). Il modulo «edge» (sizing per expectancy) è stato rimosso in 2025.6
(`docs/deprecated.md`).

**Leva e futures** (`docs/leverage.md`): `trading_mode: futures`, `margin_mode: isolated | cross`
(cross: «l'influenza fra posizioni potrebbe non essere simulata del tutto in dry-run o backtest»);
callback `leverage()` (default 1x); `liquidation_buffer` 0,05 (stop minimo sopra il prezzo di
liquidazione), `liquidation_warn_ratio` 0,2 (avviso Telegram, «best effort»); le commissioni di
liquidazione **non** sono calcolate. Prezzo di liquidazione simulato in dry-run
(`exchange.py`, `dry_run_liquidation_price`). Frase chiave: «Non fare trading con leva > 1 con una
strategia che non ha mostrato risultati positivi in un run live sullo spot».

---

## 6. Cosa può servire davvero al proprietario

### (a) Riusabile subito (come idea o come specifica, non come codice GPL)

1. **La regola di fill dei limiti e la sua contabilità.** «Eseguito se `low ≤ prezzo ≤ high`», ordine
   che resta vivo fino a timeout o sostituzione, e nel report il conteggio di timeout, ordini cancellati
   e sostituiti. Se nel paper i costi superano la perdita lorda, la prima misura è: quanti ingressi
   sono maker e quanti taker. Freqtrade lo rende visibile per costruzione (`backtesting.py`,
   `check_order_cancel`/`check_order_replace`; `exchange.py`, `add_dry_order_fee`).
2. **Il modello di fill a mercato sul book L2** del dry-run (`get_dry_market_fill_price`): prezzo medio
   camminando 20 livelli, con tetto. È una stima misurabile dello «scarto di prezzo», da confrontare
   col paper invece di una costante.
3. **Il test «taglia e rifai»** di `lookahead-analysis`: per ogni trade, rifai il calcolo con i dati
   troncati alla candela del segnale e controlla che segnale e indicatori non cambino. È un controllo
   meccanico che si può aggiungere al gate per le strategie generate a caso, dove un lookahead
   involontario è il modo più facile per «trovare» un vantaggio inesistente.
4. **Il test della lunghezza di avvio** (`recursive-analysis`): quanto cambiano gli indicatori con
   200, 500, 1000 candele di storia. Spiega una parte delle divergenze live/backtest.
5. **La lista delle assunzioni del backtest** (`docs/backtesting.md`, «Assumptions»): ordine
   segnale → stop → ROI → trailing nella stessa candela; low prima dell'high; stop al prezzo di stop e non
   al low; trailing peggiore sulla candela di entrata; ROI limitato al livello ROI. È una checklist
   diretta per `docs/audit_backtesting.md`.
6. **Le metriche onestamente commentate**: p-value del profitto medio con l'avviso sui confronti
   multipli, SQN, expectancy, «segnali rifiutati», spaccato per `enter_tag` e motivo di uscita, valori
   degli indicatori sulla candela di entrata (`backtesting-analysis`). Rispondono a «come e perché il
   sistema perde» con un numero.
7. **La struttura delle protezioni**: tre regole semplici (raffreddamento per coppia, N stop in una
   finestra, drawdown sul saldo), con blocco arrotondato alla candela e backtestabili. Poche righe
   ciascuna (`stoploss_guard.py` ~110 righe).
8. **`--timeframe-detail`**: validare le strategie a 15 minuti con candele da 1 o 5 minuti per la
   sequenza stop/ROI dentro la candela.
9. **Il backtest a finestra scorrevole di FreqAI** (addestra 30 giorni, prova 7, scorri) come schema
   di walk-forward; e la commissione **peggiore fra taker e maker** come default prudente.

### (b) Cosa NON risolve: trovare un vantaggio dopo i costi

* **Freqtrade non fornisce nessuna prova che le sue strategie guadagnino.** Testuale: la strategia
  generata da `new-strategy` «non sarà redditizia così com'è» (`docs/strategy-customization.md`,
  riga 34); «la maggior parte delle strategie pubbliche non rende bene» e «non c'è un trucco, un
  consiglio o un'opzione che aggiusti una strategia che va male» (`docs/strategy-101.md`, righe 187-191);
  «siti che classificano strategie freqtrade mostrano backtest impressionanti: non dare per scontato che
  siano raggiungibili o realistici» (`docs/strategy-101.md`); l'esempio FreqAI «non è per la produzione».
  Il README è «solo a scopo educativo». Le FAQ dicono «sarà sempre una scommessa» (`docs/faq.md`).
* **Il loro stesso esempio di report** (`docs/backtesting.md`): SampleStrategy, un mese di futures,
  +5,72% con p-value 0,4768 (cioè indistinguibile dal caso, come dice la loro nota) mentre il mercato
  faceva +30,51%. Non è una prova di rendimento; è un esempio di formattazione.
* **Niente slippage, niente walk-forward, niente correzione per i confronti multipli, niente prova
  su prezzi mescolati.** Il protocollo del proprietario (periodo chiuso, tre passaggi fuori campione,
  placebo) è più severo degli strumenti di freqtrade. Hyperopt è ottimizzazione dentro il campione
  per costruzione; l'unica difesa suggerita è «poi fai il dry-run».
* I 630 candidati provati dal proprietario senza trovarne uno che renda dopo i costi non vengono
  smentiti da nulla in questo repository: freqtrade è un'infrastruttura di esecuzione e verifica, non
  una fonte di vantaggio.

---

## 7. Rischi e punti deboli noti

* **Overfitting dell'hyperopt.** Ricerca in-sample su spazi enormi (le FAQ incoraggiano 10.000 epoche),
  funzioni di perdita che premiano il profitto, nessun fuori campione integrato; la doc avverte solo sui
  decimali e sulle «coppie vincenti». Ogni risultato hyperopt va trattato come sospetto.
* **Semplificazioni del backtest.** Nessuno slippage; fill se il prezzo è nel range; niente fill
  parziali, volume o coda; limiti e precisioni attuali, non storici; funding mancante → backtest
  dichiaratamente inaccurato; cross margin non simulato del tutto.
* **Dipendenza dagli exchange.** Tutto passa da `ccxt` e dalle API; Binance blocca alcuni paesi, ha
  regole quantitative sui futures, richiede il book; commissioni in BNB e «polvere» di monete;
  avvisi frequenti «Outdated history», «Missing data fillup», «Price jump» (`docs/faq.md`); stop su
  exchange troppo stretto = rischio di non-fill, troppo largo = rifiutato (`docs/stoploss.md`).
* **Dry-run ≠ backtest.** Ritardi dopo l'apertura della candela, callback ogni 5 s, `adjust_trade_position`
  che può ricomprare in loop (`docs/strategy-callbacks.md`, «Loose Logic»).
* **FreqAI.** Apprendimento continuo che overfitta, RL che «bara» sulla ricompensa, modelli pickle,
  dipendenze pesanti (torch ~700 MB), feature calcolate una volta su tutto il periodo.
* **Peso e licenza.** ~65.000 righe più ~80.000 di test, Python ≥ 3.12, supporto solo per l'ultima
  release; GPLv3 (copiare codice in un repo pubblico implica la GPL).
* **Issue.** 33 aperte su GitHub al 12 ott 2026 (dato API); i modelli di issue dicono che il caso
  tipico non-bug è «strategia o configurazione generata dall'IA che non funziona». Non ho potuto leggere
  l'elenco (accesso negato da questa sessione).

---

## Giudizio in 5 righe

1. **Prendere:** la regola di fill dei limiti con il conteggio maker/taker e dei timeout; il modello di
   slippage sul book del dry-run; il test «taglia i dati e rifai» contro il lookahead e il test sulla
   lunghezza di avvio; la checklist delle assunzioni del backtest; le tre protezioni; il p-value con
   l'avviso sui confronti multipli.
2. **Non prendere:** hyperopt come metodo per trovare un vantaggio (ottimizza dentro il campione, nessun
   fuori campione, nessuna correzione); FreqAI come scorciatoia (zero prove, rischi dichiarati);
   le strategie di esempio (non redditizie per loro stessa ammissione); il codice intero (GPLv3 in
   un repo pubblico, 65.000 righe che non servono).
3. **Perché:** il problema del proprietario è «costi > vantaggio lordo», e freqtrade nel backtest non
   modella lo slippage e non dimostra che alcuna strategia batta i costi.
4. Il suo valore per noi è come riferimento ingegneristico di realismo dell'esecuzione e di caccia ai
   bias, non come fonte di rendimento.
5. Passo concreto: riprodurre nel nostro motore due misure di freqtrade — quota maker/taker degli
   ingressi e fill a mercato stimato sul book — e aggiungere al gate il test «taglia e rifai».

---

## File letti (fonti)

`README.md`, `LICENSE`, `CONTRIBUTING.md`, `pyproject.toml`, `freqtrade/__init__.py`,
`.github/workflows/` (elenco), `.github/ISSUE_TEMPLATE/*.md`,
`docs/index.md`, `docs/backtesting.md`, `docs/advanced-backtesting.md`, `docs/hyperopt.md`,
`docs/lookahead-analysis.md`, `docs/recursive-analysis.md`, `docs/faq.md`, `docs/stoploss.md`,
`docs/leverage.md`, `docs/bot-basics.md`, `docs/strategy-101.md`, `docs/strategy-customization.md`
(sezione «Common mistakes»), `docs/strategy-callbacks.md` (ordini, timeout, adjust position),
`docs/configuration.md` (sizing, timeout), `docs/exchanges.md` (Binance), `docs/deprecated.md`,
`docs/utils.md` (grep), `docs/includes/protections.md`, `docs/includes/pricing.md`,
`docs/includes/showcase.md`, `docs/freqai.md`, `docs/freqai-running.md`,
`docs/freqai-feature-engineering.md`, `docs/freqai-configuration.md` (grep), `docs/freqai-parameter-table.md`
(grep), `docs/freqai-reinforcement-learning.md`;
`freqtrade/optimize/backtesting.py` (righe 268-281, 574-720, 787-860, 1025-1300, 1377-1475, 1519-1610),
`freqtrade/optimize/analysis/lookahead.py` (righe 60-200), `freqtrade/optimize/hyperopt_loss/hyperopt_loss_multi_metric.py`,
`freqtrade/optimize/hyperopt_loss/hyperopt_loss_sharpe_daily.py`, `freqtrade/plugins/protections/*.py`,
`freqtrade/strategy/interface.py` (elenco metodi, `custom_stoploss`), `freqtrade/exchange/exchange.py`
(righe 1206-1445, 2519-2527), `freqtrade/data/metrics.py` (righe 540-575),
`freqtrade/freqai/` (grep su split e valutazione), `freqtrade/templates/sample_strategy.py`,
`freqtrade/templates/FreqaiExampleStrategy.py` (target), `freqtrade/config_schema/config_schema.py` (grep).
Metadati GitHub (stelle, fork, issue aperte, data di creazione) dall'API pubblica, 12 ott 2026.
