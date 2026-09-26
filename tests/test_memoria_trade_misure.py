"""LE MISURE MANCANTI SUL TRADE (26 set 2026, audit della memoria del trade).

Solo misure, nessuna decisione: ogni trade chiuso porta con se' quanto e' andato
CONTRO (MAE), quando ha colpito il primo gradino, le fette chiuse, i fattori di
size, il portafoglio all'ingresso, la candela del segnale e la latenza; dopo uno
stop, il controfattuale «rumore o inversione». E tre correzioni di parita' col
timeframe per la prima coppia validata a 1h: orizzonte massimo, cooldown e
finestra dei verdetti in BARRE del timeframe della STRATEGIA, non del bot.
"""
from __future__ import annotations

import json
import time
import types
from datetime import datetime, timedelta, timezone

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Candle, ClosedTrade, Direction, EffectiveRiskParams, ExitReason,
    IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine, Position
from bot.main import (TradingBot, chiavi_aperte, fattore_timeframe, fattori_size,
                      portafoglio_ingresso, verdetto_post_stop)

NOW = 1_800_000_000.0


def _asset(price=100.0, atr=2.0, symbol="BTCUSDT"):
    return AssetSnapshot(
        symbol=symbol, price=price, regime=Regime.BULL_TRENDING, volume_24h=5e8,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _params(qty=1.0, stop=98.0, tp=110.0, risk_eff=0.0123):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, risk_effective_pct=risk_eff,
        notional=100.0, quantity=qty, stop_price=stop, take_profit_price=tp,
        user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True,
        notes=["alloc: convinzione x1.00", "Size ridotta per alta volatilità (3.0σ)"],
    )


def _engine(fb=None):
    return ExecutionEngine(firebase=fb or FirebaseClient(), dry_run=True)


@pytest.fixture
def classico(monkeypatch):
    """TP unico (scale-out spento), profit-lock spento: i tick fanno solo misura."""
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", False)


@pytest.fixture
def scala(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_FRACTIONS", (0.3, 0.3, 0.4))
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", False)


# --------------------------------------------------------------------------- #
# 1) MAE: low_water e mae_r                                                    #
# --------------------------------------------------------------------------- #
def test_low_water_e_mae_r_su_un_long(classico):
    eng = _engine()
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110))
    pos = eng.open_positions["BTCUSDT"]
    assert pos.low_water == 100.0                      # parte dall'entry, come high_water
    assert eng.update_position("BTCUSDT", 100.0, high=101.0, low=99.0) is None
    assert pos.low_water == 99.0 and pos.high_water == 101.0
    assert eng.update_position("BTCUSDT", 100.0, high=100.5, low=99.5) is None
    assert pos.low_water == 99.0                       # non risale mai
    closed = eng.update_position("BTCUSDT", 111.0, high=111.0, low=110.0)
    assert closed is not None and closed.exit_reason == ExitReason.TAKE_PROFIT
    assert closed.mae_r == pytest.approx(0.5)          # |100-99| / |100-98|
    assert closed.mfe_r == pytest.approx(0.5)          # high_water 101 dei tick precedenti


def test_low_water_e_mae_r_su_uno_short(classico):
    eng = _engine()
    eng.open_position(_asset(100), "s", Direction.SHORT, _params(stop=102, tp=90))
    pos = eng.open_positions["BTCUSDT"]
    eng.update_position("BTCUSDT", 100.0, high=101.0, low=99.5)
    assert pos.low_water == 101.0                      # per uno short il «contro» e' l'alto
    closed = eng.update_position("BTCUSDT", 89.0, high=90.0, low=89.0)
    assert closed.mae_r == pytest.approx(0.5)


def test_mae_r_none_senza_stop_originale():
    pos = Position(position_id="x", symbol="BTCUSDT", strategy="s", direction=Direction.LONG,
                   entry_price=100.0, quantity=1.0, leverage=1.0, stop_price=0.0,
                   take_profit_price=110.0, entry_time=datetime.now(timezone.utc),
                   regime_at_entry=Regime.SIDEWAYS)
    pos.low_water = 95.0
    assert ExecutionEngine._mae_r(pos) is None


