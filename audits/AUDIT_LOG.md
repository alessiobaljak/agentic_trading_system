# Registro degli audit

Una riga per audit. Restano le voci aperte e le ultime 10; le altre vanno in `ARCHIVE.md` con un riepilogo.

| Data | Strategia | Commit | Verdetto | Rapporto | Stato |
|---|---|---|---|---|---|
| 2026-11-07 | BTCORA (`research/prova_finta_audit/`, prova di collaudo dell'audit) | nessuno (file locali non committati) | FAIL: sguardo nel futuro, funding assente | `audits/reports/2026-11-07-BTCORA.md` | chiuso (collaudo; nessuna correzione attesa) |
| 2026-11-11 | Prova 28: K2 e F5 + M7 + K2 a rischio uguale (riesame, idea 137) | regole `cbf4167`, codice `8e0b392`, risultati `2beb4f0` (20 ott 2026); repository locale a `51a3dca` | PASS tecnico; due problemi Alti per l'esame: con N = conto (308-309) Sharpe corretto 0,75 e 0,47, sotto 0,80 (0,89 solo con N = gruppi); le regole (`VENTOTTESIMA.md:30-31`) escludono la candidatura | `audits/reports/2026-11-11-PROVA28_K2_F5M7K2.md` | aperto: decisioni di Alessio sul metodo dello Sharpe corretto e sulla candidatura |
