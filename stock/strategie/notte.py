"""Tenere solo di notte (`stock/prove/P004_notte.md`): si compra all'ultima barra della seduta e si vende alla
prima della seduta dopo."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from stock.simulatore.motore import Ordine, Stato

NY = "America/New_York"
QUOTA = 0.98


def prepara(barre: pd.DataFrame, cal: pd.DataFrame, giorni_esclusi: set) -> dict:
    """`barre` = solo seduta. Segna la penultima barra di ogni seduta (decisione d'acquisto) e l'ultima
    (decisione di vendita, eseguita alla prima barra della seduta dopo)."""
    t = barre.index.tz_convert(NY)
    giorni = np.array(t.date)
    n = len(barre)
    compra = np.zeros(n, dtype=bool)
    vendi = np.zeros(n, dtype=bool)
    tagli = np.r_[0, np.where(giorni[1:] != giorni[:-1])[0] + 1, n]
    for a, b in zip(tagli[:-1], tagli[1:]):
        d = giorni[a]
        ch = cal.loc[d, "chiusura"]
        if d in giorni_esclusi or b - a < 2:
            continue
        if t[b - 1] == ch - pd.Timedelta(minutes=1) and t[b - 2] == ch - pd.Timedelta(minutes=2):
            compra[b - 2] = True
            vendi[b - 1] = True
    return {"compra": compra, "vendi": vendi}


def con_dividendi(barre: pd.DataFrame, azioni: pd.DataFrame) -> pd.DataFrame:
    """Il dividendo sulla prima barra del giorno di stacco (lo incassa chi ha tenuto la notte prima)."""
    out = barre.copy()
    out["dividendo"] = 0.0
    if azioni is None or azioni.empty:
        return out
    giorni = pd.Index(out.index.tz_convert(NY).date)
    prima = ~pd.Series(giorni).duplicated().to_numpy()
    div = azioni[azioni["tipo"] == "dividendo"].groupby("data")["importo"].sum()
    valori = np.where(prima, [div.get(d, 0.0) for d in giorni], 0.0)
    out["dividendo"] = valori
    return out


def strategia(seg: dict):
    compra, vendi = seg["compra"], seg["vendi"]

    def decidi(storia: pd.DataFrame, stato: Stato) -> list:
        i = len(storia) - 1
        if vendi[i] and stato.azioni > 0:
            return [Ordine(-stato.azioni, "mercato", etichetta="mattina")]
        if compra[i] and stato.azioni == 0:
            c = float(storia["close"].iat[-1])
            q = math.floor(QUOTA * stato.valore(c) / c)
            return [Ordine(q, "mercato", etichetta="sera")] if q > 0 else []
        if not compra[i] and stato.azioni > 0:
            # comprati a una barra che non è l'ultima della seduta: un'uscita non è stata eseguita, si riprova subito
            return [Ordine(-stato.azioni, "mercato", etichetta="mattina, in ritardo")]
        return []
    return decidi
