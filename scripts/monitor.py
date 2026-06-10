"""
Monitoring job (GitHub Action ogni 15 min).

Legge l'heartbeat del bot da Firebase RTDB e invia un alert Telegram se il bot
è offline (heartbeat più vecchio di HEARTBEAT_MAX_AGE secondi) o se la daily loss
ha superato il 3%.
"""
from __future__ import annotations

import time

from bot.core.firebase_client import get_firebase
from bot.execution.notifier import TelegramNotifier

HEARTBEAT_MAX_AGE = 180  # secondi (il bot scrive l'heartbeat ad ogni ciclo)


def main() -> None:
    fb = get_firebase()
    notifier = TelegramNotifier()

    status = fb.get_rtdb("/bot_status") or {}
    heartbeat = status.get("heartbeat")
    now = time.time()

    if not heartbeat or (now - float(heartbeat)) > HEARTBEAT_MAX_AGE:
        age = "mai" if not heartbeat else f"{int(now - float(heartbeat))}s fa"
        print(f"[monitor] bot OFFLINE (ultimo heartbeat: {age})")
        notifier.bot_offline()
    else:
        print(f"[monitor] bot ONLINE (heartbeat {int(now - float(heartbeat))}s fa, "
              f"regime={status.get('regime')})")

    # alert daily loss > 3%
    risk_state = fb.get_rtdb("/risk_state") or {}
    daily = risk_state.get("daily_pnl_pct", 0.0)
    if daily <= -0.03:
        print(f"[monitor] daily loss {daily*100:.1f}%")
        notifier.daily_loss(abs(daily))


if __name__ == "__main__":
    main()
