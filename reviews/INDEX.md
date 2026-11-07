# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa completa del percorso e invarianti con file:riga (aggiornata il 7 nov 2026 sul commit `9f47972c`).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse (vuoto).
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 7 nov 2026)
- Ultima revisione: `reports/2026-11-07-correzioni-9-problemi.md` sul commit `9f47972c`, REQUEST CHANGES. Degli Alti del primo avvio
  chiusi 2, 3, 4, 5, 9 (corretti) e 6, 7, 8 (vecchio ramo reale bloccato); l'1 solo in parte: la correzione apre il **Problema 25
  (Alto, regressione)**: annullo rifiutato → ordine limite vivo più mercato, posizione doppia. Nuovi: 26 (Medio), 27-31 (Bassi).
- Il commit `9f47972c` era già spinto sul branch che la macchina scarica, bot non riavviato (domanda aperta sui riavvii automatici).
  `fd887589` contiene una copia intermedia del rapporto: vale il file attuale.
- Voci aperte: 3 (modifica proposta mai applicata; primo avvio con Medi e Bassi 10-24; correzioni con 25-31).
- Alla prossima revisione: controllare la correzione del 25 (rifare la prova h con un annullo rifiutato e l'ordine ancora aperto) e del 26
  (prova i, «riparti» nello stesso giorno); poi le prove a-d, b2, j1-j2; aggiornare le sezioni 7, 12, 13 della mappa.
- Decisioni per Alessio in sospeso: blocco del vecchio ramo reale; stop sul conto ogni minuto (e su che frequenza misurava la ricerca);
  riavvio; prelievo sulle chiavi vere (non limitate all'indirizzo, risposta del 7 nov); regole di Firebase mai pubblicate; più quelle del
  primo avvio (stop per posizione, soglia e ripartenza dello stop, limiti del demo come costanti fisse, valori di `DRY_RUN`,
  `BINANCE_TESTNET`, `BACKTEST_PARITY` sulla macchina).

## Promemoria
- Le prove a mano usano il Binance finto di `tests/test_demo_binance.py` (`_Demo`): passare sempre percorsi temporanei per
  interruttore, comandi e capitale (i predefiniti puntano ai file veri di `ops/`), e `TRADING_BOT_TEST_MODE=1`. Ha `posizioni_vive`
  e `guasti`; un `DELETE /fapi/v1/order` riuscito NON toglie l'ordine dagli aperti (va simulato a mano, come in
  `scratchpad/correzioni/prove_demo_nuove.py`, funzione `annullo_vero`).
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`. Suite intera al 7 nov su `9f47972c`: `2562 passed` in 145 s
  (`python3 -m pytest tests/ -q -p no:cacheprovider`, in sottofondo).
- In una copia `git worktree` `tests/test_allowlist_runnable.py` fallisce da solo (risolve `research/` dal repo principale).
- Il gancio dei segreti blocca ogni comando Bash che nomina un file che finisce in `.env` (anche le tarature): cercare con Grep.
- Scrivo in `reviews/` solo con Write (niente Edit): file brevi, riscritti per intero. La sessione principale può committare un rapporto
  mentre lo scrivo: controllare `git log` alla fine.
