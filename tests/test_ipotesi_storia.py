"""LA STORIA DELLE IPOTESI (26 set 2026, backlog J9).

Le ipotesi dei referti vanno e vengono con i trade: senza memoria non si puo'
dire se una REGOLA (un tipo) produce varianti che passano il gate o solo
rumore. Qui si protegge: le funzioni pure di `bot/learning/referti.py`
(nascita alla prima comparsa, esiti con i traguardi, `per_tipo` ricalcolato),
i ganci della discovery (variante_creata / scartata alla creazione, passata /
validata / bocciata dal merge, scritti fail-open), la riga di `gate_progress`
e la riga del diario delle vite con `ipotesi` e `genitore`.
"""
import inspect
import sys
import time

from bot.core.firebase_client import encode_pairs
from bot.learning.referti import (ESITI_STORIA, aggiorna_storia, per_tipo_storia,
                                  registra_esiti_storia)
from bot.strategies.generated import spec_id
from bot.strategies.generator import varianti_da_referto
from scripts import discover_strategies as d
from scripts import gate_progress as g
from scripts import optimize as o


def _ip(gid, tipo):
    return {"strategia": gid, "tipo": tipo, "motivo": "x", "campione": 3}


def _spec(**extra):
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec.update(extra)
    spec["id"] = spec_id(spec)
    return spec


# ---- le funzioni pure -------------------------------------------------------- #
def test_aggiorna_storia_crea_le_voci_alla_prima_comparsa_e_non_le_tocca_dopo():
    ref = {"ipotesi": [_ip("gen_a", "solo_long"), _ip("gen_b", "stop_stretto"),
                       {"strategia": None, "tipo": "solo_long"}, "boh"]}
    doc = aggiorna_storia(None, ref, 1000.0)
    assert set(doc["voci"]) == {"gen_a|solo_long", "gen_b|stop_stretto"}
    v = doc["voci"]["gen_a|solo_long"]
    assert v == {"nata_at": 1000.0, "tipo": "solo_long", "strategia": "gen_a",
                 "variante_id": None, "esito": "aperta", "at": 1000.0}
    assert doc["per_tipo"] == {"solo_long": {"nate": 1, "varianti": 0, "passate": 0,
                                             "validate": 0, "bocciate": 0},
                               "stop_stretto": {"nate": 1, "varianti": 0, "passate": 0,
                                                "validate": 0, "bocciate": 0}}
    assert doc["updated_at"] == 1000.0
    # un giorno dopo, la stessa ipotesi e una nuova: la vecchia conserva la data
    doc2 = aggiorna_storia(doc, {"ipotesi": [_ip("gen_a", "solo_long"), _ip("gen_a", "ingresso_adx")]}, 2000.0)
    assert doc2["voci"]["gen_a|solo_long"]["nata_at"] == 1000.0
    assert doc2["voci"]["gen_a|ingresso_adx"]["nata_at"] == 2000.0
    assert set(doc2["voci"]) == {"gen_a|solo_long", "gen_b|stop_stretto", "gen_a|ingresso_adx"}
    # pura: il documento precedente non e' stato mutato
    assert "gen_a|ingresso_adx" not in doc["voci"]
    # senza referti: documento uguale, data nuova
    assert aggiorna_storia(doc, None, 3000.0)["voci"] == doc["voci"]
    assert aggiorna_storia(doc, {}, 3000.0)["updated_at"] == 3000.0


def test_registra_esiti_segna_i_traguardi_una_volta_e_l_ultimo_esito_sempre():
    doc = aggiorna_storia(None, {"ipotesi": [_ip("gen_a", "solo_long")]}, 1000.0)
    doc = registra_esiti_storia(doc, {"gen_a|solo_long": ("variante_creata", "gen_f")}, 1100.0)
    v = doc["voci"]["gen_a|solo_long"]
    assert v["esito"] == "variante_creata" and v["variante_id"] == "gen_f"
    assert v["variante_at"] == 1100.0 and v["at"] == 1100.0 and v["nata_at"] == 1000.0
    doc = registra_esiti_storia(doc, {"gen_a|solo_long": ("bocciata", "gen_f")}, 1200.0)
    assert doc["voci"]["gen_a|solo_long"]["bocciata_at"] == 1200.0
    # rinasce al giro dopo: l'esito torna variante_creata, i traguardi restano
    doc = registra_esiti_storia(doc, {"gen_a|solo_long": ("variante_creata", "gen_f")}, 1300.0)
    v = doc["voci"]["gen_a|solo_long"]
    assert v["esito"] == "variante_creata" and v["variante_at"] == 1100.0 and v["bocciata_at"] == 1200.0
    doc = registra_esiti_storia(doc, {"gen_a|solo_long": ("validata", "gen_f")}, 1400.0)
    v = doc["voci"]["gen_a|solo_long"]
    assert v["validata_at"] == 1400.0 and v["esito"] == "validata"
    assert doc["per_tipo"] == {"solo_long": {"nate": 1, "varianti": 1, "passate": 1,
                                             "validate": 1, "bocciate": 1}}


