"""L'ESITO DEL CERVELLO SI LEGGE DA FUORI (25 set 2026).

Il check end-to-end del 25 set ha trovato due buchi:

  1. quante madri l'intorno avesse riprovato, quante figlie fossero passate e
     poi promosse o morte senza margine, quante varianti dai referti fossero
     entrate o state scartate — tutto questo stava SOLO nel log del gate, che da
     fuori si legge con 80 righe di coda. Ora `merge_into_registry` lo conta in
     `esito["intorno"]` / `esito["varianti"]`, la discovery lo scrive in
     `strategy_params/discovered_last_run` e lo stampa come ultime righe prima
     di «GIRO FINITO»; `gate_progress` lo rilegge dal documento;
  2. 72 coppie validate su 131 erano senza `last_pf`: alleggerite quando non
     erano validate, poi promosse dalla chiusura della finestra senza ripassare
     dal merge. Senza promessa la deriva (`bot/learning/drift.py`) va in
     fail-open. `last_pf` entra nel nucleo che l'alleggerimento non tocca;
     `regime_pf` (il dizionario che legge il veto di regime) resta fuori.
"""
import inspect
import sys
import time

from bot.core.firebase_client import decode_pairs, encode_pairs
from bot.strategies.generated import spec_id
from bot.strategies.generator import figlie_intorno, varianti_da_referto
from scripts import discover_strategies as d
from scripts import gate_progress as g
from scripts.optimize import MIN_PASSES, REGISTRY_CORE_FIELDS, slim_registry


def _spec(**extra):
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                         {"kind": "session", "hour_from": 8, "hour_to": 16}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec.update(extra)
    spec["id"] = spec_id(spec)
    return spec


def _rec(pass_count=3, **extra):
    r = {"generated": True, "pass_count": pass_count, "last_seen_at": 1e9,
         "last_pnl_pct": 0.5}
    r.update(extra)
    return r


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


def _entry(sym, spec, retro, pnl, dd, finestre):
    return {"symbol": sym, "strategy": spec["id"], "params": {}, "spec": spec,
            "oos_pf": 1.6, "oos_pnl_pct": pnl, "oos_max_dd": dd, "oos_trades": 40,
            "oos_win_rate": 0.5, "passed": True, "holdout": {"ok": True},
            "data_end": 1e9, "conferme_retro": retro, "window_pnls": finestre}


# --------------------------------------------------------------------------- #
# 1. Il merge conta l'esito dell'intorno                                       #
# --------------------------------------------------------------------------- #
def test_il_merge_racconta_l_intorno():
    """Quattro madri riprovate, quattro figlie passate: una promossa (A), una
    senza margine (B), una con la madre non valutata oggi (C), una senza
    conferme retroattive (D). I conti devono tornare: passate = somma."""
    madre = _spec()
    figlia = figlie_intorno(madre)[0]
    fb = _FB({f"{c}|{madre['id']}": _rec(strategy=madre["id"], symbol=c) for c in "ABCD"})
    out = {
        f"A|{madre['id']}": _entry("A", madre, 0, 0.50, 0.10, [0.1, 0.2, 0.2]),
        f"A|{figlia['id']}": _entry("A", figlia, MIN_PASSES - 1, 0.62, 0.10, [0.2, 0.3, 0.12]),
        f"B|{madre['id']}": _entry("B", madre, 0, 0.50, 0.10, [0.1, 0.2, 0.2]),
        f"B|{figlia['id']}": _entry("B", figlia, MIN_PASSES - 1, 0.62, 0.10, [0.5, 0.05, 0.07]),
        f"C|{figlia['id']}": _entry("C", figlia, MIN_PASSES - 1, 0.90, 0.05, [0.3, 0.3, 0.3]),
        f"D|{madre['id']}": _entry("D", madre, 0, 0.50, 0.10, [0.1, 0.2, 0.2]),
        f"D|{figlia['id']}": _entry("D", figlia, 0, 0.90, 0.05, [0.3, 0.3, 0.3]),
    }
    esito = {}
    d.merge_into_registry(fb, out, list(out), evaluated_symbols=set("ABCD"),
                          intorno_madri={f"{c}|{madre['id']}": 6 for c in "ABCD"},
                          esito=esito)
    assert esito["intorno"] == {"madri": 4, "figlie_passate": 4,
                                "promosse": [f"A|{figlia['id']}"],
                                "senza_margine": 1, "madre_non_valutata": 1,
                                "scartate": 1}
    # nessuna variante dai referti in questo giro: il dizionario c'e' lo stesso, a zero
    assert esito["varianti"] == {"create": 0, "passate": 0, "retro_ok": 0,
                                 "promosse": [], "scartate": 0, "sostituzioni": []}
    # e il registro dice la stessa cosa dei conti
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert pairs[f"A|{madre['id']}"]["sostituita_da"] == figlia["id"]
    assert not any(pairs[f"{c}|{madre['id']}"].get("sostituita_da") for c in "BCD")


