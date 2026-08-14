"""L'AUTOPSIA DEL GATE — perche' una candidata non passa, non solo che non passa.

Il gate rispondeva si'/no. Con ventimila valutazioni per run questo significa
ripetere ventimila esperimenti senza conservarne l'esito: se non passa niente non
si sa se muoiono per pochi trade, per costi non battuti o sull'holdout. E senza
saperlo l'unica reazione possibile e' abbassare le soglie a caso.

Qui si verifica che la diagnosi sia FEDELE (stesso verdetto di prima, motivo
corretto) e UTILE (i quasi-passaggi diventano i semi del run successivo).
"""
import pytest

from bot.config import settings
from backtesting.engine import gate_verdict, passes_gate


def _good():
    return dict(window_pnls=[0.2, 0.2, 0.2], n_trades=100, pf=1.6, win_rate=0.5,
                total_return=0.5)


# ---- fedelta': il verdetto non cambia ------------------------------------- #
def test_the_verdict_matches_the_old_boolean():
    """`passes_gate` e' ora una scorciatoia di `gate_verdict`: se i due divergessero,
    l'autopsia descriverebbe un gate diverso da quello che valida davvero."""
    cases = [_good(),
             {**_good(), "n_trades": 1},
             {**_good(), "pf": 0.5},
             {**_good(), "win_rate": 0.01},
             {**_good(), "total_return": -1.0},
             {**_good(), "window_pnls": [0.3, -0.05, -0.05]}]
    for c in cases:
        assert passes_gate(**c) is gate_verdict(**c).ok


def test_a_passing_candidate_has_no_reason_to_report():
    v = gate_verdict(**_good())
    assert v.ok and v.failed == () and v.binding == ""


# ---- il motivo ------------------------------------------------------------ #
def test_it_names_the_criterion_that_failed():
    v = gate_verdict(**{**_good(), "n_trades": settings.GATE_MIN_TRADES - 1})
    assert not v.ok and "trades" in v.failed and v.binding == "trades"


def test_all_failed_criteria_are_reported_not_just_the_first():
    """Fermarsi al primo direbbe che una candidata 'muore per pochi trade' anche
    quando ne avrebbe falliti altri quattro, e la diagnosi ne uscirebbe falsata:
    si finirebbe a lavorare sul sintomo piu' superficiale."""
    v = gate_verdict(window_pnls=[0.1, -0.1, -0.1], n_trades=2, pf=0.4,
                     win_rate=0.05, total_return=-0.9)
    for c in ("trades", "pf", "win_rate", "total_return", "consistency"):
        assert c in v.failed


def test_the_binding_criterion_is_the_worst_one_not_the_first():
    """Con piu' criteri falliti quello che conta e' il piu' lontano dalla soglia:
    e' li' che sta il collo di bottiglia della ricerca."""
    # trades quasi a posto (-3%), PF lontanissimo
    v = gate_verdict(window_pnls=[0.2, 0.2, 0.2],
                     n_trades=int(settings.GATE_MIN_TRADES * 0.97),
                     pf=0.1, win_rate=0.5, total_return=0.5)
    assert v.binding == "pf"


def test_the_shortfall_says_how_far_off_it_was():
    v = gate_verdict(**{**_good(), "pf": settings.GATE_PF_THRESHOLD * 0.9})
    assert v.binding == "pf"
    assert -0.11 < v.shortfall < -0.09          # circa il 10% sotto soglia


# ---- quasi-passaggi: i semi della ricerca successiva ---------------------- #
def test_one_criterion_missed_by_little_is_a_near_miss():
    v = gate_verdict(**{**_good(), "pf": settings.GATE_PF_THRESHOLD * 0.97})
    assert v.near_miss()


def test_missing_by_a_lot_is_not_a_near_miss():
    v = gate_verdict(**{**_good(), "pf": settings.GATE_PF_THRESHOLD * 0.2})
    assert not v.near_miss()


def test_two_criteria_missed_is_never_a_near_miss():
    """Anche se entrambi di poco: due condizioni mancate insieme non sono 'quasi',
    sono una candidata che non funziona su due fronti."""
    v = gate_verdict(**{**_good(), "pf": settings.GATE_PF_THRESHOLD * 0.98,
                        "win_rate": settings.GATE_WIN_RATE_FLOOR * 0.98})
    assert len(v.failed) == 2 and not v.near_miss()


