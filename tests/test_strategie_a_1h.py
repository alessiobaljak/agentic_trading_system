"""STRATEGIE NATIVE A 1 ORA, PER ORA SOLO BTC — C1, seconda meta' (22 set 2026).

«Guardare la moneta con due occhi»: oltre alla conferma a 1 ora (feature), ora
esistono strategie che VIVONO a 1 ora. Quattro proprieta' da tenere ferme:
la spec porta il suo timeframe e l'id lo include; nel bot ogni strategia decide
sul suo orologio; i trade portano il timeframe della strategia; e la passata a
1 ora non puo' sforare la finestra del timer.
"""
import inspect

from bot.strategies.generated import GeneratedStrategy, spec_id


def _spec(tf=None):
    sp = {"features": [{"kind": "rsi_extreme", "low": 30, "high": 70}],
          "atr_mult_stop": 1.5, "rr": 2.0, "min_adx": 0.0, "volume_mult": 0.0}
    if tf:
        sp["timeframe"] = tf
    return sp


def test_la_stessa_logica_a_15m_e_a_1h_sono_due_strategie():
    """Senza il timeframe nell'id, una spec a 1h erediterebbe pesi e storia della
    gemella a 15m. E una spec SENZA timeframe ha lo stesso id di prima: le 56
    validate non cambiano nome."""
    from bot.config import settings

    assert spec_id(_spec("1h")) != spec_id(_spec("15m"))
    assert spec_id(_spec()) == spec_id(_spec(settings.ORCHESTRATOR_TIMEFRAME))


def test_la_strategia_legge_gli_indicatori_del_SUO_timeframe():
    from bot.config import settings

    a = GeneratedStrategy({**_spec("1h"), "id": "gen_1h"})
    b = GeneratedStrategy({**_spec(), "id": "gen_b"})
    assert a.timeframe == "1h" and a._tf == "1h"
    assert b.timeframe == settings.ORCHESTRATOR_TIMEFRAME


def test_nel_bot_una_strategia_a_1h_decide_solo_alla_chiusura_oraria():
    """Nel backtest e' valutata a ogni SUA candela: dal vivo deve decidere una
    volta l'ora, non quattro come se fosse a 15 minuti."""
    from bot.orchestrator.orchestrator import _TF_SECS, Orchestrator

    src = inspect.getsource(Orchestrator.collect_signals)
    assert 'int(boundary) % _tf_s != 0' in src
    assert _TF_SECS["1h"] == 3600 and _TF_SECS["15m"] == 900
    # 10:15 e' una chiusura a 15m ma non a 1h; 11:00 e' entrambe
    b1, b2 = 10 * 3600 + 900, 11 * 3600
    assert b1 % _TF_SECS["1h"] != 0 and b2 % _TF_SECS["1h"] == 0
    # e il bot passa davvero il confine
    from bot.main import TradingBot
    assert "boundary=boundary" in inspect.getsource(TradingBot.trading_cycle)


def test_i_trade_portano_il_timeframe_della_strategia():
    """Il learning (trailing keep, pesi) filtra per `timeframe`: un trade a 1h
    etichettato 15m inquinerebbe le statistiche dell'altro mondo."""
    from bot.execution import executor as ex

    src = inspect.getsource(ex)
    assert "timeframe=pos.timeframe or settings.ORCHESTRATOR_TIMEFRAME" in src
    assert '"timeframe": pos.timeframe' in src and 'pos.timeframe = p.get("timeframe")' in src
    from bot.main import TradingBot
    assert "timeframe=self.adaptation.timeframe_for(decision.strategy)" in inspect.getsource(TradingBot._try_open)


def test_la_passata_a_1h_e_su_btc_e_non_puo_sforare():
    from scripts import optimize as o

    assert o.DISCOVERY_EXTRA == "1h:BTCUSDT"
    assert o.DISCOVERY_EXTRA_MAX_S <= 3600
    src = inspect.getsource(o.passata_extra)
    assert "timeout=DISCOVERY_EXTRA_MAX_S" in src and '"--interval", interval, "--symbols", coins' in src


def test_la_discovery_stampa_il_timeframe_solo_sulle_nuove_e_isola_per_intervallo():
    from scripts import discover_strategies as d

    src = inspect.getsource(d.main)
    assert 'sp = {**sp, "timeframe": args.interval}' in src
    assert '(existing[sp["id"]].get("timeframe") or tf_bot) == args.interval' in src
    assert 'f"discovered_last_run_{args.interval}"' in src


def test_il_motore_chiama_la_riga_base_col_suo_intervallo():
    from backtesting import engine as e

    assert e._TF_NAMES[1.0] == "1h" and e._TF_NAMES[0.25] == "15m"
    assert "_TF_NAMES.get(round(self.interval_hours, 4)" in inspect.getsource(e.Backtester._snapshot_from_frame)
