"""Strategia #5 — VWAP Reversion: il prezzo torna al VWAP intraday (uso istituzionale)."""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class VwapReversion(Strategy):
    name = "vwap_reversion"
    active_regimes = {Regime.SIDEWAYS, Regime.BULL_TRENDING, Regime.BEAR_TRENDING}
    description = "Quando il prezzo si allontana troppo dal VWAP (in ATR), fade verso il VWAP."

    DEVIATION_ATR = 1.5   # distanza minima dal VWAP in multipli di ATR

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind("5m") or asset.ind("15m")
        if not i or None in (i.vwap, i.atr) or i.atr == 0:
            return None
        price = asset.price
        dev = (price - i.vwap) / i.atr

        # prezzo molto sopra il VWAP -> short verso il VWAP
        if dev >= self.DEVIATION_ATR:
            conf = 55 + min(25, (dev - self.DEVIATION_ATR) * 15)
            return self._signal(asset, Direction.SHORT, conf,
                                f"Prezzo {dev:.1f} ATR sopra VWAP: reversion",
                                stop=price + i.atr * 1.5, target=i.vwap)
        # prezzo molto sotto il VWAP -> long verso il VWAP
        if dev <= -self.DEVIATION_ATR:
            conf = 55 + min(25, (abs(dev) - self.DEVIATION_ATR) * 15)
            return self._signal(asset, Direction.LONG, conf,
                                f"Prezzo {abs(dev):.1f} ATR sotto VWAP: reversion",
                                stop=price - i.atr * 1.5, target=i.vwap)
        return None