# --------------------------------------------------------------------------- #
# 2) tempi: t_tp1, t_mfe, bars_held  — 3) fette e break-even                   #
# --------------------------------------------------------------------------- #
def test_t_mfe_si_muove_solo_quando_high_water_migliora(classico):
    eng = _engine()
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110))
    pos = eng.open_positions["BTCUSDT"]
    assert pos.t_mfe is None
    t0 = time.time()
    eng.update_position("BTCUSDT", 100.0, high=101.0, low=99.5)
    assert pos.t_mfe is not None and pos.t_mfe >= t0
    prima = pos.t_mfe
    time.sleep(0.01)
    eng.update_position("BTCUSDT", 100.0, high=100.5, low=99.5)   # nessun nuovo massimo
    assert pos.t_mfe == prima


def test_prima_fetta_be_e_barre_tenute(scala):
    eng = _engine()
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110),
                      sl_to_breakeven=True, timeframe="15m")
    pos = eng.open_positions["BTCUSDT"]
    pos.entry_time = datetime.now(timezone.utc) - timedelta(hours=2)
    assert pos.t_tp1 is None and pos.be_at is None and pos.partial_fills == []
    assert eng.update_position("BTCUSDT", 103.0, high=103.0, low=100.0) is None   # TP1 = 1.5R
    assert pos.t_tp1 is not None and pos.be_at is not None
    assert len(pos.partial_fills) == 1
    f = pos.partial_fills[0]
    assert f["stage"] == 1 and f["price"] == 103.0 and f["qty"] == pytest.approx(0.3)
    assert f["ts"] == pos.t_tp1 and isinstance(f["net"], float)
    be_prima = pos.be_at
    eng.update_position("BTCUSDT", 102.0, high=102.5, low=101.0)   # niente di nuovo
    assert pos.be_at == be_prima                                   # il BE si data una volta
    closed = eng.update_position("BTCUSDT", 99.5, high=100.5, low=99.5)   # stop a pareggio
    assert closed.exit_reason == ExitReason.SCALE_OUT
    assert closed.t_tp1_s is not None and closed.t_tp1_s >= 2 * 3600 - 5
    assert closed.be_at_s == closed.t_tp1_s
    assert closed.t_mfe_s is not None
    assert closed.bars_held == pytest.approx(8.0, abs=0.05)       # 2h / 15m
    assert closed.partial_fills == pos.partial_fills


def test_barre_tenute_nel_timeframe_della_strategia(classico):
    eng = _engine()
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110), timeframe="1h")
    pos = eng.open_positions["BTCUSDT"]
    pos.entry_time = datetime.now(timezone.utc) - timedelta(hours=2)
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.bars_held == pytest.approx(2.0, abs=0.05)       # 2h / 1h
    assert closed.t_tp1_s is None and closed.be_at_s is None      # mai successi
    assert closed.partial_fills == []


# --------------------------------------------------------------------------- #
# 4) fattori di size, rischio effettivo  — 5) portafoglio  — 6) candela        #
# --------------------------------------------------------------------------- #
def test_fattori_size_e_un_dizionario_json_safe():
    d = types.SimpleNamespace(size_multiplier=0.8, confidence=61.0, adjusted_confidence=None)
    out = fattori_size(d, 0.75, 0.9, "alloc: convinzione x0.9 · FRENO x0.5 (deriva)",
                       _params(), tilt_sentiment=0.7, f_esplorativa=0.25)
    assert out["risk_mult"] == 0.75 and out["lev_mult"] == 0.9
    assert "FRENO" in out["alloc_note"]
    assert out["tilt_sentiment"] == 0.7 and out["esplorativa"] == 0.25
    assert out["size_multiplier"] == 0.8 and out["confidence"] == 61.0
    assert out["risk_per_trade"] == 0.01 and len(out["risk_notes"]) == 2
    json.dumps(out)
    assert fattori_size(d, "non un numero", 1.0, "", _params()) is None   # fail-open


