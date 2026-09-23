"""IL CONTROLLO DEL SETUP PRIMA, IL REFERTO DOPO — stessa aritmetica.

23 set 2026, MUBARAK long dopo un pump: stop -15,3%, primo incasso +31%, lock a
+15%; ore «in positivo» a 0,3R, poi stop pieno. Il proprietario: «perche' queste
analisi il sistema non le fa PRIMA? e per ogni trade perso le voglio scritte e
usate». Qui i numeri veri di quel trade sono il test.
"""
import inspect

from bot.config import settings
from bot.risk.setup_check import analizza_setup, post_mortem

E, SL = 0.07022, 0.0595          # MUBARAK, 23 set


def test_il_setup_di_mubarak_non_era_tradabile():
    g = analizza_setup(E, SL, (2.0, 4.0, 6.0))
    assert g["tradabile"] is False
    assert abs(g["stop_pct"] - 0.1527) < 0.001
    assert abs(g["primo_gradino_pct"] - 0.305) < 0.005     # +31%
    assert abs(g["lock_arma_pct"] - 0.1527) < 0.001         # +15%
    assert "stop troppo largo" in g["motivo"] and "15.3%" in g["motivo"]


def test_uno_stop_normale_passa():
    assert analizza_setup(100.0, 97.0, (2.0, 4.0, 6.0))["tradabile"] is True
    assert settings.MAX_STOP_PCT == 0.06


def test_zero_spegne_il_tetto():
    assert analizza_setup(E, SL, (2.0, 4.0, 6.0), max_stop_pct=0.0)["tradabile"] is True


def test_il_referto_di_mubarak_dice_le_cose_giuste():
    pm = post_mortem({"entry_price": E, "orig_stop": SL, "scale_r_mults": [2.0, 4.0, 6.0],
                      "mfe_r": 0.3, "pnl": -9.8, "direction": "long", "regime_at_entry": "bull_trending"})
    assert pm["classe"] == "uscita"            # a favore, sotto il primo gradino
    assert pm["stop_largo"] is True
    assert pm["lock_mai_armato"] is True
    assert pm["controtrend"] is False
    assert "stop troppo largo" in pm["verdetto"] and "lock non si e' mai armato" in pm["verdetto"]


def test_le_tre_classi_e_il_controtrend():
    base = {"entry_price": 100.0, "orig_stop": 98.0, "scale_r_mults": [1.5, 3.0, 5.0], "pnl": -1.0}
    assert post_mortem({**base, "mfe_r": 0.1, "direction": "short", "regime_at_entry": "bull_trending"})["classe"] == "ingresso"
    assert post_mortem({**base, "mfe_r": 0.1, "direction": "short", "regime_at_entry": "bull_trending"})["controtrend"] is True
    assert post_mortem({**base, "mfe_r": 1.0, "direction": "long", "regime_at_entry": "sideways"})["classe"] == "uscita"
    assert post_mortem({**base, "mfe_r": 2.0, "direction": "long", "regime_at_entry": "sideways"})["classe"] == "protezione"
    assert post_mortem({**base, "mfe_r": 2.0, "pnl": 3.0, "direction": "long"})["verdetto"].startswith("chiuso in guadagno")


def test_gate_e_bot_usano_la_STESSA_funzione():
    """Se il motore saltasse setup che il bot apre (o viceversa), il PF promesso
    descriverebbe un altro sistema: BIRBUSDT."""
    from backtesting import engine
    from bot.risk import risk_manager

    assert 'analizza_setup(entry, stop' in inspect.getsource(engine.Backtester.run_strategy)
    assert "analizza_setup(price, stop_price" in inspect.getsource(risk_manager)
    assert 'reject_reason=_geo["motivo"]' in inspect.getsource(risk_manager)


def test_il_referto_si_scrive_alla_chiusura_e_trades_lo_stampa():
    from bot.core.models import ClosedTrade
    from bot.execution import executor
    from scripts import trade_stats

    assert "post_mortem" in ClosedTrade.model_fields
    assert "trade.post_mortem = post_mortem(" in inspect.getsource(executor)
    assert "REFERTI (post_mortem)" in inspect.getsource(trade_stats.main)
