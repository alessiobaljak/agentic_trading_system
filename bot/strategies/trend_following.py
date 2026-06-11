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

    default_params = {
        "rsi_lo": 50.0, "rsi_hi": 70.0,   # banda RSI per i long (specchiata per gli short)
        "require_volume": True,
        "atr_mult_stop": 1.5, "rr": 2.0,
    }
    param_grid = {
        "rsi_hi": [65.0, 70.0, 75.0],
        "require_volume": [True, False],
        "rr": [1.5, 2.0, 2.5],
        "atr_mult_stop": [1.0, 1.5, 2.0],
    }

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i15 = asset.ind("15m")
        i1h = asset.ind("1h")
        if not i15 or not i1h:
            return None
        if None in (i15.ema_fast, i15.ema_slow, i1h.ema_fast, i1h.ema_slow, i15.rsi):
            return None

        vol_ok = (i15.volume is not None and i15.volume_sma not in (None, 0)
                  and i15.volume > i15.volume_sma)
        if self.p("require_volume") and not vol_ok:
            return None

        up_15 = i15.ema_fast > i15.ema_slow
        up_1h = i1h.ema_fast > i1h.ema_slow
        rsi_lo, rsi_hi = self.p("rsi_lo"), self.p("rsi_hi")
        am, rr = self.p("atr_mult_stop"), self.p("rr")

        if up_15 and up_1h and rsi_lo <= i15.rsi < rsi_hi:
            conf = 55 + min(20, (i15.rsi - rsi_lo)) + (10 if vol_ok else 0)
            stop, target = self._atr_stop_target(asset, Direction.LONG, atr_mult_stop=am, rr=rr)
            return self._signal(asset, Direction.LONG, conf,
                                "EMA9>EMA21 su 15m+1h, RSI in spinta", stop, target)
        if (not up_15) and (not up_1h) and (100 - rsi_hi) < i15.rsi <= (100 - rsi_lo):
            conf = 55 + min(20, ((100 - rsi_lo) - i15.rsi)) + (10 if vol_ok else 0)
            stop, target = self._atr_stop_target(asset, Direction.SHORT, atr_mult_stop=am, rr=rr)
            return self._signal(asset, Direction.SHORT, conf,
                                "EMA9<EMA21 su 15m+1h, RSI debole", stop, target)
        return None
