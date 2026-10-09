# GALAUSDT-032 — candidato di Fase 2, scartato in Fase 4 (costi doppi)

* **Moneta e timeframe**: GALAUSDT, candele da 1 ora (last price).
* **Direzione**: short.
* **Ingresso**: scarto = (close last - close mark) / close mark della barra chiusa; z = (scarto -
  media delle 168 barre precedenti) / deviazione standard delle 168 barre precedenti; se z > 2,
  short all'apertura della barra dopo.
* **Uscita**: all'apertura della barra dopo 2 barre tenute (uscita a tempo).
* **Stop**: 2 ATR(24) dal close della barra di segnale, al massimo il 6% del prezzo (tetto del
  bot). Nessun target.
* **Dimensione e leva**: regole del bot (`config/regole_dimensione.md`): rischio 1% del capitale,
  leva al massimo 2, margine isolato. Trade ridotti per il tetto di leva in costruzione: 0.
* **Filtri**: nessuno (nessun mese sotto la liquidità minima).
* **Motivo economico**: il perpetuo sopra il mark price (cioè sopra il prezzo a pronti più lo
  scarto medio) più del solito si riallinea scendendo (He, Manela, Ross, von Wachter, «Fundamentals
  of Perpetual Futures», arXiv 2212.06888, dicembre 2022).
* **Codice**: `codice/varianti.py`, classe `ScartoMark`; catalogo `codice/catalogo.py`.

## Esito

Costruzione: 325 trade, R medio +0,013 dopo i costi, profit factor 1,06, drawdown 6,6%; batte
nettamente la (a) (t 2,18, soglia 2,05) e la (b) (t 2,22, soglia 2,05). Fase 4: superate
robustezza, timeframe adiacenti, stabilità, trade estremi, ritardo e liquidazione; **non superati i
costi doppi** (R medio -0,043). Scartato: non va in validazione.
