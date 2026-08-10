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
    # meno dati nuovi della soglia -> ancora NESSUN incremento
    from scripts.optimize import NEW_DATA_MIN_S
    update_registry(fb, {key: _entry(t0 + NEW_DATA_MIN_S * 0.5)}, [key])
    assert pc() == 1
    # oltre la soglia di dati NUOVI -> incrementa
    update_registry(fb, {key: _entry(t0 + NEW_DATA_MIN_S + 60)}, [key])
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


# ---- RECENCY: i parametri si ritarano sul presente ------------------------ #
class _TT:
    """Trade con timestamp, per i pesi di recency."""
    def __init__(self, pnl, days_ago, now=1_700_000_000.0):
        self.pnl_pct = pnl
        self.entry_ts = now - days_ago * 86400.0
        self.regime_at_entry = "x"
        self.regime = "x"


def test_recency_halves_the_weight_each_half_life(monkeypatch):
    from backtesting.engine import recency_weights
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 180.0)
    w = recency_weights([_TT(0.01, 0), _TT(0.01, 180), _TT(0.01, 360)])
    assert w[0] == pytest.approx(1.0)
    assert w[1] == pytest.approx(0.5)
    assert w[2] == pytest.approx(0.25)


def test_recency_disabled_is_uniform(monkeypatch):
    """0 = comportamento storico esatto: nessuna sorpresa se lo si spegne."""
    from backtesting.engine import recency_weights
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 0.0)
    assert recency_weights([_TT(0.01, 0), _TT(0.01, 900)]) == [1.0, 1.0]


def test_recency_ignored_without_timestamps(monkeypatch):
    """Trade senza entry_ts (storici) -> pesi uniformi, nessun crash."""
    from backtesting.engine import recency_weights
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 180.0)
    assert recency_weights([_T("x", 0.01), _T("x", 0.02)]) == [1.0, 1.0]


def test_score_prefers_params_working_NOW(monkeypatch):
    """IL PUNTO. Due parametri con lo STESSO ritorno totale: uno guadagnava nel
    2022 e ora perde, l'altro perdeva allora e ora guadagna. Senza recency erano
    indistinguibili; con recency vince quello che funziona ADESSO."""
    from backtesting.optimizer import WalkForwardOptimizer
    from backtesting.engine import StrategyStats
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 180.0)
    old_glory = StrategyStats(strategy="a")
    old_glory.trades = [_TT(+0.20, 700), _TT(-0.10, 10)]      # bello ieri, brutto oggi
    fresh = StrategyStats(strategy="b")
    fresh.trades = [_TT(-0.10, 700), _TT(+0.20, 10)]          # stesso totale, invertito
    assert sum(t.pnl_pct for t in old_glory.trades) == pytest.approx(
        sum(t.pnl_pct for t in fresh.trades))
    sc = WalkForwardOptimizer._score
    assert sc(fresh, 1) > sc(old_glory, 1)


def test_weighted_return_stays_on_the_same_scale(monkeypatch):
    """La rinormalizzazione evita che pesare premi solo chi ha piu' trade: con
    performance uniforme nel tempo, il ritorno pesato ~ quello grezzo."""
    from backtesting.engine import weighted_score_parts
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 180.0)
    trades = [_TT(0.02, d) for d in (0, 30, 60, 90, 120)]
    pnl_w, _ = weighted_score_parts(trades)
    assert pnl_w == pytest.approx(sum(t.pnl_pct for t in trades), rel=1e-9)


# ---- BLOCCO C: BE per coppia, regime, feature di condizione --------------- #
def test_breakeven_is_validated_per_pair(monkeypatch):
    """Il BE dopo TP1 non era mai stato isolato in A/B (si confronto' TP-unico vs
    scale-out-CON-BE). Protegge ma taglia i runner: ora lo decide il gate."""
    from bot.execution.exit_logic import breakeven_after_tp1, effective_param_grid
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    assert breakeven_after_tp1({"sl_to_breakeven": False}) is False
    assert breakeven_after_tp1({"sl_to_breakeven": True}) is True
    assert breakeven_after_tp1(None) is True          # assente -> default globale
    assert effective_param_grid({"rr": [1.5, 2.0]})["sl_to_breakeven"] == [True, False]


