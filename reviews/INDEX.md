# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga (sezioni 1-13; sezione 14: il conto vero, `ff89531` + 12 nov).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 12 nov 2026, pomeriggio)
- Ultima revisione: `reports/2026-11-12-conto-vero-versione-firebase.md` (modifiche non committate su `d0cf6bf`: versione approvata
  dalla dashboard su Firebase, «riparti» in due passi, pulsanti e regole del conto vero, 66/72/73): **APPROVE per il commit del codice
  spento** (riavvio con l'ok di Alessio); **REQUEST CHANGES per l'accensione**: 54 (ii) Alto non chiuso (la chiave di amministratore di
  Firebase scrive l'approvazione: bot, agente della macchina, quattro flussi di GitHub); 74 Medio nuovo (un buco di Firebase salta o
  dimezza il ribilancio, prove S1-S2); 70 Medio; Bassi nuovi 75 (chiamate a Firebase da spento), 76 (fermo non arrivato su Firebase =
  niente «riparti»), 77 (codice «approvato» prima del primo controllo). Chiusi: 66 resto, 72, 73; 60 nel codice (regole da pubblicare).
- Fase 2 committata come `ff89531` (verificato il 12 nov: uguale alle copie riviste); sulla macchina gira ancora `1a8522f`.
- Voci aperte: 4 (modifica proposta mai applicata; primo avvio; correzioni 25-31; 12 nov fino all'accensione). Bassi del demo 51, 52.
- Alla prossima revisione: se committato, controllare che il commit sia uguale a `giro12nov/copia` (copia del working tree del 12 nov,
  senza git) e aggiornare la sezione 14 della mappa; rifare S1, S2, S3 (`giro12nov/test_prove_12nov.py`) dopo le correzioni di 74 e 76.
- Decisioni per Alessio in sospeso: chi può approvare i soldi veri (54 ii), il buco di Firebase (74), il pulsante «Approva» con il
  verdetto del revisore e «Revoca», pubblicare le regole e provare i pulsanti, lo stop prima della prima accensione (70), il riavvio.

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`).
  Sempre `TRADING_BOT_TEST_MODE=1`, `PYTEST_CURRENT_TEST=x`. Cartella di lavoro
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `fase1/`, `fase2/` (giri 1-3),
  `giro12nov/` (`mutazioni.py <copia>`, `test_prove_12nov.py` da lanciare con `PYTHONPATH=<radice> python3 -m pytest <file> -s`,
  `prova_bot.py <radice>`, `prova_firebase_muto.py <radice> <cartella>`).
- **Niente `git init`/`git commit` nemmeno nella cartella di lavoro** (il permesso lo nega): le prove che vogliono un repository si
  scrivono come test (gli aiuti `_repo`/`_commit` di `tests/test_conto_vero.py` lo creano dentro pytest).
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`; demo `tests/test_demo_binance.py:1520`; conto vero
  `tests/test_conto_vero.py:161`. Suite intera al 12 nov: `2758 passed, 1 failed` (la firma) in 215 s; la firma passa con
  `PYTHONPATH=<cartella di lavoro>/cripto`. Dashboard: `npx --no-install tsc --noEmit` in `dashboard/`.
- La lettura di `dashboard/node_modules` è vietata. Il gancio dei segreti blocca i comandi che nominano file `.env`: cercare con Grep.
- In `reviews/` si scrive con Write (o con un breve script Python per i file lunghi). Controllare `git log` alla fine.
