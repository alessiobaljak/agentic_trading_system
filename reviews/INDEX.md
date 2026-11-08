# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga (sezioni 1-13 sul codice committato `1a8522f`; sezione 14: fase 2).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse (vuoto).
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato all'8 nov 2026, notte)
- Ultima revisione: `reports/2026-11-08-fase2-conto-vero-2.md`, **REQUEST CHANGES** sul secondo giro della fase 2 (non committato, su
  `7d77c9a`): chiusi 53, 55, 57, 59, 61-63; 56 e 58 come scelto. Aperti: **54 (ii) Alto** (l'agente porta il tag forzato: chi lo spinge
  approva; firma o regola di GitHub, decisione di Alessio prima dell'accensione); Medi 60 resto (dashboard, regole: fase 4), **64**
  (redditi letti da `fino_ms + 1`: righe della stessa ora perse → «un prelievo?», prova q4; nessun allarme se illeggibili, q7), **65**
  (`parti_da_zero` segna i redditi con l'ora d'inizio del giro: le chiusure della fase vecchia entrano nella nuova, q5); Bassi 66
  (Firebase muto alla prima lettura = «mai acceso»), 67 (tag tolto riconosciuto dal testo inglese di git), 68 (allarme `stato_perso`
  mai spento), 69 (alla prima accensione lo stop chiude anche le posizioni non del bot).
- Fase 1 committata come `1a8522f`, in funzione dalle 19:02 UTC. Bassi 51, 52 aperti.
- Voci aperte: 5 (modifica proposta mai applicata; primo avvio; correzioni 25-31; fase 2 secondo giro; e la fase 2 primo giro chiusa).
- Alla prossima revisione: q4, q5, q7 in `fase2/giro2/prove_giro2.py` contro il codice nuovo; p1-p9 e q1-q8 di nuovo; il clone con il
  tag (`fase2/giro2/clone`, `carica.py`, `tocca.py`) per il controllo del codice; `ops_agent.py` vale al primo pull, senza riavvio.
- Decisioni per Alessio in sospeso: ordini «solo riduzione» con `DRY_RUN` vero; chi approva il tag; limiti; prelievi che fermano gli
  ordini; blocchi a ogni commit in `bot/`; stato perso che chiude tutto; «riparti» da file; pulsante in dashboard; chiave, regole,
  modo del conto, niente BNB; riavvio; più quelle di prima.

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`; il conto vero lo riusa con `HOST = "fapi.binance.com"`).
  Sempre `TRADING_BOT_TEST_MODE=1`, `PYTEST_CURRENT_TEST=x`, `dm.time.sleep` sostituito. Cartella di lavoro
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `fase1/` (giri 1-4),
  `fase2/` (`prove_fase2*.py <radice>` p1-p9 da `fase2/`; `git_tag/` = prova del tag; `demo_head.py` = `demo_binance.py` del
  `1a8522f`), `fase2/giro2/` (`prove_giro2*.py <radice>` q1-q8 da `fase2/giro2/`; il finto `_Vero` di `tests/test_conto_vero.py` ha
  `non_realizzato`: una perdita va lì, un calo del saldo senza redditi è un prelievo).
- Per provare un test nuovo sul codice di prima: `git archive HEAD bot tests scripts backtesting | tar -x -C <cartella>` e copiare il test.
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`; demo `tests/test_demo_binance.py:1520`; conto vero
  `tests/test_conto_vero.py:67`. Suite intera all'8 nov con il secondo giro della fase 2: `2681 passed, 1 failed` (la firma) in 192 s; la firma va con
  `PYTHONPATH=<cartella di lavoro>/cripto` (libreria di sistema rotta).
- La lettura di `dashboard/node_modules` è vietata. Il gancio dei segreti blocca i comandi che nominano file `.env`: cercare con Grep. Niente `grep -r` su tutto il repository.
- In `reviews/` si scrive con Write (o con un breve script Python per i file lunghi). Controllare `git log` alla fine.