def test_registra_esiti_crea_la_voce_se_manca_e_ignora_gli_esiti_sconosciuti():
    doc = registra_esiti_storia(None, {"gen_z|stop_stretto": ("passata", "gen_q"),
                                       "gen_z|solo_long": ("boh", None),
                                       "senza_barra": ("validata", "x"),
                                       "gen_y|scala": "scartata"}, 500.0)
    assert set(doc["voci"]) == {"gen_z|stop_stretto", "gen_y|scala"}
    v = doc["voci"]["gen_z|stop_stretto"]
    assert v["nata_at"] == 500.0 and v["esito"] == "passata" and v["passata_at"] == 500.0
    assert doc["voci"]["gen_y|scala"]["esito"] == "scartata"
    assert doc["voci"]["gen_y|scala"]["variante_id"] is None
    assert ESITI_STORIA == ("aperta", "variante_creata", "passata", "validata", "bocciata", "scartata")


def test_per_tipo_conta_dai_traguardi_e_in_ordine():
    voci = {"a|solo_long": {"tipo": "solo_long", "variante_id": "f", "passata_at": 1.0},
            "b|solo_long": {"tipo": "solo_long", "validata_at": 2.0, "variante_at": 1.0},
            "c|ingresso_adx": {"tipo": "ingresso_adx", "bocciata_at": 1.0},
            "rotta": "non un dict"}
    assert per_tipo_storia(voci) == {
        "ingresso_adx": {"nate": 1, "varianti": 0, "passate": 0, "validate": 0, "bocciate": 1},
        "solo_long": {"nate": 2, "varianti": 2, "passate": 2, "validate": 1, "bocciate": 0}}
    assert per_tipo_storia({}) == {} and per_tipo_storia(None) == {}


# ---- la discovery: creazione ------------------------------------------------ #
def test_varianti_dai_referti_lascia_l_esito_di_ogni_ipotesi():
    madre = _spec()
    gia_long = _spec(solo="long", atr_mult_stop=2.0)    # logica diversa dalla figlia di madre
    tf = d.settings.ORCHESTRATOR_TIMEFRAME
    existing = {madre["id"]: madre, gia_long["id"]: gia_long}
    doc = {"ipotesi": [_ip(madre["id"], "solo_long"), _ip(gia_long["id"], "solo_long"),
                       _ip(madre["id"], "scala_stretta"), _ip("gen_ignota", "solo_short"),
                       _ip(madre["id"], "solo_short")]}
    # il gate ha gia' la risposta per solo_short: il lato long ha PF >= 1 su >= 20 trade
    pairs = {f"A|{madre['id']}": {"strategy": madre["id"],
                                  "direzione_pf": {"long": {"n": 25, "pf": 1.3}}}}
    esiti = {}
    out = d.varianti_dai_referti(None, existing, tf, pairs=pairs, doc=doc, esiti=esiti)
    assert len(out) == 1 and out[0]["ipotesi"] == "solo_long"
    assert esiti == {f"{madre['id']}|solo_long": ("variante_creata", out[0]["id"]),
                     f"{gia_long['id']}|solo_long": ("scartata", None),
                     f"{madre['id']}|solo_short": ("scartata", None)}
    # senza `esiti` il comportamento e' identico a prima
    assert [v["id"] for v in d.varianti_dai_referti(None, existing, tf, pairs=pairs, doc=doc)] == [out[0]["id"]]
    # una figlia gia' nota (giro precedente) non rientra in coda ma la voce sa di lei
    esiti2 = {}
    d.varianti_dai_referti(None, {**existing, out[0]["id"]: out[0]}, tf, doc=doc, esiti=esiti2)
    assert esiti2[f"{madre['id']}|solo_long"] == ("variante_creata", out[0]["id"])


# ---- la discovery: gli esiti dal merge -------------------------------------- #
def _entry(sym, spec):
    return {"symbol": sym, "strategy": spec["id"], "spec": spec, "params": {}}


