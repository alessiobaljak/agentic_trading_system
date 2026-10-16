# Fatti del bot per il protocollo 3 (Passo 0, punto 3)

Scritto dal coordinamento il 16 ottobre 2026, leggendo solo file di codice e di configurazione del bot
(sezione 3 del protocollo): `bot/`, `backtesting/engine.py`, `scripts/setup_vps.sh`. Nessun file di dati,
log o risultati; nessun segreto (dei segreti si riporta solo il nome del parametro). I valori sono quelli
**del codice**: sulla macchina il bot legge anche `.env` e `tuning.env`, che da qui non si vedono. I
riferimenti sono `file:riga` alla data di oggi.

## 1. serie_stop

- **In paper** il bot confronta lo stop con l'intervallo di prezzo di ogni giro: `lo = min(minimo, mark)`,
  `hi = max(massimo, mark)`; un long si chiude se `lo <= stop` (`bot/execution/executor.py:829-830, 923-926`).
  Il mark price e' quello di Binance (`/fapi/v1/premiumIndex`, campo `markPrice`), letto a ogni giro
  (`bot/main.py:1438-1441`, `bot/agents/price_agent.py:127-136`). Minimo e massimo vengono dal flusso
  `bookTicker` (prezzo medio fra denaro e lettera) o, se il flusso non c'e', dalle candele da 1 minuto del
  last price (`bot/main.py:693-750`, `bot/execution/executor.py:945-963`).
- Quindi in paper lo stop scatta se lo tocca **il last o il mark, il primo dei due**. Il motore del
  protocollo 3 usa la stessa regola (`serie_stop: last_e_mark` in `parametri_3.yaml`).
