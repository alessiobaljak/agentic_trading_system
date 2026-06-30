"""
Circuit breakers — controlli di sicurezza che possono SOSPENDERE il trading.

Stato persistito su Firebase RTDB (/risk_state) così sopravvive ai riavvii del bot.
I breaker sono valutati nel `final_gate`: se uno è attivo, l'ordine viene rifiutato.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bot.risk import hard_limits


@dataclass
class CircuitBreakerState:
    daily_pnl_pct: float = 0.0            # PnL % del giorno corrente (sul capitale)
    day_key: str = ""                     # "YYYY-MM-DD" per reset giornaliero
    consecutive_sl: int = 0               # SL consecutivi
    paused_until_ts: float = 0.0          # epoch fino a cui il trading è in pausa
    macro_flat_until_ts: float = 0.0      # epoch fino a cui obbligo flat per evento macro
    halted_for_day: bool = False          # stop totale giornaliero raggiunto
    notes: list[str] = field(default_factory=list)


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class CircuitBreakers:
    """Valuta e aggiorna lo stato dei breaker."""

    def __init__(self, state: Optional[CircuitBreakerState] = None) -> None:
        self.state = state or CircuitBreakerState(day_key=_today_key())
        self._maybe_roll_day()

    def _maybe_roll_day(self) -> None:
        today = _today_key()
        if self.state.day_key != today:
            self.state.day_key = today
            self.state.daily_pnl_pct = 0.0
            self.state.halted_for_day = False
            # gli SL consecutivi NON si azzerano col giorno: rappresentano una serie

    # ---- valutazione ----
    def blocking_reason(self, now_ts: Optional[float] = None) -> Optional[str]:
        """Ritorna il motivo del blocco se un breaker è attivo, altrimenti None."""
        from bot.config import settings
        if settings.BACKTEST_PARITY:
            return None  # parita' col backtest: nessun circuit breaker (il bt non li ha)
        self._maybe_roll_day()
        now = now_ts or time.time()

        if self.state.halted_for_day:
            return (f"Stop giornaliero attivo: oggi la perdita ha toccato il limite "
                    f"-{hard_limits.DAILY_LOSS_LIMIT*100:.0f}% del capitale "
                    f"(PnL giorno ora {self.state.daily_pnl_pct*100:.2f}%). Riprende domani (UTC).")
        if now < self.state.paused_until_ts:
            mins = int((self.state.paused_until_ts - now) / 60)
            return f"Pausa dopo {hard_limits.CONSECUTIVE_SL_LIMIT} SL consecutivi: {mins} min rimanenti"
        if now < self.state.macro_flat_until_ts:
            mins = int((self.state.macro_flat_until_ts - now) / 60)
            return f"Flat obbligatorio per evento macro high-impact: {mins} min rimanenti"
        return None

    def can_trade(self, now_ts: Optional[float] = None) -> bool:
        return self.blocking_reason(now_ts) is None

    # ---- aggiornamenti di stato ----
    def register_trade_result(self, pnl_frac_equity: float, was_stop_loss: bool) -> None:
        """Da chiamare alla chiusura di OGNI trade.
        `pnl_frac_equity` = PnL del trade come FRAZIONE DEL CAPITALE (pnl_usdt/equity),
        NON il rendimento sul margine (che la leva amplifica)."""
        self._maybe_roll_day()
        self.state.daily_pnl_pct += pnl_frac_equity

        if self.state.daily_pnl_pct <= -hard_limits.DAILY_LOSS_LIMIT:
            self.state.halted_for_day = True
            self.state.notes.append(f"HALT giornaliero a {self.state.daily_pnl_pct*100:.2f}%")

        if was_stop_loss:
            self.state.consecutive_sl += 1
            if self.state.consecutive_sl >= hard_limits.CONSECUTIVE_SL_LIMIT:
                self.state.paused_until_ts = time.time() + hard_limits.CONSECUTIVE_SL_PAUSE
                self.state.consecutive_sl = 0
                self.state.notes.append("Pausa 4h dopo SL consecutivi")
        else:
            self.state.consecutive_sl = 0

    def set_macro_flat_window(self, event_ts: float) -> None:
        """Imposta la finestra flat ±MACRO_FLAT_HOURS attorno a un evento macro."""
        flat_until = event_ts + hard_limits.MACRO_FLAT_HOURS * 3600
        self.state.macro_flat_until_ts = max(self.state.macro_flat_until_ts, flat_until)

    def in_macro_window(self, event_ts: float, now_ts: Optional[float] = None) -> bool:
        """True se `now` è entro ±MACRO_FLAT_HOURS dall'evento."""
        now = now_ts or time.time()
        window = hard_limits.MACRO_FLAT_HOURS * 3600
        return abs(now - event_ts) <= window

    # ---- serializzazione (per Firebase RTDB) ----
    def to_dict(self) -> dict:
        s = self.state
        return {
            "daily_pnl_pct": s.daily_pnl_pct,
            "day_key": s.day_key,
            "consecutive_sl": s.consecutive_sl,
            "paused_until_ts": s.paused_until_ts,
            "macro_flat_until_ts": s.macro_flat_until_ts,
            "halted_for_day": s.halted_for_day,
            "notes": s.notes[-20:],
        }

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "CircuitBreakers":
        if not data:
            return cls()
        return cls(CircuitBreakerState(
            daily_pnl_pct=data.get("daily_pnl_pct", 0.0),
            day_key=data.get("day_key", _today_key()),
            consecutive_sl=data.get("consecutive_sl", 0),
            paused_until_ts=data.get("paused_until_ts", 0.0),
            macro_flat_until_ts=data.get("macro_flat_until_ts", 0.0),
            halted_for_day=data.get("halted_for_day", False),
            notes=data.get("notes", []),
        ))
