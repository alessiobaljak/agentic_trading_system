"""K7 e D6, 1 ott 2026 (si' del proprietario alle voci aperte del backlog).

K7 — l'AI riceveva numeri sbagliati:
  (a) la riga «GATE: su 1320 valutazioni ne passano 0» veniva dall'autopsia
      delle strategie BASE, ferma al 21 set: ora viene dall'autopsia del giro
      precedente dello STESSO timeframe, solo se fresca;
  (b) il giro a 15 minuti leggeva l'autopsia della passata a 1 ora (stesso
      documento) e il prompt diceva sempre il timeframe del bot: ora un
      documento per timeframe, e il prompt dice quello giusto;
  (c) le cadute sull'holdout avevano «scarto 0,000» e «quasi-passaggio» sempre
      vero, e la riga portava PF e trade delle finestre: ora scarto vero, i
      numeri dell'holdout, e lo stesso ordine nell'autopsia e nelle esplorative.
      Il verdetto pass/bocciata NON cambia (verificato anche HEAD contro nuovo).

D6 — «le idee AI servono?»: le coppie per origine della spec, contate (coppie,
non R) coi documenti che `gate` legge gia'.
"""
import random
import time
from types import SimpleNamespace

import pytest

from backtesting.engine import GateVerdict, holdout_verdict
from backtesting.optimizer import diagnosi_holdout
from bot.ai import autopsia as a
from bot.config import settings
from bot.core.registry import ORIGINI, conta_per_origine, origine_spec
from scripts import discover_strategies as d
from scripts.gate_progress import riga_origini

TF = settings.ORCHESTRATOR_TIMEFRAME


class _Fb:
    def __init__(self, docs=None):
        self.docs = dict(docs or {})
        self.scritti: dict = {}
        self.letti: list = []

    def get_doc(self, c, i):
        self.letti.append((c, i))
        return self.docs.get((c, i), {})

    def set_doc(self, c, i, v):
        self.scritti[(c, i)] = v
        self.docs[(c, i)] = v

    def query_collection(self, *a, **k):
        return []


# --------------------------------------------------------------------------- #
# K7 (c): lo scarto vero dell'holdout                                          #
# --------------------------------------------------------------------------- #
def _ok_del_controllo(n, pf, pnl, pf_ex):
    """La formula di `WalkForwardOptimizer._holdout_check`, copiata: se una delle
    due cambia, questo test lo dice."""
    return (n >= settings.GATE_HOLDOUT_MIN_TRADES and pf >= settings.GATE_HOLDOUT_PF
            and pnl > 0 and pf_ex >= settings.GATE_MIN_PF_EX_TOP)


def test_holdout_verdict_ha_lo_stesso_ok_del_controllo():
    rng = random.Random(3)
    for _ in range(5000):
        n = rng.randint(0, 20)
        pf = rng.choice([rng.uniform(0, 3), settings.GATE_HOLDOUT_PF])
        pnl = rng.choice([rng.uniform(-0.2, 0.2), 0.0])
        pf_ex = rng.choice([rng.uniform(0, 3), settings.GATE_MIN_PF_EX_TOP])
        v = holdout_verdict(n, pf, pnl, pf_ex)
        assert v.ok == _ok_del_controllo(n, pf, pnl, pf_ex)
        if not v.ok:
            assert v.binding in v.failed and v.shortfall < 0


def test_holdout_verdict_dice_quale_soglia_e_di_quanto(monkeypatch):
    monkeypatch.setattr(settings, "GATE_HOLDOUT_PF", 1.3)
    monkeypatch.setattr(settings, "GATE_HOLDOUT_MIN_TRADES", 5)
    monkeypatch.setattr(settings, "GATE_MIN_PF_EX_TOP", 1.0)
    v = holdout_verdict(9, 1.25, 0.03, 1.1)          # PF a un pelo dalla soglia
    assert v.failed == ("holdout_pf",) and v.binding == "holdout_pf"
    assert v.shortfall == pytest.approx((1.25 - 1.3) / 1.3, abs=1e-4)
    assert v.near_miss()
    v = holdout_verdict(9, 0.4, -0.05, 0.3)           # lontana: tre soglie
    assert set(v.failed) == {"holdout_pf", "holdout_pnl", "holdout_pf_ex_top"}
    assert v.shortfall <= -0.69 and not v.near_miss()
    v = holdout_verdict(9, 1.5, 0.0, 1.2)             # ritorno zero: si'/no, -1
    assert v.failed == ("holdout_pnl",) and v.shortfall == -1.0


