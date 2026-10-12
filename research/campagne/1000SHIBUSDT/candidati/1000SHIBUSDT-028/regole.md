# Candidato 1000SHIBUSDT-028 (ritocco 1 di I-08 b)

Candidato di Fase 2 (log, voce `risultato` 028): batte nettamente la (a) e la (b) in
costruzione con R medio dopo i costi positivo. Le regole sono congelate così come sono
state registrate; le verifiche della Fase 4 non le cambiano.

| | |
|---|---|
| Moneta | 1000SHIBUSDT (Binance USDS-M, perpetuo) |
| Timeframe | 30 minuti (candele last price, UTC) |
| Direzione | short |
| Condizione d'ingresso | alla chiusura della barra delle 23:00 UTC, se il rendimento della barra delle 00:00 dello stesso giorno (chiusura / apertura − 1) è ≤ −0,9% |
| Ingresso | all'apertura della barra delle 23:30 UTC (barra successiva al segnale) |
| Uscita | «chiudi» alla chiusura della barra d'ingresso: si esce all'apertura delle 00:00 UTC del giorno dopo |
| Stop | chiusura della barra di segnale + 2 ATR(14, Wilder, barre da 30 minuti), al massimo +6% (tetto del bot) |
| Target | nessuno |
| Dimensione | rischio 1% del capitale per trade: quantità = capitale × 0,01 / |apertura − stop|; nozionale al massimo 2 volte il capitale (tetto di leva del bot), margine isolato |
| Filtri | nessun ingresso su barre di mesi sotto 20 milioni di USDT al giorno (in costruzione nessuno) |
| Costi del test | commissione 0,05% per lato, slippage 0,02% per lato, funding storico |

**Motivo economico (dalla fonte).** Gao, Han, Li, Zhou, «Market intraday momentum», Journal of
Financial Economics 129(2), 2018; Shen, Urquhart, Wang, «Bitcoin intraday time series
momentum», The Financial Review 57(2), 2022: il rendimento della prima mezz'ora predice
quello dell'ultima, perché chi deve coprire o ribilanciare a fine giornata opera nella stessa
direzione dei movimenti iniziali, più forte nei giorni volatili. Qui solo il lato short e solo
nei giorni con una prima mezz'ora molto negativa (filtro nato dallo studio dei fallimenti,
log N017).

**Rischi noti fin da ora.** È un ritocco deciso dopo aver visto i risultati di costruzione;
il vantaggio medio dopo i costi è di +0,005 R, cioè quasi tutto il lordo (circa 0,05 R) se ne
va in costi; posizione di mezz'ora: il bot dal vivo ha indicatori solo per 1m, 5m, 15m e 1h
(regole_dimensione.md), quindi a 30 minuti servirebbe un'aggiunta.

Codice: `campagne/1000SHIBUSDT/codice/varianti.py` (nome `R1-I-08b`, prepara `_prep_i08`).
