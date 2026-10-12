# Candidato SOLUSDT-027 (in costruzione)

Famiglia SOLUSDT-015 (idea I-09), ritocco di 025 (che è ritocco di 015).

| Voce | Regola |
|---|---|
| Moneta, timeframe, direzione | SOLUSDT, 30m, short |
| Ingresso | come 024: prima mezz'ora in calo e giorno UTC in calo fino al close della barra 23:00–23:30; ingresso alle 23:30 |
| Uscita | una barra tenuta (uscita alle 00:00 UTC) |
| Stop | 3 ATR(14) sopra il close della barra di segnale |
| Target | nessuno |
| Filtri | mesi sotto la liquidità minima: nessun ingresso |
| Dimensione e leva | regole del bot (rischio 1%, leva 1–2, margine isolato) |
| Codice | `VARIANTI["SOLUSDT-027"]` (uguale a `i09_generale("short", filtro_giorno=True, k_stop=3.0)`) |

**Motivo economico.** Come 024, con lo stop di 025. R medio in costruzione +0,0002: candidato per un margine
minimo.

**Esecuzione nel bot.** Timeframe 30m non disponibile dal vivo: serve un'aggiunta. Stop sotto il 6%.
