"""
Strategia #8 — Grid Trading.

In regime sideways, definisce un range (bande di Bollinger) e piazza ingressi
buy nella metà inferiore / sell nella metà superiore del range. Qui emettiamo il
segnale d'ingresso direzionale; la griglia di ordini multipli viene gestita
dall'execution che scala l'ingresso.
"""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class GridTrading(Strategy):
    name = "grid_trading"
    active_regimes = {Regime.SIDEWAYS}
    description = "Mean-reverting grid all'interno di un range definito dalle bande di Bollinger."

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind("15m")
        if not i or None in (i.bb_upper, i.bb_lower, i.bb_mid, i.rsi):
            return None
        price = asset.price
        rng = i.bb_upper - i.bb_lower
        if rng <= 0:
            return None
        pos_in_range = (price - i.bb_lower) / rng  # 0 = banda inf, 1 = banda sup

        # metà inferiore del range e RSI non in caduta libera -> long verso il centro
        if pos_in_range <= 0.35 and i.rsi > 35:
            conf = 50 + (0.35 - pos_in_range) * 60
            return self._signal(asset, Direction.LONG, conf,
                                "Grid: prezzo nella metà bassa del range sideways",
                                stop=i.bb_lower - rng * 0.1, target=i.bb_mid)
        # metà superiore -> short verso il centro
        if pos_in_range >= 0.65 and i.rsi < 65:
            conf = 50 + (pos_in_range - 0.65) * 60
            return self._signal(asset, Direction.SHORT, conf,
                                "Grid: prezzo nella metà alta del range sideways",
                                stop=i.bb_upper + rng * 0.1, target=i.bb_mid)
        return None