- Il bot esce **al prezzo dello stop**, anche se il prezzo e' saltato oltre (`executor.py:877, 926`): non ha
  la regola del salto della sezione 9.2. Il motore la applica (piu' prudente).
- **Con ordini veri** (mai usati): stop `STOP_MARKET` con `stopPrice`, senza `workingType`
  (`executor.py:720-723, 738-741, 762-766`): vale il valore predefinito di Binance, che secondo la
  documentazione delle API e' `CONTRACT_PRICE`, cioe' il last price.
- Il controllo avviene a ogni giro del ciclo (pausa di 30 secondi piu' il tempo del giro;
  `bot/main.py:2497, 2610`).

## 2. regole_dimensione_bot

| Fatto | Valore nel codice | Dove |
|---|---|---|
| Rischio per trade | 1% (impostazione dell'utente `risk_per_trade`, predefinito 0,01), moltiplicato per un fattore di fiducia fra 0,5 e 1,5 e limitato al 3% | `bot/main.py:593-602`, `bot/models.py:194`, `bot/risk/risk_manager.py:63-97`, `bot/risk/hard_limits.py:18, 53-56` |
| Capitale | quello del conto in paper (predefinito 1.000 USDT), che cresce e cala con i risultati | `bot/main.py:604-607, 762-771` |
| Dimensione | capitale × rischio ÷ distanza fra prezzo e stop | `bot/risk/risk_manager.py:124-138` |
| Leva | 2 di base (impostazione dell'utente), × 0,7-1,3, abbassata con la volatilita', mai oltre 5, arrotondata all'intero | `bot/models.py:193`, `bot/risk/risk_manager.py:63-93`, `bot/risk/hard_limits.py:17, 33-50` |
| Tetto del valore della posizione | capitale × leva | `bot/risk/risk_manager.py:140-153` |
| Stop piu' largo ammesso | 6%; stop minimo: **nessuno** | `bot/config.py:707`, `bot/risk/setup_check.py:37-59` |
| Modalita' di margine | **non impostata** (con ordini veri varrebbe quella del conto; in paper non c'e' liquidazione) | ricerca nel codice di `bot/`, `scripts/`, `backtesting/` |

**Nel motore del protocollo 3** (sezione 9.4): i risultati sono in R, che non dipendono dal capitale, quindi
si usano capitale fisso 10.000 USDT e rischio 1% del capitale iniziale, senza interesse composto; la leva
massima e' **2**, quella di base del bot; margine isolato con quella leva per il controllo della
liquidazione (prudente: il bot non lo imposta). Un trade che supererebbe la leva 2 si riduce e si conta.

## 3. esecuzione_strategie_bot

- Una strategia del bot e' o una classe Python con `generate_signal` (`bot/strategies/base.py:36-139`) o una
  specifica di "strategia generata" letta da Firestore (`bot/strategies/generated.py:555-773`). Gira solo se
  la coppia `SIMBOLO|nome` e' nel registro `strategy_registry/validated`, che scrive solo il gate
  (`bot/adaptation.py:498-510`).
- Le uscite non fanno parte della strategia: il bot riceve solo stop e target; il resto e' uguale per tutte
  (uscita forzata dopo 96 candele, "profit-lock" che alza lo stop a meta' strada verso il target, pausa di 4
  candele dopo uno stop in perdita, tetto di perdita giornaliera per moneta dell'1,5%).
- La decisione avviene a ogni chiusura di candela da 15 minuti; gli indicatori si calcolano su circa 199
  candele chiuse; l'ingresso a mercato e' al prezzo del momento, qualche secondo dopo la chiusura
  (`bot/agents/price_agent.py:151-179`, `bot/main.py:1589-1598`, `bot/execution/executor.py:306`).
- **Ordini limit in paper** (dal 13 ottobre 2026, `bot/execution/executor.py:331-580`): attivi per tutte le
  strategie quando `PAPER_INGRESSO_LIMITE` e' vero; prezzo = chiusura della candela del segnale (k = 0);
  validita' globale `PAPER_LIMITE_VALIDITA_BARRE` (predefinita 1); eseguito solo se il prezzo **supera** il
  limit (anche il mark conta), al prezzo limit; un nuovo segnale sulla stessa moneta **sostituisce** l'ordine;
  nella candela di esecuzione, dal giro successivo valgono stop, target e profit-lock.

### Il catalogo della sezione 7 e il bot

Legenda: **E** eseguibile cosi' com'e'; **D** il bot ha qualcosa di simile ma diverso; **A** richiede
un'aggiunta al bot.

| Elemento | Stato | Nota |
|---|---|---|
| Timeframe 15m, 1h | E | 1h ha il suo orologio solo in modalita' di parita' |
| Timeframe 30m, 2h, 4h, 6h, 8h, 12h, 1d | A | non sono nell'elenco dei timeframe del bot (`bot/config.py:295`) |
| Incrocio "verso l'alto/basso" | A | il bot vede solo i valori dell'ultima candela, non la precedente |
| EMA 9 | D | partenza dalla prima chiusura, non dalla media delle prime n |
| EMA 20, 50, 100, 200; SMA 50, 100, 200; RSI 7 e 21 | A | non calcolati |
| SMA 20, RSI 14, MACD, ATR 14, Bollinger k 2,0 | E | |
| Bollinger k 2,5; Donchian; ATR percentile; range asiatico; giorno della settimana; funding regolato | A | |
| Stocastico, ADX, volume relativo, VWAP | D | formule diverse (ADX non di Wilder, volume medio con la candela corrente, VWAP mobile su 48 candele) |
| Sessioni (F5) | E | fino a 1h |
| E1, E2, E6, E7, E9 | D → A | il bot ha "stati" (per esempio MACD sopra il segnale), non incroci |
| E4 con k 2,0 | E | |
| E3, E5, E8, E10, E11, E12, E4 con k 2,5 | A | |
| F1, F3, F4, F6 | A | |
| F2, F7 | D → A | |
| F5 | E | fino a 1h |
| C1 | D → A | |
| C2 | A | il bot non vede l'apertura della candela |
| C3 | E | |
| S1 con ingresso M | E | |
| S1 o S3 con ingresso L | D | stop calcolato dal prezzo del momento, non dal prezzo limit |
| S2 | A | |
| S3 con ingresso M | E | con una classe nuova |
| Stop minimo 0,3% | A | |
| Uscita sul salto di prezzo | D | il bot esce al prezzo dello stop |
| U1 | D | il profit-lock globale cambia l'uscita |
| U2, U2s, U3, U4 | A | il bot ha solo l'uscita forzata dopo 96 candele |
| Ingresso M | D | in paper gli ingressi diventano limit se l'interruttore e' acceso; a mercato entra al prezzo del momento |
| Ingresso L con k 0,25 o 0,5 | A | il bot ha solo k = 0 |
| Validita' 1 candela | E | |
| Validita' 3 candele | D | impostazione globale, e un nuovo segnale sostituisce l'ordine |
| Esecuzione oltre il limit, al prezzo limit | E | |
| Nella candela di esecuzione solo lo stop | D | |

**In sintesi: nessuna variante del catalogo si puo' eseguire oggi nel bot esattamente come la descrive il
protocollo.** Servono almeno: un modo di far girare una strategia del protocollo fuori dal registro del gate,
gli incroci, le uscite U2/U2s/U3/U4 per strategia, l'ingresso a mercato per strategia, il limit con k, lo
stop minimo, e lo spegnimento per queste strategie di profit-lock, uscita a 96 candele e pausa dopo lo stop.

## 4. backtest_bot

- Il bot ha un backtest proprio, `backtesting/engine.py` (`Backtester.run_strategy`, righe 798-1009), che
  usa gli stessi indicatori e le stesse uscite del paper, ma **non e' il codice del paper**: niente ordini
  limit, niente dimensione, leva o liquidazione, funding medio continuo, uscita alla chiusura della candela 96.
- **Non esiste un rigioco storico del codice del paper** (`TradingBot` ed `ExecutionEngine`). Per costruirlo
  servono: un processo separato con `DRY_RUN` vero e senza `.env`, un orologio simulato (il codice usa l'ora
  di sistema in `executor.py`), le candele storiche servite al posto delle API, e i costi della sezione 6
  impostati solo nel rigioco.

## 5. Costi

- **Binance** (pagina di supporto «USDⓈ-M Futures trading fees», aggiornata il 1 maggio 2026, esempio per
  l'utente normale): commissione maker 0,02%, taker 0,05%. La tabella ufficiale delle commissioni non si
  legge da qui (la pagina si costruisce nel browser).
- **Margine di mantenimento di BTCUSDT** (tabella pubblica dei livelli di Binance, letta il 16 ottobre
  2026, aggiornata dalla borsa il 19 agosto 2025): primo livello da 0 a 300.000 USDT di valore della
  posizione, margine di mantenimento **0,40%**, importo di mantenimento 0, leva fino a 150. Con capitale
  10.000 e leva 2 il valore massimo di una posizione e' 20.000 USDT: vale sempre il primo livello.
- **Nel paper del bot**: un costo fisso di andata e ritorno di 0,08% del valore piu' uno spread per fascia di
  volume (0,012% sopra 200 milioni al giorno), sul valore d'ingresso per entrambi i lati, nessuno slippage
  sul prezzo; maker 0,02% sull'ingresso limit; funding continuo (ore ÷ 8 × tasso del momento), non per
  regolamento (`bot/execution/executor.py:205, 582-598, 1118-1132`, `bot/costs.py:13-39`).

## 6. DRY_RUN

`DRY_RUN` vale vero quando la variabile manca (`bot/config.py:64`); ordini veri solo se e' falso
(`bot/execution/executor.py:199, 216-217, 253-255`). Il valore sulla macchina e' nel file `.env`, che da
qui non si legge.
