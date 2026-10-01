"""VERSIONE E IMPOSTAZIONI IN VIGORE (1 ott 2026, la cattura dei dati mancanti).

Ogni avvio scrive in RTDB `/avvii_config/{avviato_at}` commit, impronta e
interruttori (MAI le chiavi); ogni trade porta {commit, config_hash}.
"""
from __future__ import annotations

import types

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import AssetSnapshot, Direction, EffectiveRiskParams, IndicatorSnapshot, Regime
from bot.execution.executor import ExecutionEngine
from bot.learning import cattura
from bot.main import pubblica_versione, versione_trade

NOW = 1_800_000_000.0
#: pezzi di nome che dicono «segreto»: nessun interruttore li deve contenere
SEGRETI = ("KEY", "SECRET", "TOKEN", "ACCOUNT", "URL", "CHAT", "WORKSPACE", "MODEL", "PASSWORD")


def test_gli_interruttori_non_contengono_segreti():
    for nome in cattura.INTERRUTTORI + cattura.INTERRUTTORI_ENV:
        assert not any(s in nome for s in SEGRETI), nome
    valori = cattura.interruttori(settings, env={})
    # nessun valore segreto puo' finirci anche per sbaglio: i nomi delle chiavi
    # non ci sono, e quelli richiesti ci sono tutti
    for nome in ("DRY_RUN", "BACKTEST_PARITY", "ORCHESTRATOR_TIMEFRAME", "AI_VETO_ENABLED",
                 "GATE_WIN_RATE_FLOOR", "ESPLORATIVE_ENABLED", "DECLASSATA_SIZE_MULT",
                 "DRIFT_ENABLED", "MAX_OPEN_POSITIONS", "COOLDOWN_HOURS"):
        assert nome in valori, nome
    assert "BINANCE_API_KEY" not in valori and "TELEGRAM_BOT_TOKEN" not in valori
    assert valori["DRY_RUN"] is settings.DRY_RUN
    assert isinstance(valori["SCALE_OUT_R_MULTIPLES"], list)          # tuple -> lista JSON


def test_config_hash_stabile_e_sensibile():
    a = cattura.interruttori(settings, env={})
    assert cattura.config_hash(a) == cattura.config_hash(dict(a))
    assert len(cattura.config_hash(a)) == 12
    b = dict(a, COOLDOWN_HOURS=(a["COOLDOWN_HOURS"] or 0) + 1)
    assert cattura.config_hash(b) != cattura.config_hash(a)


def test_commit_fail_open(tmp_path):
    # una cartella che non e' un repo git: None, mai un'eccezione
    assert cattura.commit_corto(str(tmp_path)) is None


def test_pubblica_versione_scrive_una_volta_per_avvio():
    fb = FirebaseClient()
    bot = types.SimpleNamespace(fb=fb, _avviato_at=NOW + 0.7)
    pubblica_versione(bot)
    doc = fb.get_rtdb(f"/avvii_config/{int(NOW)}")
    assert doc["config_hash"] == bot._versione["config_hash"]
    assert doc["interruttori"]["DRY_RUN"] is settings.DRY_RUN
    assert doc["avviato_at"] == NOW + 0.7
    assert versione_trade(bot) == {"commit": doc["commit"], "config_hash": doc["config_hash"]}
    assert versione_trade(types.SimpleNamespace()) is None


def test_pubblica_versione_non_solleva():
    bot = types.SimpleNamespace(fb=None, _avviato_at=NOW)
    pubblica_versione(bot)                     # fb None -> riga di log, niente eccezione


def _asset():
    return AssetSnapshot(symbol="BTCUSDT", price=100.0, regime=Regime.BULL_TRENDING, volume_24h=5e8,
                         indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=100.0)})


def _params():
    return EffectiveRiskParams(leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=1.0,
                               stop_price=98.0, take_profit_price=110.0, user_leverage=3,
                               user_risk_per_trade=0.01, safety_leverage_cap=5,
                               safety_risk_cap=0.03, approved=True)


def test_la_versione_segue_il_trade_anche_dopo_un_riavvio(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    eng.open_position(_asset(), "s", Direction.LONG, _params(),
                      versione={"commit": "abc1234", "config_hash": "0123456789ab"})
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)          # riavvio
    pos = eng2.open_positions["BTCUSDT"]
    assert pos.versione == {"commit": "abc1234", "config_hash": "0123456789ab"}
    closed = eng2.update_position("BTCUSDT", 97.0)
    assert closed.versione == {"commit": "abc1234", "config_hash": "0123456789ab"}
