"""Indicatori causali: il valore all'indice i usa solo le barre 0..i (barre chiuse)."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import List, Sequence

import numpy as np

NAN = float("nan")


def arr(candele, campo: str) -> np.ndarray:
    return np.array([getattr(c, campo) for c in candele], dtype=float)


def atr(candele, n: int = 14) -> np.ndarray:
    """ATR di Wilder; NaN finche' non ci sono n barre."""
    h, l, c = arr(candele, "high"), arr(candele, "low"), arr(candele, "close")
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    out = np.full(len(c), NAN)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), NAN)
    if len(x) < n:
        return out
    cs = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder."""
    out = np.full(len(close), NAN)
    d = np.diff(close)
    if len(d) < n:
        return out
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    ms, mg = su[:n].mean(), giu[:n].mean()
    out[n] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
    for k in range(n, len(d)):
        ms = (ms * (n - 1) + su[k]) / n
        mg = (mg * (n - 1) + giu[k]) / n
        out[k + 1] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
    return out


def max_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRIMA di i (esclusa i)."""
    out = np.full(len(x), NAN)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].max()
    return out


def min_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), NAN)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].min()
    return out


def std_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Deviazione standard (ddof=1) delle n osservazioni prima di i (esclusa i)."""
    out = np.full(len(x), NAN)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].std(ddof=1)
    return out


def quantile_precedente(x: np.ndarray, n: int, q: float) -> np.ndarray:
    """Quantile q delle n osservazioni prima di i (esclusa i), metodo lineare."""
    out = np.full(len(x), NAN)
    for i in range(n, len(x)):
        finestra = x[i - n:i]
        if np.isnan(finestra).any():
            continue
        out[i] = np.quantile(finestra, q)
    return out


def rendimenti(close: np.ndarray, k: int = 1) -> np.ndarray:
    out = np.full(len(close), NAN)
    out[k:] = close[k:] / close[:-k] - 1
    return out


def utc(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)


def ok(*valori) -> bool:
    return all(v is not None and not (isinstance(v, float) and math.isnan(v)) for v in valori)
