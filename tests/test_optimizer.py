"""Test del walk-forward optimizer e dell'integrazione parametri per-asset."""
from datetime import datetime, timezone

from backtesting.data_loader import _synthetic
from backtesting.optimizer import WalkForwardOptimizer, _param_combos
from bot.core.firebase_client import FirebaseClient
from bot.learning.adaptation import AdaptationEngine
from bot.strategies import STRATEGY_REGISTRY
from bot.strategies.breakout import Breakout


def test_param_combos():
    combos = _param_combos({"a": [1, 2], "b": [3, 4, 5]})
    assert len(combos) == 6
    assert {"a": 1, "b": 3} in combos


def test_strategies_accept_params():
    # i parametri sovrascrivono i default
    s = Breakout({"rr": 9.9})
    assert s.p("rr") == 9.9
    assert s.p("compression") == Breakout.default_params["compression"]


def test_optimizable_strategies_have_grid():
    # almeno le strategie chiave espongono una griglia da ottimizzare
    optimizable = [n for n, c in STRATEGY_REGISTRY.items() if getattr(c, "param_grid", {})]
    assert {"breakout", "trend_following", "mean_reversion", "vwap_reversion"} <= set(optimizable)


def test_walkforward_runs_and_validates_oos():
    c = _synthetic(datetime(2023, 1, 1, tzinfo=timezone.utc),
                   datetime(2023, 7, 1, tzinfo=timezone.utc))
    res = WalkForwardOptimizer(n_windows=2).optimize_symbol("BTCUSDT", c)
    assert len(res) >= 4
    for r in res:
        assert isinstance(r.best_params, dict)
        assert isinstance(r.passed, bool)


def test_adaptation_loads_optimized_params(monkeypatch):
    from bot.config import settings as _s
    monkeypatch.setattr(_s, "MIN_COINS_PER_STRATEGY", 1)  # qui non testiamo il filtro robustezza
    fb = FirebaseClient()
    fb.set_doc("strategy_params", "current", {
        "entries": {
            "BTCUSDT|breakout": {"symbol": "BTCUSDT", "strategy": "breakout",
                                 "params": {"rr": 3.0}, "passed": True},
            "ETHUSDT|grid_trading": {"symbol": "ETHUSDT", "strategy": "grid_trading",
                                     "params": {"low_band": 0.2}, "passed": False},
        },
        "passed": ["BTCUSDT|breakout"],
    })
    eng = AdaptationEngine(fb)
    assert eng.params_for("BTCUSDT") == {"breakout": {"rr": 3.0}}
    assert eng.is_enabled("BTCUSDT", "breakout") is True
    # coppia non passata -> disabilitata quando esistono dati di ottimizzazione
    assert eng.is_enabled("ETHUSDT", "grid_trading") is False
    # strategia non ottimizzata su un asset noto -> disabilitata (ci sono dati)
    assert eng.is_enabled("BTCUSDT", "mean_reversion") is False


def test_registry_accumulates_and_gates(monkeypatch):
    from scripts.optimize import update_registry, MIN_PASSES
    from bot.core.firebase_client import FirebaseClient
    from bot.config import settings as _s
    monkeypatch.setattr(_s, "MIN_COINS_PER_STRATEGY", 1)  # qui non testiamo il filtro robustezza
    fb = FirebaseClient()
    out = {
        "SOLUSDT|breakout": {"symbol": "SOLUSDT", "strategy": "breakout",
                             "params": {"rr": 2.5}, "oos_pf": 1.2, "oos_pnl_pct": 0.3, "oos_trades": 100},
        "BTCUSDT|breakout": {"symbol": "BTCUSDT", "strategy": "breakout",
                             "params": {"rr": 3.0}, "oos_pf": 0.9, "oos_pnl_pct": -0.1, "oos_trades": 50},
    }
    reg = {}
    for _ in range(MIN_PASSES):
        reg = update_registry(fb, out, passed_now=["SOLUSDT|breakout"])
    assert "SOLUSDT|breakout" in reg["validated"]
    assert "BTCUSDT|breakout" not in reg["validated"]
    from bot.core.firebase_client import decode_pairs
    assert decode_pairs(reg["pairs"])["SOLUSDT|breakout"]["pass_count"] == MIN_PASSES
    assert reg["coins_covered"] == 1 and reg["ready"] is False

    from bot.learning.adaptation import AdaptationEngine
    eng = AdaptationEngine(fb)
    assert eng.is_enabled("SOLUSDT", "breakout") is True
    assert eng.is_enabled("BTCUSDT", "breakout") is False
    assert eng.params_for("SOLUSDT") == {"breakout": {"rr": 2.5}}
