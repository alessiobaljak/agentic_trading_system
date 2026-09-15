# 0060-sonda-timeframe-3.req

_eseguito: 2026-09-15 19:18 UTC_

**richiesta:** `timeframe`
**eseguito:** `.venv/bin/python -m scripts.timeframe_probe`
**esito:** codice 0 in 374.7s

```
[firebase] connesso (Firestore + RTDB)
[probe] 20 candidate (seme 4242) x 6 monete scoperte + 3 di controllo x 3 scale · dati da 2024-01-01 · budget 780s
[probe] scoperte:  BTCUSDT, ETHUSDT, SOLUSDT, ZECUSDT, HYPEUSDT, LSKUSDT
[probe] controllo: XRPUSDT, SUIUSDT, ENAUSDT

[backtest] dati da cache: 23123 candele (LSKUSDT 1h)
[backtest] dati da cache: 23713 candele (ZECUSDT 1h)
[backtest] dati da cache: 23713 candele (ETHUSDT 1h)
[backtest] dati da cache: 23713 candele (SOLUSDT 1h)
[backtest] dati da cache: 23713 candele (BTCUSDT 1h)
[backtest] dati da binance: 11343 candele
[probe]   1h scoperte    120 valutate · PF mediano 0.910 · sopra il pareggio 29% · 0 passate, 0 quasi
[backtest] dati da cache: 21493 candele (ENAUSDT 1h)
[backtest] dati da cache: 23713 candele (XRPUSDT 1h)
[backtest] dati da cache: 23713 candele (SUIUSDT 1h)
[probe]   1h controllo    60 valutate · PF mediano 0.949 · sopra il pareggio 37% · 0 passate, 1 quasi
[probe] 1h finito in 18s
[backtest] dati da cache: 94849 candele (BTCUSDT 15m)
[backtest] dati da cache: 94849 candele (ZECUSDT 15m)
[backtest] dati da cache: 94849 candele (ETHUSDT 15m)
[backtest] dati da cache: 94614 candele (LSKUSDT 15m)
[backtest] dati da cache: 94849 candele (SOLUSDT 15m)
[backtest] dati da binance: 45367 candele
[probe]  15m scoperte    120 valutate · PF mediano 0.826 · sopra il pareggio 8% · 0 passate, 0 quasi
[backtest] dati da cache: 94849 candele (XRPUSDT 15m)
[backtest] dati da cache: 94849 candele (SUIUSDT 15m)
[backtest] dati da cache: 85967 candele (ENAUSDT 15m)
[probe]  15m controllo    60 valutate · PF mediano 0.876 · sopra il pareggio 8% · 0 passate, 0 quasi
[probe] 15m finito in 90s
[backtest] dati da cache: 284545 candele (ETHUSDT 5m)
[backtest] dati da cache: 284545 candele (SOLUSDT 5m)
[backtest] dati da cache: 284545 candele (ZECUSDT 5m)
[backtest] dati da cache: 284545 candele (BTCUSDT 5m)
[backtest] dati da cache: 283839 candele (LSKUSDT 5m)
[backtest] dati da binance: 136099 candele
[probe]   5m scoperte    120 valutate · PF mediano 0.694 · sopra il pareggio 2% · 0 passate, 0 quasi
[backtest] dati da cache: 257899 candele (ENAUSDT 5m)
[backtest] dati da cache: 284545 candele (SUIUSDT 5m)
[backtest] dati da cache: 284545 candele (XRPUSDT 5m)
[probe]   5m controllo    60 valutate · PF mediano 0.779 · sopra il pareggio 3% · 0 passate, 0 quasi
[probe] 5m finito in 264s

--- COM'E' ANDATA, PER SCALA E PER GRUPPO ---
scala   gruppo       valutate  PF mediano  sopra 1  passate  quasi
1h      scoperte          120       0.910      29%        0      0
1h      controllo          60       0.949      37%        0      1
15m     scoperte          120       0.826       8%        0      0
15m     controllo          60       0.876       8%        0      0
5m      scoperte          120       0.694       2%        0      0
5m      controllo          60       0.779       3%        0      0

--- COME SI LEGGE ---
Si guarda il PF MEDIANO, non i passaggi: col tasso di passaggio misurato
(0,19%) una casella da ~120 valutazioni produce zero passaggi anche se una
scala fosse nettamente migliore. Zero non sarebbe una risposta.

1h contro 15m (PF mediano):
  monete scoperte : +0.084
  controllo       : +0.073
  -> vanno meglio OVUNQUE, non solo dove non copriamo. E' un fatto
     sulla scala (costi, rumore), non sulle monete: trattarlo come una
     scoperta vorrebbe dire allentare il gate senza dirlo.

5m contro 15m (PF mediano):
  monete scoperte : -0.132
  controllo       : -0.097
  -> a questa scala le strategie NON vanno meglio dove non copriamo:
     cambiare timeframe non e' la risposta per queste monete.

NOTA SUL PREZZO. Tre scale triplicano le estrazioni: a parita' di tutto,
anche le coppie che passano per CASO triplicano. Il margine sul budget di
falsi positivi scende da ~10x a ~3x. Resta accettabile, ma va contato.

Questa sonda non ha scritto niente: ne' registro, ne' spec, ne' configurazione.
```
