"""Scale-out su multipli di R: scala TP (50/30/20 a 1R/2R/3R) + break-even dopo TP1.

Verifica i primitivi condivisi (usati identici da engine e executor per la parita'
GATE 1 <-> paper) e il comportamento live in DRY_RUN.
"""
import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Direction, EffectiveRiskParams, ExitReason, IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine
from bot.execution.exit_logic import scale_ladder, scale_fills


# ---- primitivi condivisi -------------------------------------------------- #
def test_scale_ladder_long_r_multiples():
    # entry 100, stop 98 -> R=2. 1R/2R/3R = 102/104/106, quote 0.5/0.3/0.2
    ladder = scale_ladder(100.0, 98.0, True)
    assert [round(p, 6) for p, _ in ladder] == [102.0, 104.0, 106.0]
    assert [f for _, f in ladder] == [0.5, 0.3, 0.2]


def test_scale_ladder_short_and_degenerate():
    ladder = scale_ladder(100.0, 102.0, False)  # short, R=2 -> 98/96/94
    assert [round(p, 6) for p, _ in ladder] == [98.0, 96.0, 94.0]
    assert scale_ladder(100.0, 100.0, True) == []  # R=0 -> vuota


def test_scale_fills_fills_in_order():
    ladder = scale_ladder(100.0, 98.0, True)
    # in una barra che arriva a 104 si riempiono i primi due livelli
    stage, fills = scale_fills(ladder, 0, True, hi=104.0, lo=100.0)
    assert stage == 2
    assert [round(p, 6) for p, _ in fills] == [102.0, 104.0]
    # dal livello 2, a 106 si riempie l'ultimo
    stage, fills = scale_fills(ladder, 2, True, hi=106.0, lo=105.0)
    assert stage == 3 and [round(p, 6) for p, _ in fills] == [106.0]


# ---- executor live (DRY_RUN) ---------------------------------------------- #
def _asset(price=100.0, atr=2.0):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING, volume_24h=5e8,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _params(qty=1.0, stop=98.0, tp=104.0):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=qty,
        stop_price=stop, take_profit_price=tp,
        user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True,
    )


@pytest.fixture
def scale_on(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)


def test_scale_out_partial_then_breakeven(scale_on):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    # TP1 a 102: chiude 50%, sposta lo stop a break-even, resta aperta
    assert eng.update_position("BTCUSDT", 102.0) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scaled_out is True
    assert abs(pos.remaining_qty - 0.5) < 1e-9
    assert abs(pos.stop_price - 100.0) < 1e-9   # break-even = entry


def test_scale_out_reversal_after_tp1_locks_gain(scale_on):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    eng.update_position("BTCUSDT", 102.0)          # TP1 -> 50% via, stop a BE
    closed = eng.update_position("BTCUSDT", 100.0)  # torna a entry -> stop BE sul residuo
    assert closed is not None
    assert closed.exit_reason == ExitReason.TRAILING_STOP
    # ho gia' incassato il 50% a +2 -> il trade e' NETTO positivo malgrado il ritorno a entry
    assert closed.pnl > 0
    assert "BTCUSDT" not in eng.open_positions


def test_scale_out_full_run_to_final_tp(scale_on):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "breakout", Direction.LONG, _params(qty=1.0, stop=98))
    assert eng.update_position("BTCUSDT", 102.0) is None   # TP1 50%
    assert eng.update_position("BTCUSDT", 104.0) is None   # TP2 30%
    closed = eng.update_position("BTCUSDT", 106.0)          # TP3 20% -> chiusura finale
    assert closed is not None
    assert closed.exit_reason == ExitReason.TAKE_PROFIT
    # PnL lordo = 0.5*2 + 0.3*4 + 0.2*6 = 3.4, meno costi -> comunque > 3
    assert closed.pnl > 3.0
    assert "BTCUSDT" not in eng.open_positions


def test_scale_out_disabled_keeps_single_tp(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "breakout", Direction.LONG, _params(qty=1.0, stop=98, tp=104))
    # con scale-out OFF, a 102 (sotto il TP unico 104) NON deve chiudere nulla
    assert eng.update_position("BTCUSDT", 102.0) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scaled_out is False
    assert abs(pos.remaining_qty - 1.0) < 1e-9
