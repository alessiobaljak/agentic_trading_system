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


class _StrictRtdbFirebase(FirebaseClient):
    """Simula il RTDB VERO: set_rtdb(None) solleva, come Firebase Admin.
    Riproduce il bug per cui la chiusura crashava e il trade non veniva loggato."""

    def set_rtdb(self, path, data):
        if data is None:
            raise ValueError("Value must not be None.")
        super().set_rtdb(path, data)


def test_close_logs_trade_even_if_node_delete_fails():
    # con il Firebase "stretto", chiudere una posizione NON deve sollevare e
    # DEVE restituire il ClosedTrade (così il logger lo registra).
    eng = ExecutionEngine(firebase=_StrictRtdbFirebase(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(stop=98, tp=110))
    closed = eng.update_position("BTCUSDT", 97.0)  # tocca lo stop
    assert closed is not None
    assert closed.exit_reason == ExitReason.STOP_LOSS
    assert "BTCUSDT" not in eng.open_positions


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


def test_take_profit_full_exit():
    # allineato al backtest: al TP esce TUTTA la posizione (niente scale-out/trailing)
    eng = _engine()
    eng.open_position(_asset(100, atr=2.0), "breakout", Direction.LONG, _params(qty=2.0, stop=98, tp=104))
    closed = eng.update_position("BTCUSDT", 104.5)  # supera il TP
    assert closed is not None
    assert closed.exit_reason == ExitReason.TAKE_PROFIT
    assert closed.pnl > 0
    assert "BTCUSDT" not in eng.open_positions
    # esce AL prezzo di target (104), non al mark: (104-100)*2 - costi
    assert closed.exit_price == 104.0


def test_no_exit_between_sl_and_tp():
    eng = _engine()
    eng.open_position(_asset(100, atr=2.0), "breakout", Direction.LONG, _params(qty=2.0, stop=98, tp=104))
    # prezzo tra stop e target -> resta aperta
    assert eng.update_position("BTCUSDT", 101.0) is None
    assert "BTCUSDT" in eng.open_positions


def test_gate_rejected_params_not_opened():
    eng = _engine()
    bad = _params()
    bad.approved = False
    bad.reject_reason = "circuit breaker"
    pos = eng.open_position(_asset(), "x", Direction.LONG, bad)
    assert pos is None
    assert not eng.open_positions


def test_restore_open_positions_after_restart():
    # stesso store Firebase condiviso = simula un riavvio del processo
    fb = FirebaseClient()
    eng1 = ExecutionEngine(firebase=fb, dry_run=True)
    eng1.open_position(_asset(100, atr=2.0), "breakout", Direction.LONG, _params(qty=2.0, stop=98, tp=104))
    # prezzo tra stop e TP: resta aperta, scrive lo stato (per il restore)
    eng1.update_position("BTCUSDT", 101.0)
    src = eng1.open_positions["BTCUSDT"]

    # "riavvio": nuovo engine, open_positions deve ripartire da Firebase
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)
    assert "BTCUSDT" in eng2.open_positions, "posizione orfana dopo il restart!"
    p = eng2.open_positions["BTCUSDT"]
    assert p.position_id == src.position_id
    assert p.entry_price == src.entry_price
    assert p.quantity == src.quantity            # quantità preservata
    assert p.stop_price == src.stop_price and p.take_profit_price == src.take_profit_price
    # la posizione ripristinata si gestisce normalmente (chiude allo stop)
    closed = eng2.update_position("BTCUSDT", 97.0)
    assert closed is not None and closed.exit_reason == ExitReason.STOP_LOSS


def test_breakeven_exit_is_net_negative_due_to_fees():
    # uscita ESATTAMENTE al prezzo d'ingresso: il gross e' 0, ma il PnL netto
    # deve essere < 0 per via di fee+slippage (come sarebbe live), non 0.00.
    eng = _engine()
    a = _asset(100)
    a.volume_24h = 300_000_000     # coin liquida (major) -> spread minimo 0.0002
    eng.open_position(a, "vwap_reversion", Direction.LONG, _params(qty=10.0, stop=98, tp=104))
    closed = eng.force_close_all({"BTCUSDT": 100.0}, ExitReason.KILL_SWITCH)[0]
    assert closed.pnl < 0, "il breakeven deve costare le commissioni"
    # costo = (fee 0.0008 + spread 0.00012 major) * notional (100*10=1000) = 0.92
    assert abs(closed.pnl + 0.92) < 0.05


def test_profit_lock_protects_gains_on_retrace():
    # la posizione va in profitto oltre il trigger (metà strada verso il TP) e poi
    # ritraccia: il profit-lock chiude IN PROFITTO (TRAILING_STOP), non la riporta in
    # perdita né aspetta che torni allo stop iniziale.
    eng = _engine()
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=10.0, stop=98, tp=110))
    # sale a 106: fav_move=6 >= trigger 0.5*10=5 -> armato, stop sale a 100+0.5*6=103
    assert eng.update_position("BTCUSDT", 106.0) is None
    assert eng.open_positions["BTCUSDT"].trailing_active is True
    # ritraccia a 103: tocca lo stop bloccato -> esce in profitto
    closed = eng.update_position("BTCUSDT", 103.0)
    assert closed is not None
    assert closed.exit_reason == ExitReason.TRAILING_STOP
    assert closed.exit_price == 103.0
    assert closed.pnl > 0   # profitto bloccato, al netto dei costi


def test_profit_lock_not_armed_below_trigger():
    # piccolo profitto sotto il trigger: lo stop resta quello iniziale (no arming).
    eng = _engine()
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=10.0, stop=98, tp=110))
    assert eng.update_position("BTCUSDT", 103.0) is None         # fav 3 < trigger 5
    assert eng.open_positions["BTCUSDT"].trailing_active is False
    # ritraccia a 99 (sopra lo stop 98): resta aperta, non c'è ancora protezione
    assert eng.update_position("BTCUSDT", 99.0) is None
    assert "BTCUSDT" in eng.open_positions


def test_open_position_upnl_is_net_of_costs():
    # l'uPnL pubblicato per una posizione APERTA deve gia' scalare fee+spread+funding
    # (quanto incasseresti chiudendo ORA), non il prezzo lordo.
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    a = _asset(100)
    a.volume_24h = 300_000_000  # major -> spread minimo
    eng.open_position(a, "vwap_reversion", Direction.LONG, _params(qty=10.0, stop=98, tp=110))
    eng.update_position("BTCUSDT", 100.0)  # mark == entry: gross 0
    node = fb.get_rtdb("/positions/BTCUSDT")
    # gross 0 ma i costi round-trip rendono l'uPnL negativo (come alla chiusura)
    assert node["unrealized_pnl"] < 0
    assert "accrued_funding" in node and "held_hours" in node


def test_kill_switch_closes_all():
    eng = _engine()
    eng.open_position(_asset(100), "x", Direction.LONG, _params())
    closed = eng.force_close_all({"BTCUSDT": 101.0}, ExitReason.KILL_SWITCH)
    assert len(closed) == 1
    assert closed[0].exit_reason == ExitReason.KILL_SWITCH
    assert not eng.open_positions
