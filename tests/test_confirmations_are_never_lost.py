"""UNA COPPIA CON CONFERME NON SI PERDE. Mai, per nessuna porta.

Questo file nasce da una domanda del proprietario, il 14 settembre: «ogni volta
trovi un problema diverso». Non erano problemi diversi. Erano lo stesso problema
quattro volte, e ogni volta e' emerso solo quando la fila era arrivata a quel
gradino:

| gradino                | cosa buttava via cio' che stavamo aspettando        |
|------------------------|-----------------------------------------------------|
| arrivare alla 1a       | il tetto del registro cancellava tutte le generate   |
| arrivare alla 2a       | la contabilita' rendeva la 3a irraggiungibile       |
| arrivare alla 3a       | il taglio della ri-valutazione ordinato per eta'    |
| arrivare alla 3a       | la coin esce dall'universo e la coppia si congela   |
| arrivare alla 3a       | ...e sei giorni dopo veniva CANCELLATA              |

L'ultima riga e' quella trovata durante il controllo unico chiesto dal
proprietario: la potatura per anzianita' della discovery cancellava le coppie
generate con `pass_count < MIN_PASSES` non viste da sei giorni — cioe' proprio
quelle a una o due conferme — dieci righe sopra un commento che promette «le coppie
con almeno una conferma non si toccano MAI». Le otto coppie ORCAUSDT a 2/3 sarebbero
sparite il 19 settembre.

Invece di aspettare il quinto, questo file fissa l'INVARIANTE una volta sola, e lo
verifica su ogni percorso che puo' romperlo. Se domani qualcuno aggiunge un tetto,
un filtro o una potatura, uno di questi test diventa rosso.

    UNA COPPIA CON ALMENO UNA CONFERMA RECENTE:
      * non viene cancellata da nessuna potatura;
      * non viene esclusa dalla ri-valutazione;
      * la sua coin resta nell'universo guardato;
      * non perde i campi che la rendono riconoscibile.
"""
import os
import time

from bot.core.firebase_client import decode_pairs, encode_pairs
from scripts.optimize import (MIN_PASSES, REGISTRY_CORE_FIELDS, coin_in_maturazione,
                              conferme_da_proteggere, slim_registry)


class _FB:
    def __init__(self, pairs: dict):
        self.docs = {("strategy_registry", "validated"): {"pairs": encode_pairs(pairs)}}

    def get_doc(self, c, d):
        return self.docs.get((c, d), {})

    def set_doc(self, c, d, data):
        self.docs[(c, d)] = data

    def query_collection(self, *a, **k):
        return []

    def pairs(self) -> dict:
        return decode_pairs(self.get_doc("strategy_registry", "validated")["pairs"])


def _mezza_strada(sym: str, gid: str, visto_giorni_fa: float) -> dict:
    """Una coppia a 2 conferme su 3 la cui coin e' uscita dall'universo."""
    ora = time.time()
    return {"symbol": sym, "strategy": gid, "generated": True, "pass_count": 2,
            "last_pass_data_end": ora - 8 * 86400,
            "window_start": ora - 8 * 86400,
            "last_seen_at": ora - visto_giorni_fa * 86400}


# --------------------------------------------------------------------------- #
# 1. La potatura per anzianita' della discovery: il difetto del 14 settembre    #
# --------------------------------------------------------------------------- #
def test_the_stale_prune_does_not_delete_a_pair_halfway():
    """IL CASO ORCAUSDT. La coin esce dall'universo il 13; nessuno valuta piu' le
    sue otto coppie a 2/3; sei giorni dopo venivano cancellate — non per un
    verdetto, ma per non essere state guardate. Otto settimane di attesa buttate da
    una condizione che nessuno confrontava col commento sotto."""
    from scripts.discover_strategies import merge_into_registry

    fb = _FB({f"ORCAUSDT|gen_{i}": _mezza_strada("ORCAUSDT", f"gen_{i}", 10)
              for i in range(8)})
    merge_into_registry(fb, {}, [])
    rimaste = [k for k in fb.pairs() if k.startswith("ORCAUSDT")]
    assert len(rimaste) == 8, (
        f"cancellate {8 - len(rimaste)} coppie a 2/3 solo perche' la coin e' uscita "
        f"dall'universo: non e' un verdetto, e' una perdita")


def test_a_pair_that_stopped_passing_long_ago_is_still_pruned():
    """La difesa non deve diventare «non si cancella mai niente»: il registro
    crescerebbe senza limite, che e' il difetto del 31 agosto dall'altro lato."""
    from scripts.discover_strategies import merge_into_registry

    ora = time.time()
    fb = _FB({"MORTAUSDT|gen_x": {
        "symbol": "MORTAUSDT", "strategy": "gen_x", "generated": True,
        "pass_count": 1, "last_pass_data_end": ora - 40 * 86400,
        "last_seen_at": ora - 40 * 86400}})
    merge_into_registry(fb, {}, [])
    assert "MORTAUSDT|gen_x" not in fb.pairs()


