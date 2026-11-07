# Revisioni del percorso degli ordini — indice

Memoria del revisore `live-path-reviewer` (istruzioni in `.claude/agents/live-path-reviewer.md`). Si legge all'inizio di ogni
invocazione, insieme a `LIVE_PATH_MAP.md`.

## File
- `LIVE_PATH_MAP.md` — mappa completa del percorso e invarianti con file:riga (aggiornata il 7 nov 2026 sul commit `013f9426`).
- `REVIEW_LOG.md` — una riga per revisione; voci aperte e ultime 10.
- `ARCHIVE.md` — revisioni più vecchie, chiuse (vuoto).
- `reports/` — un rapporto completo per revisione.

## Stato (aggiornato al 7 nov 2026)
- Ultima revisione: `reports/2026-11-07-correzione-32.md` sul `013f9426`, **APPROVE**. 32 chiuso (prova k: la posizione si chiude al primo
  minuto con `openOrders` sempre in errore). 33 ancora aperto: l'allarme dopo 2 ore viene scritto, ma nessuno lo legge. Nuovi: 36 (Basso,
  introdotto qui: con la lettura in errore e nessuna posizione il demo scrive «vuoto» e toglie l'allarme), 37 (Basso: un guasto di rete
  sulla lettura ferma ancora le chiusure da fermo), 38 (Basso: l'allarme del 33 non si spegne), 39 (Medio, c'era già: `/demo_binance/allarme`
  non lo legge né la dashboard né la fotografia).
- `013f9426` già sul remoto; il bot non è riavviato (il riavvio lo decide Alessio). Le prove j1-j3 (passaggio a 1.000 di stanotte) danno
  gli stessi numeri del `5d5d26ad`.
- Voci aperte: 4 (modifica proposta mai applicata; primo avvio con Medi e Bassi 10-24; correzioni 25-31 con 33-35; correzione 32 con 36-39).
- Alla prossima revisione: se toccati, 36 (k3: niente «vuoto» senza una lettura riuscita), 37 (k4: guasto di rete), 38 (h4b, h5), 39
  (dashboard `PaperBot.tsx` e `scripts/state_snapshot.py` devono leggere l'allarme); poi rifare k, k2, h4 e j1-j3.
- Decisioni per Alessio in sospeso: riavvio; avvisi del demo sul telefono; `DRY_RUN` falso che ferma anche il demo; stop sul conto ogni
  minuto; blocco del vecchio ramo reale; prelievo sulle chiavi vere (non limitate all'indirizzo); regole di Firebase mai pubblicate; più
  quelle del primo avvio (stop per posizione, soglia e ripartenza dello stop, limiti del demo come costanti fisse, valori sulla macchina).

## Promemoria
- Prove a mano con il Binance finto di `tests/test_demo_binance.py` (`_Demo`). Usare percorsi temporanei per interruttore, comandi e
  capitale (i predefiniti puntano ai file veri di `ops/`) e `TRADING_BOT_TEST_MODE=1`. I guasti del finto valgono una volta sola: per un
  guasto che dura, avvolgere `finto.__call__`. Script del 7 nov nella cartella di lavoro
  `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/`:
  - `correzioni2/`, con una copia del demo del `9f47972c` in `vecchio/`;
  - `correzione32/`, con l'albero del `6dacaafd` (codice del `5d5d26ad`) in `vecchio_albero/`, ottenuto con `git archive`, e le prove
    `prove_32_33.py`, `prove_bis.py`, `prove_su_5d5d.py`.
- Per provare un test nuovo sul codice di prima: `git archive <padre> bot tests | tar -x -C <cartella>` e copiare il test nuovo.
- Test dei limiti fissi: `tests/test_risk.py`, `tests/test_sizing.py:104`. Suite intera al 7 nov su `5d5d26ad`: `2566 passed` in 146 s
  (`python3 -m pytest tests/ -q -p no:cacheprovider`, in sottofondo).
- Il gancio dei segreti blocca ogni comando Bash che nomina un file che finisce in `.env`: cercare con Grep.
- In `reviews/` si scrive con Write, riscrivendo i file brevi per intero. Controllare `git log` alla fine.
