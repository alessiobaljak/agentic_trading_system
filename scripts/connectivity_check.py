"""
Connectivity check per la CI (GitHub Actions).
(re-run trigger)

A differenza di verify_keys (che è informativo e non fallisce mai), questo script
ESCE CON CODICE != 0 se la connessione a Firebase non funziona — così l'esito del
workflow è un segnale binario per "GitHub riesce a comunicare con Firebase?".

Non stampa MAI valori segreti. Pensato per girare dentro GitHub Actions con i
GitHub Secrets iniettati come variabili d'ambiente.
"""
from __future__ import annotations

import sys

from bot.config import settings

OK = "✅ OK"
FAIL = "❌ FAIL"
SKIP = "➖ assente"


def _line(name: str, status: str, detail: str = "") -> None:
    print(f"{status:<12} {name}" + (f"  — {detail}" if detail else ""))


def check_firebase() -> bool:
    """Ritorna True se Firebase è raggiungibile in lettura/scrittura."""
    if not settings.FIREBASE_SERVICE_ACCOUNT:
        _line("Firebase", FAIL, "secret FIREBASE_SERVICE_ACCOUNT NON impostato")
        return False
    try:
        import json
        json.loads(settings.FIREBASE_SERVICE_ACCOUNT)
    except Exception:  # noqa: BLE001
        _line("Firebase", FAIL, "FIREBASE_SERVICE_ACCOUNT non è JSON valido")
        return False
    try:
        from bot.core.firebase_client import FirebaseClient
        fb = FirebaseClient()
        if not fb.is_live:
            _line("Firebase", FAIL, "init non riuscito (credenziali/permessi)")
            return False
        fb.set_doc("_healthcheck", "github_ci", {"ok": True, "src": "github_actions"})
        got = fb.get_doc("_healthcheck", "github_ci")
        ok = bool(got and got.get("ok"))
        rtdb_ok = True
        rtdb_detail = "Firestore R/W"
        if settings.FIREBASE_RTDB_URL:
            try:
                fb.set_rtdb("/_healthcheck/github_ci", {"ok": True})
                rtdb_ok = bool((fb.get_rtdb("/_healthcheck/github_ci") or {}).get("ok"))
                rtdb_detail += " + RTDB R/W"
            except Exception as exc:  # noqa: BLE001
                rtdb_ok = False
                rtdb_detail += f" (RTDB FAIL: {str(exc)[:60]})"
        else:
            rtdb_detail += " (RTDB_URL assente — impostalo per lo stato live)"
        _line("Firebase", OK if (ok and rtdb_ok) else FAIL, rtdb_detail)
        return ok and rtdb_ok
    except Exception as exc:  # noqa: BLE001
        _line("Firebase", FAIL, str(exc)[:140])
        return False


def info_others() -> None:
    """Controlli informativi (non bloccanti) degli altri servizi."""
    import requests
    # Anthropic (serve al learning notturno + orchestratore)
    if settings.ANTHROPIC_API_KEY:
        try:
            import anthropic
            anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY).messages.create(
                model=settings.ANTHROPIC_MODEL, max_tokens=5,
                messages=[{"role": "user", "content": "ping"}])
            _line("Anthropic", OK, f"model={settings.ANTHROPIC_MODEL}")
        except Exception as exc:  # noqa: BLE001
            # messaggio completo per diagnosi (nessun segreto qui)
            _line("Anthropic", FAIL, f"model={settings.ANTHROPIC_MODEL} :: {str(exc)[:300]}")
    else:
        _line("Anthropic", SKIP)
    # Telegram (alert)
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe", timeout=10)
            _line("Telegram", OK if r.status_code == 200 else FAIL, f"HTTP {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            _line("Telegram", FAIL, str(exc)[:100])
    else:
        _line("Telegram", SKIP)


def main() -> int:
    print("=" * 60)
    print("CONNECTIVITY CHECK (eseguito da GitHub Actions)")
    print("Nessun valore segreto viene stampato.")
    print("=" * 60)
    firebase_ok = check_firebase()
    info_others()
    print("=" * 60)
    if firebase_ok:
        print("RISULTATO: GitHub ↔ Firebase OK ✅")
        return 0
    print("RISULTATO: GitHub NON riesce a comunicare con Firebase ❌")
    print("→ Controlla il secret FIREBASE_SERVICE_ACCOUNT (Settings → Secrets → Actions).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
