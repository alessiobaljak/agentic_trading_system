# 0077-paper-18set.req

_eseguito: 2026-09-18 06:07 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.2s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 5  (5 con apertura nota)
Giorni coperti:          3
Trade/giorno:            min 1 · media 1.7 · max 2
Durata media holding:    3.8h  (min 0.7h · max 8.0h)
Posizioni contemporanee: MAX 2 · media nel tempo 0.5
Coin distinte:           5
Strategie distinte:      5

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.
```
