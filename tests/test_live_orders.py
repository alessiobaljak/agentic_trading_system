"""Ordini di protezione REALI (solo DRY_RUN=False): il book deve rispecchiare il piano.

Con lo scale-out attivo il piano di uscita e' una SCALA (30% a 1.5R, 30% a 3R, 40% a 5R)
con stop che si sposta a break-even dopo il primo TP. Se sull'exchange restasse un solo
TP e uno stop fisso, gli ordini veri direbbero una cosa e la logica del bot un'altra:
al primo crash del bot la posizione resterebbe protetta dal piano SBAGLIATO.

Qui si usa un client Binance FINTO che registra le chiamate: si verifica cosa finisce
sul book, non la rete.

Entry 100 / stop 98 -> R=2 -> ladder 103 / 106 / 110.
"""
import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Direction, EffectiveRiskParams, IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine


class FakeBinance:
    """Registra gli ordini creati/cancellati e assegna orderId progressivi."""

    def __init__(self, fail_create: bool = False):
        self.orders: list[dict] = []
        self.cancelled: list[int] = []
        self.leverage: list[dict] = []
        self._next_id = 1000
        self.fail_create = fail_create

    def futures_change_leverage(self, **kw):
        self.leverage.append(kw)
        return {}

    def futures_create_order(self, **kw):
        if self.fail_create and kw.get("type") == "STOP_MARKET" and self.orders:
            raise RuntimeError("boom: stop non piazzato")
        self._next_id += 1
        kw = dict(kw, orderId=self._next_id)
        self.orders.append(kw)
        return kw

    def futures_cancel_order(self, **kw):
        self.cancelled.append(kw.get("orderId"))
        return {}

    # --- helper di lettura ---
    def of_type(self, t: str) -> list[dict]:
        return [o for o in self.orders if o.get("type") == t]


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


def _live_engine(client) -> ExecutionEngine:
    """Engine in modalita' LIVE simulata: dry_run=False ma client iniettato a mano
    (nessuna chiamata di rete, nessuna chiave API)."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.dry_run = False
    eng._client = client
    return eng


@pytest.fixture
def scale_on(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)


def test_live_places_full_tp_ladder(scale_on):
    """Un TAKE_PROFIT_MARKET per OGNI livello della scala, con la sua frazione."""
    fake = FakeBinance()
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))

    tps = fake.of_type("TAKE_PROFIT_MARKET")
    assert [o["stopPrice"] for o in tps] == [103.0, 106.0, 110.0]
    assert [o["quantity"] for o in tps] == [0.3, 0.3, 0.4]
    assert all(o["reduceOnly"] for o in tps)
    assert all(o["side"] == "SELL" for o in tps)          # long -> chiude vendendo


def test_live_tp_quantities_sum_to_position_without_dust(scale_on):
    """L'ultima fetta prende il RESTO: nessuna polvere non protetta per arrotondamento."""
    fake = FakeBinance()
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "breakout", Direction.LONG, _params(qty=0.7, stop=98))
    tps = fake.of_type("TAKE_PROFIT_MARKET")
    assert abs(sum(o["quantity"] for o in tps) - 0.7) < 1e-9


def test_live_short_ladder_is_below_entry(scale_on):
    """Short: entry 100, stop 102 -> R=2 -> TP a 97/94/90, chiusi comprando."""
    fake = FakeBinance()
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "breakout", Direction.SHORT, _params(qty=1.0, stop=102, tp=96))
    tps = fake.of_type("TAKE_PROFIT_MARKET")
    assert [o["stopPrice"] for o in tps] == [97.0, 94.0, 90.0]
    assert all(o["side"] == "BUY" for o in tps)


