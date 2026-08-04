"""RILEVATORE DI DERIVA — l'anello che chiude paper -> gate.

Il gate promette (PF validato, TP raggiungibili) sulla storia; il paper vive il
presente. Quando il vissuto contraddice la promessa: freno immediato in produzione
e l'evidenza pesa alla passata successiva del gate come FALLIMENTO.

Il paper FALSIFICA, non ottimizza: tararci i parametri lo consumerebbe come
training set — lo stesso difetto rimosso dal gate con l'holdout.
"""
import pytest

from bot.config import settings
from bot.learning.drift import (DRIFT, OK, WATCH, compute_drift, drifted_keys,
                                weight_factor)


def _t(sym="AUSDT", strat="s1", pnl=-5.0, mfe=0.4, reason="stop_loss"):
    return {"symbol": sym, "strategy": strat, "pnl": pnl, "mfe_r": mfe,
            "exit_reason": reason}


def _pairs(pf=1.5, mults=(1.5, 3.0, 5.0)):
    return {"AUSDT|s1": {"last_pf": pf, "last_params": {"scale_r_mults": list(mults)}}}


# ---- rilevamento ---------------------------------------------------------- #
def test_drift_when_live_pf_betrays_the_promise():
    """Il gate prometteva PF 1.5, il vissuto e' 0: deriva conclamata."""
    d = compute_drift([_t() for _ in range(10)], _pairs())
    rec = d["pairs"]["AUSDT|s1"]
    assert rec["verdict"] == DRIFT
    assert "PF" in rec["reason"] and rec["trades"] == 10


def test_drift_when_tp_ladder_is_unreachable():
    """Segnale INDIPENDENTE dal PF: anche con trade in utile, se il prezzo non
    arriva mai al primo gradino la scala e' un desiderio. Basta UN numero per
    trade (mfe_r), non serve attendere esiti completi."""
    trades = [_t(pnl=+1.0, mfe=0.5) for _ in range(10)]      # in utile ma mfe 0.5R
    d = compute_drift(trades, _pairs(pf=1.2, mults=(3.0, 6.0, 9.0)))
    rec = d["pairs"]["AUSDT|s1"]
    assert rec["verdict"] == DRIFT
    assert "mfe" in rec["reason"]
    assert rec["first_rung_r"] == 3.0


def test_healthy_pair_is_ok():
    trades = [_t(pnl=+8.0, mfe=2.5) for _ in range(10)]
    d = compute_drift(trades, _pairs())
    assert d["pairs"]["AUSDT|s1"]["verdict"] == OK
    assert d["pairs"]["AUSDT|s1"]["reason"] == ""


def test_small_sample_is_watch_not_drift():
    """Con pochi trade il sospetto si VEDE ma non si AGISCE: frenare su 2 trade
    sarebbe reagire al rumore."""
    d = compute_drift([_t() for _ in range(2)], _pairs())
    assert d["pairs"]["AUSDT|s1"]["verdict"] == WATCH
    assert weight_factor(d, "AUSDT", "s1") == 1.0        # nessun freno
    assert drifted_keys(d) == []                         # nulla arriva al gate


def test_pairs_without_a_gate_promise_are_skipped():
    """Senza un atteso non c'e' niente da falsificare."""
    d = compute_drift([_t() for _ in range(10)], {})
    assert d["pairs"] == {}


def test_external_exits_are_excluded():
    """Chiusure manuali / kill switch non dicono nulla sull'edge della strategia."""
    trades = [_t(reason="manual") for _ in range(10)]
    d = compute_drift(trades, _pairs())
    assert "AUSDT|s1" not in d["pairs"]


def test_three_granularities_have_different_sample_needs():
    """Per-coppia i trade arrivano lentissimi, per strategia molto prima: la stessa
    evidenza puo' essere 'watch' sulla coppia e gia' 'drift' aggregata."""
    trades = ([_t(sym="AUSDT") for _ in range(5)] + [_t(sym="BUSDT") for _ in range(5)]
              + [_t(sym="CUSDT") for _ in range(10)])
    pairs = {f"{s}USDT|s1": {"last_pf": 1.5} for s in ("A", "B", "C")}
    d = compute_drift(trades, pairs)
    assert d["pairs"]["AUSDT|s1"]["verdict"] == WATCH        # 5 < 8
    assert d["strategies"]["s1"]["verdict"] == DRIFT         # 20 aggregati
    assert d["global"]["trades"] == 20