def test_portafoglio_ingresso_conta_e_fail_open():
    ex = types.SimpleNamespace(open_positions={
        "A": types.SimpleNamespace(risk_effective_pct=0.01, direction=Direction.LONG),
        "B": types.SimpleNamespace(risk_effective_pct=0.02, direction=Direction.SHORT),
    })
    cb = types.SimpleNamespace(day_pnl_pct=-0.004)
    out = portafoglio_ingresso(ex, cb, Direction.LONG)
    assert out == {"posizioni_aperte": 2, "rischio_aperto_pct": pytest.approx(0.03),
                   "stessa_direzione": 1, "pnl_giorno": -0.004}
    vuoto = portafoglio_ingresso(None, None, Direction.LONG)
    assert vuoto["posizioni_aperte"] == 0 and vuoto["pnl_giorno"] is None


def _bot_try_open(monkeypatch):
    """TradingBot minimo per `_try_open` (stesso schema di test_paper_esplorativo)."""
    monkeypatch.setattr(settings, "RISK_PER_COIN_DAY", 0.0)
    monkeypatch.setattr(settings, "BACKTEST_PARITY", True)
    monkeypatch.setattr(settings, "AI_VETO_ENABLED", False)
    monkeypatch.setattr(settings, "SENTIMENT_TILT_ENABLED", False)
    b = types.SimpleNamespace()
    b.visto = {}
    params = _params()

    def open_position(asset, strategy, direction, params, **kw):
        b.visto["open"] = kw
        return types.SimpleNamespace(symbol=asset.symbol, strategy=strategy, direction=direction,
                                     entry_price=asset.price, quantity=1.0, leverage=2.0,
                                     stop_price=98.0, take_profit_price=110.0, position_id="p1")

    b.executor = types.SimpleNamespace(
        open_positions={"ETHUSDT": types.SimpleNamespace(risk_effective_pct=0.02,
                                                         direction=Direction.LONG)},
        open_position=open_position)
    b.circuit_breakers = types.SimpleNamespace(day_pnl_pct=0.011)
    b._coin_cooldown = {}
    b._used_margin = lambda: 0.0
    b.account_equity = lambda: 1000.0
    b.selected = {"BTCUSDT": _asset()}
    b._last_shadow = None
    b._correlation_blocks = lambda sym: None
    b.sentiment = types.SimpleNamespace(get_sentiment=lambda s: {})
    b.read_user_risk = lambda: None
    b.adaptation = types.SimpleNamespace(
        allocation=lambda *a, **k: (0.9, 1.1, "alloc: convinzione x0.9 · learning neutro"),
        params_for=lambda s: {}, timeframe_for=lambda s: None)
    b.risk = types.SimpleNamespace(evaluate=lambda *a, **k: params)
    b._volatility_sigma = lambda a: 0.0
    b.regime = Regime.SIDEWAYS
    b.regime_confidence = 0.8
    b._directional_risk_blocks = lambda d, r: None
    b._ombra_selettore = lambda *a, **k: (None, None)
    b._sync_stream_symbols = lambda: None
    b.stream = None
    b._publish_decision_status = lambda *a, **k: None
    b.notifier = types.SimpleNamespace(trade_opened=lambda *a, **k: None)
    b.orchestrator = types.SimpleNamespace(conta_scarto=lambda *a, **k: None)
    b.fattore_size_esplorativa = TradingBot.fattore_size_esplorativa
    b._try_open = types.MethodType(TradingBot._try_open, b)
    return b


def _decision():
    from bot.core.models import OrchestratorDecision
    return OrchestratorDecision(asset="BTCUSDT", strategy="gen_x", direction=Direction.LONG,
                                size_multiplier=1.0, confidence=60.0)


def test_try_open_passa_fattori_portafoglio_e_candela(monkeypatch):
    b = _bot_try_open(monkeypatch)
    pos = b._try_open(_decision(), NOW, signal_candle_ts=NOW - 7.0)
    assert pos is not None and pos.position_id == "p1"            # ora ritorna la posizione
    kw = b.visto["open"]
    assert kw["signal_candle_ts"] == NOW - 7.0
    sf = kw["size_factors"]
    assert sf["risk_mult"] == 0.9 and sf["lev_mult"] == 1.1 and "learning" in sf["alloc_note"]
    assert sf["esplorativa"] == 1.0 and sf["tilt_sentiment"] is None
    pf = kw["portafoglio_at_entry"]
    assert pf == {"posizioni_aperte": 1, "rischio_aperto_pct": 0.02,
                  "stessa_direzione": 1, "pnl_giorno": 0.011}


