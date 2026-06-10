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
