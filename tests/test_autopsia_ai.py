"""B3 — I QUASI-PASSAGGI ALL'AI: apprendimento sulla ricerca.

Ogni giro produce ~40 candidate fermate da una sola condizione, e di poco.
Prima si contavano; ora si chiede al modello cosa hanno in comune, e i suoi
consigli entrano nelle proposte dello stesso giro. Tre proprieta' da tenere ferme:
il modello vede le FEATURE (non solo gli id), non decide niente, e senza di lui il
giro procede identico a prima.
"""
import inspect

from bot.ai import autopsia as a


class _Fb:
    def __init__(self, near, specs):
        self.docs = {("gate_autopsy", "discover"): {"near_misses": near, "binding": {"total_return": 30},
                                                    "passed": 1, "evaluated": 900},
                     ("discovered_strategies", "specs"): {"specs": specs}}
        self.scritti = {}

    def get_doc(self, c, d):
        return self.docs.get((c, d), {})

    def set_doc(self, c, d, v):
        self.scritti[(c, d)] = v


NEAR = [{"key": "ORCAUSDT|gen_a", "binding": "total_return", "shortfall": 0.02, "pf": 1.4, "trades": 40}]
SPECS = {"gen_a": {"features": [{"kind": "rsi_extreme", "low": 30, "high": 70}, {"kind": "bb_touch"}],
                   "min_adx": 20, "atr_mult_stop": 2.0}}


def test_il_modello_vede_le_feature_la_coin_e_il_criterio(monkeypatch):
    """Un id come `gen_a` non dice niente: senza le feature il modello non puo'
    trovare uno schema, e risponderebbe con generalita'."""
    visto = {}

    def finto(system, user, **kw):
        visto["user"] = user
        return {"schema": "vendono la forza con ADX alto", "ipotesi": ["x"], "consigli": "prova adx_below"}
    monkeypatch.setattr(a, "ask_json", finto)
    monkeypatch.setattr(a, "available", lambda: True)
    fb = _Fb(NEAR, SPECS)
    out = a.analizza(fb)
    assert out and out["schema"].startswith("vendono")
    assert "rsi_extreme" in visto["user"] and "ORCAUSDT" in visto["user"] and "total_return" in visto["user"]
    assert ("ai_hypotheses", "autopsia") in fb.scritti


def test_senza_ai_o_senza_quasi_passaggi_non_succede_niente(monkeypatch):
    monkeypatch.setattr(a, "available", lambda: False)
    assert a.analizza(_Fb(NEAR, SPECS)) is None
    monkeypatch.setattr(a, "available", lambda: True)
    monkeypatch.setattr(a, "ask_json", lambda *x, **k: {"schema": "s"})
    assert a.analizza(_Fb([], SPECS)) is None


def test_una_risposta_storta_non_produce_un_esito(monkeypatch):
    monkeypatch.setattr(a, "available", lambda: True)
    monkeypatch.setattr(a, "ask_json", lambda *x, **k: ["non", "un", "oggetto"])
    assert a.analizza(_Fb(NEAR, SPECS)) is None


def test_i_consigli_entrano_nelle_proposte_e_il_giro_non_dipende_dall_ai():
    from scripts import discover_strategies as d

    src = inspect.getsource(d.main)
    assert "contesto_per_le_proposte(autopsia)" in src
    assert "autopsia = None" in src, "senza AI si propone come prima"
    assert a.contesto_per_le_proposte(None) == ""
    assert "Consigli:" in a.contesto_per_le_proposte({"n_quasi": 3, "schema": "s", "consigli": "c"})


def test_l_ai_non_decide_niente():
    """Legge e suggerisce: nessuna scrittura sul registro, sulle spec, sul paper."""
    src = inspect.getsource(a)
    for vietato in ("strategy_registry", "update_registry", '"trades"', "set_rtdb"):
        assert vietato not in src, vietato
    assert 'set_doc("ai_hypotheses", "autopsia"' in src


def test_ai_stato_la_mostra():
    from scripts import ai_status

    assert 'get_doc("ai_hypotheses", "autopsia")' in inspect.getsource(ai_status.stato_prove)


def test_i_dati_sintetici_sono_spenti_per_default_e_accesi_solo_nei_test():
    """D2. Un percorso nuovo che carica candele non deve piu' ricadere su una
    serie inventata in silenzio."""
    from backtesting import data_loader as dl

    assert 'os.getenv("BACKTEST_ALLOW_SYNTHETIC", "false")' in inspect.getsource(dl.load_candles)
    assert 'os.environ["BACKTEST_ALLOW_SYNTHETIC"] = "true"' in open("tests/conftest.py").read()


def test_i_workflow_che_non_potevano_avere_dati_veri_non_esistono_piu():
    import os

    for f in ("optimize.yml", "discover.yml", "reset-optimizer.yml", "backtest.yml"):
        assert not os.path.exists(f".github/workflows/{f}"), f
    assert os.path.exists(".github/workflows/tests.yml")
