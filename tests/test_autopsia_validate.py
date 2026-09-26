"""AUTOPSIA DELLE VALIDATE (26 set 2026): misurare l'artefatto prima di toccare il gate.

Il giro completo del 26 set ha bocciato 167 validate su 182. Un revisore ha
trovato che `evaluate_spec` fa la PRESELEZIONE (passo 1) sempre con la
configurazione GLOBALE di scala/BE/keep, e cerca quella per coppia solo
`if passed`: una coppia che il bot opera a 2/4/6 con keep 0,75 viene rigiudicata
su 1,5/3/5 con keep 0,5. Prima di cambiare il gate, `scripts/autopsia_validate.py`
misura quante bocciature spariscono col passo 1 sulla configurazione operata.

Qui si difendono le quattro cose che rendono quella misura credibile:
  * il gate NON cambia: `config_iniziale` ha default None, la discovery non lo
    passa, e senza di esso `evaluate_spec` fa esattamente le passate di prima;
  * col parametro, la configurazione forzata entra SOLO al passo 1: la ricerca
    del passo 2 parte ancora dai candidati globali, e le metriche finali si
    rifanno sulla configurazione scelta;
  * le funzioni pure (`pf_recente`, `classifica`, `config_operata`, il riassunto)
    dicono quello che dicono;
  * lo script e' in sola lettura, parte senza argomenti (voce ops) e senza
    Firebase esce con 0.
"""
import inspect
import os
from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd
import pytest

from backtesting.engine import GateVerdict, SimTrade, StrategyStats
from bot.config import settings
from scripts import autopsia_validate as av
from scripts import discover_strategies as d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIORNO = 86400.0
NOW = 1_800_000_000.0


# --------------------------------------------------------------------------- #
# i finti: un motore che registra i params visti a ogni passata                #
# --------------------------------------------------------------------------- #
class _Candle:
    def __init__(self, ts):
        self.open_time = ts


def _trade(pnl: float, ts: float = NOW) -> SimTrade:
    return SimTrade(strategy="gen_a", regime="sideways", direction="long",
                    entry_price=1.0, exit_price=1.0, pnl_pct=pnl, max_adverse_pct=0.0,
                    confidence=60, is_win=pnl > 0, pnl=pnl * 100, symbol="XUSDT",
                    regime_at_entry="sideways", mfe_r=1.0, bars_held=5, entry_ts=ts)


class _Bt:
    """Due trade per passata; il vincente rende di piu' con la scala 2/4/6, cosi'
    la scelta del passo 2 e' deterministica e si vede nei params dell'ultima
    passata."""

    def __init__(self):
        self.chiamate: list[dict] = []

    def run_strategy(self, g, symbol, candles, frame=None, context_by_ts=None):
        p = dict(getattr(g, "params", {}) or {})
        self.chiamate.append(p)
        vinto = 0.03 if list(p.get("scale_r_mults") or []) == [2.0, 4.0, 6.0] else 0.02
        st = StrategyStats(strategy=g.name)
        st.trades.extend([_trade(vinto, NOW - 10 * GIORNO), _trade(-0.01, NOW - 5 * GIORNO)])
        return st


class _Opt:
    holdout_bars = 1

    def __init__(self, bt):
        self.bt = bt
        self.holdout_params = None

    def split_holdout(self, candles):
        return candles[:-1], len(candles) - 1

    def _windows(self, n):
        return [(0, 0, 0, n)]

    def _holdout_check(self, g, symbol, candles, frame, cut, context_by_ts=None):
        self.holdout_params = dict(getattr(g, "params", {}) or {})
        return {"ok": True, "pf": 2.0, "pnl_pct": 0.02, "trades": 2}


