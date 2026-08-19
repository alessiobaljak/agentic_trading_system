"""UN VERDETTO PER FINESTRA — il difetto che rendeva la validazione impossibile.

Due regole giuste prese singolarmente, su orologi incompatibili: un pass contava
solo dopo una settimana di dati nuovi, ma il purge scattava dopo due bocciature
CONSECUTIVE, contate a ogni run. Col timer ogni tre ore, fra una conferma e la
successiva passano 56 run: per sopravvivere una coppia avrebbe dovuto passare il
gate ~28 volte in sette giorni, con un tasso di passaggio misurato dello 0.027%.

Nessuna ce la faceva. Il registro non poteva accumulare tre conferme PER
COSTRUZIONE — e infatti in tre settimane le validate sono sempre state zero, con la
popolazione a 1 pass che si rinnovava completamente ogni pochi giorni invece di
crescere. Il difetto non era in una soglia: era nell'incompatibilita' fra due
contatori.

Il test che conta e' `test_a_pair_survives_the_gap_between_confirmations`: riproduce
i 56 run reali e verifica che ora si arrivi in fondo.
"""
from scripts.optimize import judge_window

SETTIMANA = 168 * 3600.0
T0 = 1_700_000_000.0


def _run(rec, giorni, passed):
    """Un run dell'optimizer con dati che finiscono a `giorni` da T0."""
    return judge_window(rec, T0 + giorni * 86400.0, passed, SETTIMANA)


# ---- il primo avvistamento ------------------------------------------------ #
def test_the_first_pass_counts_immediately():
    """Far aspettare una settimana per il PRIMO pass ritarderebbe tutto senza
    aggiungere evidenza: non c'e' nessuna conferma precedente da cui distanziarsi."""
    rec = {}
    _run(rec, 0, True)
    assert rec["pass_count"] == 1


def test_a_first_sighting_that_fails_opens_the_window_without_a_verdict():
    """Non e' un fallimento: e' l'inizio del periodo di osservazione."""
    rec = {}
    _run(rec, 0, False)
    assert rec.get("fail_count", 0) == 0 and rec["window_start"] > 0


# ---- dentro la finestra non succede niente -------------------------------- #
def test_failures_inside_the_window_do_not_count():
    """E' IL DIFETTO CORRETTO. Rivalutare gli stessi dati tre ore dopo non e' una
    prova nuova: contarla come fallimento cancellava la coppia molto prima che la
    conferma successiva potesse arrivare."""
    rec = {}
    _run(rec, 0, True)
    for ora in range(1, 50):                 # ~6 giorni di run ogni 3h
        _run(rec, ora * 0.125, False)
    assert rec["fail_count"] == 0
    assert rec["pass_count"] == 1


def test_passing_again_inside_the_window_does_not_add_a_confirmation():
    """La simmetria conta: se le bocciature interne non pesano, nemmeno i passaggi
    interni devono. Altrimenti tre pass in un giorno varrebbero una settimana."""
    rec = {}
    _run(rec, 0, True)
    for ora in range(1, 20):
        _run(rec, ora * 0.125, True)
    assert rec["pass_count"] == 1


# ---- il verdetto arriva a fine finestra ----------------------------------- #
def test_passing_at_least_once_in_the_window_earns_a_confirmation():
    rec = {}
    _run(rec, 0, True)
    _run(rec, 3, True)                       # dentro la finestra: memorizzato
    for g in (4, 5, 6):
        _run(rec, g, False)
    _run(rec, 7.1, False)                    # finestra chiusa: vale il pass visto
    assert rec["pass_count"] == 2


def test_never_passing_in_the_window_is_one_failure():
    rec = {}
    _run(rec, 0, True)
    for g in (1, 2, 3, 4, 5, 6):
        _run(rec, g, False)
    _run(rec, 7.1, False)
    assert rec["fail_count"] == 1 and rec["pass_count"] == 1


