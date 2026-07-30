"""Parita' sui WICK (ombre): i trigger TP/SL si valutano sul RANGE del tick.

Il GATE valida sulle candele: un livello si riempie se l'OMBRA (high/low) lo tocca,
anche per un istante. Il bot live campiona il prezzo ogni ~30s e da solo non vedrebbe
i movimenti tra due letture. Su Binance REALE gli ordini TP/SL stanno sul book ed e'
l'ombra a eseguirli -> il modello del gate e' quello giusto e il paper si allinea.

Entry 100 / stop 98 -> R=2 -> ladder 103 / 106 / 110 (30/30/40).
"""
from datetime import datetime, timedelta, timezone

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Candle, Direction, EffectiveRiskParams, ExitReason,
    IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine
from bot.main import TradingBot


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


def _open(direction=Direction.LONG, stop=98.0, tp=104.0):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", direction,
                      _params(qty=1.0, stop=stop, tp=tp))
    return eng


# ---- scale-out: le ombre riempiono i TP ----------------------------------- #
def test_wick_high_fills_tp1_even_if_mark_is_below(scale_on):
    """Il mark (101) non arriva a TP1=103, ma l'ombra tocca 103.5: il gate qui
    conterebbe il fill, quindi anche il paper deve contarlo."""
    eng = _open()
    assert eng.update_position("BTCUSDT", 101.0, high=103.5, low=100.5) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scale_stage == 1
    assert pos.scaled_out is True
    assert abs(pos.remaining_qty - 0.7) < 1e-9
    assert abs(pos.stop_price - 100.0) < 1e-9        # break-even sul residuo


def test_wick_low_hits_stop_even_if_mark_is_above(scale_on):
    """Il rovescio della medaglia: l'ombra AVVERSA prende lo stop che il campionamento
    a 30s schivava. La parita' vale in entrambe le direzioni (realismo, non numeri belli)."""
    eng = _open()
    closed = eng.update_position("BTCUSDT", 99.5, high=100.0, low=97.5)
    assert closed is not None
    assert closed.exit_reason == ExitReason.STOP_LOSS
    assert abs(closed.exit_price - 98.0) < 1e-9      # esce ALLO stop, non all'ombra


def test_wick_stop_wins_when_range_touches_both(scale_on):
    """Range che tocca sia TP1 (103.5) sia lo stop (97.5): ordine intra-candela ignoto
    -> si assume il PEGGIO (stop), esattamente come fa il motore del gate."""
    eng = _open()
    closed = eng.update_position("BTCUSDT", 101.0, high=103.5, low=97.5)
    assert closed is not None
    assert closed.exit_reason == ExitReason.STOP_LOSS
    assert closed.pnl < 0


def test_wick_fills_are_idempotent_across_ticks(scale_on):
    """Rileggere la STESSA ombra al tick dopo non riempie due volte lo stesso livello
    (per questo la sovrapposizione delle candele 1m e' innocua)."""
    eng = _open()
    eng.update_position("BTCUSDT", 101.0, high=103.5, low=100.5)
    eng.update_position("BTCUSDT", 101.0, high=103.5, low=100.5)
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scale_stage == 1
    assert abs(pos.remaining_qty - 0.7) < 1e-9


def test_wick_short_direction_fills_on_low(scale_on):
    """Short: entry 100, stop 102 -> R=2 -> ladder 97/94/90. L'ombra BASSA riempie."""
    eng = _open(direction=Direction.SHORT, stop=102.0, tp=96.0)
    assert eng.update_position("BTCUSDT", 98.0, high=98.5, low=96.5) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scale_stage == 1
    assert abs(pos.stop_price - 100.0) < 1e-9