# ---- freno immediato in produzione ---------------------------------------- #
def test_weight_factor_brakes_but_never_kills(monkeypatch):
    """Frena, non spegne: rimuovere spetta al gate, che decide sulla storia."""
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    d = compute_drift([_t() for _ in range(10)], _pairs())
    f = weight_factor(d, "AUSDT", "s1")
    assert settings.DRIFT_WEIGHT_FLOOR <= f < 1.0


def test_pair_and_strategy_drift_compound_down_to_the_floor(monkeypatch):
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    trades = [_t() for _ in range(25)]                # coppia E strategia in deriva
    d = compute_drift(trades, _pairs())
    assert d["pairs"]["AUSDT|s1"]["verdict"] == DRIFT
    assert d["strategies"]["s1"]["verdict"] == DRIFT
    assert weight_factor(d, "AUSDT", "s1") == pytest.approx(settings.DRIFT_WEIGHT_FLOOR)


def test_drift_disabled_means_no_brake(monkeypatch):
    monkeypatch.setattr(settings, "DRIFT_ENABLED", False)
    d = compute_drift([_t() for _ in range(10)], _pairs())
    assert weight_factor(d, "AUSDT", "s1") == 1.0


def test_allocation_applies_the_brake_to_risk_and_leverage(monkeypatch):
    """Il freno arriva dove nascono size e leva, e puo' solo RIDURRE."""
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import Regime
    from bot.learning.adaptation import AdaptationEngine
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    a = AdaptationEngine(FirebaseClient())
    base_r, base_l, _ = a.allocation("s1", Regime.SIDEWAYS, 60.0)
    a._drift = compute_drift([_t() for _ in range(10)], _pairs())
    r, l, note = a.allocation("s1", Regime.SIDEWAYS, 60.0, drift_key=("AUSDT", "s1"))
    assert r < base_r and l < base_l
    assert "DERIVA" in note


# ---- anello di ritorno: l'evidenza pesa nel gate -------------------------- #
def test_drifted_pair_counts_as_a_gate_failure():
    """IL CUORE DELL'ANELLO: una coppia smentita dal vivo non accumula un pass
    nemmeno se la storia la promuove ancora — e va verso l'auto-purge."""
    from scripts.optimize import update_registry
    from bot.core.firebase_client import decode_pairs

    class FB:
        def __init__(self):
            self.docs = {("drift", "current"): {
                "pairs": {"AUSDT|s1": {"verdict": DRIFT}}}}
        def get_doc(self, c, d):
            return self.docs.get((c, d), {})
        def set_doc(self, c, d, data):
            self.docs[(c, d)] = data

    fb = FB()
    key = "AUSDT|s1"
    entry = {"symbol": "AUSDT", "strategy": "s1", "params": {}, "oos_pf": 1.5,
             "oos_pnl_pct": 0.4, "oos_trades": 40, "oos_win_rate": 0.5,
             "passed": True, "data_end": 1_700_000_000.0}
    update_registry(fb, {key: entry}, [key])          # la STORIA la promuove...
    rec = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]
    assert rec["pass_count"] == 0                     # ...ma il vivo la smentisce
    assert rec["fail_count"] == 1
    assert "drift_seen_at" in rec


def test_without_drift_the_pass_is_normal():
    """Nessuna deriva -> il percorso resta identico a prima (nessuna regressione)."""
    from scripts.optimize import update_registry
    from bot.core.firebase_client import decode_pairs

    class FB:
        def __init__(self):
            self.docs = {}
        def get_doc(self, c, d):
            return self.docs.get((c, d), {})
        def set_doc(self, c, d, data):
            self.docs[(c, d)] = data

    fb = FB()
    key = "AUSDT|s1"
    entry = {"symbol": "AUSDT", "strategy": "s1", "params": {}, "oos_pf": 1.5,
             "oos_pnl_pct": 0.4, "oos_trades": 40, "oos_win_rate": 0.5,
             "passed": True, "data_end": 1_700_000_000.0}
    update_registry(fb, {key: entry}, [key])
    rec = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]
    assert rec["pass_count"] == 1 and rec.get("fail_count", 0) == 0
