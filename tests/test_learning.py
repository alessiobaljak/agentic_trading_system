"""Test del motore di apprendimento: pesi dinamici, metriche, adattamento."""
import time

from bot.core.firebase_client import FirebaseClient
from bot.core.models import Regime
from bot.learning import metrics
from bot.learning.adaptation import AdaptationEngine
from bot.learning.learning_loop import LearningLoop
from bot.learning.trade_logger import TradeLogger


def _trade(strategy, regime, pnl, conf=70, hour=10, asset="BTCUSDT", timeframe="15m"):
    win = pnl > 0
    return {
        "trade_id": f"{strategy}-{regime}-{pnl}-{time.time_ns()}",
        "symbol": asset, "strategy": strategy, "regime_at_entry": regime,
        "direction": "long", "pnl": pnl, "timeframe": timeframe,
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


def test_weights_ignore_other_timeframe_trades():
    # I trade dell'era 1h (o senza campo timeframe) NON devono avvelenare i pesi
    # del timeframe corrente (15m nei test): al cambio si riparte dal prior.
    old = [_trade("breakout", "sideways", -5, timeframe="1h") for _ in range(10)]
    legacy = [_trade("breakout", "sideways", -5) for _ in range(5)]
    for t in legacy:
        t.pop("timeframe")   # trade storico senza campo
    weights = metrics.compute_weights(old + legacy)
    assert weights == []   # nessun trade del tf corrente -> nessun peso (non zero!)
    # con anche trade 15m, solo quelli contano
    weights = metrics.compute_weights(old + [_trade("breakout", "sideways", 10) for _ in range(6)])
    w = next(x for x in weights if x.strategy == "breakout")
    assert w.sample_size == 6 and w.win_rate == 1.0 and w.weight == 1.0


def test_prior_above_ramp_one_loss_is_gentle():
    # prior 0.65 SOPRA la rampa: una singola perdita riduce ma non falcia (-40%),
    # e i perdenti veri (tante perdite, zero vittorie) muoiono comunque.
    one_loss = metrics.compute_weights([_trade("momentum", "bull_trending", -5)])
    w = next(x for x in one_loss if x.strategy == "momentum")
    assert 0.7 < w.weight < 0.9, w.weight
    many_losses = metrics.compute_weights(
        [_trade("momentum", "bull_trending", -5) for _ in range(8)])
    w = next(x for x in many_losses if x.strategy == "momentum")
    assert w.weight <= 0.05, w.weight


def test_manual_and_external_exits_excluded_from_weights():
    # le uscite NON decise dalla strategia (manuale/kill/circuit) NON devono
    # influenzare il peso: sono interventi esterni, non l'edge della strategia.
    def t(strategy, pnl, reason):
        d = _trade(strategy, "sideways", pnl)
        d["exit_reason"] = reason
        return d
    # 6 perdite reali (stop_loss) -> peso basso; + 6 "vittorie" MANUALI ignorate
    trades = [t("breakout", -5, "stop_loss") for _ in range(6)]
    trades += [t("breakout", 10, "manual") for _ in range(6)]
    trades += [t("breakout", 10, "kill_switch") for _ in range(3)]
    w = next(x for x in metrics.compute_weights(trades) if x.strategy == "breakout")
    assert w.sample_size == 6            # solo le 6 uscite decise dalla strategia
    assert w.win_rate == 0.0             # le vittorie manuali NON la salvano
    assert w.weight < 0.3


def test_allocation_neutral_without_data_scaled_with_data():
    # SENZA pesi appresi: learning NEUTRO (nessuna deviazione senza dati); la sola
    # convinzione muove poco. CON dati: peso alto -> boost, peso basso -> taglio.
    from bot.core.firebase_client import FirebaseClient
    eng = AdaptationEngine(FirebaseClient())
    # nessun dato: a confidenza media il fattore resta vicino a 1
    r, l, note = eng.allocation("breakout", Regime.SIDEWAYS, confidence=60)
    assert "neutro" in note and 0.9 < r <= 1.1 and 0.9 < l <= 1.05
    # dati: peso ALTO + confidenza alta -> risk boost (mai oltre 1.5 / 1.3)
    eng._weights["breakout|sideways"] = 1.0
    r_hi, l_hi, _ = eng.allocation("breakout", Regime.SIDEWAYS, confidence=85)
    assert 1.3 < r_hi <= 1.5 and 1.1 < l_hi <= 1.3
    # peso BASSO -> riduzione netta anche a confidenza alta
    eng._weights["breakout|sideways"] = 0.2
    r_lo, l_lo, _ = eng.allocation("breakout", Regime.SIDEWAYS, confidence=85)
    assert r_lo < 0.9 and l_lo < 1.0
    assert r_lo >= 0.5 and l_lo >= 0.7      # mai sotto i floor


def test_allocation_respects_hard_caps_in_risk_manager():
    # anche col boost massimo, leva e rischio NON superano i cap di sicurezza.
    from bot.risk.risk_manager import RiskManager
    from bot.risk import hard_limits
    from bot.core.models import (AssetSnapshot, Direction, IndicatorSnapshot,
                                 OrchestratorDecision, RiskSettings)
    rm = RiskManager()
    asset = AssetSnapshot(symbol="BTCUSDT", price=100.0,
                          indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=100.0)})
    dec = OrchestratorDecision(asset="BTCUSDT", strategy="x", direction=Direction.LONG,
                               size_multiplier=1.0, confidence=90,
                               suggested_stop=98.0, suggested_target=104.0)
    user = RiskSettings(leverage=4.0, risk_per_trade=0.025)
    p = rm.resolve_effective_params(dec, user, asset, 10_000, volatility_sigma=0.0,
                                    risk_mult=1.5, lev_mult=1.3, alloc_note="test")
    assert p.leverage <= hard_limits.MAX_LEVERAGE            # 4*1.3=5.2 -> clampata a 5
    assert p.leverage == int(p.leverage) and p.leverage >= 1  # leva INTERA (Binance)
    assert p.risk_per_trade <= hard_limits.MAX_RISK_PER_TRADE  # 2.5%*1.5=3.75% -> 3%
    # e il taglio da learning riduce davvero
    p_lo = rm.resolve_effective_params(dec, user, asset, 10_000, volatility_sigma=0.0,
                                       risk_mult=0.5, lev_mult=0.7)
    assert p_lo.risk_per_trade < p.risk_per_trade
    assert p_lo.leverage < p.leverage


