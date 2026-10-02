"""2 ott 2026: la misura dell'affollamento nel report trades e gli interruttori
che spengono idee AI (con autopsia) e varianti dai referti nella discovery."""
import inspect

import scripts.trade_stats as ts
from bot.config import settings


def _t(d, en, ex, pnl):
    return {"symbol": f"C{en}", "strategy": "g", "direction": d, "entry_ts": float(en),
            "exit_ts": float(ex), "pnl": pnl, "entry_price": 10.0, "orig_stop": 9.0, "size": 1.0}


def test_affollamento_conta_le_posizioni_nello_stesso_verso():
    t0 = 1_760_000_000
    # 7 long aperti entro 2 minuti (un'ondata), piu' 1 short e 1 long isolato
    trades = [_t("long", t0 + i * 15, t0 + 3600, -1.0) for i in range(7)]
    trades += [_t("short", t0, t0 + 3600, 2.0), _t("long", t0 + 7200, t0 + 9000, 3.0)]
    rep = ts.affollamento_report(trades)
    f = rep["fasce"]
    assert f["6+"]["n"] == 2 and f["3-5"]["n"] == 3 and f["1-2"]["n"] == 4
    assert f["6+"]["r_medio"] == -1.0 and f["1-2"]["vinti"] == 2
    assert len(rep["ondate"]) == 1 and rep["ondate"][0]["verso"] == "long"
    assert rep["ondate"][0]["n"] == 7 and rep["ondate"][0]["pnl"] == -7.0


def test_affollamento_senza_ondate_e_stampa(capsys):
    rep = ts.affollamento_report([_t("long", 1, 100, 1.0), _t("short", 50, 200, -1.0)])
    assert rep["ondate"] == [] and rep["fasce"]["1-2"]["n"] == 2
    ts.print_affollamento(rep)
    out = capsys.readouterr().out
    assert "AFFOLLAMENTO" in out and "nessuna ondata" in out


def test_interruttori_spenti_di_default():
    assert settings.AI_HYPOTHESES_ENABLED is False
    assert settings.DISCOVERY_VARIANTI_REFERTI is False


def test_la_discovery_salta_proposte_autopsia_e_varianti_quando_spente():
    import scripts.discover_strategies as d
    src = inspect.getsource(d.main)
    assert "if settings.AI_HYPOTHESES_ENABLED:" in src and "ai_specs = []" in src
    assert "if settings.DISCOVERY_VARIANTI_REFERTI:" in src and "varianti = []" in src
    # l'autopsia si chiama solo dentro l'interruttore delle idee
    i = src.index("ai_autopsia(fb, interval=args.interval)")
    assert src.rfind("if settings.AI_HYPOTHESES_ENABLED:", 0, i) > src.rfind("autopsia = None", 0, i) - 200
