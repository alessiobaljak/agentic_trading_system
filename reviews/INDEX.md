# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa e invarianti con file:riga (sezione 14: il conto vero, di nuovo G1 dal 28 nov; sezione 15: il trader AI, `bcf284d`).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10. `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 28 nov 2026)
- **Ultima revisione**: riesame del 269 (28 nov, `reports/2026-11-28-conto-vero-G1-bis.md`): sotto il minimo parte solo la chiusura intera;
  APPROVE con una condizione (test del 274 nel commit, testo nel rapporto; impronte `demo_binance.py` 3cac1aeb, `test_conto_vero_g1.py`
  fdc96df8, `docs/conto_vero.md` dfd87e2d). 269 chiuso nel codice; nuovi 274 Medio, 275 Basso. Prima: `reports/2026-11-28-conto-vero-G1.md`
  (APPROVE con condizioni per il commit spento, REQUEST CHANGES per l'accensione; 268-273; tre test del 270 aggiunti in HEAD).
- **Bot**: `16c5712` committato e riavviato il 27 nov (risposta 0782); aperti 217, 221 Bassi.
- **Conto vero, per l'accensione**: 54 (ii) Alto; 70, 268, 270, 274 Medi; 78, 271-273, 275, 217, 221 Bassi; regole di Firebase pubblicate e pulsanti
  provati; la «solo riduzione» sotto il minimo vista sul demo; rifare S1b, S2b, S4 (`giro12nov/test_prove_12nov.py`) e `mutazioni2.py`;
  revisione nuova sul commit dell'accensione.
- **Numeri dei problemi**: una serie sola fino al 202 (187 no). Il 26-27 nov due serie si sono sovrapposte e non si rinumerano: trader AI
  203-267 (`trader_ai/revisioni/`, 260-267 solo in `trader_ai/README.md`), crypto stato e segreti 203-207, 218 e bot 210-217, 219-221
  (`reports/2026-11-27-*.md`). Fra 203 e 267 un numero si cita con il rapporto. **Dal 28 nov serie unica da 268; il prossimo è 276.**
- Trader AI (area `trader_ai/`): diciotto revisioni e tre riesami in `trader_ai/revisioni/` (23-27 nov); versione 8 = `bcf284d`,
  APPROVE con condizioni alla diciottesima; fermo a mano dal 26 nov, riavvio con «riparti» e l'ok di Alessio.
- Voci aperte: 9 (proposta mai applicata; primo avvio; correzioni 25-31; conto vero 12 nov fino all'accensione; trader AI settima;
  trader AI diciottesima; conto vero su G1 del 28 nov e riesame del 269; il resto chiuso o superato).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero con `_Vero`, `_conto`, `_Fb`, `_riga` di
  `tests/test_conto_vero.py`; `_attese` per togliere le pause). In testa `import tests.conftest`; lancio con `PYTHONPATH=<radice>`.
- Cartella di lavoro `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `giro12nov/`,
  `giro25nov_b/`, `rev27nov_bis/`, `rev28nov/`, `rev28nov_ter/` + `mut269.py` (copia con `bot`, `tests`, `scripts`, `backtesting`, `research/programma6`; `mutazioni.py`,
  14 mutazioni; 5 test falliscono già sulla copia perché vogliono git, dashboard, Firebase e requisiti).
- Mai un file `test_*.py` dentro `reviews/`: la voce «test» della lista bianca lancia pytest su tutto il repository. Le prove vanno nel
  rapporto come testo. Niente `git init`/`git commit` nella cartella di lavoro; `env -i` negato; `find` sulla radice negato (Glob).
- Test dei limiti: `tests/test_risk.py`, `tests/test_sizing.py:104`, demo `tests/test_demo_binance.py:1520`, conto vero
  `tests/test_conto_vero.py:169`. Suite al 28 nov: 3134 passed in 178 s.
- Dall'area `trader_ai` non si scrive in `reviews/`; il gancio dei segreti blocca i comandi che nominano file `.env`; in `reviews/` si scrive
  con Write o con un breve script Python.
