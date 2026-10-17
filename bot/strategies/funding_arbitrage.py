"""Strategia #4 — Funding Rate Arbitrage: short se funding >0.1%, long se <-0.05%."""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class FundingArbitrage(Strategy):
    name = "funding_arbitrage"
    # il funding è un segnale strutturale: attivo in tutti i regimi
    active_regimes = {Regime.BULL_TRENDING, Regime.BEAR_TRENDING,
                      Regime.SIDEWAYS, Regime.HIGH_UNCERTAINTY}
    description = "Sfrutta funding rate estremi: i longs sovra-affollati pagano, fade del crowd."

    SHORT_THRESHOLD = 0.001    # 0.1%
    LONG_THRESHOLD = -0.0005   # -0.05%

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        fr = asset.funding_rate
        if fr is None:
            return None

        # funding molto positivo -> troppi long -> short
        if fr >= self.SHORT_THRESHOLD:
            conf = 55 + min(30, (fr - self.SHORT_THRESHOLD) * 10000)
            stop, target = self._atr_stop_target(asset, Direction.SHORT, atr_mult_stop=2.0, rr=1.5)
            return self._signal(asset, Direction.SHORT, conf,
                                f"Funding {fr*100:.3f}% > 0.1%: long sovra-affollati", stop, target)
        # funding molto negativo -> troppi short -> long
        if fr <= self.LONG_THRESHOLD:
            conf = 55 + min(30, (self.LONG_THRESHOLD - fr) * 10000)
            stop, target = self._atr_stop_target(asset, Direction.LONG, atr_mult_stop=2.0, rr=1.5)
            return self._signal(asset, Direction.LONG, conf,
                                f"Funding {fr*100:.3f}% < -0.05%: short sovra-affollati", stop, target)
        return None
