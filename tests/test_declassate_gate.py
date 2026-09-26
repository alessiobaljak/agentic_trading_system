"""LE VALIDATE GIUDICATE SULLA PROPRIA CONFIGURAZIONE, E LE DECLASSATE (26 set 2026).

Il primo giro completo del 26 set ha bocciato 167 validate su 182. Due cause
trovate dai revisori e chiuse qui, lato gate (passo 2 del piano del 26 set):

  1. `evaluate_spec` giudicava OGNI coppia al passo 1 sulla scala/BE/keep
     GLOBALI, mentre una validata opera i suoi `last_params`. Ora `_disc_one`
     passa alle sole coppie GIA' validate la configurazione operata
     (`config_iniziale`, letta dal registro con le funzioni del bot), e il passo
     2 la tiene a meno che un candidato non la batta sul metro della scelta di
     almeno CONFIG_MARGINE (isteresi, stesso numero dell'intorno). Si conta
     quante sono passate SOLO grazie alla propria configurazione;
  2. una validata bocciata non lasciava traccia in `out`: una figlia
     dell'intorno con la madre bocciata moriva come «madre non valutata», e il
     merge non poteva contare le bocciature. Ora `_disc_one` ritorna le validate
     bocciate come voci LEGGERE; il merge le usa per il confronto figlia/madre e,
     SOLO nel giro completo, per i contatori delle DECLASSATE (`bocciata_notti`,
     `declassata`, `declassata_at`): due notti di fila = un quarto della size nel
     bot, mai un rifiuto, mai un tocco a pass_count, finestre o purga.

Le soglie (DECLASSATA_NOTTI, DECLASSATA_SIZE_MULT, CONFIG_MARGINE) sono
dichiarate nel codice PRIMA di ogni misura, non tarate sul paper.
"""
import inspect
import os
import re
import sys
import time
from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd
import pytest

