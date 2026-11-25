# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa e invarianti con file:riga (sezione 14: il conto vero, con F5 dal 25 nov; sezione 15: il trader AI).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10. `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 25 nov 2026)
- **Ultima revisione**: `reports/2026-11-25-conto-vero-F5.md`, il conto vero esegue F5 (`data/paper_f5.json`, età 194 ore) al posto
  di G1. **REQUEST CHANGES**: 0 bloccanti, 0 alti; Medi 178 (test che non coprono la modifica), 179 (strategia non dichiarata, testi
  «G1»/«mezzanotte»), 180 (pesi controllati solo al lunedì), 181 (blocco sopra il lunedì salta la settimana); Basso 182. Per l'APPROVE:
  178 e 179 (parte del bot). Non committato su `932c048`: md5 `conto_vero.py` `f3d97671`, test `d0c657c7`; al giro dopo confrontare.
  Prove: `giro25nov/test_prove_25nov.py` (9 prove, tutte superate).
- **Numeri dei problemi**: il trader AI ha usato fino al 177 (`trader_ai/revisioni/2026-11-25-tredicesima.md`): i nuovi partono da 183.
- Trader AI (area `trader_ai/`): tredici revisioni in `trader_ai/revisioni/` (23-25 nov); l'ultima, la tredicesima, APPROVE con
  condizioni (176 Medio, 177 Basso). Nel registro di qui solo le prime sette.
- 17 nov, funding demo contro paper: committato come `d5c6708` con le correzioni 90-92 della sessione principale (19 righe diverse dalla
  copia; grep del 25 nov: nessuna riga su richieste, cliente o chiavi). Chiusa.
- Conto vero, per l'accensione: 54 (ii) Alto, 70 Medio, 78 Basso (`reports/2026-11-12-conto-vero-versione-firebase-2.md`), più
  178-182 e le decisioni del 25 nov; regole pubblicate e pulsanti provati, revisione nuova sul commit da approvare; rifare S1b, S2b,
  S4 (`giro12nov/test_prove_12nov.py`) e `mutazioni2.py`.
- Voci aperte: 6 (proposta mai applicata; primo avvio; correzioni 25-31; conto vero fino all'accensione; trader AI settima; F5 25 nov).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`,
  `_Vero` e gli aiuti `_conto`, `_Fb` di `tests/test_conto_vero.py`; il paper di F5 con `_Finto` di `tests/test_paper_f5.py:75`).
  In testa al file di prova `import tests.conftest` (stesso isolamento della suite); lancio con `PYTHONPATH=<radice>`.
- Cartella di lavoro `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `giro12nov/`,
  `giro17nov/`, `giro25nov/`.
- **Niente `git init`/`git commit` nella cartella di lavoro** (permesso negato): le prove che vogliono un repository si scrivono come
  test (aiuti `_repo`/`_commit` di `tests/test_conto_vero.py`).
- Test dei limiti: `tests/test_risk.py`, `tests/test_sizing.py:104`, demo `tests/test_demo_binance.py:1520`, conto vero
  `tests/test_conto_vero.py:161`. Suite al 25 nov: 2818 passed, 1 deselected (la firma passa con `PYTHONPATH=<cartella di lavoro>/cripto`).
- Vietate le letture di `dashboard/node_modules`; `find` sulla radice è negato: usare Glob. Il gancio dei segreti blocca i comandi che
  nominano file `.env`. In `reviews/` si scrive con Write o con un breve script Python.
