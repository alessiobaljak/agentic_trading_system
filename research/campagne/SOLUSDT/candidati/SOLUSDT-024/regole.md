# Candidato SOLUSDT-024 (in costruzione)

Famiglia SOLUSDT-015 (idea I-09, momentum dentro la giornata), ritocco di 015.

| Voce | Regola |
|---|---|
| Moneta, timeframe, direzione | SOLUSDT, 30m, short |
| Ingresso | alla chiusura della barra 23:00–23:30 UTC, se la barra 00:00–00:30 dello stesso giorno ha chiuso sotto la sua apertura E il close della barra di segnale è sotto l'apertura delle 00:00 (giorno in calo); ingresso all'apertura delle 23:30 |
| Uscita | all'apertura della barra successiva (00:00 UTC): una barra tenuta |
| Stop | 2 ATR(14) sopra il close della barra di segnale |
| Target | nessuno |
| Filtri | mesi sotto la liquidità minima: nessun ingresso |
| Dimensione e leva | regole del bot (rischio 1%, leva 1–2, margine isolato) |
| Codice | `VARIANTI["SOLUSDT-024"]` (uguale a `i09_generale("short", filtro_giorno=True)`) |

**Motivo economico.** Stessa fonte di 015; il filtro del giorno in calo è il momentum della giornata intera,
nato dallo studio dei fallimenti di 015 (voce SOLUSDT-N021), scelto sui dati di costruzione.

**Esecuzione nel bot.** Timeframe 30m non disponibile dal vivo: serve un'aggiunta. Stop sotto il 6%.
