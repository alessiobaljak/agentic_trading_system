# GATE 2 — Paper trading

È il **gate finale** prima dei soldi reali. Riusa lo **stesso** codice di
execution in modalità simulata.

## Come funziona
- `DRY_RUN=True` (default in `.env.example` e in `config.py`).
- `ExecutionEngine` con `dry_run=True` **non** invia ordini a Binance: simula
  fill/PnL su dati **live**, ma scrive comunque lo stato su Firebase RTDB.
- I trade chiusi vengono salvati su Firestore esattamente come in live, quindi il
  **learning loop gira già** durante il paper: il sistema impara prima di
  rischiare capitale.

## Parità col GATE 1 (e col Binance reale)
Il paper deve chiudere i trade **come li chiuderebbe Binance**, altrimenti valida
un'illusione. I punti condivisi con il backtest sono in moduli unici:
- **costi**: `bot/core/costs.py` (fee+slippage, spread per fascia di liquidità, funding con segno);
- **uscite**: `bot/execution/exit_logic.py` (`locked_stop`, `scale_ladder`, `scale_fills`);
- **orizzonte**: 96 barre del timeframe in entrambi.

**Ombre (wick).** Il gate riempie un TP/SL quando l'**ombra** della candela tocca il
livello, anche per un istante — ed è ciò che fa Binance vero, dove gli ordini TP/SL
stanno appoggiati sul book. Il bot però campiona il prezzo ogni ~30s: da solo non
vedrebbe i movimenti tra due letture. Per questo valuta i trigger su un **range**
`high`/`low` (`EXEC_WICK_FILLS_ENABLED`, default on), da due fonti in cascata:

| Fonte | Vede | Quando si usa |
|---|---|---|
| **Stream WebSocket** (`bot/agents/price_stream.py`) | il prezzo in continuo, **in ordine** | default (`EXEC_PRICE_STREAM_ENABLED`) |
| **Candele 1m via REST** | gli estremi, **non** il loro ordine | se lo stream non è sano (`EXEC_WICK_LOOKBACK_1M` candele) |

**Sorgente del prezzo nello stream** (`EXEC_STREAM_TYPE`, default `bookTicker`): si legge
il miglior bid/ask e se ne usa il **mid**. Due ragioni, una pratica e una di merito:
su alcuni IP/provider Binance consegna il **book** ma non gli stream di trade
(`aggTrade`/`kline_*` restano muti *pur con la SUBSCRIBE accettata con ACK* — verificato
sul VPS con `scripts/diagnose_ws.py --deep`); e per simulare un fill il book è comunque
più pertinente, perché un ordine si esegue quando il book arriva al prezzo, non quando
un trade avviene altrove. Si usa il **mid** e non il lato del book perché lo spread è già
un costo modellato in `bot/core/costs.py`: prenderlo qui lo conteggerebbe due volte.

Se il WebSocket è bloccato (firewall/proxy) il bot ripiega da solo sulle candele e
continua a funzionare — la salute è pubblicata in `/bot_status/price_stream`, e si
verifica con `python -m scripts.check_price_stream`.

### Replay del percorso — perché l'ordine conta
Sapere che il prezzo è passato da 103 **e** da 97 non basta: se è passato *prima* da 103
il TP1 è stato incassato e il residuo esce a break-even; se è passato *prima* da 97 è
una perdita piena. Stesso range, esito opposto.

Per questo i prezzi dello stream non vengono schiacciati in un massimo/minimo: vengono
**rigiocati uno per uno nell'ordine reale** (`executor.update_position_path`), come
farebbe la matching engine di Binance. Ogni punto è valutato con `high = low = punto`,
quindi non esiste mai un range ambiguo, e il profit-lock si arma solo sui punti già
passati (nessun look-ahead). La prima uscita interrompe il replay.

Il percorso è compresso a **zigzag**: un movimento continuo aggiorna l'ultimo punto
(l'estremo raggiunto non si perde mai) e i prezzi identici non creano punti, mentre ogni
inversione apre un punto nuovo. Così la memoria dipende dalle oscillazioni reali, non dal
numero di messaggi — e la compressione utile non richiede alcun filtro per ampiezza.

`EXEC_PATH_MIN_MOVE_FRAC` scarterebbe le inversioni più piccole di quella frazione, ma il
default è **0 (nessun filtro)** ed è importante che resti tale: un livello può stare a
pochi centesimi dal prezzo — lo stop a break-even sta **esattamente** all'entry — quindi
filtrare per ampiezza cancella attraversamenti reali. Con la vecchia soglia dello 0,02%
($12.80 su BTC) un tuffo di pochi dollari sotto un break-even spariva dal percorso: il
replay non lo vedeva, proseguiva e incassava un TP mai raggiunto — errore in direzione
**ottimista**, la più pericolosa. Il costo del non filtrare è misurato e trascurabile:
~1.8 µs per punto, cioè ~40 ms per tick con 12 posizioni (0,13% di un tick da 30 s).
Oltre `EXEC_PATH_MAX_POINTS` (20k, ~5 min di book su BTC) il percorso si ferma e lo
segnala nei log.

Doppia rete di sicurezza: dopo il replay si valuta anche il **range aggregato** della
stessa finestra, perché un'inversione filtrata dallo zigzag resta comunque compresa in
`[lo, hi]` — nessun livello attraversato può sfuggire del tutto.

Regole valide per entrambe le fonti:
- lo **stop si valuta prima** dei TP: se il range tocca entrambi, l'ordine intra-candela
  è ignoto → si assume il caso peggiore (come il gate);
- il `high_water` (profit-lock) si aggiorna **a fine tick**: un range è un insieme non
  ordinato, quindi il suo estremo favorevole non può armare il lock e quello avverso
  farlo scattare nello stesso tick;
- le candele **aperte prima dell'ingresso** vengono scartate (non possono riempire i
  nostri TP);
