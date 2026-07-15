"""Test del motore di apprendimento: pesi dinamici, metriche, adattamento."""
import time

from bot.core.firebase_client import FirebaseClient
from bot.core.models import Regime
from bot.learning import metrics
from bot.learning.adaptation import AdaptationEngine
from bot.learning.learning_loop import LearningLoop
from bot.learning.trade_logger import TradeLogger


def _trade(strategy, regime, pnl, conf=70, hour=10, asset="BTCUSDT"):
    win = pnl > 0
    return {
        "trade_id": f"{strategy}-{regime}-{pnl}-{time.time_ns()}",
        "symbol": asset, "strategy": strategy, "regime_at_entry": regime,
        "direction": "long", "pnl": pnl,
        "pnl_pct": 0.02 if win else -0.01,
        "is_win": win, "hour_bucket": hour, "confidence_at_entry": conf,
        "exit_ts": time.time() - 3600,
    }


def test_losing_strategy_gets_zero_weight_in_regime():
    # 8 perdite su 10 in sideways per breakout -> peso ~0 in sideways
    trades = [_trade("breakout", "sideways", -5) for _ in range(8)]
    trades += [_trade("breakout", "sideways", 10) for _ in range(2)]
    weights = metrics.compute_weights(trades)
    w = next(x for x in weights if x.strategy == "breakout" and x.regime == Regime.SIDEWAYS)
    assert w.weight == 0.0
    assert w.win_rate == 0.2
    assert w.sample_size == 10


def test_winning_strategy_gets_high_weight():
    trades = [_trade("trend_following", "bull_trending", 10) for _ in range(8)]
    trades += [_trade("trend_following", "bull_trending", -5) for _ in range(2)]
    weights = metrics.compute_weights(trades)
    w = next(x for x in weights if x.strategy == "trend_following")
    assert w.weight > 0.5


def test_small_sample_moves_gradually():
    # SHRINKAGE: 2 perdite fanno scendere il peso SOTTO 1.0 (impara subito) ma NON
    # crollare a 0 (non reagisce al rumore di un campione minuscolo). Con piu' dati
    # si avvicina all'osservato -> vedi gli altri due test (zero / alto).
    trades = [_trade("grid_trading", "sideways", -5) for _ in range(2)]
    weights = metrics.compute_weights(trades)
    w = next(x for x in weights if x.strategy == "grid_trading")
    assert 0.0 < w.weight < 1.0


def test_confidence_outcome_correlation():
    # confidenza alta -> esito positivo (correlazione attesa > 0)
    trades = []
    for c, p in [(90, 0.03), (80, 0.02), (40, -0.01), (30, -0.02), (60, 0.005), (20, -0.03)]:
        t = _trade("x", "sideways", p)
        t["confidence_at_entry"] = c
        t["pnl_pct"] = p
        trades.append(t)
    corr = metrics.confidence_outcome_correlation(trades)
    assert corr is not None and corr > 0.5


def test_is_enabled_failsafe_when_registry_missing():
    # FAIL-SAFE: senza dati di ottimizzazione (registro non caricato) e con
    # REQUIRE_VALIDATED_PAIRS attivo, NESSUNA coppia è abilitata (bot resta flat).
    from bot.config import settings
    eng = AdaptationEngine(FirebaseClient())
    eng._has_opt_data = False
    old = settings.REQUIRE_VALIDATED_PAIRS
    settings.REQUIRE_VALIDATED_PAIRS = True
    try:
        assert eng.is_enabled("BTCUSDT", "trend_following") is False
        settings.REQUIRE_VALIDATED_PAIRS = False  # bootstrap -> coi default tutto attivo
        assert eng.is_enabled("BTCUSDT", "trend_following") is True
    finally:
        settings.REQUIRE_VALIDATED_PAIRS = old


def test_is_enabled_only_validated_pairs_when_registry_present():
    # con registro presente: SOLO le coppie validate operano.
    eng = AdaptationEngine(FirebaseClient())
    eng._has_opt_data = True
    eng._passed = {"BTCUSDT|trend_following"}
    assert eng.is_enabled("BTCUSDT", "trend_following") is True
    assert eng.is_enabled("ETHUSDT", "trend_following") is False   # non validata
    assert eng.is_enabled("BTCUSDT", "mean_reversion") is False    # non validata


def test_refresh_weights_reacts_within_the_hour():
    # Opzione A: il bot ricalcola i pesi dai trade su Firestore (niente Binance).
    # 5 perdite in sideways per 'breakout' -> dopo il refresh il peso e' 0 in sideways.
    from bot.main import TradingBot
    fb = FirebaseClient()
    for i in range(5):
        t = _trade("breakout", "sideways", -5)
        t["trade_id"] = f"loss{i}"
        fb.set_doc("trades", t["trade_id"], t)
    adaptation = AdaptationEngine(fb)
    # prima del refresh: nessun peso salvato -> default 1.0
    assert adaptation.weight_for("breakout", Regime.SIDEWAYS) == 1.0

    class _Stub:
        pass
    bot = _Stub()
    bot.logger = TradeLogger(fb)
    bot.adaptation = adaptation
    TradingBot.refresh_weights(bot, time.time())

    # dopo il refresh, in-RAM: la strategia perdente e' azzerata in sideways
    assert adaptation.weight_for("breakout", Regime.SIDEWAYS) == 0.0


def test_learning_loop_end_to_end_with_memory_firebase():
    fb = FirebaseClient()  # in-memory (nessun service account in test)
    logger = TradeLogger(fb)
    from bot.core.models import ClosedTrade, Direction, ExitReason, Regime as R
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    for i in range(10):
        win = i < 7
        logger.log(ClosedTrade(
            trade_id=f"t{i}", symbol="ETHUSDT", strategy="vwap_reversion",
            direction=Direction.LONG, entry_time=now - timedelta(hours=2),
            exit_time=now - timedelta(hours=1), entry_price=100,
            exit_price=102 if win else 99, size=1, notional=100, leverage=2,
            pnl=2 if win else -1, pnl_pct=0.02 if win else -0.01,
            exit_reason=ExitReason.TAKE_PROFIT if win else ExitReason.STOP_LOSS,
            regime_at_entry=R.SIDEWAYS, confidence_at_entry=75,
        ))
    loop = LearningLoop(fb)
    reports = loop.run()
    assert reports[30].total_trades == 10
    assert reports[30].overall_win_rate == 0.7
    # i pesi devono essere stati salvati e ricaricabili
    eng = AdaptationEngine(fb)
    w = eng.weight_for("vwap_reversion", Regime.SIDEWAYS)
    assert w > 0.5
    # baseline ignora i pesi
    assert eng.weight_for("vwap_reversion", Regime.SIDEWAYS, baseline=True) == 1.0
