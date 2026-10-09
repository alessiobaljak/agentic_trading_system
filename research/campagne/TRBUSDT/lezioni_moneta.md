# Lezioni della moneta TRBUSDT (resta in questa cartella fino al Passo 7)

Idee provate in costruzione (2020-09 → 2022-12), tutte senza vantaggio sul caso:

* **Trend** — momentum a 20 giorni (4h, long e short), rottura di canale a 20 barre (4h long),
  compressione e rottura a 1h (long e short: R +0,08 ma `t` 1,1-1,3), rottura della prima ora UTC
  a 15m (short `t` 1,37, il più alto della campagna; 3 ritocchi fino a `t` 1,25, 1,02, 0,75).
* **Ritorno dopo eccessi** — reazione eccessiva a 6 ore, RSI a 2 barre con filtro di trend,
  posizione della chiusura nella barra giornaliera, martello e stella cadente: tutti con `t` fra
  −0,6 e +0,7.
* **Flussi e volume** — short dopo un'ora di prezzo e volume esplosivi: R −0,16, peggio della (b)
  (−0,10). Volume alto e illiquidità di Amihud: sotto i 70 trade.
* **Funding affollato** (8h): sotto i 70 trade anche con soglie al 75°/25° percentile.
* **Calendario** — lunedì long `t` 0,44; prima → ultima mezz'ora UTC R −0,11 (i costi di una
  mezz'ora pesano circa 0,1 R).
* **Numeri tondi** — continuazione dopo l'attraversamento: `t` −0,33 (long) e 0,43 (short).
* **Distribuzione dei rendimenti** — asimmetria, rapporto delle varianze, volatilità bassa: `t` fra
  −1,66 e +0,39.

Fatti della moneta utili a chi ci tornerà:

* ATR mediano: 1,1% a 15m, 2,3% a 1h, 4,9% a 4h, 13,4% a 1d. Uno stop a 2 ATR supera il limite del
  6% del bot già a 4h.
* Ombre estreme frequenti (12 barre a 15m oltre il 25%, fino all'83%); R per trade del 2020 molto
  negativo in quasi tutte le varianti.
* 7 mesi di costruzione su 28 sotto i 20 milioni di USDT al giorno: le idee lente (funding, volume,
  canali di 50 barre) non arrivano a 70 trade.
* Le baseline casuali sono molto negative a 15m-1h (fino a −0,3 R): costi e stop vicini.
