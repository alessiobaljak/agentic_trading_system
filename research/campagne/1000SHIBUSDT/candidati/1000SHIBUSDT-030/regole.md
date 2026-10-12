# Candidato 1000SHIBUSDT-030 (ritocco 5 della famiglia I-08 b)

Candidato di Fase 2 (log, `risultato` 030), **scartato in Fase 4** (costi doppi: R medio
-0,028; log N023). Regole congelate come registrate.

| | |
|---|---|
| Moneta | 1000SHIBUSDT (Binance USDS-M, perpetuo) |
| Timeframe | 30 minuti (last price, UTC) |
| Direzione | short |
| Condizione d'ingresso | alla chiusura della barra delle 23:00 UTC: rendimento della barra delle 00:00 dello stesso giorno ≤ −0,5% **e** rendimento del giorno dall'apertura delle 00:00 alla chiusura delle 23:30 < 0 |
| Ingresso | apertura delle 23:30 UTC |
| Uscita | «chiudi» alla chiusura della barra d'ingresso (uscita all'apertura delle 00:00) |
| Stop | chiusura di segnale + 2 ATR(14, 30 minuti), al massimo +6% |
| Target | nessuno |
| Dimensione | rischio 1% per trade, nozionale al massimo 2 volte il capitale, margine isolato |
| Costi del test | commissione 0,05% + slippage 0,02% per lato, funding storico |

**Motivo economico.** Gao, Han, Li, Zhou (2018); Shen, Urquhart, Wang (2022): l'ultima
mezz'ora segue la prima, perché coperture e ribilanciamenti di fine giornata seguono il
movimento del giorno; qui solo nei giorni con prima mezz'ora netta in calo e giorno negativo.

**Esito delle verifiche (costruzione).** Costi doppi: fallita (R −0,028). Ritardo: superata al
limite (t 1,081 contro 1,075). Robustezza: 5 casi netti su 7. Timeframe adiacenti: 15m t 2,12,
1h t 2,22. Stabilità e trade estremi: superate. Liquidazione: nessuna violazione.

Codice: `campagne/1000SHIBUSDT/codice/varianti.py` (nome `R5-I-08b`).
