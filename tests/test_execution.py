"""Test del ciclo di vita di una posizione in DRY_RUN: SL, TP/scale-out, trailing."""
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Direction, EffectiveRiskParams, ExitReason, IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine


def _asset(price=100.0, atr=2.0):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _params(qty=1.0, stop=98.0, tp=104.0):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=qty,
        stop_price=stop, take_profit_price=tp,
        user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True,
    )


def _engine():
    return ExecutionEngine(firebase=FirebaseClient(), dry_run=True)


def test_open_and_stop_loss():
    eng = _engine()
    pos = eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(stop=98, tp=110))
    assert pos is not None and "BTCUSDT" in eng.open_positions
    # prezzo scende sotto lo stop -> chiusura in perdita
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed is not None
    assert closed.exit_reason == ExitReason.STOP_LOSS
    assert closed.pnl < 0
    assert "BTCUSDT" not in eng.open_positions


def test_scale_out_then_trailing():
    eng = _engine()
    eng.open_position(_asset(100, atr=2.0), "breakout", Direction.LONG, _params(qty=2.0, stop=98, tp=104))
    # raggiunge il TP -> scale-out 50%, posizione resta aperta
    assert eng.update_position("BTCUSDT", 104.0) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scaled_out is True
    assert pos.remaining_qty == 1.0
    assert pos.trailing_active is True
    # sale ancora (high water), poi ritraccia > 1 ATR -> trailing stop chiude
    eng.update_position("BTCUSDT", 108.0)
    closed = eng.update_position("BTCUSDT", 105.5)  # give back 2.5 > ATR 2.0
    assert closed is not None
    assert closed.exit_reason == ExitReason.TRAILING_STOP
    assert closed.pnl > 0


def test_gate_rejected_params_not_opened():
    eng = _engine()
    bad = _params()
    bad.approved = False
    bad.reject_reason = "circuit breaker"
    pos = eng.open_position(_asset(), "x", Direction.LONG, bad)
    assert pos is None
    assert not eng.open_positions


def test_kill_switch_closes_all():
    eng = _engine()
    eng.open_position(_asset(100), "x", Direction.LONG, _params())
    closed = eng.force_close_all({"BTCUSDT": 101.0}, ExitReason.KILL_SWITCH)
    assert len(closed) == 1
    assert closed[0].exit_reason == ExitReason.KILL_SWITCH
    assert not eng.open_positions
