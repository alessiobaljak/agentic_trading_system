"""LIVELLO AI — le garanzie che lo rendono sicuro da avere acceso.

Due proprieta' non negoziabili, ed e' quello che questi test difendono:

1. FAIL-OPEN. Senza chiave, o con una risposta storta, il sistema deve comportarsi
   ESATTAMENTE come prima. L'AI puo' solo aggiungere ipotesi, mai togliere
   disponibilita' o candidate valide.

2. L'OUTPUT E' UN SOSPETTO. Il modello produce testo: ogni spec va ricostruita
   contro il vocabolario chiuso del generatore. Quel che non combacia si scarta,
   non si corregge — cosi' una risposta sbagliata produce MENO candidate, mai una
   spec che il motore non sa eseguire.
"""
import pytest

from bot.ai import hypotheses, universe_filter
from bot.ai.client import _extract_json
from bot.config import settings


# ---- estrazione JSON ------------------------------------------------------- #
def test_extract_json_ignores_prose_around_and_after():
    # find('{') + rfind('}') prenderebbe anche la coda: qui si bilanciano le graffe
    assert _extract_json('Ecco:\n{"a": 1}\nSpero sia utile. }') == {"a": 1}


def test_extract_json_handles_braces_inside_strings():
    assert _extract_json('{"nota": "usa } con cautela", "a": 2}')["a"] == 2


def test_extract_json_arrays_and_failure():
    assert _extract_json('[{"a": 1}]') == [{"a": 1}]
    assert _extract_json("nessun json qui") is None
    assert _extract_json('{"rotto": ') is None


# ---- validazione delle spec proposte --------------------------------------- #
def test_clean_spec_accepts_a_well_formed_proposal():
    spec = hypotheses._clean_spec({
        "mechanism": "su coin illiquide un picco di volume precede il movimento",
        "features": [{"kind": "volume_surge", "vol_mult_feat": 2.0},
                     {"kind": "stoch_momentum"}],
        "atr_mult_stop": 2.0, "rr": 2.5, "min_adx": 20.0, "volume_mult": 1.5,
    })
    assert spec is not None
    assert spec["id"].startswith("gen_")      # stessa identita' delle spec casuali
    assert spec["mechanism"].startswith("su coin illiquide")


def test_clean_spec_rejects_unknown_feature():
    # una feature inventata dal modello non deve MAI arrivare al motore
    assert hypotheses._clean_spec({
        "features": [{"kind": "sentiment_oracle"}], "atr_mult_stop": 2.0, "rr": 2.0,
    }) is None


def test_clean_spec_rejects_without_directional_feature():
    # solo condizioni: la strategia non saprebbe da che parte andare
    assert hypotheses._clean_spec({
        "features": [{"kind": "trend_strength", "adx_lo": 22.0}],
        "atr_mult_stop": 2.0, "rr": 2.0,
    }) is None


def test_clean_spec_rejects_incompatible_pair():
    # mean-reversion + breakout sullo stesso segnale: incoerente per costruzione
    assert hypotheses._clean_spec({
        "features": [{"kind": "bb_touch"}, {"kind": "bb_break"}],
        "atr_mult_stop": 2.0, "rr": 2.0,
    }) is None


def test_clean_spec_rejects_out_of_range_numbers():
    # leva/stop fuori dallo spazio validato: si scarta, non si "corregge"
    assert hypotheses._clean_spec({
        "features": [{"kind": "ema_cross"}], "atr_mult_stop": 99.0, "rr": 2.0,
    }) is None
    assert hypotheses._clean_spec({
        "features": [{"kind": "rsi_extreme", "low": 200.0, "high": 70.0}],
        "atr_mult_stop": 2.0, "rr": 2.0,
    }) is None


def test_clean_spec_rejects_missing_required_param():
    # rsi_extreme senza soglie non e' eseguibile
    assert hypotheses._clean_spec({
        "features": [{"kind": "rsi_extreme", "low": 25.0}],
        "atr_mult_stop": 2.0, "rr": 2.0,
    }) is None