def test_try_open_senza_circuit_breakers_resta_fail_open(monkeypatch):
    b = _bot_try_open(monkeypatch)
    del b.circuit_breakers
    assert b._try_open(_decision(), NOW) is not None
    assert b.visto["open"]["portafoglio_at_entry"]["pnl_giorno"] is None
    assert b.visto["open"]["signal_candle_ts"] is None


def test_il_trade_chiuso_porta_fattori_rischio_portafoglio_e_latenza(classico):
    eng = _engine()
    t_segnale = time.time() - 12.0
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110, risk_eff=0.0123),
                      size_factors={"risk_mult": 0.9}, portafoglio_at_entry={"posizioni_aperte": 3},
                      signal_candle_ts=t_segnale)
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.size_factors_at_entry == {"risk_mult": 0.9}
    assert closed.risk_effective_pct == pytest.approx(0.0123)
    assert closed.portafoglio_at_entry == {"posizioni_aperte": 3}
    assert closed.signal_candle_ts == t_segnale
    assert 11.5 <= closed.latenza_s <= 15.0
    json.dumps(closed.model_dump(mode="json"))                      # JSON-safe


def test_trade_senza_misure_ha_none_e_liste_vuote(classico):
    eng = _engine()
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110))
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.size_factors_at_entry is None and closed.portafoglio_at_entry is None
    assert closed.signal_candle_ts is None and closed.latenza_s is None
    assert closed.partial_fills == [] and closed.t_tp1_s is None
    # i trade storici (documenti senza le chiavi) restano leggibili
    doc = closed.model_dump(mode="json")
    for k in ("mae_r", "t_tp1_s", "bars_held", "partial_fills", "be_at_s",
              "size_factors_at_entry", "portafoglio_at_entry", "latenza_s"):
        doc.pop(k)
    vecchio = ClosedTrade(**doc)
    assert vecchio.mae_r is None and vecchio.partial_fills == []


# --------------------------------------------------------------------------- #
# 7) controfattuale dopo uno STOP: rumore / inversione, finestra a 1h          #
# --------------------------------------------------------------------------- #
def _c(ts: float, high: float, low: float) -> Candle:
    return Candle(open_time=datetime.fromtimestamp(ts, tz=timezone.utc),
                  open=(high + low) / 2, high=high, low=low, close=(high + low) / 2, volume=1.0)


def test_verdetto_post_stop_rumore_e_inversione():
    # long: entry 100, stop 98 (R=2), primo gradino 103, «un altro R contro» = 96
    rumore = [_c(1, 99.0, 98.2), _c(2, 101.0, 99.0), _c(3, 103.5, 101.0), _c(4, 104.0, 95.0)]
    r = verdetto_post_stop(rumore, 100.0, 98.0, 103.0, True)
    assert r["verdict"] == "rumore" and r["post_stop_mfe_r"] == pytest.approx(2.0)
    inversione = [_c(1, 99.0, 97.0), _c(2, 97.5, 95.9), _c(3, 104.0, 96.0)]
    r = verdetto_post_stop(inversione, 100.0, 98.0, 103.0, True)
    assert r["verdict"] == "inversione" and r["post_stop_mfe_r"] == pytest.approx(2.0)
    # stessa candela: il peggio (come il motore); mai tornato sopra l'entry: mfe negativa
    stessa = [_c(1, 103.0, 96.0)]
    assert verdetto_post_stop(stessa, 100.0, 98.0, 103.0, True)["verdict"] == "inversione"
    r = verdetto_post_stop([_c(1, 99.0, 97.5), _c(2, 99.5, 98.0)], 100.0, 98.0, 103.0, True)
    assert r["verdict"] is None and r["post_stop_mfe_r"] == pytest.approx(-0.25)
    # short: entry 100, stop 102, primo gradino 97, «contro» = 104
    r = verdetto_post_stop([_c(1, 102.5, 101.0), _c(2, 101.0, 96.9)], 100.0, 102.0, 97.0, False)
    assert r["verdict"] == "rumore" and r["post_stop_mfe_r"] == pytest.approx(1.55)
    assert verdetto_post_stop([], 100.0, 100.0, 103.0, True) == {"verdict": None, "post_stop_mfe_r": None}


