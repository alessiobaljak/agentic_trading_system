# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa del percorso e invarianti con file:riga (codice committato = `013f9426`; sezione 14: modifiche dell'8 nov).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse (vuoto).
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato all'8 nov 2026, secondo giro della fase 1)
- Ultima revisione: `reports/2026-11-08-fase1-conto-vero-2.md`, modifiche **non committate** su `4f866a1`, **REQUEST CHANGES** solo per il
  **47 (Medio, introdotto nel secondo giro)**: con un capitale nuovo in attesa e le posizioni aperte lo stop perde il pavimento del 65%
  del capitale della fase (prova p11: da 6.500 a 4.615). Correzione: deroga solo con `riparti_attende_g1`. 40 (Alto) chiuso; 41-46 chiusi.
  Nuovi Bassi: 48 («riparti» con il conto non vuoto; pavimento esatto), 49 (testi dello stop, ventunesimo pezzo, p13).
- Bot non riavviato; il riavvio lo decide Alessio. Codice committato del percorso fermo al `013f9426`.
- Voci aperte: 5 (modifica proposta mai applicata; primo avvio; correzioni 25-31; correzione 32; fase 1 secondo giro).
- Alla prossima revisione: 47 (p11 di `fase1/prove_giro2.py`; il test `tests/test_demo_binance.py:1209` deve restare verde), 48 se
  toccato (p12, p16); rifare `prove_fase1.py` e `prove_giro2.py`; confronto con la copia del secondo giro in `fase1/giro2/` (`bot/`, `scripts/`,
  `test_demo_binance.py`); se committato, riscrivere le sezioni 7, 8 e 12 della mappa.
- Decisioni per Alessio in sospeso: riavvio (dopo il 47); conferma delle scelte della sessione principale (stop al pavimento, «riparti»
  alla mezzanotte, limiti nel codice con test, moneta oltre il 60%); tenere o chiudere quando G1 non decide; più quelle di prima (stop per
  posizione, avvisi sul telefono, `DRY_RUN` falso che ferma il demo, chiavi vere, prelievo, regole di Firebase, tetto di 10.000).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`, `_demo_semplice`, `_sempre`, `_DemoFiltri`, `_TROPPE`).
  Sempre `PYTEST_CURRENT_TEST=x` (spegne i file veri di `ops/`) e `dm.time.sleep` sostituito. Script nella cartella di lavoro
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`: `correzioni2/`, `correzione32/`,
  `fase1/` (`prove_fase1.py <radice>`, `prove_giro2.py <radice>`, `prova_15.py`, `prova_bordi.py`; HEAD in `fase1/vecchio/`; codice del
  primo giro in `fase1/nuovo_test_vecchi/`).
- Per provare un test nuovo sul codice di prima: `git archive HEAD bot tests scripts backtesting | tar -x -C <cartella>` e copiare il test.
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`. Suite intera all'8 nov (secondo giro): `2616 passed,
  1 deselected` in 166 s. Il test delle firme va con `PYTHONPATH=<scratchpad>/cr` (libreria di sistema rotta).
- La lettura di `dashboard/node_modules` è vietata: la compilazione della dashboard non si verifica da qui.
- Il gancio dei segreti blocca ogni comando Bash che nomina un file che finisce in `.env`: cercare con Grep.
- In `reviews/` si scrive con Write (o con un breve script Python per i file lunghi). Controllare `git log` alla fine.