def test_a_validated_pair_is_never_pruned_here():
    """Le validate sono quelle che il bot opera: toglierle in silenzio cambierebbe
    cosa fa il sistema senza che nessuno l'abbia deciso."""
    from scripts.discover_strategies import merge_into_registry

    ora = time.time()
    fb = _FB({"AUSDT|gen_v": {
        "symbol": "AUSDT", "strategy": "gen_v", "generated": True,
        "pass_count": MIN_PASSES, "last_pass_data_end": ora - 40 * 86400,
        "last_seen_at": ora - 40 * 86400}})
    merge_into_registry(fb, {}, [])
    assert "AUSDT|gen_v" in fb.pairs()


# --------------------------------------------------------------------------- #
# 2. La potatura delle base: il commento diceva una cosa, il codice un'altra    #
# --------------------------------------------------------------------------- #
def test_the_base_prune_keeps_a_pair_with_confirmations():
    """`update_registry` diceva in commento «chi ha conferme non si tocca» e in
    codice `pass_count < MIN_PASSES`, cioe' il contrario per chi ne ha una o due.
    Un commento che promette una garanzia che il codice non da' e' peggio di
    nessun commento: qualcuno ci costruira' sopra."""
    from scripts.optimize import update_registry

    ora = time.time()
    fb = _FB({"FUORIUSDT|breakout": {
        "symbol": "FUORIUSDT", "strategy": "breakout", "pass_count": 2,
        "last_pass_data_end": ora - 2 * 86400,
        "last_seen_at": ora - 10 * 86400}})
    update_registry(fb, {}, [])
    assert "FUORIUSDT|breakout" in fb.pairs()


# --------------------------------------------------------------------------- #
# 3. Il tetto sul numero di coppie: il difetto del 31 agosto                    #
# --------------------------------------------------------------------------- #
def test_the_cap_still_protects_pairs_with_confirmations():
    """Gia' coperto da tests/test_registry_capacity.py; qui si ricontrolla insieme
    agli altri, perche' l'invariante e' uno solo e va letto in un posto solo."""
    from scripts.discover_strategies import merge_into_registry

    ora = time.time()
    os.environ["OPTIMIZER_MAX_PAIRS"] = "50"
    try:
        pairs = {f"B{i}USDT|breakout": {"symbol": f"B{i}USDT", "strategy": "breakout",
                                        "pass_count": 0, "last_seen_at": ora}
                 for i in range(60)}
        pairs.update({f"G{i}USDT|gen_{i}": _mezza_strada(f"G{i}USDT", f"gen_{i}", 0)
                      for i in range(5)})
        fb = _FB(pairs)
        merge_into_registry(fb, {}, [])
        assert len([k for k in fb.pairs() if k.startswith("G")]) == 5
    finally:
        os.environ.pop("OPTIMIZER_MAX_PAIRS", None)


# --------------------------------------------------------------------------- #
# 4. Il taglio della ri-valutazione                                            #
# --------------------------------------------------------------------------- #
def test_the_reevaluation_cut_still_keeps_them():
    from scripts.discover_strategies import specs_da_rivalutare

    existing = {f"riempitivo{i}": {"id": f"riempitivo{i}"} for i in range(50)}
    existing["gen_quasi"] = {"id": "gen_quasi"}
    reg = {"pairs": encode_pairs({"AUSDT|gen_quasi": _mezza_strada("AUSDT", "gen_quasi", 0)})}
    scelte, _ = specs_da_rivalutare(existing, reg, cap=5)
    assert any(s["id"] == "gen_quasi" for s in scelte)


# --------------------------------------------------------------------------- #
# 5. L'universo guardato                                                       #
# --------------------------------------------------------------------------- #
def test_the_coin_stays_in_the_scanned_universe():
    ora = time.time()
    assert coin_in_maturazione({"A|g": _mezza_strada("ORCAUSDT", "g", 3)}, ora) == \
        ["ORCAUSDT"]


# --------------------------------------------------------------------------- #
# 6. L'alleggerimento del documento                                            #
# --------------------------------------------------------------------------- #
def test_slimming_keeps_everything_the_survival_depends_on():
    """Quando il registro sfora, `slim_registry` toglie i campi descrittivi. Se fra
    quelli finisse un campo da cui dipende la sopravvivenza, la perdita arriverebbe
    un giorno dopo e da tutt'altra parte — il modo peggiore in cui un difetto puo'
    presentarsi."""
    ora = time.time()
    r = _mezza_strada("AUSDT", "gen_a", 0)
    # tutti i campi che le difese qui sopra leggono devono sopravvivere
    for campo in ("pass_count", "last_pass_data_end", "generated", "symbol",
                  "window_start", "last_seen_at", "last_passed_at"):
        assert campo in REGISTRY_CORE_FIELDS, f"`{campo}` si perde alleggerendo"

    grosse = {f"K{i}USDT|gen_{i}": {**_mezza_strada(f"K{i}USDT", f"gen_{i}", 0),
                                    "zavorra": "x" * 400} for i in range(400)}
    grosse["AUSDT|gen_a"] = r
    dopo = decode_pairs(slim_registry(grosse, [], max_bytes=1000))
    assert conferme_da_proteggere(dopo["AUSDT|gen_a"], ora), (
        "alleggerita, la coppia non risulta piu' in maturazione: verrebbe potata")
    assert dopo["AUSDT|gen_a"].get("generated") is True
