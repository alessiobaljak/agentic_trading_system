"""MODALITA' OMBRA — il modello decide, ma non opera.

Una decisione LLM non e' riproducibile, quindi non e' backtestabile: non potrebbe
mai passare dal GATE 1, e l'unico modo di sapere se aggiunge o distrugge valore
sarebbe farla girare per mesi coi soldi. L'ombra scioglie il nodo: stesso
contesto, scelta REGISTRATA accanto a quella vera, zero rischio.

L'invariante da difendere e' una sola e vale piu' di tutte le altre: il valore
prodotto qui non deve poter finire nel percorso di esecuzione, nemmeno per
distrazione. Per questo `propose_shadow` ritorna un dict grezzo e non una
OrchestratorDecision — non c'e' modo di passarlo per sbaglio all'executor.
"""
import pytest

from bot.ai import shadow
from bot.config import settings
from bot.core.models import Regime


def _sig(sym="BTCUSDT", strat="breakout", conf=60.0):
    return {"symbol": sym, "strategy": strat, "direction": "long",
            "confidence": conf, "adjusted_confidence": conf, "coin_regime": Regime.SIDEWAYS}


# ---- fail-open -------------------------------------------------------------- #
def test_no_shadow_without_a_key(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    assert shadow.propose_shadow([_sig()], Regime.SIDEWAYS) is None


def test_no_shadow_when_switched_off(monkeypatch):
    monkeypatch.setattr(settings, "AI_SHADOW_ENABLED", False)
    monkeypatch.setattr(shadow, "available", lambda: True)
    assert shadow.propose_shadow([_sig()], Regime.SIDEWAYS) is None


def test_no_shadow_without_signals(monkeypatch):
    monkeypatch.setattr(shadow, "available", lambda: True)
    assert shadow.propose_shadow([], Regime.SIDEWAYS) is None


def test_a_malformed_answer_produces_nothing(monkeypatch):
    monkeypatch.setattr(shadow, "available", lambda: True)
    monkeypatch.setattr(shadow, "ask_json", lambda *a, **k: "non un dict")
    assert shadow.propose_shadow([_sig()], Regime.SIDEWAYS) is None


# ---- il risultato e' un DATO, non una decisione ---------------------------- #
def test_the_result_cannot_be_mistaken_for_a_decision(monkeypatch):
    """Ritorna un dict grezzo apposta: una OrchestratorDecision potrebbe finire
    nell'executor per distrazione, questo no."""
    from bot.core.models import OrchestratorDecision
    monkeypatch.setattr(shadow, "available", lambda: True)
    monkeypatch.setattr(shadow, "ask_json", lambda *a, **k: {
        "scelta": "BTCUSDT|breakout", "direzione": "long", "convinzione": 70,
        "motivo": "trend netto", "rischio_principale": "ritraccia sul volume",
        "segnali_scartati": ["ETHUSDT|momentum: momentum piatto"]})
    out = shadow.propose_shadow([_sig()], Regime.SIDEWAYS)
    assert isinstance(out, dict) and not isinstance(out, OrchestratorDecision)
    assert out["choice"] == "BTCUSDT|breakout"
    assert out["primary_risk"].startswith("ritraccia")


def test_free_text_is_truncated(monkeypatch):
    """Il documento finisce su Firestore a ogni decisione: un motivo lungo
    all'infinito lo farebbe crescere senza controllo."""
    monkeypatch.setattr(shadow, "available", lambda: True)
    monkeypatch.setattr(shadow, "ask_json", lambda *a, **k: {
        "scelta": None, "motivo": "x" * 5000, "rischio_principale": "y" * 5000,
        "segnali_scartati": [f"s{i}" for i in range(50)]})
    out = shadow.propose_shadow([_sig()], Regime.SIDEWAYS)
    assert len(out["reason"]) <= 600 and len(out["primary_risk"]) <= 300
    assert len(out["rejected"]) <= 8


# ---- confronto con la scelta vera ------------------------------------------ #
def test_the_four_verdicts():
    """Quattro esiti, tutti informativi: la sola cosa che non deve succedere e'
    perderne uno per strada."""
    s = {"choice": "BTCUSDT|breakout"}
    assert shadow.compare(s, "BTCUSDT|breakout") == "agree"
    assert shadow.compare(s, "ETHUSDT|momentum") == "different_pick"
    assert shadow.compare(s, None) == "shadow_only"
    assert shadow.compare({"choice": None}, "BTCUSDT|breakout") == "shadow_veto"
    assert shadow.compare({"choice": None}, None) == "both_flat"


def test_no_shadow_is_its_own_verdict():
    """Distinguere "il modello non ha risposto" da "il modello ha scelto flat" e'
    essenziale: confonderli falserebbe la statistica sui veti."""
    assert shadow.compare(None, "BTCUSDT|breakout") == "no_shadow"


# ---- il contesto e' fattuale ------------------------------------------------ #
def test_the_context_carries_risk_and_alerts(monkeypatch):
    seen = {}
    monkeypatch.setattr(shadow, "available", lambda: True)
    monkeypatch.setattr(shadow, "ask_json",
                        lambda sysmsg, user, **k: seen.update(user=user) or None)
    shadow.propose_shadow([_sig()], Regime.SIDEWAYS,
                          risk={"open_risk_pct": 0.045, "open_positions": 9,
                                "equity": 831.0, "day_pnl": -12.3},
                          alerts=["ghost_position"],
                          recent=[{"symbol": "A", "strategy": "s", "pnl": -3.0,
                                   "exit_reason": "stop_loss"}])
    u = seen["user"]
    assert "4.50%" in u and "9 posizioni" in u
    assert "ghost_position" in u, "il modello deve sapere se il sistema e' degradato"
    assert "ULTIMI 1 TRADE" in u