# ---- sicurezza: l'ombra non arma il profit-lock nello stesso tick --------- #
def test_wick_does_not_arm_profit_lock_within_same_tick():
    """CRITICO. Range 99..106 su entry 100 / TP 110: l'ombra alta (106) armerebbe il
    lock a 103 e l'ombra bassa (99) lo farebbe subito scattare -> uscita "in profitto"
    inventata, perche' non sappiamo quale delle due sia venuta prima. Il lock deve
    armarsi solo dal tick SUCCESSIVO (come best_fav a fine barra nel gate)."""
    eng = _open(tp=110.0)
    assert eng.update_position("BTCUSDT", 100.5, high=106.0, low=99.0) is None
    pos = eng.open_positions["BTCUSDT"]
    assert pos.high_water == 106.0        # l'ombra e' registrata per i tick futuri
    # tick successivo: ORA il lock e' armato (0.5*6=3 -> stop a 103) e scatta
    closed = eng.update_position("BTCUSDT", 102.0, high=102.5, low=101.0)
    assert closed is not None
    assert closed.exit_reason == ExitReason.TRAILING_STOP
    assert abs(closed.exit_price - 103.0) < 1e-9


# ---- nessuna regressione: il range non puo' essere piu' stretto del mark -- #
def test_range_is_widened_to_mark_so_no_trigger_is_lost():
    """Se high/low arrivassero stantii/incoerenti, il mark osservato resta sovrano:
    tutto cio' che scattava prima continua a scattare."""
    eng = _open(tp=104.0)
    closed = eng.update_position("BTCUSDT", 104.5, high=101.0, low=100.0)
    assert closed is not None
    assert closed.exit_reason == ExitReason.TAKE_PROFIT


def test_without_hi_lo_behaviour_is_unchanged():
    """Omessi high/low -> vecchio comportamento su solo mark (retrocompatibilita')."""
    eng = _open(tp=104.0)
    assert eng.update_position("BTCUSDT", 103.0) is None      # sotto il TP: niente
    closed = eng.update_position("BTCUSDT", 104.0)
    assert closed is not None
    assert closed.exit_reason == ExitReason.TAKE_PROFIT


# ---- il range viene letto solo DOPO l'ingresso ---------------------------- #
class _StubPrice:
    """Price agent finto: ritorna candele 1m note."""

    def __init__(self, candles):
        self._candles = candles

    def get_candles(self, symbol, interval, limit=200):
        return self._candles[-limit:]


class _FakeBot:
    """Minimo indispensabile per esercitare TradingBot._wick_range senza costruire
    tutto il bot (Firebase, agenti, ...)."""

    def __init__(self, price):
        self.price = price

    _wick_range = TradingBot._wick_range


def _candle(minutes_from_now: int, high: float, low: float) -> Candle:
    t = datetime.now(timezone.utc) + timedelta(minutes=minutes_from_now)
    return Candle(open_time=t, open=(high + low) / 2, high=high, low=low,
                  close=(high + low) / 2, volume=1000.0,
                  close_time=t + timedelta(minutes=1))


def test_wick_range_ignores_candles_opened_before_entry(scale_on):
    """Le candele APERTE PRIMA dell'ingresso non possono riempire i nostri TP:
    sarebbero fill inventati su prezzi che non abbiamo mai tenuto in posizione."""
    eng = _open()
    pos = eng.open_positions["BTCUSDT"]
    pos.entry_time = datetime.now(timezone.utc)
    bot = _FakeBot(_StubPrice([
        _candle(-3, high=999.0, low=1.0),    # PRIMA dell'entry: da ignorare
        _candle(+1, high=104.0, low=99.0),   # dopo l'entry: valida
    ]))
    hi, lo = bot._wick_range("BTCUSDT", pos)
    assert hi == 104.0 and lo == 99.0


def test_wick_range_returns_none_when_disabled(monkeypatch, scale_on):
    eng = _open()
    pos = eng.open_positions["BTCUSDT"]
    monkeypatch.setattr(settings, "EXEC_WICK_FILLS_ENABLED", False)
    bot = _FakeBot(_StubPrice([_candle(+1, high=104.0, low=99.0)]))
    assert bot._wick_range("BTCUSDT", pos) == (None, None)


def test_wick_range_returns_none_when_no_fresh_candles(scale_on):
    """Posizione appena apertissima: nessuna candela post-entry -> si usa il mark."""
    eng = _open()
    pos = eng.open_positions["BTCUSDT"]
    pos.entry_time = datetime.now(timezone.utc)
    bot = _FakeBot(_StubPrice([_candle(-2, high=104.0, low=99.0)]))
    assert bot._wick_range("BTCUSDT", pos) == (None, None)
