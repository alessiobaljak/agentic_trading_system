"""PERCHE' IL MOTORE E' USCITO (1 ott 2026, la cattura dei dati mancanti).

`SimTrade.exit_reason` etichetta ogni trade simulato del gate: stop prima del
TP1, trailing (lock), pareggio dopo il TP1, stop dopo il TP1 senza pareggio, tp,
orizzonte, fine dei dati. Solo un'etichetta: che i numeri non cambino lo prova
`test_dati_parita.py` con i valori di prima della modifica.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backtesting.engine import Backtester
from bot.config import settings
from bot.core.models import Candle, Direction, StrategySignal

T0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
FINESTRA = 50


class _UnSegnale:
    """Una strategia finta: un solo long alla prima barra utile, stop 98, target 110."""
    name = "finta"
    params = None

    def __init__(self):
        self.fatto = False

    def is_active_in(self, regime):
        return True

    def generate_signal(self, snap, ctx):
        if self.fatto:
            return None
        self.fatto = True
        return StrategySignal(strategy=self.name, symbol=snap.symbol, direction=Direction.LONG,
                              confidence=60.0, suggested_stop=98.0, suggested_target=110.0)


def _candele(percorso):
    """FINESTRA candele piatte a 100, poi il percorso [(high, low, close)]."""
    out = [Candle(open_time=T0 + timedelta(hours=k), open=100.0, high=100.05, low=99.95,
                  close=100.0, volume=1000.0) for k in range(FINESTRA + 1)]
    for k, (hi, lo, cl) in enumerate(percorso, start=FINESTRA + 1):
        out.append(Candle(open_time=T0 + timedelta(hours=k), open=out[-1].close, high=hi, low=lo,
                          close=cl, volume=1000.0))
    return out


@pytest.fixture
def motore(monkeypatch):
    monkeypatch.setattr(settings, "BACKTEST_ENTRY_NEXT_OPEN", False)
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_FRACTIONS", (0.3, 0.3, 0.4))
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", False)
    monkeypatch.setattr(settings, "COOLDOWN_HOURS", 0)

    def gira(percorso):
        bt = Backtester(window=FINESTRA)
        tr = bt.run_strategy(_UnSegnale(), "BTCUSDT", _candele(percorso)).trades
        assert len(tr) == 1
        return tr[0]
    return gira


def test_stop_prima_del_tp1(motore):
    assert motore([(100.5, 97.5, 98.0)] + [(100.1, 99.9, 100.0)] * 3).exit_reason == "stop"


def test_pareggio_dopo_il_tp1(motore):
    t = motore([(103.2, 99.5, 102.0), (101.0, 99.8, 100.0)] + [(100.1, 99.9, 100.0)] * 3)
    assert t.exit_reason == "breakeven"


def test_stop_dopo_il_tp1_senza_pareggio(motore, monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", False)
    t = motore([(103.2, 99.5, 102.0), (101.0, 97.5, 98.0)] + [(100.1, 99.9, 100.0)] * 3)
    assert t.exit_reason == "stop_dopo_tp1"


def test_tutta_la_scala(motore):
    assert motore([(103.2, 99.5, 103.0), (106.5, 102.0, 106.0), (111.0, 105.0, 110.5),
                   (100.1, 99.9, 100.0)]).exit_reason == "tp"


def test_trailing_col_lock(motore, monkeypatch):
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_TRIGGER", 0.5)
    # +1,0 (oltre meta' strada verso il TP1 a 103 -> lock armato), poi giu'
    t = motore([(102.5, 100.0, 102.0), (102.0, 99.0, 99.5)] + [(100.1, 99.9, 100.0)] * 3)
    assert t.exit_reason == "trailing" and t.trailing_verdict is not None


def test_fine_dati_e_orizzonte(motore, monkeypatch):
    assert motore([(100.5, 99.5, 100.0)] * 5).exit_reason == "fine_dati"
    import backtesting.engine as eng
    monkeypatch.setattr(eng, "HORIZON_BARS", 3)
    assert motore([(100.5, 99.5, 100.0)] * 6).exit_reason == "orizzonte"


def test_percorso_classico(motore, monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    assert motore([(111.0, 99.5, 110.0), (100.1, 99.9, 100.0)]).exit_reason == "tp"
    assert motore([(100.5, 97.0, 98.0), (100.1, 99.9, 100.0)]).exit_reason == "stop"
