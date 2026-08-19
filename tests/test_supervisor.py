"""IL SUPERVISORE — puo' allentare i criteri da solo, ma solo dentro un vincolo.

La domanda che questi test devono chiudere non e' "funziona", e' "puo' fare danni?".
Un sistema che taratura i propri criteri di validazione, se sbagliato, non da'
errore: promuove strategie che sembrano valide e non lo sono, e il conto arriva in
paper o coi soldi veri.

Quindi si verifica soprattutto cio' che NON deve succedere: mai sotto i pavimenti,
mai un allentamento quando il budget di falsi positivi e' esaurito, mai un
allentamento quando le candidate muoiono sull'holdout (li' allentare promuoverebbe
proprio le sovradattate), mai due parametri insieme, mai nulla durante il paper.
"""
import pytest

from bot.learning.supervisor import (NEVER, TUNABLES, Context, decide,
                                     effective_confirmations, expected_lucky,
                                     headroom, max_pass_rate)


def _ctx(**kw) -> Context:
    base = dict(ready=False, validated=0, days_stagnant=10.0,
                evaluated=20000, passed=8, binding={"pf": 900, "trades": 100},
                near={"pf": [-0.02, -0.03]},
                current={t.name: v for t, v in [
                    (TUNABLES["trades"], 30.0), (TUNABLES["pf"], 1.25),
                    (TUNABLES["win_rate"], 0.45), (TUNABLES["total_return"], 0.15),
                    (TUNABLES["consistency"], 1.0), (TUNABLES["recovery"], 2.0),
                    (TUNABLES["regime"], 0.8), (TUNABLES["pf_ex_top"], 1.0)]},
                min_passes=3, window_days=7.0, budget=1.0, independence=0.5)
    base.update(kw)
    return Context(**base)


# ---- il vincolo: quanta fortuna ci si aspetta ----------------------------- #
def test_confirmations_are_not_independent_tests():
    """Finestre a pochi giorni di distanza vedono quasi gli stessi dati: contarle
    come test indipendenti gonfierebbe la fiducia proprio dove serve prudenza."""
    assert effective_confirmations(3, 0.5) == 2.0      # non 3
    assert effective_confirmations(1, 0.5) == 1.0
    assert effective_confirmations(3, 1.0) == 3.0      # indipendenza piena, se scelta


def test_more_draws_mean_more_luck():
    a = expected_lucky(1_000, 0.01, 3)
    b = expected_lucky(100_000, 0.01, 3)
    assert b > a


def test_more_confirmations_mean_less_luck():
    assert expected_lucky(20_000, 0.01, 5) < expected_lucky(20_000, 0.01, 3)


def test_a_gate_that_passes_nothing_expects_no_luck():
    assert expected_lucky(20_000, 0.0, 3) == 0.0


def test_the_ceiling_on_the_pass_rate_is_computable():
    """E' la licenza quantitativa: dice di quanto si puo' allentare, invece di
    lasciarlo al sentimento."""
    top = max_pass_rate(20_000, 3, budget=1.0, window_days=7.0)
    assert 0 < top < 1
    # al tetto, le attese coincidono col budget
    assert expected_lucky(20_000, top, 3, window_days=7.0) == pytest.approx(1.0, rel=0.02)


def test_todays_numbers_leave_room():
    """22k valutazioni con 8 passate: il gate e' molto piu' severo di quanto il
    budget richieda. E' questo che autorizza ad allentare — non l'impazienza."""
    assert headroom(22_264, 8 / 22_264, 3, budget=1.0, window_days=7.0) > 1.0


# ---- quando NON si tocca niente ------------------------------------------ #
def test_nothing_is_tuned_while_the_paper_is_running():
    """Cambiare le regole a partita in corso renderebbe non interpretabile il
    confronto fra cio' che il gate ha promesso e cio' che il paper vive."""
    d = decide(_ctx(ready=True))
    assert [x.kind for x in d] == ["none"]


def test_it_waits_before_reacting_to_a_quiet_day():
    d = decide(_ctx(days_stagnant=0.5, stagnant_after_days=2.0))
    assert d[0].kind == "none" and "aspetta" in d[0].reason


def test_without_a_diagnosis_nothing_is_touched():
    """Tarare senza sapere dove si muore e' esattamente il comportamento che questo
    modulo esiste per sostituire."""
    d = decide(_ctx(binding={}))
    assert d[0].kind == "none" and "buio" in d[0].reason


