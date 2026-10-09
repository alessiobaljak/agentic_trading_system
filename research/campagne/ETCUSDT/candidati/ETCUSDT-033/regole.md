# ETCUSDT-033 — short nell'ultima mezz'ora UTC dopo una giornata in forte calo

Famiglia ETCUSDT-023 (idea I-12), ritocco R1 di ETCUSDT-023. Codice: `codice/varianti.py` (`_r1`,
`_i12`) e `codice/comune.py`.

* **Moneta e timeframe:** ETCUSDT perpetuo USDS-M, candele da 30 minuti (last price per i segnali).
* **Direzione:** short.
* **Ingresso:** alla chiusura della barra 23:00-23:30 UTC, se close / apertura della barra delle 00:00
  UTC dello stesso giorno − 1 < −5%, short all'apertura della barra 23:30.
* **Stop:** close della barra del segnale + 2 × ATR di Wilder a 14 barre da 30 minuti (stop sul last).
* **Target:** nessuno.
* **Uscita:** dopo 1 barra, all'apertura della barra delle 00:00 UTC del giorno dopo.
* **Filtri:** nessun ingresso su segnali di barre di mesi sotto i 20 milioni di USDT al giorno
  (2020-06, 2020-09, 2020-10).
* **Dimensione e leva (regole del bot):** rischio 1% del capitale, quantità = capitale × 1% / |apertura
  − stop|, nozionale al massimo 2 volte il capitale (trade ridotti contati), margine isolato,
  liquidazione sul mark price.
* **Motivo economico:** momento dentro la giornata (Gao, Han, Li, Zhou 2018; Shen, Urquhart, Wang
  2022): chi ribilancia o chiude posizioni a fine giornata UTC spinge nella direzione del giorno;
  l'effetto è più forte nei giorni di grande movimento.
* **Limiti noti subito:** guadagno lordo per trade dello stesso ordine dei costi (Fase 3, nota
  ETCUSDT-N011); il bot vivo ha candele solo fino a 1m, 5m, 15m, 1h: per i 30 minuti serve
  l'aggiunta decisa al Passo 0.
