"""RISCHIO DI PORTAFOGLIO — i due buchi trovati dall'audit del 04/08.

1) CORRELATION GUARD: il modulo esisteva, era documentato (max 3 posizioni
   correlate, soglia 0.85) ma NON era importato da nessun file. Il bot poteva
   aprire 5 posizioni perfettamente correlate credendo di essere diversificato:
   una sola scommessa con size 5x.
2) ESPOSIZIONE DIREZIONALE: il cap sul NUMERO di posizioni non protegge. Cinque
   long correlati rischiano quanto un unico trade con size 5x. Serve sommare il
   rischio VERO (distanza dallo stop x quantita').

Entrambi FAIL-OPEN: senza dati non bloccano nulla.
"""
import types

import pytest

from bot.config import settings
from bot.core.models import Direction
from bot.main import TradingBot
from bot.risk.correlation_guard import CorrelationGuard


# ---- il guard puro --------------------------------------------------------- #
def test_guard_blocks_a_cluster_of_correlated_positions():
    g = CorrelationGuard(threshold=0.85, max_correlated=3)
    up = [100.0, 101, 102, 103, 104, 105]          # tutte salgono insieme
    ok, reason = g.can_open("NEW", up, {"A": up, "B": up, "C": up})
    assert ok is False and "correlate" in reason


def test_guard_allows_genuinely_different_assets():
    g = CorrelationGuard(threshold=0.85, max_correlated=3)
    up = [100.0, 101, 102, 103, 104, 105]
    down = [100.0, 99, 98, 97, 96, 95]
    zig = [100.0, 103, 99, 104, 98, 105]
    ok, _ = g.can_open("NEW", up, {"A": down, "B": zig})
    assert ok is True


def test_guard_needs_at_least_three_points():
    g = CorrelationGuard()
    assert g.correlation([100.0, 101], [100.0, 101]) == 0.0


def test_guard_handles_a_flat_series_without_dividing_by_zero():
    g = CorrelationGuard()
    assert g.correlation([100.0] * 6, [100.0, 101, 102, 103, 104, 105]) == 0.0


# ---- innesto nel bot ------------------------------------------------------- #
class _Pos:
    def __init__(self, direction, entry, stop, qty):
        self.direction = direction
        self.entry_price = entry
        self.orig_stop = stop
        self.stop_price = stop
        self.remaining_qty = qty


def _bot(open_positions=None, series=None, equity=1000.0):
    """TradingBot minimo: solo cio' che i due controlli toccano."""
    b = types.SimpleNamespace()
    b.executor = types.SimpleNamespace(open_positions=open_positions or {})
    b.corr_guard = CorrelationGuard()
    b._price_cache = {}
    b.account_equity = lambda: equity
    b._price_series = lambda sym, max_age_s=1800.0: (series or {}).get(sym, [])
    b._correlation_blocks = types.MethodType(TradingBot._correlation_blocks, b)
    b._directional_risk_blocks = types.MethodType(TradingBot._directional_risk_blocks, b)
    return b


def test_correlation_blocks_the_fifth_clone(monkeypatch):
    """Lo scenario reale: 3 posizioni che si muovono insieme, ne arriva una quarta
    identica. Prima passava perche' il guard non era collegato."""
    monkeypatch.setattr(settings, "CORRELATION_GUARD_ENABLED", True)
    up = [100.0, 101, 102, 103, 104, 105]
    series = {s: up for s in ("NEW", "A", "B", "C")}
    b = _bot({s: _Pos(Direction.LONG, 100, 98, 1) for s in ("A", "B", "C")}, series)
    assert b._correlation_blocks("NEW") is not None


def test_correlation_fails_open_without_history(monkeypatch):
    """Senza storico prezzi NON si blocca: un dato mancante non deve fermare il bot."""
    monkeypatch.setattr(settings, "CORRELATION_GUARD_ENABLED", True)
    b = _bot({"A": _Pos(Direction.LONG, 100, 98, 1)}, series={})
    assert b._correlation_blocks("NEW") is None


def test_correlation_skipped_with_no_open_positions(monkeypatch):
    monkeypatch.setattr(settings, "CORRELATION_GUARD_ENABLED", True)
    assert _bot({}, {"NEW": [100.0, 101, 102]})._correlation_blocks("NEW") is None


def test_correlation_disabled_by_flag(monkeypatch):
    monkeypatch.setattr(settings, "CORRELATION_GUARD_ENABLED", False)
    up = [100.0, 101, 102, 103, 104, 105]
    b = _bot({s: _Pos(Direction.LONG, 100, 98, 1) for s in ("A", "B", "C")},
             {s: up for s in ("NEW", "A", "B", "C")})
    assert b._correlation_blocks("NEW") is None


# ---- esposizione direzionale ---------------------------------------------- #
def test_directional_cap_blocks_piling_up_the_same_side(monkeypatch):
    """Tre long che rischiano l'1% ciascuno = 3%: il quarto sfora il tetto."""
    monkeypatch.setattr(settings, "MAX_DIRECTIONAL_RISK_PCT", 0.03)
    pos = {s: _Pos(Direction.LONG, 100.0, 99.0, 10.0) for s in ("A", "B", "C")}  # 10$ = 1%
    b = _bot(pos, equity=1000.0)
    assert b._directional_risk_blocks(Direction.LONG, 10.0) is not None


def test_directional_cap_ignores_the_opposite_side(monkeypatch):
    """Uno short non consuma il budget dei long: sono rischi che si compensano."""
    monkeypatch.setattr(settings, "MAX_DIRECTIONAL_RISK_PCT", 0.03)
    pos = {s: _Pos(Direction.SHORT, 100.0, 101.0, 10.0) for s in ("A", "B", "C")}
    b = _bot(pos, equity=1000.0)
    assert b._directional_risk_blocks(Direction.LONG, 10.0) is None


def test_directional_cap_allows_within_budget(monkeypatch):
    monkeypatch.setattr(settings, "MAX_DIRECTIONAL_RISK_PCT", 0.03)
    pos = {"A": _Pos(Direction.LONG, 100.0, 99.0, 10.0)}
    assert _bot(pos, equity=1000.0)._directional_risk_blocks(Direction.LONG, 10.0) is None


def test_directional_cap_disabled_with_zero(monkeypatch):
    monkeypatch.setattr(settings, "MAX_DIRECTIONAL_RISK_PCT", 0.0)
    pos = {s: _Pos(Direction.LONG, 100.0, 99.0, 100.0) for s in ("A", "B", "C")}
    assert _bot(pos, equity=1000.0)._directional_risk_blocks(Direction.LONG, 100.0) is None


def test_directional_cap_uses_ORIGINAL_stop(monkeypatch):
    """Dopo un TP parziale lo stop va a break-even: usando quello, il rischio
    sembrerebbe ZERO e il tetto non proteggerebbe piu'. Si usa orig_stop."""
    monkeypatch.setattr(settings, "MAX_DIRECTIONAL_RISK_PCT", 0.03)
    p = _Pos(Direction.LONG, 100.0, 99.0, 10.0)
    p.stop_price = 100.0                      # spostato a break-even
    pos = {s: p for s in ("A", "B", "C")}
    b = _bot(pos, equity=1000.0)
    assert b._directional_risk_blocks(Direction.LONG, 10.0) is not None
