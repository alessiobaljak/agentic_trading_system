# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa completa del percorso e invarianti con file:riga (aggiornata il 7 nov 2026 sul commit `5d5d26ad`).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse (vuoto).
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 7 nov 2026)
- Ultima revisione: `reports/2026-11-07-correzioni-25-31.md` sul `5d5d26ad`, REQUEST CHANGES. Chiusi 25 (Alto), 26, 27, 29, 30, 31; 28 in
  parte (resto nel 13). Nuovo **Problema 32 (Medio, regressione)**: da fermo la lettura degli ordini aperti (`demo_binance.py:576`) non è
  protetta, una posizione rimasta non si richiude e l'allarme non scatta. Bassi nuovi 33-35. Passaggio a 1.000 di stanotte provato: funziona.
- Il `5d5d26ad` è già sul remoto; il servizio riparte da solo (`docs/hetzner_setup.md:117-118`, da confermare sulla macchina).
- Voci aperte: 3 (modifica proposta mai applicata; primo avvio con Medi e Bassi 10-24; correzioni 25-31 con 32-35).
- Alla prossima revisione: controllare la correzione del 32 (rifare la prova k: posizione rimasta da fermo e `openOrders` sempre in
  errore, la posizione si chiude al minuto dopo e l'allarme parte al terzo tentativo); se toccati, 33 (prova h4) e 34; poi rifare j1-j3.
- Decisioni per Alessio in sospeso: riavvio; `DRY_RUN` falso che ferma anche il demo; stop sul conto ogni minuto (e frequenza della
  ricerca); blocco del vecchio ramo reale; prelievo sulle chiavi vere (non limitate all'indirizzo); regole di Firebase mai pubblicate; più
  quelle del primo avvio (stop per posizione, soglia e ripartenza dello stop, limiti del demo come costanti fisse, valori sulla macchina).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`): percorsi temporanei per interruttore, comandi e capitale
  (i predefiniti puntano ai file veri di `ops/`), `TRADING_BOT_TEST_MODE=1`. Dal `5d5d26ad` il finto toglie dagli aperti gli ordini
  annullati; i guasti valgono una volta sola (per guasti che durano: avvolgere `finto.__call__`). Script delle prove del 7 nov in
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/correzioni2/` (con una copia del
  demo del `9f47972c` in `vecchio/` per i confronti).
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`. Suite intera al 7 nov su `5d5d26ad`: `2566 passed` in 146 s
  (`python3 -m pytest tests/ -q -p no:cacheprovider`, in sottofondo).
- In una copia `git worktree` `tests/test_allowlist_runnable.py` fallisce da solo (risolve `research/` dal repo principale).
- Il gancio dei segreti blocca ogni comando Bash che nomina un file che finisce in `.env`: cercare con Grep.
- Scrivo in `reviews/` solo con Write (niente Edit): file brevi, riscritti per intero. Controllare `git log` alla fine.
