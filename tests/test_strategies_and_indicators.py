import numpy as np
import pandas as pd

from bot.core.indicators import atr, bollinger, compute_snapshot, ema, rsi, vwap
from bot.core.models import AssetSnapshot, Candle, IndicatorSnapshot, Regime
from datetime import datetime, timedelta, timezone


def _synthetic_candles(n=120, trend=0.5, start=100.0):
    out = []
    price = start
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    rng = np.random.default_rng(42)
    for k in range(n):
        price += trend + rng.normal(0, 0.5)
        out.append(Candle(
            open_time=t0 + timedelta(minutes=15 * k),
            open=price, high=price + 1, low=price - 1, close=price, volume=1000 + k,
        ))
    return out


def test_indicators_compute():
    candles = _synthetic_candles()
    snap = compute_snapshot(candles, "15m")
    assert snap.ema_fast is not None and snap.ema_slow is not None
    assert 0 <= snap.rsi <= 100
    assert snap.atr is not None and snap.atr > 0
    assert snap.vwap is not None


def test_vwap_is_rolling_not_cumulative():
    # serie fortemente trendata: un VWAP cumulativo resterebbe ancorato all'inizio
    # (lontanissimo dal prezzo). Il rolling deve restare VICINO al prezzo recente.
    n = 500
    df = pd.DataFrame({
        "high": [100 + i for i in range(n)],
        "low": [99 + i for i in range(n)],
        "close": [100 + i for i in range(n)],
        "volume": [1000.0] * n,
    })
    v = vwap(df, window=48).iloc[-1]
    last_price = df["close"].iloc[-1]  # ~599
    # rolling su 48 barre: VWAP entro pochi % dal prezzo; cumulativo darebbe ~350
    assert abs(v - last_price) / last_price < 0.10


def test_adx_and_stochastic_in_frame():
    from bot.core.indicators import compute_indicator_frame
    df = compute_indicator_frame(_synthetic_candles(120, trend=0.5))
    assert "adx" in df.columns and "stoch_k" in df.columns and "stoch_d" in df.columns
    # stocastico è limitato a 0-100
    sk = df["stoch_k"].dropna()
    assert (sk >= -0.01).all() and (sk <= 100.01).all()
    # adx non negativo
    assert (df["adx"].dropna() >= -0.01).all()


def test_rsi_bounds():
    s = pd.Series(np.linspace(100, 200, 100))  # solo salite
    r = rsi(s)
    assert r.iloc[-1] > 70  # forte uptrend -> RSI alto


def test_strategy_registry_has_8():
    from bot.strategies import STRATEGY_REGISTRY, get_all_strategies
    assert len(STRATEGY_REGISTRY) == 8
    names = {s.name for s in get_all_strategies()}
    assert "trend_following" in names and "grid_trading" in names


def test_every_strategy_declares_regimes():
    from bot.strategies import get_all_strategies
    for s in get_all_strategies():
        assert isinstance(s.active_regimes, set)
        assert len(s.active_regimes) >= 1


def test_trend_following_signal_in_uptrend():
    from bot.strategies.trend_following import TrendFollowing
    up15 = IndicatorSnapshot(timeframe="15m", ema_fast=105, ema_slow=100, rsi=60,
                             volume=2000, volume_sma=1000, atr=2.0, close=105)
    up1h = IndicatorSnapshot(timeframe="1h", ema_fast=105, ema_slow=100)
    asset = AssetSnapshot(symbol="ETHUSDT", price=105, regime=Regime.BULL_TRENDING,
                          indicators={"15m": up15, "1h": up1h})
    sig = TrendFollowing().generate_signal(asset)
    assert sig is not None and sig.direction.value == "long"
