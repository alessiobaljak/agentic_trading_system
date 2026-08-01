"""Riforma del GATE 1 — i tre difetti che gonfiavano la validazione.

1) HOLDOUT mai riusato: le finestre OOS erano deterministiche e IDENTICHE a ogni
   run; migliaia di candidate selezionate su di esse -> l'OOS era diventato un
   training set. Ora gli ultimi GATE_HOLDOUT_DAYS sono invisibili alla selezione e
   una coppia passa solo se regge anche li', coi parametri spedibili.
2) PASS ONESTO: pass_count contava rivalutazioni degli stessi dati. Ora incrementa
   solo con >= OPTIMIZER_NEW_DATA_MIN_HOURS di dati nuovi dall'ultimo pass.
3) FILTRO DI REGIME: il gate conosce il PF per-regime dai suoi trade OOS; ora lo
   esporta e il bot non opera una coppia nel regime in cui il gate l'ha vista
   perdere (fail-open senza dati).
"""
import time

import pytest

from bot.config import settings
from backtesting.engine import pf_by_regime
from backtesting.optimizer import WalkForwardOptimizer


class _T:
    """Trade simulato minimo per pf_by_regime."""

    def __init__(self, regime, pnl):
        self.regime_at_entry = regime
        self.regime = regime
        self.pnl_pct = pnl


# ---- 3) PF per regime + veto ---------------------------------------------- #
def test_pf_by_regime_segments_correctly():
    trades = [_T("sideways", -0.02), _T("sideways", -0.01), _T("sideways", 0.01),
              _T("bull_trending", 0.05), _T("bull_trending", -0.01)]
    out = pf_by_regime(trades)
    assert out["sideways"]["trades"] == 3
    assert out["sideways"]["pf"] == pytest.approx(0.01 / 0.03, abs=1e-3)   # arrotondato a 3 decimali
    assert out["bull_trending"]["pf"] == pytest.approx(5.0)


def _adapt(regime_pf: dict):
    from bot.core.firebase_client import FirebaseClient
    from bot.learning.adaptation import AdaptationEngine
    a = AdaptationEngine(FirebaseClient())
    a._has_opt_data = True
    a._passed = {"XUSDT|s1"}
    a._regime_pf = {"XUSDT|s1": regime_pf}
    return a


def test_regime_veto_blocks_where_gate_saw_losses(monkeypatch):
    monkeypatch.setattr(settings, "REGIME_FILTER_ENABLED", True)
    a = _adapt({"sideways": {"pf": 0.7, "trades": 40},
                "bull_trending": {"pf": 1.8, "trades": 60}})
    from bot.core.models import Regime
    assert a.regime_ok("XUSDT", "s1", Regime.SIDEWAYS) is False      # perde: veto
    assert a.regime_ok("XUSDT", "s1", Regime.BULL_TRENDING) is True  # vince: ok


def test_regime_veto_fails_open_without_data(monkeypatch):
    """Coppia non ancora ri-validata / regime mai visto / campione piccolo -> MAI
    bloccare: il filtro morde solo dove il gate ha visto abbastanza."""
    monkeypatch.setattr(settings, "REGIME_FILTER_ENABLED", True)
    from bot.core.models import Regime
    assert _adapt({}).regime_ok("XUSDT", "s1", Regime.SIDEWAYS) is True
    assert _adapt({"bull_trending": {"pf": 2.0, "trades": 50}}) \
        .regime_ok("XUSDT", "s1", Regime.SIDEWAYS) is True
    few = _adapt({"sideways": {"pf": 0.2, "trades": settings.GATE_REGIME_MIN_TRADES - 1}})
    assert few.regime_ok("XUSDT", "s1", Regime.SIDEWAYS) is True
    assert _adapt({"sideways": "garbage"}).regime_ok("XUSDT", "s1", Regime.SIDEWAYS) is True


def test_regime_veto_disabled_by_flag(monkeypatch):
    monkeypatch.setattr(settings, "REGIME_FILTER_ENABLED", False)
    from bot.core.models import Regime
    a = _adapt({"sideways": {"pf": 0.1, "trades": 100}})
    assert a.regime_ok("XUSDT", "s1", Regime.SIDEWAYS) is True


