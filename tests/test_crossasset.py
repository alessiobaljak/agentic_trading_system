"""Test dell'iniezione del contesto cross-asset (BTC) nel backtest."""
from datetime import datetime, timedelta, timezone

from backtesting.engine import Backtester
from bot.core.models import Candle
from bot.strategies.base import Strategy


def _candles(n=60, start=100.0):
    out, price, t0 = [], start, datetime(2024, 1, 1, tzinfo=timezone.utc)
    for k in range(n):
        price += 0.5
        out.append(Candle(open_time=t0 + timedelta(hours=k), open=price, high=price + 1,
                          low=price - 1, close=price, volume=1000.0,
                          close_time=t0 + timedelta(hours=k)))
    return out


class _ProbeStrategy(Strategy):
    name = "probe"
    active_regimes = None  # attiva ovunque (is_active_in ritorna True con None regime)

    def __init__(self):
        super().__init__()
        self.saw_btc = False

    def is_active_in(self, regime):
        return True

    def generate_signal(self, asset, ctx=None):
        if ctx and "BTCUSDT" in ctx.all_assets:
            self.saw_btc = True
        return None


def test_backtest_injects_btc_context():
    bt = Backtester(window=5)
    btc = _candles(60, start=200.0)
    alt = _candles(60, start=10.0)
    ctx = bt.build_context("BTCUSDT", btc)
    assert len(ctx) == 60  # una snapshot per barra, per open_time
    probe = _ProbeStrategy()
    bt.run_strategy(probe, "ALTUSDT", alt, context_by_ts=ctx)
    assert probe.saw_btc is True  # il contesto BTC è arrivato alla strategia


def test_momentum_now_optimizable():
    # momentum_cross_asset ora ha una param_grid -> non è più dormiente
    from bot.strategies.momentum_cross_asset import MomentumCrossAsset
    assert MomentumCrossAsset.param_grid
