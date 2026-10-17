"""Test della strategia Momentum (trend-continuation)."""
from bot.core.models import AssetSnapshot, Direction, IndicatorSnapshot, Regime
from bot.strategies.base import STRATEGY_REGISTRY
from bot.strategies.momentum import Momentum


def _asset(adx=30.0, macd_hist=0.5, close=105.0, ema_fast=103.0, ema_slow=100.0,
           volume=200.0, volume_sma=100.0, atr=2.0):
    ind = IndicatorSnapshot(
        timeframe="15m", adx=adx, macd_hist=macd_hist, close=close,
        ema_fast=ema_fast, ema_slow=ema_slow, volume=volume, volume_sma=volume_sma, atr=atr,
    )
    return AssetSnapshot(symbol="BTCUSDT", price=close, regime=Regime.BULL_TRENDING,
                         indicators={"15m": ind})


def test_momentum_registrata():
    assert "momentum" in STRATEGY_REGISTRY


def test_momentum_long_su_trend_forte():
    sig = Momentum().generate_signal(_asset())
    assert sig is not None and sig.direction == Direction.LONG
    # deve portare SL/TP (usati dal fix di parita')
    assert sig.suggested_stop is not None and sig.suggested_target is not None


def test_momentum_short_su_trend_ribassista():
    a = _asset(macd_hist=-0.5, close=95.0, ema_fast=97.0, ema_slow=100.0)
    sig = Momentum().generate_signal(a)
    assert sig is not None and sig.direction == Direction.SHORT


def test_momentum_salta_trend_debole():
    # ADX sotto la soglia -> niente trend forte -> nessun segnale
    assert Momentum().generate_signal(_asset(adx=15.0)) is None


def test_momentum_salta_volume_basso():
    # volume sotto la media -> nessuna conferma -> nessun segnale
    assert Momentum().generate_signal(_asset(volume=90.0, volume_sma=100.0)) is None


def test_momentum_salta_struttura_incoerente():
    # ADX/volume ok ma prezzo NON sopra le EMA allineate -> nessun segnale
    assert Momentum().generate_signal(_asset(close=99.0, ema_fast=103.0, ema_slow=100.0)) is None