def _bot_verdetti(trade: dict, candles: list):
    """TradingBot minimo per evaluate_pending_trailing: un trade e le sue candele."""
    b = types.SimpleNamespace()
    b.visto = {}
    b.logger = types.SimpleNamespace(recent=lambda limit=100: [trade])

    def get_candles(symbol, interval, limit=200):
        b.visto["interval"], b.visto["limit"] = interval, limit
        return candles
    b.price = types.SimpleNamespace(get_candles=get_candles)
    b.fb = types.SimpleNamespace(set_doc=lambda coll, tid, doc: b.visto.__setitem__("doc", dict(doc)))
    b.evaluate_pending_trailing = types.MethodType(TradingBot.evaluate_pending_trailing, b)
    return b


def _stop_trade(tf: str, ex: float) -> dict:
    return {"trade_id": "t1", "symbol": "XUSDT", "exit_reason": "stop_loss", "direction": "long",
            "timeframe": tf, "entry_price": 100.0, "exit_price": 98.0, "orig_stop": 98.0,
            "stop_price": 98.0, "take_profit_price": 110.0, "tp_prices": [103.0, 106.0, 110.0],
            "exit_ts": ex, "duration_seconds": 3600.0}


def test_post_stop_a_1h_usa_le_candele_1h_e_una_finestra_di_96_barre():
    ex = NOW
    # torna al primo gradino 50 ore dopo lo stop: dentro le 96 barre di un trade a 1h
    candles = [_c(ex - 3600, 100.5, 99.0), _c(ex, 99.0, 97.9), _c(ex + 3600, 100.0, 98.5),
               _c(ex + 50 * 3600, 103.2, 100.0)]
    b = _bot_verdetti(_stop_trade("1h", ex), candles)
    b.evaluate_pending_trailing(ex + 60 * 3600)
    assert b.visto["interval"] == "1h"
    assert b.visto["limit"] >= 96 + 8                       # almeno l'orizzonte del gate
    doc = b.visto["doc"]
    assert doc["post_stop_verdict"] == "rumore" and doc["post_stop_mfe_r"] == pytest.approx(1.6)
    assert "trailing_verdict" not in doc


def test_post_stop_a_15m_la_stessa_candela_e_fuori_finestra():
    ex = NOW
    candles = [_c(ex - 900, 100.5, 99.0), _c(ex, 99.0, 97.9), _c(ex + 900, 100.0, 98.5),
               _c(ex + 50 * 3600, 103.2, 100.0)]
    b = _bot_verdetti(_stop_trade("15m", ex), candles)
    b.evaluate_pending_trailing(ex + 60 * 3600)
    assert b.visto["interval"] == "15m"
    # finestra 24h: la candela a +50h non conta; a finestra piena senza gradino
    # ne' un altro R contro -> «inversione» (non e' tornato in tempo)
    assert b.visto["doc"]["post_stop_verdict"] == "inversione"


def test_post_stop_inversione_e_definitiva_e_l_indeciso_aspetta():
    ex = NOW
    b = _bot_verdetti(_stop_trade("15m", ex),
                      [_c(ex, 99.0, 97.9), _c(ex + 900, 98.0, 95.8), _c(ex + 1800, 99.0, 98.0)])
    b.evaluate_pending_trailing(ex + 3600)                  # finestra NON piena
    assert b.visto["doc"]["post_stop_verdict"] == "inversione"
    b2 = _bot_verdetti(_stop_trade("15m", ex),
                       [_c(ex, 99.0, 97.9), _c(ex + 900, 99.5, 98.5), _c(ex + 1800, 100.0, 99.0)])
    b2.evaluate_pending_trailing(ex + 3600)
    assert "doc" not in b2.visto                             # indeciso: si riprova dopo
    gia = _stop_trade("15m", ex); gia["post_stop_verdict"] = "rumore"
    b3 = _bot_verdetti(gia, [])
    b3.evaluate_pending_trailing(ex + 3600)
    assert "interval" not in b3.visto                        # gia' giudicato: nessuna lettura


