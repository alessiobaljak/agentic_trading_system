"""Programma 5: barre di un'ora fatte dalle candele da 1 minuto, con interesse aperto, rapporti long/short e funding
noti alla fine di ogni ora (esplorazione E-001, ``esplorazione/E-001/piano.md``).

Indice = ora dall'epoca (minuto // 60). Si decide alla chiusura dell'ora t, cioe' al minuto 60·(t+1): i dati del file
``metrics`` e del funding valgono se il loro minuto e' <= 60·(t+1). Le barre si tengono in ``research/data/p5/ore/``
(fuori da git) per non rifarle.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5

CACHE = m5.DATI / "ore"
MINUTI_MINIMI = 50


def _asof(indice_minuti: np.ndarray, serie: pd.Series) -> np.ndarray:
    """Per ogni minuto dell'indice, l'ultimo valore della serie con minuto <= quello (NaN se non c'e')."""
    s = serie.dropna()
    if s.empty:
        return np.full(len(indice_minuti), np.nan)
    pos = np.searchsorted(s.index.to_numpy(), indice_minuti, "right") - 1
    out = np.where(pos >= 0, s.to_numpy(float)[np.clip(pos, 0, None)], np.nan)
    return out


def barre(simbolo: str, periodo: str = "C", idea=None, storia_giorni: int = 100) -> pd.DataFrame:
    CACHE.mkdir(parents=True, exist_ok=True)
    file = CACHE / f"{simbolo}_{periodo}.pkl"
    if file.exists():
        return pd.read_pickle(file)
    df = m5.minuti(simbolo, periodo, idea, storia_giorni=storia_giorni)
    if df.empty:
        return pd.DataFrame()
    ora = df.index.to_numpy() // 60
    valido = np.isfinite(df["close"].to_numpy())
    g = df.assign(ora=ora, valido=valido)
    g = g[g["valido"]]
    agg = g.groupby("ora").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                               close=("close", "last"), volume=("volume", "sum"),
                               buy=("taker_buy_volume", "sum"), n=("close", "size"),
                               periodo=("periodo", "max"))
    agg = agg.reindex(np.arange(agg.index.min(), agg.index.max() + 1))
    poche = ~(agg["n"] >= MINUTI_MINIMI)
    agg.loc[poche, ["open", "high", "low", "close", "volume", "buy"]] = np.nan
    agg["periodo"] = agg["periodo"].eq(True)
    fine = (agg.index.to_numpy() + 1) * 60          # minuto in cui si decide
    met = m5.metrics(simbolo, periodo, idea, storia_giorni=storia_giorni)
    for col, nome in [("sum_open_interest", "oi"), ("count_long_short_ratio", "ls_tutti"),
                      ("sum_toptrader_long_short_ratio", "ls_grandi_pos"),
                      ("count_toptrader_long_short_ratio", "ls_grandi_conti")]:
        agg[nome] = _asof(fine, met[col]) if not met.empty and col in met else np.nan
        if not met.empty and col in met:
            # un valore vecchio di oltre 30 minuti non vale come «noto alla fine dell'ora»
            ultimo = _asof(fine, pd.Series(met.index.to_numpy(float), index=met.index).where(met[col].notna()))
            agg.loc[(fine - ultimo) > 30, nome] = np.nan
    fund = m5.funding(simbolo)
    if len(fund):
        f8 = fund["tasso"] * 8.0 / fund["ore"].clip(lower=1)
        agg["funding_8h"] = _asof(fine, f8)
        cum = fund["tasso"].cumsum()
        agg["funding_cum"] = _asof(fine, cum)
        agg["funding_cum"] = agg["funding_cum"].fillna(0.0)
        agg["regolamento"] = np.isin(fine, fund.index.to_numpy())
    else:
        agg["funding_8h"], agg["funding_cum"], agg["regolamento"] = np.nan, 0.0, False
    agg.to_pickle(file)
    return agg