def test_esiti_dal_merge_validata_bocciata_passata_e_mai_passata():
    madre = _spec()
    fa = varianti_da_referto(madre, "solo_long")
    fb_ = varianti_da_referto(madre, "stop_stretto")
    fc = varianti_da_referto(madre, "conferma_trend")
    fd = varianti_da_referto(madre, "solo_short")
    fe = varianti_da_referto(_spec(volume_mult=1.5), "ingresso_adx")     # giro precedente
    out = {f"A|{fa['id']}": _entry("A", fa), f"B|{fb_['id']}": _entry("B", fb_),
           f"C|{fc['id']}": _entry("C", fc), f"E|{fe['id']}": _entry("E", fe),
           f"A|{madre['id']}": _entry("A", madre)}
    esito = {"varianti": {"promosse": [f"A|{fa['id']}"]}, "scartate": [f"B|{fb_['id']}"]}
    ev = d.esiti_varianti_dal_merge(out, list(out), esito, [fa, fb_, fc, fd])
    assert ev == {f"{madre['id']}|solo_long": ("validata", fa["id"]),
                  f"{madre['id']}|stop_stretto": ("bocciata", fb_["id"]),
                  f"{madre['id']}|conferma_trend": ("passata", fc["id"]),
                  f"{madre['id']}|solo_short": ("bocciata", fd["id"]),       # mai passata
                  f"{fe['genitore']}|ingresso_adx": ("passata", fe["id"])}   # rivalutata
    assert d.esiti_varianti_dal_merge({}, [], None, None) == {}
    assert d.esiti_varianti_dal_merge({}, [], {}, ["boh", {"id": "senza_genitore"}]) == {}


class _FB:
    def __init__(self, docs=None, rotto=False):
        self.docs = dict(docs or {})
        self.rotto = rotto
        self.scritture = 0

    def get_doc(self, c, dname):
        if self.rotto:
            raise RuntimeError("firestore giu'")
        return self.docs.get((c, dname))

    def set_doc(self, c, dname, data):
        self.scritture += 1
        self.docs[(c, dname)] = data


def test_aggiorna_ipotesi_storia_scrive_fail_open():
    fb = _FB()
    doc = d.aggiorna_ipotesi_storia(fb, doc_referti={"ipotesi": [_ip("gen_a", "solo_long")]},
                                    eventi={"gen_a|solo_long": ("variante_creata", "gen_f")},
                                    now=10.0)
    assert fb.scritture == 1 and fb.docs[("learning", "ipotesi_storia")] is doc
    assert doc["voci"]["gen_a|solo_long"]["esito"] == "variante_creata"
    assert doc["per_tipo"]["solo_long"]["varianti"] == 1
    # niente da dire: niente scrittura
    assert d.aggiorna_ipotesi_storia(fb, now=11.0) == doc and fb.scritture == 1
    # solo eventi: si scrive sopra la storia esistente
    d.aggiorna_ipotesi_storia(fb, eventi={"gen_a|solo_long": ("validata", "gen_f")}, now=12.0)
    assert fb.docs[("learning", "ipotesi_storia")]["voci"]["gen_a|solo_long"]["validata_at"] == 12.0
    # Firestore giu': None, nessuna eccezione
    assert d.aggiorna_ipotesi_storia(_FB(rotto=True), doc_referti={"ipotesi": []}, now=1.0) is None


def test_il_main_scrive_la_storia_all_inizio_e_dopo_il_merge():
    src = inspect.getsource(d.main)
    assert "esiti=esiti_referti)" in src
    inizio = src.index("aggiorna_ipotesi_storia(fb, doc_referti=doc_referti or None")
    assert src.index("varianti_dai_referti(fb, existing") < inizio < src.index("generate_specs(")
    dopo = src.index("eventi=esiti_varianti_dal_merge(out, passed_keys, esito_merge, varianti)")
    assert src.index("validated = merge_into_registry(") < dopo
    # PRIMA del filtro sulle scartate, che le toglierebbe da passed_keys
    assert dopo < src.index("passed_keys = [k for k in passed_keys if k not in scartate]")


