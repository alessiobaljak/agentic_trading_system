"""IL REGISTRO CHE SI E' RIEMPITO DI SE STESSO, e ha smesso di accumulare.

Il 31 agosto le coppie con almeno una conferma sono passate da 137 a 2 in quattro
giorni. Il meccanismo, una volta misurato, era questo:

  * l'universo e' il top-N per volume e RUOTA. Ogni coin mai scansionata lasciava
    dietro di se' 8 coppie base per sempre: nessuno le valutava piu', quindi non
    prendevano ne' conferme ne' fallimenti, e la potatura della discovery le
    risparmiava di proposito;
  * sono cresciute fino a **3041**, cioe' oltre il tetto di 3000 DA SOLE;
  * il tetto calcolava `gen_budget = max(0, 3000 - 3041)` = **zero**, e cancellava
    TUTTE le coppie generate a ogni passata;
  * le generate sono le uniche che passano il gate. La discovery ne trovava ottanta
    per giro, le scriveva, e la stessa funzione le buttava via subito dopo.

Nessun errore, nessun log, nessun test rosso: solo un registro che non poteva piu'
accumulare niente, per settimane. E' il difetto piu' costoso trovato finora, perche'
ha invalidato l'unica cosa che il sistema stava producendo.

I test qui sotto tengono chiuse tutte e due le porte: quella che ha fatto crescere
le base senza limite, e quella che ha lasciato che il tetto sacrificasse proprio le
coppie con conferme.
"""
import time

from bot.core.firebase_client import decode_pairs, encode_pairs


class _FB:
    """Firebase finto: tiene un documento in memoria."""

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


def _base(sym: str, visto: float) -> dict:
    return {"symbol": sym, "strategy": "breakout", "pass_count": 0,
            "last_seen_at": visto}


def _gen(sym: str, gid: str, passi: int, visto: float) -> dict:
    return {"symbol": sym, "strategy": gid, "generated": True,
            "pass_count": passi, "last_seen_at": visto}


# --------------------------------------------------------------------------- #
# 1. La causa: le coppie base crescevano per sempre                            #
# --------------------------------------------------------------------------- #
def test_base_pairs_of_coins_that_left_the_universe_are_removed():
    """L'universo ruota ogni giorno. Senza questa potatura ogni coin mai vista
    lasciava otto coppie per sempre, e in tre settimane hanno superato il tetto da
    sole. Chi torna nell'universo viene semplicemente ricreata al primo run."""
    from scripts.optimize import update_registry

    ora = time.time()
    fb = _FB({
        "VIVAUSDT|breakout": _base("VIVAUSDT", ora - 3600),
        "MORTAUSDT|breakout": _base("MORTAUSDT", ora - 30 * 86400),
        # una coppia con conferme non si tocca, per quanto vecchia
        "MORTAUSDT|momentum": {"symbol": "MORTAUSDT", "strategy": "momentum",
                               "pass_count": 3, "last_seen_at": ora - 30 * 86400},
    })
    out = {"VIVAUSDT|breakout": {"symbol": "VIVAUSDT", "strategy": "breakout",
                                 "params": {}, "oos_pf": 1.0, "oos_pnl_pct": 0.0,
                                 "oos_trades": 0, "oos_win_rate": 0.0,
                                 "passed": False, "data_end": ora}}
    update_registry(fb, out, [])
    dopo = fb.pairs()
    assert "VIVAUSDT|breakout" in dopo
    assert "MORTAUSDT|breakout" not in dopo, "coin fuori dall'universo: peso morto"
    assert "MORTAUSDT|momentum" in dopo, "le conferme non si buttano MAI"


# --------------------------------------------------------------------------- #
# 2. La garanzia: il tetto non puo' azzerare le generate                       #
# --------------------------------------------------------------------------- #
def test_the_cap_never_deletes_pairs_that_already_have_a_confirmation():
    """E' il difetto esatto del 31 agosto: base sopra il tetto -> budget zero ->
    tutte le generate cancellate, comprese quelle che avevano gia' pagato una
    settimana di attesa per la loro conferma.

    Se per tenerle si sfora il tetto, si sfora: e' `slim_registry` a togliere i
    campi descrittivi quando il documento cresce, e quello e' un prezzo pagabile.
    Cancellare passaggi veri no.
    """
    import os
    from scripts.discover_strategies import merge_into_registry

    ora = time.time()
    os.environ["OPTIMIZER_MAX_PAIRS"] = "50"
    try:
        pairs = {f"C{i}USDT|breakout": _base(f"C{i}USDT", ora) for i in range(60)}
        pairs.update({f"G{i}USDT|gen_x{i}": _gen(f"G{i}USDT", f"gen_x{i}", 1, ora)
                      for i in range(5)})
        fb = _FB(pairs)
        merge_into_registry(fb, {}, [])
        dopo = fb.pairs()
        sopravvissute = [k for k in dopo if k.startswith("G")]
        assert len(sopravvissute) == 5, (
            f"il tetto ha cancellato coppie con conferme: ne restano "
            f"{len(sopravvissute)} su 5")
    finally:
        os.environ.pop("OPTIMIZER_MAX_PAIRS", None)


def test_generated_pairs_without_a_confirmation_are_pruned_before_the_cap():
    """La prima versione della correzione riservava una quota anche alle generate
    SENZA conferme. Era codice morto e questo test l'ha mostrato subito: la potatura
    per `pass_count == 0` le toglie tutte un passo prima, quindi il tetto non le
    vede mai.

    Il test resta per fissare il perche': una difesa che protegge un insieme sempre
    vuoto non e' prudenza in piu', e' una riga che qualcuno un giorno leggera' come
    una garanzia che non c'e'.
    """
    import os
    from scripts.discover_strategies import merge_into_registry

    ora = time.time()
    os.environ["OPTIMIZER_MAX_PAIRS"] = "50"
    try:
        pairs = {f"C{i}USDT|breakout": _base(f"C{i}USDT", ora) for i in range(60)}
        pairs.update({f"G{i}USDT|gen_y{i}": _gen(f"G{i}USDT", f"gen_y{i}", 0, ora)
                      for i in range(40)})
        fb = _FB(pairs)
        merge_into_registry(fb, {}, [])
        assert [k for k in fb.pairs() if k.startswith("G")] == []
    finally:
        os.environ.pop("OPTIMIZER_MAX_PAIRS", None)
