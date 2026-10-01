"""LA PROMESSA DEL GATE CONGELATA ALL'INGRESSO (1 ott 2026, cattura dei dati).

Il registro si riscrive a ogni giro: il trade porta con se' cosa il gate
prometteva per la coppia quando e' stato aperto (`promessa_gate`), presa dal
registro GIA' in memoria (nessuna lettura in piu').
"""
from __future__ import annotations

from bot.config import settings
from bot.core.firebase_client import FirebaseClient, encode_pairs
from bot.learning import cattura
from bot.learning.adaptation import AdaptationEngine
from bot.main import promessa_della_decisione
from tests.test_memoria_trade_misure import NOW, _bot_try_open, _decision


def test_promessa_gate_pura():
    rec = {"pass_count": 4, "fail_count": 1, "last_pf": 1.61234, "last_win_rate": 0.52,
           "last_t": 2.345, "val_t": 2.1, "validated_at": NOW - 86400, "declassata": True,
           "last_params": {"scale_r_mults": [1, 2, 3]}, "regime_pf": {"x": 1}}
    p = cattura.promessa_gate(rec, spec={"origine": "referto"}, generata=True)
    assert p["pass_count"] == 4 and p["fail_count"] == 1
    assert p["last_pf"] == 1.6123 and p["last_t"] == 2.345 and p["val_t"] == 2.1
    assert p["declassata"] is True and p["origine"] == "varianti"
    assert "last_params" not in p and "regime_pf" not in p          # compatta
    assert cattura.promessa_gate(None) is None
    base = cattura.promessa_gate({"pass_count": 2}, generata=False)
    assert base["origine"] == "base"
    esp = cattura.promessa_gate(None, esplorativa_rec={"pf": 1.1, "trades": 30, "shortfall": -0.05,
                                                       "binding": "pf", "since": NOW})
    assert esp["esplorativa_pf"] == 1.1 and esp["esplorativa_binding"] == "pf"
    assert esp["origine"] == "spec_ignota"                          # spec non passata
    assert cattura.promessa_gate("non un dict") is None


def test_l_adattamento_tiene_la_promessa_dal_registro_gia_letto(monkeypatch):
    monkeypatch.setattr(settings, "REQUIRE_GATE1_READY", False)
    fb = FirebaseClient()
    pairs = {"BTCUSDT|gen_a": {"pass_count": 3, "fail_count": 0, "last_pf": 1.4,
                               "last_win_rate": 0.5, "generated": True,
                               "last_params": {"profit_lock_keep": 0.5}},
             "ETHUSDT|gen_b": {"pass_count": 1, "last_pf": 1.2}}
    fb.set_doc("strategy_registry", "validated",
               {"pairs": encode_pairs(pairs), "validated": ["BTCUSDT|gen_a"], "ready": True})
    fb.set_doc("discovered_strategies", "specs",
               {"specs": encode_pairs({"gen_a": {"id": "gen_a", "mechanism": "x"}})})
    a = AdaptationEngine(fb)
    p = a.promessa_per("BTCUSDT", "gen_a")
    assert p["pass_count"] == 3 and p["last_pf"] == 1.4 and p["origine"] == "ai"
    assert a.promessa_per("ETHUSDT", "gen_b") is None              # non validata: niente
    assert a.promessa_per("XUSDT", "gen_zz") is None
    # in RAM solo i campi della promessa, non il record intero
    assert "last_params" not in a._promesse["BTCUSDT|gen_a"]


def test_promessa_della_decisione_fail_open():
    class Rotto:
        def promessa_per(self, *a):
            raise RuntimeError("giu'")
    assert promessa_della_decisione(Rotto(), _decision()) is None
    assert promessa_della_decisione(object(), _decision()) is None


def test_try_open_passa_promessa_versione_e_regime_globale(monkeypatch):
    b = _bot_try_open(monkeypatch)
    b.adaptation.promessa_per = lambda s, st: {"pass_count": 5, "origine": "casuali"}
    b._versione = {"commit": "abc1234", "config_hash": "0123456789ab", "interruttori": {}}
    pos = b._try_open(_decision(), NOW, signal_candle_ts=NOW - 7.0)
    assert pos is not None
    kw = b.visto["open"]
    assert kw["promessa_gate"] == {"pass_count": 5, "origine": "casuali"}
    assert kw["versione"] == {"commit": "abc1234", "config_hash": "0123456789ab"}
    assert kw["regime_globale"] == b.regime


def test_try_open_senza_promessa_ne_versione_apre_lo_stesso(monkeypatch):
    b = _bot_try_open(monkeypatch)            # adattamento finto senza promessa_per
    assert b._try_open(_decision(), NOW) is not None
    assert b.visto["open"]["promessa_gate"] is None and b.visto["open"]["versione"] is None
