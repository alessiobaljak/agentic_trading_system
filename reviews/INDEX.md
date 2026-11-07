# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa completa del percorso e invarianti con file:riga (7 nov 2026, codice di `782a01fc` = `b29f5713`).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse (vuoto).
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 7 nov 2026)
- Primo avvio **fatto** (passi 1-3): `reports/2026-11-07-primo-avvio.md`, REQUEST CHANGES, 9 problemi alti (4 sul demo, 4 sul vecchio
  ramo reale spento da `DRY_RUN`, la parità col backtest), nessuno bloccante per il demo di oggi, tutti da chiudere prima del conto vero.
- Voci aperte: 2 (la modifica proposta del 7 nov, non applicata; il primo avvio).
- Alla prossima revisione: per ogni problema del primo avvio controllare se è stato corretto (numeri 1-24 del rapporto) e aggiornare
  la sezione 13 della mappa.
- Decisioni per Alessio e domande aperte in sospeso: sezioni omonime del rapporto del primo avvio (stop per posizione, soglia e
  ripartenza dello stop sul conto, limiti del demo come costanti fisse, vecchio ramo reale, nome delle chiavi vere, valori di
  `DRY_RUN`/`BINANCE_TESTNET`/`BACKTEST_PARITY` sulla macchina).

## Promemoria
- Le prove a mano usano il Binance finto di `tests/test_demo_binance.py` (`_Demo`): passare sempre percorsi temporanei per
  interruttore, comandi e capitale (i predefiniti puntano ai file veri di `ops/`), e `TRADING_BOT_TEST_MODE=1`.
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`. Suite intera al 7 nov: `2545 passed` in 146 s.
- In una copia `git worktree` `tests/test_allowlist_runnable.py` fallisce da solo (risolve `research/` dal repo principale).
- Il gancio dei segreti blocca i comandi che nominano i file di ambiente: per cercare usare Grep su cartelle precise.