# ---- 1) holdout ------------------------------------------------------------ #
def test_selection_never_sees_the_holdout(monkeypatch):
    monkeypatch.setattr(settings, "GATE_HOLDOUT_DAYS", 45.0)
    opt = WalkForwardOptimizer(interval="15m")
    assert opt.holdout_bars == int(45 * 24 * 4)          # 45 giorni in barre 15m
    candles = list(range(30000))                          # finti: servono solo len/slice
    body, cut = opt.split_holdout(candles)
    assert len(body) == 30000 - opt.holdout_bars
    assert cut == len(body)
    # le finestre della selezione stanno TUTTE dentro il corpo
    for (ta, tb, sa, sb) in opt._windows(len(body)):
        assert sb <= len(body)


def test_holdout_zero_days_restores_old_behaviour(monkeypatch):
    monkeypatch.setattr(settings, "GATE_HOLDOUT_DAYS", 0.0)
    opt = WalkForwardOptimizer(interval="15m")
    candles = list(range(1000))
    body, cut = opt.split_holdout(candles)
    assert body is candles and cut == len(candles)


def test_short_history_means_no_holdout_split(monkeypatch):
    """Meno candele dell'holdout: niente taglio (la coin resta valutabile; il
    requisito di storia minima la gestisce a monte)."""
    monkeypatch.setattr(settings, "GATE_HOLDOUT_DAYS", 45.0)
    opt = WalkForwardOptimizer(interval="15m")
    candles = list(range(100))
    body, cut = opt.split_holdout(candles)
    assert body is candles and cut == len(candles)


# ---- 2) pass onesto -------------------------------------------------------- #
def _fake_fb_with_registry(initial=None):
    class FB:
        def __init__(self):
            self.docs = {("strategy_registry", "validated"): initial or {}}
        def get_doc(self, c, d):
            return self.docs.get((c, d), {})
        def set_doc(self, c, d, data):
            self.docs[(c, d)] = data
    return FB()


def _entry(data_end):
    return {"symbol": "XUSDT", "strategy": "s1", "params": {"a": 1},
            "oos_pf": 1.5, "oos_pnl_pct": 0.5, "oos_trades": 40,
            "oos_win_rate": 0.5, "passed": True, "trailing": {},
            "holdout": {"pf": 1.2, "trades": 8, "ok": True},
            "regime_pf": {"sideways": {"pf": 1.1, "trades": 20}},
            "data_end": data_end}


def test_pass_count_needs_new_data():
    """Rivalutare gli STESSI dati non incrementa: MIN_PASSES deve significare
    'confermata su dati diversi', non 'valutata piu' volte'."""
    from scripts.optimize import update_registry
    fb = _fake_fb_with_registry()
    t0 = time.time()
    key = "XUSDT|s1"
    reg = update_registry(fb, {key: _entry(t0)}, [key])
    assert reg["pairs"] if isinstance(reg.get("pairs"), dict) else True
    from bot.core.firebase_client import decode_pairs
    pc = lambda: decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]["pass_count"]
    assert pc() == 1
    # stesso data_end (stessi dati) -> NESSUN incremento
    update_registry(fb, {key: _entry(t0)}, [key])
    assert pc() == 1
    # 2 giorni di dati nuovi -> incrementa
    update_registry(fb, {key: _entry(t0 + 2 * 86400)}, [key])
    assert pc() == 2


def test_registry_stores_holdout_and_regime_pf():
    from scripts.optimize import update_registry
    from bot.core.firebase_client import decode_pairs
    fb = _fake_fb_with_registry()
    key = "XUSDT|s1"
    update_registry(fb, {key: _entry(time.time())}, [key])
    rec = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]
    assert rec["holdout"]["ok"] is True
    assert rec["regime_pf"]["sideways"]["trades"] == 20


# ---- CONTINUITA': recovery factor e drawdown ------------------------------ #
def test_max_drawdown_measures_the_hole():
    from backtesting.engine import max_drawdown
    # curva: +10, -4, -4, +8  -> picco a 10, fondo a 2 -> buca 8
    assert max_drawdown([_T("x", v) for v in (0.10, -0.04, -0.04, 0.08)]) == pytest.approx(0.08)
    assert max_drawdown([]) == 0.0
    # monotona crescente: nessuna buca
    assert max_drawdown([_T("x", v) for v in (0.05, 0.05)]) == 0.0


