"""Smoke test del backtester (GATE 1) su dati sintetici piccoli."""
from datetime import datetime, timezone

from backtesting.data_loader import _synthetic
from backtesting.engine import Backtester, passes_gate
from bot.config import settings


def test_gate_requires_pf_winrate_consistency_and_return():
    # coppia "buona": abbastanza trade, PF e win-rate alti, ritorno ampio,
    # ogni finestra positiva -> passa.
    good = dict(window_pnls=[0.10, 0.08, 0.12], n_trades=30, pf=1.4,
                win_rate=0.55, total_return=0.30)
    assert passes_gate(**good) is True
    # pochi trade -> bocciata
    assert passes_gate(**{**good, "n_trades": settings.GATE_MIN_TRADES - 1}) is False
    # PF sotto soglia -> bocciata
    assert passes_gate(**{**good, "pf": settings.GATE_PF_THRESHOLD - 0.01}) is False
    # win-rate sotto il floor -> bocciata
    assert passes_gate(**{**good, "win_rate": settings.GATE_WIN_RATE_FLOOR - 0.01}) is False
    # ritorno totale troppo piccolo -> bocciata ("profittevole, e di tanto")
    assert passes_gate(**{**good, "total_return": settings.GATE_MIN_TOTAL_RETURN - 0.01}) is False
    # una finestra in perdita (in perdita un anno, recupero il dopo) -> bocciata
    assert passes_gate(**{**good, "window_pnls": [0.30, -0.05, 0.05]}) is False


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