def test_trailing_keep_learns_from_verdicts():
    from bot.learning.metrics import compute_trailing_keep
    def tv(strategy, verdict, ko):
        return {"strategy": strategy, "timeframe": "15m", "exit_reason": "trailing_stop",
                "trailing_verdict": verdict, "trailing_knockout_atr": ko}
    # tanti premature DA RUMORE -> keep si ALLENTA (sotto 0.5), mai sotto 0.35
    noisy = [tv("gen_a", "premature", 0.4) for _ in range(20)] + \
            [tv("gen_a", "protected", None) for _ in range(4)]
    # tanti protected -> keep si STRINGE (sopra 0.5), mai sopra 0.65
    prot = [tv("gen_b", "protected", None) for _ in range(20)] + \
           [tv("gen_b", "premature", 2.5) for _ in range(4)]
    # campione piccolo -> NESSUN adattamento (assente dalla mappa)
    few = [tv("gen_c", "premature", 0.3) for _ in range(3)]
    keep = compute_trailing_keep(noisy + prot + few)
    assert 0.35 <= keep["gen_a"] < 0.5
    assert 0.5 < keep["gen_b"] <= 0.65
    assert "gen_c" not in keep
    # trade di un ALTRO timeframe: ignorati
    old = [dict(t, timeframe="1h") for t in noisy]
    assert compute_trailing_keep(old) == {}


def test_locked_stop_per_strategy_keep():
    from bot.execution.exit_logic import locked_stop
    # armato (fav 106 su trigger 0.5*10=5): keep alto blocca PIU' guadagno (stop
    # piu' vicino), keep basso lascia respirare (stop piu' largo)
    tight = locked_stop(100, 110, True, 106.0, 98.0, keep=0.65)
    base = locked_stop(100, 110, True, 106.0, 98.0)            # 0.5 globale
    loose = locked_stop(100, 110, True, 106.0, 98.0, keep=0.35)
    assert tight > base > loose > 98.0


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


def test_robust_only_exempts_generated_strategies():
    # le generate (gen_*) sono coin-specifiche: NON devono cadere per la regola ">=3 coin",
    # mentre una base su 1 sola coin sì.
    from bot.core.firebase_client import FirebaseClient
    from bot.config import settings
    eng = AdaptationEngine(FirebaseClient())
    old = settings.MIN_COINS_PER_STRATEGY
    settings.MIN_COINS_PER_STRATEGY = 3
    try:
        keys = ["BTCUSDT|gen_abc", "ETHUSDT|gen_def", "SOLUSDT|trend_following"]
        robust = eng._robust_only(keys)
        assert "BTCUSDT|gen_abc" in robust and "ETHUSDT|gen_def" in robust  # generate esentate
        assert "SOLUSDT|trend_following" not in robust                       # base su 1 coin -> fuori
    finally:
        settings.MIN_COINS_PER_STRATEGY = old


def test_default_flat_until_validated():
    # DEFAULT (bootstrap OFF): senza coppie a 3 passaggi il bot resta FLAT, anche
    # se il registro ha coppie a 1 passaggio. Non si trada su strategie non validate.
    from bot.core.firebase_client import FirebaseClient, encode_pairs
    from bot.config import settings
    fb = FirebaseClient()
    pairs = {"BTCUSDT|gen_aaa": {"pass_count": 1, "last_params": {"rr": 2.0}}}
    fb.set_doc("strategy_registry", "validated", {"validated": [], "pairs": encode_pairs(pairs)})
    assert settings.BOOTSTRAP_TRADE_UNVALIDATED is False   # default
    eng = AdaptationEngine(fb)
    eng.load_params()
    assert eng._passed == set()                            # flat
    assert eng.is_enabled("BTCUSDT", "gen_aaa") is False


