# 0074-trade-chiusi.req

_eseguito: 2026-09-17 20:07 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.1s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 3  (3 con apertura nota)
Giorni coperti:          2
Trade/giorno:            min 1 · media 1.5 · max 2
Durata media holding:    4.5h  (min 0.9h · max 8.0h)
Posizioni contemporanee: MAX 2 · media nel tempo 0.5
Coin distinte:           3
Strategie distinte:      3

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.
```
