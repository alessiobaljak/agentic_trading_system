"""CALIBRAZIONE DELLA CONFIDENZA — quel numero predice davvero l'esito?

`allocation()` modula size e leva sulla confidenza del segnale, ma nessuno lo
aveva mai verificato: se la confidenza fosse rumore, staremmo dimensionando le
posizioni su una cifra senza significato, e con convinzione.

La risposta a una confidenza che non predice e' RIDURRE la sua influenza verso il
neutro — non invertirla: scommettere contro un segnale che anti-predice su pochi
trade e' adattarsi al rumore con un altro nome.
"""
import pytest

from bot.config import settings
from bot.learning.calibration import (CONSTANT, FLAT, INSUFFICIENT, INVERTED,
                                      OK, calibrate, confidence_buckets,
                                      confidence_trust)


def _t(conf, pnl, reason="stop_loss"):
    return {"confidence_at_entry": conf, "pnl_pct": pnl, "exit_reason": reason}


def _many(pairs, repeat=1):
    return [_t(c, p) for c, p in pairs for _ in range(repeat)]


# ---- rilevamento ---------------------------------------------------------- #
def test_calibrated_confidence_is_ok(monkeypatch):
    """Confidenza alta -> esiti migliori: il numero ordina correttamente."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    trades = _many([(30, -0.02), (40, -0.01), (60, 0.01), (80, 0.03)], repeat=4)
    out = calibrate(trades)
    assert out["verdict"] == OK
    assert out["trust"] == 1.0
    assert out["correlation"] > 0


def test_uncorrelated_confidence_is_flat_and_damped(monkeypatch):
    """Nessuna relazione: l'influenza si riduce, non sparisce."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    # stessa distribuzione di esiti in ogni fascia di confidenza
    trades = _many([(30, 0.02), (30, -0.02), (60, 0.02), (60, -0.02),
                    (85, 0.02), (85, -0.02)], repeat=3)
    out = calibrate(trades)
    assert out["verdict"] == FLAT
    assert out["trust"] == settings.CALIBRATION_FLAT_TRUST


def test_inverted_confidence_stops_influencing_size(monkeypatch):
    """Se ANTI-predice, la confidenza smette di contare. Non si inverte: sarebbe
    scommettere sul rumore in direzione opposta."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    trades = _many([(30, 0.03), (45, 0.01), (65, -0.01), (85, -0.03)], repeat=4)
    out = calibrate(trades)
    assert out["verdict"] == INVERTED
    assert out["trust"] == 0.0


def test_small_sample_changes_nothing(monkeypatch):
    """Sotto il campione minimo NON si tocca nulla: agire su pochi trade sarebbe
    l'errore che stiamo cercando di evitare."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 30)
    out = calibrate(_many([(30, -0.02), (85, 0.03)], repeat=3))
    assert out["verdict"] == INSUFFICIENT
    assert out["trust"] == 1.0
    assert confidence_trust(out) == 1.0


def test_external_exits_excluded(monkeypatch):
    """Chiusure manuali e kill switch non dicono nulla sulla qualita' del segnale."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 5)
    trades = [_t(85, -0.05, "manual") for _ in range(20)]
    assert calibrate(trades)["verdict"] == INSUFFICIENT     # tutti scartati


# ---- fasce ---------------------------------------------------------------- #
def test_buckets_split_by_confidence_and_show_expectancy():
    pairs = [(30.0, -0.02), (35.0, -0.01), (60.0, 0.0),
             (65.0, 0.01), (80.0, 0.02), (85.0, 0.03)]
    b = confidence_buckets(pairs, n_buckets=3)
    assert len(b) == 3
    assert b[0]["conf_max"] <= b[1]["conf_min"]           # fasce ordinate
    assert b[-1]["expectancy"] > b[0]["expectancy"]       # esito che cresce
    assert sum(x["trades"] for x in b) == len(pairs)      # nessun trade perso


def test_buckets_empty_with_too_few_trades():
    assert confidence_buckets([(50.0, 0.01)], n_buckets=3) == []


# ---- effetto su size e leva ----------------------------------------------- #
def test_trust_shrinks_the_confidence_multiplier_toward_neutral(monkeypatch):
    """Il punto pratico: con trust basso, un segnale ad alta confidenza non
    ottiene piu' size maggiorata."""
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import Regime
    from bot.learning.adaptation import AdaptationEngine
    monkeypatch.setattr(settings, "CALIBRATION_ENABLED", True)
    a = AdaptationEngine(FirebaseClient())

    a._calibration = {"trust": 1.0}
    full_r, full_l, _ = a.allocation("s1", Regime.SIDEWAYS, 85.0)
    a._calibration = {"trust": 0.0}
    none_r, none_l, note = a.allocation("s1", Regime.SIDEWAYS, 85.0)

    assert none_r < full_r and none_l < full_l     # niente bonus da confidenza alta
    assert "calibr." in note

    # e con confidenza BASSA il trust=0 toglie anche la penalita': neutro davvero
    a._calibration = {"trust": 1.0}
    low_full, _, _ = a.allocation("s1", Regime.SIDEWAYS, 30.0)
    a._calibration = {"trust": 0.0}
    low_none, _, _ = a.allocation("s1", Regime.SIDEWAYS, 30.0)
    assert low_none > low_full


