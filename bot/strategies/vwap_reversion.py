"""Strategia #5 — VWAP Reversion: il prezzo torna al VWAP intraday (uso istituzionale)."""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class VwapReversion(Strategy):
    name = "vwap_reversion"
    active_regimes = {Regime.SIDEWAYS, Regime.BULL_TRENDING, Regime.BEAR_TRENDING}
    description = "Quando il prezzo si allontana troppo dal VWAP (in ATR), fade verso il VWAP."

    default_params = {
        "deviation_atr": 1.5,   # distanza minima dal VWAP (in ATR)
        "atr_mult_stop": 1.5,
    }
    param_grid = {
        "deviation_atr": [1.5, 2.0, 2.5, 3.0],   # soglie più alte = meno trade, più selettivo
        "atr_mult_stop": [1.0, 1.5, 2.0],
    }

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind(self._tf)
        if not i or None in (i.vwap, i.atr) or i.atr == 0:
            return None
        price = asset.price
        dev = (price - i.vwap) / i.atr
        threshold = self.p("deviation_atr")
        am = self.p("atr_mult_stop")

        if dev >= threshold:
            conf = 55 + min(25, (dev - threshold) * 15)
            return self._signal(asset, Direction.SHORT, conf,
                                f"Prezzo {dev:.1f} ATR sopra VWAP: reversion",
                                stop=price + i.atr * am, target=i.vwap)
        if dev <= -threshold:
            conf = 55 + min(25, (abs(dev) - threshold) * 15)
            return self._signal(asset, Direction.LONG, conf,
                                f"Prezzo {abs(dev):.1f} ATR sotto VWAP: reversion",
                                stop=price - i.atr * am, target=i.vwap)
        return None
