"""L'UNIVERSO RUOTA, LA VALIDAZIONE NO.

Il 13 settembre ORCAUSDT e' uscita dal top-N per volume con **otto** coppie a 2
conferme su 3, il giorno stesso in cui la loro finestra scadeva. Hanno avuto un
tentativo, uno solo, e poi il sistema ha smesso di guardarle.

Non e' sfortuna isolata: fra l'8 e il 14 settembre il 26% dell'universo e' cambiato
(misura sugli snapshot committati in `docs/state.md`), mentre una coppia ha bisogno
di MIN_PASSES finestre da una settimana — almeno due settimane in cui la sua coin
deve restare dentro.

E uscire non e' fallire. Nella discovery `judge_window` e' chiamato solo sulle coppie
che passano: una coppia che nessuno valuta non passa, quindi non prende ne' la
conferma ne' il fallimento. Si ferma a meta' strada mentre il calendario continua a
stamparle accanto una data di validazione — la stessa forma di finzione gia' corretta
tre volte in `scripts/gate_progress.py`.
"""
import time

from scripts.optimize import coin_in_maturazione


def _gen(sym: str, passi: int, ultimo_pass: float) -> dict:
    """`last_passed_at` e `last_seen_at` sono OROLOGI DI PARETE, come li scrive la
    discovery. La prima versione di questo criterio confrontava `last_pass_data_end`
    — che e' un tempo dei DATI — con `time.time()`: due orologi diversi, lo stesso
    errore che `judge_window` esiste per chiudere. Tre test lo hanno mostrato."""
    return {"symbol": sym, "generated": True, "pass_count": passi,
            "last_passed_at": ultimo_pass, "last_seen_at": ultimo_pass}


def test_a_coin_with_a_pair_halfway_is_kept():
    """Il caso ORCAUSDT: otto coppie a 2/3 e la coin fuori dalla classifica."""
    ora = time.time()
    pairs = {f"ORCAUSDT|gen_{i}": _gen("ORCAUSDT", 2, ora - 86400) for i in range(8)}
    assert coin_in_maturazione(pairs, ora)[0] == ["ORCAUSDT"]


def test_a_coin_with_no_confirmations_is_not_kept():
    """Senza nemmeno un passaggio non c'e' niente da proteggere: se la coin esce
    dall'universo, esce. Altrimenti l'universo crescerebbe per sempre e ogni giro
    costerebbe di piu' senza avvicinare una sola validazione."""
    ora = time.time()
    pairs = {"TALEUSDT|gen_a": _gen("TALEUSDT", 0, 0)}
    assert coin_in_maturazione(pairs, ora)[0] == []


def test_a_pair_that_stopped_passing_long_ago_is_let_go():
    """Se in tre finestre intere non ha ripassato, quella coppia non sta maturando.
    Tenerla attaccata all'universo per sempre e' il modo in cui un elenco di
    eccezioni diventa piu' grande della regola."""
    ora = time.time()
    pairs = {"VECCHIAUSDT|gen_a": _gen("VECCHIAUSDT", 1, ora - 40 * 86400)}
    assert coin_in_maturazione(pairs, ora)[0] == []


def test_it_does_not_depend_on_the_generated_flag():
    """Il criterio guarda le CONFERME, non il flag `generated`.

    Di proposito: `slim_registry` puo' togliere i campi non essenziali quando il
    documento cresce, e finche' `generated` non era fra quelli protetti una coppia
    alleggerita diventava indistinguibile da una base. Far dipendere da quel flag la
    sopravvivenza di una coppia significa legare settimane di attesa a un campo che
    qualcun altro puo' cancellare per far spazio.
    """
    ora = time.time()
    pairs = {"AUSDT|qualcosa": {"symbol": "AUSDT", "pass_count": 2,
                                "last_passed_at": ora, "last_seen_at": ora}}
    assert coin_in_maturazione(pairs, ora)[0] == ["AUSDT"]


def test_the_generated_flag_survives_slimming():
    """Perche' se si perde, la potatura delle base cancella la coppia, il tetto
    smette di considerarla intoccabile e la sua spec perde la priorita' nella
    ri-valutazione. Un campo, tre conseguenze, tutte silenziose."""
    from scripts.optimize import REGISTRY_CORE_FIELDS
    assert "generated" in REGISTRY_CORE_FIELDS


def test_a_coin_one_step_from_validation_is_never_capped():
    """LA CONTESTAZIONE DEL PROPRIETARIO, 17 settembre: «non avevamo detto che le
    monete, anche se scendeva il volume durante i tre passaggi, le avremmo comunque
    tenute?».

    Aveva ragione. La prima versione aveva un tetto UNICO di 40 coin ordinate per
    vicinanza al traguardo: ordinare bene fa perdere le ultime della fila, ma resta
    un tetto, e una moneta a un passo dalla validazione non deve poterci finire
    sotto. Ora quelle non hanno tetto; il tetto vale solo per la coda a una conferma.
    """
    ora = time.time()
    pairs = {f"VICINA{i}USDT|gen_{i}": _gen(f"VICINA{i}USDT", 2, ora)
             for i in range(50)}
    scelte, diag = coin_in_maturazione(pairs, ora, max_coda=5)
    assert len(scelte) == 50, "una coin a 2/3 non puo' essere tagliata da un tetto"
    assert diag["intoccabili"] == 50
    assert diag["tagliate"] == 0


def test_only_the_one_confirmation_tail_is_capped():
    """Il tetto serve ancora: le coin con UNA sola conferma sono decine, il grosso
    non arrivera' in fondo, e ogni coin in piu' e' tempo di calcolo a ogni giro.
    Si tagliano le ultime della coda — e il conteggio di quante lo dice, invece di
    lasciarlo a una promessa in docstring."""
    ora = time.time()
    pairs = {f"C{i}USDT|gen_{i}": _gen(f"C{i}USDT", 1, ora) for i in range(100)}
    scelte, diag = coin_in_maturazione(pairs, ora, max_coda=60)
    assert len(scelte) == 60
    assert diag["intoccabili"] == 0
    assert diag["coda"] == 100
    assert diag["tagliate"] == 40


def test_the_untouchable_ones_do_not_eat_the_tail_budget():
    """Se le intoccabili consumassero slot della coda, un giorno con molte coppie a
    2/3 affamerebbe proprio l'esplorazione che le rifornisce."""
    ora = time.time()
    pairs = {f"V{i}USDT|gen_v{i}": _gen(f"V{i}USDT", 2, ora) for i in range(30)}
    pairs.update({f"U{i}USDT|gen_u{i}": _gen(f"U{i}USDT", 1, ora) for i in range(70)})
    scelte, diag = coin_in_maturazione(pairs, ora, max_coda=60)
    assert diag["intoccabili"] == 30
    assert diag["coda_tenuta"] == 60
    assert len(scelte) == 90


def test_the_discovery_adds_them_after_the_context_filter():
    """La riaggiunta deve stare DOPO `ai_filter_universe`: una coin che ha gia'
    prodotto conferme ha gia' dimostrato di essere informativa, e lasciarla
    escludere rimetterebbe in piedi lo stesso buco da un'altra porta."""
    import inspect
    from scripts import discover_strategies as d

    src = inspect.getsource(d.main)
    assert src.index("ai_filter_universe") < src.index("coin_in_maturazione")
