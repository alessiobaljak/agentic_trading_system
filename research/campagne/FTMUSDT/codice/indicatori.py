"""Indicatori causali: il valore all'indice i usa solo le barre 0..i (barre chiuse)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def atr(s, n: int) -> np.ndarray:
    c_prev = np.concatenate([[np.nan], s.c[:-1]])
    alto = np.where(np.isnan(c_prev), s.h, np.maximum(s.h, c_prev))
    basso = np.where(np.isnan(c_prev), s.l, np.minimum(s.l, c_prev))
    return pd.Series(alto - basso).rolling(n, min_periods=n).mean().to_numpy()


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """max(x[i-n..i-1]): le n barre PRIMA della barra i."""
    return pd.Series(x).shift(1).rolling(n, min_periods=n).max().to_numpy()


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).shift(1).rolling(n, min_periods=n).min().to_numpy()


def rendimento(c: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(c), np.nan)
    out[n:] = c[n:] / c[:-n] - 1
    return out


def log_rend(c: np.ndarray) -> np.ndarray:
    out = np.full(len(c), np.nan)
    out[1:] = np.log(c[1:] / c[:-1])
    return out


def dev_std_mobile(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).std().to_numpy()


def media_mobile(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()


def rsi_semplice(c: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder con media esponenziale alfa = 1/n (come Connors per l'RSI a 2)."""
    d = np.diff(c, prepend=np.nan)
    su = pd.Series(np.where(d > 0, d, 0.0))
    giu = pd.Series(np.where(d < 0, -d, 0.0))
    su[0] = np.nan
    giu[0] = np.nan
    ms = su.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    mg = giu.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = ms / mg
    return (100 - 100 / (1 + rs)).to_numpy()


def percentile_mobile(x: np.ndarray, n: int, q: float) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).quantile(q, interpolation="linear").to_numpy()