def _valuta(monkeypatch, bt, passa=True, config_iniziale=None):
    monkeypatch.setattr(d, "gate_verdict",
                        lambda *a, **k: GateVerdict(ok=passa, failed=() if passa else ("pf",),
                                                    binding="" if passa else "pf"))
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)
    candles = [_Candle(datetime(2026, 9, 26, tzinfo=timezone.utc))] * 4
    frame = pd.DataFrame({"close": [1.0] * 4})
    opt = _Opt(bt)
    kw = {} if config_iniziale is None else {"config_iniziale": config_iniziale}
    r = d.evaluate_spec(opt, "XUSDT", candles, frame,
                        {"id": "gen_a", "features": [{"kind": "rsi_extreme"}]},
                        scale_candidates=[(1.5, 3.0, 5.0), (2.0, 4.0, 6.0)],
                        keep_candidates=(0.35, 0.5, 0.65), **kw)
    return r, opt


OPERATA = {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": False, "profit_lock_keep": 0.75}


# --------------------------------------------------------------------------- #
# 1. il gate non cambia                                                        #
# --------------------------------------------------------------------------- #
def test_config_iniziale_ha_default_none_e_la_discovery_non_lo_passa():
    sig = inspect.signature(d.evaluate_spec)
    assert "config_iniziale" in sig.parameters
    assert sig.parameters["config_iniziale"].default is None
    for fn in (d._disc_one, d.conferme_retroattive):
        assert "config_iniziale" not in inspect.getsource(fn), \
            "la discovery deve giudicare come prima: il parametro e' SOLO dell'autopsia"
    src = inspect.getsource(d.evaluate_spec)
    # il passo 2 e' invariato: la scala si cerca una volta, sui candidati; il
    # verdetto resta su due chiamate; la passata finale porta la scelta intera
    assert src.count("_run_oos(cand") == 1 and src.count("gate_verdict(") == 2
    assert "_run_oos(best_ladder, best_be, keep=best_keep)" in src


def test_senza_config_iniziale_le_passate_sono_quelle_di_prima(monkeypatch):
    # bocciata al passo 1: UNA passata, senza params (la configurazione globale)
    bt = _Bt()
    r, opt = _valuta(monkeypatch, bt, passa=False)
    assert r["passed"] is False and len(bt.chiamate) == 1 and bt.chiamate[0] == {}
    assert opt.holdout_params is None
    # passata: preselezione, 2 scale, BE alternativo, 2 keep, finale (2/4/6 vince
    # sulla globale -> si rifa'): 7 passate, come prima di oggi
    bt = _Bt()
    r, opt = _valuta(monkeypatch, bt, passa=True)
    assert r["passed"] is True and len(bt.chiamate) == 7
    assert bt.chiamate[0] == {}
    assert r["scale_r_mults"] == [2.0, 4.0, 6.0]
    assert bt.chiamate[-1] == {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": True,
                               "profit_lock_keep": 0.5}


# --------------------------------------------------------------------------- #
# 2. col parametro, la configurazione entra SOLO al passo 1                    #
# --------------------------------------------------------------------------- #
def test_la_configurazione_forzata_si_applica_alla_preselezione(monkeypatch):
    bt = _Bt()
    r, opt = _valuta(monkeypatch, bt, passa=False, config_iniziale=OPERATA)
    assert r["passed"] is False and len(bt.chiamate) == 1
    assert bt.chiamate[0] == OPERATA, "il passo 1 deve girare sulla configurazione operata"
    # e i numeri riportati sono quelli di QUELLA passata (+0,03 -0,01, non +0,02)
    assert r["pnl"] == pytest.approx(0.02) and r["pf"] == pytest.approx(3.0)
    assert opt.holdout_params is None


def test_il_passo_2_riparte_dai_candidati_globali_e_la_finale_si_rifa(monkeypatch):
    bt = _Bt()
    r, opt = _valuta(monkeypatch, bt, passa=True, config_iniziale=OPERATA)
    assert r["passed"] is True
    assert bt.chiamate[0] == OPERATA
    # la ricerca della scala (passate 2 e 3) NON eredita BE e keep forzati: sono
    # le stesse passate che farebbe il gate senza il parametro
    assert bt.chiamate[1] == {"scale_r_mults": [1.5, 3.0, 5.0]}
    assert bt.chiamate[2] == {"scale_r_mults": [2.0, 4.0, 6.0]}
    assert "profit_lock_keep" not in bt.chiamate[3]           # il BE alternativo
    # l'ultima passata e' la configurazione SCELTA, e l'holdout la riceve
    assert bt.chiamate[-1] == {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": True,
                               "profit_lock_keep": 0.5}
    assert opt.holdout_params == bt.chiamate[-1]


def test_con_la_configurazione_forzata_la_finale_si_rifa_anche_se_vince_la_globale(monkeypatch):
    """Senza questa regola, se il passo 2 sceglie la configurazione globale le
    metriche resterebbero quelle della passata forzata: un PF di una
    configurazione col verdetto di un'altra."""
    bt = _Bt()
    r, _ = _valuta(monkeypatch, bt, passa=True,
                   config_iniziale={"scale_r_mults": [2.0, 4.0, 6.0]})
    monkeypatch.setattr(d, "SCALE_LADDER_CANDIDATES", ((1.5, 3.0, 5.0),))
    bt2 = _Bt()
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    candles = [_Candle(datetime(2026, 9, 26, tzinfo=timezone.utc))] * 4
    r2 = d.evaluate_spec(_Opt(bt2), "XUSDT", candles, pd.DataFrame({"close": [1.0] * 4}),
                         {"id": "gen_a", "features": [{"kind": "rsi_extreme"}]},
                         scale_candidates=[(1.5, 3.0, 5.0)], keep_candidates=(0.5,),
                         config_iniziale={"scale_r_mults": [2.0, 4.0, 6.0]})
    assert r2["scale_r_mults"] == [1.5, 3.0, 5.0]
    assert bt2.chiamate[-1] == {"scale_r_mults": [1.5, 3.0, 5.0], "sl_to_breakeven": True,
                                "profit_lock_keep": 0.5}
    assert r2["pnl"] == pytest.approx(0.01)          # la globale, non la forzata (0,02)
    assert r["scale_r_mults"] == [2.0, 4.0, 6.0]


# --------------------------------------------------------------------------- #
# 3. le funzioni pure                                                          #
# --------------------------------------------------------------------------- #
def test_pf_recente_filtra_per_data_e_ignora_le_date_sconosciute():
    trades = [_trade(0.03, NOW - 10 * GIORNO), _trade(-0.01, NOW - 50 * GIORNO),
              _trade(0.02, NOW - 100 * GIORNO), _trade(-0.05, NOW - 200 * GIORNO),
              _trade(0.99, 0.0)]                      # entry_ts sconosciuto: fuori
    r45 = av.pf_recente(trades, 45, NOW)
    assert (r45["trades"], r45["pf"], r45["pnl"]) == (1, 999.0, 0.03)
    r120 = av.pf_recente(trades, 120, NOW)
    assert r120["trades"] == 3 and r120["pf"] == pytest.approx(5.0)
    assert r120["pnl"] == pytest.approx(0.04)
    r180 = av.pf_recente(trades, 180, NOW)
    assert r180["trades"] == 3                          # il -0,05 e' a 200 giorni
    assert av.pf_recente(trades, 365, NOW)["pf"] == pytest.approx(round(0.05 / 0.06, 3))


def test_pf_recente_convenzioni_e_dizionari():
    assert av.pf_recente([], 45, NOW) == {"giorni": 45.0, "trades": 0, "pf": None, "pnl": 0.0}
    solo_perdite = [{"entry_ts": NOW - 1, "pnl_pct": -0.02}]
    assert av.pf_recente(solo_perdite, 45, NOW)["pf"] == 0.0
    assert av.pf_recente([{"entry_ts": NOW - 1, "pnl_pct": 0.02}], 45, NOW)["pf"] == 999.0
    assert av.pf_recente([{"entry_ts": "x", "pnl_pct": 1}], 45, NOW)["trades"] == 0


def test_classifica():
    assert av.classifica(True, True) == "passa"
    assert av.classifica(False, True) == "artefatto"
    assert av.classifica(True, False) == "solo_globale"
    assert av.classifica(False, False) == "bocciata"
    assert set(av.CLASSI) == {"passa", "artefatto", "solo_globale", "bocciata"}


def test_config_operata_legge_come_il_bot(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)
    # validata prima dello scale-out: nessun campo -> la globale (e' quello che opera)
    assert av.config_operata(None) == av.config_globale()
    assert av.e_globale(av.config_operata({}))
    piena = av.config_operata({"scale_r_mults": [2, 4, 6], "sl_to_breakeven": False,
                               "profit_lock_keep": 0.75})
    assert piena == {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": False,
                     "profit_lock_keep": 0.75}
    assert not av.e_globale(piena)
    # un keep fuori range vale come assente, come per `lock_keep` nel bot
    assert av.config_operata({"profit_lock_keep": 5.0})["profit_lock_keep"] == 0.5
    assert av.config_str(piena) == "2/4/6 noBE keep0.75"


def test_coppie_da_autopsiare_raggruppa_per_coin_e_salta_con_un_motivo(monkeypatch):
    monkeypatch.setattr(settings, "ORCHESTRATOR_TIMEFRAME", "15m")
    ora = NOW
    def rec(sym, sid, **extra):
        r = {"symbol": sym, "strategy": sid, "pass_count": 3, "last_seen_at": ora,
             "generated": True}
        r.update(extra)
        return r
    pairs = {"A|gen_1": rec("A", "gen_1"), "A|gen_2": rec("A", "gen_2"),
             "B|gen_1": rec("B", "gen_1", last_params={"scale_r_mults": [2, 4, 6]}),
             "B|gen_h": rec("B", "gen_h"),                      # spec a 1 ora
             "C|gen_x": rec("C", "gen_x"),                      # spec sconosciuta
             "C|rsi_mean_reversion": rec("C", "rsi_mean_reversion", generated=False),
             "D|gen_1": rec("D", "gen_1", pass_count=2)}        # non validata
    specs = {"gen_1": {"id": "gen_1", "features": []}, "gen_2": {"id": "gen_2", "features": []},
             "gen_h": {"id": "gen_h", "features": [], "timeframe": "1h"}}
    lavoro, saltate = av.coppie_da_autopsiare(pairs, specs, "15m", now=ora)
    assert [s for s, _ in lavoro] == ["A", "B"]                 # A ha 2 coppie: prima
    assert [k for _, l in lavoro for k, _s, _c in l] == ["A|gen_1", "A|gen_2", "B|gen_1"]
    assert lavoro[1][1][0][2]["scale_r_mults"] == [2.0, 4.0, 6.0]
    assert saltate == {"altro_timeframe": 1, "senza_spec": 1, "base": 1}
    # --limit taglia le coppie, tenendo i gruppi
    lim, _ = av.coppie_da_autopsiare(pairs, specs, "15m", now=ora, limit=2)
    assert [k for _, l in lim for k, _s, _c in l] == ["A|gen_1", "A|gen_2"]
    # a 1 ora si valuta la spec a 1 ora e le altre sono «altro timeframe»
    l1h, s1h = av.coppie_da_autopsiare(pairs, specs, "1h", now=ora)
    assert [k for _, l in l1h for k, _s, _c in l] == ["B|gen_h"] and s1h["altro_timeframe"] == 3


# --------------------------------------------------------------------------- #
# 4. il worker: (A), (B) solo se serve, (C) dai trade della serie intera       #
# --------------------------------------------------------------------------- #
class _BtC:
    """Per (C): i trade dipendono dalla scala nei params, cosi' si vede che la
    storia recente e' misurata sulla configurazione OPERATA."""
    def __init__(self):
        self.chiamate = []

    def run_strategy(self, g, symbol, candles, frame=None, context_by_ts=None):
        p = dict(getattr(g, "params", {}) or {})
        self.chiamate.append((symbol, p, len(candles)))
        st = StrategyStats(strategy=g.name)
        if list(p.get("scale_r_mults") or []) == [2.0, 4.0, 6.0]:
            st.trades.extend([_trade(-0.02, NOW - 30 * GIORNO), _trade(0.01, NOW - 100 * GIORNO)])
        else:
            st.trades.extend([_trade(0.05, NOW - 30 * GIORNO)])
        return st


def test_una_coin_fa_A_B_e_C_e_salta_B_se_la_configurazione_e_globale(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)
    candele = [_Candle(datetime.fromtimestamp(NOW - (300 - i) * GIORNO, tz=timezone.utc))
               for i in range(301)]
    monkeypatch.setattr(av, "load_candles", lambda *a, **k: candele)
    monkeypatch.setattr(av, "looks_delisted", lambda *a, **k: False)
    monkeypatch.setattr(av, "compute_indicator_frame", lambda c: pd.DataFrame({"close": [1.0] * len(c)}))
    bt = _BtC()
    stato = dict(opt=SimpleNamespace(bt=bt), end="2026-09-26", min_history=10,
                 args=SimpleNamespace(interval="15m", start="2022-01-01", source="auto", windows=3),
                 scala_paper=None, keep_paper=None, scale_strategie={}, btc_ctx=None)
    monkeypatch.setattr(d, "_W", stato)
    monkeypatch.setattr(av, "_S", {"deadline": 0.0})
    visto = []

    def finto_evaluate(opt, sym, candles, frame, spec, **kw):
        visto.append((spec["id"], kw.get("config_iniziale")))
        forzata = kw.get("config_iniziale")
        # con la configurazione operata la spec «gen_art» passa; con la globale no
        passa = bool(forzata) and spec["id"] == "gen_art"
        return {"passed": passa, "fail_binding": "" if passa else "pf", "pf": 1.2,
                "trades": 30, "holdout": {"ok": True} if passa else {}}
    monkeypatch.setattr(d, "evaluate_spec", finto_evaluate)

    globale = av.config_globale()
    operata = {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": False, "profit_lock_keep": 0.75}
    righe = av._una_coin(("XUSDT", [("XUSDT|gen_art", {"id": "gen_art", "features": []}, operata),
                                    ("XUSDT|gen_glob", {"id": "gen_glob", "features": []}, globale)]))
    assert [r["stato"] for r in righe] == ["ok", "ok"]
    art, glob = righe
    # (A) e (B) sulla coppia con configurazione propria; solo (A) sull'altra
    assert visto == [("gen_art", None), ("gen_art", operata), ("gen_glob", None)]
    assert art["classe"] == "artefatto" and art["stessa_config"] is False
    assert art["passa_a"] is False and art["binding_a"] == "pf" and art["holdout_a"] is None
    assert art["passa_b"] is True and art["holdout_b"] is True
    assert glob["classe"] == "bocciata" and glob["stessa_config"] is True
    # (C): una passata per coppia sulla serie INTERA, con la configurazione operata
    assert [(s, n) for s, _p, n in bt.chiamate] == [("XUSDT", 301), ("XUSDT", 301)]
    assert bt.chiamate[0][1] == operata and bt.chiamate[1][1] == globale
    assert art["recente"][45]["trades"] == 1 and art["recente"][45]["pf"] == 0.0
    assert art["recente"][120]["trades"] == 2 and art["recente"][120]["pf"] == pytest.approx(0.5)
    assert glob["recente"][45]["pf"] == 999.0
    assert "spec" not in art                              # non viaggia verso il main
    # la tabella si stampa senza sorprese
    assert "NO:pf" in av.riga_tabella(art) and "= A" in av.riga_tabella(glob)
    assert av.riga_tabella(art).startswith("XUSDT|gen_art")


def test_un_errore_su_una_coppia_non_ferma_la_coin(monkeypatch):
    candele = [_Candle(datetime.fromtimestamp(NOW - (30 - i) * GIORNO, tz=timezone.utc))
               for i in range(31)]
    monkeypatch.setattr(av, "load_candles", lambda *a, **k: candele)
    monkeypatch.setattr(av, "looks_delisted", lambda *a, **k: False)
    monkeypatch.setattr(av, "compute_indicator_frame", lambda c: pd.DataFrame({"close": [1.0] * len(c)}))
    monkeypatch.setattr(d, "_W", dict(opt=SimpleNamespace(bt=_BtC()), end="2026-09-26", min_history=1,
                                      args=SimpleNamespace(interval="15m", start="2022-01-01",
                                                           source="auto", windows=3)))
    monkeypatch.setattr(av, "_S", {"deadline": 0.0})

    def rotto(opt, sym, candles, frame, spec, **kw):
        if spec["id"] == "gen_ko":
            raise RuntimeError("motore rotto")
        return {"passed": True, "fail_binding": "", "pf": 1.5, "trades": 20, "holdout": {"ok": True}}
    monkeypatch.setattr(d, "evaluate_spec", rotto)
    g = av.config_globale()
    righe = av._una_coin(("YUSDT", [("YUSDT|gen_ko", {"id": "gen_ko", "features": []}, g),
                                    ("YUSDT|gen_ok", {"id": "gen_ok", "features": []}, g)]))
    assert [r["stato"] for r in righe] == ["errore", "ok"]
    assert "motore rotto" in righe[0]["errore"] and righe[1]["classe"] == "passa"
    # poca storia e deadline scaduta: righe con lo stato, mai un'eccezione
    monkeypatch.setattr(av, "load_candles", lambda *a, **k: candele[:0])
    monkeypatch.setattr(d._W, "min_history", 5) if False else d._W.update(min_history=5)
    assert [r["stato"] for r in av._una_coin(("Z", [("Z|gen_ok", {"id": "gen_ok"}, g)]))] == ["storia"]
    monkeypatch.setattr(av, "_S", {"deadline": 1.0})
    assert [r["stato"] for r in av._una_coin(("Z", [("Z|gen_ok", {"id": "gen_ok"}, g)]))] == ["tempo"]


# --------------------------------------------------------------------------- #
# 5. il riassunto e la lettura                                                 #
# --------------------------------------------------------------------------- #
def _r(key, classe, b_a="", b_b="", pf120=None, n120=0, stessa=False):
    passa_a = classe in ("passa", "solo_globale")
    passa_b = classe in ("passa", "artefatto")
    return {"key": key, "stato": "ok", "config": av.config_globale(), "classe": classe,
            "passa_a": passa_a, "passa_b": passa_b, "binding_a": b_a, "binding_b": b_b,
            "stessa_config": stessa,
            "recente": {45: {"pf": None, "trades": 0}, 120: {"pf": pf120, "trades": n120},
                        180: {"pf": pf120, "trades": n120}}}


def test_il_riassunto_conta_artefatti_binding_e_pf_recente(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)
    righe = [_r("A|1", "artefatto", "pf", "", 0.8, 5), _r("B|1", "artefatto", "trades", "", 1.3, 4),
             _r("C|1", "artefatto", "pf", "", None, 0),
             _r("D|1", "bocciata", "pf", "pf", 0.5, 9), _r("E|1", "bocciata", "holdout", "trades", 1.1, 2),
             _r("F|1", "passa", stessa=True, pf120=2.0, n120=3), _r("G|1", "solo_globale", "", "pf"),
             {"key": "H|1", "stato": "errore", "config": av.config_globale(), "errore": "x"},
             {"key": "I|1", "stato": "tempo", "config": av.config_globale()}]
    out = av.riassunto(righe, saltate={"base": 2, "altro_timeframe": 1}, n_validate=12)
    testo = "\n".join(out)
    assert out[0] == ("RIASSUNTO · 12 validate · 7 valutate · errore 1 · tempo 1 · "
                      "saltate: altro_timeframe 1, base 2")
    assert "(A) passano col gate di oggi (passo 1 = configurazione globale 1.5/3/5 BE keep0.5): 2 su 7" in testo
    assert "(B) passano col passo 1 sulla configurazione operata: 4 su 7 (1 operano gia' la configurazione globale: A = B)" in testo
    assert "ARTEFATTO della configurazione globale: 3 su 5 bocciate" in testo
    assert "passate in (A) ma bocciate in (B): 1" in testo
    assert "bocciate in entrambe: 2 · criterio binding (B): pf 1 · trades 1 · (A): pf 1 · holdout 1" in testo
    assert "PF < 1 negli ultimi 120 giorni (configurazione operata, serie intera): 2 su 5 con trade" in testo
    assert out[-1].startswith("  LETTURA: la maggior parte delle bocciature (3 su 5) e' un artefatto del passo 1")
    assert out[-1].endswith("Sugli ultimi 120 giorni 2 su 5 con trade hanno PF < 1 con la configurazione operata.")


def test_la_lettura_cambia_con_la_quota_di_artefatti():
    assert av.lettura(0, 0, 0, 0, 0, 0).startswith("nessuna coppia valutata")
    assert av.lettura(5, 5, 0, 0, 0, 0).startswith("tutte le 5 valutate passano")
    assert "la maggior parte delle bocciature (5 su 10)" in av.lettura(12, 2, 5, 10, 0, 0)
    assert "solo una parte delle bocciature (2 su 10)" in av.lettura(12, 2, 2, 10, 0, 0)
    assert av.lettura(12, 2, 0, 10, 0, 0).startswith("nessun artefatto: le 10 bocciature reggono")
    assert av.lettura(12, 2, 0, 10, 3, 8).endswith("3 su 8 con trade hanno PF < 1 con la configurazione operata.")
    vuoto = av.riassunto([], {}, n_validate=3)
    assert vuoto[0] == "RIASSUNTO · 3 validate · 0 valutate" and "niente da leggere" in vuoto[1]


# --------------------------------------------------------------------------- #
# 6. sola lettura, senza argomenti, senza Firebase                             #
# --------------------------------------------------------------------------- #
def test_e_in_sola_lettura_e_parte_senza_argomenti():
    # il CODICE, non la docstring del modulo (che spiega il contesto e nomina il merge)
    src = inspect.getsource(av).split('"""', 2)[-1]
    for vietato in ("set_doc", "merge_into_registry", "persist_specs", "set_rtdb",
                    "update_registry", "scrivi_registro"):
        assert vietato not in src, f"l'autopsia chiama `{vietato}`: deve solo misurare"
    sig = inspect.signature(av.main)
    assert not [p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]
    main = inspect.getsource(av.main)
    assert "ap.error(" not in main and '"--limit"' in main and '"--budget"' in main
    # lo STESSO initializer dei worker della discovery, e le stesse candidate dal paper
    assert "d._disc_init(args, end, [], scala_paper, None, None, False, keep_paper, scale_strategie)" \
        in inspect.getsource(av._init)
    for riga in ("keep_paper = d.keep_dal_paper(fb, trades=trades_paper)",
                 "scala_paper = d.scala_dal_paper(fb, trades=trades_paper)",
                 "scale_strategie = d.scale_per_strategia(trades_paper or [])"):
        assert riga in main
    assert "parallel_map(_una_coin" in main and av.WORKERS == 6
    assert av.BUDGET_S < 900, "la deadline propria deve stare sotto il timeout del canale ops"


def test_senza_firebase_esce_con_zero_e_lo_dice(monkeypatch, capsys):
    class _FB:
        def get_doc(self, *a):
            return None
    monkeypatch.setattr(av, "get_firebase", lambda: _FB())
    monkeypatch.setattr("sys.argv", ["autopsia_validate"])
    assert av.main() == 0
    assert "nessuna validata" in capsys.readouterr().out


def test_la_voce_ops_e_in_lista_bianca_di_esempio():
    from scripts.ops_agent import parse_allowlist
    with open(os.path.join(ROOT, "ops", "allowlist.example"), encoding="utf-8") as f:
        voci = parse_allowlist(f.read())
    v = voci["autopsia-validate"]
    assert v["cmd"] == ".venv/bin/python -m scripts.autopsia_validate" and not v["args"]
