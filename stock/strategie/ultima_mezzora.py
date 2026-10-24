"""L'ultima mezz'ora segue il resto della giornata (`stock/prove/P001_ultima_mezzora.md`).

La strategia è la funzione `decidi(storia, stato)` che il simulatore chiama alla chiusura di ogni barra.
I segnali sono preparati prima per velocità, ma ognuno usa solo barre fino a quella della decisione
(lo controlla `test_strategie.py`, tagliando il futuro).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from stock.simulatore.motore import Ordine, Stato

NY = "America/New_York"
QUOTA = 0.98   # parte del conto investita (margine contro la leva fra decisione ed esecuzione)


def solo_seduta(minuti: pd.DataFrame, cal: pd.DataFrame) -> pd.DataFrame:
    """Le barre dentro la seduta di ogni giorno (apertura ≤ t < chiusura del calendario)."""
    t = minuti.index.tz_convert(NY)
    giorni = pd.Index(t.date)
    ok = giorni.isin(cal.index)
    ap = pd.Series(cal["apertura"]).reindex(giorni[ok]).to_numpy()
    ch = pd.Series(cal["chiusura"]).reindex(giorni[ok]).to_numpy()
    tt = t[ok]
    dentro = np.zeros(len(minuti), dtype=bool)
    dentro[np.where(ok)[0]] = (tt >= ap) & (tt < ch)
    return minuti[dentro]


def prepara(barre: pd.DataFrame, cal: pd.DataFrame, giorni_esclusi: set) -> dict:
    """Per ogni barra (posizione): se è la barra del segnale, la direzione (+1, −1, 0); se è la penultima
    della seduta, l'uscita. `barre` = solo seduta."""
    t = barre.index.tz_convert(NY)
    giorni = np.array(t.date)
    chiusure = barre["close"].to_numpy()
    n = len(barre)
    direzione = np.full(n, np.nan)
    uscita = np.zeros(n, dtype=bool)
    tagli = np.r_[0, np.where(giorni[1:] != giorni[:-1])[0] + 1, n]
    ultima_chiusura_ieri = None
    for a, b in zip(tagli[:-1], tagli[1:]):
        d = giorni[a]
        ch = cal.loc[d, "chiusura"]
        minuto_segnale = ch - pd.Timedelta(minutes=31)   # barra che finisce mezz'ora prima della chiusura
        minuto_ingresso = ch - pd.Timedelta(minutes=30)
        minuto_uscita = ch - pd.Timedelta(minutes=1)
        minuto_decisione_uscita = ch - pd.Timedelta(minutes=2)
        tg = t[a:b]
        pos = {x: a + i for i, x in enumerate(tg)}
        valido = (ultima_chiusura_ieri is not None and d not in giorni_esclusi
                  and all(x in pos for x in (minuto_segnale, minuto_ingresso, minuto_uscita, minuto_decisione_uscita)))
        if valido:
            i = pos[minuto_segnale]
            r = chiusure[i] / ultima_chiusura_ieri - 1
            direzione[i] = float(np.sign(r))
            uscita[pos[minuto_decisione_uscita]] = True
        ultima_chiusura_ieri = chiusure[b - 1]
    return {"direzione": direzione, "uscita": uscita}


def strategia(segnali: dict):
    direzione, uscita = segnali["direzione"], segnali["uscita"]

    def decidi(storia: pd.DataFrame, stato: Stato) -> list:
        i = len(storia) - 1
        if uscita[i] and stato.azioni:
            return [Ordine(-stato.azioni, "mercato", etichetta="uscita")]
        d = direzione[i]
        if not np.isnan(d) and d != 0 and stato.azioni == 0:
            prezzo = float(storia["close"].iat[-1])
            q = math.floor(QUOTA * stato.valore(prezzo) / prezzo)
            if q > 0:
                return [Ordine(d * q, "mercato", etichetta="ingresso")]
        return []
    return decidi
