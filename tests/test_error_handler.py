"""ERRORI BINANCE — tre gravita', tre risposte diverse.

Un `except Exception` unico tratta allo stesso modo un sovraccarico temporaneo
(riprova e passa), un rifiuto legittimo dell'exchange (margine insufficiente:
riprovare peggiora) e un bug nostro (parametri invalidi: riprovare lo ripete
all'infinito).

I due test che contano di piu':

* `unknown_errors_do_not_retry` — un errore che non sappiamo leggere potrebbe
  essere qualunque cosa, e insistere alla cieca e' il modo peggiore di scoprirlo.
* `any_error_while_placing_protection_is_critical` — li' si e' con una posizione
  aperta e forse senza stop, e una posizione con leva e senza stop puo' perdere
  senza limite. Il codice dell'errore non conta.
"""
import pytest

from bot.execution.error_handler import (Severity, call_with_retry, classify,
                                         extract_code, final_severity)


class _Err(Exception):
    def __init__(self, code=None, msg="boom", headers=None):
        super().__init__(f"APIError(code={code}): {msg}" if code else msg)
        if code is not None:
            self.code = code
        if headers is not None:
            self.response = type("R", (), {"headers": headers})()


# ---- estrazione del codice -------------------------------------------------- #
def test_code_from_attribute_and_from_message():
    assert extract_code(_Err(-2019)) == -2019
    assert extract_code(Exception("APIError(code=-1111): precision")) == -1111


def test_no_code_at_all():
    assert extract_code(Exception("connessione persa")) is None


# ---- classificazione -------------------------------------------------------- #
@pytest.mark.parametrize("code", [429, 502, 503, 504, -1021])
def test_transient_errors_are_retryable(code):
    assert classify(_Err(code)).severity is Severity.RETRY


@pytest.mark.parametrize("code", [-2019, -2020, -1003])
def test_exchange_refusals_stop_without_retrying(code):
    """L'exchange ha risposto e ha detto no: riprovare non cambia la risposta."""
    assert classify(_Err(code)).severity is Severity.STOP


@pytest.mark.parametrize("code", [-1100, -1111, -2021])
def test_our_own_bugs_are_critical(code):
    assert classify(_Err(code)).severity is Severity.CRITICAL


def test_unknown_errors_do_not_retry():
    """Un errore che non sappiamo leggere potrebbe essere qualunque cosa:
    insistere alla cieca e' il modo peggiore di scoprirlo."""
    c = classify(Exception("qualcosa di mai visto"))
    assert c.severity is Severity.STOP
    assert "sconosciuto" in c.label


def test_any_error_while_placing_protection_is_critical():
    """Dopo l'entry si e' con una posizione aperta e forse senza stop: il codice
    dell'errore non conta, la situazione si'."""
    for exc in (_Err(429), _Err(-2019), Exception("timeout")):
        assert classify(exc, placing_protection=True).severity is Severity.CRITICAL


def test_retry_after_header_is_read():
    assert classify(_Err(429, headers={"Retry-After": "7"})).retry_after_s == 7.0


def test_a_broken_retry_after_does_not_crash_the_classification():
    assert classify(_Err(429, headers={"Retry-After": "presto"})).retry_after_s is None


# ---- retry ------------------------------------------------------------------ #
def test_a_transient_error_is_retried_until_it_works():
    calls, waits = {"n": 0}, []

    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise _Err(503)
        return "ok"
    assert call_with_retry(fn, sleep=waits.append) == "ok"
    assert calls["n"] == 3
    assert waits == [1.0, 2.0], "l'attesa deve crescere, non restare fissa"


def test_the_exchange_wait_wins_over_our_backoff():
    """Retry-After viene da chi sa quanto e' sovraccarico: il nostro backoff no."""
    waits = []

    def fn():
        raise _Err(429, headers={"Retry-After": "9"})
    with pytest.raises(_Err):
        call_with_retry(fn, sleep=waits.append)
    assert waits == [9.0, 9.0]


def test_a_stop_error_is_not_retried_at_all():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise _Err(-2019)
    with pytest.raises(_Err):
        call_with_retry(fn, sleep=lambda _s: None)
    assert calls["n"] == 1


def test_retries_are_bounded():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise _Err(503)
    with pytest.raises(_Err):
        call_with_retry(fn, attempts=3, sleep=lambda _s: None)
    assert calls["n"] == 3


def test_events_are_reported_for_every_attempt():
    seen = []

    def fn():
        raise _Err(503)
    with pytest.raises(_Err):
        call_with_retry(fn, sleep=lambda _s: None,
                        on_event=lambda c, i: seen.append((c.severity, i)))
    assert [i for _s, i in seen] == [1, 2, 3]


# ---- gravita' finale --------------------------------------------------------- #
def test_an_exhausted_retryable_becomes_a_stop():
    """Rimetterlo in coda come "riprovabile" significherebbe insistere su una
    richiesta che l'exchange sta gia' rifiutando — la strada per farsi bandire."""
    assert final_severity(_Err(503), attempts_done=3) is Severity.STOP
    assert final_severity(_Err(503), attempts_done=1) is Severity.RETRY


def test_critical_stays_critical_whatever_the_attempts():
    assert final_severity(_Err(-1111), attempts_done=1) is Severity.CRITICAL