def test_propose_returns_nothing_without_ai(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    assert hypotheses.propose(10) == []


def test_propose_drops_bad_specs_and_keeps_good_ones(monkeypatch):
    monkeypatch.setattr(hypotheses, "available", lambda: True)
    monkeypatch.setattr(hypotheses, "ask_json", lambda *a, **k: {"specs": [
        {"features": [{"kind": "ema_cross"}], "atr_mult_stop": 2.0, "rr": 2.0},
        {"features": [{"kind": "non_esiste"}], "atr_mult_stop": 2.0, "rr": 2.0},
        {"features": [], "atr_mult_stop": 2.0, "rr": 2.0},
    ]})
    specs = hypotheses.propose(10)
    assert len(specs) == 1 and specs[0]["features"][0]["kind"] == "ema_cross"


# ---- filtro universo: fail-open e guardia --------------------------------- #
def _metrics(n):
    return [{"symbol": f"C{i}USDT"} for i in range(n)]


def test_universe_filter_keeps_everything_without_ai(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    keep, dropped = universe_filter.filter_universe(_metrics(5))
    assert len(keep) == 5 and dropped == {}


def test_universe_filter_excludes_only_symbols_it_was_given(monkeypatch):
    monkeypatch.setattr(universe_filter, "available", lambda: True)
    monkeypatch.setattr(universe_filter, "ask_json", lambda *a, **k: {"escludi": [
        {"symbol": "C1USDT", "motivo": "listata da 40 giorni"},
        {"symbol": "INVENTATAUSDT", "motivo": "non era nella lista"},
    ]})
    keep, dropped = universe_filter.filter_universe(_metrics(10))
    assert "C1USDT" not in keep and len(keep) == 9
    assert "INVENTATAUSDT" not in dropped      # mai fidarsi di simboli non proposti


def test_universe_filter_ignores_a_mass_exclusion(monkeypatch):
    """Guardia: svuotare l'universo e' quasi sempre un fraintendimento, e il danno
    (nessuna coppia da validare) e' molto peggio del beneficio."""
    monkeypatch.setattr(universe_filter, "available", lambda: True)
    monkeypatch.setattr(universe_filter, "ask_json", lambda *a, **k: {
        "escludi": [{"symbol": f"C{i}USDT", "motivo": "x"} for i in range(9)]})
    keep, dropped = universe_filter.filter_universe(_metrics(10))
    assert len(keep) == 10 and dropped == {}


def test_universe_filter_survives_a_malformed_answer(monkeypatch):
    monkeypatch.setattr(universe_filter, "available", lambda: True)
    monkeypatch.setattr(universe_filter, "ask_json", lambda *a, **k: "non un dict")
    keep, dropped = universe_filter.filter_universe(_metrics(4))
    assert len(keep) == 4 and dropped == {}


# ---- analista: digest fattuale, e niente AI = niente report ---------------- #
def test_analyst_digest_reports_the_numbers_that_matter():
    from bot.ai.analyst import build_digest
    trades = [{"symbol": "AUSDT", "strategy": "s1", "pnl": -5.0, "mfe_r": 0.3,
               "exit_reason": "stop_loss", "scale_stage_reached": 0} for _ in range(3)]
    trades.append({"symbol": "AUSDT", "strategy": "s1", "pnl": 2.0, "mfe_r": 1.7,
                   "exit_reason": "scale_out", "scale_stage_reached": 1})
    d = build_digest(trades, {"AUSDT|s1": {"last_pf": 1.5}}, {}, {})
    assert "TRADE CHIUSI: 4" in d
    assert "stop_loss" in d and "ESCURSIONE FAVOREVOLE" in d
    assert "atteso 1.50" in d          # la promessa del gate entra nel confronto


def test_analyst_returns_none_without_ai(monkeypatch):
    from bot.ai import analyst
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    assert analyst.analyze([{"pnl": 1.0}], {}) is None


def test_analyst_returns_none_on_empty_history():
    from bot.ai import analyst
    assert analyst.analyze([], {}) is None


def test_digest_does_not_report_a_missing_promise_as_zero():
    """"atteso 0.00" sarebbe un artefatto: il gate non promette mai zero. Zero vuol
    dire coppia assente dal registro, e l'analisi non deve leggerlo come un dato."""
    from bot.ai.analyst import build_digest
    trades = [{"symbol": "AUSDT", "strategy": "s1", "pnl": -5.0, "mfe_r": 0.3,
               "exit_reason": "stop_loss"}]
    d = build_digest(trades, {}, {}, {})          # registro vuoto
    assert "atteso 0.00" not in d
    assert "NESSUNA PROMESSA" in d
    assert "0/1" in d and "ATTENZIONE" in d


def test_digest_reports_the_promise_when_the_pair_is_in_the_registry():
    from bot.ai.analyst import build_digest
    trades = [{"symbol": "AUSDT", "strategy": "s1", "pnl": -5.0, "mfe_r": 0.3,
               "exit_reason": "stop_loss"}]
    d = build_digest(trades, {"AUSDT|s1": {"last_pf": 1.51}}, {}, {})
    assert "atteso 1.51" in d and "NESSUNA PROMESSA" not in d
    assert "1/1" in d