def test_holdout_check_scrive_lo_scarto_solo_per_le_cadute():
    import datetime as dt

    import pandas as pd

    from backtesting.engine import StrategyStats
    from backtesting.optimizer import WalkForwardOptimizer
    opt = WalkForwardOptimizer(n_windows=1)
    base = 1.75e9
    candles = [SimpleNamespace(open_time=dt.datetime.fromtimestamp(base + i * 900, dt.timezone.utc))
               for i in range(400)]
    frame = pd.DataFrame({"x": range(400)})
    cut = 300

    def esito(pnls):
        trades = [SimpleNamespace(pnl_pct=p, entry_ts=base + (cut + i) * 900, is_win=p > 0,
                                  trailing_verdict=None) for i, p in enumerate(pnls)]
        opt.bt = SimpleNamespace(window=50, run_strategy=lambda *x, **k: StrategyStats(
            strategy="s", trades=list(trades)))
        return opt._holdout_check(SimpleNamespace(name="s"), "A", candles, frame, cut)

    buono = esito([0.02, -0.01, 0.015, 0.01, -0.005, 0.02, 0.01])
    assert buono["ok"] is True and "scarto" not in buono
    cattivo = esito([0.01, -0.02, 0.005, -0.03, -0.01, 0.002, -0.01])
    assert cattivo["ok"] is False
    sc = cattivo["scarto"]
    assert sc["criterio"] in sc["criteri"] and sc["shortfall"] < 0


def test_diagnosi_holdout():
    assert diagnosi_holdout({"ok": False, "scarto": {"criterio": "holdout_pf",
                                                     "criteri": ["holdout_pf"],
                                                     "shortfall": -0.04}}) == (-0.04, True)
    assert diagnosi_holdout({"ok": False, "scarto": {"criterio": "holdout_pf",
                                                     "criteri": ["holdout_pf", "holdout_pnl"],
                                                     "shortfall": -0.04}}) == (-0.04, False)
    assert diagnosi_holdout({"ok": False, "scarto": {"criterio": "holdout_trades",
                                                     "criteri": ["holdout_trades"],
                                                     "shortfall": -0.4}}) == (-0.4, False)
    # holdout senza diagnosi (codice vecchio): lontana, non quasi
    assert diagnosi_holdout({"ok": False}) == (-1.0, False)
    assert diagnosi_holdout(None) == (-1.0, False)


class _Bt:
    window = 0

    def run_strategy(self, g, symbol, candles, frame=None, context_by_ts=None):
        from backtesting.engine import StrategyStats
        st = StrategyStats(strategy=g.name)
        for i, p in enumerate((0.03, -0.01, 0.02)):
            st.trades.append(SimpleNamespace(pnl_pct=p, is_win=p > 0, entry_ts=1.7e9 + i,
                                             exit_ts=1.7e9 + i + 1, direction="long",
                                             regime="bull", trailing_verdict=None, mfe_r=None))
        return st


class _Opt:
    holdout_bars = 1

    def __init__(self, hold):
        self.bt = _Bt()
        self.hold = hold

    def split_holdout(self, candles):
        return candles[:-1], len(candles) - 1

    def _windows(self, n):
        return [(0, 0, 0, n)]

    def _holdout_check(self, *a, **k):
        return dict(self.hold)


def _valuta_con_holdout(monkeypatch, hold):
    import pandas as pd
    monkeypatch.setattr(d, "gate_verdict", lambda *x, **k: GateVerdict(ok=True))
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    monkeypatch.setattr(d, "righe_selettore", lambda *x, **k: ["riga"])
    candles = [SimpleNamespace(open_time=SimpleNamespace(timestamp=lambda: 1.7e9))] * 4
    return d.evaluate_spec(_Opt(hold), "XUSDT", candles, pd.DataFrame({"close": [1.0] * 4}),
                           {"id": "gen_h", "features": [{"kind": "rsi_extreme"}]},
                           righe_bocciate=True)


