"""Lo scarto fra acquisto e vendita, MISURATO sulle quotazioni (`METODO.md`, sezione 5).

Le quotazioni arrivano a raffiche: contarle tutte darebbe più peso ai momenti agitati. Si prende
quindi l'ultima quotazione valida prima di ogni minuto (una «fotografia» al minuto) e su quelle si
calcola lo scarto relativo, (vendita - acquisto) / prezzo medio.
"""
from __future__ import annotations

import pandas as pd


def quotazioni_valide(q: pd.DataFrame) -> pd.DataFrame:
    """Toglie le quotazioni senza un lato (prezzo 0), quelle «incrociate» (acquisto sopra la
    vendita) e quelle con quantità zero."""
    ok = (q["bid"] > 0) & (q["ask"] > 0) & (q["ask"] >= q["bid"])
    if "bid_size" in q and "ask_size" in q:
        ok &= (q["bid_size"] > 0) & (q["ask_size"] > 0)
    return q[ok]


def fotografie_al_minuto(q: pd.DataFrame) -> pd.DataFrame:
    """L'ultima quotazione valida prima della fine di ogni minuto in cui ce n'è almeno una."""
    q = quotazioni_valide(q)
    if q.empty:
        return q
    return q.groupby(q.index.floor("min")).last()


def scarto_relativo(q: pd.DataFrame) -> pd.Series:
    mezzo = (q["ask"] + q["bid"]) / 2
    return (q["ask"] - q["bid"]) / mezzo


def misura(q: pd.DataFrame) -> dict:
    """Riepilogo dello scarto relativo sulle fotografie al minuto: mediana, media, 90° percentile e
    quante fotografie. Il costo di un'operazione «a mercato» è circa metà dello scarto."""
    f = fotografie_al_minuto(q)
    if f.empty:
        return {"fotografie": 0, "mediana": None, "media": None, "p90": None}
    s = scarto_relativo(f)
    return {"fotografie": int(len(s)), "mediana": float(s.median()), "media": float(s.mean()),
            "p90": float(s.quantile(0.9))}
