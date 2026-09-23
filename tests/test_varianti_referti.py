"""LE VARIANTI DAI REFERTI NEL GATE (backlog B8, 23 set 2026).

«Una strategia generata non puo' essere ritarata: puo' solo morire.» Il
proprietario ha chiesto che il sistema impari da ogni trade. La strada onesta
NON e' spostare una soglia guardando il paper (il paper e' la prova, non il
training set): il paper PROPONE una variante della stessa idea — solo long,
conferma a 1 ora, stop piu' stretto — e il GATE la prova sulla storia come
qualunque candidata, tre conferme piu' holdout.

Cosa si protegge qui:
  1. gli id delle spec esistenti NON cambiano (il campo `solo` entra nell'hash
     solo se c'e'): altrimenti le spec note perderebbero storia e conferme;
  2. una spec «solo long» non produce mai uno short;
  3. ogni variante cambia UNA cosa sola, e quando non ha senso torna None;
  4. la variante non e' «gemella» del genitore per `scarta_gemelle`;
  5. la lettura dei referti e' fail-open e rispetta timeframe e tetto.
"""
import hashlib
import inspect
import json

from bot.config import settings
from bot.core.models import AssetSnapshot, Direction, IndicatorSnapshot, Regime
from bot.strategies.generated import GeneratedStrategy, spec_id
from bot.strategies.generator import _ATR_STOP, varianti_da_referto
from scripts import discover_strategies as d
from scripts.discover_strategies import firma_spec, scarta_gemelle, varianti_dai_referti


def _spec_rsi(**extra) -> dict:
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec.update(extra)
    spec["id"] = spec_id(spec)
    return spec


def _asset(rsi=50.0, price=100.0):
    ind = IndicatorSnapshot(timeframe="15m", rsi=rsi, atr=2.0, close=price,
                            bb_lower=95.0, bb_upper=105.0, bb_mid=100.0)
    return AssetSnapshot(symbol="BTCUSDT", price=price, regime=Regime.SIDEWAYS,
                         indicators={"15m": ind})


# --------------------------------------------------------------------------- #
# 1. Gli id delle spec esistenti non cambiano di una virgola                   #
# --------------------------------------------------------------------------- #
def test_spec_id_senza_solo_e_identico_alla_formula_di_prima():
    """La formula di `spec_id` PRIMA del 23 set, ricalcolata qui a mano: se
    l'hash cambiasse, ogni spec del registro diventerebbe una sconosciuta."""
    spec = _spec_rsi()
    payload = {
        "features": sorted((f.get("kind"), tuple(sorted((k, v) for k, v in f.items() if k != "kind")))
                           for f in spec["features"]),
        "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0,
        "timeframe": settings.ORCHESTRATOR_TIMEFRAME,
    }
    atteso = "gen_" + hashlib.sha1(
        json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:8]
    assert spec["id"] == atteso


def test_solo_vuoto_non_cambia_l_id_solo_long_si():
    base = _spec_rsi()
    assert spec_id({**base, "solo": None}) == base["id"]
    assert spec_id({**base, "solo": ""}) == base["id"]
    assert spec_id({**base, "solo": "long"}) != base["id"]
    assert spec_id({**base, "solo": "long"}) != spec_id({**base, "solo": "short"})


def test_origine_genitore_ipotesi_non_entrano_nell_id():
    """Sono etichette su DA DOVE viene la spec, non logica: due spec identiche
    nate in modi diversi sono la stessa strategia."""
    base = _spec_rsi()
    assert spec_id({**base, "origine": "referto", "genitore": "gen_x",
                    "ipotesi": "solo_long"}) == base["id"]


# --------------------------------------------------------------------------- #
# 2. «Solo long» non produce mai uno short                                     #
# --------------------------------------------------------------------------- #
def test_solo_long_non_produce_mai_short():
    """RSI 78 su `rsi_extreme` e' uno short netto: con `solo: long` non nasce.
    Il long a RSI 25 resta, e la descrizione dice il lato."""
    senza = GeneratedStrategy(_spec_rsi())
    assert senza.generate_signal(_asset(rsi=78.0)).direction == Direction.SHORT
    solo = GeneratedStrategy(_spec_rsi(solo="long"))
    assert solo.solo == "long"
    assert solo.generate_signal(_asset(rsi=78.0)) is None
    assert solo.generate_signal(_asset(rsi=25.0)).direction == Direction.LONG
    assert "[solo long]" in solo.description
    assert "[solo" not in senza.description and senza.solo is None


def test_solo_short_non_produce_mai_long():
    solo = GeneratedStrategy(_spec_rsi(solo="short"))
    assert solo.generate_signal(_asset(rsi=25.0)) is None
    assert solo.generate_signal(_asset(rsi=78.0)).direction == Direction.SHORT


