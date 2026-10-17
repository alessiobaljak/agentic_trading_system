"""IL TAGLIO CHE BUTTAVA VIA LE COPPIE PIU' VICINE ALLA VALIDAZIONE.

La discovery ri-valuta al massimo `--reeval-cap` spec gia' note per run (in
produzione 500), per tenere limitato il tempo di un giro. Fin qui, giusto.

Il problema era il CRITERIO del taglio. Restavano dentro le spec piu' vecchie, e
protette dal taglio erano solo quelle GIA' VALIDATE — che sono zero da quando il
registro esiste nella forma attuale. Quindi una spec a 2 passaggi su 3 stava dentro
o fuori a seconda di quando era stata scoperta: un criterio che con le conferme non
c'entra niente.

E restare fuori non vuol dire "aspetta il prossimo giro". Nella discovery
`judge_window` viene chiamato SOLO sulle coppie che passano: una spec che non viene
ri-valutata non passa, quindi non prende ne' la conferma ne' il fallimento. Non
matura: si ferma, mentre il rapporto continua a stampare per lei una data di
validazione.

E' la stessa forma dei due difetti gia' trovati — un tetto messo per limitare i
tempi che finisce per sacrificare l'unica cosa che il sistema produce. Questi test
fissano il criterio nuovo: **prima le conferme, poi l'anzianita'**.
"""
from bot.core.firebase_client import encode_pairs
from scripts.discover_strategies import specs_da_rivalutare


def _spec(gid: str) -> dict:
    return {"id": gid, "features": []}


def _reg(conferme: dict[str, int]) -> dict:
    """Registro finto: una coppia generata per spec, col suo pass_count."""
    return {"pairs": encode_pairs({
        f"AUSDT|{gid}": {"symbol": "AUSDT", "strategy": gid,
                         "generated": True, "pass_count": n}
        for gid, n in conferme.items()})}


def test_a_spec_with_confirmations_is_never_cut():
    """E' il difetto esatto: `gen_vecchia` sta in cima solo perche' e' vecchia, e
    `gen_quasi` — a due conferme su tre — cadeva fuori dal cap."""
    existing = {f"gen_riempitivo{i}": _spec(f"gen_riempitivo{i}") for i in range(50)}
    existing["gen_quasi"] = _spec("gen_quasi")      # scoperta per ultima
    scelte, diag = specs_da_rivalutare(existing, _reg({"gen_quasi": 2}), cap=10)

    assert any(s["id"] == "gen_quasi" for s in scelte), (
        "una coppia a 2/3 fuori dal taglio non arrivera' MAI a 3: non viene "
        "ri-valutata, quindi non puo' ripassare il gate")
    assert diag["n_specs_con_conferme"] == 1
    assert len(scelte) == 10


def test_confirmations_come_before_the_ones_without():
    """L'ordine conta anche dentro il taglio: se le spec con conferme finissero in
    coda, basterebbe abbassare il cap per perderle di nuovo."""
    existing = {"gen_a": _spec("gen_a"), "gen_b": _spec("gen_b"),
                "gen_c": _spec("gen_c")}
    scelte, _ = specs_da_rivalutare(existing, _reg({"gen_c": 1}), cap=3)
    assert scelte[0]["id"] == "gen_c"


def test_more_confirmations_first():
    """Fra due coppie in attesa, quella a 2/3 e' piu' vicina al traguardo di una a
    1/3: se il cap dovesse mordere davvero, si perde la meno avanti."""
    existing = {"gen_uno": _spec("gen_uno"), "gen_due": _spec("gen_due")}
    scelte, _ = specs_da_rivalutare(
        existing, _reg({"gen_uno": 1, "gen_due": 2}), cap=2)
    assert [s["id"] for s in scelte] == ["gen_due", "gen_uno"]


def test_the_cap_is_exceeded_rather_than_dropping_a_confirmation():
    """Se le spec con conferme sono piu' del cap, si sfora. Il cap esiste per
    limitare i TEMPI di un run; rinunciare a una conferma per stare nei tempi vuol
    dire non arrivare mai in fondo, che non e' un risparmio."""
    conferme = {f"gen_p{i}": 1 for i in range(20)}
    existing = {g: _spec(g) for g in conferme}
    scelte, diag = specs_da_rivalutare(existing, _reg(conferme), cap=5)
    assert len(scelte) == 20
    assert diag["n_specs_tagliate"] == 0


def test_without_confirmations_it_behaves_exactly_as_before():
    """Nessuna conferma nel registro: resta l'ordine di scoperta, tagliato al cap.
    La correzione non deve cambiare il comportamento dove non c'era niente da
    proteggere."""
    existing = {f"gen_{i}": _spec(f"gen_{i}") for i in range(10)}
    scelte, diag = specs_da_rivalutare(existing, _reg({}), cap=4)
    assert [s["id"] for s in scelte] == ["gen_0", "gen_1", "gen_2", "gen_3"]
    assert diag["n_specs_tagliate"] == 6


def test_a_base_pair_does_not_promote_a_spec():
    """Le coppie base non sono spec generate: se il loro pass_count contasse qui,
    proteggerebbe una spec a caso che condivide il nome della strategia."""
    existing = {"breakout": _spec("breakout"), "gen_a": _spec("gen_a")}
    reg = {"pairs": encode_pairs({
        "AUSDT|breakout": {"symbol": "AUSDT", "strategy": "breakout",
                           "pass_count": 3}})}      # niente `generated`
    _, diag = specs_da_rivalutare(existing, reg, cap=1)
    assert diag["n_specs_con_conferme"] == 0
