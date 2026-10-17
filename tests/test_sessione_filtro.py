"""LA SESSIONE ORARIA E' UN FILTRO, NON SCEGLIE IL LATO (27 set 2026, backlog J13).

Decisione del proprietario del 27 set: dentro la fascia `hour_from-hour_to` si
puo' operare in ENTRAMBI i versi (la direzione la danno le altre feature),
fuori in NESSUNO. Fino a quel giorno la feature sceglieva il lato (dentro solo
long, fuori solo short), senza nessuna ragione economica, ed era valutata con
l'orologio del giro invece che con l'ora della candela: le conferme delle
coppie che la usano (47 validate su 212, ops 0314) non dicevano niente sulla
spec. Per questo `discover_strategies.azzera_sessione` le fa ripartire da
zero passaggi, UNA volta, all'inizio del primo giro con questo codice.

Qui si difende: la semantica dei due lati, la combinazione con una feature
direzionale, il vocabolario del generatore, la migrazione su un registro finto
(campi azzerati, `last_params` tenuti, marcatore, seconda esecuzione a vuoto,
coin proprie e potatura), cosa vede il bot dopo, e la riga di `gate_progress`.
"""
import time
from datetime import datetime, timezone

import pytest

from bot.core import registry as reg_mod
from bot.core.firebase_client import decode_pairs, encode_pairs, encode_registry
from bot.core.models import AssetSnapshot, Regime
from bot.strategies import generated as g
from bot.strategies.generated import GeneratedStrategy
from bot.strategies.generator import _CONDITIONAL, _DIRECTIONAL, generate_specs
from scripts import discover_strategies as d
from scripts import gate_progress as gp
from scripts.optimize import (MIN_PASSES, NEW_DATA_MIN_S, REGISTRY_CORE_FIELDS,
                              conferme_da_proteggere)
from tests.test_spiega import _ind

NOW = 1_800_000_000.0
SPEC_S = {"id": "gen_s", "features": [{"kind": "rsi_extreme", "low": 20.0, "high": 75.0},
                                      {"kind": "session", "hour_from": 8, "hour_to": 16}],
          "atr_mult_stop": 1.5, "rr": 2.0}
SPEC_R = {"id": "gen_r", "features": [{"kind": "rsi_extreme", "low": 20.0, "high": 75.0}],
          "atr_mult_stop": 1.5, "rr": 2.0}


def _asset(ora: int, rsi: float) -> AssetSnapshot:
    ts = datetime(2026, 9, 27, ora, 30, tzinfo=timezone.utc).timestamp()
    return AssetSnapshot(symbol="XUSDT", price=1.42, close_chiusa=1.419, ts=ts,
                         regime=Regime.SIDEWAYS, indicators={"15m": _ind(rsi=rsi)})


@pytest.fixture(autouse=True)
def _avviso_pulito():
    g._AVVISO_ORA_CALENDARIO["stampato"] = False
    yield
    g._AVVISO_ORA_CALENDARIO["stampato"] = False


# --------------------------------------------------------------------------- #
# 1. la semantica: dentro entrambi i lati, fuori nessuno                       #
# --------------------------------------------------------------------------- #
def test_dentro_entrambi_i_lati_fuori_nessuno():
    f = {"kind": "session", "hour_from": 8, "hour_to": 16}
    for ora in (8, 12, 15):
        assert g._feat_session(None, 1.0, f, ora=ora) == (True, True)
    for ora in (0, 7, 16, 23):
        assert g._feat_session(None, 1.0, f, ora=ora) == (False, False)
    # giro di mezzanotte
    notte = {"kind": "session", "hour_from": 22, "hour_to": 4}
    assert g._feat_session(None, 1.0, notte, ora=23) == (True, True)
    assert g._feat_session(None, 1.0, notte, ora=3) == (True, True)
    assert g._feat_session(None, 1.0, notte, ora=4) == (False, False)
    assert g._feat_session(None, 1.0, notte, ora=12) == (False, False)


