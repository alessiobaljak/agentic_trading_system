"""LEARNING ROBUSTO — quattro difese contro l'inseguimento del rumore.

I pesi strategia×regime guidano size e leva di OGNI trade successivo: sbagliarli
non costa un trade, costa tutti quelli dopo. Le difese sono quattro e agiscono su
assi diversi, per questo convivono:

  * FILTRO ANOMALIE — toglie i trade che non descrivono l'edge (uscite esterne,
    timeframe sbagliato, durate impossibili, slippage fuori scala);
  * SOGLIA DI CAMPIONE — sotto N trade validi non si pubblica nulla;
  * SMOOTHING — stabilizza nel TEMPO (lo shrinkage bayesiano gia' presente
    stabilizza rispetto alla NUMEROSITA': sono cose diverse);
  * SAFETY CHECK — un salto aggregato enorme e' un difetto, non apprendimento.
"""
import time

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import Regime, StrategyRegimeWeight
from bot.learning import metrics
from bot.learning.adaptation import AdaptationEngine


def _t(**kw):
    d = {"strategy": "breakout", "regime_at_entry": "sideways", "pnl": 1.0,
         "pnl_pct": 0.01, "is_win": True, "exit_reason": "take_profit",
         "timeframe": settings.ORCHESTRATOR_TIMEFRAME, "duration_seconds": 3600.0}
    d.update(kw)
    return d


# ---- filtro anomalie ------------------------------------------------------- #
def test_filter_drops_external_exits():
    kept, why = metrics.filter_anomalous_trades(
        [_t(), _t(exit_reason="kill_switch"), _t(exit_reason="manual")])
    assert len(kept) == 1 and why["external_exit"] == 2


def test_filter_drops_other_timeframes():
    kept, why = metrics.filter_anomalous_trades([_t(), _t(timeframe="4h"), _t(timeframe=None)])
    assert len(kept) == 1 and why["wrong_timeframe"] == 2


def test_filter_drops_impossibly_short_trades():
    kept, why = metrics.filter_anomalous_trades([_t(), _t(duration_seconds=5.0)])
    assert len(kept) == 1 and why["short_duration"] == 1


def test_filter_keeps_trades_without_duration_information():
    """Assenza di dato non e' anomalia: i trade vecchi non hanno il campo e
    scartarli svuoterebbe la finestra proprio quando serve."""
    kept, why = metrics.filter_anomalous_trades([_t(duration_seconds=None)])
    assert len(kept) == 1 and "short_duration" not in why


def test_slippage_filter_needs_real_data_before_acting():
    """In DRY_RUN lo slippage e' 0: la mediana sarebbe 0 e QUALUNQUE valore
    positivo risulterebbe anomalo. Il filtro deve disattivarsi da solo."""
    kept, why = metrics.filter_anomalous_trades([_t(slippage=0.0) for _ in range(30)])
    assert len(kept) == 30 and "slippage_outlier" not in why


def test_slippage_filter_drops_the_outliers_when_data_exists():
    trades = [_t(slippage=0.001) for _ in range(20)] + [_t(slippage=0.05)]
    kept, why = metrics.filter_anomalous_trades(trades)
    assert why["slippage_outlier"] == 1 and len(kept) == 20


def test_filter_on_empty_input():
    assert metrics.filter_anomalous_trades([]) == ([], {})


# ---- soglia di campione ---------------------------------------------------- #
def _save(fb, weights, monkeypatch, **over):
    for k, v in over.items():
        monkeypatch.setattr(settings, k, v)
    AdaptationEngine(fb).save_weights(weights)


def _w(strategy="breakout", regime=Regime.SIDEWAYS, weight=0.2, n=100):
    return StrategyRegimeWeight(strategy=strategy, regime=regime, weight=weight,
                                win_rate=0.4, avg_rr=None, sample_size=n)


def test_weights_are_not_published_below_the_sample_threshold(monkeypatch):
    fb = FirebaseClient()
    _save(fb, [_w(n=10)], monkeypatch, LEARNING_MIN_TRADES_TOTAL=50)
    assert fb.get_doc("strategy_weights", "current") in (None, {})


def test_weights_are_published_above_the_threshold(monkeypatch):
    fb = FirebaseClient()
    _save(fb, [_w(n=80)], monkeypatch, LEARNING_MIN_TRADES_TOTAL=50,
          LEARNING_SMOOTHING_ALPHA=1.0)
    doc = fb.get_doc("strategy_weights", "current")
    assert doc and doc["weights"][0]["weight"] == pytest.approx(0.2)
    assert doc["version"] == 1


