"""Test del motore di strategie GENERATE: interprete, generatore, integrazione."""
from bot.core.firebase_client import FirebaseClient
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


def test_mutate_produces_valid_spec():
    parent = _rsi_spec()
    child = mutate(parent, seed=5)
    assert "id" in child and child["features"]
    assert GeneratedStrategy(child) is not None


def test_adaptation_loads_and_enables_generated():
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
