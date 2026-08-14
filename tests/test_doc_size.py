"""IL LIMITE DI 1 MiB DI FIRESTORE — il guasto che arriva dopo quattro ore.

Il documento `strategy_params/current` porta una voce per ogni coppia valutata:
duecento coin per otto strategie sono ~1500 voci, ed era gia' a ridosso del limite.
Aggiungere cinque campi diagnostici per voce lo ha sfondato, e Firestore ha
rifiutato la scrittura con un 400 — DOPO quattro ore di validazione, portandosi via
anche la diagnosi e l'aggiornamento del registro, che venivano dopo.

Da qui tre difese, tutte verificate qui sotto: si persiste solo cio' che ha un
lettore; se non basta si tengono le coppie passate DICHIARANDOLO; e un fallimento
nel salvare i parametri non puo' piu' far cadere il processo.
"""
import json

from scripts.optimize import (PARAM_DOC_FIELDS, REGISTRY_CORE_FIELDS,
                              persist_params, slim_entries, slim_registry)


def _entry(**kw):
    base = {"symbol": "BTCUSDT", "strategy": "breakout", "params": {"a": 1},
            "oos_pf": 1.2, "oos_pnl_pct": 0.3, "oos_trades": 50, "oos_win_rate": 0.5,
            "passed": False, "holdout": {}, "regime_pf": {}, "data_end": 1.0,
            # i campi dell'autopsia: utili nel processo, inutili nel documento
            "fail_criteria": ["pf", "trades"], "fail_binding": "pf",
            "fail_shortfall": -0.05, "near_miss": False, "t_stat": 1.2}
    base.update(kw)
    return base


# ---- si persiste solo cio' che ha un lettore ------------------------------ #
def test_diagnostic_fields_are_not_persisted():
    """Servono a costruire l'aggregato, che viene calcolato nello stesso processo e
    salvato altrove. Tenerli anche qui era lo spreco che ha sfondato il limite."""
    slim = slim_entries({"A|s": _entry()}, [])
    for gone in ("fail_criteria", "fail_binding", "fail_shortfall", "near_miss",
                 "t_stat"):
        assert gone not in slim["A|s"]


def test_what_the_bot_reads_survives():
    """Il bot legge i parametri; snapshot e dashboard leggono le metriche delle
    coppie passate. Se sparissero, il documento sarebbe piccolo e inutile."""
    slim = slim_entries({"A|s": _entry()}, [])
    for kept in ("params", "symbol", "strategy", "oos_pf", "oos_trades"):
        assert kept in slim["A|s"]


def test_a_small_registry_keeps_everything():
    out = {f"C{i}USDT|s": _entry() for i in range(5)}
    assert len(slim_entries(out, [])) == 5


# ---- se non basta, si tiene il necessario e lo si DICE -------------------- #
def test_an_oversize_document_keeps_the_passed_pairs():
    out = {f"C{i}USDT|s": _entry(params={"x": "y" * 500}) for i in range(400)}
    slim = slim_entries(out, ["C1USDT|s", "C2USDT|s"], max_bytes=5_000)
    assert set(slim) == {"C1USDT|s", "C2USDT|s"}


def test_the_result_actually_fits():
    """La difesa deve funzionare, non solo esistere."""
    out = {f"C{i}USDT|s": _entry(params={"x": "y" * 500}) for i in range(400)}
    slim = slim_entries(out, ["C1USDT|s"], max_bytes=5_000)
    assert len(json.dumps(slim).encode("utf-8")) <= 5_000


# ---- il registro: la contabilita' non si tocca ---------------------------- #
def test_the_registry_is_untouched_when_it_fits():
    pairs = {"A|s": {"pass_count": 2, "symbol": "A", "holdout": {"pf": 1.5}}}
    assert json.loads(slim_registry(pairs, [])) == pairs


def test_an_oversize_registry_keeps_every_pass_count():
    """E' il dato che costa settimane di attesa: si possono perdere le metriche
    descrittive, mai i passaggi accumulati."""
    pairs = {f"C{i}|s": {"pass_count": i % 4, "symbol": f"C{i}", "strategy": "s",
                         "last_pass_data_end": 1.0, "fail_count": 0,
                         "regime_pf": {"bull": {"pf": 1.2, "trades": 40}},
                         "holdout": {"pf": 1.4, "pnl_pct": 0.2, "trades": 60}}
             for i in range(300)}
    decoded = json.loads(slim_registry(pairs, validated=["C1|s"], max_bytes=5_000))
    assert len(decoded) == 300
    for k, r in pairs.items():
        assert decoded[k]["pass_count"] == r["pass_count"]
        assert decoded[k]["last_pass_data_end"] == r["last_pass_data_end"]


def test_validated_pairs_keep_their_full_record():
    """Sono quelle che il bot opera e la dashboard mostra: alleggerirle
    romperebbe cio' che serve davvero."""
    pairs = {f"C{i}|s": {"pass_count": 3, "symbol": f"C{i}", "strategy": "s",
                         "holdout": {"pf": 1.4}, "last_pf": 1.5}
             for i in range(300)}
    decoded = json.loads(slim_registry(pairs, validated=["C7|s"], max_bytes=5_000))
    assert decoded["C7|s"]["holdout"] == {"pf": 1.4}
    assert "holdout" not in decoded["C1|s"]


def test_the_core_fields_are_declared_not_guessed():
    assert {"pass_count", "last_pass_data_end", "fail_count"} <= REGISTRY_CORE_FIELDS
    assert "params" in PARAM_DOC_FIELDS


# ---- un fallimento qui non puo' costare la validazione -------------------- #
class _BrokenFb:
    def set_doc(self, *a, **k):
        raise RuntimeError("400 The value of property \"entries\" is longer than ...")


class _OkFb:
    def __init__(self):
        self.docs = {}

    def set_doc(self, coll, doc_id, data):
        self.docs[f"{coll}/{doc_id}"] = data


def test_a_failed_write_does_not_raise():
    """E' il difetto che e' costato quattro ore: l'ULTIMO passo che fallisce e si
    porta via tutto il lavoro fatto prima."""
    assert persist_params(_BrokenFb(), {"A|s": _entry()}, []) is False


def test_a_good_write_reports_success():
    fb = _OkFb()
    assert persist_params(fb, {"A|s": _entry()}, ["A|s"]) is True
    assert "strategy_params/current" in fb.docs