def test_evaluate_spec_caduta_sull_holdout_scarto_vero_e_righe_come_prima(monkeypatch):
    vicina = {"ok": False, "pf": 1.0, "trades": 9, "pf_ex_top": 1.1, "t": 0.5,
              "scarto": {"criterio": "holdout_pf", "criteri": ["holdout_pf"], "shortfall": -0.05}}
    r = _valuta_con_holdout(monkeypatch, vicina)
    assert r["passed"] is False
    assert r["fail_criteria"] == ["holdout"] and r["fail_binding"] == "holdout"
    assert r["fail_shortfall"] == -0.05 and r["near_miss"] is True
    assert r["oos_rows"] == ["riga"]
    lontana = dict(vicina, scarto={"criterio": "holdout_pf",
                                   "criteri": ["holdout_pf", "holdout_pnl"], "shortfall": -0.6})
    r = _valuta_con_holdout(monkeypatch, lontana)
    assert r["fail_shortfall"] == -0.6 and r["near_miss"] is False
    # il dataset del selettore resta quello di prima: le cadute sull'holdout
    # scrivono le righe anche quando non sono piu' «quasi-passaggi»
    assert r["oos_rows"] == ["riga"]
    passa = _valuta_con_holdout(monkeypatch, {"ok": True, "pf": 1.5, "trades": 9})
    assert passa["passed"] is True and passa["fail_criteria"] == []


def test_la_voce_del_quasi_passaggio_porta_i_numeri_dell_holdout():
    r = {"fail_binding": "holdout", "fail_shortfall": -0.05, "pf": 2.4, "trades": 120,
         "t_stat": 3.1, "holdout": {"ok": False, "pf": 1.0, "trades": 9, "pf_ex_top": 0.9,
                                    "t": 0.4, "scarto": {"criterio": "holdout_pf"}}}
    v = d.voce_quasi_passaggio("A|gen_x", r)
    assert (v["pf"], v["trades"], v["pf_ex_top"], v["t_stat"]) == (1.0, 9, 0.9, 0.4)
    assert v["numeri"] == "holdout" and v["criterio"] == "holdout_pf" and v["shortfall"] == -0.05
    r2 = {"fail_binding": "pf", "fail_shortfall": -0.03, "pf": 1.25, "trades": 80, "t_stat": 1.0,
          "holdout": {}}
    v2 = d.voce_quasi_passaggio("A|gen_y", r2)
    assert (v2["pf"], v2["trades"]) == (1.25, 80) and "numeri" not in v2
    # e all'AI arriva cosi', non piu' «scarto 0,000» coi numeri delle finestre
    riga = a._riga(v, {})
    assert "holdout_pf" in riga and "PF dell'holdout 1.0" in riga and "9 trade dell'holdout" in riga
    assert "0.000" not in riga


def test_stesso_ordine_nell_autopsia_e_nelle_esplorative():
    near = [{"key": f"C{i}USDT|gen_{i}", "shortfall": sf, "binding": "pf", "pf": 1, "trades": 9}
            for i, sf in enumerate([-0.05, 0.0, None, -0.01, -0.09, -0.0])]
    fb = _Fb()
    rep = d._publish_discover_autopsy(fb, 100, 0, {"pf": 6}, {"pf": 6}, near, interval=TF)
    ordine_autopsia = [n["key"] for n in rep["near_misses"]]
    specs = {f"gen_{i}": {"id": f"gen_{i}"} for i in range(6)}
    scelte = d.seleziona_esplorative(near, [], specs, {f"C{i}USDT" for i in range(6)}, max_n=6)
    assert [s["key"] for s in scelte] == ordine_autopsia
    assert ordine_autopsia[-1] == "C2USDT|gen_2"        # senza scarto: in fondo
    assert ordine_autopsia[0] in ("C1USDT|gen_1", "C5USDT|gen_5")   # lo 0,0 in testa


# --------------------------------------------------------------------------- #
# K7 (b): un'autopsia per timeframe                                            #
# --------------------------------------------------------------------------- #
NEAR = [{"key": "ORCAUSDT|gen_a", "binding": "pf", "shortfall": -0.02, "pf": 1.4, "trades": 40}]