def test_disabled_leaves_allocation_untouched(monkeypatch):
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import Regime
    from bot.learning.adaptation import AdaptationEngine
    monkeypatch.setattr(settings, "CALIBRATION_ENABLED", False)
    a = AdaptationEngine(FirebaseClient())
    a._calibration = {"trust": 0.0}
    r, l, note = a.allocation("s1", Regime.SIDEWAYS, 85.0)
    assert "calibr." not in note
    assert confidence_trust({"trust": 0.0}) == 1.0


def test_trust_survives_garbage():
    assert confidence_trust(None) == 1.0
    assert confidence_trust({}) == 1.0
    assert confidence_trust({"trust": "boh"}) == 1.0
    assert confidence_trust({"trust": 5.0}) == 1.0        # clampato


# ---- confidenza che non varia: niente da calibrare (25 set 2026) ---------- #
def test_constant_confidence_cannot_be_calibrated(monkeypatch):
    """Tutte le strategie generate escono a confidenza fissa 60. Con un solo
    valore i terzili non sono fasce di confidenza e il verdetto e' un artefatto:
    qui deve dire «costante», non fingere una misura."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    trades = _many([(60, 0.02), (60, -0.01), (60, 0.03), (60, -0.02)], repeat=5)
    out = calibrate(trades)
    assert out["verdict"] == CONSTANT
    assert out["trust"] == 1.0                      # nessuna influenza sulla size
    assert out["correlation"] is None               # non c'e' correlazione con un solo x
    assert "confidenza 60" in out["note"] and "non varia" in out["note"]
    assert confidence_trust(out) == 1.0


def test_constant_verdict_does_not_depend_on_trade_order(monkeypatch):
    """L'ARTEFATTO DEL 23-25 SETTEMBRE. Con confidenza costante `sorted` e'
    stabile: la «fascia alta» sono gli ULTIMI trade. Stessi trade in ordine
    inverso davano «ok» invece di «flat» senza che nulla fosse cambiato.
    Ora l'ordine non conta."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    perdite_prima = [_t(60, -0.02) for _ in range(6)] + [_t(60, 0.03) for _ in range(6)]
    vincite_prima = list(reversed(perdite_prima))
    assert calibrate(perdite_prima)["verdict"] == CONSTANT
    assert calibrate(vincite_prima)["verdict"] == CONSTANT


def test_range_below_one_point_counts_as_constant(monkeypatch):
    """60 e 60,5 non sono due fasce: nessuna differenza di size ne esce."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    trades = _many([(60, 0.02), (60.5, -0.02), (60.2, 0.01)], repeat=4)
    assert calibrate(trades)["verdict"] == CONSTANT


def test_constant_wins_over_small_sample(monkeypatch):
    """«Servono 30 trade» promette che con piu' trade si misurera' qualcosa:
    con la confidenza fissa non e' vero. La costanza va detta subito."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 30)
    out = calibrate(_many([(60, 0.01), (60, -0.01)], repeat=3))
    assert out["verdict"] == CONSTANT
    assert out["trust"] == 1.0


def test_fewer_than_two_trades_is_still_insufficient(monkeypatch):
    """Con un trade il range non e' definito: vale il verdetto di sempre."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 30)
    assert calibrate([_t(60, 0.01)])["verdict"] == INSUFFICIENT
    assert calibrate([])["verdict"] == INSUFFICIENT


def test_constant_note_does_not_blame_generated_for_other_values(monkeypatch):
    """La frase sulle strategie generate e' vera solo per il 60: con un altro
    valore costante si dice solo la costanza."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 5)
    note = calibrate(_many([(75, 0.01), (75, -0.01)], repeat=4))["note"]
    assert "costante (75)" in note and "generate" not in note


def test_variable_confidence_keeps_the_old_verdicts(monkeypatch):
    """Appena la confidenza varia, la calibrazione torna a misurare come prima:
    il verdetto «costante» non deve mai coprire un caso misurabile."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    ok = _many([(30, -0.02), (40, -0.01), (60, 0.01), (80, 0.03)], repeat=4)
    flat = _many([(30, 0.02), (30, -0.02), (60, 0.02), (60, -0.02),
                  (85, 0.02), (85, -0.02)], repeat=3)
    inv = _many([(30, 0.03), (45, 0.01), (65, -0.01), (85, -0.03)], repeat=4)
    assert calibrate(ok)["verdict"] == OK
    assert calibrate(flat)["verdict"] == FLAT
    assert calibrate(inv)["verdict"] == INVERTED
    for trades in (ok, flat, inv):
        assert calibrate(trades)["verdict"] != CONSTANT


def test_constant_verdict_leaves_allocation_untouched(monkeypatch):
    """Il punto pratico: col verdetto «costante» il bot dimensiona ESATTAMENTE
    come senza calibrazione. Non c'e' evidenza, quindi non si devia."""
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import Regime
    from bot.learning.adaptation import AdaptationEngine
    monkeypatch.setattr(settings, "CALIBRATION_ENABLED", True)
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    a = AdaptationEngine(FirebaseClient())

    a._calibration = {}
    senza = a.allocation("s1", Regime.SIDEWAYS, 60.0)
    a._calibration = calibrate(_many([(60, 0.02), (60, -0.01)], repeat=8))
    assert a._calibration["verdict"] == CONSTANT
    con = a.allocation("s1", Regime.SIDEWAYS, 60.0)
    assert con == senza
    assert "calibr." not in con[2]
