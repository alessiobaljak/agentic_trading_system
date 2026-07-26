"""Sentiment tilt (overlay di size al final gate, live-only): solo riduzione."""
from bot.config import settings
from bot.core.models import Direction
from bot.main import TradingBot

f = TradingBot._sentiment_size_factor


def test_neutral_and_aligned_full_size():
    # default: floor 0.5, strength 0.5
    assert f(0.5, Direction.LONG) == 1.0          # neutro
    assert f(1.0, Direction.LONG) == 1.0          # long + bullish (allineato)
    assert f(0.0, Direction.SHORT) == 1.0         # short + bearish (allineato)


def test_contra_reduces_to_floor():
    assert f(0.0, Direction.LONG) == 0.5          # long + molto bearish -> floor
    assert f(1.0, Direction.SHORT) == 0.5         # short + molto bullish -> floor
    assert abs(f(0.25, Direction.LONG) - 0.75) < 1e-9  # riduzione parziale


def test_never_above_one():
    for s in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert f(s, Direction.LONG) <= 1.0
        assert f(s, Direction.SHORT) <= 1.0
        assert f(s, Direction.LONG) >= settings.SENTIMENT_TILT_FLOOR
