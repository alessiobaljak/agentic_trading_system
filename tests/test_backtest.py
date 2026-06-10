"""Smoke test del backtester (GATE 1) su dati sintetici piccoli."""
from datetime import datetime, timezone

from backtesting.data_loader import _synthetic
from backtesting.engine import Backtester


def test_backtester_runs_and_segments():
    candles = _synthetic(datetime(2023, 1, 1, tzinfo=timezone.utc),
                         datetime(2023, 2, 1, tzinfo=timezone.utc))
    bt = Backtester(window=50)
    stats = bt.run("BTCUSDT", candles)
    assert len(stats) == 8                      # tutte le 8 strategie testate
    # almeno una strategia genera trade su una serie con trend
    assert any(len(s.trades) > 0 for s in stats.values())
    # il learning loop produce pesi dai trade simulati
    weights = bt.validate_learning(stats)
    assert isinstance(weights, list)
    verdict = bt.verdict(stats)
    assert "passed" in verdict


def test_liquidation_counts_increase_with_leverage():
    candles = _synthetic(datetime(2023, 1, 1, tzinfo=timezone.utc),
                         datetime(2023, 3, 1, tzinfo=timezone.utc))
    bt = Backtester(window=50)
    stats = bt.run("BTCUSDT", candles)
    for s in stats.values():
        if len(s.trades) < 5:
            continue
        liq = s.liquidations_at_leverage()
        # più leva => almeno tante liquidazioni quante con meno leva
        assert liq[20] >= liq[2]
