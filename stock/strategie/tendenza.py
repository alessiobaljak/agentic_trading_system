"""Seguire la tendenza dell'indice (`stock/prove/P005_tendenza.md`): dentro se le ultime 252 sedute sono in
guadagno, fuori altrimenti; si decide l'ultimo giorno di borsa di ogni mese."""
from __future__ import annotations

from datetime import date

import pandas as pd

from stock.simulatore.portafoglio import Storia, StatoConto, verso_pesi
from stock.strategie.rimbalzo import giorni_dopo

SEDUTE = 252


def strategia(simbolo: str, calendario: list[date], rettificata: pd.Series):
    dopo = giorni_dopo(calendario)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        prossimo = dopo.get(giorno)
        if prossimo is None or prossimo.month == giorno.month:
            return []
        h = storia(simbolo)
        passato = rettificata.loc[:giorno]
        if h is None or h.empty or h.index[-1] != giorno or len(passato) < SEDUTE + 1:
            return []
        dentro = passato.iloc[-1] / passato.iloc[-1 - SEDUTE] - 1 > 0
        prezzo = float(h["close"].iloc[-1])
        return verso_pesi(stato, {simbolo: 1.0} if dentro else {}, {simbolo: prezzo}, etichetta="mese")
    return decidi


def strategia_calma(simbolo: str, calendario: list[date], rettificata: pd.Series, obiettivo: float = 0.16,
                    massimo: float = 1.5, sedute: int = 21, soglia: float = 0.10):
    """Più investiti quando il mercato è calmo (`stock/prove/P015_calma_e_agitazione.md`)."""
    import math

    import numpy as np

    from stock.simulatore.motore import Ordine
    dopo = giorni_dopo(calendario)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        prossimo = dopo.get(giorno)
        if prossimo is None or prossimo.isocalendar()[:2] == giorno.isocalendar()[:2]:
            return []
        h = storia(simbolo)
        passato = rettificata.loc[:giorno]
        if h is None or h.empty or h.index[-1] != giorno or len(passato) < sedute + 1:
            return []
        agitazione = float(passato.iloc[-sedute - 1:].pct_change().dropna().std(ddof=1) * np.sqrt(252))
        quota = min(massimo, obiettivo / agitazione) if agitazione > 0 else massimo
        prezzo = float(h["close"].iloc[-1])
        v = stato.valore()
        voluto = math.floor(quota * 0.98 * v / prezzo)
        d = voluto - stato.azioni.get(simbolo, 0)
        if abs(d) * prezzo < soglia * v:
            return []
        return [(simbolo, Ordine(d, "mercato", etichetta="settimana"))]
    return decidi


def strategia_classi(simboli: list[str], calendario: list[date], rettificate: dict[str, pd.Series], diario: list | None = None):
    """La tendenza su più fondi (`stock/prove/P026_tendenza_altre_classi.md`): a fine mese ogni fondo con le ultime 252 sedute in
    guadagno ha la sua parte uguale del conto, gli altri restano in contanti."""
    dopo = giorni_dopo(calendario)
    parte = 1.0 / len(simboli)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        prossimo = dopo.get(giorno)
        if prossimo is None or prossimo.month == giorno.month:
            return []
        pesi, prezzi = {}, {}
        for s in simboli:
            h = storia(s)
            passato = rettificate[s].loc[:giorno]
            if h is None or h.empty or h.index[-1] != giorno or len(passato) < SEDUTE + 1:
                return []                      # si decide solo con tutti i fondi (controllo dei dati)
            prezzi[s] = float(h["close"].iloc[-1])
            if passato.iloc[-1] / passato.iloc[-1 - SEDUTE] - 1 > 0:
                pesi[s] = parte
        if diario is not None:
            diario.append({"giorno": giorno, "dentro": sorted(pesi)})
        return verso_pesi(stato, pesi, prezzi, etichetta="mese")
    return decidi
