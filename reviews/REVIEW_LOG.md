# Registro delle revisioni

Una riga per revisione. Restano qui le voci aperte e le ultime 10; le altre vanno in `ARCHIVE.md`.

| Data | Branch | Commit | Oggetto | Verdetto | Stato | Rapporto |
|---|---|---|---|---|---|---|
| 2026-11-07 | claude/brave-albattani-1b12fv | a988d5dd (base; b29f5713 equivalente) | modifica proposta: `MAX_LEVERAGE` 5→10, perdita giornaliera da Firestore | REQUEST CHANGES | aperta (modifica non applicata al codice; chiudere come «non applicata»? domanda 3 del primo avvio, ripetuta il 7 nov) | `reviews/reports/2026-11-07-limiti-leva-perdita-giornaliera.md` |
| 2026-11-07 | claude/brave-albattani-1b12fv | 782a01fc (codice del percorso = b29f5713) | primo avvio: revisione completa dello stato attuale (demo, rischio, vecchio esecutore, configurazione, Firebase, ops) | REQUEST CHANGES (0 bloccanti oggi, 9 alti, 11 medi, 4 bassi) | aperta: degli Alti chiusi 2-9 con `9f47972c` (6-8 per blocco), l'1 in parte; Medi e Bassi 10-24 aperti | `reviews/reports/2026-11-07-primo-avvio.md` |
| 2026-11-07 | claude/brave-albattani-1b12fv | 9f47972c (padre 2928d066; già spinto, bot non riavviato) | correzioni dei 9 problemi Alti del primo avvio (demo, configurazione, avvio, vecchio esecutore bloccato) | REQUEST CHANGES (0 bloccanti, 1 alto nuovo: 25, regressione; 1 medio: 26; 5 bassi: 27-31) | aperta: serve la correzione del 25 e i test h, i | `reviews/reports/2026-11-07-correzioni-9-problemi.md` |
