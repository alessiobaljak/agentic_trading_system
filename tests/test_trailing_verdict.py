"""Test del verdetto controfattuale sul trailing (Backtester._trailing_verdict)."""
from collections import namedtuple

from backtesting.engine import Backtester

C = namedtuple("C", ["high", "low"])


def test_premature_se_il_TP_arriva_prima():
    # dopo l'uscita trailing, il prezzo raggiunge il TP (110) prima dello stop (97)
    candles = [C(100, 99), C(111, 100)]
    assert Backtester._trailing_verdict(candles, 0, 1, stop=97, target=110, long=True) == "premature"


def test_protected_se_lo_stop_arriva_prima():
    # il prezzo tocca lo stop base (97) prima del TP -> il trailing ha protetto
    candles = [C(100, 99), C(101, 96)]
    assert Backtester._trailing_verdict(candles, 0, 1, stop=97, target=110, long=True) == "protected"


def test_neutral_se_nessuno_dei_due():
    candles = [C(100, 99), C(105, 98)]
    assert Backtester._trailing_verdict(candles, 0, 1, stop=97, target=110, long=True) == "neutral"


def test_short_specchiato():
    # short: TP sotto (90), stop base sopra (103). Prezzo tocca il TP prima.
    candles = [C(100, 99), C(100, 89)]
    assert Backtester._trailing_verdict(candles, 0, 1, stop=103, target=90, long=False) == "premature"
