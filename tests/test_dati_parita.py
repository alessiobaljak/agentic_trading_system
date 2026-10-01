"""LA CATTURA NON CAMBIA NIENTE (1 ott 2026, la cattura dei dati mancanti).

La regola della richiesta: si aggiungono dati, nessuna decisione cambia. Qui due
prove con numeri FISSATI PRIMA della modifica (calcolati il 1 ott 2026 col
codice del commit precedente, `git show HEAD:...`, su questi stessi dati):
  * il motore del gate (`backtesting/engine.py`, che da oggi etichetta
    `exit_reason` su ogni SimTrade) da' gli stessi trade, lo stesso PnL, le
    stesse barre, gli stessi verdetti trailing e lo stesso verdetto del gate su
    una serie sintetica fissa, con e senza scale-out;
  * l'executor del paper (che da oggi annota versione, promessa, ingresso,
    percorso dello stop) chiude gli stessi trade scritti a mano allo stesso
    prezzo, per lo stesso motivo, con lo stesso PnL e gli stessi accrediti.
Se uno di questi numeri cambia, la cattura ha toccato una decisione.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backtesting.data_loader import _synthetic
from backtesting.engine import Backtester
from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (AssetSnapshot, Direction, EffectiveRiskParams, ExitReason,
                             IndicatorSnapshot, Regime)
from bot.execution.executor import ExecutionEngine

# --------------------------------------------------------------------------- #
# 1) il motore                                                                 #
# --------------------------------------------------------------------------- #
#: per strategia: [trade, somma pnl_pct, somma barre, verdetti trailing], col
#: motore PRIMA dell'etichetta (commit precedente al 1 ott 2026)
MOTORE_PRIMA = {
    0: {"breakout": [4, -0.012396464, 16, 2], "funding_arbitrage": [0, 0, 0, 0],
        "grid_trading": [101, -0.081079173, 235, 28], "liquidity_grab": [0, 0, 0, 0],
        "mean_reversion": [0, 0, 0, 0], "momentum": [81, 0.15378513, 487, 30],
        "momentum_cross_asset": [0, 0, 0, 0], "trend_following": [97, 0.17352859, 611, 35],
        "vwap_reversion": [132, -0.046698033, 939, 42]},
    1: {"breakout": [4, -0.011816339, 15, 2], "funding_arbitrage": [0, 0, 0, 0],
        "grid_trading": [76, 0.08943248, 361, 38], "liquidity_grab": [0, 0, 0, 0],
        "mean_reversion": [0, 0, 0, 0], "momentum": [74, 0.140481994, 515, 41],
        "momentum_cross_asset": [0, 0, 0, 0], "trend_following": [98, 0.293692379, 647, 62],
        "vwap_reversion": [138, -0.139402419, 884, 69]},
}
VERDETTO_PRIMA = {
    0: (True, ["trend_following", "momentum"], 0.18714004941667425),
    1: (True, ["trend_following", "grid_trading", "momentum"], 0.37238809522223404),
}


@pytest.mark.parametrize("scala", [0, 1])
def test_il_motore_da_gli_stessi_trade_e_lo_stesso_verdetto(monkeypatch, scala):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", bool(scala))
    candles = _synthetic(datetime(2023, 1, 1, tzinfo=timezone.utc),
                         datetime(2023, 3, 1, tzinfo=timezone.utc))
    bt = Backtester(window=50)
    stats = bt.run("BTCUSDT", candles)
    for name, (n, pnl, barre, verdetti) in MOTORE_PRIMA[scala].items():
        tr = stats[name].trades
        assert len(tr) == n, name
        assert sum(t.pnl_pct for t in tr) == pytest.approx(pnl, abs=1e-8), name
        assert sum(t.bars_held for t in tr) == barre, name
        assert sum(1 for t in tr if t.trailing_verdict) == verdetti, name
        # e l'etichetta nuova c'e' su ogni trade, coerente col verdetto trailing
        assert all(t.exit_reason in ("stop", "trailing", "breakeven", "stop_dopo_tp1", "tp",
                                     "orizzonte", "fine_dati") for t in tr), name
        assert sum(1 for t in tr if t.exit_reason == "trailing") == verdetti, name
    passed, profittevoli, totale = VERDETTO_PRIMA[scala]
    v = bt.verdict(stats)
    assert v["passed"] is passed
    assert v["profitable_strategies"] == profittevoli
    assert v["total_pnl_pct"] == pytest.approx(totale, abs=1e-9)


# --------------------------------------------------------------------------- #
# 2) l'executor: apertura -> chiusura                                          #
# --------------------------------------------------------------------------- #
PERCORSI = {
    "long_tp": [(101, 102, 100.5), (103, 103.5, 101), (106, 106.5, 103), (111, 111, 105)],
    "long_trail": [(101, 102, 100.5), (103.2, 103.4, 101), (102, 102.5, 100.2),
                   (100.5, 101, 99.0), (99, 99.5, 97.0)],
    "long_stop": [(99.5, 100.2, 99), (98.5, 99.6, 97.5)],
    "short_tp": [(99, 99.5, 98), (97, 97.2, 96.5), (94, 94.2, 93.5), (89, 90, 88)],
    "short_trail": [(99, 99.5, 98.0), (96.8, 97, 96.6), (98, 99.0, 97.5), (100.5, 101.5, 99.5)],
}

#: (motivo, prezzo d'uscita, pnl, gradini, fette incassate, accrediti) PRIMA
#: della cattura (executor del commit precedente al 1 ott 2026)
EXECUTOR_PRIMA = {
    '0|0.65|long_stop': ('stop_loss', 98.0, -4.184, 0, 0.0, [-4.184]),
    '0|0.65|long_tp': ('take_profit', 110.0, 19.816, 0, 0.0, [19.816]),
    '0|0.65|long_trail': ('stop_loss', 98.0, -4.184, 0, 0.0, [-4.184]),
    '0|0.65|short_tp': ('take_profit', 90.0, 19.816, 0, 0.0, [19.816]),
    '0|0.65|short_trail': ('manual', 100.5, -1.184, 0, 0.0, [-1.184]),
    '0|None|long_stop': ('stop_loss', 98.0, -4.184, 0, 0.0, [-4.184]),
    '0|None|long_tp': ('take_profit', 110.0, 19.816, 0, 0.0, [19.816]),
    '0|None|long_trail': ('stop_loss', 98.0, -4.184, 0, 0.0, [-4.184]),
    '0|None|short_tp': ('take_profit', 90.0, 19.816, 0, 0.0, [19.816]),
    '0|None|short_trail': ('manual', 100.5, -1.184, 0, 0.0, [-1.184]),
    '1|0.65|long_stop': ('stop_loss', 98.0, -4.184, 0, 0.0, [-4.184]),
    '1|0.65|long_tp': ('trailing_stop', 101.3, 2.416, 0, 0.0, [2.416]),
    '1|0.65|long_trail': ('trailing_stop', 101.3, 2.416, 0, 0.0, [2.416]),
    '1|0.65|short_tp': ('take_profit', 90.0, 13.216, 3, 5.2896, [1.7448, 3.5448, 7.9264]),
    '1|0.65|short_trail': ('scale_out', 97.79, 4.71, 1, 1.7448, [1.7448, 2.9652]),
    '1|None|long_stop': ('stop_loss', 98.0, -4.184, 0, 0.0, [-4.184]),
    '1|None|long_tp': ('trailing_stop', 101.0, 1.816, 0, 0.0, [1.816]),
    '1|None|long_trail': ('trailing_stop', 101.0, 1.816, 0, 0.0, [1.816]),
    '1|None|short_tp': ('take_profit', 90.0, 13.216, 3, 5.2896, [1.7448, 3.5448, 7.9264]),
    '1|None|short_trail': ('scale_out', 98.3, 3.996, 1, 1.7448, [1.7448, 2.2512]),
}


def _asset(price=100.0):
    # close_chiusa diversa dal prezzo: da oggi diventa il prezzo «atteso»
    # (expected_entry_price); il prezzo eseguito NON deve cambiare
    return AssetSnapshot(symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING,
                         volume_24h=5e8, close_chiusa=price - 0.3, funding_rate=0.0001,
                         indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=price)})


def _params(long: bool):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, risk_effective_pct=0.01, notional=100.0, quantity=2.0,
        stop_price=98.0 if long else 102.0, take_profit_price=110.0 if long else 90.0,
        user_leverage=3, user_risk_per_trade=0.01, safety_leverage_cap=5, safety_risk_cap=0.03,
        approved=True)


@pytest.mark.parametrize("chiave", sorted(EXECUTOR_PRIMA))
def test_apertura_e_chiusura_paper_identiche_a_prima(monkeypatch, chiave):
    scala, keep, nome = chiave.split("|")
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", scala == "1")
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_FRACTIONS", (0.3, 0.3, 0.4))
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", True)
    long = nome.startswith("long")
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    pos = eng.open_position(_asset(), "s", Direction.LONG if long else Direction.SHORT,
                            _params(long), profit_lock_keep=None if keep == "None" else float(keep),
                            versione={"commit": "abc1234", "config_hash": "f" * 12},
                            promessa_gate={"pass_count": 3, "last_pf": 1.5},
                            regime_globale=Regime.SIDEWAYS)
    assert pos.entry_price == 100.0 and pos.quantity == 2.0       # fill invariato
    closed = None
    for mark, hi, lo in PERCORSI[nome]:
        closed = eng.update_position("BTCUSDT", float(mark), high=float(hi), low=float(lo))
        if closed:
            break
    if closed is None:
        closed = eng._close(eng.open_positions["BTCUSDT"], float(PERCORSI[nome][-1][0]),
                            ExitReason.MANUAL)
    motivo, prezzo, pnl, gradini, fette, accrediti = EXECUTOR_PRIMA[chiave]
    assert closed.exit_reason.value == motivo
    assert closed.exit_price == pytest.approx(prezzo, abs=1e-9)
    assert closed.pnl == pytest.approx(pnl, abs=1e-5)
    assert closed.scale_stage_reached == gradini
    assert closed.realized_partial == pytest.approx(fette, abs=1e-6)
    assert [round(e, 6) for e in eng.pop_realized()] == pytest.approx(accrediti, abs=1e-5)
    # e i dati nuovi ci sono, accanto
    assert closed.versione == {"commit": "abc1234", "config_hash": "f" * 12}
    assert closed.promessa_gate["pass_count"] == 3
    assert closed.regime_globale_at_entry == Regime.SIDEWAYS
    assert closed.close_segnale == pytest.approx(99.7)
