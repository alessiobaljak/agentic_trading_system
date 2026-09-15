# 0059-sonda-timeframe-2.req

_eseguito: 2026-09-15 19:08 UTC_

**richiesta:** `timeframe`
**eseguito:** `.venv/bin/python -m scripts.timeframe_probe`
**esito:** codice 0 in 748.1s

```
[firebase] connesso (Firestore + RTDB)
[probe] 20 candidate (seme 4242) x 6 monete scoperte + 3 di controllo x 3 scale · dati da 2024-01-01 · budget 780s
[probe] scoperte:  BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, ZECUSDT, LSKUSDT
[probe] controllo: XRPUSDT, SUIUSDT, ENAUSDT

[backtest] dati da binance: 23713 candele
[backtest] dati da binance: 23713 candele
[backtest] dati da binance: 23713 candele
[backtest] dati da binance: 23123 candele
[backtest] dati da binance: 23713 candele
[backtest] dati da binance: 23713 candele
[probe]   1h scoperte     120 valutate ·   0 passate (0.00%) · 0 quasi
[backtest] dati da cache: 23713 candele (XRPUSDT 1h)
[backtest] dati da binance: 21493 candele
[backtest] dati da binance: 23713 candele
[probe]   1h controllo     60 valutate ·   0 passate (0.00%) · 1 quasi
[probe] 1h finito in 32s
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] dati da bybit: 94849 candele
[backtest] dati da bybit: 94849 candele
[backtest] dati da bybit: 94849 candele
[backtest] dati da bybit: 94614 candele
[backtest] dati da bybit: 94849 candele
[backtest] dati da bybit: 94849 candele
[probe]  15m scoperte     120 valutate ·   0 passate (0.00%) · 0 quasi
[backtest] dati da cache: 94849 candele (XRPUSDT 15m)
[backtest] dati da binance: 85967 candele
[backtest] dati da binance: 94849 candele
[probe]  15m controllo     60 valutate ·   0 passate (0.00%) · 0 quasi
[probe] 15m finito in 182s
[backtest] dati da cache: 284545 candele (SOLUSDT 5m)
[backtest] dati da cache: 284545 candele (BTCUSDT 5m)
[backtest] dati da cache: 284545 candele (XRPUSDT 5m)
[backtest] dati da cache: 284545 candele (ETHUSDT 5m)
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] Binance non disponibile (429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/kl)
[backtest] dati da bybit: 283839 candele
[backtest] dati da bybit: 284545 candele
[probe]   5m scoperte     120 valutate ·   0 passate (0.00%) · 0 quasi
[backtest] dati da cache: 284545 candele (XRPUSDT 5m)
[backtest] dati da binance: 257899 candele
[backtest] dati da binance: 284545 candele
[probe]   5m controllo     60 valutate ·   0 passate (0.00%) · 0 quasi
[probe] 5m finito in 529s

--- QUANTO PASSA, PER SCALA E PER GRUPPO ---
scala   gruppo       valutate  passate    tasso   quasi
1h      scoperte          120        0    0.00%       0
1h      controllo          60        0    0.00%       1
15m     scoperte          120        0    0.00%       0
15m     controllo          60        0    0.00%       0
5m      scoperte          120        0    0.00%       0
5m      controllo          60        0    0.00%       0

--- COME SI LEGGE ---

1h contro 15m:
  monete scoperte : +0.00 punti di tasso
  controllo       : +0.00 punti di tasso
  -> a questa scala NON passa di piu' dove non copriamo: cambiare
     timeframe non e' la risposta per queste monete.

5m contro 15m:
  monete scoperte : +0.00 punti di tasso
  controllo       : +0.00 punti di tasso
  -> a questa scala NON passa di piu' dove non copriamo: cambiare
     timeframe non e' la risposta per queste monete.

NOTA SUL PREZZO. Tre scale triplicano le estrazioni: a parita' di tutto,
anche le coppie che passano per CASO triplicano. Il margine sul budget di
falsi positivi scende da ~10x a ~3x. Resta accettabile, ma va contato.

Questa sonda non ha scritto niente: ne' registro, ne' spec, ne' configurazione.
```
