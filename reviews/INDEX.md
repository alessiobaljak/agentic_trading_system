# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa e invarianti con file:riga (sezione 14: il conto vero, con F5 dal 25 nov; sezione 15: il trader AI, versione 8 `bcf284d`).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10. `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 27 nov 2026, sera)
- **Ultima revisione**: bot, secondo giro (27 nov, `reports/2026-11-27-bot-bis.md`): APPROVE con condizioni per il commit del gruppo
  (md5 `main.py` 81241dc3, `monitor.py` 3b7bb816, `test_portafoglio_audit.py` 9b8b08d6, `test_main_audit.py` 2ad06413,
  `test_demo_binance.py` 4dceff5f, `state_snapshot.py` 81d0b974, `ops/gate_fermo` 292f24e2; gli altri come al primo giro). Chiusi 210,
  212, 214-216, 218; Bassi nuovi 219-221; aperti 211 Medio, 213, 217. Riavvio con l'ok di Alessio, dopo `/commands/bot_state`,
  `/positions`, `/ordini_limite` (lo «stato» non li legge). Prima: stato e segreti, secondo giro (`2026-11-27-stato_e_segreti-bis.md`).
- **Numeri dei problemi**: una serie sola fino al 202 (187 no). Il 26-27 nov **due serie si sono sovrapposte** e non si rinumerano: il
  trader AI 203-267 (`trader_ai/revisioni/2026-11-26-sedicesima.md` → `2026-11-27-diciottesima.md`; 260-267 solo in `trader_ai/README.md`;
  lì anche 207-212 del «secondo cercatore»), le revisioni crypto stato e segreti 203-207, 218 (`reports/2026-11-27-stato_e_segreti*.md`)
  e bot 210-217, 219-221 (`reports/2026-11-27-bot*.md`; 208, 209 no). Fra 203 e 267 un numero si cita sempre con il rapporto («218 dello
  stato», «213 del bot», «213 della diciassettesima»). **I problemi nuovi partono da 268, per tutte le aree.**
- Trader AI (area `trader_ai/`): diciotto revisioni e tre riesami in `trader_ai/revisioni/` (23-27 nov); qui la settima (soldi veri: 146,
  147) e dalla quindicesima. Versione 8 = `bcf284d`, codice uguale a quello approvato alla diciottesima (APPROVE con condizioni); fermo a
  mano dal 26 nov, riavvio con «riparti» e l'ok di Alessio. Righe per `reviews/` dei rapporti applicate fino alla diciottesima (27 nov).
- Conto vero su F5 (25 nov): `reports/2026-11-25-conto-vero-F5-2.md`, APPROVE per il commit del codice spento (`conto_vero.py` 4bb9935b,
  `demo_binance.py` b98074f6, `test_conto_vero_f5.py` 99c9fd1f). Per l'accensione: 54 (ii) Alto; 70, 180, 181 Medi; 78, 182, 183 Bassi
  (`reports/2026-11-12-conto-vero-versione-firebase-2.md`); dal 27 nov anche 211, 213, 219, 220; regole pubblicate e pulsanti provati,
  revisione nuova sul commit; rifare S1b, S2b, S4 (`giro12nov/test_prove_12nov.py`) e `mutazioni2.py`.
- Voci aperte: 9 (proposta mai applicata; primo avvio; correzioni 25-31; conto vero fino all'accensione; trader AI settima; F5 secondo
  giro; trader AI diciottesima; stato e segreti bis fino al commit del bot; bot bis).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`,
  `_Vero` e gli aiuti `_conto`, `_Fb` di `tests/test_conto_vero.py`; il paper di F5 con `_Finto` di `tests/test_paper_f5.py:75`).
  In testa al file di prova `import tests.conftest` (stesso isolamento della suite); lancio con `PYTHONPATH=<radice>`.
- Cartella di lavoro `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `giro12nov/`,
  `giro17nov/`, `giro25nov/`, `giro25nov_b/`, `rev27nov/`, `rev27nov_bis/` (mutazioni del monitor e del 218).
- **Niente `git init`/`git commit` nella cartella di lavoro** (permesso negato): le prove che vogliono un repository si scrivono come
  test (aiuti `_repo`/`_commit` di `tests/test_conto_vero.py`).
- Mutazioni su una copia di `bot/`, dei test e di `research/programma6/` (`giro25nov_b/copia`); `env -i` è negato: `os.environ`.
- Test dei limiti: `tests/test_risk.py`, `tests/test_sizing.py:104`, demo `tests/test_demo_binance.py:1520`, conto vero
  `tests/test_conto_vero.py:161`. Suite al 27 nov sera: 3095 passed in 200 s.
- Dall'area `trader_ai` non si scrive in `reviews/` (blocco delle aree): righe nuove come differenza per la sessione crypto. Vietate
  le letture di `dashboard/node_modules`; `find` sulla radice è negato: usare Glob. Il gancio dei segreti blocca i comandi che
  nominano file `.env`. In `reviews/` si scrive con Write o con un breve script Python.
