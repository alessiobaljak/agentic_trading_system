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

    # soglia: ATR corrente < 70% della banda media implica compressione
    COMPRESSION_RATIO = 0.7
    VOLUME_SPIKE = 1.8

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
        compressed = band_width / i.bb_mid < self.COMPRESSION_RATIO * 0.1  # banda stretta
        vol_spike = i.volume > self.VOLUME_SPIKE * i.volume_sma
        price = asset.price

        if not (compressed and vol_spike):
            return None

        if price > i.bb_upper:
            stop, target = self._atr_stop_target(asset, Direction.LONG, atr_mult_stop=1.0, rr=2.5)
            return self._signal(asset, Direction.LONG, 65,
                                "Breakout rialzista dopo compressione, volume spike", stop, target)
        if price < i.bb_lower:
            stop, target = self._atr_stop_target(asset, Direction.SHORT, atr_mult_stop=1.0, rr=2.5)
            return self._signal(asset, Direction.SHORT, 65,
                                "Breakout ribassista dopo compressione, volume spike", stop, target)
        return None