def test_il_trailing_usa_il_timeframe_del_trade():
    ex = NOW
    t = _stop_trade("1h", ex); t["exit_reason"] = "trailing_stop"; t["exit_price"] = 104.0
    candles = [_c(ex - 3600, 105.0, 99.0), _c(ex, 104.5, 103.9), _c(ex + 3600, 106.0, 103.0),
               _c(ex + 40 * 3600, 110.5, 105.0)]   # TP a +40h: dentro 96h, fuori 24h
    b = _bot_verdetti(t, candles)
    b.evaluate_pending_trailing(ex + 41 * 3600)
    assert b.visto["interval"] == "1h"
    assert b.visto["doc"]["trailing_verdict"] == "premature"


# --------------------------------------------------------------------------- #
# 8) l'ombra registra TUTTE le aperture del ciclo                              #
# --------------------------------------------------------------------------- #
def test_chiavi_aperte_lista_e_id():
    aperte = [types.SimpleNamespace(symbol="BTCUSDT", strategy="a", position_id="1"),
              types.SimpleNamespace(symbol="ETHUSDT", strategy="b", position_id="2")]
    assert chiavi_aperte([], aperte) == (["BTCUSDT|a", "ETHUSDT|b"], ["1", "2"])
    dec = [types.SimpleNamespace(asset="SOLUSDT", strategy="c")]
    assert chiavi_aperte(dec, None) == (["SOLUSDT|c"], [])   # legacy


def test_record_shadow_scrive_actual_all_e_trade_ids(monkeypatch):
    import bot.ai.shadow as shadow_mod
    monkeypatch.setattr(settings, "AI_SHADOW_ENABLED", True)
    monkeypatch.setattr(shadow_mod, "propose_shadow",
                        lambda *a, **k: {"choice": "ETHUSDT|b", "reason": "x", "rejected": []})
    b = types.SimpleNamespace()
    b.visto = {}
    b.orchestrator = types.SimpleNamespace(collect_signals=lambda *a, **k: [1])
    b.selected, b.regime = {}, Regime.SIDEWAYS
    b.executor = types.SimpleNamespace(open_positions={})
    b.account_equity = lambda: 1000.0
    b.circuit_breakers = types.SimpleNamespace(day_pnl_pct=0.0)
    b.reconciler = types.SimpleNamespace(findings=[])
    b.logger = types.SimpleNamespace(recent=lambda n: [])
    b.fb = types.SimpleNamespace(set_doc=lambda c, i, d: b.visto.__setitem__("doc", d))
    b._record_shadow = types.MethodType(TradingBot._record_shadow, b)
    dec = [types.SimpleNamespace(asset="BTCUSDT", strategy="a"),
           types.SimpleNamespace(asset="ETHUSDT", strategy="b")]
    aperte = [types.SimpleNamespace(symbol="BTCUSDT", strategy="a", position_id="1"),
              types.SimpleNamespace(symbol="ETHUSDT", strategy="b", position_id="2")]
    b._record_shadow(dec, NOW, aperte=aperte)
    doc = b.visto["doc"]
    assert doc["actual"] == "BTCUSDT|a"                       # stringa: compatibilita'
    assert doc["actual_all"] == ["BTCUSDT|a", "ETHUSDT|b"] and doc["trade_ids"] == ["1", "2"]
    assert doc["verdict"] == "agree"                          # la scelta e' fra le aperte
    b._record_shadow(dec, NOW, aperte=[])
    assert b.visto["doc"]["actual"] is None and b.visto["doc"]["verdict"] == "shadow_only"


