"""L'INTORNO di una strategia validata (24 set 2026, backlog B8 seconda meta').

Cosa si protegge: ogni figlia cambia UN solo parametro di UN gradino sulle liste
del generatore; porta genitore/origine/ipotesi e un id suo; conserva timeframe e
lato; i parametri senza gradini non producono figlie; un valore fuori lista prende
i due gradini piu' vicini; niente duplicati.
"""
from bot.strategies.generated import spec_id
from bot.strategies.generator import (_ATR_STOP, _RSI_HIGH, _RSI_LOW, _vicini,
                                      figlie_intorno)


def _spec(**extra):
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                         {"kind": "session", "hour_from": 8, "hour_to": 16}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec.update(extra)
    spec["id"] = spec_id(spec)
    return spec


def test_vicini():
    assert _vicini(30.0, _RSI_LOW) == [25.0, 35.0]
    assert _vicini(20.0, _RSI_LOW) == [25.0]              # al minimo: solo sopra
    assert _vicini(80.0, _RSI_HIGH) == [75.0]             # al massimo: solo sotto
    assert _vicini(1.7, _ATR_STOP) == [1.5, 2.0]          # fuori lista: i vicini
    assert _vicini("x", _ATR_STOP) == [] and _vicini(1.0, None) == []


def test_figlie_cambiano_un_solo_parametro_di_un_gradino():
    madre = _spec()
    figlie = figlie_intorno(madre)
    etichette = sorted(f["ipotesi"] for f in figlie)
    # rsi low 30 -> 25/35, high 70 -> 65/75, atr 1.5 -> 1.0/2.0; volume_mult e
    # min_adx a 0 (filtro spento) NON si toccano: 0 non e' un gradino della lista
    assert etichette == ["intorno:atr_mult_stop=1", "intorno:atr_mult_stop=2",
                         "intorno:rsi_extreme.high=65", "intorno:rsi_extreme.high=75",
                         "intorno:rsi_extreme.low=25", "intorno:rsi_extreme.low=35"]
    for f in figlie:
        assert f["origine"] == "intorno" and f["genitore"] == madre["id"]
        assert f["id"] == spec_id(f) and f["id"] != madre["id"]
        assert len(f["features"]) == 2 and f["features"][1] == madre["features"][1]
    assert len({f["id"] for f in figlie}) == len(figlie)


def test_figlie_conservano_timeframe_e_lato_e_non_toccano_la_madre():
    madre = _spec(timeframe="1h", solo="long")
    copia = {k: (list(v) if isinstance(v, list) else v) for k, v in madre.items()}
    figlie = figlie_intorno(madre)
    assert all(f["timeframe"] == "1h" and f["solo"] == "long" for f in figlie)
    assert madre == copia and madre["features"][0]["low"] == 30.0


