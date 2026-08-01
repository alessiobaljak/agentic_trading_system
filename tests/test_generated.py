"""Test del motore di strategie GENERATE: interprete, generatore, integrazione."""
from bot.core.firebase_client import FirebaseClient, decode_pairs
from bot.core.models import AssetSnapshot, Direction, IndicatorSnapshot, Regime
from bot.learning.adaptation import AdaptationEngine
from bot.strategies.generated import GeneratedStrategy, spec_id
from bot.strategies.generator import generate_specs, mutate


def _asset(rsi=50.0, price=100.0, atr=2.0, bb_lower=95.0, bb_upper=105.0):
    ind = IndicatorSnapshot(timeframe="15m", rsi=rsi, atr=atr, close=price,
                            bb_lower=bb_lower, bb_upper=bb_upper, bb_mid=100.0)
    return AssetSnapshot(symbol="BTCUSDT", price=price, regime=Regime.SIDEWAYS,
                         indicators={"15m": ind})


def _rsi_spec():
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
            "volume_mult": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec["id"] = spec_id(spec)
    return spec


def test_generated_long_short_and_flat():
    strat = GeneratedStrategy(_rsi_spec())
    # rsi basso -> LONG
    sig = strat.generate_signal(_asset(rsi=25.0))
    assert sig is not None and sig.direction == Direction.LONG
    assert sig.suggested_stop is not None and sig.suggested_target is not None
    # rsi alto -> SHORT
    assert strat.generate_signal(_asset(rsi=78.0)).direction == Direction.SHORT
    # rsi neutro -> nessun segnale
    assert strat.generate_signal(_asset(rsi=50.0)) is None


def test_generated_two_features_must_both_agree():
    # rsi_extreme AND bb_touch: serve rsi basso E prezzo sotto BB inferiore
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                         {"kind": "bb_touch"}],
            "volume_mult": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec["id"] = spec_id(spec)
    strat = GeneratedStrategy(spec)
    # rsi basso ma prezzo dentro le bande -> niente (le due non concordano)
    assert strat.generate_signal(_asset(rsi=25.0, price=100.0)) is None
    # rsi basso E prezzo <= bb_lower -> LONG
    sig = strat.generate_signal(_asset(rsi=25.0, price=94.0, bb_lower=95.0))
    assert sig is not None and sig.direction == Direction.LONG


def test_generated_missing_indicator_is_safe():
    spec = {"features": [{"kind": "macd_cross"}], "atr_mult_stop": 1.5, "rr": 2.0}
    spec["id"] = spec_id(spec)
    # asset senza macd -> nessun crash, nessun segnale
    assert GeneratedStrategy(spec).generate_signal(_asset()) is None


def test_generator_unique_and_coherent():
    specs = generate_specs(30, seed=3)
    ids = [s["id"] for s in specs]
    assert len(ids) == len(set(ids))  # tutti unici
    for s in specs:
        kinds = [f["kind"] for f in s["features"]]
        assert 1 <= len(kinds) <= 3
        # nessuna coppia incompatibile (es. bb_touch + bb_break)
        assert not ({"bb_touch", "bb_break"} <= set(kinds))
        assert not ({"vwap_momentum", "vwap_reversion"} <= set(kinds))
        assert not ({"stoch_extreme", "stoch_momentum"} <= set(kinds))


