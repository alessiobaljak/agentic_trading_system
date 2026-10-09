# Candidato DYDXUSDT-008 — BTC guida, DYDX segue (long)

Regole congelate così come registrate il 2026-10-09 (log, voce `DYDXUSDT-008`); codice in
`codice/varianti.py`, funzione `_i08("long")`, e `codice/comune.py`.

* **Moneta e contratto:** DYDXUSDT, perpetuo USDS-M di Binance.
* **Timeframe dei segnali:** 1 ora (candele del last price, chiuse).
* **Direzione:** solo long.
* **Ingresso:** alla chiusura dell'ora i, se
  1. il rendimento orario di BTCUSDT (close su close dell'ora prima) supera 2 volte la deviazione standard
     (popolazione) dei rendimenti orari di BTC delle 168 ore precedenti (almeno 100 valori disponibili), e
  2. il rendimento orario di DYDXUSDT nella stessa ora (close su close) è minore di quello di BTC;
  si entra all'apertura dell'ora dopo, se non c'è già una posizione.
* **Stop:** close dell'ora del segnale meno 2 volte l'ATR di Wilder a 14 ore (sul last); scatta sul last.
* **Target:** nessuno.
* **Uscita:** dopo 3 ore chiuse in posizione, all'apertura dell'ora seguente (o prima, allo stop).
* **Riscaldamento:** nessun segnale prima della barra 170 della serie.
* **Dimensione e leva (regole del bot):** rischio 1% del capitale per trade, quantità = capitale × 1% /
  |apertura − stop|, nozionale al massimo 2 volte il capitale (riduzione al tetto, contata), margine
  isolated, liquidazione sul mark con mantenimento 2,5%.
* **Costi nel test:** commissione 0,05% per lato, slippage 0,02% per lato, funding storico ai settlement.
* **Filtri:** filtro di liquidità della Fase 0 (nessun mese escluso per DYDXUSDT).
* **Motivo economico:** correlazione incrociata ritardata (Lo e MacKinlay, 1990): l'informazione di
  mercato arriva prima sul titolo più grande e liquido (BTC) e si trasmette con ritardo a quelli minori;
  quando BTC fa un movimento forte e DYDX non l'ha ancora seguito, DYDX recupera nelle ore seguenti.
* **Eseguibile dal bot?** Il timeframe 1h è fra quelli che il bot scarica; lo stop a 2 ATR orari
  (mediano circa 4%) sta sotto il 6% nella maggior parte dei casi; la regola usa il rendimento orario di
  BTC, cioè un dato di un'altra moneta: il bot ha un «contesto di mercato» (regole_dimensione.md, punto 4),
  ma la condizione andrebbe scritta come strategia in codice, con l'aggiunta «coppia del protocollo».