- il range non è mai più stretto del mark osservato → nessun trigger che scattava prima
  può sparire.

La parità vale in **entrambe le direzioni**: più TP riempiti, ma anche più stop presi
sulle ombre. L'obiettivo è il realismo, non numeri più belli.

## Scala di TP dinamica (tarata per coppia dal GATE)
R è **già normalizzato sulla volatilità** (R = `atr_mult_stop` × ATR), quindi la domanda
non è "quanto è volatile la coin" ma "quanto **tende**, in unità della sua volatilità".
Una coppia che ritraccia subito non vedrà mai 5R; una che tende lo supera. Con una scala
globale la stessa scala è comoda per una e proibitiva per l'altra — per questo la scala
è un **parametro validato per coppia**, non una costante.

- I candidati sono in `SCALE_LADDER_CANDIDATES` (`bot/execution/exit_logic.py`) e
  includono l'attuale `1.5/3/5`: una coppia per cui è davvero la migliore la mantiene, e
  la ri-validazione **non può peggiorarla**. Le quote restano 30/30/40 (validate dall'A/B).
- Sotto scale-out `effective_param_grid` **sostituisce** `rr` con la scala nello spazio di
  ricerca. `rr` non ha effetto sulle uscite quando lo scale-out è attivo (il ramo
  scale-out non usa `target`): lasciarlo diluiva la ricerca — misurato, 67–75% delle
  combinazioni campionate con `--max-combos` erano cloni. Lo scambio mantiene lo stesso
  numero di combinazioni.
- La scala scelta finisce in `last_params` della coppia → `adaptation.params_for` →
  passata all'apertura della posizione.
- **Congelata all'ingresso** (`Position.scale_r_mults`, persistita): senza questo una
  passata dell'ottimizzatore cambierebbe i TP di un trade **già aperto** — si eseguirebbe
  un piano diverso da quello d'ingresso, la dashboard mostrerebbe altri numeri e in live
  gli ordini sul book non corrisponderebbero più.
- Coppia **non ancora ri-validata** → nessuna scala nei params → default globale, cioè
  esattamente la scala con cui è stata validata. Durante la migrazione il registro è
  misto ma **coerente**: ogni coppia esegue ciò con cui è stata validata.

### Misura: dove arriva davvero il prezzo (`mfe_r`)
Ogni trade chiuso registra `mfe_r` — la massima escursione **favorevole** in unità di R
(sia nel gate, `SimTrade.mfe_r`, sia nel paper, `ClosedTrade.mfe_r`). Da quell'unico
numero si sa quali gradini avrebbe colpito **qualunque** scala: non serve provarle una
per una né sacrificare trade per esplorare. È ciò che rende la taratura decidibile sui
dati invece che a intuito.

`python -m scripts.mfe_report` mostra la distribuzione per strategia/coppia: la frazione
di trade che raggiunge 0.5R…5R e quale candidata avrebbe incassato di più. Il confronto
tra candidate usa un modello **semplificato** (gradini raggiunti = incassati, residuo a
break-even): serve a scegliere le candidate, la validazione vera la fa il gate che simula
il percorso completo con lo stop che si sposta.

## Avvio
```bash
DRY_RUN=true python -m bot.main
```
La dashboard mostra le posizioni paper (badge `DRY_RUN`), l'equity simulata, la
heatmap e i pesi che si evolvono.

## Criteri di uscita dal gate
Mantieni il paper per **settimane** e verifica che:
1. l'equity curve sia stabile/positiva su più regimi;
2. il `memory_report` notturno produca pesi sensati (strategie scadenti → peso 0);
3. la correlazione confidenza↔esito sia ragionevole;
4. gli alert Telegram e il kill switch funzionino;
5. nessun circuit breaker si comporti in modo anomalo.

## Passaggio a live
Solo dopo aver superato i criteri sopra:
```bash
DRY_RUN=false python -m bot.main
```
Raccomandazioni: capitale ridotto, leva 1–2x, API key Binance **senza** withdraw,
monitoraggio attivo nei primi giorni. Vedi `docs/deployment.md`.