def test_a_failed_window_does_not_keep_failing_every_run():
    """Se la finestra non ripartisse dopo un verdetto, il run successivo
    aggiungerebbe subito il secondo fallimento e si tornerebbe al difetto di prima."""
    rec = {}
    _run(rec, 0, True)
    _run(rec, 7.1, False)                    # primo fallimento
    for ora in range(1, 30):
        _run(rec, 7.1 + ora * 0.125, False)
    assert rec["fail_count"] == 1


def test_two_empty_windows_are_two_failures():
    """Il purge deve restare possibile: una coppia che non passa piu' per due
    settimane intere esce dal registro, ed e' corretto."""
    rec = {}
    _run(rec, 0, True)
    _run(rec, 7.1, False)
    _run(rec, 14.2, False)
    assert rec["fail_count"] == 2


def test_a_confirmation_resets_the_failures():
    rec = {}
    _run(rec, 0, True)
    _run(rec, 7.1, False)                    # 1 fallimento
    _run(rec, 14.2, True)                    # ripassa: azzerati
    assert rec["fail_count"] == 0 and rec["pass_count"] == 2


# ---- IL TEST CHE CONTA ---------------------------------------------------- #
def test_a_pair_survives_the_gap_between_confirmations():
    """La riproduzione del caso reale: timer ogni 3 ore, una coppia che passa di
    rado. Con la contabilita' per run veniva purgata dopo 6 ore; ora arriva a tre
    conferme in tre settimane, che e' esattamente cio' che il criterio chiede."""
    rec = {}
    _run(rec, 0, True)                       # scoperta e prima conferma
    ora = 0.0
    for settimana in range(1, 3):
        # 56 run in sette giorni, con UN solo passaggio nel mezzo
        for i in range(56):
            ora += 0.125
            passa = (i == 30)
            _run(rec, ora, passa)
        _run(rec, settimana * 7 + 0.2, False)   # chiusura finestra
    assert rec["pass_count"] == 3, f"pass={rec['pass_count']} fail={rec.get('fail_count')}"
    assert rec.get("fail_count", 0) == 0


# ---- fail-closed ---------------------------------------------------------- #
def test_without_a_data_end_nothing_is_judged():
    """Nessun percorso deve poter incrementare un contatore 'gratis' dimenticando
    un campo."""
    rec = {"pass_count": 1, "window_start": T0}
    judge_window(rec, 0.0, True, SETTIMANA)
    assert rec["pass_count"] == 1 and rec.get("fail_count", 0) == 0


def test_the_window_fields_survive_the_registry_slimming():
    """Se l'alleggerimento del documento li togliesse, la finestra ripartirebbe da
    capo a ogni run e i verdetti non arriverebbero mai."""
    from scripts.optimize import REGISTRY_CORE_FIELDS
    assert {"window_start", "passed_in_window"} <= REGISTRY_CORE_FIELDS


# ---- la migrazione: la conferma regalata che stava rientrando ------------ #
def test_a_pre_existing_pair_does_not_get_a_free_confirmation():
    """Il caso della migrazione, trovato il 19 agosto. Una coppia che aveva gia' un
    passaggio ma non la finestra (perche' esisteva PRIMA che la regola entrasse in
    vigore) veniva trattata come un primo avvistamento: passando in quel momento si
    prendeva la seconda conferma senza un solo dato nuovo. E' esattamente il difetto
    che la finestra esiste per impedire, rientrato dalla porta della migrazione."""
    rec = {"pass_count": 1, "last_pass_data_end": T0}
    _run(rec, 0, True)
    assert rec["pass_count"] == 1, "nessuna conferma regalata"
    assert rec["window_start"] > 0, "ma la finestra si apre e il conto parte"


def test_a_pre_existing_pair_confirms_after_a_full_window():
    """Aspetta come tutte le altre, e poi la conferma arriva."""
    rec = {"pass_count": 1, "last_pass_data_end": T0}
    _run(rec, 0, False)
    _run(rec, 3, True)
    _run(rec, 7.1, False)
    assert rec["pass_count"] == 2


def test_a_genuinely_new_pair_still_confirms_immediately():
    """La distinzione e' fra 'mai vista' e 'gia' vista prima della regola': senza
    zero passaggi non e' un primo avvistamento."""
    rec = {}
    _run(rec, 0, True)
    assert rec["pass_count"] == 1
