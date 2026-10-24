"""Le regole mensili che scelgono i titoli dell'indice per un punteggio (prove 12 e 13)."""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from stock.simulatore.portafoglio import Storia, StatoConto, verso_pesi
from stock.strategie.rimbalzo import giorni_dopo

SEDUTE = 252


def volatilita(passato: pd.Series) -> float:
    """Deviazione standard dei rendimenti giornalieri delle ultime 252 sedute (prova 12)."""
    r = passato.iloc[-SEDUTE - 1:].pct_change().dropna()
    return float(r.std(ddof=1))


def momento(passato: pd.Series) -> float:
    """Rendimento da 252 a 21 sedute fa (prova 13)."""
    return float(passato.iloc[-1 - 21] / passato.iloc[-1 - SEDUTE] - 1)


def strategia_classifica(membri, calendario: list[date], rettificati: dict[str, pd.Series], punteggio, quanti: int = 50,
                         i_piu_bassi: bool = True):
    dopo = giorni_dopo(calendario)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        prossimo = dopo.get(giorno)
        if prossimo is None or prossimo.month == giorno.month:
            return []
        valori, prezzi = {}, {}
        for s in membri(giorno):
            r = rettificati.get(s)
            h = storia(s)
            if r is None or h is None or h.empty or h.index[-1] != giorno:
                continue
            passato = r.loc[:giorno]
            if len(passato) < SEDUTE + 1:
                continue
            v = punteggio(passato)
            if np.isfinite(v):
                valori[s] = v
                prezzi[s] = float(h["close"].iloc[-1])
        if len(valori) < quanti:
            return []
        ordine = sorted(valori, key=lambda s: (valori[s] if i_piu_bassi else -valori[s], s))
        scelti = ordine[:quanti]
        for s in stato.azioni:
            if s not in prezzi:
                h = storia(s)
                if h is not None and not h.empty:
                    prezzi[s] = float(h["close"].iloc[-1])
        return verso_pesi(stato, {s: 1 / quanti for s in scelti}, prezzi, etichetta="mese")
    return decidi
