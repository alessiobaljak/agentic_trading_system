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


def test_merge_promuove_la_figlia_solo_con_conferme_e_margine():
    """La figlia entra (validata subito) e la madre passa a `sostituita_da` SOLO
    se ha le conferme retroattive e batte la madre del 10%; altrimenti non
    entra affatto. Le madri riprovate ricevono `intorno_at`."""
    from bot.core.firebase_client import decode_pairs, encode_pairs
    from scripts.discover_strategies import merge_into_registry
    from scripts.optimize import MIN_PASSES, coppie_validate

    class FB:
        def __init__(self, pairs):
            self.docs = {("strategy_registry", "validated"): {"pairs": encode_pairs(pairs)}}
        def get_doc(self, c, dname): return self.docs.get((c, dname), {})
        def set_doc(self, c, dname, data): self.docs[(c, dname)] = data

    madre = _spec()
    figlia = figlie_intorno(madre)[0]
    fb = FB({f"A|{madre['id']}": _rec(strategy=madre["id"], symbol="A", last_pnl_pct=0.50),
             f"B|{madre['id']}": _rec(strategy=madre["id"], symbol="B", last_pnl_pct=0.50)})

    def entry(sym, retro, pnl):
        return {"symbol": sym, "strategy": figlia["id"], "params": {}, "spec": figlia,
                "oos_pf": 1.6, "oos_pnl_pct": pnl, "oos_trades": 40, "oos_win_rate": 0.5,
                "passed": True, "holdout": {"ok": True}, "data_end": 1e9,
                "conferme_retro": retro}
    out = {f"A|{figlia['id']}": entry("A", MIN_PASSES - 1, 0.60),   # +20%: promossa
           f"B|{figlia['id']}": entry("B", MIN_PASSES - 1, 0.52)}   # +4%: senza margine
    merge_into_registry(fb, out, list(out), evaluated_symbols={"A", "B"},
                        intorno_madri={f"A|{madre['id']}": 6, f"B|{madre['id']}": 6})
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    fa, ma = pairs[f"A|{figlia['id']}"], pairs[f"A|{madre['id']}"]
    assert fa["pass_count"] == MIN_PASSES and fa.get("nata_intorno_at")
    assert ma["sostituita_da"] == figlia["id"] and ma.get("intorno_at")
    assert f"B|{figlia['id']}" not in pairs                       # niente margine: fuori
    assert not pairs[f"B|{madre['id']}"].get("sostituita_da")
    assert pairs[f"B|{madre['id']}"].get("intorno_at")            # riprovata comunque
    # il bot opera la figlia e la madre B, NON la madre A
    op = coppie_validate(pairs, 1e9)
    assert f"A|{figlia['id']}" in op and f"B|{madre['id']}" in op
    assert f"A|{madre['id']}" not in op
