# 0319-ingressi-esito-controllo.req

_eseguito: 2026-09-27 19:57 UTC_

**richiesta:** `ingressi-esito`
**eseguito:** `.venv/bin/python -m scripts.ingressi_report --esito`
**esito:** codice 0 in 1.3s

```
[ingressi] referto /root/agentic_trading_system/data/ingressi_ultimo.txt · scritto 2026-09-27 19:56:24 UTC · processo 1785970 ANCORA IN CORSO (il referto e' parziale)
--------------------------------------------------------------------------
[firebase] connesso (Firestore + RTDB)
[ingressi] su file, pid 1785970, avvio 2026-09-27 19:56:23 UTC
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
==========================================================================
INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'
==========================================================================
PAPER: 135 trade chiusi su 66 coppie · rigirate 66 · tolleranza 2 barre · deadline nessuna

── SUIUSDT|gen_490a90e5 · 7 trade · 15m · scala 1/2/3 · BE si · keep globale
```
