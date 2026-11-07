# Registro delle revisioni

Una riga per revisione. Restano qui le voci aperte e le ultime 10; le altre vanno in `ARCHIVE.md`.

| Data | Branch | Commit | Oggetto | Verdetto | Stato | Rapporto |
|---|---|---|---|---|---|---|
| 2026-11-07 | claude/brave-albattani-1b12fv | a988d5dd (base; b29f5713 equivalente) | modifica proposta: `MAX_LEVERAGE` 5→10, perdita giornaliera da Firestore | REQUEST CHANGES | aperta (modifica non applicata al codice; chiudere come «non applicata»? domanda ripetuta il 7 nov) | `reviews/reports/2026-11-07-limiti-leva-perdita-giornaliera.md` |
| 2026-11-07 | claude/brave-albattani-1b12fv | 782a01fc (codice del percorso = b29f5713) | primo avvio: revisione completa dello stato attuale (demo, rischio, vecchio esecutore, configurazione, Firebase, ops) | REQUEST CHANGES (0 bloccanti oggi, 9 alti, 11 medi, 4 bassi) | aperta: Alti 1-9 tutti chiusi (6-8 per blocco; l'1 con il 25 il 7 nov); Medi e Bassi 10-24 aperti | `reviews/reports/2026-11-07-primo-avvio.md` |
| 2026-11-07 | claude/brave-albattani-1b12fv | 9f47972c (padre 2928d066; già spinto, bot non riavviato) | correzioni dei 9 problemi Alti del primo avvio | REQUEST CHANGES (1 alto nuovo: 25; 1 medio: 26; 5 bassi: 27-31) | chiusa dal 5d5d26ad: 25, 26, 27, 29, 30, 31 chiusi; 28 in parte (resto nel 13) | `reviews/reports/2026-11-07-correzioni-9-problemi.md` |
| 2026-11-07 | claude/brave-albattani-1b12fv | 5d5d26ad (padre a752e9f3; già sul remoto, bot non riavviato) | correzioni dei problemi 25-31 (annullo rifiutato, identificativo per ribilancio, «riparti» a file, attesa delle protezioni, avvio con `DRY_RUN` falso, commenti, ordini da fermo) | REQUEST CHANGES (0 bloccanti, 0 alti; 1 medio nuovo: 32, regressione; 3 bassi: 33-35) | aperta: serve la correzione del 32 con un test | `reviews/reports/2026-11-07-correzioni-25-31.md` |
