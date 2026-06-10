"""
Test del cuore della sicurezza: logica di precedenza, hard cap non bypassabili,
circuit breaker. Questi test sono un GATE: se falliscono, il sistema non è sicuro.
"""
import time

import pytest

from bot.core.models import (
    AssetSnapshot, Direction, IndicatorSnapshot, OrchestratorDecision, Regime, RiskSettings,
)
from bot.risk import hard_limits
from bot.risk.circuit_breakers import CircuitBreakers
from bot.risk.correlation_guard import CorrelationGuard
from bot.risk.risk_manager import RiskManager


def _asset(price=100.0, atr=2.0):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _decision(size_mult=1.0):
    return OrchestratorDecision(
        asset="BTCUSDT", strategy="trend_following", direction=Direction.LONG,
        size_multiplier=size_mult, confidence=80,
    )


def test_hardcap_leverage_cannot_be_exceeded():
    """L'utente chiede 10x -> il sistema limita a 5x. Mai oltre l'hard cap."""
    rm = RiskManager()
    user = RiskSettings(leverage=10.0, risk_per_trade=0.02)
    params = rm.evaluate(_decision(), user, _asset(), account_equity=10_000)
    assert params.leverage <= hard_limits.MAX_LEVERAGE == 5.0
    assert params.leverage == 5.0


def test_hardcap_risk_cannot_be_exceeded():
    """L'utente chiede 8% di rischio -> limitato al 3% hard cap."""
    rm = RiskManager()
    user = RiskSettings(leverage=3.0, risk_per_trade=0.08)
    params = rm.evaluate(_decision(), user, _asset(), account_equity=10_000)
    assert params.risk_per_trade <= hard_limits.MAX_RISK_PER_TRADE == 0.03


def test_precedence_takes_most_conservative():
    """effective = min(user, system_safety, hard_cap). Alta volatilità riduce la leva."""
    rm = RiskManager()
    user = RiskSettings(leverage=5.0, risk_per_trade=0.03)
    # volatilità 3 sigma -> safety cap leva = 2x, risk dimezzato
    params = rm.evaluate(_decision(), user, _asset(), account_equity=10_000, volatility_sigma=3.5)
    assert params.leverage == 2.0           # min(5, 2, 5)
    assert params.risk_per_trade <= 0.015    # dimezzato dal safety cap


def test_user_value_used_when_below_caps():
    rm = RiskManager()
    user = RiskSettings(leverage=2.0, risk_per_trade=0.01)
    params = rm.evaluate(_decision(), user, _asset(), account_equity=10_000)
    assert params.leverage == 2.0
    assert abs(params.risk_per_trade - 0.01) < 1e-9


def test_size_multiplier_scales_risk():
    rm = RiskManager()
    user = RiskSettings(leverage=3.0, risk_per_trade=0.02)
    full = rm.evaluate(_decision(1.0), user, _asset(), 10_000)
    half = rm.evaluate(_decision(0.5), user, _asset(), 10_000)
    assert half.quantity == pytest.approx(full.quantity / 2, rel=1e-6)


def test_circuit_breaker_daily_loss_halts():
    cb = CircuitBreakers()
    cb.register_trade_result(pnl_pct=-0.06, was_stop_loss=True)  # -6% > 5% limite
    rm = RiskManager(circuit_breakers=cb)
    params = rm.evaluate(_decision(), RiskSettings(), _asset(), 10_000)
    assert params.approved is False
    assert "circuit_breaker" in (params.reject_reason or "")


def test_circuit_breaker_consecutive_sl_pause():
    cb = CircuitBreakers()
    for _ in range(3):
        cb.register_trade_result(pnl_pct=-0.005, was_stop_loss=True)
    assert cb.can_trade() is False
    assert "consecut" in cb.blocking_reason().lower() or "SL" in cb.blocking_reason()


def test_final_gate_reclamps_defensively():
    """Anche se qualcuno costruisse params oltre i cap, il final_gate li ri-clampa."""
    rm = RiskManager()
    from bot.core.models import EffectiveRiskParams
    bad = EffectiveRiskParams(
        leverage=20.0, risk_per_trade=0.10, notional=1000, quantity=10,
        stop_price=98, take_profit_price=104,
        user_leverage=20, user_risk_per_trade=0.10,
        safety_leverage_cap=5, safety_risk_cap=0.03,
    )
    out = rm.final_gate(bad)
    assert out.leverage == hard_limits.MAX_LEVERAGE
    assert out.risk_per_trade == hard_limits.MAX_RISK_PER_TRADE


def test_correlation_guard_blocks_excess_correlated():
    guard = CorrelationGuard(threshold=0.85, max_correlated=3)
    base = [100, 101, 102, 103, 104, 105]
    open_pos = {f"A{i}": base for i in range(3)}  # 3 già correlate
    ok, reason = guard.can_open("CANDIDATE", base, open_pos)
    assert ok is False
