# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga (sezioni 1-13; sezione 14: il conto vero, `ff89531` + 12 nov).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 17 nov 2026)
- **Ultima revisione**: `reports/2026-11-17-stato-funding-demo-paper.md`, sezione «G1: il funding per regolamento, demo contro paper»
  dello «stato»: **APPROVE** (0 bloccanti, alti, medi; Bassi 90-94: monete della riga «altre», «—», Firebase muto, letture doppie, test).
  Non committata: se committata, confrontare con `giro17nov/copia/` (md5 `6b5a6a8c`, test `27399f22`). Prove: `giro17nov/test_prove_17nov.py`
  (stato intero), `giro17nov/mutazioni.py <radice> <cartella>`.
- 14 nov, pesi di oggi: committata come `96c6094`, uguale alla copia approvata salvo il commento del 89 (89 chiuso, verificato il 17 nov).
- 12 nov: funding dei paper APPROVE (committato `3624baa`; 83 Basso latente); sezione delle esecuzioni del demo APPROVE (`3566bd4`).
- Conto vero: `reports/2026-11-12-conto-vero-versione-firebase-2.md` (committato `da91124`): **APPROVE per il commit**, **REQUEST
  CHANGES per l'accensione**: 54 (ii) Alto (la chiave di amministratore di Firebase scrive l'approvazione: decisione di Alessio),
  70 Medio, 78 Basso. Riavvio della fase 2 fatto il 16 nov alle 07:36 UTC con l'ok del proprietario (conto vero spento).
- Voci aperte: 5 (proposta mai applicata; primo avvio; correzioni 25-31; conto vero fino all'accensione; funding demo contro paper fino al commit).
- Per l'accensione: decisione sul 54, test di guardia completo (78), 70, regole pubblicate e pulsanti provati, pulsante «Approva» con
  il verdetto del revisore e «Revoca», revisione nuova; rifare S1b, S2b, S4 (`giro12nov/test_prove_12nov.py`) e `mutazioni2.py`.

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
