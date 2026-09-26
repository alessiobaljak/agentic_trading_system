"""CALIBRAZIONE DEL REGIME E DEL F&G (26 set 2026, backlog J8) — solo misure.

`regime_confidence_at_entry` e `fear_greed_at_entry` sono registrati su ogni
trade «per poter misurare se predicono l'esito» (bot/core/models.py) e nessuno
li aveva mai guardati. Qui si protegge: le fasce sono quelle dichiarate (terzili
per il regime; <= 25 / 26-74 / >= 75 per il F&G), il verdetto del regime dice
«campione insufficiente» sotto MIN_PER_FASCIA, gli esiti esterni e gli
esplorativi restano fuori come per la confidenza, e `trust` NON cambia.
"""
from bot.config import settings
from bot.learning.calibration import (CRESCE, INSUFFICIENTE_FASCE, MIN_PER_FASCIA,
                                      PIATTA, calibrate, confidence_trust,
                                      fasce_fear_greed, fasce_regime,
                                      misure_contesto, verdetto_fasce)


def _t(pnl, reg=None, fg=None, conf=60.0, reason="stop_loss", **extra):
    t = {"confidence_at_entry": conf, "pnl_pct": pnl, "exit_reason": reason}
    if reg is not None:
        t["regime_confidence_at_entry"] = reg
    if fg is not None:
        t["fear_greed_at_entry"] = fg
    t.update(extra)
    return t


# ---- le fasce --------------------------------------------------------------- #
def test_fasce_regime_sono_terzili_con_n_win_rate_e_pnl_medio():
    pairs = [(0.2, -0.02), (0.3, -0.01), (0.5, 0.0), (0.6, 0.01), (0.8, 0.02), (0.9, 0.03)]
    f = fasce_regime(pairs)
    assert [x["n"] for x in f] == [2, 2, 2]
    assert f[0]["min"] == 0.2 and f[0]["max"] == 0.3 and f[0]["fascia"] == "0.20-0.30"
    assert f[0]["win_rate"] == 0.0 and f[0]["pnl_medio"] == -0.015
    assert f[-1]["win_rate"] == 1.0 and f[-1]["pnl_medio"] == 0.025
    assert fasce_regime(pairs[:2]) == []


def test_fasce_fear_greed_sono_fisse_e_le_vuote_restano():
    f = fasce_fear_greed([(10, 0.01), (25, -0.01), (26, 0.02), (74, 0.02), (75, -0.03)])
    assert [x["fascia"] for x in f] == ["<=25", "26-74", ">=75"]
    assert [x["n"] for x in f] == [2, 2, 1]
    assert f[0]["win_rate"] == 0.5 and f[0]["pnl_medio"] == 0.0
    assert f[2]["pnl_medio"] == -0.03
    vuote = fasce_fear_greed([])
    assert [x["n"] for x in vuote] == [0, 0, 0]
    assert vuote[0]["win_rate"] is None and vuote[0]["pnl_medio"] is None


def test_verdetto_regime_dichiara_il_campione_insufficiente():
    assert MIN_PER_FASCIA == 10
    piccole = [{"n": 9, "pnl_medio": -0.01}, {"n": 10, "pnl_medio": 0.0}, {"n": 10, "pnl_medio": 0.01}]
    assert verdetto_fasce(piccole) == INSUFFICIENTE_FASCE
    assert verdetto_fasce([]) == INSUFFICIENTE_FASCE
    ok = [{"n": 10, "pnl_medio": -0.01}, {"n": 10, "pnl_medio": 0.0}, {"n": 10, "pnl_medio": 0.01}]
    assert verdetto_fasce(ok) == CRESCE
    assert verdetto_fasce(list(reversed(ok))) == PIATTA
    assert verdetto_fasce([{"n": 10, "pnl_medio": 0.01}] * 3) == PIATTA     # uguale = piatta


# ---- dentro calibrate: misure, non decisioni ------------------------------- #
def test_calibrate_porta_le_due_misure_e_trust_non_le_guarda(monkeypatch):
    """Regime che «cresce» e F&G pieno, ma confidenza costante a 60: il
    verdetto resta «costante» e trust 1.0. Le misure ci sono lo stesso."""
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    trades = ([_t(-0.02, reg=0.2, fg=10) for _ in range(10)]
              + [_t(0.0, reg=0.5, fg=50) for _ in range(10)]
              + [_t(0.03, reg=0.9, fg=90) for _ in range(10)])
    out = calibrate(iter(trades))          # un iteratore basta: si legge una volta
    assert out["verdict"] == "costante" and out["trust"] == 1.0
    assert confidence_trust(out) == 1.0
    reg = out["regime_confidence"]
    assert reg["trades"] == 30 and reg["verdetto_regime"] == CRESCE
    assert [f["n"] for f in reg["fasce"]] == [10, 10, 10]
    fg = out["fear_greed"]
    assert fg["trades"] == 30
    assert [(f["fascia"], f["n"], f["win_rate"]) for f in fg["fasce"]] == [
        ("<=25", 10, 0.0), ("26-74", 10, 0.0), (">=75", 10, 1.0)]