def test_con_una_feature_direzionale_dentro_decide_l_rsi_fuori_niente():
    st = GeneratedStrategy(SPEC_S)
    # DENTRO la fascia: il verso lo da' l'rsi, in entrambi i sensi
    v = st.spiega(_asset(13, rsi=80.0))
    assert v["features"]["session"]["long"] is True and v["features"]["session"]["short"] is True
    assert v["direzione_finale"] == "short"
    assert st.generate_signal(_asset(13, rsi=80.0)).direction.value == "short"
    v = st.spiega(_asset(13, rsi=15.0))
    assert v["direzione_finale"] == "long"
    assert st.generate_signal(_asset(13, rsi=15.0)).direction.value == "long"
    # FUORI: nessun segnale, qualunque cosa dica l'rsi, e la spiegazione lo dice
    for rsi in (80.0, 15.0):
        v = st.spiega(_asset(3, rsi=rsi))
        assert v["direzione_finale"] is None
        assert v["features"]["session"]["long"] is False and v["features"]["session"]["short"] is False
        assert "fermano session" in v["motivo"]
        assert v["features"]["session"]["valori"]["dentro"] is False
        assert st.generate_signal(_asset(3, rsi=rsi)) is None
    # e la stessa spec SENZA sessione opera anche alle 3: e' la sessione che ferma
    assert GeneratedStrategy(SPEC_R).generate_signal(_asset(3, rsi=80.0)) is not None


def test_la_combinazione_in_verdetto_e_un_and_sui_due_lati():
    """(False, False) mette a False sia long_ok che short_ok: veto su entrambi.
    (True, True) non tocca niente: da sola non da' una direzione."""
    solo_sessione = GeneratedStrategy({"id": "gen_solo", "features": [
        {"kind": "session", "hour_from": 8, "hour_to": 16}]})
    dentro = solo_sessione.spiega(_asset(13, rsi=50.0))
    assert dentro["direzione_finale"] is None and "contraddittorio" in dentro["motivo"]
    fuori = solo_sessione.spiega(_asset(3, rsi=50.0))
    assert fuori["direzione_finale"] is None and "fermano session" in fuori["motivo"]
    # due condizioni: se una ferma, ferma. Una fascia che lascia passare (8-16)
    # e una che alle 13 ferma (0-8): l'AND sui lati vince, niente segnale
    due = GeneratedStrategy({"id": "gen_due", "features": [
        {"kind": "rsi_extreme", "low": 20.0, "high": 75.0},
        {"kind": "session", "hour_from": 8, "hour_to": 16},
        {"kind": "session", "hour_from": 0, "hour_to": 8}]})
    v = due.spiega(_asset(13, rsi=80.0))
    assert v["direzione_finale"] is None
    assert v["features"]["session"]["long"] is True     # la prima lasciava passare
    assert v["features"]["session#2"]["long"] is False and v["features"]["session#2"]["short"] is False
    assert "fermano session#2" in v["motivo"]


def test_il_generatore_tiene_la_sessione_fra_le_condizioni_e_mai_da_sola():
    assert "session" in _CONDITIONAL and "session" not in _DIRECTIONAL
    specs = generate_specs(300, seed=5)
    con = [s for s in specs if g.usa_sessione(s)]
    assert con, "nessuna spec con la sessione su 300: il vocabolario l'ha persa"
    for s in con:
        assert any(f["kind"] in _DIRECTIONAL for f in s["features"]), s


# --------------------------------------------------------------------------- #
# 2. la migrazione sul registro finto                                          #
# --------------------------------------------------------------------------- #
class _FB:
    def __init__(self, pairs=None, specs=None):
        self.docs = {}
        self.scritture: list[tuple] = []
        if pairs is not None:
            self.docs[("strategy_registry", "validated")] = {
                "pairs": encode_pairs(pairs), "validated": [], "updated_at": 1.0,
                "universe_size": 10, "ready": True}
        if specs is not None:
            self.docs[("discovered_strategies", "specs")] = {"specs": encode_pairs(specs)}

    def get_doc(self, c, dname):
        return self.docs.get((c, dname))

    def set_doc(self, c, dname, data):
        self.scritture.append((c, dname))
        self.docs[(c, dname)] = data

    def pairs(self) -> dict:
        return decode_pairs(self.docs[("strategy_registry", "validated")]["pairs"])

    def registro(self) -> dict:
        return self.docs[("strategy_registry", "validated")]


def _rec(pass_count, **extra):
    r = {"generated": True, "pass_count": pass_count, "last_seen_at": NOW - 100,
         "last_passed_at": NOW - 200, "last_params": {"scale_r_mults": [2.0, 4.0]},
         "last_pnl_pct": 0.4, "window_start": NOW - 3600, "window_evals": 4,
         "window_passes": 3, "window_contata": True, "passed_in_window": True,
         "fail_count": 1, "validated_at": NOW - 5e5}
    r.update(extra)
    return r


