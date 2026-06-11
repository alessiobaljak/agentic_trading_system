"""Strategia #3 — Breakout: compressione ATR + volume spike sulla rottura di un livello."""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class Breakout(Strategy):
    name = "breakout"
    active_regimes = {Regime.BULL_TRENDING, Regime.BEAR_TRENDING, Regime.HIGH_UNCERTAINTY}
    description = "Rottura delle bande di Bollinger dopo compressione di volatilità, con spike di volume."

    default_params = {
        "compression": 0.07,   # banda/mid sotto questa soglia = compressione
        "volume_spike": 1.8,   # volume > x * media
        "atr_mult_stop": 1.0,
        "rr": 2.5,
        "confidence": 65.0,
    }
    param_grid = {
        "compression": [0.05, 0.07, 0.10],
        "volume_spike": [1.5, 1.8, 2.5],
        "rr": [1.5, 2.0, 2.5, 3.0],
    }

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind("15m")
        if not i or None in (i.bb_upper, i.bb_lower, i.bb_mid, i.atr,
                             i.volume, i.volume_sma):
            return None
        if i.volume_sma == 0 or i.bb_mid == 0:
            return None

        band_width = (i.bb_upper - i.bb_lower)
        compressed = band_width / i.bb_mid < self.p("compression")
        vol_spike = i.volume > self.p("volume_spike") * i.volume_sma
        price = asset.price

        if not (compressed and vol_spike):
            return None

        if price > i.bb_upper:
            stop, target = self._atr_stop_target(asset, Direction.LONG,
                                                  atr_mult_stop=self.p("atr_mult_stop"), rr=self.p("rr"))
            return self._signal(asset, Direction.LONG, self.p("confidence"),
                                "Breakout rialzista dopo compressione, volume spike", stop, target)
        if price < i.bb_lower:
            stop, target = self._atr_stop_target(asset, Direction.SHORT,
                                                  atr_mult_stop=self.p("atr_mult_stop"), rr=self.p("rr"))
            return self._signal(asset, Direction.SHORT, self.p("confidence"),
                                "Breakout ribassista dopo compressione, volume spike", stop, target)
        return None
