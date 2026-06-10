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

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind("15m")
        if not i or None in (i.bb_upper, i.bb_lower, i.bb_mid, i.rsi):
            return None
        price = asset.price

        # LONG: prezzo sotto banda inferiore + RSI oversold -> ritorno alla media
        if price <= i.bb_lower and i.rsi <= 30:
            conf = 55 + min(25, (30 - i.rsi))
            return self._signal(asset, Direction.LONG, conf,
                                f"Prezzo sotto BB inferiore, RSI={i.rsi:.0f} oversold",
                                stop=price - (i.atr or 0) * 1.2 if i.atr else None,
                                target=i.bb_mid)
        # SHORT: prezzo sopra banda superiore + RSI overbought
        if price >= i.bb_upper and i.rsi >= 70:
            conf = 55 + min(25, (i.rsi - 70))
            return self._signal(asset, Direction.SHORT, conf,
                                f"Prezzo sopra BB superiore, RSI={i.rsi:.0f} overbought",
                                stop=price + (i.atr or 0) * 1.2 if i.atr else None,
                                target=i.bb_mid)
        return None
