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

    def trade_opened(self, symbol: str, strategy: str, direction: str,
                     entry: float, qty: float, leverage: float,
                     stop: float, take_profit: float, dry_run: bool = True) -> None:
        tag = "📝 PAPER" if dry_run else "🔴 LIVE"
        arrow = "🟢 LONG" if str(direction).lower() == "long" else "🔻 SHORT"
        self.send(
            f"{tag} · <b>APERTA</b> {arrow} <b>{symbol}</b>\n"
            f"strategia: {strategy}\n"
            f"entry: {entry:g} · qty: {qty:g} · leva: {leverage:g}x\n"
            f"SL: {stop:g} · TP: {take_profit:g}"
        )

    def trade_closed(self, symbol: str, strategy: str, direction: str,
                     exit_price: float, pnl: float, pnl_pct: float,
                     reason: str, dry_run: bool = True) -> None:
        tag = "📝 PAPER" if dry_run else "🔴 LIVE"
        emoji = "✅" if pnl >= 0 else "❌"
        self.send(
            f"{tag} · <b>CHIUSA</b> {emoji} <b>{symbol}</b> ({reason})\n"
            f"strategia: {strategy} · {direction}\n"
            f"uscita: {exit_price:g}\n"
            f"PnL: <b>{pnl:+.2f} USDT</b> ({pnl_pct*100:+.1f}%)"
        )
