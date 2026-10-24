"""Il rimbalzo dopo le cadute della settimana (`stock/prove/P003_rimbalzo.md`) e il suo termine di paragone, il
comprare e tenere le 10 di allora a pesi uguali. Funzioni per il simulatore a più titoli."""
from __future__ import annotations

from datetime import date

import pandas as pd

from stock.simulatore.portafoglio import Storia, StatoConto, verso_pesi

QUANTI = 3
SEDUTE = 5


def giorni_dopo(calendario: list[date]) -> dict[date, date]:
    c = sorted(calendario)
    return dict(zip(c[:-1], c[1:]))


def elenco_del_mese(universo: pd.DataFrame) -> dict[str, list[str]]:
    return {m: list(g.sort_values("posizione")["simbolo"]) for m, g in universo.groupby("mese")}


def strategia_rimbalzo(universo: pd.DataFrame, calendario: list[date], rettificati: dict[str, pd.Series]):
    """`rettificati`: per simbolo la chiusura corretta per dividendi, frazionamenti e scissioni, con indice
    il giorno di New York (il rapporto fra due chiusure usa solo gli eventi fra le due: niente futuro)."""
    dopo = giorni_dopo(calendario)
    elenchi = elenco_del_mese(universo)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        prossimo = dopo.get(giorno)
        if prossimo is None or prossimo.isocalendar()[:2] == giorno.isocalendar()[:2]:
            return []                                    # non è l'ultimo giorno di borsa della settimana
        elenco = elenchi.get(f"{prossimo:%Y-%m}")
        if not elenco:
            return []
        rendimenti, prezzi = {}, {}
        for s in elenco:
            r = rettificati.get(s)
            h = storia(s)
            if r is None or h is None or h.empty or h.index[-1] != giorno:
                continue
            passato = r.loc[:giorno]
            if len(passato) < SEDUTE + 1:
                continue
            rendimenti[s] = passato.iloc[-1] / passato.iloc[-1 - SEDUTE] - 1
            prezzi[s] = float(h["close"].iloc[-1])
        if len(rendimenti) < QUANTI:
            return []
        scelti = sorted(rendimenti, key=lambda s: rendimenti[s])[:QUANTI]
        return verso_pesi(stato, {s: 1 / QUANTI for s in scelti}, prezzi, etichetta="settimana")
    return decidi


def strategia_tenere_i_dieci(universo: pd.DataFrame, calendario: list[date]):
    """Il termine di paragone: le 10 di allora a pesi uguali, ribilanciate il primo giorno di borsa di ogni mese."""
    dopo = giorni_dopo(calendario)
    elenchi = elenco_del_mese(universo)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        prossimo = dopo.get(giorno)
        if prossimo is None or prossimo.month == giorno.month:
            return []
        elenco = elenchi.get(f"{prossimo:%Y-%m}")
        if not elenco:
            return []
        prezzi = {}
        for s in elenco:
            h = storia(s)
            if h is not None and not h.empty and h.index[-1] == giorno:
                prezzi[s] = float(h["close"].iloc[-1])
        if not prezzi:
            return []
        return verso_pesi(stato, {s: 1 / len(prezzi) for s in prezzi}, prezzi, etichetta="mese")
    return decidi
