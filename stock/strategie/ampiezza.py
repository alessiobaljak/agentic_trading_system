"""L'ampiezza del mercato (`stock/prove/P016_ampiezza.md`)."""
from __future__ import annotations

import math
from datetime import date

import pandas as pd

from stock.simulatore.motore import Ordine
from stock.simulatore.portafoglio import Storia, StatoConto
from stock.strategie.rimbalzo import giorni_dopo

SEDUTE = 200


def serie_ampiezza(rettificati: dict[str, pd.Series], membri, giorni: list[date]) -> pd.Series:
    """Per ogni giorno, la quota dei titoli dell'indice di quel giorno sopra la media delle loro ultime 200 sedute. La media
    mobile usa solo le chiusure fino a quel giorno; un titolo senza 200 chiusure non conta."""
    tab = pd.DataFrame(rettificati).sort_index()
    sopra = tab > tab.rolling(SEDUTE, min_periods=SEDUTE).mean()
    valida = tab.rolling(SEDUTE, min_periods=SEDUTE).mean().notna()
    out = {}
    for g in giorni:
        if g not in tab.index:
            continue
        m = [s for s in membri(g) if s in tab.columns]
        v = valida.loc[g, m]
        if v.sum() == 0:
            continue
        out[g] = float(sopra.loc[g, m][v].mean())
    return pd.Series(out)


def strategia(simbolo: str, calendario: list[date], ampiezza: pd.Series, soglia_ampiezza: float = 0.5,
              alta: float = 0.98, bassa: float = 0.49, soglia_ordine: float = 0.10):
    dopo = giorni_dopo(calendario)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        prossimo = dopo.get(giorno)
        if prossimo is None or prossimo.month == giorno.month or giorno not in ampiezza.index:
            return []
        h = storia(simbolo)
        if h is None or h.empty or h.index[-1] != giorno:
            return []
        quota = alta if ampiezza[giorno] >= soglia_ampiezza else bassa
        prezzo = float(h["close"].iloc[-1])
        v = stato.valore()
        d = math.floor(quota * v / prezzo) - stato.azioni.get(simbolo, 0)
        if d == 0 or (abs(d) * prezzo < soglia_ordine * v and stato.azioni.get(simbolo, 0)):
            return []
        return [(simbolo, Ordine(d, "mercato", etichetta="mese"))]
    return decidi
