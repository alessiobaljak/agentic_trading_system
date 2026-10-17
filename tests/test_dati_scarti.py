"""GLI SCARTI SILENZIOSI (1 ott 2026, la cattura dei dati mancanti).

Due modi in cui un segnale valido cadeva in `decide_all` senza nessuna traccia:
l'esplorativa dietro una validata sulla stessa coin, e il secondo segnale sulla
stessa coin nello stesso giro. Ora sono contati (ciclo e 24 ore), con una riga
«[scarti]» nel log; le decisioni e i contatori dei rifiuti NON cambiano.
"""
from __future__ import annotations

import types

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.main import TradingBot, conta_ciclo
from bot.orchestrator.orchestrator import Orchestrator

NOW = 1_800_000_000.0


def _s(sym, strat, conf, esplorativa=False, direction="long"):
    return {"symbol": sym, "strategy": strat, "direction": direction, "confidence": conf,
            "adjusted_confidence": conf, "weight": 1.0, "reasoning": "", "esplorativa": esplorativa,
            "suggested_stop": 98.0, "suggested_target": 110.0, "coin_regime": None}


def _orch(monkeypatch, segnali):
    monkeypatch.setattr(settings, "TREND_TILT_ENABLED", False)
    monkeypatch.setattr(settings, "ESPLORATIVE_MAX_APERTE", 10)
    o = Orchestrator()
    o.collect_signals = lambda *a, **k: list(segnali)
    o._record_status = lambda *a, **k: None
    return o


def test_scarti_silenziosi_contati_senza_cambiare_le_decisioni(monkeypatch, capsys):
    segnali = [_s("BTCUSDT", "gen_a", 80), _s("BTCUSDT", "gen_b", 70),
               _s("BTCUSDT", "gen_esp", 75, esplorativa=True), _s("ETHUSDT", "gen_c", 60)]
    o = _orch(monkeypatch, segnali)
    decisioni = o.decide_all({}, None)
    assert [(d.asset, d.strategy) for d in decisioni] == [("BTCUSDT", "gen_a"), ("ETHUSDT", "gen_c")]
    assert o.scarti_silenziosi_ciclo() == [
        {"motivo": Orchestrator.SCARTO_DIETRO_VALIDATA, "n": 1},
        {"motivo": Orchestrator.SCARTO_SECONDO_SEGNALE, "n": 1}]
    assert o.rifiuti_ciclo() == []                    # i rifiuti di sempre non cambiano
    out = capsys.readouterr().out
    assert "[scarti] 1 esplorativa dietro una validata, 1 secondo segnale stessa coin" in out
    assert "[rifiuto]" not in out
    # il ciclo dopo riparte da zero, le 24 ore no
    o.collect_signals = lambda *a, **k: []
    o.decide_all({}, None)
    assert o.scarti_silenziosi_ciclo() == []
    assert sum(r["n"] for r in o.scarti_silenziosi_24h()) == 2
    assert o.scarti_silenziosi_24h(now=NOW * 2) == []          # fuori dalla finestra


def test_senza_scarti_nessuna_riga(monkeypatch, capsys):
    o = _orch(monkeypatch, [_s("BTCUSDT", "gen_a", 80)])
    assert len(o.decide_all({}, None)) == 1
    assert "[scarti]" not in capsys.readouterr().out


def test_gli_scarti_vanno_in_decision_status(monkeypatch):
    o = _orch(monkeypatch, [_s("BTCUSDT", "gen_a", 80), _s("BTCUSDT", "gen_b", 70)])
    o.decide_all({}, None)
    fb = FirebaseClient()
    bot = types.SimpleNamespace(orchestrator=o, fb=fb)
    o.last_status = {"outcome": "decided"}
    TradingBot._publish_decision_status(bot)
    st = fb.get_rtdb("/decision_status")
    assert st["scarti_silenziosi_ciclo"] == [{"motivo": Orchestrator.SCARTO_SECONDO_SEGNALE, "n": 1}]
    assert st["scarti_silenziosi_24h"][0]["n"] == 1
    assert "rifiuti_ciclo" in st                                  # le chiavi di sempre restano


def test_conta_ciclo_somma_nella_riga_del_giorno(monkeypatch):
    o = _orch(monkeypatch, [_s("BTCUSDT", "gen_a", 80), _s("BTCUSDT", "gen_b", 70)])
    o.decide_all({}, None)
    o.conta_scarto("cooldown dopo stop")
    bot = types.SimpleNamespace(orchestrator=o)
    conta_ciclo(bot, 1, 0, NOW)
    conta_ciclo(bot, 2, 1, NOW + 900)
    (c,) = bot._conti_giorno.values()
    assert c["decisioni"] == 3 and c["aperti"] == 1
    assert c["rifiutati"] == 2 and c["scarti_silenziosi"] == 2
    conta_ciclo(types.SimpleNamespace(), 1, 1, NOW)               # senza orchestratore: niente eccezioni
