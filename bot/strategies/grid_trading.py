"""
Strategia #8 — Grid Trading.

In regime sideways entra nella metà bassa del range (long) o alta (short),
verso il centro. Parametrizzata per poter essere resa molto più selettiva
(o di fatto disattivata via peso) dall'ottimizzatore.
"""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class GridTrading(Strategy):
    name = "grid_trading"
    active_regimes = {Regime.SIDEWAYS}
    description = "Mean-reverting grid in un range Bollinger (solo zone estreme del range)."

    default_params = {
        "low_band": 0.35,    # entra long solo sotto questa posizione nel range
        "high_band": 0.65,   # entra short solo sopra
        "rsi_floor": 35.0,
        "rsi_ceil": 65.0,
        "stop_pad": 0.10,    # ampiezza stop oltre la banda (in frazioni di range)
    }
    param_grid = {
        "low_band": [0.15, 0.25, 0.35],   # più basso = più selettivo
        "high_band": [0.65, 0.75, 0.85],
        "stop_pad": [0.05, 0.10, 0.25],
    }

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind(self._tf)
        if not i or None in (i.bb_upper, i.bb_lower, i.bb_mid, i.rsi):
            return None
        price = asset.price
        rng = i.bb_upper - i.bb_lower
        if rng <= 0:
            return None
        pos = (price - i.bb_lower) / rng
        low_band, high_band = self.p("low_band"), self.p("high_band")
        pad = self.p("stop_pad")

        if pos <= low_band and i.rsi > self.p("rsi_floor"):
            conf = 50 + (low_band - pos) * 60
            return self._signal(asset, Direction.LONG, conf,
                                "Grid: metà bassa del range sideways",
                                stop=i.bb_lower - rng * pad, target=i.bb_mid)
        if pos >= high_band and i.rsi < self.p("rsi_ceil"):
            conf = 50 + (pos - high_band) * 60
            return self._signal(asset, Direction.SHORT, conf,
                                "Grid: metà alta del range sideways",
                                stop=i.bb_upper + rng * pad, target=i.bb_mid)
        return None