def test_new_features_and_adx_filter():
    from bot.core.models import IndicatorSnapshot
    # stoch_extreme: stoch_k basso -> LONG
    spec = {"features": [{"kind": "stoch_extreme", "low": 20.0, "high": 80.0}],
            "atr_mult_stop": 1.5, "rr": 2.0}
    spec["id"] = spec_id(spec)
    a = _asset()
    a.indicators["15m"] = IndicatorSnapshot(timeframe="15m", atr=2.0, close=100.0,
                                            stoch_k=10.0, stoch_d=15.0, adx=30.0)
    assert GeneratedStrategy(spec).generate_signal(a).direction == Direction.LONG
    # filtro ADX: con min_adx alto e adx basso -> nessun segnale
    spec2 = {"features": [{"kind": "stoch_extreme", "low": 20.0, "high": 80.0}],
             "min_adx": 25.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec2["id"] = spec_id(spec2)
    a.indicators["15m"].adx = 10.0  # trend debole
    assert GeneratedStrategy(spec2).generate_signal(a) is None


def test_mutate_produces_valid_spec():
    parent = _rsi_spec()
    child = mutate(parent, seed=5)
    assert "id" in child and child["features"]
    assert GeneratedStrategy(child) is not None


def test_merge_into_registry_only_passed_and_accumulates():
    from scripts.discover_strategies import merge_into_registry
    fb = FirebaseClient()
    out = {
        # data_end come nel produttore reale: senza, il pass onesto (fail-closed)
        # non conta e la potatura scarta la coppia a pass_count 0
        "BTCUSDT|gen_aaa": {"symbol": "BTCUSDT", "strategy": "gen_aaa", "params": {},
                            "oos_pf": 1.3, "oos_pnl_pct": 0.2, "oos_trades": 40,
                            "passed": True, "data_end": 1_700_000_000.0},
        "BTCUSDT|gen_bbb": {"symbol": "BTCUSDT", "strategy": "gen_bbb", "params": {},
                            "oos_pf": 0.9, "oos_pnl_pct": -0.1, "oos_trades": 30, "passed": False},
    }
    merge_into_registry(fb, out, passed_now=["BTCUSDT|gen_aaa"])
    reg = fb.get_doc("strategy_registry", "validated")
    pairs = decode_pairs(reg["pairs"])
    # solo la passata entra; la fallita NON sporca il registro
    assert "BTCUSDT|gen_aaa" in pairs
    assert "BTCUSDT|gen_bbb" not in pairs
    assert "BTCUSDT|gen_aaa" not in reg["validated"]  # serve >=3 pass
    # dopo 3 pass diventa validata/operabile
    # ogni pass richiede >=24h di dati NUOVI: si avanza data_end di un giorno
    out["BTCUSDT|gen_aaa"]["data_end"] = 1_700_000_000.0 + 86_400.0
    merge_into_registry(fb, out, passed_now=["BTCUSDT|gen_aaa"])
    out["BTCUSDT|gen_aaa"]["data_end"] = 1_700_000_000.0 + 2 * 86_400.0
    merge_into_registry(fb, out, passed_now=["BTCUSDT|gen_aaa"])
    reg = fb.get_doc("strategy_registry", "validated")
    assert decode_pairs(reg["pairs"])["BTCUSDT|gen_aaa"]["pass_count"] == 3
    assert "BTCUSDT|gen_aaa" in reg["validated"]


def test_merge_preserves_base_pairs_and_recomputes_coverage():
    import time
    from scripts.discover_strategies import merge_into_registry
    fb = FirebaseClient()
    now = time.time()
    # coppia BASE (senza flag generated) FRESCA e validata (pass>=3): va preservata,
    # e la copertura dev'essere RICALCOLATA sul set validato (Telegram e dashboard
    # leggono lo stesso campo: non puo' restare un valore stantio).
    fb.set_doc("strategy_registry", "validated", {
        "pairs": {"ETHUSDT|trend_following": {
            "pass_count": 5, "last_seen_at": now,
            "symbol": "ETHUSDT", "strategy": "trend_following"}},
        "validated": ["ETHUSDT|trend_following"],
        "universe_size": 10, "coverage": 0.0, "ready": False,
    })
    merge_into_registry(fb, {}, passed_now=[])
    reg = fb.get_doc("strategy_registry", "validated")
    assert "ETHUSDT|trend_following" in decode_pairs(reg["pairs"])   # base preservata
    assert "ETHUSDT|trend_following" in reg["validated"]             # resta validata
    assert reg["coins_covered"] == 1                                 # 1 coin validata
    assert reg["coverage"] == round(1 / 10, 3)                       # ricalcolata, non stantia


def test_robustness_filter_excludes_single_coin_strategies(monkeypatch):
    """Col filtro a 3: una strategia validata su <3 coin NON e' tradabile; su >=3 si'."""
    from bot.config import settings as _s
    monkeypatch.setattr(_s, "MIN_COINS_PER_STRATEGY", 3)
    monkeypatch.setattr(_s, "REQUIRE_GATE1_READY", False)   # qui testiamo il filtro, non il ready-gate
    fb = FirebaseClient()
    # 'breakout' validata su 3 coin (robusta) -> abilitata
    # 'mean_reversion' validata su 2 coin (sotto soglia) -> NON abilitata
    validated = ["BTCUSDT|breakout", "ETHUSDT|breakout", "SOLUSDT|breakout",
                 "BTCUSDT|mean_reversion", "ETHUSDT|mean_reversion"]
    fb.set_doc("strategy_registry", "validated", {
        "validated": validated,
        "pairs": {k: {"pass_count": 3, "last_params": {}} for k in validated},
    })
    eng = AdaptationEngine(fb)
    assert eng.is_enabled("BTCUSDT", "breakout") is True          # 3 coin -> robusta
    assert eng.is_enabled("SOLUSDT", "breakout") is True
    assert eng.is_enabled("BTCUSDT", "mean_reversion") is False   # 2 coin -> esclusa
    assert eng.is_enabled("ETHUSDT", "mean_reversion") is False


def test_adaptation_loads_and_enables_generated(monkeypatch):
    from bot.config import settings as _s
    monkeypatch.setattr(_s, "MIN_COINS_PER_STRATEGY", 1)  # qui non testiamo il filtro robustezza
    monkeypatch.setattr(_s, "REQUIRE_GATE1_READY", False)
    fb = FirebaseClient()
    spec = _rsi_spec()
    gid = spec["id"]
    fb.set_doc("discovered_strategies", "specs", {"specs": {gid: spec}})
    # registro: la coppia BTCUSDT|gen_xxx è validata
    fb.set_doc("strategy_registry", "validated", {
        "validated": [f"BTCUSDT|{gid}"],
        "pairs": {f"BTCUSDT|{gid}": {"pass_count": 3, "last_params": {}}},
    })
    adapt = AdaptationEngine(fb)
    gens = adapt.generated_strategies_for("BTCUSDT")
    assert len(gens) == 1 and gens[0].name == gid
    # su un altro asset non validato -> nessuna strategia generata
    assert adapt.generated_strategies_for("ETHUSDT") == []