def test_un_documento_per_timeframe():
    assert a.doc_autopsia(None) == a.doc_autopsia(TF) == "discover"
    altro = "1h" if TF != "1h" else "4h"
    assert a.doc_autopsia(altro) == f"discover_{altro}"
    fb = _Fb()
    d._publish_discover_autopsy(fb, 10, 1, {"pf": 3}, {"pf": 3}, NEAR, interval=altro)
    d._publish_discover_autopsy(fb, 20, 2, {"pf": 5}, {"pf": 5}, NEAR, interval=TF)
    assert fb.scritti[("gate_autopsy", f"discover_{altro}")]["interval"] == altro
    assert fb.scritti[("gate_autopsy", "discover")]["interval"] == TF
    assert fb.scritti[("gate_autopsy", "discover")]["evaluated"] == 20


def test_e_del_timeframe():
    altro = "1h" if TF != "1h" else "4h"
    assert a.e_del_timeframe({"interval": TF}, TF)
    assert not a.e_del_timeframe({"interval": altro}, TF)
    # documento scritto prima del 1 ott (senza `interval`): solo per il timeframe del bot
    assert a.e_del_timeframe({}, TF) and not a.e_del_timeframe({}, altro)
    assert not a.e_del_timeframe(None, TF)


def test_l_autopsia_ai_legge_il_suo_timeframe_e_lo_dice(monkeypatch):
    altro = "1h" if TF != "1h" else "4h"
    visto = {}

    def finto(system, user, **kw):
        visto["user"] = user
        return {"schema": "s", "ipotesi": [], "consigli": "c"}
    monkeypatch.setattr(a, "ask_json", finto)
    monkeypatch.setattr(a, "available", lambda: True)
    doc_altro = {"near_misses": NEAR, "binding": {"pf": 3}, "passed": 1, "evaluated": 900,
                 "interval": altro}
    # il giro del bot NON legge piu' l'autopsia dell'altro timeframe...
    fb = _Fb({("gate_autopsy", "discover"): doc_altro})
    assert a.analizza(fb, interval=TF) is None
    # ...e la passata dell'altro timeframe legge la sua, col suo timeframe nel prompt
    fb = _Fb({("gate_autopsy", f"discover_{altro}"): doc_altro})
    out = a.analizza(fb, interval=altro)
    assert out and out["interval"] == altro
    assert f"Timeframe: {altro}." in visto["user"]
    assert ("gate_autopsy", f"discover_{altro}") in fb.letti


def test_i_semi_delle_mutazioni_vengono_dal_proprio_timeframe():
    altro = "1h" if TF != "1h" else "4h"
    existing = {"gen_a": {"id": "gen_a"}, "gen_b": {"id": "gen_b"}}
    fb = _Fb({("gate_autopsy", "discover"): {"near_misses": [{"key": "X|gen_a"}]},
              ("gate_autopsy", f"discover_{altro}"): {"near_misses": [{"key": "X|gen_b"}]}})
    assert [s["id"] for s in d.mutation_seeds(fb, existing, interval=TF)] == ["gen_a"]
    assert [s["id"] for s in d.mutation_seeds(fb, existing, interval=altro)] == ["gen_b"]


# --------------------------------------------------------------------------- #
# K7 (a): la riga GATE dalle prove all'AI                                      #
# --------------------------------------------------------------------------- #
def test_la_riga_gate_viene_dal_giro_precedente_se_fresca():
    ora = 1.76e9
    aut = {"interval": TF, "updated_at": ora - 3 * 3600, "evaluated": 24503, "passed": 48,
           "binding": {"total_return": 15000, "pf": 5000}}
    r = d.riga_gate_per_prove(aut, TF, ora)
    assert "24503" in r and "48" in r and "total_return" in r and TF in r
    assert d.riga_gate_per_prove(dict(aut, updated_at=ora - 13 * 3600), TF, ora) is None
    altro = "1h" if TF != "1h" else "4h"
    assert d.riga_gate_per_prove(aut, altro, ora) is None
    assert d.riga_gate_per_prove(dict(aut, binding={}), TF, ora) is None
    assert d.riga_gate_per_prove(None, TF, ora) is None


