"""Programma 6: le candele a 15 minuti, 1 ora e 4 ore delle monete, fatte dalle candele da 1 minuto verificate del
programma 5 (``research/data/p5/<SIMBOLO>/klines``), con il funding cumulato. Tutto il periodo disponibile: il metodo
del programma 6 (finestre che avanzano, METODO.md) usa tutto il passato.

Le barre si tengono in ``research/data/p6/<SIMBOLO>_<tf>.pkl`` (fuori da git). Una barra vale con almeno l'80% dei minuti.

Uso: python3 -m research.programma6.dati [SIMBOLO ...]   (senza simboli: le 100 di universo_top100.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5

RADICE = Path(__file__).resolve().parents[2]
DATI6 = RADICE / "research" / "data" / "p6"
TF = {"15m": 15, "1h": 60, "4h": 240}
CENTO = tuple(json.loads((RADICE / "research" / "programma5" / "universo_top100.json").read_text())["scelte"])


def minuti_tutti(simbolo: str) -> pd.DataFrame:
    parti = [m5._csv_da_zip(p, m5.KLINE) for p in m5._file(simbolo, "klines")]
    if not parti:
        return pd.DataFrame()
    df = pd.concat(parti, ignore_index=True)
    df["open_time"] = m5._ms(df["open_time"])
    df["minuto"] = df["open_time"] // 60_000
    df = df.drop_duplicates("minuto").set_index("minuto").sort_index()
    return df[["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_volume"]].astype(float)


def costruisci(simbolo: str) -> dict:
    df = minuti_tutti(simbolo)
    if df.empty:
        return {}
    fund = m5.funding(simbolo)
    cum = np.concatenate([[0.0], np.cumsum(fund["tasso"].to_numpy(float))]) if len(fund) else np.array([0.0])
    f_min = fund.index.to_numpy() if len(fund) else np.array([], dtype=np.int64)
    out = {}
    for tf, m in TF.items():
        g = df.assign(barra=df.index.to_numpy() // m)
        b = g.groupby("barra").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                   close=("close", "last"), volume=("volume", "sum"),
                                   quote_volume=("quote_volume", "sum"), buy=("taker_buy_volume", "sum"),
                                   n=("close", "size"))
        b = b.reindex(np.arange(b.index.min(), b.index.max() + 1))
        poche = ~(b["n"] >= 0.8 * m)
        b.loc[poche, ["open", "high", "low", "close", "volume", "quote_volume", "buy"]] = np.nan
        fine = (b.index.to_numpy() + 1) * m                     # minuto in cui la barra chiude
        b["funding_cum"] = cum[np.searchsorted(f_min, fine, "right")] if len(f_min) else 0.0
        b["minuto"] = b.index.to_numpy() * m                    # minuto in cui la barra apre
        b = b.drop(columns="n").reset_index(drop=True)
        DATI6.mkdir(parents=True, exist_ok=True)
        b.to_pickle(DATI6 / f"{simbolo}_{tf}.pkl")
        out[tf] = len(b)
    return out


def barre(simbolo: str, tf: str) -> pd.DataFrame:
    f = DATI6 / f"{simbolo}_{tf}.pkl"
    return pd.read_pickle(f) if f.exists() else pd.DataFrame()


if __name__ == "__main__":
    for s in (sys.argv[1:] or CENTO):
        if (DATI6 / f"{s}_4h.pkl").exists():
            continue
        print(s, costruisci(s), flush=True)
