# 0006-supervisor-budget.req

_eseguito: 2026-08-19 10:27 UTC_

**richiesta:** `supervisor`
**eseguito:** `.venv/bin/python -m scripts.supervisor --dry-run`
**esito:** codice 0 in 1.5s

```
[firebase] connesso (Firestore + RTDB)
[supervisor] validate=0 ready=False stagnazione=5.9g · valutazioni=41940 passate=94 (tasso 0.224%)
[supervisor] SET_PARAM: 22 candidate sono fermate SOLO da 'win_rate' (mediana: manca 1.2%). La mossa ne dovrebbe sbloccare ~12, e il budget la consente (spazio 6x, attese 0.030/giorno contro un tetto di 1)
[supervisor]   GATE_WIN_RATE_FLOOR: 0.45 -> 0.443912
```
