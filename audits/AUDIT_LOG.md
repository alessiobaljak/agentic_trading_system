# Registro degli audit

Una riga per audit. Restano le voci aperte e le ultime 10; le altre vanno in `ARCHIVE.md` con un riepilogo.

| Data | Strategia | Commit | Verdetto | Rapporto | Stato |
|---|---|---|---|---|---|
| 2026-11-07 | BTCORA (`research/prova_finta_audit/`, prova di collaudo dell'audit) | nessuno (file locali non committati) | FAIL: sguardo nel futuro, funding assente | `audits/reports/2026-11-07-BTCORA.md` | chiuso (collaudo; nessuna correzione attesa) |
| 2026-11-11 | Prova 28: K2 e F5 + M7 + K2 a rischio uguale (riesame, idea 137) | regole `cbf4167`, codice `8e0b392`, risultati `2beb4f0` (20 ott 2026); repository locale a `51a3dca` | PASS tecnico; due problemi Alti per l'esame: con N = conto (308-309) Sharpe corretto 0,75 e 0,47, sotto 0,80 (0,89 solo con N = gruppi); le regole (`VENTOTTESIMA.md:30-31`) escludono la candidatura | `audits/reports/2026-11-11-PROVA28_K2_F5M7K2.md` | aperto: decisioni di Alessio sul metodo dello Sharpe corretto e sulla candidatura |
| 2026-11-11 | Prova 113: N3G, monete nuove distribuite gratis (riesame, riga 4 di `research/riesame/ELENCO.md`) | regole `67833d4`, codice `436325b`, risultati `95e1d66` (27 ott 2026); eventi della 32 `a2e7b29` (21 ott); repository locale `6e36631` | PASS tecnico del «no»: corretti, 632 eventi, 90 gratis +11,81%, altre +3,01%, differenza +7,63 punti, p 0,0268 (serve 0,01); Alto: eventi della 32 di prima della correzione della lettura oraria (19 persi, 3 gratis); Medi: tenute troncate, contratti su azioni, «senza uscita» senza liquidazione, misura in avanti non registrata | `audits/reports/2026-11-11-PROVA113_N3G.md` | aperto: rifare gli eventi della 32 e chi li legge; elenco ufficiale dei contratti dalla macchina; misura in avanti |
