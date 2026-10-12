# Candidato SOLUSDT-026 (in costruzione)

Famiglia SOLUSDT-015 (idea I-09), ritocco di 025 (che è ritocco di 015).

| Voce | Regola |
|---|---|
| Moneta, timeframe, direzione | SOLUSDT, 30m, short |
| Ingresso | come 023: prima mezz'ora in calo e close della barra 23:00–23:30 sotto la SMA di 200 barre; ingresso alle 23:30 |
| Uscita | una barra tenuta (uscita alle 00:00 UTC) |
| Stop | 3 ATR(14) sopra il close della barra di segnale |
| Target | nessuno |
| Filtri | mesi sotto la liquidità minima: nessun ingresso |
| Dimensione e leva | regole del bot (rischio 1%, leva 1–2, margine isolato) |
| Codice | `VARIANTI["SOLUSDT-026"]` (uguale a `i09_generale("short", filtro_sma200=True, k_stop=3.0)`) |

**Motivo economico.** Come 023; lo stop più largo nasce dallo studio delle uscite per stop di 015 (voce
SOLUSDT-N022), il filtro dallo studio di 025 (voce SOLUSDT-N023). Entrambi scelti sui dati di costruzione.

**Esecuzione nel bot.** Timeframe 30m non disponibile dal vivo: serve un'aggiunta. Stop sotto il 6%.
