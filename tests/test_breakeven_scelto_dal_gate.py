"""A2 — IL BREAK-EVEN DOPO IL PRIMO GRADINO LO SCEGLIE IL GATE, PER COPPIA.

Fino al 21 set 2026 tutte le 56 coppie validate giravano su `sl_to_breakeven=true`
senza che il gate l'avesse mai provato: le generate non hanno griglia, e il passo
che sceglie la scala dei TP non sceglieva anche questo. Con il lock ancorato al
primo gradino (A1) il BE cambia significato, quindi va misurato.
"""
import inspect

from scripts import discover_strategies as d


def test_si_prova_l_alternativa_al_default_sulla_scala_scelta():
    """UNA passata in piu', non il doppio della ricerca: costa un quarto e
    decide la stessa cosa."""
    src = inspect.getsource(d.evaluate_spec)
    assert "_run_oos(best_ladder, not be_default)" in src
    assert src.count("_run_oos(cand") == 1, "la scala non va ricercata due volte"


def test_la_scelta_viaggia_fino_al_registro():
    src = inspect.getsource(d.evaluate_spec)
    assert '"sl_to_breakeven": best_be' in src
    assert '"sl_to_breakeven": r.get("sl_to_breakeven")' in inspect.getsource(d._disc_one)
    tutto = inspect.getsource(d)
    assert 'rec["last_params"]["sl_to_breakeven"] = bool(e["sl_to_breakeven"])' in tutto


def test_le_metriche_finali_usano_la_scelta_vera():
    """Il registro deve pubblicare il PF della configurazione che il bot opera:
    se il BE scelto fosse diverso dal default e le metriche uscissero dalla
    passata col default, il PF promesso descriverebbe un altro sistema."""
    src = inspect.getsource(d.evaluate_spec)
    assert "or best_be != bool(settings.SCALE_OUT_SL_TO_BREAKEVEN)" in src
    assert "_run_oos(best_ladder, best_be)" in src


def test_il_bot_legge_gia_la_scelta():
    from bot.execution.exit_logic import breakeven_after_tp1

    assert breakeven_after_tp1({"sl_to_breakeven": False}) is False
    assert breakeven_after_tp1({"sl_to_breakeven": True}) is True