# --------------------------------------------------------------------------- #
# 9) parita' 1h: orizzonte massimo e cooldown in barre della STRATEGIA         #
# --------------------------------------------------------------------------- #
def test_max_hold_per_timeframe_della_posizione(classico):
    eng = _engine()
    eng.open_position(_asset(100), "s", Direction.LONG, _params(), timeframe="15m")
    eng.open_position(_asset(100, symbol="ETHUSDT"), "s", Direction.LONG, _params(), timeframe="1h")
    p15, p1h = eng.open_positions["BTCUSDT"], eng.open_positions["ETHUSDT"]
    assert eng._max_hold_for(p15) == pytest.approx(24.0)
    assert eng._max_hold_for(p1h) == pytest.approx(96.0)
    p15.timeframe = None
    assert eng._max_hold_for(p15) == pytest.approx(24.0)      # None = timeframe del bot
    # a 30 ore: la 15m e' fuori orizzonte, la 1h no
    p15.entry_time = p1h.entry_time = datetime.now(timezone.utc) - timedelta(hours=30)
    assert eng.update_position("BTCUSDT", 100.5).exit_reason == ExitReason.TIME_EXIT
    assert eng.update_position("ETHUSDT", 100.5) is None
    p1h.entry_time = datetime.now(timezone.utc) - timedelta(hours=97)
    assert eng.update_position("ETHUSDT", 100.5).exit_reason == ExitReason.TIME_EXIT


def test_max_hold_dall_env_vale_per_tutte(classico):
    eng = _engine()
    eng.max_hold_hours, eng._max_hold_from_env = 10.0, True
    eng.open_position(_asset(100), "s", Direction.LONG, _params(), timeframe="1h")
    assert eng._max_hold_for(eng.open_positions["BTCUSDT"]) == 10.0


def test_fattore_timeframe():
    assert fattore_timeframe("15m") == 1.0
    assert fattore_timeframe(None) == 1.0
    assert fattore_timeframe("1h") == 4.0
    assert fattore_timeframe("4h") == 16.0


def _closed(tf: str) -> ClosedTrade:
    now = datetime.now(timezone.utc)
    return ClosedTrade(trade_id="t", symbol="XUSDT", strategy="s", direction=Direction.LONG,
                       timeframe=tf, entry_time=now, exit_time=now, entry_price=100.0,
                       exit_price=98.0, size=1.0, notional=100.0, leverage=1.0, pnl=-2.0,
                       pnl_pct=-0.02, exit_reason=ExitReason.STOP_LOSS,
                       regime_at_entry=Regime.SIDEWAYS)


def _bot_ciclo(monkeypatch, closed: ClosedTrade):
    """TradingBot minimo per il punto (1) di trading_cycle: una posizione che
    si chiude allo stop. Dopo il giro delle posizioni il ciclo si ferma."""
    monkeypatch.setattr(settings, "STRATEGY_LOSS_STREAK", 1)
    b = types.SimpleNamespace()
    b.executor = types.SimpleNamespace(
        open_positions={"XUSDT": types.SimpleNamespace(entry_price=100.0)},
        update_position=lambda *a, **k: closed)
    b.price = types.SimpleNamespace(get_mark_price=lambda s: 99.0)
    b._price_path = lambda s, p: []
    b._wick_range = lambda s, p: (None, None)
    b._sync_stream_symbols = lambda: None
    b._settle_realized = lambda: None
    b.account_equity = lambda: 1000.0
    b._log_closed = lambda c: None
    b.notifier = types.SimpleNamespace(trade_closed=lambda *a, **k: None)
    b._coin_cooldown, b._strat_cooldown, b._strat_streak = {}, {}, {}
    b._save_adapt_state = lambda: None
    b.circuit_breakers = types.SimpleNamespace(register_trade_result=lambda *a, **k: None)
    b._persist_risk_state = lambda: None
    b.fb = types.SimpleNamespace(get_rtdb=lambda p: None)
    b._stream_recovery_guard = lambda now: True           # ferma il ciclo dopo il punto (1)
    b._publish_decision_status = lambda *a, **k: None
    b.trading_cycle = types.MethodType(TradingBot.trading_cycle, b)
    return b