# --------------------------------------------------------------------------- #
# 3. Ogni variante cambia una cosa sola                                        #
# --------------------------------------------------------------------------- #
def test_variante_solo_long_e_solo_short():
    gen = _spec_rsi(timeframe="1h")
    v = varianti_da_referto(gen, "solo_long")
    assert v["solo"] == "long" and v["id"] != gen["id"]
    assert v["origine"] == "referto" and v["genitore"] == gen["id"]
    assert v["ipotesi"] == "solo_long" and v["timeframe"] == "1h"
    assert v["features"] == gen["features"] and v["atr_mult_stop"] == gen["atr_mult_stop"]
    assert v["id"] == spec_id(v), "l'id e' ricalcolato sulla figlia"
    assert varianti_da_referto(gen, "solo_short")["solo"] == "short"
    # gia' su quel lato: niente da proporre
    assert varianti_da_referto(v, "solo_long") is None
    assert varianti_da_referto(v, "solo_short")["solo"] == "short"


def test_variante_conferma_trend_aggiunge_l_ora_una_volta_sola():
    gen = _spec_rsi()
    v = varianti_da_referto(gen, "conferma_trend")
    assert [f["kind"] for f in v["features"]] == ["rsi_extreme", "htf_confirm"]
    assert varianti_da_referto(v, "conferma_trend") is None, "ce l'ha gia'"
    fade = _spec_rsi(features=[{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                               {"kind": "htf_fade", "htf_gap": 0.01}])
    assert varianti_da_referto(fade, "conferma_trend") is None, "incoerente col fade"
    # tre feature + la conferma = quattro: ammesso, e' un filtro non un segnale
    tre = _spec_rsi(features=[{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                              {"kind": "bb_touch"}, {"kind": "volume_surge",
                                                     "vol_mult_feat": 1.5}])
    assert len(varianti_da_referto(tre, "conferma_trend")["features"]) == 4


def test_variante_stop_stretto_scende_di_un_gradino():
    assert varianti_da_referto(_spec_rsi(atr_mult_stop=2.5), "stop_stretto")["atr_mult_stop"] == 2.0
    assert varianti_da_referto(_spec_rsi(atr_mult_stop=1.5), "stop_stretto")["atr_mult_stop"] == 1.0
    assert varianti_da_referto(_spec_rsi(atr_mult_stop=min(_ATR_STOP)), "stop_stretto") is None
    # valore fuori lista: il gradino piu' grande sotto di lui
    assert varianti_da_referto(_spec_rsi(atr_mult_stop=1.7), "stop_stretto")["atr_mult_stop"] == 1.5
    assert varianti_da_referto(_spec_rsi(atr_mult_stop=0.5), "stop_stretto") is None


def test_variante_e_pura_e_non_tocca_il_genitore():
    gen = _spec_rsi()
    copia = json.loads(json.dumps(gen))
    for tipo in ("solo_long", "solo_short", "conferma_trend", "stop_stretto"):
        varianti_da_referto(gen, tipo)
    assert gen == copia
    assert varianti_da_referto(gen, "tipo_inventato") is None
    assert varianti_da_referto("non una spec", "solo_long") is None


# --------------------------------------------------------------------------- #
# 4. La variante non e' gemella del genitore                                   #
# --------------------------------------------------------------------------- #
def test_firma_spec_distingue_genitore_e_variante_solo():
    gen = _spec_rsi()
    assert firma_spec(gen) == firma_spec({**gen, "solo": None})
    assert firma_spec(gen) != firma_spec(varianti_da_referto(gen, "solo_long"))
    assert firma_spec(varianti_da_referto(gen, "solo_long")) != \
        firma_spec(varianti_da_referto(gen, "solo_short"))


def test_scarta_gemelle_tiene_la_variante_accanto_al_genitore():
    gen = _spec_rsi()
    figlie = [varianti_da_referto(gen, t)
              for t in ("solo_long", "conferma_trend", "stop_stretto")]
    tenute, scartate = scarta_gemelle([gen] + figlie, {gen["id"]: gen})
    assert scartate == 0 and len(tenute) == 4


# --------------------------------------------------------------------------- #
# 5. La lettura dei referti: timeframe, sconosciute, tetto, fail-open          #
# --------------------------------------------------------------------------- #
class _Fb:
    def __init__(self, doc=None, rotto=False):
        self.doc, self.rotto = doc, rotto

    def get_doc(self, coll, name):
        if self.rotto:
            raise RuntimeError("firestore giu'")
        assert (coll, name) == ("learning", "referti")
        return self.doc


def _ipotesi(gid, tipo):
    return {"strategia": gid, "tipo": tipo, "motivo": "test", "campione": 4}


def test_varianti_dai_referti_filtra_timeframe_e_sconosciute():
    tf = settings.ORCHESTRATOR_TIMEFRAME
    a = _spec_rsi()                                  # timeframe del bot
    b = _spec_rsi(timeframe="1h", atr_mult_stop=2.0)  # nativa a 1 ora
    existing = {a["id"]: a, b["id"]: b}
    doc = {"ipotesi": [_ipotesi(a["id"], "solo_long"), _ipotesi(b["id"], "solo_long"),
                       _ipotesi("gen_ignota", "solo_long"),
                       _ipotesi(a["id"], "solo_long")]}   # doppione
    out = varianti_dai_referti(_Fb(doc), existing, tf)
    assert [v["genitore"] for v in out] == [a["id"]]
    assert out[0]["solo"] == "long" and out[0]["id"] not in existing
    out_1h = varianti_dai_referti(_Fb(doc), existing, "1h")
    assert [v["genitore"] for v in out_1h] == [b["id"]] and out_1h[0]["timeframe"] == "1h"


def test_varianti_dai_referti_salta_le_gia_note_e_rispetta_il_tetto():
    tf = settings.ORCHESTRATOR_TIMEFRAME
    a = _spec_rsi()
    gia = varianti_da_referto(a, "solo_long")
    existing = {a["id"]: a, gia["id"]: gia}
    doc = {"ipotesi": [_ipotesi(a["id"], "solo_long"), _ipotesi(a["id"], "solo_short"),
                       _ipotesi(a["id"], "conferma_trend"),
                       _ipotesi(a["id"], "stop_stretto")]}
    tutte = varianti_dai_referti(_Fb(doc), existing, tf)
    assert sorted(v["ipotesi"] for v in tutte) == ["conferma_trend", "solo_short",
                                                   "stop_stretto"]
    assert len(varianti_dai_referti(_Fb(doc), existing, tf, limit=2)) == 2


def test_varianti_dai_referti_fail_open():
    """Senza documento, senza Firebase o con un documento storto il giro e'
    identico a prima: nessuna variante, nessuna eccezione."""
    existing = {_spec_rsi()["id"]: _spec_rsi()}
    tf = settings.ORCHESTRATOR_TIMEFRAME
    assert varianti_dai_referti(_Fb(rotto=True), existing, tf) == []
    assert varianti_dai_referti(_Fb(None), existing, tf) == []
    assert varianti_dai_referti(_Fb({}), existing, tf) == []
    assert varianti_dai_referti(_Fb({"ipotesi": "boh"}), existing, tf) == []
    assert varianti_dai_referti(_Fb({"ipotesi": [None, 3, {"strategia": None}]}),
                                existing, tf) == []
    # Un id genitore NON hashabile (lista, dict) fermava tutto il giro con un
    # TypeError invece di essere scartato: qui si protegge quel caso.
    assert varianti_dai_referti(_Fb({"ipotesi": [{"strategia": ["gen_x"], "tipo": "solo_long"},
                                                 {"strategia": {"id": "x"}, "tipo": "solo_long"}]}),
                                existing, tf) == []


def test_la_discovery_mette_davvero_le_varianti_in_coda():
    """Se la funzione esistesse ma `main` non la chiamasse, i test sopra
    sarebbero verdi e il gate non vedrebbe mai una variante. E le spec note
    devono essere lette PRIMA: una variante nasce da una spec gia' operata."""
    src = inspect.getsource(d.main)
    assert "varianti_dai_referti(fb, existing, args.interval)" in src
    assert src.index("existing = decode_pairs") < src.index("varianti_dai_referti(")
    assert "args.generate - len(ai_specs) - len(varianti)" in src, \
        "le varianti sostituiscono casuali, non allungano il giro"


def test_il_timbro_del_timeframe_non_cambia_l_id_della_variante():
    """In `main` le candidate nuove ricevono il timeframe della passata e l'id
    viene ricalcolato: per una variante gia' filtrata sullo stesso timeframe
    l'id deve restare quello, altrimenti `genitore -> id` nel log mentirebbe."""
    gen = _spec_rsi(timeframe="1h")
    v = varianti_da_referto(gen, "stop_stretto")
    assert spec_id({**v, "timeframe": "1h"}) == v["id"]


# --------------------------------------------------------------------------- #
# Rilievi dei revisori del 23 set: normalizzazione, contraddizione, mutazione  #
# --------------------------------------------------------------------------- #
def test_solo_normalizzato_nell_id_e_ignorato_se_non_valido():
    base = _spec_rsi()
    assert spec_id({**base, "solo": "Long"}) == spec_id({**base, "solo": "long"})
    assert spec_id({**base, "solo": "boh"}) == base["id"]      # come non averlo
    assert GeneratedStrategy({**base, "solo": "boh"}).solo is None


def test_solo_long_non_apre_dove_il_genitore_era_contraddittorio():
    """`rsi_momentum` con rsi == mid dice (True, True): il genitore non apre
    (contraddittorio) e la figlia «solo long» deve fare lo stesso, non
    trasformare la contraddizione in un long."""
    spec = {"features": [{"kind": "rsi_momentum", "mid": 50.0}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec["id"] = spec_id(spec)
    assert GeneratedStrategy(spec).generate_signal(_asset(rsi=50.0)) is None
    figlia = GeneratedStrategy({**spec, "solo": "long"})
    assert figlia.generate_signal(_asset(rsi=50.0)) is None
    assert figlia.generate_signal(_asset(rsi=60.0)).direction == Direction.LONG
    assert figlia.generate_signal(_asset(rsi=40.0)) is None


def test_mutate_conserva_il_lato():
    from bot.strategies.generator import mutate
    figlia = varianti_da_referto(_spec_rsi(), "solo_long")
    for seed in range(5):
        m = mutate(figlia, seed=seed)
        assert m["solo"] == "long" and m["id"] == spec_id(m)
