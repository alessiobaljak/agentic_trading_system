"""
Strategia #6 — Momentum Cross-Asset.

Quando BTC rompe un livello, le altcoin tendono a seguire con lag di 15-30 min.
Si trada quel lag: se BTC ha un forte momentum su 15m e l'altcoin NON si è ancora
mossa nella stessa direzione, si entra anticipando il movimento.
"""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy

BTC_SYMBOL = "BTCUSDT"


@register_strategy
class MomentumCrossAsset(Strategy):
    name = "momentum_cross_asset"
    active_regimes = {Regime.BULL_TRENDING, Regime.BEAR_TRENDING}
    description = "Anticipa le altcoin sul momentum di BTC (lag 15-30m)."

    default_params = {"btc_move_threshold": 0.6, "atr_mult_stop": 1.5, "rr": 2.0}
    param_grid = {
        "btc_move_threshold": [0.4, 0.6, 0.8],
        "atr_mult_stop": [1.0, 1.5, 2.0],
        "rr": [1.5, 2.0, 2.5],
    }

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        if asset.symbol == BTC_SYMBOL or ctx is None:
            return None
        btc = ctx.all_assets.get(BTC_SYMBOL)
        if btc is None:
            return None
        btc_i = btc.ind(self._tf)
        alt_i = asset.ind(self._tf)
        if not btc_i or not alt_i:
            return None
        if None in (btc_i.macd_hist, btc_i.atr, btc_i.ema_fast, btc_i.ema_slow):
            return None
        if btc_i.atr == 0:
            return None

        thr = self.p("btc_move_threshold")
        am, rr = self.p("atr_mult_stop"), self.p("rr")
        btc_momo = btc_i.macd_hist / btc_i.atr
        btc_up = btc_i.ema_fast > btc_i.ema_slow

        # altcoin "in ritardo": la sua EMA non ha ancora confermato la direzione di BTC
        alt_up = (alt_i.ema_fast or 0) > (alt_i.ema_slow or 0)

        if btc_up and btc_momo >= thr and not alt_up:
            stop, target = self._atr_stop_target(asset, Direction.LONG, atr_mult_stop=am, rr=rr)
            return self._signal(asset, Direction.LONG, 60,
                                "BTC momentum rialzista forte, altcoin in ritardo", stop, target)
        if (not btc_up) and btc_momo <= -thr and alt_up:
            stop, target = self._atr_stop_target(asset, Direction.SHORT, atr_mult_stop=am, rr=rr)
            return self._signal(asset, Direction.SHORT, 60,
                                "BTC momentum ribassista forte, altcoin in ritardo", stop, target)
        return None