def test_an_exhausted_budget_forbids_any_relaxation():
    """Con il budget sforato allentare comprerebbe candidate fortunate. Si riducono
    le estrazioni, che e' l'altro modo di rientrare."""
    d = decide(_ctx(evaluated=200_000, passed=40_000))     # tasso enorme
    assert d[0].kind == "tighten" and "SFORATO" in d[0].reason
    assert not any(x.kind == "set_param" for x in d)


def test_dying_on_the_holdout_never_relaxes_anything():
    """E' il caso piu' pericoloso: le candidate superano tutto e cadono sui dati mai
    visti. Allentare promuoverebbe proprio le sovradattate."""
    d = decide(_ctx(binding={"holdout": 500, "pf": 10}, near={"holdout": [0.0, 0.0]}))
    assert d[0].kind == "tighten" and "sovradattamento" in d[0].reason
    assert not any(x.kind == "set_param" for x in d)


def test_a_parameter_at_its_floor_is_not_pushed_further():
    """pf_ex_top parte gia' al pavimento: sotto il pareggio senza i colpi migliori si
    validerebbe la fortuna, e non c'e' budget che lo giustifichi."""
    d = decide(_ctx(binding={"pf_ex_top": 900}, near={"pf_ex_top": [-0.01]}))
    assert d[0].kind == "none" and "pavimento" in d[0].reason


def test_the_floor_is_never_crossed_even_after_many_moves():
    """Il controllo che conta davvero: iterando le decisioni, nessun parametro puo'
    finire sotto il proprio pavimento."""
    cur = {TUNABLES["pf"].name: 1.25}
    for _ in range(50):
        d = decide(_ctx(binding={"pf": 900}, near={"pf": [-0.9]},
                        current={**_ctx().current, **cur}))
        sets = [x for x in d if x.kind == "set_param"]
        if not sets:
            break
        cur[TUNABLES["pf"].name] = sets[0].new
    assert cur[TUNABLES["pf"].name] >= TUNABLES["pf"].floor


# ---- quando si tocca, si tocca poco e si dice perche' -------------------- #
def test_it_relaxes_the_criterion_that_stops_the_most():
    d = decide(_ctx(binding={"trades": 5000, "pf": 100},
                    near={"trades": [-0.05, -0.06]}))
    s = [x for x in d if x.kind == "set_param"]
    assert s and s[0].param == "GATE_MIN_TRADES"
    assert s[0].new < s[0].old


def test_only_one_parameter_moves_at_a_time():
    """Due modifiche insieme rendono impossibile sapere quale ha prodotto l'effetto
    misurato al run successivo: si perde proprio il segnale di ritorno."""
    d = decide(_ctx(binding={"trades": 5000, "pf": 4000, "win_rate": 3000},
                    near={"trades": [-0.05, -0.06], "pf": [-0.02],
                          "win_rate": [-0.03]}))
    assert len([x for x in d if x.kind == "set_param"]) == 1


def test_an_integer_parameter_always_moves_by_at_least_one():
    """Con l'arrotondamento un passo del 15% su un intero piccolo poteva non
    muovere nulla, e il supervisore avrebbe 'deciso' a vuoto per sempre."""
    d = decide(_ctx(binding={"trades": 900}, near={"trades": [-0.02]},
                    current={**_ctx().current, TUNABLES["trades"].name: 21.0}))
    s = [x for x in d if x.kind == "set_param"]
    assert s and s[0].new < 21.0


def test_every_decision_carries_the_numbers_that_justify_it():
    """Fra due mesi la domanda sara' 'perche' questa soglia sta qui?'. La risposta
    deve stare nella decisione, non nella memoria di qualcuno."""
    d = decide(_ctx(binding={"pf": 900}, near={"pf": [-0.02]}))
    s = [x for x in d if x.kind == "set_param"][0]
    assert "pass_rate" in s.detail and "expected_lucky_per_day" in s.detail
    assert "budget" in s.reason or "spazio" in s.reason


# ---- misurare subito: fast_gate ------------------------------------------ #
def test_a_change_is_measured_in_hours_not_in_weeks():
    """Un parametro cambiato che aspetta tre settimane per essere giudicato non e'
    un anello chiuso, e' una scommessa."""
    d = decide(_ctx(days_stagnant=10.0, days_since_fast_gate=999.0,
                    fast_gate_after_days=5.0))     # armato esplicitamente
    assert any(x.kind == "fast_gate" for x in d)


def test_fast_gate_respects_its_cooldown():
    """E' distruttivo (azzera il registro): ripeterlo ogni giorno cancellerebbe di
    continuo i pass veri accumulati nel frattempo."""
    d = decide(_ctx(days_stagnant=10.0, days_since_fast_gate=1.0,
                    fast_gate_after_days=5.0, fast_gate_cooldown_days=7.0))
    assert not any(x.kind == "fast_gate" for x in d)


