# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa e invarianti con file:riga (sezione 14: il conto vero, con F5 dal 25 nov; sezione 15: il trader AI).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10. `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 25 nov 2026)
- **Ultima revisione**: `reports/2026-11-25-conto-vero-F5-2.md`, secondo giro del conto vero su F5: **APPROVE per il commit**
  del codice spento (178 e 179 chiusi; 183 Basso nuovo, testi «G1» rimasti). Non committato su `ecf55d7` (percorso = `932c048`):
  al commit confrontare le md5 nel rapporto (`conto_vero.py` 4bb9935b, `demo_binance.py` b98074f6, `test_conto_vero_f5.py`
  99c9fd1f). Mutazioni: `giro25nov_b/mutazioni_f5.py <copia>` (10 su 12 prese; le 2 vive sono solo testi). Primo giro:
  `reports/2026-11-25-conto-vero-F5.md` (180, 181 Medi e 182 Basso, ancora aperti).
- **Numeri dei problemi**: il trader AI ha usato fino al 177 (`trader_ai/revisioni/2026-11-25-tredicesima.md`): il 183 è del 25 nov (F5): i nuovi partono da 184.
- Trader AI (area `trader_ai/`): tredici revisioni in `trader_ai/revisioni/` (23-25 nov); l'ultima, la tredicesima, APPROVE con
  condizioni (176 Medio, 177 Basso). Nel registro di qui solo le prime sette.
- 17 nov, funding demo contro paper: committato come `d5c6708` con le correzioni 90-92 della sessione principale (19 righe diverse dalla
  copia; grep del 25 nov: nessuna riga su richieste, cliente o chiavi). Chiusa.
- Conto vero, per l'accensione: 54 (ii) Alto, 70 Medio, 78 Basso (`reports/2026-11-12-conto-vero-versione-firebase-2.md`), più
  180-183 e le decisioni del 25 nov; regole pubblicate e pulsanti provati, revisione nuova sul commit da approvare; rifare S1b, S2b,
  S4 (`giro12nov/test_prove_12nov.py`) e `mutazioni2.py`.
- Voci aperte: 6 (proposta mai applicata; primo avvio; correzioni 25-31; conto vero fino all'accensione; trader AI settima; F5 25 nov, secondo giro).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`,
  `_Vero` e gli aiuti `_conto`, `_Fb` di `tests/test_conto_vero.py`; il paper di F5 con `_Finto` di `tests/test_paper_f5.py:75`).
  In testa al file di prova `import tests.conftest` (stesso isolamento della suite); lancio con `PYTHONPATH=<radice>`.
- Cartella di lavoro `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `giro12nov/`,
  `giro17nov/`, `giro25nov/`, `giro25nov_b/`.
- **Niente `git init`/`git commit` nella cartella di lavoro** (permesso negato): le prove che vogliono un repository si scrivono come
  test (aiuti `_repo`/`_commit` di `tests/test_conto_vero.py`).
- Mutazioni su una copia di `bot/`, dei test e di `research/programma6/` (`giro25nov_b/copia`); `env -i` è negato: `os.environ`.
- Test dei limiti: `tests/test_risk.py`, `tests/test_sizing.py:104`, demo `tests/test_demo_binance.py:1520`, conto vero
  `tests/test_conto_vero.py:161`. Suite al 25 nov: 2826 passed, 1 deselected (la firma passa con `PYTHONPATH=<cartella di lavoro>/cripto`).
- Vietate le letture di `dashboard/node_modules`; `find` sulla radice è negato: usare Glob. Il gancio dei segreti blocca i comandi che
  nominano file `.env`. In `reviews/` si scrive con Write o con un breve script Python.
