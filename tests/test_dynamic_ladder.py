"""Scala di TP DINAMICA: tarata per coppia dal gate, congelata all'ingresso.

Perche' dinamica: R e' gia' normalizzato sulla volatilita' (R = atr_mult x ATR), quindi
la domanda non e' "quanto e' volatile la coin" ma "quanto TENDE, in unita' della sua
volatilita'". Una coin che ritraccia subito non vedra' mai 5R; una che tende lo supera.
Con una scala globale la stessa scala e' comoda per una e proibitiva per l'altra.

Perche' congelata: se la scala venisse riletta dal registro a ogni tick, una passata
dell'ottimizzatore cambierebbe i TP di un trade GIA' APERTO.
"""
import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Direction, EffectiveRiskParams, ExitReason, IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine
from bot.execution.exit_logic import (
    SCALE_LADDER_CANDIDATES, effective_param_grid, ladder_multiples, mfe_in_r,
    scale_ladder,
)


def _asset(price=100.0, atr=2.0):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING, volume_24h=5e8,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _params(qty=1.0, stop=98.0, tp=104.0):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=qty,
        stop_price=stop, take_profit_price=tp,
        user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True,
    )


@pytest.fixture
def scale_on(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)


# ---- helper puri ---------------------------------------------------------- #
def test_ladder_multiples_reads_validated_params():
    assert ladder_multiples({"scale_r_mults": [1.0, 2.0, 3.0]}) == (1.0, 2.0, 3.0)


def test_ladder_multiples_none_means_global_default():
    """Coppia non ancora ri-validata -> None -> default globale, cioe' ESATTAMENTE la
    scala con cui e' stata validata. E' cio' che rende coerente il registro misto
    durante la migrazione."""
    for bad in (None, {}, {"scale_r_mults": None}, {"scale_r_mults": []},
                {"scale_r_mults": ["x"]}):
        assert ladder_multiples(bad) is None


def test_mfe_in_r_measures_excursion_in_r_units():
    # entry 100, stop 98 -> R=2. Massimo a favore 106 -> 3R
    assert mfe_in_r(100.0, 106.0, 98.0) == 3.0
    # short: entry 100, stop 102 -> R=2. Minimo 94 -> 3R
    assert mfe_in_r(100.0, 94.0, 102.0) == 3.0
    assert mfe_in_r(100.0, 106.0, 100.0) == 0.0     # R=0 -> non calcolabile


def test_ladder_candidates_are_increasing_and_include_current_default():
    """Ogni candidata deve essere crescente (i gradini si riempiono in sequenza), e
    l'attuale 1.5/3/5 deve essere tra le candidate: cosi' una coppia per cui e' davvero
    la migliore la mantiene, e la ri-validazione non puo' peggiorarla."""
    for cand in SCALE_LADDER_CANDIDATES:
        assert list(cand) == sorted(cand)
        assert len(cand) == 3
    assert (1.5, 3.0, 5.0) in SCALE_LADDER_CANDIDATES


# ---- spazio di ricerca ---------------------------------------------------- #
def test_grid_swaps_dead_rr_for_the_ladder_under_scale_out(monkeypatch):
    """`rr` non ha effetto sotto scale-out: va SOSTITUITO, non aggiunto, altrimenti
    con --max-combos che campiona a caso la ricerca resta diluita."""
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    grid = {"adx_min": [20, 25], "rr": [1.5, 2.0, 2.5, 3.0]}
    eff = effective_param_grid(grid)
    assert "rr" not in eff
    assert eff["scale_r_mults"] == list(SCALE_LADDER_CANDIDATES)
    # stesso numero di combinazioni: e' uno scambio, non un'espansione
    assert len(eff["scale_r_mults"]) == len(grid["rr"])