def test_il_merge_scrive_ipotesi_e_genitore_sul_record_della_variante():
    madre = _spec()
    var = varianti_da_referto(madre, "solo_long")
    pairs = {f"A|{madre['id']}": {"generated": True, "pass_count": 3, "last_seen_at": 1e9,
                                  "strategy": madre["id"], "symbol": "A"}}
    fb = _FB({("strategy_registry", "validated"): {"pairs": encode_pairs(pairs)}})
    out = {f"A|{var['id']}": {"symbol": "A", "strategy": var["id"], "params": {}, "spec": var,
                              "oos_pf": 1.6, "oos_pnl_pct": 0.6, "oos_max_dd": 0.1,
                              "oos_trades": 40, "oos_win_rate": 0.5, "passed": True,
                              "holdout": {"ok": True}, "data_end": 1e9,
                              "conferme_retro": o.MIN_PASSES - 1, "window_pnls": [0.2] * 3}}
    d.merge_into_registry(fb, out, list(out), evaluated_symbols={"A"}, esito={})
    from bot.core.firebase_client import decode_pairs
    rec = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])[f"A|{var['id']}"]
    assert rec["ipotesi"] == "solo_long" and rec["genitore"] == madre["id"]
    # e la riga del diario delle vite li porta
    vite = fb.docs[("gate_history", "lifecycle")]["events"]
    assert vite[-1]["key"] == f"A|{var['id']}" and vite[-1]["tipo"] == "promossa"
    assert vite[-1]["ipotesi"] == "solo_long" and vite[-1]["genitore"] == madre["id"]


def test_la_riga_di_vita_porta_ipotesi_e_genitore_solo_se_presenti():
    senza = o._riga_vita("X|gen_a", {"pass_count": 3}, "promossa", 1.0)
    assert "ipotesi" not in senza and "genitore" not in senza
    con = o._riga_vita("X|gen_f", {"pass_count": 3, "ipotesi": "stop_stretto",
                                   "genitore": "gen_a"}, "rimossa", 1.0)
    assert con["ipotesi"] == "stop_stretto" and con["genitore"] == "gen_a"


# ---- gate_progress ----------------------------------------------------------- #
def test_riga_ipotesi_per_tipo():
    assert g.riga_ipotesi_storia(None).startswith("  IPOTESI PER TIPO: storia non ancora scritta")
    assert g.riga_ipotesi_storia({"per_tipo": {}}) == "  IPOTESI PER TIPO: nessuna ipotesi ancora nata nei referti"
    doc = {"per_tipo": {"solo_long": {"nate": 9, "varianti": 9, "passate": 1, "validate": 1, "bocciate": 6},
                        "ingresso_adx": {"nate": 3, "varianti": 3, "passate": 0, "validate": 0, "bocciate": 2}}}
    riga = g.riga_ipotesi_storia(doc, {"evaluated": 20000, "passed": 60})
    assert riga.startswith("  IPOTESI PER TIPO: ingresso_adx 3 nate / 3 varianti / 0 passate / 0 validate "
                           "/ 2 bocciate · solo_long 9 nate / 9 varianti / 1 passate / 1 validate / 6 bocciate")
    assert "tasso figlie 8% (1/12 spec) contro 0.3% delle candidate dell'ultimo giro (60/20000" in riga
    assert "unita' diverse" in riga
    # senza autopsia: solo il tasso delle figlie
    assert g.riga_ipotesi_storia(doc).endswith("tasso figlie 8% (1/12 spec)")
    assert g.riga_ipotesi_storia(doc, {"evaluated": 0}).endswith("tasso figlie 8% (1/12 spec)")


def test_gate_progress_stampa_la_riga_dal_documento(monkeypatch, capsys):
    pairs = {"AUSDT|gen_a": {"generated": True, "pass_count": 2, "symbol": "AUSDT",
                             "strategy": "gen_a", "last_seen_at": time.time(),
                             "window_start": time.time() - 100, "last_pnl_pct": 0.5}}
    fb = _FB({("strategy_registry", "validated"): {"pairs": encode_pairs(pairs)},
              ("learning", "ipotesi_storia"): {"per_tipo": {"stop_stretto": {
                  "nate": 2, "varianti": 1, "passate": 0, "validate": 0, "bocciate": 1}}}})
    fb.docs.setdefault(("strategy_params", "discovered_last_run"), {})
    monkeypatch.setattr(g, "get_firebase", lambda: fb)
    monkeypatch.setattr(sys, "argv", ["gate_progress"])
    assert g.main() == 0
    out = capsys.readouterr().out
    assert "IPOTESI PER TIPO: stop_stretto 2 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate" in out
    assert out.index("ESPLORATIVE:") < out.index("IPOTESI PER TIPO:")