def test_il_merge_racconta_le_varianti_dai_referti():
    """Tre varianti messe in coda dal main; due passate: una con le conferme
    retroattive (promossa, e sostituisce la madre), una solo con i dati di oggi
    (scartata)."""
    madre = _spec()
    var = varianti_da_referto(madre, "solo_long")
    assert var["origine"] == "referto"
    fb = _FB({f"A|{madre['id']}": _rec(strategy=madre["id"], symbol="A"),
              f"B|{madre['id']}": _rec(strategy=madre["id"], symbol="B")})
    out = {f"A|{var['id']}": _entry("A", var, MIN_PASSES - 1, 0.6, 0.1, [0.2, 0.2, 0.2]),
           f"B|{var['id']}": _entry("B", var, 0, 0.9, 0.05, [0.3, 0.3, 0.3])}
    esito = {}
    d.merge_into_registry(fb, out, list(out), evaluated_symbols={"A", "B"},
                          esito=esito, varianti_create=3)
    assert esito["varianti"] == {
        "create": 3, "passate": 2, "retro_ok": 1,
        "promosse": [f"A|{var['id']}"], "scartate": 1,
        "sostituzioni": [{"figlia": f"A|{var['id']}", "madre": f"A|{madre['id']}"}]}
    assert esito["intorno"]["madri"] == 0 and esito["intorno"]["figlie_passate"] == 0
    assert esito["scartate"] == [f"B|{var['id']}"]
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert pairs[f"A|{var['id']}"]["pass_count"] == MIN_PASSES
    assert pairs[f"A|{madre['id']}"]["sostituita_da"] == var["id"]
    assert f"B|{var['id']}" not in pairs


def test_senza_esito_il_merge_non_esplode():
    fb = _FB({})
    d.merge_into_registry(fb, {}, [], evaluated_symbols={"A"})


# --------------------------------------------------------------------------- #
# 2. La discovery lo scrive nel documento e lo stampa in coda al log            #
# --------------------------------------------------------------------------- #
def test_le_righe_del_cervello_si_stampano_sempre_anche_a_zero():
    assert d.riga_cervello_intorno({}).startswith("[cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse")
    assert d.riga_cervello_varianti(None).startswith("[cervello] varianti dai referti: 0 create / 0 passate")
    assert "sostituzioni: nessuna" in d.riga_cervello_varianti({})
    ri = d.riga_cervello_intorno({"madri": 4, "figlie_passate": 4, "promosse": ["A|gen_f"],
                                  "senza_margine": 1, "madre_non_valutata": 1, "scartate": 1})
    assert "4 madri riprovate / 4 figlie passate / 1 promosse (A|gen_f) / 1 senza margine" in ri
    rv = d.riga_cervello_varianti({"create": 3, "passate": 2, "retro_ok": 1,
                                   "promosse": ["A|gen_v"], "scartate": 1,
                                   "sostituzioni": [{"figlia": "A|gen_v", "madre": "A|gen_m"}]})
    assert "3 create / 2 passate / 1 con conferme retroattive / 1 promosse (A|gen_v) / 1 scartate" in rv
    assert "sostituzioni: A|gen_v -> A|gen_m" in rv


def test_il_main_scrive_l_esito_nel_documento_e_lo_stampa_prima_di_giro_finito():
    src = inspect.getsource(d.main)
    assert "varianti_create=len(varianti)" in src
    assert '"intorno": esito_intorno' in src and '"varianti": esito_varianti' in src
    # ULTIME righe prima di GIRO FINITO: e' cosi' che restano nella coda del log
    fine = src.index("GIRO FINITO in")
    assert src.rindex("print(riga_cervello_intorno(") < fine
    assert src.rindex("print(riga_cervello_varianti(") < fine
    assert src.rindex("print(riga_cervello_varianti(") > src.rindex("print(riga_cervello_intorno(")


