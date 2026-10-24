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
