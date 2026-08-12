"""COSTI SCOMPOSTI — il PnL netto e' un numero solo e nasconde il conto.

Due sistemi con lo stesso risultato possono avere costi molto diversi, e quello
coi costi alti e' molto piu' fragile: basta un edge leggermente peggiore e va
sotto. Separare commissioni, spread e funding permette di rispondere a due
domande che il PnL da solo non consente:

  * quanto deve rendere il sistema SOLO per coprire cio' che spende;
  * quali coin costano di piu' da tradare.

In DRY_RUN sono STIME dallo stesso modello del gate, non misure dai fill: il
campo `costs_are_estimated` lo dichiara, cosi' nessuno legge una stima come una
misura quando si passera' ai soldi veri.
"""
import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Direction, EffectiveRiskParams, ExitReason, IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine
from bot.learning.metrics import cost_alerts, cost_report


def _asset(price=100.0, vol=3e8):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.SIDEWAYS, volume_24h=vol,
        indicators={settings.ORCHESTRATOR_TIMEFRAME: IndicatorSnapshot(
            timeframe=settings.ORCHESTRATOR_TIMEFRAME, atr=2.0, close=price)})


def _params(qty=10.0, stop=98.0, tp=110.0):
    return EffectiveRiskParams(
        leverage=2.0, risk_per_trade=0.01, notional=qty * 100, quantity=qty,
        stop_price=stop, take_profit_price=tp, user_leverage=2, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True)


# ---- scomposizione sul trade chiuso ---------------------------------------- #
def _closed():
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(), "s", Direction.LONG, _params())
    return eng.force_close_all({"BTCUSDT": 105.0}, ExitReason.MANUAL)[0]


def test_the_three_cost_lines_add_up_to_the_total():
    t = _closed()
    assert t.total_cost_usdt == pytest.approx(
        t.commission_usdt + t.spread_usdt + t.funding_paid_usdt, abs=1e-6)


def test_gross_minus_costs_equals_the_net_pnl():
    """Se questa identita' si rompe, la scomposizione racconta una storia diversa
    dal numero che finisce in equity."""
    t = _closed()
    assert t.pnl == pytest.approx(t.gross_pnl_usdt - t.total_cost_usdt, abs=1e-6)


def test_gross_pnl_ignores_costs():
    t = _closed()      # long 10 @ 100 -> 105 = +50 lordi
    assert t.gross_pnl_usdt == pytest.approx(50.0)
    assert t.pnl < t.gross_pnl_usdt


def test_costs_are_flagged_as_estimated_in_dry_run():
    """In paper i costi vengono dal modello, non dai fill: dirlo evita che una
    stima venga scambiata per una misura quando si passera' ai soldi veri."""
    assert _closed().costs_are_estimated is True


def test_a_thin_coin_costs_more_than_a_liquid_one():
    """Lo spread viene dalla fascia di liquidita': una microcap deve costare di
    piu' della stessa operazione su una major."""
    def spread_for(vol):
        eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
        eng.open_position(_asset(vol=vol), "s", Direction.LONG, _params())
        return eng.force_close_all({"BTCUSDT": 105.0}, ExitReason.MANUAL)[0].spread_usdt
    assert spread_for(2e6) > spread_for(5e8)


# ---- report aggregato ------------------------------------------------------ #
def _t(**kw):
    d = {"symbol": "AUSDT", "commission_usdt": 1.0, "spread_usdt": 0.5,
         "funding_paid_usdt": 0.2, "total_cost_usdt": 1.7,
         "gross_pnl_usdt": 3.0, "pnl": 1.3, "costs_are_estimated": True}
    d.update(kw)
    return d


def test_report_sums_the_lines_and_computes_break_even():
    r = cost_report([_t(), _t()], equity=1000.0)
    assert r["trades"] == 2
    assert r["total_cost_usdt"] == pytest.approx(3.4)
    assert r["cost_per_trade_usdt"] == pytest.approx(1.7)
    assert r["break_even_pct"] == pytest.approx(0.34)


def test_report_shows_which_coins_cost_most():
    r = cost_report([_t(symbol="AUSDT", total_cost_usdt=5.0),
                     _t(symbol="BUSDT", total_cost_usdt=1.0)], equity=1000.0)
    assert list(r["cost_by_symbol"])[0] == "AUSDT"


def test_report_is_empty_without_cost_data():
    """I trade vecchi non hanno i campi: il report deve tacere, non inventare zeri
    che sembrerebbero "costi nulli"."""
    assert cost_report([{"pnl": 1.0}], equity=1000.0) == {}


def test_alert_when_break_even_is_too_high(monkeypatch):
    monkeypatch.setattr(settings, "COST_ALERT_BREAKEVEN_PCT", 1.5)
    r = cost_report([_t(total_cost_usdt=20.0) for _ in range(2)], equity=1000.0)
    assert any("Costi operativi elevati" in a for a in cost_alerts(r))


def test_alert_when_costs_eat_a_positive_gross():
    """Il caso piu' insidioso: il mercato ti ha dato ragione e il conto resta
    negativo. Senza la scomposizione sembrerebbe una strategia che non funziona."""
    r = cost_report([_t(gross_pnl_usdt=2.0, total_cost_usdt=3.0, pnl=-1.0)],
                    equity=1000.0)
    assert any("mangiano i costi" in a for a in cost_alerts(r))


def test_no_alerts_when_costs_are_reasonable(monkeypatch):
    monkeypatch.setattr(settings, "COST_ALERT_BREAKEVEN_PCT", 1.5)
    assert cost_alerts(cost_report([_t()], equity=1000.0)) == []