def test_live_stop_is_replaced_when_moved_to_breakeven(scale_on):
    """Dopo TP1 lo stop logico va a break-even: quello sul BOOK deve seguirlo,
    altrimenti la protezione esiste solo nella memoria del bot."""
    fake = FakeBinance()
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    pos = eng.open_positions["BTCUSDT"]
    first_stop_id = pos.sl_order_id
    assert pos.exchange_stop == 98.0

    eng.update_position("BTCUSDT", 103.0)          # TP1 -> break-even

    assert first_stop_id in fake.cancelled          # vecchio stop cancellato
    stops = fake.of_type("STOP_MARKET")
    assert len(stops) == 2                          # ripiazzato
    assert stops[-1]["stopPrice"] == 100.0          # a break-even (= entry)
    assert abs(stops[-1]["quantity"] - 0.7) < 1e-9  # sulla qty RESIDUA
    assert pos.exchange_stop == 100.0


def test_live_stop_not_touched_when_unchanged(scale_on):
    """Nessun churn di ordini: se lo stop non si muove non si cancella/ripiazza nulla."""
    fake = FakeBinance()
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    eng.update_position("BTCUSDT", 100.5)          # nessun TP, lock non armato
    eng.update_position("BTCUSDT", 101.0)
    assert fake.cancelled == []
    assert len(fake.of_type("STOP_MARKET")) == 1


def test_live_stop_follows_profit_lock():
    """Senza scale-out: quando il profit-lock alza lo stop, il book viene allineato."""
    fake = FakeBinance()
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "trend_following", Direction.LONG,
                      _params(qty=10.0, stop=98, tp=110))
    eng.update_position("BTCUSDT", 106.0)      # registra high_water=106 (lock dal tick dopo)
    eng.update_position("BTCUSDT", 105.0)      # ora lo stop bloccato e' 103
    stops = fake.of_type("STOP_MARKET")
    assert stops[-1]["stopPrice"] == 103.0
    assert eng.open_positions["BTCUSDT"].exchange_stop == 103.0


def test_live_failed_stop_replacement_is_flagged_not_silent(scale_on, capsys):
    """Se il ripiazzamento fallisce la posizione e' SCOPERTA sul book: lo stato deve
    dirlo (exchange_stop=None) e l'avviso deve comparire nei log, non passare zitto."""
    fake = FakeBinance(fail_create=True)
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    eng.update_position("BTCUSDT", 103.0)      # tenta il break-even -> create fallisce
    pos = eng.open_positions["BTCUSDT"]
    assert pos.exchange_stop is None
    assert pos.sl_order_id is None
    assert "ATTENZIONE" in capsys.readouterr().out


def test_dry_run_places_no_orders(scale_on):
    """In paper NESSUN ordine reale, mai: il client non viene toccato."""
    fake = FakeBinance()
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng._client = fake
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    eng.update_position("BTCUSDT", 103.0)
    assert fake.orders == [] and fake.cancelled == []


def test_live_order_ids_survive_restart(scale_on):
    """Dopo un riavvio il bot deve sapere QUALE stop cancellare, altrimenti ne
    accumulerebbe uno nuovo a ogni spostamento."""
    fake = FakeBinance()
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    pos = eng.open_positions["BTCUSDT"]
    state = eng.fb.get_rtdb("/positions/BTCUSDT")
    assert state["sl_order_id"] == pos.sl_order_id
    assert state["exchange_stop"] == 98.0

    restored = eng._position_from_state(state)
    assert restored.sl_order_id == pos.sl_order_id
    assert restored.exchange_stop == 98.0


def test_live_close_cancels_leftover_protective_orders(scale_on):
    """Alla chiusura la scala TP/SL non deve restare ORFANA sul book: potrebbe
    chiudere a prezzi arbitrari una posizione futura sullo stesso simbolo."""
    calls = []
    fake = FakeBinance()
    fake.futures_cancel_all_open_orders = lambda **kw: calls.append(kw.get("symbol"))
    eng = _live_engine(fake)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    closed = eng.update_position("BTCUSDT", 98.0)     # stop pieno
    assert closed is not None
    assert calls == ["BTCUSDT"]
