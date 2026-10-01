"""LA QUALITA' DELL'INGRESSO E IL REGIME GLOBALE (1 ott 2026, cattura dei dati).

Dallo snapshot su cui si apre (nessuna chiamata in piu'): ora dello snapshot,
chiusura del segnale, ingresso contro segnale in R, open interest, volume 24h,
mark price. `expected_entry_price` = la chiusura del segnale (prima non veniva
mai impostato e lo slippage d'ingresso usciva sempre 0); il prezzo eseguito NON
cambia. E il regime GLOBALE accanto a quello della coin.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import AssetSnapshot, Direction, IndicatorSnapshot, Regime
from bot.execution.executor import ExecutionEngine
from bot.learning import cattura
from tests.test_memoria_trade_misure import _params

TS = datetime(2026, 10, 1, 8, 0, 5, tzinfo=timezone.utc)


def _asset(price=100.0, close=99.6, **kw):
    return AssetSnapshot(symbol="BTCUSDT", price=price, close_chiusa=close, regime=Regime.BEAR_TRENDING,
                         volume_24h=5e8, open_interest=12345.0, mark_price=100.05, timestamp=TS,
                         indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=price)},
                         **kw)


def test_qualita_ingresso_pura():
    q = cattura.qualita_ingresso(_asset(), 100.0, 98.0, True)
    assert q["snapshot_ts"] == pytest.approx(TS.timestamp())
    assert q["close_segnale"] == 99.6
    assert q["ingresso_vs_segnale_r"] == pytest.approx(0.2)        # 0,4 sopra su R=2: peggio
    assert q["open_interest_at_entry"] == 12345.0
    assert q["volume_24h_at_entry"] == 5e8 and q["mark_price_at_entry"] == 100.05
    s = cattura.qualita_ingresso(_asset(), 100.0, 102.0, False)
    assert s["ingresso_vs_segnale_r"] == pytest.approx(-0.2)       # short piu' in alto: meglio
    vuoto = cattura.qualita_ingresso(object(), 100.0, 98.0, True)
    assert vuoto["close_segnale"] is None and vuoto["ingresso_vs_segnale_r"] is None


def test_l_ingresso_va_sul_trade_e_il_fill_non_cambia(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    pos = eng.open_position(_asset(), "s", Direction.LONG, _params(stop=98, tp=110),
                            regime_globale=Regime.SIDEWAYS)
    assert pos.entry_price == 100.0                                 # eseguito al prezzo vivo
    assert pos.expected_entry_price == 99.6
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.exit_price == 98.0 and closed.entry_price == 100.0
    assert closed.expected_entry_price == 99.6
    assert closed.entry_slippage_pct == pytest.approx((100.0 - 99.6) / 99.6)
    assert closed.close_segnale == 99.6
    assert closed.ingresso_vs_segnale_r == pytest.approx(0.2)
    assert closed.snapshot_ts == pytest.approx(TS.timestamp())
    assert closed.open_interest_at_entry == 12345.0 and closed.mark_price_at_entry == 100.05
    # regime: quello della COIN resta in regime_at_entry, il GLOBALE accanto
    assert closed.regime_at_entry == Regime.BEAR_TRENDING
    assert closed.regime_globale_at_entry == Regime.SIDEWAYS


def test_senza_chiusura_del_segnale_resta_come_prima(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(close=None), "s", Direction.LONG, _params(stop=98, tp=110))
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.expected_entry_price == 100.0 and closed.entry_slippage_pct == 0.0
    assert closed.close_segnale is None and closed.regime_globale_at_entry is None


def test_l_ingresso_sopravvive_al_riavvio(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    fb = FirebaseClient()
    ExecutionEngine(firebase=fb, dry_run=True).open_position(
        _asset(), "s", Direction.LONG, _params(stop=98, tp=110), regime_globale="bull_trending",
        promessa_gate={"pass_count": 2})
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.expected_entry_price == 99.6 and closed.close_segnale == 99.6
    assert closed.regime_globale_at_entry == Regime.BULL_TRENDING
    assert closed.promessa_gate == {"pass_count": 2}


def test_un_annotazione_rotta_non_ferma_l_apertura(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    import bot.learning.cattura as c

    def esplode(*a, **k):
        raise RuntimeError("rotta")
    monkeypatch.setattr(c, "qualita_ingresso", esplode)
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    pos = eng.open_position(_asset(), "s", Direction.LONG, _params(stop=98, tp=110))
    assert pos is not None and pos.entry_price == 100.0
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.pnl < 0 and closed.close_segnale is None