from backtesting.engine import GateVerdict, SimTrade, StrategyStats
from bot.config import settings
from bot.core import registry as reg
from bot.core.firebase_client import decode_pairs, encode_pairs
from bot.strategies.generated import spec_id
from bot.strategies.generator import figlie_intorno
from scripts import discover_strategies as d
from scripts import gate_progress as g
from scripts.optimize import MIN_PASSES, REGISTRY_CORE_FIELDS, slim_registry

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = 1_800_000_000.0
GLOBALE = {"scale_r_mults": [1.5, 3.0, 5.0], "sl_to_breakeven": True, "profit_lock_keep": 0.5}
OPERATA = {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": False, "profit_lock_keep": 0.75}


# --------------------------------------------------------------------------- #
# i finti                                                                      #
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
    """Due trade per passata (+resa(params), -0,01): con l'emivita a 0 il metro
    della scelta e' `resa - 0,02` (somma meno drawdown), cosi' i confronti con il
    margine si fanno a mano."""

    def __init__(self, resa):
        self.resa = resa
        self.chiamate: list[dict] = []

    def run_strategy(self, g, symbol, candles, frame=None, context_by_ts=None):
        p = dict(getattr(g, "params", {}) or {})
        self.chiamate.append(p)
        st = StrategyStats(strategy=g.name)
        st.trades.extend([_trade(self.resa(p)), _trade(-0.01)])
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


def _globale(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 0.0)


def _valuta(monkeypatch, bt, config_iniziale=None, verdetto=None):
    """`verdetto(pnl)` decide il pass del finto `gate_verdict` (default: passa)."""
    _globale(monkeypatch)

    def _gv(window_pnls, n, pf, win, pnl, **k):
        ok = True if verdetto is None else bool(verdetto(pnl))
        return GateVerdict(ok=ok, failed=() if ok else ("pf",), binding="" if ok else "pf")
    monkeypatch.setattr(d, "gate_verdict", _gv)
    candles = [_Candle(datetime(2026, 9, 26, tzinfo=timezone.utc))] * 4
    frame = pd.DataFrame({"close": [1.0] * 4})
    opt = _Opt(bt)
    r = d.evaluate_spec(opt, "XUSDT", candles, frame,
                        {"id": "gen_a", "features": [{"kind": "rsi_extreme"}]},
                        scale_candidates=[(1.5, 3.0, 5.0), (2.0, 4.0, 6.0)],
                        keep_candidates=(0.35, 0.5, 0.65), config_iniziale=config_iniziale)
    return r, opt


def _resa(keep_65: float):
    """2/4/6 rende 0,03 (0,02 le altre scale); col keep 0,65 rende `keep_65`."""
    def resa(p):
        if list(p.get("scale_r_mults") or []) != [2.0, 4.0, 6.0]:
            return 0.02
        return keep_65 if p.get("profit_lock_keep") == 0.65 else 0.03
    return resa


# --------------------------------------------------------------------------- #
# 1. le soglie sono dichiarate, e la regola del margine e' una                 #
# --------------------------------------------------------------------------- #
def test_le_soglie_sono_dichiarate_nel_codice():
    assert settings.DECLASSATE_ENABLED is True
    assert settings.DECLASSATA_SIZE_MULT == pytest.approx(0.25)
    assert settings.DECLASSATA_NOTTI == 2
    assert d.CONFIG_MARGINE == pytest.approx(0.10) == pytest.approx(d.INTORNO_MARGINE)


def test_batte_con_margine_e_la_regola_dell_intorno():
    assert d._batte_con_margine(1.1, 1.0, 0.10) is True          # esattamente il 10%
    assert d._batte_con_margine(1.0999, 1.0, 0.10) is False
    assert d._batte_con_margine(0.5, 1.0, 0.10) is False
    assert d._batte_con_margine(0.001, 0.0, 0.10) is True         # vecchio non positivo: basta > 0
    assert d._batte_con_margine(0.0, -0.5, 0.10) is False
    assert d._batte_con_margine(None, None, 0.10) is False
    # `_batte_per_finestra` la usa: una sola regola in un posto solo
    assert "_batte_con_margine(" in inspect.getsource(d._batte_per_finestra)


def test_la_configurazione_operata_si_legge_come_il_bot(monkeypatch):
    _globale(monkeypatch)
    assert d.config_operata(None) == GLOBALE and d.config_operata({}) == GLOBALE
    assert d.config_operata({"scale_r_mults": [2, 4, 6], "sl_to_breakeven": False,
                             "profit_lock_keep": 0.75}) == OPERATA
    # un keep fuori range vale come assente, come per `lock_keep` nel bot
    assert d.config_operata({"profit_lock_keep": 5.0})["profit_lock_keep"] == 0.5
    assert d.stessa_config(GLOBALE, d.config_globale_uscita())
    assert not d.stessa_config(OPERATA, GLOBALE) and not d.stessa_config(None, GLOBALE)
    pairs = {"A|gen_a": {"last_params": {"scale_r_mults": [2, 4, 6], "sl_to_breakeven": False,
                                         "profit_lock_keep": 0.75}},
             "B|gen_b": {"last_params": {}}, "C|gen_c": {}, "Z|gen_z": "storto"}
    cfg = d.config_validate_dal_registro(pairs, ["A|gen_a", "B|gen_b", "C|gen_c", "Z|gen_z", "X|no"])
    assert cfg == {"A|gen_a": OPERATA, "B|gen_b": GLOBALE, "C|gen_c": GLOBALE}


# --------------------------------------------------------------------------- #
# 2. evaluate_spec: isteresi e misura «solo con la propria configurazione»     #
# --------------------------------------------------------------------------- #
def test_senza_config_iniziale_niente_cambia(monkeypatch):
    bt = _Bt(_resa(0.03))
    r, opt = _valuta(monkeypatch, bt)
    # preselezione, 2 scale, BE, 2 keep, finale (2/4/6 vince sulla globale)
    assert len(bt.chiamate) == 7 and bt.chiamate[0] == {}
    assert r["scale_r_mults"] == [2.0, 4.0, 6.0] and r["solo_propria_config"] is False
    assert bt.chiamate[-1] == {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": True,
                               "profit_lock_keep": 0.5}


def test_l_operata_resta_se_nessun_candidato_la_batte_del_margine(monkeypatch):
    # il candidato migliore (keep 0,65: metro 0,0109) non batte l'operata
    # (0,03 - 0,02 = 0,01) del 10%: la scelta E' la configurazione operata
    bt = _Bt(_resa(0.0309))
    r, opt = _valuta(monkeypatch, bt, config_iniziale=OPERATA)
    assert r["passed"] is True
    assert (r["scale_r_mults"], r["sl_to_breakeven"], r["profit_lock_keep"]) == \
        ([2.0, 4.0, 6.0], False, 0.75)
    # passate: operata, 2 scale, BE alternativo, 2 keep, poi SOLO la misura sulla
    # globale (passo 4): nessuna passata finale, i numeri del passo 1 sono gia' i suoi
    assert bt.chiamate[0] == OPERATA and len(bt.chiamate) == 7
    assert bt.chiamate[1] == {"scale_r_mults": [1.5, 3.0, 5.0]}          # la ricerca parte dai globali
    assert bt.chiamate[-1] == {}
    assert r["pnl"] == pytest.approx(0.02) and r["pf"] == pytest.approx(3.0)
    # l'holdout riceve la configurazione operata, intera
    assert opt.holdout_params == OPERATA
    # la globale passa (verdetto finto sempre ok): NON e' passata solo grazie alla sua
    assert r["solo_propria_config"] is False


def test_un_candidato_che_batte_l_operata_del_margine_vince(monkeypatch):
    # keep 0,65: metro 0,012 >= 0,01 x 1,1: la ricerca vince, con BE default e keep 0,65
    bt = _Bt(_resa(0.032))
    r, opt = _valuta(monkeypatch, bt, config_iniziale=OPERATA)
    assert (r["scale_r_mults"], r["sl_to_breakeven"], r["profit_lock_keep"]) == \
        ([2.0, 4.0, 6.0], True, 0.65)
    # ...e le metriche finali si rifanno sulla configurazione scelta
    assert len(bt.chiamate) == 8
    assert bt.chiamate[-2] == {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": True,
                               "profit_lock_keep": 0.65}
    assert bt.chiamate[-1] == {}                       # la misura sulla globale
    assert r["pnl"] == pytest.approx(0.022) and opt.holdout_params == bt.chiamate[-2]


def test_passata_solo_grazie_alla_propria_configurazione(monkeypatch):
    # la globale rende 0,02 - 0,01 = 0,01 e il verdetto finto la boccia: la
    # coppia passa SOLO con la sua configurazione, e lo si conta
    bt = _Bt(_resa(0.03))
    r, _ = _valuta(monkeypatch, bt, config_iniziale=OPERATA, verdetto=lambda pnl: pnl > 0.015)
    assert r["passed"] is True and r["solo_propria_config"] is True
    assert bt.chiamate[-1] == {}
    # se la stessa spec non passa nemmeno con la sua: bocciata, UNA passata, niente misura
    bt = _Bt(_resa(0.03))
    r, opt = _valuta(monkeypatch, bt, config_iniziale=OPERATA, verdetto=lambda pnl: False)
    assert r["passed"] is False and r["solo_propria_config"] is False
    assert len(bt.chiamate) == 1 and opt.holdout_params is None


def test_chi_opera_la_globale_non_paga_la_misura_in_piu(monkeypatch):
    """Una validata prima dello scale-out opera la globale: la sua configurazione
    E' la globale, l'isteresi la tiene (nessun candidato la batte) e la passata
    del passo 4 non si fa (sarebbe la stessa)."""
    bt = _Bt(lambda p: 0.02)
    r, _ = _valuta(monkeypatch, bt, config_iniziale=dict(GLOBALE))
    assert (r["scale_r_mults"], r["sl_to_breakeven"], r["profit_lock_keep"]) == \
        ([1.5, 3.0, 5.0], True, 0.5)
    assert len(bt.chiamate) == 6 and bt.chiamate[-1] != {}
    assert r["solo_propria_config"] is False


def test_il_verdetto_resta_sui_numeri_non_pesati_anche_al_passo_4():
    src = inspect.getsource(d.evaluate_spec)
    assert src.count("gate_verdict(") == 3            # preselezione, finale, misura sulla globale
    for riga in src.splitlines():
        if "gate_verdict(" in riga:
            assert "_metrica_scelta" not in riga and "weighted" not in riga
    assert "_batte_con_margine(rif_metric, metrica_operata," in src
    assert "CONFIG_MARGINE" in src


# --------------------------------------------------------------------------- #
# 3. _disc_one: la configurazione solo alle validate, le bocciate leggere      #
# --------------------------------------------------------------------------- #
def _spec(**extra):
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                         {"kind": "session", "hour_from": 8, "hour_to": 16}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec.update(extra)
    spec["id"] = spec_id(spec)
    return spec


def _esito_finto(passa: bool, con_config) -> dict:
    return {"passed": passa, "pf": 1.2 if passa else 0.8, "pnl": 0.3 if passa else -0.1,
            "trades": 30, "win": 0.5, "holdout": {"ok": True} if passa else {},
            "regime_pf": {}, "max_dd": 0.1,
            "scale_r_mults": [1.5, 3.0, 5.0] if passa else None,
            "sl_to_breakeven": True if passa else None,
            "profit_lock_keep": 0.5 if passa else None, "data_end": NOW,
            "fail_criteria": [] if passa else ["pf", "total_return"],
            "fail_binding": "" if passa else "pf", "fail_shortfall": 0.0 if passa else 0.2,
            "near_miss": False, "t_stat": 1.1, "oos_rows": [],
            "window_pnls": [0.1, 0.2, 0.0], "direzione_pf": {},
            "solo_propria_config": bool(passa and con_config)}


def test_disc_one_passa_la_configurazione_solo_alle_validate_e_ritorna_le_bocciate(monkeypatch):
    validata_ko, validata_ok, nuova = _spec(volume_mult=1.5), _spec(volume_mult=2.0), _spec(min_adx=20.0)
    chiavi = {s["id"]: f"XUSDT|{s['id']}" for s in (validata_ko, validata_ok, nuova)}
    cfg = {chiavi[validata_ko["id"]]: OPERATA, chiavi[validata_ok["id"]]: OPERATA}
    prima = dict(d._W)
    visto = []

    def finto(opt, sym, candles, frame, spec, **kw):
        visto.append((spec["id"], kw.get("config_iniziale")))
        return _esito_finto(spec["id"] != validata_ko["id"], kw.get("config_iniziale"))
    try:
        d._W.clear()
        d._W.update(opt=SimpleNamespace(bt=None), end="2026-09-26", min_history=2,
                    args=SimpleNamespace(interval="15m", start="2022-01-01", source="auto"),
                    specs=[validata_ko, validata_ok, nuova], scala_paper=None, keep_paper=None,
                    scale_strategie={}, btc_ctx=None, specs_per_symbol={}, bocciate_ok=False,
                    gia_validate=set(cfg), config_validate=cfg)
        monkeypatch.setattr(d, "load_candles", lambda *a, **k: [_Candle(datetime(2026, 9, 26, tzinfo=timezone.utc))] * 4)
        monkeypatch.setattr("backtesting.quality.looks_delisted", lambda *a, **k: False)
        monkeypatch.setattr(d, "compute_indicator_frame", lambda c: pd.DataFrame({"close": [1.0] * len(c)}))
        monkeypatch.setattr(d, "evaluate_spec", finto)
        ris = d._disc_one("XUSDT")
    finally:
        d._W.clear()
        d._W.update(prima)
    assert len(ris) == 9
    sym, entries, p_keys, p_specs, n_ev, summary, diag, righe, bocciate = ris
    # la configurazione operata SOLO alle validate; la candidata nuova come prima
    assert visto == [(validata_ko["id"], OPERATA), (validata_ok["id"], OPERATA), (nuova["id"], None)]
    assert n_ev == 3 and sorted(p_keys) == sorted([chiavi[validata_ok["id"]], chiavi[nuova["id"]]])
    # la validata bocciata: una voce LEGGERA con il perche' e i numeri del confronto
    assert set(bocciate) == {chiavi[validata_ko["id"]]}
    voce = bocciate[chiavi[validata_ko["id"]]]
    assert voce == {"symbol": "XUSDT", "strategy": validata_ko["id"],
                    "fail_binding": "pf", "fail_criteria": ["pf", "total_return"],
                    "pf": 0.8, "trades": 30, "holdout_ok": None, "data_end": NOW,
                    "oos_pnl_pct": -0.1, "oos_max_dd": 0.1, "window_pnls": [0.1, 0.2, 0.0]}
    assert "spec" not in voce and "oos_rows" not in voce
    # una candidata nuova bocciata NON e' fra le bocciate (non era validata): solo l'autopsia
    assert diag["binding"] == {"pf": 1}
    # la passata SOLO con la propria configurazione lo dice nell'entry
    assert entries[chiavi[validata_ok["id"]]]["solo_propria_config"] is True
    assert entries[chiavi[nuova["id"]]]["solo_propria_config"] is False


def test_disc_init_riceve_la_configurazione_delle_validate_in_coda_con_default(monkeypatch):
    sig = inspect.signature(d._disc_init)
    assert list(sig.parameters)[-1] == "config_validate" and sig.parameters["config_validate"].default is None
    prima = dict(d._W)
    try:
        monkeypatch.setattr(d, "WalkForwardOptimizer", lambda **k: SimpleNamespace(bt=None))
        monkeypatch.setattr(d, "load_candles", lambda *a, **k: [])
        args = SimpleNamespace(windows=3, interval="15m", start="2022-01-01", source="")
        d._disc_init(args, "2026-09-26", [], None, None, {"A|gen_a"}, False, None, None,
                     {"A|gen_a": OPERATA})
        assert d._W["config_validate"] == {"A|gen_a": OPERATA} and d._W["gia_validate"] == {"A|gen_a"}
        d._disc_init(args, "2026-09-26", [])            # l'autopsia chiama cosi': vuoto
        assert d._W["config_validate"] == {}
    finally:
        d._W.clear()
        d._W.update(prima)
    main = inspect.getsource(d.main)
    assert "config_validate = config_validate_dal_registro(" in main
    assert "bocciate_ok, keep_paper, scale_strategie, config_validate)" in main
    assert "summary, diag, rows, bocciate in parallel_map(" in main
    assert "bocciate_validate.update(bocciate or {})" in main
    assert "bocciate_validate=bocciate_validate," in main and 'completa=(modalita == "completa")' in main


# --------------------------------------------------------------------------- #
# 4. il merge: figlia contro madre bocciata, contatori delle declassate        #
# --------------------------------------------------------------------------- #
class _FB:
    def __init__(self, pairs=None, extra=None):
        self.docs = {}
        if pairs is not None:
            self.docs[("strategy_registry", "validated")] = {"pairs": encode_pairs(pairs)}
        for k, v in (extra or {}).items():
            self.docs[k] = v

    def get_doc(self, c, dname):
        return self.docs.get((c, dname), {})

    def set_doc(self, c, dname, data):
        self.docs[(c, dname)] = data

    def pairs(self) -> dict:
        return decode_pairs(self.docs[("strategy_registry", "validated")]["pairs"])


def _rec(pass_count=MIN_PASSES, **extra):
    r = {"generated": True, "pass_count": pass_count, "last_seen_at": 1e9, "last_pnl_pct": 0.5}
    r.update(extra)
    return r


def _entry(sym, spec, retro, pnl, dd, finestre):
    return {"symbol": sym, "strategy": spec["id"], "params": {}, "spec": spec,
            "oos_pf": 1.6, "oos_pnl_pct": pnl, "oos_max_dd": dd, "oos_trades": 40,
            "oos_win_rate": 0.5, "passed": True, "holdout": {"ok": True},
            "data_end": 1e9, "conferme_retro": retro, "window_pnls": finestre}


def _leggera(sym, spec, pnl, dd, finestre):
    return {"symbol": sym, "strategy": spec["id"], "fail_binding": "pf", "fail_criteria": ["pf"],
            "pf": 0.9, "trades": 40, "holdout_ok": None, "data_end": 1e9,
            "oos_pnl_pct": pnl, "oos_max_dd": dd, "window_pnls": finestre}


def test_una_figlia_puo_sostituire_la_madre_bocciata_oggi():
    madre = _spec()
    figlia = figlie_intorno(madre)[0]
    fb = _FB({f"{c}|{madre['id']}": _rec(strategy=madre["id"], symbol=c) for c in "ABC"})
    out = {
        # A: madre bocciata oggi (voce leggera), figlia la batte sul metro e in 3 finestre su 3
        f"A|{figlia['id']}": _entry("A", figlia, MIN_PASSES - 1, 0.62, 0.10, [0.2, 0.3, 0.12]),
        # B: madre bocciata oggi ma con numeri migliori della figlia: senza margine
        f"B|{figlia['id']}": _entry("B", figlia, MIN_PASSES - 1, 0.40, 0.10, [0.1, 0.1, 0.1]),
        # C: madre non valutata oggi (ne' passata ne' bocciata): nessun confronto, come prima
        f"C|{figlia['id']}": _entry("C", figlia, MIN_PASSES - 1, 0.90, 0.05, [0.3, 0.3, 0.3]),
    }
    bocciate = {f"A|{madre['id']}": _leggera("A", madre, 0.50, 0.10, [0.1, 0.2, 0.2]),
                f"B|{madre['id']}": _leggera("B", madre, 0.50, 0.10, [0.3, 0.3, 0.3])}
    esito = {}
    d.merge_into_registry(fb, out, list(out), evaluated_symbols=set("ABC"),
                          intorno_madri={f"{c}|{madre['id']}": 6 for c in "ABC"},
                          esito=esito, bocciate_validate=bocciate, completa=True)
    pairs = fb.pairs()
    assert pairs[f"A|{madre['id']}"]["sostituita_da"] == figlia["id"]
    assert pairs[f"A|{figlia['id']}"]["pass_count"] == MIN_PASSES
    assert not pairs[f"B|{madre['id']}"].get("sostituita_da") and f"B|{figlia['id']}" not in pairs
    assert not pairs[f"C|{madre['id']}"].get("sostituita_da") and f"C|{figlia['id']}" not in pairs
    assert esito["intorno"] == {"madri": 3, "figlie_passate": 3, "promosse": [f"A|{figlia['id']}"],
                                "senza_margine": 1, "madre_non_valutata": 1, "scartate": 0}
    # la madre bocciata e ancora operata (B) ha preso una notte (giro completo);
    # la sostituita (A) tiene il contatore (i tre campi sono nel nucleo dal 26
    # set: sopravvivono all'alleggerimento) ma non si opera piu' e NON conta fra
    # le declassate (`registry.declassate` guarda solo le validate); la madre non
    # valutata (C) resta intatta
    assert pairs[f"B|{madre['id']}"]["bocciata_notti"] == 1
    assert pairs[f"A|{madre['id']}"]["bocciata_notti"] == 1
    assert f"A|{madre['id']}" not in reg.declassate(pairs, reg.coppie_validate(pairs, time.time()))
    assert "bocciata_notti" not in pairs[f"C|{madre['id']}"]
    assert esito["declassate"] == {"totale": 0, "nuove": [], "tornate_piene": [],
                                   "bocciate_giro": 2, "aggiornate": True}


def _tre_validate():
    return _FB({"A|gen_a": _rec(strategy="gen_a", symbol="A"),
                "B|gen_b": _rec(strategy="gen_b", symbol="B"),
                "C|gen_c": _rec(strategy="gen_c", symbol="C")})


def _passa(fb, chiavi, bocciate, completa, esito=None):
    out = {k: _entry(k.split("|")[0], {"id": k.split("|")[1]}, 0, 0.5, 0.1, [0.1, 0.2, 0.2])
           for k in chiavi}
    for e in out.values():
        del e["spec"]
    d.merge_into_registry(fb, out, list(out), evaluated_symbols={"A", "B", "C"},
                          esito=esito, completa=completa,
                          bocciate_validate={k: _leggera(k.split("|")[0], {"id": k.split("|")[1]},
                                                         -0.1, 0.2, [0.0, -0.1, 0.0])
                                             for k in bocciate})
    return fb.pairs()


def test_i_contatori_delle_declassate_si_muovono_solo_nel_giro_completo(monkeypatch):
    monkeypatch.setattr(settings, "DECLASSATA_NOTTI", 2)
    fb = _tre_validate()
    # notte 1 (completa): A passa, B bocciata, C non giudicata
    e1 = {}
    p = _passa(fb, ["A|gen_a"], ["B|gen_b"], completa=True, esito=e1)
    assert (p["A|gen_a"]["bocciata_notti"], p["A|gen_a"]["declassata"]) == (0, False)
    assert p["B|gen_b"]["bocciata_notti"] == 1 and not p["B|gen_b"].get("declassata")
    assert "bocciata_notti" not in p["C|gen_c"]
    assert e1["declassate"] == {"totale": 0, "nuove": [], "tornate_piene": [],
                                "bocciate_giro": 1, "aggiornate": True}
    # giro urgente: B bocciata di nuovo, ma i contatori NON si muovono
    e2 = {}
    p = _passa(fb, [], ["B|gen_b"], completa=False, esito=e2)
    assert p["B|gen_b"]["bocciata_notti"] == 1 and not p["B|gen_b"].get("declassata")
    assert e2["declassate"]["aggiornate"] is False and e2["declassate"]["bocciate_giro"] == 1
    # notte 2 (completa): seconda bocciatura di fila -> declassata
    e3 = {}
    prima = time.time()
    p = _passa(fb, [], ["B|gen_b"], completa=True, esito=e3)
    assert p["B|gen_b"]["bocciata_notti"] == 2 and p["B|gen_b"]["declassata"] is True
    assert p["B|gen_b"]["declassata_at"] >= prima
    assert e3["declassate"] == {"totale": 1, "nuove": ["B|gen_b"], "tornate_piene": [],
                                "bocciate_giro": 1, "aggiornate": True}
    at = p["B|gen_b"]["declassata_at"]
    # notte 3: ancora bocciata: resta declassata, NON e' «nuova» un'altra volta
    e4 = {}
    p = _passa(fb, [], ["B|gen_b"], completa=True, esito=e4)
    assert p["B|gen_b"]["bocciata_notti"] == 3 and p["B|gen_b"]["declassata_at"] == at
    assert e4["declassate"]["nuove"] == [] and e4["declassate"]["totale"] == 1
    # notte 4: ripassa -> torna piena
    e5 = {}
    p = _passa(fb, ["B|gen_b"], [], completa=True, esito=e5)
    assert (p["B|gen_b"]["bocciata_notti"], p["B|gen_b"]["declassata"]) == (0, False)
    assert e5["declassate"] == {"totale": 0, "nuove": [], "tornate_piene": ["B|gen_b"],
                                "bocciate_giro": 0, "aggiornate": True}
    # MAI un tocco a pass_count, fail_count o finestre: B e' validata come prima
    assert p["B|gen_b"]["pass_count"] == MIN_PASSES and not p["B|gen_b"].get("fail_count")
    assert "B|gen_b" in reg.coppie_validate(p, time.time())


def test_senza_bocciate_il_merge_e_quello_di_prima():
    fb = _tre_validate()
    esito = {}
    d.merge_into_registry(fb, {}, [], evaluated_symbols={"A"}, esito=esito)
    assert esito["declassate"] == {"totale": 0, "nuove": [], "tornate_piene": [],
                                   "bocciate_giro": 0, "aggiornate": False}
    assert all("bocciata_notti" not in r for r in fb.pairs().values())


def test_il_flag_sopravvive_al_codec_e_all_alleggerimento_delle_validate():
    pairs = {"B|gen_b": _rec(strategy="gen_b", symbol="B", bocciata_notti=2, declassata=True,
                             declassata_at=1e9, last_params={"profit_lock_keep": 0.65})}
    giro = decode_pairs(encode_pairs(pairs))["B|gen_b"]
    assert giro["declassata"] is True and giro["bocciata_notti"] == 2
    # una validata non si alleggerisce: i tre campi restano
    r = decode_pairs(slim_registry(pairs, ["B|gen_b"], max_bytes=10**9))["B|gen_b"]
    assert r["declassata"] is True and r["bocciata_notti"] == 2 and r["declassata_at"] == 1e9
    # e nell'alleggerimento d'EMERGENZA (tetto sforato anche dopo quello normale:
    # restano SOLO i campi del nucleo) i tre campi devono restare lo stesso,
    # altrimenti la coppia tornerebbe a size piena in silenzio (verifica del 26
    # set 2026: erano fuori da REGISTRY_CORE_FIELDS)
    assert {"bocciata_notti", "declassata", "declassata_at"} <= REGISTRY_CORE_FIELDS
    grossa = dict(pairs["B|gen_b"], descrizione="x" * 5000)
    r2 = decode_pairs(slim_registry({"B|gen_b": grossa}, ["B|gen_b"], max_bytes=1000))["B|gen_b"]
    assert "descrizione" not in r2
    assert r2["declassata"] is True and r2["bocciata_notti"] == 2 and r2["declassata_at"] == 1e9


# --------------------------------------------------------------------------- #
# 5. il registro, gate_progress, il log del giro, il documento del gate       #
# --------------------------------------------------------------------------- #
def test_registry_conta_le_declassate_solo_fra_le_validate():
    pairs = {"A|gen_a": {"declassata": True}, "B|gen_b": {"declassata": False},
             "C|gen_c": {}, "D|gen_d": {"declassata": True}, "E|gen_e": "storto"}
    assert reg.declassate(pairs, ["A|gen_a", "B|gen_b", "C|gen_c", "E|gen_e", "X|no"]) == {"A|gen_a"}
    assert reg.conta_declassate(pairs, ["A|gen_a", "D|gen_d"]) == 2
    assert reg.conta_declassate(pairs, ["B|gen_b"]) == 0 and reg.conta_declassate({}, None) == 0


def test_gate_progress_stampa_la_riga_delle_declassate(monkeypatch, capsys):
    monkeypatch.setattr(settings, "DECLASSATA_SIZE_MULT", 0.25)
    monkeypatch.setattr(settings, "DECLASSATA_NOTTI", 2)
    pairs = {"A|gen_a": {"declassata": True}, "B|gen_b": {}}
    val = ["A|gen_a", "B|gen_b"]
    assert g.riga_declassate(pairs, val, {"declassate": {"totale": 1, "nuove": ["A|gen_a"],
                                                        "tornate_piene": [], "aggiornate": True}}) == \
        "  DECLASSATE: 1 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 1"
    assert g.riga_declassate(pairs, val, {"declassate": {"totale": 1, "nuove": [], "tornate_piene": ["Z|z"],
                                                        "aggiornate": False}}).endswith(
        "tornate piene nel giro 1 · nuove nel giro 0 (contatori fermi: giro solo urgenti)")
    assert g.riga_declassate(pairs, val, {}).endswith("esito del giro non registrato (arriva col primo giro finito dal 26 set)")
    monkeypatch.setattr(settings, "DECLASSATA_SIZE_MULT", 0.5)
    assert g.riga_declassate({}, [], None).startswith("  DECLASSATE: 0 validate a 0.5x size")
    # e `main` la stampa, dopo il keep del lock
    now = time.time()
    fb = _FB({"AUSDT|gen_a": _rec(symbol="AUSDT", strategy="gen_a", last_seen_at=now,
                                  window_start=now - 100, declassata=True, bocciata_notti=2)},
             {("strategy_params", "discovered_last_run"):
              {"started_at": now - 3600, "duration_s": 60,
               "declassate": {"totale": 1, "nuove": [], "tornate_piene": [], "aggiornate": True}}})
    monkeypatch.setattr(settings, "DECLASSATA_SIZE_MULT", 0.25)
    monkeypatch.setattr(g, "get_firebase", lambda: fb)
    monkeypatch.setattr(sys, "argv", ["gate_progress"])
    assert g.main() == 0
    out = capsys.readouterr().out
    assert "  DECLASSATE: 1 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0" in out
    assert out.index("KEEP DEL LOCK") < out.index("DECLASSATE:")


def test_la_riga_del_cervello_e_in_coda_al_log_e_nel_documento_del_giro():
    assert d.riga_cervello_declassate({"totale": 3, "nuove": ["A|x"], "tornate_piene": ["B|y", "C|z"],
                                       "aggiornate": True}) == \
        "[cervello] declassate: 3 (nuove 1, tornate piene 2)"
    assert d.riga_cervello_declassate({}, solo_config=4, bocciate=9) == \
        "[cervello] declassate: 0 (nuove 0, tornate piene 0) · validate bocciate nel giro 9 · passate solo con la propria configurazione 4"
    assert "contatori fermi: giro solo urgenti" in d.riga_cervello_declassate({"aggiornate": False})
    src = inspect.getsource(d.main)
    assert src.rindex("print(riga_cervello_declassate(") < src.index("GIRO FINITO in")
    assert src.rindex("print(riga_cervello_declassate(") > src.rindex("print(riga_cervello_uscita(")
    assert '"passate_solo_con_propria_config": passate_solo_config' in src
    assert '"declassate": esito_declassate' in src and '"validate_bocciate": len(bocciate_validate)' in src


def test_il_documento_del_gate_porta_i_due_campi_e_il_contratto_li_nomina():
    from tests.test_doc_gate import _costruisci, _fixture_piccola, _run
    from tests.test_schema_controllo import campi_del_contratto
    pairs, specs, trades, drift = _fixture_piccola()      # BUSDT|gen_b e' gia' declassata
    pairs["AUSDT|gen_a"]["declassata"] = True
    pairs["AUSDT|gen_m"]["declassata"] = True          # madre sostituita: non si opera, non conta
    doc = _costruisci(pairs, specs, trades, drift, run=_run(passate_solo_con_propria_config=3))
    assert doc["giro"]["passate_solo_con_propria_config"] == 3
    assert doc["registro"]["declassate"] == 2
    # un giro col codice precedente non l'ha contata: null, non zero
    doc0 = _costruisci(pairs, specs, trades, drift, run={k: v for k, v in _run().items()
                                                          if k != "passate_solo_con_propria_config"})
    assert doc0["giro"]["passate_solo_con_propria_config"] is None
    c = campi_del_contratto()
    assert "passate_solo_con_propria_config" in c["2.2 giro"] and "declassate" in c["2.3 registro"]
    with open(os.path.join(ROOT, "dashboard", "app", "lib", "gate.ts"), encoding="utf-8") as f:
        ts = f.read()
    assert re.search(r"passate_solo_con_propria_config\?: number \| null", ts)
    assert re.search(r"declassate\?: number \| null", ts)
