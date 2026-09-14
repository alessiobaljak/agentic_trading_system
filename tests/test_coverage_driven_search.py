"""LA RICERCA DEVE ANDARE DOVE NON COPRIAMO ANCORA.

Obiettivo dichiarato dal proprietario il 14 settembre: «l'importante e' che il
sistema continui a trovare nuove monete e strategie; se ci sono monete che non
copriamo dobbiamo focalizzarci su quelle — un sistema che non si ferma mai».

Il ciclo delle mutazioni evolve attorno ai QUASI-PASSAGGI del giro precedente. E'
efficiente, ma prendeva i semi nell'ordine in cui capitavano: quindi tendeva a
rinforzare le coin dove qualcosa gia' funziona. Il numero che decide quante monete
il bot potra' operare — le coin COPERTE — non ne beneficiava.

Il 14 settembre il registro aveva 7 coppie validate, tutte sulla STESSA moneta.
Un'ottava strategia su quella moneta non aggiunge una moneta operabile: la prima su
una moneta nuova si'. Da qui la precedenza.

Questi test fissano la precedenza E il suo limite: non si abbandonano del tutto le
coin coperte, perche' una coin con una sola coppia validata e' fragile.
"""
from scripts.discover_strategies import mutation_seeds


class _FB:
    """Firebase finto con la sola autopsia che `mutation_seeds` legge."""

    def __init__(self, near):
        self.near = near

    def get_doc(self, coll, doc_id):
        if coll == "gate_autopsy" and doc_id == "discover":
            return {"near_misses": self.near}
        return {}


def _spec(gid):
    return {"id": gid, "features": []}


SPECS = {f"gen_{c}": _spec(f"gen_{c}") for c in "abcdefgh"}


def _validata(sym):
    return {"symbol": sym, "generated": True, "pass_count": 3}


def test_seeds_prefer_coins_we_do_not_cover_yet():
    """Il caso del 14 settembre: ORCAUSDT gia' coperta, le altre no."""
    fb = _FB([
        {"key": "ORCAUSDT|gen_a"},
        {"key": "ORCAUSDT|gen_b"},
        {"key": "NUOVAUSDT|gen_c"},
    ])
    pairs = {"ORCAUSDT|gen_x": _validata("ORCAUSDT")}
    out = mutation_seeds(fb, SPECS, limit=1, pairs=pairs)
    assert [s["id"] for s in out] == ["gen_c"], (
        "il seme e' andato su una coin gia' coperta: una strategia in piu' li' non "
        "aggiunge una moneta operabile")


def test_covered_coins_are_not_abandoned():
    """L'errore opposto. Una coin con UNA sola coppia validata e' fragile: se quella
    smette di funzionare la copertura torna indietro. Quando restano slot liberi, i
    semi sulle coin coperte li prendono."""
    fb = _FB([{"key": "ORCAUSDT|gen_a"}, {"key": "NUOVAUSDT|gen_c"}])
    pairs = {"ORCAUSDT|gen_x": _validata("ORCAUSDT")}
    out = mutation_seeds(fb, SPECS, limit=10, pairs=pairs)
    assert {s["id"] for s in out} == {"gen_c", "gen_a"}
    assert out[0]["id"] == "gen_c", "prima comunque chi estende la copertura"


def test_a_coin_with_confirmations_but_not_validated_still_counts_as_uncovered():
    """Due conferme su tre non rendono una moneta operabile: il bot opera solo le
    VALIDATE. Finche' non ci arriva, cercare li' estende ancora la copertura."""
    fb = _FB([{"key": "QUASIUSDT|gen_a"}])
    pairs = {"QUASIUSDT|gen_y": {"symbol": "QUASIUSDT", "generated": True,
                                 "pass_count": 2}}
    out = mutation_seeds(fb, SPECS, limit=1, pairs=pairs)
    assert [s["id"] for s in out] == ["gen_a"]


def test_without_the_registry_it_behaves_exactly_as_before():
    """Fail-open: se il registro non arriva, si torna all'ordine dei quasi-passaggi.
    Una ricerca che si ferma perche' manca un dato diagnostico sarebbe peggio di una
    ricerca non guidata."""
    fb = _FB([{"key": "AUSDT|gen_b"}, {"key": "BUSDT|gen_a"}])
    out = mutation_seeds(fb, SPECS, limit=2)
    assert [s["id"] for s in out] == ["gen_b", "gen_a"]


def test_the_same_spec_is_not_seeded_twice():
    """Una spec che quasi passa su tre coin comparirebbe tre volte, e mangerebbe tre
    slot di mutazione per evolvere sempre la stessa idea — il contrario di cercare
    largo."""
    fb = _FB([{"key": "AUSDT|gen_a"}, {"key": "BUSDT|gen_a"}, {"key": "CUSDT|gen_b"}])
    out = mutation_seeds(fb, SPECS, limit=3, pairs={})
    assert [s["id"] for s in out] == ["gen_a", "gen_b"]


def test_it_survives_an_unreadable_autopsy():
    class Rotto:
        def get_doc(self, *a):
            raise RuntimeError("firestore giu'")

    assert mutation_seeds(Rotto(), SPECS, pairs={}) == []