def test_flat_until_gate1_ready(monkeypatch):
    # Anche con coppie VALIDATE (3 passaggi), se il GATE 1 non e' "ready"
    # (copertura < soglia) il bot resta FLAT. Diventa operativo solo quando ready.
    from bot.core.firebase_client import FirebaseClient, encode_pairs
    from bot.config import settings as _s
    monkeypatch.setattr(_s, "MIN_COINS_PER_STRATEGY", 1)
    fb = FirebaseClient()
    pairs = {"BTCUSDT|gen_aaa": {"pass_count": 3, "last_params": {"rr": 2.0}}}
    reg = {"validated": ["BTCUSDT|gen_aaa"], "pairs": encode_pairs(pairs), "ready": False}
    fb.set_doc("strategy_registry", "validated", reg)
    eng = AdaptationEngine(fb)
    eng.load_params()
    assert eng._passed == set()                    # ready=False -> flat
    # ora il gate e' ready -> la coppia validata diventa operativa
    reg["ready"] = True
    fb.set_doc("strategy_registry", "validated", reg)
    eng.load_params()
    assert eng._passed == {"BTCUSDT|gen_aaa"}


def test_bootstrap_opt_in_trades_single_pass_generated(monkeypatch):
    # con BOOTSTRAP_TRADE_UNVALIDATED attivo (e ready-gate disattivato), le generate
    # a 1 passaggio diventano operative (decode, generate esentate dal filtro).
    from bot.core.firebase_client import FirebaseClient, encode_pairs
    from bot.config import settings as _s
    monkeypatch.setattr(_s, "REQUIRE_GATE1_READY", False)
    monkeypatch.setattr(_s, "BOOTSTRAP_TRADE_UNVALIDATED", True)
    fb = FirebaseClient()
    pairs = {
        "BTCUSDT|gen_aaa": {"pass_count": 1, "last_params": {"rr": 2.0}},
        "ETHUSDT|gen_bbb": {"pass_count": 1, "last_params": {"rr": 1.5}},
        "SOLUSDT|breakout": {"pass_count": 0, "fail_count": 1},   # fallita -> esclusa
    }
    fb.set_doc("strategy_registry", "validated",
               {"validated": [], "pairs": encode_pairs(pairs)})
    eng = AdaptationEngine(fb)
    eng.load_params()
    assert eng._passed == {"BTCUSDT|gen_aaa", "ETHUSDT|gen_bbb"}
    assert eng._params["BTCUSDT|gen_aaa"]["rr"] == 2.0
    assert eng.is_enabled("BTCUSDT", "gen_aaa") is True


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


def test_probation_reentry_instead_of_amnesia():
    # Un gruppo ucciso (peso 0) che ESCE dalla finestra 30g non deve risorgere
    # di colpo a 1.0: il peso viene trascinato e recupera gradualmente
    # (WEIGHT_RECOVERY_DAYS). A recupero completo viene potato (default 1.0).
    fb = FirebaseClient()
    eng = AdaptationEngine(fb)
    # stato precedente: breakout|sideways ucciso 15 giorni fa
    fb.set_doc("strategy_weights", "current", {
        "weights": [{"strategy": "breakout", "regime": "sideways", "weight": 0.0}],
        "updated_at": time.time() - 15 * 86400,
    })
    # ricalcolo SENZA quel gruppo (i suoi trade sono usciti dalla finestra)
    other = metrics.compute_weights([_trade("momentum", "bull_trending", 10) for _ in range(6)])
    eng.save_weights(other)
    w = eng.weight_for("breakout", Regime.SIDEWAYS)
    assert 0.4 < w < 0.6, f"dopo 15/30 giorni deve essere ~0.5, non {w}"
    # dopo ALTRI 30 giorni di silenzio -> riabilitata e potata dal documento
    doc = fb.get_doc("strategy_weights", "current")
    doc["updated_at"] = time.time() - 30 * 86400
    fb.set_doc("strategy_weights", "current", doc)
    eng.save_weights(other)
    assert eng.weight_for("breakout", Regime.SIDEWAYS) == 1.0
    saved = {(x["strategy"], x["regime"]) for x in
             fb.get_doc("strategy_weights", "current")["weights"]}
    assert ("breakout", "sideways") not in saved, "a 1.0 il gruppo va potato"
    # un gruppo PRESENTE nel ricalcolo non viene toccato dalla probation
    assert eng.weight_for("momentum", Regime.BULL_TRENDING) == 1.0


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
            direction=Direction.LONG, timeframe="15m",
            entry_time=now - timedelta(hours=2),
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
