"""Test dello sharding: il merge riunisce i risultati senza perdere nulla."""
from argparse import Namespace

from bot.core.firebase_client import FirebaseClient, decode_pairs


def _entry(sym, strat, pf=1.3, pnl=0.2):
    # data_end presente come nel produttore REALE (senza, il pass onesto non conta)
    return {"symbol": sym, "strategy": strat, "params": {}, "oos_pf": pf,
            "oos_pnl_pct": pnl, "oos_trades": 40, "oos_win_rate": 0.5, "passed": True,
            "data_end": 1_700_000_000.0}


def test_optimize_merge_combines_shards():
    from scripts.optimize import _merge_shards
    fb = FirebaseClient()
    fb.set_doc("optimize_shards", "0", {
        "run_id": "", "out": {"BTCUSDT|trend_following": _entry("BTCUSDT", "trend_following")},
        "passed": ["BTCUSDT|trend_following"]})
    fb.set_doc("optimize_shards", "1", {
        "run_id": "", "out": {"ETHUSDT|breakout": _entry("ETHUSDT", "breakout")},
        "passed": ["ETHUSDT|breakout"]})
    _merge_shards(fb, Namespace(num_shards=2, reset_registry=False))

    # entrambe le coppie finiscono nel run corrente e nel registro
    # (entries e' codificato come stringa JSON per non sfondare il limite indici Firestore)
    sp = fb.get_doc("strategy_params", "current")
    assert isinstance(sp["entries"], str)
    assert set(decode_pairs(sp["entries"]).keys()) == {"BTCUSDT|trend_following", "ETHUSDT|breakout"}
    reg = fb.get_doc("strategy_registry", "validated")
    pairs = decode_pairs(reg["pairs"])
    assert "BTCUSDT|trend_following" in pairs
    assert "ETHUSDT|breakout" in pairs
    # copertura calcolata sull'intero universo coperto dagli shard (2 coin)
    assert reg["universe_size"] == 2


def test_discover_merge_combines_shards():
    from scripts.discover_strategies import _merge_discover_shards
    from bot.strategies.generated import spec_id
    fb = FirebaseClient()
    spec_a = {"features": [{"kind": "bb_touch"}], "atr_mult_stop": 1.5, "rr": 2.0}
    spec_a["id"] = spec_id(spec_a)
    spec_b = {"features": [{"kind": "macd_cross"}], "atr_mult_stop": 1.5, "rr": 2.0}
    spec_b["id"] = spec_id(spec_b)
    ka, kb = f"BTCUSDT|{spec_a['id']}", f"ETHUSDT|{spec_b['id']}"
    fb.set_doc("discover_shards", "0", {"run_id": "", "n_eval": 100,
        "passed_entries": {ka: {"symbol": "BTCUSDT", "strategy": spec_a["id"], "params": {}, "data_end": 1_700_000_000.0,
                                "spec": spec_a, "oos_pf": 1.2, "oos_pnl_pct": 0.3, "oos_trades": 40}},
        "passed_keys": [ka], "specs": {spec_a["id"]: spec_a}})
    fb.set_doc("discover_shards", "1", {"run_id": "", "n_eval": 100,
        "passed_entries": {kb: {"symbol": "ETHUSDT", "strategy": spec_b["id"], "params": {}, "data_end": 1_700_000_000.0,
                                "spec": spec_b, "oos_pf": 1.3, "oos_pnl_pct": 0.4, "oos_trades": 50}},
        "passed_keys": [kb], "specs": {spec_b["id"]: spec_b}})
    _merge_discover_shards(fb, Namespace(num_shards=2))
    specs = decode_pairs(fb.get_doc("discovered_strategies", "specs")["specs"])
    assert spec_a["id"] in specs and spec_b["id"] in specs  # spec di entrambi gli shard salvate
    reg = fb.get_doc("strategy_registry", "validated")
    pairs = decode_pairs(reg["pairs"])
    assert ka in pairs and kb in pairs
