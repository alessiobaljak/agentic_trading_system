"""
Strategia #7 — Liquidity Grab.

Identifica i fake breakout progettati per prendere gli stop prima di invertire
(comportamento delle balene). Pattern: il prezzo buca un estremo recente (banda di
Bollinger) con uno spike, ma chiude rapidamente di nuovo dentro il range -> si trada
l'inversione nella direzione opposta al falso breakout.
"""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class LiquidityGrab(Strategy):
    name = "liquidity_grab"
    active_regimes = {Regime.HIGH_UNCERTAINTY, Regime.SIDEWAYS}
    description = "Fade dei falsi breakout (stop hunt) con rientro nel range e volume anomalo."

    default_params = {"volume_spike": 2.0, "atr_mult_stop": 1.0}
    param_grid = {"volume_spike": [2.0, 2.5, 3.0], "atr_mult_stop": [0.8, 1.0, 1.5]}

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind(self._tf)
        if not i or None in (i.bb_upper, i.bb_lower, i.bb_mid, i.close,
                             i.volume, i.volume_sma, i.atr):
            return None
        if i.volume_sma == 0:
            return None

        price = asset.price
        if i.volume <= self.p("volume_spike") * i.volume_sma:
            return None
        am = self.p("atr_mult_stop")

        if price >= i.bb_upper * 0.995 and i.close < i.bb_upper and i.close > i.bb_mid:
            return self._signal(asset, Direction.SHORT, 58,
                                "Sospetto stop hunt sopra la resistenza, rientro nel range",
                                stop=price + i.atr * am, target=i.bb_mid)
        if price <= i.bb_lower * 1.005 and i.close > i.bb_lower and i.close < i.bb_mid:
            return self._signal(asset, Direction.LONG, 58,
                                "Sospetto stop hunt sotto il supporto, rientro nel range",
                                stop=price - i.atr * am, target=i.bb_mid)
        return None