def test_position_freezes_its_breakeven_choice(monkeypatch):
    """Come la scala: congelato all'ingresso, altrimenti una passata cambierebbe
    il comportamento di un trade gia' aperto."""
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import (AssetSnapshot, Direction, EffectiveRiskParams,
                                 IndicatorSnapshot, Regime)
    from bot.execution.executor import ExecutionEngine
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    asset = AssetSnapshot(symbol="BTCUSDT", price=100.0, regime=Regime.BULL_TRENDING,
                          volume_24h=5e8,
                          indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=100.0)})
    prm = EffectiveRiskParams(leverage=3.0, risk_per_trade=0.01, notional=100.0,
                              quantity=1.0, stop_price=98.0, take_profit_price=104.0,
                              user_leverage=3, user_risk_per_trade=0.01,
                              safety_leverage_cap=5, safety_risk_cap=0.03, approved=True)
    eng.open_position(asset, "trend_following", Direction.LONG, prm, sl_to_breakeven=False)
    pos = eng.open_positions["BTCUSDT"]
    eng.update_position("BTCUSDT", 103.0)             # TP1
    assert pos.scale_stage == 1
    assert pos.stop_price == 98.0                     # NON spostato a break-even
    state = eng.fb.get_rtdb("/positions/BTCUSDT")
    assert state["sl_to_breakeven"] is False
    assert eng._position_from_state(state).sl_to_breakeven is False


def test_gate_rejects_a_pair_that_bleeds_in_one_regime(monkeypatch):
    """Una coppia poteva validarsi vivendo di UN solo regime: profitto enorme in
    trend, perdite in laterale, totale positivo -> promossa. Poi il paper la
    incontrava in laterale. Non si pretende profitto ovunque: si esige che nessun
    regime con campione sufficiente sia un buco conclamato."""
    from backtesting.engine import passes_gate, regime_ok
    monkeypatch.setattr(settings, "GATE_REGIME_MIN_PF", 0.8)
    monkeypatch.setattr(settings, "GATE_REGIME_MIN_TRADES", 10)
    good = dict(window_pnls=[0.10, 0.08, 0.12], n_trades=40, pf=1.4,
                win_rate=0.55, total_return=0.30, max_dd=0.10)
    bleeding = {"bull_trending": {"pf": 3.0, "trades": 30},
                "sideways": {"pf": 0.4, "trades": 25}}
    assert regime_ok(bleeding) is False
    assert passes_gate(**good, regime_pf=bleeding) is False
    healthy = {"bull_trending": {"pf": 1.6, "trades": 30},
               "sideways": {"pf": 1.1, "trades": 25}}
    assert passes_gate(**good, regime_pf=healthy) is True
    # campione piccolo -> non blocca; assente -> non blocca
    small = {"sideways": {"pf": 0.1, "trades": 3}}
    assert passes_gate(**good, regime_pf=small) is True
    assert passes_gate(**good) is True


def test_generator_creates_market_condition_features():
    """Il generatore era solo oscillatori sullo stesso timeframe: sapeva DOVE sta
    il prezzo, mai in che CONDIZIONE e' il mercato."""
    from bot.strategies.generator import generate_specs
    from bot.strategies.generated import FEATURE_LIBRARY
    cond = {"volatility_regime", "trend_strength", "volume_surge", "session"}
    assert cond <= set(FEATURE_LIBRARY)
    specs = generate_specs(200, seed=11)
    with_cond = [s for s in specs if any(f["kind"] in cond for f in s["features"])]
    assert 0.2 * len(specs) < len(with_cond) < 0.8 * len(specs)   # mix, non monocultura
    assert all(1 <= len(s["features"]) <= 3 for s in specs)       # tetto rispettato


def test_condition_features_return_a_valid_verdict():
    """Ogni feature deve dare (long, short) o None se i dati mancano."""
    from bot.core.models import IndicatorSnapshot
    from bot.strategies.generated import FEATURE_LIBRARY
    full = IndicatorSnapshot(timeframe="15m", close=100.0, atr=2.0, adx=25.0,
                             volume=1000.0, volume_sma=500.0)
    empty = IndicatorSnapshot(timeframe="15m", close=100.0)
    for name in ("volatility_regime", "trend_strength", "volume_surge", "session"):
        out = FEATURE_LIBRARY[name](full, 100.0, {})
        assert out is not None and len(out) == 2
        assert FEATURE_LIBRARY[name](empty, 100.0, {}) is not None or name != "session"
