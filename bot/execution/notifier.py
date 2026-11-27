"""Alert Telegram: bot offline, liquidazione, daily loss > 3%, kill switch; da scripts/monitor.py anche gli allarmi
di demo e conto vero."""
from __future__ import annotations

from urllib.parse import quote

import requests

from bot.config import settings


class TelegramNotifier:
    def __init__(self) -> None:
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, text: str) -> bool:
        """Manda il messaggio. Non solleva mai: True solo se Telegram l'ha accettato.

        Audit del 26 novembre 2026 (salute-3): prima la risposta non si guardava, e un rifiuto (400 testo non valido, 403 chat
        bloccata, 429 troppi messaggi) non lasciava nessuna traccia. Ora un rifiuto si scrive nel log con il codice e il motivo
        dato da Telegram. Il token non va mai nel log (i log finiscono in ops/results, in un repository pubblico): un errore di rete
        di `requests` puo' contenere l'indirizzo intero, con il token dentro."""
        if not self.enabled:
            print(f"[telegram:disabled] {text}")
            return False
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"},
                timeout=8,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[telegram] invio fallito: {self._senza_token(exc)}")
            return False
        try:
            if r.ok:
                return True
            print(f"[telegram] messaggio rifiutato da Telegram: HTTP {r.status_code} {self._motivo(r)}")
        except Exception as exc:  # noqa: BLE001
            print(f"[telegram] risposta di Telegram non leggibile: {self._senza_token(exc)}")
        return False

    def _senza_token(self, testo) -> str:
        """Il testo con il token sostituito (mai il token in un log). Non solleva: lo chiama anche chi gestisce un errore."""
        try:
            testo = str(testo)
            if self.token:
                for forma in (str(self.token), quote(str(self.token), safe="")):   # anche scritto come in un indirizzo
                    testo = testo.replace(forma, "<token>")
            return testo
        except Exception:  # noqa: BLE001
            return "(testo dell'errore non leggibile)"

    def _motivo(self, r) -> str:
        """Il motivo del rifiuto come lo dice Telegram (`description`, piu' l'attesa chiesta con il 429), al massimo
        200 lettere."""
        try:
            dati = r.json()
            motivo = str(dati.get("description") or "")
            attesa = (dati.get("parameters") or {}).get("retry_after")
            if attesa is not None:
                motivo += f" (riprovare fra {attesa} s)"
        except Exception:  # noqa: BLE001
            motivo = str(getattr(r, "text", "") or "")
        return self._senza_token(motivo)[:200]

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