# ---- smoothing ------------------------------------------------------------- #
def test_smoothing_moves_only_partway_towards_the_new_value(monkeypatch):
    fb = FirebaseClient()
    fb.set_doc("strategy_weights", "current", {
        "weights": [{"strategy": "breakout", "regime": "sideways", "weight": 1.0}],
        "updated_at": time.time(), "version": 7})
    # alpha 0.3: da 1.0 verso 0.0 -> 0.3*0 + 0.7*1.0 = 0.7
    _save(fb, [_w(weight=0.0, n=80)], monkeypatch, LEARNING_MIN_TRADES_TOTAL=1,
          LEARNING_SMOOTHING_ALPHA=0.3, LEARNING_MAX_TOTAL_CHANGE=1.0)
    doc = fb.get_doc("strategy_weights", "current")
    assert doc["weights"][0]["weight"] == pytest.approx(0.7)
    assert doc["version"] == 8            # la versione avanza


def test_a_new_group_is_not_smoothed_towards_anything(monkeypatch):
    """Senza un valore precedente non c'e' nulla da smorzare: prendere meta'
    strada dal default farebbe nascere ogni strategia con un peso inventato."""
    fb = FirebaseClient()
    _save(fb, [_w(weight=0.2, n=80)], monkeypatch, LEARNING_MIN_TRADES_TOTAL=1,
          LEARNING_SMOOTHING_ALPHA=0.3)
    assert fb.get_doc("strategy_weights", "current")["weights"][0]["weight"] == \
        pytest.approx(0.2)


# ---- safety check ---------------------------------------------------------- #
def test_a_huge_aggregate_jump_is_not_published(monkeypatch):
    fb = FirebaseClient()
    fb.set_doc("strategy_weights", "current", {
        "weights": [{"strategy": "breakout", "regime": "sideways", "weight": 1.0}],
        "updated_at": time.time(), "version": 3})
    # alpha 1.0 (nessuno smoothing) -> il salto arriva intero al controllo
    _save(fb, [_w(weight=0.0, n=80)], monkeypatch, LEARNING_MIN_TRADES_TOTAL=1,
          LEARNING_SMOOTHING_ALPHA=1.0, LEARNING_MAX_TOTAL_CHANGE=0.40)
    doc = fb.get_doc("strategy_weights", "current")
    assert doc["weights"][0]["weight"] == 1.0, "i pesi vecchi devono restare"
    assert doc["version"] == 3, "la versione non deve avanzare"


def test_a_moderate_change_passes_the_safety_check(monkeypatch):
    fb = FirebaseClient()
    fb.set_doc("strategy_weights", "current", {
        "weights": [{"strategy": "breakout", "regime": "sideways", "weight": 1.0}],
        "updated_at": time.time(), "version": 3})
    _save(fb, [_w(weight=0.8, n=80)], monkeypatch, LEARNING_MIN_TRADES_TOTAL=1,
          LEARNING_SMOOTHING_ALPHA=1.0, LEARNING_MAX_TOTAL_CHANGE=0.40)
    doc = fb.get_doc("strategy_weights", "current")
    assert doc["weights"][0]["weight"] == pytest.approx(0.8)
    assert doc["version"] == 4


# ---- storico --------------------------------------------------------------- #
def test_history_is_written_and_bounded(monkeypatch):
    """Anello di N slot: l'id e' la versione modulo N, cosi' lo storico resta
    limitato senza dover elencare la collection per potarla."""
    fb = FirebaseClient()
    monkeypatch.setattr(settings, "LEARNING_HISTORY_VERSIONS", 3)
    eng = AdaptationEngine(fb)
    monkeypatch.setattr(settings, "LEARNING_MIN_TRADES_TOTAL", 1)
    monkeypatch.setattr(settings, "LEARNING_SMOOTHING_ALPHA", 1.0)
    monkeypatch.setattr(settings, "LEARNING_MAX_TOTAL_CHANGE", 10.0)
    for i in range(5):
        eng.save_weights([_w(weight=0.5 + i / 100, n=80)])
    assert fb.get_doc("strategy_weights", "current")["version"] == 5
    slots = [fb.get_doc("strategy_weights", f"v{n:03d}") for n in range(3)]
    assert all(s for s in slots), "tutti gli slot dell'anello devono esistere"
    # v002 e' stato riscritto dalla versione 5 (5 % 3 == 2)
    assert slots[2]["version"] == 5
