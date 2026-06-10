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

    VOLUME_SPIKE = 2.0

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind("15m")
        if not i or None in (i.bb_upper, i.bb_lower, i.bb_mid, i.close,
                             i.volume, i.volume_sma, i.atr):
            return None
        if i.volume_sma == 0:
            return None

        price = asset.price
        vol_spike = i.volume > self.VOLUME_SPIKE * i.volume_sma
        if not vol_spike:
            return None

        # Falso breakout rialzista: il prezzo ha toccato/superato la banda superiore con
        # volume anomalo ma ha richiuso dentro il range (close < bb_upper) -> stop hunt -> short.
        if price >= i.bb_upper * 0.995 and i.close < i.bb_upper and i.close > i.bb_mid:
            return self._signal(asset, Direction.SHORT, 58,
                                "Sospetto stop hunt sopra la resistenza, rientro nel range",
                                stop=price + i.atr * 1.0, target=i.bb_mid)
        # Falso breakout ribassista: stop hunt sotto il supporto -> long.
        if price <= i.bb_lower * 1.005 and i.close > i.bb_lower and i.close < i.bb_mid:
            return self._signal(asset, Direction.LONG, 58,
                                "Sospetto stop hunt sotto il supporto, rientro nel range",
                                stop=price - i.atr * 1.0, target=i.bb_mid)
        return None