SPECS = {"gen_s": SPEC_S, "gen_r": SPEC_R}
PAIRS = {
    "AUSDT|gen_s": _rec(MIN_PASSES, declassata=True, bocciata_notti=2, declassata_at=NOW - 10),
    "BUSDT|gen_s": _rec(1),
    "CUSDT|gen_r": _rec(MIN_PASSES),
    "DUSDT|gen_s": _rec(0),
    "EUSDT|gen_z": _rec(2),
}


def _migra(capsys=None):
    fb = _FB({k: dict(v) for k, v in PAIRS.items()}, SPECS)
    reg = fb.get_doc("strategy_registry", "validated")
    existing = decode_pairs(fb.get_doc("discovered_strategies", "specs")["specs"])
    doc = d.azzera_sessione(fb, existing, reg, NOW)
    return fb, doc


def test_azzera_le_coppie_con_sessione_e_tiene_il_resto(capsys):
    fb, doc = _migra()
    pairs = fb.pairs()
    for k in ("AUSDT|gen_s", "BUSDT|gen_s"):
        r = pairs[k]
        assert r["pass_count"] == 0 and r["fail_count"] == 0
        assert r["passed_in_window"] is False
        for campo in ("window_start", "window_evals", "window_passes", "window_contata"):
            assert campo not in r, (k, campo)
        assert r["declassata"] is False and r["bocciata_notti"] == 0
        assert r["sessione_azzerata_at"] == NOW
        # il record e i suoi parametri restano: la coppia e' ancora NOTA
        assert r["last_params"] == {"scale_r_mults": [2.0, 4.0]}
        assert r["generated"] is True
    # senza sessione, a zero pass, o senza spec: intatte
    assert fb.pairs()["CUSDT|gen_r"]["pass_count"] == MIN_PASSES
    assert "sessione_azzerata_at" not in pairs["CUSDT|gen_r"]
    assert pairs["DUSDT|gen_s"]["pass_count"] == 0 and "sessione_azzerata_at" not in pairs["DUSDT|gen_s"]
    assert pairs["EUSDT|gen_z"]["pass_count"] == 2 and "sessione_azzerata_at" not in pairs["EUSDT|gen_z"]
    # il registro e' stato scritto UNA volta, con la lista delle validate rifatta
    assert fb.scritture.count(("strategy_registry", "validated")) == 1
    assert doc is fb.registro()
    assert doc["validated"] == ["CUSDT|gen_r"]
    assert doc["updated_at"] == NOW and doc["coins"] == ["CUSDT"]
    # il marcatore, scritto DOPO il registro
    assert fb.scritture[-1] == ("strategy_params", "migrazioni")
    m = fb.get_doc("strategy_params", "migrazioni")
    assert m["sessione_lato_at"] == NOW and m["sessione_lato_n"] == 2 and m["sessione_lato_validate"] == 1
    out = capsys.readouterr().out
    assert ("[cervello] sessione: 2 coppie azzerate (1 validate) perche' la feature ha "
            "cambiato significato: ripartono da zero passaggi") in out


def test_la_migrazione_gira_una_volta_sola():
    fb, _ = _migra()
    n = len(fb.scritture)
    # secondo giro, anche molto dopo: il marcatore la ferma, niente si riscrive
    doc2 = d.azzera_sessione(fb, SPECS, fb.registro(), NOW + 7 * 86400)
    assert len(fb.scritture) == n and doc2 is fb.registro()
    assert fb.get_doc("strategy_params", "migrazioni")["sessione_lato_at"] == NOW


def test_senza_registro_o_senza_spec_non_si_segna_niente(capsys):
    fb = _FB(None, SPECS)
    assert d.azzera_sessione(fb, SPECS, None, NOW) == {}
    assert fb.get_doc("strategy_params", "migrazioni") is None
    fb = _FB(PAIRS, None)
    reg = fb.registro()
    assert d.azzera_sessione(fb, {}, reg, NOW) is reg
    assert fb.get_doc("strategy_params", "migrazioni") is None and fb.scritture == []
    assert "rimandato al prossimo giro" in capsys.readouterr().out