def test_fast_gate_is_not_run_when_something_has_been_validated():
    d = decide(_ctx(validated=3, days_stagnant=10.0, fast_gate_after_days=5.0))
    assert not any(x.kind == "fast_gate" for x in d)


# ---- la lista dei divieti ------------------------------------------------- #
def test_the_untouchables_are_never_proposed():
    """L'holdout, i dati sintetici, la parita' col backtest, DRY_RUN e il numero di
    conferme non sono parametri di ricerca."""
    proposed = {t.name for t in TUNABLES.values()}
    assert proposed.isdisjoint(NEVER)
    for k in ("GATE_HOLDOUT_DAYS", "BACKTEST_ALLOW_SYNTHETIC", "DRY_RUN",
              "OPTIMIZER_MIN_PASSES", "OPTIMIZER_NEW_DATA_MIN_HOURS"):
        assert k in NEVER


def test_every_floor_states_why_it_exists():
    """Un pavimento senza motivo scritto e' un numero che qualcuno abbassera'."""
    for t in TUNABLES.values():
        assert t.why_floor, f"{t.name} non dice perche' il pavimento sta li'"


# ---- lo stato fra un giro e l'altro --------------------------------------- #
class _Fb:
    def __init__(self, docs):
        self.docs = docs

    def get_doc(self, coll, doc_id):
        return self.docs.get(f"{coll}/{doc_id}")

    def set_doc(self, coll, doc_id, data):
        self.docs[f"{coll}/{doc_id}"] = data


def test_an_unknown_previous_count_does_not_reset_the_clock():
    """Regressione. Il conteggio si azzera solo se le validate sono DAVVERO
    cresciute: un valore precedente assente significa 'non lo so ancora', e
    trattarlo come un aumento azzerava la stagnazione a ogni giro — il supervisore
    non sarebbe mai arrivato a decidere niente."""
    import time
    from bot.core.firebase_client import encode_pairs
    from scripts.supervisor import build_context
    fb = _Fb({"strategy_registry/validated": {"pairs": encode_pairs({}), "ready": False}})
    ctx = build_context(fb, {"validated_since": time.time() - 9 * 86400})
    assert ctx.days_stagnant > 8


def test_the_clock_restarts_when_something_gets_validated():
    import time
    from bot.core.firebase_client import encode_pairs
    from scripts.supervisor import build_context
    pairs = {"BTCUSDT|x": {"pass_count": 3, "symbol": "BTCUSDT"}}
    fb = _Fb({"strategy_registry/validated": {"pairs": encode_pairs(pairs)}})
    ctx = build_context(fb, {"validated_since": time.time() - 9 * 86400,
                             "last_validated": 0})
    assert ctx.validated == 1 and ctx.days_stagnant < 0.1


def test_both_autopsies_are_summed():
    """La discovery porta il grosso del volume, l'optimizer le strategie base: per
    sapere dove si muore contano insieme."""
    from bot.core.firebase_client import encode_pairs
    from scripts.supervisor import build_context
    fb = _Fb({"strategy_registry/validated": {"pairs": encode_pairs({})},
              "gate_autopsy/current": {"evaluated": 1000, "passed": 1,
                                       "binding": {"pf": 10}},
              "gate_autopsy/discover": {"evaluated": 20000, "passed": 7,
                                        "binding": {"pf": 5, "trades": 90}}})
    ctx = build_context(fb, {"validated_since": 1.0, "last_validated": 0})
    assert ctx.evaluated == 21000 and ctx.passed == 8
    assert ctx.binding == {"pf": 15, "trades": 90}


def test_the_tuning_file_round_trips(tmp_path, monkeypatch):
    import scripts.supervisor as sup
    monkeypatch.setattr(sup, "TUNING_FILE", str(tmp_path / "tuning.env"))
    sup.write_tuning({"GATE_MIN_TRADES": "25", "GATE_PF_THRESHOLD": "1.19"})
    assert sup.read_tuning() == {"GATE_MIN_TRADES": "25", "GATE_PF_THRESHOLD": "1.19"}


def test_the_tuning_file_says_it_is_machine_written(tmp_path, monkeypatch):
    """Chi lo apre a mano deve capire subito che le sue modifiche verranno
    sovrascritte, e come tornare ai default."""
    import scripts.supervisor as sup
    monkeypatch.setattr(sup, "TUNING_FILE", str(tmp_path / "tuning.env"))
    sup.write_tuning({"GATE_MIN_TRADES": "25"})
    text = (tmp_path / "tuning.env").read_text()
    assert "NON modificare a mano" in text and "cancella" in text


