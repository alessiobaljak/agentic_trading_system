"""Indicatori causali: il valore all'indice i usa solo le barre 0..i (NaN nel riscaldamento)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

import numpy as np
import pandas as pd


def serie(candele: Sequence) -> dict:
    return {
        "open": np.array([c.open for c in candele], dtype=float),
        "high": np.array([c.high for c in candele], dtype=float),
        "low": np.array([c.low for c in candele], dtype=float),
        "close": np.array([c.close for c in candele], dtype=float),
        "volume": np.array([c.volume for c in candele], dtype=float),
        "ts": np.array([c.ts for c in candele], dtype=np.int64),
    }


def sma(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()


def ema(x: np.ndarray, n: int) -> np.ndarray:
    s = pd.Series(x).ewm(span=n, adjust=False, min_periods=n).mean().to_numpy()
    return s


def rolling_max(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).max().to_numpy()


def rolling_min(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).min().to_numpy()


def rolling_std(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).std(ddof=0).to_numpy()


def ritardo(x: np.ndarray, k: int) -> np.ndarray:
    """x spostato di k barre in avanti: out[i] = x[i-k] (NaN per i < k). k >= 1."""
    out = np.full_like(x, np.nan, dtype=float)
    out[k:] = x[:-k]
    return out


def true_range(h: np.ndarray, l: np.ndarray, c: np.ndarray) -> np.ndarray:
    prec = ritardo(c, 1)
    tr = np.maximum(h - l, np.maximum(np.abs(h - prec), np.abs(l - prec)))
    tr[0] = h[0] - l[0]
    return tr


def atr(h: np.ndarray, l: np.ndarray, c: np.ndarray, n: int) -> np.ndarray:
    return sma(true_range(h, l, c), n)


def rsi(c: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder (media esponenziale con alfa 1/n)."""
    d = np.diff(c, prepend=np.nan)
    su = pd.Series(np.where(d > 0, d, 0.0))
    giu = pd.Series(np.where(d < 0, -d, 0.0))
    su.iloc[0] = np.nan
    giu.iloc[0] = np.nan
    m_su = su.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    m_giu = giu.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = m_su / m_giu
    return (100 - 100 / (1 + rs)).to_numpy()


def rendimento(c: np.ndarray, k: int) -> np.ndarray:
    """c[i] / c[i-k] - 1."""
    return c / ritardo(c, k) - 1


def ora_utc(ts: np.ndarray) -> np.ndarray:
    return ((ts // 3_600_000) % 24).astype(int)


def giorno_settimana(ts: np.ndarray) -> np.ndarray:
    """0 = lunedi' ... 6 = domenica (UTC)."""
    return np.array([datetime.fromtimestamp(t / 1000, tz=timezone.utc).weekday() for t in ts], dtype=int)
