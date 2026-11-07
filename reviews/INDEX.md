# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga. **Copertura parziale** (7 nov 2026): solo limiti fissi
  (`bot/risk/`) e parametri della dashboard.
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse.
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 7 nov 2026)
- Revisione completa del percorso (primo avvio, passo 2): **NON ancora fatta**. Va fatta nella prossima invocazione utile.
- Voci aperte: 1 (REQUEST CHANGES del 7 nov sulla modifica proposta leva 10 e perdita giornaliera dalla dashboard; non
  applicata al codice).
- Preesistenti da approfondire nella revisione completa: `BACKTEST_PARITY` spegne tutti gli interruttori
  (`bot/risk/circuit_breakers.py:50-52`); leva e rischio della dashboard tagliati con una nota invece di rifiutati
  (`bot/risk/risk_manager.py:77-80`); `day_pnl_pct` inesistente letto a `bot/main.py:270`, `:1173`.
- Decisioni per Alessio in sospeso: vedi la sezione omonima del rapporto del 7 nov.

## Promemoria
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`. Prima della modifica 120 passati sugli 11 file che
  toccano `bot/risk` (7 nov 2026).
- In una copia `git worktree` il test `tests/test_allowlist_runnable.py` fallisce da solo (risolve `research/` dal repo
  principale): non è un fallimento della modifica.
