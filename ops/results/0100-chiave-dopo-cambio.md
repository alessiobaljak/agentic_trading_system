# 0100-chiave-dopo-cambio.req

_eseguito: 2026-09-19 16:13 UTC_

**richiesta:** `connettivita`
**eseguito:** `.venv/bin/python -m scripts.connectivity_check`
**esito:** codice 0 in 16.5s

```
============================================================
CONNECTIVITY CHECK (eseguito da GitHub Actions)
Nessun valore segreto viene stampato.
============================================================
[firebase] connesso (Firestore + RTDB)
✅ OK         Firebase  — Firestore R/W + RTDB R/W
✅ OK         Anthropic  — model=claude-opus-4-8
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
