"""Test del verdetto controfattuale sul trailing (Backtester._trailing_verdict)."""
from collections import namedtuple

from backtesting.engine import Backtester
from bot.execution.exit_logic import trailing_reason

C = namedtuple("C", ["high", "low"])
FullC = namedtuple("FullC", ["high", "low", "close"])


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


def test_trailing_reason_premature_da_rumore():
    # long entry=100 TP=110 stop=95. Durante il trade il prezzo sale a 106 (max),
    # poi un ritracciamento piccolo (~ATR) ci butta fuori a 104; DOPO tocca il TP.
    during = [FullC(101, 100, 100), FullC(103, 101, 102), FullC(106, 103, 104)]
    after = [FullC(108, 104, 106), FullC(111, 107, 110)]
    res = trailing_reason(during, after, entry=100, exit_price=104,
                          stop=95, target=110, long=True)
    assert res["verdict"] == "premature"
    # uscito a 104 su un tragitto 100->110: lasciato sul tavolo 6/10 = 0.6
    assert abs(res["miss_to_tp"] - 0.6) < 1e-6
    # ritracciamento 106->104 = 2, piccolo rispetto all'ATR -> segnale di rumore
    assert res["knockout_atr"] is not None and res["knockout_atr"] < 2.0
