"""Test dell'adattamento real-time: una strategia in panchina viene saltata."""
from bot.core.models import AssetSnapshot, IndicatorSnapshot, Regime
from bot.orchestrator.orchestrator import Orchestrator


def _asset():
    # condizioni che fanno scattare mean_reversion LONG: prezzo sotto BB inf, RSI oversold
    ind = IndicatorSnapshot(timeframe="15m", rsi=20.0, atr=2.0, close=94.0,
                            bb_lower=95.0, bb_upper=105.0, bb_mid=100.0)
    return AssetSnapshot(symbol="BTCUSDT", price=94.0, regime=Regime.SIDEWAYS,
                         indicators={"15m": ind})


def test_disabled_strategy_is_skipped():
    o = Orchestrator()
    assets = {"BTCUSDT": _asset()}
    names = {s["strategy"] for s in o.collect_signals(assets, Regime.SIDEWAYS)}
    assert "mean_reversion" in names  # normalmente scatta
    names2 = {s["strategy"] for s in o.collect_signals(assets, Regime.SIDEWAYS, disabled={"mean_reversion"})}
    assert "mean_reversion" not in names2  # in panchina -> saltata
