"""Strategia #1 — Trend Following: EMA 9/21 dual timeframe + RSI + volume confirm."""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class TrendFollowing(Strategy):
    name = "trend_following"
    active_regimes = {Regime.BULL_TRENDING, Regime.BEAR_TRENDING}
    description = "EMA 9/21 allineate su 15m e 1h, confermate da RSI e volume."

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i15 = asset.ind("15m")
        i1h = asset.ind("1h")
        if not i15 or not i1h:
            return None
        if None in (i15.ema_fast, i15.ema_slow, i1h.ema_fast, i1h.ema_slow, i15.rsi):
            return None

        vol_ok = i15.volume is not None and i15.volume_sma not in (None, 0) and \
            i15.volume > i15.volume_sma
        up_15 = i15.ema_fast > i15.ema_slow
        up_1h = i1h.ema_fast > i1h.ema_slow

        # LONG: trend rialzista allineato sui due timeframe, RSI con momentum ma non ipercomprato
        if up_15 and up_1h and 50 <= i15.rsi < 70 and vol_ok:
            conf = 55 + min(20, (i15.rsi - 50)) + (10 if vol_ok else 0)
            stop, target = self._atr_stop_target(asset, Direction.LONG)
            return self._signal(asset, Direction.LONG, conf,
                                "EMA9>EMA21 su 15m+1h, RSI in spinta, volume sopra media",
                                stop, target)
        # SHORT: trend ribassista allineato
        if (not up_15) and (not up_1h) and 30 < i15.rsi <= 50 and vol_ok:
            conf = 55 + min(20, (50 - i15.rsi)) + (10 if vol_ok else 0)
            stop, target = self._atr_stop_target(asset, Direction.SHORT)
            return self._signal(asset, Direction.SHORT, conf,
                                "EMA9<EMA21 su 15m+1h, RSI debole, volume sopra media",
                                stop, target)
        return None
