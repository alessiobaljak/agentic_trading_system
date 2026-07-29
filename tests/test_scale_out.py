"""Scale-out su multipli di R: scala TP (default 30% 1.5R / 30% 3R / 40% 5R) + BE.

Verifica i primitivi condivisi (usati identici da engine e executor per la parita'
GATE 1 <-> paper) e il comportamento live in DRY_RUN. Con entry=100 e stop=98,
R=2 -> livelli 103 / 106 / 110.
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
    # entry 100, stop 98 -> R=2. 1.5R/3R/5R = 103/106/110, quote 0.3/0.3/0.4
    ladder = scale_ladder(100.0, 98.0, True)
    assert [round(p, 6) for p, _ in ladder] == [103.0, 106.0, 110.0]
    assert [f for _, f in ladder] == [0.3, 0.3, 0.4]


def test_scale_ladder_short_and_degenerate():
    ladder = scale_ladder(100.0, 102.0, False)  # short, R=2 -> 97/94/90
    assert [round(p, 6) for p, _ in ladder] == [97.0, 94.0, 90.0]
    assert scale_ladder(100.0, 100.0, True) == []  # R=0 -> vuota


def test_scale_fills_fills_in_order():
    ladder = scale_ladder(100.0, 98.0, True)
    # in una barra che arriva a 106 si riempiono i primi due livelli
    stage, fills = scale_fills(ladder, 0, True, hi=106.0, lo=100.0)
    assert stage == 2
    assert [round(p, 6) for p, _ in fills] == [103.0, 106.0]
    # dal livello 2, a 110 si riempie l'ultimo
    stage, fills = scale_fills(ladder, 2, True, hi=110.0, lo=109.0)
    assert stage == 3 and [round(p, 6) for p, _ in fills] == [110.0]


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
    # TP1 a 103 (1.5R): chiude 30%, sposta lo stop a break-even, resta aperta
    assert eng.update_position("BTCUSDT", 103.0) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scaled_out is True
    assert abs(pos.remaining_qty - 0.7) < 1e-9
    assert abs(pos.stop_price - 100.0) < 1e-9   # break-even = entry


def test_scale_out_reversal_after_tp1_locks_gain(scale_on):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    eng.update_position("BTCUSDT", 103.0)          # TP1 -> 30% via, stop a BE
    closed = eng.update_position("BTCUSDT", 100.0)  # torna a entry -> stop BE sul residuo
    assert closed is not None
    # ha gia' bancato TP1 (scaled_out) -> l'uscita del residuo e' SCALE_OUT, non un
    # trailing/stop protettivo: distingue "residuo dopo >=1 TP" da "stop puro".
    assert closed.exit_reason == ExitReason.SCALE_OUT
    # ho gia' incassato il 30% a +3 -> il trade e' NETTO positivo malgrado il ritorno a entry
    assert closed.pnl > 0
    assert "BTCUSDT" not in eng.open_positions


def test_scale_out_stop_before_tp1_is_full_stop_loss(scale_on):
    # stoppato PRIMA di qualsiasi fetta (nessun TP bancato) -> STOP_LOSS pieno,
    # non SCALE_OUT ne' TRAILING_STOP (perdita piena, edge dello stop reale).
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    closed = eng.update_position("BTCUSDT", 98.0)   # tocca lo stop base a -1R
    assert closed is not None
    assert closed.exit_reason == ExitReason.STOP_LOSS
    assert closed.pnl < 0
    assert "BTCUSDT" not in eng.open_positions


def test_scale_out_full_run_to_final_tp(scale_on):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "breakout", Direction.LONG, _params(qty=1.0, stop=98))
    assert eng.update_position("BTCUSDT", 103.0) is None   # TP1 30% @1.5R
    assert eng.update_position("BTCUSDT", 106.0) is None   # TP2 30% @3R
    closed = eng.update_position("BTCUSDT", 110.0)          # TP3 40% @5R -> chiusura finale
    assert closed is not None
    assert closed.exit_reason == ExitReason.TAKE_PROFIT
    # PnL lordo = 0.3*3 + 0.3*6 + 0.4*10 = 6.7, meno costi -> comunque > 5
    assert closed.pnl > 5.0
    assert "BTCUSDT" not in eng.open_positions


def test_scale_out_equity_realized_incrementally(scale_on):
    """Ogni fetta (TP parziale) accredita subito il netto all'equity, e la somma
    di TUTTI gli eventi == PnL del trade loggato (nessun doppio conteggio)."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "breakout", Direction.LONG, _params(qty=1.0, stop=98))
    # gli eventi si accumulano (in produzione TradingBot li svuota con pop_realized)
    eng.update_position("BTCUSDT", 103.0)   # TP1 -> evento parziale
    pos = eng.open_positions["BTCUSDT"]
    assert pos.realized_net > 0             # incassato subito
    assert len(eng.realized_events) == 1    # un evento accodato al TP1
    eng.update_position("BTCUSDT", 106.0)   # TP2 -> secondo evento
    closed = eng.update_position("BTCUSDT", 110.0)  # TP3 -> chiusura + evento residuo
    assert len(eng.realized_events) == 3
    # somma di tutti i realizzi == PnL loggato (coerenza equity <-> trade, no doppi conteggi)
    assert abs(sum(eng.realized_events) - closed.pnl) < 1e-6


def test_scale_out_disabled_keeps_single_tp(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "breakout", Direction.LONG, _params(qty=1.0, stop=98, tp=104))
    # con scale-out OFF, a 103 (sotto il TP unico 104) NON deve chiudere nulla
    assert eng.update_position("BTCUSDT", 103.0) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scaled_out is False
    assert abs(pos.remaining_qty - 1.0) < 1e-9
