"""Alert Telegram: bot offline, liquidazione, daily loss > 3%, kill switch."""
from __future__ import annotations

import requests

from bot.config import settings


class TelegramNotifier:
    def __init__(self) -> None:
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, text: str) -> None:
        if not self.enabled:
            print(f"[telegram:disabled] {text}")
            return
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"},
                timeout=8,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[telegram] invio fallito: {exc}")

    # alert tipizzati
    def bot_offline(self) -> None:
        self.send("🔴 <b>BOT OFFLINE</b> — heartbeat mancante.")

    def liquidation(self, symbol: str) -> None:
        self.send(f"💥 <b>LIQUIDAZIONE</b> su {symbol}!")

    def daily_loss(self, pct: float) -> None:
        self.send(f"⚠️ <b>Daily loss {pct*100:.1f}%</b> — soglia 3% superata.")

    def kill_switch(self) -> None:
        self.send("🛑 <b>KILL SWITCH</b> attivato — tutte le posizioni chiuse.")
