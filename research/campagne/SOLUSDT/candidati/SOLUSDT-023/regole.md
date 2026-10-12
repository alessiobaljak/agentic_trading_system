# Candidato SOLUSDT-023 (in costruzione)

Famiglia SOLUSDT-015 (idea I-09, momentum dentro la giornata), ritocco di 015.

| Voce | Regola |
|---|---|
| Moneta, timeframe, direzione | SOLUSDT, 30m, short |
| Ingresso | alla chiusura della barra 23:00–23:30 UTC, se la barra 00:00–00:30 dello stesso giorno ha chiuso sotto la sua apertura E il close della barra di segnale è sotto la SMA di 200 barre (30m); ingresso all'apertura delle 23:30 |
| Uscita | all'apertura della barra successiva (00:00 UTC del giorno dopo): una barra tenuta |
| Stop | 2 ATR(14) sopra il close della barra di segnale, sul last price |
| Target | nessuno |
| Filtri | mesi sotto la liquidità minima (2020-09, 2020-10, 2020-12): nessun ingresso |
| Dimensione e leva | regole del bot: rischio 1% del capitale per trade sulla distanza dello stop, leva effettiva fra 1 e 2, margine isolato (`config/regole_dimensione.md`) |
| Codice | `codice/varianti.py`, `VARIANTI["SOLUSDT-023"]` (uguale a `i09_generale("short", filtro_sma200=True)`) |

**Motivo economico.** Fonte: Gao, Han, Li, Zhou (2018) e Shen, Urquhart, Wang (2022): il rendimento della
prima mezz'ora della giornata prevede quello dell'ultima, per chi fornisce liquidità e chi ribilancia a fine
giornata. Il filtro della media di 200 barre (circa 4 giorni) è nato dallo studio dei fallimenti di 015 sui
dati di costruzione (voce SOLUSDT-N020): è scelto sugli stessi dati e il suo valore lo giudica solo la
validazione.

**Esecuzione nel bot.** Il bot oggi ha indicatori dal vivo solo per 1m, 5m, 15m e 1h (`parametri.yaml`,
`esecuzione_strategie_bot`): una strategia a 30m richiede un'aggiunta. Lo stop (circa 1,5–2,5%) è sotto il
tetto del 6%.