# =========================================================================== #
# LA LEZIONE DEI PRIMI DATI VERI                                              #
# =========================================================================== #
# Prima autopsia reale: 21.948 valutazioni, 8 passate. Il 78% moriva su
# `total_return` — ma quelle stesse candidate fallivano anche pf (96%), pf_ex_top
# (98%), win_rate (94%), recovery (88%), consistency (88%). Sei criteri insieme.
# Allentare `total_return`, il criterio "dominante", non ne avrebbe convertita
# NESSUNA: quando quasi tutto fallisce quasi tutto, il conteggio delle bocciature
# descrive la qualita' media delle candidate, non un collo di bottiglia.

def test_the_lever_is_not_the_most_frequent_failure():
    """Il caso reale: `total_return` ferma la maggioranza, ma nessuna di quelle
    candidate e' vicina a passare. La leva deve andare dove ci sono i
    quasi-passaggi, altrimenti si spende una mossa di budget per zero conversioni."""
    d = decide(_ctx(binding={"total_return": 15747, "recovery": 1338, "trades": 2019},
                    near={"trades": [-0.03, -0.03, -0.06]}))
    s = [x for x in d if x.kind == "set_param"]
    assert s and s[0].param == TUNABLES["trades"].name


def test_no_near_misses_means_no_move_at_all():
    """Se nessuna candidata e' fermata da un solo criterio, non esiste una soglia
    che ne sbloccherebbe qualcuna: allentare sarebbe una mossa al buio."""
    d = decide(_ctx(binding={"total_return": 15747}, near={}))
    assert d[0].kind == "none" and "sono le candidate" in d[0].reason


def test_the_criterion_with_most_near_misses_wins():
    d = decide(_ctx(binding={"total_return": 999},
                    near={"trades": [-0.05], "recovery": [-0.02, -0.03, -0.04]}))
    s = [x for x in d if x.kind == "set_param"]
    assert s and s[0].param == TUNABLES["recovery"].name


def test_the_step_is_sized_on_the_gap_not_on_the_maximum():
    """Allentare piu' del necessario regala passaggi a candidate che non erano
    vicine: e' il modo in cui una taratura ragionevole diventa una svendita."""
    d = decide(_ctx(binding={"recovery": 9},
                    near={"recovery": [-0.02, -0.02, -0.03]}))
    s = [x for x in d if x.kind == "set_param"][0]
    mossa = (s.old - s.new) / s.old
    assert 0.02 <= mossa <= 0.05          # copre la mediana, non il passo massimo


def test_the_move_predicts_how_many_it_should_unblock():
    """Una decisione che non dice cosa dovrebbe succedere non e' verificabile al
    giro dopo, ed e' allora che una taratura sbagliata resta in piedi per mesi."""
    d = decide(_ctx(binding={"recovery": 9},
                    near={"recovery": [-0.02, -0.02, -0.03]}))
    s = [x for x in d if x.kind == "set_param"][0]
    assert s.detail["expected_conversions"] >= 2
    assert "sbloccare" in s.reason


def test_near_misses_stuck_on_the_anti_luck_test_stop_everything():
    """Il caso vero e piu' importante: le candidate piu' vicine al passaggio sono
    ferme su pf_ex_top, che sta gia' al pavimento (pareggio senza i colpi migliori).
    Scendere sotto significherebbe validare strategie che PERDONO senza le loro
    poche corse fortunate. Il supervisore deve fermarsi e dirlo."""
    d = decide(_ctx(binding={"total_return": 15747},
                    near={"pf_ex_top": [-0.006, -0.007, -0.024, -0.043]}))
    assert d[0].kind == "none"
    assert "pavimento" in d[0].reason
    assert not any(x.kind == "set_param" for x in d)


def test_near_misses_on_the_holdout_trigger_tightening():
    """Quattro coppie base con PF fra 1.4 e 4.7 sulle finestre, tutte morte
    sull'holdout: e' la firma del sovradattamento, e la reazione e' opposta
    all'allentamento."""
    d = decide(_ctx(binding={"total_return": 1248},
                    near={"holdout": [0.0, 0.0, 0.0, 0.0]}))
    assert d[0].kind == "tighten" and "sovradattamento" in d[0].reason


# ---- fast_gate: disarmato per default ------------------------------------ #
def test_fast_gate_is_disarmed_by_default():
    """E' l'unica azione IRREVERSIBILE che il supervisore puo' decidere da solo:
    azzera il registro, cioe' le conferme che costano una settimana l'una, il
    backup resta sul disco della macchina fuori da git e non esiste nessuno script
    che lo ripristini. Un'azione che non si puo' ne' osservare ne' annullare da
    lontano non deve partire da sola."""
    d = decide(_ctx(days_stagnant=30.0, validated=0, days_since_fast_gate=999.0,
                    fast_gate_after_days=0.0))
    assert not any(x.kind == "fast_gate" for x in d)


