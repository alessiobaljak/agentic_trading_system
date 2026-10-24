"""Dove stanno i prezzi scaricati: FUORI dal repository.

I prezzi non si committano (sono grandi, e la licenza dei dati di borsa di regola non permette
di ripubblicarli: il repository è pubblico). La cartella è `STOCK_DATI_DIR` se impostata,
altrimenti `~/stock_dati`. Una cartella dentro il repository viene rifiutata.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

RADICE_REPO = Path(__file__).resolve().parents[2]


class CartellaVietata(ValueError):
    pass


def cartella_dati(cartella: str | os.PathLike | None = None) -> Path:
    p = Path(cartella or os.environ.get("STOCK_DATI_DIR") or Path.home() / "stock_dati").expanduser().resolve()
    if p == RADICE_REPO or RADICE_REPO in p.parents:
        raise CartellaVietata(f"{p} è dentro il repository: i prezzi non ci vanno")
    p.mkdir(parents=True, exist_ok=True)
    return p


def percorso(simbolo: str, tipo: str, cartella=None) -> Path:
    """`tipo`: per esempio "1Day_raw", "1Day_all", "1Min_raw", "azioni"."""
    return cartella_dati(cartella) / simbolo / f"{tipo}.csv.gz"


def salva(df: pd.DataFrame, simbolo: str, tipo: str, cartella=None) -> Path:
    p = percorso(simbolo, tipo, cartella)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not tipo.startswith("azioni"):
        df = df.rename_axis("t")
    df.to_csv(p, compression="gzip")
    return p


def carica(simbolo: str, tipo: str, cartella=None) -> pd.DataFrame | None:
    p = percorso(simbolo, tipo, cartella)
    if not p.exists():
        return None
    if tipo.startswith("azioni"):
        df = pd.read_csv(p, index_col=0)
        df["data"] = pd.to_datetime(df["data"]).dt.date
        return df
    df = pd.read_csv(p, index_col="t")
    df.index = pd.to_datetime(df.index, utc=True)
    return df