# --------------------------------------------------------------------------- #
# 3. gate_progress lo rilegge dal documento                                    #
# --------------------------------------------------------------------------- #
def _gate_output(monkeypatch, capsys, last_run: dict) -> str:
    pairs = {"AUSDT|gen_a": _rec(2, symbol="AUSDT", strategy="gen_a",
                                 last_seen_at=time.time(), window_start=time.time() - 100)}
    fb = _FB(pairs, {("strategy_params", "discovered_last_run"): last_run})
    monkeypatch.setattr(g, "get_firebase", lambda: fb)
    monkeypatch.setattr(sys, "argv", ["gate_progress"])
    assert g.main() == 0
    return capsys.readouterr().out


def test_gate_progress_stampa_il_cervello_dell_ultimo_giro(monkeypatch, capsys):
    out = _gate_output(monkeypatch, capsys, {
        "started_at": 1e9, "duration_s": 3600,
        "intorno": {"madri": 4, "figlie_passate": 4, "promosse": ["A|gen_f"],
                    "senza_margine": 1, "madre_non_valutata": 1, "scartate": 1},
        "varianti": {"create": 3, "passate": 2, "retro_ok": 1, "promosse": ["A|gen_v"],
                     "scartate": 1, "sostituzioni": [{"figlia": "A|gen_v", "madre": "A|gen_m"}]},
    })
    riga = next(l for l in out.splitlines() if "IL CERVELLO NELL'ULTIMO GIRO" in l)
    assert ("intorno 4 madri / 4 figlie passate / 1 promosse (A|gen_f) / 1 senza margine"
            " / 1 con madre non valutata / 1 senza conferme retroattive o seconde figlie"
            " · varianti 3 create / 2 passate / 1 con conferme retroattive / 1 promosse (A|gen_v)"
            " / 1 scartate / sostituzioni A|gen_v -> A|gen_m") in riga
    # e sta DOPO il tempo del giro, come chiesto
    assert out.index("TEMPO DELL'ULTIMO GIRO") < out.index("IL CERVELLO NELL'ULTIMO GIRO")


def test_gate_progress_a_zero_non_tace(monkeypatch, capsys):
    out = _gate_output(monkeypatch, capsys, {
        "intorno": {"madri": 0, "figlie_passate": 0, "promosse": [], "senza_margine": 0,
                    "madre_non_valutata": 0, "scartate": 0},
        "varianti": {"create": 0, "passate": 0, "retro_ok": 0, "promosse": [],
                     "scartate": 0, "sostituzioni": []}})
    assert ("IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 0 figlie passate / 0 promosse"
            " / 0 senza margine · varianti 0 create / 0 passate / 0 con conferme retroattive"
            " / 0 promosse / 0 scartate / sostituzioni nessuna") in out


def test_gate_progress_senza_le_chiavi_lo_dice(monkeypatch, capsys):
    """Un giro col codice precedente non ha `intorno`/`varianti`: si dice, invece
    di stampare zeri che sembrerebbero un esito."""
    out = _gate_output(monkeypatch, capsys, {"started_at": 1e9, "duration_s": 60})
    assert "IL CERVELLO NELL'ULTIMO GIRO: non registrato: giro precedente al 25 set" in out
    assert "non registrato: giro precedente al 25 set" in g.riga_cervello({})
    assert "non registrato" in g.riga_cervello({"intorno": {"madri": 1}})   # meta' non basta


# --------------------------------------------------------------------------- #
# 4. `last_pf` sopravvive all'alleggerimento                                   #
# --------------------------------------------------------------------------- #
def test_last_pf_e_nel_nucleo_e_regime_pf_no():
    assert "last_pf" in REGISTRY_CORE_FIELDS
    assert "regime_pf" not in REGISTRY_CORE_FIELDS      # un dizionario per coppia: fuori


def test_l_alleggerimento_conserva_last_pf_a_una_coppia_non_validata():
    """Il caso misurato il 25 set: alleggerita a 2 conferme, promossa poi dalla
    chiusura della finestra senza ripassare dal merge. La promessa deve esserci
    ancora, sia nell'alleggerimento normale sia in quello d'emergenza."""
    pairs = {"AUSDT|gen_a": {"pass_count": 2, "symbol": "AUSDT", "strategy": "gen_a",
                             "last_pf": 1.42, "holdout": {"pf": 1.3},
                             "regime_pf": {"bull": {"pf": 1.2, "trades": 40}}}}
    for tetto in (10**9, 1):
        r = decode_pairs(slim_registry(pairs, [], max_bytes=tetto))["AUSDT|gen_a"]
        assert r["last_pf"] == 1.42, f"last_pf perso col tetto {tetto}"
        assert "regime_pf" not in r and "holdout" not in r