def test_grid_untouched_without_scale_out(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    grid = {"adx_min": [20, 25], "rr": [1.5, 2.0]}
    assert effective_param_grid(grid) == grid


def test_grid_untouched_when_strategy_has_no_rr(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    grid = {"btc_move_threshold": [0.4, 0.6]}
    assert effective_param_grid(grid) == grid


# ---- scala per-coppia nell'executor -------------------------------------- #
def test_position_uses_its_own_ladder(scale_on):
    """Con scala (1,2,3) e R=2 i gradini sono 102/104/106, non 103/106/110."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG,
                      _params(qty=1.0, stop=98), scale_r_mults=(1.0, 2.0, 3.0))
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scale_r_mults == (1.0, 2.0, 3.0)
    # a 102 (1R) la scala corta riempie il primo gradino; quella globale no
    assert eng.update_position("BTCUSDT", 102.0) is None
    assert pos.scale_stage == 1
    assert abs(pos.stop_price - 100.0) < 1e-9        # break-even


def test_without_ladder_falls_back_to_global_default(scale_on):
    """Nessuna scala per-coppia -> comportamento IDENTICO a prima (1.5/3/5)."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    pos = eng.open_positions["BTCUSDT"]
    assert pos.scale_r_mults is None
    assert eng.update_position("BTCUSDT", 102.0) is None    # sotto 1.5R: niente
    assert pos.scale_stage == 0
    assert eng.update_position("BTCUSDT", 103.0) is None    # 1.5R: primo gradino
    assert pos.scale_stage == 1


def test_ladder_is_frozen_against_config_changes_mid_trade(scale_on, monkeypatch):
    """CRITICO. Cambiare il default globale (come farebbe una passata dell'ottimizzatore
    sul registro) NON deve spostare i TP di una posizione GIA' APERTA."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG,
                      _params(qty=1.0, stop=98), scale_r_mults=(1.0, 2.0, 3.0))
    pos = eng.open_positions["BTCUSDT"]
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (9.0, 12.0, 15.0))
    ladder = scale_ladder(pos.entry_price, pos.orig_stop, True, r_mults=pos.scale_r_mults)
    assert [round(p, 6) for p, _ in ladder] == [102.0, 104.0, 106.0]
    assert eng.update_position("BTCUSDT", 102.0) is None
    assert pos.scale_stage == 1          # riempie ancora sui livelli d'ingresso


def test_frozen_ladder_survives_restart(scale_on):
    """Dopo un riavvio la posizione deve ripartire con gli STESSI TP, non con quelli
    del registro aggiornato nel frattempo."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG,
                      _params(qty=1.0, stop=98), scale_r_mults=(1.0, 2.0, 3.0))
    state = eng.fb.get_rtdb("/positions/BTCUSDT")
    assert state["scale_r_mults"] == [1.0, 2.0, 3.0]
    assert eng._position_from_state(state).scale_r_mults == (1.0, 2.0, 3.0)


def test_tp_ladder_published_uses_the_frozen_ladder(scale_on):
    """La dashboard deve mostrare i gradini della coppia, non quelli globali."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG,
                      _params(qty=1.0, stop=98), scale_r_mults=(1.0, 2.0, 3.0))
    eng.update_position("BTCUSDT", 100.5)
    published = eng.fb.get_rtdb("/positions/BTCUSDT")["tp_ladder"]
    assert [round(x["price"], 6) for x in published] == [102.0, 104.0, 106.0]


# ---- misura dell'escursione sul trade chiuso ----------------------------- #
def test_closed_trade_records_mfe_in_r(scale_on):
    """Il trade chiuso porta quanto lontano e' arrivato il prezzo, in R: e' il dato
    da cui si decide se una scala e' raggiungibile per quella coppia."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=1.0, stop=98))
    eng.update_position("BTCUSDT", 103.0)            # tocca 1.5R -> high_water 103
    closed = eng.update_position("BTCUSDT", 100.0)   # torna a BE
    assert closed is not None
    assert closed.mfe_r == 1.5                       # e' arrivato a 1.5R


def test_mfe_r_records_the_peak_not_the_exit(scale_on):
    """Deve registrare il MASSIMO raggiunto, non il prezzo di uscita: e' l'unica cosa
    che dice quali gradini un'altra scala AVREBBE colpito."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "breakout", Direction.LONG, _params(qty=1.0, stop=98))
    eng.update_position("BTCUSDT", 103.0)
    eng.update_position("BTCUSDT", 105.0)            # picco a 2.5R
    closed = eng.update_position("BTCUSDT", 100.0)
    assert closed is not None
    assert closed.mfe_r == 2.5


# ---- lato GATE: la scala per-coppia e la misura arrivano nel motore ------- #
def _synthetic_candles():
    from datetime import datetime, timezone
    from backtesting.data_loader import _synthetic
    return _synthetic(datetime(2023, 1, 1, tzinfo=timezone.utc),
                      datetime(2023, 3, 1, tzinfo=timezone.utc))


def _run(strategy_params, monkeypatch):
    from backtesting.engine import Backtester
    import bot.strategies  # noqa: F401  (registra le strategie)
    from bot.strategies.base import STRATEGY_REGISTRY
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    cls = STRATEGY_REGISTRY["momentum"]
    bt = Backtester(window=50)
    return bt.run_strategy(cls(strategy_params), "BTCUSDT", _synthetic_candles())


def test_engine_records_mfe_r_on_every_trade(monkeypatch):
    """Il gate deve registrare l'escursione in R: e' il dato su cui si decide la scala,
    e va raccolto sulle centinaia di trade storici, non solo sui pochi trade paper."""
    stats = _run({}, monkeypatch)
    if not stats.trades:
        pytest.skip("i dati sintetici non hanno generato trade")
    assert all(t.mfe_r >= 0 for t in stats.trades)
    assert any(t.mfe_r > 0 for t in stats.trades)


def test_engine_uses_the_per_pair_ladder_from_params(monkeypatch):
    """Cambiando la scala nei params della strategia il RISULTATO deve cambiare:
    e' la prova che il gate sta validando davvero la scala per-coppia."""
    short = _run({"scale_r_mults": (0.5, 1.0, 1.5)}, monkeypatch)
    long_ = _run({"scale_r_mults": (3.0, 6.0, 9.0)}, monkeypatch)
    if not short.trades or not long_.trades:
        pytest.skip("i dati sintetici non hanno generato trade")
    tot_short = sum(t.pnl_pct for t in short.trades)
    tot_long = sum(t.pnl_pct for t in long_.trades)
    assert tot_short != tot_long
