"""Strategia #2 — Mean Reversion: Bollinger extremes + RSI oversold/overbought."""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class MeanReversion(Strategy):
    name = "mean_reversion"
    active_regimes = {Regime.SIDEWAYS, Regime.HIGH_UNCERTAINTY}
    description = "Rientro verso la media quando il prezzo tocca le bande di Bollinger con RSI estremo."

    default_params = {
        "rsi_oversold": 30.0, "rsi_overbought": 70.0,
        "atr_mult_stop": 1.2,
    }
    param_grid = {
        "rsi_oversold": [20.0, 25.0, 30.0],
        "rsi_overbought": [70.0, 75.0, 80.0],
        "atr_mult_stop": [1.0, 1.2, 1.8],
    }

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind(self._tf)
        if not i or None in (i.bb_upper, i.bb_lower, i.bb_mid, i.rsi):
            return None
        price = asset.price
        oversold, overbought = self.p("rsi_oversold"), self.p("rsi_overbought")
        am = self.p("atr_mult_stop")

        if price <= i.bb_lower and i.rsi <= oversold:
            conf = 55 + min(25, (oversold - i.rsi))
            return self._signal(asset, Direction.LONG, conf,
                                f"Prezzo sotto BB inferiore, RSI={i.rsi:.0f} oversold",
                                stop=price - (i.atr or 0) * am if i.atr else None, target=i.bb_mid)
        if price >= i.bb_upper and i.rsi >= overbought:
            conf = 55 + min(25, (i.rsi - overbought))
            return self._signal(asset, Direction.SHORT, conf,
                                f"Prezzo sopra BB superiore, RSI={i.rsi:.0f} overbought",
                                stop=price + (i.atr or 0) * am if i.atr else None, target=i.bb_mid)
        return None
