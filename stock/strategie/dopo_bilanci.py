"""La deriva dopo i bilanci (`stock/prove/P010_dopo_i_bilanci.md`)."""
from __future__ import annotations

import bisect
import math
from datetime import date

import pandas as pd

from stock.simulatore.motore import Ordine
from stock.simulatore.portafoglio import Storia, StatoConto
from stock.strategie.rimbalzo import elenco_del_mese

QUOTA = 0.10
MASSIMO = 10
SEDUTE = 20


def piano(comunicati: dict[str, list[date]], calendario: list[date]) -> dict[date, list[tuple[str, date, date]]]:
    """Per ogni giorno di decisione (il giorno di borsa dopo d): (simbolo, giorno prima di d, giorno dopo d)."""
    c = sorted(calendario)
    out: dict[date, list[tuple[str, date, date]]] = {}
    for s, giorni in comunicati.items():
        for d in giorni:
            k = bisect.bisect_left(c, d)
            if k < 1 or k + 2 >= len(c):
                continue
            out.setdefault(c[k + 1], []).append((s, c[k - 1], c[k + 1]))
    return out


def strategia(comunicati: dict[str, list[date]], universo: pd.DataFrame, calendario: list[date],
              rettificati: dict[str, pd.Series], indice: pd.Series):
    c = sorted(calendario)
    pos = {d: i for i, d in enumerate(c)}
    da_decidere = piano(comunicati, c)
    elenchi = elenco_del_mese(universo)
    da_vendere: dict[date, list[str]] = {}

    def reazione(s: str, prima: date, dopo: date, giorno: date) -> float | None:
        r = rettificati.get(s)
        if r is None or dopo > giorno or prima not in r.index or dopo not in r.index:
            return None
        if prima not in indice.index or dopo not in indice.index:
            return None
        return (r[dopo] / r[prima] - 1) - (indice[dopo] / indice[prima] - 1)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        ordini = []
        for t in da_vendere.pop(giorno, []):
            q = stato.azioni.get(t, 0)
            if q > 0:
                ordini.append((t, Ordine(-q, "mercato", etichetta="uscita")))
        k = pos.get(giorno)
        if k is None or k + 1 >= len(c):
            return ordini
        ingresso = c[k + 1]
        elenco = set(elenchi.get(f"{ingresso:%Y-%m}", []))
        tenuti = {t for t, q in stato.azioni.items() if q > 0} - {t for t, _ in ordini}
        liberi = MASSIMO - len(tenuti)
        for s, prima, dopo in sorted(da_decidere.get(giorno, [])):
            if liberi <= 0 or s in tenuti or s not in elenco:
                continue
            x = reazione(s, prima, dopo, giorno)
            h = storia(s)
            if x is None or x <= 0 or h is None or h.empty or h.index[-1] != giorno:
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