def test_fast_gate_still_fires_when_explicitly_armed():
    """Disarmato non vuol dire rimosso: chi guarda puo' armarlo."""
    d = decide(_ctx(days_stagnant=30.0, validated=0, days_since_fast_gate=999.0,
                    fast_gate_after_days=5.0))
    assert any(x.kind == "fast_gate" for x in d)


def test_the_dataclass_default_is_disarmed_too():
    """Il default del codice e quello dell'env devono dire la stessa cosa: se
    divergessero, il comportamento dipenderebbe da quale percorso costruisce il
    contesto."""
    assert Context().fast_gate_after_days == 0.0


# ---- disfare la propria mossa prima di accusare il mondo ----------------- #
def test_an_exceeded_budget_undoes_its_own_tuning_first():
    """Il caso reale del 17 agosto: win_rate allentato, budget a 1.64 contro un
    tetto di 1. Il sistema restava li' a ripetere 'non allento piu'' senza mai
    disfare cio' che aveva gia' fatto — una posizione insostenibile mantenuta
    all'infinito. L'ipotesi piu' semplice, quando il conto non torna dopo una
    propria modifica, e' che quella modifica fosse eccessiva."""
    d = decide(_ctx(evaluated=200_000, passed=40_000,
                    tuned={"GATE_WIN_RATE_FLOOR": "0.398537"}))
    assert d[0].kind == "revert"
    assert d[0].detail["reverted"] == ["GATE_WIN_RATE_FLOOR"]
    assert not any(x.kind == "set_param" for x in d)


def test_without_its_own_changes_it_blames_the_search():
    """Se non c'e' niente da disfare, il tasso alto viene dalla ricerca e non da una
    soglia: l'altro modo di rientrare e' ridurre le estrazioni."""
    d = decide(_ctx(evaluated=200_000, passed=40_000, tuned={}))
    assert d[0].kind == "tighten" and "ricerca" in d[0].reason


def test_the_revert_names_everything_it_undoes():
    """Fra due mesi deve restare scritto cosa e' stato disfatto e perche'."""
    d = decide(_ctx(evaluated=200_000, passed=40_000,
                    tuned={"GATE_PF_THRESHOLD": "1.2", "GATE_MIN_TRADES": "25"}))
    assert set(d[0].detail["reverted"]) == {"GATE_PF_THRESHOLD", "GATE_MIN_TRADES"}
    assert "GATE_MIN_TRADES" in d[0].reason


def test_tuning_does_not_block_a_healthy_budget():
    """Avere modifiche in corso non deve impedire di continuare a tarare quando il
    budget e' ampio: il revert e' una reazione allo sforamento, non alla presenza
    di una taratura."""
    d = decide(_ctx(tuned={"GATE_WIN_RATE_FLOOR": "0.4"}, binding={"pf": 900},
                    near={"pf": [-0.02]}))
    assert any(x.kind == "set_param" for x in d)


# ---- l'unita' di occasione e' la FINESTRA, non il run -------------------- #
def test_more_runs_per_day_no_longer_inflate_the_risk():
    """Il difetto misurato il 19 agosto: il budget moltiplicava per le passate
    giornaliere, ma da quando il registro giudica per finestra una coppia guadagna
    al massimo UNA conferma a settimana. Il vecchio modello sovrastimava di 56
    volte, e il supervisore ripeteva 'budget sforato' per un allarme che era il suo
    stesso modello a fabbricare."""
    lucky = expected_lucky(26_000, 0.00227, 3, window_days=7.0)
    assert lucky < 0.05, f"atteso ben sotto il tetto, ottenuto {lucky}"


def test_a_shorter_window_means_more_opportunities():
    """Se le conferme arrivassero ogni giorno invece che ogni settimana, il rischio
    di validare fortuna crescerebbe davvero — ed e' l'unico modo in cui deve
    crescere."""
    assert (expected_lucky(26_000, 0.002, 3, window_days=1.0)
            > expected_lucky(26_000, 0.002, 3, window_days=7.0))


def test_a_zero_window_is_not_an_infinite_risk():
    """Una configurazione assurda non deve produrre una divisione per zero ne' un
    allarme infinito: si risponde zero e non si decide niente su quel numero."""
    assert expected_lucky(26_000, 0.002, 3, window_days=0.0) == 0.0
    assert max_pass_rate(26_000, 3, window_days=0.0) == 0.0
