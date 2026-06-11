"""
Verifica self-service delle credenziali.

Esegui QUESTO script dove vivono i segreti (VPS o locale con un .env compilato):

    python -m scripts.verify_keys

Controlla la validità di ogni credenziale facendo una chiamata autenticata
leggera e NON stampa mai i valori segreti — solo OK / FAIL / assente.
Pensato per essere lanciato da te, non da una sessione condivisa.
"""
from __future__ import annotations

import json
import os
import sys

from bot.config import settings

OK = "✅ OK"
FAIL = "❌ FAIL"
SKIP = "➖ assente (non configurata)"


def _line(name: str, status: str, detail: str = "") -> None:
    print(f"{status:<28} {name}" + (f"  — {detail}" if detail else ""))


def check_binance() -> None:
    if not settings.BINANCE_API_KEY or not settings.BINANCE_API_SECRET:
        return _line("Binance Futures", SKIP)
    try:
        from binance.client import Client
        c = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET,
                   testnet=settings.BINANCE_TESTNET)
        acc = c.futures_account()
        bal = acc.get("totalWalletBalance", "?")
        env = "testnet" if settings.BINANCE_TESTNET else "MAINNET"
        # avviso se le chiavi possono prelevare (rischio): non possiamo leggerlo
        _line("Binance Futures", OK, f"{env}, wallet={bal} USDT")
    except Exception as exc:  # noqa: BLE001
        _line("Binance Futures", FAIL, str(exc)[:120])


def check_anthropic() -> None:
    if not settings.ANTHROPIC_API_KEY:
        return _line("Anthropic (Claude)", SKIP)
    try:
        import anthropic
        c = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        r = c.messages.create(model=settings.ANTHROPIC_MODEL, max_tokens=5,
                              messages=[{"role": "user", "content": "ping"}])
        _line("Anthropic (Claude)", OK, f"model={settings.ANTHROPIC_MODEL}")
    except Exception as exc:  # noqa: BLE001
        _line("Anthropic (Claude)", FAIL, str(exc)[:120])


def check_lunarcrush() -> None:
    if not settings.LUNARCRUSH_API_KEY:
        return _line("LunarCrush (opzionale)", SKIP)
    import requests
    try:
        r = requests.get("https://lunarcrush.com/api4/public/coins/BTC/v1",
                         headers={"Authorization": f"Bearer {settings.LUNARCRUSH_API_KEY}"},
                         timeout=10)
        _line("LunarCrush (opzionale)", OK if r.status_code == 200 else FAIL, f"HTTP {r.status_code}")
    except Exception as exc:  # noqa: BLE001
        _line("LunarCrush (opzionale)", FAIL, str(exc)[:120])


def check_coingecko() -> None:
    """Fonte sentiment GRATUITA (sostituisce LunarCrush). Sempre testata."""
    import requests
    try:
        r = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin",
                         params={"localization": "false", "tickers": "false",
                                 "market_data": "false", "community_data": "false",
                                 "developer_data": "false"}, timeout=10)
        ok = r.status_code == 200 and "sentiment_votes_up_percentage" in r.json()
        _line("CoinGecko sentiment (gratis)", OK if ok else FAIL, f"HTTP {r.status_code}")
    except Exception as exc:  # noqa: BLE001
        _line("CoinGecko sentiment (gratis)", FAIL, str(exc)[:120])


def check_binance_futures_data() -> None:
    """OI / long-short pubblici di Binance (gratis, sostituiscono Coinglass)."""
    import requests
    try:
        r = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio",
                         params={"symbol": "BTCUSDT", "period": "1h", "limit": 1}, timeout=10)
        ok = r.status_code == 200 and isinstance(r.json(), list)
        _line("Binance futures-data (gratis)", OK if ok else FAIL, f"HTTP {r.status_code}")
    except Exception as exc:  # noqa: BLE001
        _line("Binance futures-data (gratis)", FAIL, str(exc)[:120])


def check_coinglass() -> None:
    if not settings.COINGLASS_API_KEY:
        return _line("Coinglass (opzionale)", SKIP)
    import requests
    try:
        r = requests.get("https://open-api-v3.coinglass.com/api/futures/supported-coins",
                         headers={"coinglassSecret": settings.COINGLASS_API_KEY}, timeout=10)
        _line("Coinglass (opzionale)", OK if r.status_code == 200 else FAIL, f"HTTP {r.status_code}")
    except Exception as exc:  # noqa: BLE001
        _line("Coinglass (opzionale)", FAIL, str(exc)[:120])


