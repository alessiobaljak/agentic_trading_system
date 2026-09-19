# 0096-chiave-prova-diretta.req

_eseguito: 2026-09-19 14:42 UTC_

**richiesta:** `connettivita`
**eseguito:** `.venv/bin/python -m scripts.connectivity_check`
**esito:** codice 0 in 3.5s

```
============================================================
CONNECTIVITY CHECK (eseguito da GitHub Actions)
Nessun valore segreto viene stampato.
============================================================
[firebase] connesso (Firestore + RTDB)
✅ OK         Firebase  — Firestore R/W + RTDB R/W
❌ FAIL       Anthropic  — model=claude-opus-4-8 :: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'This API key is not scoped to a workspace, so this request must include the anthropic-workspace-id header with the ID of the workspace to use. Add the header, or use an API key that is scoped to a workspace.'}
✅ OK         Telegram  — HTTP 200
✅ OK         Binance klines (pubblico)  — HTTP 200
✅ OK         Binance futures-data OI/LS (pubblico)  — HTTP 200
✅ OK         CoinGecko sentiment (gratis)  — HTTP 200
❌ FAIL       LunarCrush (opzionale)  — coins/BTC -> HTTP 402 | coins/list -> HTTP 402
➖ assente    Coinglass (opzionale)
✅ OK         NewsAPI  — HTTP 200
============================================================
RISULTATO: GitHub ↔ Firebase OK ✅
```
