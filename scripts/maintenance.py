"""
Attiva/disattiva la modalita' MANUTENZIONE.

Quando e' attiva, il job di monitoraggio (scripts/monitor.py, ogni 15 min) NON
manda l'alert Telegram "bot OFFLINE": utile quando il bot e' fermo di proposito
(rebuild GATE 1, deploy, debug). Il bot DISATTIVA da solo questo flag al prossimo
avvio, quindi il monitoraggio torna attivo per il live senza che tu te ne ricordi.

Uso (sul VPS, col bot fermo):
    .venv/bin/python -m scripts.maintenance on    # silenzia gli alert "offline"
    .venv/bin/python -m scripts.maintenance off   # riattiva il monitoraggio
"""
from __future__ import annotations

import sys

from bot.core.firebase_client import get_firebase


def main() -> int:
    arg = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    if arg not in ("on", "off"):
        print("uso: python -m scripts.maintenance on|off")
        return 1
    val = arg == "on"
    get_firebase().set_rtdb("/commands/maintenance", val)
    print(f"[maintenance] manutenzione = {val} "
          f"({'alert offline SILENZIATI' if val else 'monitoraggio ATTIVO'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