def test_a_bleeding_regime_is_never_almost_fine():
    """Il regime e' booleano: non ha una distanza dalla soglia, e inventargliene una
    lo farebbe entrare fra i quasi-passaggi. Un regime in emorragia non e' 'quasi'."""
    bleeding = {"bull_trending": {"trades": 999, "pf": 0.1}}
    v = gate_verdict(**_good(), regime_pf=bleeding)
    assert v.binding == "regime" and not v.near_miss()


# ---- l'aggregato ---------------------------------------------------------- #
def _entry(passed, binding=None, crits=(), near=False, pf=1.0):
    return {"passed": passed, "fail_binding": binding, "fail_criteria": list(crits),
            "near_miss": near, "fail_shortfall": -0.05, "oos_pf": pf, "oos_trades": 50}


def test_the_report_counts_where_candidates_die():
    from scripts.optimize import autopsy
    out = {"A|s": _entry(False, "trades", ["trades"]),
           "B|s": _entry(False, "trades", ["trades", "pf"]),
           "C|s": _entry(False, "pf", ["pf"]),
           "D|s": _entry(True)}
    rep = autopsy(out)
    assert rep["evaluated"] == 4 and rep["passed"] == 1 and rep["diagnosed"] == 3
    assert rep["binding"] == {"trades": 2, "pf": 1}
    assert rep["involved"]["pf"] == 2        # coinvolto due volte, binding una sola


def test_a_pass_without_a_diagnosis_is_not_invented():
    """Una bocciatura senza criteri registrati (codice vecchio, dato monco) non deve
    entrare nei conteggi: un istogramma che si inventa le voci mancanti e' peggio
    di un istogramma incompleto, perche' non si vede che manca qualcosa."""
    from scripts.optimize import autopsy
    rep = autopsy({"A|s": {"passed": False}})
    assert rep["diagnosed"] == 0 and rep["binding"] == {}


def test_near_misses_come_out_sorted_by_how_close_they_were():
    from scripts.optimize import autopsy
    out = {"A|s": {**_entry(False, "pf", ["pf"], near=True), "fail_shortfall": -0.09},
           "B|s": {**_entry(False, "pf", ["pf"], near=True), "fail_shortfall": -0.01}}
    rep = autopsy(out)
    assert [n["key"] for n in rep["near_misses"]] == ["B|s", "A|s"]


# ---- l'anello si chiude: i quasi-passaggi tornano come semi --------------- #
class _FakeFb:
    def __init__(self, docs):
        self.docs = docs

    def get_doc(self, coll, doc_id):
        return self.docs.get(f"{coll}/{doc_id}")


def test_near_misses_become_the_next_run_mutation_seeds():
    from scripts.discover_strategies import mutation_seeds
    fb = _FakeFb({"gate_autopsy/discover": {
        "near_misses": [{"key": "BTCUSDT|gen_aaa"}, {"key": "ETHUSDT|gen_bbb"}]}})
    existing = {"gen_aaa": {"id": "gen_aaa"}, "gen_bbb": {"id": "gen_bbb"},
                "gen_ccc": {"id": "gen_ccc"}}
    assert mutation_seeds(fb, existing) == [{"id": "gen_aaa"}, {"id": "gen_bbb"}]


def test_base_strategies_are_not_mutable_seeds():
    """L'autopsia dell'optimizer parla di strategie BASE, che non sono spec: se
    finissero fra i semi il chiamante muterebbe None."""
    from scripts.discover_strategies import mutation_seeds
    fb = _FakeFb({"gate_autopsy/current": {
        "near_misses": [{"key": "BTCUSDT|breakout"}]}})
    assert mutation_seeds(fb, {"gen_aaa": {"id": "gen_aaa"}}) == []


def test_no_autopsy_means_the_old_behaviour():
    """Fail-open: senza diagnosi la discovery torna a mutare le prime spec, come
    faceva prima. Una novita' che rompe il giro precedente quando manca un dato
    sarebbe un peggioramento travestito."""
    from scripts.discover_strategies import mutation_seeds
    assert mutation_seeds(_FakeFb({}), {"gen_aaa": {"id": "gen_aaa"}}) == []


def test_an_unreadable_autopsy_does_not_stop_discovery():
    from scripts.discover_strategies import mutation_seeds

    class _Broken:
        def get_doc(self, *a):
            raise ConnectionError("firebase giu'")

    assert mutation_seeds(_Broken(), {"gen_aaa": {"id": "gen_aaa"}}) == []