def check_newsapi() -> None:
    if not settings.NEWSAPI_KEY:
        return _line("NewsAPI", SKIP)
    import requests
    try:
        r = requests.get("https://newsapi.org/v2/everything",
                         params={"q": "bitcoin", "pageSize": 1, "apiKey": settings.NEWSAPI_KEY},
                         timeout=10)
        _line("NewsAPI", OK if r.status_code == 200 else FAIL, f"HTTP {r.status_code}")
    except Exception as exc:  # noqa: BLE001
        _line("NewsAPI", FAIL, str(exc)[:120])


def check_firebase() -> None:
    if not settings.FIREBASE_SERVICE_ACCOUNT:
        return _line("Firebase (service account)", SKIP)
    try:
        from bot.core.firebase_client import resolve_service_account
        if resolve_service_account(settings.FIREBASE_SERVICE_ACCOUNT) is None:
            raise ValueError("vuoto")
    except Exception as exc:  # noqa: BLE001
        return _line("Firebase (service account)", FAIL, f"JSON/file non valido: {str(exc)[:60]}")
    try:
        from bot.core.firebase_client import FirebaseClient
        fb = FirebaseClient()
        if not fb.is_live:
            return _line("Firebase (service account)", FAIL, "init non riuscito (vedi log sopra)")
        fb.set_doc("_healthcheck", "ping", {"ok": True})
        got = fb.get_doc("_healthcheck", "ping")
        ok = bool(got and got.get("ok"))
        rtdb = " + RTDB" if settings.FIREBASE_RTDB_URL else " (RTDB URL assente!)"
        _line("Firebase", OK if ok else FAIL, f"Firestore R/W{rtdb}")
    except Exception as exc:  # noqa: BLE001
        _line("Firebase", FAIL, str(exc)[:120])


def check_telegram() -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return _line("Telegram", SKIP)
    import requests
    try:
        r = requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe", timeout=10)
        if r.status_code != 200:
            return _line("Telegram", FAIL, f"getMe HTTP {r.status_code}")
        name = r.json().get("result", {}).get("username", "?")
        _line("Telegram", OK, f"@{name} (chat_id impostato)")
    except Exception as exc:  # noqa: BLE001
        _line("Telegram", FAIL, str(exc)[:120])


def check_vercel_client() -> None:
    """La dashboard usa le NEXT_PUBLIC_FIREBASE_* (config client). Qui ne controllo
    solo la PRESENZA — vanno impostate su Vercel, non in questo .env."""
    keys = ["NEXT_PUBLIC_FIREBASE_API_KEY", "NEXT_PUBLIC_FIREBASE_PROJECT_ID",
            "NEXT_PUBLIC_FIREBASE_DATABASE_URL", "NEXT_PUBLIC_FIREBASE_APP_ID"]
    present = [k for k in keys if os.getenv(k)]
    if not present:
        return _line("Vercel/dashboard (NEXT_PUBLIC_*)", SKIP,
                     "da impostare su Vercel, non qui")
    _line("Vercel/dashboard (NEXT_PUBLIC_*)", OK if len(present) == len(keys) else FAIL,
          f"{len(present)}/{len(keys)} presenti")


def main() -> int:
    print("=" * 60)
    print("VERIFICA CREDENZIALI — i valori segreti NON vengono stampati")
    print(f"DRY_RUN={settings.DRY_RUN}  BINANCE_TESTNET={settings.BINANCE_TESTNET}")
    print("=" * 60)
    check_binance()
    check_anthropic()
    check_firebase()
    check_telegram()
    print("--- fonti dati gratuite (sentiment / on-chain) ---")
    check_coingecko()
    check_binance_futures_data()
    check_newsapi()
    print("--- opzionali a pagamento (non necessari) ---")
    check_lunarcrush()
    check_coinglass()
    check_vercel_client()
    print("=" * 60)
    print("Nota: 'assente' = credenziale non configurata in questo ambiente.")
    print("Esegui questo script sulla VPS o in locale con un .env compilato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
