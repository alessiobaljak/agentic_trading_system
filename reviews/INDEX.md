# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga (sezioni 1-13 sul codice committato `1a8522f`; sezione 14: fase 2).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse (vuoto).
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato all'8 nov 2026, sera)
- Ultima revisione: `reports/2026-11-08-fase2-conto-vero.md`, **REQUEST CHANGES** sulla fase 2 non committata (su `8ec65db`): Alti 53
  (interruttore tolto o `DRY_RUN` vero con posizioni = nessuna protezione; `DRY_RUN` falso senza interruttore = bot che non parte) e 54
  (il tag copre solo 5 percorsi, fuori `research/programma6/esclusi.py` e `bot/core/firebase_client.py`; tag spostabile da chi spinge);
  Medi 55 (la macchina non scarica il tag: provato), 56 (blocco a metà ribilancio = un lato solo), 57 (fermo perso con il file di stato),
  58 (versamenti e prelievi), 59 (chiude posizioni non sue), 60 (niente pulsante, regole, «riparti» in due passi); Bassi 61-63.
- Fase 1 committata come `1a8522f` (identica a `fase1/giro4/`), in funzione dal riavvio delle 19:02 UTC. Bassi 51, 52 aperti.
- Voci aperte: 5 (modifica proposta mai applicata; primo avvio; correzioni 25-31; fase 2; più la fase 1 chiusa).
- Alla prossima revisione (fase 2 corretta): prove p1-p9 in `fase2/` contro il codice nuovo; 53 con test (spento con posizioni, avvio
  senza interruttore); come arriva il tag sulla macchina; aggiornare la sezione 14 e, se committata, le sezioni 1, 3, 8.
- Decisioni per Alessio in sospeso: spegnimento con sole protezioni; chi approva il tag (firma); limiti del conto vero (300, 600, 200%,
  60%); conto dei future solo del bot e prelievi; blocco a metà ribilancio; «riparti» in due passi; pulsante in dashboard; chiave
  (prelievo, indirizzo), regole di Firebase, modo del conto; riavvio per la fase 2; più quelle di prima (stop per posizione, avvisi).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`).
  Sempre `TRADING_BOT_TEST_MODE=1`, `PYTEST_CURRENT_TEST=x`, `dm.time.sleep` sostituito. Cartella di lavoro
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `fase1/` (giri 1-4),
  `fase2/` (`prove_fase2.py <radice>` p1-p7, `prove_fase2b.py`, `prove_fase2c.py`, `prove_fase2d.py` si lanciano da `fase2/`;
  `git_tag/` = prova del tag; `demo_head.py` = `demo_binance.py` del `1a8522f`; `suite.txt`).
- Per provare un test nuovo sul codice di prima: `git archive HEAD bot tests scripts backtesting | tar -x -C <cartella>` e copiare il test.
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`; demo `tests/test_demo_binance.py:1520`; conto vero
  `tests/test_conto_vero.py:67`. Suite intera all'8 nov con la fase 2: `2656 passed, 1 failed` (la firma) in 211 s; la firma va con
  `PYTHONPATH=<cartella di lavoro>/cripto` (libreria di sistema rotta).
- La lettura di `dashboard/node_modules` è vietata. Il gancio dei segreti blocca i comandi che nominano file `.env`: cercare con Grep.
- Niente `grep -r` sull'intero repository (dati pesanti): cercare per cartella.
- In `reviews/` si scrive con Write (o con un breve script Python per i file lunghi). Controllare `git log` alla fine.