def test_le_prove_non_leggono_piu_l_autopsia_delle_base():
    ora = time.time()
    vecchia = {"evaluated": 1320, "passed": 0, "binding": {"total_return": 900},
               "updated_at": ora - 10 * 86400}
    fb = _Fb({("gate_autopsy", "current"): vecchia})
    assert "1320" not in d.prove_dal_paper(fb, interval=TF, now=ora)
    assert ("gate_autopsy", "current") not in fb.letti
    fresca = {"interval": TF, "updated_at": ora - 600, "evaluated": 24503, "passed": 48,
              "binding": {"total_return": 15000}}
    fb = _Fb({("gate_autopsy", "current"): vecchia, ("gate_autopsy", "discover"): fresca})
    testo = d.prove_dal_paper(fb, interval=TF, now=ora)
    assert "24503" in testo and "1320" not in testo


# --------------------------------------------------------------------------- #
# D6: le coppie per origine                                                    #
# --------------------------------------------------------------------------- #
def test_origine_spec():
    assert origine_spec({"mechanism": "perche'"}) == "ai"
    assert origine_spec({"origine": "referto", "mechanism": "madre AI"}) == "varianti"
    assert origine_spec({"origine": "intorno"}) == "intorno"
    assert origine_spec({"features": []}) == "casuali"
    assert origine_spec(None) == "spec_ignota"
    assert origine_spec({"mechanism": "x"}, generata=False) == "base"


def test_conta_per_origine_e_riga():
    specs = {"gen_ai": {"mechanism": "m"}, "gen_ca": {}, "gen_va": {"origine": "referto"}}
    pairs = {"A|gen_ai": {"generated": True, "pass_count": 3, "declassata": True},
             "B|gen_ai": {"generated": True, "pass_count": 1},
             "A|gen_ca": {"generated": True, "pass_count": 3},
             "C|gen_va": {"generated": True, "pass_count": 2},
             "D|gen_xx": {"generated": True, "pass_count": 1},
             "E|rsi": {"pass_count": 3}}
    validated = ["A|gen_ai", "A|gen_ca", "E|rsi"]
    c = conta_per_origine(pairs, validated, specs)
    assert c["ai"] == {"registro": 2, "validate": 1, "declassate": 1}
    assert c["casuali"] == {"registro": 1, "validate": 1, "declassate": 0}
    assert c["varianti"]["registro"] == 1 and c["spec_ignota"]["registro"] == 1
    assert c["base"] == {"registro": 1, "validate": 1, "declassate": 0}
    assert set(c) == set(ORIGINI)
    diag = {"spec_per_origine": {"nuove": {"ai": 5, "casuali": 20, "mutazioni": 30, "varianti": 2},
                                 "note": {"casuali": 600, "ai": 29}, "intorno_figlie": 0}}
    riga = riga_origini(pairs, validated, specs, diag, {})
    assert "non l'R" in riga and "AI: 2 nel registro / 1 validate / 1 declassate" in riga
    assert "nuove ai 5 · casuali 20 · mutazioni 30 · varianti 2" in riga
    assert "passata a 1 ora: non registrate" in riga
    assert "spec non leggibili" in riga_origini(pairs, validated, None)


def test_conta_spec_per_origine_del_giro():
    ai, va, ca, mu = [{"id": "g1", "mechanism": "m"}], [{"id": "g2", "origine": "referto"}], \
        [{"id": "g3"}, {"id": "g4"}], [{"id": "g5"}]
    note = [{"id": "g6"}, {"id": "g7"}]
    existing = {"g6": {"mechanism": "m"}, "g7": {}}
    fonti = d.fonti_delle_spec((("ai", ai), ("varianti", va), ("casuali", ca),
                                ("note", note), ("mutazioni", mu)))
    c = d.conta_spec_per_origine(ai + va + ca + note + mu, existing, fonti)
    assert c == {"nuove": {"ai": 1, "casuali": 2, "mutazioni": 1, "varianti": 1},
                 "note": {"ai": 1, "casuali": 1}}


def test_il_giro_scrive_le_origini_nel_riepilogo():
    import inspect
    src = inspect.getsource(d.main)
    assert "fonti_delle_spec(" in src and '"spec_per_origine"' in src
    # la generazione e' la stessa di prima: casuali e mutazioni nello stesso ordine
    assert "casuali = generate_specs(n_casuali, seed=args.seed)" in src
    assert "mutate(base, seed=args.seed + i + 1)" in src