def test_le_azzerate_restano_coin_proprie_e_protette_ma_non_validate():
    fb, doc = _migra()
    pairs = fb.pairs()
    proprie = d.coin_proprie_delle_spec(pairs)
    assert proprie["gen_s"] == {"AUSDT", "BUSDT"}        # non DUSDT: zero pass e mai azzerata
    assert proprie["gen_r"] == {"CUSDT"}
    # il bot non le opera piu': la regola condivisa le esclude
    assert reg_mod.coppie_validate(pairs, NOW) == ["CUSDT|gen_r"]
    assert reg_mod.coppie_validate(pairs, NOW) == doc["validated"]
    # la potatura le protegge per MIN_PASSES finestre dall'azzeramento, poi no
    a = pairs["AUSDT|gen_s"]
    assert conferme_da_proteggere(a, NOW) is True
    assert conferme_da_proteggere(a, NOW + MIN_PASSES * NEW_DATA_MIN_S - 1) is True
    assert conferme_da_proteggere(a, NOW + MIN_PASSES * NEW_DATA_MIN_S + 1) is False
    assert conferme_da_proteggere(pairs["DUSDT|gen_s"], NOW) is False
    # e il giro completo le rigiudica anche con il cap a zero
    scelte, diag = d.specs_da_rivalutare(SPECS, doc, cap=0, completa=True, now=NOW)
    assert {s["id"] for s in scelte} == {"gen_s", "gen_r"}
    # nel giro «solo urgenti» non sono urgenti: niente finestra aperta (le
    # altre due spec, con la finestra scaduta, lo sono)
    assert d.spec_urgenti(pairs, NOW + NEW_DATA_MIN_S) == {"gen_r", "gen_z"}


def test_il_merge_non_pota_un_azzerata():
    fb, _ = _migra()
    d.merge_into_registry(fb, {}, [], evaluated_symbols=set(), esito={}, completa=False)
    pairs = fb.pairs()
    assert "AUSDT|gen_s" in pairs and pairs["AUSDT|gen_s"]["sessione_azzerata_at"] == NOW
    assert "BUSDT|gen_s" in pairs
    assert "DUSDT|gen_s" not in pairs                     # zero pass e mai azzerata: via, come sempre


def test_il_campo_sopravvive_all_alleggerimento_e_al_codec():
    assert "sessione_azzerata_at" in REGISTRY_CORE_FIELDS
    rec = {"generated": True, "pass_count": 0, "sessione_azzerata_at": NOW + 0.7, "last_pnl_pct": 0.3}
    fuori = decode_pairs(encode_registry({"AUSDT|gen_s": rec}))["AUSDT|gen_s"]
    assert fuori["sessione_azzerata_at"] == int(NOW)      # un epoch intero, come gli altri tempi


def test_il_bot_smette_di_aprire_le_azzerate_alla_ricarica(monkeypatch):
    from bot.config import settings
    from bot.learning.adaptation import AdaptationEngine
    monkeypatch.setattr(settings, "MIN_COINS_PER_STRATEGY", 1)
    fb = _FB({k: dict(v) for k, v in PAIRS.items()}, SPECS)
    fb.registro()["validated"] = ["AUSDT|gen_s", "CUSDT|gen_r"]
    ad = AdaptationEngine(firebase=fb)
    ad.load_params()
    assert ad._passed == {"AUSDT|gen_s", "CUSDT|gen_r"}
    assert ad.registro_cambiato() is False
    d.azzera_sessione(fb, SPECS, fb.registro(), NOW)
    assert ad.registro_cambiato() is True                # `updated_at` e' cambiato: ricarica
    ad.load_params()
    assert ad._passed == {"CUSDT|gen_r"}
    assert "AUSDT|gen_s" not in ad._params


# --------------------------------------------------------------------------- #
# 3. la visibilita'                                                            #
# --------------------------------------------------------------------------- #
def test_gate_progress_conta_le_azzerate():
    fb, doc = _migra()
    pairs = fb.pairs()
    riga = gp.riga_sessione(doc["validated"], SPECS, pairs)
    assert riga.startswith("  FEATURE session: 0 validate su 1 usano la sessione oraria")
    assert riga.endswith(" · 2 azzerate il 27 set, ripassano da zero")
    # una che ripassa torna validata e la coda lo dice
    pairs["AUSDT|gen_s"]["pass_count"] = MIN_PASSES
    riga = gp.riga_sessione(reg_mod.coppie_validate(pairs, NOW), SPECS, pairs)
    assert riga.startswith("  FEATURE session: 1 validate su 2 usano la sessione oraria")
    assert riga.endswith(" · 2 azzerate il 27 set, ripassano da zero (1 gia' ripassate)")
    # senza azzerate, la riga e' quella di prima
    assert "azzerate" not in gp.riga_sessione(["CUSDT|gen_r"], SPECS, {"CUSDT|gen_r": PAIRS["CUSDT|gen_r"]})
