# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga (sezioni 1-13; sezione 14: il conto vero, `ff89531` + 12 nov).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 12 nov 2026, notte)
- **Ultima revisione** (notte): `reports/2026-11-12-funding-dei-paper.md`, funding dei paper: secondo giro **APPROVE** per
  commit e riavvio (82 chiuso; 83 Basso latente: una chiave di formato vecchio fermerebbe G1, oggi impossibile).
- Sera: `reports/2026-11-12-stato-demo-esecuzioni.md`, sezione di sola lettura del demo nello «stato»:
  secondo giro **APPROVE** (finestra 23:50-01:45 UTC, stop al primo 429 o 418, soglia 600, riga del peso in cima). Conto vero: `da91124`.
- Conto vero: `reports/2026-11-12-conto-vero-versione-firebase-2.md` (secondo giro, committato come `da91124`): **APPROVE per
  il commit**; **REQUEST CHANGES per l'accensione**: 54 (ii) Alto (la chiave di amministratore di Firebase scrive l'approvazione:
  decisione di Alessio), 70 Medio, 78 Basso nuovo (il test di guardia del 54 non vede la costante importata, un nome a pezzi, un `.json`).
  Chiusi: 74 (approvazione letta negli ultimi 10 minuti, con git; revoca non letta: fino a 10 minuti), 75, 76, 77. Primo giro `a267c40`.
- Fase 2 `ff89531`; sulla macchina gira ancora `1a8522f` (riavvio con l'ok di Alessio).
- Voci aperte: 4 (proposta mai applicata; primo avvio; correzioni 25-31; conto vero fino all'accensione).
- Alla prossima revisione: se committato, confrontare il commit con `giro12nov/copia2` (copia del secondo giro, senza git); rifare
  S1b, S2b, S4 (`giro12nov/test_prove_12nov.py`, un giro al minuto: S1 e S2 senza giri restano bloccate, giusto) e `mutazioni2.py`.
- Per l'accensione: decisione sul 54, test di guardia completo (78), 70, regole pubblicate e pulsanti provati, pulsante «Approva» con
  il verdetto del revisore e «Revoca», revisione nuova.

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`).
  Sempre `TRADING_BOT_TEST_MODE=1`, `PYTEST_CURRENT_TEST=x`. Cartella di lavoro
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `fase1/`, `fase2/` (giri 1-3),
  `giro12nov/` (`mutazioni.py <copia>`, `mutazioni2.py <copia2>`, `test_prove_12nov.py` da lanciare con `PYTHONPATH=<radice> python3 -m pytest <file> -s`,
  `prova_bot.py <radice>`, `prova_firebase_muto.py <radice> <cartella>`).
- **Niente `git init`/`git commit` nemmeno nella cartella di lavoro** (il permesso lo nega): le prove che vogliono un repository si
  scrivono come test (gli aiuti `_repo`/`_commit` di `tests/test_conto_vero.py` lo creano dentro pytest).
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`; demo `tests/test_demo_binance.py:1520`; conto vero
  `tests/test_conto_vero.py:161`. Suite intera al 12 nov: vedi l'ultimo rapporto; la firma passa con
  `PYTHONPATH=<cartella di lavoro>/cripto`. Dashboard: `npx --no-install tsc --noEmit` in `dashboard/`.
- La lettura di `dashboard/node_modules` è vietata. Il gancio dei segreti blocca i comandi che nominano file `.env`: cercare con Grep.
- In `reviews/` si scrive con Write (o con un breve script Python per i file lunghi). Controllare `git log` alla fine.
