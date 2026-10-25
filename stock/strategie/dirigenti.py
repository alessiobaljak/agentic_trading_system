"""Gli acquisti dei dirigenti (`stock/prove/P018_acquisti_dirigenti.md`)."""
from __future__ import annotations

import bisect
import math
from datetime import date

from stock.simulatore.motore import Ordine
from stock.simulatore.portafoglio import Storia, StatoConto

QUOTA = 0.05
MASSIMO = 20
SEDUTE = 20


def strategia(eventi: list[tuple[date, str, float]], calendario: list[date]):
    """`eventi`: (giorno di deposito, simbolo, valore). Decisione alla chiusura del primo giorno di borsa non prima del
    deposito, ingresso all'apertura del giorno di borsa dopo (un deposito di sabato o domenica entra un giorno più tardi)."""
    c = sorted(calendario)
    pos = {d: i for i, d in enumerate(c)}
    piano: dict[date, list[tuple[float, str]]] = {}
    for d, s, v in eventi:
        k = bisect.bisect_left(c, d)
        if k + 1 < len(c):
            piano.setdefault(c[k], []).append((v, s))
    da_vendere: dict[date, list[str]] = {}

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        ordini = []
        for t in da_vendere.pop(giorno, []):
            q = stato.azioni.get(t, 0)
            if q > 0:
                ordini.append((t, Ordine(-q, "mercato", etichetta="uscita")))
        k = pos.get(giorno)
        if k is None:
            return ordini
        tenuti = {t for t, q in stato.azioni.items() if q > 0} - {t for t, _ in ordini}
        liberi = MASSIMO - len(tenuti)
        for v, s in sorted(piano.get(giorno, []), key=lambda x: (-x[0], x[1])):
            if liberi <= 0 or s in tenuti:
                continue
            h = storia(s)
            if h is None or h.empty or h.index[-1] != giorno:
                continue
            q = math.floor(QUOTA * stato.valore() / float(h["close"].iloc[-1]))
            if q <= 0:
                continue
            ordini.append((s, Ordine(q, "mercato", etichetta="ingresso")))
            if k + SEDUTE < len(c):
                da_vendere.setdefault(c[k + SEDUTE], []).append(s)
            tenuti.add(s)
            liberi -= 1
        return ordini
    return decidi


def strategia_contro(eventi: list[tuple[date, str, float]], calendario: list[date], base: str = "SPY", quota_base: float = 0.98,
                     primo: date | None = None):
    """Tenere `base` e vendere allo scoperto per 20 sedute i titoli appena comprati dai dirigenti (`P019_contro_i_dirigenti.md`).
    `primo`: il giorno da cui si comincia (prima non si fa niente)."""
    c = sorted(calendario)
    pos = {d: i for i, d in enumerate(c)}
    piano: dict[date, list[tuple[float, str]]] = {}
    for d, s, v in eventi:
        k = bisect.bisect_left(c, d)
        if k + 1 < len(c) and s != base:
            piano.setdefault(c[k], []).append((v, s))
    da_ricoprire: dict[date, list[str]] = {}

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        if primo is not None and giorno < primo:
            return []
        ordini = []
        hb = storia(base)
        if not stato.azioni.get(base) and hb is not None and not hb.empty and hb.index[-1] == giorno:
            q = math.floor(quota_base * stato.valore() / float(hb["close"].iloc[-1]))
            if q > 0:
                ordini.append((base, Ordine(q, "mercato", etichetta="base")))
        for t in da_ricoprire.pop(giorno, []):
            q = stato.azioni.get(t, 0)
            if q < 0:
                ordini.append((t, Ordine(-q, "mercato", etichetta="ricopertura")))
        k = pos.get(giorno)
        if k is None:
            return ordini
        scoperti = {t for t, q in stato.azioni.items() if q < 0} - {t for t, _ in ordini}
        liberi = MASSIMO - len(scoperti)
        for v, s in sorted(piano.get(giorno, []), key=lambda x: (-x[0], x[1])):
            if liberi <= 0 or s in scoperti:
                continue
            h = storia(s)
            if h is None or h.empty or h.index[-1] != giorno:
                continue
            q = math.floor(QUOTA * stato.valore() / float(h["close"].iloc[-1]))
            if q <= 0:
                continue
            ordini.append((s, Ordine(-q, "mercato", etichetta="scoperto")))
            if k + SEDUTE < len(c):
                da_ricoprire.setdefault(c[k + SEDUTE], []).append(s)
            scoperti.add(s)
            liberi -= 1
        return ordini
    return decidi
