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
vedrebbe i movimenti tra due letture. Per questo a ogni tick rilegge le ultime candele
1m e valuta i trigger sul loro `high`/`low` (`EXEC_WICK_FILLS_ENABLED`, default on;
`EXEC_WICK_LOOKBACK_1M` = quante candele). Regole:
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