# =========================================================================== #
# t-stat: "e' fortuna?" misurato senza assumere una frazione                  #
# =========================================================================== #
# `pf_without_top` boccia chi non pareggia togliendo il 5% di trade migliori. Ma
# confonde due cose: profitto concentrato per FORTUNA (poche vincite casuali) e
# profitto concentrato perche' il MECCANISMO e' quello — lo scale-out con l'ultimo
# gradino a 5R fa arrivare il guadagno dalla coda per costruzione. Il t-stat separa
# i due casi attraverso la dispersione, ed e' deterministico e O(n): calcolabile su
# tutte le ventimila valutazioni di ogni run, cosa che un bootstrap non sarebbe.

class _T:
    def __init__(self, pnl):
        self.pnl_pct = pnl


def test_a_steady_edge_scores_high():
    from backtesting.engine import t_stat
    trades = [_T(0.01)] * 50 + [_T(-0.005)] * 50      # piccolo ma regolare
    assert t_stat(trades) > 3


def test_one_lucky_trade_carrying_everything_scores_low():
    """Il caso che il gate vuole escludere: un colpo enorme e cento perdite. Il PF
    puo' essere ottimo, ma il rendimento medio non si distingue dallo zero."""
    from backtesting.engine import t_stat
    trades = [_T(5.0)] + [_T(-0.04)] * 100
    assert abs(t_stat(trades)) < 2


def test_a_designed_tail_is_not_punished_like_luck():
    """Coda REGOLARE (un vincitore grosso ogni cinque, come da scale-out) contro
    coda casuale con lo stesso profitto totale: la prima deve segnare piu' alto."""
    from backtesting.engine import t_stat
    disegnata = ([_T(0.30)] + [_T(-0.05)] * 4) * 20
    fortunata = [_T(6.0)] + [_T(-0.05)] * 99
    assert t_stat(disegnata) > t_stat(fortunata)


def test_a_losing_strategy_scores_negative():
    from backtesting.engine import t_stat
    assert t_stat([_T(-0.02)] * 30 + [_T(0.01)] * 10) < 0


def test_it_is_deterministic():
    """Un criterio che cambia verdetto fra due run identici renderebbe il gate non
    riproducibile — ed e' il motivo per cui qui NON si usa un bootstrap."""
    from backtesting.engine import t_stat
    trades = [_T(0.03), _T(-0.01), _T(0.05), _T(-0.02)]
    assert t_stat(trades) == t_stat(trades)


def test_too_few_trades_give_no_verdict():
    from backtesting.engine import t_stat
    assert t_stat([]) == 0.0
    assert t_stat([_T(0.5)]) == 0.0


def test_it_does_not_touch_the_gate_verdict():
    """E' MISURATO, non collegato: il gate deve dare lo stesso verdetto di prima.
    E' la stessa disciplina usata per la calibrazione e per l'ombra dell'LLM —
    prima si misura, poi semmai si collega."""
    import inspect
    from backtesting.engine import gate_verdict
    assert "t_stat" not in inspect.getsource(gate_verdict)


# =========================================================================== #
# LA SOGLIA DEL t-STAT DIPENDE DA QUANTI TEST SI FANNO                        #
# =========================================================================== #
# Il 2 canonico vale per UN esperimento. Qui se ne fanno oltre ventimila per run:
# a t=2 ci si aspettano CENTINAIA di candidate che passano per puro caso. Leggere
# "8 su 14 superano t=2" come prova che il gate boccia edge veri sarebbe scambiare
# la lotteria per un edge — l'errore che tutto il sistema esiste per non fare.

def test_more_tests_demand_a_higher_bar():
    from scripts.gate_autopsy import required_t
    assert required_t(22_500) > required_t(1_000) > required_t(20)


def test_the_bar_at_our_scale_is_about_four_not_two():
    """Con ~22mila valutazioni per run la soglia onesta e' vicina a 4."""
    from scripts.gate_autopsy import required_t
    assert 3.8 < required_t(22_500) < 4.2


def test_a_stricter_budget_raises_the_bar():
    from scripts.gate_autopsy import required_t
    assert required_t(22_500, budget=0.1) > required_t(22_500, budget=1.0)


def test_the_bar_lets_through_about_one_lucky_candidate():
    """E' la definizione stessa della soglia: si sceglie il valore che, per puro
    caso, ne lascerebbe passare al massimo una."""
    from scripts.gate_autopsy import expected_by_chance, required_t
    n = 22_500
    assert expected_by_chance(required_t(n), n) == pytest.approx(1.0, rel=0.05)


def test_the_canonical_two_would_let_through_hundreds():
    from scripts.gate_autopsy import expected_by_chance
    assert expected_by_chance(2.0, 22_500) > 300


def test_a_single_test_falls_back_to_something_sane():
    from scripts.gate_autopsy import required_t
    assert required_t(0) == 2.0 and required_t(1) == 2.0