def test_spec_senza_numeri_non_ha_figlie():
    spec = {"features": [{"kind": "bb_touch"}, {"kind": "session", "hour_from": 0, "hour_to": 8}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": "boh", "rr": 2.0}
    spec["id"] = spec_id(spec)
    assert figlie_intorno(spec) == []
    assert figlie_intorno("non una spec") == []


def test_filtri_accesi_hanno_i_loro_gradini():
    madre = _spec(volume_mult=1.5, min_adx=20.0)
    etichette = {f["ipotesi"] for f in figlie_intorno(madre)}
    assert "intorno:volume_mult=2" in etichette
    assert "intorno:min_adx=25" in etichette


# --------------------------------------------------------------------------- #
# La discovery: chi va nell'intorno, e chi sostituisce chi                     #
# --------------------------------------------------------------------------- #
def _rec(pass_count=3, **extra):
    r = {"generated": True, "pass_count": pass_count, "last_seen_at": 1e9,
         "last_pnl_pct": 0.5}
    r.update(extra)
    return r


def test_coppie_per_intorno_sceglie_validate_fresche_con_precedenza_al_watch():
    from scripts.discover_strategies import coppie_per_intorno
    from scripts.optimize import MIN_PASSES
    now = 1e9
    g = 86400
    existing = {f"gen_{i}": _spec(volume_mult=float(i)) for i in range(7)}
    existing["gen_1h"] = {**_spec(), "timeframe": "1h"}
    pairs = {
        "A|gen_0": _rec(strategy="gen_0"),                                   # valida
        "B|gen_1": _rec(strategy="gen_1", intorno_at=now - 3 * g),           # riprovata 3 gg fa: no
        "C|gen_2": _rec(strategy="gen_2", intorno_at=now - 8 * g),           # 8 gg fa: si'
        "D|gen_3": _rec(strategy="gen_3", nata_intorno_at=now - 5 * g),      # figlia giovane: no
        "E|gen_4": _rec(strategy="gen_4", sostituita_da="gen_x"),            # sostituita: no
        "F|gen_5": _rec(pass_count=MIN_PASSES - 1, strategy="gen_5"),        # non validata: no
        "G|gen_6": _rec(strategy="gen_6"),                                   # in watch: PRIMA
        "H|gen_1h": _rec(strategy="gen_1h"),                                 # altro timeframe: no
        "I|gen_z": _rec(strategy="gen_z"),                                   # spec sconosciuta: no
    }
    drift = {"pairs": {"G|gen_6": {"verdict": "watch"}}}
    scelte = coppie_per_intorno(pairs, existing, drift, now, "15m", cap=10)
    assert [k for k, _ in scelte] == ["G|gen_6", "A|gen_0", "C|gen_2"]
    assert scelte[0][1]["id"] == existing["gen_6"]["id"]
    assert len(coppie_per_intorno(pairs, existing, drift, now, "15m", cap=2)) == 2
    assert coppie_per_intorno(pairs, existing, None, now, "15m", cap=0) == []


def _fb_con(pairs):
    from bot.core.firebase_client import encode_pairs

    class FB:
        def __init__(self):
            self.docs = {("strategy_registry", "validated"): {"pairs": encode_pairs(pairs)}}
        def get_doc(self, c, dname): return self.docs.get((c, dname), {})
        def set_doc(self, c, dname, data): self.docs[(c, dname)] = data
    return FB()


def _entry(sym, spec, retro, pnl, dd, finestre):
    return {"symbol": sym, "strategy": spec["id"], "params": {}, "spec": spec,
            "oos_pf": 1.6, "oos_pnl_pct": pnl, "oos_max_dd": dd, "oos_trades": 40,
            "oos_win_rate": 0.5, "passed": True, "holdout": {"ok": True},
            "data_end": 1e9, "conferme_retro": retro, "window_pnls": finestre}


def test_merge_promuove_la_figlia_solo_con_conferme_confronto_appaiato_e_margine():
    """Audit del 24 set: la figlia entra (validata subito) e la madre passa a
    `sostituita_da` SOLO se ha le conferme retroattive, la madre e' stata
    rivalutata nello STESSO giro, la batte su (ritorno - drawdown) col margine e
    vince in almeno 2 finestre su 3. Altrimenti non entra affatto."""
    from bot.core.firebase_client import decode_pairs
    from scripts.discover_strategies import merge_into_registry
    from scripts.optimize import MIN_PASSES, coppie_validate

    madre = _spec()
    figlia = figlie_intorno(madre)[0]
    fb = _fb_con({f"A|{madre['id']}": _rec(strategy=madre["id"], symbol="A"),
                  f"B|{madre['id']}": _rec(strategy=madre["id"], symbol="B"),
                  f"C|{madre['id']}": _rec(strategy=madre["id"], symbol="C")})
    out = {
        # A: madre rivalutata oggi; figlia +30% sul metro e vince 3 finestre su 3
        f"A|{madre['id']}": _entry("A", madre, 0, 0.50, 0.10, [0.1, 0.2, 0.2]),
        f"A|{figlia['id']}": _entry("A", figlia, MIN_PASSES - 1, 0.62, 0.10, [0.2, 0.3, 0.12]),
        # B: madre rivalutata, figlia +30% ma vince UNA finestra sola: fuori
        f"B|{madre['id']}": _entry("B", madre, 0, 0.50, 0.10, [0.1, 0.2, 0.2]),
        f"B|{figlia['id']}": _entry("B", figlia, MIN_PASSES - 1, 0.62, 0.10, [0.5, 0.05, 0.07]),
        # C: madre NON valutata oggi: nessun confronto, figlia fuori
        f"C|{figlia['id']}": _entry("C", figlia, MIN_PASSES - 1, 0.90, 0.05, [0.3, 0.3, 0.3]),
    }
    esito = {}
    merge_into_registry(fb, out, list(out), evaluated_symbols={"A", "B", "C"},
                        intorno_madri={f"{c}|{madre['id']}": 6 for c in "ABC"},
                        esito=esito)
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    fa, ma = pairs[f"A|{figlia['id']}"], pairs[f"A|{madre['id']}"]
    assert fa["pass_count"] == MIN_PASSES and fa.get("nata_intorno_at")
    assert ma["sostituita_da"] == figlia["id"] and ma.get("intorno_at")
    assert f"B|{figlia['id']}" not in pairs and f"C|{figlia['id']}" not in pairs
    assert not pairs[f"B|{madre['id']}"].get("sostituita_da")
    assert sorted(esito["scartate"]) == sorted([f"B|{figlia['id']}", f"C|{figlia['id']}"])
    op = coppie_validate(pairs, 1e9)
    assert f"A|{figlia['id']}" in op and f"A|{madre['id']}" not in op
    assert f"B|{madre['id']}" in op and f"C|{madre['id']}" in op


def test_due_figlie_della_stessa_madre_entra_solo_la_migliore():
    from bot.core.firebase_client import decode_pairs
    from scripts.discover_strategies import merge_into_registry
    from scripts.optimize import MIN_PASSES

    madre = _spec()
    f1, f2 = figlie_intorno(madre)[:2]
    fb = _fb_con({f"A|{madre['id']}": _rec(strategy=madre["id"], symbol="A")})
    out = {f"A|{madre['id']}": _entry("A", madre, 0, 0.50, 0.10, [0.1, 0.2, 0.2]),
           f"A|{f1['id']}": _entry("A", f1, MIN_PASSES - 1, 0.70, 0.10, [0.2, 0.3, 0.2]),
           f"A|{f2['id']}": _entry("A", f2, MIN_PASSES - 1, 0.90, 0.10, [0.3, 0.4, 0.2])}
    merge_into_registry(fb, out, list(out), evaluated_symbols={"A"},
                        intorno_madri={f"A|{madre['id']}": 2})
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert f"A|{f2['id']}" in pairs and f"A|{f1['id']}" not in pairs
    assert pairs[f"A|{madre['id']}"]["sostituita_da"] == f2["id"]


def test_variante_passata_solo_oggi_non_entra():
    """Una variante (referti o intorno) senza conferme retroattive muore subito:
    non entra nel registro, e la sua chiave torna in `esito["scartate"]` cosi'
    la discovery non la persiste ne' la annuncia."""
    from bot.core.firebase_client import decode_pairs
    from scripts.discover_strategies import merge_into_registry
    from bot.strategies.generator import varianti_da_referto

    madre = _spec()
    var = varianti_da_referto(madre, "solo_long")
    fb = _fb_con({f"A|{madre['id']}": _rec(strategy=madre["id"], symbol="A")})
    out = {f"A|{var['id']}": _entry("A", var, 0, 0.9, 0.05, [0.3, 0.3, 0.3])}
    esito = {}
    merge_into_registry(fb, out, list(out), evaluated_symbols={"A"}, esito=esito)
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert f"A|{var['id']}" not in pairs and esito["scartate"] == [f"A|{var['id']}"]
    # con le conferme retroattive entra, e la madre viene sostituita
    out[f"A|{var['id']}"]["conferme_retro"] = 2
    merge_into_registry(fb, out, list(out), evaluated_symbols={"A"})
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert pairs[f"A|{var['id']}"]["pass_count"] >= 3
    assert pairs[f"A|{madre['id']}"]["sostituita_da"] == var["id"]


def test_una_bocciatura_chiude_la_finestra_della_generata():
    """Audit del 24 set: una coppia generata a 1-2 conferme, valutata e NON
    passata con la finestra scaduta, prende UN fallimento e la finestra riparte:
    cosi' il giro «solo urgenti» si svuota invece di rivalutarla ogni tre ore."""
    from bot.core.firebase_client import decode_pairs
    from scripts.discover_strategies import merge_into_registry
    from scripts.optimize import NEW_DATA_MIN_S

    ora = 1e9
    fb = _fb_con({"A|gen_a": _rec(pass_count=1, strategy="gen_a", symbol="A",
                                  window_start=ora - NEW_DATA_MIN_S - 10, passed_in_window=False),
                  "A|gen_b": _rec(pass_count=1, strategy="gen_b", symbol="A",
                                  window_start=ora - 100, passed_in_window=False),
                  "Z|gen_a": _rec(pass_count=1, strategy="gen_a", symbol="Z",
                                  window_start=ora - NEW_DATA_MIN_S - 10, passed_in_window=False,
                                  last_seen_at=__import__("time").time())})
    merge_into_registry(fb, {}, [], evaluated_symbols={"A"},
                        evaluated_spec_ids={"gen_a", "gen_b"}, data_end_run=ora)
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert pairs["A|gen_a"]["fail_count"] == 1 and pairs["A|gen_a"]["window_start"] == int(ora)
    assert pairs["A|gen_a"]["pass_count"] == 1                    # nessuna conferma persa
    assert not pairs["A|gen_b"].get("fail_count")                 # finestra ancora aperta
    assert not pairs["Z|gen_a"].get("fail_count")                 # coin non valutata


def test_pf_per_direzione():
    from types import SimpleNamespace
    from scripts.discover_strategies import _pf_per_direzione
    tr = [SimpleNamespace(direction="long", pnl_pct=0.02), SimpleNamespace(direction="long", pnl_pct=-0.01),
          SimpleNamespace(direction="short", pnl_pct=-0.01), SimpleNamespace(direction="short", pnl_pct=-0.02)]
    d = _pf_per_direzione(tr)
    assert d["long"] == {"pf": 2.0, "n": 2} and d["short"] == {"pf": 0.0, "n": 2}
