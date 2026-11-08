# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga (sezioni 1-13 sul codice committato `1a8522f`; sezione 14: fase 2).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato all'8 nov 2026, notte, terzo giro)
- Ultima revisione: `reports/2026-11-08-fase2-conto-vero-3.md`: **APPROVE per il commit del codice spento** (e per il riavvio, con
  l'ok di Alessio); **REQUEST CHANGES per l'accensione**: 54 (ii) Alto (chi spinge il tag approva; decisione di Alessio), **70** Medio
  (stato e traccia su Firebase persi → posizioni del bot senza stop, prova r2; la traccia si scrive una volta senza conferma), 60 resto
  (dashboard, regole), Bassi 66 resto (Firebase muto al primo giro → riarmo senza «riparti», prova r1), 71 chiuso dal delta (`crea_conto_vero`,
  APPROVE), 73 nuovo (errore di creazione solo nel log, non su Firebase), 72 (il ritardo di 60 s dei redditi senza test). Chiusi nel terzo giro: 64, 65, 67, 68; 69 come scelto.
- Fase 1 committata come `1a8522f`, in funzione dalle 19:02 UTC. Bassi 51, 52 aperti.
- Voci aperte: 5 (modifica proposta mai applicata; primo avvio; correzioni 25-31; fase 2 terzo giro fino all'accensione).
- Alla prossima revisione (prima dell'accensione): r1, r2 in `fase2/giro3/prove_giro3.py`; q4-q8; p1-p9; il clone con il tag; se
  committato, controllare che il commit sia uguale a `fase2/giro3/` e riscrivere le sezioni 1, 3, 8, 11 della mappa.
- Decisioni per Alessio in sospeso: quelle del secondo giro più lo stop prima della prima accensione (70).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`).
  Sempre `TRADING_BOT_TEST_MODE=1`, `PYTEST_CURRENT_TEST=x`, `dm.time.sleep` sostituito. Cartella di lavoro
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `fase1/` (giri 1-4),
  `fase2/` (`prove_fase2*.py <radice>` p1-p9 da `fase2/`; `git_tag/` = prova del tag; `demo_head.py` = `demo_binance.py` del
  `1a8522f`), `fase2/giro2/` (`prove_giro2*.py <radice>` q1-q8; nel terzo giro rifatte con l'orologio finto in `fase2/giro3/prove_giro3.py`; il finto `_Vero` di `tests/test_conto_vero.py` ha
  `non_realizzato`: una perdita va lì, un calo del saldo senza redditi è un prelievo).
- Per provare un test nuovo sul codice di prima: `git archive HEAD bot tests scripts backtesting | tar -x -C <cartella>` e copiare il test.
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`; demo `tests/test_demo_binance.py:1520`; conto vero
  `tests/test_conto_vero.py:67`. Suite intera all'8 nov con il terzo giro della fase 2: `2688 passed, 1 failed` (la firma) in 196 s; la firma va con
  `PYTHONPATH=<cartella di lavoro>/cripto` (libreria di sistema rotta).
- La lettura di `dashboard/node_modules` è vietata. Il gancio dei segreti blocca i comandi che nominano file `.env`: cercare con Grep. Niente `grep -r` su tutto il repository.
- In `reviews/` si scrive con Write (o con un breve script Python per i file lunghi). Controllare `git log` alla fine.