def test_le_misure_ci_sono_in_ogni_verdetto(monkeypatch):
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 30)
    # insufficient (confidenza varia, pochi trade)
    out = calibrate([_t(-0.01, conf=30, reg=0.3), _t(0.01, conf=80, reg=0.8)])
    assert out["verdict"] == "insufficient"
    assert out["regime_confidence"]["verdetto_regime"] == INSUFFICIENTE_FASCE
    assert out["regime_confidence"]["trades"] == 2 and out["fear_greed"]["trades"] == 0
    # ok / flat / inverted: stesso contratto
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 10)
    out = calibrate([_t(-0.02, conf=30), _t(0.03, conf=80)] * 6)
    assert out["verdict"] in ("ok", "flat", "inverted")
    assert "regime_confidence" in out and "fear_greed" in out
    assert out["regime_confidence"]["fasce"] == []


def test_ogni_misura_usa_i_suoi_trade_noti_e_esclude_esterni_ed_esplorativi():
    trades = ([_t(0.01, reg=0.5) for _ in range(4)]               # regime si', F&G no
              + [_t(0.01, fg=50) for _ in range(2)]                 # F&G si', regime no
              + [_t(-0.05, reg=0.9, fg=90, reason="kill_switch")]
              + [_t(-0.05, reg=0.9, fg=90, esplorativa=True)]
              + [_t(-0.05, reg="boh", fg="n/d")])                   # valori storti: fuori
    m = misure_contesto(trades)
    assert m["regime_confidence"]["trades"] == 4
    assert m["fear_greed"]["trades"] == 2
    assert sum(f["n"] for f in m["fear_greed"]["fasce"]) == 2


# ---- il documento su Firestore e trades ------------------------------------ #
def test_il_bot_pubblica_calibration_current_con_calibrate():
    import inspect
    from bot import main as bot_main
    src = inspect.getsource(bot_main.TradingBot._publish_calibration)
    assert "calibrate(trades)" in src and 'set_doc("calibration", "current"' in src


def test_trade_stats_stampa_le_fasce_del_regime_e_del_fg(monkeypatch, capsys):
    from scripts import trade_stats

    doc = calibrate([_t(-0.02, reg=0.2, fg=10)] * 10 + [_t(0.0, reg=0.5, fg=50)] * 10
                    + [_t(0.03, reg=0.9, fg=90)] * 10)

    class _FakeFB:
        def query_collection(self, *a, **k):
            return [{"strategy": "gen_x", "symbol": "AUSDT", "direction": "long", "pnl": -1.0,
                     "exit_reason": "stop_loss", "exit_ts": 1.0, "entry_ts": 0.5}]

        def get_doc(self, c, d):
            return doc if (c, d) == ("calibration", "current") else None

    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB())
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "CALIBRAZIONE (regime, F&G)" in out
    assert "confidenza del REGIME (terzili, 30 trade): verdetto cresce" in out
    assert "FEAR & GREED all'apertura (30 trade)" in out
    righe = [r for r in out.splitlines() if r.strip().startswith(">=75")]
    assert righe and "10" in righe[0] and "100%" in righe[0] and "+3.00%" in righe[0]


def test_trade_stats_senza_documento_o_vecchio_lo_dice(monkeypatch, capsys):
    from scripts import trade_stats

    class _FakeFB:
        doc = None

        def query_collection(self, *a, **k):
            return [{"strategy": "gen_x", "symbol": "AUSDT", "direction": "long", "pnl": -1.0,
                     "exit_reason": "stop_loss", "exit_ts": 1.0, "entry_ts": 0.5}]

        def get_doc(self, c, d):
            return self.doc if (c, d) == ("calibration", "current") else None

    fb = _FakeFB()
    monkeypatch.setattr(trade_stats, "get_firebase", lambda: fb)
    assert trade_stats.main() == 0
    assert "calibration/current non disponibile" in capsys.readouterr().out
    fb.doc = {"verdict": "costante", "trust": 1.0}          # documento del 25 set
    assert trade_stats.main() == 0
    assert "documento precedente al 26 set" in capsys.readouterr().out