def test_cooldown_dopo_stop_in_barre_del_timeframe_della_strategia(monkeypatch):
    b = _bot_ciclo(monkeypatch, _closed("1h"))
    b.trading_cycle(NOW)
    assert b._coin_cooldown["XUSDT"] == pytest.approx(NOW + settings.COOLDOWN_HOURS * 3600 * 4)
    assert b._strat_cooldown["s"] == pytest.approx(NOW + settings.STRATEGY_COOLDOWN_HOURS * 3600 * 4)
    b15 = _bot_ciclo(monkeypatch, _closed("15m"))
    b15.trading_cycle(NOW)
    assert b15._coin_cooldown["XUSDT"] == pytest.approx(NOW + settings.COOLDOWN_HOURS * 3600)
    assert b15._strat_cooldown["s"] == pytest.approx(NOW + settings.STRATEGY_COOLDOWN_HOURS * 3600)


# --------------------------------------------------------------------------- #
# 10) persistenza: scrittura, riavvio, documenti vecchi, JSON                  #
# --------------------------------------------------------------------------- #
def test_le_misure_sopravvivono_al_riavvio(scala):
    fb = FirebaseClient()
    eng = _engine(fb)
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110),
                      sl_to_breakeven=True, timeframe="15m",
                      size_factors={"risk_mult": 0.9, "alloc_note": "n"},
                      portafoglio_at_entry={"posizioni_aperte": 2}, signal_candle_ts=NOW)
    eng.update_position("BTCUSDT", 100.0, high=101.0, low=99.0)
    eng.update_position("BTCUSDT", 103.0, high=103.0, low=102.0)   # TP1 + BE
    pos = eng.open_positions["BTCUSDT"]
    doc = fb.get_rtdb("/positions/BTCUSDT")
    json.dumps(doc)                                               # JSON-safe
    assert doc["low_water"] == 99.0 and doc["partial_fills"] == pos.partial_fills
    assert doc["t_tp1"] == pos.t_tp1 and doc["t_mfe"] == pos.t_mfe and doc["be_at"] == pos.be_at
    assert doc["size_factors"] == {"risk_mult": 0.9, "alloc_note": "n"}
    assert doc["portafoglio_at_entry"] == {"posizioni_aperte": 2}
    assert doc["signal_candle_ts"] == NOW
    eng2 = _engine(fb)                                            # riavvio
    r = eng2.open_positions["BTCUSDT"]
    for k in ("low_water", "t_tp1", "t_mfe", "be_at", "partial_fills", "size_factors",
              "portafoglio_at_entry", "signal_candle_ts", "high_water"):
        assert getattr(r, k) == getattr(pos, k), k
    closed = eng2.update_position("BTCUSDT", 99.5, high=100.5, low=99.5)
    assert closed.mae_r == pytest.approx(0.5) and len(closed.partial_fills) == 1
    assert closed.size_factors_at_entry == {"risk_mult": 0.9, "alloc_note": "n"}
    assert closed.latenza_s == pytest.approx(pos.entry_time.timestamp() - NOW, abs=1e-3)


def test_un_documento_vecchio_ripristina_i_default():
    eng = _engine()
    p = eng._position_from_state({
        "symbol": "BTCUSDT", "direction": "long", "entry_price": 100.0, "quantity": 1.0,
        "stop_price": 98.0, "take_profit_price": 110.0, "entry_time": "2026-09-20T00:00:00+00:00",
    })
    assert p.low_water == 100.0 and p.t_tp1 is None and p.t_mfe is None and p.be_at is None
    assert p.partial_fills == [] and p.size_factors is None
    assert p.portafoglio_at_entry is None and p.signal_candle_ts is None


# --------------------------------------------------------------------------- #
# il motore del gate: la stessa misura sui trade simulati                      #
# --------------------------------------------------------------------------- #
def test_simtrade_espone_mae_r():
    from backtesting.engine import SimTrade
    t = SimTrade(strategy="s", regime="sideways", direction="long", entry_price=100.0,
                 exit_price=104.0, pnl_pct=0.04, max_adverse_pct=0.01, confidence=60.0,
                 is_win=True, pnl=4.0, symbol="BTCUSDT", mae_r=0.5)
    d = t.as_trade_dict()
    assert d["mae_r"] == 0.5 and d["feats"] == {}
