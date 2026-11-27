# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa e invarianti con file:riga (sezione 14: il conto vero, con F5 dal 25 nov; sezione 15: il trader AI).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10. `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 26 nov 2026)
- **Ultima revisione**: secondo riesame della quindicesima (sezione «Secondo riesame» di `trader_ai/revisioni/2026-11-26-quindicesima.md`),
  copia `.../scratchpad/wt2` su `c52fbab`: **APPROVE con condizioni** per commit e riavvio sul simulato (194-197 e N1-N5 chiusi; 198 Medio
  solo demo; 202 Medio, test da aggiungere prima del commit; 199-201 Bassi). md5 al commit: `avvio.py` c19205d2, `messaggio.py` 0ca870c9,
  `ripara.py` 4e1e13a9. Prove: `.../scratchpad/riesame2_v7/` (sessione 3e86fc2d; il primo riesame in `riesame_v7/`).
- **Numeri dei problemi**: trader AI fino al 202 (187 non usato); i nuovi partono da 203.
- Trader AI (area `trader_ai/`): quindici revisioni e due riesami in `trader_ai/revisioni/` (23-26 nov); 184-186 chiusi nel `f7fe784`. Nel registro
  di qui la settima (condizioni per i soldi veri: 146, 147) e le ultime tre.
- Conto vero su F5 (25 nov): `reports/2026-11-25-conto-vero-F5-2.md`, APPROVE per il commit del codice spento; al commit confrontare
  le md5 (`conto_vero.py` 4bb9935b, `demo_binance.py` b98074f6, `test_conto_vero_f5.py` 99c9fd1f). 180, 181 Medi e 182, 183 Bassi aperti.
- Conto vero, per l'accensione: 54 (ii) Alto, 70 Medio, 78 Basso (`reports/2026-11-12-conto-vero-versione-firebase-2.md`), più
  180-183 e le decisioni del 25 nov; regole pubblicate e pulsanti provati, revisione nuova sul commit da approvare; rifare S1b, S2b,
  S4 (`giro12nov/test_prove_12nov.py`) e `mutazioni2.py`.
- Voci aperte: 7 (proposta mai applicata; primo avvio; correzioni 25-31; conto vero fino all'accensione; trader AI settima; F5 secondo
  giro; trader AI secondo riesame della quindicesima).

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
  `tests/test_conto_vero.py:161`. Suite al 26 nov sera: 2825 passed, 1 skipped, 1 deselected (ricerca).
- Dall'area `trader_ai` non si scrive in `reviews/` (blocco delle aree): righe nuove come differenza per la sessione crypto. Vietate
  le letture di `dashboard/node_modules`; `find` sulla radice è negato: usare Glob. Il gancio dei segreti blocca i comandi che
  nominano file `.env`. In `reviews/` si scrive con Write o con un breve script Python.
