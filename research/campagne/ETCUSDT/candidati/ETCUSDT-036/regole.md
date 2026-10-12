# ETCUSDT-036 — short nell'ultima mezz'ora UTC dopo un calo oltre il 3%, solo in mezz'ore volatili

Famiglia ETCUSDT-023 (idea I-12), ritocco R4 di ETCUSDT-035. Codice: `codice/varianti.py` (`_r4`,
`_i12`) e `codice/comune.py`.

* **Moneta e timeframe:** ETCUSDT perpetuo USDS-M, candele da 30 minuti.
* **Direzione:** short.
* **Ingresso:** alla chiusura della barra 23:00-23:30 UTC, se il rendimento dalle 00:00 UTC è < −3% e
  2 × ATR(14, 30m) / close ≥ 2,5%, short all'apertura della barra 23:30.
* **Stop:** close + 2 × ATR(14, 30m). **Target:** nessuno. **Uscita:** dopo 1 barra (alle 00:00 UTC).
* **Filtri:** mesi sotto la liquidità minima esclusi (2020-06, 2020-09, 2020-10).
* **Dimensione e leva:** come il bot (rischio 1%, leva massima 2, margine isolato).
* **Motivo economico:** come ETCUSDT-033; il filtro di volatilità viene dalla Fase 3 di ETCUSDT-035
  (nota ETCUSDT-N012) e dalla fonte (effetto più forte nei giorni volatili).
