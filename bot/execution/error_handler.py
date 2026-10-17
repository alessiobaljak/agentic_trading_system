"""ERRORI BINANCE — non tutti gli errori vogliono la stessa risposta.

Un `except Exception` unico tratta allo stesso modo tre cose molto diverse: un
sovraccarico temporaneo (riprova e passa), un rifiuto legittimo dell'exchange
(margine insufficiente: riprovare peggiora e basta) e un bug nostro (parametri
invalidi: riprovare lo ripete all'infinito). Qui la distinzione e' esplicita.

  * RIPROVABILI — la richiesta e' giusta, l'exchange ora non puo'. Fino a tre
    tentativi con attesa crescente; se il codice porta un `Retry-After`, quello
    vince sul backoff, perche' e' l'exchange a dire quanto aspettare. Dopo il
    terzo tentativo diventa un errore da FERMATA: insistere oltre significa solo
    farsi bandire.
  * DA FERMATA — l'exchange ha risposto, e ha detto no. Nessun retry: si logga,
    si avvisa e si sospende quell'asset per un po'. Il bot continua sulle altre.
  * CRITICI — l'errore descrive un difetto NOSTRO (parametri invalidi, precisione
    sbagliata) o una situazione ambigua sull'ordine. Riprovare puo' fare danni:
    il bot si ferma e chiede un intervento.

CASO SPECIALE, il piu' pericoloso di tutti: un errore mentre si piazza lo SL/TP
DOPO che l'entry e' passata. Qualunque sia il codice, li' si e' con una posizione
aperta e forse senza protezione — e una posizione con leva e senza stop puo'
perdere senza limite. Quel caso e' sempre critico e attiva la riconciliazione su
quel simbolo.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, TypeVar

RETRY_ERRORS = {
    429: "rate_limit",        # troppe richieste: l'header Retry-After dice quanto
    502: "gateway",
    503: "service",
    504: "timeout",
    -1021: "timestamp",       # clock disallineato: si risincronizza e si riprova
}

STOP_ERRORS = {
    -2019: "margin_insufficient",
    -2020: "would_trigger",       # l'ordine scatterebbe subito: setup non valido
    -1003: "too_many_requests",
}

CRITICAL_ERRORS = {
    -1100: "invalid_params",      # bug nostro: riprovare lo ripete all'infinito
    -1111: "precision_error",     # sizing sbagliato
    -2021: "order_filled_denied",  # ambiguo sullo stato dell'ordine
}


class Severity(str, Enum):
    RETRY = "retry"
    STOP = "stop"
    CRITICAL = "critical"


@dataclass
class Classified:
    severity: Severity
    code: Optional[int]
    label: str
    retry_after_s: Optional[float] = None


_CODE_RE = re.compile(r"-?\d{3,5}")


def extract_code(exc: BaseException) -> Optional[int]:
    """Codice Binance dall'eccezione, qualunque libreria la sollevi.

    python-binance espone `.code`; altri client mettono tutto nel messaggio. Si
    prova prima l'attributo e poi il testo: senza questo, un client diverso
    farebbe ricadere ogni errore nel ramo peggiore.
    """
    for attr in ("code", "status_code"):
        v = getattr(exc, attr, None)
        if isinstance(v, int):
            return v
    m = _CODE_RE.search(str(exc))
    return int(m.group()) if m else None


def _retry_after(exc: BaseException) -> Optional[float]:
    """Secondi indicati dall'exchange, se li indica. Hanno precedenza sul backoff:
    e' Binance a sapere quanto e' sovraccarico, non noi."""
    hdrs = getattr(getattr(exc, "response", None), "headers", None) or {}
    try:
        v = hdrs.get("Retry-After") or hdrs.get("retry-after")
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def classify(exc: BaseException, placing_protection: bool = False) -> Classified:
    """Gravita' di un errore. `placing_protection=True` quando si sta piazzando lo
    SL/TP dopo un'entry gia' eseguita: li' QUALUNQUE errore e' critico, perche' si
    resta con una posizione aperta e forse scoperta."""
    code = extract_code(exc)
    if placing_protection:
        return Classified(Severity.CRITICAL, code,
                          "protezione non piazzata dopo l'entry", None)
    if code in RETRY_ERRORS:
        return Classified(Severity.RETRY, code, RETRY_ERRORS[code], _retry_after(exc))
    if code in STOP_ERRORS:
        return Classified(Severity.STOP, code, STOP_ERRORS[code])
    if code in CRITICAL_ERRORS:
        return Classified(Severity.CRITICAL, code, CRITICAL_ERRORS[code])
    # sconosciuto: si FERMA, non si riprova. Un errore che non sappiamo leggere
    # potrebbe essere qualunque cosa, e insistere alla cieca e' il modo peggiore
    # di scoprirlo.
    return Classified(Severity.STOP, code, f"sconosciuto ({type(exc).__name__})")


T = TypeVar("T")


def call_with_retry(fn: Callable[[], T], *, attempts: int = 3,
                    base_delay: float = 1.0, sleep=None,
                    placing_protection: bool = False,
                    on_event: Optional[Callable[[Classified, int], None]] = None) -> T:
    """Esegue `fn` gestendo gli errori per gravita'. Rilancia se non si recupera.

    Solo i RIPROVABILI vengono ritentati, con attesa esponenziale (o quella
    indicata dall'exchange). Dopo l'ultimo tentativo l'errore vale come DA
    FERMATA: il chiamante lo vedra' come tale invece di come "riprovabile", cosi'
    non entra in un ciclo di tentativi che l'exchange sta gia' rifiutando.

    `sleep` e' iniettabile: senza, i test dovrebbero attendere davvero.
    """
    import time as _time
    sleep = sleep or _time.sleep
    last: Optional[BaseException] = None
    for i in range(max(1, attempts)):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last = exc
            c = classify(exc, placing_protection)
            if on_event:
                on_event(c, i + 1)
            if c.severity is not Severity.RETRY or i == attempts - 1:
                raise
            sleep(c.retry_after_s if c.retry_after_s is not None
                  else base_delay * (2 ** i))
    raise last if last else RuntimeError("call_with_retry: nessun tentativo eseguito")


def final_severity(exc: BaseException, attempts_done: int, attempts: int = 3,
                   placing_protection: bool = False) -> Severity:
    """Gravita' DEFINITIVA dopo che i tentativi sono finiti.

    Serve al chiamante per decidere: un riprovabile esaurito non e' piu'
    riprovabile, e trattarlo come tale rimetterebbe in coda la stessa richiesta
    che l'exchange sta rifiutando.
    """
    c = classify(exc, placing_protection)
    if c.severity is Severity.RETRY and attempts_done >= attempts:
        return Severity.STOP
    return c.severity