def test_gate_rejects_deep_holes_even_if_profitable(monkeypatch):
    """Il cuore dell'obiettivo 'profitto continuo': stesso ritorno, stessa
    consistenza per finestra, ma una curva che scava una buca profonda meta'
    del guadagno NON passa (recovery < 2)."""
    from backtesting.engine import passes_gate
    monkeypatch.setattr(settings, "GATE_MIN_RECOVERY", 2.0)
    good = dict(window_pnls=[0.10, 0.08, 0.12], n_trades=40, pf=1.4,
                win_rate=0.55, total_return=0.30)
    assert passes_gate(**good, max_dd=0.10) is True     # 0.30/0.10 = 3 >= 2
    assert passes_gate(**good, max_dd=0.20) is False    # 0.30/0.20 = 1.5 < 2
    assert passes_gate(**good, max_dd=0.0) is True      # nessuna buca
    assert passes_gate(**good) is True                  # senza dd: invariato (compat)


def test_gate_accepts_low_win_rate_if_curve_is_smooth(monkeypatch):
    """Il committente accetta WR 'apparentemente basso' se il profitto e'
    continuo: con recovery alto e PF alto, il WR al floor passa — e' il PF/DD
    a decidere, non la frequenza di vincita."""
    from backtesting.engine import passes_gate
    monkeypatch.setattr(settings, "GATE_MIN_RECOVERY", 2.0)
    runner = dict(window_pnls=[0.15, 0.12, 0.18], n_trades=60, pf=1.6,
                  win_rate=settings.GATE_WIN_RATE_FLOOR,   # esattamente al floor
                  total_return=0.45)
    assert passes_gate(**runner, max_dd=0.12) is True


def test_score_prefers_smooth_curve_over_volatile_same_return():
    """A parita' di ritorno, la grid search deve scegliere i parametri con la
    curva piu' regolare (prima vinceva il ritorno grezzo)."""
    from backtesting.engine import StrategyStats
    from backtesting.optimizer import WalkForwardOptimizer
    smooth = StrategyStats(strategy="s")
    smooth.trades = [_T("x", v) for v in (0.05, 0.05, 0.05, 0.05)]       # 0.20, dd 0
    volatile = StrategyStats(strategy="v")
    volatile.trades = [_T("x", v) for v in (0.30, -0.25, 0.30, -0.15)]   # 0.20, dd 0.25+
    sc = WalkForwardOptimizer._score
    assert sc(smooth, 1) > sc(volatile, 1)


def test_pass_count_fail_closed_without_data_end():
    """Un percorso che DIMENTICA data_end non deve poter incrementare: era il buco
    da cui i run sharded gonfiavano pass_count (coppie 'validate' in un giorno)."""
    from scripts.optimize import update_registry
    from bot.core.firebase_client import decode_pairs
    fb = _fake_fb_with_registry()
    key = "XUSDT|s1"
    e = _entry(0)                      # data_end mancante/azzerato
    update_registry(fb, {key: e}, [key])
    update_registry(fb, {key: e}, [key])
    rec = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]
    assert rec["pass_count"] == 0      # mai incrementato senza dati datati


def test_generated_ladder_survives_last_params_assignment():
    """REGRESSIONE: last_params veniva assegnato DOPO aver innestato la scala e la
    cancellava -> le generate sarebbero tornate mute sulla scala globale."""
    from scripts.discover_strategies import merge_into_registry
    from bot.core.firebase_client import FirebaseClient, decode_pairs
    fb = FirebaseClient()
    key = "BTCUSDT|gen_zzz"
    out = {key: {"symbol": "BTCUSDT", "strategy": "gen_zzz", "params": {"a": 1},
                 "oos_pf": 1.4, "oos_pnl_pct": 0.3, "oos_trades": 40,
                 "oos_win_rate": 0.5, "passed": True,
                 "scale_r_mults": [1.0, 2.0, 3.0], "data_end": 1_700_000_000.0}}
    merge_into_registry(fb, out, passed_now=[key])
    lp = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]["last_params"]
    assert lp["scale_r_mults"] == [1.0, 2.0, 3.0]
    assert lp["a"] == 1        # i params originali non si perdono
